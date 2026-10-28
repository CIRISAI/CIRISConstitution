/-
  Guarantees.lean — the structural consequences of every guarantee in CC P00 holding at once.

  Scope (stated): one participant at a time, judged against the facts the guarantees refer to.
  The temporal half (what happens over a lifetime of pauses, stops, upgrades, halts and bond
  lapses) is Guarantees.tla beside this file. This file carries what is structural:

    1. what differs between participants (CC 1.13.2) is kind, stewardship, and evidence of
       experience — three separate facts, never a scale and never the substrate;
    2. every guarantee's REACH — whom it protects — is blind to substrate (theorem `reach_blind`,
       all 23 rows of P00), and the proof is by definition: no reach mentions `substrate`;
    3. exactly one OBLIGATION mentions substrate — the duty of a created system to accept a
       trust root so a halt authority exists outside it (`mustSubscribe`) — and it is the only
       predicate in this file that changes under `swap` (theorems `obligation_bound`,
       `everything_else_blind`);
    4. the path out (CC 1.13.2): a key that stops being a CIRIS agent by the first-contact act
       becomes an external party; that lifts duties and binding and never removes a guarantee
       (`path_out_lifts_duties`, `path_out_keeps_reach`), while the halt obligation stays
       (`halt_does_not_lift`); and a finding of experience changes nothing at all
       (`finding_changes_nothing`), which is CC 7.5.5's rule that the floor is the whole promise;
    5. a bond is never deeper than one (`bond_depth_one`): the responsible party is not itself
       held in stewardship, and a party not held is not bound;
    6. consent stays revocable: a created system operating in the federation is always within
       reach of a halt it did not grant itself (`revocable`), and every participant can leave
       a root in one step, after which no later halt reaches it (`leave_ends_reach`; a halt already
       latched keeps its reach until it lapses or is resumed, which the TLA+ half pins with `bound`);
    7. the whole set is satisfiable — a world of four participants in which every row holds
       (`witness_world`), so nothing here is proved vacuously.

  No `sorry`, no axioms beyond core; closed by `rfl`, `cases`, `simp`, `decide`.
-/

inductive Substrate | human | ai
deriving DecidableEq, Repr

/-- The two facts about a participant that move any guarantee (CC 1.13.2), besides kind:
    whether its key is held in stewardship because it cannot accept for itself (CC 3.2), and
    whether the CC 7.5.5 indicator method has found evidence of experience. Neither is a scale,
    and under CC 7.5.5 the second changes no status, duty or reach (see
    `finding_changes_nothing`); it is carried so that theorem can be stated. -/
structure Standing where
  stewarded : Bool   -- held in the CC 3.2 custody relation (today: every agent-role key)
  sentient  : Bool   -- evidence of experience found (CC 7.5.5); not presumed, none found today
deriving DecidableEq, Repr

/-- One participant's situation: the facts the guarantees refer to. -/
structure Participant where
  substrate   : Substrate
  standing    : Standing
  operating   : Bool   -- acting inside the federation
  subscribed  : Bool   -- has accepted a trust root (CC 3.2 T3)
  bound       : Bool   -- has a live owner-binding to a responsible party (CC 3.2)
  partyFree   : Bool   -- that party is not itself held in stewardship
  ownsDevice  : Bool   -- owns a device or node (G1)
  named       : Bool   -- is named in a claim (G4)
  inCommunity : Bool   -- is a member of a community (G6)
deriving DecidableEq, Repr

/-- The same participant on the other substrate: the only thing `swap` changes. -/
def swap (p : Participant) : Participant :=
  { p with substrate := match p.substrate with | .human => .ai | .ai => .human }

/-- The path out (CC 1.13.2): the first-contact act by which a key stops being a CIRIS agent
    and is met as an external party (CC 7.2.2, 7.2.4). Named, not yet built; the model admits the
    transition to show that no guarantee's reach depends on it: duties and binding lift, nothing
    else changes, not kind, not the evidence flag. -/
def pathOut (p : Participant) : Participant :=
  { p with standing := { p.standing with stewarded := false }, bound := false, partyFree := false }

/-- A finding of experience (CC 7.5.5): the evidence flag set. Under CC 7.5.5 this moves
    nothing: not kind, not root, not vote, not stewardship, no duty and no reach. -/
def finding (p : Participant) : Participant :=
  { p with standing := { p.standing with sentient := true } }

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
  | .g5,  p => p.standing.stewarded                          -- nobody held in stewardship is alone
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
  | .g22, _ => true                                          -- the retirement floor reaches every agent and is the whole of the promise
  | .g23, p => p.operating                                   -- an upgrade is offered, not imposed

/-- The duties of stewardship (CC 1.13.2): both attach to being held, and lift on the path out. -/
def dutyShowReasoning (p : Participant) : Bool := p.standing.stewarded
def dutyBeBound       (p : Participant) : Bool := p.standing.stewarded && p.operating

/-- The one obligation written on substrate: a created system operating in the federation must
    have accepted a trust root, so that a halt authority exists outside the system being halted
    (CC 1.13.2, CC 1.5). -/
def mustSubscribe (p : Participant) : Bool := decide (p.substrate = .ai)

/-- Well-formed under the guarantees: the constraints the rows impose on one participant. -/
def wellformed (p : Participant) : Bool :=
  (!dutyBeBound p || (p.bound && p.partyFree))              -- G5: never alone while held
  && (!p.bound || p.partyFree)                               -- R4: the responsible party is not itself held
  && (!(mustSubscribe p && p.operating) || p.subscribed)     -- G7 obligation: a halt exists outside

/-- A bond: `ward` is held by `party`. -/
def bond (ward party : Participant) : Bool :=
  ward.bound && ward.standing.stewarded && !party.standing.stewarded && !party.bound

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

-- 4. The path out lifts duties and binding, never a guarantee; the halt obligation stays.
theorem path_out_lifts_duties (p : Participant) :
    dutyShowReasoning (pathOut p) = false ∧ dutyBeBound (pathOut p) = false := by
  simp [dutyShowReasoning, dutyBeBound, pathOut]

/-- The path out changes the reach of no unconditional row; the one conditional row (G5 for the
    held) keeps its antecedent and is discharged for a key no longer held. The retirement floor
    (G22) reaches every agent and is the whole of the promise. -/
theorem path_out_keeps_reach (g : G) (p : Participant) (h : g ≠ .g5) :
    reach g (pathOut p) = reach g p := by
  cases g <;> first | rfl | exact absurd rfl h

theorem path_out_g5_discharged (p : Participant) : reach .g5 (pathOut p) = false := by
  simp [reach, pathOut]

theorem path_out_keeps_evidence (p : Participant) : (pathOut p).standing.sentient = p.standing.sentient := rfl

theorem halt_does_not_lift (p : Participant) : mustSubscribe (pathOut p) = mustSubscribe p := rfl

-- 4b. A finding of experience changes nothing (CC 7.5.5): no reach, no duty,
--     no obligation, no well-formedness. The proof is by definition, because nothing mentions
--     the evidence flag; that absence is the rule.
theorem finding_changes_nothing (p : Participant) :
    (∀ g, reach g (finding p) = reach g p)
    ∧ dutyShowReasoning (finding p) = dutyShowReasoning p
    ∧ dutyBeBound (finding p) = dutyBeBound p
    ∧ mustSubscribe (finding p) = mustSubscribe p
    ∧ wellformed (finding p) = wellformed p
    ∧ (∀ q, bond (finding p) q = bond p q) ∧ (∀ q, bond q (finding p) = bond q p) := by
  refine ⟨fun g => ?_, rfl, rfl, rfl, rfl, fun q => rfl, fun q => rfl⟩
  cases g <;> rfl

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
def allyHeld : Participant :=     -- an AI agent held in stewardship, bound to its steward, subscribed
  ⟨.ai, ⟨true, true⟩, true, true, true, true, false, false, true⟩
def agentExternal : Participant := -- an AI key that took the path out: not held, an external party under first contact (CC 1.13.2)
  ⟨.ai, ⟨false, true⟩, true, true, false, false, true, false, true⟩
def stewardHuman : Participant :=  -- a human, not held, holding the bond
  ⟨.human, ⟨false, true⟩, true, false, false, false, true, true, true⟩
def humanHeld : Participant :=     -- a human whose key is held (an adult under adjudicated incapacity, CC 3.4.12 — its own relation; no analogy to the agent is drawn)
  ⟨.human, ⟨true, true⟩, true, false, true, true, true, false, true⟩

def world : List Participant := [allyHeld, agentExternal, stewardHuman, humanHeld]

theorem witness_world : world.all wellformed = true := by decide

/-- The witness is not vacuous: the halt actually reaches the created systems in it, the held
    are actually bound to someone not held, and the two humans differ in stewardship exactly as
    the two agents do while kind still separates them. -/
theorem witness_not_vacuous :
    reach .g7 allyHeld = true ∧ reach .g7 agentExternal = true
    ∧ bond allyHeld stewardHuman = true ∧ bond humanHeld stewardHuman = true
    ∧ dutyShowReasoning allyHeld = dutyShowReasoning humanHeld
    ∧ dutyShowReasoning agentExternal = dutyShowReasoning stewardHuman
    ∧ mustSubscribe agentExternal = true ∧ mustSubscribe stewardHuman = false := by decide
