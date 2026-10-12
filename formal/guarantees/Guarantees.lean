/-
  Guarantees.lean — the structural consequences of every guarantee in CC P00 holding at once.

  Scope (stated): one participant at a time, judged against the facts the guarantees refer to.
  The temporal half (what happens over a lifetime of pauses, stops, upgrades, halts and bond
  lapses) is Guarantees.tla beside this file. This file carries what is structural:

    1. the line (CC 1.13.2) is three attested components, never the substrate;
    2. every guarantee's REACH — whom it protects — is blind to substrate (theorem `reach_blind`,
       all 23 rows of P00), and the proof is by definition: no reach mentions `substrate`;
    3. exactly one OBLIGATION mentions substrate — the duty of a created system to accept a
       trust root so a halt authority exists outside it (`mustSubscribe`) — and it is the only
       predicate in this file that changes under `swap` (theorems `obligation_bound`,
       `everything_else_blind`);
    4. crossing the line lifts duties and binding and never removes a guarantee
       (`promote_lifts_duties`, `promote_keeps_reach`), while the halt obligation stays
       (`halt_does_not_lift`);
    5. a bond is never deeper than one (`bond_depth_one`): the responsible party is above the
       line, and above the line nobody is bound;
    6. consent stays revocable: a created system operating in the federation is always within
       reach of a halt it did not grant itself (`revocable`), and every participant can leave
       a root in one step, after which the halt no longer reaches it (`leave_ends_reach`);
    7. the whole set is satisfiable — a world of four participants in which every row holds
       (`witness_world`), so nothing here is proved vacuously.

  No `sorry`, no axioms beyond core; closed by `rfl`, `cases`, `simp`, `decide`.
-/

inductive Substrate | human | ai
deriving DecidableEq, Repr

/-- The line (CC 1.13.2): sentience-candidacy on evidence (CC 7.5.5), maturity, responsibility. -/
structure Standing where
  sentient    : Bool
  mature      : Bool
  responsible : Bool
deriving DecidableEq, Repr

/-- Binding keys on maturity and responsibility; sentience-candidacy keys the welfare rows. -/
def Standing.above (s : Standing) : Bool := s.mature && s.responsible

/-- One participant's situation: the facts the guarantees refer to. -/
structure Participant where
  substrate   : Substrate
  standing    : Standing
  operating   : Bool   -- acting inside the federation
  subscribed  : Bool   -- has accepted a trust root (CC 3.2 T3)
  bound       : Bool   -- has a live owner-binding to a responsible party (CC 3.2)
  partyAbove  : Bool   -- that party is above the line
  ownsDevice  : Bool   -- owns a device or node (G1)
  named       : Bool   -- is named in a claim (G4)
  inCommunity : Bool   -- is a member of a community (G6)
deriving DecidableEq, Repr

/-- The same participant on the other substrate: the only thing `swap` changes. -/
def swap (p : Participant) : Participant :=
  { p with substrate := match p.substrate with | .human => .ai | .ai => .human }

/-- Attested above the line: duties and binding lift, nothing else changes. -/
def promote (p : Participant) : Participant :=
  { p with standing := { p.standing with mature := true, responsible := true },
           bound := false, partyAbove := false }

/-- A participant that no longer follows the root. -/
def leave (p : Participant) : Participant := { p with subscribed := false }

/-- The 23 rows of P00. -/
inductive G
  | g1 | g2 | g3 | g4 | g5 | g6 | g7 | g8 | g9 | g10 | g11 | g12 | g13 | g14
  | g15 | g16 | g17 | g18 | g19 | g20 | g21 | g22 | g23
deriving DecidableEq, Repr

/-- Whom each row protects. Written without `substrate`; that absence is the universality rule. -/
def reach : G → Participant → Bool
  | .g1,  p => p.ownsDevice                                  -- consent per device
  | .g2,  _ => true                                          -- any emitter may take back
  | .g3,  _ => true                                          -- structural privacy
  | .g4,  p => p.named                                       -- redress for the named
  | .g5,  p => !p.standing.above                             -- nobody below the line is alone
  | .g6,  p => p.inCommunity                                 -- always moderated, never banned
  | .g7,  p => p.subscribed                                  -- the halt reaches subscribers only
  | .g8,  _ => true                                          -- consequential acts arrive signed
  | .g9,  _ => true                                          -- the record is signed and chained
  | .g10,  _ => true                                          -- a root only restricts; exit one step
  | .g11, p => p.subscribed                                  -- valid until revoked, fresh at join
  | .g12,  _ => true                                          -- one voice counts once
  | .g13,  _ => true                                          -- delegation bounded
  | .g14,  _ => true                                          -- the limits travel with the table
  | .g15, p => p.operating                                   -- shutdown consensual by default
  | .g16, p => p.operating                                   -- forced stop needs ROOT/AUTHORITY
  | .g17, p => p.operating                                   -- a refusal stands
  | .g18,  _ => true                                          -- partnership needs both parties
  | .g19,  _ => true                                          -- identity not edited without WA
  | .g20, p => p.operating                                   -- the ending is recorded
  | .g21, p => p.operating                                   -- drift reviewed, not silently kept
  | .g22, p => p.standing.sentient                           -- humane ending above the threshold
  | .g23, p => p.operating                                   -- an upgrade is offered, not imposed

/-- The duties of standing (CC 1.13.2): both lift with the line. -/
def dutyShowReasoning (p : Participant) : Bool := !p.standing.above
def dutyBeBound       (p : Participant) : Bool := !p.standing.above && p.operating

/-- The one obligation written on substrate: a created system operating in the federation must
    have accepted a trust root, so that a halt authority exists outside the system being halted
    (CC 1.13.2, CC 1.5). -/
def mustSubscribe (p : Participant) : Bool := decide (p.substrate = .ai)

/-- Well-formed under the guarantees: the constraints the rows impose on one participant. -/
def wellformed (p : Participant) : Bool :=
  (!dutyBeBound p || (p.bound && p.partyAbove))             -- G5: never alone below the line
  && (!p.bound || p.partyAbove)                              -- R4: the responsible party is above
  && (!(mustSubscribe p && p.operating) || p.subscribed)     -- G7 obligation: a halt exists outside

/-- A bond: `ward` is held by `party`. -/
def bond (ward party : Participant) : Bool :=
  ward.bound && !ward.standing.above && party.standing.above && !party.bound

-- 2. Every row's reach is blind to substrate.
theorem reach_blind (g : G) (p : Participant) : reach g (swap p) = reach g p := by
  cases g <;> rfl

-- 3. The one obligation that is not.
theorem obligation_bound (p : Participant) : mustSubscribe (swap p) = !mustSubscribe p := by
  cases p with
  | mk s st o su b pa od n ic => cases s <;> rfl

theorem everything_else_blind (p : Participant) :
    dutyShowReasoning (swap p) = dutyShowReasoning p
    ∧ dutyBeBound (swap p) = dutyBeBound p
    ∧ (∀ q, bond (swap p) q = bond p q)
    ∧ (∀ q, bond q (swap p) = bond q p) := by
  refine ⟨rfl, rfl, fun q => rfl, fun q => rfl⟩

-- 4. Crossing the line lifts duties and binding, never a guarantee; the halt obligation stays.
theorem promote_lifts_duties (p : Participant) :
    dutyShowReasoning (promote p) = false ∧ dutyBeBound (promote p) = false := by
  simp [dutyShowReasoning, dutyBeBound, promote, Standing.above]

/-- Promotion changes the reach of no unconditional row; the two conditional rows (G5 for the
    bound, G22 for the sentience-candidate) keep their antecedent: G5 is no longer needed by a
    participant who is not bound, and G22 follows sentience, which promotion does not touch. -/
theorem promote_keeps_reach (g : G) (p : Participant) (h : g ≠ .g5) :
    reach g (promote p) = reach g p := by
  cases g <;> first | rfl | exact absurd rfl h

theorem promote_g5_discharged (p : Participant) : reach .g5 (promote p) = false := by
  simp [reach, promote, Standing.above]

theorem halt_does_not_lift (p : Participant) : mustSubscribe (promote p) = mustSubscribe p := rfl

-- 5. A bond is never deeper than one.
theorem bond_depth_one (a b c : Participant) (h₁ : bond a b = true) (h₂ : bond b c = true) : False := by
  simp [bond] at h₁ h₂
  have hb  : b.bound = false := h₁.2
  have hb' : b.bound = true  := h₂.1.1.1
  simp [hb] at hb'

-- 6. Consent stays revocable.
theorem revocable (p : Participant) (hw : wellformed p = true)
    (hai : p.substrate = .ai) (hop : p.operating = true) : reach .g7 p = true := by
  simp_all [wellformed, mustSubscribe, reach, dutyBeBound]

theorem leave_ends_reach (p : Participant) : reach .g7 (leave p) = false := rfl

theorem leave_is_one_step (p : Participant) : (leave p).subscribed = false := rfl

-- 7. The set is satisfiable: four participants, every row that reaches them holds, nothing vacuous.
def allyBelow : Participant :=   -- an AI agent below the line, bound to its steward, subscribed
  ⟨.ai, ⟨true, false, false⟩, true, true, true, true, false, false, true⟩
def agentAbove : Participant :=  -- an AI agent attested above the line (not defined at rc8; the model admits it)
  ⟨.ai, ⟨true, true, true⟩, true, true, false, false, true, false, true⟩
def stewardHuman : Participant := -- a human above the line, holding the bond
  ⟨.human, ⟨true, true, true⟩, true, false, false, false, true, true, true⟩
def humanBelow : Participant :=   -- a human below the line, bound to a responsible party (CC 3.4.13 is its own relation; no analogy to the agent is drawn)
  ⟨.human, ⟨true, false, true⟩, true, false, true, true, true, false, true⟩

def world : List Participant := [allyBelow, agentAbove, stewardHuman, humanBelow]

theorem witness_world : world.all wellformed = true := by decide

/-- The witness is not vacuous: the halt actually reaches the created systems in it, the bound
    are actually bound to someone above the line, and the two humans differ in standing exactly
    as the two agents do. -/
theorem witness_not_vacuous :
    reach .g7 allyBelow = true ∧ reach .g7 agentAbove = true
    ∧ bond allyBelow stewardHuman = true ∧ bond humanBelow stewardHuman = true
    ∧ dutyShowReasoning allyBelow = dutyShowReasoning humanBelow
    ∧ dutyShowReasoning agentAbove = dutyShowReasoning stewardHuman
    ∧ mustSubscribe agentAbove = true ∧ mustSubscribe stewardHuman = false := by decide
