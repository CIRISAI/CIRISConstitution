/-
  formal/affiliation/Affiliation.lean — the affiliation tier split in two, and the promises it maps to

  The steward (2026-10-28): "I am a solo practitioner who wants the data protections — it just is;
  how do we protect that small-business scenario while keeping the protection? The second
  protection is for people; we don't want affiliations to become where despots despot."

  The split: an affiliation bundles two things the text can hold apart. The DATA REGIME (CC
  4.4.3.2.8: classification, retention, legal hold, erasure policy, designated officials, …) attaches
  to the record and its subjects, at any size. The FLOORS (CC 4.5.13: no single vote admits, no
  single vote removes, a named moderator, removal on a harm report by more than one voice) bind
  power over MEMBERS, and the second voice can come from outside the deciding seat: the designated
  official where that is a distinct key, or a review-holder of the body that conferred or oversees
  the affiliation. Hiring is appointment with the appointee's own acceptance: two consents.

  The model is finite and the verdicts are decidable. Every theorem names the promise of the
  constitution's summary it descends from, and `commitments_mapped` checks the map is total.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core.
-/

namespace Affiliation

abbrev Key := Nat

/-- the body: its deciding seats (officers who vote under its protocol), its members (people
    subject to its power), the designated official (a key, which may coincide with a seat), and the
    body that conferred or oversees it (its review-holders) -/
structure Body where
  seats : List Key
  members : List Key
  official : Key
  overseers : List Key
  dataLimbsDeclared : Bool     -- the 4.4.3.2.8 limbs resolve to a value (classification, retention, …)
  deriving Repr

inductive ActKind | appoint | remove | quarantine | slash | takedown
  deriving DecidableEq, Repr

/-- an act of the body touching a member (or appointee) -/
structure Act where
  kind : ActKind
  target : Key
  signers : List Key          -- the seats that signed, under the body's protocol
  countersign : Option Key    -- a second signature from outside the deciding seat
  accepted : Bool             -- the appointee's own acceptance (appointment only)
  deriving Repr

def oneVoice (b : Body) : Bool := b.seats.length == 1

/-- a key is outside the deciding seat when it is not a seat -/
def outsideSeat (b : Body) (k : Key) : Bool := !(b.seats.contains k)

/-- the countersign the floors accept from a one-voice body: the designated official when that key
    is not a seat, or any review-holder of the overseeing body -/
def validCountersign (b : Body) (k : Key) : Bool :=
  (k == b.official && outsideSeat b k) || (b.overseers.contains k && outsideSeat b k)

/-- the body's own signature under its protocol: every signer a seat and at least one -/
def bodySigned (b : Body) (a : Act) : Bool :=
  !a.signers.isEmpty && a.signers.all (fun k => b.seats.contains k)

/-- the floors, as the text now states them for an affiliation:
    * appointment lands on the body's signature AND the appointee's acceptance (two consents);
    * an act against a member lands on the body's signature AND, where the body has one voice, a
      valid countersign from outside the deciding seat; a body of two or more voices decides under
      its own protocol as any community does (its protocol already carries the second voice). -/
def admitted (b : Body) (a : Act) : Bool :=
  match a.kind with
  | .appoint => bodySigned b a && a.accepted
  | _ => bodySigned b a && (if oneVoice b then (match a.countersign with | some k => validCountersign b k | none => false) else true)

/-- the data regime: the limbs bind when declared, whatever the size -/
def dataRegimeBinds (b : Body) : Bool := b.dataLimbsDeclared

/-! ## Theorems, each with the promise it descends from -/

/-- the eleven promises of the summary, by number -/
inductive Promise | p1 | p2 | p3 | p4 | p5 | p6 | p7 | p8 | p9 | p10 | p11
  deriving DecidableEq, Repr

/-- A1 (promise 1, promise 8): the data regime attaches to the record at any size — a one-member
    affiliation that declares the limbs is bound by them -/
theorem a1_data_regime_at_any_size (b : Body) (h : b.dataLimbsDeclared = true) :
    dataRegimeBinds b = true ∧ (b.members.length = 0 → dataRegimeBinds b = true) :=
  ⟨h, fun _ => h⟩

/-- A2 (promise 1, promise 2): a one-voice body can appoint — with the appointee's acceptance -/
theorem a2_one_voice_appoints_with_acceptance (b : Body) (a : Act) (hk : a.kind = .appoint)
    (hs : bodySigned b a = true) (hacc : a.accepted = true) : admitted b a = true := by
  unfold admitted; rw [hk]; simp [hs, hacc]

/-- A2' (promise 1): and never without it — nobody is appointed unconsenting -/
theorem a2_no_appointment_without_acceptance (b : Body) (a : Act) (hk : a.kind = .appoint)
    (hacc : a.accepted = false) : admitted b a = false := by
  unfold admitted; rw [hk]; simp [hacc]

/-- A3 (promise 6, promise 2): a one-voice body removes nobody alone — without a countersign the
    act is not admitted, whatever the seat signed -/
theorem a3_one_voice_removes_nobody_alone (b : Body) (a : Act) (hk : a.kind = .remove)
    (h1 : oneVoice b = true) (hc : a.countersign = none) : admitted b a = false := by
  unfold admitted; rw [hk]; simp [h1, hc]

/-- A3' (promise 6): nor with a countersign from inside the deciding seat — the seat cannot be its
    own second voice -/
theorem a3_seat_cannot_countersign_itself (b : Body) (a : Act) (hk : a.kind = .remove)
    (h1 : oneVoice b = true) (k : Key) (hc : a.countersign = some k) (hin : b.seats.contains k = true) :
    admitted b a = false := by
  unfold admitted; rw [hk]; simp [h1, hc, validCountersign, outsideSeat, hin]
  intro _
  have hm := List.mem_of_elem_eq_true hin
  exact ⟨fun _ => hm, fun _ => hm⟩

/-- A3'' (promise 2, promise 6): with a valid outside countersign the act is admitted, and the act
    carries two named signatures — contestable on the record -/
theorem a3_outside_countersign_admits (b : Body) (a : Act) (hk : a.kind = .remove)
    (h1 : oneVoice b = true) (hs : bodySigned b a = true) (k : Key) (hc : a.countersign = some k)
    (hv : validCountersign b k = true) : admitted b a = true := by
  unfold admitted; rw [hk]; simp [h1, hs, hc, hv]

/-- A4 (promise 4): the same for every act of power over a member — quarantine, slash, takedown —
    none lands on one voice -/
theorem a4_no_power_act_on_one_voice (b : Body) (a : Act) (h1 : oneVoice b = true)
    (hc : a.countersign = none) (hk : a.kind ≠ .appoint) : admitted b a = false := by
  unfold admitted
  cases hkk : a.kind <;> simp [hkk] at hk ⊢ <;> simp [h1, hc]

/-- A5 (promise 6): a body of two or more voices decides under its own protocol, as a community
    does — the countersign rule is the one-voice rule only -/
theorem a5_two_voices_decide_as_a_community (b : Body) (a : Act) (hk : a.kind = .remove)
    (h2 : oneVoice b = false) (hs : bodySigned b a = true) : admitted b a = true := by
  unfold admitted; rw [hk]; simp [h2, hs]

/-! ## The map of commitments

  Each rule names the promises it descends from. `commitments_mapped` checks every rule maps to
  at least one promise, and every promise the split touches is touched: 1 (consent), 2 (every act
  of power signed by a named person and contestable), 4 (the power is bounded and left by leaving),
  6 (no hand bans; nobody ranked by what they are; one voice never decides who is in a room), 8
  (reachable on the record). Promises 3, 5, 7, 9, 10, 11 are not touched by this split. -/

inductive Rule | a1 | a2 | a3 | a4 | a5
  deriving DecidableEq, Repr

def descendsFrom : Rule → List Promise
  | .a1 => [.p1, .p8]
  | .a2 => [.p1, .p2]
  | .a3 => [.p6, .p2]
  | .a4 => [.p4, .p2]
  | .a5 => [.p6]

def Rule.all : List Rule := [.a1, .a2, .a3, .a4, .a5]
def touched : List Promise := [.p1, .p2, .p4, .p6, .p8]

theorem commitments_mapped :
    Rule.all.all (fun r => !(descendsFrom r).isEmpty) = true ∧
    touched.all (fun p => Rule.all.any (fun r => (descendsFrom r).contains p)) = true := by decide

/-! ## The worked world: the solo practitioner

  One seat (the practitioner, key 1), the official is the practitioner too (so no countersign from
  that key), one overseer (the professional body's review-holder, key 9), the limbs declared. She
  appoints an assistant (key 2) who accepts; she cannot remove the assistant alone; with the
  overseer's countersign she can; the assistant's data sits under the declared limbs from day one. -/

def solo : Body := ⟨[1], [], 1, [9], true⟩
def hire : Act := ⟨.appoint, 2, [1], none, true⟩
def fireAlone : Act := ⟨.remove, 2, [1], none, false⟩
def fireSelfCountersigned : Act := ⟨.remove, 2, [1], some 1, false⟩
def fireWithOverseer : Act := ⟨.remove, 2, [1], some 9, false⟩

theorem solo_is_bound_by_the_limbs : dataRegimeBinds solo = true := by decide
theorem solo_hires : admitted solo hire = true := by decide
theorem solo_cannot_fire_alone : admitted solo fireAlone = false := by decide
theorem solo_cannot_countersign_herself : admitted solo fireSelfCountersigned = false := by decide
theorem solo_fires_with_the_overseer : admitted solo fireWithOverseer = true := by decide

/-- a two-seat body (a partnership): removal under its own protocol, no countersign needed -/
def partnership : Body := ⟨[1, 3], [2], 1, [], true⟩
def partnersFire : Act := ⟨.remove, 2, [1, 3], none, false⟩
theorem partners_decide_as_a_community : admitted partnership partnersFire = true := by decide

end Affiliation
