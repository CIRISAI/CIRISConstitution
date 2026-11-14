/-
  Settled.lean — which answers are final against every later row, and what makes a count final

  The challenge. Rows G (a grant), E (an act relying on G) and R (a cut on E's slot), with G in
  the past of E and of R, and E concurrent with R. A node holding {G, E} finds that E counts.
  At {G, E, R} it does not. So "E counts" is not monotone in the rows held, and no fold recovers
  the absence of an unseen concurrent row.

  What this file proves.
    Part 1  An admissible extension adds rows; it never changes the past of a row it already
            holds, since a row names its parents by digest and `parent` is one relation for every
            set. The kept layer and the concluded layer are final under every admissible
            extension, of any size, not only one row at a time (`kept_ext`, `concl_ext`).
    Part 2  The reviewer's counterexample, on three rows, under the cut as `Seat.lean` states it
            (`count_not_monotone`). Counting is a derived answer and is not final.
    Part 3  The general form. A cut voids a row unless it is disarmed against that row. If every
            cut that could void E in any extension is disarmed, E counts in every extension
            (`counts_final_of_disarmed`). Monotone disarming and a concluded E are all it needs.
    Part 4  One voice to a cut. `settled`: every voice that may cut E has signed a row
            acknowledging E. It is monotone (`settled_mono`). Under two rules the kernel does
            not state, (a) the voices that may cut E are fixed by E, and (b) an acknowledgement
            disarms its signer's cuts against what it acknowledges, a settled concluded act
            counts in every extension (`settled_final`). Necessity: an unsettled act is defeated
            by one row of a voice that has not acknowledged it (`unsettled_defeated`), and
            with that voice able to sign such a row, counting is final exactly when the act is
            settled (`final_iff_settled`).
    Part 5  A body cuts by a count. With the voices of a cut that acknowledged E not counted
            against E, acknowledgements by at least half of the members at E's head disarm
            every strict-majority cut (`body_settled_disarms`); fewer than half leave a strict
            majority that has acknowledged nothing (`body_unsettled_majority_free`).
    Part 6  Instances: a voice's fork, a voice's later overrule, and a voice seated later, each
            defeating an acknowledged act under the cut as stated (`fork_voids_acknowledged`,
            `overrule_voids_acknowledged`, `later_seat_defeats_acknowledged`). Rule (b) answers
            the first two; nothing in the kernel answers the third.
    Part 7  The closing theorem: kept and concluded are final by form, counting is final by
            acknowledgement and otherwise provisional (`three_ways_final`).
    Part 8  Blocking sets. Acknowledgements that meet every coalition able to cut block every
            cut (`blocking_set_blocks_all_cuts`); for a count of q of n members that is exactly
            n - q + 1 acknowledgements (`ack_blocking_quorum`, `five_three`).
    Part 9  Row by row, for a cut carried as one row with its signatures. A clean
            acknowledgement (no cut of the act by the same key in its own past) and a cut by the
            same key: the acknowledgement is in the cut's past (the act is then in it too), or
            the two are concurrent (`ack_cut_three_cases`). With the eligible voices and the
            count read at the act's head and a forked signature not counted against the act,
            clean acknowledgements meeting n - q + 1 make the act final against cuts in every
            extension (`ack_finality_future_stable`), and so does an effect row that names them
            (`effect_row_settled`). The fork rule is not derived (`fork_stands_on_row_count`),
            and an unclean acknowledgement blocks nothing (`unclean_ack_does_not_block`).
    Part 10 Closure. A view is closed under a step when its next value is a function of its
            value, exactly when there is no witness pair (`closed_iff_no_witness_pair`). Rows
            with answers are closed (`full_view_closed`); a view that keeps the rows of an
            unblocked act and drops those of a blocked one is closed (`pruned_view_closed`);
            "the act counts" with its rows dropped is not (`count_view_not_closed`).
    Part 11 The incremental fold and the checkpoint: under any extension a conclusion changes
            only where a newly kept row is in concurrent conflict with its row or an ancestor
            (`concl_ext_local`); a checkpoint row's past folded alone gives the conclusions of
            every later set (`checkpoint_conclusions`, `checkpoint_resume`).
    Part 12 Answers indexed by head. Whether an act counts at a head reads only the rows naming
            that head (`countsAt_local`), so a voice seated later acts forward and changes what is
            carried to its head, not the act's own (`later_head_changes_nothing`,
            `Rows.later_seat_is_forward`). Within a head each voice has one say; one that has
            said both has none (`symmetric_say_forced`: forced by treating its two rows alike;
            `say3_not_closed`: "both" must be kept apart from "nothing"). Acknowledgements by
            n - t + 1 members at the head then block every cut there in every extension
            (`say_settled_final`); a sole cutter that forks has no say (`Rows.fork_has_no_say`),
            and a deciding row with the act in its past is no vote (`Rows.overrule_is_no_vote`).

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports Recount.lean.
-/

import Recount

namespace Kernel

namespace Settled

open Order Relation Causal

/-! ## Part 1. Admissible extensions; the two layers final by form -/

section Form

variable {Row : Type} (parent : Row → Row → Prop) (wf : WellFounded parent)
variable (wellFormed : Row → Prop)

/-- An admissible extension: every row held is held still. The parents of a row are fixed by
    `parent`, one relation for every set, so no extension changes the past of a held row. -/
def Extends (S S' : Row → Prop) : Prop := ∀ r, S r → S' r

theorem extends_refl (S : Row → Prop) : Extends S S := fun _ h => h

theorem extends_trans (S S' S'' : Row → Prop) (h1 : Extends S S') (h2 : Extends S' S'') :
    Extends S S'' := fun r h => h2 r (h1 r h)

/-- Offering rows one at a time (`Recount.Grows`) is an admissible extension. -/
theorem grows_extends (S T : Row → Prop) (hg : Recount.Grows S T) : Extends S T := by
  induction hg with
  | refl => exact extends_refl S
  | step x _ _ ih => exact fun r h => Or.inl (ih r h)

/-- The past of a row is the same in every set: a held ancestor of a held row is an ancestor
    in every extension, and nothing new becomes its ancestor. -/
theorem past_fixed (S : Row → Prop) (p r : Row) (hk : kept parent wf wellFormed S r)
    (hp : TransGen parent p r) : S p :=
  kept_offered parent wf wellFormed S p (kept_ancestors parent wf wellFormed S p r hp hk)

/-- Kept is final under every admissible extension. -/
theorem kept_ext (S S' : Row → Prop) (h : Extends S S') (r : Row)
    (hk : kept parent wf wellFormed S r) : kept parent wf wellFormed S' r :=
  kept_mono parent wf wellFormed S S' h r hk

variable (judge : Row → (Row → Prop) → (Row → Prop) → Prop)

/-- Concluded is final under every admissible extension, of any size, for a rule that reads
    no concurrent row: the conclusion about a kept row is the same in every extension. This is
    `concl_final` for an arbitrary extension rather than one row. -/
theorem concl_ext (hC0 : ∀ r P (C C' : Row → Prop), judge r P C ↔ judge r P C')
    (root S S' : Row → Prop) (h : Extends S S') (r : Row)
    (hk : kept parent wf wellFormed S r) :
    concl parent wf judge wellFormed root S r ↔ concl parent wf judge wellFormed root S' r := by
  unfold concl
  apply conclOf_local parent wf judge (fun _ _ => False) (fun r P C C' _ => hC0 r P C C')
    (Live parent wf wellFormed root S) (Live parent wf wellFormed root S')
    (fun q => kept parent wf wellFormed S' q ∧ ¬ kept parent wf wellFormed S q)
  · intro q hq
    constructor
    · intro ⟨a, b⟩
      exact ⟨kept_mono parent wf wellFormed S S' h q a, b⟩
    · intro ⟨a, b⟩
      exact ⟨Classical.byContradiction fun hn => hq ⟨a, hn⟩, b⟩
  · intro q hq
    refine ⟨fun ⟨_, hn⟩ => hn ?_, fun _ _ hf => hf.elim⟩
    cases hq with
    | inl e => exact e ▸ hk
    | inr hqr => exact kept_ancestors parent wf wellFormed S q r hqr hk

/-- The same, read as growth: a concluded row stays concluded in every extension. -/
theorem concl_grows_ext (hC0 : ∀ r P (C C' : Row → Prop), judge r P C ↔ judge r P C')
    (root S S' : Row → Prop) (h : Extends S S') (r : Row)
    (hc : concl parent wf judge wellFormed root S r) :
    concl parent wf judge wellFormed root S' r :=
  (concl_ext parent wf wellFormed judge hC0 root S S' h r
    (concl_live parent wf judge wellFormed root S r hc).1).1 hc

end Form

/-! ## Part 3. Counting under the cut, with a disarming rule -/

section Disarm

variable {Row : Type} (parent : Row → Row → Prop)
variable (isCut : Row → Prop) (clashes overrules : Row → Row → Prop)
variable (ent : (Row → Prop) → (Row → Prop) → Row → Prop)
variable (hits : Row → Row → Prop)
variable (C : (Row → Prop) → Row → Prop)

/- `disarmed S x e`: in the set `S`, the cut `x` does not void the row `e`. The cut as the
   kernel states it is the case where nothing is disarmed. -/
variable (disarmed : (Row → Prop) → Row → Row → Prop)

/-- `e` counts at `S` when the cuts that may count void it only where they are not disarmed. -/
def countsD (S : Row → Prop) (e : Row) : Prop :=
  C S e ∧ ¬ rowVoided parent (fun x q => overrules x q ∧ ¬ disarmed S x q)
    (fun x q => hits x q ∧ ¬ disarmed S x q) (cutPoss parent isCut clashes overrules ent (C S)) e

/-- With nothing disarmed, `countsD` is the cut's own `rowCounts`. -/
theorem countsD_none (S : Row → Prop) (e : Row) :
    countsD parent isCut clashes overrules ent hits C (fun _ _ _ => False) S e ↔
      rowCounts parent isCut clashes overrules ent hits (C S) e := by
  unfold countsD rowCounts rowVoided
  constructor
  · intro ⟨a, b⟩
    refine ⟨a, fun hv => b ?_⟩
    cases hv with
    | inl h => let ⟨x, h1, h2, h3⟩ := h; exact Or.inl ⟨x, h1, h2, h3, fun f => f⟩
    | inr h => let ⟨x, h1, h2, h3⟩ := h; exact Or.inr ⟨x, h1, h2, h3, fun f => f⟩
  · intro ⟨a, b⟩
    refine ⟨a, fun hv => b ?_⟩
    cases hv with
    | inl h => let ⟨x, h1, h2, h3, _⟩ := h; exact Or.inl ⟨x, h1, h2, h3⟩
    | inr h => let ⟨x, h1, h2, h3, _⟩ := h; exact Or.inr ⟨x, h1, h2, h3⟩

/-- Disarming only takes voiding away: what counts under the cut counts under any disarming. -/
theorem countsD_of_rowCounts (S : Row → Prop) (e : Row)
    (h : rowCounts parent isCut clashes overrules ent hits (C S) e) :
    countsD parent isCut clashes overrules ent hits C disarmed S e := by
  refine ⟨h.1, fun hv => h.2 ?_⟩
  cases hv with
  | inl h => let ⟨x, h1, h2, h3, _⟩ := h; exact Or.inl ⟨x, h1, h2, h3⟩
  | inr h => let ⟨x, h1, h2, h3, _⟩ := h; exact Or.inr ⟨x, h1, h2, h3⟩

/-- A cut that counts or is contested is concluded, is a cut, and is entitled when nothing
    voids it. -/
theorem poss_candidate (hent : EntAnti ent) (A : Row → Prop) (x : Row)
    (h : cutPoss parent isCut clashes overrules ent A x) :
    A x ∧ isCut x ∧ ent A (fun _ => False) x :=
  ⟨h.1, h.2.1, hent A (fun _ => False) _ (fun _ f => f.elim) x h.2.2.1⟩

/-- Part 3. Let `e` be concluded and stay concluded in every extension. If in every extension
    every cut that could void `e` (concluded, a cut, entitled, and hitting or overruling `e`) is
    disarmed against it, `e` counts in every extension. -/
theorem counts_final_of_disarmed (hent : EntAnti ent)
    (S : Row → Prop) (e : Row)
    (hgrow : ∀ S', Extends S S' → C S' e)
    (hdis : ∀ S', Extends S S' → ∀ x, C S' x → isCut x → ent (C S') (fun _ => False) x →
      (hits x e ∨ overrules x e) → disarmed S' x e) :
    ∀ S', Extends S S' → countsD parent isCut clashes overrules ent hits C disarmed S' e := by
  intro S' hS
  refine ⟨hgrow S' hS, fun hv => ?_⟩
  cases hv with
  | inl h =>
    let ⟨x, hp, _, hh, hnd⟩ := h
    let ⟨a, b, c⟩ := poss_candidate parent isCut clashes overrules ent hent (C S') x hp
    exact hnd (hdis S' hS x a b c (Or.inl hh))
  | inr h =>
    let ⟨x, hp, _, ho, hnd⟩ := h
    let ⟨a, b, c⟩ := poss_candidate parent isCut clashes overrules ent hent (C S') x hp
    exact hnd (hdis S' hS x a b c (Or.inr ho))

end Disarm

/-! ## Part 4. One voice to a cut: settled by acknowledgement -/

section OneVoice

variable {Row Key : Type} (parent : Row → Row → Prop)
variable (isCut : Row → Prop) (clashes overrules : Row → Row → Prop)
variable (ent : (Row → Prop) → (Row → Prop) → Row → Prop)
variable (hits : Row → Row → Prop)
variable (C : (Row → Prop) → Row → Prop)
/- `voice x k`: `k` signed `x`. `acks a e`: `a` acknowledges `e`; it has `e` in its past. -/
variable (voice : Row → Key → Prop) (acks : Row → Row → Prop)

/-- `k` has acknowledged `e` in `S`: some held row signed by `k` acknowledges it. Counted or
    not: a row of a removed key still says what its signer said. -/
def acked (S : Row → Prop) (k : Key) (e : Row) : Prop :=
  ∃ a, S a ∧ voice a k ∧ acks a e

/-- Rule (b), for one voice. A cut is disarmed against `e` when one of its signers has
    acknowledged `e`, by any row, whichever rows the cut names. -/
def bound (S : Row → Prop) (x e : Row) : Prop :=
  ∃ k, voice x k ∧ acked voice acks S k e

/-- Settled: every voice that may cut `e` (`Q`) has acknowledged it. -/
def settled (Q : Key → Prop) (S : Row → Prop) (e : Row) : Prop :=
  ∀ k, Q k → acked voice acks S k e

/-- Claim A. Settled is monotone: a positive existential over held rows. -/
theorem settled_mono (Q : Key → Prop) (S S' : Row → Prop) (h : Extends S S') (e : Row)
    (hs : settled voice acks Q S e) : settled voice acks Q S' e :=
  fun k hk => let ⟨a, ha, hv, hack⟩ := hs k hk; ⟨a, h a ha, hv, hack⟩

/-- Rule (a), as a hypothesis: `Q` holds every voice that can cut `e`, in every set. -/
def Blocks (Q : Key → Prop) (e : Row) : Prop :=
  ∀ S x, C S x → isCut x → ent (C S) (fun _ => False) x → (hits x e ∨ overrules x e) →
    ∃ k, voice x k ∧ Q k

/-- Claim B. Under rule (a) (`Blocks`) and rule (b) (`bound`), a settled act that is concluded
    and stays concluded counts in every admissible extension. Whether it counts at `S` is not
    assumed: settled and concluded give it. -/
theorem settled_final (hent : EntAnti ent) (Q : Key → Prop) (S : Row → Prop) (e : Row)
    (hgrow : ∀ S', Extends S S' → C S' e)
    (hQ : Blocks isCut overrules ent hits C voice Q e)
    (hs : settled voice acks Q S e) :
    ∀ S', Extends S S' →
      countsD parent isCut clashes overrules ent hits C (bound voice acks) S' e :=
  counts_final_of_disarmed parent isCut clashes overrules ent hits C (bound voice acks) hent S e
    hgrow (fun S' hS x a b c d =>
      let ⟨k, hv, hk⟩ := hQ S' x a b c d
      ⟨k, hv, settled_mono voice acks Q S S' hS e hs k hk⟩)

/-- (b) without a new rule, half of it. Where a voice's cut names the voice's own
    acknowledgement (its rows form one line), the cut has `e` in its past and is not concurrent
    with `e`; no rule beyond the cut is needed against a concurrent void. The overrule half is
    not covered: see `overrule_voids_acknowledged`. -/
theorem own_line_not_concurrent (hack : ∀ a e, acks a e → TransGen parent e a)
    (a x e : Row) (ha : acks a e) (hline : TransGen parent a x) : ¬ conc parent x e :=
  fun h => h.2.1 (anc_trans (hack a e ha) hline)

/-- (e) Necessity. Let `k` not have acknowledged `e` at `S`, and let `x` be a row signed by `k`
    alone, not held, concurrent with `e` and hitting it, that counts or is contested as a cut
    once offered. Then at `S` with `x`, `e` does not count, even with rule (b). -/
theorem unsettled_defeated (hack : ∀ a e, acks a e → TransGen parent e a)
    (S : Row → Prop) (e x : Row) (k : Key)
    (hno : ¬ acked voice acks S k e) (hvx : ∀ k', voice x k' → k' = k)
    (hconc : conc parent x e) (hhit : hits x e)
    (hposs : cutPoss parent isCut clashes overrules ent (C (fun q => S q ∨ q = x)) x) :
    ¬ countsD parent isCut clashes overrules ent hits C (bound voice acks)
        (fun q => S q ∨ q = x) e := by
  intro ⟨_, hn⟩
  apply hn
  refine Or.inl ⟨x, hposs, hconc, hhit, ?_⟩
  intro ⟨k', hv, a, ha, hva, hacka⟩
  have e1 := hvx k' hv
  cases ha with
  | inl hS => exact hno ⟨a, hS, e1 ▸ hva, hacka⟩
  | inr ex => exact hconc.2.1 (ex ▸ hack a e hacka)

/-- (e) Counting is final exactly when the act is settled. Under rules (a) and (b), and with
    every voice of `Q` that has not acknowledged `e` able to sign one cut of its own that
    hits `e` and stands as a cut (`havail`, a statement about what keys can sign, which the
    rows do not prove), `e` counts in every extension iff it is settled. -/
theorem final_iff_settled (hent : EntAnti ent) (hack : ∀ a e, acks a e → TransGen parent e a)
    (Q : Key → Prop) (S : Row → Prop) (e : Row)
    (hgrow : ∀ S', Extends S S' → C S' e)
    (hQ : Blocks isCut overrules ent hits C voice Q e)
    (havail : ∀ k, Q k → ¬ acked voice acks S k e →
      ∃ x, ¬ S x ∧ (∀ k', voice x k' → k' = k) ∧ conc parent x e ∧ hits x e ∧
        cutPoss parent isCut clashes overrules ent (C (fun q => S q ∨ q = x)) x) :
    (∀ S', Extends S S' →
      countsD parent isCut clashes overrules ent hits C (bound voice acks) S' e) ↔
    settled voice acks Q S e := by
  constructor
  · intro hall k hk
    apply Classical.byContradiction
    intro hno
    let ⟨x, _, hvx, hconc, hhit, hposs⟩ := havail k hk hno
    exact unsettled_defeated parent isCut clashes overrules ent hits C voice acks hack S e x k
      hno hvx hconc hhit hposs (hall _ (fun r h => Or.inl h))
  · intro hs
    exact settled_final parent isCut clashes overrules ent hits C voice acks hent Q S e hgrow hQ hs

end OneVoice

/-! ## Part 5. A body cuts by a count -/

section Body

variable {Row K : Type} [DecidableEq K]
variable (voice : Row → K → Prop) (acks : Row → Row → Prop)
/- `M`: the members at the head `e` names, as a list without repeats. A cut by the body
   counts against `e` on a strict majority of `M`. -/
variable (M : List K)

/-- Rule (b) for a body. A cut is disarmed against `e` unless the voices it carries that have
    not acknowledged `e` are, alone, a strict majority of `M`. An acknowledgement takes its
    signer's voice out of every count against what it acknowledges; it does not veto the cut. -/
def disarmedBody (S : Row → Prop) (x e : Row) : Prop :=
  ¬ ∃ V : List K, V.Nodup ∧
    (∀ k, k ∈ V → k ∈ M ∧ voice x k ∧ ¬ acked voice acks S k e) ∧ M.length < 2 * V.length

/-- Settled by a body: members of `M` that have acknowledged `e` number at least half of `M`. -/
def settledBody (S : Row → Prop) (e : Row) : Prop :=
  ∃ Q : List K, Q.Nodup ∧ (∀ k, k ∈ Q → k ∈ M ∧ acked voice acks S k e) ∧
    M.length ≤ 2 * Q.length

/-- (c) Acknowledgements by at least half the members disarm every cut, in every extension. -/
theorem body_settled_disarms (S S' : Row → Prop) (h : Extends S S') (e : Row)
    (hs : settledBody voice acks M S e) (x : Row) : disarmedBody voice acks M S' x e := by
  intro ⟨V, hV, hVs, hqV⟩
  let ⟨Q, hQ, hQs, hqQ⟩ := hs
  have hd : ∀ k, k ∈ V → ¬ k ∈ Q := fun k hkV hkQ =>
    let ⟨a, ha, hv, hack⟩ := (hQs k hkQ).2
    (hVs k hkV).2.2 ⟨a, h a ha, hv, hack⟩
  have := disjoint_length V Q M hV hQ (fun k hk => (hVs k hk).1) (fun k hk => (hQs k hk).1) hd
  omega

omit [DecidableEq K] in
theorem filter_split (p : K → Bool) : ∀ l : List K,
    (l.filter p).length + (l.filter (fun k => !p k)).length = l.length
  | [] => rfl
  | k :: l => by
    have ih := filter_split p l
    cases hp : p k <;> simp [List.filter_cons, hp] <;> omega

omit [DecidableEq K] in
/-- (c) The threshold is tight. If fewer than half of `M` have acknowledged `e`, the members
    that have not are a strict majority of `M` that no acknowledgement disarms. -/
theorem body_unsettled_majority_free (S : Row → Prop) (e : Row) (hM : M.Nodup)
    (ackB : K → Bool) (hackB : ∀ k, ackB k = true ↔ acked voice acks S k e)
    (hfew : 2 * (M.filter ackB).length < M.length) :
    ∃ V : List K, V.Nodup ∧ (∀ k, k ∈ V → k ∈ M ∧ ¬ acked voice acks S k e) ∧
      M.length < 2 * V.length := by
  refine ⟨M.filter (fun k => !ackB k), List.Pairwise.filter _ hM, ?_, ?_⟩
  · intro k hk
    have ⟨h1, h2⟩ := List.mem_filter.1 hk
    refine ⟨h1, fun ha => ?_⟩
    have := (hackB k).2 ha
    simp [this] at h2
  · have := filter_split ackB M
    omega

/-- (c) For the strict majority: half is enough and needed. A list of members that have not
    acknowledged, disjoint from at least half of `M` that have, is no strict majority. -/
theorem half_disarms_majority (V Q : List K) (hV : V.Nodup) (hQ : Q.Nodup)
    (hVM : ∀ k, k ∈ V → k ∈ M) (hQM : ∀ k, k ∈ Q → k ∈ M) (hd : ∀ k, k ∈ V → ¬ k ∈ Q)
    (hq : M.length ≤ 2 * Q.length) : ¬ M.length < 2 * V.length := by
  have := disjoint_length V Q M hV hQ hVM hQM hd
  omega

/-- (c) Any count. Where a cut needs `t` voices of `M`, acknowledgements by `Q` with
    `M.length < t + Q.length` (so `Q` holds at least `M.length - t + 1` members) leave fewer than
    `t` voices that have not acknowledged. -/
theorem count_disarmed (t : Nat) (V Q : List K) (hV : V.Nodup) (hQ : Q.Nodup)
    (hVM : ∀ k, k ∈ V → k ∈ M) (hQM : ∀ k, k ∈ Q → k ∈ M) (hd : ∀ k, k ∈ V → ¬ k ∈ Q)
    (hq : M.length < t + Q.length) : V.length < t := by
  have := disjoint_length V Q M hV hQ hVM hQM hd
  omega

end Body

/-! ## Part 7. The closing theorem -/

section Close

variable {Row Key : Type} (parent : Row → Row → Prop) (wf : WellFounded parent)
variable (wellFormed : Row → Prop) (judge : Row → (Row → Prop) → (Row → Prop) → Prop)
variable (root : Row → Prop)
variable (isCut : Row → Prop) (clashes overrules : Row → Row → Prop)
variable (ent : (Row → Prop) → (Row → Prop) → Row → Prop)
variable (hits : Row → Row → Prop)
variable (voice : Row → Key → Prop) (acks : Row → Row → Prop)

/-- Every answer about a kept row is final by form, final by acknowledgement, or provisional,
    and which is a function of the rows held. With a conclusion rule that reads no concurrent
    row: (1) the row is kept in every extension; (2) its conclusion is the same in every
    extension; (3) under rules (a) and (b), and with every voice that may cut it able to sign
    a cut of its own, it counts in every extension exactly when every voice that may cut it
    has acknowledged it. Otherwise one row of one such voice defeats it. -/
theorem three_ways_final
    (hC0 : ∀ r P (C C' : Row → Prop), judge r P C ↔ judge r P C')
    (hent : EntAnti ent) (hack : ∀ a e, acks a e → TransGen parent e a)
    (Q : Key → Prop) (S : Row → Prop) (e : Row)
    (hc : concl parent wf judge wellFormed root S e)
    (hQ : Blocks isCut overrules ent hits (concl parent wf judge wellFormed root) voice Q e)
    (havail : ∀ k, Q k → ¬ acked voice acks S k e →
      ∃ x, ¬ S x ∧ (∀ k', voice x k' → k' = k) ∧ conc parent x e ∧ hits x e ∧
        cutPoss parent isCut clashes overrules ent
          (concl parent wf judge wellFormed root (fun q => S q ∨ q = x)) x) :
    (∀ S', Extends S S' → kept parent wf wellFormed S' e) ∧
    (∀ S', Extends S S' → concl parent wf judge wellFormed root S' e) ∧
    ((∀ S', Extends S S' →
        countsD parent isCut clashes overrules ent hits (concl parent wf judge wellFormed root)
          (bound voice acks) S' e) ↔ settled voice acks Q S e) := by
  have hk := (concl_live parent wf judge wellFormed root S e hc).1
  have hgrow : ∀ S', Extends S S' → concl parent wf judge wellFormed root S' e :=
    fun S' h => concl_grows_ext parent wf wellFormed judge hC0 root S S' h e hc
  exact ⟨fun S' h => kept_ext parent wf wellFormed S S' h e hk, hgrow,
    final_iff_settled parent isCut clashes overrules ent hits
      (concl parent wf judge wellFormed root) voice acks hent hack Q S e hgrow hQ havail⟩

end Close

/-! ## Parts 2 and 6. Instances on seven rows

  `h` is a head (the grant G). `e` is an act naming `h`, signed by `m`. `a` is `V`'s
  acknowledgement of `e`. `x` is a cut on `e`'s slot by `V`, naming only `h` (the reviewer's R,
  and a fork of `V`'s own rows). `d` is a deciding row by `V` naming `a` that overrules `e`.
  `h1` is a later head naming `h` that seats `W`; `w` is `W`'s cut on `e`'s slot naming `h1`.
  The voices with standing to cut `e` at the head `e` names are `V` alone. -/

namespace Rows

inductive Key | m | V | W
  deriving DecidableEq, Repr

inductive R | h | e | a | x | d | h1 | w
  deriving DecidableEq, Repr

open R

def parentB : R → R → Bool
  | h, e => true | e, a => true | h, x => true | a, d => true | h, h1 => true | h1, w => true
  | _, _ => false
def parent (p q : R) : Prop := parentB p q = true

def depth : R → Nat
  | h => 0 | e => 1 | a => 2 | x => 1 | d => 3 | h1 => 1 | w => 2

theorem parent_wf : WellFounded parent :=
  Subrelation.wf (r := InvImage (· < ·) depth)
    (fun {p q} hp => by
      revert hp; cases p <;> cases q <;> simp [parent, parentB, depth, InvImage])
    (InvImage.wf depth Nat.lt_wfRel.wf)

def ancB : R → R → Bool
  | h, e => true | h, a => true | h, x => true | h, d => true | h, h1 => true | h, w => true
  | e, a => true | e, d => true | a, d => true | h1, w => true
  | _, _ => false

theorem par_anc : ∀ p q, parentB p q = true → ancB p q = true := by
  intro p q; cases p <;> cases q <;> decide

theorem anc_step : ∀ p b c, ancB p b = true → parentB b c = true → ancB p c = true := by
  intro p b c; cases p <;> cases b <;> cases c <;> decide

theorem anc_sound {p q : R} (hpq : TransGen parent p q) : ancB p q = true := by
  induction hpq with
  | single hp => exact par_anc _ _ hp
  | tail _ hp ih => exact anc_step _ _ _ ih hp

def signerOf : R → Key
  | e => Key.m | w => Key.W | _ => Key.V
def voice (r : R) (k : Key) : Prop := signerOf r = k

def isCut (r : R) : Prop := r = x ∨ r = d ∨ r = w
def hits (c q : R) : Prop := (c = x ∨ c = w) ∧ q = e
def overrules (c q : R) : Prop := c = d ∧ q = e
def clashes (_ _ : R) : Prop := False
/-- Every cut's signer is seated at the head the cut names: `V` at `h`, `W` at `h1`. -/
def ent (_ _ : R → Prop) (_ : R) : Prop := True
def acks (p q : R) : Prop := p = a ∧ q = e
/-- The voices with standing on `e`'s slot at the head `e` names. -/
def Q (k : Key) : Prop := k = Key.V

theorem ent_anti : EntAnti ent := fun _ _ _ _ _ _ => trivial

theorem acks_past : ∀ p q, acks p q → TransGen parent q p := by
  intro p q ⟨hp, hq⟩
  subst hp; subst hq
  exact TransGen.single rfl

abbrev Cn (S : R → Prop) : R → Prop :=
  concl parent parent_wf (fun _ _ _ => True) (fun _ => True) (fun _ => True) S

theorem concluded (S : R → Prop) (hcl : ∀ p q, parent p q → S q → S p) (q : R) (hq : S q) :
    Cn S q :=
  concl_all parent parent_wf _ S q
    (kept_of_closed parent parent_wf _ S (fun _ _ => trivial) hcl q hq)

theorem offered (S : R → Prop) (q : R) (hq : Cn S q) : S q :=
  kept_offered parent parent_wf _ S q (concl_live parent parent_wf _ _ _ S q hq).1

/-- With no cut clashing with or overruling another, a cut counts or is contested exactly when
    it is concluded. -/
theorem poss_iff (A : R → Prop) (c : R) :
    cutPoss parent isCut clashes overrules ent A c ↔ A c ∧ isCut c := by
  unfold cutPoss poss
  constructor
  · intro hc; exact ⟨hc.1, hc.2.1⟩
  · intro ⟨ha, hc⟩
    refine ⟨ha, hc, trivial, fun ⟨_, _, _, f⟩ => f, fun ⟨_, _, _, ho⟩ => ?_⟩
    rcases hc with h | h | h <;> subst h <;> simp [overrules] at ho

def S0b : R → Bool | h => true | e => true | a => true | _ => false
def SGEb : R → Bool | h => true | e => true | _ => false
def SGERb : R → Bool | h => true | e => true | x => true | _ => false
def Sfb : R → Bool | h => true | e => true | a => true | x => true | _ => false
def Sob : R → Bool | h => true | e => true | a => true | d => true | _ => false
def Slb : R → Bool | h => true | e => true | a => true | h1 => true | w => true | _ => false
abbrev S0 (q : R) : Prop := S0b q = true     -- the act and V's acknowledgement
abbrev SGE (q : R) : Prop := SGEb q = true   -- the reviewer's H: G and E
abbrev SGER (q : R) : Prop := SGERb q = true -- the reviewer's H': G, E and R
abbrev Sf (q : R) : Prop := Sfb q = true     -- S0 and V's fork cut
abbrev So (q : R) : Prop := Sob q = true     -- S0 and V's overrule on its own line
abbrev Sl (q : R) : Prop := Slb q = true     -- S0, a later head seating W, and W's cut

theorem S0_cl : ∀ p q, parent p q → S0 q → S0 p := by
  intro p q; cases p <;> cases q <;> simp [parent, parentB, S0, S0b]
theorem SGE_cl : ∀ p q, parent p q → SGE q → SGE p := by
  intro p q; cases p <;> cases q <;> simp [parent, parentB, SGE, SGEb]
theorem SGER_cl : ∀ p q, parent p q → SGER q → SGER p := by
  intro p q; cases p <;> cases q <;> simp [parent, parentB, SGER, SGERb]
theorem Sf_cl : ∀ p q, parent p q → Sf q → Sf p := by
  intro p q; cases p <;> cases q <;> simp [parent, parentB, Sf, Sfb]
theorem So_cl : ∀ p q, parent p q → So q → So p := by
  intro p q; cases p <;> cases q <;> simp [parent, parentB, So, Sob]
theorem Sl_cl : ∀ p q, parent p q → Sl q → Sl p := by
  intro p q; cases p <;> cases q <;> simp [parent, parentB, Sl, Slb]

theorem conc_xe : conc parent x e :=
  ⟨fun hp => by have := anc_sound hp; simp [ancB] at this,
   fun hp => by have := anc_sound hp; simp [ancB] at this, by decide⟩

theorem conc_we : conc parent w e :=
  ⟨fun hp => by have := anc_sound hp; simp [ancB] at this,
   fun hp => by have := anc_sound hp; simp [ancB] at this, by decide⟩

theorem e_before_d : TransGen parent e d :=
  TransGen.tail (TransGen.single (b := a) rfl) rfl

abbrev Counts (S : R → Prop) : R → Prop :=
  rowCounts parent isCut clashes overrules ent hits (Cn S)

abbrev CountsB (S : R → Prop) : R → Prop :=
  countsD parent isCut clashes overrules ent hits Cn (bound voice acks) S

/-- A cut that is concluded in `S` voids `e` when it is `x` or `w`. -/
theorem voided_by (S : R → Prop) (c : R) (hS : S c) (hcl : ∀ p q, parent p q → S q → S p)
    (hc : c = x ∨ c = w) : ¬ Counts S e := by
  intro ⟨_, hn⟩
  apply hn
  refine Or.inl ⟨c, (poss_iff _ c).2 ⟨concluded S hcl c hS, ?_⟩, ?_, ⟨hc, rfl⟩⟩
  · rcases hc with hc | hc <;> subst hc <;> simp [isCut]
  · rcases hc with hc | hc <;> subst hc
    · exact conc_xe
    · exact conc_we

/-- Part 2. The reviewer's counterexample. At {G, E} the act counts; at {G, E, R}, an
    admissible extension, it does not. It is concluded at both: the conclusion is final and
    counting is not. -/
theorem count_not_monotone :
    Extends SGE SGER ∧ Cn SGE e ∧ Cn SGER e ∧ Counts SGE e ∧ ¬ Counts SGER e := by
  refine ⟨?_, concluded SGE SGE_cl e rfl, concluded SGER SGER_cl e rfl, ?_,
    voided_by SGER x rfl SGER_cl (Or.inl rfl)⟩
  · intro q hq; cases q <;> simp_all [SGE, SGEb, SGER, SGERb]
  · refine ⟨concluded SGE SGE_cl e rfl, fun hv => ?_⟩
    rcases hv with ⟨c, hp, _, hh⟩ | ⟨c, hp, _, ho⟩
    · have := offered SGE c hp.1
      rcases hh.1 with hc | hc <;> subst hc <;> simp [SGE, SGEb] at this
    · have := offered SGE c hp.1
      rw [ho.1] at this; simp [SGE, SGEb] at this

/-- `e` is settled at `S0`: the one voice with standing at its head has acknowledged it. -/
theorem settled_S0 : settled voice acks Q S0 e :=
  fun _ hk => ⟨a, rfl, hk.symm ▸ rfl, rfl, rfl⟩

/-- A row signed by `V` is disarmed against `e` wherever `V`'s acknowledgement is held. -/
theorem bound_V (S : R → Prop) (hS : S a) (c : R) (hc : signerOf c = Key.V) :
    bound voice acks S c e :=
  ⟨Key.V, hc, a, hS, rfl, rfl, rfl⟩

/-- (b), a fork. `V` acknowledged `e`, then signed a cut that does not name its
    acknowledgement. Under the cut as stated, `e` does not count; under rule (b) it does. -/
theorem fork_voids_acknowledged :
    settled voice acks Q Sf e ∧ ¬ Counts Sf e ∧ CountsB Sf e := by
  refine ⟨fun k hk => ⟨a, rfl, hk.symm ▸ rfl, rfl, rfl⟩,
    voided_by Sf x rfl Sf_cl (Or.inl rfl), concluded Sf Sf_cl e rfl, fun hv => ?_⟩
  rcases hv with ⟨c, hp, _, hh, hnb⟩ | ⟨c, hp, _, ho, hnb⟩
  · rcases hh.1 with hc | hc <;> subst hc
    · exact hnb (bound_V Sf rfl x rfl)
    · have := offered Sf w ((poss_iff _ w).1 hp).1
      simp [Sf, Sfb] at this
  · rw [ho.1] at hnb
    exact hnb (bound_V Sf rfl d rfl)

/-- (b), an overrule on the voice's own line. `V` acknowledged `e`, then signed a deciding row
    that names its acknowledgement and overrules `e`. The overrule is not concurrent with `e`,
    and under the cut as stated `e` still does not count; under rule (b) it does. So a single
    line of rows for each voice does not give (b). -/
theorem overrule_voids_acknowledged :
    TransGen parent a d ∧ settled voice acks Q So e ∧ ¬ Counts So e ∧ CountsB So e := by
  refine ⟨TransGen.single rfl, fun k hk => ⟨a, rfl, hk.symm ▸ rfl, rfl, rfl⟩, ?_,
    concluded So So_cl e rfl, fun hv => ?_⟩
  · intro ⟨_, hn⟩
    apply hn
    exact Or.inr ⟨d, (poss_iff _ d).2 ⟨concluded So So_cl d rfl, Or.inr (Or.inl rfl)⟩,
      e_before_d, rfl, rfl⟩
  · rcases hv with ⟨c, hp, _, hh, _⟩ | ⟨c, hp, _, ho, hnb⟩
    · have := offered So c ((poss_iff _ c).1 hp).1
      rcases hh.1 with hc | hc <;> subst hc <;> simp [So, Sob] at this
    · rw [ho.1] at hnb
      exact hnb (bound_V So rfl d rfl)

/-- (a). `W` is seated at a later head and its cut names that head. `e` was settled at `S0`,
    and `Sl` is an admissible extension of `S0`; with rule (b), `e` does not count at `Sl`.
    The cut is entitled at the head it names, and nobody at `e`'s head was asked. -/
theorem later_seat_defeats_acknowledged :
    settled voice acks Q S0 e ∧ Extends S0 Sl ∧ ¬ CountsB Sl e := by
  refine ⟨settled_S0, ?_, ?_⟩
  · intro q hq; cases q <;> simp_all [S0, S0b, Sl, Slb]
  · intro ⟨_, hn⟩
    apply hn
    refine Or.inl ⟨w, (poss_iff _ w).2 ⟨concluded Sl Sl_cl w rfl, Or.inr (Or.inr rfl)⟩,
      conc_we, ⟨Or.inr rfl, rfl⟩, ?_⟩
    intro ⟨k, hv, a', _, hva, hack⟩
    have hk : k = Key.W := hv.symm
    rw [hack.1] at hva
    rw [hk] at hva
    exact absurd hva (by simp [voice, signerOf])

/-- (a), the rule that answers it. Read the entitlement to cut `e` at the head `e` names, where
    only `V` stands: then every extension of `S0`, the one above included, leaves `e` counting
    under rule (b). -/
def entAtE (_ _ : R → Prop) (c : R) : Prop := signerOf c = Key.V

theorem seat_at_head_restores :
    ∀ S', Extends S0 S' →
      countsD parent isCut clashes overrules entAtE hits Cn (bound voice acks) S' e :=
  settled_final parent isCut clashes overrules entAtE hits Cn voice acks
    (fun _ _ _ _ _ h => h) Q S0 e
    (fun S' h => concl_grows_ext parent parent_wf (fun _ => True) (fun _ _ _ => True)
      (fun _ _ _ _ => Iff.rfl) (fun _ => True) S0 S' h e (concluded S0 S0_cl e rfl))
    (fun _ _ _ _ hent _ => ⟨Key.V, hent, rfl⟩) settled_S0

end Rows

/-! ## Part 8. Blocking sets: a hitting set, and the count's threshold -/

section Blocking

variable {K : Type} [DecidableEq K]

omit [DecidableEq K] in
/-- If every coalition that can produce a cut of the act holds a voice of `B`, and no voice of
    `B` gives an effective cut vote, no coalition produces an effective cut. -/
theorem blocking_set_blocks_all_cuts (Coal : List K → Prop) (B eff : K → Prop)
    (hblk : ∀ V, Coal V → ∃ k, k ∈ V ∧ B k) (hab : ∀ k, B k → ¬ eff k) :
    ¬ ∃ V, Coal V ∧ ∀ k, k ∈ V → eff k :=
  fun ⟨V, hc, he⟩ => let ⟨k, hk, hb⟩ := hblk V hc; hab k hb (he k hk)

omit [DecidableEq K] in
/-- The converse shape: a coalition disjoint from `B` whose every voice can give an effective
    vote (realizable) produces a cut. -/
theorem unblocked_coalition_can_cut (Coal : List K → Prop) (B eff : K → Prop)
    (V : List K) (hc : Coal V) (hd : ∀ k, k ∈ V → ¬ B k)
    (hreal : ∀ k, k ∈ V → ¬ B k → eff k) :
    ∃ V, Coal V ∧ ∀ k, k ∈ V → eff k :=
  ⟨V, hc, fun k hk => hreal k hk (hd k hk)⟩

/-- The coalitions of a count: `q` distinct members of `M`. -/
def countCoal (M : List K) (q : Nat) (V : List K) : Prop :=
  V.Nodup ∧ (∀ k, k ∈ V → k ∈ M) ∧ q ≤ V.length

/-- The threshold, both ways. A list `Bl` of members meets every coalition of `q` of the `n`
    members of `M` exactly when `|Bl| ≥ n - q + 1`. -/
theorem ack_blocking_quorum (M Bl : List K) (q : Nat) (hM : M.Nodup) (hB : Bl.Nodup)
    (hBM : ∀ k, k ∈ Bl → k ∈ M) :
    (∀ V, countCoal M q V → ∃ k, k ∈ V ∧ k ∈ Bl) ↔ M.length < q + Bl.length := by
  constructor
  · intro h
    apply Classical.byContradiction
    intro hn
    have hsplit : (M.filter (fun k => decide (k ∈ Bl))).length +
        (M.filter (fun k => !decide (k ∈ Bl))).length = M.length := filter_split _ M
    have hin : (M.filter (fun k => decide (k ∈ Bl))).length ≤ Bl.length :=
      nodup_subset_length _ _ (List.Pairwise.filter _ hM)
        (fun k hk => of_decide_eq_true (List.mem_filter.1 hk).2)
    have hV : countCoal M q (M.filter (fun k => !decide (k ∈ Bl))) :=
      ⟨List.Pairwise.filter _ hM, fun k hk => (List.mem_filter.1 hk).1, by omega⟩
    have ⟨k, hk, hkB⟩ := h _ hV
    have := (List.mem_filter.1 hk).2
    simp [hkB] at this
  · intro hq V ⟨hV, hVM, hqV⟩
    apply Classical.byContradiction
    intro hn
    have hd : ∀ k, k ∈ V → ¬ k ∈ Bl := fun k hk hb => hn ⟨k, hk, hb⟩
    have := disjoint_length V Bl M hV hB hVM hBM hd
    omega

/-- Five members, a count of three: three acknowledgements block every cut, and two do not. -/
theorem five_three (M Bl : List K) (hM : M.Nodup) (hB : Bl.Nodup)
    (hBM : ∀ k, k ∈ Bl → k ∈ M) (h5 : M.length = 5) :
    (∀ V, countCoal M 3 V → ∃ k, k ∈ V ∧ k ∈ Bl) ↔ 3 ≤ Bl.length :=
  (ack_blocking_quorum M Bl 3 hM hB hBM).trans ⟨fun h => by omega, fun h => by omega⟩

end Blocking

/-! ## Part 9. Acknowledgements and counted cuts, row by row

  A cut of the act `act` by a body is one row carrying its signers' signatures (`sig`); its
  count is a property of that row (`Consent.count_is_final_against_members`). Two choices are
  rules, not derived (rules_needed.md): the members `M` and the count `q` are those at the head
  `act` names (the eligible cutters are frozen by the act), and a signature on a cut is not
  counted against `act` when its signer holds a CLEAN acknowledgement of `act` concurrent with
  the cut. An acknowledgement is clean when no cut of `act` signed by the same key is it or in
  its past; cleanness reads the acknowledgement's own past only, so it is final by form. -/

section Acks

variable {Row K : Type} [DecidableEq K] (parent : Row → Row → Prop)
variable (sig : Row → K → Prop) (isCutOf isAck : Row → Prop) (act : Row)
variable (M : List K) (q : Nat)

/-- A clean acknowledgement of `act` by `k`. -/
def clean (A : Row) (k : K) : Prop :=
  isAck A ∧ sig A k ∧ ¬ ∃ c, (c = A ∨ TransGen parent c A) ∧ isCutOf c ∧ sig c k

/-- `k` holds, in `H`, a clean acknowledgement concurrent with the cut `c`: the fork. -/
def forkAck (H : Row → Prop) (c : Row) (k : K) : Prop :=
  ∃ A, H A ∧ clean parent sig isCutOf isAck A k ∧ conc parent A c

/-- The cut `c` voids `act` at `H`: it is concurrent with `act`, and its signatures that are
    members at `act`'s head and not forked against a clean acknowledgement reach `q`. -/
def voids (H : Row → Prop) (c : Row) : Prop :=
  isCutOf c ∧ conc parent c act ∧ ∃ V : List K, V.Nodup ∧
    (∀ k, k ∈ V → k ∈ M ∧ sig c k ∧ ¬ forkAck parent sig isCutOf isAck H c k) ∧ q ≤ V.length

/-- `act` counts at `H`: held, and no held cut voids it. -/
def countsA (H : Row → Prop) : Prop :=
  H act ∧ ¬ ∃ c, H c ∧ voids parent sig isCutOf isAck act M q H c

omit [DecidableEq K] in
/-- The cases of a clean acknowledgement `A` and a cut `c` signed by the same key. (i) `A` in the
    past of `c`: `act` is in the past of `c`, which then does not void it as a concurrent row.
    (ii) `c` in the past of `A`: excluded by cleanness. `A` is not `c`. (iii) concurrent: the
    signature is forked and not counted. -/
theorem ack_cut_three_cases (hack : ∀ A, isAck A → TransGen parent act A)
    (A c : Row) (k : K) (hA : clean parent sig isCutOf isAck A k) (hc : isCutOf c)
    (hs : sig c k) :
    (TransGen parent A c → ¬ conc parent c act) ∧ ¬ TransGen parent c A ∧ A ≠ c ∧
      (conc parent A c → ∀ H : Row → Prop, H A → forkAck parent sig isCutOf isAck H c k) :=
  ⟨fun h hcon => hcon.2.1 (anc_trans (hack A hA.1) h),
   fun h => hA.2.2 ⟨c, Or.inr h, hc, hs⟩,
   fun e => hA.2.2 ⟨c, Or.inl e.symm, hc, hs⟩,
   fun hcon _ hH => ⟨A, hH, hA, hcon⟩⟩

omit [DecidableEq K] in
/-- So a key holding a clean acknowledgement is never a counted voice of a cut that voids. -/
theorem ack_blocks_cut (hack : ∀ A, isAck A → TransGen parent act A)
    (H : Row → Prop) (c A : Row) (k : K) (hH : H A) (hA : clean parent sig isCutOf isAck A k)
    (hc : isCutOf c) (hconc : conc parent c act) (hs : sig c k)
    (hnf : ¬ forkAck parent sig isCutOf isAck H c k) : False := by
  have ⟨h1, h2, h3, h4⟩ := ack_cut_three_cases parent sig isCutOf isAck act hack A c k hA hc hs
  by_cases e1 : TransGen parent A c
  · exact h1 e1 hconc
  · exact hnf (h4 ⟨e1, h2, h3⟩ H hH)

/-- A cut that has a clean acknowledgement in its past has `act` in its past. -/
theorem cut_with_ack_is_ancestor (hack : ∀ A, isAck A → TransGen parent act A)
    (A c : Row) (hA : isAck A) (h : TransGen parent A c) : TransGen parent act c :=
  anc_trans (hack A hA) h

/-- Finality by acknowledgement, against cuts. Let `H` hold clean acknowledgements by a list
    `Bl` of members with `n < q + |Bl|`. In every admissible extension of `H` no cut voids
    `act`; the members and the count are those at `act`'s head, and nobody leaves the count. -/
theorem ack_finality_future_stable (hack : ∀ A, isAck A → TransGen parent act A)
    (H H' : Row → Prop) (hext : Extends H H') (Bl : List K) (hB : Bl.Nodup)
    (hBl : ∀ k, k ∈ Bl → k ∈ M ∧ ∃ A, H A ∧ clean parent sig isCutOf isAck A k)
    (hq : M.length < q + Bl.length) :
    ∀ c, ¬ voids parent sig isCutOf isAck act M q H' c := by
  intro c ⟨hc, hconc, V, hV, hVs, hqV⟩
  have hd : ∀ k, k ∈ V → ¬ k ∈ Bl := fun k hkV hkB =>
    let ⟨A, hA, hcl⟩ := (hBl k hkB).2
    ack_blocks_cut parent sig isCutOf isAck act hack H' c A k (hext A hA) hcl hc hconc
      (hVs k hkV).2.1 (hVs k hkV).2.2
  have := disjoint_length V Bl M hV hB (fun k hk => (hVs k hk).1) (fun k hk => (hBl k hk).1) hd
  omega

theorem ack_counts_future_stable (hack : ∀ A, isAck A → TransGen parent act A)
    (H : Row → Prop) (ha : H act) (Bl : List K) (hB : Bl.Nodup)
    (hBl : ∀ k, k ∈ Bl → k ∈ M ∧ ∃ A, H A ∧ clean parent sig isCutOf isAck A k)
    (hq : M.length < q + Bl.length) :
    ∀ H', Extends H H' → countsA parent sig isCutOf isAck act M q H' :=
  fun H' hext => ⟨hext act ha, fun ⟨c, _, hv⟩ =>
    ack_finality_future_stable parent sig isCutOf isAck act M q hack H H' hext Bl hB hBl hq c hv⟩

/-- An effect row rests on a settled act when its own past holds clean acknowledgements by a
    blocking list. This reads the effect row's past and no held set: it is final by form. -/
def restsSettled (f : Row) : Prop :=
  ∃ Bl : List K, Bl.Nodup ∧
    (∀ k, k ∈ Bl → k ∈ M ∧ ∃ A, TransGen parent A f ∧ clean parent sig isCutOf isAck A k) ∧
    M.length < q + Bl.length

/-- The collapse. Wherever an effect row resting on a settled act is kept, no cut voids the act
    in that set or in any admissible extension of it. Whoever evaluates the effect row holds
    its past, so holds the acknowledgements it names. -/
theorem effect_row_settled (wf : WellFounded parent) (wellFormed : Row → Prop)
    (hack : ∀ A, isAck A → TransGen parent act A)
    (H : Row → Prop) (f : Row) (hk : kept parent wf wellFormed H f)
    (hr : restsSettled parent sig isCutOf isAck M q f) :
    ∀ H', Extends H H' → ∀ c, ¬ voids parent sig isCutOf isAck act M q H' c :=
  let ⟨Bl, hB, hBl, hq⟩ := hr
  fun H' hext => ack_finality_future_stable parent sig isCutOf isAck act M q hack H H' hext Bl hB
    (fun k hkB => let ⟨hm, A, hA, hcl⟩ := hBl k hkB
      ⟨hm, A, past_fixed parent wf wellFormed H A f hk hA, hcl⟩) hq

/-- Blocked at `H`: `act` held, and clean acknowledgements by a blocking list held. -/
def blocked (H : Row → Prop) : Prop :=
  H act ∧ ∃ Bl : List K, Bl.Nodup ∧
    (∀ k, k ∈ Bl → k ∈ M ∧ ∃ A, H A ∧ clean parent sig isCutOf isAck A k) ∧
    M.length < q + Bl.length

omit [DecidableEq K] in
theorem blocked_mono (H H' : Row → Prop) (h : Extends H H')
    (hb : blocked parent sig isCutOf isAck act M q H) :
    blocked parent sig isCutOf isAck act M q H' :=
  let ⟨ha, Bl, hB, hBl, hq⟩ := hb
  ⟨h act ha, Bl, hB, fun k hk => let ⟨hm, A, hA, hcl⟩ := hBl k hk; ⟨hm, A, h A hA, hcl⟩, hq⟩

end Acks

/-! ## Part 10. Closure: a view whose next value is a function of its value -/

section Closure

/-- `v` is closed under the steps `T i` when the view after a step is a function of the view
    before it. -/
def Closed {α β ι : Type} (v : α → β) (T : ι → α → α) : Prop :=
  ∃ h : ι → β → β, ∀ i s, v (T i s) = h i (v s)

/-- Two states with one view whose images under one step have different views. -/
def WitnessPair {α β ι : Type} (v : α → β) (T : ι → α → α) : Prop :=
  ∃ i s1 s2, v s1 = v s2 ∧ v (T i s1) ≠ v (T i s2)

/-- The normal form of failure: a view is closed exactly when it has no witness pair. -/
theorem closed_iff_no_witness_pair {α β ι : Type} (v : α → β) (T : ι → α → α) :
    Closed v T ↔ ¬ WitnessPair v T := by
  constructor
  · intro ⟨h, hh⟩ ⟨i, s1, s2, e, ne⟩
    exact ne (by rw [hh, hh, e])
  · intro hn
    refine ⟨fun i y => @dite _ (∃ s, v s = y) (Classical.propDecidable _)
      (fun hy => v (T i (Classical.choose hy))) (fun _ => y), ?_⟩
    intro i s
    have hy : ∃ s', v s' = v s := ⟨s, rfl⟩
    show v (T i s) = @dite _ (∃ s', v s' = v s) (Classical.propDecidable _)
      (fun hy => v (T i (Classical.choose hy))) (fun _ => v s)
    rw [dif_pos hy]
    exact Classical.byContradiction fun hne =>
      hn ⟨i, s, Classical.choose hy, (Classical.choose_spec hy).symm, hne⟩

variable {Row : Type}

/-- The step of an admissible extension: add the rows of `X`. -/
def addRows (X H : Row → Prop) : Row → Prop := fun r => H r ∨ X r

/-- (1) The full view: the rows held and any answer computed from them. It is closed under every
    admissible extension: the incremental fold equals the fold over the union. -/
theorem full_view_closed {β : Type} (F : (Row → Prop) → β) :
    Closed (fun H : Row → Prop => (H, F H)) (fun X H => addRows X H) :=
  ⟨fun X p => (addRows X p.1, F (addRows X p.1)), fun _ _ => rfl⟩

end Closure

section Pruned

variable {Row K : Type} [DecidableEq K] (parent : Row → Row → Prop)
variable (sig : Row → K → Prop) (isCutOf isAck : Row → Prop) (act : Row)
variable (M : List K) (q : Nat)

/-- The pruned view: whether `act` is blocked, and the rows only while it is not. A blocked act
    keeps no row at all, only the fact (with its acknowledgements, if they are to be shown). -/
def prunedView (H : Row → Prop) : Prop × (Row → Prop) :=
  (blocked parent sig isCutOf isAck act M q H,
   fun r => ¬ blocked parent sig isCutOf isAck act M q H ∧ H r)

omit [DecidableEq K] in
/-- (2) The pruned view is closed under every admissible extension. -/
theorem pruned_view_closed :
    Closed (prunedView parent sig isCutOf isAck act M q) (fun X H => addRows X H) := by
  refine ⟨fun X p => (p.1 ∨ blocked parent sig isCutOf isAck act M q (addRows X p.2),
    fun r => ¬ (p.1 ∨ blocked parent sig isCutOf isAck act M q (addRows X p.2)) ∧
      addRows X p.2 r), ?_⟩
  intro X H
  have hR : ¬ blocked parent sig isCutOf isAck act M q H →
      ∀ r, addRows X (fun r => ¬ blocked parent sig isCutOf isAck act M q H ∧ H r) r ↔
        addRows X H r :=
    fun hn r => ⟨fun h => h.elim (fun h => Or.inl h.2) Or.inr,
      fun h => h.elim (fun h => Or.inl ⟨hn, h⟩) Or.inr⟩
  have key : blocked parent sig isCutOf isAck act M q (addRows X H) ↔
      (blocked parent sig isCutOf isAck act M q H ∨
        blocked parent sig isCutOf isAck act M q
          (addRows X (fun r => ¬ blocked parent sig isCutOf isAck act M q H ∧ H r))) := by
    constructor
    · intro hb
      by_cases h0 : blocked parent sig isCutOf isAck act M q H
      · exact Or.inl h0
      · exact Or.inr (blocked_mono parent sig isCutOf isAck act M q _ _
          (fun r h => (hR h0 r).2 h) hb)
    · intro h
      cases h with
      | inl h => exact blocked_mono parent sig isCutOf isAck act M q _ _ (fun _ h' => Or.inl h') h
      | inr h =>
        exact blocked_mono parent sig isCutOf isAck act M q _ _
          (fun _ h' => h'.elim (fun h'' => Or.inl h''.2) Or.inr) h
  show (_, _) = (_, _)
  rw [propext key]
  congr 1
  funext r
  apply propext
  constructor
  · intro ⟨hn, h⟩
    exact ⟨hn, (hR (fun h0 => hn (Or.inl h0)) r).2 h⟩
  · intro ⟨hn, h⟩
    exact ⟨hn, (hR (fun h0 => hn (Or.inl h0)) r).1 h⟩

/-- And the answer is read off the pruned view: a blocked act counts in every extension, and
    otherwise the view holds every row. -/
theorem pruned_view_answers (hack : ∀ A, isAck A → TransGen parent act A) (H : Row → Prop) :
    (blocked parent sig isCutOf isAck act M q H →
      ∀ H', Extends H H' → countsA parent sig isCutOf isAck act M q H') ∧
    (¬ blocked parent sig isCutOf isAck act M q H →
      ∀ r, (prunedView parent sig isCutOf isAck act M q H).2 r ↔ H r) :=
  ⟨fun ⟨ha, Bl, hB, hBl, hq⟩ =>
    ack_counts_future_stable parent sig isCutOf isAck act M q hack H ha Bl hB hBl hq,
   fun hn _ => ⟨fun h => h.2, fun h => ⟨hn, h⟩⟩⟩

end Pruned

/-! ## Part 11. Incremental fold, checkpoint, read-sets -/

section Incremental

variable {Row : Type} (parent : Row → Row → Prop) (wf : WellFounded parent)
variable (wellFormed : Row → Prop) (judge : Row → (Row → Prop) → (Row → Prop) → Prop)

/-- A row kept in `S` is kept in any set that holds its past. -/
theorem kept_sub (S S' : Row → Prop) (r : Row) (hk : kept parent wf wellFormed S r)
    (h : ∀ q, (q = r ∨ TransGen parent q r) → S' q) : kept parent wf wellFormed S' r := by
  induction r using WellFounded.induction wf with | _ r ih => ?_
  have ⟨a, b, c⟩ := (kept_iff parent wf wellFormed S r).1 hk
  exact (kept_iff parent wf wellFormed S' r).2 ⟨h r (Or.inl rfl), b, fun p hp =>
    ih p hp (c p hp) (fun q hq => h q (Or.inr (hq.elim (fun e => e ▸ TransGen.single hp)
      (fun hqp => TransGen.tail hqp hp))))⟩

/-- 6a, with concurrent reads. Under any admissible extension the conclusion about a kept row is
    unchanged unless a newly kept row is in concurrent conflict with it or with an ancestor:
    its read-set. A node recomputes exactly the rows whose read-set the extension touches. -/
theorem concl_ext_local (conflict : Row → Row → Prop)
    (hC : ∀ r P (C C' : Row → Prop), (∀ y, conflict y r → (C y ↔ C' y)) →
      (judge r P C ↔ judge r P C'))
    (root S S' : Row → Prop) (h : Extends S S') (r : Row)
    (hk : kept parent wf wellFormed S r)
    (hfar : ∀ q, (q = r ∨ TransGen parent q r) → ∀ y, kept parent wf wellFormed S' y →
      ¬ kept parent wf wellFormed S y → conflict y q → ¬ conc parent y q) :
    concl parent wf judge wellFormed root S r ↔ concl parent wf judge wellFormed root S' r := by
  unfold concl
  apply conclOf_local parent wf judge conflict hC
    (Live parent wf wellFormed root S) (Live parent wf wellFormed root S')
    (fun q => kept parent wf wellFormed S' q ∧ ¬ kept parent wf wellFormed S q)
  · intro q hq
    constructor
    · intro ⟨a, b⟩
      exact ⟨kept_mono parent wf wellFormed S S' h q a, b⟩
    · intro ⟨a, b⟩
      exact ⟨Classical.byContradiction fun hn => hq ⟨a, hn⟩, b⟩
  · intro q hq
    refine ⟨fun ⟨_, hn⟩ => hn ?_, fun y ⟨h1, h2⟩ hc => hfar q hq y h1 h2 hc⟩
    cases hq with
    | inl e => exact e ▸ hk
    | inr hqr => exact kept_ancestors parent wf wellFormed S q r hqr hk

/-- 6a for a derived answer reading the conclusions of its parties `T` only. -/
theorem derived_ext_local (conflict : Row → Row → Prop)
    (hC : ∀ r P (C C' : Row → Prop), (∀ y, conflict y r → (C y ↔ C' y)) →
      (judge r P C ↔ judge r P C'))
    (root S S' : Row → Prop) (h : Extends S S')
    (D : (Row → Prop) → Prop) (T : Row → Prop)
    (hD : ∀ A B : Row → Prop, (∀ r, T r → (A r ↔ B r)) → (D A ↔ D B))
    (hT : ∀ r, T r → kept parent wf wellFormed S r ∧
      ∀ q, (q = r ∨ TransGen parent q r) → ∀ y, kept parent wf wellFormed S' y →
        ¬ kept parent wf wellFormed S y → conflict y q → ¬ conc parent y q) :
    D (concl parent wf judge wellFormed root S) ↔ D (concl parent wf judge wellFormed root S') :=
  hD _ _ (fun r hr => concl_ext_local parent wf wellFormed judge conflict hC root S S' h r
    (hT r hr).1 (hT r hr).2)

/-- The rows at or beneath a checkpoint row `k`: the heads it names and their past. -/
def beneath (k : Row) : Row → Prop := fun q => q = k ∨ TransGen parent q k

/-- 6b. A checkpoint is the node's own row `k` naming the heads it held. Every held set is the
    rows beneath `k` and the rest, so any answer is the same over both. -/
theorem checkpoint_resume {β : Type} (S : Row → Prop) (k : Row)
    (hk : kept parent wf wellFormed S k) (F : (Row → Prop) → β) :
    F S = F (fun r => beneath parent k r ∨ (S r ∧ ¬ beneath parent k r)) := by
  congr 1
  funext r
  apply propext
  constructor
  · intro h
    by_cases hb : beneath parent k r
    · exact Or.inl hb
    · exact Or.inr ⟨h, hb⟩
  · intro h
    cases h with
    | inl hb =>
      cases hb with
      | inl e => exact e ▸ kept_offered parent wf wellFormed S k hk
      | inr ht => exact past_fixed parent wf wellFormed S r k hk ht
    | inr h => exact h.1

/-- 6b. The conclusions the checkpoint stores for rows beneath it, folded over those rows alone,
    are the conclusions over every later set, for a rule that reads no concurrent row. -/
theorem checkpoint_conclusions (hC0 : ∀ r P (C C' : Row → Prop), judge r P C ↔ judge r P C')
    (root S : Row → Prop) (k : Row) (hk : kept parent wf wellFormed S k) (r : Row)
    (hr : beneath parent k r) :
    concl parent wf judge wellFormed root (beneath parent k) r ↔
      concl parent wf judge wellFormed root S r := by
  have hkr : kept parent wf wellFormed S r := hr.elim (fun e => e ▸ hk)
    (fun ht => kept_ancestors parent wf wellFormed S r k ht hk)
  have hsub : kept parent wf wellFormed (beneath parent k) r :=
    kept_sub parent wf wellFormed S _ r hkr (fun q hq => hq.elim (fun e => e ▸ hr)
      (fun hqr => Or.inr (hr.elim (fun e => e ▸ hqr) (fun hrk => anc_trans hqr hrk))))
  exact concl_ext parent wf wellFormed judge hC0 root _ S
    (fun q hq => hq.elim (fun e => e ▸ kept_offered parent wf wellFormed S k hk)
      (fun ht => past_fixed parent wf wellFormed S q k hk ht)) r hsub

end Incremental

/-! ## Instances for Parts 9 and 10, on seven rows and five keys

  `g` a head; `a` the act, naming `g`. `c` a cut of `a` naming `g`, signed by k1, k4, k5.
  `A1` k1's clean acknowledgement of `a` (concurrent with `c`: k1's fork). `U` k1's
  acknowledgement naming `a` and `c` (k1's vote is in its past: not clean). `A2`, `A3` clean
  acknowledgements by k2 and k3. Members at `a`'s head: k1 … k5; the count three. -/

namespace Rows2

inductive Key | k1 | k2 | k3 | k4 | k5
  deriving DecidableEq, Repr

inductive R | g | a | c | A1 | U | A2 | A3
  deriving DecidableEq, Repr

open R Key

def parentB : R → R → Bool
  | g, a => true | g, c => true | a, A1 => true | a, U => true | c, U => true
  | a, A2 => true | a, A3 => true
  | _, _ => false
def parent (p q : R) : Prop := parentB p q = true

def ancB : R → R → Bool
  | g, a => true | g, c => true | g, A1 => true | g, U => true | g, A2 => true | g, A3 => true
  | a, A1 => true | a, U => true | a, A2 => true | a, A3 => true | c, U => true
  | _, _ => false

theorem par_anc : ∀ p q, parentB p q = true → ancB p q = true := by
  intro p q; cases p <;> cases q <;> decide
theorem anc_step : ∀ p b d, ancB p b = true → parentB b d = true → ancB p d = true := by
  intro p b d; cases p <;> cases b <;> cases d <;> decide
theorem anc_sound {p q : R} (hpq : TransGen parent p q) : ancB p q = true := by
  induction hpq with
  | single hp => exact par_anc _ _ hp
  | tail _ hp ih => exact anc_step _ _ _ ih hp

def sigB : R → Key → Bool
  | c, k1 => true | c, k4 => true | c, k5 => true
  | A1, k1 => true | U, k1 => true | A2, k2 => true | A3, k3 => true
  | _, _ => false
def sig (r : R) (k : Key) : Prop := sigB r k = true
def isCutOf (r : R) : Prop := r = c
def isAck (r : R) : Prop := r = A1 ∨ r = U ∨ r = A2 ∨ r = A3
def M : List Key := [k1, k2, k3, k4, k5]

theorem hack : ∀ A, isAck A → TransGen parent a A := by
  intro A h
  rcases h with h | h | h | h <;> subst h <;> exact TransGen.single rfl

abbrev Voids (H : R → Prop) (x : R) : Prop := voids parent sig isCutOf isAck a M 3 H x
abbrev CountsA (H : R → Prop) : Prop := countsA parent sig isCutOf isAck a M 3 H
abbrev Clean (A : R) (k : Key) : Prop := clean parent sig isCutOf isAck A k

theorem not_anc (p q : R) (h : ancB p q = false) : ¬ TransGen parent p q :=
  fun ht => by have := anc_sound ht; rw [h] at this; exact Bool.false_ne_true this

theorem conc_ca : conc parent c a := ⟨not_anc c a rfl, not_anc a c rfl, by decide⟩

theorem clean_of (A : R) (k : Key) (hA : isAck A) (hs : sig A k) (hk : sigB c k = false ∨ ancB c A = false)
    (hne : A ≠ c) : Clean A k := by
  refine ⟨hA, hs, fun ⟨x, hx, hcx, hsx⟩ => ?_⟩
  have e : x = c := hcx
  subst e
  rcases hx with hx | hx
  · exact hne hx.symm
  · rcases hk with hk | hk
    · simp [sig, hk] at hsx
    · exact not_anc c A hk hx

theorem clean_A1 : Clean A1 k1 := clean_of A1 k1 (Or.inl rfl) rfl (Or.inr rfl) (by decide)
theorem clean_A2 : Clean A2 k2 := clean_of A2 k2 (Or.inr (Or.inr (Or.inl rfl))) rfl (Or.inl rfl) (by decide)
theorem clean_A3 : Clean A3 k3 := clean_of A3 k3 (Or.inr (Or.inr (Or.inr rfl))) rfl (Or.inl rfl) (by decide)
theorem not_clean_U : ¬ Clean U k1 := fun h => h.2.2 ⟨c, Or.inr (TransGen.single rfl), rfl, rfl⟩

/-- The cut `c` voids `a` at `H` when no acknowledgement held forks any of its signers. -/
theorem voids_of (H : R → Prop) (hno : ∀ A, H A → isAck A → A = U ∨ A = A2 ∨ A = A3) :
    Voids H c := by
  refine ⟨rfl, conc_ca, [k1, k4, k5], by decide, ?_, Nat.le_refl 3⟩
  intro k hk
  refine ⟨by simp [M] at hk ⊢; rcases hk with h | h | h <;> simp [h], ?_, ?_⟩
  · simp at hk; rcases hk with h | h | h <;> subst h <;> rfl
  · intro ⟨A, hA, hcl, _⟩
    rcases hno A hA hcl.1 with e | e | e <;> subst e
    · exact not_clean_U (by
        have : k = k1 := by
          have := hcl.2.1; simp at hk
          rcases hk with h | h | h <;> subst h <;> simp_all [sig, sigB]
        exact this ▸ hcl)
    · have := hcl.2.1; simp at hk; rcases hk with h | h | h <;> subst h <;> simp [sig, sigB] at this
    · have := hcl.2.1; simp at hk; rcases hk with h | h | h <;> subst h <;> simp [sig, sigB] at this

/-- With k1's clean acknowledgement held, the counted signers of `c` are among k4 and k5. -/
theorem no_void_with_A1 (H : R → Prop) (hA1 : H A1) : ¬ Voids H c := by
  intro ⟨_, _, V, hV, hVs, hq⟩
  have hsub : ∀ k, k ∈ V → k ∈ [k4, k5] := by
    intro k hk
    have ⟨_, hs, hnf⟩ := hVs k hk
    cases k with
    | k1 => exact absurd ⟨A1, hA1, clean_A1, ⟨not_anc A1 c rfl, not_anc c A1 rfl, by decide⟩⟩ hnf
    | k2 => simp [sig, sigB] at hs
    | k3 => simp [sig, sigB] at hs
    | k4 => simp
    | k5 => simp
  have := nodup_subset_length V [k4, k5] hV hsub
  simp at this
  omega

def G0b : R → Bool | g => true | a => true | _ => false
def H1b : R → Bool | g => true | a => true | c => true | _ => false
def H2b : R → Bool | g => true | a => true | c => true | A1 => true | _ => false
def H3b : R → Bool | g => true | a => true | c => true | U => true | A2 => true | A3 => true | _ => false
def G1b : R → Bool | g => true | a => true | A1 => true | _ => false
def G2b : R → Bool | g => true | a => true | A1 => true | A2 => true | A3 => true | _ => false
abbrev G0 (r : R) : Prop := G0b r = true
abbrev H1 (r : R) : Prop := H1b r = true
abbrev H2 (r : R) : Prop := H2b r = true
abbrev H3 (r : R) : Prop := H3b r = true
abbrev G1 (r : R) : Prop := G1b r = true
abbrev G2 (r : R) : Prop := G2b r = true

/-- Test (2), the fork seen in both orders. A reader holding the cut and not k1's acknowledgement
    sees the count met; once the acknowledgement is held, the cut is recounted and falls, with
    the members unchanged. -/
theorem fork_recount_falls : Voids H1 c ∧ ¬ Voids H2 c :=
  ⟨voids_of H1 (fun A hA hk => by
      rcases hk with h | h | h | h <;> subst h <;> simp [H1, H1b] at hA),
   no_void_with_A1 H2 rfl⟩

/-- Test (1). k1, k2, k3 acknowledge cleanly; k1 forks a concurrent cut, which k4 and k5 sign:
    every voice that has not acknowledged signs it. The cut fails in every extension; the
    count is still three of five. -/
theorem acknowledged_fork_fails :
    ∀ H', Extends G2 H' → ¬ Voids H' c :=
  fun H' h => ack_finality_future_stable parent sig isCutOf isAck a M 3 hack G2 H' h
    [k1, k2, k3] (by decide)
    (fun k hk => by
      simp at hk
      rcases hk with e | e | e <;> subst e
      · exact ⟨by simp [M], A1, rfl, clean_A1⟩
      · exact ⟨by simp [M], A2, rfl, clean_A2⟩
      · exact ⟨by simp [M], A3, rfl, clean_A3⟩)
    (by decide) c

/-- Test (2), the unclean order. k1 signs the cut, then acknowledges naming it. Counted with any
    acknowledgement, k1, k2 and k3 would be three of five; the cut still voids `a`, as the
    count once met must. Only clean acknowledgements block. -/
theorem unclean_ack_does_not_block :
    (∀ k, k ∈ [k1, k2, k3] → ∃ A, H3 A ∧ isAck A ∧ sig A k) ∧ M.length < 3 + 3 ∧
      ¬ Clean U k1 ∧ Voids H3 c := by
  refine ⟨fun k hk => ?_, by decide, not_clean_U, voids_of H3 (fun A hA hk => ?_)⟩
  · simp at hk
    rcases hk with e | e | e <;> subst e
    · exact ⟨U, rfl, Or.inr (Or.inl rfl), rfl⟩
    · exact ⟨A2, rfl, Or.inr (Or.inr (Or.inl rfl)), rfl⟩
    · exact ⟨A3, rfl, Or.inr (Or.inr (Or.inr rfl)), rfl⟩
  · rcases hk with h | h | h | h <;> subst h <;> simp_all [H3, H3b]

theorem extends_H1 : Extends G0 H1 := by intro q hq; cases q <;> simp_all [G0, G0b, H1, H1b]
theorem extends_H2 : Extends G1 H2 := by intro q hq; cases q <;> simp_all [G1, G1b, H2, H2b]

theorem countsA_of (H : R → Prop) (ha : H a) (hnc : ¬ H c ∨ ¬ Voids H c) : CountsA H := by
  refine ⟨ha, fun ⟨x, hx, hv⟩ => ?_⟩
  have e : x = c := hv.1
  subst e
  exact hnc.elim (fun h => h hx) (fun h => h hv)

/-- The pruning rule's necessity, as a witness pair. The view "`a` counts" with the rows dropped
    gives `G0` and `G1` the same value; both are unsettled (one clean acknowledgement of the
    three needed). Adding the cut `c` voids `a` over `G0` and not over `G1`. So a checkpoint of
    an unsettled act must keep the acknowledgements a cut would be recounted against. -/
theorem unsettled_drop_has_witness_pair :
    CountsA G0 ∧ CountsA G1 ∧ ¬ CountsA H1 ∧ CountsA H2 ∧
      WitnessPair (fun H : R → Prop => CountsA H) (fun (_ : Unit) H => addRows (fun r => r = c) H) := by
  have hc0 : CountsA G0 := countsA_of G0 rfl (Or.inl (by simp [G0, G0b]))
  have hc1 : CountsA G1 := countsA_of G1 rfl (Or.inl (by simp [G1, G1b]))
  have hn1 : ¬ CountsA H1 := fun h => h.2 ⟨c, rfl, fork_recount_falls.1⟩
  have hc2 : CountsA H2 := countsA_of H2 rfl (Or.inr fork_recount_falls.2)
  have e0 : addRows (fun r => r = c) G0 = H1 := by
    funext r; apply propext; cases r <;> simp [addRows, G0, G0b, H1, H1b]
  have e1 : addRows (fun r => r = c) G1 = H2 := by
    funext r; apply propext; cases r <;> simp [addRows, G1, G1b, H2, H2b]
  refine ⟨hc0, hc1, hn1, hc2, (), G0, G1, propext ⟨fun _ => hc1, fun _ => hc0⟩, ?_⟩
  show CountsA (addRows _ G0) ≠ CountsA (addRows _ G1)
  rw [e0, e1]
  intro e
  exact hn1 (e ▸ hc2)

/-- So the view "`a` counts" over histories is not closed: a node may not drop the rows of an
    unsettled act and keep only its answer. -/
theorem count_view_not_closed :
    ¬ Closed (fun H : R → Prop => CountsA H) (fun (_ : Unit) H => addRows (fun r => r = c) H) :=
  fun h => (closed_iff_no_witness_pair _ _).1 h unsettled_drop_has_witness_pair.2.2.2.2

/-- Case (iii) is not derived. Read as the kernel states a count, from the signatures the cut
    row carries (`Consent.count_is_final_against_members`), k1's concurrent clean
    acknowledgement changes nothing: the cut voids `a` at `H2`, where it does not under the fork
    rule. That rule is what `voids` adds. -/
theorem fork_stands_on_row_count :
    voids parent sig isCutOf (fun _ => False) a M 3 H2 c ∧ ¬ Voids H2 c := by
  refine ⟨⟨rfl, conc_ca, [k1, k4, k5], by decide, fun k hk => ⟨?_, ?_, fun ⟨_, _, hcl, _⟩ => hcl.1⟩,
    Nat.le_refl 3⟩, no_void_with_A1 H2 rfl⟩
  · simp at hk; simp [M]; rcases hk with h | h | h <;> simp [h]
  · simp at hk; rcases hk with h | h | h <;> subst h <;> rfl

end Rows2

/-! ## Part 12. Answers indexed by head, and one say for each voice

  `rowCounts` (Seat.lean) gives one answer for a row, for ever, while the cut's entitlement is
  read at the head the cut names. That conflates two answers. Here they are apart:
    countsAt S x   the act `E` counts at head `x`: no cut count is met there;
    carriedTo S x1 `E` still counts at every head from the head `E` names up to `x1`.
  A cut naming a later head changes `carriedTo` there, which is moderating forward, and leaves
  `countsAt` at `E`'s head as it was. Within one head a voice has one say on the slot: it votes
  to cut (a cut row concurrent with `E`), it acknowledges `E`, both, or neither. A voice that
  has said both has no say there, as CC 3.1.3.2 states for replies; it stays among the members
  the count is over. A row with `E` in its past is not a vote against `E` ("rows in its past
  stand"). Cuts naming a head older than `x` are not read: for a reader that acknowledged `x`
  they are void (`Reader.line_voids_old_fork`), and otherwise they are the fork on a past head
  that KERNEL.md 8a lists. -/

section Heads

variable {Row K : Type} [DecidableEq K] (parent : Row → Row → Prop) (headOf : Row → Row)
variable (sig : Row → K → Prop) (isCutOf isAck : Row → Prop) (E : Row)
variable (mem : Row → List K) (t : Nat)

/-- `k` acknowledged `E` by a row naming head `x`. -/
def ackedAt (S : Row → Prop) (x : Row) (k : K) : Prop :=
  ∃ A, S A ∧ isAck A ∧ sig A k ∧ headOf A = x

/-- `k` signed a cut on `E`'s slot naming head `x`, concurrent with `E`. -/
def cutVotedAt (S : Row → Prop) (x : Row) (k : K) : Prop :=
  ∃ c, S c ∧ isCutOf c ∧ sig c k ∧ headOf c = x ∧ conc parent c E

/-- The say rule: `k` says cut at `x` when it voted to cut and did not acknowledge there. -/
def yesAt (S : Row → Prop) (x : Row) (k : K) : Prop :=
  cutVotedAt parent headOf sig isCutOf E S x k ∧ ¬ ackedAt headOf sig isAck S x k

/-- The cut count at head `x`, over the members at `x`. -/
def cutMetAt (S : Row → Prop) (x : Row) : Prop :=
  ∃ V : List K, V.Nodup ∧
    (∀ k, k ∈ V → k ∈ mem x ∧ yesAt parent headOf sig isCutOf isAck E S x k) ∧ t ≤ V.length

def countsAt (S : Row → Prop) (x : Row) : Prop :=
  S E ∧ ¬ cutMetAt parent headOf sig isCutOf isAck E mem t S x

/-- `E` is carried to `x1`: it counts at every head from the one it names up to `x1`. -/
def carriedTo (S : Row → Prop) (x1 : Row) : Prop :=
  S E ∧ ∀ x, (x = x1 ∨ TransGen parent x x1) → (x = headOf E ∨ TransGen parent (headOf E) x) →
    ¬ cutMetAt parent headOf sig isCutOf isAck E mem t S x

omit [DecidableEq K] in
/-- Whether `E` counts at `x` reads only the rows naming `x` (and `E` itself). -/
theorem countsAt_local (S S' : Row → Prop) (x : Row)
    (hagree : ∀ r, headOf r = x → (S r ↔ S' r)) (hE : S E ↔ S' E) :
    countsAt parent headOf sig isCutOf isAck E mem t S x ↔
      countsAt parent headOf sig isCutOf isAck E mem t S' x := by
  have hack : ∀ k, ackedAt headOf sig isAck S x k ↔ ackedAt headOf sig isAck S' x k :=
    fun k => ⟨fun ⟨A, h1, h2, h3, h4⟩ => ⟨A, (hagree A h4).1 h1, h2, h3, h4⟩,
      fun ⟨A, h1, h2, h3, h4⟩ => ⟨A, (hagree A h4).2 h1, h2, h3, h4⟩⟩
  have hcut : ∀ k, cutVotedAt parent headOf sig isCutOf E S x k ↔
      cutVotedAt parent headOf sig isCutOf E S' x k :=
    fun k => ⟨fun ⟨c, h1, h2, h3, h4, h5⟩ => ⟨c, (hagree c h4).1 h1, h2, h3, h4, h5⟩,
      fun ⟨c, h1, h2, h3, h4, h5⟩ => ⟨c, (hagree c h4).2 h1, h2, h3, h4, h5⟩⟩
  have hyes : ∀ k, yesAt parent headOf sig isCutOf isAck E S x k ↔
      yesAt parent headOf sig isCutOf isAck E S' x k :=
    fun k => ⟨fun ⟨a, b⟩ => ⟨(hcut k).1 a, fun h => b ((hack k).2 h)⟩,
      fun ⟨a, b⟩ => ⟨(hcut k).2 a, fun h => b ((hack k).1 h)⟩⟩
  have hmet : cutMetAt parent headOf sig isCutOf isAck E mem t S x ↔
      cutMetAt parent headOf sig isCutOf isAck E mem t S' x :=
    ⟨fun ⟨V, a, b, c⟩ => ⟨V, a, fun k hk => ⟨(b k hk).1, (hyes k).1 (b k hk).2⟩, c⟩,
     fun ⟨V, a, b, c⟩ => ⟨V, a, fun k hk => ⟨(b k hk).1, (hyes k).2 (b k hk).2⟩, c⟩⟩
  exact ⟨fun ⟨a, b⟩ => ⟨hE.1 a, fun h => b (hmet.2 h)⟩,
    fun ⟨a, b⟩ => ⟨hE.2 a, fun h => b (hmet.1 h)⟩⟩

omit [DecidableEq K] in
/-- Rows naming any other head, a later one included, never change whether `E` counts at `x`:
    a voice seated later acts at its own head, forward. -/
theorem later_head_changes_nothing (S X : Row → Prop) (x : Row)
    (hX : ∀ r, X r → headOf r ≠ x) (hE : ¬ X E ∨ S E) :
    countsAt parent headOf sig isCutOf isAck E mem t S x ↔
      countsAt parent headOf sig isCutOf isAck E mem t (addRows X S) x :=
  countsAt_local parent headOf sig isCutOf isAck E mem t _ _ x
    (fun r hr => ⟨Or.inl, fun h => h.elim id (fun hx => absurd hr (hX r hx))⟩)
    ⟨Or.inl, fun h => h.elim id (fun hx => hE.elim (fun n => absurd hx n) id)⟩

omit [DecidableEq K] in
/-- Carried to a later head implies counting at the act's own head; not conversely. -/
theorem carried_to_head (S : Row → Prop) (x1 : Row)
    (hle : headOf E = x1 ∨ TransGen parent (headOf E) x1)
    (h : carriedTo parent headOf sig isCutOf isAck E mem t S x1) :
    countsAt parent headOf sig isCutOf isAck E mem t S (headOf E) :=
  ⟨h.1, h.2 (headOf E) hle (Or.inl rfl)⟩

omit [DecidableEq K] in
/-- A voice that has acknowledged at `x` never says cut at `x` again, whatever it signs. -/
theorem ack_never_yes (S S' : Row → Prop) (h : Extends S S') (x : Row) (k : K)
    (ha : ackedAt headOf sig isAck S x k) :
    ¬ yesAt parent headOf sig isCutOf isAck E S' x k :=
  fun ⟨_, hn⟩ => let ⟨A, h1, h2, h3, h4⟩ := ha; hn ⟨A, h A h1, h2, h3, h4⟩

/-- Settled at a head, under the say rule. Acknowledgements at `x` by a list `Bl` of members
    with `n < t + |Bl|`, any acknowledgements, clean or not: no cut count is met at `x` in any
    extension. The members stay `mem x`; a voice that said both stays among them. -/
theorem say_settled_final (S : Row → Prop) (x : Row) (Bl : List K) (hB : Bl.Nodup)
    (hBl : ∀ k, k ∈ Bl → k ∈ mem x ∧ ackedAt headOf sig isAck S x k)
    (hq : (mem x).length < t + Bl.length) :
    ∀ S', Extends S S' → ¬ cutMetAt parent headOf sig isCutOf isAck E mem t S' x := by
  intro S' hS ⟨V, hV, hVs, htV⟩
  have hd : ∀ k, k ∈ V → ¬ k ∈ Bl := fun k hkV hkB =>
    ack_never_yes parent headOf sig isCutOf isAck E S S' hS x k (hBl k hkB).2 (hVs k hkV).2
  have := disjoint_length V Bl (mem x) hV hB (fun k hk => (hVs k hk).1)
    (fun k hk => (hBl k hk).1) hd
  omega

theorem countsAt_final (S : Row → Prop) (x : Row) (hE : S E) (Bl : List K) (hB : Bl.Nodup)
    (hBl : ∀ k, k ∈ Bl → k ∈ mem x ∧ ackedAt headOf sig isAck S x k)
    (hq : (mem x).length < t + Bl.length) :
    ∀ S', Extends S S' → countsAt parent headOf sig isCutOf isAck E mem t S' x :=
  fun S' hS => ⟨hS E hE, say_settled_final parent headOf sig isCutOf isAck E mem t S x Bl hB hBl hq S' hS⟩

omit [DecidableEq K] in
/-- Necessity: members that have not acknowledged at `x` and have voted to cut there meet the
    count when they are `t` or more. -/
theorem say_unblocked_can_cut (S : Row → Prop) (x : Row) (V : List K) (hV : V.Nodup)
    (hVs : ∀ k, k ∈ V → k ∈ mem x ∧ cutVotedAt parent headOf sig isCutOf E S x k ∧
      ¬ ackedAt headOf sig isAck S x k) (ht : t ≤ V.length) :
    cutMetAt parent headOf sig isCutOf isAck E mem t S x :=
  ⟨V, hV, fun k hk => ⟨(hVs k hk).1, (hVs k hk).2.1, (hVs k hk).2.2⟩, ht⟩

/-- A sole cutter that forks: it acknowledged at `x` and signed a concurrent cut; it has no say
    and `E` counts at `x` in every extension. -/
theorem sole_cutter_fork_stands (S : Row → Prop) (x : Row) (v : K) (hE : S E)
    (hmem : mem x = [v]) (ht : t = 1) (ha : ackedAt headOf sig isAck S x v) :
    ∀ S', Extends S S' → countsAt parent headOf sig isCutOf isAck E mem t S' x :=
  countsAt_final parent headOf sig isCutOf isAck E mem t S x hE [v] (List.nodup_cons.2 ⟨List.not_mem_nil v, List.nodup_nil⟩)
    (fun k hk => by
      rw [List.mem_singleton] at hk
      subst hk
      exact ⟨by rw [hmem]; exact List.mem_singleton_self _, ha⟩)
    (by rw [hmem, ht]; simp)

end Heads

/-! ### Why one say: closure and symmetry

  A voice's rows on a slot at a head, seen as two facts: it has acknowledged, it has voted to
  cut. A step adds one row of the voice. Four ways to read its say. -/

section SayClosure

inductive Say | silent | yes | no | both
  deriving DecidableEq, Repr

/-- (b) The say rule, keeping "said both" apart from "said nothing". -/
def say4 : Bool × Bool → Say
  | (false, false) => .silent | (false, true) => .yes | (true, false) => .no | (true, true) => .both

/-- (b) with "said both" and "said nothing" merged into one "no say". -/
def say3 : Bool × Bool → Say
  | (false, true) => .yes | (true, false) => .no | _ => .silent

/-- (a) The cut as `rowCounts` reads it: any cut vote is a cut vote. -/
def sayA : Bool × Bool → Say
  | (_, true) => .yes | (true, false) => .no | (false, false) => .silent

/-- (c) An acknowledgement binds: it wins over the voice's own cut vote. -/
def sayC : Bool × Bool → Say
  | (true, _) => .no | (false, true) => .yes | (false, false) => .silent

/-- A step: `true` adds an acknowledgement, `false` a cut vote. -/
def step : Bool → Bool × Bool → Bool × Bool
  | true, (_, c) => (true, c)
  | false, (a, _) => (a, true)

def swap : Bool × Bool → Bool × Bool | (a, c) => (c, a)
def swapSay : Say → Say | .yes => .no | .no => .yes | s => s

def decode : Say → Bool × Bool
  | .silent => (false, false) | .yes => (false, true) | .no => (true, false) | .both => (true, true)

/-- (b) is closed: the next say is a function of the say. -/
theorem say4_closed : Closed say4 step :=
  ⟨fun i y => say4 (step i (decode y)), by
    intro i s; rcases s with ⟨a, c⟩; cases i <;> cases a <;> cases c <;> rfl⟩

/-- Merging "both" into "silent" is not closed: two voices with no say part when each adds an
    acknowledgement. -/
theorem say3_witness : WitnessPair say3 step :=
  ⟨true, (false, false), (true, true), rfl, by decide⟩

theorem say3_not_closed : ¬ Closed say3 step :=
  fun h => (closed_iff_no_witness_pair say3 step).1 h say3_witness

/-- Under (b), once a voice has acknowledged, it never says cut again. -/
theorem say4_absorbing (i : Bool) (s : Bool × Bool) (h : say4 s = .no ∨ say4 s = .both) :
    say4 (step i s) = .no ∨ say4 (step i s) = .both := by
  revert h; rcases s with ⟨a, c⟩; cases i <;> cases a <;> cases c <;> decide

/-- Under (a) an acknowledgement does not hold: a cut vote after it says cut. -/
theorem sayA_not_safe : sayA (true, false) = .no ∧ sayA (step false (true, false)) = .yes :=
  ⟨rfl, rfl⟩

/-- (b) treats a voice's two opposite rows alike; (c) does not. -/
theorem say4_symmetric : ∀ s, say4 (swap s) = swapSay (say4 s) := by
  intro s; rcases s with ⟨a, c⟩; cases a <;> cases c <;> rfl

theorem sayC_not_symmetric : sayC (swap (true, true)) ≠ swapSay (sayC (true, true)) := by decide

/-- Symmetry forces the rule: any reading that treats the two opposite rows of one voice alike
    gives a voice that has said both neither a cut vote nor an acknowledgement. -/
theorem symmetric_say_forced (f : Bool × Bool → Say)
    (hf : ∀ s, f (swap s) = swapSay (f s)) : f (true, true) ≠ .yes ∧ f (true, true) ≠ .no := by
  have h := hf (true, true)
  have e : swap (true, true) = (true, true) := rfl
  rw [e] at h
  cases hc : f (true, true) with
  | silent => decide
  | both => decide
  | yes => rw [hc] at h; exact absurd h (by decide)
  | no => rw [hc] at h; exact absurd h (by decide)

end SayClosure

/-! ### The earlier instance read by head -/

namespace Rows

/-- The head each row names: `e`, `a`, `x` and `d` name `h`; `w` names `h1`. -/
def headOf : R → R
  | R.h1 => R.h1 | R.w => R.h1 | _ => R.h

def isCutOfH (r : R) : Prop := r = R.x ∨ r = R.d ∨ r = R.w
def isAckH (r : R) : Prop := r = R.a
/-- Members: `V` at `h`; `V` and `W` at `h1`. -/
def memH : R → List Key
  | R.h1 => [Key.V, Key.W] | _ => [Key.V]

abbrev CountsAt (S : R → Prop) (y : R) : Prop :=
  countsAt parent headOf voice isCutOfH isAckH R.e memH 1 S y
abbrev CarriedTo (S : R → Prop) (y : R) : Prop :=
  carriedTo parent headOf voice isCutOfH isAckH R.e memH 1 S y

/-- Later seating, read by head. `W`'s cut changes nothing at `h`, where `e` counts, and `e` is
    not carried to `h1`: moderation forward. Compare `later_seat_defeats_acknowledged`, the
    timeless reading. -/
theorem later_seat_is_forward : CountsAt Sl R.h ∧ ¬ CarriedTo Sl R.h1 := by
  refine ⟨⟨rfl, fun ⟨V, _, hVs, ht⟩ => ?_⟩, fun ⟨_, hc⟩ => ?_⟩
  · cases V with
    | nil => simp at ht
    | cons k _ =>
      have ⟨_, ⟨c, hc, hcut, _, hh, _⟩, _⟩ := hVs k (List.mem_cons_self _ _)
      rcases hcut with e | e | e <;> subst e
      · simp [Sl, Slb] at hc
      · simp [Sl, Slb] at hc
      · simp [headOf] at hh
  · apply hc R.h1 (Or.inl rfl) (Or.inr (TransGen.single rfl))
    refine ⟨[Key.W], by decide, fun k hk => ?_, by decide⟩
    rw [List.mem_singleton] at hk
    subst hk
    refine ⟨by simp [memH], ⟨R.w, rfl, Or.inr (Or.inr rfl), rfl, rfl, conc_we⟩, ?_⟩
    intro ⟨A, _, hA, hs, _⟩
    rw [hA] at hs
    simp [voice, signerOf] at hs

/-- The fork, read by head. `V` acknowledged `e` at `h` and signed a concurrent cut there: it
    has no say, and `e` counts at `h` in every extension. Compare `fork_voids_acknowledged`. -/
theorem fork_has_no_say : ∀ S', Extends Sf S' → CountsAt S' R.h :=
  sole_cutter_fork_stands parent headOf voice isCutOfH isAckH R.e memH 1 Sf R.h Key.V rfl rfl rfl
    ⟨R.a, rfl, rfl, rfl, rfl⟩

/-- The deciding row `d`, a cut by `V` at `h`, names `a` and so has `e` in its past: rows in its
    past stand, so it is no vote against `e` at `h`.
    `e` counts at `h` with `d` held. Compare `overrule_voids_acknowledged`. -/
theorem overrule_is_no_vote : CountsAt So R.h := by
  refine ⟨rfl, fun ⟨V, _, hVs, ht⟩ => ?_⟩
  cases V with
  | nil => simp at ht
  | cons k _ =>
    have ⟨_, ⟨c, hc, hcut, _, _, hconc⟩, _⟩ := hVs k (List.mem_cons_self _ _)
    rcases hcut with e | e | e <;> subst e
    · simp [So, Sob] at hc
    · exact hconc.2.1 e_before_d
    · simp [So, Sob] at hc

end Rows

/-! ## Axioms used -/

#print axioms extends_trans
#print axioms grows_extends
#print axioms past_fixed
#print axioms kept_ext
#print axioms concl_ext
#print axioms concl_grows_ext
#print axioms countsD_none
#print axioms countsD_of_rowCounts
#print axioms poss_candidate
#print axioms counts_final_of_disarmed
#print axioms settled_mono
#print axioms settled_final
#print axioms own_line_not_concurrent
#print axioms unsettled_defeated
#print axioms final_iff_settled
#print axioms body_settled_disarms
#print axioms body_unsettled_majority_free
#print axioms half_disarms_majority
#print axioms count_disarmed
#print axioms three_ways_final
#print axioms Rows.count_not_monotone
#print axioms Rows.fork_voids_acknowledged
#print axioms Rows.overrule_voids_acknowledged
#print axioms Rows.later_seat_defeats_acknowledged
#print axioms Rows.seat_at_head_restores
#print axioms blocking_set_blocks_all_cuts
#print axioms unblocked_coalition_can_cut
#print axioms ack_blocking_quorum
#print axioms five_three
#print axioms ack_cut_three_cases
#print axioms ack_blocks_cut
#print axioms cut_with_ack_is_ancestor
#print axioms ack_finality_future_stable
#print axioms ack_counts_future_stable
#print axioms effect_row_settled
#print axioms blocked_mono
#print axioms closed_iff_no_witness_pair
#print axioms full_view_closed
#print axioms pruned_view_closed
#print axioms pruned_view_answers
#print axioms kept_sub
#print axioms concl_ext_local
#print axioms derived_ext_local
#print axioms checkpoint_resume
#print axioms checkpoint_conclusions
#print axioms Rows2.fork_recount_falls
#print axioms Rows2.acknowledged_fork_fails
#print axioms Rows2.unclean_ack_does_not_block
#print axioms Rows2.unsettled_drop_has_witness_pair
#print axioms Rows2.count_view_not_closed
#print axioms Rows2.fork_stands_on_row_count
#print axioms countsAt_local
#print axioms later_head_changes_nothing
#print axioms carried_to_head
#print axioms ack_never_yes
#print axioms say_settled_final
#print axioms countsAt_final
#print axioms say_unblocked_can_cut
#print axioms sole_cutter_fork_stands
#print axioms say4_closed
#print axioms say3_witness
#print axioms say3_not_closed
#print axioms say4_absorbing
#print axioms sayA_not_safe
#print axioms say4_symmetric
#print axioms sayC_not_symmetric
#print axioms symmetric_say_forced
#print axioms Rows.later_seat_is_forward
#print axioms Rows.fork_has_no_say
#print axioms Rows.overrule_is_no_vote

end Settled

end Kernel
