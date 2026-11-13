/-
  Harden3.lean — the checkpoint of KERNEL.md section 8a

  A counted row on a roster's lineage names the head it is counted over. The checkpoint: a
  counted act concurrent with a counting counted act, and naming only heads strictly older
  than the heads that act names, does not count.

  Part 1. The group checkpoint is the cut of Seat.lean with one more way to clash. Function
          of the kept set; the bound on backdating; re-signing.
  Part 2. The reader's acknowledged line: its own checkpoint, which no other voids.
  Part 3. Why a window's answers are outside it.
  Part 4. The witness of Part 3 on nine rows.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports Harden2.lean.
-/

import Harden2

namespace Kernel

namespace Harden

open Order Relation Causal

namespace CP

/-! ## Part 1. The group checkpoint -/

section Acts

variable {Row : Type}
variable (parent : Row → Row → Prop)
/- `head r h`: the counted act `r` names `h` as a head it is counted over. -/
variable (head : Row → Row → Prop)

/-- `r` names a head, and every head `r` names is strictly in the past of a head `c` names. -/
def olderHeads (r c : Row) : Prop :=
  (∃ h, head r h) ∧ ∀ h, head r h → ∃ h', head c h' ∧ TransGen parent h h'

/-- An act that names a head not strictly in the past of any head `k` names is not older. -/
theorem not_older_of_head (r k h : Row) (hr : head r h)
    (hno : ∀ h', head k h' → ¬ TransGen parent h h') : ¬ olderHeads parent head r k :=
  fun ho => let ⟨h', hk, ha⟩ := ho.2 h hr; hno h' hk ha

/-- Two acts counted over one and the same head: neither is older. They wait (KERNEL.md 7). -/
theorem same_head_not_older (wf : WellFounded parent) (r k h : Row) (hr : head r h)
    (hk : ∀ h', head k h' → h' = h) : ¬ olderHeads parent head r k :=
  not_older_of_head parent head r k h hr
    (fun h' hk' ha => Recount.anc_irrefl parent wf h (hk h' hk' ▸ ha))

variable (isAct : Row → Prop) (clashes overrules : Row → Row → Prop)
variable (ent : (Row → Prop) → (Row → Prop) → Row → Prop)

/-- THE CHECKPOINT, as one more clash of the cut: `x` clashes with `c` when it did before, or
    when `c` names only heads older than the heads `x` names. `Kernel.cutT` then says: a
    counted act counts iff it is concluded, entitled at its head, no counting act it is
    concurrent with clashes with it or leaves it behind, and none that names it overrules it. -/
def cpClash (x c : Row) : Prop := clashes x c ∨ olderHeads parent head c x

/-- A counted act counts, under the checkpoint. -/
def cpCounts (A : Row → Prop) : Row → Prop :=
  cutCounts parent isAct (cpClash parent head clashes) overrules ent A

/-- Counts or is contested. -/
def cpPoss (A : Row → Prop) : Row → Prop :=
  cutPoss parent isAct (cpClash parent head clashes) overrules ent A

/-- (1) A function of the offered set (`Kernel.cut_status_function`). -/
theorem cp_function (C : (Row → Prop) → Row → Prop) (S S' : Row → Prop) (h : ∀ r, S r ↔ S' r) :
    cpCounts parent head isAct clashes overrules ent (C S)
        = cpCounts parent head isAct clashes overrules ent (C S') ∧
      cpPoss parent head isAct clashes overrules ent (C S)
        = cpPoss parent head isAct clashes overrules ent (C S') :=
  cut_status_function parent isAct (cpClash parent head clashes) overrules ent C S S' h

/-- The status is still the alternating fixed point of an antitone operator. -/
theorem cp_anti (hent : EntAnti ent) (A : Row → Prop) :
    Anti (cutT parent isAct (cpClash parent head clashes) overrules ent A) :=
  cutT_anti parent isAct (cpClash parent head clashes) overrules ent hent A

/-- (2) THE BOUND ON BACKDATING, at one set. `k` is a checkpoint: a counted act that counts.
    A counted act concurrent with `k` that names only heads older than the heads `k` names
    is void: it neither counts nor is contested. -/
theorem stale_never_counts (A : Row → Prop) (k r : Row)
    (hk : cpCounts parent head isAct clashes overrules ent A k) (hc : conc parent k r)
    (ho : olderHeads parent head r k) :
    ¬ cpPoss parent head isAct clashes overrules ent A r :=
  fun h => h.2.2.2.1 ⟨k, hk, hc, Or.inr ho⟩

/-- (2), read the other way: what a backdated act needs. A counted act that counts, or is
    even contested, names no head at all, or names a head that is not strictly in the past of
    any head named by a checkpoint concurrent with it. An old count can act only on the
    heads the newest counted rows are themselves counted over. -/
theorem backdating_bound (A : Row → Prop) (k r : Row)
    (hr : cpPoss parent head isAct clashes overrules ent A r)
    (hk : cpCounts parent head isAct clashes overrules ent A k) (hc : conc parent k r) :
    (¬ ∃ h, head r h) ∨ ∃ h, head r h ∧ ¬ ∃ h', head k h' ∧ TransGen parent h h' := by
  cases Classical.em (∃ h, head r h ∧ ¬ ∃ h', head k h' ∧ TransGen parent h h') with
  | inl h => exact Or.inr h
  | inr hn =>
    refine Or.inl (fun hex => stale_never_counts parent head isAct clashes overrules ent A k r hk hc
      ⟨hex, fun h hh => Classical.byContradiction fun hc' => hn ⟨h, hh, hc'⟩⟩ hr)

/-- (2), for ever. The checkpoint `k` is kept at `S`. A row `r` first offered afterwards,
    that does not name `k` and names only heads older than the heads `k` names, is void at
    every later set in which `k` still counts, whatever else is held. "Until the next counted
    row on a newer head": from the moment such a `k` is kept, nothing signed on the older
    heads without naming it ever counts. -/
theorem backdated_after_checkpoint (wf : WellFounded parent) (wellFormed : Row → Prop)
    (S : Row → Prop) (k r : Row) (hk : kept parent wf wellFormed S k) (hr : ¬ S r)
    (hnn : ¬ TransGen parent k r) (ho : olderHeads parent head r k) (A' : Row → Prop)
    (hc : cpCounts parent head isAct clashes overrules ent A' k) :
    ¬ cpPoss parent head isAct clashes overrules ent A' r :=
  have hn := new_row_not_ancestor parent wf wellFormed S r k hk hr
  stale_never_counts parent head isAct clashes overrules ent A' k r hc ⟨hnn, hn.2, hn.1⟩ ho

/-- (3) RE-SIGNING. The same act signed again naming the checkpoint is not concurrent with
    it: the checkpoint says nothing against it, and it is judged at the head it names. -/
theorem resigned_not_left_behind (k r' : Row) (hn : TransGen parent k r') :
    ¬ conc parent k r' :=
  fun h => h.1 hn

/-- An act whose heads count for nothing is not entitled, where entitlement asks that each
    head act it names passes under the same voiding set (`hbuild`: the roster-version shape,
    where a version needs the versions it builds on). Then a line built on a void act is void
    row by row. Without `hbuild` only the first row of such a line is reached by the
    checkpoint. -/
theorem built_on_void_is_void (A : Row → Prop)
    (hbuild : ∀ X c h, ent A X c → head c h → isAct h →
      cutT parent isAct (cpClash parent head clashes) overrules ent A X h)
    (c h : Row) (hh : head c h) (ha : isAct h)
    (hv : ¬ cpPoss parent head isAct clashes overrules ent A h) :
    ¬ cpPoss parent head isAct clashes overrules ent A c :=
  fun hc => hv (hbuild _ c h hc.2.2.1 hh ha)

end Acts

section Voices

variable {Row Key T : Type}
variable (signer : Row → Key) (holder : T → Key)
variable (voice : Row → Row → Prop) (member : T → Row → Prop) (need : T → Nat)

/-- (3) A count is a count of keys. Whatever rows are its voices, `confGroup` gives a list
    of distinct keys, as many as the count needs, each a seated member with a voice. -/
theorem count_is_of_keys (Q : T → Prop) (A : Row → Prop) (o : Row) (t : T)
    (h : confGroup signer holder voice member need Q A o t) :
    ∃ ks : List Key, ks.Nodup ∧ need t ≤ ks.length ∧
      ∀ k, k ∈ ks → ∃ v, A v ∧ voice v o ∧ signer v = k ∧
        ∃ t', Q t' ∧ holder t' = k ∧ member t' o := by
  obtain ⟨l, hp, hn, hv⟩ := h
  refine ⟨l.map signer, List.pairwise_map.2 hp, by rw [List.length_map]; exact hn, fun k hk => ?_⟩
  obtain ⟨v, hvl, e⟩ := List.mem_map.1 hk
  obtain ⟨a, b, t', c, d, f⟩ := hv v hvl
  exact ⟨v, a, b, e, t', c, d.trans e, f⟩

/-- (3) The same voice signed again is the same voice. Two rows by one key are never both
    counted in one count: a cosigner who signs its voice again, naming the checkpoint, has
    one voice and not two. -/
theorem resigned_is_one_voice (l : List Row) (hp : l.Pairwise (fun u v => signer u ≠ signer v))
    (v v' : Row) (hv : v ∈ l) (hv' : v' ∈ l) (hs : signer v = signer v') : v = v' :=
  pairwise_inj signer l hp v v' hv hv' hs

end Voices

/-! ## Part 2. The reader's acknowledged line

  `mine`: the counted acts this reader has acknowledged, with the counted acts in their past.
  For this reader they are checkpoints whether or not they count for anyone else, and no
  checkpoint voids them. -/

section Reader

variable {Row : Type}
variable (parent : Row → Row → Prop) (head : Row → Row → Prop)
variable (isAct : Row → Prop) (clashes overrules : Row → Row → Prop)
variable (ent : (Row → Prop) → (Row → Prop) → Row → Prop)
variable (mine : Row → Prop)

/-- The reader's operator. As `cutT` with the checkpoint, except: an act of the reader's line
    is left behind by nothing, and a concluded act of the reader's line leaves others behind
    whatever does the voiding. -/
def rdT (A X : Row → Prop) (c : Row) : Prop :=
  A c ∧ isAct c ∧ ent A X c ∧
    (mine c ∨ ¬ ∃ x, (X x ∨ (mine x ∧ A x ∧ isAct x)) ∧ conc parent x c ∧
      olderHeads parent head c x) ∧
    (¬ ∃ x, X x ∧ conc parent x c ∧ clashes x c) ∧
    (¬ ∃ x, X x ∧ TransGen parent c x ∧ overrules x c)

def rdCounts (A : Row → Prop) : Row → Prop :=
  sure (rdT parent head isAct clashes overrules ent mine A)

def rdPoss (A : Row → Prop) : Row → Prop :=
  poss (rdT parent head isAct clashes overrules ent mine A)

/-- A function of the offered set and the reader's line. -/
theorem rd_function (C : (Row → Prop) → Row → Prop) (mineOf : (Row → Prop) → Row → Prop)
    (S S' : Row → Prop) (h : ∀ r, S r ↔ S' r) :
    rdCounts parent head isAct clashes overrules ent (mineOf S) (C S)
        = rdCounts parent head isAct clashes overrules ent (mineOf S') (C S') ∧
      rdPoss parent head isAct clashes overrules ent (mineOf S) (C S)
        = rdPoss parent head isAct clashes overrules ent (mineOf S') (C S') := by
  have e : S = S' := funext fun r => propext (h r)
  rw [e]
  exact ⟨rfl, rfl⟩

/-- Antitone, so the status of Seat.lean Part B is defined for it. -/
theorem rdT_anti (hent : EntAnti ent) (A : Row → Prop) :
    Anti (rdT parent head isAct clashes overrules ent mine A) :=
  fun X Y hXY c ⟨h1, h2, h3, h4, h5, h6⟩ =>
    ⟨h1, h2, hent A X Y hXY c h3,
     h4.elim Or.inl (fun hn => Or.inr (fun ⟨x, hx, r⟩ =>
       hn ⟨x, hx.elim (fun a => Or.inl (hXY x a)) Or.inr, r⟩)),
     fun ⟨x, hx, r⟩ => h5 ⟨x, hXY x hx, r⟩, fun ⟨x, hx, r⟩ => h6 ⟨x, hXY x hx, r⟩⟩

/-- A reader that has acknowledged nothing has the group checkpoint and no more. -/
theorem no_line_is_group (A X : Row → Prop) (c : Row) :
    rdT parent head isAct clashes overrules ent (fun _ => False) A X c ↔
      cutT parent isAct (cpClash parent head clashes) overrules ent A X c := by
  constructor
  · intro ⟨h1, h2, h3, h4, h5, h6⟩
    refine ⟨h1, h2, h3, fun ⟨x, hx, hc, hcl⟩ => ?_, h6⟩
    cases hcl with
    | inl hcl => exact h5 ⟨x, hx, hc, hcl⟩
    | inr ho => exact h4.elim id (fun hn => hn ⟨x, Or.inl hx, hc, ho⟩)
  · intro ⟨h1, h2, h3, h4, h5⟩
    exact ⟨h1, h2, h3,
      Or.inr (fun ⟨x, hx, hc, ho⟩ => hx.elim (fun hx => h4 ⟨x, hx, hc, Or.inr ho⟩) (fun hx => hx.1)),
      fun ⟨x, hx, hc, hcl⟩ => h4 ⟨x, hx, hc, Or.inl hcl⟩, h5⟩

/-- No checkpoint voids what the reader has acknowledged: for an act of its line the
    checkpoint clause is gone. -/
theorem acked_not_left_behind (A X : Row → Prop) (c : Row) (hm : mine c) :
    rdT parent head isAct clashes overrules ent mine A X c ↔
      (A c ∧ isAct c ∧ ent A X c ∧ (¬ ∃ x, X x ∧ conc parent x c ∧ clashes x c) ∧
        (¬ ∃ x, X x ∧ TransGen parent c x ∧ overrules x c)) :=
  ⟨fun ⟨h1, h2, h3, _, h5, h6⟩ => ⟨h1, h2, h3, h5, h6⟩,
   fun ⟨h1, h2, h3, h5, h6⟩ => ⟨h1, h2, h3, Or.inl hm, h5, h6⟩⟩

/-- (4) THE ACKNOWLEDGED LINE. `m` is a concluded act of the reader's line. An act `v` outside
    the line, concurrent with `m` (neither an ancestor nor a descendant of it), that names
    only heads older than the heads `m` names, passes under no voiding set: it is void for
    this reader. Nothing is asked about whether `m` counts for anyone else, about who signed
    `v`, or about how many signed it. -/
theorem line_voids_old_fork (A X : Row → Prop) (m v : Row) (hm : mine m) (hAm : A m)
    (hact : isAct m) (hv : ¬ mine v) (hc : conc parent m v) (ho : olderHeads parent head v m) :
    ¬ rdT parent head isAct clashes overrules ent mine A X v :=
  fun h => h.2.2.2.1.elim hv (fun hn => hn ⟨m, Or.inr ⟨hm, hAm, hact⟩, hc, ho⟩)

/-- So it neither counts nor is contested, for that reader. -/
theorem old_fork_void_for_reader (A : Row → Prop) (m v : Row) (hm : mine m) (hAm : A m)
    (hact : isAct m) (hv : ¬ mine v) (hc : conc parent m v) (ho : olderHeads parent head v m) :
    ¬ rdPoss parent head isAct clashes overrules ent mine A v :=
  line_voids_old_fork parent head isAct clashes overrules ent mine A _ m v hm hAm hact hv hc ho

/-- (4), for ever: the acknowledged act is kept at `S`; the forged act is offered later and
    does not name it. It is void for this reader at every later set in which the
    acknowledged act is concluded. -/
theorem old_fork_void_for_ever (wf : WellFounded parent) (wellFormed : Row → Prop)
    (S : Row → Prop) (m v : Row) (hk : kept parent wf wellFormed S m) (hv' : ¬ S v)
    (hnn : ¬ TransGen parent m v) (hm : mine m) (hact : isAct m) (hv : ¬ mine v)
    (ho : olderHeads parent head v m) (A' : Row → Prop) (hAm : A' m) :
    ¬ rdPoss parent head isAct clashes overrules ent mine A' v :=
  have hn := new_row_not_ancestor parent wf wellFormed S v m hk hv'
  old_fork_void_for_reader parent head isAct clashes overrules ent mine A' m v hm hAm hact hv
    ⟨hnn, hn.2, hn.1⟩ ho

/-- A forged line, row by row, where entitlement asks that the head acts pass (`hbuild`, as
    in `built_on_void_is_void`): what is built on an act void for the reader is void for the
    reader. -/
theorem built_on_void_for_reader (A : Row → Prop)
    (hbuild : ∀ X c h, ent A X c → head c h → isAct h →
      rdT parent head isAct clashes overrules ent mine A X h)
    (c h : Row) (hh : head c h) (ha : isAct h)
    (hv : ¬ rdPoss parent head isAct clashes overrules ent mine A h) :
    ¬ rdPoss parent head isAct clashes overrules ent mine A c :=
  fun hc => hv (hbuild _ c h hc.2.2.1 hh ha)

/-- Where the reader's line is no obstacle. If no act of the line that is concurrent with `s`
    leaves it behind, the reader judges `s` exactly as a reader with no acknowledgement
    does: by the group checkpoint. -/
theorem line_no_obstacle (A X : Row → Prop) (s : Row) (hs : ¬ mine s)
    (hno : ∀ m, mine m → conc parent m s → ¬ olderHeads parent head s m) :
    rdT parent head isAct clashes overrules ent mine A X s ↔
      cutT parent isAct (cpClash parent head clashes) overrules ent A X s := by
  constructor
  · intro ⟨h1, h2, h3, h4, h5, h6⟩
    refine ⟨h1, h2, h3, fun ⟨x, hx, hc, hcl⟩ => ?_, h6⟩
    cases hcl with
    | inl hcl => exact h5 ⟨x, hx, hc, hcl⟩
    | inr ho => exact h4.elim hs (fun hn => hn ⟨x, Or.inl hx, hc, ho⟩)
  · intro ⟨h1, h2, h3, h4, h5⟩
    exact ⟨h1, h2, h3,
      Or.inr (fun ⟨x, hx, hc, ho⟩ => hx.elim (fun hx => h4 ⟨x, hx, hc, Or.inr ho⟩)
        (fun hx => hno x hx.1 hc ho)),
      fun ⟨x, hx, hc, hcl⟩ => h4 ⟨x, hx, hc, Or.inl hcl⟩, h5⟩

/-- (4) A SIBLING WAITS. The reader acknowledged `H`, counted over the one head `h`; the rest
    of its line is `h` or in the past of `h`. An act `s` counted over the same head `h`
    (which it names) is not voided by the line: the reader judges it as everyone does, and
    the two wait as two tips. -/
theorem sibling_waits (wf : WellFounded parent) (A X : Row → Prop) (H h s : Row)
    (hline : ∀ m, mine m → m = H ∨ m = h ∨ TransGen parent m h)
    (hH : ∀ h', head H h' → h' = h) (hsh : head s h) (hnamed : parent h s) (hs : ¬ mine s) :
    rdT parent head isAct clashes overrules ent mine A X s ↔
      cutT parent isAct (cpClash parent head clashes) overrules ent A X s := by
  apply line_no_obstacle parent head isAct clashes overrules ent mine A X s hs
  intro m hm hc ho
  cases hline m hm with
  | inl e => exact same_head_not_older parent head wf s H h hsh hH (e ▸ ho)
  | inr h' =>
    cases h' with
    | inl e => exact hc.1 (e ▸ TransGen.single hnamed)
    | inr ha => exact hc.1 (TransGen.tail ha hnamed)

/-- (4) A MERGE IS ACCEPTED. An act that names the acknowledged `H` (has it in its past) is
    concurrent with no act of the line: the reader judges it as everyone does. -/
theorem merge_accepted (A X : Row → Prop) (H mg : Row)
    (hline : ∀ m, mine m → m = H ∨ TransGen parent m H) (hnames : TransGen parent H mg)
    (hs : ¬ mine mg) :
    rdT parent head isAct clashes overrules ent mine A X mg ↔
      cutT parent isAct (cpClash parent head clashes) overrules ent A X mg := by
  apply line_no_obstacle parent head isAct clashes overrules ent mine A X mg hs
  intro m hm hc _
  cases hline m hm with
  | inl e => exact hc.1 (e ▸ hnames)
  | inr ha => exact hc.1 (anc_trans ha hnames)

end Reader

/-! ## Part 3. Why a window's answers are outside the checkpoint

  The checkpoint applied to answers (checkpoint.py `stale_answer`): a concurrent answer `x`
  to window `p` is not counted when a checkpoint `c` is concurrent with it, names a head
  newer than every head `p` was opened on, and has everything `x` names in its past. -/

section Answers

variable {Row Key Out : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key)
variable (answers : Row → Row → Prop)
variable (outcome : (Row → Prop) → Out) (states : Row → Out)
variable (head : Row → Row → Prop)

/-- `K`: the checkpoints (the counted acts on the window's object that count). -/
def staleAns (K : Row → Prop) (p x : Row) : Prop :=
  ∃ c, K c ∧ conc parent c x ∧ olderHeads parent head p c ∧ ∀ n, parent n x → TransGen parent n c

def countedK (K A : Row → Prop) (p lam x : Row) : Prop :=
  Recount.pastAns parent answers A p lam x ∨
    (Recount.concAns parent answers A p lam x ∧ ¬ staleAns parent head K p x)

/-- Recount with the checkpoint applied to answers. Not the kernel's rule. -/
def standsK (K A : Row → Prop) (p lam : Row) : Prop :=
  Recount.honest parent answers outcome states A p lam ∧
    outcome (countedK parent answers head K A p lam) = states lam

theorem no_checkpoint_is_recount (A : Row → Prop) (p lam : Row) :
    standsK parent answers outcome states head (fun _ => False) A p lam ↔
      Recount.stands parent answers outcome states A p lam := by
  have e : countedK parent answers head (fun _ => False) A p lam
      = Recount.recounted parent answers A p lam :=
    funext fun x => propext
      ⟨fun h => h.elim Or.inl (fun h => Or.inr h.1),
       fun h => h.elim Or.inl (fun h => Or.inr ⟨h, fun ⟨_, hk, _⟩ => hk⟩)⟩
  unfold standsK Recount.stands
  rw [e]

/-- (5) THE MAJORITY VOIDS ANY ANSWER. Let `x` be any row that names `p`, where `p` names the
    heads it was opened on. Two counted rows suffice, and neither needs anything of `x`'s
    signer: `c1`, which has in its past everything `x` names, and `c2`, counted over the head
    `c1` (which it names), concurrent with `x`. If `c2` counts as a checkpoint, `x` is stale.
    Every hypothesis is about `c1`, `c2` and the opener: who signed `x`, what it says, and how
    timely it was do not enter. -/
theorem two_rows_make_stale (K : Row → Prop) (p x c1 c2 h0 : Row)
    (hp : parent p x) (hh : head p h0) (hnamed : ∀ h, head p h → parent h p)
    (hc1 : ∀ n, parent n x → TransGen parent n c1)
    (hhead : head c2 c1) (hpar : parent c1 c2) (hconc : conc parent c2 x) (hK : K c2) :
    staleAns parent head K p x :=
  ⟨c2, hK, hconc,
   ⟨⟨h0, hh⟩, fun h hhp => ⟨c1, hhead, anc_trans (TransGen.single (hnamed h hhp)) (hc1 p hp)⟩⟩,
   fun n hn => TransGen.tail (hc1 n hn) hpar⟩

/-- So that answer is not counted for any landing that does not itself name it. For every
    standing honest answer of a minority, the keys that make the count have a sequence of two
    counted rows after which it is not counted. -/
theorem checkpoint_voids_any_answer (K A : Row → Prop) (p lam x c1 c2 h0 : Row)
    (hp : parent p x) (hh : head p h0) (hnamed : ∀ h, head p h → parent h p)
    (hc1 : ∀ n, parent n x → TransGen parent n c1)
    (hhead : head c2 c1) (hpar : parent c1 c2) (hconc : conc parent c2 x) (hK : K c2)
    (hnp : ¬ TransGen parent x lam) :
    ¬ countedK parent answers head K A p lam x :=
  fun h => h.elim (fun h => hnp h.2.2)
    (fun h => h.2 (two_rows_make_stale parent head K p x c1 c2 h0 hp hh hnamed hc1 hhead hpar hconc hK))

/-- And the reply to it. The same answer signed again naming the checkpoint is not stale
    against that checkpoint; `two_rows_make_stale` applies to the new row as it did to the
    old. One counted row a round against one re-signature. -/
theorem resigned_answer_not_stale_against (c x' : Row) (hn : TransGen parent c x') :
    ¬ conc parent c x' :=
  fun h => h.1 hn

variable (wf : WellFounded parent) (wellFormed : Row → Prop)
variable (C : (Row → Prop) → Row → Prop)

/-- (5), WITHOUT the checkpoint on answers. Under recount, whether a concluded answer is
    counted for a landing is fixed for ever: no row offered later, counted or not, by anyone,
    changes it. -/
theorem without_checkpoint_fixed
    (hCk : ∀ S r, C S r → kept parent wf wellFormed S r)
    (hfin : ∀ S x r, kept parent wf wellFormed S r → ¬ S x →
      (C S r ↔ C (fun q => S q ∨ q = x) r))
    (S S' : Row → Prop) (p lam x : Row) (hg : Recount.Grows S S') (hx : C S x) :
    Recount.recounted parent answers (C S') p lam x ↔ Recount.recounted parent answers (C S) p lam x := by
  rw [Recount.recounted_iff_notLate parent answers wf, Recount.recounted_iff_notLate parent answers wf]
  exact ⟨fun h => ⟨hx, h.2.1, h.2.2⟩,
    fun h => Recount.notLate_grows parent answers wf wellFormed C hCk hfin S S' p lam x hg h⟩

variable (ends : Row → Key → Prop)

/-- (5), with rule F1 in force. A counted answer stays counted against every later row,
    counted or not, except an ending of its own signer's seat that does not have it in its
    past. A count that leaves the answer unnamed while admitting, removing or appointing
    OTHER keys changes nothing; a row that ends the answerer's own seat without naming the
    answer does, and that is rule F1. -/
theorem counted_survives_others
    (hCk : ∀ S r, C S r → kept parent wf wellFormed S r)
    (hfin : ∀ S x r, kept parent wf wellFormed S r → ¬ S x →
      (C S r ↔ C (fun q => S q ∨ q = x) r))
    (ES ES' S S' : Row → Prop) (p lam x : Row) (hg : Recount.Grows S S')
    (hE : ∀ e, ES' e → ends e (signer x) → ES e ∨ TransGen parent x e)
    (h : F1.countedE parent signer answers ends ES (C S) p lam x) :
    F1.countedE parent signer answers ends ES' (C S') p lam x := by
  cases h with
  | inl h =>
    exact Or.inl ⟨(Recount.concl_grows parent wf wellFormed C hfin S S' x hg (hCk S x h.1)).1 h.1,
      h.2.1, h.2.2⟩
  | inr h =>
    refine Or.inr ⟨⟨(Recount.concl_grows parent wf wellFormed C hfin S S' x hg
      (hCk S x h.1.1)).1 h.1.1, h.1.2.1, h.1.2.2⟩, fun ⟨e, he, hend, hn⟩ => ?_⟩
    cases hE e he hend with
    | inl hes => exact h.2 ⟨e, hes, hend, hn⟩
    | inr ha => exact hn ha

end Answers

end CP

/-! ## Part 4. The witness: the majority voids the moderator (attacks.py `checkpoint_price`)

  `h0`: the head the window is opened on. `p`: the report. `a`: the moderator's answer, in
  time, naming `p`. `r`, `L`: a member's receipt and landing "fallback", which leaves `a`
  unnamed. `s1`: a counted row by the majority, naming `p`. `s2`: a second, counted over `s1`.
  `a2`: the moderator answers again, naming `s2`. `s3`: a third counted row, over `s2`. The
  table: answered if the moderator's answer is counted, else the members' fallback. -/

namespace ModRows

inductive R | h0 | p | a | r | L | s1 | s2 | a2 | s3
  deriving DecidableEq, Repr

inductive Out | answered | fallback
  deriving DecidableEq, Repr

open R

def parentB : R → R → Bool
  | h0, p => true | p, a => true | p, r => true | r, L => true | p, s1 => true | s1, s2 => true
  | s2, a2 => true | p, a2 => true | s2, s3 => true
  | _, _ => false
def parent (x y : R) : Prop := parentB x y = true

def ancB : R → R → Bool
  | h0, h0 => false | h0, _ => true
  | p, h0 => false | p, p => false | p, _ => true
  | r, L => true
  | s1, s2 => true | s1, a2 => true | s1, s3 => true
  | s2, a2 => true | s2, s3 => true
  | _, _ => false

theorem anc_step1 : ∀ x y, parent x y → ancB x y = true := by
  intro x y; cases x <;> cases y <;> simp [parent, parentB, ancB]

theorem anc_step2 : ∀ x y z, ancB x y = true → parent y z → ancB x z = true := by
  intro x y z; cases x <;> cases y <;> cases z <;> simp [parent, parentB, ancB]

theorem anc_sound {x y : R} (h : TransGen parent x y) : ancB x y = true := by
  induction h with
  | single h => exact anc_step1 _ _ h
  | tail _ h ih => exact anc_step2 _ _ _ ih h

def ansB : R → Bool | a => true | a2 => true | _ => false
def answers (x q : R) : Prop := ansB x = true ∧ q = p

def headB : R → R → Bool | p, h0 => true | s1, h0 => true | s2, s1 => true | s3, s2 => true | _, _ => false
def head (x h : R) : Prop := headB x h = true

open Classical in
noncomputable def table (X : R → Prop) : Out := if X a ∨ X a2 then Out.answered else Out.fallback

def says (_ : R) : Out := Out.fallback

def All (_ : R) : Prop := True
/-- After the majority's two counted rows. -/
abbrev A1 (x : R) : Prop := x ≠ a2 ∧ x ≠ s3
/-- After the moderator answers again. -/
abbrev A2 (x : R) : Prop := x ≠ s3

def K0 (_ : R) : Prop := False
def K2 (c : R) : Prop := c = s2
def K3 (c : R) : Prop := c = s2 ∨ c = s3

theorem h0_s1 : TransGen parent h0 s1 := TransGen.tail (b := p) (TransGen.single rfl) rfl
theorem p_s2 : TransGen parent p s2 := TransGen.tail (b := s1) (TransGen.single rfl) rfl
theorem h0_s2 : TransGen parent h0 s2 := TransGen.tail (b := s1) h0_s1 rfl
theorem p_s3 : TransGen parent p s3 := TransGen.tail (b := s2) p_s2 rfl

theorem no_past (A : R → Prop) :
    ¬ (Recount.pastAns parent answers A p L a ∨ Recount.pastAns parent answers A p L a2) :=
  fun h => h.elim (fun h => absurd (anc_sound h.2.2) (by decide))
    (fun h => absurd (anc_sound h.2.2) (by decide))

theorem fallback_honest (A : R → Prop) (hl : A L) :
    Recount.honest parent answers table says A p L := by
  refine ⟨hl, ?_⟩
  unfold table
  rw [if_neg (no_past A)]
  rfl

theorem a_conc : conc parent a L :=
  ⟨fun h => absurd (anc_sound h) (by decide), fun h => absurd (anc_sound h) (by decide), by decide⟩

theorem a2_conc : conc parent a2 L :=
  ⟨fun h => absurd (anc_sound h) (by decide), fun h => absurd (anc_sound h) (by decide), by decide⟩

/-- The two counted rows make the moderator's answer stale: the general theorem, here. -/
theorem a_stale (K : R → Prop) (hK : K s2) : CP.staleAns parent head K p a :=
  CP.two_rows_make_stale parent head K p a s1 s2 h0 rfl rfl
    (fun h hh => by
      have hh' : headB p h = true := hh
      cases h <;> simp [headB] at hh'
      rfl)
    (fun n hn => by
      have hn' : parentB n a = true := hn
      cases n <;> simp [parentB] at hn'
      exact TransGen.single rfl)
    rfl rfl
    ⟨fun h => absurd (anc_sound h) (by decide), fun h => absurd (anc_sound h) (by decide), by decide⟩
    hK

/-- And the third makes the second answer stale. -/
theorem a2_stale (K : R → Prop) (hK : K s3) : CP.staleAns parent head K p a2 :=
  ⟨s3, hK,
   ⟨fun h => absurd (anc_sound h) (by decide), fun h => absurd (anc_sound h) (by decide), by decide⟩,
   ⟨⟨h0, rfl⟩, fun h hh => by
      have hh' : headB p h = true := hh
      cases h <;> simp [headB] at hh'
      exact ⟨s2, rfl, h0_s2⟩⟩,
   fun n hn => by
      have hn' : parentB n a2 = true := hn
      cases n <;> simp [parentB] at hn'
      · exact p_s3
      · exact TransGen.single rfl⟩

/-- WITHOUT the checkpoint on answers (the kernel's rule). The moderator answered in time:
    the members' fallback does not stand, whatever counted rows the majority signs after. -/
theorem off_fallback_never_stands (A : R → Prop) (ha : A a) :
    ¬ CP.standsK parent answers table says head K0 A p L := by
  intro hs
  have h : CP.countedK parent answers head K0 A p L a ∨ CP.countedK parent answers head K0 A p L a2 :=
    Or.inl (Or.inr ⟨⟨ha, ⟨rfl, rfl⟩, a_conc⟩, fun ⟨_, hk, _⟩ => hk⟩)
  have h2 := hs.2
  unfold table at h2
  rw [if_pos h] at h2
  exact absurd h2 (by decide)

/-- WITH the checkpoint on answers. After two counted rows that leave the answer unnamed,
    the fallback stands over a moderator who answered in time. -/
theorem on_two_rows_void_the_moderator :
    CP.standsK parent answers table says head K2 A1 p L := by
  refine ⟨fallback_honest A1 (by decide), ?_⟩
  have h : ¬ (CP.countedK parent answers head K2 A1 p L a ∨
      CP.countedK parent answers head K2 A1 p L a2) := by
    intro h
    cases h with
    | inl h => exact h.elim (fun h => no_past A1 (Or.inl h)) (fun h => h.2 (a_stale K2 rfl))
    | inr h => exact h.elim (fun h => no_past A1 (Or.inr h)) (fun h => h.1.1.1 rfl)
  unfold table
  rw [if_neg h]
  rfl

/-- The moderator signs again, naming the checkpoint: it is counted, and the fallback does
    not stand. -/
theorem on_resigned_counts :
    ¬ CP.standsK parent answers table says head K2 A2 p L := by
  intro hs
  have h : CP.countedK parent answers head K2 A2 p L a ∨ CP.countedK parent answers head K2 A2 p L a2 :=
    Or.inr (Or.inr ⟨⟨by decide, ⟨rfl, rfl⟩, a2_conc⟩, fun ⟨c, hk, hc, _⟩ => by
      have e : c = s2 := hk
      subst e
      exact hc.1 (TransGen.single rfl)⟩)
  have h2 := hs.2
  unfold table at h2
  rw [if_pos h] at h2
  exact absurd h2 (by decide)

/-- One more counted row: both answers are stale and the fallback stands again. Whoever
    signed last has the answer. -/
theorem on_third_row_voids_again :
    CP.standsK parent answers table says head K3 All p L := by
  refine ⟨fallback_honest All trivial, ?_⟩
  have h : ¬ (CP.countedK parent answers head K3 All p L a ∨
      CP.countedK parent answers head K3 All p L a2) := by
    intro h
    cases h with
    | inl h => exact h.elim (fun h => no_past All (Or.inl h)) (fun h => h.2 (a_stale K3 (Or.inl rfl)))
    | inr h => exact h.elim (fun h => no_past All (Or.inr h)) (fun h => h.2 (a2_stale K3 (Or.inr rfl)))
  unfold table
  rw [if_neg h]
  rfl

end ModRows

/-! ## Axioms used -/

#print axioms CP.not_older_of_head
#print axioms CP.same_head_not_older
#print axioms CP.cp_function
#print axioms CP.cp_anti
#print axioms CP.stale_never_counts
#print axioms CP.backdating_bound
#print axioms CP.backdated_after_checkpoint
#print axioms CP.resigned_not_left_behind
#print axioms CP.built_on_void_is_void
#print axioms CP.count_is_of_keys
#print axioms CP.resigned_is_one_voice
#print axioms CP.rd_function
#print axioms CP.rdT_anti
#print axioms CP.no_line_is_group
#print axioms CP.acked_not_left_behind
#print axioms CP.line_voids_old_fork
#print axioms CP.old_fork_void_for_reader
#print axioms CP.old_fork_void_for_ever
#print axioms CP.built_on_void_for_reader
#print axioms CP.line_no_obstacle
#print axioms CP.sibling_waits
#print axioms CP.merge_accepted
#print axioms CP.no_checkpoint_is_recount
#print axioms CP.two_rows_make_stale
#print axioms CP.checkpoint_voids_any_answer
#print axioms CP.resigned_answer_not_stale_against
#print axioms CP.without_checkpoint_fixed
#print axioms CP.counted_survives_others
#print axioms ModRows.a_stale
#print axioms ModRows.a2_stale
#print axioms ModRows.off_fallback_never_stands
#print axioms ModRows.on_two_rows_void_the_moderator
#print axioms ModRows.on_resigned_counts
#print axioms ModRows.on_third_row_voids_again

end Harden

end Kernel
