/-
  TwoMechanisms.lean — a claim and content are carried by consent; the door and consent are not
  carried by each other

  KERNEL.md section 5a says the four shapes (consent, door, claim, content) rest on two
  mechanisms, consent and the door. This file proves what the existing definitions allow.

  (a) CLAIM. PROVED IN FULL for the meaning walk of Causal.lean.
      `edge_is_one_voice_consent`: an edge of the walk is exactly a relation binding one voice,
      standing by `Consent.stands` (one row, `Consent.one_voice_one_row`).
      `claim_is_one_voice_consent`: what a row means to a reader is its conclusion and a bounded
      walk of such one-voice consents from the reader's own key to its signer.
      `claim_lost_only_by_walk_voice`: a new row removes that meaning only if it, or a row
      waiting on it, is a withdrawal signed by a key on the reader's walk. Only loss is stated;
      new rows may give meaning, through edges of keys the walk reaches.
  (b) CONTENT. PROVED FOR STATED INSTANCES. The audience is `Carry.AudR` with each row's own
      audience instantiated as one of three scopes: the members at a roster head
      (`RosterHead.mem`), everyone, or one named key.
      `content_holders_are_consents`: where no author carries its own row out of its room,
      everyone who may hold a row is, for some row of its room, a member at the roster head it
      names, or the row is for everyone, or the key is the one it names.
      `content_audience_function`: the audience is decided by the pasts of the roster heads the
      scopes name and the concluded naming rows.
      `content_audience_final`: holding more rows, with no holes, takes nobody out of an
      audience. What a row's life is (the state answer) is not modelled here: measured only.
  (c) THE DOOR DOES NOT REDUCE; CONSENT DOES NOT REDUCE. PROVED FOR STATED INSTANCES.
      `door_reads_now`, `door_not_function_of_rows`: a window that closes on the reader's own
      clock, with no answer held, is open at one instant and closed at a later one over the
      same rows, so no function of the rows gives it. The window rules of Window.lean and
      Recount.lean read no instant (`Window.landsI_function`): there the clock is read only by
      the concluder when it signs its landing, and is not in this file.
      `consent_not_door`: for every way of saying which rows answer the window an offer opens,
      and every end, no function of that window's outcome at every instant says whether the
      seat stands. `offer_alone_never_stands`: an offer with no acceptance is
      no seat at any instant.

  What remains measured: that the 184 families fall into the four shapes, and that every
  content family's audience is one of the three scopes (formal/causal_kernel/check_shapes.py).

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports RosterHead.lean and
  Carry.lean.
-/

import RosterHead
import Carry

namespace Kernel

namespace TwoMechanisms

open Relation Causal

/-! ## (a) A claim is the reader's own one-voice consent, walked -/

section Claim

variable {Row Key : Type}
variable (parent : Row → Row → Prop) (signer : Row → Key) (names : Row → Option Key)
variable (isWd : Row → Prop) (C : (Row → Prop) → Row → Prop)

/-- The relation "`k`, in `s`'s reading", as an act of `Consent.lean`: it binds one voice, `s`;
    a consent to it is a row by `s` naming `k`; there are no answers and no cuts. -/
def oneVoice (S : Row → Prop) (s k : Key) : Prop :=
  Consent.stands parent signer isWd (T := Key × Key)
    (fun e t => signer e = t.1 ∧ names e = some t.2) (fun _ => False) (fun t k' => k' = t.1)
    (fun _ _ => True) (C S) (C S) (fun _ _ => False) (s, k)

/-- An edge of the meaning walk is exactly that one-voice consent. -/
theorem edge_is_one_voice_consent (S : Row → Prop) (s k : Key) :
    oneVoice parent signer names isWd C S s k ↔
      Edge parent signer names isWd C (fun _ => True) S s k := by
  unfold oneVoice
  rw [Consent.one_voice_one_row parent signer isWd _ _ _ _ (C S) (C S) _ (s, k) s
    (fun _ => Iff.rfl)]
  constructor
  · intro ⟨o, h1, ⟨_, hn⟩, hs, _, hw, _⟩
    exact ⟨o, ⟨h1, ⟨k, hn⟩, fun ⟨w, hwd, hc, _⟩ => hw ⟨w, hwd, hc⟩⟩, hs, hn⟩
  · intro ⟨e, ⟨h1, _, h3⟩, hs, hn⟩
    exact ⟨e, h1, ⟨hs, hn⟩, hs, trivial, fun ⟨w, hwd, hc⟩ => h3 ⟨w, hwd, hc, trivial⟩, id⟩

/-- (a) CLAIM REDUCES TO CONSENT. A row means something to the reader iff it is concluded and a
    walk of at most `depth` live one-voice consents leads from the reader's own key to its
    signer. -/
theorem claim_is_one_voice_consent (depth : Nat) (own : Key) (S : Row → Prop) (r : Row) :
    means parent signer names isWd C depth own S r ↔
      (C S r ∧ reaches (oneVoice parent signer names isWd C S) own depth (signer r)) := by
  have e : oneVoice parent signer names isWd C S = Edge parent signer names isWd C (fun _ => True) S :=
    funext fun s => funext fun k => propext (edge_is_one_voice_consent parent signer names isWd C S s k)
  rw [e]
  exact Iff.rfl

variable (wf : WellFounded parent) (wellFormed : Row → Prop)
variable (hCk : ∀ S r, C S r → kept parent wf wellFormed S r)
variable (hfin : ∀ S x r, kept parent wf wellFormed S r → ¬ S x →
    (C S r ↔ C (fun q => S q ∨ q = x) r))
include hCk hfin

/-- (a) Let `r` mean something to the reader and let `x` be offered. If no withdrawal that is
    `x`, or waits on `x`, is signed by a key the reader's walk reaches in fewer than `depth`
    steps, `r` still means something. So only a voice on the walk, by its own withdrawal,
    removes a claim's meaning. -/
theorem claim_lost_only_by_walk_voice (depth : Nat) (own : Key) (S : Row → Prop) (x r : Row)
    (hx : ¬ S x) (hm : means parent signer names isWd C depth own S r)
    (hno : ∀ w, isWd w → (w = x ∨ TransGen parent x w) → ∀ n, n < depth →
      ¬ reaches (oneVoice parent signer names isWd C S) own n (signer w)) :
    means parent signer names isWd C depth own (fun q => S q ∨ q = x) r := by
  have e : oneVoice parent signer names isWd C S = Edge parent signer names isWd C (fun _ => True) S :=
    funext fun s => funext fun k => propext (edge_is_one_voice_consent parent signer names isWd C S s k)
  refine meaning_survives parent wf wellFormed signer names isWd C hCk hfin depth own S x r hx hm ?_
  intro ed w n hn _ hr hwd
  have hs : signer w = signer ed := hwd.2.2
  rw [← e] at hr
  exact ⟨fun ex => hno w hwd.1 (Or.inl ex) n hn (hs ▸ hr),
    fun t => hno w hwd.1 (Or.inr t) n hn (hs ▸ hr)⟩

end Claim

/-! ## (b) Content: who may hold a row is read off consents and cuts -/

section Content

/-- A row's own audience: the members at a roster head, everyone, or one named key. -/
inductive Scope (Row Key : Type)
  | roster (h : Row)
  | everyone
  | key (k : Key)

variable {Row Key Rm : Type}

def ownOf (M : Row → Key → Prop) (scope : Row → Scope Row Key) (r : Row) (k : Key) : Prop :=
  match scope r with
  | .roster h => M h k
  | .everyone => True
  | .key k' => k = k'

theorem ownOf_iff (M : Row → Key → Prop) (scope : Row → Scope Row Key) (r : Row) (k : Key) :
    ownOf M scope r k ↔
      ((∃ h, scope r = .roster h ∧ M h k) ∨ scope r = .everyone ∨ scope r = .key k) := by
  unfold ownOf
  cases scope r with
  | roster h =>
    exact ⟨fun x => Or.inl ⟨h, rfl, x⟩, fun x => x.elim (fun ⟨_, e, m⟩ => by cases e; exact m)
      (fun y => y.elim (fun e => nomatch e) (fun e => nomatch e))⟩
  | everyone => exact ⟨fun _ => Or.inr (Or.inl rfl), fun _ => trivial⟩
  | key k' =>
    exact ⟨fun x => Or.inr (Or.inr (x ▸ rfl)), fun x => x.elim (fun ⟨_, e, _⟩ => nomatch e)
      (fun y => y.elim (fun e => nomatch e) (fun e => by cases e; rfl))⟩

variable (L : RosterHead.Lineage Row Key) (scope : Row → Scope Row Key) (room : Row → Rm)

/-- The audience as Carry.lean narrows it, with the own audience read off the roster. -/
def aud (P : Row → Prop) (A : Row → Prop) : Row → Key → Prop :=
  Carry.AudR L.parent L.signer (ownOf (RosterHead.mem L P) scope) room A

theorem AudR_mono {own own' : Row → Key → Prop} {A A' : Row → Prop}
    (ho : ∀ r k, own r k → own' r k) (hA : ∀ r, A r → A' r) :
    ∀ r k, Carry.AudR L.parent L.signer own room A r k →
      Carry.AudR L.parent L.signer own' room A' r k := by
  intro r k h
  induction h with
  | base h => exact Carry.AudR.base (ho _ _ h)
  | carry hp hA' hm _ _ ih1 ih2 => exact Carry.AudR.carry hp (hA _ hA') hm ih1 ih2

/-- (b) CONTENT REDUCES TO CONSENT. Where no concluded row names a row of its own signer from
    another room (`Carry.nothing_leaves`), a key in a row's audience is, for some row of the
    same room, a member at the roster head it names, or that row is for everyone, or the key is
    the one it names. -/
theorem content_holders_are_consents (P : Row → Prop) (A : Row → Prop)
    (hauthor : ∀ r d, L.parent r d → A d → L.signer d = L.signer r → room d = room r)
    (r : Row) (k : Key) (h : aud L scope room P A r k) :
    ∃ r', room r' = room r ∧
      ((∃ hh, scope r' = .roster hh ∧ RosterHead.mem L P hh k) ∨
        scope r' = .everyone ∨ scope r' = .key k) :=
  let ⟨r', e, ho⟩ := Carry.nothing_leaves L.parent L.signer _ room A hauthor r k h
  ⟨r', e, (ownOf_iff _ scope r' k).1 ho⟩

theorem ownOf_congr (P P' : Row → Prop)
    (hm : ∀ h, (∃ r, scope r = .roster h) → ∀ k, RosterHead.mem L P h k ↔ RosterHead.mem L P' h k)
    (r : Row) (k : Key) :
    ownOf (RosterHead.mem L P) scope r k ↔ ownOf (RosterHead.mem L P') scope r k := by
  unfold ownOf
  cases e : scope r with
  | roster h => exact hm h ⟨r, e⟩ k
  | everyone => exact Iff.rfl
  | key _ => exact Iff.rfl

/-- (b) The audience is decided by the roster heads the scopes name and their pasts, and the
    concluded naming rows: two sets of rows that agree on the past of every head named give
    every row the same audience. -/
theorem content_audience_function (P P' : Row → Prop) (A : Row → Prop)
    (hsame : ∀ h, (∃ r, scope r = .roster h) →
      ∀ x, RosterHead.pastOrSelf L x h → (P x ↔ P' x))
    (r : Row) (k : Key) :
    aud L scope room P A r k ↔ aud L scope room P' A r k := by
  have ho := ownOf_congr L scope P P'
    (fun h hh k => RosterHead.membersAt_function L P P' h (hsame h hh) k)
  exact ⟨AudR_mono L room (fun r k => (ho r k).1) (fun _ x => x) r k,
    AudR_mono L room (fun r k => (ho r k).2) (fun _ x => x) r k⟩

/-- (b) FINAL. Where the held rows have no holes and include every roster head a scope names,
    holding more rows and more concluded naming rows takes nobody out of an audience. -/
theorem content_audience_final (P P' : Row → Prop) (A A' : Row → Prop)
    (hcl : ∀ p r, L.parent p r → P r → P p) (hPP : ∀ r, P r → P' r)
    (hh : ∀ h, (∃ r, scope r = .roster h) → P h) (hA : ∀ r, A r → A' r) :
    ∀ r k, aud L scope room P A r k → aud L scope room P' A' r k :=
  AudR_mono L room (fun r k => (ownOf_congr L scope P P'
    (fun h hx k => (RosterHead.standing_final L P P' h hcl hPP (hh h hx)).2 k) r k).1) hA

end Content

/-! ## (c) The door reads now; consent is not a door -/

section Door

variable {Row : Type}

/-- A window opened by `p` that the reader closes on its own clock: held, past its end at
    `now`, and with no answer held. `endOf p` is read from the row or the table. -/
def closedUnanswered (answers : Row → Row → Prop) (endOf : Row → Nat) (S : Row → Prop)
    (now : Nat) (p : Row) : Prop :=
  S p ∧ endOf p < now ∧ ¬ ∃ a, S a ∧ answers a p

/-- The window was answered. -/
def answered (answers : Row → Row → Prop) (S : Row → Prop) (p : Row) : Prop :=
  S p ∧ ∃ a, S a ∧ answers a p

/-- (c) Over the same rows, an unanswered window is open at its end and closed one step later. -/
theorem door_reads_now (answers : Row → Row → Prop) (endOf : Row → Nat) (S : Row → Prop)
    (p : Row) (hp : S p) (hn : ¬ ∃ a, S a ∧ answers a p) :
    closedUnanswered answers endOf S (endOf p + 1) p ∧
      ¬ closedUnanswered answers endOf S (endOf p) p :=
  ⟨⟨hp, Nat.lt_succ_self _, hn⟩, fun h => Nat.lt_irrefl _ h.2.1⟩

/-- (c) THE DOOR DOES NOT REDUCE. Where some set of rows holds the opener and no answer, no
    function of the rows gives the window's outcome at every instant. -/
theorem door_not_function_of_rows (answers : Row → Row → Prop) (endOf : Row → Nat) (p : Row)
    (hex : ∃ S : Row → Prop, S p ∧ ¬ ∃ a, S a ∧ answers a p) :
    ¬ ∃ f : (Row → Prop) → Prop, ∀ S now, closedUnanswered answers endOf S now p ↔ f S := by
  intro ⟨f, hf⟩
  have ⟨S, hp, hn⟩ := hex
  have ⟨h1, h2⟩ := door_reads_now answers endOf S p hp hn
  exact h2 ((hf S _).2 ((hf S _).1 h1))

end Door

namespace SeatModel

/-- An offer `o` by the conferrer `c`, the holder `h`'s acceptance `a` naming it, and `h`'s
    withdrawal `w` of its acceptance. -/
inductive R | o | a | w deriving DecidableEq
inductive K | c | h deriving DecidableEq

def parentB : R → R → Bool
  | .o, .a => true
  | .a, .w => true
  | _, _ => false

def parent (p r : R) : Prop := parentB p r = true

def signer : R → K
  | .o => .c | .a => .h | .w => .h

def isWd (r : R) : Prop := r = .w
def offer (r : R) (_ : Unit) : Prop := r = .o
def isAcc (r : R) : Prop := r = .a
def holder (_ : Unit) : K := .h

/-- The seat over the rows `S`, every conferrer allowed, no cuts. -/
def sp (S : R → Prop) : Prop :=
  seat parent signer isWd offer isAcc holder S S (fun _ _ => True) (fun _ _ => False) ()

def S1 (r : R) : Prop := r = .o
def S2 (r : R) : Prop := r = .o ∨ r = .a
def S3 (_ : R) : Prop := True

theorem not_wd_S2 (x : R) : ¬ withdrawn parent signer isWd S2 x :=
  fun ⟨y, ⟨hy, _, _⟩, hs⟩ => by
    cases hy; exact hs.elim (fun e => nomatch e) (fun e => nomatch e)

theorem stands_S2 : sp S2 :=
  ⟨.o, .a, Or.inl rfl, rfl, trivial, Or.inr rfl, Or.inl ⟨rfl, rfl⟩, rfl, not_wd_S2 _,
    not_wd_S2 _, id⟩

theorem acc_is_a (o' a' : R) (ho : offer o' ()) (hl : accLink parent isAcc o' a')
    (hs : signer a' = holder ()) : a' = .a := by
  cases ho
  cases hl with
  | inl h => exact h.1
  | inr e => cases e; exact nomatch hs

/-- (c) AN OFFER ALONE IS NO SEAT, at any instant: no outcome of any window makes it stand. -/
theorem offer_alone_never_stands : ¬ sp S1 := by
  intro ⟨o', a', _, ho, _, hP, hl, hs, _⟩
  have e := acc_is_a o' a' ho hl hs
  subst e
  exact nomatch hP

/-- The holder's withdrawal of its acceptance ends the seat. -/
theorem withdrawn_falls : ¬ sp S3 := by
  intro ⟨o', a', _, ho, _, _, hl, hs, _, hw, _⟩
  have e := acc_is_a o' a' ho hl hs
  subst e
  exact hw ⟨.w, ⟨rfl, rfl, rfl⟩, trivial⟩

/-- Two sets of rows give the window the offer opens the same outcome: answered or not, and
    closed or not at every instant. -/
def sameDoor (answers : R → R → Prop) (endOf : R → Nat) (S S' : R → Prop) : Prop :=
  (answered answers S .o ↔ answered answers S' .o) ∧
    ∀ now, closedUnanswered answers endOf S now .o ↔ closedUnanswered answers endOf S' now .o

/-- Where the acceptance answers the window, the withdrawal of it changes no outcome. -/
theorem same_if_acceptance_answers (answers : R → R → Prop) (endOf : R → Nat)
    (ha : answers .a .o) : sameDoor answers endOf S2 S3 :=
  have both : ∀ S : R → Prop, S .a → ∃ x, S x ∧ answers x .o := fun _ hs => ⟨.a, hs, ha⟩
  ⟨⟨fun _ => ⟨trivial, both S3 trivial⟩, fun _ => ⟨Or.inl rfl, both S2 (Or.inr rfl)⟩⟩,
   fun _ => ⟨fun h => absurd (both S2 (Or.inr rfl)) h.2.2, fun h => absurd (both S3 trivial) h.2.2⟩⟩

/-- Where it does not, the acceptance itself changes no outcome. -/
theorem same_if_acceptance_does_not_answer (answers : R → R → Prop) (endOf : R → Nat)
    (hna : ¬ answers .a .o) : sameDoor answers endOf S2 S1 :=
  have same : (∃ x, S2 x ∧ answers x .o) ↔ (∃ x, S1 x ∧ answers x .o) :=
    ⟨fun ⟨x, hx, hans⟩ => hx.elim (fun e => ⟨x, e, hans⟩) (fun e => absurd (e ▸ hans) hna),
     fun ⟨x, hx, hans⟩ => ⟨x, Or.inl hx, hans⟩⟩
  ⟨⟨fun ⟨_, x⟩ => ⟨rfl, same.1 x⟩, fun ⟨_, x⟩ => ⟨Or.inl rfl, same.2 x⟩⟩,
   fun _ => ⟨fun ⟨_, h2, h3⟩ => ⟨rfl, h2, fun x => h3 (same.2 x)⟩,
     fun ⟨_, h2, h3⟩ => ⟨Or.inl rfl, h2, fun x => h3 (same.1 x)⟩⟩⟩

/-- (c) CONSENT DOES NOT REDUCE TO THE DOOR. Whatever rows count as answers to the window the
    offer opens, and whatever its end, no function of that window's outcome (answered or not,
    and closed or not at every instant) says whether the seat stands. If the acceptance
    answers, the holder's withdrawal of it changes the seat and not the outcome; if it does
    not, the acceptance itself does. -/
theorem consent_not_door (answers : R → R → Prop) (endOf : R → Nat) :
    ¬ ∃ g : Prop → (Nat → Prop) → Prop, ∀ S, sp S ↔
      g (answered answers S .o) (fun now => closedUnanswered answers endOf S now .o) := by
  intro ⟨g, hg⟩
  have carry : ∀ S S', sameDoor answers endOf S S' → sp S → sp S' := by
    intro S S' ⟨h1, h2⟩ hs
    have e1 : answered answers S .o = answered answers S' .o := propext h1
    have e2 : (fun now => closedUnanswered answers endOf S now .o)
        = (fun now => closedUnanswered answers endOf S' now .o) :=
      funext fun now => propext (h2 now)
    have := (hg S).1 hs
    rw [e1, e2] at this
    exact (hg S').2 this
  have n1 : ¬ answers .a .o := fun ha =>
    withdrawn_falls (carry S2 S3 (same_if_acceptance_answers answers endOf ha) stands_S2)
  exact offer_alone_never_stands
    (carry S2 S1 (same_if_acceptance_does_not_answer answers endOf n1) stands_S2)

end SeatModel

end TwoMechanisms

#print axioms TwoMechanisms.edge_is_one_voice_consent
#print axioms TwoMechanisms.claim_is_one_voice_consent
#print axioms TwoMechanisms.claim_lost_only_by_walk_voice
#print axioms TwoMechanisms.ownOf_iff
#print axioms TwoMechanisms.AudR_mono
#print axioms TwoMechanisms.content_holders_are_consents
#print axioms TwoMechanisms.ownOf_congr
#print axioms TwoMechanisms.content_audience_final
#print axioms TwoMechanisms.content_audience_function
#print axioms TwoMechanisms.door_reads_now
#print axioms TwoMechanisms.door_not_function_of_rows
#print axioms TwoMechanisms.SeatModel.offer_alone_never_stands
#print axioms TwoMechanisms.SeatModel.withdrawn_falls
#print axioms TwoMechanisms.SeatModel.same_if_acceptance_answers
#print axioms TwoMechanisms.SeatModel.same_if_acceptance_does_not_answer
#print axioms TwoMechanisms.SeatModel.consent_not_door

end Kernel
