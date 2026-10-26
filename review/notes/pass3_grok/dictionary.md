# The Dictionary (ciris_constitution-1.0-rc11-dictionary.pdf, 109 pages)

**Care score:** 4
**One-line verdict:** Admission rules disagree with themselves, and several registered families are invisible to the table-only generator this volume says is the count of record, so it cannot be the source of a pinned manifest until those conflicts are ruled.

## Strengths
- The bind and the refusal are stated before the catalogue: an unregistered family is refused, and a reserved prefix from the wrong key is refused by name (p. 1).
- R3 and R4 pin case classes and polarity classes as manifest data, including the point-set reading of `+1.0 only` and `-1 / -0.5 only` (pp. 28–29).
- LegalBasis and wrap_algorithm are two-column (variant name vs wire string), and the text says the wire-string column governs (pp. 45–48).
- The age self-rung split is the same on the Verify row and in the enforcement section: no `self` level on `age_assurance:` (p. 7, p. 94). `licensure:{authority_id}` is open-emitter in both places (p. 3, p. 93).

## Weaknesses
- `age_assurance:*` is "signed" in the Verify table (p. 7) and "enumerated" in the multimedia table (p. 73). R4 makes those different admission sets (p. 28).
- `consent:replication:{version}` is "signed" (p. 23, p. 42) and, later, "positive-only" with "never a negative score" (p. 64), mis-attributed to "the family's consent:state:granted polarity".
- `observation:access_assumption:v1` says "score fixed at +1" and "positive only", then "Polarity: signed" (p. 38).
- `judge_model:verdict:{model_id}` is "PASS/FAIL/UNDETERMINED" and "boolean-via-score" (p. 37). Boolean-via-score is only `{-1, +1}` (p. 28); UNDETERMINED has no point.
- R1 says a family is registered iff it has a CC 3.1 table row "or a CC 3.3 family table", then says a CC 3.3-only family "is registered only once its CC 3.1 row exists" (p. 27).
- Census and ballot prefixes bake `:v1` into the family pattern (`census:share:{class}:v1`, p. 13; also `deferral:request:v1`, p. 36; `rendezvous:route:v1`, p. 21). R3 says the manifest lists family segments "and never this tail", and match strips exactly one trailing version (p. 29).
- The generator "reaches only the CC 3.1 tables" (p. 27), but Persist leaves (p. 9), Edge leaves (p. 20), the four DMA prefixes (p. 25), the four conscience prefixes (p. 26), the RATCHET flags (p. 26), and the coherence detectors (p. 31) are prose, not table rows. That breaks "the family count is generated, not asserted" (p. 1).
- Comparative and other-project wording the house rules exclude: "every widely-used content licence" (p. 3); "what make this Ubuntu-aligned" (p. 36); "Alice scrolls Twitter" (p. 52); "AT Protocol app.bsky.embed.video" (p. 75); "the eltoo argument against Lightning-class penalties" (p. 71).
- History, dates, and attributions on rules: "RFC 6648's lesson" (p. 27); "Guerraoui et al., PODC 2019" (p. 71); "retirement horizons near 2030" (p. 47); "GDPR Art 7(4)/Recital 43, EDPB Op. 08/2024, CJEU C-252/21 Meta" (p. 85); "Texas HB 1181 / Paxton 2025" (p. 103); "Britney's included" (p. 100).
- Code and type pointers in normative text: `EnvelopeKind::IdentityOccurrence` (p. 57), `MessageType::ContentFetch` (p. 34), "persist's DeferralRequest" (p. 36), "the proto enum" (p. 66).
- "The CC 1.13+4 lockdown holds" (p. 72) is not a section id used anywhere else in the volume.
- Worked consent composition emits `hard_case:consent_sla_breach` (p. 44). That kind is not among the canonical `hard_case:{kind}` values, and new kinds "land via the CC 4.5.1 amendment process" (p. 37). The normative deletion signal on the same page is `hard_case:deletion_window_breach` (p. 44).
- `system:*` is a Persist family (p. 9) and an Edge canonical leaf (p. 20). Page 1 promises one owner per family.
- `agent_files:{kind}:{platform_or_target}` is a full Registry row (p. 3) and a full NodeCore row (p. 34). A table extractor will double-count it.
- Transition leftovers: deferral "travels as a contribution: row" "until a substrate's door carries this family" (p. 36); organization / org_membership / partner_record "remain registered and in force" while the affiliation reading is also in force "until that amendment lands" (p. 66).
- Unsourced figures in prose: census composite refused when `source_count < 10` (p. 13); "the row-type slot admits only the five" (p. 18); witness diversity "N=3 default" (p. 36); path ordinals "Twelfth path", "Fourteenth path", "Fifteenth path", "Sixteenth path" (pp. 57, 61, 68, 69) with no list in this volume.
- 3.1.7 ("Namespace summary", including R1–R4) sits before LensCore and NodeCore are catalogued (pp. 27–32).

## Opportunities
- One polarity token per family: delete the second statement on `age_assurance:*`, `consent:replication:*`, and `observation:access_assumption:v1`, and map `judge_model` verdicts onto the point set R4 already defines.
- Strip literal `:v1` from Prefix cells so the tail lives only in `_meta.case_rule.version_segment`, matching the matcher paragraph (p. 29).
- Put every prose-only leaf (pp. 9, 20, 25–26, 31) into the same Prefix / Polarity / Reserved table the generator is said to parse, or the manifest will not match this volume.
- Move comments out of the JCS listings (pp. 8–9) so the signed preimage is only the JSON.
- Cut comparative asides, case citations, and "Design notes (informative)" (pp. 71–72) without adding rules; point the deletion-SLA example at a kind that is already canonical, or add that kind to the p. 37 list in the same edit.
- Move §3.1.7 to after §3.1.10 so the summary is not read as closing the catalogue.

## Threats
- A second implementation can admit a row the first refuses: signed vs enumerated on `age_assurance:*` (p. 7 vs p. 73); signed vs positive-only on `consent:replication:*` (p. 23 vs p. 64); signed vs "positive only" on `observation:access_assumption:v1` (p. 38). R4 says the substrate reads the class from the registry, not the prose (p. 28) — and this prose is what the registry is generated from.
- Page 1 says the prose and the manifest "cannot disagree without the build failing" and, in the next paragraph, "when they differ, the build is broken and the manifest is what shipped." A hostile reader will ask which sentence governs a bad release.
- The wrap_algorithm wire string is broken mid-token in the table that p. 48 says must be matched byte-exactly, in the same section that calls a spelling mismatch a dropped removal notice (pp. 47–48).
- "Zero new structural primitives" / "1+4 preserved" (pp. 40–41, 68) sits next to "Edge v2 EnvelopeKind additions" for `organization`, `org_membership`, and `partner_record` (p. 66). That is the integrity claim of the Part, stated stronger than the wire text.
- Child-safety and incapacity rules cite a 2025 statute and a celebrity conservatorship (pp. 100, 103). A regulator will treat those as politics and anecdote, not as the floor in Q1–Q7.
- Two live models for the same facts — affiliation rows and the three operational subject_kinds (p. 66), and `deferral:*` plus a `contribution:` fallback (p. 36) — are leftovers. An implementer can ship either and claim conformance.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 7, 73 | contradiction | `age_assurance:*` polarity is "signed" and "enumerated". | Keep one class in both tables; regenerate the polarity set from that row. |
| 2 | 23, 42, 64 | contradiction | `consent:replication:{version}` is "signed" and "positive-only" / "never a negative score". | One polarity; delete the consent:state:granted analogy. |
| 3 | 9, 20, 25–27, 31 | contradiction | Prose leaves are "registered" while the generator "reaches only the CC 3.1 tables". | Catalogue those leaves in extractable rows, or stop calling them registered. |
| 4 | 27 | contradiction | Registered "iff" a 3.1 or 3.3 table row, then "only once its CC 3.1 row exists". | One sentence for what "registered" means. |
| 5 | 13, 21, 29, 36 | contradiction | Family patterns include `:v1`; R3 strips one version tail and does not store it on the family. | Prefix column stops before the version segment. |
| 6 | 38 | contradiction | Same row: "score fixed at +1" / "positive only" and "Polarity: signed". | Pick one class. |
| 7 | 47 | rendering | Variant and wire string split mid-token (`HkdfSha` / `256`, `x25519_mlkem768_` / `aes256_gcm_hkdf_` / `sha256`) in a byte-exact table. | Unbreakable row, or the wire string repeated in a single line under the table. |
| 8 | 37, 44 | stale | Example requires `hard_case:consent_sla_breach`, which is not a canonical kind and is not the D2 token `hard_case:deletion_window_breach`. | Emit a listed kind, or add the token to the canonical list in the same passage. |

## Rendering
- p. 3: `cardinality ̸= 1` uses a combining slash over `=`, not a not-equal glyph.
- p. 8–9: SkillImportManifest canonical-bytes listing is split across the page break, with `//` comments inside the JCS object.
- p. 11: type name broken as "SignedIdentityOccurr enceRevocation".
- p. 21: justification gap in "delivered-versus-claimed    A/V".
- p. 47: WrapAlgorithm variant name and wire string broken mid-token (see defect 7).
- pp. 52–53: household diagram split across the page; tree marks render as `-+` and `|`.
- pp. 60–61: pinned RNS hash algorithm split across the page break.
- p. 85: literal backslash in "dimension\'s".

## Effort estimate
About 25–40 hours, and it is not mechanical: polarity, registration, version tails, and the dual organization/deferral encodings need the steward's rulings before a copy edit can delete the comparisons, case citations, and broken table cells.

<!-- model x-ai/grok-4.7; 109 pages; prompt_tokens 94744; completion_tokens 19191; 229s -->
