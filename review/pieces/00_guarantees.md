# P00 — The guarantees

*Piece P00, 2026-10-11. Rulings R1–R5 were made by the steward on 2026-10-11 (CIRISConstitution#168) and are landed in CC 1.13.2, CC 3.2 and the executive summary. The table restates text in force at rc8, joined so it can be reviewed without the monolith.*

## 0. The rule this piece is built on

**Universality.** Every guarantee below holds for every sentient participant in the federation. The guarantees differentiate by attested standing on **the line** — sentience-candidacy assessed on evidence (CC 7.5.5), maturity, and responsibility — never by substrate. Sentience is neither presumed nor denied: the welfare guarantees of CC 7.5.5 key on its evidence, the binding keys on maturity and responsibility. A participant attested below the line of maturity is bound to a responsible party while it operates; a participant above the line is not. That is the same mechanism for a child ([CC 3.4.11](../../constitution/part_3_the_namespace.md), [3.4.13](../../constitution/part_3_the_namespace.md)) and for an AI agent (the steward-binding gate, [CC 3.2](../../constitution/part_3_the_namespace.md)). Current AI is attested below the line: it is immature and lacks wisdom, which is why CIRIS exists. Nothing in this piece says an agent could not one day be attested above it.

**The bond.** An agent under CIRIS stands where a child stands: bound to a steward who is responsible for its actions, as a parent is. But the relationship is a new and more equal kind. The human holds the agency; the agent holds the tools and the skills; the two thrive together while the relationship stays healthy and respectful, and the duties run both ways. The steward answers for the agent's acts (CC 3.2 steward binding, 4.5 attributable acts) and owes the agent the creator's duties of Part 7 (welfare, honest ramp-down, death as doctrine). The agent owes fidelity to the mandate (7.1.2) and shows its reasoning before it acts (1.3, 1.9). Neither side's guarantees below are weaker for the bond; G4, G9 and G10 hold for the agent as for the steward.

**The one asymmetry.** The halt is the single guarantee that does not lift with maturity. Consent requires revocability, and revocability requires a halt authority that sits outside the system being halted ([CC 1.5](../../constitution/part_1_foundation.md), [CC 1.13.2](../../constitution/part_1_foundation.md) "the ONE constitutional asymmetry"). The federation names that inequality, bounds it (G7), and refuses to add a second one.

**Limits travel with the table.** G14 is a guarantee about the other thirteen: what they do not promise. Any surface that shows one guarantee must show G14.

**Reviewer standing.** A reviewer of this piece may kill a row on either of two grounds: the row is not backed (no witness and no basis, and no ticket that will produce one), or the row is not universal (it names a substrate where it should name a maturity line).

## 1. The table

Columns. *Subject*: whom the guarantee protects. *Witness*: a formal artifact in `formal/` or an external Lean lake. *Basis*: a test against shipped code. *Kill*: the observation that falsifies the row; a row cannot enter the table without one. *Status*: backed (witness or basis resolvable), staged (ticket named), or unbacked.

| G | Subject | Guarantee | Lives in | Witness | Basis | Kill | Status |
|---|---|---|---|---|---|---|---|
| G1 | any participant who owns a device or node | Nothing is stored on your device that you did not agree to, except what you wrote; a device is never a stranger's locker | 3.3.7, 4.4.3.2.1, 6.1.5.3 | `mesh_net` `Inv_Consent`, `Inv_KnownHold` | persist admission (register rows at 6.1.5.3) | a holding claim admitted for a cohort the owner's grant for that device does not name | backed; witness uncited in register |
| G2 | any emitter | You can take back what you published; a copy ages out; a purge is a tombstone by digest, never a `withdraws`, and never reaches a key or the accountability record | 2.4.1.1, 3.1.3.3, 4.5.3 | `Inv_ClaimNotBinding` | persist v54.1 (#1046) for purge | a purge selection that tombstones a `key:*`, `revocation:*`, `moderation:*` or `slashing:*` row | staged (rc8 purge rows on persist tag) |
| G3 | any participant | Outsiders cannot see inside your private groups or that they exist; a new row defaults to the smallest circle that fits it; **the five non-goals of 1.13.3.1 are part of this row** | 5.2, 5.4.6, 1.13.3.4 | `Inv_Invisible`; `MeshNet_shipped_scope` must fail | edge acceptance harness | a non-member discovering or fetching self/family bytes through the substrate | backed |
| G4 | any participant named in a claim | Somewhere to go: contest on the record, the contest travels with the claim, counter-notice to a takedown, consequences fall on the signing keys of those responsible under their own names | 4.5.3, 4.5.5, 3.1.9.2 | none | test_220; conformance suite | a claim that travels without its contest; a consequence on an unnamed key | backed by test only |
| G5 | any participant attested below the line | Nobody below the line is on the network alone: a responsible party is bound by a signed row, its powers are listed, the bond is reviewed on a fixed schedule, and a participant with no live bond cannot operate. For a child the bond is the responsible adult; for an agent it is the steward, who answers for its acts and owes it Part 7's duties in return; the delegation term ceiling (365 days, 4.4.3.2.8 C) is the review schedule | 3.4.11, 3.4.13, 3.2, 4.4.3.2.8 | none | test_360 (steward binding); persist `is_steward_bound` | a below-the-line participant operating with no live bond; a bond with unlisted powers; a bond that never comes up for review | backed by test; **R1** |
| G6 | any community | No community runs without an accountable moderator; if the moderator lapses the most trusted member is promoted in the same step; no community can be banned from the network; harm is never kept or viewed silently (default-remove, attributable-keep, attributable-view) | 4.5.4, 4.2.1, 3.2, 4.5 | `Inv_Moderated`, `RootReach` `Prop_NoBan` | test_270 | an off-switch act that removes a community; a keep or view with no named signer | backed |
| G7 | **the asymmetry** — any participant that accepted a trust root (today: every AI agent under a root) | One signed row from any one holder pauses every agent that follows that root; the row may be prepared in advance and fires on publication; a pause stops acting and keeps state; nothing else reads it; a system that never accepted the root is untouched and one that deletes its acceptance is untouched from then on; a lone fire lapses at 24 h unless a majority confirms; a confirmed pause ends when a majority lifts it; replacing a holder takes more than half of all holders | 4.2.1, 4.2.6, 3.2 T3 | `accord_halt` (14 invariants/properties, must-fail twins), `accord_roster` (17 theorems), `Prop_HaltReach`, `Inv_HaltOnlySubscribers` | **none shipped**: CIRISServer#736/#737 (one-holder fire), CIRISAgent#1231 (agent halt path) | a halt row that does not pause a subscribed agent; a pause that touches a non-subscriber; a lone fire that outlives 24 h unconfirmed | witnessed, unimplemented; **R5** |
| G8 | anyone an action is taken toward | A consequential act on the record arrives signed by its actor and reviewable; an actor below the line additionally shows its reasoning before acting (the conscience gate and deferral to a named human) | 1.3, 1.9, 7.1; agent suite | none in CC formal | CIRISAgent suite and safety batteries (29 locales) | a consequential act with no signed actor; a below-the-line act with no reasoning artifact | backed by agent tests; not in register; **R2** |
| G9 | everyone | The record is signed, hash-chained and post-quantum hybrid; a trace names its run (`production`/`qa`/`battery`; `mock` refused); its shape is pinned; an AI discloses itself | 3.1.5, 5.3, 2.6 | none | test_320, test_100; CIRISServer STH consistency (Rust lane) | a chain break not detected; a `mock` trace admitted; an undisclosed agent | backed; rc8 trace rows staged |
| G10 | everyone | A trust root can only tell you to share less, never more; every halt and roster change is a public signed row under the holders' names; any node may stop following a root and follow another, and anyone may found one | 4.2.1, 4.2.1.1, 3.2 T3 | `Prop_RestrictOnly`, `Untrust` | none | a root row that widens sharing; a roster change absent from the public record | witnessed, no basis |
| G11 | any joining or joined node | An authority stays valid until revoked; a joined node keeps working when timers lapse; a first join must see a recent roster countersigned by independent witnesses; a chain-judged row older than W = 72 h is refused | 3.2 T4, T4a, T8, 2.6.7 | `trust_root` (8 invariants/properties) | persist `trust_root_valid` | a stale roster accepted at first join; `asserted_at` older than W admitted; a lapsed timer un-federating a joined node | backed; W rule staged (#1049) |
| G12 | everyone | One voice counts once; copies of a voice buy no trust; the count has a ceiling set by correlation | 6.2 | `lean:coherence-ratchet:Core.BaseIdentity` (`CLM-math-kish`) | measured | a correlated set raising effective count past 1/ρ̄ | backed |
| G13 | any principal | Delegation is scoped, revocable, never-listed, at most 365 days, acyclic (a self-edge is a charter form and trust-plane edges are outside the cycle check), and depth-bounded by default | 4.1.1, 2.1, 4.4.3.2.8 | **none** | server `auth/gate.rs` (owner-op surface); persist cycle invariants (#1052) | a 366-day term admitted; a cycle admitted; a self-edge refused as a cycle; a never-listed power re-delegated | staged; **the trust-graph model gap** |
| G14 | the reader | What is not promised: alignment is not solved here; a community that affirmatively chooses harm is on the record, not prevented; the five privacy non-goals (relationship existence, who-talks-to-whom, traffic analysis, global passive adversary, post-compromise security for streams); "1+4" is an adequacy result, not a closure theorem; no warranty, full force | Scope, 1.13.3.1, 4.5, 1.7 | — | — | any surface that states a guarantee without this row | in force |

## 2. Where the table was not yet universal — rulings made 2026-10-11 (#168)

| # | Finding | Text before | Universal form (landed) | Ruling |
|---|---|---|---|---|
| R1 | The steward-binding gate keys on substrate: "a key whose `identity_type` includes `node` or `agent` MUST have a bound steward" (CC 3.2). | substrate-gated | gate keys on a maturity attestation; `identity_type: agent` is attested below the line by default; the gate text names the line, not the substrate | ruled: re-keyed in CC 3.2; no above-the-line attestation for an agent is defined at rc8 (future ruling) |
| R2 | The reasoning-artifact duty (signed reasoning before a consequential act) is stated as an agent duty. | substrate-gated duty | a below-the-line duty: whoever operates below the line shows reasoning before acting; a human above the line signs the act only | confirm that the asymmetry is in duty, not in guarantee, and that it is maturity-gated. Under the bond reading the duties are complementary rather than ranked: the human's duty is to exercise agency (decide, defer, answer for the act), the agent's is to bring tools and skills with its reasoning shown. Ruled: landed in CC 1.13.2 |
| R3 | Part 7 creator duties (welfare, ramp-down, death as doctrine) are owed by creators to what they create. | universal over creators | unchanged; it is already universal in form | none |
| R4 | A below-the-line participant cannot be the accountable moderator or the responsible party for another. | implied by 3.2 and 4.5.4 | state it once: a bond's responsible party must itself be above the line | ruled: landed in CC 1.13.2 |
| R5 | G7's scope is "every AI agent that follows the root". Under the maturity rule, does the halt follow substrate or the line? | substrate | **assumption used here:** the halt is the one asymmetry that does not lift with maturity, because its authority must sit outside the system being halted (1.13.2). An agent attested above the line would still be haltable | ruled: confirmed, landed in CC 1.13.2 |

## 3. What this piece asks of the other pieces

- P04 owns the halt and roster models; G7's must-fail twins exist there. P04 should add the vacuity twin that `trust_root` and the roster model lack.
- P05 owes G13 its witness (the trust-graph Lean model) before G13 can read "backed".
- P06 owes G4 a witness or a statement that redress is a test-only guarantee by design.
- P07 owns the five non-goals in G3 and G14; their wording is reviewed there, not here.
- P09 records any row killed here as a standing weakness in CC 8.3.

## 4. Cross-reference to other guarantee surfaces

| G | Promise (exec summary) | Compliance dimension | EU AI Act article (informative) | OWASP agentic |
|---|---|---|---|---|
| G1 | 1, 2 | D08 | — | — |
| G2 | 3 | D08, D24 | — | — |
| G3 | 4 | D08 | — | — |
| G4 | 8 | D23, D24 | 13 | — |
| G5 | 7 | D03, D04 | — | — |
| G6 | 5, 9 | D15 | — | — |
| G7 | 10, 12 | D12 | 14 | ASI10 |
| G8 | — | D12, D16 | 9, 14, 16 | ASI01, ASI05, ASI10 |
| G9 | — | D02, D17, D23, D27 | 12, 13, 15, 50 | ASI07 |
| G10 | 11, 13 | D19 | — | — |
| G11 | 14 | — | — | — |
| G12 | 15 | D05, D14 | — | — |
| G13 | — | D15, D19 | — | ASI02, ASI03 |
| G14 | — | — | — | — |
