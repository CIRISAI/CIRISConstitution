# RC12 volume review — pass 6, Grok 4.7 again on the rc12 volumes, 2026-10-26

**What this is.** The same brief (`review/VOLUME_REVIEW_BRIEF.md`), the nine volumes rebuilt from rc12 at `9d5471a` (after the rc11 cut, the persist #1125 landings, the cascade work, today's three edge rulings and the persist v60 re-pin), read by `x-ai/grok-4.7` over OpenRouter, nine calls in parallel, `tools/review_volume_external.py --max-tokens 60000`. Reports: `review/notes/pass6_grok/<volume>.md`. Every finding was then checked against the rc12 *source* (not the PDF) by nine in-house verifiers, one per volume, each also checking whether an earlier pass had raised the same point; their lists are summarised here, with file:line.

**Cost and size.** 497,567 prompt tokens, 178,228 completion tokens; the longest call 319 s (Dictionary). Grok writes about three times as much as Gemini did for the same brief.

| Volume | Pages | Pass 1 | Pass 2 | Pass 3 (Grok) | Pass 4 (GPT) | Pass 5 (Gemini) | Pass 6 (Grok, rc12) |
|---|---|---|---|---|---|---|---|
| Charter | 39 | 4 | 5 | 4 | 5 | 3 | 4 |
| Constitution | 68 | 4 | 4 | 4 | 5 | 3 | 4 |
| Wire | 109 | 4 | 4 | 4 | 5 | 3 | 4 |
| Dictionary | 110 | 4 | 4 | 4 | 4 | 3 | 4 |
| Reader's Policies | 35 | 4 | 5 | 4 | 5 | 3 | 4 |
| Mathematics | 21 | 4 | 4 | 4 | 4 | 3 | 4 |
| Evidence Register | 131 | 4 | 4 | 4 | 5 | 3 | 4 |
| Threat Model | 47 | 4 | 4 | 4 | 5 | 4 | 4 |
| Digest | 34 | 5 | 4 | 4 | 4 | 3 | 4 |

A flat 4 across the board, one notch above Gemini's 3s and the same as Grok's own pass 3. The verification explains the flatness: Grok's lists are dominated by items an earlier pass already found and the steward already accepted as mechanical, which were planned under the M1/M4/M6/M7/M8/M10/M11/M14 batches on 2026-10-25 and **never applied to the source**. The landings that day took the rulings (R41–R92) and left most of the mechanical sweep behind. That is the finding of this pass, more than any single defect.

## The one finding that matters: the unlanded mechanical batches

Checked against source at `9d5471a`; each item below is one an earlier pass raised, the steward accepted as mechanical, and the text still carries.

- **Charter (pass 3 M7, pass 4 M9/M10, pass 5 M15):** 1.7's working-note asides ("honestly, near-unfalsifiable", "Adversarial reviewers: this is the test to push on", `part_1_foundation.md:104–112`); the WBD block duplicated verbatim at 1.9 and 1.16.4 (`:124–134` = `:426–436`); the Conclusion-before-Introduction order in 1.15 and 1.16 (`:395`, `:412`); "CC 1.4–1.12" cited as the six principles (`:418`; the range holds the kill-switch and the 1+4 essay); the ">80% … NIST guidelines" threshold (`part_7:255`); the dangling plain-rule shorthand ("plain rule 7b", "N5", "1c and 1e", "(G16)", `part_7:55, 372, 375`), which resolves only in the Digest's pieces; the raw `formal/retirement` path (`part_7:375`); 7.3.1 "must be balanced" (`part_7:165`).
- **Constitution (pass 3 M7, pass 4 #5, pass 5 #3):** the stale "CC 4.2.6 restore path" (`part_3:811`) and "contest ↔ restore cross-replay" (`part_4:281`) beside the retirement at `part_4:277`; code pointers in rule text (`part_3:927`, `part_4:184, 235, 1718`); "Why this is still 1+4" four times in §3.2 (`part_3:679, 843, 852, 866`); the unscoped NCMEC MUST (`part_4:1379`); the *Magnifica Humanitas* "first deployment" line (`part_4:1621`).
- **Wire (pass 3 M1, pass 4 M10):** `<base64-url>` in the STH and lineage-head request bodies against the RFC 4648 §4 pin (`part_5:136–140, 170–171` vs `part_2:449, 703`); Rule 0 "rules 1–4 below" with the table above it (`part_2:306`); `subject_key_ids` in three shapes (`part_2:253, 446, 470, 579, 694`); `subject_kind` "inside the payload" (`part_2:204`) against "rides the envelope untyped" (`part_2:664`); "~5 km² edge-length" (`part_2:824`); the refusal tokens absent from the error table (`part_5:591–608`); the `personhood_consti` clip (`part_2:316`, renderer, flagged in every pass since 3).
- **Mathematics (pass 3 M4, R51):** R51 unlanded in 6.1.3 ("every CC 6.1 object never instantiates a CC 2.1 Contribution", `part_6:159`, against "the composite is a CC 2.1 scores row", `:309`); "descends — fewer holders, then none" against "revocation does not require destroying the collective gist" (`:170` vs `:176`); "etc." in a normative list (`:160`); "is said to be —" dangling (`:134`); "max(k, two significant figures)" (`:312`); "CEWP-1.0" undefined in the volume (`:184`); Lean and `formal/` paths in prose (`:126, :317`); "verified by an unspecified upstream tier" (`:286`); "why v3 exists" (`:120`).
- **Reader's Policies (pass 3, pass 4 M3/M11, pass 5 #2/#5/#8):** "the operator the seed lacked" (`part_4:632`), "M-1's symmetry is structural, not bolted on" (`:1228`), "the four implementations MUST follow this shape" (`:793`); `score ≥ 0.7` uncited (`:1141`); the legal gloss (FISA "complies", `:653`; GDPR 17(3)(c) mislabelled as archiving, `:634`; "Honors the HIPAA minimum-necessary standard", `:641`); the stray ")" (`:827`); the self-pointing comment (`:890`); no A–M index at 4.4.3; the Policy G clip (`:1212`, renderer).
- **Evidence Register (pass 1–5):** Annex J's inner clauses restarting at 1.1 under §7, §8, §9, §11 (`part_8:1407ff`); §8.6.4 as one sentence with no list (`:431–433`); the house-style lines ("trio Phase 4 audit" `:264`, "was Art 61 in the 2021 proposal" `:606, 1255, 1357`, "We never adopt anyone's semantics" `:290`, "C2PA has no consent architecture" `:311`, "as it did for email authentication" `:177`).
- **Threat Model (pass 3 M1/M6, pass 4, pass 5):** "CC 3.4.4–3.4.2" backwards (`part_1:215`); "named as a bet, CC 8.3.1 R14" and "mechanized in coherence-ratchet" (`:236`); "the label CIRIS-AV-INNER-V1 is retired" (`part_5:430`); the CHECK-arm migration note (`:507`) and "in 1.0 scope" (`:367`); the figures (`:38, :284, :390`); "The wire learns nothing from a shaped link at any setting" (`:740`); the E1 cell of 4,865 characters (`:467`); the editorial lines at `part_1:250` and `part_5:860`.
- **Dictionary (pass 3 M2, R53, pass 1 #8):** the four polarity contradictions R53 ruled (`part_3:72/1750`, `:324/1571`, `:401/51/522`); R1's double definition (`:398`); "reaches only the CC 3.1 tables" (`:396`); the `system:*` double listing (`:133, :287`); the deferral family's transitional wire (`:512`); "The CC 1.13+4 lockdown holds" (`:1737`); the literal backslash (`:1959`).
- **Digest (pass 3 M8, pass 4 M14, pass 5):** promise headers stamped "works today" above sub-rules the same piece marks modelled, staged or rule-only (promises 2, 4, 7; `EXECUTIVE_SUMMARY.md:17, 21, 27`); promise 1 mapped without "private" (`00_guarantees.md:33`); the Check column naming a conformance suite for rule-only promises 8 and 9 (`EXECUTIVE_SUMMARY.md:62–63`); "death as doctrine" (`00_guarantees.md:65`); the G7 lab-log pins (`:58`); the leaked piece paths and ids (`EXECUTIVE_SUMMARY.md:13`, `00_operator_digest.md:5`, `00_guarantees.md:1`); the Tor comparisons that M14 said were out (`00_guarantees_plain.md:88`, `00_guarantees.md:73`, `EXECUTIVE_SUMMARY.md:47`).

**→ M16.** One landing of the whole list above, volume by volume, each item checked back against the pass that planned it, with `check_stale_refs` extended for the patterns it still misses (plain-rule shorthand, "honestly", "Adversarial reviewers", raw `formal/` paths outside `part_\d` matches, "etc." in a normative list). Estimated at one working session; the pass-5 regressions (M12's doubled clause, the Charter cover's overclaim) are the reason to do it as one diffed batch and re-read each volume once after.

## What is new in this pass, confirmed against source

**Charter.**
- The R29 landing left four ranking words: PDMA step 5 "Implement the ethically optimal action" (`part_1:67`), step 3 "principle conflicts or trade-offs" (`:61`), 7.2.2 "locally optimised within it" (`part_7:96`), 7.3.1 "must be balanced" (`:165`). → M16.
- **The pass-5 fix to the Charter cover made its claim false instead of true.** The cover now says every capital MUST in the volume quotes a rule whose home is the Wire or the Constitution (`covers/charter.md:9`). 1.3's "the agent MUST route the action to WBD" and "The substrate MUST NOT be relied on to perform or enforce the Veto" (`part_1:80`), and 1.13.6's four substrate MUSTs ("the substrate MUST purge it", "MUST emit a terminal ACTION_RESULT", `:281–289`) have no home in Parts 2–6; `ACTION_RESULT` occurs in no wire Part. → **R93.**
- 1.14 is the Foreword's number in `toc.tsv:24–31` while Part 1 has no 1.14 heading and the Foreword prints unnumbered; the omission marker does not fire. → P (toc) or M.
- `STEWARDSHIP.md:8–10` still lets "the founder, or any accord-holder" amend and "the maintainer decides"; R2 bounded the authority but left the actor ambiguous. → M (one actor named).

**Constitution.**
- H3 areas: "resolution 5–6 (city-scale ~250–1700 km²)" (`part_3:688`) is resolution 4–5; res 6 is ~36 km². → M16.
- "over-18" (`part_3:826`) beside the predicate `>= 18` (`:836`). → M16.
- 4.2's scope-isolation list "cannot sign anything else" (`part_4:71`) omits the amendment sign-off and 4.5.1.2 ratification that the next paragraph (`:73`) admits. → M16.
- **The cover promises "anyone may leave one" while the register cell says an agent's exit is "none while held"** (`covers/constitution.md:7` vs `part_4:1257`). The register is right by the condition-of-symmetry ruling; the cover overstates. → **R94.**
- "The roster is being widened … until about seven hold seats" (`part_4:201`): an instance statement with no source row. → **R106.**
- Grok's headline, `quorum:2/3` vs `majority`, is **false**: two objects on two planes, which `part_3:753` states outright and the pass-3 note already adjudicated. The absence-rule, forward-secrecy and duplicated-opt-in findings are false too. One nit survives: "information-theoretically unrecoverable" is the wrong term for key deletion over surviving ciphertext (`part_3:674`).

**Wire.**
- `cohort_scope` has no row in the 2.1 table although 2.3.2.3 names it among "exactly those in the CC 2.1 table" and the mirror makes it REQUIRED (`part_2:13–73, 204, 580`). → M16.
- The catalogue's `community_id` row rejects only `cohort_scope == community`; 2.1 and the signed-object table say community or affiliations (`part_2:489` vs `:30, :645`). → M16.
- "The canonical form is the array" while a bare token stays valid signed bytes (`part_2:592, 738`): "canonical" is the wrong word for a form that is not the one byte string. → M16 ("the form an emitter writes"), or R if bare tokens should be refused.
- 2.6 is titled "Foreword" and the canonicalisation and signed-object rules hang under it (`part_2:394`, `toc.tsv:73`). → M16.
- 2.6.7 says an attestation is rejected when its `signed_at` is more than five minutes in the future (`part_2:848`); an attestation's instant is `asserted_at` and the signature's is `scrub_timestamp` (`:588, :706`). → M16.
- The consent window is named four ways (`part_5:211, 219, 221, 244, 286`). → M16.
- 1.13.3.4 "community content is sealed, its holding claims staying within the cohort" (`part_1:248`) was not updated when the plaintext bodies of infrastructure communities and public rooms were ruled (`part_5:100`). → M16.
- `HMAC-SHA3` unpinned at `part_5:790` against `HMAC-SHA3-256` at `:643`. → M16.
- Rekey "conforms to MLS TreeKEM (RFC 9420, normative)" (`part_5:42`) while the same section says "MUST select per deployment" between TreeKEM and the flat cascade (`:55`) and 5.3.3 calls media multicast a flat per-epoch `key_grant` cascade (`:324`). → **R103 (edge).**
- The receipt's `epoch`/`K` as `u64 LE` (`part_5:482, 484`): edge has now answered (#891) that the receipt really is little-endian and that CC's layout omits `subscriber_key_id` and `chunk_root`. → M16 under the answer: pin LE in the receipt's own words and add the two members.
- `K_record_id`/`K_symbol`: edge's answer is that 5.4.1 should name the first-stage exporter label. → M16 under the answer.
- Reassembly "≥ K valid symbols" with no carrier for K (`part_5:744, 748, 696`). → **R103 (edge)**: state the carrier, or confirm the symbol text is the scope-privacy envelope and not a code.
- `P2:514` still says 5.2 forbids any holding claim leaving a bounded cohort "unconditionally" after R48 confined 5.2 to self and family. → M16.
- The key-plane null exception that Grok flagged is **already in the text** (`part_2:295, 446`); the email-vector digest finding is **false** (the suffix is the last nine characters).

**Mathematics.**
- **A deny-on-low-`k_eff` threshold is called "safe" in the sentence before "an implementation MUST NOT gate on" any band of it** (`part_6:126`). → **R96.**
- **The freeze release: the text says two consecutive recovered periods, the model releases after one** (`part_6:313` vs `formal/census_ballot/CensusBallot.tla:213, 245–248`). → **R97.**
- The ratchet prose reads "a fall of more than a third" without saying of what; the model measures the raw composite (`CensusBallot.tla:212`). → M16.
- `retention_priority` sits in the freeze-gate vector list (`part_6:166`) three lines after being declared edge-internal and never on the wire (`:162, :179`). → M16.
- "The only path from measurement to action is the mesh-config plane" (`:13`) while the census supplies the governance base (`:302`) and "narrowing relief" (`:313`) is defined nowhere. → M16.
- `hard_case:*` called a "CC 3.4 reserved-prefix candidate" (`:32`); it is registered open vocabulary at 3.1.9.4. → M16.
- The integer form of the dominance test, `n_eff * 2 >= source_count`, is exactly the pinned `min_ratio = 0.5` and matches the no-IEEE-754 rule (`:111, :114`). → M16, opportunity.
- Grok's privacy "overclaim" from sender-chosen seats is **false** (`Inv_SharePrivacy` is conditional on the two aggregators not both colluding, as the text says); one sentence on how federation seats are drawn (`H(period ‖ class)`, in the model README and not the prose) would close the residue.

**Reader's Policies.**
- The consent-record JCS paragraph says "these seven members are REQUIRED" over a table of eight, and the mapping still says `partner ≡ subject_key_ids[0]` while the shape is singular `subject_key_id` (`part_4:864, 870, 883`): residue of the #1125 landing. → M16.
- `history_on_join` is declared reserved at `:604` while `:609–611` still describe `full` as deciding. → M16 (R68 exists).
- `resolve_consent`'s comment says a withdrawn grant resolves to `none`, the code returns `unspecified` (`:1061, :1064`). → M16.
- **The accept half of the steward binding is "never withheld — an agent has no veto" and "may be withdrawn by its signer" in one paragraph** (`:807`), while Part 3 calls the halves independent unilateral grants (`part_3:1573`). → **R95.**
- The Austin H3 example is wrong: the true res-5 parent of `872830828ffffff` is `85283083fffffff`, and both cells are the H3 documentation's San Francisco examples (`:549`). → M16.
- `designated_officials` "waivable below threshold" names no threshold (`:649`). → M16.
- Grok's headline, the cover's licence/grant rule against the body, is **false**: it conflates a licence with a `license`-scoped delegation; 2.4.1.2.1 and the #1125 ruling state the cover's rule.

**Evidence Register.**
- R14 uses present tense ("CC 4.4.2 aggregates") for a staged row (`part_8:179`, `claims.tsv:202`). → M16.
- R5 is "Discharged" while the row is still titled "Hardware-class self-assertion gap (acknowledged)" (`part_8:170`, `claims.tsv:102`). → M16.
- **"First contact" names two things:** the accord's recognition act that bounds stewardship (`claims.tsv:313–314`, `part_4:1261`) and the device-pairing plane of 3.2 (`claims.tsv:469, 476, 480`). → **R98.**
- Art. 50's "Evidence-bearing" and OSHA's "Partial" have no slot in the graduation rule (`part_8:605, 610, 616`). → M16.
- "a format nobody has implemented is not made real by ratifying a paragraph about it" (`:268`). → M16.
- Carried rulings still open: §8.4's informative box against the MUST at 8.4.2.2 (`:284, :335`); Annex G §8.2's MH reconciliation note against "no normative force" (`:937, :957`); the vendor names in the factual-premise row (`claims.tsv:321`). → **R102** (the first two; the third was ruled kept).
- The two glyph findings (≠, 10²⁶) are **extraction artifacts**; the page images are correct.

**Threat Model.**
- "The substrate MUST wrap the DEK with v2" (`part_5:15`) against "an unrecorded live call wraps nothing" (`:42`). → M16 ("a DEK that is wrapped MUST use v2").
- "No reachable holder MUST resolve to a ContentMiss" (`:748`) is not a sentence. → M16.
- `target_rate` is defined nowhere (`:786, 795`) and "federation-tier slashing condition" names no object. → M16 for the plane; **R** for what `target_rate` is (pass 3 M6, still open).
- `part_5:764` attributes XChaCha20-Poly1305 to the A/V plane; live A/V is AES-256-GCM at every layer and `:742` itself places XChaCha at the scope-privacy layer. → M16.
- Proof language ("by reduction to … IND-CCA", "under the IND of HMAC-SHA3", `:703, :792`) and draft citations without a revision (`:752, :754`; also `part_2:798–800`). → M16 for the wording; **R107** on pinning draft revisions.
- "multicast" in two senses, TreeKEM commit delivery (`:55`) and content (`:466`). → M16.
- The Anonymous Tier MUST for the global passive adversary (`part_1:244`) against a planned tier with stated residuals (`part_5:858`) and shaping off by default (`:717`). → **R54 (carried, still open).**
- Two findings are **false**: the `hard_case` pointers to 3.4.2 and 3.4.4 are both correct, and "every link is attributed to a key" is consistent with "the storage node sees the last relay".

**Digest.**
- **The re-cut is only half-synced into the volume:** `00_guarantees.md:43` now says rehearsal and the non-goals are practices, while `EXECUTIVE_SUMMARY.md:35` still narrates them inside promise 11, `00_guarantees_plain.md:131–134` lists 11c/11e as promise-11 rules, and 8a's disclaimer still sits inside promise 8 (`EXECUTIVE_SUMMARY.md:29`, `00_guarantees_plain.md:104`). → M16, first.
- The cover's "present tense only for what ships" against eleven sub-rules marked "[a rule, no code yet]" (`covers/digest.md:7`; `00_guarantees_plain.md:87–134`). → **R99** (which sentence wins; the default is M: every promise header carries its weakest sub-rule's marker).
- "three rules follow from being made … and nothing else does" (`00_guarantees_plain.md:7`) beside "Kind reaches the rules in three ways and no others" (`:9`), which names promises 5 and 7 as well. → M16.
- **"agents lack consciousness and need a conscience"** (`00_guarantees_plain.md:7`, `00_guarantees.md:7`) beside "it is not consciousness, which these rules do not judge" (`:17`). → **R100** (the steward's phrase).
- "evidence of experience … moves the holder's welfare duties and nothing else" (`00_guarantees.md:7`) beside "a finding of experience changes nothing" (`:17`, `00_guarantees_plain.md:17`). → M16 (the second is the ruling).
- G16's status cell is literally "enforced;" with nothing after it (`00_guarantees.md:74`). → M16.
- The operator digest says delegation "has no cycles" where the guarantee says acyclic across distinct keys with a self-edge as a charter form (`00_operator_digest.md:47` vs `00_guarantees.md:64`). → M16.
- `ρ̄` appears once in the volume and is defined nowhere in it (`00_guarantees.md:63`). → M16.
- "Every rule in the Parts is tied either to code on a named commit or to an open ticket" (`EXECUTIVE_SUMMARY.md:43`) is false of the 30 normative rows; README already has the accurate wording. → M16.
- The volume is titled "The Digests" by the build and the cover and "The Digest" by the tool and the filename. → P.

**Dictionary.**
- The polarity residue of R53 is still in the text: `age_assurance:*` signed at `part_3:72` and enumerated at `:1750`; `consent:replication` signed at `:324` and "never a negative score" at `:1571`; `boolean-via-score` as two points at `:401` while `Indeterminate` (`:51`) and `UNDETERMINED` (`:522`) survive, though R53 ruled UNDETERMINED is no row. New in the same family: `content_class:{class}` and `cw_class:{class}` signed at `:496–497`, enumerated at `:1748–1749`. → M16 under R53 (the manifest governs the prose).
- R1 defines "registered" twice in one paragraph (`:398`); "the generator reaches only the CC 3.1 tables" (`:396`) is a wrong sentence, but Grok's inference that the prose-only leaves are missing from the manifest is **false**: the generator parses the prose leaf lines and all 26 are in `namespace_registry.json`. → M16 (pass 3 M2, unlanded).
- `system:*` listed by both persist and edge against "the disjoint union" (`:11, :133, :287`): by design per 3.4.3 (`:1901`), badly phrased. → M16.
- The organisation kinds "withdrawn and kept" (`:1593`): **ruled** (R16, the three kinds remain registered and in force until amendment); the paragraph should say so in one sentence rather than carry both halves. → M16.
- The deferral family's transitional `contribution:` wire (`:512`): pass 1 dispositioned the transitional prose out. → M16.
- Incapacity: the closer "only rooted in prior-will, due process, or a bounded emergency necessity" (`:2269`) against the court-order-only predicate (`:2209–2212`). → M16 (reword to `:2190`'s own words).
- Q1's "a permissive deployment opts DOWN … and MUST NOT lower the CIRIS default" (`:2291`) cancels itself beside Q2's "MUST NEVER lower any element below the floor" (`:2298`). → M16 (strike the clause). Grok's "protections taper at 16" reading is **false**: autonomy increases and the under-18 protections do not taper (`:2279–2283`).
- Two breach tokens: the worked steps emit `hard_case:consent_sla_breach` (`:974`), D2 says `hard_case:deletion_window_breach` (`:984`). → **R109**: are `consent:deletion_sla:{days}` and the envelope's `deletion_window` one mechanism? If one, one token.
- `objection:{state}` closed set and "the vocabulary stays open" in one cell (`:491`); `consent:replication` "an open-vocabulary member" (`:1542`) against "closed in its leaves" (`:315`); `identity:canonical_binding` "reserved" (`:1851`) while open-emitter; "bounded by the hold window below" (`:227`) pointing to a window defined only at `:1180`; family events "reserved under CC 3.4.3" (`:1204`) when their table is 3.4.4. → M16, all new.
- House style: "F-3", "P8", "PoB" labels, "The CC 1.13+4 lockdown holds" (`:1737`), code pointers (`:483, :512, :1451, :1607, :2401`), "celebrity", "defeated by construction", Apple and Google product names as acceptable emitters (`:2286`), the literal backslash at `:1959`. → M16. The "Design notes (informative)" essay (`:1721`) and the "Provisional" tag on `accord:human_dignity` (`:1875`) → **R108.**
- Rendering, new: backticks inside fenced code blocks print literally (`:965–975`, `:1331–1354`); the household figure's box-drawing characters print as `-+` and `|` in the code font (`:1231–1247`). → M16 for the backticks; P for the font map.
- Rejected: `founder_only` (the 3.3.4 table says family and publication; `:221` covers families); the takedown digest (`:1027` defines the selection digest per kind); roster-landing timing against T8 (vii) (`:1536` makes it a per-holder verdict, not an admission); `live_stream` and `accord_data` (sub-kinds, not dimension families); `prohibited:*` and the attestation ladder having no emitter rule (open-emitter by the no-authority-rosters design); `source_count < 10` (k = 10 is CC 6.1.9); the ≠ glyph.

## Rulings this pass asks for (R93–R109; R54, R102 carried)

| # | Volume | Question | Default, model-first where a model speaks |
|---|---|---|---|
| R93 | Charter | 1.3's and 1.13.6's substrate MUSTs have no wire home; the cover's new sentence is false of them | move 1.13.6's durable-trace and orphan-purge rules to Part 5 as the substrate's duties and cite them from 1.13.6; lowercase 1.3's "MUST route to WBD" as the agent's charter duty (no model reads either) |
| R94 | Constitution | cover "anyone may leave one" vs "agent: none while held" | "Any person or node may found a root and leave one; a made thing leaves with the hand that holds it" — the condition of symmetry (reciprocity §1'', guarantees `obligation_bound`) |
| R95 | Policies | may the agent occurrence withdraw the accept half of the steward binding, or is it "never withheld"? | either half may be withdrawn (R5: consent is revocability; Part 3's "independent unilateral grants"); an occurrence's withdrawal ends the binding and enters the retirement machine's objection path, it is not a veto over the steward's data choices (retirement `Inv_RefuseAvailable`, `Prop_RefusalStands`) |
| R96 | Maths | does a deny-only `k_eff` threshold stand beside "MUST NOT gate on a band"? | yes: "this document pins no band; an implementation MAY deny at a threshold of its own and MUST NOT grant on one" |
| R97 | Maths | freeze release: two consecutive recovered periods (text) or one (model)? | the model (one period): it closed on it, and the two-period sentence has no witness; else the model moves |
| R98 | Register | "first contact" names the accord's recognition act and the device-pairing plane | rename the accord act "the recognition act" at 1.13.2 and 4.5.1; the pairing plane keeps its wire name |
| R99 | Digest | cover "present tense only for what ships" vs eleven rule-only sub-items | keep the cover; every promise header carries its weakest sub-rule's marker (M) |
| R100 | Digest | "agents lack consciousness and need a conscience" | "agents are not judged on consciousness and are given a conscience" (1.15.11's own words) |
| R101 | Digest | the Tor and decentralized-network comparisons M14 said were out | cut the two Tor lines; the steward says whether the "Among other systems" paragraph stays |
| R102 | Register | carried: §8.4 informative vs the 8.4.2.2 MUST; Annex G §8.2's MH note | cite 3.4.14 R3 instead of restating the MUST; keep §8.2 as a documentation duty and say so |
| R103 | Wire (edge) | TreeKEM normative vs per-deployment selection; the carrier of K | edge names the conformance target and the carrier, or confirms the symbol text is the scope envelope |
| R104 | Threats (edge) | what `target_rate` is | edge defines it or the sentence goes |
| R105 | Wire/Threats | shipped-state sentences ("witnessed mode off") and the throughput figures inside the Wire | move the state to the register's row; mark the figures informative or cut them |
| R106 | Constitution | "until about seven hold seats" | the steward's instance statement: keep with a source, or cut |
| R107 | Wire/Threats | pin draft citations to a revision, or wait for the RFC | pin `-NN` (M-level) |
| R108 | Dictionary | the "Design notes (informative)" essay at 3.4.1 and the "Provisional" tag on `accord:human_dignity` | cut the essay to its one rule; retire the tag (the register carries status, the Parts state rules) |
| R109 | Dictionary | `consent:deletion_sla:{days}` and the envelope's `deletion_window`: one mechanism or two? | one mechanism, one breach token (`hard_case:deletion_window_breach`, D2's); the worked steps follow |
| R54 | Threats | carried: the Anonymous Tier MUST against a planned tier | "MUST, once the tier ships; until then the residual is stated at 1.13.3.1" |

## Rejected this pass (Grok misreads, for the record)

`quorum:2/3` vs `majority` (two objects on two planes); the Policies cover's licence rule (licence vs `license`-scoped delegation); the `hard_case` pointers; "every link attributed" vs "last relay"; the census privacy overclaim; witnessed mode off (disclosed); the email vector's digest suffix; the key-plane null exception (already stated); the two glyph findings (≠ and 10²⁶ are pdftotext artifacts; ² at `part_6:45` wants a look at the page image before it is called a renderer defect).

## Pipeline, carried and new

Overfull inline-code spans still clip at the margin in the Constitution, Wire, Policies and Maths volumes (`part_2:316`, `part_4:71, 1344, 1404, 1459, 1212`, `part_6:76, 213, 233`), flagged by every pass since 3; the four-column table at `part_5:28`; the `cc` field of `manifests/signed_object.json` pointing 6.1.9 and 4.5.13 members at `[2.1]`; the generated 2.6.1.7 note spelling the quorum formula differently from 2.1; the G7 lab-log pins and piece ids printing in the Digest; "The Digests" vs "The Digest"; the Foreword's 1.14 number in `toc.tsv`.

## What this pass says about the text

Nothing Grok found moves a rule. The nine rulings that are new (R93–R98, R100, R108, R109) are each one sentence, and four of them (R94, R96, R98, R109) are the text catching up with rulings already made. The debt is the mechanical sweep: about seventy items across the nine volumes that four passes have named and the source still carries. Land M16 as one batch, re-read each volume once, and the next outside pass measures the text rather than the backlog.
