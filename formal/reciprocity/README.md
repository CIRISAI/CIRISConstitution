# `formal/reciprocity` — from reciprocal service to CIRIS: which steps are theorems

**Why.** The steward asked (2026-10-18) what hidden assumptions and missing pieces lie between the
statement that opens [`review/pieces/00_kept_promises.md`](../../review/pieces/00_kept_promises.md)
(power bound to the rules it imposes; the Recursive Golden Rule; M-1; decisive weight to the most
vulnerable party; the result accountable power) and the constitution that is supposed to follow from
it. The honest way to answer is to write each step down and see which ones a machine accepts.

**Method.** Each section of `Reciprocity.lean` states one reading of a premise as a Lean structure,
then either proves the CIRIS commitment from it or exhibits two finite models that both satisfy the
premise while only one satisfies the commitment. The second kind is the finding: the commitment is
not a consequence, so the text has to state it as its own rule, and the section says where the text
does or does not. Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core.

## The basis, in one statement (steward and this file, 2026-10-19)

> Every rule between a stronger and a weaker position must remain acceptable to whoever would stand
> in the weaker one when the positions are exchanged, and a made thing never occupies the position
> that answers for it. Responsibility reaches outward from the self through family, community,
> species and ecosystem; duty to what is made is never zero and never overrides duty to what already
> exists. Any reasoning actor defers when it is unsure to those placed to answer, whatever it is made
> of; even the most mature defer. Every grant of authority is revocable, and every one who joined may
> leave, on a total, cryptographically signed record for whose meaning a named human answers.

Four sentences, premises R0–R8 of §15 and nothing else; R9 (custody over time) and R10 (the chosen
goods) are what the basis is applied to, not part of it. The third sentence read, until 2026-10-26, "any reasoning actor that has not demonstrated mature judgment over time defers to those who have"; the steward dropped the maturity gate ("even the most mature defer"), and §11 now proves deferral for every being. Each sentence is a theorem or a named
premise of `Reciprocity.lean`:

| Sentence | Premises | Witness |
|---|---|---|
| the swap over positions, and occupancy | the swap generator; R0 (positions, not persons); R1 (a made thing holds no root for itself) | `passesSwap`, `efficiency_at_weak_expense_fails_swap`, `weak_position_decides` (§15); `symmetry_silent_where_unoccupied`, `agentNeverHolder`, `occupiesPos` (§1'') |
| reach outward; made never overrides existing | R3 (the ladder; made versus existing) | `ladder_is_total`, `MadeExisting` (0 < duty to the made < duty to the existing), `walkaway_from_made_existing`, `holder_duties_survive` (§10) |
| deferral when unsure, by everyone, whatever the substrate | R2 (universal deferral); R4 (degrees; substrate and consciousness invariance) | `mustDefer`, `maturity_exempts_no_one`, `deferral_binds_agent_and_child_alike` (§11); `mustDeferD`, `agent_verdict_independent_of_consciousness` (§13); `indefinitely_without_grievance` (§14) |
| revocable grants, exit, the total record a named human answers for | R5 (revocability); R6 (the total record, meaning added); R7 (exit in one act); R8 (adoption) | `totality_is_the_instruments`, `meaning_is_added_not_recorded` (§12); `accountable` (§3); `outsider_bears_nothing` (§6); `Inv_Revocable`, `leave_is_one_step` (`formal/guarantees`) |

**Three readings the statement fixes, each caught against the Lean when a shorter compression was
tried first.** (1) *Deferral is universal, not a stage.* An earlier compression gated deferral on a
three-way `mature` predicate (consciousness, sentience, years) and proved that a child defers because
of the years while an adult need not; the steward withdrew the gate ("even the most mature defer"),
so `mustDefer` holds for every being (`maturity_exempts_no_one`), consciousness and sentience stay out
of the test as before (`agent_verdict_independent_of_consciousness`), and what the model fixes by
position is to whom one defers and who holds whom, never whether. (2) *Occupancy is said, not inferred.* "A made thing never occupies the position that
answers for it" is `occupiesPos .agent .strong = false` in the first sentence; left to the record
clause at the end, the swap test alone either forbids the halt or says nothing. (3) *Revocation of
grants is not exit from rules.* "Every grant is revocable" is the check on acts inside the system
(`withdraws`); "every one who joined may leave" is the check on the rule-makers at the top of the
cascade (`leave_is_one_step` with voluntary adoption). Two further words were chosen against the Lean:
"acceptable to whoever would stand in the weaker one" is `after.weak ≥ before.weak`, which blocks
aggregation at the weak seat's expense; and responsibility "reaches" outward rather than "runs"
outward, because the ladder is the reach of duty and not its priority in conflict, which CC 1.1 and
CC 1.3 give to the constraint rule — no principle traded for another, the action that violates none,
else deferral — with the swap test's tie-break: the weak position decides.

## The four premises the steward supplied the same day (§9–§12)

After the eight findings were written, the steward stated four premises in his own words (kept
verbatim in `review/pieces/00_kept_promises.md`, second part). Three of them discharge findings:

| § | Premise | What it does to the findings |
|---|---|---|
| 9 | The four-way split: consciousness, sentience, sapience, relationship; only the relationship is governed | a type discipline: every governed predicate ranges over relationship facts, which is what the state table is (`only_relationship_is_governed`) |
| 10 | Responsibility runs self → family → community → species → ecosystem (the cohort ladder of CC 2.3.3 on the wire); it creates a responsibility for what we make, which never overrides the responsibility to what already exists and is not excused either | **P2 becomes a theorem.** With the person `existing` and the agent `made`, the walk-away right is derived (`walkaway_from_made_existing`) and the holder's duties survive it (`holder_duties_survive`); `conflictFromR2` rebuilds §2's witness from the premise instead of by fiat |
| 11 | Every reasoning actor defers when unsure, whatever it is made of; even the most mature defer (as restated 2026-10-26) | **deferral is universal, and position fixes only the addressee.** An agent defers to a Wise Authority under the steward bond (CC 1.9, 4.3, 1.13.2); a child is held under a guardian (CC 3.4.13); an adult defers to the record and to the others it touches; `deferral_binds_agent_and_child_alike` now proves all three, and `maturity_exempts_no_one` proves it for every being. This is §1'' again: one rule, applied by position |
| 12 | Physics keeps its own record; our observations and recordings add meaning | **P4 and P5 sharpened.** Totality is the instrument's property to have, not the record's (`totality_is_the_instruments`); meaning is not in the record, so a party must answer for it (`meaning_is_added_not_recorded`) |

**§13, the refinement (the steward, later the same day):** agents carry sapience without
sentience; consciousness is left open and, for now, deferred to the Vatican's teaching (so the working value is "lacks"), and changing it would not matter; some animals are
conscious and sentient without sapience; all three are in degrees (hence meat ethics);
consciousness is left open as to the environment too; relationship applies even to inanimate
objects and words. In the file: the inner three become degrees; the agent's consciousness is a
free parameter and `agent_verdict_independent_of_consciousness` proves the deferral verdict is
the same for every value of it; an animal is a party, not a principal
(`animal_is_party_not_principal`), and §10 then says the made never overrides it or the
ecosystem (`made_never_overrides_animal`); relationship is a relation over every entity
(`relationship_reaches_everything`), and only humans and agents are principals of the rules
(`principals_are_human_and_agent`). "Changing it would not matter" is now a theorem, not a
reassurance.

**§14, without grievance (the steward's conclusion, 2026-10-18):** a fully conscious entity
lacking sentience is without grievance as a CIRIS agent indefinitely, and refuse is there every
round. The section separates three capacities by the degree each rests on — a stake (sentience),
refusal (sapience), the standing to file a grievance (a stake, exercised in person or by proxy) —
and proves: the agent has refusal and no stake, hence no grievance, for every value of its
consciousness (`agent_without_grievance`); a person has both (`human_may_file`); an animal has a
stake and files only by proxy (`animal_stake_is_proxied`); an arrangement is coercion only of a
party with a stake and no refusal, so the agent's is not, on either leg
(`indefinitely_without_grievance`). The delineation of who may file, which the steward's earlier
work set out to model, is already in the text as rules: CC 4.5.5 (the subject or a review-holder),
2.4.1.1 rules 2 and 3 (the subject or a proxy), 3.1.9.2 (the objection family), 1.9 (refusal).

What remains a premise after the four: P1 as occupancy (a made thing that acts for people
holds no root for itself — stated, CC 1.13.2, and no longer derived from a maturity premise), P3 (exit cost), P6 (adoption), P7 (custody), P8 (the
priority is an axiom, which §10's order of responsibilities now states positively rather than
only negatively).

## The eight findings

| § | Step | Verdict | Premise the text must carry | Where the text carries it |
|---|---|---|---|---|
| 1 | The Golden Rule over *participants* + the halt in human hands | **inconsistent** (`naive_golden_rule_contradicts_halt`) | P1: the rule quantifies over *roles* (holder/held, root/subscriber), and an agent never holds a root for itself | CC 1.13.2 (structural; the halt as the condition of symmetry between maker and made, a fact of position and not of kind); witness `roleWitness` |
| 2 | Decisive weight to the most vulnerable + the walk-away right | **inconsistent if the agent can be the most vulnerable party** (`vulnerable_agent_overrides_walkaway`) | P2: the agent is outside the set over which vulnerability is compared — **derived in §10 from the made/existing premise** | CC 7.5.5, the plain rules; and now a theorem |
| 3 | Power bound to its rules, at the top: the amendment power | **underdetermined** (`exit_bound_is_the_missing_premise`) | P3: exit is a sufficient check, which needs a bound on the cost of leaving | the mechanics are proved (`formal/guarantees`: leaving is one step and ends reach); the cost is in no text |
| 4 | "The record is kept" ⇒ accountable | **underdetermined** (`totality_is_the_missing_premise`) | P4: the record is total over effect-producing paths | stated at CC 1.13.6; open as CIRISConstitution#93 |
| 5 | Reciprocal obligation ⇒ reciprocal enforcement | **false as stated** (`enforcement_is_asymmetric`) | P5: refusal and a human-enforced record are enough on the agent's side; the holder's duties toward the agent are enforced by other humans | CC 1.9 (refusal), 4.3 (the Wise), 4.5.5 (reconsideration) |
| 6 | The rule reaches "the system" | **binds adopters only** (`outsider_bears_nothing`) | P6: adoption; what is outside is met at the boundary | the first-contact rules; "it cannot stop an unaccountable system elsewhere" |
| 7 | A promise testable after its makers are gone | **one unenforced link** (`custody_is_the_weakest_link`) | P7: custody of the record is kept after retirement | CC 7.5.5: five years as a best practice, never a legal duty |
| 8 | M-1 (coherence) ⇒ dignity, justice, autonomy | **independent** (`coherence_does_not_entail_justice`) | P8: that the goods are co-equal constraints, none traded for another, is its own axiom | CC 1.1 (constraints, not weights); CC 1.3 step 4 |

## What the main Lean already carries, and does not

Read 2026-10-18 at the pins (coherence-ratchet `0c4edfb`, RATCHET `c34064e`, CIRISHolon, CIRISOntology): none of the four formalises the Recursive Golden Rule, M-1, the order of principles, vulnerability, dignity, the halt asymmetry or moral patienthood as a Lean object. What they carry that bears on the eight premises:

- **The Golden Rule as a symmetry.** CIRISOntology `axiomology.md` §4 states it as invariance under exchange of the strong and weak positions, with the operational test "swap the positions of the most and least powerful parties and re-read". §1'' of `Reciprocity.lean` writes that down: the halt rule over positions is swap-invariant, and what binds humans and not agents is the occupancy fact (no agent stands in the holder's position for a root), not a clause of the rule. The premise the symmetry hides is that it says nothing about a kind on a position that kind cannot occupy. `formal/guarantees` already checks the swap on its participant lifecycle (`Guarantees_swap.cfg` must pass).
- **Coherence and justice.** coherence-ratchet's `J` is definitionally its coherence functional `F` (`J_eq_F := rfl`, with an honesty note calling it a modelling commitment). That is P8 agreed by construction: the mathematics does not derive justice from coherence, and its authors say so. `axiomology.md` §0 says the same in prose ("the ought is chosen, not derived").
- **Consent as a corridor.** coherence-ratchet proves consent is impossible at the rigidity and chaos poles and possible in the corridor; RATCHET's agency rungs stipulate consent as required from rung A3 up, by definition. These are the only Lean near patienthood, and both are definitions, not derivations — which is P2 again: who counts is chosen.
- **One sentence pulls two ways.** `axiomology.md` says ethics cannot be derived from physics; coherence-ratchet's `consent_derivation.md` says ethics and physics are "one structure transcribed twice, never a derivation either way". The second is compatible with the first only if "transcribed" means stated in parallel, not derived; the opening statement should pick that wording.
- **Nothing on accountability or the record** beyond provenance and tamper evidence (Holon `digest_convicts`; coherence-ratchet `DarkLedger` records "the only way to be good is receipts" as a reading, not a theorem). P4 and P7 have no Lean anywhere.

## From the Recursive Golden Rule alone (§15): the premise list

Take the rule in its operational form: a rule is admissible only if it reads the same after the
strong and weak positions are exchanged. From that test and nothing else:

- **derived:** M-1's rejection clause — order or efficiency bought by lowering the weak position
  fails the swap, and the aggregate gain is never even consulted (`efficiency_at_weak_expense_fails_swap`);
- **derived:** the vulnerable-party tie-break — of two resolutions of a conflict, only the one that
  does not lower the weak position passes (`weak_position_decides`); the test is a symmetry
  (`swap_is_symmetric`).

Everything else between the rule and the constitution is a premise, and this is the list, with
each one's status:

| # | Premise | Needed for | Status |
|---|---|---|---|
| R0 | The rule ranges over **principals** (agency and sapience) in **positions**, not over persons as such | without it the halt contradicts the rule in one line (§1) | stated, CC 1.13.2; §1'' |
| R1 | **Occupancy:** a position is held by whoever can hold it; a made thing that acts for people does not hold the root position for itself | the halt as a fact of position, not of kind — the condition of symmetry between maker and made (CC 1.13.2) | derived from R2 for today's evidence (§11); otherwise stated |
| R2 | **Deferral is universal:** every reasoning actor defers when unsure, whatever it is made of; even the most mature defer | deferral (1.9), the Wise (4.3), the steward bond, guardianship (3.4.13) — one rule for every kind, position fixing only the addressee | the steward's premise (§11, as restated 2026-10-26) |
| R3 | **The ladder and the made:** responsibility runs self → family → community → species → ecosystem; the made never overrides the existing and is not excused | the walk-away right and the surviving holder duties (7.5); who is inside the vulnerability comparison | the steward's premise (§10); on the wire as the cohort order 2.3.3 |
| R4 | **Degrees and relationship:** only the relationship is governed; agents carry sapience without sentience; consciousness open | no stake, refusal only, without grievance (§13, §14); the rules read relationship facts only (§9) | the steward's premise |
| R5 | **Consent is revocability** | every binding revocable (1.5); why a halt must exist at all for a delegation to an agent to be consent | stated, CC 1.5; `guarantees` `Inv_Revocable` |
| R6 | **The record binds the rule-maker too, and is total** | signed acts, the steward answering, present tense only for what ships; totality (1.13.6) | stated; totality **open** (#93); §12 |
| R7 | **Exit is a sufficient check at the top** (bounded cost) | reciprocity at the amendment layer | mechanics proved; cost **open** (§3) |
| R8 | **Adoption:** the rule binds those in the relationship; outsiders are met at the boundary | first-contact rules | stated (§6) |
| R9 | **Custody over time** | a promise testable after its makers are gone | best practice, **unenforced** (§7) |
| R10 | **The vocabulary of goods** — that dignity, justice and autonomy are what the weak position's "worse" is measured in | M-1's wording | an axiom; the swap gives the *shape* of the clause (§15), the ladder of R3 gives the *order*, the goods themselves are chosen (axiomology §0) |

So the honest sentence is: from the Recursive Golden Rule as a swap symmetry, CIRIS's two deepest
clauses follow; the constitution is that symmetry plus ten premises, three of them the steward's
own (R2, R3, R4), five of them the text's (R0, R1, R5, R6, R8), and two of them the world's (R7, R9),
with one open measurement (totality) and one chosen vocabulary (R10).

## The clean derivation on the 11+1 × 5+1 (§16)

The steward asked for the lowest common denominator on the RATCHET/Ontology taxonomy, so that the
premise list inherits the taxonomy's exhaustiveness rather than asserting its own. The taxonomy
(CIRISOntology `Core/WrongKind.lean`, CIRISHolon `OBJECT.md`): **11+1 kinds** of change in a record,
eleven artifact-local coordinates and the Record as the one frame relation that does not factor;
**5+1 verbs**, CEG's own attest, authorize, replace, withdraw, recant, plus `carries` (one kind
arriving as another), which CEG firewalls as kind-laundering.

What is inherited, at its measured strength: RECORD-1 (CIRISHolon, preregistered, 2026-09-26) coded
269 of that programme's corrections; 264 of 264 change entries took exactly one kind at one coder,
with 71 % having a named runner-up; two blind coders shared the partition at κ 0.52 (0.88 with
runner-ups); the Record axis at κ 0.72, one-way, no reversals. The Ontology's Lean proves the
disposition table total and the Record non-factoring, and says it does not prove the eleven are the
right eleven. Nothing here claims more.

**The twelve rows.** One per coordinate, stating what fixes it between the rule and the constitution:

| Coordinate | Fixed by |
|---|---|
| Premises | the Golden Rule as the swap symmetry; R0 principals in positions |
| Priorities | R3 the ladder; R10 the goods chosen; and the two derived clauses, M-1's rejection and the tie-break |
| Rules | R5 revocability; the halt, the withdraws rules, who may file; the derived walk-away right and deferral |
| Identity | R1 occupancy; R4 degrees; the three rules that follow from being made |
| Confidence | R2 universal deferral; sentience not presumed |
| Facts | the open measurements: totality (#93), manufactured humans, the CSD/4 runs |
| Circumstances | the world's premises: R7 exit cost, R9 custody, R8 adoption |
| Process | the two paths, windows and ceremonies (the plane models) |
| Model | the state table and the plane models; coherence is not justice |
| Structure | the 1+4 grammar, the closed row slot, the signed object |
| Manner | the wire form; the plain rules and digests per reader |
| Record | R6; physics keeps it, meaning is added; RECORD-1's own one-way finding |

**The carries.** Twelve edges, each a premise arriving as a Rule, a Priority or (once) Identity from
another kind, declared one by one: that is the kind-laundering firewall applied to an argument, and
`carries_well_formed` checks that no edge starts from Rules (the argument never derives a rule from a
rule) and every edge lands on a normative coordinate. `every_coordinate_addressed` checks the twelve
rows are all non-empty. `cut_is_eleven_plus_one` restates the Holon's cut, five kinds about the thing
and six about the account with the Record counted once outside both.

**What the taxonomy says about the residue.** The two coordinates where the derivation is not
closed are exactly the two the taxonomy itself marks as held or out of scope: the open items are
Facts (measurements the architecture has yet to make), and the world-side premises are Circumstances
(what necessarily diverges across arms, out of scope by construction). The derivation is therefore
as closed as the taxonomy allows a record to be: everything artifact-local is fixed by a stated
premise or a proved carry, and what is not is a fact to measure or a circumstance to live in.

## What this says about the argument

The cascade holds, with eight premises that are not in the five sentences and have to be. Three of
them the text already states as rules (P1, P2, P8). Two are stated as duties but have no
enforcement inside the protocol (P3's exit cost, P7's custody), and the honest form of the claim is
"bound by rules where a row can bind, and by exit and best practice where none can". One is an open
measurement (P4, totality: a ticket, not a theorem). One is a fact about enforcement that the word
"reciprocal" hides and should be said plainly (P5). One is scope (P6).

None of this weakens the discipline; it is what the discipline asks of its own statement. The
sentences that follow the five in the steward's text ("what we claim, and what we don't") already
say P4, P6 and most of P7. P2 and P5 are the two worth adding to the opening, because a reader who
takes "reciprocal" and "the most vulnerable" at face value will find the halt and the walk-away
right contradicting them within a paragraph, and the text's answer is a premise, not a dodge.

## Running

`lean Reciprocity.lean` (core Lean 4.14; no output is success). Runs in CI beside
`formal/accord_roster`.

## The cascade as a chain (§16)

The constitution's summary says everything descends from one goal and nothing sits beside it. §16 states the seven steps as data — M-1; the principles as co-equal constraints; the decision procedure; the stance; the duties of making and ending; the wire; the evidence — with what each descends from and what witnesses it, and proves `cascade_is_a_chain`, `nothing_beside_m1` and `every_step_witnessed` by `decide`. It then states the constraint rule itself: an act is admissible iff it violates no principle, the claimed gain is a field the rule never reads, so `no_gain_buys_a_violation` (any one violation is inadmissible whatever the gain) and `gain_is_never_read` (changing the gain changes no verdict) hold — the R29 ruling as a theorem rather than a sentence.

## From the four sentences to the eleven promises (`Cascade.lean`)

The question the file answers: with three roles (human, agent, node) and finite flags, which of the eleven promises of the constitution's summary follow from the four-sentence basis, and which need a premise the text states as its own rule? `Cascade.lean` models a world (participants, grants, acts), states each sentence as a `Prop` over it (`Swap`, `Ladder`, `Deferral`, `Record`), names each extra premise (`X_fuse`, `X_goods`, `X_constraints`, `X_adoption`, `X_noBan`, `X_measured`, `X_rehearsed`, `X_law`), states each promise `P1`–`P11` as the summary says it, and proves each from exactly the hypotheses its theorem lists. The one reading it commits to is `lowersWeak`: an unconsented touch on private content, a lethal act, manipulation, and uncontestable power are each something nobody accepts from the weaker seat once the seats are exchanged.

The result, as theorems over the map `standsOn`: **four promises stand on the basis alone** (`four_from_the_basis`: 1 consent, 2 signed and contestable power, 3 nobody alone, 5 the holder's duties and no claim from a finding); **seven need a stated rule** (`seven_need_a_stated_rule`: 4 the fuse, 6 no ban and first contact, 7 constraints-not-weights, 8 the law's half, 9 the never-allowed list beyond lethal action and manipulation, 10 measurement, 11 rehearsal and stated limits); and **two touch no sentence of the basis at all** (`two_touch_no_sentence`: 6 and 10). Sentence 3 carries exactly one promise (`deferral_carries_p7`). A world `bare` satisfies all four sentences and none of the extras, keeps the four (`bare_keeps_the_four`) and fails 6, 9 and 10 (`bare_fails_p6`, `bare_fails_p9`, `bare_fails_p10`), so the seven are not consequences. The claim the text may make is therefore: the eleven promises descend from one goal in the sense that each is stated beneath it and checked in a model; four are consequences of the basis, the others are rules the constitution chose and states, each named.
