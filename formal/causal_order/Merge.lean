/-
  Merge.lean — a version naming several heads, counted over the members common to them

  Window.lean Part D counts a version over one head. The rule as it runs
  (formal/roster_fork/fork.py rule M0; KERNEL.md section 7): a version names the heads it
  extends (a list), it is counted over the members COMMON to them, and a merge states its own
  roster. Here

    (a) `common` is that set as a list, `countedCommon` the count over it, and a merge counted
        so that names every tip is the one tip with the roster it states (`merge_counted_one_tip`);
        the common members of the tips are exactly the roster while the tips wait
        (`common_is_waiting_roster`), and every voice of the merge is listed by every tip it
        names (`merge_voices_in_every_tip`);
    (b) two merges of the same heads, each counted by a strict majority of the common
        members, share a signer, a member of every head (`merges_share_signer`): quorum
        intersection over the common list;
    (c) with the built-on clause over the plain cut (Reader.lean, no group checkpoint): a
        merge that names a tip which does not count for the reader is void
        (`merge_on_void_tip_void`, `merge_on_cut_tip_void`), and one whose tips all count, that
        the cut lets count and the reader's line does not leave behind, counts (`merge_counts`).
        A void act anywhere below is `Reader.line_void`.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports Reader.lean.
-/

import Reader

namespace Kernel

namespace Merge

open Order Relation Causal Harden

/-! ## The common members of several heads -/

section Common

variable {V K : Type} [DecidableEq K]
/- `members v`: the roster version `v` states, as a list. `heads v`: the heads `v` names.
   `signed v k`: `k` signed `v` (its own signature or a cosignature naming it). -/
variable (members : V → List K) (heads : V → List V) (signed : V → K → Prop)

/-- The members common to a list of heads. -/
def common : List V → List K
  | [] => []
  | h :: rest => (members h).filter (fun k => rest.all (fun h' => decide (k ∈ members h')))

theorem mem_common (k : K) : ∀ hs : List V,
    k ∈ common members hs ↔ hs ≠ [] ∧ ∀ h, h ∈ hs → k ∈ members h
  | [] => by simp [common]
  | h :: rest => by
    simp only [common, List.mem_filter, List.all_eq_true, decide_eq_true_eq, ne_eq,
      List.mem_cons]
    constructor
    · intro ⟨h1, h2⟩
      exact ⟨List.cons_ne_nil h rest, fun h' hh => hh.elim (fun e => e ▸ h1) (fun m => h2 h' m)⟩
    · intro ⟨_, h2⟩
      exact ⟨h2 h (Or.inl rfl), fun h' m => h2 h' (Or.inr m)⟩

theorem common_nodup (hnd : ∀ v, (members v).Nodup) : ∀ hs : List V, (common members hs).Nodup
  | [] => List.nodup_nil
  | h :: _ => List.Pairwise.filter _ (hnd h)

/-- Counted over the common members: a strict majority of the members common to the heads it
    names signed it. -/
def countedCommon (m : V) : Prop :=
  ∃ a : List K, a.Nodup ∧ (∀ k, k ∈ a → k ∈ common members (heads m) ∧ signed m k) ∧
    (common members (heads m)).length < 2 * a.length

/-- A version named by nothing is the shape `Kernel.tips` reads: `names h v` iff `h` is among
    the heads `v` names. -/
def names (h v : V) : Prop := h ∈ heads v

/-- The roster a version states. -/
def roster (v : V) (k : K) : Prop := k ∈ members v

/-! ### (a) One tip, the roster it states -/

/-- While tips wait, the members common to the heads a version names, when it names exactly
    the tips, are the roster (`Kernel.rosterOf`). -/
theorem common_is_waiting_roster (S : V → Prop) (m : V)
    (hheads : ∀ v, v ∈ heads m ↔ tips (names heads) S v) (hne : heads m ≠ []) (k : K) :
    k ∈ common members (heads m) ↔ rosterOf (names heads) (roster members) S k := by
  rw [mem_common]
  exact ⟨fun h v hv => h.2 v ((hheads v).2 hv), fun h => ⟨hne, fun v hv => h v ((hheads v).1 hv)⟩⟩

/-- Every voice counted for the merge is a member of every head it names. -/
theorem merge_voices_in_every_tip (m : V) (a : List K)
    (ha : ∀ k, k ∈ a → k ∈ common members (heads m) ∧ signed m k) :
    ∀ k, k ∈ a → ∀ h, h ∈ heads m → k ∈ members h :=
  fun k hk h hh => ((mem_common members k (heads m)).1 (ha k hk).1).2 h hh

omit [DecidableEq K] in
/-- (a) A merge that names every tip, once held (its count over the common members is what
    admits it; `countedCommon`), with nothing held naming it, is the one tip, and the roster is
    what it states. -/
theorem merge_counted_one_tip (S : V → Prop) (m : V)
    (hall : ∀ v, tips (names heads) S v → v ∈ heads m)
    (hfresh : ∀ u, (S u ∨ u = m) → ¬ m ∈ heads u) :
    (∀ v, tips (names heads) (fun q => S q ∨ q = m) v ↔ v = m) ∧
      ∀ k, rosterOf (names heads) (roster members) (fun q => S q ∨ q = m) k ↔ k ∈ members m :=
  ⟨merge_one_tip (names heads) S m hall hfresh,
   merge_roster (names heads) (roster members) S m hall hfresh⟩

/-! ### (b) Two merges of the same heads share a signer -/

theorem nil_of_same (l l' : List V) (h : ∀ x, x ∈ l ↔ x ∈ l') (hl : l = []) : l' = [] := by
  cases l' with
  | nil => rfl
  | cons x _ => exact absurd ((h x).2 (List.mem_cons_self _ _)) (by rw [hl]; exact List.not_mem_nil x)

/-- (b) Two versions naming the same heads, each counted by a strict majority of the members
    common to them, share a signer, and that signer is a member of every head they name.
    Nothing is asked about concurrency or about what the two state. -/
theorem merges_share_signer (hnd : ∀ v, (members v).Nodup) (m1 m2 : V)
    (hsame : ∀ h, h ∈ heads m1 ↔ h ∈ heads m2)
    (h1 : countedCommon members heads signed m1) (h2 : countedCommon members heads signed m2) :
    ∃ k, signed m1 k ∧ signed m2 k ∧ ∀ h, h ∈ heads m1 → k ∈ members h := by
  obtain ⟨a, ha, has, hqa⟩ := h1
  obtain ⟨b, hb, hbs, hqb⟩ := h2
  have hmem : ∀ k, k ∈ common members (heads m1) ↔ k ∈ common members (heads m2) := by
    intro k
    rw [mem_common, mem_common]
    constructor
    · intro ⟨hn, hk⟩
      exact ⟨fun e => hn (nil_of_same _ _ (fun x => (hsame x).symm) e),
        fun h hh => hk h ((hsame h).2 hh)⟩
    · intro ⟨hn, hk⟩
      exact ⟨fun e => hn (nil_of_same _ _ hsame e), fun h hh => hk h ((hsame h).1 hh)⟩
  have hlen : (common members (heads m1)).length = (common members (heads m2)).length := by
    have x := nodup_subset_length _ _ (common_nodup members hnd (heads m1)) (fun k hk => (hmem k).1 hk)
    have y := nodup_subset_length _ _ (common_nodup members hnd (heads m2)) (fun k hk => (hmem k).2 hk)
    omega
  obtain ⟨k, hka, hkb⟩ := quorum_intersection a b (common members (heads m1)) ha hb
    (fun k hk => (has k hk).1) (fun k hk => (hmem k).2 (hbs k hk).1) hqa (by rw [hlen]; exact hqb)
  exact ⟨k, (has k hka).2, (hbs k hkb).2,
    merge_voices_in_every_tip members heads signed m1 a has k hka⟩

/-- So if no member common to the heads signs two versions of them, there is one. -/
theorem no_double_signer_one_merge (hnd : ∀ v, (members v).Nodup) (m1 m2 : V)
    (hsame : ∀ h, h ∈ heads m1 ↔ h ∈ heads m2)
    (h1 : countedCommon members heads signed m1) (h2 : countedCommon members heads signed m2)
    (hon : ∀ k, signed m1 k → signed m2 k → m1 = m2) : m1 = m2 :=
  let ⟨k, s1, s2, _⟩ := merges_share_signer members heads signed hnd m1 m2 hsame h1 h2
  hon k s1 s2

end Common

/-! ## (c) The built-on clause, over the plain cut (`Reader.lean`) -/

section BuiltOn

variable {Row : Type}
variable (parent : Row → Row → Prop) (heads : Row → List Row) (isAct : Row → Prop)
variable (mine : Row → Prop) (L : Row → Prop)

/-- The head relation of a version: `r` names `h`. -/
def headOf (r h : Row) : Prop := h ∈ heads r

/-- (c) A MERGE THAT NAMES A VOID TIP IS VOID. `L` is what the plain cut lets count; a merge
    off the reader's line that names a counted act which does not count for the reader does
    not count for it (`Reader.built_on_void`). With `mine` empty this is every reader with no
    acknowledgement. -/
theorem merge_on_void_tip_void (m h : Row) (hm : ¬ mine m) (hh : h ∈ heads m) (ha : isAct h)
    (hv : ¬ Reader.rd parent (headOf heads) isAct mine L h) :
    ¬ Reader.rd parent (headOf heads) isAct mine L m :=
  Reader.built_on_void parent (headOf heads) isAct mine L m h hm hh ha hv

/-- (c) And a merge naming a tip the plain cut does not let count. -/
theorem merge_on_cut_tip_void (m h : Row) (hm : ¬ mine m) (hh : h ∈ heads m) (ha : isAct h)
    (hL : ¬ L h) : ¬ Reader.rd parent (headOf heads) isAct mine L m :=
  Reader.built_on_cut_void parent (headOf heads) isAct mine L m h hm hh ha hL

/-- (c) A merge all of whose named tips count for the reader, which the cut lets count, and
    which is not left behind, counts. -/
theorem merge_counts (m : Row) (hL : L m) (ha : isAct m)
    (htips : ∀ h, h ∈ heads m → isAct h → Reader.rd parent (headOf heads) isAct mine L h)
    (hnb : ¬ Reader.behind parent (headOf heads) isAct mine L m) :
    Reader.rd parent (headOf heads) isAct mine L m :=
  (Reader.rd_iff parent (headOf heads) isAct mine L m).2 ⟨hL, ha, Or.inr ⟨htips, hnb⟩⟩

end BuiltOn

/-- The count of (a) and (b) as the count term of (c): it does not read the voiding set. -/
theorem countedCommon_ent_anti {Row K : Type} [DecidableEq K] (members : Row → List K)
    (heads : Row → List Row) (signed : Row → K → Prop) :
    EntAnti (fun (A _ : Row → Prop) c => A c ∧ countedCommon members heads signed c) :=
  fun _ _ _ _ _ h => h

end Merge

/-! ## Axioms used -/

#print axioms Merge.mem_common
#print axioms Merge.common_nodup
#print axioms Merge.common_is_waiting_roster
#print axioms Merge.merge_voices_in_every_tip
#print axioms Merge.merge_counted_one_tip
#print axioms Merge.merges_share_signer
#print axioms Merge.no_double_signer_one_merge
#print axioms Merge.merge_on_void_tip_void
#print axioms Merge.merge_on_cut_tip_void
#print axioms Merge.merge_counts
#print axioms Merge.countedCommon_ent_anti

end Kernel
