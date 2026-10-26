# Grok pass-6 Wire report: verification against rc12 source

Checked against the source on branch rc12 (not the PDF). P2 = constitution/part_2_the_grammar.md, P5 = constitution/part_5_transport_substrate.md, P1 = constitution/part_1_foundation.md. Prior = review/notes/pass3_grok/wire.md, pass4_gpt/wire.md, pass5_gemini/wire.md and the volume_swot_rc11_pass{3,4,5} notes.

Report: review/notes/pass6_grok/wire.md
Care score: 4
Verdict paragraph (verbatim): "A second producer cannot pick one signing input or one record-id derivation from this volume until several page-to-page contradictions are ruled; large stretches of the grammar are usable only after that."

Dispositions: M = mechanical fix, R = needs the steward's ruling, P = pipeline/generator, X = reject.

## CONFIRMED

1. `cohort_scope` has no row in the CC 2.1 table while 2.3.2.3 says the envelope fields are "exactly those in the [CC 2.1] table (`cohort_scope`, `subject_key_ids`, `community_id`, `family_id`, `delivery_mode`, etc.)" and the mirror row says "Closed set of seven. No wire default: the member is required." Source: P2:13–73 (no row), P2:204, P2:580. Prior: pass3 raised 2.1-vs-2.6.1.7 member set generally, not this row. Disposition: M (2.1 is hand-written, not generated).

2. Catalog `community_id` row rejects only `cohort_scope == community`. Quote (P2:489): "member absent (admission rejects if cohort_scope == community)" while the Required column on the same row and P2:30 / P2:645 say iff ∈ {community, affiliations}. Prior: none. Disposition: M.

3. `subject_key_ids` has three shapes for one meaning. Quotes: P2:253 "`subject_key_ids: null` or `[]` is the status-quo shape"; P2:446 explicit null refused `envelope_member_null`; P2:470 catalog "member absent" when omitted; P2:579 "Always present in the mirror, an empty array when there is no subject; the column beside the row is absent when empty"; P2:694 beside "OPTIONAL (absent when empty)". Prior: pass3 defect 3; pass3 M1 planned "the 2.1 catalog's subject_key_ids row names the position it describes", NOT landed. Disposition: M (catalog row names `row.subject_key_ids`, always present; 2.3.6 "null" becomes "absent").

4. "Canonical" scope form is not one byte string. Quote (P2:592, repeated P2:738): "The canonical form is the array: an emitter writes ["retain"], and a bare token is admitted as the one-element array it denotes; admission normalises nothing in the signed bytes." P2:34 admits "a bare token or an array of tokens". Prior: none. Disposition: M (reword "canonical" to "preferred"/"the form an emitter writes"), or R if the steward wants bare tokens refused.

5. Structural-invisibility scope residual. 5.2 heading, MUST and pseudocode cover self and family only (P5:61–63, P5:76 "cohort_scope ∈ {self, family}"), but 2.6.1.3 says (P2:514) "[CC 5.2] forbids any holding claim leaving a bounded cohort, unconditionally, and that is the structural-invisibility promise, not a tunable" and 5.2's boundary case says (P5:112) "One rule at every tier ... Self/family is not a special case but the audience rule applied to the smallest roster." Prior: pass3 R48, ruled "5.2 stated once for self/family; community/affiliations get holding claims within the cohort; the other sentences cite 5.2 without adding scope", landed 2efa68e; P2:514 still adds scope to 5.2. Disposition: M under R48 (P2:514 cites the audience rule / 6.1.5.3 for community, not 5.2).

6. 2.6 is titled "Foreword" and the canonicalisation rules, the 1 MiB cap and the signed object (2.6.1–2.6.9) hang under it. Source: P2:394 "## 2.6 `foreword` — Foreword"; constitution/toc.tsv:73. Prior: none. Disposition: M (retitle; toc/codebook row too).

7. Rule 0 says "rules 1–4 below do not reach it" (P2:306); the rules table is above it (P2:297–302). Prior: pass3 M1 planned "below → above", NOT landed. Disposition: M.

8. Consent window named four ways. Quotes: P5:211 "Default window: **24 hours** (operator-tunable per local policy)"; P5:219 "within the 24-hour SLA defined above"; P5:221 "When the 24-hour window lapses"; P5:244 "the CC 5.3.2.2 24-hour obligation"; P5:286 "the CC 5.3.2.2 24-hour window is the one tunable". Prior: pass4 R76 adjacent ("no window" sentence), not this. Disposition: M ("the window, 24 hours by default").

9. 2.6.7 freshness names `signed_at` for attestations. Quote (P2:848): "Consumers receiving an attestation with `signed_at` more than 5 minutes in the future MUST reject as malformed." The attestation envelope's instant is `asserted_at` (P2:588: "Judged against the receiver's clock only where 2.6.7 says (the future bound ...)") and the signature's is `scrub_timestamp`, beside (P2:706); `signed_at` is an STH/cosign member. Prior: none. Disposition: M (name `asserted_at`). The asymmetry STH-cosign skew vs the STH's `signed_at` (P2:850) against lineage-head skew vs the Registry clock (P5:159) is two routes with different reference objects, not a contradiction: MATTER-OF-TASTE.

10. Receipt `epoch` and `K` are `u64 LE`. Quote (P5:482, 484): "‖ epoch (u64 LE) ... ‖ K (u64 LE)" against "`epoch_be8` = the `u64` epoch as 8-byte big-endian" (P5:334; also P5:49); the BE/LE warning at P5:334 is about the nonce and is not pointed at the receipt. Prior: pass3 defect 8; filed on CIRISEdge#891. Disposition: R (edge's answer; the implementer's wire shape).

11. K (fountain-code parameter) has no carrier. Quotes: P5:748 "decodes the chunk once `≥ K` valid symbols have arrived"; P5:744 "the code's parameters are the stream's, not substrate constants"; P5:696 "symbol_envelope = (record_id, u16_be(symbol_index), nonce, ..., tag)" carries no K; no carrier is named in Parts 3, 5 or 6 (grep). Prior: pass4 nonce-input class; A/V framing questions on CIRISEdge#891. Disposition: R (edge).

12. Cover-leaf HMAC unpinned. Quote (P5:790): "`HMAC-SHA3(witness_signing_key, leaf_position || epoch_id)`" against P5:643 "HMAC-SHA3-256(K_record_id, record_id_input)". Prior: none. Disposition: M.

13. Refusal tokens absent from the error table. P5:577 "All error responses MUST conform to:"; the table P5:591–608 maps only `federation_envelope_too_large` (P5:605). Unmapped: `attestation_type_unregistered` (P2:261), `federation_malformed_row` and its reasons (P2:567), `federation_set_semantics_unsorted`, `asserted_at_stale` (P2:854), `trust_root_head_unwitnessed` / `trust_root_head_stale` (P5:542), the census tokens (P2:612–626). Prior: pass3 opportunity ("add one line ... admission tokens are not HTTP codes, or map them"), NOT landed. Disposition: M.

14. `<base64-url>` in the STH and lineage-head request bodies (P5:136–137, 140, 170–171) against the pin (P2:449) "every field documented as base64 MUST use the RFC 4648 §4 STANDARD alphabet, WITH padding" and P2:703 "RFC 4648 section 4 standard alphabet, padded". Prior: pass3 defect 7, pass4 defect 4, pass5 defect 1; pass3 M1 planned `<base64>`, NOT landed. Disposition: M.

15. `K_record_id` / `K_symbol` derivations contradict. Quotes: P5:622–632 "`K_record_id` is a bare HKDF-Expand (no Extract, no MLS KDF-label framing) over the raw group `exporter_secret` ... MUST NOT route this label through RFC 9420 `MLS_Exporter()`"; P5:686 "`K_symbol` and `K_record_id` are the MLS-exporter-derived per-scope subkeys (`HKDF-SHA256-Expand` over the group's raw `exporter_secret`)"; P5:702 "The same ASCII label is used both to derive `K_symbol` from the MLS exporter and as this info-prefix"; P5:837 "`S_dest` is a **separate** exporter from `S_record` (`"ciris-scope-record-v1"`, which feeds `K_record_id` and `K_symbol`, [CC 5.4.1])" — 5.4.1 contains no such label. Prior: pass3 defect 1, pass4 defect 1; on CIRISEdge#891. Disposition: R (edge; read the implementer's design first).

16. TreeKEM conformance vs per-deployment selection. Quotes: P5:42 "**Rekey conforms to MLS TreeKEM ([RFC 9420], normative).** The epoch-DEK rekey on member change is the MLS TreeKEM construction"; P2:791 references row "the streaming epoch-key rekey conforms to MLS TreeKEM"; P5:55 "the **flat per-member cascade (O(N), one grant per member) is competitive-to-better**. The substrate MUST select per deployment based on whether the transport multicasts"; P5:324 media multicast "flat per-epoch `key_grant` cascade". Prior: none in the wire notes (pass5 raised the SFU/relay point, a different item). Disposition: R (edge: which construction is the conformance target; the other becomes a deployment note).

17. "community content is sealed" vs public rooms plaintext. Quote (P1:248, 1.13.3.4): "and `community` content is sealed, its holding claims staying within the cohort ([CC 5.2], [CC 4.4.3.4])" against P5:100 "At those tiers the only plaintext bodies are those of authorized infrastructure communities and public rooms, which [CC 4.4.3.4] names" and part_4 line 559 ("a public room is plaintext, by its record"). A public room is a community (`community:listing:v1`). Prior: none; 1.13.3.4 missed the R9/R49 landing. Disposition: M (name the exception in 1.13.3.4 in 5.2's words).

18. `subject_kind` placement. Quotes: P2:204 "`subject_kind` ... is a **payload-level** field — it lives inside the Contribution payload ... It is NOT an envelope-level field."; P2:664 (and manifests/signed_object.json:796) "Every other member, including subject_kind and the per-family payloads of CC 3.3, rides the envelope untyped by the substrate and is preserved on relay (2.1.1)". The signed-object model has no payload container other than `attestation_envelope`. Prior: pass4 defect/M10 ("subject_kind nesting stated once"), this item NOT landed. Disposition: M under "the signed-object data is the contract": rewrite 2.3.2.3 as "not a typed 2.1 member; rides inside `attestation_envelope` untyped per the `*` row".

19. `[2.1]` cites on members the 2.1 table never defines: `for_key_id`, `period`, `return_token`, `share_index`, `share_count`, `source_count`, `n_eff`, `max_source_multiplicity`, `mass_commitment_hex`, `member_commitment_hex`, `mass_total`, `aggregation_algorithm_id`, `noise_floor_descriptor`, `version`, `partial_a`, `partial_b`, `window_periods`, `active_count`, `floor_applied` (P2:609–627). Prior: pass3 weakness 1 (2.1 "consolidated here once" vs the longer 2.6.1.7 set). Disposition: P (the `cc` field in manifests/signed_object.json; point at 6.1.9 / 4.5.13), regenerate.

20. Shipped state inside the wire volume. Quotes: P5:542 "**Shipped charter defaults.** The shipped roots are minted with **witnessed mode off** (`witness_quorum: 0`, no directory; CC 3.2 T6)"; P1:233 "the shipped roots run with witnessed mode off until it is turned on"; cover (constitution/covers/wire.md) "whether a given MUST has shipped, which is the register's". Prior: pass3 threat. Disposition: R.

21. Underived figures. Quotes: P5:38 "realistic audience churn (~30%/hr), one rotation per departure ≈ 83 epochs/s → a flat-unicast cascade of **~3.1 Tbps — exceeding the ~2 Tbps content fan-out itself** ... ~18.7 Gbps"; P5:284 "ML-DSA-65 sign ~330 µs". Prior: pass3, pass4, pass5. Disposition: R (cut, or cite a register row).

22. Rationale, history and undefined names in normative text. Quotes: P1:219 "the way MLS PCS provides"; P1:235 "mechanized in coherence-ratchet as a consequence of the Kish definition and not yet measured on any attester population"; P1:250 "it would be the surveillance backdoor this framework refuses" and "What CEG adds beyond systems that ship default privacy with no in-network governance"; P2:267 "which requires the founder's explicit ratification"; P5:271 "the 'store at massive scale' CEWP crux"; P5:764 "the CEWP substrate". CEWP is expanded only in the Part 8 glossary (part_8_appendices.md:24), outside this volume. "Stewarded by Eric Moore" is the title page in build_pdf.py. Prior: pass3/pass4/pass5 for most (MLS PCS, "What CEG adds", witnessed-off, coherence-ratchet); CEWP expansion new. Disposition: M for the CEWP expansion at first use; R for the editorial cuts; X for the attribution (deliberate).

23. Cover "One envelope, one signing input, one signature construction" (covers/wire.md) against the STH cosign preimage `sha256("ciris.sth_cosign.v1\n" || ...)` (P5:147), the lineage-head label (P5:178) and the length-prefixed receipt bytes (P5:478). P2:267 already says "What stays off the plane, by definition, is not a claim: ... transparency-log heads and cosigns ([CC 5.3.1] framing)". Prior: pass3 threat. Disposition: M (scope the cover sentence to the attestation row) or R.

24. 5.3.3.3 "canonical bytes per [CC 2.6.1] JCS for the envelope-bearing wrapper" (P5:443) and the receipt's "per [CC 2.6.1] the envelope-bearing wrapper is JCS-encoded, but the receipt's signed-bytes inner payload follows the explicit-length-prefix shape below" (P5:475). Consistent (the receipt's inner signature is a payload member; the `scores` row signs as any row) but never said. Prior: pass3 adjacent. Disposition: M (one sentence).

25. "~5 km² edge-length" (P2:824: "H3 resolution 7 hexagons average ~5 km² edge-length") gives area as length; P2:844 treats the same figure as area. Prior: pass4 M10 ("→ area"), NOT landed. Disposition: M.

26. E1 is one run-on table cell carrying the route fetch, the seal, the LXMF exclusion and the relay-key rule (P5:467). Prior: none. Disposition: M (taste: numbered MUSTs).

27. `GET /v1/rotation-history` is one sentence with no schema (P5:556–558) and 5.3.5 defers schemas to "a versioned OpenAPI document alongside this one" (P5:564) while the cover says the volume is what an implementer builds from. Prior: none. Disposition: MATTER-OF-TASTE (R only if the volume should carry those schemas).

28. Normative crypto cites unversioned drafts: X-Wing, HPKE-PQ, XChaCha (P2:798–800, no -NN). Prior: none. Disposition: MATTER-OF-TASTE, low M (pin the draft revision).

29. `additional_scrubs` row in the JCS catalog (P2:483) already carries "(beside the row)" in the cell; the table heading still reads "Canonical when explicit". Prior: none. Disposition: MATTER-OF-TASTE, optional M (move to a note under the table).

30. Quorum formula spelled `floor(|witnesses|/2)+1` in the generated 2.6.1.7 note (P2:606, from manifests/signed_object.json) against `⌊|witnesses|/2⌋ + 1` at P2:47. Cosmetic. Disposition: P.

## ALREADY-FIXED-IN-SOURCE

31. Key-plane explicit nulls against 2.6.1.1.1 (Grok threat: "A key-plane revocation binds explicit JSON nulls inside revocation_envelope (p. 22) while the attestation rule refuses null (p. 29)"). P2:295: "This is the key plane's own signing contract: `scrub_timestamp` is inside the bytes because it is the anti-rollback ordering key, and the explicit `null` is the one exception to the no-null rule of [CC 2.6.1.1.1], which governs the attestation envelope." P2:446: "(the key plane's `revocation_envelope` of [CC 2.4.1.1] is the one exception: it binds its absent optionals as explicit `null`)". Prior: pass5 R88 (CIRISPersist#1125). The text names the exception on both sides.

## FALSE

32. Email vector mismatch ("abbreviated wire form is `04481a02...98d0a263f`. The hex printed beside it ends in `8d0a263f`, not `98d0a263f`"). The hex (P2:175) is `04481a02fccfc8d99a47bde4f0563dd360d425b0734e8fcd8d5dd7198d0a263f`, ending `…dd7198d0a263f`; `98d0a263f` is its last nine characters. All five digests recompute correctly (sha256 of the UTF-8 preimages). Prior: pass3 made the same misread. Optional M: the five suffixes are 7, 8, 8, 8 and 9 characters; make them uniform.

## Rendering (all P; source checked intact)

33. p. 24 clipped `scope: ["personhood_consti`: source P2:316 intact. Flagged in passes 3, 4, 5 and 6; renderer still clips a long code span at a line end.
34. pp. 14, 16, 28 hex and JSON wraps inside code spans and table cells: source intact; converter.
35. pp. 3–4 mid-word hyphenation in the adversary table (`ob-server`, `re-ceiver`): renderer.
36. `X25519MlKe m768Aes256GcmHkdfSha256`: source P5:17 intact; identifier-break rule.
37. p. 69 `federation_stream_chunks(stream_id,` collides with the next column: P5:28; the table needs the row-block path.
38. p. 59 single-row continuation page: renderer.
39. pp. 89–90 E1 as one run-on paragraph: that is the source (item 26), not the renderer.

## Summary

30 of Grok's 32 substantive findings hold against the rc12 source, 1 is already fixed (the key-plane null exception, R88), 1 is false (the email vector). Seven confirmed items were planned as mechanical by earlier passes and never landed (base64-url, Rule 0 "below", the subject_key_ids catalog row, km² edge-length, subject_kind nesting, the error-table line, the personhood clip); eight are new (cohort_scope row, community_id catalog scope, "Foreword", 24-hour wording, signed_at freshness, HMAC-SHA3 unpinned, "community content is sealed", TreeKEM vs per-deployment select); five need rulings (K_record_id, TreeKEM, receipt endianness, the K carrier, shipped state and figures).
