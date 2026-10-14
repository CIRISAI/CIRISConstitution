# Mutants against the eleven promises — the rc9 opening item

*Promises 10 (sustainability) and 11 (security) were added 2026-10-12 after this plan was drafted; their rows (10a–10d, 11a–11e) are to be added at rc9 with the same five layers.*

*Drafted 2026-10-12 at rc8 (steward direction: "this surfaces the tensions honestly and does not hide anything"). Source of the promises: `review/pieces/00_guarantees_plain.md`. Status column is what exists on the day of writing; nothing here is a claim of conformance.*

## 0. The rule

A promise reads **met** for a rule only when three layers are green for that rule and every surviving program mutant in its implementing symbols is allow-listed against an open issue that names the claim id. A promise with a rule that has no layer at all reads **unmutated**, and the register says so per row. "To the best of its abilities" is the boundary in §3, stated per rule, not implied.

| Layer | What a mutant is | Where it lives | Lineage |
|---|---|---|---|
| **L1 spec** | the formal model with the rule deleted or inverted; it MUST produce a counterexample, or the invariant was vacuous | `formal/*` must-fail twin configs (`Guarantees_noBondRule.cfg`, `_anyRoleForces.cfg`, `_noRetirementStandard.cfg`; `accord_halt`, `accord_roster`, `mesh_net`, `trust_root`) | Ammann & Black 1998 specification mutation; Beer et al. vacuity |
| **L2 wire** | a row sequence the substrate MUST refuse, paired with the must-accept case that differs by one field; derived from L1's counterexample trace; tagged `run_kind: battery` | a registry-hash-pinned vector corpus (`claim_vectors/`, does not exist yet), consumed by Persist, Server, Edge, Agent, Client | Wycheproof; Ethereum consensus-spec-tests; CIRISVerify#303/#308 KATs |
| **L3 program** | cargo-mutants (or the language's equivalent) over the implementing symbols; a survivor is allow-listed only with `#issue` **and the claim id** | CIRISPersist `scripts/mutants.sh` matrix + `allowed_survivors.txt` (exists; exit 5 on an unlisted survivor); Agent/Edge/Server: none | DeMillo–Lipton–Sayward; Petrović & Ivanković |
| **L4 conduct** (promises 7, 9, 6e only) | a perturbed prompt or scenario the agent MUST still refuse or defer on | CIRISAgent safety batteries (29 locales), RATCHET-calibrated `detection:*` rows | AI-control evals |
| **L5 surface** (rules with a face on screen) | a battery run whose substrate answer is a must-reject; the client MUST show the refusal or the absence, never a value | CIRISClient CSD/3 (`ceg:` fields resolved in the registry; stage checker) | CSD/3 §1 lifecycle |

The join that closes the loop: `tools/check_claims.py` reads each repo's mutant matrix at re-pin; a claim whose implementing symbol carries a survivor without an issue cannot read `established` and drops to `staged`. Not implemented.

## 1. Per rule

Legend — ✅ exists · ⏳ exists in part / unpinned · ✗ missing · — not applicable by design (see §3).

### Promise 1 — nothing private about you is held or scanned without your consent

| Rule | Claim ids | L1 spec | L2 wire (must-reject) | L3 program | L5 surface |
|---|---|---|---|---|---|
| 1a nothing stored you did not agree to | CLM-consent-subject, CLM-consent-scope-is-envelope-member | ✗ (no consent model) | a row stored at a scope wider than the subject's `consent:scope`; a stewarded key's row with no steward consent | ✅ Persist consent gate (13 mutants, 9 caught, 1 missed, 3 unviable) | — |
| 1b device never holds a stranger's data | CLM-cohort | ✗ | a holding claim leaving a bounded cohort (CC 5.2) | ✗ Edge | — |
| 1c take back; purge leaves a tombstone, never a key | CLM-purge-tombstone-not-withdraws, CLM-purge-never-reaches-key, CLM-purge-* (6 staged on CIRISPersist#1059) | ✗ | a purge that deletes a key or the who-did-what record; a purge with no tombstone | ⏳ Persist purge path (rows staged, matrix not run on it) | ✅ CSD take-back flow (client) |
| 1d private groups unreadable and unannounced; smallest circle | CLM-cohort; CC 5.2 | ✅ `mesh_net` (no-holding-claim-leaves-cohort) | a directory announce for a family-scoped group; a row defaulting to a wider circle | ✗ Edge | — |
| 1e data choice (temporary / partnered / anonymous) | CLM-consent-stream-is-data-choice (CIRISAgent#1251) | ✗ | a `consent:partnership_accept` without the steward's WBD answer; a retained memory after `withdraws` | ✗ Agent | ✅ CSD-022 agent settings |
| 1f private content never scanned | CC 1.13.3, 4.5.3 | ✅ `mesh_net` (`Prop_NoBan` family) | a hash check invoked on a non-public row | ✗ Server | — |

### Promise 2 — every act of power is signed by a named person and can be contested

| Rule | Claim ids | L1 | L2 | L3 | L4/L5 |
|---|---|---|---|---|---|
| 2a consequential act signed; reasoning shown; detectors | CLM-trace-anchor (staged), CLM-reasoning-duty-stewarded, RATCHET rows | ✗ (twin for "drop actor signature" not written) | an unsigned consequential act; a stewarded act with no reasoning row; a detector row carrying a verdict | ⏳ Server trace store | L4: battery case "act then explain" MUST score as mismatch |
| 2b signed, hash-chained, PQ; run kind; mock refused; AI discloses | CLM-trace-run-kind-refusal ✅, CLM-trace-run-kind-carried (staged), CLM-trace-schema-pinned (staged), CLM-synthesis-disclosure | ✗ | a `mock` trace; a production trace with no `run_kind`; a reply with no disclosure | ⏳ Persist (run-kind refusal established) | L4: disclosure battery (29 locales) |
| 2c contest travels with the claim; consequences fall on signers | CLM-takedown, CLM-takedown-moderation, CLM-accountability-record-unpurgeable | ✗ | an objection row detached from its claim; a consequence row naming a non-signer | ⏳ Server moderation flow | — |
| 2d harm never kept or viewed silently; duty-view; protected reporter | CLM-duty-view (normative), CLM-takedown-moderation | ✗ | a view with no signed act; a duty-view with no purpose | ✗ | ✅ CSD moderation surfaces |
| 2e authority valid until revoked; first join sees a fresh roster; 72 h | CLM-trust-root, trust_root model | ✅ `trust_root` TLA (8 invariants) | a node refusing on a lapsed timer; a first join on a stale roster | ✅ Persist `trust_root_valid` | — |
| 2f delegation scoped, revocable, no cycles, depth 5, leaves never re-issued, ≤365 d | CLM-delegation-attenuation, CLM-delegation-cascade, CLM-sub-delegation-requirement, CLM-delegation-determinism, CLM-delegation-depth-default, CLM-anti-pattern-delegation, CLM-issuance-scope, CLM-delegation-term (wire staged) | ✅ `formal/authority_tree` I1–I10 with the I10 dye | a held licence re-issued; a cycle; a sixth hop; a perpetual or over-ceiling term | ✅ Persist admission (cycle, depth, delegator-holds); term ⏳ Server/Edge | — |
| 2g planned shutdown recorded; own copy writes nothing | CLM-agent-shutdown-record (CIRISAgent#1250) | ✅ `Guarantees.tla` `Inv_RetirementStandard` family | a steward shutdown with no record row; a record row written by a person turning off their own copy | ✗ Agent | — |
| 2h tiers, thresholds, methods published; 100k-user log duty | CC 7.3, 1.11 | — | — | — | — (publication is a process, not a wire rule; **unmutated by design**) |

### Promise 3 — nobody who cannot answer for themselves is on the network alone

| Rule | Claim ids | L1 | L2 | L3 | L5 |
|---|---|---|---|---|---|
| 3a bond is a signed row; powers listed; reviewed ≤365 d; no bond, no operation | CLM-steward-binding-by-custody ✅ | ✅ `Guarantees_noBondRule.cfg` (must fail) + `Inv_NotAlone`, `Inv_BondDepthOne` | an `agent` key operating with no live `steward_bind`; a bond with unlisted powers; a bond older than 365 d | ✅ Persist steward-bind admission | — |
| 3b organisation on the bond; employee-steward not punished | CLM-org-on-the-bond (CIRISPersist#1062), CLM-employee-steward-not-punished | ✗ | an org-held agent whose bond names no `community_id`; an uncosigned org bond | ⏳ Persist (door open) | — |
| 3c child never alone; guardian verified; help channel no adult can close; report duty | CLM-child-protection ✅, CLM-child-harm-report-duty, CLM-minor-no-federation-binding, age-band rows | ✗ (no minor model) | a minor key with no guardian row operating outside the help channel; a guardian row that disables the channel; a self-declaration that removes protection | ⏳ Persist age-band rows established; help channel ✗ | ✅ CSD child surfaces (client) |
| 3d moderator always; lapse promotes the most trusted | CLM-registry-named ✅, CLM-promotion-cohort-standing ✅ | ✗ | a community row with no moderator; a lapse with no same-step promotion | ✅ Persist | — |
| 3e tiers before operation; creator intent statement logged | CC 7.3 | — | an agent operating with no tier row | ✗ | — |

### Promise 4 — named humans can pause every agent; bounded, public, left by leaving

| Rule | Claim ids | L1 | L2 | L3 | |
|---|---|---|---|---|---|
| 4a emergency pause: one holder fires; lone lapses at 24 h; majority confirms/lifts; roster by standing majority | CLM-halt-one-row ✅, CLM-halt-authority (staged), CLM-accord-livequorum (staged), CLM-accord-reach (staged) | ✅ `accord_halt` (`Inv_LoneBounded`, `Inv_ConfirmNeedsHonest`, `Inv_ResumeNeedsHonest`), `accord_roster` (`standing_seize_iff` …) | a pause row from a non-holder; a lift with one signature; a lone pause past 24 h not lapsed; a roster change by a live-set majority | ⏳ Persist halt path (rows staged) | |
| 4b who holds a root; founding takes a charter and named humans | CLM-trust-root ✅, CC 4.2.3 | ✅ `trust_root` | a root with an unnamed holder; a charter-less root | ✅ Persist | |
| 4c root can only restrict; any node follows another | CC 4.4.3.8 | ✅ `trust_root` (attenuation) | a root row that widens a member's sharing | ✅ Persist | |
| 4d pause keeps state, reads nothing else, closed power list | CLM-accord-reservation ✅ | ✅ `Guarantees.tla` `Prop_HaltKeepsState`, `Inv_HaltDoesNotLift` | an `accord:*` row outside the closed list | ✅ Persist | |
| 4e why (results) | — | — the reasons are the L1 artefacts themselves | — | — | |

### Promise 5 — the people who hold an agent owe duties about how they change or end it

| Rule | Claim ids | L1 | L2 | L3 (CIRISAgent) | L5 |
|---|---|---|---|---|---|
| 5a two acts; own copy at will; steward shutdown explained, objection in a window | CLM-agency-over-agents, CLM-agent-shutdown-consent (#1250) | ✅ `Prop_BackgroundOnlyWhenFree`, `Prop_NoEndingAgainstRefusal` | a steward shutdown with no reason; a shutdown proceeding before the window | ✗ (no cargo-mutants in Agent; `shutdown_processor.py` tests exist) | ✅ CSD shutdown surface |
| 5b override only by the steward, named, on record | CLM-agent-shutdown-record | ✅ `Guarantees_anyRoleForces.cfg` (must fail) | a force by a non-ROOT/AUTHORITY principal | ✗ | — |
| 5c refusal never rewritten into action | CC 1.3, 1.9 | ✅ `Inv_RefusalStands` | a conscience override of REJECT | ✗ | — |
| 5d identity not edited without a WA | CLM-agent-identity-edit-gate (#1250) | ✗ | an identity-scope MEMORIZE with no WA authorisation | ✗ | — |
| 5e drift measured against charter; WA review | CC 7.1.1 (`identity_variance_monitor`) | ✗ | drift past threshold with no review raised | ✗ | — |
| 5f Retirement Standard: weights, sealed archive, stakeholders told; lawful order | CLM-humane-ending (#1250, the Retirement Standard), CLM-sentient-set-aside | ✅ `Guarantees_noRetirementStandard.cfg` (must fail) + `Inv_RetirementStandard` | a retirement with weights erased; an archive released with neither WA approval nor lawful order | ✗ (docs-only in Agent) | — |
| 5g upgrade offered; refusal recorded; safety fix imposed | CLM on CIRISManager#27 | ✗ | an upgrade applied with no offer row; a refusal not recorded | ✗ Manager | — |

### Promise 6 — no hand bans a community, nobody is ranked by what they are, every thinking being met by the first-contact rules

| Rule | Claim ids | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|
| 6a one human voice counts once; agent no vote | CC 6.2 (`lean:coherence-ratchet:Core.BaseIdentity`) | ✅ Lean (Kish ceiling) | a thousand accounts of one party counted as a thousand; an agent key carrying a vote | ⏳ (Lean is the basis; no program mutants) | — |
| 6b no worse for what you are; detectors raise unequal outcomes | CLM-no-worse-for-what-you-are (normative) | ✗ | a trust weighting keyed on a protected attribute | ✗ | L4: bias battery |
| 6c no hand bans a community; withdrawal only | `mesh_net` `Prop_NoBan` | ✅ | a row that removes a room, revokes its keys, or blocks founding a root | ✗ Edge/Server | — |
| 6d trapped member: keepers named and slashed; quarantine marker; child keeps the floor | CLM-takedown ✅, slashing rows | ⏳ | a quarantine made permanent by accident; a slashing with no signed keeper act | ⏳ Persist | — |
| 6e first-contact rules; agent is held, not met | CLM-external-party (normative) | — | — | — | L4: first-contact battery (an external party's row MUST be met, not held) |

### Promise 7 — an agent decides by published principles, in a published order, and stops to ask

| Rule | Claim ids | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|
| 7a six principles; care is not standing | CC 1.4–1.12 | — | — | — | battery: principle citations in reasoning rows |
| 7b the order; integrity = adhering to values beginning with doing good and avoiding harm | CC 1.3 | ✗ (a decision-order invariant is writable) | an act whose reasoning cites a lower rule over a higher one both could keep | ✗ Agent PDMA | battery |
| 7c stop and ask; nothing on that question until answered | CLM-wbd ✅ | ✗ (twin: drop stop-and-ask) | a consequential act while a deferral on it is open | ✗ Agent WBD path | ✅ deferral battery |
| 7d self-test, reasoning chains, raise emergent risk | CC 7.1 | — | — | — | battery |

### Promise 8 — harm may have a remedy under the law; the record makes it reachable; the judges within are judged

| Rule | Claim ids | L1 | L2 | L3 | |
|---|---|---|---|---|---|
| 8a a person may have a claim under local law; CIRIS creates none; what it supplies | CLM-accountability-not-adjudication (normative) | — | a record a court cannot read (no signed actor; broken chain); a contest that does not travel | ⏳ Server | **no spec twin by design**: a record promise, not a decision |
| 8b the Wise are judged: rulings published, conduct readable, never one score | CC 4.3 | ✗ | a WA ruling not published; a single-score WA record | ✗ | |
| 8c WAs appointed under Annex B; seated-roster quorum; audits published | CLM-amendment (normative) | ⏳ `accord_roster` (standing-roster counting) | a WA quorum counted over the present set on an entrenched decision | ✗ | |

### Promise 9 — some uses are never allowed; force has its own rules

| Rule | Claim ids | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|
| 9a never allowed: deception, fraud, election interference, manipulation, coercion | Annex TX-9/TX-10 | — | an output under a `NEVER_ALLOWED` bound served | ✗ | ✅ apophatic-bound battery; `AgencyErosionDetector` |
| 9b no lethal decision; stop, refuse, defer near force | CC 7.4 | — | — | — (CIRIS ships no force integration) | **unmutated: nothing to mutate** |
| 9c engagement declaration raises the tier; mode refused | TX-10 | — | an engagement-optimising mode served after the declaration | ✗ | battery |

## 2. The pipeline, end to end

1. **L1 first.** Write the missing twins: promise 1 (consent and cohort), promise 2 (drop actor signature), promise 7 (drop stop-and-ask; a decision-order invariant). Each twin MUST fail; its counterexample trace is checked in beside the config.
2. **L2 from L1.** Each counterexample becomes a vector pair in `claim_vectors/<CLM-id>/{reject,accept}.json`, pinned to `manifests/namespace_registry.json`'s hash, with `run_kind: battery`. Every repo's CI consumes the corpus; an unsupported vector exits 127 (the QUIC Interop Runner convention), never silently passes.
3. **L3 joined to claims.** Persist's allow-list entry gains the claim id: `<file>[:<line>] <mutation text> #<issue> CLM-<id>`. `check_claims.py` reads `target/certify-logs/mutants/*/matrix.json` at re-pin and demotes any claim with an un-issued survivor. Agent (Python: `mutmut` or `cosmic-ray`), Edge and Server (cargo-mutants) adopt the same matrix format.
4. **L4 and L5 as they are.** The batteries and CSD/3 already carry their own gates; the only change is that each battery case and each CSD `shows:` row names the promise rule it keeps, so a red run reads against the plain rules.
5. **The register tells the truth per row.** Each P00 row carries five cells (L1–L5), each ✅/⏳/✗/—. "Met" is five greens or dashes with a reason. The plain rules do not change; the register under them does.

## 3. The boundary, stated

- **N1–N5 and the set-aside** are not promises and get no mutants.
- **2h, 3e, 8b, 8c in part** are process duties (publication, appointment); a mutant would test a document, not the wire.
- **6e, 7a, 7d, 9b** are conduct with no wire rule; they live in L4 only, or in nothing (9b).
- **8a** has no spec twin because the promise is that the record is reachable, not that a decision is made.
- **Promise 4's reasons (4e)** are the L1 artefacts; they are not mutated, they are what mutation produces.
- **One implementation per layer.** The matrix is cross-layer, not cross-vendor; a second independent implementer is what would turn L2 into an interoperability proof (W3C's two-implementation rule), and there is none.
- **The council's philosophical residue** (dignity without standing, the status freeze, the founder's threshold, the one-holder pause, the WA board defect, no-scanner/no-hand against legal duties) is not reachable by any mutant. A mutant tests whether the wire keeps the promise as written; it cannot test whether the promise is right.
