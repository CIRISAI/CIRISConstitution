# Verification of Grok pass-6 register report

Report: /home/emoore/CIRISConstitution/review/notes/pass6_grok/register.md (Grok 4.7, 131 pages, rc12 register PDF built 2026-10-26 17:55).
Care score: 4. Verdict paragraph as written: "The generated register is countable and often honest about staged work, but it does not meet its own 'present tense only for what ships' rule, and Part 8 (especially the annexes and the 2026 deployment citations) cannot go to 1.0 without steward rulings."

Staleness check: constitution/claims.tsv last changed 14:29 today (9d5471a, the v60 re-pin). PDF built after that; no status finding is stale. Counts 370/106/30/0 = 506 match p. 59. No established row carries a `staged:` pointer.

Source files: constitution/part_8_appendices.md (P8), constitution/claims.tsv (CT), constitution/part_3_the_namespace.md, constitution/part_7_lifecycle_stewardship.md, constitution/part_4_composition_governance.md, constitution/covers/register.md, tools/_md2latex.py.
Earlier passes: review/notes/volume_swot_rc11_pass{3_grok,4_gpt,5_gemini}_2026-10-25.md, review/notes/pass{3_grok,4_gpt,5_gemini}/register.md, plus pass 1/2 notes.

## CONFIRMED

1. R14 uses present tense for a staged rule. CONFIRMED. P8:179 "CC 4.4.2 aggregates `signed` dimensions by the mean of `score × confidence`"; CT:202 CLM-nsproc-aggregation-policy = staged:CIRISPersist#803, status staged. New for R14 (pass 3 raised glossary/FedCode present tense). Disposition M: "is specified to aggregate" / "the staged rule aggregates".

2. R5 "Discharged" but register row still titled "Hardware-class self-assertion gap (acknowledged)". CONFIRMED. P8:170 "**Discharged:** the per-platform attestation chains are evidence-established"; P8:232 "**No longer deferred**: discharged per R5"; CT:102 "CLM-hardware-class-hardware | 4.2.2.1 | Hardware-class self-assertion gap (acknowledged) | impl:CIRISServer/src/hardware_attestation.rs#admit_hardware_class | established". Row-title half is new (pass 2 only said R5 sits in the open risks table). Disposition M: retitle summary to the residual (TPM vendor anchors unbaked by design).

3. "First contact" names two things. CONFIRMED. CT:313 (CC 4.5.1) "stewardship ends only by the first-contact act"; CT:314 (CC 1.13.2) "recognised by an act of the HUMANITY_ACCORD under the first-contact discipline … no such act is defined yet"; part_4:1261 "its stewardship bound is the first-contact act". CT:469/476/480 (CC 3.2) use "first-contact plane"/"first-contact link" for device pairing (CIRISEdge/src/first_contact.rs). Standing half raised pass 2 (charter) and pass 4 R81; term collision with pairing is new. Disposition R: steward picks a distinct name for the accord act (rows individually true; undefined act is the declared state).

4. §8.4 boxed informative, §8.4.2.2 says MUST. CONFIRMED. P8:284 "**This whole section is informative (CC 2.5).** Nothing here touches the frozen normative interior"; P8:335 "the node MUST emit the C2PA assertion"; P8:309 concedes "Disposition: import bridge informative, emit normative for generated media per CC 3.4.14; … the register row is staged." Raised pass 3 (#3), pass 4. Disposition R (carried): cite CC 3.4.14 R3 instead of restating a MUST, or lift the sentence out of the informative box.

5. Annex G §8.2 gives MH a change-control role while §8.6.1 says no normative force. CONFIRMED. P8:937 "the sign-off process … includes a written reconciliation note explaining how the change remains consistent with MH or explicitly records the divergence"; P8:957 "These citations are informative … the threshold binds by being stated here"; P8:377 "Everything here is informational … with no normative force." Raised pass 3 (#2). Disposition R (carried). Note §8.2 allows "records the divergence": a documentation duty, not a veto; Grok's "veto-shaped" overstates.

6. Factual-premise row names vendors and an EO. CONFIRMED that the row says it: CT:321 CLM-factual-premise "already deployed at consumer scale (Muse Glimmer, Dots, EO 14434)", normative-only; P8:414 source note says "minimal oversight" is "the reporter's description; whether it is the vendor's own wording is unverified." Raised passes 1, 2, 3 (#1), 4; pass-3 verification note (volume_swot_rc11_pass3_grok_2026-10-25.md:59) records citations gathered by web search at the steward's request. Disposition R (already ruled to keep); residual question only whether the three names belong in the row summary vs the 8.6.1 note.

7. Art. 50 status "Evidence-bearing" while "legal sufficiency unreviewed"; graduation rule has no slot for Partial/Evidence-bearing. CONFIRMED. P8:605 ends "… In application (Art 113) | Evidence-bearing |" and contains "(legal sufficiency unreviewed)"; P8:610 OSHA row "Partial"; P8:616 "A statutory row moves from *Informative* to *Verified* when qualified legal review confirms…" with no other states defined. New. Disposition M: define Evidence-bearing (operational cross-walk layer has artefacts) and Partial in the graduation rule, or set Art 50 to Informative.

8. "Established" wording vs the reading key. CONFIRMED as wording tension. covers/register.md "the artefact that establishes it"; generated header p. 59 "Every load-bearing claim names the artifact that establishes it"; P8:392 "it never certifies that the sentence it hangs on is true of the world"; P8:412 "strength is graded here, in prose, and is not a registry column". Raised pass 4 (#7) and pass 5. Disposition P (generated header in tools/check_claims.py: "names the artifact that backs it", pointing to the 8.6.1 key); a grade column is R.

9. House-style breaks in Part 8. All CONFIRMED in source:
   - "5 ergonomic considerations from trio Phase 4 audit" P8:264 (pass 5). M.
   - "was Art 61 in the 2021 COM(2021) 206 proposal" P8:606, 1255, 1357 (pass 3). M.
   - "a format nobody has implemented is not made real by ratifying a paragraph about it" P8:268. New. M.
   - "We never adopt anyone's semantics. We adopt…" P8:290 (pass 1). M.
   - "C2PA has no consent architecture, no revocation, no 1+4" P8:311 (pass 4, 5). M.
   - "as it did for email authentication" R12 P8:177 (pass 3). M.
   - "exactly as 'the Web' is the emergent network of HTTP-speaking servers" P8:24 (pass 3). Analogy, not comparative claim: MATTER-OF-TASTE.
   - SCITT "delta" P8:355 (pass 3). CEG's own gap stated against RFC 9943, labelled informative: MATTER-OF-TASTE.

10. Annex J inner clauses restart numbering. CONFIRMED. P8:1407 "**7. Scenario Library**" then P8:1409 "*1.1 Selection methodology.*", "*1.2 …*"; 2.x under §8, 3.x under §9, 5.x under §11; code block at P8:1420 cross-refers "fields: 1.3 under §7". Raised pass 4 (#8), pass 5 (#4). Disposition M.

11. §8.6.4 is one sentence, no list. CONFIRMED. P8:431-433 "The namespace stewards are the owning components of CC 3.1, each named by its mission document in its own repository." Raised passes 2, 4, 5 (then placeholder). Disposition M: list them, or fold into 8.6.3 and retire 8.6.4.

12. Banned word in printed symbols. CONFIRMED. CT:323 test_negotiation_timeout_forces_graceful_shutdown; CT:446 test_drain_requests_graceful_shutdown_only; prose at CT:446 says "orderly shutdown". Raised passes 2, 3, 4, 5; pass-3 verification ruled "the name of a test in another repository … is not renamed." Disposition X (ruled) unless steward asks CIRISAgent to rename.

## MATTER-OF-TASTE

13. CC 3.4.13 "federation duty, not deferred to jurisdiction" vs CC 7.3.5 "exists only where the law recognises one … orders no remedy". MATTER-OF-TASTE, not a contradiction. part_3:2322 is a reporting duty: "a federation duty in its own right, not one left to whatever a jurisdiction may compel under the Q2 ratchet (which only adds to it). Silence … is a breach the `slash` duty-holder may act on". part_7:281 governs legal claims of harm: "adjudicated by the court, regulator or licensing authority with jurisdiction … never a federation office." A conduct duty with an in-federation slash consequence is not a cause of action. The clash is manufactured by the row summary CT:315 compressing to "not deferred to jurisdiction". New. Disposition M: reword the 3.4.13 row summary to the source's "not left to what a jurisdiction may compel".

14. "open 0" beside residuals "not yet a register row". MATTER-OF-TASTE. "open" is a row status (0 rows); "Open stubs: 0" at 8.9 counts referenced-but-undefined pieces; a measurement that is not a row is neither. Raised pass 3, 4. Disposition M optional: one sentence at p. 59 distinguishing open stub / staged / acknowledged residual.

15. "The moderation surface is complete" (p. 8). MATTER-OF-TASTE. P8:188 says exactly this and continues "the remaining child-safety work is implementation". Claim about the rule surface, not shipped code. New. M optional ("is specified in full").

16. Annex thresholds bind adopters but sit outside the register. MATTER-OF-TASTE. Declared at p. 21 ("not evidenced in the register unless a row says so … where an annex and a Part disagree the Part is the rule"). Raised pass 3 (#2). X.

17. Annex letters out of section order (8.8.2 B, 8.8.3 D, 8.8.5 C). MATTER-OF-TASTE. p. 21 discloses "8.8.1 and 8.8.4 are retired identifiers … the numbering keeps their places so citations stay stable." Raised passes 3, 4, 5. X.

18. "era-sure" hyphenation in the R9 heading. Confirmed on the page-7 image (narrow table cell) but a valid TeX break. P optional (a \hyphenation exception).

## FALSE

19. Not-equal printed as combining slash plus "=". FALSE. Page-7 image shows a proper ≠; tools/_md2latex.py:332 maps "≠" to $\neq$. Combining character is a pdftotext extraction artifact. Pass 3 raised; pass-3 verification dismissed.

20. CRE trigger printed "1026 FLOP". FALSE. P8:570 is "10²⁶ FLOP"; page-22 image renders 10²⁶. Same pdftotext flattening; dismissed in pass-3 verification (volume_swot_rc11_pass3_grok_2026-10-25.md:55).

## Summary

Of about twenty concrete findings, twelve are confirmed against source, five of them new to this pass (R14 verb, R5 row title, first-contact term overload, Art 50 Evidence-bearing slot, the "nobody has implemented" editorial line); the two glyph findings are extraction artifacts and the 3.4.13/7.3.5 "contradiction" dissolves on reading the source rules, though the row summary invites it.
Dispositions: M for R14, R5 title, Art 50 graduation rule, Annex J numbering, 8.6.4, the house-style lines, and the 3.4.13 row summary; R for first-contact naming, the §8.4 MUST, Annex G §8.2 and the vendor names in the premise row (last three carried from pass 3); P for the generated-header "establishes" wording; X for graceful symbols, annex letter order, and annex thresholds.
