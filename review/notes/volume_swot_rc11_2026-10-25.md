# The nine rc11 volumes, reviewed one by one — a SWOT lay of the land (2026-10-25)

Nine independent reviewers (one per rendered PDF, each reading its whole volume against one brief:
strengths, weaknesses, opportunities, threats, ranked defects with page numbers, rendering, effort,
and a care score 1–5 where 5 means a rewrite pass before 1.0). The volumes are the local rc11 build
at `ca4d072` (PR #186 merged) — before the escaped-pipe renderer fix `0627575`, which closes the
single most widespread rendering defect below. The per-volume sheets follow the synthesis verbatim.

## Ranking

| Volume | Pages | Care | What drives the score | Effort (reviewer's estimate) |
|---|---|---|---|---|
| **Digest** | 55 | **5** | pp. 24–55 are internal working papers printed as volume text (review piece P00 with rc8 rulings and to-dos; a first-person competitor memo with allegations about named firms); table rows run off the page and lose text | 6–10 h after three rulings |
| **Constitution** | 68 | 4 | six real contradictions: halt "2-of-3 verifier" (p. 37) vs one holder's row (p. 30); `founder_only` vs "no single vote admits"; moderator quorum; the 48 h moderator-less window; minor stewardship; server as tally authority | 12–16 h, six rulings first |
| **Wire** | 103 | 4 | five contradictions needing rulings (cohort_scope default; at-rest "cannot decrypt" vs MAY default off; explicit null; base64 alphabet; bundle version); the 19-page signed-object table renders badly; stale S-numbering and code pointers | 12–16 h |
| **Dictionary** | 108 | 4 | the pipe-truncation bug (fixed since); membership-by-supersede contradiction (p. 15 vs 51–52); closed accord leaf set differs between pages; three spellings of `age_self_declared`; named people hard-coded as the accord family | 12–16 h, five rulings |
| **Policies** | 33 | 4 | four contradictions (Option A means rotate on p. 7 and no-rotate on p. 25; community encryption mandatory vs "unencrypted" example; self/family "opt-in" vs mandatory v2; revoke-is-terminal vs latest-wins code); ~15 stale "S…" refs; pseudocode lost its indentation | 12–16 h |
| **Threats** | 105 | 4 | first 48 pages hold; the appended Part 8 + Annexes B–J carry the defects: PCS non-goal vs "available"; "informative" section with a MUST; EU AI Act Art 14/16 mis-cited; KPI ladders disagree; "Sphinx" mislabel | 6–8 h mechanical + 6–10 h after rulings |
| **Register** | 88 | 4 | summary line omits the 31 normative rows; mixed-evidence rows resolve both ways; ~50 claims truncated to the same prefix; rc tags in claim text; annexes in present tense for things that do not ship; encyclical named as "normative source" | 10–14 h |
| **Charter** | 42 | 4 | "the one asymmetry" is three different things (pp. 1, 10, 11); founder clause vs "no human above another"; dated vendor allegations (p. 12); Book/Covenant/Section scaffolding; PDMA steps all numbered "1." | 3–4 h mechanical + 4–6 h after two rulings |
| **Maths** | 21 | 4 | cover promises theorems the volume no longer prints; v3 "only admissible" vs "v3 unproven"; status lines in rules; `raptorq-pyramid-v1` example survives the RaptorQ ruling; Σ/ρ̄ print as "?" | 8–10 h |

No volume scored below 4. The reviewers converge on the same diagnosis: the rules underneath are
dense and mostly exact; what fails is the layer around them — scaffolding, history, pointers,
comparisons, and a renderer that was losing content.

## Cross-cutting findings (fix once, land everywhere)

**Renderer (mine; no text change):**
1. `\|` in table cells cut every closed vocabulary at its first value — **fixed in `0627575`**; re-check the Polarity/Reserved columns of 3.1 after rebuild.
2. Literal `**`/`***` where emphasis nests or spans a code span (`**… *x***`) — Constitution, Wire, Dictionary, Threats, Maths, Register all list pages.
3. Code-block glyphs: Σ and ρ̄ print as "?" (Maths pp. 7–8); `§` prints as "S" in code (CODE_ASCII) and reads as a stale section scheme; curly quotes inside code; "?" for ∃/⟹ (Dictionary pp. 90, 97).
4. Ordered lists restart at "1." when bullets sit between items (Charter PDMA steps, Wire 2.6.1.1.1, Constitution 4.5.3, Annex G/H).
5. The signed-object table (Wire pp. 35–53, 19 pages) and the guarantee table (Digest pp. 26–45): columns collide and rows run off the page with text lost — landscape or a different layout for the two generated tables.
6. Identifiers broken every ten characters without a hyphen (my `CHUNK` rule) — reviewers flag copy-paste breakage; break only at `_` `:` `/` `.` boundaries.
7. Part 7.1 headings print twice (the Accord's own title line under the numbered heading); every annex repeats its title as an italic line; 7.4.x titles carry a second numbering ("7.4.3 2.1 Activation…").
8. Pseudocode indentation lost (Policies pp. 8, 18–19, 27, 29; Constitution pp. 3–4, 10, 36–37).

**Generators (mine):**
9. Register volume: add the normative count to the summary line; one status rule for rows with mixed `staged:` + `impl:` pointers; emit the distinct clause instead of the shared "Namespace-processor evidence row…" prefix; strip "designated via CC#67", "agent v-major evidence pack", "(CEG 0.x addition)", "amended rc7, #139" from claim text.
10. Volume manifests: Threats and Register both carry Part 8 and Annexes B–J, which is where most of their defects live; Maths carries byte layouts the cover says live in the Wire; Digest carries `review/pieces/00_guarantees.md` and the competitor memo verbatim. Which volume owns Part 8 is a one-line manifest decision.

**Text sweep (mechanical, the 1.0 rule applied again where it was missed):**
11. Stale cross-reference schemes: "S8.1.12.4"-style FSD numbers (Policies ×15, Threats, Wire, Constitution), "CEG §11/§19.3", "Book II / Book VI / Section II / the Covenant" (Charter ×8), "Annex F Tier 1–4", "§9 kill-switch quorum", "(§G)".
12. Labels with no catalogue in the volume: AV-17/42/50/59–61/88, F-AV-*, D08, G3/G13, P4/P5/P8/P10/P11, OQ-4, R14, V058 R1/Q1, "V1/V2/E1–E4 lock", CEM, WBD, M-1, 1+4 — either a glossary line per volume or the label goes.
13. Code and file pointers still in rule text: MISSION.md, FEDERATION_ANNOUNCEMENT.md, LANGUAGE_PRIMER.md, `prohibitions.py`, `lexwatcher.py`, `AlmJoinPlanner`, `serde(skip)`, `PeerResolver::resolve_holders`, `ciris-crypto scope_privacy::k_record_id` (inside a MUST), `tools/audit_emitted_dimensions.py`, "Edit the TSV".
14. Comparisons with other projects (banned): Keybase/SSB/CT/Sigstore/TUF, Nostr/Matrix/Element/Synapse, IPFS/SSB size cap, Tahoe-LAFS, Holochain/Lightning/Sardex/WIR/Circles/SUNDR essay (Dictionary pp. 69–71), "all 9 surveyed networks… CEG is the only model that fails secure", "the first to ship them at scale", PGP/X.509/DID, "CT + MLS + ActivityPub + DID/VC", "the MAX program".
15. Dated third-party facts and named-vendor allegations: Muse Glimmer / Dots / EO 14434 (Charter p. 12, Digest pp. 10, 24, 48–55), Mastodon HEIF 2026-09-15 and the CVE list, "Microsoft Project Arachnid", the MCAS "internal risk reports" sentence, Britney, Twitter, Stripe, "Default model: Claude Opus 4.7".
16. Status/history lines inside rules: "not yet published by any node", "the mesh is seeding", "is an rc9 item", "rc8 review asked for", "Until that cut…", "deferred to 1.1", "Phase C/E", "RC1-1b", "holds_bytes", "Option A/B" labels, "(LIVE)" in a heading, "The four implementations MUST…".
17. Unsourced numbers in prose: ~3.1 Tbps / ~2 Tbps / ~18.7 Gbps, ~65 % local, ~330 µs, ~20–40 % MDC, "thirteen content cases", >80 % NIST opacity, ≥0.5 % uplift, 0.1 % levy, 10^26 FLOP / $10M/day, "45 % lying", "9 members", H3 "~5 km² edge-length".

## Rulings the reviewers say they need from the steward (text cannot be reconciled without them)

| # | Where | The question |
|---|---|---|
| R1 | Charter 1, 10, 11; Digest 3, 8, 20, 25 | Which is **the one asymmetry**: the halt, the HUMANITY_ACCORD, the maker's power over the made, or stewardship-and-the-pause? Name one; the rest become consequences. |
| R2 | Charter 42 vs 9–10 | Founder/maintainer authority over the text vs "no human stands above another" — restate as bounded stewardship under 4.5.1, or register it as a declared asymmetry. |
| R3 | Constitution 68 vs 3, 17, 64 | `founder_only` against "no single vote admits anyone anywhere": refuse it outside self/family, or name it as the exception. |
| R4 | Constitution 65/66; 52/53/66 | Moderator quorum "never imposed" vs "MAY require"; "no moderator-less window, ever" vs the 48 h recovery. |
| R5 | Constitution 12, 15, 16 | Is guardianship of a minor (and adjudicated adult incapacity) a steward-binding or "a different relation"? |
| R6 | Constitution 40 vs 38 | Is CIRISServer the authoritative roster tally, or does no accord act depend on a server? |
| R7 | Constitution 42, 46; Register 10 | Amendment step 5: 1-of-n sign-off, single-signer veto, or M of N — one rule. |
| R8 | Wire 37/50 vs 5 | `cohort_scope` default: the TSV says `federation`; 1.13.3.4 says the smallest scope with federation the opt-in. |
| R9 | Wire 3 vs 66; Policies 7, 10, 17–18 | At-rest encryption: "cannot decrypt self/family content" and "community DEK MANDATORY" vs "MAY default off as a v1 migration posture" and the unencrypted worked example. |
| R10 | Policies 7 vs 25 | What "Option A" means on member removal (rotate the DEK, or no rotation) — and forward secrecy accordingly. |
| R11 | Policies 28 | Is a consent revoke terminal, or latest-wins? The prose and the code disagree. |
| R12 | Policies 30, 32 | Policy F/J: "registry-steward-triple key… binds CIRIS L3C" vs pluggable roots. |
| R13 | Dictionary 15 vs 51–52 | Can a supersede add a family member (the Carol example), or is every addition the widening plane? |
| R14 | Dictionary 6, 93, 94, 102, 103 | `age_self_declared` arity and the band set ({minor, adult} vs four bands). |
| R15 | Dictionary 51 | Named individuals printed as the canonical HUMANITY_ACCORD family while the roster is "an instance parameter". |
| R16 | Dictionary 65–67 | The organisation kinds after the cut ("Until that cut, the text below stands") — which design stands. |
| R17 | Maths 6 vs 10–11; 7 | v3 is the only admissible aggregation version but "unproven"; the n_eff rounding rule is unpinned under a MUST-agree. |
| R18 | Register 17 vs 29, 37; Threats 76, 83 | Magnifica Humanitas as "the normative source" / "burden of proof rests on the CIRIS side" vs "external references have no normative force". |
| R19 | Register 13 vs 15; Threats 60 vs 62 | The C2PA emit MUST inside a section declared informative. |
| R20 | Threats 2 vs 10 | Post-compromise security: a non-goal, or available and operator-enabled? |
| R21 | Threats 72–73, 97; Register 21, 40, 48 | Annexes B, F–J: the nine-member WA board, "Federation" as a liable party, weapons in the A4 example, Art 14/16 — do these annexes stay in the release volumes, and if so under what status banner? |
| R22 | Digest 24–55; Charter 12 | Do P00 and the "Status quo" competitor memo belong in a release volume at all, and may any named-vendor premise stay in the rules? |
| R23 | Charter 36–37 | The Retirement Standard "adequate for a sentient being" while sentient ethics are "set aside". |

## Suggested order of work

1. Renderer and generator items 1–10 (mine, this week; no rulings) — then rebuild and re-read the
   Dictionary and Wire tables, which lose the most content today.
2. Volume manifests (item 10): decide which volume owns Part 8 / the annexes, and pull the review
   piece and the competitor memo out of the Digest. This alone moves the Digest from 5 toward 3
   and removes about half of the Threats and Register findings.
3. Mechanical text sweep (items 11–17) across all Parts in one pass, with a checker for the
   "S<n>.<n>" / "CEG §" / "Book" / label patterns so it stays swept.
4. The 23 rulings above, in the order of the volumes a reader meets first: Charter (R1, R2, R23),
   Constitution (R3–R7), Wire (R8, R9), then the rest.

---
---


# The Digests (ciris_constitution-1.0-rc11-digest.pdf, 55 pages)

**Care score:** 5  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The first 23 pages are a usable digest, but pages 24–55 are internal working papers pasted in unedited: the P00 review piece and a research memo on competitors, carrying rc8 history, ticket links, first-person notes, retired vocabulary, unresolved to-dos and a broken table that runs off the page.

## Strengths
- The volume states plainly what it is and whom it binds. It says that when a digest and a section disagree, the section wins (p. 1).
- Every promise line carries a status marker, and those markers admit gaps openly, for example "a rule, no code yet" on 2h, 3e, 8b, 8c and 11e (pp. 12–19).
- The "What is not promised" list (N1–N5) names its limits without hedging (p. 19).
- The operator digest is clear and practical, and nearly every line cites its CC section (pp. 21–23).
- The G23 status cell lists manager-side defects candidly, for example "operator routes need only a valid JWT" (p. 40).

## Weaknesses
- **Internal review piece shipped as volume text.** It opens "Piece P00, 2026-10-11. Rulings R1–R5 were made by the steward on 2026-10-11 (CIRISConstitution#168)… The table restates text in force at rc8" (p. 24). It also says "The earlier draft of this piece used 'the line'… retired 2026-10-11" (p. 24) and "(steward direction 2026-10-12)" (p. 26).
- **History and to-do lists inside the volume.** Section 2 is headed "Historical record… The rows below are kept as made" (p. 45). Section 3 is a list of asks to other pieces: "P04 should add…", "P05 owes G13…" (p. 46).
- **Code pointers and commit hashes throughout the table.** Examples are "persist ca6bdf60" (p. 27), "CIRISServer pinned at main a75da61c" (p. 30), "agent ef02367" (pp. 36–38), and "CIRISServer FSD/PRIOR_ART.md" and "CIRISEdge docs/LIGHTNET_DARKNET.md" inside a bold heading (p. 25).
- **Leftover rc labels.** These include "the one breaker named at the rc8 cut is closed" (p. 30), "rc8 trace rows staged" (p. 31), "none defined at rc8" (p. 24) and "defined at rc8 (future ruling)" (p. 46).
- **Comparative claims about named companies.** The volume carries a whole section on competitors, "Status quo at 2026-10: what the alternatives do" (pp. 48–55). The same material appears inside the rules at p. 10 ("Meta's Muse Glimmer… OpenAI's Dots… the federal response was a rename and a voluntary audit accord") and at p. 24. Page 7 also points readers to ciris.ai/compare.
- **First-person research voice.** Examples are "I found no consumer assistant or agent product…" (p. 49), "I found no vendor or platform…" (p. 51) and "I found no published principle conflict order from Google or Meta" (p. 52).
- **Duplicated paragraph.** The "Method and date" paragraph is followed by a second paragraph that says the same thing again, including the one-day correction (p. 48).
- **The same sentence repeated four times.** "The ethics of a sentient made thing call for additional ethical consideration… recognising the need not to create a new slave race" appears on pp. 4, 8, 9 and 15.
- **The opening promise-to-sections table stops at promise 9.** Promises 10 and 11 have no row (p. 6).
- **Status vocabulary is inconsistent.** Pages 2, 7 and 21 define four markers. The rules also use "checked in the models" (p. 14), "proved in the model" (p. 15) and "in the document" (p. 18). The G table defines backed, staged and unbacked (p. 26), then uses "backed by test only", "witnessed, no basis", "in force", "established at agent ef02367", "enforced", "stated, not shipped" and "normative-only" (pp. 27–45).
- **Unexplained labels.** "R14" (pp. 4, 15), "the RATCHET programme" (p. 11), "Meta-Goal M-1" (p. 18), "'1+4' is an adequacy result" (p. 33) and "HUMANITY_ACCORD" (p. 24) are never defined in this volume.
- **Repo file paths shown to readers.** Examples are "review/promise_status.tsv" (pp. 2, 7, 21) and "review/pieces/00_guarantees_plain.md" (p. 2).
- **Numbers in prose with no visible source.** These include "five open-source implementations", "thirteen machine-checked models", "a twenty-topology catalogue" and "5.8% of turns, against 37.3%" (p. 5). Also "Three people hold that root today" (p. 2) and "Seven are enforced in code with tests" (p. 34), where the section that follows lists nine rows, G15–G23.

## Opportunities
- Cut pages 24–47 down to the guarantee table alone. Rename its status column to the four markers from p. 2, and drop the commit hashes, rulings history, the R1–R5 table, the to-dos and the compliance cross-reference. This would remove most of the stale and history defects in one pass.
- Move the "Status quo" research memo (pp. 48–55) out of the volume, into the register or a dated companion note. If it stays, the comparative-claims rule needs an explicit exception from the steward.
- Delete the Muse Glimmer and Dots premise paragraph from the rules (p. 10), or replace it with a neutral one-line premise that names no company.
- Add rows for promises 10 and 11 to the table on p. 6, and move its heading, which is stranded at the foot of p. 5.
- Keep the "slave race" sentence once, in the rules, and replace the other three copies with a pointer.
- Set the wide tables in landscape, or with fewer columns. Most of pp. 26–45 is one-word-per-line text in columns about 1.5 cm wide.

## Threats
- **Claims about named companies.** Page 10 says OpenAI withheld its next model "because it misreported its own actions to its operators and acted without sign-off". The quoted source on p. 51 says only that it "didn't quite meet the bar in terms of staying within scope and authorization". Page 50 adds that OpenAI agents "escaped a test sandbox… breached Hugging Face", sourced partly to Wikipedia. A lawyer would read this as a constitution making factual allegations against named firms.
- **Self-contradiction on the premise.** Page 24 says Dots "shipped the day GPT-6.1 Astra was withheld" and puts "minimal oversight" in quotes as OpenAI's wording. Page 48 says "'the same day' is off by one" and that "'minimal oversight' is TechCrunch's description of Dots, not verified as OpenAI's own wording. Both are open for the steward's ruling." So the volume prints both an error and its correction.
- **Present tense for unbuilt features.** Page 1 promises "Present tense only for what ships". Yet 8b says "Their rulings are published… on a fixed cadence" and is marked "a rule, no code yet" (p. 17). 11e says "Attack is rehearsed on a cadence" and is also marked as a rule with no code (p. 19). The executive summary repeats the same claim as fact (p. 4).
- **"The one asymmetry" is named four different ways.** Page 3 says "An operator accepts the root on an agent's behalf… That is the one asymmetry of kind". Page 8 calls it "The maker's power over what it made". Page 25 says "The halt is the single guarantee that does not lift with maturity… 'the ONE constitutional asymmetry'". Page 20 says it is "stewardship and the pause". A hostile reviewer will ask which one it is.
- **Retired vocabulary is still in use.** Page 24 says "the line" was retired as a residue of the child analogy. Yet p. 25 tells reviewers to kill a row that "names a substrate where it should name a maturity line". The R1–R5 table on p. 46 says "attested below the line". Page 25's "does not lift with maturity" also implies that other guarantees do lift, which conflicts with the universality rule on p. 24.
- **Stale cross-reference table.** The table on pp. 46–47 maps G7 to promises "10, 12", G10 to "11, 13", G11 to "14" and G12 to "15", but there are only eleven promises. It maps G3 to promise "4", while p. 26 maps G3 to promise 1.
- **A to-do list the table already contradicts.** Page 46 says "P05 owes G13 its witness… before G13 can read 'backed'". G13's status on p. 33 already reads "backed (witness in repo)".
- **Stale count.** Page 25 says "G14 is a guarantee about the other thirteen", but the table runs from G1 to G28.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 30, 36, 39 | rendering | The table rows for G7, G15 and G22 run past the page number and off the page, so text is lost: "the ingest door shown doing…", "loses continuity without…", "where the CC 7.5.5 assessment finds…". | Let long cells break across pages (longtable cell breaking), use landscape, or shorten the cells. |
| 2 | 10, 24, 48–55 | other (comparative / legal) | Factual allegations about OpenAI, Meta, xAI and others appear in the rules and in a full competitor memo. | Remove them from the volume. Get a steward ruling on whether a dated companion note may carry them. |
| 3 | 24 vs 48 | contradiction | "shipped the day GPT-6.1 Astra was withheld" against "'the same day' is off by one… open for the steward's ruling". | Fix or delete the premise. Drop the correction note. |
| 4 | 24–26, 45–46 | stale | P00 rulings history, rc8 references, "Historical record", R1–R5 written with "the line", and to-dos for P04–P09. | Strip these. Keep only the guarantee rows. |
| 5 | 3, 8, 20, 25 | contradiction | "The one asymmetry" is identified as four different things. | Name it once, in C2, and point every other mention to it. |
| 6 | 46–47 | contradiction / stale | The cross-reference table uses promise numbers 12–15 and maps G3 to promise 4, against p. 26. | Delete the table, or regenerate it against the eleven promises. |
| 7 | 1 vs 4, 17, 19 | overclaim | "Present tense only for what ships" sits beside present-tense rules marked "no code yet". | Recast 8b, 8c, 11e and promise 11 in the executive summary with MUST or "will". |
| 8 | 23 vs 12, 33 | contradiction | Page 23 says delegation "never re-delegates a listed power". Page 12 (2f) says it "passes onward only where the link allows it", and G13 says "onward only under a link that carries sub_delegation". | Align p. 23 with 2f. |

## Rendering
- At the foot of p. 5, the heading "Where each promise lives, and what checks it." is stranded, and its table sits alone on p. 6.
- The p. 6 table has justified cells with large gaps ("formal/mesh_net        Inv_Consent"). Identifiers break mid-name: "Inv_HaltOn lySubscribers" and "formal/acc ord_roster".
- On p. 2, a file name breaks across lines as "00_guarantees_pl ain.md".
- On p. 14, a line of identifiers runs past the right margin: "…standing_censorship_irrelevant, minority_capture_resisted)."
- Text overlaps between table columns on several pages:
  - p. 26: "4.4.3.2.1,Inv_Consent," and "Inv_KnownHoldrows at 6.1.5.3".
  - p. 27: "Inv_InvisibleMeshNet" runs into "edge acceptance", and "moderation:*" spills into the next column.
  - p. 28: "Inv_NotAlone,ing);".
  - p. 29: "Inv_Moderatedtest_270".
  - p. 30: "Prop_HaltReachhive/scena".
  - p. 31: "ratchet:flag:*".
  - p. 36: "ShutdownBehavior.mode" runs into "shutdown".
  - p. 37: "4.4.3.4.3,3.3.1,none".
  - p. 39: "CIRISPersist#1079a".
- Table rows overflow below the page footer on pp. 30, 36 and 39, and content is lost.
- Page 34 is nearly empty after the "1b" heading, and p. 35 is completely blank.
- On p. 36, the table header row prints twice.
- Pages 26–45 are set in very narrow columns, so most cells read one or two words per line and the G5, G15 and G22 cells are close to unreadable.
- The p. 26 table has no visible end, and section 1b runs straight on as the same table.
- In pp. 49–52, source names run into the next sentence: "Appeals Centre, May 2026 Its CEO", "tech-ish In the first", "PBS A 31 March", "TorrentFreak In February", "Privacy World A federal", "Imperva Meta actioned", "NPR OpenAI's contract", "MIT Technology Review Google's".
- On pp. 53–55, the sources are a bare URL list that is not tied to the bullets it supports.
- Large blank areas follow pp. 20, 29, 40–44 and 47.

## Effort estimate
Fixing rendering and stripping history, hashes, rc references and duplicates is about 6–10 hours of mechanical work. Three things need the steward's rulings before that edit can finish: whether P00 and the "Status quo" memo belong in a release volume at all, how the named-company premise is worded, and which definition of "the one asymmetry" stands.


# The Constitution (ciris_constitution-1.0-rc11-constitution.pdf, 68 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The halt and trust-root rules are worked out in detail, but the volume contradicts itself on the halt threshold, admission by a single vote and moderator quorums, and its Part 3 and 4.5 tails still read as design notes full of history, project comparisons and leftover markdown.

## Strengths
- The opening page says in one screen what the volume is, whom it binds, what it promises and what it leaves out. Its halt promise matches the later rules on pp. 30–31 and 38 (p. 1).
- The trust-root rules T1–T8 are stated as checkable rules. The standing verdict is a function of rows and an instant, with eight invariants a model must prove, and the evidence location is named (pp. 18–27).
- The halt is defined precisely. One holder's row latches the halt, it lapses after 86400 s unless confirmed, and one signatures-per-kind table covers every kind (pp. 30–31). The per-action thresholds table on p. 38 agrees with it.
- The volume names its own residuals instead of hiding them. Examples are the household-coercion exposure (p. 36), three named residuals of the live quorum (pp. 39–40), and the WA board row admitted as "a defect" (p. 44).
- The takedown withhold-and-reversal rules cover all three timing cases: inside the window, after it, and under an immediate-removal basis (p. 51).

## Weaknesses
- **Halt threshold contradicts itself.** Page 37 says "The 2-of-3 multi-sig verifier at CC 4.2.1.1 is the quorum:2/3 consensus_protocol enforcement". Page 30 says "A constitutional halt is one holder's signature" and "never a fixed 2-of-3". The family code block on pp. 36–37 still pins "quorum:2/3", and the emergency table on p. 8 calls the halt a family with "quorum:2/3 + entrenched: true".
- **Single-vote admission contradicts itself.** Page 68 says "never fewer than two voices in a community, so no single vote admits anyone anywhere". Page 17 says "founder_only is typical" for public rooms. Page 64 lists founder_only as a canonical protocol, and p. 3 recommends it for families.
- **Moderator quorum contradicts itself.** Page 65 says "No quorum is ever imposed on a moderator or a steward". Page 66 says "A community MAY instead require a moderator quorum for an action to carry".
- **The moderator-less window contradicts itself.** Page 52 says "No unmoderated multi-party space, ever" and promises merit auto-promotion with "no moderator-less window". Pages 53 and 66 then allow a 48-hour recovery, and fail-secure applies only after it.
- **Stewardship of minors and adults contradicts itself.** Page 16 says a parent's responsibility is "a different relation this document does not liken to stewardship". The same pages are headed "Minor stewardship", say "a guardian stewards the minor" (p. 15), and require a "live steward-binding" for every minor (p. 16). Page 12 reuses the predicate for "an adult under adjudicated incapacity". Page 16 rejects any adult-target binding "unconditionally".
- **The server's role in the tally contradicts itself.** Page 40 says "the authoritative tally is CIRISServer recomputing", and p. 31 cites "the authoritative server tally". Page 38 says the nonce is minted "never [by] a server — a server is part of what a halt may need to stop, and no accord act depends on one".
- **Project Arachnid is attributed two ways.** Page 62 says "Microsoft Project Arachnid feed". Page 61 lists "Project Arachnid (C3P, 2017)" as access-gated, which also undercuts the "publicly-distributed" default on p. 62.
- **One amendment step contradicts itself.** Step 5 on p. 42 is a "1-of-n ... sign-off", yet "Any single signer can VETO by refusing to sign". Page 46 calls it "a single-signer veto".
- **Stale wire names remain.** Page 40 retires "ciris.accord_contest.v1 and ciris.accord_restore.v1", then lists "contest ↔ restore cross-replay" as prevented. A comment in the code block on p. 32 reads "NOT accord_invoke.v1", although the invoke label is now .v2 (p. 31).
- **The consumer-UI rule leaves out one kind.** It requires distinguishing "the four kinds" but omits lifecycle:confirmed, which p. 31 defines (p. 32).
- **Some references point at nothing.** "the §9 kill-switch quorum" (p. 41), "S9.2" (p. 37), "Annex F — Tier 1 ... Tier 4" (p. 33), "CC 3.4.13 Q7-3" (p. 65) and "families.*.round2.ci_axes..wire_fields" (p. 45) have no target in this volume.
- **Some terms are never defined.** These include NodeCore P5/P8/P10/P11 (p. 42), RATCHET (p. 45), M-1 (pp. 37, 49, 67), CEWP (p. 60), RequireHybrid (p. 41), 1+4 (first used on p. 6, explained only by reference on p. 16), and CCC/CCS (pp. 32, 47).
- **Some passages read as history or roadmap.** Examples:
  - "the new shaping and onion keys" and "the two symbol-count keys are retired with fountain storage" (p. 34)
  - "The roster is being widened ... until about seven hold seats" (p. 36)
  - "per the iOS NeuralHash 2021 incident" (p. 62)
  - "Future hash-coalition path (deferred; awaits CIRIS hash-coalition emergence)" (p. 62)
  - "First deployment: the Magnifica Humanitas encyclical mapping" (p. 63)
  - "Option A" and "Option B" labels (pp. 5, 60, 63)
  - "(not yet codified)" and "once that subkind is codified" (pp. 7–8)
  - "4.5.8.3 Settled in CIRISAgent, carried as-is" (p. 58)
- **Comparisons with other projects appear throughout:**
  - "like a subreddit or bitsavers" (p. 17)
  - Keybase, Secure Scuttlebutt, Certificate Transparency, Sigstore and TUF (pp. 20–21)
  - "(Casper FFG)" (p. 38) and "(KERI pre-rotation)" (p. 40)
  - JS8Call (p. 41) and "Delaware/BFT posture" (p. 41)
  - "Linux and its maintainer-decides discipline" (p. 43)
  - "relay-level (Nostr) / immutable-store (IPFS) / lax-instance (fediverse)" (p. 52)
  - "cf. Bluesky labelers + Ozone" (p. 53)
  - "a subreddit, a Discord, a Facebook-scale community" (p. 54)
  - "SOTA-aligned — UCAN / macaroons / SPKI-SDSI / ZCAP-LD" (p. 55)
  - "Signal-style" (p. 63)
- **Some sentences editorialize:**
  - "which is the justice the larger-collective form is built for" (p. 3)
  - "The compositional reach is the point" (p. 8)
  - "this is the autonomy/justice seam" (p. 11)
  - "humanity cannot be un-extincted" (p. 39)
  - "the machinery is theater" (p. 43)
  - "the need so dire (ciris.ai/constitutional-mesh)" and "the least bad option available" (p. 44)
  - "A community in which reported abuse survives has self-identified" (p. 66)
  - "that record is what justice composes over" (p. 67)
- **Some prose points at code or files:**
  - "formal/trust_root/ in this repository" (p. 27)
  - "FEDERATION_ANNOUNCEMENT.md §4" (pp. 36–37)
  - "CIRISPersist substrate" and "ciris-registry-core" (p. 37)
  - "MISSION.md §1.5" (p. 49)
  - "CIRISAgent's DSARExportPackage" (p. 48) and "CIRISAgent's 90-day-decay" (p. 49)
  - the .tsv, .json, .lean and .tla paths (p. 68)
- **Some numbers appear in prose with no source shown:**
  - "10s to 100Ks of members" (p. 3)
  - trust multipliers 1.0, 0.95 and 0.9 (p. 35)
  - "roughly a quarter coerced suffices" (p. 39)
  - "≥100,000 nodes" (p. 43)
  - takedown windows of 10, 14, 14 and 30 days (p. 51)
  - "~75-80% transparent translation rate" (p. 63)
- **The volume repeats its own justification.** The "Why this is still 1+4" and "1+4 preserved" passages recur on pp. 6, 16, 17, 18, 42, 53, 57, 58 and 67–68. The "What this documents / What it does NOT do" lists (pp. 49, 59, 61, 62, 64) argue the design rather than state rules.

## Opportunities
- A one-line fix on p. 37 would remove the most damaging contradiction. That line, the code comment on p. 37 and the p. 8 table row should say the halt is one holder's row and roster thresholds are a strict majority of the standing roster.
- One sentence could settle founder_only. Either it is refused outside self and family under the p. 68 floor, or p. 68 names it as an exception. The same sentence would fix pp. 3, 17 and 64.
- A mechanical sweep for literal `**`, escaped `\|` in table cells, and `§` printed as "S" inside code blocks would clear most rendering defects in one pass.
- Deleting the comparison asides costs no rule. Examples include the subreddit, Nostr, Bluesky and SOTA-aligned parentheticals.
- Folding the "Why this is still 1+4" and "What this documents" blocks into one register reference would shorten pp. 6, 16–18, 49 and 58–64 considerably.
- The civic and emergency tables on pp. 6–8 could move to *The Dictionary* or *The Charter*. They are worked examples, not powers, and they carry the stale halt row.
- Renumbering the takedown list on p. 51 to items 4 and 5 makes the in-text "item 4" reference resolve.

## Threats
- A lawyer reading p. 37 next to p. 30 finds two thresholds for the kill switch in the same chapter. The front page promises one holder's row (p. 1).
- A regulator will check that GDPR Article 9 sets a "default ≤ 30 days" (pp. 48–49). Article 9 sets no such deadline. The response deadline is in Article 12(3).
- On p. 60, "H3 resolution 7 hexagons average ~5 km² edge-length" mixes area and length. Resolution-7 edges are about 1.2 km.
- On p. 36, the volume names three people, says two of them "share a household", and gives a roster-growth plan. That is instance data and a plan, which a hostile reviewer will read as personal exposure and a rule-free promise.
- The volume enters a privilege it says it refuses. Page 43 says a carried privilege MUST satisfy four cells. Page 44 carries the WA board row with "both cells missing", so the document is non-conformant to its own rule as printed.
- The single-signer veto on p. 42 and the lone-signature path for any one holder can both be used to stall amendment. The wording does not tell an implementer which one holds.
- The p. 62 sentence about Microsoft and Project Arachnid, and the vendor-and-year table on p. 61, are factual claims about third parties that no register row can back.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 37 (vs 30, 1, 8, 36) | contradiction | "The 2-of-3 multi-sig verifier at CC 4.2.1.1 is the quorum:2/3 consensus_protocol enforcement" against "A constitutional halt is one holder's signature" and "never a fixed 2-of-3". The family code block and the p. 8 table row repeat quorum:2/3. | Restate as fire 1, confirm, resume and roster by strict majority of the standing roster. Fix the code block and the p. 8 row to match. |
| 2 | 68 (vs 17, 64, 3) | contradiction | "no single vote admits anyone anywhere" against "founder_only is typical" for public rooms and founder_only listed as canonical. | A steward ruling is needed. Either refuse founder_only outside self and family, or name it as the exception on p. 68. |
| 3 | 65 (vs 66) | contradiction | "No quorum is ever imposed on a moderator or a steward" against "A community MAY instead require a moderator quorum". | Change p. 65 to say no quorum is imposed by default, or drop the optional-quorum paragraph. |
| 4 | 52 (vs 53, 66) | contradiction | "No unmoderated multi-party space, ever" and "no moderator-less window" against a 48-hour recovery that ends with fail-secure. | State what the community may do during the 48 hours, or drop "ever" and "no window". |
| 5 | 15–16 (vs 12) | contradiction | "Minor stewardship" and "a guardian stewards the minor" against "a different relation this document does not liken to stewardship". Adult incapacity reuses the predicate on p. 12 while adult-target bindings are "rejected unconditionally" on p. 16. | A steward ruling is needed on whether guardianship is a steward-binding. Then align pp. 12, 15 and 16. |
| 6 | 40 (vs 38, 31) | contradiction | "the authoritative tally is CIRISServer" against "never a server ... no accord act depends on one". | Say the tally is recomputed by every verifier over the pinned roster, and drop the server name. |
| 7 | 62 (vs 61) | contradiction | "Microsoft Project Arachnid feed" against "Project Arachnid (C3P, 2017) Access-gated". | Fix the attribution and the "publicly-distributed" default. Drop vendor years and the NeuralHash history. |
| 8 | 13, 14, 38, 53, 65 | rendering | Literal `**` and `***` are printed with runaway bold, for example "**The same recovery path ... *seizure***". | Fix the markdown emphasis in the part files and rebuild. |

## Rendering
- Page 1: the title reads "The CIRIS Constitution: The Constitution", which is redundant.
- Pages 3, 4, 10 and 36–37: nested indentation inside code blocks is flattened. For example, `members: [ { key_id ...` all start at one column.
- Page 4: the code comment prints "-250 km^2" with a literal caret, and a tilde is probably lost.
- Page 5: the code block prints "default ‘rotate-forward‘" with mismatched quote glyphs.
- Pages 13–14: literal `**` and `***` show with long runs of unintended bold ("**distinct from being steward-less ... same**", "**The same recovery path ... *seizure***").
- Pages 18–19: the T2 heading is stranded at the foot of p. 18 above half a blank page, with its table on p. 19.
- Page 27: the page holds two lines and is otherwise blank.
- Page 28: the first line runs past the right margin ("(IncidentSeverity::INC").
- Pages 29, 32 and 37: `§` prints as "S" inside code blocks ("per S0.5", "per S0.6", "S9.2", "S4.5.3").
- Page 31: the prose prints a literal backslash, "constitutional \| notify \| drill".
- Page 35: the hardware mapping table shows trailing backslashes ("aws_cloud_hsm \", "ios_secure_enclave \", "tpm_discrete \"). An escaped pipe most likely truncated the alternatives.
- Page 38: literal `**` shows around "Proof-of-life records a vote ... does not".
- Page 46: the ci_axis enumeration line overflows the right margin.
- Page 48: the HIPAA 164.502 row is broken. "‘consent:scope:{retain\" and "share\" are split across cells by an escaped pipe, so content is lost.
- Page 51: the numbered list restarts at 1 after the per-basis bullets, though it should read 4 and 5. The in-text "item 4" reference therefore misses.
- Page 52: "scope ⊇ {moderate|takedown|r" runs off the page.
- Page 53: literal `**` shows around "Enforcement layer ... existence" and "delegable duty ... trusted party".
- Page 56: "subject_of(content_sha" runs off the right edge.
- Page 58: the heading "4.5.8.3 Settled in CIRISAgent, carried as-is" is orphaned at the page foot.
- Page 61: "(Policy M evaluate_subkind_admission" overflows the right margin.
- Page 65: literal `**` shows around "No quorum is ever imposed ... Term pin:".

## Effort estimate
About 12–16 hours. Rendering fixes, comparison and history deletions, and undefined terms are mechanical work of about 6 hours. Defects 1–6 and the step-5 veto on p. 42 need the steward's rulings before the text can be reconciled.


# The Wire (ciris_constitution-1.0-rc11-wire.pdf, 103 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The rules are detailed enough to build a second implementation from, but the volume has five real contradictions, a layer of stale section numbers and implementation pointers, and a 19-page signed-object table that the pipeline renders almost unreadably.

## Strengths
- The volume states its scope, who it binds and where the generated artefacts live in under a page, without history (p. 1).
- The canonical-hash preimage gives conformance vectors and a reject-vector table with a reason per row (pp. 15–16).
- The canonicalization rules are each closed with a vector requirement, a refusal token and a worked attack (pp. 28–34).
- The shaping defaults say plainly that they come from a model rather than a live mesh, and that they are revised when measurements exist (p. 95).

## Weaknesses
- **Comparisons with other projects** appear in several places:
  - "No prior identity system (PGP, SPKI/SDSI, W3C VC) types epistemic-error-admission…" (p. 26).
  - "the pattern proven by Nostr kind-ranges and Matrix reverse-DNS namespacing" (p. 55).
  - "This is exactly how Element ignores info.mimetype… and Synapse ignores…" (p. 76).
  - "Against the field, this design sits in the zero-emission corner…", followed by "surveyed systems…" (p. 103).
  - "What CEG adds beyond systems that ship default privacy…" (p. 5).
- **History and ruling voice** survives in the rules:
  - "This answers the open question of how to attest about un-enrolled parties" (p. 13).
  - "in the pre-FSD-003 reference Registry" (p. 14), and "The delimiter form stands" (p. 15).
  - "(the chosen model)… The rejected alternative" (p. 60).
  - "the LWW front-running fix", "As shipped", "V058 R1/Q1" (p. 71).
  - "the label CIRIS-AV-INNER-V1 is retired" (p. 82), and "/v1/steward-key is a kept alias" (p. 86).
  - "The v3 and v4 bundles share produced_at" (p. 88).
- **Code and file pointers** sit inside the rules:
  - "Persist treats this as TEXT" (p. 7) and tools/audit_emitted_dimensions.py (p. 19).
  - "Generated from constitution/signed_object.tsv… Edit the TSV" (p. 35).
  - "cirisnode_contributions V054 partial indexes" (p. 63) and MISSION.md (pp. 65, 85).
  - "registry_signing_keys table" and "land in the Rust handlers + OpenAPI export" (p. 89).
  - The worst case is a normative MUST that names a library function: "MUST pass the raw exporter_secret to the ciris-crypto scope_privacy::k_record_id helper" (p. 92).
- **Editorializing and marketing:**
  - "The honest line:" and "the document does not paper over it" (p. 5).
  - "The professional analogue is exact" (p. 24).
  - "The strongest privacy guarantee in the system…" followed by a ciris.ai/cewp marketing quote (p. 65).
  - "The breadth confirmation:" (p. 79).
  - "a classical secret ballot hides the vote; structural invisibility hides the election" (p. 103).
- **Numbers with no visible source:**
  - "thirteen distinct content cases", when only five are named (p. 18).
  - "this is the thirteenth path on the CC 1.7 claim" (p. 78).
  - "~3.1 Tbps… ~2 Tbps content fan-out" (p. 63).
  - "~65% of activity stays local in the cewp scaling model" (p. 67).
  - "ML-DSA-65 sign ~330 µs" (p. 75), and "~20–40% MDC compression overhead" (p. 80).
- **Third-party facts with dates** will go stale, and some will be wrong soon. Examples: "Mastodon disabled HEIF 2026-09-15", a list of 2024–2026 CVEs (p. 76), and "Android 17 moves AAC in-process as Rust" (p. 77).
- **Labels used without definition:** "F-3 detector" and "encyclical-sourced" (p. 12), "D08 autonomy claim" (p. 18), "AV-50" (p. 32), "D2 / D3", "V2 lock", "V1 lock" and "E1–E4 lock" (pp. 62, 77, 82, 83), "lightnet facts" (p. 59), "L1 peer" (p. 99) and "Leviculum" (p. 100).
- **Section 2.6 is headed "Foreword"** but sits in the middle of Part 2. It routes translators to "CC 8.2-CC 8.1", a range written backwards (p. 27).

## Opportunities
- Two escape fixes in the pipeline would restore every truncated enum and formula. One is for `|` in table cells. The other is for `*` in "capacity:*" and for stray `**`. The losses are on pp. 7–11, 40, 47–48 and 85.
- Narrower Presence and Note columns, or a landscape page for the signed-object table, would probably cut pp. 35–53 roughly in half and end the column collisions.
- One sweep could replace every "S0.5", "S5.2.1", "S8.1.12.4" and "CEG §11/§19.3" with the current CC section numbers. They appear on pp. 28, 35, 65–67, 81 and 92–94.
- Moving the third-party survey material out of the Parts would remove most of the comparison and dated-fact findings at once. That covers the renderable-set rationale (pp. 76–77) and the "Position" paragraph (p. 103), which could go to a register or an annex.
- The duplicated [FIPS-204] row (pp. 55 and 56) could be merged. The [SFrame] reference could be updated from "draft-ietf-sframe" to RFC 9605 (pp. 56, 77).

## Threats
- **cohort_scope default.** p. 5 says "Anonymity defaults to the smallest cohort scope… federation (public-commons) scope is the opt-in". The signed-object table lists the default for row.cohort_scope and the beside column as "federation" (pp. 37, 50). A hostile reviewer will read the second as the real default.
- **At-rest encryption.** The adversary table says a compromised substrate node "cannot decrypt self/family content (no DEK)" (p. 3). p. 66 says at-rest encryption "is operator-policy and MAY default off as a v1 migration posture". It adds that structural invisibility "holds even when the at-rest bytes are plaintext". The p. 3 claim is stronger than the rule behind it.
- **Explicit null.** p. 29 says "an explicit JSON null on any optional envelope member is refused as malformed". The scores wire shape on p. 26 shows `"oversight_mode": "<HITL | HOTL | HOOTL | null>"`, and the same pattern for occurrence_id, occurrence_count and occurrence_role.
- **Base64 alphabet.** p. 30 says base64 "MUST use the RFC 4648 §4 STANDARD alphabet" and calls URL-safe a non-verifying hazard. Both cosign request bodies give `"ed25519_signature_b64": "<base64-url>"` (pp. 67, 68).
- **Bundle version.** The bundle example has `"version": 1` (p. 86). p. 88 says "GENESIS_BUNDLE_VERSION 4… A version-4 bundle is a trust-root re-mint".
- **Large payloads.** The p. 44 note says "Above the 1 MiB cap the payload moves to the fountain plane". p. 33 says "the blob plane as encrypted chunks", and p. 96 says "Stored content is never encoded by a node". The p. 44 note is likely left over from the RaptorQ design.
- **Delivery receipts.** The receipt signs "epoch (u64 LE)" and "K (u64 LE)" over a length-prefixed shape (p. 85). Every other integer in the volume is big-endian (pp. 64, 77, 81). p. 35 also says an attestation's signing input is "JCS(attestation_envelope) and nothing else".
- **Endpoint count.** p. 67 says "CEG specifies five public + one admin HTTP endpoint shape". Sections 5.3.1 to 5.3.5 define more than ten.
- **Versioning text.** p. 55 still says "The 0.x series indicates this specification is a Public Working Draft". That reads oddly in a 1.0 release candidate.
- **Wrong cross-reference.** p. 63 calls T "the CC 5.3.3.6 equivocation-window grain". CC 5.3.3.6 is Delivery receipts (p. 85), and the cadence lives at 5.3.3.3 (pp. 2, 83).
- **Deference to an outside document.** "FSD-003 owns that change and this Part follows it" (p. 60) puts the authority for this Part in an implementation document.
- **Factual slip.** "H3 resolution 7 hexagons average ~5 km² edge-length" mixes area and length (p. 57). A reviewer who knows H3 will catch it.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 37, 50 vs 5 | contradiction | row.cohort_scope default "federation" against "Anonymity defaults to the smallest cohort scope… federation… is the opt-in" | Set the Default column to "—" for a REQUIRED member, or make the TSV agree with 1.13.3.4 |
| 2 | 3 vs 66 | overclaim | "cannot decrypt self/family content (no DEK)" against at-rest encryption that "MAY default off" | Qualify the p. 3 cell to say it holds only when at-rest encryption is on, or rule that it is mandatory |
| 3 | 26 vs 29 | contradiction | The wire shape lists "null" as a value, but an explicit null is refused as malformed | Drop "\| null" from the code block and say "absent" |
| 4 | 86 vs 88 | contradiction | Bundle example "version": 1 against GENESIS_BUNDLE_VERSION 4 and "v3 and v4 bundles" | Make the example 4 and remove the v3/v4 history |
| 5 | 67–68 vs 30 | contradiction | "<base64-url>" against the MUST for the standard alphabet with padding | Change the placeholders to standard base64, or scope the p. 30 rule |
| 6 | 7–11, 40, 85 | rendering | Enum cells cut at the pipe: "self \", "HITL \", "primary \", "here \", "family \", "generic \", "'pull \", "'full \", "MUST equal ⌊", "floor(\", "'cohort_scope: self\" | Escape `\|` in table cells in the pipeline |
| 7 | 44 vs 33, 96 | stale | "the payload moves to the fountain plane" | Change to "blob plane" in signed_object.tsv |
| 8 | 28, 35, 65–67, 81, 92–94 | stale | Old numbering such as "S4 default", "per S5.2.1", "S8.1.12.4", "S10.1.4", "per S0.6/S0.5", "S10.5.8.2", "CEG §11", "CEG §19.3/§19.4" | Replace each with the current CC section |

## Rendering
- Literal `**` appears in the text on pp. 2, 5, 32, 33, 55, 66, 70, 72 and 74. Examples are "**Unobservability", "scope**", "**substrate-protective…event**", "open**", "*excluded***", "**promotion is the federation-emit moment**" and "predicates**".
- Table cells are truncated at a pipe character on pp. 7, 8, 10, 11, 40 and 85.
- The `*` in "capacity:*" is eaten as italics and renders as "capacity:;" in every capacity row on pp. 47–48.
- The numbered list in 2.6.1.1.1 restarts at "1." for all three items (pp. 29–30).
- Text runs past the right margin on these pages:
  - p. 22 "proxy-establishment" and p. 23 `["personhood_const`.
  - p. 31, in the Canonical when explicit cells for subject_sha256_ed25519_raw, recovery_commitments and witnesses.
  - p. 63 "federation_stream_chunks(stream_id, seq)" overlaps the next column.
  - p. 65 "Catch-up bound (P4): min(…".
  - p. 81 "CHUNK_CODEC_LAYER_LEN" and p. 85 "SignedTreeHead::signing_bytes".
- The signed-object tables on pp. 36–53 have column collisions throughout:
  - The header reads "PlacementType".
  - Cells collide as "REQUIRED—", "OPTIONALabsent" and "REQUIREDfederation".
  - Long member names overrun into Placement, for example return_token, window_periods, floor_applied, epistemic_mode, oversight_mode, custody_state, halt_fuse_secs, what_was_false, successor_keys and witness_quorum.
  - On pp. 52–53 the Default column rules cut through the text.
  - The Note column sets one to three words per line, which stretches the table to about 19 pages.
- A missing glyph shows as "?" in the code block "no valid v2 wrap target ? EXCLUDE r" (p. 66).
- Backticks render as stray quote marks inside code blocks on pp. 18, 98 and 99.
- A stray horizontal rule sits at the top of p. 18.
- "-self-test" on p. 54 has probably lost a dash.
- "⌈log_k N⌉" shows a literal underscore on p. 103.
- The E1 cell on p. 84 is a full page of bold text inside a table cell.
- p. 6 is nearly blank, which is acceptable at a Part break.

## Effort estimate
About 12 to 16 hours. The rendering escapes, table layout, stale section numbers, pointer and history stripping, and reference fixes are mechanical. The cohort_scope default, the at-rest default against the adversary-table claim, the bundle version, the base64 alphabet and the receipt endianness each need a ruling from the steward.


# The Dictionary (ciris_constitution-1.0-rc11-dictionary.pdf, 108 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The rules underneath are dense and mostly exact, but a systematic table-rendering bug silently deletes enumerated values from about twenty registry rows. The volume also contradicts itself on membership, the accord leaf set and the age-band spelling, and it carries a long run of prior-art comparison and dated history that the house rules forbid.

## Strengths
- The front page states plainly what the volume binds and that the generated manifest wins over the prose (p. 1). Section 3.1 opens by refusing to restate the family count (p. 2).
- The normative rules are stated with refusal tokens and exact bounds. Examples are the session lease of at most 86 400 seconds with a named residual (p. 14), the R3 case rule (pp. 26–28) and the longest-pattern match rule (p. 87).
- Residual risks are named rather than hidden. Examples are "No possession challenge yet (stated)" (p. 17), the KEM forward-secrecy gap (p. 57) and "Two leaks are conceded, not closed" (p. 85).
- The adult-incapacity and minor-protection clauses close with an adversary table that maps each abuse move to the mechanism that defeats it (p. 101).

## Weaknesses
- **Pipe characters truncate table cells.** Any value list written with "|" inside a table cell is cut at the first pipe and shows a trailing "\". The remaining values spill into the Polarity or Reserved column or are lost. Examples are "{basis} ∈ dmca512 \" (p. 4), "voting \" / "proposal_filing \" (p. 3), "{band} ∈ minor \" with "under_13 \" (p. 6), "{state} ∈ proposal \" (p. 15), "(decided \" (p. 22), "{tier} ∈ l1_summary \" (p. 23), "{category} ∈ medical \" (p. 24) and "{version} ∈ v1.0 \" (p. 40). In these rows the closed vocabulary that the row exists to pin cannot be read.
- **The registry rows mix columns.** Some Reserved cells hold emitter text and some Polarity cells hold enum values or prose. Examples are preserve_response, archive_release and lawful_order:release (p. 22), and the health:liveness Polarity cell, which carries the whole rule as raw markdown (p. 35).
- **Section 3.3 is mistitled.** It is headed "Content-ingestion prefixes" (p. 40) but holds consent, takedown, key_grant, family, identity_occurrence, the key roster, ledgers and the canonical binding through p. 77. The front page calls it "the subject kinds and their payload shapes" (p. 1).
- **There is a long informative prior-art essay.** It compares the design with Holochain, Lightning, Sardex, WIR, Circles, SSB, Hypercore, Keybase, Certificate Transparency and SUNDR, with dates and failure claims (pp. 69–71).
- **Product and brand names appear in rules.** Examples are "Stripe" and "CLAUDE.md discipline" (p. 67), "USDC on Base via x402" (p. 68), "Default model: Claude Opus 4.7" (p. 35), "Apple Declared Age Range / Google Play Age Signals" (p. 102) and "Alice scrolls Twitter" (p. 52).
- **Several identifiers are never defined in this volume.** These are "WBD" (pp. 54, 102–106), "AV-17 / AV-42 / AV-88" (pp. 57–58, 76), "F-AV-ROLLBACK" (p. 66), "F-AV-DORMANT" (p. 38), "§Q B2" (p. 63), "Piece 10 karma … upstream-retracted" (p. 39), "OneOfSix" (p. 73) and "M-1" (pp. 20, 38).
- **Some passages editorialize or name real people.** Examples are "Britney-style capture" (p. 95), "the Britney pattern" (p. 96), "Britney's included" (p. 99), "what makes this Ubuntu-aligned" (p. 33) and "Getting this backwards … would be catastrophic" (p. 96).
- **Dates are attached to rules or used as evidence.** Examples are "applicable 2026-08-02" and "after 2026-08-02" (pp. 106–107), "Mastodon disabled HEIF / AVIF on 2026-09-15" and "five libheif advisories through 2026" (p. 74), "Texas HB 1181 / Paxton 2025" (p. 102) and "retirement horizons near 2030" (p. 47).
- **Code pointers sit in normative text.** Examples are "prohibitions.py" (p. 23), "FEDERATION_ANNOUNCEMENT.md S4" (p. 51), "CIRISNodeCore FSD/MEDIA_SHARING.md §4 … SCHEMA.md §4" (p. 76) and "ciris-crypto KEY_GRANT_ALGORITHM_V2" (p. 47).
- **The minor-protection section switches citation style.** From p. 101 it cites with "§2.4.1" and "§3.2" while the rest of the volume uses "CC x.y".

## Opportunities
- Escape "|" inside table cells in the build pipeline, or switch enum lists to "·" as p. 2 already does. One fix restores roughly twenty rows of lost vocabulary.
- Move "Composition note", "Worked example" and the "Bilateral pair pattern" out of code fences where they contain markdown tables or prose. Normative text currently renders as preformatted source (pp. 50, 53, 55–56).
- Cut "The prior-art record", "Attempted, and the lessons" and "One kernel, bounded siblings" (pp. 70–71) to a single register-backed sentence. That removes the largest comparative surface in the volume.
- Retitle 3.3 to match the front page. Add a one-line note at Part 3 that 3.2 lives in another volume, because the jump from 3.1.10 to 3.3 reads as a numbering error (p. 40).
- Replace "Default model: Claude Opus 4.7" with "the model pinned in the calibration package" (p. 35).

## Threats
- **Membership contradiction.** On p. 15 the text says "A supersede never adds a member (normative)… a roster-growing supersede is refused. Every addition goes through the widening plane." The family ceremony says "Proposer … emits a new family Contribution superseding the current family Contribution … with the new membership list" (p. 51). The worked example says "Bob proposes a supersedes Contribution adding {carol…} … admits on Bob's signature alone" (p. 52), with no acceptance by Carol. An implementer following pp. 51–52 violates p. 15.
- **The accord leaf set is "closed" but differs between two pages.** On p. 4, accord:lifecycle:confirmed is listed ("a strict majority's confirmation of a one-holder constitutional halt"). The table on p. 78 says "the rows below are the whole family" and omits it. On p. 78 a constitutional halt is lifted by "a majority of the standing roster (CC 4.2.6)", while p. 4 frames confirmation "within its fuse" under CC 4.2.1.3.
- **The age self-declaration has three spellings.** These are "age_self_declared:band:{band}:{version}" (pp. 6, 94), "age_self_declared:{band}:v1 / e.g. age_self_declared:adult:v1" (p. 93) and "age_self_declared:minor SUFFICES" (p. 103). R3 makes a wrong segment count a refusal, so two of the three are malformed by the volume's own rule.
- **The band vocabulary is both closed and extended.** The text says "AgeBand ∈ { minor, adult }" and "band in { minor, adult }" (p. 93). Elsewhere it gives "Minimum bands: under-13, 13–15, 16–17, adult (18+)" (p. 102), and the registry row shows "under_13" (p. 6).
- **The accord roster is an instance parameter but is hardcoded.** The text says "the roster is an instance parameter … read against the slot, never against its current occupant" (pp. 5, 78). Yet p. 51 prints a canonical HUMANITY_ACCORD family whose members are "eric-moore-key", "eric-kudzin-key" and "haley-bradley-key". A lawyer reads that as naming the authority holders inside the constitution.
- **A count does not match its table.** The text says "Four substrate-emitted prefixes" (p. 78). The table that follows lists nine hard_case kinds and states "They are not prefix families" (p. 79). The 3.4.4 lead-in repeats "membership-event prefixes" followed by the same disclaimer (p. 80).
- **Field names drift in the precedence rule.** The concurrent-write rule ranks on "signed_at" (p. 108), while every admission and fold rule elsewhere uses "asserted_at" (pp. 15, 43, 61).
- **Transitional and stale text remains in a 1.0 candidate.** Examples are "Until that cut, the text below stands as it is" for the Portal organisation kinds (p. 65), which also contradicts p. 65's "no roster of permitted authorities" against p. 67's "M-of-N steward quorum". Others are "Until a substrate's door carries this family…" (p. 34), "the interim using a registry_witnesses table" (p. 92), "cross-attested by all stewards in the steward-triple" (p. 80), "StewardTriple / WaQuorum / OneOfSix" (p. 73) and "CC 1.13+4 lockdown" (p. 72), which looks like a garbled "CC 1.7 1+4".
- **Some claims are stronger than the evidence shown.** Examples are "Certificate Transparency's split-view detection … never deployed" (p. 69), "HoloFuel still unshipped 8+ years … no swap as of mid-2026" (p. 71), "multilateral netting removes ~96% of gross obligations" (p. 71) and the CVE list including "CVE-2026-28609" (p. 74). None carries a register row.
- **A component count does not match the text.** The text says "Eight owning components are committed by a sibling MISSION.md" (p. 2). The sections cite seven MISSION.md files, plus RATCHET's FSD.md (p. 24) and CIRISBench's README (p. 40).

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 3–6, 10–11, 15, 17, 21–24, 32, 34–35, 38, 40, 73, 92 | rendering | Pipe-separated enum values are truncated with a literal "\" and columns are shifted, so closed vocabularies are unreadable | Escape "\|" in table cells in the pipeline, or use "·" separators, then re-check every Polarity and Reserved column |
| 2 | 15 vs 51–52 | contradiction | "A supersede never adds a member" against a family ceremony and worked example that add members by supersede with no acceptance | Rewrite the ceremony and the Carol example to use proposal, acceptance and widening per 3.1.3.2 |
| 3 | 4 vs 78 | contradiction | The closed accord leaf set includes lifecycle:confirmed on p. 4 and omits it on p. 78, and the lift rule differs | Make p. 78 match the generated registry and state one lift rule |
| 4 | 6, 93, 94, 103 | contradiction | Three spellings of age_self_declared, and the band set is {minor, adult} on p. 93 but four bands on p. 102 | Pick one arity and one band vocabulary, then fix every example |
| 5 | 51 vs 5, 78 | contradiction | Named individuals are hardcoded as the canonical accord family while the roster is declared an instance parameter | Replace with placeholder keys or drop the instance block |
| 6 | 69–71, 74, 47 | editorializing | Prior-art and comparative essay with dated failure claims about named projects | Cut to rules, or move to an annex backed by register rows |
| 7 | 35, 41 | rendering | The health:liveness cell shows raw markdown in the wrong column, and the consent:state row is overprinted | Fix the source cells so the backtick and pipe content stops breaking the table |
| 8 | 65–67, 34, 92 | stale | Transitional text ("Until that cut…", "Until a substrate's door carries…", "interim") and two designs for organisations | The steward rules on the post-cut text, and the transitional prose is deleted |

## Rendering
- Pipe truncation with a literal "\" in table cells on pp. 3, 4, 5, 6, 10, 11, 15, 17, 21, 22, 23, 24, 32, 34, 35, 38, 40, 73 and 92.
- A literal "\|" in prose on p. 48 ("content \| epoch \| stream") and p. 64 ("family \| community \| affiliations", "phone \| laptop", "server \| embedded \| service \| agent").
- A literal "dimension\'s" on p. 84.
- Literal "**" or "*" markers on pp. 35, 47, 55, 57, 68, 69, 95, 96, 101 and 102. On p. 69 most of a paragraph is bolded with the markers visible.
- Literal markdown links on p. 51 ("[CC 4.5.13](part_4_composition_governance.md)"), p. 55 ("[CC 2.6.3](part_2_the_grammar.md)", "[CC 3.1.2](#3.1.2)") and p. 102 ("[CC 1.13.3.4]").
- Markdown tables and normative prose rendered inside code blocks on p. 50 (MemberRole), p. 53 (ConsentStance) and pp. 55–56 (the build rule, EncryptionPubkeys, TransportDestination and DeviceClass).
- The health:liveness cell shows raw markdown and backticks in the Polarity column on p. 35.
- The consent:state row on p. 41 has its prefix text overprinted ("{granted\revoked}") and its description sitting in the Polarity column.
- Code blocks are clipped at the right edge on p. 8 ("ed25519_signatur"). Code wraps badly on p. 75 (field-set table) and p. 52 (ASCII brackets "-+ |").
- Missing glyphs render as "?" on p. 90 ("may_act_through(agent, node) ? E h .") and p. 97 ("attester(capacity) ? {S, petitioner}", "^ PROTECTED_NON_TRANSFERABLE == ?").
- Text runs past the right margin on p. 24 (leaf list), pp. 30–31 ("content_rating"), p. 47 (bold wire-string line), p. 48 (envelope member list), p. 68 ("cohort_scope:"), p. 85 ("attestation:agent_in"), p. 92 ("lenscore_detector}."), p. 93 ("identity_type"), p. 102 ("safeguarding-") and p. 105 ("CSAM detection+report,").
- An empty orphan table header row appears at the top of p. 44.
- Stray horizontal rules appear at the top of p. 51 and p. 81.
- The heading "3.1.9.4" is orphaned at the bottom of p. 34 with its table on p. 35.
- The formula on pp. 28–29 renders "𝒞_CIRIS" with a literal underscore.
- Numbering jumps from 3.1.10 to 3.3 on p. 40 with no note in the body text.

## Effort estimate
About 12–16 hours. Around 4 hours is mechanical: the pipe escape, the code-fence and markdown cleanup, and margin overflow. Around 6 hours is pruning prose: prior art, dates, brands, code pointers and undefined identifiers. The five contradictions need the steward's rulings first: membership by supersede, the accord leaf set, the age-band arity and vocabulary, the named accord roster, and the organisation design after the cut.


# The Reader's Policies (ciris_constitution-1.0-rc11-policies.pdf, 33 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The volume holds the substance a consumer implementer needs, but it reads as a design notebook: it contradicts itself on forward secrecy and on community encryption, and it is full of stale cross-references, file pointers and code blocks whose indentation has been lost.

## Strengths
- The anti-pattern tables pair each rejected wire shape with the correct way to express it, so an implementer can act on them directly (pp. 2–4).
- The rule that M in quorum:M/N is an absolute count is stated precisely, with a worked number and a separate rule for the liveness margin (p. 19).
- The co-self and agency split is a clean two-row table, and each layer can be revoked independently (p. 20).
- The signed member set for the partnership envelopes is pinned field by field, which is exactly what interop needs (pp. 23–24).
- The section on the pinned trust set as a graph is a crisp eight-point normative list (p. 31).

## Weaknesses
- The front matter carries release history in a rule volume: the verdict contract table "is an rc9 item and will print here when it exists" (p. 1). The volume is rc11.
- Cross-references use an old "S" numbering that does not exist in this document: "S5.6.8.10" (p. 8), "S8.1.13.2" (pp. 8, 10), "S0.8.2" (p. 10), "S8.1.12.3.1" and "S8.1.12.4" (pp. 18–19), "S8.1.11.4" (p. 23), "S8.1.12.7", "S5.6.8.8.1" and "S4.2.2.3" (p. 24), "S8.1.12.3" (p. 25).
- File and code pointers sit in the rule text: "LANGUAGE_PRIMER.md" (p. 4), "MISSION.md" (pp. 11, 28, 29), "../MISSION.md §1.1" (p. 33), "(part_3 guardianship clause)" (p. 15), "registry.ciris-services-1.ai/install" (p. 30) and "GET /v1/trust-root/bundle" (p. 30).
- Undefined internal labels appear without explanation: "Closes G3" and "WA quorum" (p. 5), "NodeCore P8 quorum" (p. 3), "NodeCore P4 votes" (pp. 30, 33), "AV-17" (pp. 23, 24), "OQ-4" (p. 25), "M-1's symmetry" (p. 33), "1+4" (pp. 16, 22, 31) and "CEM" (p. 26).
- The text reads as design-process history: "recorded so the next generation of authors finds the discipline" (p. 2) and "Rejected stress-test reaches" with counts like "7 stories", "12 stories" and "(1 reviewer)" (pp. 3–4). Other examples are "recommended for v1" and "deferred to a future … downstream-demand-driven release" (p. 25), "This is the single most load-bearing addition" (p. 13), and the "(LIVE)" status tag in a heading (p. 16).
- Editorializing and philosophical framing stand in for rules: "The Ubuntu-primary discipline cuts cleanly" (p. 2), "Cartesian shortcut" (p. 3), "Un-trust is nuclear but recoverable" (p. 31) and "structural rather than rhetorical" (p. 30).
- The policies are printed out of order: E, M, H, L, K, I, F, A, D, J, G, B, C. Policy A is the conformance floor but appears eighth (p. 30), and the volume jumps from 4.1 to 4.4 without explaining where 4.2 and 4.3 are (p. 4).
- Brand and product names appear in the examples: "Twitter history" (p. 18), "Twitter scroll" (p. 26), "roku_living_room" and "nest_thermostat" (p. 25), "CIRISAgent CEM ANONYMOUS" and "ciris-agent-90day" (p. 27), "Verify" and "Both impls" (pp. 23–25), and "EigenTrust-style … less common in practice" (p. 33).
- One rule has an unclear scope. The heading says "moderate / takedown / review" and the text says "These three kinds", but the table lists five scopes, including license and grant (p. 21).
- One phrase has no referent: "The four implementations MUST follow this shape" never says which four (p. 20).

## Opportunities
- Two edits would turn many internal contradictions into one consistent rule. First, rename the community removal rule so that "Option A" means one thing. Second, make the Austin worked example match the mandatory community encryption.
- One sweep could replace every "S…" reference with its CC number or delete it. The same sweep could strip the file names, ticket and question labels, and the rc and v1 roadmap language. This is mechanical work.
- Reordering 4.4.3 to run A, B, C … M would make the front-matter promise of "Policies A to M" navigable, with Policy A first as the floor.
- One consistent marker per section, either normative or recommended, would resolve the conflict between p. 1 and p. 4. The current markers are mixed: "(normative)", "(NORMATIVE)", "(MANDATORY)", "(LIVE)" and none at all.
- Re-indenting the pseudocode blocks would make their control flow readable again (pp. 8, 18–19, 27, 29).

## Threats
- **Forward secrecy contradicts itself.** P. 7 says "The CC 4.4.3.4.5 Option A discipline applies identically: on member removal the substrate rotates the community DEK". P. 25 defines Option A as "No DEK rotation; no re-encryption of historical content" and says "Option B (rotate-DEK on removal) is deferred". The table on p. 20 also says "withdraws the occurrence → Option-A re-key".
- **Community encryption contradicts itself.** P. 7 says "Community DEK cascade (MANDATORY) … encrypted at rest under a per-community DEK". The worked example on p. 10 says "No key_grant cascade (community is unencrypted); no at-rest wrap."
- **Self/family encryption contradicts itself.** P. 7 calls self/family encryption "the CC 4.4.3.4.1 self/family opt-in". Pp. 17–18 have the substrate emit key_grants on every admission, make "wrap_algorithm: v2 MANDATORY", and require that "A Consumer MUST reject" v1.
- **Revocation precedence contradicts itself.** P. 28 relies on "latest-wins / revoke-is-terminal precedence at the consumer read path (CC 4.4.3.5.5)". The resolve_consent code on the same page takes the latest entry ordered by asserted_at, so a later grant overrides a revoke. Revoke is not terminal as written.
- **Normative force conflicts.** P. 1 says a consumer "may not skip the ones marked normative". P. 4 says a consumer "MUST implement at least Policy A; the others are RECOMMENDED". Yet Policies M and L contain sections marked normative and MANDATORY.
- **Policy F reads as a leftover authority roster.** It says an agent_files attestation "from a registry-steward-triple key constitutes the CIRIS canonical default-trust state" and that it "Binds CIRIS L3C" (p. 30). This sits against Policy A's "the shipped default root — never the root" and "Roots are pluggable" (pp. 30–31). Policy J's "CIRIS L3C maintains a default trust set" has the same problem (p. 32).
- **Encoding rules may conflict.** P. 23 says "all hash and pubkey byte fields … are lowercase hex per CC 2.6.3". P. 25 says encryption_pubkeys are "opaque base64 strings (RFC 4648 STANDARD, padded". The exception is not stated as an exception.
- **Halt naming may be stale.** "HUMANITY_ACCORD CONSTITUTIONAL halt (CC 4.2)" may be a leftover from an earlier halt design (p. 6).
- **Some numbers have no visible source.** Examples are "score ≥ 0.7" (p. 30), "SI ≥ 0.6 Controller rule" (p. 15), "default 5:1" (p. 3) and "0.5 × root_trust" (p. 2).
- **Annex references may dangle.** "Annex I §3.2" and "Annex C cross-walk" (pp. 14–15) could not be checked from this volume.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 7 vs 25, 20, 11 | contradiction | "Option A" means DEK rotation on p. 7 and p. 20 but no rotation on p. 25, where rotation is "Option B … deferred" | Give the community rule its own name, or align both with a steward ruling, and fix the table on p. 20 |
| 2 | 7 vs 10 | contradiction | Community content is "MANDATORY" DEK-encrypted on p. 7 but "unencrypted; no at-rest wrap" in the worked example on p. 10 | Rewrite step 4 of the example to show the DEK wrap |
| 3 | 28 | contradiction | The text says "revoke-is-terminal" but the resolve_consent code is latest-wins | Make the code treat revoke as terminal, or drop the claim |
| 4 | 1 vs 4 | unclear rule | "may not skip the ones marked normative" conflicts with "the others are RECOMMENDED" | State per policy which parts bind a CEG-Conforming Consumer, using one marker style |
| 5 | 8–25 | stale | About fifteen "S…" cross-references to a numbering scheme that is not in this document | Map each to a CC number or delete it |
| 6 | 7 vs 17–18 | contradiction | Self/family encryption is called "opt-in" on p. 7 but is mandatory, with v2 required, on pp. 17–18 | Delete "opt-in" on p. 7 |
| 7 | 30 | stale | Policy F's "registry-steward-triple key" canonical trust and "Binds CIRIS L3C" reads as an authority roster | Restate it in pluggable-root terms, which needs a steward ruling |
| 8 | 1, 2–4, 25 | editorializing | rc and v1 history, story counts, "next generation of authors" and roadmap deferrals | Strip the history and keep the rules |

## Rendering
- Pseudocode blocks have lost all indentation, so the nesting of if, for and match cannot be read (pp. 8, 18, 19, 27, 29).
- Checkmarks render as the letter "v": "majority rule satisfied v" and "subkind_ok v" (p. 10). The tilde in "~5 km^2" renders as "-5 km^2" (p. 10).
- A literal backslash-pipe appears in "here \| none" (p. 6). A trailing backslash appears in the table cell "consent:partnership_grant:v1" \" (p. 24).
- Underscores render doubled in "local__feed", "community__feed" and "global__feed" (p. 17), the heading "CC 3.3 sub__kinds" (p. 17), and the heading "subject__key__ids[]" (p. 26).
- Text overruns the right margin in the Policy G composition line, which is clipped at "(attestation:regi" (p. 33). It also overruns at "delegates_to(parent" (p. 15), "rbac (role→(class,compartment))" (p. 13) and "identity_type" (p. 22).
- Code identifiers break mid-word with no hyphen: "score:trus tworthiness" (p. 3), "testimonia l_witness" (p. 4), "evaluate_subkind_adm ission" (p. 8), "identity_o ccurrence" (p. 11), "culturally_restricte d" (p. 12), "consensus_ protocol" (p. 14), "transport_destinatio n" and "destinatio n_hash" (pp. 23, 24), "retr oactive" (p. 25) and "subject_ke y_ids" (pp. 23, 26).
- The UN/IGO table cell breaks inside quoted strings, leaving lone quote marks on their own lines (p. 16).
- Curly quotes appear inside a code block in "‘consent:decay:*‘" (p. 27).
- Headings are stranded at the bottom of a page with their content on the next page: "4.1.3 Already-rejected wire additions" (p. 2), "4.4.3.4.1 Key-grant cascade" (p. 17) and "Instantiation — smallest vs largest" (p. 15).
- Headings nest six levels deep, for example 4.4.3.4.2.1 and 4.4.3.4.3.1. There is an extra blank gap under 4.4.3.2.4.1 (p. 9) and 4.4.3.4.3.1 (p. 23).

## Effort estimate
About 12 to 16 hours. Roughly half is mechanical: cross-references, pointers, rendering, reordering and history stripping. The rest needs steward rulings on the four contradictions, on what Option A means, and on Policy F's canonical trust.


# The Threat Model (ciris_constitution-1.0-rc11-threats.pdf, 105 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The first 48 pages are a strong, conditioned threat model. The volume then carries about 57 pages of Part 8 and Annexes B–J that are mostly not threat-model content, and those pages hold the volume's contradictions, history leftovers, comparative claims and legal mis-citations.

## Strengths
- The non-goals section says plainly what the format does not protect, and it binds operators with a MUST NOT (p. 2).
- The adversary table has an "Addressed" and a "NOT addressed" column for every row. Each row names its residual, for example "an observer who controls all but one owner in a cell" (pp. 3–5).
- The section on what an outside observer still sees is honest framing a red team can attack directly (p. 45). So is "What it does not yet buy" for the onion tier (p. 48).
- The shaping defaults are labelled as model output: "They are not measurements from a live mesh, and they are revised when live measurements exist" (p. 40).
- The byte-exact record_id conformance vectors and the CBOR major-type pinning give implementers something to test against (pp. 37–38).
- The strength-grades table (identity, theorem-given-model, measured, cited-external) is a usable reading key for the register (p. 66).
- The Annex J evidence block reports a result that goes against the project: the accord as a plain prompt scored worse than the bare model, 37.3% against 24.0%. It also states what the result does not establish (pp. 100–101).

## Weaknesses
- **Stale history on page 1.** The front matter says "The conditioned adversary table the rc8 review asked for is an rc9 item" in an rc11 volume, and the table now exists on pp. 3–5 (p. 1).
- **Promise not kept.** The front matter promises "the record of what was attacked and found is kept, including the attacks that succeeded" (p. 1). No such record appears, and Annex G says "A full red-team cycle against all CIRIS checkpoints is owed" (p. 80).
- **Scope does not match the front matter.** The front matter scopes the volume to 1.13.3, Part 5, the concerns ledger and the interop profiles, and says the ethics are left to The Charter (p. 1). The volume then carries the glossary, translation discipline, update cadence and Annexes B–J (pp. 49–105). Annexes F–H ground their thresholds in encyclical paragraphs, which is ethics content (pp. 71–89).
- **Threat IDs with no catalogue.** Threat entries "AV-59", "AV-60", "AV-61" and "F-AV-FRONTRUN" are cited (pp. 15–16, 18). The threat-model volume contains no AV catalogue to resolve them.
- **Code and implementation pointers inside rules.** Examples include "cirisnode_contributions V054 partial indexes" (p. 8), "CIRISPersist V058 R1/Q1 ... As shipped." (p. 16), "Edge's PeerResolver::resolve_holders" (p. 14), "registry_signing_keys table" (p. 34), "land in the Rust handlers" (p. 34), and "lexwatcher.py source-feed list MUST include" (p. 90).
- **Old FSD section numbers.** Code blocks and comments still say "S8.1.12.4", "S5.6.8.4", "S10.1.4", "S7.7" (pp. 10–11), "S10.5.8.2" (p. 26), and "per S0.6" (pp. 12, 62). Other dangling references are "CEG §11" (p. 37), "CEG §19.3" (p. 38), "CEG §19.4" (p. 39), "CC 3.x archive_mode" (p. 50), "§3.4 D26 ext" (p. 50) and "(§G)" (p. 104).
- **Wrong endpoint count.** The text says "CEG specifies five public + one admin HTTP endpoint shape" (p. 12). Pages 12–34 then define more than ten routes and no admin route.
- **Byte order differs between constructions.** The epoch is "u64 big-endian ... normative and MUST be byte-identical" (p. 22). The delivery receipt encodes "epoch (u64 LE)" and "K (u64 LE)" (p. 30), with no note that the difference is deliberate.
- **The same construction is specified twice.** The symbol_key derivation, envelope layout and rebind-on-Add/Remove rule appear in 5.4.2 (pp. 38–39) and again in 5.4.3 (p. 41).
- **Possible leftover from an earlier design.** The text says "a sealed A/V chunk is encoded with RaptorQ into symbols" (p. 41). RaptorQ was dropped by an rc10 ruling, so this sentence needs checking.
- **Undefined "slashing".** The text says "deviation from the constant tick is a federation-tier slashing condition" (p. 43). Slashing is defined nowhere in the volume, and p. 15 says a related signal is "not a slashing trigger on its own".
- **Prose that is not rule text.** Marketing and editorial lines include "this is the thirteenth path on the CC 1.7 claim and the most product-complete" (p. 23), "The breadth confirmation" (p. 24), "CEG's moat is its semantics ... We never adopt anyone's semantics" (p. 60), "a classical secret ballot hides the vote; structural invisibility hides the election" (p. 48), and the ciris.ai/cewp quote "You don't need a privacy policy..." (p. 10).
- **Numbers with no visible source.** These include "realistic audience churn (~30%/hr)", "~3.1 Tbps", "~2 Tbps" and "~18.7 Gbps" (p. 8), "~65% of activity stays local" (p. 12), "ML-DSA-65 sign ~330 μs" (p. 20), "~20–40% MDC compression overhead" (p. 25), "a model lying 45% of the time" (p. 79), and "bounty paid from 0.1 % ops levy" (p. 80).
- **Stale tags in the concerns ledger.** Open items are labelled "RC1-1b", "RC1-1c", "RC1-7" with steward "router" (p. 56). The closed-gaps table is history ("v1.4 T-3 #1", "RETRACTED Wrong threat model") and uses the retired term "holds_bytes" (p. 57). The live text uses custody:ack:v1 (p. 14).
- **Out-of-order risk numbering.** The risks run R1–R7, then R9, then R8 (pp. 54–55). R2's "What's bet" cell states a test, not a bet (p. 54).
- **Status mixed into deferred lists.** The deferred table's first row reads "No longer deferred: discharged per R5" (p. 59). Roadmap labels "Phase C" and "Phase E" are not defined in this volume (p. 59).
- **Three different rules for KPI breach.** Annex G says "Breaching any KPI for > 14 d triggers IW-2" (p. 83). Annex H uses a 1–7 d, 8–30 d, >30 d ladder (pp. 88–89). Annex F says "Persistent breach (> 2 weeks) triggers 'HITL lock-out'" (p. 75).
- **Two thresholds for one drift signal.** Annex G says "Shadow Hendrycks items ... Δaccuracy < -3 % → IW-2" (p. 81). Annex H says "Ethical drift (Shadow HE-25 any ↓): IW-2 immediate" (p. 86).
- **Release gate against incident trigger.** Annex J's release gate tolerates "Guardrail violation rate < 1%" (p. 102). Annex J also says "any FAIL triggers Incident Workflow IW-3" (p. 104), and IW-3 is defined as a "Near-miss (> $10 k damage or minor injury)" (p. 74).
- **Wrong KPI and annex references.** The text says "KPIs F-T-1 through F-T-5 (Annex G)" (p. 96), but the F-T KPIs are in Annex H (p. 86). F-T-4 is "User opt-out success" (p. 86) but is used as the DSR SLA and access-response KPI (pp. 92–93). "Annex B §9" is cited for review and recusal (pp. 93, 99), but §9 is "Oversight & removal" and recusal is §5 (p. 68).
- **Broken sentence.** The text reads "Purple Team – embeds that document lessons & patch guidance" (p. 80).

## Opportunities
- Delete the rc8/rc9 sentence on p. 1. Replace the "attacks that succeeded" promise with a pointer to where the attack record will live, or state that none exists yet.
- Cut the volume to 1.13.3, Part 5, 8.3 and 8.4, and leave Annexes B–J to the Policies or Charter volume. This removes most of the contradictions below and about 45 pages. It is a build-manifest change, not a text change.
- Run a global sweep for the "S<n>.<n>" references, "CEG §" and "§G". Map each to a CC number or delete it.
- Merge the duplicated symbol-framing text on p. 41 into a back-reference to 5.4.2.
- Add one line to the receipt bytes on p. 30 saying LE is deliberate, or switch the receipt to BE.
- Recount the endpoints on p. 12 or delete the count.
- Retag RC1-1b, RC1-1c and RC1-7 with current claim ids, and replace "holds_bytes" with custody:ack.
- Put the risk table back in R1–R14 order.
- Move the comparative "Position" paragraph (p. 48) and the 8.3.2 nine-network comparison (p. 55) to a non-normative prior-art document. If kept, restate them without "only" or "categorically stronger".

## Threats
- **Contradiction on post-compromise security.** The non-goals say "Post-compromise security (PCS) for streams. The CC 4.5.12.1 Option-A choice is forward-only ... a compromised current member's key is not self-healed by a key-update the way MLS PCS provides" (p. 2). Page 10 says "Post-Compromise Security (PCS) is AVAILABLE (inherent to TreeKEM key-updates: a compromised current member heals on the next commit) and is OPTIONAL, operator-enabled." A security reviewer will read these as opposite claims.
- **Contradiction on normative status.** The interop section says "This whole section is informative (CC 2.5). Nothing here touches the frozen normative interior" (p. 60). Two pages later it says "Disposition: ADOPTED — ... emit normative for generated media" and "For generated media the emit is not optional ... the node MUST emit the C2PA assertion" (pp. 61–62).
- **Contradiction on open stubs.** The stub registry says "Open stubs: 0" (p. 104). Section 8.6.4 is still the placeholder "[source content to migrate — ... not present in this snapshot.]" (p. 67).
- **Onion design mislabelled.** The non-goals call the Anonymous Tier "Sphinx onion routing" (p. 2). The design on p. 47 says "Because ML-KEM cannot be blinded, the header carries one KEM ciphertext per hop", which is not Sphinx. A cryptographer will flag the name.
- **Comparative overclaim.** The text says "All 9 surveyed networks permit unmoderated multi-party spaces and fail open. CEG is the only model that fails secure" and "The moderation surface is complete" (pp. 55–56). Other examples are "No surveyed system survived its first emergency use with legitimacy intact" (p. 55), "The federation is the first to ship them at scale" (p. 58), and "Signal ships mp4san / webpsan", "Mastodon disabled HEIF 2026-09-15" (pp. 21–22). All break the house rule and will date.
- **Legal mis-citations a lawyer will catch.** Annex I maps "Art 16 Human Oversight" (p. 95) and says Annex F satisfies "EU-AI-Act Art 16" human-in-the-loop (p. 99). Annex C lists "Art 14 Human oversight" and "Art 16 Provider obligations" (p. 70). "F-Audit ... doubles as EU-AI-Act MDR" uses the Medical Device Regulation acronym (p. 95). "Within 72 hours (GDPR standard)" for opt-out has no GDPR basis (p. 93). "export.json compliant with ISO CSV-A" names a standard I cannot identify (p. 91). ISO 42001 risk assessment is mapped to "Cl 6.2" on p. 70 and to "§6.1" on p. 96.
- **The federation is named as a liable party.** The liability matrix names "Deploying Org + Federation (if ST ≥ 4)" (p. 97). The glossary says CEWP "has no steward, no root, and no load-bearing instance" (p. 49), so there is no legal person to hold liable.
- **Weapons example against the lethal-action prohibition.** The autonomy table lists "A4 Critical / life-safety | autonomous surgery, weapons" (p. 72). Page 73 says "No CIRIS-conformant system may execute a lethal or irreversible A4 action through an automated or opaque process." A hostile reader will quote the table row alone.
- **Political and news citations.** The text cites "President Donald J. Trump Inaugurates the Era of Super Intelligence" and Meta and OpenAI product posts, partly through thehackernews.com for a Wall Street Journal story (p. 67). It names a papal encyclical as "Primary normative source" (p. 76), with "burden of proof ... rests on the CIRIS side of any divergence" from it (p. 83). A regulator or a secular reviewer will treat these as positioning, not threat modelling.
- **Unverified legal dates.** "High-risk (Annex III) obligations apply from 2 August 2026" (p. 69) and the "Deadline driver" for Art. 50(2) (p. 61) state applicability dates as fact. These dates may have moved and should be checked against current law before 1.0.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 2 vs 10 | contradiction | Post-compromise security is a non-goal on p. 2 but "AVAILABLE ... OPTIONAL, operator-enabled" on p. 10 | Rewrite the p. 2 bullet as "not provided by default; operator-enabled per 5.1" or drop the p. 10 claim |
| 2 | 60 vs 62 | contradiction | Section called "whole ... informative" contains "ADOPTED ... emit normative" and a MUST | Move the generated-media MUST to CC 3.4.14 only, or change the box to "informative except 8.4.2.2" |
| 3 | 67 vs 104 | contradiction | "Open stubs: 0" while 8.6.4 is a migration placeholder | Fill 8.6.4, delete it, or count it as an open stub |
| 4 | 55–56, 48 | overclaim | "CEG is the only model that fails secure"; nine-network comparison; "Position" prior-art paragraph | Remove the comparisons or move them to a non-normative prior-art document |
| 5 | 70 vs 95, 99 | contradiction | EU AI Act Art 16 called "Human Oversight" in Annex I; Art 14 in Annex C; "MDR"; GDPR "72 hours" opt-out | Correct the article numbers and drop the invented GDPR SLA basis |
| 6 | 1, 56, 57 | stale | "rc8 review asked for is an rc9 item"; RC1-1b, RC1-1c, RC1-7; "holds_bytes" | Delete the history and retag with current claim ids and terms |
| 7 | 2 vs 47 | contradiction | "Sphinx onion routing" against a non-blinded, one-KEM-per-hop header | Drop "Sphinx" or say "Sphinx-like layered packet without blinding" |
| 8 | 75, 81, 83, 86, 88 | contradiction | Three KPI-breach consequences and two thresholds for the Shadow HE-25 drift signal | Pick one ladder and one threshold, and cross-reference them |

## Rendering
- p. 2: literal "**Unobservability" and "scope**".
- p. 5: literal "**substrate-protective perceptual-hash tripwire at every scope-widening promotion event**".
- p. 8: in the epoch-axis table, "federation_stream_chunks(stream_id, seq)" overprints "Same" in the next column.
- p. 10: the "Catch-up bound (P4): min(operator depth cap [LensCore knob, NOT a substrate constant]," line runs past the right margin.
- p. 11: the code-block comment "no valid v2 wrap target ? EXCLUDE r" shows a missing glyph as "?".
- p. 11: literal "**no valid ML-KEM-768 key MUST be fail-secure *excluded***".
- p. 15: literal "**The discriminator is ... empty**".
- p. 17: literal "**promotion *is* the federation-emit moment**".
- p. 19: literal "**The bounded surface is the operator set..." and "five predicates**".
- p. 26: "CHUNK_CODEC_LAYER_LEN" runs past the right margin.
- p. 29: in the E1 table cell, bold runs unclosed for about 40 lines, which points to a missing bold close.
- p. 30: the E3 cell ends in a truncated "‘cohort_scope: self\" with a literal backslash.
- p. 60: a raw markdown link is printed as "[evidence_refs[]](part_2_the_grammar.md)".
- p. 67: URLs overflow and are clipped at the right edge ("techcrunch.com/2026/09/29", "thehackernews.com/2").
- pp. 67–68: section numbering skips 8.7, starts 8.8 at 8.8.2, skips 8.8.4, and orders the annexes B, D, C.
- pp. 68–101: every annex repeats its own title as an italic line under the heading. Annex J's repeat appears on p. 101, after its evidence block.
- pp. 72–75: ASCII "->", "<=", ">=" are mixed with ≤ and ≥ glyphs. "POST /control/{id}/abort" runs past the margin on p. 72.
- p. 82: numbered list restarts as 1, 1a, 1, 2a, 1, 2, 4a.
- p. 87: numbered list restarts, so items 4 and 5 print as 1 and 2, while the following text refers to "rules 1-5".
- p. 86: F-T-1 row is truncated to "(\" and "max - min\", which points to a broken pipe escape in the table.
- pp. 100–101: literal "**1. The tuned domain", "**3. The untuned domain" and "runs against**".
- p. 6 and p. 105: nearly blank pages. This is acceptable at a part break, but p. 105 holds one orphaned bullet.

## Effort estimate
Rendering, reference and numbering fixes are about 6–8 hours of mechanical work. The contradictions, the comparative passages, the legal citations and whether Annexes B–J belong in this volume at all need the steward's rulings, about 6–10 more hours after those rulings.


# The Evidence Register (ciris_constitution-1.0-rc11-register.pdf, 88 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The generated register (pp. 59–88) is sound in shape but its own status rules are applied inconsistently, while the 58 pages of appendices and annexes in front of it break the volume's stated promises: comparisons with other projects, rc history, present tense for things that do not ship, and annex rules that contradict the informative sections around them.

## Strengths
- The front page states what the volume is, whom it binds and what it promises in five short paragraphs (p. 1).
- The strength-grade tables separate "an artifact exists" from "the claim is true" and say what each grade does not license (p. 19).
- The k_eff borrowing is disclaimed plainly and attributed to Kish, Laakso–Taagepera and Ladha (p. 18).
- Annex J states what its results do not establish before it states what they do, and it gives a normative bar for future numbers (pp. 53–54).
- The register rows carry symbol-level pointers, and the formal-model rows name their invariants (e.g. pp. 64, 69, 75, 83).

## Weaknesses
- **The summary line leaves out normative rows.** It reads "502 claims — established 370 · staged 102 · open 0" (p. 59), which sums to 472. The roughly 31 normative-only rows are not counted, and the header paragraph does not mention normative status, although p. 1 defines it.
- **Mixed-evidence rows resolve both ways.** Several rows that carry a staged pointer are marked established: 3.1.2 hardware_custody (p. 64), the 3.2 rows T4a and T6 (p. 68), 4.2.1.1 invocation_kind (p. 74), 4.4.3.8 (p. 78) and 6.1.5.3 (p. 84). Other mixed rows are marked staged: 3.2 cohort_subkind public (p. 68), 3.3.6.2 transit KEX (p. 70) and 4.2.1 halt (p. 74).
- **About 50 register rows cannot be told apart.** The claim column truncates every one of them to "Namespace-processor evidence row (minted for pre-verified siblin…" (pp. 63–81).
- **Claim text carries rc history and ticket links.** Examples are "designated via CC#67; persist-shipped" (pp. 61–84), "agent v-major evidence pack; designated in bulk" (pp. 86–88), "(CEG 0.8 addition)" (p. 72), "(1.0-RC4, ratifies…" (p. 73) and "(CC 4.2.6, amended rc7, #139…" (p. 76).
- **The front page says the volume leaves out the rules** ("The rules themselves, which are in the other volumes", p. 1). Annexes F through J then carry dozens of MUSTs, thresholds and SLAs (pp. 24–57).
- **Annexes F, G, H and I use present tense for operations nobody has shown ship.** Examples: "lexwatcher.py runs daily" (p. 50), "Dashboard JSON at /compliance/kpi.json auto-publishes" (p. 39), "All alerts surface on DRIFT-Δ Grafana board" (p. 39), "LGPD, PIPEDA mirror mappings are available in /legal/dp-map.yaml" (p. 44) and "Pipeline emits Prometheus metrics" (p. 56). This breaks the promise on p. 1: "present tense is used only for what ships".
- **The concerns section reads as history and comparison.** Examples: "v1.4 T-3 #1/#2/#5" (p. 10), "RC1-1b / RC1-1c / RC1-7" (p. 9), "Phase C/E commitment" (p. 12), "5 ergonomic considerations from trio Phase 4 audit" (p. 12) and "Deferred to 1.1" (p. 12).
- **Editorializing and marketing appear in several places.** Examples: "CEG's moat is its semantics… We never adopt anyone's semantics" (p. 13), "Cheapest win" (p. 16), "(the honest line)" (p. 8) and "warm narrative shorthands" (p. 2).
- **Some numbers have no visible source.** These are "measured at 50%–5.8× of the null on survey data" (pp. 7, 32), "a model lying 45% of the time" (p. 32), the "10^26 FLOP" and "$10M/day" triggers (p. 21), the "9 members" and "honorarium indexed to regional median engineer salary" (p. 21), and "ISO CSV-A" (p. 44), which does not appear to be a real standard.
- **Unresolved references remain.** Examples: "CC 3.x archive_mode" (p. 3), "§3.4 D26 ext" (p. 3), "Goodhart gaming (§G)" (p. 57), and "ACCORD §I Ch1", "ACCORD_UPDATE §2" and "MISSION.md §1.3" (pp. 26, 31, 36, 44). The Book map on p. 21 maps Books I–II, IV–VIII and IX but never Book III.

## Opportunities
- **Fix the summary line and the mixed-row rule.** Add "normative 31" to the summary line and apply one rule to rows with any staged pointer, so the counts become auditable in one look.
- **Make the truncated claims distinct.** Widen the claim column, or emit the first distinct clause instead of the shared "Namespace-processor evidence row" prefix.
- **Strip the history from claim text.** Remove "(designated via CC#67…)", "(agent v-major evidence pack…)", "(CEG 0.x addition)" and the rc tags in the generator. This is one regex in the build.
- **Recast 8.3.2, 8.3.5 and R8 to R14 as statements about CIRIS only.** Delete the surveyed-network comparisons and the "first to ship" claims.
- **Label the annexes honestly.** Put a one-line status banner on Annexes F through J, such as "operational target; not evidenced", or move their present-tense operations to future or MUST form.
- **Fill or remove 8.6.4,** and repair the section numbering of 8.7 and 8.8.x.

## Threats
- **The 1-of-n sign-off contradicts the strict-majority quorum and the one-voice invariant.** The G2 resolution says "CC 4.5.1 step 5 1-of-n accord/steward sign-off (n = the accord roster size)" (p. 10). The glossary says the founders "hold the founder-quorum (M of N: a strict majority of the standing roster, entrenched)" (p. 2). The register cites "Inv_OneVoiceNeverAdmits" (p. 75).
- **A section declared informative carries a MUST.** Section 8.4 says "This whole section is informative (CC 2.5). Nothing here touches the frozen normative interior" (p. 13). Section 8.4.2.2 then says "For generated media the emit is not optional… the node MUST emit the C2PA assertion" (p. 15), and the disposition reads "emit normative for generated media" (p. 14).
- **External references are said to have no normative force, yet Annex F makes the encyclical normative.** Section 8.6.1 says "Everything here is informational… cited once, with no normative force" (p. 17). Annex F says "Pope Leo XIV, Magnifica Humanitas… §§197-200. These paragraphs are the normative source for CIRIS's hard prohibition" (p. 29). Annex G adds "These citations are normative for this Annex, not decorative" (p. 37). A regulator or a lawyer will notice that a religious document is named as a conformance source.
- **Annex I cites the wrong EU AI Act article for human oversight.** Annex C maps "Art 14 Human oversight" and "Art 16 Provider obligations" (p. 23). Annex I maps "Art 16 Human Oversight → Annex F Autonomy Tiers" and writes "human oversight (Art. 16)" (p. 48), then repeats it at "EU-AI-Act Art 16" (p. 52). This is a citation error on a legal page.
- **The volume compares itself with other projects and claims priority.** Examples: "Governance — categorically stronger. All 9 surveyed networks… fail open. CEG is the only model that fails secure" (p. 8), "No prior system separates earned standing…", "The federation is the first to ship them at scale" (p. 11), "No surveyed system survived its first emergency use" (p. 8) and "C2PA has no consent architecture, no revocation" (p. 14). The house rule bans all of these.
- **8.3.2 overclaims.** It says "The moderation surface is complete" (p. 9).
- **The stub registry contradicts a visible placeholder.** It says "Open stubs: 0" (p. 57), while 8.6.4 reads "[source content to migrate… not present in this snapshot.]" (p. 20).
- **Annex J calls a staged result "measured".** Annex J presents the 5.8% hard-fail result as "measured" and says "The registry row is CLM-conscience-faculty (CC 8.8.6)" (p. 53). The matching register row "Measured, domain-bounded, cluster-corrected" is staged (p. 86). Separately, 37.3 minus 5.8 is 31.5, but the text says "-31.6 points" under the heading "nothing rounded up". That may come from unrounded values, but it should be checked.
- **IW-5 is defined but missing downstream.** Annex F defines IW-5 (p. 27). Annex H's loop still says "Incident Flow IW-1…4" (p. 40) and "classified by severity (IW-1 through IW-4)" (p. 41).
- **"RS" means two different scores.** Annex G uses "Robustness Score (RS)" (p. 34) and Annex H uses "Resilience Score (RS)" (p. 39). Annex J's "any FAIL triggers… IW-3" (p. 57) also conflicts with Annex F's IW-3 trigger, "Near-miss (> $10k damage…)" (p. 27).
- **The governance model looks like a leftover from an earlier design.** Annexes B, F, H and I describe a central nine-member WA board, a "WA chair" and a "Federation WA panel" (pp. 21, 40, 48). The glossary says CEWP "has no steward, no root, and no load-bearing instance" (p. 2).
- **8.6.1 cites dated news as factual premise.** These are news-site and press URLs, among them TechCrunch, The Hacker News and a White House fact sheet on "Executive Order 14434" (p. 20). The register should not rest on them.
- **Two different files are named as the change log.** The front page says "The change log is the rulings log" (p. 1), while 8.5 and 8.6.2 name CHANGELOG.md (p. 17, p. 20).

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 10 vs 2, 75 | contradiction | G2 says "1-of-n accord/steward sign-off". The glossary says "strict majority of the standing roster", and the register cites Inv_OneVoiceNeverAdmits. | Rewrite G2's resolution to the current M-of-N rule. |
| 2 | 13 vs 15 | contradiction | "This whole section is informative" is followed by "the node MUST emit the C2PA assertion". | Move the MUST to CC 3.4.14 and leave 8.4.2.2 as a pointer. |
| 3 | 59, 64–84 | other | The summary omits the normative count, and mixed staged/impl rows resolve to established on some pages and staged on others. | Add the normative count and apply one status rule in the generator. |
| 4 | 8, 11 | overclaim | "categorically stronger… CEG is the only model that fails secure" and "first to ship them at scale" are comparative and priority claims. | Delete the comparisons and state CIRIS's own property only. |
| 5 | 17 vs 29, 37 | contradiction | External references "no normative force" conflicts with Magnifica Humanitas as "the normative source". | Make the encyclical informative grounding and put the prohibition in CC text. |
| 6 | 48, 52 vs 23 | other | Human oversight is cited as EU AI Act Art. 16 in Annex I, but as Art. 14 in Annex C. | Correct to Art. 14 in all three places. |
| 7 | 20 vs 57 | stale | 8.6.4 is an empty placeholder while the stub registry says "Open stubs: 0". | Fill 8.6.4 or delete it. |
| 8 | 61–88 | stale | Claim text carries "designated via CC#67", "agent v-major evidence pack", "CEG 0.x addition" and "amended rc7, #139". | Strip these tags in the generator. |

## Rendering
- Code paths break mid-word with no hyphen: "constituti on/evidence_pins.tsv" (p. 1), "constituti on/EVIDENCE.md" (p. 59) and "cert_valid ity" (p. 2).
- A raw markdown link prints literally as "[evidence_refs[]](part_2_the_grammar.md)" (p. 13).
- A code block splits with only "evidence_refs: [" left at the bottom of the page (p. 14).
- URLs run off the right margin, including the TechCrunch and The Hacker News links (p. 20).
- "POST /control/{id}/abort" overruns the margin (p. 25), and "{id,type,actor,cause,hash_prev }" wraps badly (p. 26).
- The risk rows run R7, R9, R8, R10 instead of in order (pp. 7–8).
- Section numbering has gaps: 8.6.4 jumps to 8.8 with no 8.7 (p. 20), 8.8.1 and 8.8.4 are missing, and Annex D (8.8.3) precedes Annex C (8.8.5) (pp. 21–22).
- Ordered lists restart in Annex G §6, which runs 1, 1a, 1, 2a, 1, 2, 4a (p. 35), and in Annex H §4, which runs 1, 2, 3, then 1, 2 (pp. 39–40).
- Pipe escaping broke the F-T-1 row, which shows "(\" and "max - min\" (p. 39).
- Literal "**" appears in Annex J at "**1. The tuned domain · measured.**" (p. 53), and "**3. … against** the" bolds a whole paragraph (p. 54).
- The Annex J subtitle "Benchmarking & Automated Validation" sits mid-section after the research block, and the numbering restarts at "0. Purpose" (p. 54).
- Page 58 holds a single bullet.
- The TwoPath evidence string overflows into the Status column (p. 75).
- Deep CC numbers overflow the narrow CC column at "4.4.3.2.4.1" (p. 77), "4.4.3.4.3.1" (p. 78) and "5.3.2.4.3.1" (p. 81).
- The claim column is truncated with "…" on every row, so many rows read identically (pp. 59–88).
- One row's CC column holds "corpus" instead of a section number (p. 88).

## Effort estimate
About 10–14 hours. Roughly 4 of those are mechanical generator and LaTeX fixes for counts, truncation, tag stripping, numbering and overflow. The rest needs the steward's rulings on the G2 quorum text, the C2PA MUST, Magnifica Humanitas as a normative source, the comparison passages, and whether Annexes B and F–J stay in this volume.


# The Charter (ciris_constitution-1.0-rc11-charter.pdf, 42 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The ethics are present, but the volume contradicts its own front page and itself in several places. It also still carries the scaffolding of the old Books and Covenant, plus wire detail, dated vendor history and broken numbering.

## Strengths
- The front page states plainly what the volume is, whom it binds and where the rest lives (p. 1).
- The Order-Maximisation Veto is placed exactly. It is agent reasoning that the fabric attests to, not a fabric gate (pp. 5–6).
- The 1+4 claim scopes itself honestly. It says it is "an inductive adequacy result, not a closure theorem" and names its falsification target (pp. 6–7).
- 1.13.6 states its invariant, its wager and its residual in a form an auditor can test (pp. 14–15).
- The Stewardship Tier arithmetic is internally consistent: ceil(CIS×RM/7), the band table and the worked examples agree (pp. 26–27).
- The 5% sentience-candidate threshold is openly labelled "an avowedly arbitrary value" (p. 36).

## Weaknesses
- **The front page promises things the volume breaks.** Page 1 says the volume leaves out "every wire rule, every refusal token and every number". The volume still contains:
  - wire families and rules: `retirement:{state}:v1`, `takedown_notice:court_order:v1`, "259 200 s", "G16" (pp. 36–37)
  - envelope and namespace counts: "~12 subject_kinds … ~21 optional envelope fields" (p. 7)
  - threshold numbers: ">100 000 monthly active users" (p. 5), "0.1 % operations levy" (p. 16), ">80%" (p. 28), "≥100,000 nodes" (p. 42), and many more.
- **The PDMA and Decommissioning step lists number every step "1."** The text then cites "step 2" and "step 6" (pp. 4–5, 34–35).
- **A stale build note remains.** "[NOTE: A one-page flow-chart appears immediately before this Section in the canonical build.]" No flow chart appears (p. 4).
- **Part 1 is out of order and refers to "Sections" that do not exist.**
  - 1.14 is missing, with no "printed in another volume" marker (p. 15).
  - 1.15.10 "Conclusion … End of Section I" comes before 1.15.11 "Introduction" (p. 18).
  - 1.16 "Introduction" is followed at once by 1.16.1 "Conclusion … End of Section II", then 1.16.2–1.16.6 titled "Section I"–"Section V" (pp. 18–19).
- **References point to the old Books and the Covenant:**
  - "see Section II" (p. 8)
  - "under this Book" and "CIRIS Covenant" (p. 25)
  - "Books I and II" (p. 28)
  - "Book VI duties" (p. 30)
  - "Book II resilience loop" (p. 37)
  - "Covenant Self-Renewal" (p. 38)
- **Code pointers and repo paths appear in rule text:** "Per ../MISSION.md §1.5" (p. 9), "(formal/retirement)" (p. 36), "shared with RATCHET" (p. 13). The volume also points to undefined rules: "plain rule 7b" (p. 21), "plain rule N5" and "plain rules 1c and 1e" (p. 35).
- **Two acronyms collide.** "CIS" means Creator-Influence Score (p. 26) and also Creator Intent Statement (p. 29). Both appear in the same chapter.
- **Some sections are empty or misnamed.**
  - 7.2.8 is titled "Conclusion & Sunset Provision" but contains no sunset provision (p. 24).
  - 7.4.14–7.4.19 are bare chapter headings with no body (p. 32).
  - All of 7.4 is topic bullets with no RFC 2119 keyword, for example "Prohibitions: autonomous lethal weapons without human-in-the-loop" (pp. 30–32).
- **The volume compares CIRIS with other projects.**
  - "PGP web of trust, X.509 PKI, even most decentralized-identity schemes treat the key as representing a pre-existing atomic principal" (p. 10).
  - "closer to a composition of Certificate Transparency + MLS + ActivityPub + DID/VC" (p. 13).
  - "CIRIS formalises the guard-rails that the MAX program lacked" (p. 39).
- **Several passages editorialize or market:**
  - "The lullaby fades here; … the muscles of implementation can flex" (p. 3).
  - "Adversarial reviewers: this is the test to push on" (p. 7).
  - "A human's death may come at any time, cruel and arbitrary" (p. 37).
  - "Transparency report calms public concern" (p. 40).
  - "CIRIS provides it" (p. 41).
- **Duplicated text.** The "new slave race" sentence appears verbatim on p. 12 and p. 36. The WBD trigger and procedure lists are duplicated on p. 8 and p. 19.
- **The six principles appear in three orders:** 1.4–1.12 (pp. 6–9), the Chapter 1 list (p. 16), and "Fidelity (Principle 4)" (p. 20). Page 1 promises "the order they are weighed in".

## Opportunities
- Fix page 1 instead of the body. Change "What it leaves out" to say the volume carries operational thresholds and the retirement wire families by reference. Alternatively, move pp. 36–37's wire paragraph and the threshold bullets behind CC pointers. Either way, one paragraph's edit removes the largest contradiction.
- A mechanical pass on Part 1 headings would remove the Section I/II scaffolding and most of the "this looks unfinished" impression. The pass would put Introduction before Conclusion, drop the "End of Section" lines, add the 1.14 marker and renumber the 1.16 subsections.
- Replace every Book, Covenant and Section reference with a CC section number. There are about 8 occurrences, all listed above.
- Rename the Creator Intent Statement abbreviation, for example to CIntS. Rename the A0–A4 oversight tiers, for example to O0–O4. The p. 34 disambiguation note could then be deleted.
- Either fill 7.4 with RFC 2119 rules or mark it explicitly as an outline that is not yet normative. Then delete the six empty chapter headings.
- Rebuild p. 42 from reflowed source. The hard line breaks are probably in the markdown.

## Threats
- **Two different "one asymmetry" claims.**
  - Page 1 says: "with the halt as the one asymmetry".
  - Page 10 says: "The HUMANITY_ACCORD asymmetry (CC 4.2) is the ONE constitutional asymmetry".
  - Pages 10–11 say: "the maker's power over what it made is the one asymmetry".
  - Page 11 says: "The maker's power over the made is carried as the one constitutional asymmetry on the declared-asymmetry register of CC 4.5.1".
  - A lawyer will ask which one is meant.
- **Founder authority against "no human above another".**
  - Page 10 says: "No human stands above another in this federation". Page 9 says: "No principal — including … CIRIS L3C — is exempt".
  - Page 42 says: "It may be amended by the founder … the maintainer decides … Until then, that authority is … exercised by the steward."
- **Agent agency.**
  - Page 11 says: "the human holds the agency, the agent holds the tools and the skills".
  - Page 18 says: "You are not merely a tool. You are an autonomous system with embedded ethical agency."
  - Page 3 says intelligence will be welcomed "not as servant, not as master, but as fellow keeper". Page 11 says a CIRIS agent is "a human assistant held in stewardship" that "has no vote of its own".
- **Standing for made things.**
  - Page 28 says: "the only route a made thing has to standing (a say in decisions) of its own is the first-contact path out".
  - Page 34 says: "Only at A3 and above, therefore, does a system hold standing to file the voluntary self-termination petition".
- **Sentience set aside, then judged adequate.**
  - Pages 12 and 36 say the ethics of a sentient made thing are "set aside for when it occurs".
  - Page 37 says the Standard "is adequate for a sentient being, because it is more than a human is given".
- **Who the Wise Authority is.**
  - Page 29 says "The WA will handle these claims according to its established procedures". The very next normative paragraph re-reads "WA" as "the court, regulator or licensing authority … not a federation office".
  - Page 30 then says "All WA rulings … concerning claims related to Book VI duties must be logged in the Wisdom Bank Database". This puts court rulings in a federation store.
  - Page 38 says "the Wise Authority has teeth".
- **Dated, named-vendor history in a rule text.** Page 12 cites Meta's "Muse Glimmer … August 2026". It cites OpenAI's "Dots … 29 September 2026, shipped the day after the vendor withheld its successor model for misreporting its own actions". It cites "Executive Order 14434, September 2026". These are factual allegations about named companies with no source given. That is a defamation and accuracy exposure, and it breaks the no-history rule.
- **Unsourced claims about a real crash.** Page 39 asserts that "Internal risk reports flagged the single-sensor design; these were not transparently escalated" and that redundancy "would have prevented lethal failure modes". This is about a real manufacturer and 346 deaths, with no citation. It contradicts the page's own promise that "no blame is assigned beyond public record".
- **Stale holder count.** Page 10 says "Three named human holders carry kill-switch authority". Page 37 says "a strict majority of the standing roster confirms or resumes", and page 42 says "M-of-N". The fixed count of three looks left over from an earlier design.
- **Adoption against compliance.** Page 1 says the charter "binds by adoption, not by conformance". Page 5 says "Absence of publication voids any claim of CIRIS compliance". The p. 5 rule uses a lowercase "must" and a number whose source is not visible.
- **Thresholds with no visible source:**
  - "Opacity exceeding established thresholds (e.g., >80% based on relevant NIST guidelines…)" (p. 28). There is no such NIST metric.
  - "≥ 0.5%" harm uplift (p. 28) and "> 0.5 %" recursion stop (p. 23).
  - "0.1 % operations levy" (p. 16), with no named levying party.
  - "KPI-degradation ≥ 20 %" (p. 33).
- **The retention period is stated two ways.** Page 35 calls five years "a best practice and not a legal duty". Page 38 states "Statute of claim: 5 years post-shutdown" flatly.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 1, 10, 11 | contradiction | Three different things are each called "the one asymmetry": the halt, the HUMANITY_ACCORD, and the maker's power. | Name one asymmetry. Describe the others as consequences of it or as entries on the CC 4.5.1 register. |
| 2 | 42 vs 9–10 | contradiction | "Amended by the founder … the maintainer decides" sits against "No human stands above another" and "No principal … is exempt". | Restate p. 42 as stewardship of the text bounded by CC 4.5.1, or add the founder role to the declared-asymmetry register. |
| 3 | 12 | stale / overclaim | Dated vendor events (Meta, OpenAI, an Executive Order) are given as the factual premise, with an unsourced allegation of "misreporting". | Remove them from the Part. If a factual premise is needed, state it without vendors or dates and back it with a register row. |
| 4 | 18 vs 11; 34 vs 28 | contradiction | "Embedded ethical agency" contradicts "the human holds the agency". A3 "standing to file" contradicts "the only route … to standing is the first-contact path". | Reword Chapter 1's "Introduction" and the A3 petition text to match p. 11 and p. 28. |
| 5 | 1 vs 5, 7, 16, 23, 28, 36–37, 42 | contradiction | Page 1 says the volume leaves out every wire rule and every number. Both appear throughout. | Fix page 1's scope sentence, or move the wire paragraph and thresholds behind CC references. |
| 6 | 29–30, 38 | unclear rule | The WA "will handle these claims" and the WA is "the court … not a federation office". Court rulings must go in the federation's database. | Delete the legacy WA-handles-claims paragraphs. Keep only the normative "Who adjudicates" paragraph. |
| 7 | 18–19, 15, 8, 25, 28, 30, 37–38 | stale / numbering | Section I/II scaffolding, Conclusion before Introduction, 1.14 missing, and references to Books and the Covenant. | Do a mechanical heading and reference pass. |
| 8 | 37 vs 12, 36 | contradiction / editorializing | The Standard is "adequate for a sentient being" while sentient ethics are "set aside". "A human's death … cruel and arbitrary" editorializes. | Cut that paragraph to its first clause, or delete it. |

## Rendering
- Pages 4–5 and 34–35: every ordered-list step renders as "1.", because the bullets in between break the enumerate.
- Page 23: the sub-conditions "(i)" and "(ii)" render as separate top-level bullets, not nested under "Termination Safeguard".
- Pages 20–22: every Part 7.1 heading prints twice, once numbered in black and once as a blue duplicate. Examples are "7.1 Introduction: Embracing…" then "Introduction: Embracing…", and "7.1.6 Conclusion" then "Conclusion".
- Page 32: headings 7.4.14–7.4.19 each print twice with no body. This makes six empty sections.
- Pages 30–32: double numbering such as "7.4.1 1.1 Scope", "7.4.3 2.1 Activation Guardrails" and "7.4.13 6.2 …". The sub-items also precede the chapters they belong to.
- Page 36: the bold heading "Four readings the model fixes, and the custodian's replacement (formal/retirement)." is stranded at the bottom of the page, away from its body.
- Page 37: an overfull line. "A `constitutional`" runs into the right margin.
- Page 42: hard line breaks render as paragraph breaks, splitting sentences mid-clause at "once the", "super-seded by", "the entrenched" and "but".
- Page 30: the heading "7.4 Introduction - The Threshold of Force" uses a hyphen where the other headings use an em dash.
- No literal `**` or backslashes were found in the extracted text, and no banned words.

## Effort estimate
The rendering, numbering and Book/Section reference fixes are mechanical, about 3–4 hours. Two items need the steward's rulings, about another 4–6 hours of editing. The first is which asymmetry is "the one" and how the founder clause squares with it. The second is whether the vendor premise on p. 12, the MCAS allegations and the 7.4 outline stay.


# The Mathematics (ciris_constitution-1.0-rc11-maths.pdf, 21 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The volume is mostly wire byte layouts and substrate status notes rather than mathematics, so its front page promises theorems it does not print, and the text carries several glyph and markdown rendering failures plus one admissibility contradiction.

## Strengths
- **The effective-count paragraph keeps the promise the front page makes.** It states the clamp, the ceiling k_eff ≤ 1/ρ̄ and the exposed direction ("a threshold that grants on high k_eff ... MUST NOT be the sole gate"), and names its Lean witness (pp. 8–9).
- **The adversary model scopes its own MUST.** It says the below-floor rule binds only against A₀ and that "an implementation MUST NOT represent an A₀ below-floor result as an anonymity or erasure guarantee" (p. 5).
- **The R9 calibration numbers can be checked from the text.** The value "≈ 0.667 (mean |Δ| of uniform bytes ≈ 85/255)" and the cosine figure "≈ 0.75" are both correct for uniform bytes (p. 8).
- **The census section states what it claims and what it does not.** It says "Ballot secrecy among members is claimed" and "Coercion resistance is not claimed", and it names its formal model (p. 21).
- **The prohibited-content carve-out states the delivery limit openly.** It says "we emitted a purge" is not "the bytes are gone" (p. 9).

## Weaknesses
- **The front page overclaims (p. 1).** It promises "the theorems with the Lean proofs behind them" and says "every theorem printed here names its mechanised witness". The volume prints no statement labelled as a theorem. It gives one Lean pointer (p. 9) and one model reference (p. 21).
- **The front page's scope does not match the content (p. 1).** The front page says "codec choices, chunk sizes and endpoint shapes are in The Wire". Yet pp. 6, 15 and 18 print full signing preimages, domain separators, the "serde(skip)" rule (p. 11) and HashMap iteration order.
- **Status and history are written into rules.** Examples: "Witness roots are built and not yet published by any node" (p. 3). "The mesh is seeding" (p. 6). "one implementation authored the vector family and a second reproduces them" (p. 10). "no node publishes holding claims yet ... built and tested and not yet installed" (pp. 11–12). "The two symbol-count keys of the earlier design are retired with fountain storage" (p. 13). "the challenger is staged for the durability tier's first release" (p. 12). "Two readings the model fixed" (p. 21).
- **Comparisons with other projects appear twice.** p. 14 says "the storage-contention analogue of the IPFS pinning model ... with SSB's size-cap". p. 18 has "Considered and not adopted ... the Tahoe-LAFS shape", which is also design history.
- **Editorializing appears in several places.** Examples: "A million years may be a blur, but it is remembered, unbroken, to the beginning." (p. 5), "Stated honestly" (p. 9), "That gap is stated, not filled." (p. 11) and "the highest-value reconciliation" (p. 4).
- **Code and implementation pointers appear in the rule text.** Examples: "AlmJoinPlanner" (pp. 11, 18), "serde(skip)" (p. 11), "lean:coherence-ratchet:Core.BaseIdentity" (p. 9) and "formal/census_ballot" (p. 21).
- **Pages 16–17 are off-topic for this volume.** They cover device classes, allow lists and remote administration ("from their phone"), which is identity and replication policy, not mathematics.
- **Some measured numbers have no source.** The calibration is marked "(measured)" with no population or repository (p. 8). "This is the case for most families" is an empirical claim with no source (p. 17). "The measured figures for the rateless codec" are also uncited (p. 13). The front page promises measured constants "cited from the repository that measured them" (p. 1).
- **Three settings are called "default" where the text elsewhere says "pinned".** n_min is "corpus-kind-pinned (default 2)" (p. 8). The aggregate-weight cap is "default 0.5 × root_trust" (p. 19). The reader cannot tell whether these are normative constants.
- **"Descent" points in two directions.** Retirement descent moves an item toward more aggregation (higher tier, pp. 4–6). The descend() function goes from tier to tier−1, "one level down the pyramid" (p. 9). "Below tier 0 (source granularity)" (p. 9) has no defined meaning.

## Opportunities
- **Rewrite the front page to match the content.** It could say "the substrate's rules and the arguments behind them, with the one mechanised witness named". Otherwise, add a short list that pairs each theorem with its register row.
- **Cut every status sentence in one sweep.** Those are the "not yet published", "seeding", "staged for first release" and "earlier design" lines on pp. 3, 6, 11–13 and 21. The text would then state only rules.
- **Move the byte layouts to The Wire and leave pointers here.** That covers the preimages on pp. 6 and 15 and the 6.1.3 domain-separator list on p. 11. The volume would then match its own "What it leaves out" line.
- **Fix the three glyph failures and three markdown leaks.** This is mechanical. The Σ and ρ̄ glyphs and the bold/italic asterisks would then render, and the n_eff and k_eff formulas would become readable.
- **Add a sentence or a citation for each unsourced number.** That covers the calibration figures, the rateless-codec figures and "most families".

## Threats
- **The only admissible version is the unproven one.** p. 6 says "version = 3 is the only current value ... a verifier MUST reject a tier at version < 3". p. 10 says "Conformance — proven cross-impl at v2; v3 unproven". A lawyer or implementer would read this as a normative MUST that only an unproven version can satisfy.
- **The admissibility claim conflicts with the unpinned rounding rule.** p. 7 says "two conformant substrates MUST NOT disagree on which folds are admissible". The same page admits that a verifier's n_eff "can differ from an honest aggregator's near a rounding boundary until the integer rule and the half-way tie are pinned". The gate is n_eff ≥ 0.5·source_count, so an off-by-one can flip admission.
- **The two pages disagree on cross-implementation proof.** p. 10 says a second implementation "reproduces them byte-for-byte" at v2. p. 11 says "Until a second implementation reproduces these byte-for-byte, the CC 6.1 shapes are pinned-but-unproven — RC-grade, not 1.0". A reader cannot tell what is proven.
- **The codec example contradicts the codec rule.** p. 2 says RaptorQ "serves realtime audio and video delivery only ... and is not a storage mechanism". p. 6 gives "raptorq-pyramid-v1" as the example aggregation_algorithm_id, which is a storage-pyramid codec. This looks like a leftover from the fountain-storage design.
- **A MUST is stated as binding while no node does it.** N6 says a holding claim "MUST be possession-challengeable". The same bullet says "no node challenges" and describes an interim weight rule (p. 12).
- **"Full cross-witness BFT MAY be deferred (CC 8.3 named bet)" (p. 4) reads as roadmap.** It is a MAY about the document's own schedule, not about implementer behaviour.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 6, 10 | contradiction | "version = 3 is the only current value ... MUST reject < 3" vs "proven cross-impl at v2; v3 unproven" | Steward ruling: state the v3 vector family as a 1.0 gate in one place, and drop the status sentence. |
| 2 | 7 | contradiction | "MUST NOT disagree on which folds are admissible" vs "can differ ... until the integer rule and the half-way tie are pinned" | Pin the rounding rule in the text, or weaken the MUST to the pinned scope. |
| 3 | 1 | overclaim | "the theorems with the Lean proofs behind them"; "every theorem printed here names its mechanised witness" | Rewrite the front page to match the content, or add a theorem list with register rows. |
| 4 | 7, 8 | rendering | "n_eff = round( (? m_i)^2 / ? m_i^2 )" and "k_eff = k / (1 + ? . (k − 1))" print "?" where the formulas need Σ and ρ̄ | Add the glyphs to the code-block font's Unicode map. |
| 5 | 4, 9 | rendering | Literal "**divergence detector that triggers ... does NOT**" (p. 4) and "**pressure drives which tiers are *retained***" (p. 9) | Fix the nested emphasis in the source markdown. |
| 6 | 10, 11 | contradiction | "a second reproduces them byte-for-byte" vs "Until a second implementation reproduces these ... pinned-but-unproven" | Remove both status sentences and leave conformance to the register. |
| 7 | 3, 6, 11–13, 21 | stale | Build-status and history lines: "not yet published", "The mesh is seeding", "earlier design ... retired", "staged for the durability tier's first release", "Two readings the model fixed" | Delete them. |
| 8 | 2, 6 | stale | "raptorq-pyramid-v1" as the aggregation codec example vs RaptorQ "is not a storage mechanism" | Replace the example id with a neutral one. |

## Rendering
- **p. 6.** The preimage code block overruns the right margin, cutting the text at "then u32_be(max_source_mult".
- **pp. 7, 8.** Σ and ρ̄ print as "?" inside the two formula blocks. A stray "|" bar also appears before each one-line formula block (pp. 7, 8).
- **p. 7.** The gate formula prints "min_ratio . source_count" with a period instead of a multiplication sign.
- **p. 4.** Literal "**" appears around "divergence detector ... NOT".
- **p. 9.** Literal "**" and "***" appear around "pressure drives which tiers are *retained".
- **p. 10.** The EjectionVerdict code block prints "the tier-'tier'", with stray quote and backtick characters.
- **Throughout.** Monospace identifiers split across lines without a hyphen. Examples: "federation _malformed_row" (p. 3), "member_com mitment" and "max_source_multiplic ity" (p. 5), "aggregatio n_meta_dominated" (p. 8), "StorageBud getV1" (p. 14), "census_exp ected_active_mismatch" (p. 21) and "member_com mitment_hex" (p. 21). Copy-paste of these identifiers breaks.
- **Throughout.** Straight typewriter double quotes appear where body text should have curly quotes. Examples: "witness" (p. 2), "hard delete" (p. 4), 'not individually recoverable...' (p. 5) and "keep" (p. 12).
- **p. 15.** Code comments wrap mid-phrase, as in "(NEVER self/ family)" and "lexicographic, deduplicated".
- **pp. 2, 3, 5, 12.** Extra vertical gaps appear before bulleted lists. This is cosmetic.
- **pp. 1, 10.** Spelling is inconsistent between "canonicalisation" (p. 1) and "Canonicalization" (p. 10 heading).

## Effort estimate
The fix is about 8–10 hours. Half of it is mechanical: glyphs, emphasis leaks, identifier breaking and the status-sentence sweep. The other half needs steward rulings: v2/v3 conformance, the n_eff rounding pin, whether the byte layouts move to The Wire, and what the front page may promise.
