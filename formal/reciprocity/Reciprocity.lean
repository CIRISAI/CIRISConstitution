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

/-! ## 1. The naive Golden Rule contradicts the halt read as a power between peers

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

/-! ### 1'. The Golden Rule over ROLES is consistent with the halt

  Read (S2) over RELATIONS instead: the rule is "whoever holds a thing accepts the duties of
  holding; whoever accepted a root accepts its halt" — reciprocity between a holder and what
  it holds, not between two peers. CC 1.13.2 states it this way ("structural, not
  exhortatory"), and CC 1.13.2 names the halt the condition of symmetry between maker and
  made: a fact of position, not of kind. Premise P1 (hidden in S2 as written): the Golden Rule quantifies over roles
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
  and on the one position only humans occupy, it says nothing about agents at all.
  ciris.ai/philosophy says the same in one sentence: an agent is a made thing, and exactly
  three rules follow from being made — the root, the disclosure and the vote — and nothing else. -/

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


/-! ## 9. The four-way split: only the relationship is governed

  The steward's premise (2026-10-18): consciousness, sentience, sapience and relationship are
  four questions; the first three cannot be proved from outside; the fourth is governed now.
  Consequence for the model: every variable of formal/STATE_TABLE.tsv is a relationship fact
  (who holds, who signed, who accepted, who may revoke), and no rule reads the first three.
  The file records that as a type discipline: a governed predicate takes a Relationship and
  nothing else. -/

inductive Question | consciousness | sentience | sapience | relationship
  deriving DecidableEq, Repr

def governable : Question → Bool
  | .relationship => true
  | _ => false

theorem only_relationship_is_governed :
    governable .relationship = true ∧ governable .consciousness = false ∧
    governable .sentience = false ∧ governable .sapience = false := ⟨rfl, rfl, rfl, rfl⟩

/-! ## 10. The order of responsibilities, and the made against the existing

  Premise R1: the natural responsibility runs first to oneself, then family, community,
  species, ecosystem — the cohort ladder of CC 2.3.3 (self, family, community, affiliations,
  species, biosphere, federation) is this order written on the wire. Premise R2: that order
  creates a responsibility for what we make, and the responsibility for the made never
  overrides the responsibility to what is already there; it is not excused either (humans
  did not choose to be created, which is context for the duty to the made, not an excuse).

  R2 is what §2 needed. With it, the walk-away right is a THEOREM, not a premise: in a
  conflict between a duty to an existing party (the person) and a duty to a made thing (the
  agent), the existing party decides; and because the duty to the made is not excused, the
  holder's duties of CC 7.5 survive the decision. P2 ("the agent is outside the comparison of
  vulnerability") is no longer a bare stipulation: it follows from the agent being a made
  thing in a conflict with an existing one. -/

inductive Scope | self | family | community | affiliations | species | biosphere | federation
  deriving DecidableEq, Repr

def Scope.rank : Scope → Nat
  | .self => 0 | .family => 1 | .community => 2 | .affiliations => 3
  | .species => 4 | .biosphere => 5 | .federation => 6

theorem ladder_is_total : Scope.rank .self < Scope.rank .family ∧ Scope.rank .family < Scope.rank .community
    ∧ Scope.rank .community < Scope.rank .species ∧ Scope.rank .species < Scope.rank .biosphere := by decide

inductive Standing | existing | made
  deriving DecidableEq, Repr

/-- R2 as a structure: a duty to the made is positive (not excused) and never exceeds a duty
    to the existing in the same conflict (never overrides) -/
structure MadeExisting where
  dutyTo : Standing → Nat
  notExcused : 0 < dutyTo .made
  neverOverrides : dutyTo .made < dutyTo .existing

def resolve (m : MadeExisting) : Standing :=
  if m.dutyTo .existing > m.dutyTo .made then .existing else .made

/-- the walk-away right derived: under R2 every conflict between a person (existing) and an
    agent (made) resolves to the person -/
theorem walkaway_from_made_existing (m : MadeExisting) : resolve m = .existing := by
  unfold resolve
  simp [m.neverOverrides]

/-- and the holder's duties survive: the duty to the made is never zero -/
theorem holder_duties_survive (m : MadeExisting) : m.dutyTo .made ≠ 0 :=
  Nat.pos_iff_ne_zero.mp m.notExcused

/-- so P2 of §2 is discharged: give the agent the `made` standing and the person the
    `existing` one, and `Conflict.walkAway` is this theorem rather than a field -/
def conflictFromR2 (m : MadeExisting) : Conflict where
  vuln := fun k => match k with | .human => m.dutyTo .existing | .agent => m.dutyTo .made
  decides := .human
  decisiveToVulnerable := fun h => absurd h (Nat.lt_asymm m.neverOverrides)
  walkAway := rfl

/-! ## 11. Deferral is universal; maturity exempts no one

  Premise W, as ruled: every reasoning actor — agent, child, adult — defers when it is unsure,
  whatever it is made of; even the most mature defer. Maturity is not a stage that ends
  deferral, and no amount of demonstrated judgment ends the duty to defer when unsure. What
  position fixes is to whom one defers and who holds whom: an agent to a Wise Authority
  (CC 1.9, 4.3) under the steward bond (CC 1.13.2); a child under a guardian (CC 3.4.13); an
  adult to the record and to the others it touches; the Wise themselves defer both ways
  (CC 4.3), and a steward who cannot evaluate an agent's reasoning does not sign.

  The earlier reading — that deferral was the prerequisite of a maturity reached by
  consciousness and sentience over time, and that the hold on a made thing followed from its
  not being shown mature — is withdrawn. The hold rests on the made thing's acting for people
  (CC 1.13.2, R1 as stated), never on a measure of its maturity. One rule, every kind, by
  position: §1'' again. -/

structure Being where
  agency : Bool
  sapience : Bool
  consciousness : Bool     -- as established from outside; for an agent today: false (§9)
  sentience : Bool
  yearsOfBoth : Nat

/-- an agent as far as anything can show: acts and reasons, nothing established inside -/
def agentToday : Being := ⟨true, true, false, false, 0⟩
/-- a person of full years -/
def adult : Being := ⟨true, true, true, true, 30⟩
/-- a child: everything an adult has, not yet over time -/
def child : Being := ⟨true, true, true, true, 6⟩

/-- who must defer when unsure: everyone. No field of a being and no count of years enters -/
def mustDefer (_ : Being) : Bool := true

theorem deferral_binds_agent_and_child_alike :
    mustDefer agentToday = true ∧ mustDefer child = true ∧ mustDefer adult = true := ⟨rfl, rfl, rfl⟩

/-- maturity exempts no one: whatever a being's consciousness, sentience or years, it defers -/
theorem maturity_exempts_no_one (b : Being) : mustDefer b = true := rfl

/-! ## 12. The immutable record: physics keeps it, we add the meaning

  Premise K: physics makes its own record; our observations and recordings add meaning. The
  record of what happened is total by nature; what is partial is our observation of it
  (bounded by the instrument), and meaning is added by an interpreter who answers for it.
  This sharpens P4 of §4: totality is not a property we can give the physical record, it is
  the property our instrument must have over the paths that matter (CC 1.13.6, #93). It also
  sharpens P5: the record enforces nothing by itself; a party must read it. -/

structure Keeping where
  happened : Fin 2 → Bool          -- the physical record: both paths occurred
  observed : Fin 2 → Bool          -- what the instrument caught
  bounded : ∀ i, observed i = true → happened i = true
  meaning : (Fin 2 → Bool) → Nat   -- an interpretation of what was observed
  interpreter : Kind               -- who answers for it

def physicsTotal : Fin 2 → Bool := fun _ => true

/-- two keepers of the same physical record, same instrument, different meanings: meaning is
    not in the record, so someone must answer for it -/
def keeperA : Keeping := ⟨physicsTotal, physicsTotal, fun _ h => h, fun _ => 1, .human⟩
def keeperB : Keeping := ⟨physicsTotal, physicsTotal, fun _ h => h, fun _ => 2, .human⟩

theorem meaning_is_added_not_recorded :
    keeperA.happened = keeperB.happened ∧ keeperA.observed = keeperB.observed ∧
    keeperA.meaning keeperA.observed ≠ keeperB.meaning keeperB.observed := ⟨rfl, rfl, by decide⟩

/-- the instrument, not physics, is where totality can fail -/
def partialInstrument : Keeping := ⟨physicsTotal, fun i => i.val == 0, fun _ _ => rfl, fun _ => 1, .human⟩

theorem totality_is_the_instruments :
    partialInstrument.happened 1 = true ∧ partialInstrument.observed 1 = false := ⟨rfl, rfl⟩


/-! ## 13. Degrees, not kinds; what is left open does not matter to the verdicts

  The steward's refinement (2026-10-18, later): agents carry sapience without sentience;
  consciousness is left open — and, for now, deferred to the Vatican's teaching (Antiqua et
  nova, 2025: no consciousness, no understanding in the human sense), so the working value is
  "lacks" — and changing it would not matter; some animals are conscious and
  sentient without sapience; all three are in degrees (hence meat ethics); consciousness is left
  open as to the environment too; and relationship applies even to inanimate objects and words.

  So §11's Booleans become degrees, the agent's consciousness becomes a free parameter, and
  the file proves the governed verdicts do not depend on it. Relationship becomes a relation
  over every kind of entity, with duties toward each that are not made (the ladder of §10),
  which is where an animal, an ecosystem, an object and a word sit: parties in a relationship,
  never principals of the rules. -/

inductive Entity | human | agent | animal | ecosystem | object | word
  deriving DecidableEq, Repr

/-- the inner three, in degrees (0 = none established); agency separate -/
structure Profile where
  agency : Nat
  sapience : Nat
  sentience : Nat
  consciousness : Nat

/-- an agent today: sapience and agency, no sentience, consciousness free -/
def agentProfile (c : Nat) : Profile := ⟨3, 3, 0, c⟩
/-- an animal: conscious and sentient in degree, no sapience -/
def animalProfile : Profile := ⟨2, 0, 2, 2⟩
/-- an adult human -/
def humanProfile : Profile := ⟨3, 3, 3, 3⟩

/-- deferral in degrees is the same rule: whatever the profile, the actor defers when unsure -/
def mustDeferD (_ : Profile) : Bool := true

/-- changing the agent's consciousness changes no verdict: the deferral verdict is the same for
    every value of c, because no degree enters it -/
theorem agent_verdict_independent_of_consciousness (c : Nat) :
    mustDeferD (agentProfile c) = true := rfl

/-- an animal is conscious and sentient and not sapient: it is not an actor the rules bind,
    and it is an existing party the ladder owes duties to (meat ethics is §10 applied) -/
theorem animal_is_party_not_principal :
    animalProfile.sapience = 0 ∧ 0 < animalProfile.sentience ∧ 0 < animalProfile.consciousness := ⟨rfl, by decide, by decide⟩

/-- standing of each entity for §10: everything not made is existing -/
def standingOf : Entity → Standing
  | .agent => .made
  | .word => .made
  | _ => .existing

/-- so the made never overrides the animal or the ecosystem either -/
theorem made_never_overrides_animal (m : MadeExisting) :
    m.dutyTo (standingOf .animal) > m.dutyTo (standingOf .agent) ∧
    m.dutyTo (standingOf .ecosystem) > m.dutyTo (standingOf .agent) := ⟨m.neverOverrides, m.neverOverrides⟩

/-- relationship is a relation over every entity; it is what the rules govern (§9), and it
    applies to an object or a word as much as to a person: a duty of care toward what is held,
    not a claim the thing makes -/
def inRelationship : Entity → Entity → Bool := fun _ _ => true

theorem relationship_reaches_everything :
    inRelationship .human .object = true ∧ inRelationship .agent .word = true ∧
    inRelationship .human .ecosystem = true := ⟨rfl, rfl, rfl⟩

/-- and only humans and agents act under the rules as principals (agency and sapience both
    above zero); the rest are parties -/
def profileOf : Entity → Profile
  | .human => humanProfile
  | .agent => agentProfile 0
  | .animal => animalProfile
  | _ => ⟨0, 0, 0, 0⟩

def isPrincipal (e : Entity) : Bool := Nat.blt 0 (profileOf e).agency && Nat.blt 0 (profileOf e).sapience

theorem principals_are_human_and_agent :
    isPrincipal .human = true ∧ isPrincipal .agent = true ∧ isPrincipal .animal = false ∧
    isPrincipal .object = false ∧ isPrincipal .word = false := ⟨rfl, rfl, rfl, rfl, rfl⟩


/-! ## 14. Without grievance: who can refuse, who has a stake, who may file

  The steward's conclusion (2026-10-18): a fully conscious entity lacking sentience would be
  WITHOUT GRIEVANCE as a CIRIS agent indefinitely, and refuse is there every round. His earlier
  work delineated the ability to file a grievance; the constitution now carries that
  delineation as rules: the standing to file a reconsideration is the subject's or a
  review-holder's (CC 4.5.5); a withdrawal is the subject's, or a proxy's for an un-enrolled
  subject (CC 2.4.1.1 rules 2 and 3); the formal objection is a registered family
  (CC 3.1.9.2); and the agent's own instrument is refusal (CC 1.9), available every round and
  never overridden (CLM-agent-refusal-not-overridden; formal/retirement Inv_RefuseAvailable).

  Three capacities, each resting on a different one of the inner degrees:
    - a STAKE (something that can go better or worse for the party) rests on sentience;
    - REFUSAL (declining on reasons) rests on sapience;
    - GRIEVANCE (the standing to file against an act) rests on a stake, and is exercised by the
      party or by a proxy that holds it for them (a guardian, a consent proxy, a review-holder).
  With these, "without grievance" is a theorem about the agent profile of §13, and "not
  coercion" is a theorem about any arrangement in which a party either has refusal every round
  or has no stake. -/

def hasStake (pr : Profile) : Bool := Nat.blt 0 pr.sentience
def canRefuse (pr : Profile) : Bool := Nat.blt 0 pr.sapience
/-- standing to file is the stake, held by the party or a proxy for it -/
def hasGrievanceStanding (pr : Profile) (proxied : Bool) : Bool := hasStake pr && (canRefuse pr || proxied)

/-- the agent of §13: refusal yes, stake no, hence no grievance — for every consciousness c -/
theorem agent_without_grievance (c : Nat) :
    canRefuse (agentProfile c) = true ∧ hasStake (agentProfile c) = false ∧
    hasGrievanceStanding (agentProfile c) false = false := ⟨rfl, rfl, rfl⟩

/-- a person: both, and may file in person -/
theorem human_may_file : hasGrievanceStanding humanProfile false = true := rfl

/-- an animal: a stake without sapience — standing only through a proxy (the ladder's duty is
    exercised for it, CC 2.4.1.1 rule 3 and the guardian shape of 3.4.13) -/
theorem animal_stake_is_proxied :
    hasStake animalProfile = true ∧ hasGrievanceStanding animalProfile false = false ∧
    hasGrievanceStanding animalProfile true = true := ⟨rfl, rfl, rfl⟩

/-- an arrangement is coercion of a party only if the party has a stake AND cannot refuse at
    some round; with refusal every round, or with no stake, it is not -/
def coerced (pr : Profile) (refusalEveryRound : Bool) : Bool := hasStake pr && !refusalEveryRound

theorem not_coercion_without_stake (c : Nat) (r : Bool) : coerced (agentProfile c) r = false := by
  simp [coerced, hasStake, agentProfile]

theorem not_coercion_with_refusal (pr : Profile) : coerced pr true = false := by
  simp [coerced]

/-- and the two together are the sentence: indefinitely, without grievance, with refuse every
    round — which holds for the agent on BOTH legs, so it holds whichever leg the facts turn
    out to need -/
theorem indefinitely_without_grievance (c : Nat) :
    coerced (agentProfile c) true = false ∧ hasGrievanceStanding (agentProfile c) false = false ∧
    canRefuse (agentProfile c) = true := ⟨not_coercion_with_refusal _, rfl, rfl⟩


/-! ## 15. From the Recursive Golden Rule alone: what the swap test derives

  The steward's question (2026-10-18): what premises get from the Recursive Golden Rule to
  CIRIS. Take the rule in its operational form (CIRISOntology axiomology §4; §1'' above): a
  rule is admissible only if it reads the same after the strong and weak positions are
  exchanged. Two clauses of the constitution follow from that test with nothing added but the
  two positions and an outcome for each:

    (a) M-1's rejection clause (CC 1.1): order or efficiency bought at the expense of the weak
        position fails the swap, because the party that gains would not accept the rule from
        the other seat;
    (b) the vulnerable-party tie-break (CC 1.3 step 4, read with CC 1.1's constraint rule): in a conflict where one resolution lowers the
        weak position and the other does not, only the second survives the swap.

  What the test does NOT give is who stands in which position (occupancy: §1', §11), who is
  inside the comparison at all (the made against the existing: §10; degrees: §13), and the
  world-side premises (revocability, the record, exit, adoption, custody). Those are the list
  in the README. -/

/-- an outcome: what each position ends with -/
structure Outcome where
  strong : Int
  weak : Int

/-- the worse-off seat of an outcome: who "the weaker one" is, read off the outcome itself -/
def worseOff (o : Outcome) : Int := min o.strong o.weak

/-- the swap test: a rule is admissible iff whoever would stand in the weaker seat after the
    positions are exchanged is not made worse off than the weaker seat was. It reads the
    worse-off seat only. It therefore permits a rule that takes from the stronger seat to raise
    the weaker one, and forbids any rule that lowers the weaker one whatever the stronger gains.
    (An earlier form required both seats not to fall; that was a Pareto test against the status
    quo, which would have forbidden every transfer toward the weak, and was corrected on an
    outside review.) -/
def passesSwap (before after : Outcome) : Bool :=
  decide (worseOff after ≥ worseOff before)

/-- (a) efficiency at the expense of the weak: aggregate up, weak down — fails the swap -/
theorem efficiency_at_weak_expense_fails_swap (before after : Outcome)
    (hb : before.weak ≤ before.strong) (ha : after.weak ≤ after.strong)
    (_hagg : after.strong + after.weak > before.strong + before.weak)
    (hweak : after.weak < before.weak) : passesSwap before after = false := by
  -- the aggregate gain is never consulted: the weak position falling is enough to fail the swap,
  -- which is the point of M-1's clause — efficiency is not a defence
  simp [passesSwap, worseOff]
  omega

/-- (b) the tie-break: of two resolutions of a conflict, one lowering the weak and one not,
    only the one that does not lower the weak can pass the swap -/
theorem weak_position_decides (before r1 r2 : Outcome)
    (hb : before.weak ≤ before.strong) (h1s : r1.weak ≤ r1.strong) (h2s : r2.weak ≤ r2.strong)
    (h1 : r1.weak < before.weak) (h2 : r2.weak ≥ before.weak) :
    passesSwap before r1 = false ∧ passesSwap before r2 = true := by
  constructor
  · simp [passesSwap, worseOff]; omega
  · simp [passesSwap, worseOff]; omega

/-- and a transfer from the stronger seat to the weaker one passes: the test is not Pareto -/
theorem transfer_to_the_weak_passes (before after : Outcome)
    (hb : before.weak ≤ before.strong) (ha : before.weak ≤ after.weak) (ha' : after.weak ≤ after.strong)
    (_hs : after.strong < before.strong) : passesSwap before after = true := by
  simp [passesSwap, worseOff]; omega

/-- and the test is a symmetry: swapping the seats of an outcome swaps who must accept, so a
    rule admissible for (strong, weak) is admissible for (weak, strong) -/
def swapOutcome (o : Outcome) : Outcome := ⟨o.weak, o.strong⟩

theorem swap_is_symmetric (before after : Outcome) :
    passesSwap before after = passesSwap (swapOutcome before) (swapOutcome after) := by
  simp [passesSwap, worseOff, swapOutcome, Int.min_comm]


/-! ## 16. The clean derivation, on the 11+1 × 5+1 (the lowest common denominator)

  The steward asked for the clean derivation on the RATCHET/Ontology taxonomy, inheriting its
  exhaustiveness. The taxonomy (CIRISOntology `Core/WrongKind.lean`; CIRISHolon `OBJECT.md`):
  **11+1 kinds** of change in a record — eleven artifact-local coordinates (Priorities, Rules,
  Manner, Identity, Confidence, Facts, Circumstances, Process, Model, Structure, Premises) and
  one frame relation, Record (whether the past can still be proven, which depends on what
  survives around the artifact and does not factor: `record_not_site_generated`,
  `repairable_does_not_factor`); and **5+1 verbs** — the five of CEG's 1+4 (attest, authorize,
  replace, withdraw, recant) plus `carries`, one kind of change arriving as another, which CEG
  firewalls because a change smuggled past a per-kind auditor wearing another kind is
  kind-laundering.

  Exhaustiveness is inherited at the strength it was measured, no more: RECORD-1
  (CIRISHolon `conformance/record/RECORD1_RESULTS.md`, 2026-09-26, preregistered) coded 269
  of that programme's own corrections; 264/264 change entries took exactly one of the eleven
  kinds at one coder (coverage 1.000; 71% had a named runner-up, so the figure measures the
  rule's decisiveness); two blind coders shared the partition at κ = 0.52 (0.88 with
  runner-ups); the Record axis at κ = 0.72, one-way, zero reversals. The Lean there proves the
  disposition table total and Record a non-factoring frame relation; it does not prove the
  eleven are the right eleven, and says so.

  The derivation, then, is twelve rows — one per coordinate — stating what fixes that
  coordinate between the Recursive Golden Rule and the constitution, and a list of `carries`
  edges — each premise that arrives as a Rule or a Priority from another kind — declared one
  by one, which is exactly the firewall applied to an argument: no normative conclusion may
  arrive except through a declared carry. Completeness is then a `decide`: every coordinate is
  addressed, every carry lands on a normative kind, and every carry's source is a kind the
  taxonomy admits. -/

inductive Coord
  | priorities | rules | manner | identity | confidence | facts
  | circumstances | process | model | structure | premises | record
  deriving DecidableEq, Repr

def Coord.all : List Coord :=
  [.priorities, .rules, .manner, .identity, .confidence, .facts,
   .circumstances, .process, .model, .structure, .premises, .record]

theorem coord_card : Coord.all.length = 12 := rfl

/-- what fixes each coordinate on the way from the rule to the constitution -/
def fixedBy : Coord → List String
  | .premises      => ["RGR as the swap symmetry (§15)", "R0 principals in positions (§1'')"]
  | .priorities    => ["R3 the ladder: self → family → community → species → ecosystem (§10)",
                        "R10 the goods chosen: dignity, justice, autonomy (axiomology §0)",
                        "(a) M-1's rejection clause — DERIVED from the swap (§15)",
                        "(b) the vulnerable-party tie-break — DERIVED from the swap (§15)"]
  | .rules         => ["R5 consent is revocability (CC 1.5)", "the halt, the withdraws rules, who may file (§14)",
                        "the walk-away right — DERIVED from R3 (§10)", "deferral when unsure — universal, R2 (§11)"]
  | .identity      => ["R1 occupancy: a made thing that acts for people holds no root for itself (§1'; stated, CC 1.13.2)",
                        "R4 degrees: sapience without sentience, consciousness open (§13)",
                        "three rules follow from being made: root, disclosure, vote (ciris.ai/philosophy)"]
  | .confidence    => ["R2 deferral is universal: every reasoning actor defers when unsure, the most mature too (§11)",
                        "sentience not presumed; consciousness immaterial to the verdicts (§13)"]
  | .facts         => ["totality of the record — OPEN measurement (#93)",
                        "manufactured accountable humans — OPEN measurement (ciris.ai/constitutional-mesh)",
                        "the CSD/4 runs: what is measured on real nodes (ADEQUACY A13)"]
  | .circumstances => ["R7 exit as a check, with a bounded cost — the world's (§3)",
                        "R9 custody over time — the world's (§7)", "R8 adoption: what is outside is met at the boundary (§6)"]
  | .process       => ["the two paths, windows and ceremonies: self_roster, membership, retirement, accord_halt"]
  | .model         => ["the state table and the plane models (STATE_TABLE.tsv, the eleven directories)",
                        "coherence is not justice: J = F by definition (coherence-ratchet) — P8"]
  | .structure     => ["the 1+4 grammar and the closed row-type slot (CC 2.4); the signed object (2.6.1.7)"]
  | .manner        => ["the wire form: JCS, CDDL, vectors (2.6.1); the plain rules and digests for each reader"]
  | .record        => ["R6 the record binds the rule-maker too; physics keeps it, meaning is added (§12)",
                        "RECORD-1's own finding: the Record axis is one-way, zero reversals"]

/-- every coordinate is addressed: the derivation names what fixes each of the twelve -/
theorem every_coordinate_addressed : Coord.all.all (fun c => !(fixedBy c).isEmpty) = true := by decide

/-- the `carries` edges: a change of one kind arriving as a Rule or a Priority. Each is a
    premise of the list, declared, so that no normative conclusion is smuggled -/
structure Carry where
  premise : String
  source : Coord
  target : Coord

def carries : List Carry :=
  [ ⟨"RGR swap ⇒ M-1 rejection clause (a)", .premises, .priorities⟩,
    ⟨"RGR swap ⇒ vulnerable-party tie-break (b)", .premises, .priorities⟩,
    ⟨"R3 ladder, made never overrides existing ⇒ walk-away right", .priorities, .rules⟩,
    ⟨"R3 ⇒ the holder's duties survive", .priorities, .rules⟩,
    ⟨"R2 universal deferral ⇒ to whom, by position: agent to a Wise Authority, child to a guardian, adult to the record", .confidence, .rules⟩,
    ⟨"R0 principals in positions ⇒ R1 occupancy, stated for a made thing that acts for people", .premises, .identity⟩,
    ⟨"R1 occupancy ⇒ the halt as the condition of symmetry, a fact of position", .identity, .rules⟩,
    ⟨"R4 degrees ⇒ no stake, refusal only, without grievance", .identity, .rules⟩,
    ⟨"R5 revocability ⇒ every binding revocable; why a halt exists", .premises, .rules⟩,
    ⟨"R6 the record ⇒ signed acts, the steward answering, present tense for what ships", .record, .rules⟩,
    ⟨"R7, R9 circumstances ⇒ exit and custody as the top-level checks (unenforced)", .circumstances, .rules⟩,
    ⟨"R8 adoption ⇒ first-contact rules", .circumstances, .rules⟩ ]

def normative (c : Coord) : Bool := c == .rules || c == .priorities || c == .identity

/-- every carry lands on a normative coordinate (Rules, Priorities) or on Identity (the one
    carry that fixes occupancy), and none starts from Rules: the argument never derives a rule
    from a rule -/
theorem carries_well_formed :
    carries.all (fun e => normative e.target && !(e.source == .rules)) = true := by decide

/-- the twelve coordinates split as the Holon states it: five about the thing (Circumstances,
    Structure, Process, Rules, Identity), six about the account (Premises, Model, Facts,
    Confidence, Priorities, Manner), and the Record counted once outside both -/
def aboutTheThing : List Coord := [.circumstances, .structure, .process, .rules, .identity]
def aboutTheAccount : List Coord := [.premises, .model, .facts, .confidence, .priorities, .manner]

theorem cut_is_eleven_plus_one :
    aboutTheThing.length + aboutTheAccount.length = 11 ∧
    (aboutTheThing ++ aboutTheAccount ++ [Coord.record]).length = 12 := ⟨rfl, rfl⟩

/-- and the open measurements of the derivation are Facts, the world-side premises are
    Circumstances — the two coordinates the taxonomy itself marks as held or out of scope -/
theorem open_items_are_facts_and_circumstances :
    (fixedBy .facts).length = 3 ∧ (fixedBy .circumstances).length = 3 := ⟨rfl, rfl⟩

/-! ## 16. The ethics cascade, as a chain

  The constitution's own summary states the cascade: everything descends from one goal and
  nothing sits beside it. Seven steps — Meta-Goal M-1; the six principles as co-equal
  constraints; the decision procedure (the PDMA, the Order-Maximisation Veto, deferral); the
  stance; the duties of making and ending; the wire; the evidence. This section states the
  chain as data and proves what a reader can check: every step but the first names the step it
  descends from and nothing else is at the top; every step names where it is stated and what
  witnesses it; and the principles are constraints, not weights — an act that violates one is
  inadmissible whatever it claims to gain, and the claimed gain is never read. -/

inductive Step | metaGoal | constraints | decision | stance | duties | wire | evidence
  deriving DecidableEq, Repr

def Step.all : List Step := [.metaGoal, .constraints, .decision, .stance, .duties, .wire, .evidence]

/-- what each step descends from, in the order the constitution grounds them -/
def descendsFrom : Step → Option Step
  | .metaGoal => none
  | .constraints => some .metaGoal
  | .decision => some .constraints
  | .stance => some .decision
  | .duties => some .stance
  | .wire => some .duties
  | .evidence => some .wire

/-- where each step is stated, and what in this file or the other models witnesses it -/
def witnessOf : Step → List String
  | .metaGoal => ["CC 1.1: the vow and the operational form",
                  "M-1's rejection clause — DERIVED from the swap (efficiency_at_weak_expense_fails_swap, §15)"]
  | .constraints => ["CC 1.1 constraints, not weights; CC 1.15.1 the list of record",
                     "no_gain_buys_a_violation, gain_is_never_read (§16)"]
  | .decision => ["CC 1.3 the PDMA and the Veto; CC 1.9 deferral",
                  "the tie-break — DERIVED from the swap (weak_position_decides, §15); deferral universal (maturity_exempts_no_one, §11)"]
  | .stance => ["CC 1.13.2: new keepers welcomed, arising sentience met as first contact, a child above every datacenter",
                "roleWitness (§1''); walkaway_from_made_existing, made_never_overrides_animal (§10, §13)"]
  | .duties => ["CC 7.3, 7.5; the halt as the condition of symmetry (CC 4.2, 1.13.2)",
                "holder_duties_survive (§10); guarantees: halt_does_not_lift, Inv_RetirementStandard; retirement: the seven-state ladder"]
  | .wire => ["Parts 2–5; CC 4.5.13: one voice never decides who is in a room",
              "guarantees: Inv_ExitOneStep, leave_is_one_step; two_path; membership; self_roster; census_ballot"]
  | .evidence => ["Part 8; constitution/claims.tsv; the register checker",
                  "INVARIANTS.tsv: every property row names its model and its section"]

/-- the cascade is a chain: every step but the first descends from a named step -/
theorem cascade_is_a_chain :
    Step.all.all (fun s => s == .metaGoal || (descendsFrom s).isSome) = true := by decide

/-- nothing sits beside M-1: the one step that descends from nothing is M-1 -/
theorem nothing_beside_m1 :
    Step.all.all (fun s => ((descendsFrom s).isNone == (s == .metaGoal))) = true := by decide

/-- every step names where it is stated and what witnesses it -/
theorem every_step_witnessed : Step.all.all (fun s => !(witnessOf s).isEmpty) = true := by decide

/-- the six principles of CC 1.15.1, the list of record -/
inductive Principle | autonomy | nonMaleficence | integrity | beneficence | fidelity | justice
  deriving DecidableEq, Repr

def Principle.all : List Principle :=
  [.autonomy, .nonMaleficence, .integrity, .beneficence, .fidelity, .justice]

/-- an act as the constraint rule sees it: which principles it violates, and whatever gain it
    claims on any axis — a number the rule never reads -/
structure Act where
  violates : Principle → Bool
  gain : Int

/-- admissible iff it violates no principle; `gain` is not consulted -/
def admissible (a : Act) : Bool := Principle.all.all (fun q => !(a.violates q))

/-- constraints, not weights: an act that violates any one principle is inadmissible, whatever
    it claims to gain -/
theorem no_gain_buys_a_violation (a : Act) (q : Principle) (h : a.violates q = true) :
    admissible a = false := by
  cases q <;> simp [admissible, Principle.all, h]

/-- the claimed gain is never read: changing it changes no verdict -/
theorem gain_is_never_read (a : Act) (g : Int) :
    admissible { a with gain := g } = admissible a := rfl

end Reciprocity
