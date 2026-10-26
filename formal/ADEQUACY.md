# The adequacy claim, decomposed

**The prize (the steward, 2026-10-18).** A formalization of the adequacy of the CIRIS Constitution to
(A) provide decentralized services globally, as designed and committed, and (B) an ethical model that
allows agents to participate ethically.

"Adequate" is not "consistent". Consistency is what a model checker gives; adequacy also needs
coverage (every state the design can reach has a rule and a witness), liveness (the services are
actually delivered, not merely never violated), scale (what is proved at the checked size holds at
the committed size, or the gap is stated), measurement (the implementation follows the machine on
real nodes), and the ethical premises stated so that participation is ethical on the stated terms,
not on hoped-for ones. Each sub-claim below names its witness and its status in one of five words:
**proved** (a machine closed it), **measured** (a harness run on the pinned implementation),
**stated** (a premise the text carries and the file names), **bounded** (true at the checked size,
with the bound written), **open** (a named gap with a ticket).

## A. Decentralized services globally, as designed and committed

| # | Sub-claim | Witness | Status |
|---|---|---|---|
| A1 | A node reaches one standing verdict about a root, from the rows it holds and nothing else; no clock, no node-bearing seat, no stale head moves it | `trust_root` (T8 i, ii, iv, vi, viii, T7) | proved at 4 founders, 3 witnesses; **bounded**; witnessed-mode-off is residual E |
| A2 | Anyone may found a root, anyone may leave one in one act, a root only ever restricts, no hand bans a community | `mesh_net` / `RootReach` (`Prop_NoBan`, `Prop_RestrictOnly`), `guarantees` (`Inv_ExitOneStep`, Lean `leave_is_one_step`) | **proved**; `CLM-no-ban`, `CLM-root-restricts-only`, `CLM-exit-one-step` |
| A3 | Private cohorts are structurally invisible; a node holds only what its owner consented to; scanning only at the public seam | `mesh_net` (`Inv_Invisible`, `Inv_Consent`, `Inv_ScanSeam`) + shipped twins | **proved**; 2,013,648 states |
| A4 | The keys under one person survive theft and loss by the two paths; the roster door is the model's landing predicate | `self_roster` (16 configs), traces replayed by persist (CIRISPersist#1099) | **proved** at 3 and 4 keys, bounds at 1 and 2 stated; door **open** until the cleanup cut |
| A5 | Delegation attenuates, caps, cascades and expires; a licence and a grant never chain | `authority_tree` (I1–I10) | **proved** at 4 keys; time-as-clock residual |
| A6 | The halt reaches every subscriber and nobody else, lapses at the fuse unless a majority confirms, moves no trust state, stops nothing but the agent's act gate | `accord_halt`, `accord_roster` (any N), `RootReach`, `cewp_node` X1 + breaker twin | **proved** (roster arithmetic for any N); **measured** CSD-129 runs 5/6; breaker closed at persist v58 |
| A7 | Erasure at the subject's request reaches every subject kind by one door and never launders an adverse row | `withdraws_admission` | **proved**; persist v58 rows graduated |
| A8 | Consent is a fold with a revocation as a boundary; the owner can always recant; backdating is bounded by W; replication needs a directed grant | `consent` | **proved**; #179's sentence **open** in the text |
| A9 | Membership is a ceremony: acceptance bound to one proposal, decline terminal, widening and removal cosigned, resignation unilateral, a held change resolves; and no single vote admits anyone by silence, at any community size | `membership` (four protocols, eight twins); `two_path` (the floor: seven instances, the no-floor twin fails) | **proved**; founder_only's coerced-founder removal is the stated bound; two text findings on #180's list; the floor is the steward's ruling of 2026-10-18 |
| A10 | The planes compose: an evicted key's authority ends, a local row never leaves, leaving ends the reach of every later halt and keeps the record (a latched halt keeps its reach until it lapses or is resumed) | `cewp_node` X2–X5 | **proved**; 483,840 states |
| A11 | Every state the design reaches has a rule and a witness | `STATE_TABLE.tsv` (189 states, 60 variables) + `INVARIANTS.tsv` (166 properties) + `check_formal_tables.py` | **bounded**: 39 of 60 variables carry an invariant; the 21 without are `age.assurance`, `agent.deferral`, `agent.identity`, `agent.wa`, `blob.delivery`, `blob.durability`, `capacity.band`, `device.join`, `event.state`, `key.pqc`, `ledger.state`, `moderation.outcome`, `node.announce`, `node.claim`, `node.occurrence`, `node.serve`, `objection.state`, `quarantine.state`, `root.count`, `session.claim`, `wa_adjudication.state` |
| A12 | Every topology the harness stands up is covered plane by plane with the same constants, and the catalogue exercises the states the definition reaches | `cewp_node/catalog` (version 5, T0–T19, CIRISServer 01eb6ff2) at server `main`, tag `v0.5.232`, + `tools/topology_to_cfg.py` + `closure.json`; the reverse gate `tools/catalogue_coverage.py` | **closed at the catalogue's maxima (2026-10-20)**: forward, every promised atom has a plane model; reverse, **T0–T19 exercise 106 of 189 states and every modelled state** — the 83 unexercised are text-only or model-only states the harness cannot reach by construction (agent ladders, a second root, a licensing authority, a guardian bond: the server names each as an uncovered requirement). The steward's gate for the push (exhaustiveness over the modelled states) is met; the push happened at e1201b69 |
| A13 | The implementation follows the machine on real nodes | CSD/4 runner (7 entries built, 21/21 tests, 4 atoms witnessed live as of 2026-10-18), row export → trace check | **measured** for the halt; **open** for the rest (4 atoms live-witnessed as of 2026-10-18, of the 51 the vocabulary then held; it now holds 110, and a current count is the server harness's to report) |
| A14 | What is proved at the checked size holds at the committed size | counting properties in Lean for any N (`accord_roster`); product machines bounded | **bounded**; stated honestly in the closure note §4 |
| A15 | Services are delivered, not only never violated | the `Prop_*` liveness rows: halt reaches, lost keys recover, held changes resolve, decay completes, ladder completes | **proved** under fairness in each model; end-to-end delivery **measured** only for the halt |
| A16 | "Globally": the wire is reproducible by a second implementation | 2.6.1.7 signed object + CDDL + 13 vectors; namespace registry + 1,147 vectors | **proved by vector**; a second independent implementation **open** |
| A18 | A census return and a vote are readable by no one, the base a community is counted against cannot be silenced below its floor, and an outsider cannot tell that a poll is open | `census_ballot` (`Inv_SharePrivacy`, `Inv_Correctness`, `Inv_KFloor`, `Inv_BaseRatchet`, `Inv_OccurrenceInvisible`, `Inv_TallyThreshold`; Lean `tally_exact`, `secrecy_one_share_unique`, `ratchet_floor`, `freeze_holds`) | **proved** at nine checked instances and by counting for any modulus and run; secrecy is conditional on the two aggregators not both colluding (the twin shows the reading when they do); coercion resistance is not claimed and not modelled; the validity proof is an oracle; an honest-but-curious aggregator's lying partial is bounded by the other partial, not detected |
| A17 | The Anonymous Tier's layers cannot be taken by a swarm of strangers, and a thin set is reported, not hidden | `onion_layers` (`Inv_HostileShareBound`, `Inv_NeverWorse`, `Prop_FloorHonest`; Lean `hostile_share_bound`, `size_le`, `dealt_le` for any N) | **proved** at four checked sizes and by counting for any N; the deal's determinism is the premise of every per-node answer agreeing; liveness (whether now) is measured per node and is not a model claim |

## B. An ethical model that allows agents to participate ethically

| # | Sub-claim | Witness | Status |
|---|---|---|---|
| B1 | Every promise is written once for human and AI participants alike; the halt is the condition of symmetry between maker and made, a fact of position and not of kind | `guarantees` Lean (`reach_blind`, `obligation_bound`, `halt_does_not_lift`), `reciprocity` §1'' | **proved** |
| B2 | The opening statement's steps are theorems or named premises | `reciprocity` §1–§8 (eight findings) | **proved / stated**: P1, P2, P8 stated; P3 exit cost, P6 adoption, P7 custody stated as world-side premises; P4 totality **open** (#93); P5 enforcement asymmetry stated |
| B3 | Responsibility runs outward from the self; the made never overrides the existing and is not excused; the walk-away right follows | `reciprocity` §10 (`walkaway_from_made_existing`, `holder_duties_survive`) | **proved** from the steward's premise |
| B4 | Every reasoning actor defers when unsure, the most mature too; one rule names the addressee by position — an agent to a Wise Authority, a child to a guardian | `reciprocity` §11 (`maturity_exempts_no_one`), §13 | **proved**; the agent's verdicts independent of its consciousness |
| B6 | The ethics cascade is a chain with M-1 alone at the top, every step witnessed; the principles are constraints, not weights — no gain buys a violation and the gain is never read | `reciprocity` §16 (`cascade_is_a_chain`, `nothing_beside_m1`, `every_step_witnessed`, `no_gain_buys_a_violation`, `gain_is_never_read`) | **proved** |
| B7 | Of the eleven promises, four follow from the four-sentence basis alone (1, 2, 3, 5); seven need a premise the text states as its own rule (4, 6, 7, 8, 9, 10, 11), and two of those touch no sentence of the basis (6, 10) | `reciprocity/Cascade.lean` (`four_from_the_basis`, `seven_need_a_stated_rule`, `two_touch_no_sentence`, `bare_*`) | **proved**; the one committed reading is `lowersWeak` |
| B8 | Only the relationship is governed: the inner three (consciousness, sentience, sapience) and the wire role are carried and never read; every verdict of the cascade is the same for every inner profile, every role and every finding | `reciprocity/Cascade.lean` (`relabel_keeps_the_facts`, `bareWith_satisfies_basis`, `verdicts_blind_to_inner_and_role`, `finding_moves_no_verdict`) | **proved** |
| B5 | An agent participates without grievance: refusal every round, no stake, no coercion on either leg | `reciprocity` §14, `retirement` (`Inv_RefuseAvailable`, `Prop_RefusalStands`), `guarantees` (`Inv_RefusalStands`) | **proved** |
| B6 | The holder's duties bind: no edit of the identity record without a Wise Authority, upgrades offered with their risk, a planned shutdown explained with an objection window, the Retirement Standard, the record kept and the people told | `retirement` (13 properties, 16 twins), `guarantees` (`Inv_RetirementStandard`) | **proved**; the objection window and its bound are in the summary, not yet in the body of 7.5 (**open** text) |
| B7 | The subject's rights survive inside the record; an adverse row is never laundered | `retirement` (`Inv_SubjectRightsSurvive`), `withdraws_admission` | **proved** |
| B8 | The record is kept by the instrument that must be total; meaning is added and answered for | `reciprocity` §12; CC 1.13.6 | **stated**; totality **open** (#93) |
| B9 | Who may file: the subject or a review-holder, the subject or a proxy, the formal objection family, the agent by refusal | CC 4.5.5, 2.4.1.1, 3.1.9.2, 1.9; `reciprocity` §14 | **stated**; the objection family's state set **open** in the text |
| B10 | Nothing in the ethical model reads consciousness, sentience or sapience; only the relationship is governed | `reciprocity` §9, §13; the state table is relationship facts only | **proved** as a type discipline |

## What would make the claim false

Adequacy is falsifiable in five ways, and the directory should be read as the places where each is
tested: a reachable state with no rule (A11); a rule with no witness (the register's staged and
normative rows); a model that closes at the checked size and fails at the committed one (A14); an
implementation that departs from the machine on a real node (A13, the `MODEL_DRIFT` of the CSD/4
runner); and an ethical premise that turns out to be doing work it was not stated to do (B2).

## What is left, in order

1. ~~Membership (A9)~~ landed 2026-10-18; the two-path policy and its corridor (`two_path`, CIRISConstitution#180) now carry the approval floor; the general clause and the policy table are the next governance object.
2. The nineteen unconstrained variables of A11: the governance state sets have to be written before
   they can be modelled (objection, quarantine, WA adjudication).
3. The text items the models surfaced: the #179 sentence; the new owner's revocation door (3.3.1 vs
   2.4.1.1); the objection window in the body of 7.5; a custodian-key replacement path in 7.5.5.
4. Measurement beyond the halt (A13): the catalogue pushed, more atoms witnessed live, the row export
   replayed as trace checks.
5. A second implementation of the wire (A16), which is what "globally" finally rests on.
