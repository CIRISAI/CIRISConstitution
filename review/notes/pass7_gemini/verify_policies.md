# Gemini pass-7 verification: The Reader's Policies (rc12)

Checked against branch rc12 at f7d2af2 (constitution/part_4_composition_governance.md unless stated; no commit after f0b6328 touches Part 4) and volumes/ciris_constitution-1.0-rc12-policies.pdf (built 2026-10-26 20:44, after f0b6328 at 20:04, so PDF and source match). Pages are PDF pages; lines are source lines. Volume = covers/policies.md + 4.1.x + 4.4.x (toc.tsv); 4.2, 4.3 and 4.5 are outside it.

**Care score recorded:** 3 (pass 6 Grok gave 4).
**Verdict paragraph recorded:** "Substantively rigorous and free of banned words or historical attribution, but needs a targeted editing pass to resolve two direct contradictions on delegation depth and trust-root attachment, fix clipped tokens, and replace design-review shorthand with constitutional prose." Of the two "direct contradictions", the depth-cap one is a misread and the trust-root one is a vocabulary gap rather than a contradiction of mechanism.

Dispositions: M = mechanical fix, R = steward ruling, P = pipeline, X = reject. Pass 6 = review/notes/volume_swot_rc12_pass6_grok_2026-10-26.md + review/notes/pass6_grok/verify_policies.md.

## CONFIRMED

1. **Trust-root attachment edge in 4.4.3.8 is pre-T3 vocabulary (Gemini defect 1, "contradiction").** Finding: 4.4.3.8 item 3 describes the consumer's root-attachment row as a scoped capability delegation and never names the `trust:accepts:v1` dimension that CC 3.2 T3 requires and that 4.1.1 relies on to exempt the edge from the cycle check.
   - part_4:1188: "A consumer trusts one by hanging `delegates_to(user → root, [infra:attest, infra:serve])` off the base — added and removed freely, base untouched."
   - part_4:23 (4.1.1 table): "a `trust:accepts:v1` acceptance edge ([CC 3.2] T3, node → root) is the node's un-trust lever and confers nothing on the root, so it is outside the cycle check in either arrival order; a capability `delegates_to` closing the same pair is still refused"
   - part_3:881 (T3): "a live acceptance edge `delegates_to(node → root)` bearing `trust:accepts:v1`"; part_3:33: the trust jobs are "carried as `dimension` values on `delegates_to` rows".
   - Verdict: CONFIRMED as stale vocabulary, not as a contradiction. Both texts put the edge on a `delegates_to(user/node → root)` row; what item 3 omits is the `trust:accepts:v1` marker, and as written (a scope list, no dimension) it reads as the capability edge 4.1.1 says is refused when the root has already delegated to that key (item 6, `delegates_to(root → key, [scope])`). Item 4's "Deleting the `user → root` edge" is the T3 one-row deletion and is consistent. Gemini's "will reject it as a cycle" is the right worry about the sentence as written, not about the design.
   - Pass 6: not raised. M16: did not touch 4.4.3.8. Not a regression.
   - Disposition: **M** — rewrite item 3 as "hanging the acceptance edge — `delegates_to(user → root)` bearing `trust:accepts:v1` (CC 3.2 T3) — off the base". Whether the acceptance edge also carries a scope list is a wire-shape question for persist; if the steward wants the scope list kept, that half is **R**.

2. **`resolve_community` / `resolve_family` pseudocode still walks a `supersedes` chain over a `community` Contribution (Gemini defect 4, "unclear rule").** Finding: the prose says a roster change is a `prev_head_digest`-chained roster version and never a `supersedes` Contribution; the two resolvers and the determinism bullet still say the opposite.
   - part_4:426 (4.4.3.2.3): "A proposed membership change is a **new version of the roster record** ([CC 3.2] T6), admitted under the group's quorum and chained by `prev_head_digest` … — never a single-signer `supersedes` Contribution"; part_4:761 (4.4.3.4.2) the same for families.
   - part_4:497–499 (`resolve_community`): `.where(subject_kind == "community")` / `.where(supersedes chain → latest non-superseded)`; part_4:947 (`resolve_family`) and :984 (`resolve_self`) identical; part_4:512 (4.4.3.2.4.1 (a)): "**"latest non-superseded"** — the `community` Contribution with the highest `signed_at`".
   - part_3:148: the roster version is `group:roster:v1`, "a cosigned `scores` row — `attested_key_id` the group, envelope carrying the fold …, `prev_head_digest` and `charter_digest`."
   - Verdict: CONFIRMED. The sentences at :426/:761 came in with erratum 92458e6 (2026-10-04); the resolvers were never re-pointed. M16 reflowed the three blocks (diff lines 100–105, 288–293, 302–306) and kept the `supersedes chain` text, which it never claimed to fix.
   - Pass 6: item 15 raised only the reflow (P/M); the vocabulary mismatch is new. Not a regression.
   - Disposition: **M** — the resolvers walk the `group:roster:v1` lineage by `prev_head_digest` to the T6 head and bullet (a) defines "latest" as the head, not the highest `signed_at`. If the implementer's `community` Contribution still exists beside the roster row, the resolver shape is persist's and the rewrite is **R** (read the implementer design first).

3. **`resolve_member_transport` comment generalises the founder-quorum to every community (Gemini defect 7).** Finding: bullet (a) scopes founder-subset evaluation to `cohort_subkind: infrastructure`, the (b) comment and the "three resolutions" sentence say founder-quorum for any `C`.
   - part_4:514: "**founder-subset eval** — for `cohort_subkind: infrastructure` … admission is `evaluate_consensus_protocol` over `{m: m.role == founder}`, NOT all members."
   - part_4:520: `members = resolve_community(C, now) // (a) above; founder-quorum verified`; part_4:535: "**WHO** = `resolve_community` (signed Contribution + founder-quorum)".
   - Verdict: CONFIRMED (an imprecise comment, not a conflicting rule; :537 cold-start is about `ciris-canonical`, which is infrastructure, so that one is right).
   - Pass 6: not raised. Not a regression.
   - Disposition: **M** — "// (a) above; admission verified under the current consensus_protocol (founder subset for infrastructure)"; same at :535.

4. **"1+4" used three times in the volume and defined nowhere in it (Gemini defect 5, "editorializing").** Finding: the slogan is defined at CC 1.7 (part_1:100, Charter/Constitution volumes) and glossed at 4.5.x (part_4:1320, :1538), none of which is in the Policies volume.
   - part_4:703 (p. 17): "**Why this is still 1+4.** One `cohort_scope` value (`affiliations`) + one declared config record riding existing machinery"
   - part_4:849 (p. 23): "**1+4 preserved** — a `scope` vocabulary + enforcement addition over the existing `delegates_to`"
   - part_4:1195 (p. 34): "**1+4 preserved** — every element above composes the existing `attestation` and `delegates_to` primitives; no new structural primitive"
   - Verdict: CONFIRMED (the volume does not stand alone on the term). Gemini's suggested gloss "the five structural primitives of CC 2.4" is the right one; its Opportunities gloss "one structural primitive plus four envelope/scope mechanisms" is wrong.
   - Pass 6: not raised (pass 6 flagged other design-note residue, landed in M16). Not a regression.
   - Disposition: **M** — one gloss on first in-volume use (:703): "the 1+4 primitive set of [CC 1.7] / [CC 2.4]"; the other two may stay as is.

5. **Implementation names as actors in 4.4.3.4.3.1 and 4.4.3.3 (Gemini defect 6, "stale").** Finding: `Verify`, `Registry` and `NodeCore` remain as proper-noun actors after M16 removed three of the pass-6 instances.
   - part_4:872 (heading): "Signing member sets (normative — the JCS contract Verify hybrid-signs)"
   - part_4:891 (table column): "| Member | Value | Verify name |"
   - part_4:934: "Registry owns these member sets (this section); Verify computes `JCS(...)` + the hybrid Ed25519+ML-DSA-65 signature over each"
   - part_4:715: "each NodeCore `external_content` sub_kind (`encyclopedia_article`, `news_article`, `accord_data`, `local_data`)"
   - Verdict: CONFIRMED for `Verify`/`Registry`/`NodeCore`. **FALSE for `lenscore_detector`** (part_4:1191): it is an `identity_type` role value (part_3:1999, :2009), i.e. wire vocabulary, not a component name.
   - Pass 6: item 12 raised "Per CIRISNodeCore three-tier interface model" (:688), "Portal / Verify dashboards" (:62), "a Verify implementation" (:1133) and "the JCS contract Verify hybrid-signs" (heading). M16 fixed :62, :688 and :1133 (diff lines 18, 211, 347–348) and left the heading, the column, :934 and :715. **REGRESSION** (partial landing of a claimed M16 batch).
   - Disposition: **M** — "the JCS contract the verifier hybrid-signs"; column "Verifier name" or drop; "This section owns these member sets; the verifier computes `JCS(...)`"; "each `external_content` sub_kind". Part 5:256 carries the same "Registry owns … Verify recomputes" sentence and should move with it.

6. **Missing connective in the 4.1.4 table (Gemini defect 8).** Finding: the CC link is used as a bare citation so the rendered sentence reads "matters CC 2.4.1.3".
   - part_4:49: "The `recants` distinction matters [CC 2.4.1.3](part_2_the_grammar.md#2.4.1.3), but the practical anti-arbitrage countermeasure is consumer-policy behavioral analysis". PDF p. 3 line 43: "The recants distinction matters CC 2.4.1.3, but the practical".
   - Verdict: CONFIRMED. Pass 6: not raised. Not a regression.
   - Disposition: **M** — "matters ([CC 2.4.1.3])" or "matters per [CC 2.4.1.3]".

7. **Missing space in the 4.4.3.2.5 worked-example code block (Gemini rendering p. 11).** Finding: one `cohort_scope:community` inside the fenced step 4; everywhere else the volume writes `cohort_scope: community`.
   - part_4:574: "4. Alice now receives cohort-filtered visibility for cohort_scope:community content". PDF p. 11 line 21 identical.
   - Verdict: CONFIRMED. Pass 6: not raised. Not a regression. Disposition: **M**.

8. **`watch_sla` and `ratified_pair` long lines wrap mid-expression (Gemini rendering p. 29).** Finding: three single-line `.where(...)` chains in source wrap onto unindented continuation lines in the PDF.
   - part_4:1034: `sla = T.attestations.where(attesting_key_id == T.attesting_key_id).where(dimension == "consent:deletion_sla:*").latest.extract_days`
   - part_4:1040: `completion = T.attestations.where(attesting_key_id == T.attesting_key_id).where(dimension == "consent:deletion_complete").where(asserted_at > revocation_at).first`
   - part_4:1054: `rows   = federation_attestations.where(subject_kind == "consent_record").where(envelope.bilateral_pair_id == pair_id).where(envelope.stance == "granted")`
   - PDF p. 29 lines 31, 38, 55 show the continuation fragments Gemini quotes.
   - Verdict: CONFIRMED. Pass 6: item 15 raised the same class for `resolve_community`/`resolve_family`/`resolve_self` (pp. 8–10, 19, 26), which M16 reflowed; these two blocks were not on that list. Not a regression.
   - Disposition: **M** (reflow in source like the resolvers) plus **P** (a code-block wrap rule would make the source reflow unnecessary).

9. **Policy G inline code clipped at the margin (Gemini defect 3, rendering p. 35).** Finding: the inline composition pattern overflows and the overflow is cut, not wrapped.
   - part_4:1239 (intact): "Composition pattern: `cert_validity:{authority} + transparency_log:inclusion + (attestation:registry_consensus OR attestation:license_validity)`"
   - PDF p. 35 lines 39–40: "Composition pattern: cert_validity:{authority} + transparency_log:inclusion + (attestation:regi" / "OR attestation:license_validity)" — `stry_consensus` is lost.
   - Verdict: CONFIRMED (renderer). Pass 6: item 14 (and every pass since 3). M16 did not claim it (renderer work is a separate thread). Not a regression.
   - Disposition: **P** — allow breaks after `:`/`_` in inline code, or **M** split the pattern into a fenced block.

## FALSE

10. **Depth cap "contradiction" (Gemini defect 2, Threats paragraph 1).** Finding: 4.1.1 names a consumer default of 5 that is explicitly configurable and a separate, optional substrate ceiling; 4.4.3.2.8.C's "configurable depth cap (> the CC 4.1.1 default-5 for deep secretariats)" is that same consumer configuration; the cover's "within the depth cap" is the cap in force.
   - part_4:21: "Consumer policy MUST cap traversal depth at **5 hops** by default (configurable) … A substrate MAY additionally clamp any caller-requested depth at an absolute ceiling; the ceiling bounds the walk, it does not raise the default"
   - part_4:667: "a **configurable depth cap** (> the [CC 4.1.1] default-5 for deep secretariats)"
   - covers/policies.md:7: "only a `grant`-scoped delegation from the owner confers issuance, within the depth cap and the yearly term."
   - Verdict: FALSE. The three sentences compose: the consumer raises its default; a substrate ceiling, where one exists, bounds the walk and chains past it fall to `attestation:self_verify`. "An implementer cannot tell" is answered by "(configurable)" and "the ceiling bounds the walk". Gemini's quotation "the ceiling bounds the walk, it does not raise the default" is accurate and is the rule. Pass 6: not raised. Disposition: **X** (optionally a two-word M at :667, "raised above its default of 5 by consumer policy").

11. **`lenscore_detector` as an undefined component name (half of Gemini defect 6).** It is an `identity_type` role token (part_3:1999: "a folded CIRISAgent occurrence whose key is BOTH `agent` AND `lenscore_detector`"), reserved-prefix holder for `detection:*`; wire vocabulary, not a repository. Disposition: **X**.

## MATTER-OF-TASTE

12. **The Opportunities gloss for "1+4".** Gemini proposes "one structural primitive plus four envelope/scope mechanisms"; CC 1.7 says the structural set is five (part_1:106: "The structural set is five"). The defect (item 4) stands; the proposed wording would introduce an error. Noted so the landing does not copy it.

13. **Gemini's suggested comment text for item 3** ("consensus_protocol verified (founder-quorum for infrastructure)") is fine as is.

## Not raised by Gemini (for the record)

The cover's licence rule vs a `license`-scoped delegation (the settled misread) was not raised. R95 (part_4:826 now "The pair is a data-management record, not a veto … An agent has no veto over its steward's data choices … the accept half carries the binding, not a say in the stream") and `history_on_join` were not raised. Spot-check of the pass-6 M16 batch in Part 4: "seven members" 0, `subject_key_ids[0]` 0, H3 parent `85283083fffffff` present, "waivable below threshold" 0, "M-1's symmetry" 0, "the operator the seed lacked" 0, "four implementations" 0, "decides nothing today" 0, "resolves to none" 0, `CIRISNodeCore` 0, the A–M policy index present at :352. One FISA mention survives at :682 but as an enum example ("not a closed HIPAA/SOX/FISA enum"), not the compliance claim pass 6 flagged.

## Summary

9 confirmed (8 M, of which one is a REGRESSION — the Verify/Registry/NodeCore residue of a pass-6 M16 item — and one needs persist's roster-resolver shape before landing, possibly R; 1 P for the Policy G clip), 2 false (the depth-cap "contradiction"; `lenscore_detector`), 2 taste. Top three: the 4.4.3.8 root-attachment sentence that omits `trust:accepts:v1` (the one finding that could mislead an implementer into writing a capability edge the cycle check refuses); the three resolvers and bullet (a) still walking a `supersedes` chain over a `community` Contribution after the roster became a `prev_head_digest`-chained `group:roster:v1` row; the `Verify`/`Registry`/`NodeCore` residue after M16.
The volume reads better than at pass 6: every pass-6 confirmed item except the renderer clip is gone from source (the eight-member JCS set, the reserved `history_on_join`, the `resolve_consent` comment, R95 landed as "not a veto", the H3 cells, the `designated_officials` threshold, the legal gloss, the stray ")", the self-pointing comment, the A–M index), and Gemini found no new contradiction that survives verification; what remains is one vocabulary gap at the trust-root seam, one stale pseudocode shape, and mechanical residue, which is why Gemini's 3 against Grok's 4 reflects Gemini weighting its two misread "contradictions" rather than a worse text.
