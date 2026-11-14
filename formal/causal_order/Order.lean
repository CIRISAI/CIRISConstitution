/-
  Order.lean — is the kernel a function of the set of rows a node holds?

  A node holds signed rows. The kernel takes the rows the node was offered and returns which of
  them are admitted (and from those, who holds which role and what a count is). Two concerns:
  (a) a guard "refuse this row if a matching row is already admitted" reads arrival order;
  (b) admission reads the signer's standing, standing is a fold over admitted rows including
      removals, a removal needs a count of standing voices, and the count admits the removal:
      a recursion that passes through negation.

  What this file proves.
    T1  With a well-founded `below` relation that is a property of the rows (a rank), and ANY
        judging rule (negation allowed) that reads only the admitted rows below, the admitted
        set is defined by recursion on rank, is the only solution of its defining equation, and
        is a function of the offered set. An executable form (sort by rank, then fold) returns
        the same list for any two arrival orders, and that list is the specified set.
    T2  The arrival kernel (fold in arrival order) is not a function of the set: two rows with
        a first-wins guard, two orders, two results.
    T3  Adding a row r changes the verdict only of r and of rows above r. With an admission
        window W, verdicts on rows signed more than W before now are final.
    T4  A worked instance of standing / admission / count / removal through negation, the same
        under every order tried in the rank kernel and different in the arrival kernel. And the
        necessity of a total tie-break: a kernel that treats two tied rows alike cannot admit
        exactly one of them; in the rank kernel two tied rows that exclude each other are both
        admitted.
    T5  Monotone case: any arrival order that keeps refused rows and re-judges until nothing
        more is admitted ends at the same set (the least fixed point). Termination of the
        re-judging is not proved here.

  Causal order without a global rank (T6, T7) is in Causal.lean, which imports this file.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core.
-/

namespace Order

/-! ## Part 1. The rank kernel as a specification (sets of rows) -/

section Spec

variable {Row : Type}

/-- The admitted set, by well-founded recursion on `below`. `S` is the set of offered rows.
    `judge r P` is the rule: `P` is the set of rows below `r` already judged admitted. -/
noncomputable def adm (below : Row → Row → Prop) (wf : WellFounded below)
    (judge : Row → (Row → Prop) → Prop) (S : Row → Prop) : Row → Prop :=
  wf.fix (fun r ih => S r ∧ judge r (fun q => ∃ h : below q r, ih q h))

variable {below : Row → Row → Prop} (wf : WellFounded below)
variable (judge : Row → (Row → Prop) → Prop)

/-- The defining equation: a row is admitted iff it was offered and the rule accepts it
    against the admitted rows below it. -/
theorem adm_iff (S : Row → Prop) (r : Row) :
    adm below wf judge S r ↔
      (S r ∧ judge r (fun q => below q r ∧ adm below wf judge S q)) := by
  have h := WellFounded.fix_eq wf
    (fun r (ih : (y : Row) → below y r → Prop) => S r ∧ judge r (fun q => ∃ h : below q r, ih q h)) r
  have e : (fun q => below q r ∧ adm below wf judge S q)
      = (fun q => ∃ _ : below q r, adm below wf judge S q) :=
    funext fun q => propext ⟨fun ⟨h, a⟩ => ⟨h, a⟩, fun ⟨h, a⟩ => ⟨h, a⟩⟩
  rw [e]
  exact Iff.of_eq h

theorem adm_offered (S : Row → Prop) (r : Row) (h : adm below wf judge S r) : S r :=
  ((adm_iff wf judge S r).1 h).1

/-- T1 (well-defined). The defining equation has exactly one solution, whatever the rule,
    negation included. No stratification of the rule is asked for. -/
theorem adm_unique (S : Row → Prop) (A : Row → Prop)
    (hA : ∀ r, A r ↔ (S r ∧ judge r (fun q => below q r ∧ A q))) :
    ∀ r, A r ↔ adm below wf judge S r := by
  intro r
  induction r using WellFounded.induction wf with | _ r ih => ?_
  have e : (fun q => below q r ∧ A q) = (fun q => below q r ∧ adm below wf judge S q) :=
    funext fun q => propext
      ⟨fun ⟨h, a⟩ => ⟨h, (ih q h).1 a⟩, fun ⟨h, a⟩ => ⟨h, (ih q h).2 a⟩⟩
  rw [hA r, adm_iff, e]

/-- T1 (function of the set). Two offered sets with the same members give the same verdicts. -/
theorem adm_congr (S S' : Row → Prop) (h : ∀ r, S r ↔ S' r) :
    adm below wf judge S = adm below wf judge S' := by
  have e : S = S' := funext fun r => propext (h r)
  rw [e]

/-- T1 (arrival orders). Two lists that are permutations of each other give the same verdicts. -/
theorem adm_perm (l l' : List Row) (h : l.Perm l') :
    adm below wf judge (fun r => r ∈ l) = adm below wf judge (fun r => r ∈ l') :=
  adm_congr wf judge _ _ (fun _ => h.mem_iff)

/-- The same for any two lists with the same members (repeats and order both ignored). -/
theorem adm_same_members (l l' : List Row) (h : ∀ r, r ∈ l ↔ r ∈ l') :
    adm below wf judge (fun r => r ∈ l) = adm below wf judge (fun r => r ∈ l') :=
  adm_congr wf judge _ _ h

/-! ### T3. What a late row may reverse -/

/-- The verdict on `x` reads only `x` and the rows below `x`. -/
theorem adm_local (trans : ∀ a b c, below a b → below b c → below a c)
    (S S' : Row → Prop) (x : Row)
    (h : ∀ q, (q = x ∨ below q x) → (S q ↔ S' q)) :
    adm below wf judge S x ↔ adm below wf judge S' x := by
  induction x using WellFounded.induction wf with | _ x ih => ?_
  have e : (fun q => below q x ∧ adm below wf judge S q)
      = (fun q => below q x ∧ adm below wf judge S' q) :=
    funext fun q => propext
      ⟨fun ⟨hq, a⟩ => ⟨hq, (ih q hq (fun p hp => h p (Or.inr
          (hp.elim (fun e => e ▸ hq) (fun hpq => trans p q x hpq hq))))).1 a⟩,
       fun ⟨hq, a⟩ => ⟨hq, (ih q hq (fun p hp => h p (Or.inr
          (hp.elim (fun e => e ▸ hq) (fun hpq => trans p q x hpq hq))))).2 a⟩⟩
  rw [adm_iff, adm_iff wf judge S', e]
  have hx : S x ↔ S' x := h x (Or.inl rfl)
  exact ⟨fun ⟨a, b⟩ => ⟨hx.1 a, b⟩, fun ⟨a, b⟩ => ⟨hx.2 a, b⟩⟩

/-- T3. Adding a row `r` to the offered set leaves the verdict on `x` as it was, unless `x`
    is `r` or `r` is below `x`. -/
theorem late_row_keeps (trans : ∀ a b c, below a b → below b c → below a c)
    (S : Row → Prop) (r x : Row) (hne : x ≠ r) (hnb : ¬ below r x) :
    adm below wf judge S x ↔ adm below wf judge (fun q => S q ∨ q = r) x := by
  apply adm_local wf judge trans
  intro q hq
  have hqr : q ≠ r := by
    intro e
    cases hq with
    | inl h => exact hne (h ▸ e)
    | inr h => exact hnb (e ▸ h)
  exact ⟨Or.inl, fun h => h.elim id (fun e => absurd e hqr)⟩

/-- T3, read the other way: a verdict that a late row `r` changed is the verdict on `r`
    itself or on a row above `r`. -/
theorem late_row_reverses_only_above (trans : ∀ a b c, below a b → below b c → below a c)
    (S : Row → Prop) (r x : Row)
    (hchg : ¬ (adm below wf judge S x ↔ adm below wf judge (fun q => S q ∨ q = r) x)) :
    x = r ∨ below r x :=
  Classical.byContradiction fun hn =>
    hchg (late_row_keeps wf judge trans S r x (fun e => hn (Or.inl e)) (fun b => hn (Or.inr b)))

/-- T3 corollary (finality). `signed` is the instant a row carries; rank refines it. If two
    offered sets differ only on rows signed at or after `now - W`, every verdict on a row
    signed before `now - W` is the same in both. -/
theorem final_after_window (trans : ∀ a b c, below a b → below b c → below a c)
    (signed : Row → Nat) (hmono : ∀ q r, below q r → signed q ≤ signed r)
    (W now : Nat) (S S' : Row → Prop)
    (hsame : ∀ q, signed q + W < now → (S q ↔ S' q))
    (x : Row) (hx : signed x + W < now) :
    adm below wf judge S x ↔ adm below wf judge S' x := by
  apply adm_local wf judge trans
  intro q hq
  apply hsame
  cases hq with
  | inl h => rw [h]; exact hx
  | inr h => exact Nat.lt_of_le_of_lt (Nat.add_le_add_right (hmono q x h) W) hx

/-- The window gate. `O r t` says row `r` was offered to this node and first seen at `t`.
    A row passes when it was first seen no later than `W` after its signed instant. The gate
    reads the row and its first-seen instant and nothing else. -/
def gate (signed : Row → Nat) (W : Nat) (O : Row → Nat → Prop) (r : Row) : Prop :=
  ∃ t, O r t ∧ t ≤ signed r + W

/-- T3 corollary, with the gate. `O` is what the node has been offered up to `now`; `O'` is
    any later state: nothing is lost and every new offer is first seen at `now` or after.
    Then the verdict on every row signed more than `W` before `now` is final. -/
theorem final_after_window_gate (trans : ∀ a b c, below a b → below b c → below a c)
    (signed : Row → Nat) (hmono : ∀ q r, below q r → signed q ≤ signed r)
    (W now : Nat) (O O' : Row → Nat → Prop)
    (hkeep : ∀ r t, O r t → O' r t)
    (hnew : ∀ r t, O' r t → O r t ∨ now ≤ t)
    (x : Row) (hx : signed x + W < now) :
    adm below wf judge (gate signed W O) x ↔ adm below wf judge (gate signed W O') x := by
  apply final_after_window wf judge trans signed hmono W now _ _ _ x hx
  intro q hq
  constructor
  · intro ⟨t, ho, ht⟩
    exact ⟨t, hkeep q t ho, ht⟩
  · intro ⟨t, ho, ht⟩
    cases hnew q t ho with
    | inl h => exact ⟨t, h, ht⟩
    | inr h => exact absurd (Nat.lt_of_le_of_lt (Nat.le_trans h ht) hq) (Nat.lt_irrefl _)

/-! ### T4 (second half). Ties -/

include wf in
theorem wf_asymm (a b : Row) (hab : below a b) (hba : below b a) : False := by
  induction a using WellFounded.induction wf generalizing b with | _ a ih => ?_
  exact ih b hba a hba hab

include wf in
theorem wf_irrefl (a : Row) : ¬ below a a := fun h => wf_asymm wf a a h h

/-- A row with no offered row below it is judged against the empty set. -/
theorem adm_bottom (S : Row → Prop) (a : Row) (hbot : ∀ q, S q → ¬ below q a) :
    adm below wf judge S a ↔ (S a ∧ judge a (fun _ => False)) := by
  have e : (fun q => below q a ∧ adm below wf judge S q) = (fun _ => False) :=
    funext fun q => propext
      ⟨fun ⟨hq, ha⟩ => hbot q (adm_offered wf judge S q ha) hq, False.elim⟩
  rw [adm_iff, e]

/-- T4 (the failure case inside the rank kernel). Two rows of equal rank (neither below the
    other), offered alone, are each judged against the empty set. If the rule accepts each
    when nothing is admitted, as a first-wins guard does, both are admitted, although each
    was meant to exclude the other. -/
theorem tie_admits_both (S : Row → Prop) (a b : Row)
    (hS : ∀ q, S q ↔ (q = a ∨ q = b))
    (hab : ¬ below a b) (hba : ¬ below b a)
    (ja : judge a (fun _ => False)) (jb : judge b (fun _ => False)) :
    adm below wf judge S a ∧ adm below wf judge S b := by
  constructor
  · rw [adm_bottom wf judge S a]
    · exact ⟨(hS a).2 (Or.inl rfl), ja⟩
    · intro q hq hb
      cases (hS q).1 hq with
      | inl h => exact wf_irrefl wf a (h ▸ hb)
      | inr h => exact hba (h ▸ hb)
  · rw [adm_bottom wf judge S b]
    · exact ⟨(hS b).2 (Or.inr rfl), jb⟩
    · intro q hq hb
      cases (hS q).1 hq with
      | inl h => exact hab (h ▸ hb)
      | inr h => exact wf_irrefl wf b (h ▸ hb)

end Spec

/-- T4 (necessity of a tie-break). `K` is any kernel at all: a map from the offered set to the
    admitted set. `σ` is a relabelling of rows (for two tied rows, the swap). If `K` treats rows
    alike under `σ` and the offered set is unchanged by `σ`, then `K` gives `a` and `σ a` the
    same verdict. -/
theorem symmetric_same_verdict {Row : Type} (K : (Row → Prop) → (Row → Prop)) (σ : Row → Row)
    (hK : ∀ S r, K (fun x => S (σ x)) r ↔ K S (σ r))
    (S : Row → Prop) (hS : ∀ x, S (σ x) ↔ S x) (a : Row) :
    K S a ↔ K S (σ a) := by
  have e : (fun x => S (σ x)) = S := funext fun x => propext (hS x)
  have h := hK S a
  rw [e] at h
  exact h

/-- So no kernel that treats two tied rows alike admits exactly one of them. A kernel that does
    admit exactly one tells them apart by something: that something is the tie-break, and it
    has to be a property of the rows (the id) if the kernel is to stay a function of the set. -/
theorem no_symmetric_choice {Row : Type} (K : (Row → Prop) → (Row → Prop)) (σ : Row → Row)
    (hK : ∀ S r, K (fun x => S (σ x)) r ↔ K S (σ r))
    (S : Row → Prop) (hS : ∀ x, S (σ x) ↔ S x) (a : Row) :
    ¬ ((K S a ∧ ¬ K S (σ a)) ∨ (¬ K S a ∧ K S (σ a))) := by
  have h := symmetric_same_verdict K σ hK S hS a
  intro hc
  cases hc with
  | inl c => exact c.2 (h.1 c.1)
  | inr c => exact c.1 (h.2 c.2)

/-! ## Part 2. Executable kernels (lists of rows) -/

section Exec

variable {Row : Type}

/-- The arrival kernel: fold in arrival order, judge each row against those admitted so far,
    drop a refused row. -/
def arrive (j : Row → List Row → Bool) (l : List Row) : List Row :=
  l.foldl (fun acc r => if j r acc then acc ++ [r] else acc) []

def ins (rank : Row → Nat) (r : Row) : List Row → List Row
  | [] => [r]
  | x :: xs => if rank r ≤ rank x then r :: x :: xs else x :: ins rank r xs

def isort (rank : Row → Nat) : List Row → List Row
  | [] => []
  | x :: xs => ins rank x (isort rank xs)

/-- The rank kernel, executable: sort the offered rows by rank, then run the same fold. -/
def sortKernel (rank : Row → Nat) (j : Row → List Row → Bool) (l : List Row) : List Row :=
  arrive j (isort rank l)

theorem ins_perm (rank : Row → Nat) (r : Row) : ∀ l, (ins rank r l).Perm (r :: l)
  | [] => List.Perm.refl _
  | x :: xs => by
    unfold ins
    split
    · exact List.Perm.refl _
    · exact ((ins_perm rank r xs).cons x).trans (List.Perm.swap r x xs)

theorem isort_perm (rank : Row → Nat) : ∀ l, (isort rank l).Perm l
  | [] => List.Perm.refl _
  | x :: xs => (ins_perm rank x (isort rank xs)).trans ((isort_perm rank xs).cons x)

theorem ins_sorted (rank : Row → Nat) (r : Row) :
    ∀ l, l.Pairwise (fun a b => rank a ≤ rank b) →
      (ins rank r l).Pairwise (fun a b => rank a ≤ rank b)
  | [], _ => List.pairwise_cons.2 ⟨fun _ h => (nomatch h), List.Pairwise.nil⟩
  | x :: xs, h => by
    have hx := List.pairwise_cons.1 h
    unfold ins
    split
    · rename_i hle
      refine List.pairwise_cons.2 ⟨?_, h⟩
      intro b hb
      cases List.mem_cons.1 hb with
      | inl e => rw [e]; exact hle
      | inr m => exact Nat.le_trans hle (hx.1 b m)
    · rename_i hnle
      refine List.pairwise_cons.2 ⟨?_, ins_sorted rank r xs hx.2⟩
      intro b hb
      cases List.mem_cons.1 ((ins_perm rank r xs).mem_iff.1 hb) with
      | inl e => rw [e]; exact Nat.le_of_lt (Nat.lt_of_not_le hnle)
      | inr m => exact hx.1 b m

theorem isort_sorted (rank : Row → Nat) :
    ∀ l, (isort rank l).Pairwise (fun a b => rank a ≤ rank b)
  | [] => List.Pairwise.nil
  | x :: xs => ins_sorted rank x _ (isort_sorted rank xs)

/-- T1 (executable). If the offered rows have distinct ranks, the rank kernel returns the same
    list for any two arrival orders. `j` is ANY rule on (row, admitted so far): it may negate,
    count, or apply a first-wins guard. -/
theorem sortKernel_perm (rank : Row → Nat) (j : Row → List Row → Bool) (l l' : List Row)
    (hdistinct : ∀ a, a ∈ l → ∀ b, b ∈ l → rank a = rank b → a = b)
    (h : l.Perm l') :
    sortKernel rank j l = sortKernel rank j l' := by
  unfold sortKernel
  have hp : (isort rank l).Perm (isort rank l') :=
    (isort_perm rank l).trans (h.trans (isort_perm rank l').symm)
  have e : isort rank l = isort rank l' :=
    List.Perm.eq_of_sorted
      (fun a b ha hb h1 h2 =>
        hdistinct a ((isort_perm rank l).mem_iff.1 ha) b
          (h.mem_iff.2 ((isort_perm rank l').mem_iff.1 hb)) (Nat.le_antisymm h1 h2))
      (isort_sorted rank l) (isort_sorted rank l') hp
  rw [e]

/-- The arrival kernel, when the rows happen to arrive in rank order, computes the specified
    admitted set. `j` reads the admitted list as a set and agrees with `judge`. -/
theorem arrive_sorted_spec {below : Row → Row → Prop} (wf : WellFounded below)
    (judge : Row → (Row → Prop) → Prop) (j : Row → List Row → Bool)
    (hj : ∀ r acc, j r acc = true ↔ judge r (fun q => q ∈ acc))
    (L : List Row) (hL : L.Pairwise below) :
    ∀ x, x ∈ arrive j L ↔ adm below wf judge (fun r => r ∈ L) x := by
  have key : ∀ (suf pre acc : List Row), pre ++ suf = L →
      (∀ x, x ∈ acc ↔ (x ∈ pre ∧ adm below wf judge (fun r => r ∈ L) x)) →
      ∀ x, x ∈ suf.foldl (fun acc r => if j r acc then acc ++ [r] else acc) acc ↔
        adm below wf judge (fun r => r ∈ L) x := by
    intro suf
    induction suf with
    | nil =>
      intro pre acc hpre hacc x
      rw [List.append_nil] at hpre
      rw [List.foldl_nil, hacc x, hpre]
      exact ⟨fun h => h.2, fun h => ⟨adm_offered wf judge _ x h, h⟩⟩
    | cons r suf ih =>
      intro pre acc hpre hacc x
      rw [List.foldl_cons]
      have hpw : (pre ++ r :: suf).Pairwise below := by rw [hpre]; exact hL
      have hsplit := List.pairwise_append.1 hpw
      have hrL : r ∈ L := by rw [← hpre]; simp
      -- the admitted list so far is exactly the admitted rows below r
      have hset : (fun q => q ∈ acc)
          = (fun q => below q r ∧ adm below wf judge (fun r => r ∈ L) q) := by
        funext q
        apply propext
        rw [hacc q]
        constructor
        · intro ⟨hq, ha⟩
          exact ⟨hsplit.2.2 q hq r (List.mem_cons_self r suf), ha⟩
        · intro ⟨hb, ha⟩
          refine ⟨?_, ha⟩
          have hqL : q ∈ pre ++ r :: suf := by rw [hpre]; exact adm_offered wf judge _ q ha
          cases List.mem_append.1 hqL with
          | inl h => exact h
          | inr h =>
            cases List.mem_cons.1 h with
            | inl e => exact absurd (e ▸ hb) (wf_irrefl wf r)
            | inr m =>
              exact (wf_asymm wf q r hb ((List.pairwise_cons.1 hsplit.2.1).1 q m)).elim
      have hjr : j r acc = true ↔ adm below wf judge (fun r => r ∈ L) r := by
        rw [hj r acc, hset, adm_iff wf judge (fun r => r ∈ L) r]
        exact ⟨fun h => ⟨hrL, h⟩, fun h => h.2⟩
      apply ih (pre ++ [r])
      · rw [List.append_assoc]; exact hpre
      · intro y
        cases hc : j r acc with
        | true =>
          have har := hjr.1 hc
          simp only [if_true, List.mem_append, List.mem_singleton]
          rw [hacc y]
          constructor
          · intro h
            cases h with
            | inl h => exact ⟨Or.inl h.1, h.2⟩
            | inr h => exact ⟨Or.inr h, h ▸ har⟩
          · intro ⟨h, ha⟩
            cases h with
            | inl h => exact Or.inl ⟨h, ha⟩
            | inr h => exact Or.inr h
        | false =>
          have hnar : ¬ adm below wf judge (fun r => r ∈ L) r := by
            intro har
            have := hjr.2 har
            rw [hc] at this
            exact Bool.noConfusion this
          simp only [Bool.false_eq_true, if_false, List.mem_append, List.mem_singleton]
          rw [hacc y]
          constructor
          · intro h
            exact ⟨Or.inl h.1, h.2⟩
          · intro ⟨h, ha⟩
            cases h with
            | inl h => exact ⟨h, ha⟩
            | inr h => exact absurd (h ▸ ha) hnar
  intro x
  exact key L [] [] (List.nil_append L) (fun x => ⟨fun h => (nomatch h), fun h => (nomatch h.1)⟩) x

/-- Rank as a relation on rows. -/
def rankBelow (rank : Row → Nat) (q r : Row) : Prop := rank q < rank r

theorem rankBelow_wf (rank : Row → Nat) : WellFounded (rankBelow rank) :=
  InvImage.wf rank Nat.lt_wfRel.wf

theorem pairwise_combine {R Q T : Row → Row → Prop} (hc : ∀ a b, R a b → Q a b → T a b) :
    ∀ l : List Row, l.Pairwise R → l.Pairwise Q → l.Pairwise T
  | [], _, _ => List.Pairwise.nil
  | x :: xs, hr, hq => by
    have hr' := List.pairwise_cons.1 hr
    have hq' := List.pairwise_cons.1 hq
    exact List.pairwise_cons.2
      ⟨fun b hb => hc x b (hr'.1 b hb) (hq'.1 b hb), pairwise_combine hc xs hr'.2 hq'.2⟩

/-- T1 (the executable kernel meets the specification). If the offered rows have pairwise
    distinct ranks, the sort-then-fold kernel admits exactly the rows the specification admits
    for the set of offered rows. -/
theorem sortKernel_spec (rank : Row → Nat)
    (judge : Row → (Row → Prop) → Prop) (j : Row → List Row → Bool)
    (hj : ∀ r acc, j r acc = true ↔ judge r (fun q => q ∈ acc))
    (l : List Row) (hdistinct : l.Pairwise (fun a b => rank a ≠ rank b)) :
    ∀ x, x ∈ sortKernel rank j l ↔
      adm (rankBelow rank) (rankBelow_wf rank) judge (fun r => r ∈ l) x := by
  have hne : (isort rank l).Pairwise (fun a b => rank a ≠ rank b) :=
    (List.Perm.pairwise_iff (fun h => fun e => h e.symm) (isort_perm rank l)).2 hdistinct
  have hlt : (isort rank l).Pairwise (rankBelow rank) :=
    pairwise_combine (fun a b h1 h2 => Nat.lt_of_le_of_ne h1 h2) _ (isort_sorted rank l) hne
  have e := adm_congr (rankBelow_wf rank) judge
    (fun r => r ∈ isort rank l) (fun r => r ∈ l) (fun _ => (isort_perm rank l).mem_iff)
  intro x
  rw [← e]
  exact arrive_sorted_spec (rankBelow_wf rank) judge j hj (isort rank l) hlt x

end Exec

/-! ## Part 3. T2: the arrival kernel is not a function of the set -/

namespace Two

inductive R | a | b
  deriving DecidableEq, Repr

/-- First wins: a row is refused if a matching row is already admitted. Here the two rows
    match each other. -/
def firstWins (_ : R) (acc : List R) : Bool := acc.isEmpty

theorem arrive_ab : arrive firstWins [R.a, R.b] = [R.a] := by decide
theorem arrive_ba : arrive firstWins [R.b, R.a] = [R.b] := by decide

/-- T2. Same two rows, two arrival orders, two different admitted sets. -/
theorem arrival_not_a_function :
    ∃ l l' : List R, l.Perm l' ∧ arrive firstWins l ≠ arrive firstWins l' :=
  ⟨[R.a, R.b], [R.b, R.a], List.Perm.swap R.b R.a [], by decide⟩

/-- With a rank that tells the two rows apart, the rank kernel gives one answer for both. -/
def rank : R → Nat | R.a => 0 | R.b => 1

theorem sort_ab : sortKernel rank firstWins [R.a, R.b] = [R.a] := by decide
theorem sort_ba : sortKernel rank firstWins [R.b, R.a] = [R.a] := by decide

end Two

/-! ## Part 4. T4 (first half): standing, admission, count and removal, through negation -/

namespace Roster

inductive Act
  | add (p : Nat)      -- admit p as a member
  | vote (p : Nat)     -- one voice for removing p
  | remove (p : Nat)   -- the removal of p; lands only when the count is met
  | post               -- anything else a member signs
  deriving DecidableEq, Repr

structure Row where
  id : Nat
  signed : Nat
  signer : Nat
  act : Act
  deriving DecidableEq, Repr

/-- Rank is (signed instant, id). Ids here are below 100. -/
def rank (r : Row) : Nat := r.signed * 100 + r.id

/-- Standing is a fold over admitted rows, with a negation: added (or the founder, 0) and
    NOT removed. -/
def standing (acc : List Row) (p : Nat) : Bool :=
  (p == 0 || acc.any (fun q => decide (q.act = Act.add p)))
    && !(acc.any (fun q => decide (q.act = Act.remove p)))

/-- The count of admitted voices for removing p. -/
def voices (acc : List Row) (p : Nat) : Nat :=
  (acc.filter (fun q => decide (q.act = Act.vote p))).length

/-- Admission: the signer must have standing. A second vote by the same signer is refused
    (a first-wins guard). A removal is admitted only when two voices are counted. -/
def judge (r : Row) (acc : List Row) : Bool :=
  standing acc r.signer &&
    match r.act with
    | Act.add _ => true
    | Act.post => true
    | Act.vote p => !(acc.any (fun q => decide (q.signer = r.signer ∧ q.act = Act.vote p)))
    | Act.remove p => decide (2 ≤ voices acc p)

def r1 : Row := ⟨1, 1, 0, Act.add 1⟩
def r2 : Row := ⟨2, 2, 0, Act.add 2⟩
def r3 : Row := ⟨3, 3, 0, Act.vote 2⟩
def r4 : Row := ⟨4, 4, 1, Act.vote 2⟩
def r5 : Row := ⟨5, 5, 1, Act.vote 2⟩      -- second vote by 1: refused by the guard
def r6 : Row := ⟨6, 6, 0, Act.remove 2⟩    -- two voices counted: admitted
def r7 : Row := ⟨7, 7, 2, Act.post⟩        -- signed by 2 after the removal: refused
def r8 : Row := ⟨8, 8, 2, Act.vote 1⟩      -- likewise refused

def inOrder : List Row := [r1, r2, r3, r4, r5, r6, r7, r8]
def late    : List Row := [r7, r8, r6, r5, r4, r3, r2, r1]
def mixed   : List Row := [r1, r2, r7, r6, r3, r8, r5, r4]

/-- The rank kernel gives one answer on every order tried: the removal lands, and what the
    removed member signed afterwards is refused. -/
theorem rank_inOrder : sortKernel rank judge inOrder = [r1, r2, r3, r4, r6] := by decide
theorem rank_late    : sortKernel rank judge late    = [r1, r2, r3, r4, r6] := by decide
theorem rank_mixed   : sortKernel rank judge mixed   = [r1, r2, r3, r4, r6] := by decide

/-- The arrival kernel gives three answers on the same rows. In `late` nothing but the
    founder's first row survives; in `mixed` the removed member's post is admitted and the
    removal never lands, so member 2 keeps standing. -/
theorem arrive_inOrder : arrive judge inOrder = [r1, r2, r3, r4, r6] := by decide
theorem arrive_late    : arrive judge late    = [r3, r2, r1] := by decide
theorem arrive_mixed   : arrive judge mixed   = [r1, r2, r7, r3, r8, r5] := by decide

theorem standing_rank    : standing (sortKernel rank judge mixed) 2 = false := by decide
theorem standing_arrival : standing (arrive judge mixed) 2 = true := by decide

/-- The general theorem applies to this instance: every arrival order of these eight rows
    gives the rank kernel's one answer. -/
theorem rank_any_order (l : List Row) (h : inOrder.Perm l) :
    sortKernel rank judge l = [r1, r2, r3, r4, r6] := by
  rw [← sortKernel_perm rank judge inOrder l (by decide) h]
  exact rank_inOrder

end Roster

/-! ## Part 5. T5: the monotone case -/

section Monotone

variable {Row : Type}
variable (S : Row → Prop) (judge : Row → (Row → Prop) → Prop)

/-- A set is closed when every offered row the rule accepts against it is already in it. -/
def Closed (A : Row → Prop) : Prop := ∀ r, S r → judge r A → A r

/-- The least closed set. A function of `S` by its definition. -/
def least (r : Row) : Prop := ∀ A, Closed S judge A → A r

/-- What an arrival kernel that keeps refused rows can reach: start empty; at any moment admit
    any offered row that the rule accepts against what is admitted so far. Every arrival order
    with every schedule of re-judging is a path of such steps. -/
inductive Reach : (Row → Prop) → Prop
  | empty : Reach (fun _ => False)
  | step (A : Row → Prop) (r : Row) : Reach A → S r → judge r A → Reach (fun q => A q ∨ q = r)

variable (mono : ∀ r (A B : Row → Prop), (∀ q, A q → B q) → judge r A → judge r B)
include mono

/-- With a monotone rule, nothing is admitted along the way that the least closed set lacks. -/
theorem reach_sound (A : Row → Prop) (h : Reach S judge A) : ∀ q, A q → least S judge q := by
  induction h with
  | empty => intro q hq; exact hq.elim
  | step A r _ hS hj ih =>
    intro q hq
    cases hq with
    | inl h => exact ih q h
    | inr e =>
      rw [e]
      intro B hB
      exact hB r hS (mono r A B (fun q hq => ih q hq B hB) hj)

/-- T5. Re-judged until nothing more is admitted, every arrival order ends at the same set. -/
theorem saturated_is_least (A : Row → Prop) (h : Reach S judge A) (hsat : Closed S judge A) :
    ∀ q, A q ↔ least S judge q :=
  fun q => ⟨reach_sound S judge mono A h q, fun hl => hl A hsat⟩

theorem saturated_agree (A B : Row → Prop)
    (hA : Reach S judge A) (hAs : Closed S judge A)
    (hB : Reach S judge B) (hBs : Closed S judge B) :
    ∀ q, A q ↔ B q :=
  fun q => (saturated_is_least S judge mono A hA hAs q).trans
    (saturated_is_least S judge mono B hB hBs q).symm

end Monotone

/-- T5 needs monotonicity: the first-wins rule of Part 3 is not monotone, and there two
    saturated runs disagree (each one-row result is closed: the other row is refused). -/
theorem first_wins_not_monotone :
    ¬ (∀ (r : Two.R) (A B : List Two.R), (∀ q, q ∈ A → q ∈ B) →
        Two.firstWins r A = true → Two.firstWins r B = true) := by
  intro h
  exact absurd (h Two.R.a [] [Two.R.b] (fun _ hq => nomatch hq) rfl) (by decide)

/-! ## Axioms used -/

#print axioms adm_unique
#print axioms adm_congr
#print axioms adm_perm
#print axioms sortKernel_perm
#print axioms sortKernel_spec
#print axioms Two.arrival_not_a_function
#print axioms late_row_keeps
#print axioms late_row_reverses_only_above
#print axioms final_after_window
#print axioms final_after_window_gate
#print axioms Roster.rank_any_order
#print axioms Roster.standing_arrival
#print axioms tie_admits_both
#print axioms no_symmetric_choice
#print axioms saturated_agree

end Order
