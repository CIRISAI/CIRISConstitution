# Verification of review/notes/pass6_grok/constitution.md (Grok pass 6, The Constitution volume)

Checked against constitution/ source on branch rc12 (Part 1 §1.2, Part 3 §3.2, Part 4 §§4.2–4.3 and 4.5, covers/constitution.md), the rendered rc12 volume PDF (pdftotext), formal/accord_roster and formal/membership READMEs, and the pass 3/4/5 notes. No files edited.

**Report metadata.** Care score 4. One-line verdict: "The halt and roster rules are specified in enough detail to implement, but the power-bearing pages contradict each other, and a large share of the volume is essay, instance roster, and clipped tokens rather than rules."

Dispositions: M = mechanical text fix; R = steward's ruling; P = pipeline/renderer; X = reject.

## CONFIRMED

1. **Stale restore path.** part_3_the_namespace.md:811 still says "on a WA seizure finding (the same adjudication as the [CC 4.2.6] restore path)", while part_4_composition_governance.md:277 says "**There is no restore and no contest.** ... The domain labels `ciris.accord_contest.v1` and `ciris.accord_restore.v1` are retired and MUST NOT be reused" and part_4:281 still lists "proposal ↔ participation ↔ contest ↔ restore cross-replay". Prior: pass4_gpt/constitution.md defect #5 (p.14 vs p.40); volume_swot_rc11_pass2 lines 525–526 (the p.40/41 words). Disposition **M**: delete the parenthetical at P3:811 (the WA seizure finding stands alone) and drop "contest ↔ restore" at P4:281.

2. **H3 area figures wrong.** part_3:688: "`community` with `cohort_subkind: geographic` at resolution 5-6 (city-scale ~250-1700 km²)". H3 average hexagon areas: res 4 ≈ 1,770 km², res 5 ≈ 253 km², res 6 ≈ 36 km². "~250–1700" is res 4–5; "5–6" is ~36–250 km². Prior: none (pass4 R63 concerned proofs ≤ res 7, a different point). Disposition **M**: "resolution 4-5 (~250-1,770 km²)" or "resolution 5-6 (~36-250 km²)"; city scale fits 4–5.

3. **Guardian age boundary wording.** part_3:826: "An under-18 `user` identity **MUST** have a **live steward-binding** ... from an over-18 `user` identity at all times" vs part_3:836: `require age_band(S) == adult (>= 18)`. "over-18" leaves exactly 18 ambiguous; the predicate governs. Prior: none. Disposition **M**: "from an adult (18 or older) `user` identity".

4. **Scope-isolation enumeration omits the amendment sign-off.** part_4:71: "`HUMANITY_ACCORD` signatures are valid only on `EmergencyShutdown CONSTITUTIONAL` ..., `accord:invoke:notify:{notify_id}`, `accord:invoke:drill:{drill_id}`, `accord:lifecycle:active`, the canonical-conferral co-scrub and the pipeline-attest co-scrub below, and the corresponding `FederationAnnouncement` priority `AccordCarrier` ... humanity-accord authority cannot sign anything else. **Wire-isolated AND scope-isolated.**" The next paragraph, part_4:73, says "It does **not** isolate the amendment plane — CC 4.5.1 step 5 and its before the scale gate authority, and the CC 4.5.1.2 entrenched M-of-N ratification, all name accord-holders. That reach is stated here rather than denied"; part_4:211 ("It does **not** wall off amendment"), 1244 and 1303 require accord-roster signatures on amendment and ratification. Narrower than Grok frames it (the carve-out is stated in the same section), but the "only on"/"anything else" enumeration is literally incomplete. Prior: none. Disposition **M**: add the 4.5.1 step-5 sign-off and 4.5.1.2 ratification to the enumeration, or qualify "anything else" as "no other `accord:*` wire domain".

5. **Cover promise vs register cell on leaving.** covers/constitution.md:7: "Anyone may found a root and anyone may leave one." vs part_4:1257: "'must is not acceptance' — the operator accepted the root on the agent's behalf, and the agent cannot leave it"; Exit cell "**agent:** none while held — this cell is stated, not hidden"; Bounded-by cell "ends only when the key stops being a CIRIS agent — the first-contact act of CC 1.13.2, not yet defined". The register states this deliberately ("the condition of symmetry, not an asymmetry"), so the cover overstates. Prior: the "not yet defined" cell was raised by pass3_grok (line 19) and carried in swot pass3 M7 ("the first-contact act named or the cell marked unresolved"); the cover pairing is new. Disposition **R**: steward picks the cover wording (e.g. "any person or node may leave one") against the 2026-10-11 universality ruling; "not yet defined" remains a carried item.

6. **Code pointers in rule text (house rule).** part_3:927 "lives at `formal/trust_root/` in this repository"; part_4:184 `ciris_keyring::HardwareType`; part_4:235 "lives in **`ciris-registry-core`**"; part_4:1718 "refused as policy ([`formal/two_path/PolicyCorridor.lean`](...)). **The table is [`constitution/gover...`". Prior: pass5_gemini defect #3, pass3_grok line 20, swot pass3 M7 ("repository paths → cut"). Not yet applied. Disposition **M** (point to the register's witness row).

7. **"Why this is still 1+4" repeated.** Four instances inside §3.2 alone: part_3:679, 843, 852, 866. Prior: pass3_grok line 21; swot pass3 M7 ("trimmed to one statement"). Not yet applied. Disposition **M**.

8. **NCMEC MUST with no jurisdiction limit.** part_4:1379: "`NcmecCsam` + `PerceptualHashCsam` — operator MUST file the NCMEC CyberTipline report (US 18 USC §2258A)". Prior: pass3_grok line 22; swot pass3 line 46 → M7 ("scoped to operators under US jurisdiction, with 'the equivalent duty under the operator's law' elsewhere"). Not yet applied. Disposition **M**.

9. **History / instance lines in a rule Part.**
   - part_4:1621 "**First deployment**: the *Magnifica Humanitas* encyclical mapping." The "~75-80%" figure pass5 flagged is gone (ALREADY-FIXED for the number); the sentence remains. Prior: pass3, pass5. Disposition **M**.
   - part_4:201 "**The roster is being widened: further named humans will be seated, by roster change on the public record under the standing-majority rule, until about seven hold seats.**" plus the named-holder table at part_4:203–207 (explicitly labelled the instance's current roster, not a grant). "about seven" has no source row. Prior: new. Disposition **R** (steward's instance statement).
   - part_4:1246 "a maintainer-decides model, in the lineage of the open-source projects this ultimately is". Prior: swot pass3 M7 ruled "steward's lines; flagged, not touched". Disposition **X**.

10. **Rendering (source intact, PDF clipped).** Verified in pdftotext of volumes/ciris_constitution-1.0-rc12-constitution.pdf:
    - `IncidentSeverity::INC` cut at the margin (source part_4:71 has `IncidentSeverity::INCIDENT_CONSTITUTIONAL = 5`). Prior: pass3/4/5.
    - 4.5.2.2 HIPAA cell split "retain|sh / are|analyze|train|pu / blish" (source part_4:1344 intact). New.
    - Named-moderator predicate cut at `{moderate|takedown|r` (source part_4:1404 intact). Prior: pass3/5.
    - `subject_of(content_sha` cut (source part_4:1459 intact). New.
    - "Trust ̸= membership" renders ≠ as a combining slash (source part_3:791 has ≠; the PDF Unicode-map gotcha). New.
    Disposition **P**.

## FALSE / MATTER-OF-TASTE / ALREADY-FIXED

11. **`quorum:2/3` vs `"majority"` (Grok defect #3): FALSE.** Two objects. part_3:782 `consensus_protocol: "quorum:2/3", // over the 3 founders — the accord holders` is the `ciris-canonical` *infrastructure community* example; part_3:745 makes `quorum:M/N` mandatory there and bare `majority` non-conformant. part_4:224 `consensus_protocol: "majority", // a strict majority of the standing roster, as every accord threshold is (CC 4.2.6)` is the `humanity-accord` *family*. part_3:753 says so outright: "The same three keys therefore act on two planes that stay distinct: as the accord they decide by `accord_decision` objects under CC 4.2.6 and hold the halt; as the community's founders they sign community rows under `quorum:2/3`." part_3:771 "every later change is 2-of-3" is the community row; part_4:100 "Every threshold here is **M of N over the standing roster**, never a fixed 2-of-3" is the accord. Already adjudicated: volume_swot_rc11_pass3_grok line 57 ("two objects with two protocols"); formal/membership/README.md closes both `majority` and `quorum2of3` configurations. Disposition **X**. Residual reader hazard is real but the source names it in 3.2.

12. **Absence rule (Grok defect #6): FALSE.** part_4:1677, same sentence: "one present, accountable actor may act alone; on that actor's absence a count carries, over the set the door's policy names ...; whoever stays absent never blocks the present actor. The CC 4.2.6 accord kill-switch is the constitutional instance of this pattern: one present holder fires, and a roster change counts its yes-votes against the standing roster, because the roster is the capture vector"; part_4:247 "The firing decision must never deadlock; a roster decision may." "Never blocks the present actor" is the single-actor fast path only. Prior: none. Disposition **X**.

13. **Forward-secrecy "contradiction": FALSE as framed.** part_3:674 says "past-epoch content becomes information-theoretically unrecoverable **to honest holders**" in the very sentence that carries "honest-holder discipline, not a cryptographic guarantee ... structurally undetectable". Nit: "information-theoretically" is the wrong term for key deletion over surviving ciphertext (computational, not information-theoretic). Prior: none. Disposition **M-nit**: drop the adverb.

14. **Duplicated geographic opt-in prose: FALSE.** part_3:646 is one summary paragraph ("**Privacy as opt-in**: joining a geographic community is a one-way disclosure ...") that cites CC 4.5.9; part_4:1541–1548 (4.5.9.1) is the rule. A cross-reference, not duplicated text. Prior: none. Disposition **X**.

15. **Producer MUST vs "rejects the row, or admits it": MATTER-OF-TASTE.** part_4:1332 states the layering on purpose: "the producer's duty is the MUST above ... What the substrate does with a Contribution that breaks it is operator policy: it rejects the row, or admits it and flags `hard_case:subject_authority_missing` for review." Prior: none. Disposition **X**.

16. **WA row "unbounded as drafted" / "none for the deferring party": MATTER-OF-TASTE.** part_4:1256 says "This cell is the finding" in both cells; a declared open privilege, which Grok's own Strengths section credits. Prior: pass3_grok line 19. Disposition **X**.

17. **"Outside the federation's participant set" vs the same three keys as founders: MATTER-OF-TASTE.** part_4:239 concerns the `AccordCarrier` authority class no federation-side class can grant itself; part_3:753 separates the two planes the same keys act on. Prior: none. Disposition **X**.

18. **Regulatory table and "rsvps repurposed as votes" as universal claims: MATTER-OF-TASTE.** 4.5.2.2 is titled "(informational)" and ends "CEG does NOT prescribe which regulatory framework an operator MUST comply with" (part_4:1352). The civic catalogue (part_3:680–692) is headed "Worked example" but carries no explicit informative label; swot pass3 M7 asked for one ("labelled informative"), not applied. Prior: pass4 line 29, pass3 line 21. Disposition **M-lite** for the label; otherwise **X**.

19. **Multipliers 0.95 / 0.9 unsourced: MATTER-OF-TASTE.** part_4:182 "Per-class recommended trust-multipliers: ... `Apple_Secure_Enclave` = 0.95; `YubiKey_5_FIPS` = 0.95; `TPM_2_0` = 0.9" is backed by register row CLM-hardware-class (claims.tsv:101, "per-class trust multipliers"); the derivation is not stated. Prior: pass4_gpt line 18. Disposition **X**.

20. **"Dated external systems" (p.61): MATTER-OF-TASTE.** part_4:1592–1596 dates external matchers ("PDQ (Meta, 2019)", "PhotoDNA (Microsoft, 2009)") in an informational landscape table; not dates on rules. Prior: none. Disposition **X**.

21. **Magnifica Humanitas "~75-80% transparent translation rate": ALREADY-FIXED-IN-SOURCE.** The figure pass5 flagged is no longer at part_4:1621; only the "First deployment" sentence remains (item 9).

## Summary

Counts: CONFIRMED 10 (dispositions: M ×6, R ×1, P ×1, one split M/R/X, one M+R carried cell); FALSE 4; MATTER-OF-TASTE 6; ALREADY-FIXED 1. Previously raised and still open in source: restore path, code pointers, 1+4 refrain, NCMEC scoping, "not yet defined" cell. New and real: H3 areas, over-18 wording, scope-isolation enumeration, cover-vs-register leave promise, three new render clips plus the ≠ glyph.
Most important: (1) the cover's "anyone may leave one" against the register's "agent: none while held" needs the steward's wording (R); (2) part_4:71's "cannot sign anything else" enumeration omits the amendment sign-off its own next paragraph admits (M); (3) part_3:811's "CC 4.2.6 restore path" and part_4:281's "contest ↔ restore" are leftovers of a removed design (M). Grok's headline "quorum:2/3 vs majority" contradiction is a misread of two different objects.
