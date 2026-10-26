# RC11 volume review — pass 5, a fourth model family (Gemini 4 Argon), 2026-10-25

**What this is.** The same brief, the nine volumes rebuilt at `3334fae` (after the pass-4 defaults R45, R57–R82 and M9–M14 landed), read by `google/gemini-4-argon` over OpenRouter, nine calls in parallel. Tool: `tools/review_volume_external.py --max-tokens 60000`. Reports: `review/notes/pass5_gemini/<volume>.md`.

**Cost and size.** 508,293 prompt tokens, 31,217 completion tokens, every call under 65 seconds; about $1.35 at the posted rates.

| Volume | Pages | Pass 1 | Pass 2 | Pass 3 (Grok) | Pass 4 (GPT) | Pass 5 (Gemini) |
|---|---|---|---|---|---|---|
| Charter | 40 | 4 | 5 | 4 | 5 | **3** |
| Constitution | 69 | 4 | 4 | 4 | 5 | **3** |
| Wire | 110 | 4 | 4 | 4 | 5 | **3** |
| Dictionary | 110 | 4 | 4 | 4 | 4 | **3** |
| Reader's Policies | 35 | 4 | 5 | 4 | 5 | **3** |
| Mathematics | 21 | 4 | 4 | 4 | 4 | **3** |
| Evidence Register | 131 | 4 | 4 | 4 | 5 | **3** |
| Threat Model | 48 | 4 | 4 | 4 | 5 | 4 |
| Digest | 35 | 5 | 4 | 4 | 4 | **3** |

First pass with any volume under 4, and the first read of the text after the pass-4 landing. Two readings are possible and both are partly true: the landing closed the layer GPT found (every one of its eight-per-volume top defects that was landed is absent from Gemini's lists), and Gemini is a more lenient grader whose effort estimates (3–8 hours per volume, 35–45 hours in all) are a quarter of GPT's. Its reports are the shortest of the four families, the most mechanical, and the most page-exact; it found fewer contradictions and more residue, and it caught three regressions that today's own edits introduced.

## What a fourth model family added

Checked against the source at `3334fae`.

**Regressions from today's edits, confirmed.**
- The charter cover now says "This volume does not use RFC 2119", and Part 1 still carries ten capitalised `MUST`s (1.3's MUST-abort, 1.13.6's durable-trace rules) plus a `SHOULD` in Part 7 (charter pp. 1, 5–6, 14–15, 33). The cover sentence overclaimed. → M15: the cover says the Charter's *duties* are plain imperatives and that a capital MUST in it quotes a rule whose home is another volume.
- 6.1.2.1 now reads "appended in version order … so the fields are appended in version order" (maths p. 6): the M12 edit left the clause it replaced. → M15.
- 5.3.3.2's transport table now says "no selective-forwarding relay role" while 5.3.3.2.1–.3 still design clear `codec_id` / `ChunkLayer` headers "so a relay drops by (codec_id, layer)" and 5.3.3.2.2 says "(direct Reticulum Links / SFU at scale)" (wire pp. 86–88, 90; threats pp. 24–25). The M10 edit removed the roadmap and exposed the older relay design beside it. → R87: under pull-only fan-out, the selector is the fetching node or the serving peer, never a relay; delete "/ SFU at scale" and reword the "relay drops" sentences.

**Confirmed, new in this pass.**
- The 7.3.5 intro still says creation duties are enforced by "a claims process the Wise Authority adjudicates after the fact" (charter p. 29), one page before the R27 jurisdiction rule. Grok flagged this in pass 3; R27's landing missed the intro sentence. → M15.
- 7.1.4 still carries a numbered "Prioritisation Heuristic" and 7.2.2 "default to Non-Maleficence Priority plus local optimisation" (charter pp. 22–23), beside R29/R45's "no ordering to apply, only constraints". → M15 (constraint checklist; "non-maleficence fail-safe").
- The autonomy table at 7.5.3.1 gives "surgery, weapons" as the A4 example (charter p. 32) two pages after 7.4's prohibition. The R21 cut of weapons reached Annex F's table and not this one. → M15.
- Part 3's community schema comment says `consensus_protocol // same six canonical kinds as family`, and the infrastructure rule reads as the only carve-out, while 4.5.13 refuses `founder_only` for every community above the family (constitution pp. 3, 9, 64, 68). → M15: the comment and the rule name the refusal for all communities.
- 4.5.13's protective default and outcome ladder allow approve-to-keep by "a steward's" signature only, while the mechanism paragraph lets "a moderator or steward" act and a steward is optional (constitution pp. 65–67). A moderator-only community could not keep falsely reported content. → M15: "a moderator's or steward's".
- `key:revocation:v1` is described in 2.4.1.1 as binding eight members including `revoked_key_id (string or null)`, `reason (string or null)` and `scrub_timestamp`, while 2.6.1.1.1 refuses explicit nulls and the signed-object table places `scrub_timestamp` beside the signature (wire pp. 23, 31, 57). → R88, persist: the signed-object data is the contract; 2.4.1.1's list follows it.
- `halt_fuse_secs` appears twice in the signed-object table, once under the persist-typed members and once under the untyped (wire pp. 42, 49). The data file has one row; the generator prints it in two categories. → M15, pipeline.
- The MLS Welcome's inviter signature is bare ML-DSA-65 "(no algorithm field)" where every other federation-tier signature is hybrid Ed25519 + ML-DSA-65 (threats pp. 18, 41). → R89, edge: state why the Welcome is single-primitive, or make it hybrid.
- 1.13.3.1's non-goal says group existence and churn are observable because `family_id` / `community_id` ride the envelope and `hard_case:*` events reach the log, while 5.4.6 says the cohort tiers exist to withhold "that the group exists at all" and the construction "hides the group's existence, membership and querier → invitee edges from outsiders" (threats pp. 2, 43–44). The signed-object data confirms `community_id` and `family_id` are required envelope members at their scopes. → R90, *steward*: which claim is the rule. Default: both, at their layers — an outsider never holds a cohort's envelopes, so the ids on them reveal nothing to it; what it can learn is the existence inference from traffic and from federation-tier `hard_case:*` events, which the non-goal names. 5.4.6 says "from an outsider who holds no envelope of the cohort" and points at the non-goal for the rest.
- `max_source_multiplicity` is a signed member of the census composite row while R66 says the multiplicity gate does not read the census (maths pp. 8, 20). → R91: pin the value the composite carries (the one-return-per-owner construction gives 1), or drop the member from the census row — persist's call on the data.
- The similarity graph's edge predicate (`≥ 950` or `> 950` in milli-units) and the fixed-point denominator of "1 − normalized L1" are not written out, in a section that calls any divergence "a fork in admissibility" (maths p. 8). → M15 if the vectors fix it; otherwise persist.
- "the small-community size" in the governance ratchet floor names no number and no section (maths p. 21); 4.5.13's policy table carries the count minimum. → M15: cite it.
- The register row `CLM-wa-board-asymmetry-declared` says the Wise Authority board "carries neither a bound nor an exit" and waits on Annex B, while Annex B §2 states staggered three-year terms with a two-term maximum and §9 removal by a two-thirds vote (register pp. 21, 108). → R92, *steward*: whether Annex B's bound and exit discharge the row. Default: not yet — Annex B is an operational target, not a wire object; the row cites §2 and §9 as the remedy's text and stays declared until the board's roster is a signed object.
- Seven register rows are `established` while their evidence cell still carries a `staged:` ticket (3.1.2, 3.2 ×2, 4.2.1.1, 4.4.3.8, 6.1.5.3 ×2). → M15, checker: a mixed row is either split or `staged`; `check_claims.py` enforces it.
- Eight legacy locators survive in the annexes ("Accord Addendum 1", "ACCORD_UPDATE §2", "ACCORD §I Ch1", "Section VI Ch3 Creator Ledger"), none mapped in 8.9 (register pp. 22, 31, 34, 39, 43–44, 52). → M15, with checker patterns.
- `Leviculum` appears twice in the Parts as an unnamed substrate (3.x line 1467, 5.4.6 line 852). Grok read it as "Levicium" and the pass-3 note wrongly said the token did not occur in the source; it does. → M15: name it as what it is (an onion-routing substrate extension of the node's transport) without the product name, or define it once.
- "(part_3 guardianship clause)" is printed as a raw file reference in 4.4.3.2.8 (policies p. 16); `AGENT_OCCURRENCE_ID env var` in 2.1; "[LensCore knob, NOT a substrate constant]" in 5.1; "`S4` default" in 2.6.1.1's example; "five public + one admin HTTP endpoint shape" in 5.3 against the dozen endpoints it then lists; lock tags "(normative: V1 lock)", "(normative: D2 / D3)", "P4" through Part 5; "[configurable; default 5 s]" in Annex F; "~75-80% transparent translation rate" in 4.x; "the pace of change is so great and the need so dire (ciris.ai/constitutional-mesh)" in 4.5.1; "Dual-emit … during a declared window" and the un-reminted-bundle exception in 4.2.1 and 3.2 (register says the v2 label is established, so the window is over); "the three kinds retire … until that amendment lands" in 3.3.9 (R16 keeps the kinds; the sentence can state the rule without the forecast). → M15, with the stale-reference checker gaining the lock-tag, legacy-locator and raw-path patterns.
- The digest cover still promises "what the alternatives do, promise by promise" (the status-quo memo R22 took out of the volume), and "one-page versions" for pieces of 5, 13, 4 and 12 pages; the pieces print "Source: review/…" lines; P00 keeps its rc8 and ruling-date history (digest pp. 1–2, 7, 20, 24–35). → M14/M15.
- G23 states the manager-side bypasses (`strategy: immediate` forces, `strategy: docker` restarts without asking, `/updates/retry` re-stages after a refusal) while 5g and the operator digest now say a refusal stands "[works today on the agent]" (digest pp. 4, 15, 21, 33). → M15: 5g and the operator digest carry the manager-side limit in the same bracket.

**Where the pass is wrong or lenient, checked.**
- `CLM-conscience-faculty` is in the register (section 8.8.10); the reviewer's "does not appear anywhere in the table" is a search miss.
- "Missing section 3.2" in the Dictionary: 3.2 prints in the Constitution volume by `pieces.tsv`; the Dictionary cover should say so (the same note the pass-3 Register cover needs). Mechanical, not a defect of the Part.
- The "polarity contradiction" on `age_assurance` is R53, already with persist.
- `graceful` in two test names is an evidence pointer into CIRISAgent, not CC prose (pass 3 said the same).
- The reviewer graded the volumes at 3 while listing, per volume, two to four items of the same kind GPT scored at 5. The grades are not comparable across families; the lists are.

## Rulings, pass 5 (R87–R92), and the mechanical set (M15)

| # | Where | The two sentences | Default |
|---|---|---|---|
| R87 | 5.3.3.2 vs 5.3.3.2.1–.3 | "no selective-forwarding relay role" vs clear `codec_id` / `ChunkLayer` "so a relay drops by (codec_id, layer)" and "SFU at scale" | Under pull-only fan-out the selector is the fetching node or the serving peer; the clear header exists so a fetch can ask for a layer; no relay, no SFU |
| R88 persist | 2.4.1.1 `key:revocation:v1` member list vs 2.6.1.1.1 and the signed-object table | eight members with nullable strings and `scrub_timestamp` inside vs no nulls, `scrub_timestamp` beside | The signed-object data is the contract; 2.4.1.1 lists what it says |
| R89 edge | 5.4.4 Welcome inviter signature vs the hybrid mandate | bare ML-DSA-65 vs Ed25519 + ML-DSA-65 everywhere else | Edge says why; the text then either states the exception as a rule or the signature becomes hybrid |
| R90 *steward* | 1.13.3.1 non-goal vs 5.4.6 | group existence observable (ids on the envelope, `hard_case:*` in the log) vs the cohort tiers withhold that the group exists | Both at their layers: an outsider holds no cohort envelope, so the ids reveal nothing to it; existence leaks through traffic and federation-tier events, which the non-goal names; 5.4.6 qualifies "from an outsider who holds no envelope of the cohort" |
| R91 persist | census composite members vs R66 | `max_source_multiplicity` signed on a row the multiplicity gate does not read | Carry 1 (one return per owner) or drop the member; persist's data |
| R92 *steward* | `CLM-wa-board-asymmetry-declared` vs Annex B §2, §9 | "neither a bound nor an exit" vs three-year terms, two-term maximum, two-thirds removal | The row cites §2 and §9 as the remedy's text and stays declared until the board's roster is a signed object |

**M15.** The charter cover's RFC 2119 sentence narrowed; the 6.1.2.1 tautology; the 7.3.5 intro; the 7.1.4 checklist and 7.2.2 "fail-safe"; "weapons" out of the 7.5.3.1 example; the community schema comment and the infrastructure rule naming `founder_only`'s refusal for all communities; "a moderator's or steward's approve-to-keep"; `halt_fuse_secs` printed once (generator); mixed register rows split or staged (checker); the eight legacy locators; `Leviculum` named for what it is; the raw-path, env-var, knob, "S4", endpoint-count, lock-tag, placeholder, translation-rate and "need so dire" residues; the cutover window and the bundle exception retired; 3.3.9 stated without the forecast; the Dictionary and Register covers naming the Part sections they do not carry; the digest cover's "alternatives" and "one-page"; the pieces' "Source:" lines; P00's history; 5g's manager-side bracket; the similarity edge predicate written out if the vectors fix it; the small-community size cited. Checker patterns to add: `\(normative: [A-Z]\d`, `V\d lock`, `Addendum 1`, `ACCORD_UPDATE`, `ACCORD §`, `Section VI Ch`, `part_\d `, `_env var`, `Closes G\d`, `\d+ stories`, `Per [A-Z]\w+ [A-Z]\w+'s`.

**Still open from earlier passes, not yet landed.** R48 and R49 (the 5.2 scope sentences and the "WHEN enabled" branch; Gemini and GPT both still see them), R52 (the Mathematics cover), R72 (the Threat Model cover; Gemini's first defect), R46/R47/R43/R53/R68 (persist), R74/R75/R77/R79 (to verify), R24 (persist #1121).

## Reading the five passes together

Four model families have now read the same nine volumes. Their lists converge on the same classes and differ on the grade: the in-house passes and Grok sat at 4, GPT at 5 and Gemini at 3 for text that is one landing apart. What moved between pass 4 and pass 5 is that no GPT top defect that was landed reappears; what did not move is the residue class, which no landing touches because no checker matches it yet. The checker patterns above are the cheapest next step, then R87–R92 with the two steward items, then the carried R48/R49/R52/R72, then a build and a sixth read by whichever family has not seen the text since its last landing.
