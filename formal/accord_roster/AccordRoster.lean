/-
  AccordRoster.lean — which roster-change rule the HUMANITY_ACCORD needs once the
  regional-steward backstop of CC 4.2.6 is removed.

  Scope (stated): a counting model of ONE roster decision. Holders are partitioned by
  what an adversary has done to them before the participation window W closes:

    h — honest, reachable: shows up in W and votes against an adversarial change
    s — honest, censored for all of W (may resurface later)
    d — lost: dead, incapacitated, or key material gone
    c — coerced (or a manufactured insider already seated): shows up and votes as told

  Hybrid signatures are assumed unforgeable (keys in FIPS hardware); an adversary that
  can forge them defeats every rule here equally, a second roster included. Firing the
  kill switch is floor-1 over the live set (CC 4.2.6) and is NOT gated by any rule
  modelled here; what a roster rule decides is whether an honest holder can be
  removed (losing fire authority once the removal takes effect) and whether lost
  holders can be replaced.

  Three candidate rules for a roster change (add, remove or swap):
    live     — strict majority of the live set L          (CC 4.2.6 as written, minus the backstop)
    present  — strict majority of L, and L a strict majority of the standing roster
               (the backstop's second trigger, without a backstop body: refused instead)
    standing — yes-votes a strict majority of the standing roster N

  No `sorry`, no axioms beyond core; every theorem is closed by `simp`/`omega`.
-/

structure Cfg where
  h : Nat
  s : Nat
  d : Nat
  c : Nat
deriving Repr, DecidableEq

namespace Cfg
def N (x : Cfg) : Nat := x.h + x.s + x.d + x.c
end Cfg

inductive Rule | live | present | standing
deriving Repr, DecidableEq

/-- Does a change with `yes` votes, live set size `L`, standing roster `N` pass? -/
def passes : Rule → Nat → Nat → Nat → Prop
  | .live,     yes, L, _ => 2 * yes > L
  | .present,  yes, L, N => 2 * yes > L ∧ 2 * L > N
  | .standing, yes, _, N => 2 * yes > N

instance (r : Rule) (y L N : Nat) : Decidable (passes r y L N) := by
  cases r <;> unfold passes <;> infer_instance

/-- The adversary removes an honest holder (or, identically, seats a puppet):
    the coerced vote yes, reachable honest holders vote no, the censored and lost are absent. -/
def seizes (r : Rule) (x : Cfg) : Prop :=
  passes r x.c (x.h + x.c) x.N ∧ x.h + x.s ≥ 1

/-- Honest holders replace a lost holder; the coerced (if any) vote no. -/
def heals (r : Rule) (x : Cfg) : Prop :=
  passes r x.h (x.h + x.c) x.N

/-! ## 1. Option 3 as literally "drop the backstop": one coerced holder seizes any roster -/

/-- Under the live rule, one coerced holder plus censorship of every honest holder
    removes an honest holder — for a roster of ANY size. This is the case the
    backstop existed for. -/
theorem live_one_coerced_seizes (s d : Nat) (hs : s ≥ 1) :
    seizes .live ⟨0, s, d, 1⟩ := by
  simp [seizes, passes, Cfg.N]; omega

/-- ...and seating a puppet is the same vote, so the adversary can then pack the
    standing roster without limit: the live rule makes the accord's size irrelevant. -/
theorem live_seizure_independent_of_size (n : Nat) :
    seizes .live ⟨0, n + 1, 0, 1⟩ := live_one_coerced_seizes (n + 1) 0 (by omega)

/-! ## 2. The "present majority" rule is weaker than it looks -/

/-- With 10 holders, 4 coerced seize under `present` by letting 2 honest holders
    through and censoring the other 4: L = 6 > 5, and 4 yes > 3. -/
theorem present_quarter_seizes : seizes .present ⟨2, 4, 0, 4⟩ := by
  simp [seizes, passes, Cfg.N]

/-- Under `present`, the adversary needs only c > h and h + c > N/2, so roughly a
    quarter of the roster: c > (N+1)/4 suffices when it controls who gets through. -/
theorem present_needs_only_quarter (x : Cfg) (hc : x.c ≥ x.h + 1) (hL : 2 * (x.h + x.c) > x.N)
    (hon : x.h + x.s ≥ 1) : seizes .present x := by
  simp [seizes, passes]; omega

/-! ## 3. The standing rule: seizure needs a coerced strict majority of the whole roster -/

theorem standing_seize_iff (x : Cfg) :
    seizes .standing x ↔ (2 * x.c > x.N ∧ x.h + x.s ≥ 1) := by
  simp [seizes, passes]

/-- Censorship buys the adversary nothing under `standing`: the bound is on yes-votes
    against the whole roster, so who is reachable does not enter it. -/
theorem standing_censorship_irrelevant (x : Cfg) (k : Nat) (hk : k ≤ x.h) :
    seizes .standing x ↔ seizes .standing ⟨x.h - k, x.s + k, x.d, x.c⟩ := by
  simp [seizes, passes, Cfg.N]; omega

/-- Minimum coercion to seize an accord of X holders under `standing`: ⌊X/2⌋ + 1. -/
theorem standing_min_coercion (X c : Nat) :
    (∃ x : Cfg, x.N = X ∧ x.c = c ∧ seizes .standing x) ↔ (2 * c > X ∧ c < X) := by
  constructor
  · rintro ⟨x, hN, hc, hseize, hon⟩
    subst hc; constructor <;> simp [passes, Cfg.N] at * <;> omega
  · rintro ⟨h1, h2⟩
    exact ⟨⟨0, X - c, 0, c⟩, by simp [Cfg.N]; omega, rfl,
      by simp [seizes, passes, Cfg.N]; omega, by simp; omega⟩

/-- Ordering of strength: anything that seizes under `standing` seizes under the other
    two, and nothing about `present` or `live` is needed to resist a minority. -/
theorem standing_strongest (x : Cfg) (hx : seizes .standing x) :
    seizes .present x ∨ x.h > x.c := by
  simp [seizes, passes, Cfg.N] at *; omega

/-! ## 4. What `standing` costs: healing needs a reachable honest majority -/

theorem standing_heal_iff (x : Cfg) : heals .standing x ↔ 2 * x.h > x.N := by
  simp [heals, passes]

theorem live_heal_iff (x : Cfg) : heals .live x ↔ x.h > x.c := by
  simp [heals, passes]; omega

/-- After a first strike that leaves fewer than half the holders reachable and honest,
    the roster is frozen under `standing` ... -/
theorem standing_frozen_after_decimation (x : Cfg) (hx : 2 * x.h ≤ x.N) : ¬ heals .standing x := by
  simp [heals, passes]; omega

/-- ... but firing is untouched: no honest holder can be removed without a coerced
    majority, so every honest survivor keeps the floor-1 kill. -/
theorem standing_survivors_keep_fire (x : Cfg) (hc : 2 * x.c ≤ x.N) : ¬ seizes .standing x := by
  simp [seizes, passes]; omega

/-! ## 5. Scenarios -/

/-- ASI first strike with no human coercion (kill and censor only, c = 0): no rule
    removes anyone, so the halt is blocked only if EVERY honest holder is lost or
    censored forever. The roster rule is irrelevant; a second roster adds nothing. -/
theorem first_strike_no_coercion (r : Rule) (x : Cfg) (hc : x.c = 0) : ¬ seizes r x := by
  cases r <;> simp [seizes, passes, hc]

/-- Institutional capture of a minority (legal compulsion of fewer than half):
    `standing` resists at every roster size; `live` falls to one coerced holder. -/
theorem minority_capture_resisted (x : Cfg) (hc : 2 * x.c ≤ x.N) : ¬ seizes .standing x :=
  standing_survivors_keep_fire x hc

/-- Majority capture (more than half coerced): every rule falls, and so would a
    restore-only second roster's guarantee if the same adversary can coerce it.
    What remains is not a rule but the node's own un-trust lever (CC 3.2 T3). -/
theorem majority_capture_unstoppable (r : Rule) (x : Cfg) (hc : 2 * x.c > x.N)
    (hon : x.h + x.s ≥ 1) (hh : x.h = 0) : seizes r x := by
  cases r <;> simp [seizes, passes, Cfg.N, hh] at * <;> omega

/-- Option 2 (pre-committed recovery keys held by the same humans) converts a holder
    lost to KEY loss back into a reachable honest holder. It strictly helps healing
    and never helps an adversary, because it adds no new person to coerce. -/
theorem recovery_keys_help_heal (x : Cfg) (k : Nat) (hk : k ≤ x.d) (hheal : heals .standing x) :
    heals .standing ⟨x.h + k, x.s, x.d - k, x.c⟩ := by
  simp [heals, passes, Cfg.N] at *; omega

theorem recovery_keys_never_help_seizure (x : Cfg) (k : Nat) (hk : k ≤ x.d)
    (hon : x.h + x.s ≥ 1) (hn : ¬ seizes .standing x) : ¬ seizes .standing ⟨x.h + k, x.s, x.d - k, x.c⟩ := by
  simp [seizes, passes, Cfg.N] at *; omega

/-- Growing the accord raises the coercion bar linearly: X = 21 needs 11 coerced. -/
example : (∃ x : Cfg, x.N = 21 ∧ x.c = 10 ∧ seizes .standing x) = False := by
  apply propext; constructor
  · intro h; have := (standing_min_coercion 21 10).mp h; omega
  · intro h; exact h.elim
