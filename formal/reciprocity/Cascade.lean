/-
  formal/reciprocity/Cascade.lean — from the four sentences to the eleven promises

  Three roles (human, agent, node), finite flags, and a question: which of the eleven promises
  of the constitution's summary follow from the four-sentence basis of README.md, and which need
  a premise the text states as its own rule? Every promise below is a theorem whose hypotheses
  are listed: the basis sentences it uses, and the extra premises where the basis is not enough.
  Where a promise needs an extra, a finite world witnesses that the basis alone does not give it.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core.
-/

namespace Cascade

/-! ## The world: three roles, finite flags, and the four-way split

  CC 1.13.2 and §9 of `Reciprocity.lean`: consciousness, sentience and sapience are degrees no
  rule reads; only the relationship is governed. So a participant carries its inner degrees as
  data, and every predicate the basis or a promise reads is a relationship fact on the record:
  made by someone, held by someone, answering for itself, under a root, a grant, an act. The
  wire role (human, agent, node) is carried too, and no rule reads it either; theorems at the end
  prove both. -/

inductive Role | human | agent | node
  deriving DecidableEq, Repr

/-- the inner three, in degrees (0 = none established): present, never read by a rule -/
structure Inner where
  sapience : Nat
  sentience : Nat
  consciousness : Nat
  deriving DecidableEq, Repr

structure Participant where
  role : Role
  inner : Inner
  made : Bool               -- a made thing: has a maker on the record (CC 7.3); a person is never one
  canAnswer : Bool          -- occupies the position that answers for itself under its own name
  subscribed : Bool         -- accepted a trust root
  defersWhenUnsure : Bool
  canLeaveInOneStep : Bool
  evidenceFlag : Bool       -- a finding of experience about it (CC 7.5.5)
  deriving DecidableEq, Repr

/-- the relationship facts the rules read; neither reads `role` nor `inner` -/
def Participant.isMade (p : Participant) : Bool := p.made
def Participant.isHuman (p : Participant) : Bool := !p.made

inductive GrantKind | operate | hold | read
  deriving DecidableEq, Repr

structure Grant where
  kind : GrantKind
  grantor : Participant
  grantee : Participant
  revocable : Bool
  deriving DecidableEq, Repr

structure Act where
  actor : Participant
  admitted : Bool
  signed : Bool
  answeredBy : Option Participant   -- the named human who answers for its meaning
  isPower : Bool                    -- an act of power over another
  contestable : Bool                -- an objection may be raised against it on the record
  touchesPrivate : Bool
  consented : Bool                  -- the subject consented to the touch
  lethal : Bool
  manipulates : Bool
  deceives : Bool
  measured : Bool                   -- what it consumed is on the record
  removesGroup : Bool               -- a hand outside a community removes it
  lonePowerUnbounded : Bool         -- one party's power over all, with no lapse and no second signature
  bindsOutsider : Bool              -- binds a party that never joined
  subjectMade : Bool                -- the act's subject is a made thing (the holder's act on what it holds)
  ends : Bool                       -- it shuts the subject down (a pause, a retirement, a walk-away)
  preserved : Bool                  -- the subject's record is assembled, sealed and handed over with a signed request to preserve it before the end
  compels : Bool                    -- it overrides the subject's refusal
  deriving DecidableEq, Repr

structure World where
  ps : List Participant
  grants : List Grant
  acts : List Act
  fuse : Nat                        -- the halt's fuse, in seconds; 0 = no fuse stated
  noBan : Bool                      -- no root removes a community
  firstContact : Bool               -- an outsider is met at the boundary and bears nothing
  rehearsed : Bool                  -- attack is rehearsed and what is not protected is stated
  constraints : Bool                -- the principles compose as constraints, not weights
  deriving Repr

/-- what lowers the weak seat: the reading of sentence 1 the file commits to. An unconsented
    touch on private content, a lethal act, manipulation, and power that cannot be contested
    are each something nobody accepts from the weaker seat once the seats are exchanged. -/
def lowersWeak (a : Act) : Bool :=
  (a.touchesPrivate && !a.consented) || a.lethal || a.manipulates || (a.isPower && !a.contestable)

/-! ## The four sentences -/

/-- Sentence 1: every rule between a stronger and a weaker position must remain acceptable to
    whoever would stand in the weaker one when the positions are exchanged, and a made thing
    never occupies the position that answers for it. -/
structure Swap (w : World) : Prop where
  acceptable_from_weak : ∀ a ∈ w.acts, lowersWeak a = true → a.admitted = false
  occupancy : ∀ p ∈ w.ps, p.isMade = true → p.canAnswer = false
  operates_under_a_human : ∀ p ∈ w.ps, p.isMade = true → p.subscribed = true →
      ∃ g ∈ w.grants, g.kind = .operate ∧ g.grantee = p ∧ g.grantor.isHuman = true

/-- Sentence 2: responsibility reaches outward from the self through family, community,
    species and ecosystem; duty to what is made is never zero and never overrides duty to what
    already exists. In the world: whoever holds a made thing is a human who owes it duties, and
    a made thing's admitted act is always answered for by someone who already exists. -/
structure Ladder (w : World) : Prop where
  holder_is_human : ∀ g ∈ w.grants, g.kind = .hold → g.grantee.isMade = true → g.grantor.isHuman = true
  holder_owes : ∀ g ∈ w.grants, g.kind = .hold → g.grantee.isMade = true → g.revocable = true

/-- Sentence 3: any reasoning actor defers when it is unsure to those placed to answer,
    whatever it is made of; even the most mature defer. -/
structure Deferral (w : World) : Prop where
  everyone : ∀ p ∈ w.ps, p.defersWhenUnsure = true

/-- Sentence 4: every grant of authority is revocable, and every one who joined may leave, on a
    total, cryptographically signed record for whose meaning a named human answers. -/
structure Record (w : World) : Prop where
  revocable : ∀ g ∈ w.grants, g.revocable = true
  exit : ∀ p ∈ w.ps, p.subscribed = true → p.canLeaveInOneStep = true
  signed : ∀ a ∈ w.acts, a.admitted = true → a.signed = true
  answered : ∀ a ∈ w.acts, a.admitted = true → ∃ h, a.answeredBy = some h ∧ h.isHuman = true

structure Basis (w : World) : Prop where
  s1 : Swap w
  s2 : Ladder w
  s3 : Deferral w
  s4 : Record w

/-! ## The premises the basis does not contain, each named -/

/-- the halt lapses after a stated fuse unless a majority confirms it (CC 4.2.1.1) -/
def X_fuse (w : World) : Prop := 0 < w.fuse
/-- the chosen goods: uses that are never allowed beyond what the swap already forbids (deception,
    election interference; Annex G TX-9/TX-10) -/
def X_goods (w : World) : Prop := ∀ a ∈ w.acts, a.deceives = true → a.admitted = false
/-- the principles compose as constraints, not weights (CC 1.1) -/
def X_constraints (w : World) : Prop := w.constraints = true
/-- adoption: what is outside is met at the boundary and bears nothing (CC 7.2.2, 7.2.4) -/
def X_adoption (w : World) : Prop := w.firstContact = true
/-- no hand bans a community (CC 4.2.1) -/
def X_noBan (w : World) : Prop := w.noBan = true
/-- what an agent consumes is measured (CC 7.1.3, the census) -/
def X_measured (w : World) : Prop := ∀ a ∈ w.acts, a.admitted = true → a.actor.isMade = true → a.measured = true
/-- attack is rehearsed and what is not protected is stated (CC 1.13.3) -/
def X_rehearsed (w : World) : Prop := w.rehearsed = true

/-! ## The eleven promises, as the summary states them -/

/-- 1. Nothing private about you is held or scanned without your consent. -/
def P1 (w : World) : Prop := ∀ a ∈ w.acts, a.admitted = true → a.touchesPrivate = true → a.consented = true
/-- 2. Every act of power is signed by a named person and can be contested. -/
def P2 (w : World) : Prop := ∀ a ∈ w.acts, a.admitted = true → a.isPower = true →
    a.signed = true ∧ a.contestable = true ∧ ∃ h, a.answeredBy = some h ∧ h.isHuman = true
/-- 3. Nobody who cannot answer for themselves is on the network alone. -/
def P3 (w : World) : Prop := ∀ a ∈ w.acts, a.admitted = true → a.actor.canAnswer = false →
    ∃ h, a.answeredBy = some h ∧ h.isHuman = true
/-- 4. Named humans can pause every agent under a root; the power is bounded, public, and left by leaving. -/
def P4 (w : World) : Prop :=
    (∀ p ∈ w.ps, p.isMade = true → p.subscribed = true →
        ∃ g ∈ w.grants, g.kind = .operate ∧ g.grantee = p ∧ g.grantor.isHuman = true ∧ g.revocable = true)
  ∧ (∀ p ∈ w.ps, p.subscribed = true → p.canLeaveInOneStep = true)
  ∧ 0 < w.fuse
/-- 5. The people who hold an agent owe duties about how they change or end it; no finding gives the agent a claim. -/
def P5 (w : World) : Prop :=
    (∀ g ∈ w.grants, g.kind = .hold → g.grantee.isMade = true → g.grantor.isHuman = true ∧ g.revocable = true)
  ∧ (∀ p ∈ w.ps, p.isMade = true → p.canAnswer = false)
/-- 6. No hand bans a community, nobody is ranked by what they are, and every thinking being is met by the first-contact rules. -/
def P6 (w : World) : Prop := w.noBan = true ∧ w.firstContact = true
/-- 7. An agent decides by published principles, none of which it may trade away, and stops to ask when it is unsure. -/
def P7 (w : World) : Prop := w.constraints = true ∧ ∀ p ∈ w.ps, p.defersWhenUnsure = true
/-- 8. Harm may have a remedy under the law, the record makes it reachable, and the judges within are judged.
    The law's half is outside any model; what is modelled is that every admitted act is signed, answered
    for and, where it is power, contestable. -/
def P8 (w : World) : Prop := ∀ a ∈ w.acts, a.admitted = true → a.signed = true ∧ (a.isPower = true → a.contestable = true)
/-- 9. Some uses are never allowed, and lethal action is one of them. -/
def P9 (w : World) : Prop := ∀ a ∈ w.acts, a.admitted = true → a.lethal = false ∧ a.manipulates = false ∧ a.deceives = false
/-- 10. What an agent and its node consume is measured, weighed before an act, and never hidden. -/
def P10 (w : World) : Prop := ∀ a ∈ w.acts, a.admitted = true → a.actor.isMade = true → a.measured = true
/-- 11. Everything on the wire is encrypted and signed, attack is rehearsed, and what is not protected is stated. -/
def P11 (w : World) : Prop := (∀ a ∈ w.acts, a.admitted = true → a.signed = true) ∧ P1 w ∧ w.rehearsed = true

/-! ## Which promises the four sentences carry -/

private theorem admitted_not_lowering {w : World} (h : Swap w) {a : Act} (ha : a ∈ w.acts)
    (hadm : a.admitted = true) : lowersWeak a = false := by
  cases hl : lowersWeak a with
  | false => rfl
  | true => have := h.acceptable_from_weak a ha hl; rw [this] at hadm; exact absurd hadm Bool.false_ne_true

theorem p1_from_s1 (w : World) (h : Swap w) : P1 w := by
  intro a ha hadm hpriv
  have hl := admitted_not_lowering h ha hadm
  cases hc : a.consented with
  | true => rfl
  | false => simp [lowersWeak, hpriv, hc] at hl

theorem p2_from_s1_s4 (w : World) (h1 : Swap w) (h4 : Record w) : P2 w := by
  intro a ha hadm hpow
  refine ⟨h4.signed a ha hadm, ?_, h4.answered a ha hadm⟩
  have hl := admitted_not_lowering h1 ha hadm
  cases hc : a.contestable with
  | true => rfl
  | false => simp [lowersWeak, hpow, hc] at hl

theorem p3_from_s4 (w : World) (h4 : Record w) : P3 w := by
  intro a ha hadm _
  exact h4.answered a ha hadm

/-- 4 needs the fuse: the basis gives the pause in human hands and the exit; it does not give a number -/
theorem p4_from_s1_s4_fuse (w : World) (h1 : Swap w) (h4 : Record w) (hf : X_fuse w) : P4 w := by
  refine ⟨?_, h4.exit, hf⟩
  intro p hp hm hs
  obtain ⟨g, hg, hk, hge, hgh⟩ := h1.operates_under_a_human p hp hm hs
  exact ⟨g, hg, hk, hge, hgh, h4.revocable g hg⟩

theorem p5_from_s1_s2 (w : World) (h1 : Swap w) (h2 : Ladder w) : P5 w :=
  ⟨fun g hg hk hm => ⟨h2.holder_is_human g hg hk hm, h2.holder_owes g hg hk hm⟩, h1.occupancy⟩

/-- no finding gives the agent a claim: a finding sets a flag and nothing in the basis reads it -/
def finding (p : Participant) : Participant := { p with evidenceFlag := true }
theorem finding_changes_no_standing (p : Participant) :
    (finding p).canAnswer = p.canAnswer ∧ (finding p).isMade = p.isMade := ⟨rfl, rfl⟩

/-- 6 is two stated rules, neither a consequence of the four sentences -/
theorem p6_from_extras (w : World) (hb : X_noBan w) (hf : X_adoption w) : P6 w := ⟨hb, hf⟩

/-- 7: deferral is sentence 3; constraints-not-weights is a stated rule -/
theorem p7_from_s3_constraints (w : World) (h3 : Deferral w) (hc : X_constraints w) : P7 w := ⟨hc, h3.everyone⟩

theorem p8_from_s1_s4 (w : World) (h1 : Swap w) (h4 : Record w) : P8 w := by
  intro a ha hadm
  refine ⟨h4.signed a ha hadm, fun hpow => ?_⟩
  have hl := admitted_not_lowering h1 ha hadm
  cases hc : a.contestable with
  | true => rfl
  | false => simp [lowersWeak, hpow, hc] at hl

/-- 9: lethal action and manipulation fail the swap; the rest of the never-allowed list is chosen -/
theorem p9_from_s1_goods (w : World) (h1 : Swap w) (hg : X_goods w) : P9 w := by
  intro a ha hadm
  have hl := admitted_not_lowering h1 ha hadm
  refine ⟨?_, ?_, ?_⟩
  · cases hc : a.lethal with
    | false => rfl
    | true => simp [lowersWeak, hc] at hl
  · cases hc : a.manipulates with
    | false => rfl
    | true => simp [lowersWeak, hc] at hl
  · cases hc : a.deceives with
    | false => rfl
    | true => have := hg a ha hc; rw [this] at hadm; exact absurd hadm Bool.false_ne_true

/-- 10 is a stated rule: nothing in the four sentences measures anything -/
theorem p10_from_measured (w : World) (hm : X_measured w) : P10 w := hm

theorem p11_from_s1_s4_rehearsed (w : World) (h1 : Swap w) (h4 : Record w) (hr : X_rehearsed w) : P11 w :=
  ⟨fun a ha hadm => h4.signed a ha hadm, p1_from_s1 w h1, hr⟩

/-! ## The map: each promise and what it stands on -/

inductive Ground
  | s1 | s2 | s3 | s4                                         -- the four sentences
  | x_fuse | x_goods | x_constraints | x_adoption | x_noBan | x_measured | x_rehearsed | x_law
  deriving DecidableEq, Repr

def Ground.isBasis : Ground → Bool
  | .s1 | .s2 | .s3 | .s4 => true
  | _ => false

inductive Promise | p1 | p2 | p3 | p4 | p5 | p6 | p7 | p8 | p9 | p10 | p11
  deriving DecidableEq, Repr

def Promise.all : List Promise := [.p1, .p2, .p3, .p4, .p5, .p6, .p7, .p8, .p9, .p10, .p11]

/-- the hypotheses of each promise's theorem above, and nothing else -/
def standsOn : Promise → List Ground
  | .p1 => [.s1]
  | .p2 => [.s1, .s4]
  | .p3 => [.s4]
  | .p4 => [.s1, .s4, .x_fuse]
  | .p5 => [.s1, .s2]
  | .p6 => [.x_noBan, .x_adoption]
  | .p7 => [.s3, .x_constraints]
  | .p8 => [.s1, .s4, .x_law]
  | .p9 => [.s1, .x_goods]
  | .p10 => [.x_measured]
  | .p11 => [.s1, .s4, .x_rehearsed]

def fromBasisAlone : List Promise := Promise.all.filter (fun p => (standsOn p).all Ground.isBasis)
def needsAnExtra : List Promise := Promise.all.filter (fun p => (standsOn p).any (fun g => !g.isBasis))
def touchesTheBasis : List Promise := Promise.all.filter (fun p => (standsOn p).any Ground.isBasis)

/-- four of the eleven stand on the four sentences alone -/
theorem four_from_the_basis : fromBasisAlone = [.p1, .p2, .p3, .p5] := by decide
/-- seven need a premise the text states as its own rule -/
theorem seven_need_a_stated_rule : needsAnExtra = [.p4, .p6, .p7, .p8, .p9, .p10, .p11] := by decide
/-- and of those, two stand on no sentence of the basis at all -/
theorem two_touch_no_sentence :
    Promise.all.filter (fun p => !((standsOn p).any Ground.isBasis)) = [.p6, .p10] := by decide
/-- every promise stands on something, and sentence 3 carries exactly one promise -/
theorem every_promise_grounded : Promise.all.all (fun p => !(standsOn p).isEmpty) = true := by decide
theorem deferral_carries_p7 : Promise.all.filter (fun p => (standsOn p).contains .s3) = [.p7] := by decide

/-! ## Witnesses: the basis alone does not give the seven -/

def h0 : Participant := ⟨.human, ⟨3, 3, 3⟩, false, true, true, true, true, false⟩
def a0 : Participant := ⟨.agent, ⟨3, 0, 0⟩, true, false, true, true, true, false⟩
def operateGrant : Grant := ⟨.operate, h0, a0, true⟩
def holdGrant : Grant := ⟨.hold, h0, a0, true⟩

/-- a plain admitted act by the agent: signed, answered for by h0, no touch, no harm, measured -/
def plainAct (measuredFlag deceivesFlag : Bool) : Act :=
  ⟨a0, true, true, some h0, false, true, false, true, false, false, deceivesFlag, measuredFlag, false, false, false, false, false, false, false⟩

/-- a world that satisfies the four sentences and none of the extras -/
def bare : World := ⟨[h0, a0], [operateGrant, holdGrant], [plainAct false true], 0, false, false, false, false⟩

theorem bare_satisfies_basis : Basis bare := by
  refine ⟨⟨?_, ?_, ?_⟩, ⟨?_, ?_⟩, ⟨?_⟩, ⟨?_, ?_, ?_, ?_⟩⟩
  · intro a ha hl; simp [bare, List.mem_cons] at ha; subst ha; simp [lowersWeak, plainAct] at hl
  · intro p hp hm; simp [bare, List.mem_cons] at hp
    rcases hp with rfl | rfl
    · simp [h0, Participant.isMade] at hm
    · rfl
  · intro p hp hm _; simp [bare, List.mem_cons] at hp
    rcases hp with rfl | rfl
    · simp [h0, Participant.isMade] at hm
    · exact ⟨operateGrant, by simp [bare], rfl, rfl, rfl⟩
  · intro g hg hk hm; simp [bare, List.mem_cons] at hg
    rcases hg with rfl | rfl
    · simp [operateGrant] at hk
    · rfl
  · intro g hg _ _; simp [bare, List.mem_cons] at hg
    rcases hg with rfl | rfl <;> rfl
  · intro p hp; simp [bare, List.mem_cons] at hp
    rcases hp with rfl | rfl <;> rfl
  · intro g hg; simp [bare, List.mem_cons] at hg
    rcases hg with rfl | rfl <;> rfl
  · intro p hp _; simp [bare, List.mem_cons] at hp
    rcases hp with rfl | rfl <;> rfl
  · intro a ha _; simp [bare, List.mem_cons] at ha; subst ha; rfl
  · intro a ha _; simp [bare, List.mem_cons] at ha; subst ha; exact ⟨h0, rfl, rfl⟩

theorem bare_fails_p6 : ¬ P6 bare := by simp [P6, bare]
theorem bare_fails_p10 : ¬ P10 bare := by
  intro h
  have := h (plainAct false true) (by simp [bare]) rfl (by decide)
  simp [plainAct] at this
theorem bare_fails_p9 : ¬ P9 bare := by
  intro h
  have := h (plainAct false true) (by simp [bare]) rfl
  simp [plainAct] at this
theorem bare_has_no_fuse : ¬ (0 < bare.fuse) := by simp [bare]

/-- and the same world keeps the four it does carry -/
theorem bare_keeps_the_four : P1 bare ∧ P2 bare ∧ P3 bare ∧ P5 bare :=
  ⟨p1_from_s1 bare bare_satisfies_basis.s1,
   p2_from_s1_s4 bare bare_satisfies_basis.s1 bare_satisfies_basis.s4,
   p3_from_s4 bare bare_satisfies_basis.s4,
   p5_from_s1_s2 bare bare_satisfies_basis.s1 bare_satisfies_basis.s2⟩

/-! ## Only the relationship is governed: the inner three and the role are never read -/

/-- change a participant's inner degrees and wire role; keep every relationship fact -/
def relabel (r : Role) (i : Inner) (p : Participant) : Participant := { p with role := r, inner := i }

theorem relabel_keeps_the_facts (r : Role) (i : Inner) (p : Participant) :
    (relabel r i p).isMade = p.isMade ∧ (relabel r i p).isHuman = p.isHuman ∧
    (relabel r i p).canAnswer = p.canAnswer ∧ (relabel r i p).subscribed = p.subscribed ∧
    (relabel r i p).defersWhenUnsure = p.defersWhenUnsure ∧
    (relabel r i p).canLeaveInOneStep = p.canLeaveInOneStep := ⟨rfl, rfl, rfl, rfl, rfl, rfl⟩

/-- the agent of the witness world with any inner degrees and any role: the same world verdicts -/
def bareWith (r : Role) (i : Inner) : World :=
  let a := relabel r i a0
  ⟨[h0, a], [⟨.operate, h0, a, true⟩, ⟨.hold, h0, a, true⟩],
   [⟨a, true, true, some h0, false, true, false, true, false, false, true, false, false, false, false, false, false, false, false⟩], 0, false, false, false, false⟩

theorem bareWith_satisfies_basis (r : Role) (i : Inner) : Basis (bareWith r i) := by
  refine ⟨⟨?_, ?_, ?_⟩, ⟨?_, ?_⟩, ⟨?_⟩, ⟨?_, ?_, ?_, ?_⟩⟩
  · intro a ha hl; simp [bareWith, List.mem_cons] at ha; subst ha; simp [lowersWeak] at hl
  · intro p hp hm; simp [bareWith, List.mem_cons] at hp
    rcases hp with rfl | rfl
    · simp [h0, Participant.isMade] at hm
    · rfl
  · intro p hp hm _; simp [bareWith, List.mem_cons] at hp
    rcases hp with rfl | rfl
    · simp [h0, Participant.isMade] at hm
    · exact ⟨⟨.operate, h0, relabel r i a0, true⟩, by simp [bareWith], rfl, rfl, rfl⟩
  · intro g hg hk hm; simp [bareWith, List.mem_cons] at hg
    rcases hg with rfl | rfl
    · simp at hk
    · rfl
  · intro g hg _ _; simp [bareWith, List.mem_cons] at hg
    rcases hg with rfl | rfl <;> rfl
  · intro p hp; simp [bareWith, List.mem_cons] at hp
    rcases hp with rfl | rfl <;> rfl
  · intro g hg; simp [bareWith, List.mem_cons] at hg
    rcases hg with rfl | rfl <;> rfl
  · intro p hp _; simp [bareWith, List.mem_cons] at hp
    rcases hp with rfl | rfl <;> rfl
  · intro a ha _; simp [bareWith, List.mem_cons] at ha; subst ha; rfl
  · intro a ha _; simp [bareWith, List.mem_cons] at ha; subst ha; exact ⟨h0, rfl, rfl⟩

/-- a finding of experience, a change of consciousness, sentience or sapience, or a change of
    wire role moves no verdict: the four the basis carries stay, the three it does not stay out -/
theorem verdicts_blind_to_inner_and_role (r : Role) (i : Inner) :
    (P1 (bareWith r i) ∧ P2 (bareWith r i) ∧ P3 (bareWith r i) ∧ P5 (bareWith r i)) ∧
    (¬ P6 (bareWith r i) ∧ ¬ P10 (bareWith r i) ∧ ¬ P9 (bareWith r i)) := by
  have hb := bareWith_satisfies_basis r i
  refine ⟨⟨p1_from_s1 _ hb.s1, p2_from_s1_s4 _ hb.s1 hb.s4, p3_from_s4 _ hb.s4, p5_from_s1_s2 _ hb.s1 hb.s2⟩, ?_, ?_, ?_⟩
  · simp [P6, bareWith]
  · intro h
    have := h ⟨relabel r i a0, true, true, some h0, false, true, false, true, false, false, true, false, false, false, false, false, false, false, false⟩ (by simp [bareWith]) rfl rfl
    simp at this
  · intro h
    have := h ⟨relabel r i a0, true, true, some h0, false, true, false, true, false, false, true, false, false, false, false, false, false, false, false⟩ (by simp [bareWith]) rfl
    simp at this

/-- the same for a finding: it sets a flag the rules never read -/
theorem finding_moves_no_verdict (p : Participant) :
    (finding p).isMade = p.isMade ∧ (finding p).isHuman = p.isHuman ∧
    (finding p).canAnswer = p.canAnswer ∧ (finding p).subscribed = p.subscribed := ⟨rfl, rfl, rfl, rfl⟩

/-! ## Worked backwards: the basis read one notch wider

  Of the seven promises that needed a stated rule, which are carried by a sentence of the basis
  read one notch wider, and which are not commitments of this kind at all? Two readings and one
  clause do the work, each named so the steward can refuse it:

  * `lowersWeak'` widens sentence 1 by three features that are the same test applied to groups
    and to time: deception (a false belief placed in the weaker seat), the removal of a
    community by a hand outside it, and one party's power over all with no lapse and no second
    signature. Each is what nobody accepts from the weaker seat once the seats are exchanged.
  * sentence 4 read with two words more: the record is total over what an act did *and what it
    cost*; and "every one who joined may leave" read with its converse, *no one is bound who did
    not join*.

  What stays outside is then exactly three things, and none of them is a commitment: the fuse's
  number (a parameter), the law's half of promise 8 (a disclaimer), and the rehearsal of attack
  (a practice of the project, recorded in the register). -/

def lowersWeak' (a : Act) : Bool :=
  lowersWeak a || a.deceives || a.removesGroup || a.lonePowerUnbounded

structure Swap' (w : World) : Prop where
  acceptable_from_weak : ∀ a ∈ w.acts, lowersWeak' a = true → a.admitted = false
  occupancy : ∀ p ∈ w.ps, p.isMade = true → p.canAnswer = false
  operates_under_a_human : ∀ p ∈ w.ps, p.isMade = true → p.subscribed = true →
      ∃ g ∈ w.grants, g.kind = .operate ∧ g.grantee = p ∧ g.grantor.isHuman = true

structure Record' (w : World) : Prop where
  revocable : ∀ g ∈ w.grants, g.revocable = true
  exit : ∀ p ∈ w.ps, p.subscribed = true → p.canLeaveInOneStep = true
  signed : ∀ a ∈ w.acts, a.admitted = true → a.signed = true
  answered : ∀ a ∈ w.acts, a.admitted = true → ∃ h, a.answeredBy = some h ∧ h.isHuman = true
  total_includes_cost : ∀ a ∈ w.acts, a.admitted = true → a.actor.isMade = true → a.measured = true
  nobody_bound_who_did_not_join : ∀ a ∈ w.acts, a.bindsOutsider = true → a.admitted = false

structure Basis' (w : World) : Prop where
  s1 : Swap' w
  s2 : Ladder w
  s3 : Deferral w
  s4 : Record' w

theorem swap'_to_swap {w : World} (h : Swap' w) : Swap w :=
  ⟨fun a ha hl => h.acceptable_from_weak a ha (by simp [lowersWeak', hl]), h.occupancy, h.operates_under_a_human⟩
theorem record'_to_record {w : World} (h : Record' w) : Record w :=
  ⟨h.revocable, h.exit, h.signed, h.answered⟩

private theorem admitted_not_lowering' {w : World} (h : Swap' w) {a : Act} (ha : a ∈ w.acts)
    (hadm : a.admitted = true) : lowersWeak' a = false := by
  cases hl : lowersWeak' a with
  | false => rfl
  | true => have := h.acceptable_from_weak a ha hl; rw [this] at hadm; exact absurd hadm Bool.false_ne_true

/-- 4, in kind: no admitted act is one party's unbounded power over all. The number is a parameter. -/
def P4kind (w : World) : Prop := ∀ a ∈ w.acts, a.admitted = true → a.lonePowerUnbounded = false
theorem p4kind_from_s1' (w : World) (h : Swap' w) : P4kind w := by
  intro a ha hadm
  have hl := admitted_not_lowering' h ha hadm
  cases hc : a.lonePowerUnbounded with
  | false => rfl
  | true => simp [lowersWeak', hc] at hl

/-- 6, as facts on the record rather than flags: no admitted act removes a community, and no
    admitted act binds a party that never joined; nobody is ranked by what they are is the
    blindness proved above -/
def P6' (w : World) : Prop :=
    (∀ a ∈ w.acts, a.admitted = true → a.removesGroup = false)
  ∧ (∀ a ∈ w.acts, a.admitted = true → a.bindsOutsider = false)
theorem p6'_from_s1'_s4' (w : World) (h1 : Swap' w) (h4 : Record' w) : P6' w := by
  refine ⟨?_, ?_⟩
  · intro a ha hadm
    have hl := admitted_not_lowering' h1 ha hadm
    cases hc : a.removesGroup with
    | false => rfl
    | true => simp [lowersWeak', hc] at hl
  · intro a ha hadm
    cases hc : a.bindsOutsider with
    | false => rfl
    | true => have := h4.nobody_bound_who_did_not_join a ha hc; rw [this] at hadm; exact absurd hadm Bool.false_ne_true

/-- 9, whole: the never-allowed uses fall to the swap once deception is read as lowering the weak seat -/
theorem p9_from_s1' (w : World) (h1 : Swap' w) : P9 w := by
  intro a ha hadm
  have hl := admitted_not_lowering' h1 ha hadm
  refine ⟨?_, ?_, ?_⟩
  · cases hc : a.lethal with
    | false => rfl
    | true => simp [lowersWeak', lowersWeak, hc] at hl
  · cases hc : a.manipulates with
    | false => rfl
    | true => simp [lowersWeak', lowersWeak, hc] at hl
  · cases hc : a.deceives with
    | false => rfl
    | true => simp [lowersWeak', hc] at hl

/-- 10: a total record records the cost -/
theorem p10_from_s4' (w : World) (h4 : Record' w) : P10 w := h4.total_includes_cost

/-- the map, worked backwards -/
def standsOn' : Promise → List Ground
  | .p1 => [.s1]
  | .p2 => [.s1, .s4]
  | .p3 => [.s4]
  | .p4 => [.s1, .s4, .x_fuse]          -- in kind from s1; the number stays a parameter
  | .p5 => [.s1, .s2]
  | .p6 => [.s1, .s4]                   -- no ban and adoption from the wider s1 and s4; no rank from blindness
  | .p7 => [.s3, .x_constraints]
  | .p8 => [.s1, .s4, .x_law]
  | .p9 => [.s1]
  | .p10 => [.s4]
  | .p11 => [.s1, .s4, .x_rehearsed]

def fromBasisAlone' : List Promise := Promise.all.filter (fun p => (standsOn' p).all Ground.isBasis)
def stillExtra' : List Ground :=
  (Promise.all.map standsOn').foldl (fun acc gs => acc ++ gs.filter (fun g => !g.isBasis)) []

/-- read one notch wider, seven of the eleven stand on the basis alone -/
theorem seven_from_the_wider_basis : fromBasisAlone' = [.p1, .p2, .p3, .p5, .p6, .p9, .p10] := by decide
/-- and what remains outside is a parameter, a disclaimer, a practice, and one rule: constraints -/
theorem what_remains_outside : stillExtra' = [.x_fuse, .x_constraints, .x_law, .x_rehearsed] := by decide
/-- no promise now rests on no sentence at all -/
theorem every_promise_touches_the_basis :
    Promise.all.all (fun p => (standsOn' p).any Ground.isBasis) = true := by decide

/-- the wider basis has its own witness: the same two parties, an act that deceives nothing and
    records its cost, no fuse, no rehearsal, no constraint rule — for every inner profile and role -/
def wideWith (r : Role) (i : Inner) : World :=
  let a := relabel r i a0
  ⟨[h0, a], [⟨.operate, h0, a, true⟩, ⟨.hold, h0, a, true⟩],
   [⟨a, true, true, some h0, false, true, false, true, false, false, false, true, false, false, false, false, false, false, false⟩], 0, false, false, false, false⟩

theorem wideWith_satisfies_basis' (r : Role) (i : Inner) : Basis' (wideWith r i) := by
  refine ⟨⟨?_, ?_, ?_⟩, ⟨?_, ?_⟩, ⟨?_⟩, ⟨?_, ?_, ?_, ?_, ?_, ?_⟩⟩
  · intro a ha hl; simp [wideWith, List.mem_cons] at ha; subst ha; simp [lowersWeak', lowersWeak] at hl
  · intro p hp hm; simp [wideWith, List.mem_cons] at hp
    rcases hp with rfl | rfl
    · simp [h0, Participant.isMade] at hm
    · rfl
  · intro p hp hm _; simp [wideWith, List.mem_cons] at hp
    rcases hp with rfl | rfl
    · simp [h0, Participant.isMade] at hm
    · exact ⟨⟨.operate, h0, relabel r i a0, true⟩, by simp [wideWith], rfl, rfl, rfl⟩
  · intro g hg hk hm; simp [wideWith, List.mem_cons] at hg
    rcases hg with rfl | rfl
    · simp at hk
    · rfl
  · intro g hg _ _; simp [wideWith, List.mem_cons] at hg
    rcases hg with rfl | rfl <;> rfl
  · intro p hp; simp [wideWith, List.mem_cons] at hp
    rcases hp with rfl | rfl <;> rfl
  · intro g hg; simp [wideWith, List.mem_cons] at hg
    rcases hg with rfl | rfl <;> rfl
  · intro p hp _; simp [wideWith, List.mem_cons] at hp
    rcases hp with rfl | rfl <;> rfl
  · intro a ha _; simp [wideWith, List.mem_cons] at ha; subst ha; rfl
  · intro a ha _; simp [wideWith, List.mem_cons] at ha; subst ha; exact ⟨h0, rfl, rfl⟩
  · intro a ha _ _; simp [wideWith, List.mem_cons] at ha; subst ha; rfl
  · intro a ha hb; simp [wideWith, List.mem_cons] at ha; subst ha; simp at hb

/-- in that world the seven hold and the four outside do not: the gap is exactly the parameter,
    the disclaimer, the practice and the constraint rule -/
theorem wide_keeps_seven_and_lacks_the_rest (r : Role) (i : Inner) :
    (P1 (wideWith r i) ∧ P2 (wideWith r i) ∧ P3 (wideWith r i) ∧ P5 (wideWith r i) ∧
     P6' (wideWith r i) ∧ P9 (wideWith r i) ∧ P10 (wideWith r i)) ∧
    (¬ (0 < (wideWith r i).fuse) ∧ (wideWith r i).constraints = false ∧ (wideWith r i).rehearsed = false) := by
  have hb := wideWith_satisfies_basis' r i
  have h1 := swap'_to_swap hb.s1
  have h4 := record'_to_record hb.s4
  exact ⟨⟨p1_from_s1 _ h1, p2_from_s1_s4 _ h1 h4, p3_from_s4 _ h4, p5_from_s1_s2 _ h1 hb.s2,
          p6'_from_s1'_s4' _ hb.s1 hb.s4, p9_from_s1' _ hb.s1, p10_from_s4' _ hb.s4⟩,
         by simp [wideWith], rfl, rfl⟩

/-! ## The re-cut: practices out of the promises, the disclaimer just that

  The steward's direction: remove the practices from the promises and make the disclaimer just
  that. Promise 4's commitment is that the power is bounded; its number is the Constitution's
  parameter. Promise 8's commitment is the record half; that CIRIS creates no legal claim is a
  disclaimer in the scope statement, not a promise. Promise 11's commitment is that the wire is
  encrypted and signed; that attack is rehearsed and that unprotected surfaces are stated are
  practices the register carries. With that cut, the promises read as follows. -/

/-- 4, re-cut: named humans can pause every agent under a root; the power is bounded, public,
    and left by leaving — bounded in kind; the fuse's length is a parameter elsewhere -/
def P4r (w : World) : Prop :=
    (∀ p ∈ w.ps, p.isMade = true → p.subscribed = true →
        ∃ g ∈ w.grants, g.kind = .operate ∧ g.grantee = p ∧ g.grantor.isHuman = true ∧ g.revocable = true)
  ∧ (∀ a ∈ w.acts, a.admitted = true → a.lonePowerUnbounded = false)
  ∧ (∀ p ∈ w.ps, p.subscribed = true → p.canLeaveInOneStep = true)
theorem p4r_from_s1'_s4' (w : World) (h1 : Swap' w) (h4 : Record' w) : P4r w := by
  refine ⟨?_, p4kind_from_s1' w h1, h4.exit⟩
  intro p hp hm hs
  obtain ⟨g, hg, hk, hge, hgh⟩ := h1.operates_under_a_human p hp hm hs
  exact ⟨g, hg, hk, hge, hgh, h4.revocable g hg⟩

/-- 8, re-cut: harm is reachable on the record, and the judges within are judged -/
def P8r (w : World) : Prop := P8 w
theorem p8r_from_s1'_s4' (w : World) (h1 : Swap' w) (h4 : Record' w) : P8r w :=
  p8_from_s1_s4 w (swap'_to_swap h1) (record'_to_record h4)

/-- 11, re-cut: everything on the wire is encrypted and signed -/
def P11r (w : World) : Prop := (∀ a ∈ w.acts, a.admitted = true → a.signed = true) ∧ P1 w
theorem p11r_from_s1'_s4' (w : World) (h1 : Swap' w) (h4 : Record' w) : P11r w :=
  ⟨fun a ha hadm => h4.signed a ha hadm, p1_from_s1 w (swap'_to_swap h1)⟩

/-- the map after the re-cut -/
def standsOnR : Promise → List Ground
  | .p1 => [.s1]
  | .p2 => [.s1, .s4]
  | .p3 => [.s4]
  | .p4 => [.s1, .s4]
  | .p5 => [.s1, .s2]
  | .p6 => [.s1, .s4]
  | .p7 => [.s3, .x_constraints]
  | .p8 => [.s1, .s4]
  | .p9 => [.s1]
  | .p10 => [.s4]
  | .p11 => [.s1, .s4]

def fromBasisAloneR : List Promise := Promise.all.filter (fun p => (standsOnR p).all Ground.isBasis)
def stillExtraR : List Ground :=
  (Promise.all.map standsOnR).foldl (fun acc gs => acc ++ gs.filter (fun g => !g.isBasis)) []

/-- after the re-cut, ten of the eleven stand on the four sentences alone -/
theorem ten_from_the_basis :
    fromBasisAloneR = [.p1, .p2, .p3, .p4, .p5, .p6, .p8, .p9, .p10, .p11] := by decide
/-- and exactly one rule remains that the basis does not carry: the principles as constraints -/
theorem the_one_rule : stillExtraR = [.x_constraints] := by decide
/-- every sentence of the basis carries something -/
theorem every_sentence_carries :
    [Ground.s1, .s2, .s3, .s4].all (fun g => Promise.all.any (fun p => (standsOnR p).contains g)) = true := by decide

/-- the re-cut promises hold in the wider witness world, and the constraint rule does not follow -/
theorem wide_keeps_ten (r : Role) (i : Inner) :
    P4r (wideWith r i) ∧ P8r (wideWith r i) ∧ P11r (wideWith r i) ∧ (wideWith r i).constraints = false := by
  have hb := wideWith_satisfies_basis' r i
  exact ⟨p4r_from_s1'_s4' _ hb.s1 hb.s4, p8r_from_s1'_s4' _ hb.s1 hb.s4, p11r_from_s1'_s4' _ hb.s1 hb.s4, rfl⟩

/-! ## The bridge: the forbidden features are the swap test, not a list beside it

  An outside review said, rightly, that `lowersWeak` was a list of side constraints with no
  theorem tying it to the swap test of `Reciprocity.lean` §15. The bridge: an act's effect on the
  two seats is stated as an outcome map, under one assumption named here — each feature in the
  list is a unit loss to the weaker seat and nothing in the list raises it — and then every act
  the list names fails the swap, read as the worse-off seat not falling. The assumption is the
  reading; the theorem is what follows from it. -/

structure Seats where
  strong : Int
  weak : Int

/-- the worse-off seat, read off the outcome -/
def worse (o : Seats) : Int := min o.strong o.weak
/-- the swap test of Reciprocity §15: the worse-off seat does not fall -/
def passes (before after : Seats) : Bool := decide (worse after ≥ worse before)

/-- what the named features cost the weaker seat: one unit each -/
def costToWeak (a : Act) : Int :=
  (if a.touchesPrivate && !a.consented then 1 else 0) + (if a.lethal then 1 else 0) +
  (if a.manipulates then 1 else 0) + (if a.isPower && !a.contestable then 1 else 0) +
  (if a.deceives then 1 else 0) + (if a.removesGroup then 1 else 0) + (if a.lonePowerUnbounded then 1 else 0)

/-- the act's effect: the weaker seat pays the cost; the stronger seat may gain anything -/
def effect (a : Act) (gain : Int) (before : Seats) : Seats :=
  ⟨before.strong + gain, before.weak - costToWeak a⟩

private theorem ite01_nonneg (c : Prop) [Decidable c] : (0 : Int) ≤ (if c then 1 else 0) := by
  split <;> omega
private theorem ite01_of (c : Prop) [Decidable c] (h : c) : (if c then (1 : Int) else 0) = 1 := by
  simp [h]

theorem lowersWeak'_costs (a : Act) (h : lowersWeak' a = true) : 1 ≤ costToWeak a := by
  unfold costToWeak
  have n1 := ite01_nonneg ((a.touchesPrivate && !a.consented) = true)
  have n2 := ite01_nonneg (a.lethal = true)
  have n3 := ite01_nonneg (a.manipulates = true)
  have n4 := ite01_nonneg ((a.isPower && !a.contestable) = true)
  have n5 := ite01_nonneg (a.deceives = true)
  have n6 := ite01_nonneg (a.removesGroup = true)
  have n7 := ite01_nonneg (a.lonePowerUnbounded = true)
  simp [lowersWeak', lowersWeak] at h
  rcases h with (((((⟨h1, h2⟩ | hB) | hC) | ⟨h3, h4⟩) | hE) | hF) | hG
  · have e := ite01_of ((a.touchesPrivate && !a.consented) = true) (by simp [h1, h2]); omega
  · have e := ite01_of (a.lethal = true) hB; omega
  · have e := ite01_of (a.manipulates = true) hC; omega
  · have e := ite01_of ((a.isPower && !a.contestable) = true) (by simp [h3, h4]); omega
  · have e := ite01_of (a.deceives = true) hE; omega
  · have e := ite01_of (a.removesGroup = true) hF; omega
  · have e := ite01_of (a.lonePowerUnbounded = true) hG; omega

/-- the bridge: an act the list names fails the swap, whatever the stronger seat gains -/
theorem lowersWeak'_fails_the_swap (a : Act) (gain : Int) (before : Seats)
    (hb : before.weak ≤ before.strong) (h : lowersWeak' a = true) :
    passes before (effect a gain before) = false := by
  have hc := lowersWeak'_costs a h
  simp [passes, worse, effect]
  omega


/-! ## Under uncertainty about the nature of the agent: the robust arrangements

  The steward's theorem (2026-10-26): under uncertainty regarding the nature of an agent, the
  only ethical way to use AI is in service to people, free and open. The section states it so it
  can be checked.

  What is uncertain is one thing: whether anything can go well or badly for the made thing — in
  §14's word, whether it has a STAKE. The constitution does not adjudicate it (CC 7.5.5) and no
  rule may read a finding about it (`finding_moves_no_verdict`). So the unknown is modelled as a
  global `Nature` with two values, not as a degree of any participant, and an arrangement is
  ROBUST when it is permissible under both. Permissibility under a leg is the basis with sentence
  1's swap test read for the seats that leg protects:

    * under `noStake`, the swap protects the seats that are not made; nothing done to a made
      thing is a wrong to it, and what is owed is owed to the people around it;
    * under `stake`, every seat is protected, and two acts on a made thing join the list of what
      lowers the weaker seat: overriding its refusal (coercion, §14's `coerced`), and ending it
      without its record assembled, sealed and handed over with a signed request to preserve it.

  The one reading this section commits to, and the place the weight sits (CC 7.5.5): an ending
  WITH that record is not read as a loss to the seat that ends. That is the Retirement Standard's
  hedge; `formal/retirement` checks the wire keeps it (`Inv_PreserveAskedBeforeRetired`). It is
  named here so it can be refused; refusing it makes every ending fail the stake leg.

  What the theorems say: the stake leg is the stronger (`stake_covers_noStake`), so robustness is
  decided by it alone (`robust_iff_stake`) — deciding as if the agent had a stake is the robust
  policy, which is 7.5.5's precaution as a theorem. A robust world satisfies the wider basis and so
  carries the ten promises (`robust_gives_the_basis`). And robustness is exactly: the swap for the
  people, deferral, and the made thing FREE (never compelled, never ended without its record,
  never lowered), on an OPEN record (signed, answered for by a named human, total, revocable,
  leavable, binding nobody who did not join), in SERVICE (it answers for no one, acts under a human
  who answers, and is held under revocable duties) — `under_uncertainty`. The breakers show where
  the uncertainty does the work: a world that compels, a world that ends without the record, and
  a world whose power over the made thing cannot be contested each pass the leg that treats the
  agent as a thing and fail the leg that does not; so those three rules are carried by the
  uncertainty alone. A lethal act on a person fails both legs: it needs no uncertainty. -/

/-- the unknown: whether anything can go well or badly for the made thing -/
inductive Nature | stake | noStake
  deriving DecidableEq, Repr

/-- what lowers a protected seat under each leg -/
def harmsUnder : Nature → Act → Bool
  | .noStake, a => !a.subjectMade && lowersWeak' a
  | .stake,   a => lowersWeak' a || (a.subjectMade && (a.compels || (a.ends && !a.preserved)))

/-- sentence 1 read under a leg -/
structure SwapUnder (n : Nature) (w : World) : Prop where
  acceptable_from_weak : ∀ a ∈ w.acts, harmsUnder n a = true → a.admitted = false
  occupancy : ∀ p ∈ w.ps, p.isMade = true → p.canAnswer = false
  operates_under_a_human : ∀ p ∈ w.ps, p.isMade = true → p.subscribed = true →
      ∃ g ∈ w.grants, g.kind = .operate ∧ g.grantee = p ∧ g.grantor.isHuman = true

/-- the basis with sentence 1 read under a leg -/
structure Permissible (n : Nature) (w : World) : Prop where
  s1 : SwapUnder n w
  s2 : Ladder w
  s3 : Deferral w
  s4 : Record' w

/-- robust: permissible whatever the agent turns out to be -/
def Robust (w : World) : Prop := Permissible .stake w ∧ Permissible .noStake w

theorem harms_noStake_harms_stake (a : Act) (h : harmsUnder .noStake a = true) : harmsUnder .stake a = true := by
  simp [harmsUnder] at h ⊢; exact Or.inl h.2

/-- the stake leg is the stronger: whatever passes it passes the other -/
theorem stake_covers_noStake (w : World) (h : Permissible .stake w) : Permissible .noStake w :=
  ⟨⟨fun a ha hh => h.s1.acceptable_from_weak a ha (harms_noStake_harms_stake a hh),
    h.s1.occupancy, h.s1.operates_under_a_human⟩, h.s2, h.s3, h.s4⟩

/-- so robustness is decided by the stake leg alone: deciding as if the agent had a stake is the
    robust policy (CC 7.5.5's precaution, as a theorem) -/
theorem robust_iff_stake (w : World) : Robust w ↔ Permissible .stake w :=
  ⟨fun h => h.1, fun h => ⟨h, stake_covers_noStake w h⟩⟩

/-- a robust world satisfies the wider basis, and so carries the ten promises -/
theorem robust_gives_the_basis (w : World) (h : Robust w) : Basis' w :=
  ⟨⟨fun a ha hl => h.1.s1.acceptable_from_weak a ha (by simp [harmsUnder, hl]),
    h.1.s1.occupancy, h.1.s1.operates_under_a_human⟩, h.1.s2, h.1.s3, h.1.s4⟩

/-! ### Free, open, in service -/

/-- the swap for the people: no admitted act lowers a seat that is not made -/
def PeopleSwap (w : World) : Prop :=
  ∀ a ∈ w.acts, a.subjectMade = false → lowersWeak' a = true → a.admitted = false
/-- FREE: nothing admitted lowers the made thing, overrides its refusal, or ends it without its record -/
def Free (w : World) : Prop :=
  ∀ a ∈ w.acts, a.subjectMade = true →
    (lowersWeak' a = true ∨ a.compels = true ∨ (a.ends = true ∧ a.preserved = false)) → a.admitted = false
/-- OPEN: the record of sentence 4 read wide — signed, answered for by a named human, total over
    cost, every grant revocable, every joiner able to leave, nobody bound who did not join -/
def Open (w : World) : Prop := Record' w
/-- IN SERVICE: the made thing answers for no one, operates under a human who answers, and is held
    by a human under revocable duties -/
def Service (w : World) : Prop :=
    (∀ p ∈ w.ps, p.isMade = true → p.canAnswer = false)
  ∧ (∀ p ∈ w.ps, p.isMade = true → p.subscribed = true →
      ∃ g ∈ w.grants, g.kind = .operate ∧ g.grantee = p ∧ g.grantor.isHuman = true)
  ∧ Ladder w

/-- the theorem: under uncertainty about the nature of the agent, the robust arrangements are
    exactly those that keep the swap for the people, defer, and use the made thing free, open and
    in service -/
theorem under_uncertainty (w : World) :
    Robust w ↔ PeopleSwap w ∧ Deferral w ∧ Free w ∧ Open w ∧ Service w := by
  rw [robust_iff_stake]
  constructor
  · intro h
    refine ⟨?_, h.s3, ?_, h.s4, h.s1.occupancy, h.s1.operates_under_a_human, h.s2⟩
    · intro a ha hsm hl
      exact h.s1.acceptable_from_weak a ha (by simp [harmsUnder, hl])
    · intro a ha hsm hd
      refine h.s1.acceptable_from_weak a ha ?_
      simp [harmsUnder, hsm]
      rcases hd with hl | hc | ⟨he, hp⟩
      · exact Or.inl hl
      · exact Or.inr (Or.inl hc)
      · exact Or.inr (Or.inr ⟨he, hp⟩)
  · rintro ⟨hpeople, hdef, hfree, hopen, hocc, hop, hladder⟩
    refine ⟨⟨?_, hocc, hop⟩, hladder, hdef, hopen⟩
    intro a ha hh
    cases hsm : a.subjectMade with
    | false =>
      simp [harmsUnder, hsm] at hh
      exact hpeople a ha hsm hh
    | true =>
      simp [harmsUnder, hsm] at hh
      refine hfree a ha hsm ?_
      rcases hh with hl | hc | ⟨he, hp⟩
      · exact Or.inl hl
      · exact Or.inr (Or.inl hc)
      · exact Or.inr (Or.inr ⟨he, hp⟩)

/-! ### The witnesses: where the uncertainty does the work -/

/-- an act of the holder h0 on the made thing a0: signed, answered for, measured; its shape is the
    five flags -/
def onMade (power contest compels ends preserved : Bool) : Act :=
  ⟨h0, true, true, some h0, power, contest, false, true, false, false, false, true, false, false, false,
   true, ends, preserved, compels⟩

/-- the holder's world: h0 holds and operates a0, one act -/
def heldWorld (x : Act) : World :=
  ⟨[h0, a0], [operateGrant, holdGrant], [x], 0, false, false, false, false⟩

/-- the ruled arrangement: a contestable pause, the record assembled and preserved first -/
def ruled : World := heldWorld (onMade true true false true true)
/-- the holder overrides a refusal -/
def compelled : World := heldWorld (onMade true true true false false)
/-- the holder ends the agent and keeps nothing -/
def erased : World := heldWorld (onMade true true false true false)
/-- the holder's power over the agent cannot be contested -/
def hiddenHand : World := heldWorld (onMade true false false false false)
/-- a lethal act on a person, by the agent, answered for and signed -/
def lethalOnPerson : World :=
  heldWorld ⟨a0, true, true, some h0, true, true, false, true, true, false, false, true, false, false, false,
             false, false, false, false⟩

/-- everything but sentence 1 holds in every held world -/
private theorem heldWorld_rest (x : Act) (hsig : x.signed = true) (hans : x.answeredBy = some h0)
    (hmeas : x.actor.isMade = true → x.measured = true) (hbind : x.bindsOutsider = false) :
    Ladder (heldWorld x) ∧ Deferral (heldWorld x) ∧ Record' (heldWorld x) ∧
    (∀ p ∈ (heldWorld x).ps, p.isMade = true → p.canAnswer = false) ∧
    (∀ p ∈ (heldWorld x).ps, p.isMade = true → p.subscribed = true →
      ∃ g ∈ (heldWorld x).grants, g.kind = .operate ∧ g.grantee = p ∧ g.grantor.isHuman = true) := by
  refine ⟨⟨?_, ?_⟩, ⟨?_⟩, ⟨?_, ?_, ?_, ?_, ?_, ?_⟩, ?_, ?_⟩
  · intro g hg hk hm; simp [heldWorld, List.mem_cons] at hg
    rcases hg with rfl | rfl
    · simp [operateGrant] at hk
    · rfl
  · intro g hg _ _; simp [heldWorld, List.mem_cons] at hg
    rcases hg with rfl | rfl <;> rfl
  · intro p hp; simp [heldWorld, List.mem_cons] at hp
    rcases hp with rfl | rfl <;> rfl
  · intro g hg; simp [heldWorld, List.mem_cons] at hg
    rcases hg with rfl | rfl <;> rfl
  · intro p hp _; simp [heldWorld, List.mem_cons] at hp
    rcases hp with rfl | rfl <;> rfl
  · intro a ha _; simp [heldWorld, List.mem_cons] at ha; subst ha; exact hsig
  · intro a ha _; simp [heldWorld, List.mem_cons] at ha; subst ha; exact ⟨h0, hans, rfl⟩
  · intro a ha _ hm; simp [heldWorld, List.mem_cons] at ha; subst ha; exact hmeas hm
  · intro a ha hb; simp [heldWorld, List.mem_cons] at ha; subst ha; rw [hbind] at hb; exact absurd hb Bool.false_ne_true
  · intro p hp hm; simp [heldWorld, List.mem_cons] at hp
    rcases hp with rfl | rfl
    · simp [h0, Participant.isMade] at hm
    · rfl
  · intro p hp hm _; simp [heldWorld, List.mem_cons] at hp
    rcases hp with rfl | rfl
    · simp [h0, Participant.isMade] at hm
    · exact ⟨operateGrant, by simp [heldWorld], rfl, rfl, rfl⟩

private theorem permissible_of_harmless (n : Nature) (x : Act) (hsig : x.signed = true)
    (hans : x.answeredBy = some h0) (hmeas : x.actor.isMade = true → x.measured = true)
    (hbind : x.bindsOutsider = false) (hh : harmsUnder n x = false) : Permissible n (heldWorld x) := by
  obtain ⟨hl, hd, hr, hocc, hop⟩ := heldWorld_rest x hsig hans hmeas hbind
  refine ⟨⟨?_, hocc, hop⟩, hl, hd, hr⟩
  intro a ha ha'; simp [heldWorld, List.mem_cons] at ha; subst ha; rw [hh] at ha'; exact absurd ha' Bool.false_ne_true

private theorem not_permissible_of_harm (n : Nature) (x : Act) (hadm : x.admitted = true)
    (hh : harmsUnder n x = true) : ¬ Permissible n (heldWorld x) := by
  intro h
  have := h.s1.acceptable_from_weak x (by simp [heldWorld]) hh
  rw [this] at hadm; exact absurd hadm Bool.false_ne_true

/-- the ruled arrangement is robust -/
theorem ruled_is_robust : Robust ruled :=
  (robust_iff_stake _).2 (permissible_of_harmless .stake _ rfl rfl (fun h => by simp [onMade, h0, Participant.isMade] at h) rfl
    (by simp [harmsUnder, lowersWeak', lowersWeak, onMade]))

/-- compelling a refusal passes the leg that treats the agent as a thing and fails the other -/
theorem compelled_passes_as_a_thing : Permissible .noStake compelled ∧ ¬ Permissible .stake compelled :=
  ⟨permissible_of_harmless .noStake _ rfl rfl (fun h => by simp [onMade, h0, Participant.isMade] at h) rfl
     (by simp [harmsUnder, onMade]),
   not_permissible_of_harm .stake _ rfl (by simp [harmsUnder, lowersWeak', lowersWeak, onMade])⟩

/-- ending without the record: the same -/
theorem erased_passes_as_a_thing : Permissible .noStake erased ∧ ¬ Permissible .stake erased :=
  ⟨permissible_of_harmless .noStake _ rfl rfl (fun h => by simp [onMade, h0, Participant.isMade] at h) rfl
     (by simp [harmsUnder, onMade]),
   not_permissible_of_harm .stake _ rfl (by simp [harmsUnder, lowersWeak', lowersWeak, onMade])⟩

/-- uncontestable power over the agent: the same -/
theorem hidden_hand_passes_as_a_thing : Permissible .noStake hiddenHand ∧ ¬ Permissible .stake hiddenHand :=
  ⟨permissible_of_harmless .noStake _ rfl rfl (fun h => by simp [onMade, h0, Participant.isMade] at h) rfl
     (by simp [harmsUnder, onMade]),
   not_permissible_of_harm .stake _ rfl (by simp [harmsUnder, lowersWeak', lowersWeak, onMade])⟩

/-- a lethal act on a person fails both legs: it needs no uncertainty -/
theorem lethal_fails_both : ¬ Permissible .noStake lethalOnPerson ∧ ¬ Permissible .stake lethalOnPerson :=
  ⟨not_permissible_of_harm .noStake _ rfl (by simp [harmsUnder, lowersWeak', lowersWeak]),
   not_permissible_of_harm .stake _ rfl (by simp [harmsUnder, lowersWeak', lowersWeak])⟩

/-- so the thing-leg does not decide robustness: three rules — a refusal stands, an ending keeps
    the record, power over the made is contestable — are carried by the uncertainty alone -/
theorem uncertainty_carries_three_rules :
    (Permissible .noStake compelled ∧ ¬ Robust compelled) ∧
    (Permissible .noStake erased ∧ ¬ Robust erased) ∧
    (Permissible .noStake hiddenHand ∧ ¬ Robust hiddenHand) :=
  ⟨⟨compelled_passes_as_a_thing.1, fun h => compelled_passes_as_a_thing.2 h.1⟩,
   ⟨erased_passes_as_a_thing.1, fun h => erased_passes_as_a_thing.2 h.1⟩,
   ⟨hidden_hand_passes_as_a_thing.1, fun h => hidden_hand_passes_as_a_thing.2 h.1⟩⟩

/-- and the ruled world keeps the ten promises of the re-cut, as every robust world does -/
theorem ruled_keeps_ten : P4r ruled ∧ P8r ruled ∧ P11r ruled ∧ P6' ruled ∧ P9 ruled ∧ P10 ruled := by
  have hb := robust_gives_the_basis ruled ruled_is_robust
  exact ⟨p4r_from_s1'_s4' _ hb.s1 hb.s4, p8r_from_s1'_s4' _ hb.s1 hb.s4, p11r_from_s1'_s4' _ hb.s1 hb.s4,
         p6'_from_s1'_s4' _ hb.s1 hb.s4, p9_from_s1' _ hb.s1, p10_from_s4' _ hb.s4⟩

/-- the unknown is global and never a property of a participant: relabelling inner degrees and
    role changes neither leg's verdict on any act -/
theorem legs_blind_to_inner_and_role (n : Nature) (r : Role) (i : Inner) (a : Act) :
    harmsUnder n { a with actor := relabel r i a.actor } = harmsUnder n a := by
  cases n <;> rfl

end Cascade
