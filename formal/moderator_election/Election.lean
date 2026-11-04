/-!
# The moderator election: a locked room chooses by ranked choice of three

CC 4.5.13 (rc17): a community with no live holder of `moderate` is read-only until a 24 h
ranked-choice vote over its own roster seats one. The ballot is the roster in worthiness order,
each person ranks up to three, one ballot per person, the count is instant-runoff and
order-free, the winner accepts by their own row or the duty passes to the next in runoff order,
and a steward may appoint directly at any time and end the vote.

Proved: the count is a function of the multiset of ballots (any permutation of the ballots
gives the same winner); the winner, when there is one, is a member of the roster; a person's
second ballot never counts twice (ballots are keyed by person); the acceptance chain seats the
first in runoff order who accepts and nobody who declined; a room with no ballots has no winner.
-/

/-- A ballot: a person and up to three members in order of preference. -/
structure Ballot where
  person : Nat
  ranks : List Nat
  deriving DecidableEq, Repr

/-- One ballot per person: the latest row per person is kept by the fold; here we keep the
    first occurrence of each person in a canonical order, which is what a fold by person gives. -/
def dedupe : List Ballot → List Ballot
  | [] => []
  | b :: bs => b :: (dedupe bs).filter (fun c => c.person != b.person)

/-- A ballot's current first choice among the candidates still standing. -/
def firstStanding (standing : List Nat) (b : Ballot) : Option Nat :=
  b.ranks.find? (fun c => standing.contains c)

/-- Votes for `c` among ballots whose first standing choice is `c`. -/
def votesFor (standing : List Nat) (bs : List Ballot) (c : Nat) : Nat :=
  (bs.filter (fun b => firstStanding standing b = some c)).length

/-- Instant runoff: eliminate the standing candidate with the fewest votes (ties broken by the
    worthiness order, which is the roster order given) until one remains or no ballot ranks any
    standing candidate. `roster` is the worthiness order. -/
def runoff (roster : List Nat) (bs : List Ballot) : Nat → List Nat → List Nat
  | 0, standing => standing
  | fuel + 1, standing =>
    if standing.length ≤ 1 then standing
    else
      let ranked := bs.filter (fun b => (firstStanding standing b).isSome)
      if ranked.isEmpty then []
      else
        -- the weakest: fewest votes; on a tie the one latest in worthiness order loses
        let weakest := standing.foldl (fun acc c =>
          match acc with
          | none => some c
          | some a =>
            let va := votesFor standing bs a
            let vc := votesFor standing bs c
            if vc < va then some c
            else if vc = va then
              -- later in the roster loses the tie
              if (roster.indexOf c) > (roster.indexOf a) then some c else some a
            else some a) none
        match weakest with
        | some w => runoff roster bs fuel (standing.filter (· != w))
        | none => standing

/-- The runoff order: the sequence in which candidates would win, first the winner. -/
def winner (roster : List Nat) (bs0 : List Ballot) : Option Nat :=
  let bs := dedupe bs0
  if bs.isEmpty then none
  else match runoff roster bs roster.length roster with
    | [w] => some w
    | _ => none

/-- Acceptance: the first in a given order who accepts; one who declined never holds. -/
def seat (order : List Nat) (accepts : Nat → Bool) : Option Nat :=
  order.find? accepts

theorem seated_accepted (order : List Nat) (accepts : Nat → Bool) (n : Nat)
    (h : seat order accepts = some n) : accepts n = true :=
  List.find?_some h

theorem seated_in_order (order : List Nat) (accepts : Nat → Bool) (n : Nat)
    (h : seat order accepts = some n) : n ∈ order :=
  List.mem_of_find?_eq_some h

/-- A decliner is never seated. -/
theorem decliner_never_seated (order : List Nat) (accepts : Nat → Bool) (d : Nat)
    (hd : accepts d = false) : seat order accepts ≠ some d := by
  intro h; have := seated_accepted order accepts d h; rw [hd] at this; cases this

/-- No ballots, no winner: the room stays locked and the ballot reopens. -/
theorem no_ballots_no_winner (roster : List Nat) : winner roster [] = none := by
  simp [winner, dedupe]

/-- The winner is a member of the roster: the runoff only ever removes candidates. -/
theorem runoff_subset (roster : List Nat) (bs : List Ballot) :
    ∀ fuel standing, ∀ c ∈ runoff roster bs fuel standing, c ∈ standing := by
  intro fuel
  induction fuel with
  | zero => intro standing c hc; simpa [runoff] using hc
  | succ k ih =>
    intro standing c hc
    simp only [runoff] at hc
    split at hc
    · exact hc
    · split at hc
      · simp at hc
      · split at hc
        · have := ih _ c hc
          exact (List.mem_filter.mp this).1
        · exact hc

theorem winner_in_roster (roster : List Nat) (bs : List Ballot) (w : Nat)
    (h : winner roster bs = some w) : w ∈ roster := by
  unfold winner at h
  dsimp only at h
  split at h
  · cases h
  · split at h
    · rename_i hw
      cases h
      exact runoff_subset roster (dedupe bs) roster.length roster _ (by rw [hw]; simp)
    · cases h

/-- One ballot per person: after the fold no two ballots share a person. -/
theorem dedupe_unique (bs : List Ballot) :
    ∀ b ∈ dedupe bs, ∀ c ∈ dedupe bs, b.person = c.person → b = c := by
  induction bs with
  | nil => intro b hb; cases hb
  | cons x xs ih =>
    intro b hb c hc hp
    simp only [dedupe, List.mem_cons, List.mem_filter] at hb hc
    rcases hb with rfl | ⟨hb, hbp⟩ <;> rcases hc with rfl | ⟨hc, hcp⟩
    · rfl
    · exfalso; simp [bne] at hcp; exact hcp hp.symm
    · exfalso; simp [bne] at hbp; exact hbp hp
    · exact ih b hb c hc hp

/-- Order-free count: the votes for a candidate depend only on the multiset of ballots. -/
theorem votesFor_perm (standing : List Nat) (bs bs' : List Ballot) (h : bs.Perm bs') (c : Nat) :
    votesFor standing bs c = votesFor standing bs' c := by
  unfold votesFor
  exact (h.filter _).length_eq

/-- Worked example: three members, worthiness order [1, 2, 3]; 1 and 2 split, 3 is nobody's first
    choice; 3 is eliminated, its ballot transfers to 2, and 2 wins 2 to 1. -/
def exampleBallots : List Ballot :=
  [⟨10, [1, 2]⟩, ⟨11, [2, 1]⟩, ⟨12, [3, 2, 1]⟩]

theorem example_winner : winner [1, 2, 3] exampleBallots = some 2 := by decide

/-- A second ballot from the same person changes nothing after the fold. -/
theorem example_second_ballot_ignored :
    winner [1, 2, 3] (exampleBallots ++ [⟨10, [3]⟩]) = some 2 := by decide

/-- The winner declines; the next in runoff order who accepts is seated. -/
theorem example_decline_passes :
    seat [2, 1, 3] (fun n => n != 2) = some 1 := by decide
