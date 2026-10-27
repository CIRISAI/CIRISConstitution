# verify-threats (pass 7, Gemini 4 Argon) — checked against rc12 @ f7d2af2

Source: review/notes/pass7_gemini/threats.md. Volume = CC 1.13.3 (constitution/part_1_foundation.md:207–250) + Part 5 (constitution/part_5_transport_substrate.md) + constitution/covers/threats.md.
Pass-6 baseline: review/notes/pass6_grok/verify_threats.md (16 confirmed, 5 carried; care 4) and the Threat Model block of review/notes/volume_swot_rc12_pass6_grok_2026-10-26.md:97–106.

**Care score recorded:** 3.
**Verdict paragraph recorded (verbatim):** "Cryptographically rigorous and honest about non-goals, but needs a targeted cleanup pass to fix an inconsistency in MLS exporter KDF hash functions, resolve a contradiction on live-call relay topology, and purge a broken markdown link and internal design shorthand."

Legend: (a) finding · (b) verdict · (c) file:line + quote (CONFIRMED only) · (d) pass-6 status; REGRESSION if M16 (f0b6328) or edge-answers (81746c7) claimed the fix · (e) disposition M / R / P / X.

---

## 1. Broken markdown link in 1.13.3.4 (Top #2, Rendering p.5)
(a) A literal `.4.3.4](part_4_composition_governance.md#4.4.3.4))` fragment sits in the running prose of 1.13.3.4 after the public-rooms cite.
(b) **CONFIRMED.**
(c) `constitution/part_1_foundation.md:248`: `…whose holding claims sit at federation scope ([CC 4.4.3.2.1](part_4_composition_governance.md#4.4.3.2.1)).4.3.4](part_4_composition_governance.md#4.4.3.4)) — where, for `self`…`
(d) Pass 6 did not raise it. Introduced by the pass-5 landing (2efa68e); M16 (f0b6328) rewrote line 248 and carried the fragment through unfixed. Not claimed fixed → not a REGRESSION, but it survived one full edit of the line and the link checker (check_links.py) does not catch a stray tail after a closed link.
(e) **M** — delete the stray `.4.3.4](…))` tail; the 4.4.3.4 cite already appears earlier in the sentence.

## 2. KDF hash-family "inconsistency" 5.4.1 / 5.4.2 / 5.4.6, and "0x004D key-schedule hash is suspect" (Weakness 2, Top #3)
(a) Report says 5.4.1 derives `K_symbol` with HKDF-SHA256-Expand while 5.4.2 uses HKDF-SHA3-256, and 5.4.6 derives `k_destination` with SHA256-Expand then `destination` with SHA3-256 "without noting a hash-family switch"; and that X-Wing's internal SHA3/SHAKE makes "the ciphersuite 0x004D key-schedule hash is SHA-256" suspect.
(b) **FALSE** as an inconsistency. The chain is one deliberate two-stage pattern applied identically twice: stage 1 is a bare HKDF-SHA256-Expand over an MLS exporter output (SHA-256 because that is the MLS key-schedule hash of the X-Wing suites, `part_5:663`), stage 2 is an HKDF-SHA3-256 extract-then-expand producing the per-object key (`symbol_key` at `:724`, `destination` at `:850`). 5.4.3 states the rationale once (`:775`: "chosen for hash-family separation from the SHA-256 key-schedule hash used one layer up"). On 0x004D: X-Wing's SHA3-256/SHAKE256 live inside the KEM combiner, not in the MLS key schedule; the MLS KDF for the X-Wing ciphersuites is HKDF-SHA256, which is also why 5.4.4 pins `KDF = HKDF-SHA256` for the Welcome HPKE (`:791`). The parenthetical is correct.
(c) n/a.
(d) Not raised by pass 6. Not a regression (the two-stage text at `:646–:663` was added by M16 as edge's 5.4.1 exporter chain; it is internally consistent).
(e) **X** — the only residue is taste: 5.4.6 could carry a four-word pointer to the 5.4.3 rationale. Not required.

## 3. "No relay" vs "a relay sees the outer layer only" (Weakness 3, Top #4)
(a) 5.3.3.2 says realtime groups use direct Links with "no relay tree" / "no selective-forwarding relay role" and 5.3.3.2.1 says "no relay reads it"; 5.3.3.2.5, E1 and 5.4.2 speak of a relay that forwards and sees only the outer seal.
(b) **CONFIRMED** as a terminology ambiguity, not a contradiction. The sentences reconcile (an application-layer fan-out/SFU relay is absent; an RNS transport hop forwarding Link packets exists and sees outer ciphertext) but the Part never says "relay" has two senses, and 5.4.6 uses a third phrase ("non-member transport node", "forwarder") for the same thing.
(c) `part_5:366`: "direct Reticulum Links between participants (low-latency push; no relay tree needed at small N)"; `:367`: "no selective-forwarding relay role"; `:379`: "no relay reads it"; `:430`: "the outer seal is the per-RNS-Link transit wrap (a relay sees the outer layer only, never plaintext — the [CC 5.3.3.5 E1] two-layer posture)"; `:487`: "Which key binds a non-member relay"; `:738`: "the symbol AEAD protects the A/V plane's symbols in transit and at any relay that forwards them"; `:866`: "a non-member transport node … the forwarder carries link ciphertext only".
(d) Pass 6 raised the sibling ("multicast" in two senses, verify #15 → M16 landed "one-to-many delivery") but not "relay". Pass 5 R87 ("no relay under pull-only fan-out") is the fan-out sense. Not a regression.
(e) **M** — one sentence at 5.3.3.2.5 or E1 §1: "relay here means a transport node forwarding Link frames, never a media fan-out role (5.3.3.2 has none)"; align 5.4.6's "forwarder" wording to it.

## 4. SealedAvChunk whole-chunk double AES-256-GCM vs A/V "symbols" each XChaCha20-Poly1305-sealed; clear 48..52 header blinded (Weakness 4, Threat 1, Top #1)
(a) 5.3.3.2.3/5.3.3.2.5 define the A/V unit on an RNS Link as `SealedAvChunk` with a clear 52-byte header and two AES-256-GCM layers, and 5.4.4 says the live A/V chunk is AES-256-GCM "at every layer"; 5.4.2 and 5.4.3 say the A/V plane alone carries each sealed chunk as indexed symbols and the substrate MUST seal every A/V symbol under XChaCha20-Poly1305 in a `symbol_envelope` that carries no codec/layer header.
(b) **CONFIRMED.** Three-way contradiction in normative text. Either the symbol seal is a third AEAD layer on A/V (then "at every layer" is false and the clear `codec_id`/`ChunkLayer` block is inside symbol 0's ciphertext, so a serving peer selects a layer only after opening symbol envelopes — contradicting "clear metadata, NOT inside the AEAD"), or the A/V chunk rides the Link whole under the E1 seal (then 5.4.2's MUST and 5.4.3's "only the A/V plane emits symbols" are dead text). A fourth strand: 5.4.2 requires real A/V symbol envelopes be indistinguishable from *cover* symbol envelopes (`:715`), while 5.4.3 §4 says the A/V plane is never shaped (`:751`), so no cover exists on that plane.
(c) `part_5:412`: "The realtime A/V chunk that lands on each RNS Link payload (and the broadcast pull path)" + layout `52.. double_sealed_ciphertext`; `:430`: "`double_sealed_ciphertext` is outer-AEAD( inner-AEAD( chunk_plaintext ) ) — two independent AES-256-GCM layers"; `:436`: "`codec_id` and `ChunkLayer` stay clear metadata outside both AEADs"; `:795`: "the live A/V chunk is sealed with AES-256-GCM at every layer ([CC 5.3.3.2.5])"; `:715`: "the realtime A/V plane ([CC 5.3.3.2]) alone carries each sealed chunk as symbols — its indexed fragments on the wire — and each emitted symbol is sealed under its own AEAD key … The substrate MUST seal every A/V symbol it emits with the framing below"; `:728`: "XChaCha20-Poly1305(symbol_key, nonce, fragment)"; `:775`: "Only the realtime A/V plane ([CC 5.3.3.2]) emits symbols: a sealed A/V chunk is carried as indexed symbols, the fragment unit of that plane … Each symbol is sealed independently under the `symbol_key` derivation and `symbol_envelope` layout of [CC 5.4.2]".
(d) Pass 6 raised it: verify #6 EXTRA ("P5:764 XChaCha attributed to A/V symbols; live A/V is AES-256-GCM → M") and SWOT line 101 ("`part_5:764` attributes XChaCha20-Poly1305 to the A/V plane; live A/V is AES-256-GCM at every layer … → M16"). **REGRESSION:** M16 (f0b6328) answered by *adding* the "at every layer" sentence at 5.4.4 (`:795`, absent at 2efa68e) while leaving 5.4.2 and 5.4.3 attributing XChaCha symbol seals to the A/V plane; the edge-answers commit (81746c7) then removed the fountain-coding/RaptorQ sentence at 5.4.3 but kept "symbols" as the A/V fragment unit, so the defect pass 6 named is now an explicit, sharper contradiction rather than a stray attribution. Register context: CLM-symbol (5.4.2) is established only on `derive_symbol_key` in CIRISVerify; the producer path is staged on CIRISEdge#651 as planned; the clear-header authentication is the open wire change CIRISEdge#892. None of those rows resolves which text is right.
(e) **R** — steward/edge ruling: with fountain coding gone, does the A/V plane still fragment into `symbol_envelope`s at all? If the chunk rides the Link whole under E1 (the 5.3.3.2.3 reading), 5.4.2 retargets or is cut and 5.4.3's "fragment unit on the A/V plane" paragraph goes; if symbols stay, 5.4.4's "at every layer" goes and 5.3.3.2.3 must say where the 52-byte header sits relative to symbol 0 (this is the CIRISEdge#892 surface). The cover-on-an-unshaped-plane strand (`:715` vs `:751`) falls out of the same ruling.

## 5. Design-log tags D2 / D3 / D4 / D6 (D1, D5 never appear) (Weakness 5, Top #6)
(a) Decision labels from an internal design log survive in a heading, two bold lead-ins and two cross-references, with no definition anywhere in the CC and gaps in the numbering.
(b) **CONFIRMED.**
(c) `part_5:11`: "## 5.1 `epoch` — Epoch keying + cascade (normative — D2 / D3)"; `:30`: "**Epoch triggers (D3)**"; `:358`: "the D6 reachable set ([CC 5.3.3.4])"; `:450`: "**Incremental verify** (D4)"; `:453`: "#### 5.3.3.4 `liveness` — D6 liveness invariant"; `part_1:235`: "([CC 5.3.3.4] D6)". `grep -w D1`/`D5` across constitution/: no hits.
(d) Not raised by pass 6 (pass 5's stale-ref checker covers ticket shorthand and lock tags; these escaped it). Not a regression.
(e) **M** — drop the four D-tags (the section numbers already carry the reference); add `\bD[1-9]\b` next to a section heading to check_stale_refs.py's shorthand class.

## 6. E1–E4 labels (same Weakness/Top #6)
(a) Report wants E1–E4 stripped alongside the D-tags.
(b) **MATTER-OF-TASTE.** Unlike the D-tags, E1–E4 are defined in place as the Decision column of the 5.3.3.5 table (`part_5:466–471`) and are load-bearing cross-references from part_1:248, part_5:15, :430, :478, :566, :748 and :872 ("the E1 handshake", "E1 two-layer hybrid"). Pass 6 flagged only E1's cell length (verify #16 → M16 landed the numbered sentences at `:473–:487`).
(c) n/a.
(d) Pass 6: the cell, not the labels. Not a regression.
(e) **X** — keep; if the steward wants names, "E1" → "the transit seal rule" is a global rename, not a cleanup.

## 7. `DAS` never expanded (Weakness 6)
(a) 5.3.2.4.5 says "the [CC 2.1]/DAS scope-filtered read".
(b) **CONFIRMED.** `grep -w DAS constitution/*.md` returns this one line in the whole Constitution.
(c) `part_5:287`: "- **query**: the [CC 2.1](part_2_the_grammar.md)/DAS scope-filtered read; cost is the predicate + index, independent of tier."
(d) Not raised by pass 6. Not a regression.
(e) **M** — delete "/DAS" (the CC 2.1 cite is the definition) or expand it once.

## 8. `Path B` with no Path A (Weakness 6)
(a) 5.3.5 labels one endpoint "(Path B)".
(b) **CONFIRMED.** No "Path A" anywhere in constitution/.
(c) `part_5:584`: "`GET /v1/verify/build-manifest/{project}/{version}/{target}` (Path B) returns the verbatim signed BuildManifest."
(d) Not raised by pass 6. Not a regression.
(e) **M** — drop "(Path B)".

## 9. "the 1+4 surface" used before definition (Weakness 6)
(a) "1+4" appears eight times in Part 5 (`:242, :319, :373, :377, :525, :529, :638`) as insider shorthand.
(b) **MATTER-OF-TASTE / volume assembly.** It is defined at CC 1.7 (`part_1:100`, "The 1+4 minimal-and-adequate claim"), which the Threat Model volume does not include (it carries 1.13.3 only). Inside the full Constitution the term is defined before Part 5.
(c) n/a.
(d) Not raised by pass 6. Not a regression.
(e) **M** (cheap) — one gloss at the first Part-5 use (`:242`: "the 1+4 surface, CC 1.7") so each volume stands alone.

## 10. "iOS has no WebM / Opus playback; the common UI toolkits decode none of the images" (Weakness 7, Top #8)
(a) A Tier-B table cell justifies the sender-converts rule by naming a third-party platform's codec support.
(b) **CONFIRMED** as a house-rule breach (comparative/product claim in a Part). The pass-5 stale-ref checker's PROJECTS list already treats "Android 1x" as a product name (tools/check_stale_refs.py:35); "iOS" is not in the list, so it passed. The factual half (whether current iOS plays WebM/Opus) is contestable and is not adjudicated here; the table is marked "recommended CCC policy — not normative" (`:302`), which limits the damage.
(c) `part_5:309`: "| AVIF, HEIC / HEIF, JXL, WebM, MOV, MKV, Ogg / Opus, FLAC, WAV, ADTS, Markdown | **B — sender converts to a Tier-A form before hashing; raw arrival = C** | iOS has no WebM / Opus playback; the common UI toolkits decode none of the images |"
(d) Not raised by pass 6. Not a regression.
(e) **M** — restate the condition as the receiver-side baseline ("not decoded natively by the common mobile and browser platforms; no memory-safe decoder is assumed") and add `\biOS\b` to the checker's product class.

## 11. "once the tier ships" (Weakness 8, Top #5)
(a) Report reads the Anonymous Tier MUST at 1.13.3.3 as pre-1.0 roadmap phrasing.
(b) **ALREADY-RULED.** This is the R54 landing text as the steward ruled it ("MUST, once the tier ships; until then the residual is stated at 1.13.3.1"), and the tier is planned by ruling; the sentence is the honesty device, not leakage.
(c) `part_1:244` (for reference): "it MUST layer the Anonymous Tier once the tier ships; until then the residual is stated at [CC 1.13.3.1]".
(d) Pass 6 carried it as R54; M16 landed it. Not a regression.
(e) **X.**

## 12. "The variable-depth `SubStreamPath` … is a follow-on" and "encoder lineage academic-grade today" (Weakness 8, Top #5)
(a) Two roadmap/temporal phrases in the normative codec_id section.
(b) **CONFIRMED.**
(c) `part_5:385`: "**Reserved** — encoder lineage academic-grade today; substrate is MDC-ready."; `:390`: "The variable-depth `SubStreamPath` (MDC tree-path encoding) is a follow-on."
(d) Not raised by pass 6 (pass 6 caught the neighbouring "in 1.0 scope" at `:367`, which M16 fixed; these two sit in the same section and were missed). Not a regression.
(e) **M** — "Reserved; no production encoder is assumed" and "`SubStreamPath` is reserved for amendment".

## 13. "They are not measurements from a live mesh, and they are revised when live measurements exist" (Weakness 8, Top #5)
(a) Report reads the shaping-defaults rationale as process leakage.
(b) **ALREADY-FIXED-BY-RULING.** Pass 6 verify #10 / R105 asked for the figures to be marked informative; M16 did ("*Why these values (informative).*", `:765`). The sentence is the disclosure the steward asked to keep (CHANGELOG.md:120: "note the justification so we can incorporate reality into the model later").
(c) n/a.
(d) Pass 6 raised; landed as ruled. Not a regression.
(e) **X.**

## 14. "stays on the roadmap" (Weakness 8, Top #5)
(a) The identity-plane-link paragraph in 5.4.6 says the blinded-retained-state mechanism "stays on the roadmap".
(b) **CONFIRMED.** It sits in a paragraph headed "(normative)" and is the one temporal/roadmap phrase left in 5.4.6; the Position paragraph already states the same thing timelessly ("For any future multi-hop amendment, the blinded-retained-state family is the nearest admissible relaxation").
(c) `part_5:866`: "The mechanism that would hide the endpoint correlation from the forwarder as well — blinded, rotating retained state, the family the Position below names — is the more secure option and stays on the roadmap; a deployment that needs it layers it."
(d) Not raised by pass 6. Not a regression.
(e) **M** — "…is the more secure option and is reserved for the multi-hop amendment the Position names; a deployment that needs it layers it."

## 15. Witnessed-mode bootstrap exposure (Threat 2)
(a) Report says a hostile reviewer will note the root ships with witnessing off until amended.
(b) **FALSE** as a defect. That is a disclosed residual, stated three times by design: the adversary matrix row (`part_1:233`: "a lineage that runs with witnessed mode off has a single-signer anchor for as long as it does"), the charter defaults (`part_5:564`), and the cover, which names "the transparency logs where witnessed mode is off" as a trust assumption "a reviewer should attack first" (covers/threats.md:3). Pass 6 verified the same finding FALSE ("witnessed-mode-off disclosed") and R105 moved the shipped state to the register's CLM-witnessed-lineage row.
(c) n/a.
(d) Pass 6: FALSE; R105 landed. Not a regression.
(e) **X.**

## 16. Unanchored simulation numbers in 5.4.3 (Threat 3)
(a) The 380 s / 910 s / 29 s / 54 s figures cite a model run with no Evidence Register row.
(b) **CONFIRMED** on the narrow point. The figures are now informative (M16) and the steward accepted them (CHANGELOG.md:120), but no claims.tsv row or evidence pin names the model artefact: CLM-fragmentation (5.4.3) points at test_571 (fragmentation vectors), not at the scheduler model.
(c) `part_5:765`: "*Why these values (informative).* They come from a model run on the production scheduler and budget meter over a virtual clock with real row sizes."; `:769`: "near the limit delay rose to about 380 s mean and 910 s at the 95th percentile, against 29 s and 54 s at 3,600 s."
(d) Pass 6 raised the figures (verify #10 → informative; R105). Landed as ruled; the register half was not asked for. Not a regression.
(e) **P** — edge pins the model script/run as an evidence row (or a CLM-shaping-defaults row staged on it); the text then cites the row.

## 17. Rendering: mid-identifier wrap (p.6), table column overflow (p.7, Top #7), heading hyphenation, narrow table headers (pp.16–45)
(a) PDF-layer breaks.
(b) **MATTER-OF-TASTE / pipeline.** The source is clean at each spot (`:17` the identifier; `:25–:26` the axis table; headings at `:240`, `:264`, `:296`); these are build_pdf.py hyphenation/column-width behaviours, the same class pass 6 verify filed as "rendering breaks (P)".
(c) n/a.
(d) Pass 6: P. Not a regression.
(e) **P.**

## 18. "Unformatted markdown list inside a code block" (Rendering pp.44–45)
(a) The discovery-discipline block in 5.4.6 renders as a bulleted list inside a monospace block.
(b) **CONFIRMED in source**, not the renderer: it is a fenced ``` block whose body is four "- " bullets of prose.
(c) `part_5:833–:841`: "```\n- Every participating L1 peer maintains a COMPLETE local copy of the\n  federation directory's X-Wing public keys … - Phone-class peers that cannot hold the full directory resolve through\n  their L1-relay parent over a relay-blinded path.\n```"
(d) Not raised by pass 6. Not a regression.
(e) **M** — unfence it into an ordinary list.

## 19. Opportunity: publish golden vectors for `K_symbol` and `destination` (Opportunity 1)
(a) Report asks for a label/KDF summary table and vectors.
(b) Not a defect. 5.4.6 already says the destination golden vector is published with CIRISVerify (`:844`); CLM-symbol cites test_500 scope-privacy vectors. A summary table is editorial.
(e) **X** (folds into item 4's ruling if 5.4.2 survives).

---

## Summary
Counts: 19 items — CONFIRMED 11 (items 1, 3, 4, 5, 7, 8, 10, 12, 14, 16, 18; one REGRESSION: item 4), FALSE 2 (items 2, 15), ALREADY-FIXED/RULED 2 (items 11, 13), MATTER-OF-TASTE/pipeline 3 (items 6, 9, 17) plus 1 non-defect (item 19). Dispositions: M 10 (1, 3, 5, 7, 8, 9, 10, 12, 14, 18) · R 1 (4) · P 2 (16, 17) · X 6 (2, 6, 11, 13, 15, 19). Top three: (1) item 4, the A/V symbol XChaCha seal vs "AES-256-GCM at every layer", a pass-6 M that M16 half-fixed into an explicit three-way contradiction and 81746c7 left standing (R); (2) item 1, the literal broken link in 1.13.3.4 that survived the M16 rewrite of its own line (M); (3) items 3 and 5 together, the undefined second sense of "relay" and the orphan D2/D3/D4/D6 tags (M).
Reads better than pass 6: yes. Of pass 6's 16 confirmed findings, 14 are gone from the text (receipt-endianness quarantine, E1 numbered sentences, target_rate, witness-chain disambiguation and the proof language are now listed by Gemini as strengths or are silent), and the residue is cosmetic (tags, two acronyms, one link, three temporal phrases) except for the one substantive item, which is the M16 regression; Gemini's lower care score (3 vs 4) reflects its own two false findings (the KDF "inconsistency" and the witnessed-mode "exposure"), not a worse volume.
