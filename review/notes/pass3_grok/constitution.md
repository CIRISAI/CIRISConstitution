# The Constitution (ciris_constitution-1.0-rc11-constitution.pdf, 69 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The halt, the fire path, and the accord protocol are each stated both ways, a normative sentence is clipped, and instance history sits in the rules.

## Strengths
- Halt, confirm, and resume use separate canonical-byte domains, with the one-holder fuse stated as 86400 seconds unless the charter overrides it (pp. 29–33).
- T7 names stalled, non-admitting, and the one recovery widening, and says T7 does not evaluate `humanity-accord` (pp. 24–25).
- Immediate-removal versus counter-notice bases, withhold windows, and what a reversal can and cannot restore are stated as rules, not examples (pp. 50–52).

## Weaknesses
- Page 1 promises a halt "moves no trust state and touches nothing but an agent's act gate." T4 says a root is valid until revoked "by tombstone, withdraws/recants, supersession, or the halt latch" (p. 20). T8 then lists "the halt latched" inside NotRooted (p. 25) and requires Rooted only "on which no halt has reached this node" (p. 25), then invariant (v) says "V at t is the same with and without a latched halt" (p. 26).
- Fire is "taken over the live set" (p. 38) and "counted over the live set" (p. 39), while the same section's table says "one holder's signed row" with "no live set, no vote" (p. 38) and p. 40 says proposal objects "none of them exists on the fire path." The proposal preimage still allows `action=fire` (p. 40).
- The accord triple is "a family with `consensus_protocol: quorum:2/3`" (p. 8) and, later, `consensus_protocol: "majority"` (p. 37). Page 30 says thresholds are "never a fixed 2-of-3."
- A new `identity_occurrence` is admitted by "the root identity_key_id OR any currently-admitted occurrence" (p. 64). Page 13 says the next device's occurrence is signed by "the owner's own pen" and that "the owner's one approval signs" that occurrence.
- "this document draws no analogy between an agent and a child" (p. 12). The minor rule then says "The row and the gate are the same as for a node or an agent" (p. 16).
- CC 4.2.2.1 is cited for "Holder custody" (p. 25). In this volume 4.2.2.1 is "Hardware-class claim, and the attestation chain" (p. 35).
- The scale-gate revision condition is "if the register grows past a handful of entries" (p. 44). The next rule says a revision condition "MUST name its mechanical evaluator" because "a falsifier nothing evaluates is a ruling nobody can lose" (p. 45). "A handful" names neither check nor where it runs.
- The maker/made bound is "the first-contact act of CC 1.13.2, not yet defined" (p. 44). The WA-board row is carried with "Bounded by: unbounded as drafted" and "Exit: none" and "This cell is the finding" (p. 44).
- History, attribution, comparison, and code pointers are in the rules: "two of the three holders share a household" and a majority "from one street address" (p. 36); "Delaware/BFT posture" (p. 42); "the open-source projects this ultimately is" (p. 43); "Magnifica Humanitas encyclical mapping at ~75-80% transparent translation rate" (p. 62); `formal/trust_root/` (p. 27); `ciris_keyring::HardwareType` (p. 35); `ciris-registry-core` (p. 37); `PolicyCorridor.lean` and `TwoPath.tla` (p. 68).
- Pages 6–8 are a civic and emergency catalogue ("repurposed as votes", "bypass per-message consensus") with no non-normative label. "Why this is still 1+4" and "Zero new structural primitives" recur as argument (pp. 6, 16, 17). "The structural no-slavery guarantee" (p. 15) and "Why this isn't a Golden-Rule violation" (p. 37) are essays, not rules.
- Guardianship age is "age_self_declared / age_assurance:*" (p. 16) without saying which satisfies `age_band`. NCMEC filing under "US 18 USC §2258A" is a MUST on "the operator" with no jurisdiction limit (p. 50). Collision handling returns "409 IDEMPOTENT_CONFLICT" (p. 47) in a text that says HTTPS is outside the spec (p. 11).

## Opportunities
- Delete one side of each paired claim after a steward ruling: halt-as-validity (pp. 20, 25–26) versus halt-moves-no-state (pp. 1, 19, 26); live-set fire (pp. 38–39) versus one-row fire (pp. 30, 38, 40); `quorum:2/3` (p. 8) versus `"majority"` (p. 37). Do not add a third formulation.
- Mark pp. 6–8 non-normative or cut them. The infrastructure rules they interrupt are the operative text.
- Strike "not yet defined", the household sentence, the encyclical percentage, project comparisons, and repository paths. Point at register decimals already used in prose, not at trees.
- Repair the three clipped lines so the verifier can read the identifier, the scope set, and the subject-self sentence without guessing.

## Threats
- A hostile implementer can cite p. 20 and p. 25 to refuse federation while a halt is latched, and cite p. 1 and p. 26 (v) to keep serving. Both readings are in this volume. That breaks the cover promise that a halt "touches nothing but an agent's act gate."
- A hostile reviewer of the kill switch can cite "counted over the live set" (p. 39) against "no live set" (p. 38) and against `action=fire` still in the proposal bytes (p. 40). That is an earlier design left in the entrenched section.
- The accord's own protocol is `quorum:2/3` on p. 8 and `"majority"` on p. 37, while p. 30 forbids reading thresholds as a fixed 2-of-3. An implementer cannot fold the roster from this volume alone.
- The document ships a declared privilege that fails its own four-part test, says so (p. 44), and then imposes a mechanical-evaluator rule it does not meet (p. 45). The entrenched maker/made exit is "not yet defined" (p. 44).
- Named holders, a shared household, and "one street address" (p. 36) are personal facts in a rule text. The ~75–80% translation rate (p. 62) is an unsourced number. "Delaware/BFT" (p. 42) is a comparison the house rules disallow.
- Child-safety and takedown text will not survive a regulator: the under-18 gate can be read as self-declared age (p. 16); CSAM watchlists are "NEVER global" (p. 57); CyberTipline filing is stated as a universal operator MUST under a US statute (p. 50).

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 1, 19, 20, 25, 26 | contradiction | Halt "moves no trust state" and "the agent's act gate is the only gate that reads it" (pp. 1, 19); T4 revokes validity by "the halt latch" (p. 20); T8 puts "the halt latched" in NotRooted (p. 25) and says V is "the same with and without a latched halt" (p. 26). | Steward picks one. Delete the other sentences, including the halt clause in the NotRooted list or invariant (v), so p. 1 matches T4 and T8. |
| 2 | 38, 39, 40 | stale | Fire is "over the live set" (pp. 38–39) and also a pre-signed row with "no live set" (p. 38). `accord_proposal` still encodes `action=fire` though "none of them exists on the fire path" (p. 40). | Delete the live-set fire sentences and the `fire` alternative in the proposal preimage. Leave the one-row rule on pp. 30 and 38. |
| 3 | 8, 37 | contradiction | Accord family is `quorum:2/3` (p. 8) and `"majority"` (p. 37). | One token in both places. If the rule is "strict majority of the standing roster" (p. 30), the p. 8 `quorum:2/3` example is the leftover. |
| 4 | 56 | rendering | Normative sentence ends at "attesting_key_id ∈ subject_of(content_sha" and does not continue on p. 57. | Re-flow the line so `subject_of(content_sha256)` and the rest of the admit-(a) sentence are on the page. |
| 5 | 13, 64 | contradiction | Next-device occurrence is the owner's signature only (p. 13) or any already-admitted occurrence (p. 64). | State one signer. Cut the other sentence. |
| 6 | 44, 45 | unclear rule | Privilege bound "not yet defined"; WA row "unbounded" with "Exit: none"; revision tripwire is "a handful" with no evaluator, against the MUST in the next paragraph. | Delete "not yet defined" only by pointing at an existing act already named in CC 1.13.2, or mark the cell unresolved. Replace "a handful" with a check that already exists, or drop the condition. |
| 7 | 28, 52 | rendering | `IncidentSeverity::INC` is cut (p. 28); the full token on p. 31 is `INCIDENT_CONSTITUTIONAL`. Scope set breaks at "{moderate|takedown|r" (p. 52) and p. 53 does not restore `review}`. | Unbreak both lines. Do not leave the verifier to infer the missing characters. |
| 8 | 25, 35 | numbering | "Holder custody (CC 4.2.2.1)" does not match this volume's 4.2.2.1. | Retarget the cite or rename the local heading so the decimal is one section. |

## Rendering
- p. 2: reference printed as "CC 3. 1.7 R3" (space in the decimal).
- p. 4: "~5 km2" loses the superscript used in "∼250 km^2" on the same page.
- p. 28: `IncidentSeverity::INC` truncated; p. 31 has `IncidentSeverity::INCIDENT_CONSTITUTIONAL`.
- p. 52–53: `{moderate|takedown|r` clipped at the page boundary; `review}` does not reappear.
- p. 56: `subject_of(content_sha` clipped; the sentence does not resume on p. 57.

## Effort estimate
About two days: a mechanical day to cut the catalogues, code paths, comparisons, and clipped lines, and a steward day to rule the halt, the fire path, the accord protocol token, and who signs a device occurrence — those four are contradictions, not copy-edits.

<!-- model x-ai/grok-4.7; 69 pages; prompt_tokens 60532; completion_tokens 14040; 173s -->
