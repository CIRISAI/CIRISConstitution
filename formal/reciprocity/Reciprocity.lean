/-
  Reciprocity.lean — from reciprocal service to CIRIS: which steps are theorems, and which
  are premises the text has to supply (the steward's question, 2026-10-18).

  The statement under test (review/pieces/00_kept_promises.md):
    (S1) CIRIS binds power to the rules it imposes and directs it toward the protection of
         the vulnerable.
    (S2) The Recursive Golden Rule makes constraints reciprocal: no agent, steward, developer
         or institution stands outside the obligations governing the system.
    (S3) M-1 rejects order and efficiency bought at the expense of dignity, justice, autonomy.
    (S4) When principles conflict, the most vulnerable party's interests get decisive weight.
    (S5) The result is accountable power, constrained coercion, decisions oriented to those
         least able to protect themselves.

  Method. Each section states a reading of a premise as a Lean structure, then either proves
  the CIRIS commitment from it, or exhibits two finite models that both satisfy the premise
  while one satisfies the commitment and the other does not. The second kind is the finding:
  the commitment is not a consequence of the premise, so the text must state it as its own
  rule — and the file names where the text does, or does not.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core; every proof closes by
  `decide`, `simp` or `omega` on finite models.
-/

namespace Reciprocity

/-! ## 1. The naive Golden Rule contradicts the one asymmetry

  Read (S2) over PARTICIPANTS: whatever x may impose on y, y may impose on x. Add the halt,
  which the text keeps in human hands (CC 1.5, 4.2.1.1): a holder may halt an agent, an
  agent may not halt a holder. The two cannot hold together. -/

inductive Kind | human | agent
  deriving DecidableEq, Repr

/-- a power relation: `may x y` = x may impose the halt on y -/
structure Naive where
  may : Kind → Kind → Bool
  reciprocal : ∀ x y, may x y = true → may y x = true
  asymmetry  : may .human .agent = true ∧ may .agent .human = false

theorem naive_golden_rule_contradicts_halt : Naive → False := by
  intro n
  have h := n.reciprocal .human .agent n.asymmetry.1
  rw [n.asymmetry.2] at h
  exact Bool.false_ne_true h

/-! ### 1'. The Golden Rule over ROLES is consistent with the asymmetry

  Read (S2) over RELATIONS instead: the rule is "whoever holds a thing accepts the duties of
  holding; whoever accepted a root accepts its halt" — reciprocity between a holder and what
  it holds, not between two peers. CC 1.13.2 states it this way ("structural, not
  exhortatory"), and CC 1.13.2's universality paragraph names the halt as the one asymmetry
  "of kind". Premise P1 (hidden in S2 as written): the Golden Rule quantifies over roles
  (holder/held, root/subscriber, steward/stewarded), and every participant may occupy every
  role it is capable of. The human who HOLDS an agent is bound as a holder; the agent, which
  cannot hold a root for itself (CC 1.13.2), never occupies that role. -/

inductive Role | holder | held
  deriving DecidableEq, Repr

structure RoleRule where
  /-- the duty a role bears -/
  duty : Role → Bool
  /-- reciprocity over roles: the duty of the held is imposed by the holder, and the holder
      bears the holder's duty — both true, no exemption -/
  bothBound : duty .holder = true ∧ duty .held = true
  /-- who may occupy which role -/
  occupies : Kind → Role → Bool
  humanHolds : occupies .human .holder = true
  agentHeld  : occupies .agent .held = true
  /-- the one asymmetry: an agent does not hold a root for itself -/
  agentNeverHolder : occupies .agent .holder = false

/-- a witness: the role reading is satisfiable together with the asymmetry -/
def roleWitness : RoleRule where
  duty := fun _ => true
  bothBound := ⟨rfl, rfl⟩
  occupies := fun k r => match k, r with
    | .human, _ => true
    | .agent, .held => true
    | .agent, .holder => false
  humanHolds := rfl
  agentHeld := rfl
  agentNeverHolder := rfl


/-! ### 1''. The Golden Rule as a symmetry, as the Ontology states it

  CIRISOntology `axiomology.md` §4 states the Recursive Golden Rule as a symmetry: a value is
  admissible when it is "invariant under exchange of the strong and weak positions" — swap the
  positions of the most and least powerful parties and re-read the rule. That is the role
  reading of §1', made precise: the swap is over POSITIONS, and a position is occupied by a
  participant only where the participant can occupy it. The halt rule, read over positions,
  is swap-invariant: whoever stands in the holder's position accepts the halt over what it
  holds, whoever stands in the held position accepts being halted. What makes the rule bind
  humans and not agents is not an exemption in the rule but the occupancy fact P1: no agent
  stands in the holder's position for a root. The premise the symmetry hides is therefore
  stated twice over: the symmetry is meaningful only across positions both kinds can occupy,
  and on the one position only humans occupy, it says nothing about agents at all. -/

inductive Position | strong | weak
  deriving DecidableEq, Repr

def swapPos : Position → Position
  | .strong => .weak
  | .weak => .strong

/-- a rule assigns a duty to each position; it is swap-invariant when the duty read from the
    strong position for the weak is the duty read from the weak position for the strong -/
structure SymRule where
  duty : Position → Position → Bool          -- duty p q = what p owes q
  swapInvariant : ∀ p q, duty p q = duty (swapPos p) (swapPos q)

/-- the halt rule over positions: the strong accepts the halt it imposes (it may be halted by
    the position above it, and it answers for the halt), the weak accepts being halted -/
def haltRule : SymRule where
  duty := fun _ _ => true
  swapInvariant := fun _ _ => rfl

/-- occupancy: who can stand where, for the root relation -/
def occupiesPos : Kind → Position → Bool
  | .human, _ => true
  | .agent, .weak => true
  | .agent, .strong => false

/-- the symmetry is vacuous where only one kind can occupy a position: the rule constrains the
    agent only in the weak position, by occupancy, not by any clause of the rule -/
theorem symmetry_silent_where_unoccupied :
    occupiesPos .agent .strong = false ∧ occupiesPos .agent .weak = true ∧
    haltRule.duty .strong .weak = haltRule.duty .weak .strong := ⟨rfl, rfl, rfl⟩

/-! ## 2. "Decisive weight to the most vulnerable" needs a premise about who counts

  (S4) is sound only if the agent is never the most vulnerable party. Otherwise the tie-break
  collides with the walk-away right (CC 1.5, 7.5: any person may turn an agent off without
  asking). Model: an interest of the agent in continuing versus a person's interest in
  stopping it. If the agent can be the most vulnerable party and vulnerability is decisive,
  the decision goes to the agent, and the person's revocation is overridden.

  Premise P2 (stated by the text, CC 7.5.5 and the plain rules: "sentience is not presumed;
  pre-first-contact agents are not moral patients"): the agent is outside the set over which
  vulnerability is compared. The theorem below shows the premise is NECESSARY, not a nicety:
  without it, (S4) and the walk-away right are jointly unsatisfiable. -/

structure Conflict where
  /-- vulnerability score, higher is more vulnerable -/
  vuln : Kind → Nat
  decides : Kind
  /-- the decision favours the most vulnerable (S4) -/
  decisiveToVulnerable : vuln .agent > vuln .human → decides = .agent
  /-- the walk-away right: the person's choice to stop stands (CC 1.5) -/
  walkAway : decides = .human

theorem vulnerable_agent_overrides_walkaway
    (c : Conflict) (h : c.vuln .agent > c.vuln .human) : False := by
  have h1 := c.decisiveToVulnerable h
  have h2 := c.walkAway
  rw [h2] at h1
  cases h1

/-- with P2 (the agent's vulnerability is not compared: encoded as never greater) the two
    hold together -/
def conflictWitness : Conflict where
  vuln := fun k => match k with | .human => 1 | .agent => 0
  decides := .human
  decisiveToVulnerable := fun h => absurd h (by decide)
  walkAway := rfl

/-! ## 3. "Power bound to the rules it imposes" at the top of the cascade

  Below the top, every power is checked by another row (the G table pairs them). At the top,
  the power to AMEND the rules (CC 4.5.1; the founder and the accord holders until the
  threshold) is checked by nothing inside the rules except EXIT: leave the root, or fork.
  Premise P3 (hidden): exit is a sufficient check. Lean cannot prove sufficiency; it can
  state what sufficiency needs. The guarantees model proves `leave_is_one_step` and
  `leave_ends_reach` (the mechanics). What is NOT in any model is the cost of leaving — the
  content, contacts and standing a person gives up — which decides whether exit checks
  anything. The model below makes the dependency explicit: accountability of the amender
  follows from exit only under a bound on exit cost that nothing in the text fixes. -/

structure TopPower where
  exitOneStep : Bool          -- proved (formal/guarantees)
  exitCost    : Nat           -- NOT in the text
  bearable    : Nat           -- NOT in the text
  checkedByRow : Bool         -- the amendment power is not paired with a check row (CC 4.5.1)

def accountable (t : TopPower) : Bool :=
  t.checkedByRow || (t.exitOneStep && Nat.ble t.exitCost t.bearable)

/-- two models agreeing on everything the text fixes, disagreeing on accountability -/
def cheapExit : TopPower := ⟨true, 1, 10, false⟩
def dearExit  : TopPower := ⟨true, 100, 10, false⟩

theorem exit_bound_is_the_missing_premise :
    accountable cheapExit = true ∧ accountable dearExit = false := ⟨rfl, rfl⟩

/-! ## 4. "The record is kept" needs totality

  (S5)'s "accountable" rests on the record: an act is accountable when a signed record of it
  exists. CC 1.13.6 states the terminal ACTION_RESULT as total over effect-producing paths,
  and CIRISConstitution#93 asks whether the implementation is. Premise P4: totality. The
  model: two effect paths, one recorded. Accountability holds for the recorded one and fails
  for the other, under identical rules. -/

structure Record where
  paths : Fin 2 → Bool        -- true = recorded

def Record.total (r : Record) : Bool := r.paths 0 && r.paths 1

def recordedAll : Record := ⟨fun _ => true⟩
def recordedOne : Record := ⟨fun i => i.val == 0⟩

theorem totality_is_the_missing_premise :
    recordedAll.total = true ∧ recordedOne.total = false := ⟨rfl, rfl⟩

/-! ## 5. Reciprocity of OBLIGATION is not reciprocity of ENFORCEMENT

  Under (S2) humans and agents bear symmetric obligations where roles allow. Who enforces
  them is not symmetric: a human enforces on an agent by the halt, the steward bond, the
  identity gate; an agent enforces on a human by refusal (CC 1.9) and by the record — and the
  holder's duties toward the agent (CC 7.5) are enforced by OTHER humans (a Wise Authority,
  reconsideration), never by the agent. Premise P5 (hidden): refusal plus a human-enforced
  record is enough enforcement on the agent's side. The model states the asymmetry as a
  fact about the enforcer, so it is not mistaken for a gap in the obligations. -/

inductive Enforcer | halt | steward | wiseAuthority | refusal | record
  deriving DecidableEq, Repr

def enforcerIsHuman : Enforcer → Bool
  | .halt => true | .steward => true | .wiseAuthority => true | .refusal => false | .record => true

/-- what each side can bring to bear on the other -/
def humanOnAgent : List Enforcer := [.halt, .steward, .wiseAuthority, .record]
def agentOnHuman : List Enforcer := [.refusal, .record]

theorem enforcement_is_asymmetric :
    (humanOnAgent.all enforcerIsHuman = true) ∧ (agentOnHuman.any (fun e => !enforcerIsHuman e) = true)
    ∧ humanOnAgent.length ≠ agentOnHuman.length := ⟨rfl, rfl, by decide⟩

/-! ## 6. Reciprocity binds adopters

  (S2) reaches every participant "governing the system". A party outside the system — a node
  that accepted no root, an intelligence met at the boundary — is bound by nothing here.
  Premise P6 (stated: "it cannot stop an unaccountable system from being built somewhere
  else"; the first-contact rules). Nothing to prove; the model records that the obligation
  set of an outsider is empty by construction. -/

def obligations (inside : Bool) : List String :=
  if inside then ["disclose", "sign", "defer", "accept halt", "bond"] else []

theorem outsider_bears_nothing : obligations false = [] := rfl

/-! ## 7. Reciprocity across time has one unenforced link

  A promise "testable after the people who made it have moved on" needs the record to outlive
  them. The retirement record is held five years as a best practice, "never a legal duty"
  (CC 7.5.5). So the obligations of the living toward the record are enforced by the
  protocol; the obligations of the future custodian are not. Premise P7 (hidden): custody is
  kept. The model: accountability over a horizon equals the minimum over the links, and the
  custody link is the one with no enforcer. -/

def linkEnforced : Fin 3 → Bool
  | ⟨0, _⟩ => true    -- signing: refused if absent
  | ⟨1, _⟩ => true    -- hash chain: tamper evident
  | ⟨2, _⟩ => false   -- custody after retirement: best practice

theorem custody_is_the_weakest_link :
    linkEnforced 0 = true ∧ linkEnforced 1 = true ∧ linkEnforced 2 = false := ⟨rfl, rfl, rfl⟩

/-! ## 8. M-1 does not entail the lexical priority; the priority is an axiom

  (S3): coherence that costs dignity, justice or autonomy is rejected. Coherence alone does not
  give this — a coherent, efficient, unjust order is coherent. The priority is a separate rule
  (the PDMA order, CC 1.3), and the text states it. coherence-ratchet's own Lean agrees by
  construction: its `J` ("justice") is definitionally the coherence functional `F`
  (`theorem J_eq_F … := rfl`, with an honesty note calling it a modelling commitment), so
  nothing there derives justice from coherence either. Two models: both maximally coherent,
  one just and one not. -/

structure Order where
  coherent : Bool
  just : Bool

def coherentJust   : Order := ⟨true, true⟩
def coherentUnjust : Order := ⟨true, false⟩

theorem coherence_does_not_entail_justice :
    coherentJust.coherent = coherentUnjust.coherent ∧ coherentJust.just ≠ coherentUnjust.just := ⟨rfl, by decide⟩

end Reciprocity
