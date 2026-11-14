/-!
# The moderator election: a locked room chooses by ranked choice of three

CC 4.5.13: a community with no live holder of `moderate` is read-only until a 24 h ranked-choice
vote over its own roster seats one. Each person ranks up to three, one ballot per person, the
count is instant-runoff and order-free, and the winner accepts by their own row or the duty
passes to the next in runoff order.

The general ranked count breaks a tie for weakest against the option later in the choice's
declared order. An election declares no order, so a tie there seats nobody and the count runs
again (CC 4.5.13). The ballot's shown order "is presentation only: it confers nothing and decides
nothing" (CC 4.5.4).

`count brk` is instant runoff with the tie rule as a parameter: `later order` is the declared
order's, `noOrder` is the election's and settles no tie.

Proved:
- (i) with no declared order the result does not depend on the order the options are listed in
  (`free_perm`);
- (ii) it agrees with the declared-order count whenever it seats anyone, that is whenever no tie
  for weakest arose (`free_agrees`), and a tie for weakest seats nobody (`free_tie_seats_nobody`);
- (iii) one ballot per person, and a person whose ballots disagree has none (`fold_unique`,
  `fold_disagree_none`);
- (iv) nobody is seated below two voices (`below_floor`);
- a winner is a member of the roster under either rule (`winner_in_roster`, `free_in_roster`);
- the vote count of an option is a function of the multiset of ballots (`votesFor_perm`);
- the acceptance chain seats the first in runoff order who accepts and nobody who declined.
-/

/-- A ballot: a person and up to three members in order of preference. -/
structure Ballot where
  person : Nat
  ranks : List Nat
  deriving DecidableEq, Repr

/-- The first ballot of each person, in a canonical order. -/
def dedupe : List Ballot → List Ballot
  | [] => []
  | b :: bs => b :: (dedupe bs).filter (fun c => c.person != b.person)

/-- Every ballot of `b`'s person ranks as `b` does. -/
def agreed (bs : List Ballot) (b : Ballot) : Bool :=
  bs.all (fun c => c.person != b.person || c.ranks == b.ranks)

/-- One ballot per person, and a person whose ballots disagree has none (the fold `pick=agree`). -/
def fold (bs : List Ballot) : List Ballot := (dedupe bs).filter (agreed bs)

/-- A ballot's current first choice among the options still standing. -/
def firstStanding (standing : List Nat) (b : Ballot) : Option Nat :=
  b.ranks.find? (fun c => standing.contains c)

/-- Votes for `c` among ballots whose first standing choice is `c`. -/
def votesFor (standing : List Nat) (bs : List Ballot) (c : Nat) : Nat :=
  (bs.filter (fun b => firstStanding standing b = some c)).length

/-- The ballots still counting: those that rank a standing option. -/
def live (standing : List Nat) (bs : List Ballot) : Nat :=
  (bs.filter (fun b => (firstStanding standing b).isSome)).length

/-- The one element of a list of one. -/
def single? : List Nat → Option Nat
  | [w] => some w
  | _ => none

/-- The standing options with more than half the ballots still counting. -/
def leaders (standing : List Nat) (bs : List Ballot) : List Nat :=
  standing.filter (fun c => live standing bs < 2 * votesFor standing bs c)

/-- Every standing option with the fewest votes. -/
def weakest (standing : List Nat) (bs : List Ballot) : List Nat :=
  standing.filter (fun c => standing.all (fun d => votesFor standing bs c ≤ votesFor standing bs d))

/-- The option to eliminate: the one weakest, or, on a tie, what the tie rule `brk` gives. -/
def pick (brk : List Nat → Option Nat) (ws : List Nat) : Option Nat :=
  match single? ws with
  | some w => some w
  | none => brk ws

/-- The declared order's tie rule: the tied option latest in `order` goes. -/
def later (order : List Nat) (ws : List Nat) : Option Nat :=
  order.reverse.find? (fun c => ws.contains c)

/-- The election's tie rule: there is no order, so no tie is settled. -/
def noOrder (_ : List Nat) : Option Nat := none

/-- Instant runoff: while no option holds more than half the ballots still counting, the weakest
    goes and its ballots pass to their next standing choice. `none` is nobody seated. -/
def count (brk : List Nat → Option Nat) (bs : List Ballot) : Nat → List Nat → Option Nat
  | 0, _ => none
  | fuel + 1, standing =>
    match single? standing with
    | some w => some w
    | none =>
      if live standing bs = 0 then none
      else match single? (leaders standing bs) with
        | some c => some c
        | none =>
          match pick brk (weakest standing bs) with
          | some w => count brk bs fuel (standing.filter (· != w))
          | none => none

/-- The general count, with the roster as the declared order. -/
def winner (roster : List Nat) (bs0 : List Ballot) : Option Nat :=
  let bs := fold bs0
  if bs.length < 2 then none else count (later roster) bs (roster.length + 1) roster

/-- The election's count: no declared order. -/
def winnerFree (roster : List Nat) (bs0 : List Ballot) : Option Nat :=
  let bs := fold bs0
  if bs.length < 2 then none else count noOrder bs (roster.length + 1) roster

/-! ## (i) With no declared order, the listing of the options decides nothing -/

theorem contains_perm {s s' : List Nat} (h : s.Perm s') (c : Nat) : s.contains c = s'.contains c := by
  simp [List.contains, List.elem_eq_mem, h.mem_iff]

theorem all_perm {s s' : List Nat} (h : s.Perm s') (p : Nat → Bool) : s.all p = s'.all p := by
  apply Bool.eq_iff_iff.2; simp [List.all_eq_true, h.mem_iff]

theorem firstStanding_perm {s s' : List Nat} (h : s.Perm s') (b : Ballot) :
    firstStanding s b = firstStanding s' b := by
  unfold firstStanding
  have : (fun c => s.contains c) = (fun c => s'.contains c) := funext (contains_perm h)
  rw [this]

theorem votesFor_standing_perm {s s' : List Nat} (h : s.Perm s') (bs : List Ballot) (c : Nat) :
    votesFor s bs c = votesFor s' bs c := by
  unfold votesFor
  have : (fun b => decide (firstStanding s b = some c)) = (fun b => decide (firstStanding s' b = some c)) :=
    funext (fun b => by rw [firstStanding_perm h])
  rw [this]

theorem live_perm {s s' : List Nat} (h : s.Perm s') (bs : List Ballot) : live s bs = live s' bs := by
  unfold live
  have : (fun b => (firstStanding s b).isSome) = (fun b => (firstStanding s' b).isSome) :=
    funext (fun b => by rw [firstStanding_perm h])
  rw [this]

theorem single?_perm {l l' : List Nat} (h : l.Perm l') : single? l = single? l' := by
  cases e : single? l with
  | some w =>
    have hl : l = [w] := by
      match l, e with
      | [x], e => simp [single?] at e; rw [e]
    rw [hl] at h
    rw [List.perm_singleton.mp h.symm]; rfl
  | none =>
    cases e' : single? l' with
    | none => rfl
    | some w =>
      have hl : l' = [w] := by
        match l', e' with
        | [x], e' => simp [single?] at e'; rw [e']
      rw [hl] at h
      rw [List.perm_singleton.mp h] at e; simp [single?] at e

theorem leaders_perm {s s' : List Nat} (h : s.Perm s') (bs : List Ballot) :
    (leaders s bs).Perm (leaders s' bs) := by
  unfold leaders
  have : (fun c => decide (live s bs < 2 * votesFor s bs c)) = (fun c => decide (live s' bs < 2 * votesFor s' bs c)) :=
    funext (fun c => by rw [live_perm h, votesFor_standing_perm h])
  rw [this]; exact h.filter _

theorem weakest_perm {s s' : List Nat} (h : s.Perm s') (bs : List Ballot) :
    (weakest s bs).Perm (weakest s' bs) := by
  unfold weakest
  have : (fun c => s.all (fun d => decide (votesFor s bs c ≤ votesFor s bs d)))
       = (fun c => s'.all (fun d => decide (votesFor s' bs c ≤ votesFor s' bs d))) := by
    funext c
    rw [all_perm h]
    have : (fun d => decide (votesFor s bs c ≤ votesFor s bs d)) = (fun d => decide (votesFor s' bs c ≤ votesFor s' bs d)) :=
      funext (fun d => by rw [votesFor_standing_perm h, votesFor_standing_perm h])
    rw [this]
  rw [this]; exact h.filter _

theorem count_free_perm (bs : List Ballot) :
    ∀ fuel (s s' : List Nat), s.Perm s' → count noOrder bs fuel s = count noOrder bs fuel s' := by
  intro fuel
  induction fuel with
  | zero => intro s s' _; rfl
  | succ k ih =>
    intro s s' h
    simp only [count]
    rw [single?_perm h, live_perm h, single?_perm (leaders_perm h bs)]
    have hp : pick noOrder (weakest s bs) = pick noOrder (weakest s' bs) := by
      unfold pick noOrder; rw [single?_perm (weakest_perm h bs)]
    rw [hp]
    split
    · rfl
    · split
      · rfl
      · split
        · rfl
        · split
          · rename_i w _
            exact ih _ _ (h.filter _)
          · rfl

/-- (i) With no declared order, listing the options in another order changes nothing. -/
theorem free_perm (roster roster' : List Nat) (h : roster.Perm roster') (bs : List Ballot) :
    winnerFree roster bs = winnerFree roster' bs := by
  unfold winnerFree
  simp only
  rw [h.length_eq, count_free_perm _ _ _ _ h]

/-! ## (ii) It agrees with the declared count whenever it seats anyone -/

theorem count_agrees (brk : List Nat → Option Nat) (bs : List Ballot) (w : Nat) :
    ∀ fuel (s : List Nat), count noOrder bs fuel s = some w → count brk bs fuel s = some w := by
  intro fuel
  induction fuel with
  | zero => intro s h; simp [count] at h
  | succ k ih =>
    intro s h
    simp only [count] at h ⊢
    split at h
    · exact h
    · split at h
      · cases h
      · rename_i hl; rw [if_neg hl]
        split at h
        · exact h
        · cases hw : single? (weakest s bs) with
          | none => simp [pick, hw, noOrder] at h
          | some v =>
            simp [pick, hw] at h ⊢
            exact ih _ h

/-- (ii) Where the election's count seats someone, the declared count seats the same one. -/
theorem free_agrees (roster : List Nat) (bs : List Ballot) (w : Nat)
    (h : winnerFree roster bs = some w) : winner roster bs = some w := by
  unfold winnerFree at h; unfold winner
  simp only at h ⊢
  split at h
  · cases h
  · rename_i hf; rw [if_neg hf]; exact count_agrees _ _ _ _ _ h

/-- (ii) A tie for weakest, with no option over half and more than one standing, seats nobody. -/
theorem free_tie_seats_nobody (bs : List Ballot) (k : Nat) (s : List Nat)
    (h1 : single? s = none) (h2 : live s bs ≠ 0) (h3 : single? (leaders s bs) = none)
    (h4 : single? (weakest s bs) = none) : count noOrder bs (k + 1) s = none := by
  simp [count, h1, h2, h3, pick, h4, noOrder]

/-! ## (iii) One ballot per person; a person whose ballots disagree has none -/

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

theorem fold_unique (bs : List Ballot) :
    ∀ b ∈ fold bs, ∀ c ∈ fold bs, b.person = c.person → b = c := by
  intro b hb c hc hp
  exact dedupe_unique bs b (List.mem_filter.mp hb).1 c (List.mem_filter.mp hc).1 hp

theorem fold_disagree_none (bs : List Ballot) (b1 b2 : Ballot) (h1 : b1 ∈ bs) (h2 : b2 ∈ bs)
    (hp : b1.person = b2.person) (hr : b1.ranks ≠ b2.ranks) :
    ∀ b ∈ fold bs, b.person ≠ b1.person := by
  intro b hb hbp
  have ha := (List.mem_filter.mp hb).2
  simp only [agreed, List.all_eq_true] at ha
  have e1 := ha b1 h1
  have e2 := ha b2 h2
  simp [bne, hbp, ← hp] at e1 e2
  exact hr (e1.trans e2.symm)

/-! ## (iv) Nobody is seated below two voices -/

theorem below_floor (roster : List Nat) (bs : List Ballot) (h : (fold bs).length < 2) :
    winner roster bs = none ∧ winnerFree roster bs = none := by
  unfold winner winnerFree; simp [h]

/-- No ballots, no winner: the room stays locked and the ballot stays open until a seating lands. -/
theorem no_ballots_no_winner (roster : List Nat) : winner roster [] = none ∧ winnerFree roster [] = none :=
  below_floor roster [] (by decide)

/-! ## A winner is a member of the roster -/

theorem single?_mem {l : List Nat} {w : Nat} (h : single? l = some w) : w ∈ l := by
  match l, h with
  | [x], h => simp [single?] at h; simp [h]

theorem count_mem (brk : List Nat → Option Nat) (bs : List Ballot) :
    ∀ fuel (s : List Nat) (w : Nat), count brk bs fuel s = some w → w ∈ s := by
  intro fuel
  induction fuel with
  | zero => intro s w h; simp [count] at h
  | succ k ih =>
    intro s w h
    simp only [count] at h
    split at h
    · rename_i hs; cases h; exact single?_mem hs
    · split at h
      · cases h
      · split at h
        · rename_i c hc; cases h; exact (List.mem_filter.mp (single?_mem hc)).1
        · split at h
          · exact (List.mem_filter.mp (ih _ _ h)).1
          · cases h

theorem winner_in_roster (roster : List Nat) (bs : List Ballot) (w : Nat)
    (h : winner roster bs = some w) : w ∈ roster := by
  unfold winner at h; simp only at h
  split at h
  · cases h
  · exact count_mem _ _ _ _ _ h

theorem free_in_roster (roster : List Nat) (bs : List Ballot) (w : Nat)
    (h : winnerFree roster bs = some w) : w ∈ roster :=
  winner_in_roster roster bs w (free_agrees roster bs w h)

/-! ## The count of an option is a function of the multiset of ballots -/

theorem votesFor_perm (standing : List Nat) (bs bs' : List Ballot) (h : bs.Perm bs') (c : Nat) :
    votesFor standing bs c = votesFor standing bs' c := by
  unfold votesFor
  exact (h.filter _).length_eq

/-! ## The acceptance chain -/

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

/-! ## Worked examples -/

/-- Three members, roster [1, 2, 3]; each is one ballot's first choice, a three-way tie for weakest. -/
def exampleBallots : List Ballot :=
  [⟨10, [1, 2]⟩, ⟨11, [2, 1]⟩, ⟨12, [3, 2, 1]⟩]

/-- The declared count: 3 is latest in the order and goes, its ballot passes to 2, and 2 wins 2 to 1. -/
theorem example_winner : winner [1, 2, 3] exampleBallots = some 2 := by decide

/-- The election's count: the tie seats nobody, and the count runs again. -/
theorem example_free_tie : winnerFree [1, 2, 3] exampleBallots = none := by decide

/-- Repeating a ballot changes nothing. -/
theorem example_repeat_ballot :
    winner [1, 2, 3] (exampleBallots ++ [⟨10, [1, 2]⟩]) = some 2 := by decide

/-- A person whose two ballots disagree has none: person 10 drops out. -/
theorem example_disagree_dropped :
    fold (exampleBallots ++ [⟨10, [3]⟩]) = [⟨11, [2, 1]⟩, ⟨12, [3, 2, 1]⟩] := by decide

/-- No tie: 3 alone is weakest, its ballot passes to 1, and 1 wins 3 to 2 under either rule and in
    any listing of the options. -/
def exampleClear : List Ballot :=
  [⟨10, [1, 2]⟩, ⟨11, [2, 1]⟩, ⟨12, [2, 3]⟩, ⟨13, [3, 1]⟩, ⟨14, [1]⟩]

theorem example_clear :
    winnerFree [1, 2, 3] exampleClear = some 1 ∧ winnerFree [3, 1, 2] exampleClear = some 1 ∧
    winner [1, 2, 3] exampleClear = some 1 := by decide

/-- The winner declines; the next in runoff order who accepts is seated. -/
theorem example_decline_passes :
    seat [2, 1, 3] (fun n => n != 2) = some 1 := by decide
