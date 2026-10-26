# The Constitution (ciris_constitution-1.0-rc12-constitution.pdf, 68 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The halt and roster rules are specified in enough detail to implement, but the power-bearing pages contradict each other, and a large share of the volume is essay, instance roster, and clipped tokens rather than rules.

## Strengths
- Accord kinds, the fuse, and resumption sit in one signature table and two canonical-byte domains (pp. 30–33).
- The standing verdict is stated as one function with invariants (i)–(viii), not only scattered prose (pp. 25–27).
- The declared-asymmetry register records a privilege that fails its own test, instead of omitting the cells (pp. 43–44).

## Weaknesses
- Cover promise against the register: "Anyone may found a root and anyone may leave one" (p. 1) against "agent: none while held" and "the agent cannot leave it" (p. 43). The agent’s bound is "not yet defined" (p. 43).
- Scope isolation is stated as absolute and then withdrawn: "humanity-accord authority cannot sign anything else. Wire-isolated AND scope-isolated" (p. 28) against "It does not isolate the amendment plane" (p. 29).
- Same accord family, two protocol strings: "consensus_protocol: quorum:2/3" (p. 8) against `consensus_protocol: "majority"` (p. 36). p. 10 then freezes later changes at "2-of-3" while p. 30 says "never a fixed 2-of-3".
- Leftover restore path: "the CC 4.2.6 restore path" (p. 14) against "There is no restore and no contest" and retired `ciris.accord_restore.v1` (p. 39). p. 40 still lists "contest ↔ restore cross-replay".
- Age boundary splits: "an over-18 user identity" (p. 16) against `age_band(S) == adult (>= 18)` (p. 16).
- Absence rule splits: "whoever stays absent never blocks the present actor" (p. 64) against a roster change that needs "strict majority of the standing roster in yes-votes" so absence stalls it (p. 38).
- "past-epoch content becomes information-theoretically unrecoverable" (p. 5) in the same section that says retention by a coerced holder is "not a cryptographic guarantee" and "structurally undetectable" (p. 5).
- House-rule breaches: code pointers (`formal/trust_root/`, `ciris_keyring::HardwareType`, `ciris-registry-core`, `PolicyCorridor.lean`, pp. 27, 34, 37, 68); "in the lineage of the open-source projects this ultimately is" (p. 42); named holders and "The roster is being widened… until about seven" (p. 35); "First deployment: the Magnifica Humanitas encyclical mapping" (p. 62); dated external systems (p. 61). "Why this is still 1+4" is repeated as design essay (pp. 6, 16, 17, 18).
- H3 areas in the worked example are wrong: "resolution 5-6 (city-scale ~250-1700 km2)" (p. 6). ~250 km² is resolution 5; ~1700 km² is resolution 4; resolution 6 is ~36 km². Unsourced ratings: multipliers 0.95 and 0.9 (p. 34); "about seven" (p. 35).
- A producer MUST name the subject, but the substrate "rejects the row, or admits it" as operator policy (p. 47). Geographic opt-in on p. 4 is restated at pp. 59–60.

## Opportunities
- One steward pass that picks, for each pair above, which sentence remains, then delete the other. No new rule is required to make pp. 8, 10, 28, 29, 30, 36, 38, and 64 agree.
- Replace "over-18" with the predicate already in the admission block on p. 16.
- Delete or mark non-normative the civic/emergency composition essays (pp. 6–8), the "1+4" refrains, the repository paths, and the bootstrap-tradition paragraph (p. 62).
- Re-flow the regulatory table (p. 48) and the named-moderator predicate (p. 52) so `share`, `publish`, and `review` are whole tokens.

## Threats
- A lawyer will read p. 1’s leave promise against p. 43’s "Exit: … agent: none" and the undefined first-contact act, and will read p. 28’s "cannot sign anything else" against accord signatures on amendment (pp. 29, 36).
- The same lawyer will treat the WA row as shipped defective power: "Exit: none for the deferring party" and "Bounded by: unbounded as drafted" (p. 43), while deferral freezes the agent (p. 41).
- An implementer will not know whether the accord wire value is `majority` or `quorum:2/3`, whether a grown roster is still 2-of-3, or whether a restore domain still verifies. Clipped tokens on pp. 28, 48, 52, and 56 will be copied into verifiers.
- A regulator will treat the GDPR/HIPAA/AI Act table (p. 48) and "operator MUST file the NCMEC CyberTipline report (US 18 USC §2258A)" (p. 50) as universal compliance claims, and will treat "rsvps repurposed as votes" (p. 6) as equating consent with a ballot.
- p. 37’s "outside the federation’s participant set" is hard to defend once the same three keys are ciris-canonical founders (p. 10) and named instance holders (p. 35).

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 28, 29 | contradiction | "cannot sign anything else. Wire-isolated AND scope-isolated" (p. 28) vs "It does not isolate the amendment plane" (p. 29). | Delete the absolute sentence; keep the enumeration plus the amendment-plane sentence already on p. 29. |
| 2 | 1, 43 | contradiction | "anyone may leave one" (p. 1) vs "agent: none while held" and a bound "not yet defined" (p. 43). | Steward picks one; the cover promise must match the register cell. |
| 3 | 8, 10, 30, 36 | contradiction | Accord family is `quorum:2/3` (p. 8) and `"majority"` (p. 36); later changes are "2-of-3" (p. 10) and "never a fixed 2-of-3" (p. 30). | One protocol string, one growth rule, in all four places. |
| 4 | 14, 39, 40 | stale | p. 14 cites a "CC 4.2.6 restore path"; p. 39 retires restore and contest; p. 40 still names them in the replay list. | Remove the p. 14 cross-reference and the contest/restore words on p. 40, unless the steward restores those domains. |
| 5 | 16 | contradiction | Guardian must be "over-18"; the predicate admits `adult (>= 18)`. | Use one boundary, the one in the `require` block. |
| 6 | 38, 64 | contradiction | Absence "never blocks the present actor" (p. 64); standing-roster yes-votes mean absence stalls a roster change (p. 38). | Qualify p. 64 so it does not restate 4.2.6 as a single absence rule. |
| 7 | 28, 48, 52, 56 | rendering | `IncidentSeverity::INC = 5` (p. 28); `retain\|sh` / `pu` / `blish` collided with the next column (p. 48); `{moderate\|takedown\|r` then `community_id` (p. 52); `subject_of(content_sha` (p. 56). | Re-flow so each normative token is intact. |
| 8 | 6 | overclaim | "resolution 5-6 (city-scale ~250-1700 km2)" does not match H3 average areas. | Replace with figures that match the resolutions named, or drop the km² claims. |

## Rendering
- p. 28: severity token broken; the line ends at `IncidentSeverity::INC` and the next line is `= 5`, not `INCIDENT_CONSTITUTIONAL`.
- p. 48: overfull regulatory table; `share` and `publish` are split and interleaved with the adjacent column (`retain|sh`, `are|analyze|train|pu`, `blish`).
- p. 52: named-moderator predicate clipped at `{moderate|takedown|r`; `review}` is not on the next line.
- p. 56: `subject_of(content_sha` cut off before `256)`.
- p. 11: "Trust ̸= membership" uses a composed slash rather than ≠.
- Duplicated geographic opt-in prose: p. 4 and pp. 59–60.
- No literal `**` or stray `\` seen. `\n` in the canonical-byte blocks is intentional.

## Effort estimate
About two to three days: half a day of steward rulings on the six contradictions (which sentence stands), then a mechanical day-plus to strip essays, code pointers, instance plans, and to re-flow the clipped table and predicates.

<!-- model x-ai/grok-4.7; 68 pages; prompt_tokens 60603; completion_tokens 17962; 209s -->
