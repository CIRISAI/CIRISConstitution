# The Constitution (ciris_constitution-1.0-rc11-constitution.pdf, 69 pages)

**Care score:** 5  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** Conflicting rules about halts, stewardship, withdrawal and erasure leave core powers open to incompatible implementations; these need a reconciliation pass before copyediting.

## Strengths
- The text separates conferral, acceptance, roster standing and agent action into individually specified decisions, providing identifiable places to resolve the contradictions below (pp. 18–26, 30).
- Takedown provisions distinguish notices, withheld bytes, destruction, reversal and subject-requested erasure, rather than treating them as one operation (pp. 50–52).

## Weaknesses
- **The halt has incompatible reach and effects.** Cutting an edge “MUST NOT remove” a node from an existing halt’s reach (p. 29), but cutting it means “the halt it holds then binds nothing that node runs” (p. 40). Nodes continue “serving” during a halt (p. 30), whereas resumption assumes “a halted node is not serving” (p. 33). The blanket “halt carries no TTL” statement also needs the later unconfirmed-halt fuse qualification (pp. 28, 30).
- **Stewardship has competing predicates.** The admission description requires an occurrence relationship “with a live delegates_to” (p. 11); the boolean lists alternative paths (p. 12); the normative clarification accepts “owner-binding edges alone” (p. 12); the next page explicitly permits stewardship through “a non-owner-purpose delegates_to” (p. 13).
- **Withdrawal has incompatible temporal effects.** A withdrawn delegation loses standing “for every claim ever made under it” (p. 19), but delegation withdrawal invalidates downstream authority only “for acts not yet taken,” leaving an already-issued licence standing (p. 55).
- **Erasure and geographic retention conflict.** An ordinary subject-bearing row “is erased” through the subject’s withdrawal (p. 52), but a withdrawn location proof remains with federation peers and its historical claim “is permanent” (p. 61). The latter section does not identify an exception to the erasure rule.
- **Equivocation is defined too broadly.** “Two heads for one lineage that each meet the witness quorum are equivocation” omits incompatibility or non-descent (p. 23). Read literally, ordinary successive witnessed versions satisfy it, despite the version-chain definition (pp. 21–22).
- **Non-rule material is extensive.** Examples include the “renamed” prefix narrative (p. 2); shipped-bundle migration exceptions (pp. 20–21); label-cutover instructions (pp. 31–32); retired fountain-storage commentary (p. 34); named current holders, household information and planned expansion (p. 36); implementation locations (p. 37); “Settled in CIRISAgent, carried as-is” (p. 59); and bootstrap deployment history and commitments (p. 63). Code/repository pointers also appear on pp. 27, 35, 45–46 and 69.
- **Editorializing and comparisons remain.** “A forced root is a walled garden” (p. 11), “the machinery is theater” (p. 43), the urgency appeal and website link (pp. 44–45), the claim about gaps other architecture classes “leave open” (p. 52), and “the controversy around option (c)” (p. 62) do not belong in rule text. The hash-database access comparison also conflicts with the no-comparisons house rule (p. 62).
- **Several quantitative or universal claims lack visible support.** These include the hardware trust multipliers (p. 35), a “few-hundred-byte signed proof-of-life” despite the hybrid-signature requirement (p. 41), the “~75-80% transparent translation rate” (p. 63), and what good-faith protection “in every jurisdiction turns on” (p. 68). No supporting register row is visible here; these are unverifiable from here.

## Opportunities
- Consolidate halt reach, latch effects, fuse and resumption into one authoritative statement, then replace conflicting summaries with references. This would remove several implementation forks without adding policy (pp. 28–40).
- Use one purpose-filtered stewardship predicate everywhere, and reconcile the existing withdrawal and erasure rules explicitly rather than relying on distant qualifications (pp. 11–16, 19, 52, 55, 61).
- Move deployment status, migrations, named-instance narrative, implementation pointers and design advocacy to the volumes already assigned those functions. Retain the rules and their register references here (pp. 1, 20–21, 27, 31–37, 59, 63, 69).
- Correct the stale “1-of-n sign-off” heading and “two codified subkinds” statement: the operative amendment threshold is a strict majority, and `public` is subsequently specified as a third subkind (pp. 3, 17, 42–43).

## Threats
- A hostile implementer can justify either escaping an already-fired halt or remaining bound by it, and either stopping data service or continuing it, using explicit text in this volume (pp. 29–30, 33, 40).
- The recovery promise depends partly on a removed design: owner-seizure recovery invokes “the same adjudication as the CC 4.2.6 restore path” (p. 14), while that section says “There is no restore and no contest” (p. 40). The WA procedure on p. 15 does not repair that cross-reference.
- A regulator could mistake the compliance tables for established legal sufficiency. A default of ≤30 days is not always inside a calendar month (p. 48); “primitives compose to ANY” framework overstates the informational mapping (p. 49); and the blanket “No content retention” instruction for NCMEC reporting needs reconciliation with applicable preservation duties (p. 51).
- The text itself records an unresolved governance defect: the WA board privilege has neither a bound nor an exit (pp. 44–45). Before the scale gate, amendment authority also rests with the founder or any accord-holder, including authority to move the gate itself (p. 43). A reviewer cannot treat the later quorum protections as protections currently guaranteed.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 28–30, 33, 40 | contradiction | Halt reach survives post-invocation exit on p. 29 but disappears on p. 40; data serving both continues and stops; the no-TTL summary omits the fuse. | Obtain one ruling on existing-halt reach; align every summary with the agent-only latch and confirmed/unconfirmed distinction. |
| 2 | 11–13 | contradiction | Steward-binding alternately requires combined relationships, alternative paths, owner-purpose edges only, and non-owner-purpose edges. | Publish one authoritative predicate and make the gate, examples and ownership distinction use it verbatim. |
| 3 | 19, 55 | contradiction | Delegation withdrawal retrospectively repudiates every claim on p. 19 but preserves completed acts on p. 55. | State whether these are different grant classes or competing rules; make their temporal scope explicit. |
| 4 | 52, 61 | contradiction | Subject withdrawal erases ordinary rows, yet location-proof history is permanently retained. | Resolve whether location proofs fall within erasure or an existing exception; distinguish retained audit metadata from retained subject claims. |
| 5 | 14–15, 40 | stale | Owner-seizure recovery cites an accord restore/adjudication path that the accord section expressly removes. | Point recovery to its actual surviving authority and procedure; remove the obsolete analogy. |
| 6 | 4, 6–7, 60 | contradiction | Admission requires a candidate’s proof cell to be contained within the community constraint, but examples use resolution 8–10 communities while proofs cannot exceed resolution 7. | Correct the examples or the intended containment direction; do not imply coarse proof establishes membership inside a finer cell. |
| 7 | 23–24 | unclear rule | Any two witnessed heads trigger equivocation as written, including successive versions. | Specify incompatible or competing heads and preserve ordinary witnessed descent. |
| 8 | 48–51, 68 | overclaim | Calendar-deadline, regulatory-composition, retention and universal legal-protection statements exceed the support shown. | Obtain legal verification, cite the supporting register rows, and distinguish document defaults from statutory requirements. |

## Rendering
- The supplied page text visibly truncates the severity identifier after `IncidentSeverity::INC` on p. 28.
- The named-moderator appointment expression is cut after `scope ⊇ {moderate|takedown|r` on p. 52; p. 53 resumes at `community_id`, leaving the scope expression incomplete.
- The subject-self membership expression is cut after `subject_of(content_sha` on p. 56.
- The long `evaluate_subkind_admission` reference appears cut before its closing text on p. 61.
- Code-comment continuations appear on separate lines without comment markers in the family example and proposal preimage (pp. 37, 41), making the rendered snippets ambiguous to copy.
- The HIPAA scope token is split mid-token across lines (`sh` / `are`, `pu` / `blish`) in the narrow table column (p. 49).
- These observations concern the supplied rendered-page text; visual margins, clipping and glyph fidelity cannot be independently confirmed without the PDF itself.

## Effort estimate
Allow roughly 30–45 hours for reconciliation, editorial relocation, legal-reference checking and a fresh PDF proof; the authority and temporal conflicts require steward rulings, while heading, cross-reference and layout repairs are mechanical.

<!-- model openai/gpt-6-astra-pro; 69 pages; prompt_tokens 184831; completion_tokens 6590; 83s -->
