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

## The eight findings

| § | Step | Verdict | Premise the text must carry | Where the text carries it |
|---|---|---|---|---|
| 1 | The Golden Rule over *participants* + the halt in human hands | **inconsistent** (`naive_golden_rule_contradicts_halt`) | P1: the rule quantifies over *roles* (holder/held, root/subscriber), and an agent never holds a root for itself | CC 1.13.2 (structural; the one asymmetry of kind); witness `roleWitness` |
| 2 | Decisive weight to the most vulnerable + the walk-away right | **inconsistent if the agent can be the most vulnerable party** (`vulnerable_agent_overrides_walkaway`) | P2: the agent is outside the set over which vulnerability is compared (sentience not presumed; pre-first-contact agents are not moral patients) | CC 7.5.5, the plain rules; necessary, not decorative |
| 3 | Power bound to its rules, at the top: the amendment power | **underdetermined** (`exit_bound_is_the_missing_premise`) | P3: exit is a sufficient check, which needs a bound on the cost of leaving | the mechanics are proved (`formal/guarantees`: leaving is one step and ends reach); the cost is in no text |
| 4 | "The record is kept" ⇒ accountable | **underdetermined** (`totality_is_the_missing_premise`) | P4: the record is total over effect-producing paths | stated at CC 1.13.6; open as CIRISConstitution#93 |
| 5 | Reciprocal obligation ⇒ reciprocal enforcement | **false as stated** (`enforcement_is_asymmetric`) | P5: refusal and a human-enforced record are enough on the agent's side; the holder's duties toward the agent are enforced by other humans | CC 1.9 (refusal), 4.3 (the Wise), 4.5.5 (reconsideration) |
| 6 | The rule reaches "the system" | **binds adopters only** (`outsider_bears_nothing`) | P6: adoption; what is outside is met at the boundary | the first-contact rules; "it cannot stop an unaccountable system elsewhere" |
| 7 | A promise testable after its makers are gone | **one unenforced link** (`custody_is_the_weakest_link`) | P7: custody of the record is kept after retirement | CC 7.5.5: five years as a best practice, never a legal duty |
| 8 | M-1 (coherence) ⇒ dignity, justice, autonomy | **independent** (`coherence_does_not_entail_justice`) | P8: the lexical priority is its own axiom | the PDMA order, CC 1.3 |

## What the main Lean already carries, and does not

Read 2026-10-18 at the pins (coherence-ratchet `0c4edfb`, RATCHET `c34064e`, CIRISHolon, CIRISOntology): none of the four formalises the Recursive Golden Rule, M-1, the order of principles, vulnerability, dignity, the halt asymmetry or moral patienthood as a Lean object. What they carry that bears on the eight premises:

- **The Golden Rule as a symmetry.** CIRISOntology `axiomology.md` §4 states it as invariance under exchange of the strong and weak positions, with the operational test "swap the positions of the most and least powerful parties and re-read". §1'' of `Reciprocity.lean` writes that down: the halt rule over positions is swap-invariant, and what binds humans and not agents is the occupancy fact (no agent stands in the holder's position for a root), not a clause of the rule. The premise the symmetry hides is that it says nothing about a kind on a position that kind cannot occupy. `formal/guarantees` already checks the swap on its participant lifecycle (`Guarantees_swap.cfg` must pass).
- **Coherence and justice.** coherence-ratchet's `J` is definitionally its coherence functional `F` (`J_eq_F := rfl`, with an honesty note calling it a modelling commitment). That is P8 agreed by construction: the mathematics does not derive justice from coherence, and its authors say so. `axiomology.md` §0 says the same in prose ("the ought is chosen, not derived").
- **Consent as a corridor.** coherence-ratchet proves consent is impossible at the rigidity and chaos poles and possible in the corridor; RATCHET's agency rungs stipulate consent as required from rung A3 up, by definition. These are the only Lean near patienthood, and both are definitions, not derivations — which is P2 again: who counts is chosen.
- **One sentence pulls two ways.** `axiomology.md` says ethics cannot be derived from physics; coherence-ratchet's `consent_derivation.md` says ethics and physics are "one structure transcribed twice, never a derivation either way". The second is compatible with the first only if "transcribed" means stated in parallel, not derived; the opening statement should pick that wording.
- **Nothing on accountability or the record** beyond provenance and tamper evidence (Holon `digest_convicts`; coherence-ratchet `DarkLedger` records "the only way to be good is receipts" as a reading, not a theorem). P4 and P7 have no Lean anywhere.

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
