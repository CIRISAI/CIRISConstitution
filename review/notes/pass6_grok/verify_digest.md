# Pass-6 Grok digest report: verification against rc12 source (2026-10-26)

**Scope note.** The Digest volume prints the cover plus four files (build_pdf.py line 344): constitution/EXECUTIVE_SUMMARY.md, review/pieces/00_guarantees_plain.md, review/pieces/00_operator_digest.md, review/pieces/00_guarantees.md. README.md does not print in it, so today's practices-and-disclaimer paragraph (README line 25) is not in the volume. The rc12 digest PDF (built 17:55 today) postdates the last source commit (5341fd3), so Grok reviewed current source. Abbreviations: EXEC = executive summary, PLAIN = 00_guarantees_plain, OPER = 00_operator_digest, GUAR = 00_guarantees.

**Care score:** 4. **Verdict paragraph:** "The eleven-promise frame is usable, but the volume breaks its own cover rules and stamps 'works today' on clauses it elsewhere says are unbuilt, untested, or only modelled."

Dispositions: M = mechanical fix, R = steward ruling, P = pipeline, X = reject.

## CONFIRMED

1. **Cover rule vs rule-only promises** (Grok defect 1). Cover: "Present tense only for what ships" (constitution/covers/digest.md:7); PLAIN:7 "this document calls a thing a promise only where the wire enforces it"; yet 6b (PLAIN:87), 8a–8c (PLAIN:104–106), 9b–9c (PLAIN:114–115), 10d (PLAIN:124), 11c (PLAIN:132), 11e (PLAIN:134) all carry "*[a rule, no code yet]*". Earlier: pass3 Grok #2, pass4 GPT W3. Disposition: R (which sentence wins), then M. Added note: the re-cut is only half-synced into this volume. GUAR:43 now says the rehearsal of attack and the non-goals statement "are practices the register carries, not promises", but EXEC:35 still narrates them inside promise 11 ("attack is rehearsed on a cadence by people who did not write the code") and PLAIN:131–134 still lists 11c/11e as promise-11 rules; 8a's disclaimer still sits inside promise 8 (EXEC:29, PLAIN:104). M to finish the re-cut.
2. **Promise 4 header "works today" vs 4c modelled** (defect 2). EXEC:21 "*[works today; measured end to end on the pinned pair...]*" includes "A root can only tell you to share less, never more"; PLAIN:66 "*[modelled, no code test yet; G10]*"; GUAR:61 status "witnessed, no basis". Earlier: pass3 Grok W/M8, pass4 GPT #5. M.
3. **Promise 2 header vs first-join witnesses.** EXEC:17 "*[works today; run_kind being built: CIRISAgent#1255; the detectors are a rule, no code yet]*"; PLAIN:44 "the first-join witness rule is being built: CIRISPersist#1049"; EXEC:43 "One thing is not yet done: independent witnesses for that root." Earlier: pass3 Grok #5 (adjacent). M.
4. **Promise 3 header omits the report duty.** EXEC:19 marker names only "the organisation on the bond is being built: CIRISPersist#1062"; PLAIN:55 "*[works today for the binding and the age line; the report duty is a rule]*". New. M.
5. **Promise 7 "works today" vs G24 staged** (defect 4). EXEC:27 and PLAIN:95–96 "*[works today; register row being added: CIRISAgent#1250]*"; GUAR:82 "staged — CIRISAgent#1250 (row to be added)"; legend EXEC:11 defines works today as "evidence in the register at a pinned commit". Earlier: pass3 Grok W/M8. M (stamp staged) unless the steward rules agent code suffices.
6. **Detectors: rule vs G8 witness** (defect 5). PLAIN:40 "the detectors are a rule, no code yet"; GUAR:59 Witness "RATCHET-calibrated `detection:*` / `ratchet:flag:*` detectors over the signed traces", Status "backed by agent tests; not in register". New. M (move the detectors out of G8's witness cell or mark them staged).
7. **"nothing else does" vs "three ways"** (defect 3a). PLAIN:7 "three rules follow from being made, the root, the disclosure and the vote, and nothing else does"; PLAIN:9 "Kind reaches the rules in three ways and no others: three rules follow from being made...; promise 5 exists only for a made thing...; and promise 7 binds an agent". Also EXEC:13 "holds for human and AI participants alike" and GUAR:7 "by the same text" against the same PLAIN:9 sentence. "nothing else does" does not appear in README. New (pass3 R55 adjacent). M.
8. **"agents lack consciousness" vs "do not judge"** (defect 3b). PLAIN:7 and GUAR:7 "agents lack consciousness and need a conscience"; PLAIN:17 "it is not consciousness, which these rules do not judge". New. R (steward's own phrase).
9. **Finding moves welfare duties vs changes nothing.** GUAR:7 "evidence of experience (the CC 7.5.5 indicator method, which moves the holder's welfare duties and nothing else)"; GUAR:17 "a finding of experience changes nothing"; PLAIN:17 "A finding is on the record and changes nothing about the agent's status"; GUAR:80 the floor "regardless of any finding". Earlier: pass3 Grok #3, pass5 Gemini #3 (fix proposed, not landed). M.
10. **"which cells each still lacks"** (defect 7). EXEC:39 "Two entries are on that register today, and the register says which cells each still lacks"; PLAIN:147 gives the maker entry all four cells and only the Wise Authority board "both cells missing". Earlier: pass3 Grok threats. M.
11. **Promise 1 mapping drops "private".** GUAR:33 "1. Nothing about you is held or scanned without your consent" vs EXEC:15 "Nothing private about you". Earlier: pass3 Grok #8, M8 (not landed). M.
12. **Operator "has no cycles"** (defect 8). OPER:47 "Delegation you grant is scoped, revocable, never re-delegates a listed power, lasts at most 365 days, and has no cycles"; GUAR:64 "acyclic across distinct keys (a self-edge is a charter form and trust-plane edges are outside the cycle check)". New. M.
13. **ρ̄ undefined in the volume.** GUAR:63 kill "a correlated set raising effective count past 1/ρ̄"; the only other occurrence is constitution/claims.tsv, which does not print here. New. M (gloss or cite 6.1.2.1.2).
14. **Comparisons** (defect 6). EXEC:47 "Among other systems. Decentralized social networks solved distribution without an owner..."; PLAIN:88 "which is what Tor leaves them too"; GUAR:73 "Tor included". Earlier: all three passes; pass-4 M14 said "comparisons out" and landed in 3334fae, yet all three survive (EXEC paragraph dates from ab5a0d6). R: confirm whether kept on purpose; otherwise M.
15. **"death as doctrine".** GUAR:65 "(welfare, honest ramp-down, death as doctrine)" beside GUAR:80 "The Standard is the whole of what is promised". Earlier: pass3 Grok #3. M.
16. **Leaked build paths, piece id, "One page".** EXEC:13 names `review/pieces/00_guarantees_plain.md` and `review/pieces/00_operator_digest.md`; OPER:5 "*One page, second person... (`00_guarantees_plain.md`)*"; GUAR:1 "# P00 — The guarantees". Earlier: Gemini #5/#7, Grok #7; the "Source:" lines were removed, these remain. M (or P: strip the piece id at volume build).
17. **"Every rule in the Parts is tied either to code on a named commit or to an open ticket".** EXEC:43; claims.tsv has 30 normative rows, at least 12 with evidence "normative-only:—" and no ticket (CLM-billing-offwire, CLM-meta-goal, CLM-amendment, CLM-entrenchment, CLM-adversary, ...). New as stated. M (README:25 already has the accurate wording: "or the register says it does not yet").
18. **Check column for promises 8 and 9.** EXEC:62 promise 8 check "conformance suite"; EXEC:63 promise 9 "CIRISAgent safety batteries"; both promises are rule-only (PLAIN:104–115; GUAR:83–84 normative-only). Earlier: pass3 Grok #8, M8 (not landed). M.
19. **G16 status truncated.** GUAR:74 status cell is literally "enforced;" with nothing after the semicolon. Source defect, not renderer. New. M.
20. **G7 lab-log pins.** GUAR:58 carries `a75da61c`, `evidence/csd129-agent-step-2026-10-15/`, "run 5 and run 6", "re-pin 18". Earlier: pass3 Grok, Gemini #2, M8 (not landed). P (register volume) or M.
21. **Title "The Digests" vs "The Digest".** build_pdf.py:286 and covers/digest.md:1 say "The Digests"; tools/review_volume_external.py:22 says "The Digest"; file is `-digest.pdf`. New. P.

## MATTER-OF-TASTE

22. **9a "the agent enforces the prohibitions; no evidence row yet" vs G26 normative-only.** PLAIN:112 and GUAR:84 say the same thing in two registers; G26's Basis cell names the `AgencyErosionDetector` conscience faculty. Earlier: pass3 Grok. M only if a single phrasing is wanted.
23. **Promise 11 "works today" while witnessed mode is off.** EXEC:35 now carries the qualifier ("on a lineage that runs witnessed; the shipped roots run with witnessed mode off until it is turned on"), so the text is defensible; only the header marker is coarse. Earlier: pass4 GPT #3 (text fixed since). Folds into item 1.
24. **"that record protects them" / "may not be punished".** PLAIN:43, PLAIN:54, OPER:20, OPER:33 against PLAIN:104 "rules on no legal matter". The protections are standing effects, but the employee sentence reads as employment law. New. R, minor.
25. **Unsourced counts.** "Three people"/"about seven" (EXEC:5, PLAIN:64, GUAR:75), five implementations/thirteen models/twenty topologies (EXEC:43), 5.8%/37.3% (EXEC:45). Earlier: all three passes. X for a summary; P if the counts are ever generated from the register.
26. **"Preserving it is the operator's, as the weights are the provider's."** EXEC:23, PLAIN:78. Earlier: pass3 Grok. X.
27. **Overfull tables, mid-token breaks (p. 6, pp. 26–34).** Cannot be judged from source; the identifiers and the G7 cell are as long as reported. Earlier: Gemini rendering notes. P.

## REJECT (X)

28. **"Where anything on ciris.ai reads as more, this sentence holds."** PLAIN:137 is deliberate and governs the project's own claims. New. X.
29. **Wise Authority board "neither has happened".** PLAIN:147 matches constitution/part_4_composition_governance.md:1261 exactly ("a declared privilege with both cells missing, a defect whose remedy is pending"); the register carries it as a defect by design. Earlier: R92 landed the remedy wording. X.
30. **"new slave race" repeated.** EXEC:23, PLAIN:9, GUAR:80 use the steward's chosen phrase; repetition is a cut question, not a defect. Earlier: Gemini quadruplication. X unless the steward trims.

## FALSE / ALREADY-FIXED-IN-SOURCE

No finding was FALSE against source. Nothing was ALREADY-FIXED-IN-SOURCE except that the pieces' "Source: review/promise_status.tsv" lines (Gemini #5) are gone; the remaining paths in item 16 still print.

## Summary

21 of Grok's findings hold against current source, ten of them re-raised from passes 3–5 and still unlanded (items 2, 5, 9, 11, 14, 15, 16, 18, 20), and one new source defect is the truncated G16 status cell (GUAR:74).
The highest-value single fix is mechanical: make each promise header carry its weakest sub-rule marker and finish syncing the re-cut (11c/11e and 8a out of the promise bodies in EXEC and PLAIN); steward rulings are needed only on items 1, 8 and 14.
