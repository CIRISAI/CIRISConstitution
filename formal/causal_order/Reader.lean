/-
  Reader.lean — the reader's line and the built-on clause, over the plain cut

  Harden3.lean proved the reader's line with the group checkpoint (`CP.cpClash`) inside its
  operator, and the built-on clause over `CP.cpPoss`. The group checkpoint is not the
  kernel's rule (KERNEL.md 8a, "No line wins by being longer"; checkpoint.py `group=False`).
  This file states the rule as checkpoint.py `settle` runs it with `group=False`:

    the cut      the plain status of Seat.lean Part B: `cutCounts` of `cutT`, with no
                 `olderHeads` clash. Call what it lets count `L`.
    the reader   a counted act counts for the reader iff the cut lets it count, and either it
                 is on the reader's acknowledged line (`mine`), or every counted act among the
                 heads it names counts for the reader (BUILT ON) and no act of the reader's
                 line that the cut lets count, concurrent with it, names heads all strictly
                 newer than every head it names (LEFT BEHIND).

  The reader's layer reads `L` and `mine` only, and refers to itself positively (built on):
  it is a least fixed point, with no negation of itself and one answer. The reader's line is
  applied ON TOP of the cut, as `settle` does: an act left behind by the reader's line still
  voids, inside the cut, what it clashes with (it is in `L`). Harden3.lean's `rdT` put the line
  inside the operator, where an act left behind no longer voids anything; that is not the run.

  The group checkpoint appears here once, as the thing shown wrong: the depth race.

  SUPERSEDES in Harden3.lean: `CP.built_on_void_is_void`, and the whole of Part 2 (`rdT`,
  `rdCounts`, `rdPoss`, `rd_function`, `rdT_anti`, `no_line_is_group`, `acked_not_left_behind`,
  `line_voids_old_fork`, `old_fork_void_for_reader`, `old_fork_void_for_ever`,
  `built_on_void_for_reader`, `line_no_obstacle`, `sibling_waits`, `merge_accepted`).
  Uses from Harden3.lean only the neutral `CP.olderHeads` and `CP.same_head_not_older`, and,
  for the race, the rejected `CP.cpCounts`, `CP.cpPoss`, `CP.stale_never_counts`.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports Harden3.lean.
-/

import Harden3

namespace Kernel

namespace Reader

open Order Relation Causal Harden

section Line

variable {Row : Type}
variable (parent : Row → Row → Prop) (head : Row → Row → Prop) (isAct : Row → Prop)
/- `mine`: the counted acts this reader has acknowledged, with the counted acts in their past
   (checkpoint.py `own_line`). `L`: the counted acts the cut lets count. -/
variable (mine : Row → Prop) (L : Row → Prop)

/-- LEFT BEHIND by the reader's line (checkpoint.py `behind`, marks = the line ∩ what the cut
    lets count). -/
def behind (r : Row) : Prop :=
  ∃ m, mine m ∧ L m ∧ isAct m ∧ conc parent m r ∧ CP.olderHeads parent head r m

/-- One step of `settle`'s `gamma`, group off. -/
def rdF (P : Row → Prop) (r : Row) : Prop :=
  L r ∧ isAct r ∧
    (mine r ∨ ((∀ h, head r h → isAct h → P h) ∧ ¬ behind parent head isAct mine L r))

/-- The counted acts that count for the reader. -/
def rd : Row → Prop := lfp (rdF parent head isAct mine L)

theorem rdF_mono : ∀ X Y : Row → Prop, (∀ r, X r → Y r) →
    ∀ r, rdF parent head isAct mine L X r → rdF parent head isAct mine L Y r :=
  fun _ _ hXY _ ⟨h1, h2, h3⟩ =>
    ⟨h1, h2, h3.elim Or.inl (fun ⟨hb, hn⟩ => Or.inr ⟨fun h hh ha => hXY h (hb h hh ha), hn⟩)⟩

/-- The equation it solves. -/
theorem rd_iff (r : Row) : rd parent head isAct mine L r ↔
    (L r ∧ isAct r ∧ (mine r ∨ ((∀ h, head r h → isAct h → rd parent head isAct mine L h) ∧
      ¬ behind parent head isAct mine L r))) :=
  ⟨lfp_post _ (rdF_mono parent head isAct mine L) r, lfp_pre _ (rdF_mono parent head isAct mine L) r⟩

/-- What counts for a reader the cut lets count. -/
theorem rd_live (r : Row) (h : rd parent head isAct mine L r) : L r :=
  ((rd_iff parent head isAct mine L r).1 h).1

/-- A function of what the cut lets count and the reader's line. -/
theorem rd_function (LOf mineOf : (Row → Prop) → Row → Prop) (S S' : Row → Prop)
    (h : ∀ r, S r ↔ S' r) :
    rd parent head isAct (mineOf S) (LOf S) = rd parent head isAct (mineOf S') (LOf S') := by
  have e : S = S' := funext fun r => propext (h r)
  rw [e]

/-- The only solution where naming is well-founded: any `P` that solves the same equation is
    `rd`. (With the group checkpoint off nothing here is negated: one answer.) -/
theorem rd_unique (wfh : WellFounded (fun h r => head r h)) (P : Row → Prop)
    (hP : ∀ r, P r ↔ rdF parent head isAct mine L P r) :
    ∀ r, P r ↔ rd parent head isAct mine L r := by
  intro r
  induction r using WellFounded.induction wfh with | _ r ih => ?_
  rw [hP r, rd_iff]
  constructor
  · intro ⟨a, b, c⟩
    exact ⟨a, b, c.elim Or.inl (fun ⟨hb, hn⟩ =>
      Or.inr ⟨fun h hh ha => (ih h hh).1 (hb h hh ha), hn⟩)⟩
  · intro ⟨a, b, c⟩
    exact ⟨a, b, c.elim Or.inl (fun ⟨hb, hn⟩ =>
      Or.inr ⟨fun h hh ha => (ih h hh).2 (hb h hh ha), hn⟩)⟩

/-! ### The reader's line -/

/-- An act of the reader's line that the cut lets count counts for the reader. -/
theorem acked_counts (r : Row) (hm : mine r) :
    rd parent head isAct mine L r ↔ (L r ∧ isAct r) :=
  ⟨fun h => let ⟨a, b, _⟩ := (rd_iff parent head isAct mine L r).1 h; ⟨a, b⟩,
   fun ⟨a, b⟩ => (rd_iff parent head isAct mine L r).2 ⟨a, b, Or.inl hm⟩⟩

/-- (4) THE ACKNOWLEDGED LINE. `m` is on the reader's line and the cut lets it count. An act `v`
    off the line, concurrent with `m`, naming only heads older than the heads `m` names, does
    not count for this reader. Nothing is asked about who signed `v` or how many did. -/
theorem line_voids_old_fork (m v : Row) (hm : mine m) (hLm : L m) (hact : isAct m)
    (hv : ¬ mine v) (hc : conc parent m v) (ho : CP.olderHeads parent head v m) :
    ¬ rd parent head isAct mine L v :=
  fun h => ((rd_iff parent head isAct mine L v).1 h).2.2.elim hv
    (fun ⟨_, hn⟩ => hn ⟨m, hm, hLm, hact, hc, ho⟩)

/-- (4), for ever: `m` is kept at `S`; `v` is offered later and does not name `m`. At every
    later set at which the cut still lets `m` count, `v` does not count for this reader. -/
theorem old_fork_void_for_ever (wf : WellFounded parent) (wellFormed : Row → Prop)
    (S : Row → Prop) (m v : Row) (hk : kept parent wf wellFormed S m) (hv' : ¬ S v)
    (hnn : ¬ TransGen parent m v) (hm : mine m) (hact : isAct m) (hv : ¬ mine v)
    (ho : CP.olderHeads parent head v m) (L' : Row → Prop) (hLm : L' m) :
    ¬ rd parent head isAct mine L' v :=
  have hn := new_row_not_ancestor parent wf wellFormed S v m hk hv'
  line_voids_old_fork parent head isAct mine L' m v hm hLm hact hv ⟨hnn, hn.2, hn.1⟩ ho

/-! ### The built-on clause -/

/-- BUILT ON. A counted act off the reader's line that names a counted act that does not count
    for the reader does not count for it. No hypothesis on the entitlement is needed: the
    clause is part of the definition. -/
theorem built_on_void (c h : Row) (hc : ¬ mine c) (hh : head c h) (ha : isAct h)
    (hv : ¬ rd parent head isAct mine L h) : ¬ rd parent head isAct mine L c :=
  fun hr => ((rd_iff parent head isAct mine L c).1 hr).2.2.elim hc (fun ⟨hb, _⟩ => hv (hb h hh ha))

/-- Down the whole line: each step names a counted act, and no row above the void one is on
    the reader's line. -/
theorem line_void (h c : Row)
    (hb : TransGen (fun h c => head c h ∧ isAct h ∧ ¬ mine c) h c)
    (hv : ¬ rd parent head isAct mine L h) : ¬ rd parent head isAct mine L c := by
  induction hb with
  | single st => exact built_on_void parent head isAct mine L _ h st.2.2 st.1 st.2.1 hv
  | tail _ st ih => exact built_on_void parent head isAct mine L _ _ st.2.2 st.1 st.2.1 ih

/-- What the cut does not let count does not count, and neither does what is built on it. -/
theorem built_on_cut_void (c h : Row) (hc : ¬ mine c) (hh : head c h) (ha : isAct h)
    (hL : ¬ L h) : ¬ rd parent head isAct mine L c :=
  built_on_void parent head isAct mine L c h hc hh ha
    (fun hr => hL (rd_live parent head isAct mine L h hr))

/-! ### A reader with no line, and where the line is no obstacle -/

/-- A reader that has acknowledged nothing has the plain cut and the built-on clause, and
    nothing that ranks one line above another. -/
theorem no_line_is_plain (r : Row) :
    rd parent head isAct (fun _ => False) L r ↔
      (L r ∧ isAct r ∧ ∀ h, head r h → isAct h → rd parent head isAct (fun _ => False) L h) := by
  rw [rd_iff]
  constructor
  · intro ⟨a, b, c⟩
    exact ⟨a, b, c.elim False.elim (fun x => x.1)⟩
  · intro ⟨a, b, c⟩
    exact ⟨a, b, Or.inr ⟨c, fun ⟨_, hm, _⟩ => hm⟩⟩

/-- Where the line is no obstacle to `s`: the reader judges `s` by the cut and the built-on
    clause alone. -/
theorem line_no_obstacle (s : Row) (hs : ¬ mine s)
    (hno : ∀ m, mine m → conc parent m s → ¬ CP.olderHeads parent head s m) :
    rd parent head isAct mine L s ↔
      (L s ∧ isAct s ∧ ∀ h, head s h → isAct h → rd parent head isAct mine L h) := by
  rw [rd_iff]
  constructor
  · intro ⟨a, b, c⟩
    exact ⟨a, b, c.elim (fun x => absurd x hs) (fun x => x.1)⟩
  · intro ⟨a, b, c⟩
    exact ⟨a, b, Or.inr ⟨c, fun ⟨m, hm, _, _, hc, ho⟩ => hno m hm hc ho⟩⟩

/-- Where the line is no obstacle to anything, and every act of the line already counts for a
    reader with no line, the reader with the line concludes exactly what that reader does. -/
theorem line_no_obstacle_all
    (hno : ∀ s, ¬ mine s → ¬ behind parent head isAct mine L s)
    (hmine : ∀ m, mine m → rd parent head isAct (fun _ => False) L m) :
    ∀ r, rd parent head isAct mine L r ↔ rd parent head isAct (fun _ => False) L r := by
  intro r
  constructor
  · apply lfp_least _ (rd parent head isAct (fun _ => False) L)
    intro q ⟨a, b, c⟩
    cases c with
    | inl hm => exact hmine q hm
    | inr x => exact (no_line_is_plain parent head isAct L q).2 ⟨a, b, x.1⟩
  · apply lfp_least _ (rd parent head isAct mine L)
    intro q ⟨a, b, c⟩
    cases c with
    | inl hf => exact hf.elim
    | inr x =>
      exact (rd_iff parent head isAct mine L q).2
        ⟨a, b, (Classical.em (mine q)).elim Or.inl (fun hm => Or.inr ⟨x.1, hno q hm⟩)⟩

/-- (4) A SIBLING WAITS. The reader acknowledged `H`, counted over the one head `h`; the rest of
    its line is `h` or in the past of `h`. An act `s` counted over `h` (which it names) is not
    left behind: the reader judges it by the cut and the built-on clause, and the two wait as
    two tips. -/
theorem sibling_waits (wf : WellFounded parent) (H h s : Row)
    (hline : ∀ m, mine m → m = H ∨ m = h ∨ TransGen parent m h)
    (hH : ∀ h', head H h' → h' = h) (hsh : head s h) (hnamed : parent h s) (hs : ¬ mine s) :
    rd parent head isAct mine L s ↔
      (L s ∧ isAct s ∧ ∀ h', head s h' → isAct h' → rd parent head isAct mine L h') := by
  apply line_no_obstacle parent head isAct mine L s hs
  intro m hm hc ho
  cases hline m hm with
  | inl e => exact CP.same_head_not_older parent head wf s H h hsh hH (e ▸ ho)
  | inr h' =>
    cases h' with
    | inl e => exact hc.1 (e ▸ TransGen.single hnamed)
    | inr ha => exact hc.1 (TransGen.tail ha hnamed)

/-- (4) A MERGE IS ACCEPTED. An act that has the acknowledged `H` in its past is concurrent
    with no act of the line: it is judged by the cut and the built-on clause. -/
theorem merge_accepted (H mg : Row)
    (hline : ∀ m, mine m → m = H ∨ TransGen parent m H) (hnames : TransGen parent H mg)
    (hs : ¬ mine mg) :
    rd parent head isAct mine L mg ↔
      (L mg ∧ isAct mg ∧ ∀ h, head mg h → isAct h → rd parent head isAct mine L h) := by
  apply line_no_obstacle parent head isAct mine L mg hs
  intro m hm hc _
  cases hline m hm with
  | inl e => exact hc.1 (e ▸ hnames)
  | inr ha => exact hc.1 (anc_trans ha hnames)

end Line

/-! ### Over the plain cut -/

section OverCut

variable {Row : Type}
variable (parent : Row → Row → Prop) (head : Row → Row → Prop) (isAct : Row → Prop)
variable (clashes overrules : Row → Row → Prop)
variable (ent : (Row → Prop) → (Row → Prop) → Row → Prop) (mine : Row → Prop)

/-- What counts for the reader: the reader's layer over what the PLAIN cut (no checkpoint)
    surely lets count. -/
def rdCounts (A : Row → Prop) : Row → Prop :=
  rd parent head isAct mine (cutCounts parent isAct clashes overrules ent A)

/-- The same over what the plain cut lets count or leaves contested: an upper bound. -/
def rdPoss (A : Row → Prop) : Row → Prop :=
  rd parent head isAct mine (cutPoss parent isAct clashes overrules ent A)

theorem rdCounts_function (C : (Row → Prop) → Row → Prop) (mineOf : (Row → Prop) → Row → Prop)
    (S S' : Row → Prop) (h : ∀ r, S r ↔ S' r) :
    rdCounts parent head isAct clashes overrules ent (mineOf S) (C S)
      = rdCounts parent head isAct clashes overrules ent (mineOf S') (C S') := by
  have e : S = S' := funext fun r => propext (h r)
  rw [e]

/-- The reader's layer only removes: what counts for the reader the cut surely lets count. -/
theorem rdCounts_sub_cut (A : Row → Prop) (r : Row)
    (h : rdCounts parent head isAct clashes overrules ent mine A r) :
    cutCounts parent isAct clashes overrules ent A r :=
  rd_live parent head isAct mine _ r h

/-- The layers nest when the line's marks agree (a reader with no line, or a line inside what
    surely counts): what counts lies inside the upper bound. -/
theorem rdCounts_sub_rdPoss (hent : EntAnti ent) (A : Row → Prop)
    (hm : ∀ m, mine m → cutPoss parent isAct clashes overrules ent A m →
      cutCounts parent isAct clashes overrules ent A m) :
    ∀ r, rdCounts parent head isAct clashes overrules ent mine A r →
      rdPoss parent head isAct clashes overrules ent mine A r := by
  apply lfp_least
  intro q ⟨a, b, c⟩
  refine (rd_iff parent head isAct mine _ q).2
    ⟨sure_sub_poss _ (cutT_anti parent isAct clashes overrules ent hent A) q a, b, ?_⟩
  exact c.elim Or.inl (fun ⟨hb, hn⟩ => Or.inr ⟨hb, fun ⟨m, h1, h2, h3, h4, h5⟩ =>
    hn ⟨m, h1, hm m h1 h2, h3, h4, h5⟩⟩)

end OverCut

/-! ## The rejected rule: the depth race

  With the group checkpoint (`CP.cpClash`), every act that counts leaves behind each act
  concurrent with it that is counted over older heads. Of two lines from one head `h0`, the
  one with a second counted row leaves the other's first row behind, whatever either says,
  and never the reverse. -/

section Race

variable {Row : Type}
variable (parent : Row → Row → Prop) (head : Row → Row → Prop) (isAct : Row → Prop)
variable (clashes overrules : Row → Row → Prop)
variable (ent : (Row → Prop) → (Row → Prop) → Row → Prop)

/-- (Rejected rule) THE DEPTH RACE. `a1` is counted over `h0` only. `b2` is counted over `b1`,
    which has `h0` in its past (`b1` is the first row of the other line). If `b2` counts under
    the checkpoint, `a1` is void, whatever it states and whoever signed it. -/
theorem depth_race (A : Row → Prop) (a1 b1 b2 h0 : Row)
    (ha : ∀ h, head a1 h → h = h0) (ha0 : head a1 h0) (hb2 : head b2 b1)
    (hdeep : TransGen parent h0 b1) (hconc : conc parent b2 a1)
    (hcount : CP.cpCounts parent head isAct clashes overrules ent A b2) :
    ¬ CP.cpPoss parent head isAct clashes overrules ent A a1 :=
  CP.stale_never_counts parent head isAct clashes overrules ent A b2 a1 hcount hconc
    ⟨⟨h0, ha0⟩, fun h hh => ⟨b1, hb2, ha h hh ▸ hdeep⟩⟩

/-- (Rejected rule) And never the reverse: the shorter line leaves the longer behind by no
    row. The race is won by depth. -/
theorem race_one_way (wf : WellFounded parent) (a1 b1 b2 h0 : Row)
    (ha : ∀ h, head a1 h → h = h0) (hb2 : head b2 b1) (hdeep : TransGen parent h0 b1) :
    ¬ CP.olderHeads parent head b2 a1 :=
  fun ⟨_, ho⟩ =>
    let ⟨h', hh', ht⟩ := ho b1 hb2
    wf_asymm (WellFounded.transGen wf) h0 b1 hdeep (ha h' hh' ▸ ht)

/-- WITHOUT it (the rule). A reader with no line judges `a1` by the plain cut and the built-on
    clause: no row of the other line, however deep, enters, unless the cut itself voids `a1`. -/
theorem no_race_without (A : Row → Prop) (a1 : Row) :
    rdCounts parent head isAct clashes overrules ent (fun _ => False) A a1 ↔
      (cutCounts parent isAct clashes overrules ent A a1 ∧ isAct a1 ∧
        ∀ h, head a1 h → isAct h →
          rdCounts parent head isAct clashes overrules ent (fun _ => False) A h) :=
  no_line_is_plain parent head isAct _ a1

end Race

end Reader

/-! ## Axioms used -/

#print axioms Reader.rd_iff
#print axioms Reader.rd_function
#print axioms Reader.rd_unique
#print axioms Reader.acked_counts
#print axioms Reader.line_voids_old_fork
#print axioms Reader.old_fork_void_for_ever
#print axioms Reader.built_on_void
#print axioms Reader.line_void
#print axioms Reader.built_on_cut_void
#print axioms Reader.no_line_is_plain
#print axioms Reader.line_no_obstacle
#print axioms Reader.line_no_obstacle_all
#print axioms Reader.sibling_waits
#print axioms Reader.merge_accepted
#print axioms Reader.rdCounts_function
#print axioms Reader.rdCounts_sub_cut
#print axioms Reader.rdCounts_sub_rdPoss
#print axioms Reader.depth_race
#print axioms Reader.race_one_way
#print axioms Reader.no_race_without

end Kernel
