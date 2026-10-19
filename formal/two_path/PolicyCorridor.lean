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

/-- a policy: enact and cancel as fractions, window in seconds, irreversible -/
structure Policy where
  enactNum : Nat
  enactDen : Nat
  cancelNum : Nat
  cancelDen : Nat
  windowSecs : Nat
  irreversible : Bool
  enactDenPos : 0 < enactDen
  cancelDenPos : 0 < cancelDen

/-- the base the fractions are taken over: the standing roster N, or an expected-active count -/
def enactVotes (p : Policy) (base : Nat) : Nat := p.enactNum * base / p.enactDen + 1   -- strict: more than the fraction
def cancelVotes (p : Policy) (base : Nat) : Nat := (p.cancelNum * base + p.cancelDen - 1) / p.cancelDen  -- at least the fraction

/- ---- the two poles, stated as what breaks ---- -/

/-- rigidity: the cancel threshold is reachable by one voter, or enact needs everyone — then a
    single coerced key blocks every change (liveness dies) -/
def rigidityPole (p : Policy) (base : Nat) : Bool :=
  decide (cancelVotes p base ≤ 1) || decide (enactVotes p base ≥ base)

/-- chaos: enact is reachable by one voter, or cancel needs everyone — then one key enacts a
    takedown and nothing can stop it (safety dies) -/
def chaosPole (p : Policy) (base : Nat) : Bool :=
  decide (enactVotes p base ≤ 1) || decide (cancelVotes p base ≥ base)

/-- the corridor: neither pole, cancel ≤ enact, an enact floor of a strict majority, a window
    floor by sensitivity (the constitution's constants: 24 h for the halt fuse, 72 h for W) -/
def inCorridor (p : Policy) (base windowFloor : Nat) : Bool :=
  !rigidityPole p base && !chaosPole p base
  && decide (p.cancelNum * p.enactDen ≤ p.enactNum * p.cancelDen)       -- cancel ≤ enact
  && decide (2 * p.enactNum ≥ p.enactDen)                               -- enact ≥ 1/2 (strict in use)
  && decide (windowFloor ≤ p.windowSecs)

/-- the steward's example: enact 2/3, cancel 1/3, 72 h — in the corridor at N = 6 -/
def ruled : Policy := ⟨2, 3, 1, 3, 259200, false, by decide, by decide⟩
theorem ruled_in_corridor : inCorridor ruled 6 86400 = true := by decide
theorem ruled_in_corridor_at_7 : inCorridor ruled 7 86400 = true := by decide

/-- the self roster: strict majority both ways at N = 3 -/
def selfRoster : Policy := ⟨1, 2, 1, 2, 86400, false, by decide, by decide⟩
theorem self_roster_in_corridor : inCorridor selfRoster 3 86400 = true := by decide

/-- the poles, each excluded -/
def libertumVeto : Policy := ⟨2, 3, 1, 6, 259200, false, by decide, by decide⟩   -- one of six cancels
theorem one_voice_cancels_is_rigidity : rigidityPole libertumVeto 6 = true := by decide
theorem rigidity_outside : inCorridor libertumVeto 6 86400 = false := by decide

def oneEnacts : Policy := ⟨1, 7, 1, 3, 259200, false, by decide, by decide⟩       -- enact below 1/N: one of six enacts a takedown
theorem one_voice_enacts_is_chaos : chaosPole oneEnacts 6 = true := by decide
theorem chaos_outside : inCorridor oneEnacts 6 86400 = false := by decide

def unanimity : Policy := ⟨1, 1, 1, 3, 259200, false, by decide, by decide⟩
theorem unanimity_is_rigidity : rigidityPole unanimity 6 = true := by decide

/-- a window below the floor is outside the corridor however the fractions sit -/
def tooFast : Policy := ⟨2, 3, 1, 3, 60, false, by decide, by decide⟩
theorem too_fast_outside : inCorridor tooFast 6 86400 = false := by decide

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

/-- a floor keeps the active base from collapsing a tiny roster into one voice: the base is
    never below the standing roster when the roster is small, and never below the floor -/
def effectiveBase (k floor N : Nat) : Nat := max floor (expectedActive k N)
theorem floor_holds : effectiveBase 12 3 2 = 3 ∧ effectiveBase 12 3 10 = 10 := ⟨rfl, rfl⟩

end TwoPathCorridor
