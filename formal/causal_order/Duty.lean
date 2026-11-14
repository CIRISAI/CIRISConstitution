/-
  Duty.lean — the duty seat of a community (CC 4.5.4), stated on the definitions of the earlier files

  A community has members and duty holders, and no other tier. The founding record seats the duty
  holders who sign it. A duty seat is conferred by a strict majority of the duty holders, or by a lone
  holder, with the new holder's acceptance. It is withdrawn by a strict majority of the other holders,
  never on fewer than two voices where there are two or more. A removal from the roster ends a member's
  duty seats. With no duty holder left the members' count seats one.

  THE SETTING. A duty row `x` (a conferral or a withdrawal) is the relation it places, as RosterHead.lean
  takes a version as its own relation. It names a head, and `holders x` are the duty holders at that
  head, a list without repeats. `to x` is the key the row seats or unseats. A conferral is placed by a
  body, the duty holders, so it stands by `Consent.standsCounted`: the holders' consent is a count of
  their signatures carried on the row (`Consent.bodyConsents`), and the new holder's own yes. The lone
  holder's rule is not a second rule: it is the strict majority of one.

  Proved here.
   (1) `lone_holder_confers`: with one duty holder, its signature on the row and the new holder's yes
       seat; nobody else's signature is a voice.
   (2) `one_of_several_confers_nothing`: with two or more holders, a row that carries one holder's
       signature alone seats nobody; so do any number of such rows, each judged alone.
   (3) `majority_confers`, `confers_only_by_majority`: a strict majority of the holders' signatures,
       with the new holder's yes, seats; nothing less does.
   (4) `withdrawal_needs_two_others`, `two_holders_neither_unseats`, `lone_holder_not_unseated`,
       `one_holder_unseats_nothing`, `withdrawal_counts_of`: a withdrawal counts exactly on a strict
       majority of the other holders and at least two of them; of two neither unseats the other, and
       no holder unseats a lone one.
   (5) `conferrer_cannot_end`, `conferrer_cannot_lower_count`: once a duty seat stands, a withdrawal
       signed by a key that is not its holder, a conferrer's included, ends nothing.
   (6) `equals_perm`, `equals_rename`: every count above reads the holders only as a set: the same
       under any reordering of the holders (who was seated first) and under any renaming of keys.
   (7) `removal_ends_duty`, `removed_confers_nothing`, `removal_cuts_duty`: a key a standing version
       of the roster leaves out is no duty holder at that version or any head below it until a version
       lists it again; its signatures confer nothing there; and a removal that cuts its duty seat ends
       every conferral of that seat in the removal's past.
   (8) `none_left_members_seat`, `holders_left_members_do_not`: with no duty holder at the head a row
       names, the holders' count seats nobody and the members' count is the one way a duty seat is
       conferred; while a holder remains, the members' count is not that way.

  How F5 and Founders (Harden2.lean) stand against these is stated at the end of this file, and the
  claims that are false under the community law are kept under `Rejected` with their counter-models.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports Consent.lean, RosterHead.lean
  and Harden2.lean.
-/

import Consent
import RosterHead
import Harden2

namespace Kernel

namespace Duty

open Relation

/-! ### The two counts -/

/-- A strict majority of `n`: the least count `c` with `n < 2 * c`. Of one holder it is one. -/
def majority (n : Nat) : Nat := n / 2 + 1

theorem majority_iff (n c : Nat) : majority n ≤ c ↔ n < 2 * c := by
  unfold majority; omega

/-- The count of a withdrawal over `n` holders, the holder concerned among them: a strict majority
    of the `n - 1` others, and never fewer than two voices. -/
def wdNeed (n : Nat) : Nat := max 2 (majority (n - 1))

theorem wdNeed_iff (n c : Nat) : wdNeed n ≤ c ↔ 2 ≤ c ∧ n - 1 < 2 * c := by
  unfold wdNeed majority
  constructor
  · intro h; have := Nat.le_max_left 2 ((n - 1) / 2 + 1)
    have := Nat.le_max_right 2 ((n - 1) / 2 + 1); omega
  · intro ⟨h1, h2⟩; exact Nat.max_le.2 ⟨h1, by omega⟩

/-! ### Lists of keys -/

theorem nodup_map_inj {α β : Type} (f : α → β) (hf : ∀ a b, f a = f b → a = b) :
    ∀ l : List α, l.Nodup → (l.map f).Nodup
  | [], _ => List.Pairwise.nil
  | a :: l, h => by
    have ⟨h1, h2⟩ := List.nodup_cons.1 h
    refine List.nodup_cons.2 ⟨fun hm => ?_, nodup_map_inj f hf l h2⟩
    obtain ⟨b, hb, e⟩ := List.mem_map.1 hm
    exact h1 (hf b a e ▸ hb)

section Law

variable {Row Key : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key) (isWd : Row → Prop)
/- `gives r x`: row `r` is a root of the duty row `x` (here `x` itself). `ans a`: an answering row
   (an acceptance). `holders x`: the duty holders at the head `x` names, without repeats; it is read
   from that head and its past (RosterHead.lean). `to x`: the key `x` seats or unseats. `cosigns x k`:
   `k`'s signature is carried on `x`. -/
variable (gives : Row → Row → Prop) (ans : Row → Prop)
variable (holders : Row → List Key) (to : Row → Key) (cosigns : Row → Key → Prop)

/-- A conferral's body: the duty holders at the head it names. -/
def holderAt (x : Row) (k : Key) : Prop := k ∈ holders x

/-- A withdrawal's body: the duty holders at the head it names, the holder concerned not counted. -/
def otherAt (x : Row) (k : Key) : Prop := k ∈ holders x ∧ k ≠ to x

/-- The holders' consent to a conferral: a strict majority of them, carried on the row. -/
def confCounts (P : Row → Prop) (o : Row) : Prop :=
  Consent.bodyConsents (holderAt holders) (fun x => majority (holders x).length) cosigns P o o

/-- A withdrawal of the duty seat of `to x` counts: a strict majority of the others, two at least. -/
def wdCounts (P : Row → Prop) (x : Row) : Prop :=
  Consent.bodyConsents (otherAt holders to) (fun x => wdNeed (holders x).length) cosigns P x x

/-- The duty seat conferred by row `o` stands: the holders' count and the new holder's own yes
    (`Consent.standsCounted`, with the body the holders at the head `o` names). -/
def dutyStands (P W : Row → Prop) (cut : Row → Row → Prop) (o : Row) : Prop :=
  Consent.standsCounted parent signer isWd gives ans (holderAt holders)
    (fun x => majority (holders x).length) to cosigns P W cut o o

theorem dutyStands_count (P W : Row → Prop) (cut : Row → Row → Prop) (o : Row)
    (h : dutyStands parent signer isWd gives ans holders to cosigns P W cut o) :
    confCounts holders cosigns P o :=
  h.2.2.2.1

/-! ### (1) The lone holder -/

/-- (1) LONE HOLDER CONFERS. With exactly one duty holder `c` at the head the row names, the row
    stands when it is held, carries `c`'s signature and has the new holder's yes. -/
theorem lone_holder_confers (P W : Row → Prop) (cut : Row → Row → Prop) (o : Row) (c : Key)
    (h1 : holders o = [c]) (hP : P o) (hg : gives o o) (hc : ¬ cut o o) (hs : cosigns o c)
    (hy : Consent.holderYes parent signer isWd ans to cosigns P W o o) :
    dutyStands parent signer isWd gives ans holders to cosigns P W cut o := by
  refine ⟨hP, hg, hc, ?_, hy⟩
  refine (Consent.count_of_one_is_one_row (holderAt holders) (fun x => majority (holders x).length)
    cosigns P o o c (fun k => ?_) (by simp [h1, majority])).2 ⟨hP, hs⟩
  show k ∈ holders o ↔ k = c
  rw [h1]; exact List.mem_singleton

/-- (1), the other way: a lone holder's count is its own signature, and no other key's. -/
theorem lone_count_is_own (P : Row → Prop) (o : Row) (c : Key) (h1 : holders o = [c]) :
    confCounts holders cosigns P o ↔ P o ∧ cosigns o c :=
  Consent.count_of_one_is_one_row (holderAt holders) (fun x => majority (holders x).length)
    cosigns P o o c (fun k => by show k ∈ holders o ↔ k = c; rw [h1]; exact List.mem_singleton)
    (by simp [h1, majority])

/-! ### (2) One of several -/

/-- (2) ONE OF SEVERAL CONFERS NOTHING. With two or more duty holders at the head a row names, a row
    whose holders' signatures are all `c`'s seats nobody. Each row is judged alone, since a signature
    is part of its row, so any number of such rows seat nobody. -/
theorem one_of_several_confers_nothing (P W : Row → Prop) (cut : Row → Row → Prop) (c : Key)
    (o : Row) (h2 : 2 ≤ (holders o).length) (hone : ∀ k, k ∈ holders o → cosigns o k → k = c) :
    ¬ dutyStands parent signer isWd gives ans holders to cosigns P W cut o :=
  fun h => Consent.one_voice_is_not_a_count (holderAt holders) (fun x => majority (holders x).length)
    cosigns P o o (by show 2 ≤ (holders o).length / 2 + 1; omega)
    (fun k k' hk hk' hc hc' => (hone k hk hc).trans (hone k' hk' hc').symm)
    (dutyStands_count parent signer isWd gives ans holders to cosigns P W cut o h)

theorem one_of_several_rows (P W : Row → Prop) (cut : Row → Row → Prop) (c : Key)
    (rows : List Row) (h2 : ∀ o, o ∈ rows → 2 ≤ (holders o).length)
    (hone : ∀ o, o ∈ rows → ∀ k, k ∈ holders o → cosigns o k → k = c) :
    ∀ o, o ∈ rows → ¬ dutyStands parent signer isWd gives ans holders to cosigns P W cut o :=
  fun o ho => one_of_several_confers_nothing parent signer isWd gives ans holders to cosigns P W cut
    c o (h2 o ho) (hone o ho)

/-! ### (3) A strict majority -/

/-- (3) A STRICT MAJORITY CONFERS. Signatures of distinct holders, more than half of them, with the
    new holder's yes, seat. -/
theorem majority_confers (P W : Row → Prop) (cut : Row → Row → Prop) (o : Row) (l : List Key)
    (hnd : l.Nodup) (hin : ∀ k, k ∈ l → k ∈ holders o ∧ cosigns o k)
    (hmaj : (holders o).length < 2 * l.length) (hP : P o) (hg : gives o o) (hc : ¬ cut o o)
    (hy : Consent.holderYes parent signer isWd ans to cosigns P W o o) :
    dutyStands parent signer isWd gives ans holders to cosigns P W cut o :=
  ⟨hP, hg, hc, ⟨hP, l, hnd, (majority_iff _ _).2 hmaj, hin⟩, hy⟩

/-- (3) NOTHING LESS. A duty seat that stands carries the signatures of more than half the holders. -/
theorem confers_only_by_majority (P W : Row → Prop) (cut : Row → Row → Prop) (o : Row)
    (h : dutyStands parent signer isWd gives ans holders to cosigns P W cut o) :
    ∃ l : List Key, l.Nodup ∧ (holders o).length < 2 * l.length ∧
      ∀ k, k ∈ l → k ∈ holders o ∧ cosigns o k :=
  let ⟨_, l, hnd, hn, hl⟩ := dutyStands_count parent signer isWd gives ans holders to cosigns P W cut o h
  ⟨l, hnd, (majority_iff _ _).1 hn, hl⟩

/-! ### (4) A withdrawal -/

/-- (4) A WITHDRAWAL NEEDS TWO OTHERS. A withdrawal that counts carries the signatures of at least
    two distinct holders other than the one concerned, and of more than half of those others. -/
theorem withdrawal_needs_two_others (P : Row → Prop) (x : Row) (h : wdCounts holders to cosigns P x) :
    ∃ l : List Key, l.Nodup ∧ 2 ≤ l.length ∧ (holders x).length - 1 < 2 * l.length ∧
      ∀ k, k ∈ l → k ∈ holders x ∧ k ≠ to x ∧ cosigns x k :=
  let ⟨_, l, hnd, hn, hl⟩ := h
  have ⟨a, b⟩ := (wdNeed_iff _ _).1 hn
  ⟨l, hnd, a, b, fun k hk => ⟨(hl k hk).1.1, (hl k hk).1.2, (hl k hk).2⟩⟩

/-- (4) And that is enough. -/
theorem withdrawal_counts_of (P : Row → Prop) (x : Row) (l : List Key) (hP : P x) (hnd : l.Nodup)
    (h2 : 2 ≤ l.length) (hmaj : (holders x).length - 1 < 2 * l.length)
    (hin : ∀ k, k ∈ l → k ∈ holders x ∧ k ≠ to x ∧ cosigns x k) :
    wdCounts holders to cosigns P x :=
  ⟨hP, l, hnd, (wdNeed_iff _ _).2 ⟨h2, hmaj⟩, fun k hk => ⟨⟨(hin k hk).1, (hin k hk).2.1⟩, (hin k hk).2.2⟩⟩

/-- (4) ONE HOLDER UNSEATS NOTHING. A withdrawal whose other holders' signatures are all `c`'s does
    not count, however many holders there are. -/
theorem one_holder_unseats_nothing (P : Row → Prop) (x : Row) (c : Key)
    (hone : ∀ k, k ∈ holders x → k ≠ to x → cosigns x k → k = c) :
    ¬ wdCounts holders to cosigns P x :=
  Consent.one_voice_is_not_a_count (otherAt holders to) (fun x => wdNeed (holders x).length) cosigns
    P x x (Nat.le_max_left _ _)
    (fun k k' hk hk' hc hc' => (hone k hk.1 hk.2 hc).trans (hone k' hk'.1 hk'.2 hc').symm)

/-- (4) OF TWO, NEITHER UNSEATS THE OTHER. With two holders, one of them the holder concerned, no
    withdrawal counts, whoever signs it. -/
theorem two_holders_neither_unseats (P : Row → Prop) (x : Row) (a b : Key) (h2 : holders x = [a, b])
    (ht : to x = a ∨ to x = b) : ¬ wdCounts holders to cosigns P x := by
  have hk : ∀ k, k ∈ holders x → k = a ∨ k = b := fun k hk => by rw [h2] at hk; simpa using hk
  cases ht with
  | inl e =>
    exact one_holder_unseats_nothing holders to cosigns P x b (fun k h1 hne _ =>
      (hk k h1).elim (fun e' => absurd (e'.trans e.symm) hne) id)
  | inr e =>
    exact one_holder_unseats_nothing holders to cosigns P x a (fun k h1 hne _ =>
      (hk k h1).elim id (fun e' => absurd (e'.trans e.symm) hne))

/-- (4) NO HOLDER UNSEATS A LONE ONE. With one holder, the holder concerned, no withdrawal counts:
    there the seat ends only by its holder's own act or by the members' recall. -/
theorem lone_holder_not_unseated (P : Row → Prop) (x : Row) (b : Key) (h1 : holders x = [b])
    (ht : to x = b) : ¬ wdCounts holders to cosigns P x :=
  one_holder_unseats_nothing holders to cosigns P x b (fun k hk hne _ => by
    rw [h1] at hk; exact absurd ((List.mem_singleton.1 hk).trans ht.symm) hne)

/-! ### (5) A conferrer's withdrawal ends nothing -/

/-- (5) The count once met is final: more rows, by any key, the conferrers' included, leave it met
    (`Consent.count_is_final_against_members`). -/
theorem conferrer_cannot_lower_count (P P' : Row → Prop) (o : Row) (hP : ∀ r, P r → P' r)
    (h : confCounts holders cosigns P o) : confCounts holders cosigns P' o :=
  Consent.count_is_final_against_members (holderAt holders) (fun x => majority (holders x).length)
    cosigns P P' o o hP h

/-- (5) CONFERRER CANNOT END. Once the duty seat of row `o` stands, a further row `w` signed by a key
    `c` that is not the holder, held and read as a withdrawal, leaves it standing. That is a key that
    conferred it, or any other. Only the holder's own withdrawal or a cut ends it. -/
theorem conferrer_cannot_end (P W : Row → Prop) (cut : Row → Row → Prop) (o w : Row)
    (hc : signer w ≠ to o) (h : dutyStands parent signer isWd gives ans holders to cosigns P W cut o) :
    dutyStands parent signer isWd gives ans holders to cosigns (fun r => P r ∨ r = w)
      (fun r => W r ∨ r = w) cut o :=
  Consent.only_holder_or_cut_ends parent signer isWd gives ans (holderAt holders)
    (fun x => majority (holders x).length) to cosigns P _ W _ cut cut o o (fun _ => Or.inl)
    (fun _ hw' hs => hw'.elim id (fun e => absurd (e ▸ hs) hc)) id h

/-! ### (6) Equals -/

/-- Two bodies with the same members and the same count give the same consent. -/
theorem body_congr {T : Type} (m m' : T → Key → Prop) (n n' : T → Nat) (P : Row → Prop) (t : T)
    (o : Row) (hm : ∀ k, m t k ↔ m' t k) (hn : n t = n' t) :
    Consent.bodyConsents m n cosigns P t o ↔ Consent.bodyConsents m' n' cosigns P t o :=
  ⟨fun ⟨h0, l, hnd, hl, hk⟩ => ⟨h0, l, hnd, hn ▸ hl, fun k h => ⟨(hm k).1 (hk k h).1, (hk k h).2⟩⟩,
   fun ⟨h0, l, hnd, hl, hk⟩ => ⟨h0, l, hnd, hn ▸ hl, fun k h => ⟨(hm k).2 (hk k h).1, (hk k h).2⟩⟩⟩

/-- (6) EQUALS, BY ORDER. Two readings of the holders at a head that list the same keys in another
    order (which was seated first, which conferred which) give the same answer to every count:
    a conferral, a withdrawal, and whether a duty seat stands. -/
theorem equals_perm (holders' : Row → List Key) (x : Row) (hp : (holders x).Perm (holders' x)) :
    (∀ P, confCounts holders cosigns P x ↔ confCounts holders' cosigns P x) ∧
    (∀ P, wdCounts holders to cosigns P x ↔ wdCounts holders' to cosigns P x) ∧
    (∀ P W cut, dutyStands parent signer isWd gives ans holders to cosigns P W cut x ↔
      dutyStands parent signer isWd gives ans holders' to cosigns P W cut x) := by
  have hc : ∀ P, confCounts holders cosigns P x ↔ confCounts holders' cosigns P x := fun P =>
    body_congr cosigns _ _ _ _ P x x (fun k => hp.mem_iff) (by simp [hp.length_eq])
  refine ⟨hc, fun P => body_congr cosigns _ _ _ _ P x x
    (fun k => by show k ∈ holders x ∧ _ ↔ k ∈ holders' x ∧ _; rw [hp.mem_iff])
    (by simp [hp.length_eq]), fun P W cut => ?_⟩
  exact ⟨fun ⟨a, b, c, d, e⟩ => ⟨a, b, c, (hc P).1 d, e⟩, fun ⟨a, b, c, d, e⟩ => ⟨a, b, c, (hc P).2 d, e⟩⟩

/-- Renaming the keys of a body by a bijection gives the same consent. -/
theorem body_rename {T : Type} (e e' : Key → Key) (he : ∀ k, e' (e k) = k) (he' : ∀ k, e (e' k) = k)
    (m : T → Key → Prop) (n : T → Nat) (P : Row → Prop) (t : T) (o : Row) :
    Consent.bodyConsents m n cosigns P t o ↔
      Consent.bodyConsents (fun t k => m t (e' k)) n (fun r k => cosigns r (e' k)) P t o := by
  have inj : ∀ a b, e a = e b → a = b := fun a b h => by rw [← he a, ← he b, h]
  have inj' : ∀ a b, e' a = e' b → a = b := fun a b h => by rw [← he' a, ← he' b, h]
  constructor
  · intro ⟨h0, l, hnd, hl, hk⟩
    refine ⟨h0, l.map e, nodup_map_inj e inj l hnd, by simpa using hl, fun k hk' => ?_⟩
    obtain ⟨a, ha, rfl⟩ := List.mem_map.1 hk'
    show m t (e' (e a)) ∧ cosigns o (e' (e a))
    rw [he a]; exact hk a ha
  · intro ⟨h0, l, hnd, hl, hk⟩
    refine ⟨h0, l.map e', nodup_map_inj e' inj' l hnd, by simpa using hl, fun k hk' => ?_⟩
    obtain ⟨a, ha, rfl⟩ := List.mem_map.1 hk'
    exact hk a ha

/-- (6) EQUALS, BY NAME. Rename every key by a bijection `e`: the holders, the key concerned and the
    signatures. Every count gives the same answer, so no count tells one holder from another. -/
theorem equals_rename (e e' : Key → Key) (he : ∀ k, e' (e k) = k) (he' : ∀ k, e (e' k) = k)
    (P : Row → Prop) (x : Row) :
    (confCounts holders cosigns P x ↔
      confCounts (fun y => (holders y).map e) (fun r k => cosigns r (e' k)) P x) ∧
    (wdCounts holders to cosigns P x ↔
      wdCounts (fun y => (holders y).map e) (fun y => e (to y)) (fun r k => cosigns r (e' k)) P x) := by
  have mem : ∀ y k, k ∈ (holders y).map e ↔ e' k ∈ holders y := fun y k =>
    ⟨fun h => by obtain ⟨a, ha, rfl⟩ := List.mem_map.1 h; rw [he a]; exact ha,
     fun h => List.mem_map.2 ⟨e' k, h, he' k⟩⟩
  constructor
  · refine (body_rename cosigns e e' he he' _ _ P x x).trans
      (body_congr _ _ _ _ _ P x x (fun k => (mem x k).symm) (by simp))
  · refine (body_rename cosigns e e' he he' _ _ P x x).trans
      (body_congr _ _ _ _ _ P x x (fun k => ?_) (by simp))
    show e' k ∈ holders x ∧ e' k ≠ to x ↔ k ∈ (holders x).map e ∧ k ≠ e (to x)
    rw [mem x k]
    exact and_congr_right fun _ =>
      ⟨fun h h' => h (by rw [h', he]), fun h h' => h (by rw [← h', he'])⟩

end Law

/-! ### (7) A removal from the roster ends the removed member's duty seats -/

section Removal

variable {Row Key : Type} (L : RosterHead.Lineage Row Key)
/- `head x`: the roster version the duty row `x` names. `dutyListed x k`: the duty record at that
   head lists `k`. A non-member holds no duty: the holders at the head are the listed keys that are
   members of the roster there (`RosterHead.mem`). -/
variable (head : Row → Row) (cosigns : Row → Key → Prop)

/-- The duty holders at the head `x` names: listed, and members there. -/
def heldAt (P : Row → Prop) (dutyListed : Row → Key → Prop) (x : Row) (k : Key) : Prop :=
  dutyListed x k ∧ RosterHead.mem L P (head x) k

/-- (7) REMOVAL ENDS DUTY. Let a version `u` of the roster not list `k`, and let the duty row `x`
    name a head `d` that is `u` or below it, with no version on the way re-admitting `k`. Then `k`
    holds no duty at `x`'s head. -/
theorem removal_ends_duty (P : Row → Prop) (dutyListed : Row → Key → Prop) (u : Row) (k : Key)
    (x : Row) (hu : ¬ L.states u k)
    (hl : head x = u ∨ TransGen (RosterHead.hd L) u (head x))
    (hno : ∀ w h, TransGen (RosterHead.hd L) u w → (w = head x ∨ TransGen (RosterHead.hd L) w (head x)) →
      RosterHead.hd L h w → ¬ RosterHead.mem L P h k →
      ¬ (RosterHead.standsV L P w ∧ L.states w k)) :
    ¬ heldAt L head P dutyListed x k := by
  intro ⟨_, hm⟩
  cases hl with
  | inl e => exact RosterHead.not_stated_not_member L P u k hu (e ▸ hm)
  | inr t => exact RosterHead.readmission_needed L P u (head x) k hu t hno hm

/-- (7) So a removed key's signatures confer nothing at such a head: where no key held at the head
    signed the row, the holders' count is not met (a strict majority is at least one). -/
theorem removed_confers_nothing (holders : Row → List Key) (P : Row → Prop) (o : Row)
    (hno : ∀ k, k ∈ holders o → ¬ cosigns o k) : ¬ confCounts holders cosigns P o := by
  intro ⟨_, l, _, hn, hl⟩
  match l, hn, hl with
  | [], hn, _ => exact absurd hn (by simp [majority])
  | a :: _, _, hl => exact hno a (hl a (List.mem_cons_self _ _)).1 (hl a (List.mem_cons_self _ _)).2

/-- (7) The removal as a cut. Where the removal `c` of `to o` from the roster cuts each of its duty
    seats (`cutsSeat c o`), the conferral `o` in the removal's past does not stand, whatever else is
    held (`Kernel.cutOut`). A conferral naming the removal is a new seat and is judged at its head. -/
theorem removal_cuts_duty {parent : Row → Row → Prop} {signer : Row → Key} {isWd : Row → Prop}
    {gives : Row → Row → Prop} {ans : Row → Prop} {to : Row → Key}
    (holders : Row → List Key) (cutsSeat : Row → Row → Prop) (X P W : Row → Prop) (c o : Row)
    (hX : X c) (hcut : cutsSeat c o) (hpast : ¬ TransGen parent c o) :
    ¬ dutyStands parent signer isWd gives ans holders to cosigns P W (cutOut parent cutsSeat X) o :=
  fun h => h.2.2.1 ⟨c, hX, hcut, hpast⟩

end Removal

/-! ### (8) With no duty holder left, the members' count seats one -/

section NoneLeft

variable {Row Key : Type}
/- `members x k`: `k` is a member at the roster head `x` names (`RosterHead.mem` or `voters` at that
   head). `mneed x`: the count the members' election asks, with its floor. -/
variable (holders : Row → List Key) (cosigns : Row → Key → Prop)
variable (members : Row → Key → Prop) (mneed : Row → Nat)

/-- The members' count on row `o`. -/
def membersCount (P : Row → Prop) (o : Row) : Prop :=
  Consent.bodyConsents (fun x k => members x k) mneed cosigns P o o

/-- How a duty seat is conferred: the holders' count where a holder remains, and the members' count
    where none is left (CC 4.5.4 (iv), (v)). -/
def conferred (P : Row → Prop) (o : Row) : Prop :=
  ((holders o) ≠ [] ∧ confCounts holders cosigns P o) ∨
    ((holders o) = [] ∧ membersCount cosigns members mneed P o)

/-- (8) NONE LEFT, THE MEMBERS SEAT. With no duty holder at the head the row names, the holders'
    count seats nobody, whatever is signed, and the row confers exactly when the members' count is
    met. Nothing else seats one. -/
theorem none_left_members_seat (P : Row → Prop) (o : Row) (h0 : holders o = []) :
    ¬ confCounts holders cosigns P o ∧
      (conferred holders cosigns members mneed P o ↔ membersCount cosigns members mneed P o) := by
  have hn : ¬ confCounts holders cosigns P o := fun ⟨_, l, _, hn, hl⟩ => by
    match l, hn, hl with
    | [], hn, _ => exact absurd hn (by simp [majority])
    | a :: _, _, hl =>
      have := (hl a (List.mem_cons_self _ _)).1
      simp [holderAt, h0] at this
  exact ⟨hn, ⟨fun h => h.elim (fun x => absurd h0 x.1) (fun x => x.2), fun h => Or.inr ⟨h0, h⟩⟩⟩

/-- (8) While a duty holder remains, the members' count is not the way a seat is conferred: the
    row confers exactly when the holders' count is met. -/
theorem holders_left_members_do_not (P : Row → Prop) (o : Row) (h0 : holders o ≠ []) :
    conferred holders cosigns members mneed P o ↔ confCounts holders cosigns P o :=
  ⟨fun h => h.elim (fun x => x.2) (fun x => absurd x.1 h0), fun h => Or.inl ⟨h0, h⟩⟩

/-- (8) One member's signatures are no members' count where the count asks two or more. -/
theorem one_member_seats_nothing (P : Row → Prop) (o : Row) (j : Key) (h2 : 2 ≤ mneed o)
    (hone : ∀ k, members o k → cosigns o k → k = j) :
    ¬ membersCount cosigns members mneed P o :=
  Consent.one_voice_is_not_a_count (fun x k => members x k) mneed cosigns P o o h2
    (fun k k' hk hk' hc hc' => (hone k hk hc).trans (hone k' hk' hc').symm)

end NoneLeft

/-! ## F5 and Founders against the community law

  `Harden2.lean` states F5 over founding seats and a conferrer rule `F5.conf5` (the founding row, a
  seat that may confer, or a count). Read against the law, each theorem is one of three things.

  EQUAL or A SPECIAL CASE (true under the law, and implied by the theorems above):
    `F5.cut_needs_two_voices`, `one_key_cuts_nothing`, `no_single_founder_removes`: the floor of
      two voices; the law's withdrawal also asks a strict majority of the others and does not count
      the holder concerned (4).
    `F5.two_founders_neither_removes`: (4) `two_holders_neither_unseats`; the law needs no
      hypothesis that the holder signs nothing against itself, since that holder is not counted.
    `F5.removed_cannot_reseat`, `Founders.new_removed_cannot_reseat`: a removed holder is no holder
      at a head below the removal (7), and its own rows are one voice (2).
    `Founders.new_u2_void`, `new_f2_keeps_seat`, `new_xf_counts`: (4) at three holders: one voice
      of the others is void, two of the two others count.
    `Founders.new_grant_falls`: its conclusion holds (K holds no seat), for another reason: f1's
      lone grant among three holders never stood (2).
    `F5.counts_concluded`, `counts_of_unopposed`, `conf5_mono`, `under_dead_falls`, `step_one`,
      `step_all`, `twoVoices_new`, `no_group`: lemmas about the definitions, true and not about
      the law.
    `Founders.old_one_founder_removes`, `old_removed_reseats`, `old_grant_survives`: witnesses of
      the rule before F5; they stay true of that rule, which the law rejects too.

  FALSE UNDER THE LAW (the counter-models are below, under `Rejected`):
    `Founders.new_grant_live_before`: one holder's own grant, with three holders, is live. Under
      the law it never concludes (`Rejected.three_holders_lone_grant`).
    `F5.self_grant_falls`, read as the law: a holder's own grant ends with that holder's seat. Under
      the law a duty seat validly conferred by the lone holder stands as an equal after its conferrer
      withdraws (`Rejected.lone_grant_outlives_conferrer`).
    `F5.emptied_founders_stay_empty`, `no_row_restores_a_founder`, read for duty seats: once none is
      left, nothing brings one back. Under the law the members' count seats one
      (`Rejected.members_restore`). As stated over founding seats (`isF`) both stay true: a seat the
      members confer is not a founding seat. -/

namespace Rejected

/-- The rows of the counter-models: `o` a conferral, `a` the new holder's acceptance, `w` a
    withdrawal by the conferrer. -/
inductive R | o | a | w
  deriving DecidableEq, Repr

inductive K | f1 | f2 | f3 | K | m1 | m2
  deriving DecidableEq, Repr

def parent (p r : R) : Prop := (p = .o ∧ r = .a) ∨ (p = .o ∧ r = .w)
def signer : R → K | .o => .f1 | .a => .K | .w => .f1
def isWd (r : R) : Prop := r = .w
def isAcc (r : R) : Prop := r = .a
def gives (r x : R) : Prop := r = .o ∧ x = .o
def to (_ : R) : K := .K
/-- Only f1 signs the conferral. -/
def cosigns (r : R) (k : K) : Prop := r = .o ∧ k = .f1
def All (_ : R) : Prop := True
def noCut (_ _ : R) : Prop := False

theorem yes (W : R → Prop) (hW : ∀ x, W x → x = .w) :
    Consent.holderYes parent signer isWd isAcc to cosigns All W R.o R.o :=
  Or.inl ⟨.a, trivial, rfl, trivial, Or.inl ⟨rfl, Or.inl ⟨rfl, rfl⟩⟩,
    fun ⟨x, ⟨_, hp, hs⟩, hx⟩ => by
      have := hW x hx; subst this
      cases hp with
      | inl h => exact nomatch h.1
      | inr h => exact nomatch h.1⟩

/-- `Founders.new_grant_live_before`, FALSE under the law: with three holders f1, f2, f3, f1's own
    conferral of a duty seat on K, accepted by K, seats nobody. -/
theorem three_holders_lone_grant :
    ¬ dutyStands parent signer isWd gives isAcc (fun _ => [K.f1, K.f2, K.f3]) to cosigns All All
      noCut R.o :=
  one_of_several_confers_nothing parent signer isWd gives isAcc (fun _ => [K.f1, K.f2, K.f3]) to
    cosigns All All noCut K.f1 R.o (by decide) (fun _ _ h => h.2)

/-- `F5.self_grant_falls`, read as the law, FALSE: with f1 the lone holder, its conferral on K with
    K's acceptance stands, and stands still with f1's withdrawal `w` of it held. -/
theorem lone_grant_outlives_conferrer :
    dutyStands parent signer isWd gives isAcc (fun _ => [K.f1]) to cosigns All (fun _ => False)
      noCut R.o ∧
    dutyStands parent signer isWd gives isAcc (fun _ => [K.f1]) to cosigns (fun r => All r ∨ r = .w)
      (fun r => False ∨ r = .w) noCut R.o := by
  have h : dutyStands parent signer isWd gives isAcc (fun _ => [K.f1]) to cosigns All (fun _ => False)
      noCut R.o :=
    lone_holder_confers parent signer isWd gives isAcc (fun _ => [K.f1]) to cosigns All _ noCut R.o
      K.f1 rfl trivial ⟨rfl, rfl⟩ id ⟨rfl, rfl⟩ (yes _ (fun _ h => h.elim))
  exact ⟨h, conferrer_cannot_end parent signer isWd gives isAcc (fun _ => [K.f1]) to cosigns All _
    noCut R.o R.w (by decide) h⟩

/-- `F5.emptied_founders_stay_empty` and `no_row_restores_a_founder`, read for duty seats, FALSE:
    with no duty holder at the head, two members' signatures on a row meet a members' count of two,
    so the row confers a duty seat. -/
theorem members_restore :
    conferred (fun _ => ([] : List K)) (fun r k => r = R.o ∧ (k = K.m1 ∨ k = K.m2))
      (fun _ k => k = K.m1 ∨ k = K.m2) (fun _ => 2) All R.o :=
  Or.inr ⟨rfl, trivial, [K.m1, K.m2], by decide, Nat.le_refl 2, fun k hk => by
    simp only [List.mem_cons, List.mem_singleton, List.not_mem_nil, or_false] at hk
    exact ⟨hk, rfl, hk⟩⟩

end Rejected

end Duty

#print axioms Duty.majority_iff
#print axioms Duty.wdNeed_iff
#print axioms Duty.nodup_map_inj
#print axioms Duty.lone_holder_confers
#print axioms Duty.lone_count_is_own
#print axioms Duty.one_of_several_confers_nothing
#print axioms Duty.one_of_several_rows
#print axioms Duty.majority_confers
#print axioms Duty.confers_only_by_majority
#print axioms Duty.withdrawal_needs_two_others
#print axioms Duty.withdrawal_counts_of
#print axioms Duty.one_holder_unseats_nothing
#print axioms Duty.two_holders_neither_unseats
#print axioms Duty.lone_holder_not_unseated
#print axioms Duty.conferrer_cannot_lower_count
#print axioms Duty.conferrer_cannot_end
#print axioms Duty.body_congr
#print axioms Duty.equals_perm
#print axioms Duty.body_rename
#print axioms Duty.equals_rename
#print axioms Duty.removal_ends_duty
#print axioms Duty.removed_confers_nothing
#print axioms Duty.removal_cuts_duty
#print axioms Duty.none_left_members_seat
#print axioms Duty.holders_left_members_do_not
#print axioms Duty.one_member_seats_nothing
#print axioms Duty.Rejected.three_holders_lone_grant
#print axioms Duty.Rejected.lone_grant_outlives_conferrer
#print axioms Duty.Rejected.members_restore

end Kernel
