/-
  formal/standing/Standing.lean — standing over a row that names another person

  CC 2.1: a key listed in subject_key_ids holds consent authority over the row (it may withdraw it
  and emit consent about it). CC 3.4.5: the subject of a row holds standing to file reconsideration
  and is promised a read over the rows it is party to. CC 6.1.5.3 / 5.2: a bounded cohort's rows
  reach its members and nobody else. CC 2.4.1.1: a subject may not withdraw an adverse record about
  itself (capacity, detection, licensure, revocation; the accountability record), only contest it;
  a cosigned row is undone only cosigned (Rule 0).

  The question this file settles: whom may a row at a bounded scope name? Three admission policies
  are compared on one world: the loose reading (any key), the strict reading (only the producer),
  and the audience rule (only keys the row reaches: members of the cohort by the roster fold at the
  row's instant, or the key the family delivers the row to). The audience rule is the one under
  which standing always comes with reach and a community can still speak about its own members.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core.
-/

namespace Standing

abbrev Key := Nat
abbrev Instant := Nat

inductive Kind | scores | delegatesTo | cosigned
  deriving DecidableEq, Repr

/-- a cohort is its roster fold: who is a member at an instant (CC 3.1.3.2; the same fold every
    bounded-scope door uses) -/
structure Cohort where
  members : Instant → List Key

structure Row where
  producer : Key
  cohort : Nat                 -- 0 = federation (everyone); n ≥ 1 indexes a bounded cohort
  instant : Instant            -- asserted_at
  kind : Kind
  subjects : List Key          -- subject_key_ids
  deliveredTo : List Key       -- the key the family delivers the row to (invitee, recipient, own node)
  accountability : Bool        -- hard_case / moderation / slashing / capacity / detection / licensure / revocation
  deriving Repr

structure World where
  everyone : List Key
  cohorts : List Cohort

def membersAt (w : World) (c : Nat) (t : Instant) : List Key :=
  match w.cohorts.get? (c - 1) with
  | some co => co.members t
  | none => []

/-- who the row reaches: everyone at federation scope; at a bounded scope the cohort's members at
    the row's instant, plus the key the family delivers it to -/
def audience (w : World) (r : Row) : List Key :=
  (if r.cohort = 0 then w.everyone else membersAt w r.cohort r.instant) ++ r.deliveredTo

def reaches (w : World) (r : Row) (k : Key) : Bool := (audience w r).contains k

/-- consent standing: the key is a listed subject (CC 2.1) -/
def hasStanding (r : Row) (k : Key) : Bool := r.subjects.contains k

/-! ## Three admission policies for a row naming another person -/

/-- the loose reading: any key may be named at any scope -/
def admitLoose (_ : World) (_ : Row) : Bool := true

/-- the strict reading: at a bounded scope a row names nobody but its producer -/
def admitStrict (_ : World) (r : Row) : Bool :=
  r.cohort = 0 || r.subjects.all (fun s => s == r.producer)

/-- the audience rule: every named subject is within the row's audience -/
def admitAudience (w : World) (r : Row) : Bool := r.subjects.all (fun s => reaches w r s)

/-! ## What a subject may do with a row about it -/

/-- withdraw: the producer always; a subject under CC 2.4.1.1 rule 2, except an adverse record
    (contest only) and a cosigned row (Rule 0) -/
def mayWithdraw (r : Row) (k : Key) : Bool :=
  k == r.producer || (hasStanding r k && !r.accountability && r.kind != .cosigned)

/-- contest: every subject, always (CC 3.4.5 reconsideration) -/
def mayContest (r : Row) (k : Key) : Bool := hasStanding r k

/-! ## Theorems -/

/-- under the audience rule, standing always comes with reach: a subject of an admitted row can
    see the row it may withdraw or contest (CC 3.4.5's promise, kept by construction) -/
theorem standing_reaches (w : World) (r : Row) (k : Key)
    (h : admitAudience w r = true) (hs : hasStanding r k = true) : reaches w r k = true := by
  unfold admitAudience at h; unfold hasStanding at hs
  have := List.all_eq_true.mp h k (List.mem_of_elem_eq_true hs)
  simpa using this

/-- a subject's contest path is never closed by the kind of row: whatever the row is, a listed
    subject may contest it -/
theorem contest_always_open (r : Row) (k : Key) (hs : hasStanding r k = true) :
    mayContest r k = true := hs

/-- an adverse record is contest-only for its subject: no subject withdraws it (unless the subject
    is the producer) -/
theorem adverse_is_contest_only (r : Row) (k : Key) (ha : r.accountability = true)
    (hk : k ≠ r.producer) : mayWithdraw r k = false := by
  unfold mayWithdraw; simp [ha, hk]

/-- a cosigned row is undone only cosigned: a listed subject alone cannot withdraw it -/
theorem cosigned_undone_only_cosigned (r : Row) (k : Key) (hc : r.kind = .cosigned)
    (hk : k ≠ r.producer) : mayWithdraw r k = false := by
  unfold mayWithdraw; simp [hc, hk]

/-! ## The worked world

  Everyone = keys 1..9. Cohort 1 is a community whose roster is {1, 2, 3} until instant 5, when 3
  is removed, leaving {1, 2}. Key 7 belongs to no cohort. Key 9 is a stranger invited by 1. -/

def room : Cohort := ⟨fun t => if t < 5 then [1, 2, 3] else [1, 2]⟩
def w : World := ⟨[1, 2, 3, 4, 5, 6, 7, 8, 9], [room]⟩

/-- member 1 scores member 2 inside the room, at instant 6 -/
def scoreAbout2 : Row := ⟨1, 1, 6, .scores, [2], [], false⟩
/-- member 1 scores 3 at instant 6, after 3 was removed -/
def scoreAbout3Late : Row := ⟨1, 1, 6, .scores, [3], [], false⟩
/-- member 1 scores 3 at instant 4, while 3 was a member -/
def scoreAbout3Early : Row := ⟨1, 1, 4, .scores, [3], [], false⟩
/-- member 1 names outsider 7 inside the room, nothing delivered to 7 -/
def about7 : Row := ⟨1, 1, 6, .scores, [7], [], false⟩
/-- a proposal: member 1 invites stranger 9, the family delivering the row to 9 -/
def proposalTo9 : Row := ⟨1, 1, 6, .scores, [9], [9], false⟩
/-- a hard_case about member 2, filed by 1 -/
def hardCaseAbout2 : Row := ⟨1, 1, 6, .scores, [2], [], true⟩
/-- the room removes 3: a cosigned row naming 3 -/
def removal3 : Row := ⟨1, 1, 5, .cosigned, [3], [], false⟩

/-- the audience rule lets a community speak about its own members -/
theorem audience_admits_a_score_about_a_member : admitAudience w scoreAbout2 = true := by decide
/-- the strict reading forbids it: a community could score nobody but the scorer -/
theorem strict_refuses_a_score_about_a_member : admitStrict w scoreAbout2 = false := by decide
/-- the loose reading admits a row whose subject can never see it: standing without reach -/
theorem loose_gives_standing_without_reach :
    admitLoose w about7 = true ∧ hasStanding about7 7 = true ∧ reaches w about7 7 = false := by decide
/-- the audience rule refuses that row -/
theorem audience_refuses_the_unreachable_subject : admitAudience w about7 = false := by decide
/-- the delivered key is within the audience: an invitee may be named -/
theorem invitee_is_reached : admitAudience w proposalTo9 = true ∧ reaches w proposalTo9 9 = true := by decide
/-- membership is judged at the row's instant: a member removed before it is outside -/
theorem removed_before_the_instant_is_outside :
    admitAudience w scoreAbout3Late = false ∧ admitAudience w scoreAbout3Early = true := by decide
/-- a subject of an admitted row may withdraw an ordinary score and only contest a hard_case -/
theorem subject_withdraws_a_score_contests_a_hard_case :
    mayWithdraw scoreAbout2 2 = true ∧ mayWithdraw hardCaseAbout2 2 = false ∧ mayContest hardCaseAbout2 2 = true := by decide
/-- the removed member cannot withdraw the cosigned removal, and may contest it -/
theorem removal_is_contested_not_withdrawn :
    mayWithdraw removal3 3 = false ∧ mayContest removal3 3 = true := by decide

end Standing
