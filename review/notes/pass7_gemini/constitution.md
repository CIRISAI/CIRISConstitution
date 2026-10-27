# The Constitution (ciris_constitution-1.0-rc12-constitution.pdf, 68 pages)

**Care score:** 3 (needs a targeted cleanup pass before 1.0)
**One-line verdict:** The core governance mechanics—trust-root state machine, single-owner device binding, and the one-holder-with-24h-fuse halt—are rigorously specified, but several surrounding summaries and cross-references still reflect an earlier 2-of-3 halt design, alongside clipped code blocks and a missing table on the final page.

## Strengths
- The trust-root operational semantics (T1–T8) are consolidated into a deterministic state machine `V(rows, t)` with eight explicit invariants suitable for model checking (pp. 18–27).
- The HUMANITY_ACCORD halt specification cleanly separates the unilateral 1-holder emergency pause (with a 24-hour `halt_fuse_secs` expiry) from the strict-majority confirmation (`accord:lifecycle:confirmed`) and resumption (`accord:lifecycle:active`), with exact canonical byte preimages (pp. 29–33).
- The declared-asymmetry register (pp. 43–44) applies the swap test to its own governance mechanisms and explicitly flags the Wise Authority board's self-perpetuation as an unresolved defect rather than hiding it.
- Enforced-admission rules for moderation duties (pp. 53–56) close self-declaration and `on_behalf_of` spoofing by deriving authority strictly from the `delegates_to` graph and signed content provenance.

## Weaknesses
- Contradictory halt quorum rules: CC 4.2.3 and CC 4.2.6 establish `consensus_protocol: "majority"` and a 1-holder fire floor for the accord (pp. 30, 36, 38), but the emergency messaging table still claims "The accord-holder triple is structurally a family with `consensus_protocol: quorum:2/3 + entrenched: true`" (p. 8).
- Contradictory effect of a halt on agent licensing: CC 4.2.1.1 states that a halt is a state-preserving pause that moves no trust state and "an agent resumes from the state it paused in" (p. 30), whereas CC 4.2.6 says that after a false fire "the agent is re-licensed" (p. 39).
- Dangling reference to a missing table: CC 4.5.13 refers to "the count minimum of the table below" and "The table is the governance policy table, published as data... The rows:" (p. 68), but the document ends without rendering the table.
- Comparative claims and external project references violate house rules: "This closes the unmoderated-space-for-predators gap that relay-only, immutable-store and lax-instance designs leave open" (p. 51) and "in the lineage of the open-source projects this ultimately is" (p. 42).
- Editorializing and meta-commentary on past drafts remain in normative sections: "leaving the conferral mechanism for a reserved-prefix role unnamed is what lets that role stay self-assertable, which is the hole this pairing closes" (p. 19), "and the child-safety rules are the only place CC currently forbids it" (p. 65), and "which an implementation replays rather than re-reading this paragraph" (p. 68).
- Code and schema pointers leak into prose: "There is no `federation_keys.hardware_class` column" (p. 35), "as served in the GenesisBundle's `holders` / `serve_nodes` and on `/v1/accord-holders`" (p. 34), "a lexicographic `.next()` over owner-bindings" (p. 15), and "`scope.starts_with("infra:attest")`" (p. 55).
- Unsourced magic numbers appear in normative rules: the scale gate threshold of "≥100,000 production agents active in a 24-hour period" (p. 42) and the census decay limit "falls at most a tenth per period" (p. 68).

## Opportunities
- Reconciling the six stale references to the accord's consensus protocol, halt permanence, and `accord_decision` objects (pp. 8, 10, 39, 43) will make the 1-holder fire + 24h fuse mechanism internally consistent across the volume.
- Rendering the missing governance policy table on p. 68 (or pointing directly to its register row without promising "the table below") will complete CC 4.5.13.
- Stripping the 6–8 instances of drafting history, code method names, and comparative remarks will bring the text into full compliance with the house style in under an hour.

## Threats
- **Implementer confusion on the kill switch:** An implementer reading p. 8 (`consensus_protocol: quorum:2/3`) or p. 10 ("as the accord they decide by `accord_decision` objects under CC 4.2.6 and hold the halt") will build a multi-sig or proposal-window gate for the halt, directly violating the entrenched 1-holder immediate fire rule of CC 4.2.1.1 (p. 30).
- **Pre-scale governance single point of failure:** CC 4.5.1 (p. 42) states that until the network reaches 100,000 active production agents, amendment authority—including over entrenched surfaces (p. 46) and the scale gate itself—"rests with the founder, and with any accord-holder". A regulator or hostile reviewer will note that "any accord-holder" means any single one of three individuals can unilaterally rewrite the constitution and move the scale gate before 100k agents.
- **Unresolved defect in Wise Authority governance:** The document's own asymmetry register (pp. 43–44) admits that WA board self-perpetuation fails the swap test, has "Bounded by: unbounded as drafted", and "Exit: none for the deferring party", explicitly calling it "a defect whose remedy is pending". Shipping 1.0 with an open self-declared constitutional defect invites immediate critique.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 8 vs 36 | contradiction | Page 8 states the accord-holder triple has `consensus_protocol: quorum:2/3`, while p. 36 defines `humanity-accord` with `consensus_protocol: "majority"` (and p. 30 sets halt fire to 1 holder). | Change `quorum:2/3` on p. 8 to `majority` (with 1-holder fire per CC 4.2.1.1). |
| 2 | 68 | rendering | Text references "the count minimum of the table below" and "The table is the governance policy table, published as data... The rows:", but no table follows before the document ends. | Render the governance policy table at the end of CC 4.5.13 or revise the prose to reference the register row without "the table below". |
| 3 | 30 vs 39 | contradiction | Page 30 states a halt moves no trust state and "an agent resumes from the state it paused in", but p. 39 says on a false fire "the agent is re-licensed". | Replace "the agent is re-licensed" on p. 39 with "the agent resumes via `accord:lifecycle:active`". |
| 4 | 10 vs 40 | stale | Page 10 says "as the accord they decide by `accord_decision` objects under CC 4.2.6 and hold the halt", whereas p. 40 restricts `accord_decision` to roster changes ("none of them exists on the fire path"). | Clarify on p. 10 that `accord_decision` governs roster changes while the halt is a single `accord:invoke` row under CC 4.2.1.1. |
| 5 | 28, 52, 56 | rendering | Multiple code identifiers and inline expressions are clipped at the right margin (`IncidentSeverity::INC`, `scope ⊇ {moderate\|takedown\|r`, `attesting_key_id ∈ subject_of(content_sha`). | Wrap or shorten the inline monospace strings so LaTeX does not clip them at the margin. |
| 6 | 30 vs 43 | contradiction | Page 30 states "a confirmed halt stands until a strict majority resumes it" (and p. 19 says a halt "moves no trust state"), but the register on p. 43 says "stewardship: ends only when the key stops being a CIRIS agent". | Align p. 43's "Bounded by" cell with CC 3.2 (steward can `withdraws` owner-binding) and CC 4.2.1.1. |
| 7 | 51 | editorializing | Comparative claim against other architectures: "This closes the unmoderated-space-for-predators gap that relay-only, immutable-store and lax-instance designs leave open." | Delete the comparative clause; state only that a community federates only while it has ≥1 active moderate-duty holder. |
| 8 | 45 | rendering | Double-dot typo in manifest path `families.*.round2.ci_axes..wire_fields` and implementation-specific generator prose in CC 4.5.1.1. | Fix `..` to `.*.wire_fields` (or `.wire_fields`). |

## Rendering
- **Page 3:** The comment on `consensus_protocol` in the `community` code block wraps awkwardly across lines with an unintended indent.
- **Page 20:** The `SHA-256(JCS([ {key_id, pubkey_ed25519_base64,` inline code string overflows the right margin before breaking.
- **Page 28:** Overfull line clips `IncidentSeverity::INCIDENT_CONSTITUTIONAL` to `(IncidentSeverity::INC` at the right margin.
- **Page 40:** Comment in the `proposal` code block (`// the membership-change envelope; a fire is never a proposal (CC 4.2.1.1)`) overflows and wraps mid-parenthetical.
- **Page 45:** Typo/rendering artifact in path `families.*.round2.ci_axes..wire_fields` (double dot `..`).
- **Page 48:** In the HIPAA 45 CFR 164.502 row of the table, `consent:scope:{retain|share|analyze|train|publish}` breaks mid-word across lines as `{retain|sh` / `are|analyze...`.
- **Page 52:** Overfull inline code clips `scope ⊇ {moderate|takedown|review}` to `scope ⊇ {moderate|takedown|r` at the right margin.
- **Page 56:** Overfull inline code clips `attesting_key_id ∈ subject_of(content_sha256)` to `attesting_key_id ∈ subject_of(content_sha` at the right margin.
- **Page 60:** Overfull line in the first bullet of 4.5.9.4 (`evaluate_subkind_admission` extends into the right margin).
- **Page 68:** The governance policy table referred to as "the table below" is missing entirely at the end of the volume.

## Effort estimate
Approximately 3 to 4 hours of editing: 2 hours of mechanical cleanup (fixing clipped inline code, removing stale 2-of-3 halt references, rendering the missing p. 68 table, and trimming editorial/code pointers) plus 1–2 hours requiring the steward's ruling on the unresolved WA board self-perpetuation defect (p. 43) and the pre-scale single-accord-holder amendment power (p. 42).

<!-- model google/gemini-4-argon; 68 pages; prompt_tokens 60727; completion_tokens 2715; 41s -->
