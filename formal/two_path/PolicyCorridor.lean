/-
  PolicyCorridor.lean — the admissible region of two-path policies (steward direction 2026-10-18):
  a governance policy (enact fraction, cancel fraction, window, irreversible) must lie in a
  corridor between the most open community the constitution allows (a takedown very hard) and
  the most restricted (a takedown very easy), across roster and content, invites and accepts,
  so that no roster can configure itself into an extreme. The shape is coherence-ratchet's
  consent corridor (`Core/ConsentFoundation.lean`: consent impossible at the rigidity pole and
  at the chaos pole, possible in the corridor) applied to thresholds.

  Known results the corridor rests on (stated, not re-proved here):
    - the rigidity pole is unanimity / the single veto (Poland's liberum veto; Buchanan & Tullock
      1962: decision cost diverges as the required majority approaches 1);
    - the chaos pole is simple or sub-majority enactment without a check (Greenberg 1979 and
      Caplin & Nalebuff 1988: a stable collective choice exists for all profiles only above a
      supermajority bound — 64 % in the Euclidean case — so below it any coalition can be
      undone by the next, which for a takedown means anyone's content goes on one voice);
    - the standing-versus-live question is Olson 1965 and the participation literature: the
      active fraction of a group falls with its size, so a fixed fraction of the standing
      roster becomes unreachable above some size and the reverse path silently dies.

  Everything is on naturals with fractions as num/den; thresholds are read as "votes * den
  (>|>=) num * base". Core Lean 4.14, no Mathlib, no sorry.
-/

namespace TwoPathCorridor

/-- a policy: enact, cancel and floor as fractions, window in seconds, irreversible.
    The floor (steward 2026-10-18, on membership: "I don't like a single vote being able to admit
    someone to a 10k community") is the least approval the reverse path needs before silence may
    land a change; without it the reverse path is the chaos pole reached through the back door. -/
structure Policy where
  enactNum : Nat
  enactDen : Nat
  cancelNum : Nat
  cancelDen : Nat
  floorNum : Nat
  floorDen : Nat
  windowSecs : Nat
  irreversible : Bool
  enactDenPos : 0 < enactDen
  cancelDenPos : 0 < cancelDen
  floorDenPos : 0 < floorDen

/-- the base the fractions are taken over: the standing roster N, or an expected-active count -/
def enactVotes (p : Policy) (base : Nat) : Nat := p.enactNum * base / p.enactDen + 1   -- strict: more than the fraction
def cancelVotes (p : Policy) (base : Nat) : Nat := (p.cancelNum * base + p.cancelDen - 1) / p.cancelDen  -- at least the fraction
def floorVotes (p : Policy) (base : Nat) : Nat := (p.floorNum * base + p.floorDen - 1) / p.floorDen     -- at least the fraction

/- ---- the two poles, stated as what breaks ---- -/

/-- rigidity: the cancel threshold is reachable by one voter, or enact needs everyone — then a
    single coerced key blocks every change (liveness dies) -/
def rigidityPole (p : Policy) (base : Nat) : Bool :=
  decide (cancelVotes p base ≤ 1) || decide (enactVotes p base ≥ base)

/-- chaos: enact is reachable by one voter, or cancel needs everyone — then one key enacts a
    takedown and nothing can stop it (safety dies) -/
def chaosPole (p : Policy) (base : Nat) : Bool :=
  decide (enactVotes p base ≤ 1) || decide (cancelVotes p base ≥ base)
  || decide (floorVotes p base ≤ 1)      -- one voice lands by silence: the back door to the same pole

/-- the corridor: neither pole, cancel ≤ enact, an enact floor of a strict majority, a window
    floor by sensitivity (the constitution's constants: 24 h for the halt fuse, 72 h for W) -/
def inCorridor (p : Policy) (base windowFloor : Nat) : Bool :=
  !rigidityPole p base && !chaosPole p base
  && decide (p.cancelNum * p.enactDen ≤ p.enactNum * p.cancelDen)       -- cancel ≤ enact
  && decide (2 * p.enactNum ≥ p.enactDen)                               -- enact ≥ 1/2 (strict in use)
  && decide (p.floorNum * p.enactDen ≤ p.enactNum * p.floorDen)         -- floor ≤ enact
  && decide (windowFloor ≤ p.windowSecs)

/-- the steward's example: enact 2/3, cancel 1/3, 72 h — in the corridor at N = 6 -/
def ruled : Policy := ⟨2, 3, 1, 3, 1, 3, 259200, false, by decide, by decide, by decide⟩
theorem ruled_in_corridor : inCorridor ruled 6 86400 = true := by decide
theorem ruled_in_corridor_at_7 : inCorridor ruled 7 86400 = true := by decide

/-- the self roster: strict majority both ways at N = 3, and a floor of one key — the one roster
    where one voice on the reverse path is right, because every key is the same person's; it is
    therefore outside the community corridor by the floor clause and inside its own (3.3.6.3) -/
def selfRoster : Policy := ⟨1, 2, 1, 2, 1, 3, 86400, false, by decide, by decide, by decide⟩
theorem self_roster_floor_is_one : floorVotes selfRoster 3 = 1 := rfl
theorem self_roster_outside_community_corridor : inCorridor selfRoster 3 86400 = false := by decide
/-- the community corridor without the floor clause, for the self roster's own check -/
def inCorridorNoFloor (p : Policy) (base windowFloor : Nat) : Bool :=
  !rigidityPole p base && !(decide (enactVotes p base ≤ 1) || decide (cancelVotes p base ≥ base))
  && decide (p.cancelNum * p.enactDen ≤ p.enactNum * p.cancelDen)
  && decide (2 * p.enactNum ≥ p.enactDen) && decide (windowFloor ≤ p.windowSecs)
theorem self_roster_in_own_corridor : inCorridorNoFloor selfRoster 3 86400 = true := by decide

/-- the poles, each excluded -/
def libertumVeto : Policy := ⟨2, 3, 1, 6, 1, 3, 259200, false, by decide, by decide, by decide⟩   -- one of six cancels
theorem one_voice_cancels_is_rigidity : rigidityPole libertumVeto 6 = true := by decide
theorem rigidity_outside : inCorridor libertumVeto 6 86400 = false := by decide

def oneEnacts : Policy := ⟨1, 7, 1, 3, 1, 7, 259200, false, by decide, by decide, by decide⟩       -- enact below 1/N: one of six enacts a takedown
theorem one_voice_enacts_is_chaos : chaosPole oneEnacts 6 = true := by decide
theorem chaos_outside : inCorridor oneEnacts 6 86400 = false := by decide

def unanimity : Policy := ⟨1, 1, 1, 3, 1, 3, 259200, false, by decide, by decide, by decide⟩
theorem unanimity_is_rigidity : rigidityPole unanimity 6 = true := by decide

/-- a window below the floor is outside the corridor however the fractions sit -/
def tooFast : Policy := ⟨2, 3, 1, 3, 1, 3, 60, false, by decide, by decide, by decide⟩
theorem too_fast_outside : inCorridor tooFast 6 86400 = false := by decide

/-- the steward's case: a sound forward policy with NO floor on the reverse path (floor 0) lets one
    voice admit to a community of 10,000 by silence — it is the chaos pole however the enact and
    cancel fractions sit, at every size -/
def noFloor : Policy := ⟨2, 3, 1, 3, 0, 1, 259200, false, by decide, by decide, by decide⟩
theorem no_floor_is_chaos_at_6 : chaosPole noFloor 6 = true := by decide
theorem no_floor_is_chaos_at_10000 : chaosPole noFloor 10000 = true := by decide
theorem no_floor_outside : inCorridor noFloor 10000 86400 = false := by decide
/-- and in general: for any policy with a zero floor and any base, the pole is reached -/
theorem zero_floor_is_chaos (p : Policy) (base : Nat) (h : p.floorNum = 0) : chaosPole p base = true := by
  have hf : floorVotes p base = 0 := by
    unfold floorVotes; rw [h, Nat.zero_mul, Nat.zero_add]
    exact Nat.div_eq_of_lt (Nat.sub_lt p.floorDenPos Nat.one_pos)
  unfold chaosPole; rw [hf]; simp
/-- the floor is a count of at least two voices wherever the corridor holds -/
theorem corridor_floor_at_least_two (p : Policy) (base w : Nat) (h : inCorridor p base w = true) :
    2 ≤ floorVotes p base := by
  unfold inCorridor chaosPole at h
  simp at h
  omega

/- ---- the standing-versus-live question: participation falls with size ---- -/

/-- an expected-active model: active(N) = N for N ≤ k, then a slow linear tail (one in thirty
    beyond k). A stand-in for the measured participation law, whose direction is Olson's and
    whose exponent is a measurement, not a constant of this file. -/
def expectedActive (k N : Nat) : Nat := if N ≤ k then N else k + (N - k) / 30

theorem small_groups_all_active : expectedActive 12 10 = 10 := rfl
theorem large_group_mostly_quiet : expectedActive 12 10000 = 344 := rfl

/-- a cancel fraction taken over the STANDING roster becomes unreachable once the expected
    active fall below it: at N = 10,000 with 1/3 over standing, 3,334 objections are needed and
    about 344 members are active — the reverse path is dead, which is the rigidity pole arrived
    at by size -/
theorem standing_fraction_dies_with_size :
    cancelVotes ruled 10000 = 3334 ∧ expectedActive 12 10000 < cancelVotes ruled 10000 := ⟨rfl, by decide⟩

/-- the same fraction over the EXPECTED-ACTIVE base stays reachable: 115 of ~344 -/
theorem active_base_stays_reachable :
    cancelVotes ruled (expectedActive 12 10000) = 115 ∧ cancelVotes ruled (expectedActive 12 10000) ≤ expectedActive 12 10000 := ⟨rfl, by decide⟩

/-- and at N = 10 the two bases coincide, so a small community pays the full fraction:
    4 of 10 to cancel, 7 of 10 to enact -/
theorem small_community_pays_full :
    cancelVotes ruled 10 = 4 ∧ enactVotes ruled 10 = 7 := ⟨rfl, rfl⟩

/-- a base floor keeps the active base from collapsing a tiny roster into one voice: the base is
    never below the standing roster when the roster is small, and never below the floor -/
def effectiveBase (k floor N : Nat) : Nat := max floor (expectedActive k N)
theorem floor_holds : effectiveBase 12 3 2 = 3 ∧ effectiveBase 12 3 10 = 10 := ⟨rfl, rfl⟩

/-- the approval floor scaled with the community: over the expected-active base of a 10,000
    community the ruled floor of one third is 115 approvals, reachable; over the standing roster it
    would be 3,334, dead (the same arithmetic as the cancel path); at 10 it is 4 of 10 -/
theorem floor_scales_with_size :
    floorVotes ruled (expectedActive 12 10000) = 115 ∧ floorVotes ruled 10000 = 3334 ∧ floorVotes ruled 10 = 4 :=
  ⟨rfl, rfl, rfl⟩
/-- the count minimum: a community's floor and cancel never resolve to fewer than two voices, so the
    ruled third, which is one voice at three members, is lifted to two there (the self roster keeps
    one, every key being the same person's) -/
def minCount (community : Bool) : Nat := if community then 2 else 1
def floorVotesMin (p : Policy) (base : Nat) (community : Bool) : Nat := max (minCount community) (floorVotes p base)
def cancelVotesMin (p : Policy) (base : Nat) (community : Bool) : Nat := max (minCount community) (cancelVotes p base)
theorem ruled_at_three_is_one_voice : floorVotes ruled 3 = 1 := rfl
theorem ruled_at_three_lifted_to_two : floorVotesMin ruled 3 true = 2 ∧ cancelVotesMin ruled 3 true = 2 := ⟨rfl, rfl⟩
theorem self_keeps_one : floorVotesMin selfRoster 3 false = 1 := rfl
theorem lifted_floor_never_one (p : Policy) (base : Nat) : 2 ≤ floorVotesMin p base true := by
  unfold floorVotesMin minCount; simp; omega

/-- a community may tighten: a floor at enact switches the reverse path off (every landing is
    forward), and it is still inside the corridor — strictness is allowed, laxity is not -/
def strict : Policy := ⟨2, 3, 1, 3, 2, 3, 259200, false, by decide, by decide, by decide⟩
theorem strict_in_corridor : inCorridor strict 344 86400 = true := by decide
theorem strict_floor_is_enact : floorVotes strict 344 = enactVotes strict 344 - 1 + 1 := rfl
/-- and may not loosen below two voices: a floor of one in a 344-active community is outside -/
def lax : Policy := ⟨2, 3, 1, 3, 1, 344, 259200, false, by decide, by decide, by decide⟩
theorem lax_outside : inCorridor lax 344 86400 = false := by decide

end TwoPathCorridor
