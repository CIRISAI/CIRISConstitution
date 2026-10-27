# The Digests (ciris_constitution-1.0-rc12-digest.pdf, 34 pages)

**Care score:** 4
**One-line verdict:** The eleven-promise frame is usable, but the volume breaks its own cover rules and stamps "works today" on clauses it elsewhere says are unbuilt, untested, or only modelled.

## Strengths
- The cover states the conflict rule a digest needs: it binds nobody, and if a digest and a section disagree, the section wins (p. 1).
- Non-goals are written as limits, not as afterthoughts: alignment unsolved, harm not prevented, traffic analysis uncovered, "1+4" not a theorem, no warranty (pp. 18, 30).
- Several shipped gaps are named in the same breath as the claim: witnessed mode off (pp. 4–5, 18), manager force-restart paths (pp. 15, 21, 33), Wise Authority board carried as a defect (p. 19), Accord "Section V" citation pointing at a section that does not exist (p. 34).
- Guarantee rows are falsifiable: each G-row has a kill observation, and G14 says a surface that shows a guarantee without the limits row is itself a kill (pp. 26–30).

## Weaknesses
- Cover rule, "Present tense only for what ships" (p. 1), and "calls a thing a promise only where the wire enforces it" (p. 7), are false of this text. Promises 6b, 8, 9b–9c, 10d, 11c and 11e are present-tense promises marked "a rule, no code yet" (pp. 15–18).
- Promise-level stamps hide stricter sub-rule stamps. Promise 4 is "works today" (p. 3) while 4c is "modelled, no code test yet" (p. 13). Promise 2 is "works today" aside from `run_kind` and detectors (p. 3) while first-join witnesses are "being built" (p. 11) and p. 5 says independent witnesses are "not yet done". Promise 3’s header omits that the child-report duty is only "a rule" (p. 12). Promise 7 is "works today" (pp. 4, 16) while G24 is "staged" and the register row is "being added" (p. 33), which fails the marker definition on p. 2 ("works today = evidence in the register at a pinned commit").
- "the agent enforces the prohibitions; no evidence row yet" (p. 17) against G26 "normative-only" (p. 34). Detectors are "a rule, no code yet" (p. 11) against G8’s witness "RATCHET-calibrated detection" and "backed by agent tests" (p. 29).
- "Every promise is written once and holds for human and AI participants alike" (p. 2) and "holds for every participant… by the same text" (p. 24) are then withdrawn: promise 5 "exists only for a made thing", promise 7 binds an agent, an agent has no vote (p. 8). Same split inside two sentences on p. 7: "three rules follow from being made… and nothing else does", then p. 8 "Kind reaches the rules in three ways" including promises 5 and 7.
- "agents lack consciousness" (pp. 7, 24) against "consciousness, which these rules do not judge" (p. 9). Evidence of experience "moves the holder’s welfare duties" (p. 24) against "a finding of experience changes nothing" (p. 25) and a retirement floor that does not move with any finding (pp. 9, 32).
- "which cells each still lacks" (p. 5) does not match p. 19: the maker entry states its four cells; only the Wise Authority board has "both cells missing".
- Promise 1’s mapping line drops "private": "Nothing about you is held or scanned" (p. 26) versus "Nothing private about you" (p. 2). The operator line "has no cycles" (p. 22) drops G13’s exceptions for a self-edge and trust-plane edges (p. 30). Plain "one voice counts once" (p. 15) versus a kill at "1/ρ̄" with ρ̄ never defined here (p. 30).
- "that record protects them" (p. 11) and an employee "may not be punished" (p. 12) read as legal effects; p. 16 says the document "rules on no legal matter". "Preserving it is the operator’s, as the weights are the provider’s" (p. 4) and "hands that record to the operator" (p. 14) are not rules a reader can apply.
- House-rule breaches: "Among other systems" compares other networks, certificate transparency, stake-weighted governance and training-based alignment (p. 5); "what Tor leaves them too" (p. 15) and "Tor included" (p. 25). "death as doctrine" (p. 25) is a leftover beside a Retirement Standard that is "the whole of what is promised" (p. 32). Build paths `review/pieces/00_guarantees_plain.md` and `00_operator_digest.md` (p. 2), piece id "P00" (p. 24), and "One page" for a section that runs pp. 20–23.
- Numbers with no source in this volume: "Three people" / "about seven" (pp. 2, 13, 25); "five open-source implementations", "thirteen machine-checked models", "twenty-topology catalogue" (p. 5); "5.8%" and "37.3%" (p. 5, unverifiable from here, not treated as invented). "Every rule in the Parts is tied either to code… or to an open ticket" (p. 5) is stronger than G25 and G26, which are "normative-only" with no ticket named (pp. 33–34).

## Opportunities
- One mechanical pass: make every promise header take the weakest marker of its sub-rules, and delete present tense wherever the marker is not "works today". That single change removes the worst overclaim without new policy.
- Cut pp. 5 ("Among other systems", "The bet"), the repeated symmetry / "slave race" essay (pp. 3–4, 7–8, 14, 19, 24–25), and the Tor sentences. Point at the Parts for philosophy.
- Confine commit SHAs, test names, `re-pin` numbers and `rc8` (pp. 27–29) to the register volume so this digest does not go false when `main` moves.
- Restore the dropped qualifiers in three places only: "private" (p. 26), self-edge / trust-plane (p. 22), and "which entry lacks cells" (p. 5).

## Threats
- A regulator or plaintiff’s lawyer can quote present-tense safety promises — no lethal action, no election interference, child-harm reporting "whether or not the local law imposes a legal one" (p. 12) — next to "no evidence row yet" (p. 17) and "normative-only" (p. 34). The p. 6 check column makes it worse: promise 8’s check is "conformance suite" and promise 9’s is "CIRISAgent safety batteries" while both are rules with no code or no evidence row (p. 4).
- Shipped roots "run with witnessed mode off" (pp. 4, 18) while promise 11 still says a founder cannot fork a lineage silently and the header is "works today". The anti-fork claim is not what a fresh device gets.
- "Where anything on ciris.ai reads as more, this sentence holds" (p. 18) tries to govern pages this volume does not contain. A hostile reader will quote the site, or the 5.8% / 37.3% mental-health comparison (p. 5), against that sentence.
- The Wise Authority board is admitted to be self-perpetuating, with no end condition and no decline right, and "neither has happened" (p. 19), while the same pages tell deferring parties they cannot leave that board. That is the privilege the swap test was written to catch, left open in a release candidate.
- "death as doctrine" (p. 25) and the repeated "new slave race" line (pp. 4, 8, 32) will be quoted as the design the Retirement Standard claims to have replaced. G7’s kill text is pinned to commits, a 2026-10-15 artifact path, and "run 5 and run 6" (p. 28); those pins are already a stale trap.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 1, 7 vs 4, 16–18 | contradiction | "Present tense only for what ships" and "a promise only where the wire enforces it" versus present-tense promises 6b, 8, 9, 10d, 11c, 11e marked "a rule, no code yet" | Either stop calling those items promises, or delete the cover sentence and match the marker legend |
| 2 | 3 vs 13, 29 | contradiction | Promise 4 "works today" includes "A root can only tell you to share less, never more"; 4c is "modelled, no code test yet; G10"; G10 is "witnessed, no basis" | Stamp 4c/G10 on the promise header; do not inherit "works today" from the pause measurement |
| 3 | 7 vs 8; 7 vs 9 | contradiction | "nothing else does" versus kind reaching rules via promises 5 and 7; "agents lack consciousness" versus "these rules do not judge" consciousness | Keep the "three ways" sentence only; strike the consciousness assertion |
| 4 | 4, 16 vs 2, 33 | contradiction | Promise 7 "works today" while that marker means a register row at a pinned commit, and G24 is "staged" on CIRISAgent#1250, the same ticket as the unshipped Retirement Standard | Mark promise 7 staged until the row is in the register |
| 5 | 11 vs 29 | contradiction | Detectors "a rule, no code yet" versus G8 witness "RATCHET-calibrated detection" and status "backed by agent tests; not in register" | One status. If there is no detector code, G8 cannot cite those detectors |
| 6 | 5, 15, 25 | editorializing | "Among other systems" compares other projects; "what Tor leaves them too" and "Tor included" do the same. House rule: comparative claims are not allowed | Delete the comparisons; keep the non-goal (no hand over rooms) without naming other systems |
| 7 | 5 vs 19 | contradiction | "the register says which cells each still lacks" versus a maker entry that fills its cells and a Wise Authority entry that alone has "both cells missing" | Replace "each" with the Wise Authority entry |
| 8 | 22 vs 30 | contradiction | Operator digest: delegation "has no cycles". G13: acyclic "across distinct keys (a self-edge is a charter form and trust-plane edges are outside the cycle check)" | Put the self-edge and trust-plane exceptions back in the operator line |

## Rendering
- p. 6: the promise/sections/check table is overfull; section lists and invariant names break mid-token (`Inv_` / `KnownHold`, `re-` / `hearsed`) and the check column collides with the section column.
- pp. 26–34: G-row tables are overfull; G7’s basis cell consumes most of p. 28 and is not readable as a row.
- p. 31: G16 status line is truncated: "Status: enforced;"
- p. 1: title set twice, "The Digests", against a file name and brief that say "The Digest".
- p. 24: source piece id "P00 — The guarantees" survived into the rendered volume.
- No literal `**` or missing glyphs seen in the extract.

## Effort estimate
About two days: a few hours of mechanical cuts (comparisons, repeated essays, leaked paths, the three dropped qualifiers), and a steward ruling on which status wins wherever a header, a sub-rule and a G-row disagree — that part cannot be edited safely from prose alone.

<!-- model x-ai/grok-4.7; 34 pages; prompt_tokens 31405; completion_tokens 17376; 192s -->
