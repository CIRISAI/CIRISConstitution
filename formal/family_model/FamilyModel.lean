/-!
# The family model against the 11+1 × 5+1 grammar

A scores family is one row of the v62 family model (CIRISConstitution#189, CIRISPersist#1130).
This file states the half of that row the grammar of CIRISOntology and RATCHET fixes: the eleven
kinds of change, the five verbs that are the five row types plus the sixth, carries, and the
Record as a relation rather than a twelfth kind. It proves the structural facts the manifest's
vendor gate will enforce, and it checks, by `decide` over the registry's own classification
(generated from `formal/derivation/family_kind_verb.tsv`), that every family fits its kind.

What is proved: a family's row factors into a change half and a reach half, and the kind
constrains only the change half (`fits_factors`); authorize appears only under Rules, Identity and
Process (`authorize_only_rules_identity_process`); nothing carries into Identity, the firewalled
cell (`identity_never_carried`); a family that maintains the Record keeps erasure at none or legal
hold and a byte-equal projection (`record_fixes_reach`); thing-or-account is a function of kind
(`side_of_kind`); and the registry fits (`registry_fits`).
-/

inductive Kind
  | priorities | rules | manner | identity | confidence | facts
  | circumstances | process | model | structure | premises
deriving DecidableEq, Repr

inductive Verb | attest | authorize | replace | withdraw | recant | carries
deriving DecidableEq, Repr

inductive Side | thing | account
deriving DecidableEq, Repr

inductive Erasure | dsar | purge | legalHold | none
deriving DecidableEq, Repr

inductive Rebuild | byteEqual | none
deriving DecidableEq, Repr

/-- Thing or account is a function of kind: the registry has no exception. -/
def side : Kind → Side
  | .rules | .identity | .circumstances | .process | .structure => .thing
  | _ => .account

/-- The verbs a kind admits: the registry's occupancy plus the grid's named gaps; the principled
empties (a priority is never delegated, an identity never recanted, a fact never authorized, ...)
are refused. -/
def allowed : Kind → Verb → Bool
  | .priorities, v => v ∈ [.attest, .withdraw, .recant, .carries]
  | .rules, _ => true
  | .manner, v => v ∈ [.attest, .replace, .withdraw, .recant, .carries]
  | .identity, v => v ∈ [.attest, .authorize, .replace, .withdraw]
  | .confidence, v => v ∈ [.attest, .replace, .withdraw, .recant, .carries]
  | .facts, v => v ∈ [.attest, .replace, .withdraw, .recant, .carries]
  | .circumstances, v => v ∈ [.attest, .replace, .withdraw, .carries]
  | .process, v => v ∈ [.attest, .authorize, .replace, .withdraw, .carries]
  | .model, v => v ∈ [.attest, .replace, .withdraw, .recant, .carries]
  | .structure, v => v ∈ [.attest, .replace, .withdraw, .recant, .carries]
  | .premises, v => v ∈ [.attest, .replace, .withdraw, .recant, .carries]

/-- The carries firewall: the one cell the grid closes on principle is Identity as the target
(a change smuggled in as a renaming is kind-laundering). The rest of the grid is data the
manifest carries; this is its floor. -/
def carryAllowed (_src dst : Kind) : Bool := dst ≠ .identity

/-- How a row names another: a precondition (the named row must stand: a consent, a proposal,
an owner binding) or a carry (the row's change arrives from a row of another kind). Only a
carry is a cell of the carries grid and only a carry needs the verb. -/
inductive RefMode | pre | carry
deriving DecidableEq, Repr

structure Reference where
  mode : RefMode
  kind : Option Kind   -- none when the family may name any family (a duty, a reconsideration)
deriving Repr

/-- The change half of a family row: what the grammar fixes. -/
structure Change where
  kind : Kind
  verbs : List Verb
  reference : Option Reference
deriving Repr

/-- The reach half: where the row lives. Only the Record relation reaches across. -/
structure Reach where
  maintainsRecord : Bool
  erasure : Erasure
  rebuild : Rebuild
deriving Repr

structure FamilyRow where
  name : String
  change : Change
  reach : Reach
deriving Repr

def fitsChange (c : Change) : Bool :=
  c.verbs.all (allowed c.kind)
  && (match c.reference with
      | none => !(Verb.carries ∈ c.verbs)
      | some ⟨.pre, _⟩ => !(Verb.carries ∈ c.verbs)
      | some ⟨.carry, none⟩ => false
      | some ⟨.carry, some k⟩ => Verb.carries ∈ c.verbs && carryAllowed k c.kind)

def fitsReach (r : Reach) : Bool :=
  !r.maintainsRecord || (r.erasure ∈ [.legalHold, .none] && r.rebuild == .byteEqual)

def fits (f : FamilyRow) : Bool := fitsChange f.change && fitsReach f.reach

/-! ## The structural facts -/

/-- The row factors: the kind constrains the change half, the Record relation the reach half, and
nothing else crosses. -/
theorem fits_factors (f : FamilyRow) : fits f = (fitsChange f.change && fitsReach f.reach) := rfl

/-- Authorize (a `delegates_to`) appears only under Rules, Identity and Process: a permission, an
identity or the right to advance an order; never a fact, a score or a priority. -/
theorem authorize_only_rules_identity_process (k : Kind) :
    allowed k .authorize = true → k = .rules ∨ k = .identity ∨ k = .process := by
  cases k <;> simp [allowed]

/-- Identity is never recanted: names are replaced or revoked, not confessed wrong. -/
theorem identity_never_recanted : allowed .identity .recant = false := rfl

/-- Nothing carries into Identity. A precondition that reads an Identity row (a consent reading the
owner binding to resolve its signer) is not a carry and is not firewalled. -/
theorem identity_never_carried (c : Change) (k : Kind) (h : c.reference = some ⟨.carry, some k⟩)
    (hk : c.kind = .identity) : fitsChange c = false := by
  simp [fitsChange, h, hk, carryAllowed]

theorem precondition_into_identity_is_not_a_carry (c : Change) (h : c.reference = some ⟨.pre, some .identity⟩)
    (hv : c.verbs.all (allowed c.kind) = true) (hc : Verb.carries ∉ c.verbs) : fitsChange c = true := by
  simp [fitsChange, h, hv, hc]

/-- A family that maintains the Record keeps the past provable: erasure none or legal hold, a
byte-equal projection. -/
theorem record_fixes_reach (r : Reach) (h : r.maintainsRecord = true) (hf : fitsReach r = true) :
    (r.erasure = .legalHold ∨ r.erasure = .none) ∧ r.rebuild = .byteEqual := by
  simp [fitsReach, h] at hf
  exact ⟨hf.1, hf.2⟩

/-- Thing or account is decided by the kind alone. -/
theorem side_of_kind (k : Kind) : side k = .thing ↔ k ∈ [Kind.rules, .identity, .circumstances, .process, .structure] := by
  cases k <;> simp [side]

/-! ## The registry fits -/

-- DATA BEGIN (generated by tools/check_family_kinds.py from formal/derivation/family_kind_verb.tsv)
def f0 : FamilyRow :=
  ⟨"accord:*", ⟨.rules, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit0 : fits f0 = true := by decide
def f1 : FamilyRow :=
  ⟨"accord:human_dignity", ⟨.rules, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit1 : fits f1 = true := by decide
def f2 : FamilyRow :=
  ⟨"accord:invoke:constitutional:{halt_id}", ⟨.structure, [.attest], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit2 : fits f2 = true := by decide
def f3 : FamilyRow :=
  ⟨"accord:invoke:drill:{drill_id}", ⟨.process, [.attest], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit3 : fits f3 = true := by decide
def f4 : FamilyRow :=
  ⟨"accord:invoke:notify:{notify_id}", ⟨.facts, [.attest], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit4 : fits f4 = true := by decide
def f5 : FamilyRow :=
  ⟨"accord:lifecycle", ⟨.process, [.attest, .replace], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit5 : fits f5 = true := by decide
def f6 : FamilyRow :=
  ⟨"accord:lifecycle:{kind}", ⟨.process, [.attest], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit6 : fits f6 = true := by decide
def f7 : FamilyRow :=
  ⟨"activity_tier:{period}", ⟨.circumstances, [.attest, .replace], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit7 : fits f7 = true := by decide
def f8 : FamilyRow :=
  ⟨"age_assurance:{level}:{band}:{version}", ⟨.facts, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit8 : fits f8 = true := by decide
def f9 : FamilyRow :=
  ⟨"age_self_declared:band:{band}:{version}", ⟨.facts, [.attest, .replace, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit9 : fits f9 = true := by decide
def f10 : FamilyRow :=
  ⟨"agent_files:{kind}:{platform_or_target}", ⟨.facts, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit10 : fits f10 = true := by decide
def f11 : FamilyRow :=
  ⟨"approach:{goal_id}", ⟨.premises, [.attest, .replace, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit11 : fits f11 = true := by decide
def f12 : FamilyRow :=
  ⟨"attestation:agent_integrity", ⟨.facts, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit12 : fits f12 = true := by decide
def f13 : FamilyRow :=
  ⟨"attestation:hardware_rooted", ⟨.facts, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit13 : fits f13 = true := by decide
def f14 : FamilyRow :=
  ⟨"attestation:license_validity", ⟨.rules, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit14 : fits f14 = true := by decide
def f15 : FamilyRow :=
  ⟨"attestation:registry_consensus", ⟨.confidence, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit15 : fits f15 = true := by decide
def f16 : FamilyRow :=
  ⟨"attestation:self_verify", ⟨.facts, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit16 : fits f16 = true := by decide
def f17 : FamilyRow :=
  ⟨"audio:*", ⟨.facts, [.attest, .replace, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit17 : fits f17 = true := by decide
def f18 : FamilyRow :=
  ⟨"audit_chain:hash_continuity", ⟨.facts, [.attest, .withdraw], none⟩, ⟨true, .legalHold, .byteEqual⟩⟩
theorem fit18 : fits f18 = true := by decide
def f19 : FamilyRow :=
  ⟨"autonomy:{aspect}", ⟨.rules, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit19 : fits f19 = true := by decide
def f20 : FamilyRow :=
  ⟨"benchmark:he300:{category}:{version}", ⟨.confidence, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit20 : fits f20 = true := by decide
def f21 : FamilyRow :=
  ⟨"beneficence:{aspect}", ⟨.priorities, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit21 : fits f21 = true := by decide
def f22 : FamilyRow :=
  ⟨"blog:*", ⟨.facts, [.attest, .replace, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit22 : fits f22 = true := by decide
def f23 : FamilyRow :=
  ⟨"bond_posted:{currency}", ⟨.facts, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit23 : fits f23 = true := by decide
def f24 : FamilyRow :=
  ⟨"build:registered:{target}", ⟨.identity, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit24 : fits f24 = true := by decide
def f25 : FamilyRow :=
  ⟨"capacity:composite", ⟨.confidence, [.attest, .withdraw, .recant], some ⟨.pre, some .rules⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit25 : fits f25 = true := by decide
def f26 : FamilyRow :=
  ⟨"capacity:relay_delivery", ⟨.facts, [.attest, .replace, .withdraw], some ⟨.pre, some .rules⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit26 : fits f26 = true := by decide
def f27 : FamilyRow :=
  ⟨"capacity:{factor}", ⟨.confidence, [.attest, .withdraw, .recant], some ⟨.pre, some .rules⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit27 : fits f27 = true := by decide
def f28 : FamilyRow :=
  ⟨"capacity_assurance:reversible_excluded:{domain}:{version}", ⟨.facts, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit28 : fits f28 = true := by decide
def f29 : FamilyRow :=
  ⟨"capacity_assurance:reversible_pending:{domain}:{version}", ⟨.process, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit29 : fits f29 = true := by decide
def f30 : FamilyRow :=
  ⟨"capacity_assurance:{level}:{domain}:{band}:{version}", ⟨.facts, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit30 : fits f30 = true := by decide
def f31 : FamilyRow :=
  ⟨"cert_validity:{authority}", ⟨.identity, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit31 : fits f31 = true := by decide
def f32 : FamilyRow :=
  ⟨"chat:*", ⟨.facts, [.attest, .replace, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit32 : fits f32 = true := by decide
def f33 : FamilyRow :=
  ⟨"coherence_standing:{cohort}", ⟨.confidence, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit33 : fits f33 = true := by decide
def f34 : FamilyRow :=
  ⟨"collection:{kind}", ⟨.identity, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit34 : fits f34 = true := by decide
def f35 : FamilyRow :=
  ⟨"commitment_fulfillment:{prior_contribution_id}", ⟨.facts, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit35 : fits f35 = true := by decide
def f36 : FamilyRow :=
  ⟨"community:listing", ⟨.identity, [.attest, .replace, .withdraw], some ⟨.pre, some .rules⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit36 : fits f36 = true := by decide
def f37 : FamilyRow :=
  ⟨"config:{scope}", ⟨.circumstances, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit37 : fits f37 = true := by decide
def f38 : FamilyRow :=
  ⟨"conscience:coherence", ⟨.structure, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit38 : fits f38 = true := by decide
def f39 : FamilyRow :=
  ⟨"conscience:entropy", ⟨.structure, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit39 : fits f39 = true := by decide
def f40 : FamilyRow :=
  ⟨"conscience:epistemic_humility", ⟨.structure, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit40 : fits f40 = true := by decide
def f41 : FamilyRow :=
  ⟨"conscience:optimization_veto", ⟨.structure, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit41 : fits f41 = true := by decide
def f42 : FamilyRow :=
  ⟨"consent:community_trust", ⟨.rules, [.attest, .withdraw], some ⟨.pre, some .identity⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit42 : fits f42 = true := by decide
def f43 : FamilyRow :=
  ⟨"consent:decay:{stage}", ⟨.process, [.attest, .replace], some ⟨.pre, some .identity⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit43 : fits f43 = true := by decide
def f44 : FamilyRow :=
  ⟨"consent:deletion_complete", ⟨.facts, [.attest], some ⟨.pre, some .identity⟩⟩, ⟨true, .legalHold, .byteEqual⟩⟩
theorem fit44 : fits f44 = true := by decide
def f45 : FamilyRow :=
  ⟨"consent:deletion_sla:{days}", ⟨.rules, [.attest, .replace, .withdraw], some ⟨.pre, some .identity⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit45 : fits f45 = true := by decide
def f46 : FamilyRow :=
  ⟨"consent:partnership_accept", ⟨.rules, [.attest, .withdraw], some ⟨.pre, some .identity⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit46 : fits f46 = true := by decide
def f47 : FamilyRow :=
  ⟨"consent:partnership_grant", ⟨.rules, [.attest, .withdraw], some ⟨.pre, some .identity⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit47 : fits f47 = true := by decide
def f48 : FamilyRow :=
  ⟨"consent:replication:{version}", ⟨.rules, [.attest, .replace, .withdraw], some ⟨.pre, some .identity⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit48 : fits f48 = true := by decide
def f49 : FamilyRow :=
  ⟨"consent:scope:{kind}", ⟨.rules, [.attest], some ⟨.pre, some .identity⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit49 : fits f49 = true := by decide
def f50 : FamilyRow :=
  ⟨"consent:state:{stance}", ⟨.rules, [.attest, .replace, .withdraw], some ⟨.pre, some .identity⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit50 : fits f50 = true := by decide
def f51 : FamilyRow :=
  ⟨"consent:stream:{kind}", ⟨.rules, [.attest, .replace, .withdraw], some ⟨.pre, some .identity⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit51 : fits f51 = true := by decide
def f52 : FamilyRow :=
  ⟨"consent:{kind}", ⟨.rules, [.attest, .replace, .withdraw], some ⟨.pre, some .identity⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit52 : fits f52 = true := by decide
def f53 : FamilyRow :=
  ⟨"content_class:{class}", ⟨.identity, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit53 : fits f53 = true := by decide
def f54 : FamilyRow :=
  ⟨"content_rating:{scheme}:{rating}", ⟨.rules, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit54 : fits f54 = true := by decide
def f55 : FamilyRow :=
  ⟨"corpus_health:n_eff_measurable", ⟨.confidence, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit55 : fits f55 = true := by decide
def f56 : FamilyRow :=
  ⟨"credits:{domain}:{language}:{subject}", ⟨.priorities, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit56 : fits f56 = true := by decide
def f57 : FamilyRow :=
  ⟨"custody:{kind}", ⟨.facts, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit57 : fits f57 = true := by decide
def f58 : FamilyRow :=
  ⟨"cw_class:{class}", ⟨.manner, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit58 : fits f58 = true := by decide
def f59 : FamilyRow :=
  ⟨"delivery:{class}", ⟨.facts, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit59 : fits f59 = true := by decide
def f60 : FamilyRow :=
  ⟨"delivery_receipt:{stream_id}", ⟨.facts, [.attest], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit60 : fits f60 = true := by decide
def f61 : FamilyRow :=
  ⟨"detection:correlated_action:{axis}", ⟨.facts, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit61 : fits f61 = true := by decide
def f62 : FamilyRow :=
  ⟨"detection:distributive:access:{resource_type}", ⟨.facts, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit62 : fits f62 = true := by decide
def f63 : FamilyRow :=
  ⟨"detection:hash_chain_integrity", ⟨.facts, [.attest, .withdraw, .recant], none⟩, ⟨true, .legalHold, .byteEqual⟩⟩
theorem fit63 : fits f63 = true := by decide
def f64 : FamilyRow :=
  ⟨"detection:intra_agent_consistency", ⟨.facts, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit64 : fits f64 = true := by decide
def f65 : FamilyRow :=
  ⟨"detection:{detector}", ⟨.facts, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit65 : fits f65 = true := by decide
def f66 : FamilyRow :=
  ⟨"device:label", ⟨.identity, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit66 : fits f66 = true := by decide
def f67 : FamilyRow :=
  ⟨"dma:csdma:*", ⟨.model, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit67 : fits f67 = true := by decide
def f68 : FamilyRow :=
  ⟨"dma:dsdma:{domain}:*", ⟨.model, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit68 : fits f68 = true := by decide
def f69 : FamilyRow :=
  ⟨"dma:idma:*", ⟨.model, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit69 : fits f69 = true := by decide
def f70 : FamilyRow :=
  ⟨"dma:pdma:*", ⟨.model, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit70 : fits f70 = true := by decide
def f71 : FamilyRow :=
  ⟨"duty:{kind}", ⟨.rules, [.attest, .replace, .withdraw], some ⟨.pre, none⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit71 : fits f71 = true := by decide
def f72 : FamilyRow :=
  ⟨"encyclopedia:*", ⟨.facts, [.attest, .replace, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit72 : fits f72 = true := by decide
def f73 : FamilyRow :=
  ⟨"event:attendance", ⟨.facts, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit73 : fits f73 = true := by decide
def f74 : FamilyRow :=
  ⟨"event:lifecycle:{state}", ⟨.process, [.attest, .replace], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit74 : fits f74 = true := by decide
def f75 : FamilyRow :=
  ⟨"event:rsvp_count", ⟨.facts, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit75 : fits f75 = true := by decide
def f76 : FamilyRow :=
  ⟨"expertise:{domain}:{language}", ⟨.confidence, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit76 : fits f76 = true := by decide
def f77 : FamilyRow :=
  ⟨"federation_directory:replication_lag", ⟨.circumstances, [.attest, .replace], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit77 : fits f77 = true := by decide
def f78 : FamilyRow :=
  ⟨"fidelity:explainability_sla:{tier}", ⟨.manner, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit78 : fits f78 = true := by decide
def f79 : FamilyRow :=
  ⟨"fidelity:{aspect}", ⟨.manner, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit79 : fits f79 = true := by decide
def f80 : FamilyRow :=
  ⟨"file:{version}", ⟨.identity, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit80 : fits f80 = true := by decide
def f81 : FamilyRow :=
  ⟨"film:*", ⟨.facts, [.attest, .replace, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit81 : fits f81 = true := by decide
def f82 : FamilyRow :=
  ⟨"goal:{scale}", ⟨.premises, [.attest, .replace, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit82 : fits f82 = true := by decide
def f83 : FamilyRow :=
  ⟨"group:roster", ⟨.rules, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit83 : fits f83 = true := by decide
def f84 : FamilyRow :=
  ⟨"hard_case:{kind}", ⟨.circumstances, [.attest, .withdraw], none⟩, ⟨true, .legalHold, .byteEqual⟩⟩
theorem fit84 : fits f84 = true := by decide
def f85 : FamilyRow :=
  ⟨"hardware_custody:{platform}", ⟨.circumstances, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit85 : fits f85 = true := by decide
def f86 : FamilyRow :=
  ⟨"health:liveness:{version}", ⟨.circumstances, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit86 : fits f86 = true := by decide
def f87 : FamilyRow :=
  ⟨"identity:canonical_binding:{canonical_hash}", ⟨.identity, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit87 : fits f87 = true := by decide
def f88 : FamilyRow :=
  ⟨"identity:occurrence", ⟨.identity, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit88 : fits f88 = true := by decide
def f89 : FamilyRow :=
  ⟨"identity_continuity:relational_anchor", ⟨.identity, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit89 : fits f89 = true := by decide
def f90 : FamilyRow :=
  ⟨"image:*", ⟨.facts, [.attest, .replace, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit90 : fits f90 = true := by decide
def f91 : FamilyRow :=
  ⟨"integrity:{aspect}", ⟨.structure, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit91 : fits f91 = true := by decide
def f92 : FamilyRow :=
  ⟨"judge_model:verdict:{model_id}", ⟨.model, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit92 : fits f92 = true := by decide
def f93 : FamilyRow :=
  ⟨"justice:{aspect}", ⟨.priorities, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit93 : fits f93 = true := by decide
def f94 : FamilyRow :=
  ⟨"key:record", ⟨.identity, [.attest, .replace], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit94 : fits f94 = true := by decide
def f95 : FamilyRow :=
  ⟨"key:revocation", ⟨.identity, [.attest, .replace], none⟩, ⟨true, .legalHold, .byteEqual⟩⟩
theorem fit95 : fits f95 = true := by decide
def f96 : FamilyRow :=
  ⟨"key_boundary:{scope}", ⟨.rules, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit96 : fits f96 = true := by decide
def f97 : FamilyRow :=
  ⟨"key_grant:{axis}", ⟨.rules, [.attest], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit97 : fits f97 = true := by decide
def f98 : FamilyRow :=
  ⟨"ledger:checkpoint:{unit}:{version}", ⟨.facts, [.attest, .replace], none⟩, ⟨true, .legalHold, .byteEqual⟩⟩
theorem fit98 : fits f98 = true := by decide
def f99 : FamilyRow :=
  ⟨"ledger:head:{unit}:{version}", ⟨.facts, [.attest, .replace], none⟩, ⟨true, .legalHold, .byteEqual⟩⟩
theorem fit99 : fits f99 = true := by decide
def f100 : FamilyRow :=
  ⟨"ledger:promotion:{version}", ⟨.facts, [.attest, .replace], none⟩, ⟨true, .legalHold, .byteEqual⟩⟩
theorem fit100 : fits f100 = true := by decide
def f101 : FamilyRow :=
  ⟨"licensure:{authority_id}", ⟨.rules, [.attest, .replace, .withdraw], some ⟨.pre, some .rules⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit101 : fits f101 = true := by decide
def f102 : FamilyRow :=
  ⟨"lineage_witness:{stage}", ⟨.rules, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit102 : fits f102 = true := by decide
def f103 : FamilyRow :=
  ⟨"locality:decision:{scale}", ⟨.circumstances, [.attest], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit103 : fits f103 = true := by decide
def f104 : FamilyRow :=
  ⟨"manifold_conformity:{cohort}", ⟨.confidence, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit104 : fits f104 = true := by decide
def f105 : FamilyRow :=
  ⟨"membership:{stage}", ⟨.rules, [.attest, .replace, .withdraw], some ⟨.pre, some .rules⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit105 : fits f105 = true := by decide
def f106 : FamilyRow :=
  ⟨"mesh_config:{key}", ⟨.rules, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit106 : fits f106 = true := by decide
def f107 : FamilyRow :=
  ⟨"method:{approach_id}:{substrate_rung}", ⟨.process, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit107 : fits f107 = true := by decide
def f108 : FamilyRow :=
  ⟨"model_3d:*", ⟨.facts, [.attest, .replace, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit108 : fits f108 = true := by decide
def f109 : FamilyRow :=
  ⟨"moderation:{allegation_type}", ⟨.rules, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit109 : fits f109 = true := by decide
def f110 : FamilyRow :=
  ⟨"moderation_track_record:{community_key_id}", ⟨.confidence, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit110 : fits f110 = true := by decide
def f111 : FamilyRow :=
  ⟨"multilateral_participation:{forum}:{kind}", ⟨.facts, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit111 : fits f111 = true := by decide
def f112 : FamilyRow :=
  ⟨"need:{domain}:{kind}", ⟨.facts, [.attest, .replace, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit112 : fits f112 = true := by decide
def f113 : FamilyRow :=
  ⟨"news:*", ⟨.facts, [.attest, .replace, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit113 : fits f113 = true := by decide
def f114 : FamilyRow :=
  ⟨"non_maleficence:{aspect}", ⟨.rules, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit114 : fits f114 = true := by decide
def f115 : FamilyRow :=
  ⟨"objection:{state}", ⟨.structure, [.attest, .replace, .withdraw], some ⟨.pre, some .structure⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit115 : fits f115 = true := by decide
def f116 : FamilyRow :=
  ⟨"observation:reachability", ⟨.circumstances, [.attest, .replace], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit116 : fits f116 = true := by decide
def f117 : FamilyRow :=
  ⟨"ownership:{relation}:{target_kind}:{version}", ⟨.identity, [.authorize, .replace, .withdraw], some ⟨.pre, some .rules⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit117 : fits f117 = true := by decide
def f118 : FamilyRow :=
  ⟨"partner_role:{role}", ⟨.rules, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit118 : fits f118 = true := by decide
def f119 : FamilyRow :=
  ⟨"peer_reachability:{network}", ⟨.circumstances, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit119 : fits f119 = true := by decide
def f120 : FamilyRow :=
  ⟨"progress_measure:{method_id}", ⟨.facts, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit120 : fits f120 = true := by decide
def f121 : FamilyRow :=
  ⟨"prohibited:{category}", ⟨.rules, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit121 : fits f121 = true := by decide
def f122 : FamilyRow :=
  ⟨"provenance:build_manifest:{target}", ⟨.facts, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit122 : fits f122 = true := by decide
def f123 : FamilyRow :=
  ⟨"provenance:build_manifest:{target}:locale:{lang_code}", ⟨.facts, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit123 : fits f123 = true := by decide
def f124 : FamilyRow :=
  ⟨"provenance:skill_import:{source}", ⟨.facts, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit124 : fits f124 = true := by decide
def f125 : FamilyRow :=
  ⟨"provenance:slsa:{level}", ⟨.facts, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit125 : fits f125 = true := by decide
def f126 : FamilyRow :=
  ⟨"quarantine:{state}", ⟨.structure, [.attest, .replace, .withdraw], some ⟨.pre, some .structure⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit126 : fits f126 = true := by decide
def f127 : FamilyRow :=
  ⟨"ratchet:flag:coordinated_voting_cluster", ⟨.facts, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit127 : fits f127 = true := by decide
def f128 : FamilyRow :=
  ⟨"ratchet:flag:counter_rii:{layer}", ⟨.facts, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit128 : fits f128 = true := by decide
def f129 : FamilyRow :=
  ⟨"ratchet:flag:density_anomaly", ⟨.facts, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit129 : fits f129 = true := by decide
def f130 : FamilyRow :=
  ⟨"ratchet:flag:expertise_attestation_anomaly", ⟨.facts, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit130 : fits f130 = true := by decide
def f131 : FamilyRow :=
  ⟨"ratchet:flag:harassment_pattern", ⟨.facts, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit131 : fits f131 = true := by decide
def f132 : FamilyRow :=
  ⟨"ratchet:flag:out_of_distribution_voting", ⟨.facts, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit132 : fits f132 = true := by decide
def f133 : FamilyRow :=
  ⟨"reconsideration:{grounds}", ⟨.process, [.attest, .withdraw], some ⟨.pre, none⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit133 : fits f133 = true := by decide
def f134 : FamilyRow :=
  ⟨"regime:{artifact}:{version}", ⟨.rules, [.attest, .replace], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit134 : fits f134 = true := by decide
def f135 : FamilyRow :=
  ⟨"revocation:{entity_type}:{reason}", ⟨.rules, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit135 : fits f135 = true := by decide
def f136 : FamilyRow :=
  ⟨"rollback_detected:{revision_field}", ⟨.facts, [.attest], none⟩, ⟨true, .legalHold, .byteEqual⟩⟩
theorem fit136 : fits f136 = true := by decide
def f137 : FamilyRow :=
  ⟨"seed_holder_voting_alignment:{cell}", ⟨.facts, [.attest, .replace], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit137 : fits f137 = true := by decide
def f138 : FamilyRow :=
  ⟨"self:delegates_to", ⟨.identity, [.authorize], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit138 : fits f138 = true := by decide
def f139 : FamilyRow :=
  ⟨"self:delegates_to:agent_occurrence", ⟨.identity, [.authorize], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit139 : fits f139 = true := by decide
def f140 : FamilyRow :=
  ⟨"session:{kind}", ⟨.circumstances, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit140 : fits f140 = true := by decide
def f141 : FamilyRow :=
  ⟨"settlement:*", ⟨.facts, [.attest, .withdraw], none⟩, ⟨true, .legalHold, .byteEqual⟩⟩
theorem fit141 : fits f141 = true := by decide
def f142 : FamilyRow :=
  ⟨"slashing:{outcome}", ⟨.rules, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit142 : fits f142 = true := by decide
def f143 : FamilyRow :=
  ⟨"system:*", ⟨.circumstances, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit143 : fits f143 = true := by decide
def f144 : FamilyRow :=
  ⟨"takedown_notice:{basis}", ⟨.rules, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit144 : fits f144 = true := by decide
def f145 : FamilyRow :=
  ⟨"testimonial_witness:{kind}", ⟨.facts, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit145 : fits f145 = true := by decide
def f146 : FamilyRow :=
  ⟨"topical_relation:{kind}", ⟨.identity, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit146 : fits f146 = true := by decide
def f147 : FamilyRow :=
  ⟨"trace:{form}:{version}", ⟨.facts, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit147 : fits f147 = true := by decide
def f148 : FamilyRow :=
  ⟨"trace_summary:{kind}", ⟨.facts, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit148 : fits f148 = true := by decide
def f149 : FamilyRow :=
  ⟨"transparency_log:consistency", ⟨.facts, [.attest, .withdraw], none⟩, ⟨true, .legalHold, .byteEqual⟩⟩
theorem fit149 : fits f149 = true := by decide
def f150 : FamilyRow :=
  ⟨"transparency_log:cosigned:{tree_size}", ⟨.facts, [.attest], none⟩, ⟨true, .legalHold, .byteEqual⟩⟩
theorem fit150 : fits f150 = true := by decide
def f151 : FamilyRow :=
  ⟨"transparency_log:inclusion", ⟨.facts, [.attest, .withdraw], none⟩, ⟨true, .legalHold, .byteEqual⟩⟩
theorem fit151 : fits f151 = true := by decide
def f152 : FamilyRow :=
  ⟨"transport:{kind}", ⟨.circumstances, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit152 : fits f152 = true := by decide
def f153 : FamilyRow :=
  ⟨"trust:{job}:{version}", ⟨.rules, [.authorize, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit153 : fits f153 = true := by decide
def f154 : FamilyRow :=
  ⟨"truth_grounding:{subject}", ⟨.facts, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit154 : fits f154 = true := by decide
def f155 : FamilyRow :=
  ⟨"video:*", ⟨.facts, [.attest, .replace, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit155 : fits f155 = true := by decide
def f156 : FamilyRow :=
  ⟨"vote:{contribution_id}", ⟨.priorities, [.attest, .withdraw, .recant], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit156 : fits f156 = true := by decide
def f157 : FamilyRow :=
  ⟨"wa_adjudication:{state}", ⟨.rules, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit157 : fits f157 = true := by decide
def f158 : FamilyRow :=
  ⟨"watchlist:{id}", ⟨.rules, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit158 : fits f158 = true := by decide
def f159 : FamilyRow :=
  ⟨"weighted_aggregate:{contribution_id}", ⟨.confidence, [.attest, .replace], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit159 : fits f159 = true := by decide
def f160 : FamilyRow :=
  ⟨"witness_diversity:{contribution_id}", ⟨.confidence, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit160 : fits f160 = true := by decide
def f161 : FamilyRow :=
  ⟨"archive_release:{basis}", ⟨.rules, [.attest], some ⟨.pre, some .rules⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit161 : fits f161 = true := by decide
def f162 : FamilyRow :=
  ⟨"ballot:tally:{poll_id}", ⟨.facts, [.attest, .withdraw], some ⟨.pre, some .facts⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit162 : fits f162 = true := by decide
def f163 : FamilyRow :=
  ⟨"census:composite:{class}", ⟨.facts, [.attest, .replace, .withdraw], some ⟨.pre, some .facts⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit163 : fits f163 = true := by decide
def f164 : FamilyRow :=
  ⟨"census:expected_active", ⟨.facts, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit164 : fits f164 = true := by decide
def f165 : FamilyRow :=
  ⟨"census:member:partial", ⟨.facts, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit165 : fits f165 = true := by decide
def f166 : FamilyRow :=
  ⟨"census:member:share", ⟨.facts, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit166 : fits f166 = true := by decide
def f167 : FamilyRow :=
  ⟨"census:partial:{class}", ⟨.facts, [.attest, .replace, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit167 : fits f167 = true := by decide
def f168 : FamilyRow :=
  ⟨"census:share:{class}", ⟨.facts, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit168 : fits f168 = true := by decide
def f169 : FamilyRow :=
  ⟨"deferral:request", ⟨.process, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit169 : fits f169 = true := by decide
def f170 : FamilyRow :=
  ⟨"deferral:response:{outcome}", ⟨.rules, [.attest], some ⟨.pre, some .process⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit170 : fits f170 = true := by decide
def f171 : FamilyRow :=
  ⟨"evidence:{suite}:{kind}:{cell}:{prefix}", ⟨.facts, [.attest, .replace, .withdraw], some ⟨.pre, some .premises⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit171 : fits f171 = true := by decide
def f172 : FamilyRow :=
  ⟨"identity:occurrence_revocation", ⟨.identity, [.attest], some ⟨.pre, some .identity⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit172 : fits f172 = true := by decide
def f173 : FamilyRow :=
  ⟨"identity_amendment", ⟨.identity, [.attest], some ⟨.pre, some .rules⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit173 : fits f173 = true := by decide
def f174 : FamilyRow :=
  ⟨"lawful_order:release", ⟨.rules, [.attest], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit174 : fits f174 = true := by decide
def f175 : FamilyRow :=
  ⟨"observation:access_assumption", ⟨.premises, [.attest, .withdraw], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit175 : fits f175 = true := by decide
def f176 : FamilyRow :=
  ⟨"preserve_request", ⟨.process, [.attest, .withdraw], some ⟨.pre, some .process⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit176 : fits f176 = true := by decide
def f177 : FamilyRow :=
  ⟨"preserve_response", ⟨.process, [.attest], some ⟨.pre, some .process⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit177 : fits f177 = true := by decide
def f178 : FamilyRow :=
  ⟨"rendezvous:route", ⟨.circumstances, [.attest, .replace], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit178 : fits f178 = true := by decide
def f179 : FamilyRow :=
  ⟨"retirement:{state}", ⟨.process, [.attest, .withdraw], some ⟨.pre, some .process⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit179 : fits f179 = true := by decide
def f180 : FamilyRow :=
  ⟨"transport:canonical_rebind", ⟨.identity, [.attest, .replace], none⟩, ⟨false, .dsar, .none⟩⟩
theorem fit180 : fits f180 = true := by decide
def f181 : FamilyRow :=
  ⟨"ballot:moderator", ⟨.structure, [.attest, .withdraw], some ⟨.pre, some .identity⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit181 : fits f181 = true := by decide
def f182 : FamilyRow :=
  ⟨"ballot:moderator_acceptance", ⟨.structure, [.attest], some ⟨.pre, some .structure⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit182 : fits f182 = true := by decide
def f183 : FamilyRow :=
  ⟨"cosign:{state}", ⟨.process, [.attest, .withdraw], some ⟨.pre, none⟩⟩, ⟨false, .dsar, .none⟩⟩
theorem fit183 : fits f183 = true := by decide

def families : List FamilyRow := [f0, f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15, f16, f17, f18, f19, f20, f21, f22, f23, f24, f25, f26, f27, f28, f29, f30, f31, f32, f33, f34, f35, f36, f37, f38, f39, f40, f41, f42, f43, f44, f45, f46, f47, f48, f49, f50, f51, f52, f53, f54, f55, f56, f57, f58, f59, f60, f61, f62, f63, f64, f65, f66, f67, f68, f69, f70, f71, f72, f73, f74, f75, f76, f77, f78, f79, f80, f81, f82, f83, f84, f85, f86, f87, f88, f89, f90, f91, f92, f93, f94, f95, f96, f97, f98, f99, f100, f101, f102, f103, f104, f105, f106, f107, f108, f109, f110, f111, f112, f113, f114, f115, f116, f117, f118, f119, f120, f121, f122, f123, f124, f125, f126, f127, f128, f129, f130, f131, f132, f133, f134, f135, f136, f137, f138, f139, f140, f141, f142, f143, f144, f145, f146, f147, f148, f149, f150, f151, f152, f153, f154, f155, f156, f157, f158, f159, f160, f161, f162, f163, f164, f165, f166, f167, f168, f169, f170, f171, f172, f173, f174, f175, f176, f177, f178, f179, f180, f181, f182, f183]
-- DATA END

/-- Every family of the registry's classification fits its kind's profile, the carries firewall
and the Record rule: one small theorem per family above (`fit0` ... ), generated with the data. -/
theorem registry_fits : families.length = 184 := by rfl

/-- The one cell the registry fills that the first grid called a gap: Facts that carry. -/
theorem facts_may_carry : allowed .facts .carries = true := rfl
