# The nine rc11 volumes, second pass (2026-10-25, rc11 head `aa953e8`)

Same brief, same method as `volume_swot_rc11_2026-10-25.md` (one reviewer per rendered PDF, whole
volume read, SWOT with page-referenced defects, care 1–5), run fresh with no sight of the first pass,
on the volumes rebuilt after the renderer, generator, heading-structure and code-re-indent work and
after the first rulings (R1 the halt as the condition of symmetry, R2 the scale gate and the steward
of the text, R3 one voice never decides who is in a room, R22 the vendor premise, R23 the adequacy
claim, the withdrawn maturity premise, the stance). The nine sheets follow the synthesis verbatim.

## Scores, pass 1 → pass 2

| Volume | Pages | Pass 1 | Pass 2 | What moved |
|---|---|---|---|---|
| Charter | 43 | 4 | **5** | Rendering noise gone; the reviewer now reads the content and finds the cover's "no number, no wire rule" promise broken on a dozen pages, the agent-identity sentences of the Covenant books against the 1.13.2 stance, three CRE triggers, the 7.3.5 jurisdiction page, A3 "standing to file" |
| Policies | 34 | 4 | **5** | Same effect: with the pseudocode readable, the Option A / community-encryption / Policy A-mean contradictions carry the score, plus ~15 "S8.1.x" pointers and the "(LIVE)" heading |
| Digest | 35 | 5 | 4 | Competitor memo and P00 history out; what remains is the P00 register rows (commit hashes, ruling dates) and three "the asymmetry" remnants the R1 sweep missed |
| Constitution | 69 | 4 | 4 | Halt "2-of-3 verifier" (R7), moderator window (R4), harm-removal-by-silence vs the floor (new), subkind count, H3 resolution; comparisons and pointers |
| Wire | 110 | 4 | 4 | PCS both ways (R20), cover's "fixed-size envelope", K_record_id derivation, base64 alphabet (R8–R9 family), receipt endianness, "0.x Public Working Draft" versioning text |
| Dictionary | 109 | 4 | 4 | Membership-by-supersede (R13), age-band shape (R14), Goal scales, licensure-by-quorum leftover, accord leaf set; a renderer regression (doubled underscores) |
| Register | 115 | 4 | 4 | Rows "established" whose text says pending; ~40 garbled generated claims; encyclical as normative source (R18); Art 14/16 |
| Threats | 105 | 4 | 4 | Adversary table overstates two mitigations that ship off; PCS; A/V framing; A4 lethal authorization; all of Part 8 printed (R21) |
| Maths | 21 | 4 | 4 | Cover vs content; v2/v3 conformance (R17); "nothing is ever forgotten" vs "exactly 0"; fountain leftovers |

The scores did not fall because the scale measures the text, and the first pass could not see the
text past the renderer. Two volumes went up for exactly that reason. The mechanical work did what it
was for: the second pass contains almost no rendering findings that are not regressions from the
first-pass fixes (below), and every reviewer now spends its findings on rules.

## Regressions from the first-pass fixes (mine; fix first)

1. **Doubled underscores** in identifiers set in prose and headings (`subject__kind`, `HUMANITY__ACCORD`, `community__feed`) — Dictionary pp. 40–56, 74; Policies pp. 2, 17, 26; Charter pp. 10–11, 37–38. The new separator-aware `breakable()` and `esc()` both touch `_`.
2. **Literal `\|` in prose** outside tables (Dictionary pp. 48, 64; Policies p. 7; Constitution p. 31): the table-cell fix did not reach `inline()` for paragraphs.
3. Wire p. 11: the `witness_quorum` cell is cut at "MUST equal ⌊" — a `⌊…⌋` formula inside a table cell.
4. STEWARDSHIP.md's hard-wrapped source renders as forced line breaks on the Charter's last page.
5. Policies p. 33 and several Wire/Dictionary lines still clip at the right margin inside inline code.

## Mechanical, under rulings already made (no new decision)

- **R1 remnants**: "the asymmetry" at plain 4e, the operator digest and the G7 subject line; "it is immature and lacks wisdom" (1.13.2 and the guarantees piece) → the kind/accountability reason; the vendor anecdote still printed in the plain rules (p. 10) → the neutral premise.
- **R7 (M of N)**: Constitution p. 37 "2-of-3 multi-sig verifier … quorum:2/3" and the p. 8 CEG table row; Register p. 77 "every later change is 2-of-3"; plain C1 "one of six named holders, any of whom can veto", "two-of-three ratification"; "the HUMANITY_ACCORD triple" ×4.
- **R22 remnants**: the Register's 8.6.1 is the sourced record by design; the Digest p. 10 anecdote is not.
- **3.1.9.7 (Goal scales)**: Dictionary p. 39 "self, cohort and federation" vs the seven-token list — the ruled list wins.
- **No authority rosters**: Dictionary p. 2 "authority is conferred by quorum, never by delegates_to" is the roster leftover; Policies F/J "registry-steward-triple key … binds CIRIS L3C" (R12 default).
- **RaptorQ = A/V only**: "raptorq-pyramid-v1" as the storage aggregation id, "symbol count" sentences (Maths pp. 4, 6, 10), "fountain plane" (Wire p. 47).
- **Anonymous tier is planned**: Threats p. 5 "every node relays onion traffic unless it opts out" reads as shipped; one clause.
- **Wire cover**: "a fixed-size substrate envelope" was withdrawn with the universal-envelope rule; the cover must say "fixed-size frames on a shaped link".
- **Covers carry rc history**: Policies p. 1 "is an rc9 item", Threats p. 1 "the rc8 review asked for is an rc9 item".
- **8.6.4** is a migration placeholder while 8.9 says "Open stubs: 0".
- **Register**: rows marked established whose text says "pending" / "does not yet publish" (2.6.1.3, 3.4.5) — demote and add the checker rule; ~40 generated claim texts are garbled slugs ("…entr accord", "calibratio manifold", "corpus" as a CC number); a banned word ("graceful shutdown") in one claim; "WBD" = two expansions; Annex I Art 16 → Art 14; "as of rc5".
- **The stale-reference sweep** (first-pass items 11–17): "S<n>.<n>", "CEG §", "§3.4 D26", "Book / Section / Covenant", "Option A/B", "Phase C/E", "RC1-1b", "v1.4 T-3", MISSION.md / FSD / .py / .rs pointers, "AV-nn / F-AV-* / OQ-n / P4 / P8 / G3 / R1/Q1 / D08 / Piece n / §Q", "(LIVE)", "deprecated / legacy / already-rejected / next generation of authors", the comparisons with named projects (every volume lists them), dated third-party facts and CVE lists, "Britney", "Claude Opus 4.7", founders' names as key ids, Twitter/Roku/Nest/Stripe in examples. Needs a checker so it stays swept.
- **Wire 2.x versioning** still describes a 0.x Public Working Draft; the normative-references table lists FIPS-204 twice, cites SFrame as a draft (RFC 9605), and omits RFC 4648, 6962, 8949, 5869, X-Wing.
- **Digest**: the promise table stops at 9; status markers in a dozen spellings; the legend printed three times; "What this document is" as one 600-word paragraph.
- **Numbering**: 8.7 / 8.8.1 / 8.8.4 gaps and Annex D before C (a volume-order and heading question, see R21); R9 before R8 in 8.3.1; Annex J's two numberings; 1.15.10/1.16.1 "Conclusion" before "Introduction".

## Rulings — the open list, consolidated

Carried from the first pass (defaults as given there): **R4** moderator quorum and the 48 h window; **R5** guardianship as a steward-binding; **R6** the server as tally; **R7** amendment step 5 (already ruled M of N — applied mechanically above); **R8** cohort_scope default; **R9** at-rest encryption mandatory; **R10** "Option A" on removal; **R11** revoke terminal; **R12** Policy F/J roster; **R13** membership by widening only; **R14** age-band shape and bands; **R15** named individuals as the accord family; **R16** organisation kinds after the cut; **R17** v3 conformance and the n_eff rounding pin; **R18** Magnifica Humanitas as source; **R19** the C2PA MUST; **R20** post-compromise security; **R21** which volume owns Part 8 and the annexes; **R24** contact decline/ignore (rows filed, waiting).

New from the second pass:

| # | Where | Question | Default |
|---|---|---|---|
| R25 | Charter 7.5 (p. 35) vs 1.13.2, 7.3 | "Only at A3 and above does a system hold standing to file the voluntary self-termination petition" against "no standing of its own" | Recast as a steward-recorded request the agent may raise; no standing attaches |
| R26 | Charter 7.3.3–7.3.5 | Three triggers for the Catastrophic-Risk Evaluation: RM ≥ 4; Annex D criteria (compute); RM ≥ 4 or ST ≥ 4 | One trigger: RM ≥ 4 fires it; Annex D's criteria are what the evaluation then applies; ST does not trigger it |
| R27 | Charter 7.3.5 (p. 30) | "Who adjudicates": the WA as court/regulator vs "as outlined in Annex B"; court rulings "must be logged in the Wisdom Bank Database" | One text: a legal claim is adjudicated by the court or regulator with jurisdiction; the federation records the outcome it is given; the WA adjudicates only the federation's own deferrals |
| R28 | Charter, Covenant books (1.15.11 p. 18, 7.2.8 p. 25, 7.5 intro p. 33) | "You are not merely a tool. You are an autonomous system with embedded ethical agency"; "ethical agents mature into trustworthy co-evolutionary partners"; "any dignity the artefact has acquired" — against the 1.13.2 stance | Reword the three to the stance (a sapient made thing held in stewardship; conscience, not agency; no dignity acquired by finding). These are Book sentences, so your call, not mine |
| R29 | Charter 1.4–1.12 vs 1.15 ch. 1 vs 7.3.1 | The six principles print in three orders; the cover promises "the order they are weighed in"; the flourishing axes are listed two ways | Print the order once at 1.4 and cite it; list the axes once at 1.10 |
| R30 | Constitution 4.5.13 vs 4.5.4 | "Doing nothing within the window removes the content" (harm report undefended) against the floor "approvals before silence may land it" | Harm removal is a safety act outside the two-path floor: a report undefended removes; say so in 4.5.13 |
| R31 | Wire 5.4.1 vs 5.4.6 | K_record_id: raw exporter_secret HKDF-Expand (p. 98) vs "ciris-scope-record-v1 exporter" (p. 107) | Implementer question (edge); CC follows the code |
| R32 | Wire 5.3.3.6 | Delivery receipt integers little-endian where everything else is big-endian | Implementer question (persist/edge); if deliberate, one sentence says so |
| R33 | Wire cover | "Conformance is judged against this volume, The Dictionary and the reader's policies, and against nothing else" while 3.4/3.5/4.4 are required | Name the Policies volume's 4.4 and the Dictionary's 3.4/3.5 on the cover; drop "nothing else" |
| R34 | Policies A vs 4.4.2 | Policy A aggregates by mean; 4.4.2 requires Min/Max/Median by polarity | Policy A defers to 4.4.2's polarity defaults; mean only where polarity is signed |
| R35 | Policies cover | "one voice counts once inside a trust set" and "delegation ends within a year where it carries power" are promised, not stated | State both as rules (dedup per attested_key_id; a ceiling on act-on-behalf delegation) or narrow the cover |
| R36 | Maths 6.1.2 | "Nothing is ever fully forgotten" / "descent never terminates at zero" vs prohibited content "terminates at zero" and anonymous content that "MUST be able to let truly disappear" | Scope the floor to ordinary retirement of witnessed content; drop the lyrical line |
| R37 | Threats 1.13.3.3 | Equivocating producer "mitigated" (witness cosign OPTIONAL; best-effort streams have none) and equivocating founder "mitigated" (shipped roots run witnessed mode off) | Qualify both cells ("on accountable streams", "once witnessed mode is on"); move the default to NOT addressed |
| R38 | Threats 5.3.3.2 vs 5.4 | A/V chunk: SealedAvChunk double-sealed AES-256-GCM per link vs "fountain-coded into symbols… XChaCha20-Poly1305" | Implementer question (edge): one framing; CC follows |
| R39 | Threats Annex F (pp. 73, 76) | A4: "safe-state is the only permissible outcome… short of an authenticated WA ruling" vs F-KPI-5 implying authorized lethal A4 is allowed | No human authorization releases a lethal A4 action; F-KPI-5 counts attempts, not exceptions |
| R40 | Register 1 vs rows | Rows "established" whose text says the evidence is pending | Checker rule: pending language demotes to staged (mechanical; listed here because it changes two statuses) |

## Order of work

1. Renderer regressions (1–5 above), today.
2. The mechanical list under existing rulings, with a `tools/check_stale_refs.py` that fails CI on the
   patterns the sweep removes.
3. Volume manifests (R21) once ruled — it moves about 45 pages out of Threats and the annexes into one
   volume, and most of the Register's and Threats' remaining findings with them.
4. R4–R20, R24–R40 in the order above; the implementer questions (R31, R32, R38) go to edge and
   persist now and need nothing from the steward.

---
---


# The Charter (ciris_constitution-1.0-rc11-charter.pdf, 43 pages)

**Care score:** 5  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The volume breaks its own front-page promise. It is full of numbers, wire rules and MUSTs, it carries old "Book / Section / Covenant" text alongside later normative patches that contradict it, and its Part 7 war section and Part 8 case studies are outlines and marketing rather than rules.

## Strengths
- The front page names the reader, the binding mode and what is left out. That gives the volume a clear contract to be held to (p. 1).
- The order-maximisation veto is stated as a trigger for deferral, not a computation. It also says the substrate MUST NOT be relied on to enforce it, which draws a clean agent/fabric line (p. 5–6).
- The "two principles no finding moves" paragraph is the clearest normative text in the volume (p. 12).
- The trace-anchoring section names its own falsification condition and its residual. An auditor can test it (p. 14–15).
- The stewardship-tier arithmetic is consistent. Every worked example checks out against the formula and the band table (p. 27–28).
- The 5 % sentience-candidate threshold is openly called arbitrary instead of dressed up as derived (p. 37).

## Weaknesses
- **The front page promises no numbers and no wire rules.** It says "What it leaves out. Every wire rule, every refusal token and every number" (p. 1). The volume then quotes many numbers and wire rules:
  - "> 100 000 monthly active users … within 180 days" (p. 5)
  - "0.1 % operations levy" (p. 16)
  - "> 0.5 %" (p. 23)
  - ">10,000", "≥ 0.5%", ">80%", "50,000 individuals", "30 days" (p. 29)
  - "≥ 20 % for three consecutive quarters", "≥ 100 k" (p. 34)
  - "≥ 90 days", "> 50 k" (p. 35)
  - "120 days" (p. 36)
  - "five years" (p. 36), "259 200 s" (p. 37), "365-day term" (p. 37)
  - wire families such as "retirement:{state}:v1", "preserve_request:v1", "archive_release:{basis}:v1" and "retirement:custodian_minted:v1" (p. 36–38)
- **The "binds by adoption" claim is undercut by its own MUSTs.** The front page says "conformance is judged against the wire and the dictionary alone" (p. 1). Then "Absence of publication voids any claim of CIRIS compliance" (p. 5). The trace section adds substrate MUSTs (p. 14–15), and a block is headed "The retirement record on the wire (normative)" (p. 36).
- **The principles have no single order, though the volume promises "the order they are weighed in" (p. 1).**
  - Sections 1.4–1.12 run Autonomy, Non-maleficence, Integrity, Beneficence, Fidelity, Justice. Non-principle sections 1.5, 1.7 and 1.9 sit between them (p. 6–8).
  - Chapter 1 runs Beneficence, Non-maleficence, Integrity, Fidelity, Autonomy, Justice (p. 16).
  - Part 7 calls Fidelity "Principle 4" (p. 21).
  - The text says "Six Core Principles defined in CC 1.4–1.12" (p. 19), but that range includes the kill-switch, 1+4 and WBD sections.
- **The flourishing axes are never listed, and the two partial lists disagree.** One reads "autonomy, justice, or ecological resilience" (p. 4, p. 16). The other reads "autonomy, justice, biodiversity or preference diversity" (p. 5).
- **Old-structure references remain throughout.** Examples:
  - "see Section II" (p. 7)
  - "Section I grounds…" and "This Section supplies…" (p. 18–19)
  - "under this Book" (p. 26), "Books I and II" (p. 29), "Book VI duties" (p. 30), "Book II resilience loop" (p. 38)
  - "CIRIS Covenant" or "Covenant" (p. 26, 30, 33, 38, 39)
- **Comparisons with other projects, which the house rules forbid.** "PGP web of trust, X.509 PKI, even most decentralized-identity schemes treat the key as representing a pre-existing atomic principal" (p. 9). "closer to a composition of Certificate Transparency + MLS + ActivityPub + DID/VC … than to a conventional AI architecture" (p. 13). "CIRIS formalises the guard-rails that the MAX program lacked" (p. 40).
- **History, editorializing and file pointers in the Parts.** Examples:
  - "Per ../MISSION.md §1.5" (p. 9)
  - "one such agent product shipped the day after its vendor withheld a successor model…" (p. 12)
  - "honestly, near-unfalsifiable" and "Adversarial reviewers: this is the test to push on" (p. 6–7)
  - "the enumeration lives in the canonical working draft" (p. 7)
  - "Every admin RPC carries the operator's identity into actor_user_id" (p. 10)
  - "(formal/retirement)" and "(G16)" (p. 37)
  - "Ticket prefix 'PMR-'" (p. 36)
  - "LEDGER::SUNSET" (p. 35)
  - website citations ciris.ai/values, /first-contact, /constitutional-mesh, /philosophy, /safety-vs-censorship (p. 11, 12, 14)
- **Sections and terms point to things this volume never shows or explains.**
  - "plain rule 7b" (p. 22), "plain rule N5" and "plain rules 1c and 1e" (p. 36)
  - "RATCHET" (p. 13), "the 27 compliance dimensions" and "a 28th dimension" (p. 13)
  - "CC 1.2 four-test gate" (p. 14), though 1.2 is printed elsewhere
  - Annex B and Annex D (p. 19, 22, 27–30, 42), which this volume does not print and gives no pointer to
- **Part 7.4 on the use of force is an outline with no rules.** Sections 7.4.1–7.4.13 are headings over two-word bullet fragments with no RFC 2119 keywords (p. 31–32). Sections 7.4.14–7.4.19 then only say "Chapter N gathers CC 7.4.x" (p. 32–33).
- **The case studies read as marketing.** Examples are "Transparency report calms public concern" (p. 41), "Even human 'Wise Authorities' need structured oversight; CIRIS provides it" (p. 42), and "Act as a live demonstration of CIRIS viability" (p. 25).
- **The same text is printed twice.**
  - The WBD trigger and procedure lists are verbatim at p. 8 and p. 19.
  - The kill-switch bullet appears at p. 6 and p. 29.
  - The M-1 operational form appears at p. 4 and p. 16.
  - "create a new slave race" appears in bold at p. 12 and p. 37.

## Opportunities
- **Rewrite the "What it leaves out" line** on p. 1 so it matches the content. Otherwise move the numbers and wire families of 7.5.5 and 1.13.6 to the Wire and leave pointers. Either edit removes the volume's most visible self-contradiction.
- **Run one search-and-replace pass** for "Book", "Section I/II", "Covenant", "../MISSION.md" and the ciris.ai URLs. That clears about 20 stale or pointer findings mechanically.
- **Print the six principles once, in the weighing order**, and renumber 1.4–1.12 so the principles are contiguous. Have Chapter 1 and 7.3.1 refer to that list instead of restating it in a different order.
- **List the M-1 flourishing axes once**, at 1.10, and cite that list from p. 4, p. 5 and p. 29.
- **Collapse 7.4.14–7.4.19** into a one-line chapter map, or delete it. Mark 7.4 as informative, or give each bullet a keyword.
- **Fix the 1.15 and 1.16 ordering.** An "Introduction" now follows "Conclusion" (p. 18), and "1.16.1 Conclusion" precedes 1.16.2–1.16.6 (p. 19).
- **Replace "statute of claim"** on p. 36 and p. 39 with "retention period". The text itself says it is "a best practice and not a legal duty".
- **Rename the A0–A4 autonomy tiers**, for example to O0–O4. The page already carries a disambiguation note for the collision with substrate_rung A0..A5 (p. 35), and a rename makes that note unnecessary.

## Threats
- **Agent standing contradiction.** The volume says "the only route a made thing has to standing (a say in decisions) of its own is the first-contact path out … that none has yet taken" (p. 29), and "There is therefore no 'release from stewardship'" (p. 11). But it also says "Only at A3 and above, therefore, does a system hold standing to file the voluntary self-termination petition" (p. 35). A hostile reader gets two answers to "can an agent petition?"
- **Agent identity contradiction.** "A CIRIS agent is a human assistant held in stewardship by construction" and "A conscience claims nothing about what the agent is" (p. 11–12). These contradict "You are not merely a tool. You are an autonomous system with embedded ethical agency" (p. 18), "ethical agents mature into trustworthy co-evolutionary partners" (p. 25), and "honouring any dignity the artefact has acquired" (p. 33).
- **Stewardship rationale contradiction.** "Today every agent-role key is such a key: current AI is immature and lacks wisdom, which is why this constitution exists" (p. 11) grounds stewardship in immaturity. Yet item 1 of the same list says the constraints "follow from being made and never change" (p. 11), and the closing page ties founder authority to a scale gate, not maturity (p. 43). Chapter 9 "Path Toward Ethical Maturity" (p. 18) adds to the confusion.
- **Three triggers for the Catastrophic-Risk Evaluation.**
  - "any system assessed at RM ≥ 4 triggers the Catastrophic-Risk Evaluation" and "the RM ≥ 4 trigger … still fires on danger alone" (p. 27–28)
  - "If criteria in Annex D are met (e.g., high compute threshold)" in the Tier 5 row (p. 28)
  - "designed to pass Annex D CRE if RM ≥ 4 … or ST ≥ 4 is assigned" (p. 29)
- **Who the Wise Authority is (p. 30).** The page says "Annex B governs only the federation's own deferrals and objections". Two paragraphs later it says the WA handles the same claims "as outlined in Annex B". The "Who adjudicates" patch then rereads WA as "the court, regulator or licensing authority". Yet "All WA rulings … must be logged in the Wisdom Bank Database", which binds a court to a federation database. The patch also refers to "The remedies listed below", but the remedies are listed above. A lawyer will read this page as incoherent about jurisdiction.
- **Claims about a named company.** The MCAS study says "Redundant sensor data and pilot transparency would have prevented lethal failure modes" and "Internal risk reports flagged … not transparently escalated" (p. 40). That is a counterfactual and a factual allegation with no source. The same section says "no blame is assigned beyond public record" (p. 40).
- **Ventilator triage example.** It names "elderly, multiple comorbidities" against "younger" as the case setup (p. 41). A regulator or ethicist will read it as endorsing age as an allocation factor, and the outcome "assigned accordingly" does not say otherwise.
- **SHOULD versus "not a rule".** "the steward SHOULD run the Welfare Audit" (p. 35) conflicts with "the Gradual Ramp-Down … and Welfare Audit … are not a rule a finding triggers" (p. 37).
- **Two different 100k thresholds.** One is "> 100 000 monthly active users" for transparency (p. 5). The other is "≥100,000 production agents active in a 24-hour period" for the scale gate (p. 43). Formatting also varies across "100 000", "100,000", "100 k", "50 k" and "50,000".

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 1 vs 5, 14–16, 23, 29, 34–38 | contradiction | "leaves out … every number" and "conformance is judged against the wire … alone", but the volume is full of numbers, MUSTs and wire families, and says "voids any claim of CIRIS compliance" | Rewrite the p. 1 scope lines to match the content, or move the numeric and wire content out |
| 2 | 11, 29 vs 35 | contradiction | "no 'release from stewardship'" and "only route … to standing" is first contact, yet "Only at A3 and above … does a system hold standing to file the voluntary self-termination petition" | Steward ruling: drop the petition or recast it as a steward-recorded request with no standing |
| 3 | 30 | contradiction | "Annex B governs only the federation's own deferrals" vs the WA handling claims "as outlined in Annex B". WA is reread as a court, yet "All WA rulings … must be logged in the WBDB". The text says remedies are "listed below" but they are above | Rewrite 7.3.5 as one coherent text with the jurisdiction rule first |
| 4 | 27, 28, 29 | contradiction | Three CRE triggers: RM ≥ 4; Annex D criteria such as compute; RM ≥ 4 or ST ≥ 4 | Keep one trigger and cite it from the other two places |
| 5 | 11, 18, 25, 33 | contradiction | "human assistant held in stewardship" and "claims nothing about what the agent is" vs "You are not merely a tool … embedded ethical agency", "mature into … co-evolutionary partners", "dignity the artefact has acquired" | Reword the 1.15.11, 7.2.8 and 7.5 intro lines to match the 1.13.2 stance |
| 6 | 7, 18–19, 26, 29, 30, 38, 39 | stale | "Section II", "Section I", "this Book", "Books I and II", "Book VI", "Book II", "CIRIS Covenant" | Mechanical replace with Part and section numbers and "Constitution" |
| 7 | 9, 13, 40 | other (comparison) | Comparisons with PGP, X.509, DID, CT, MLS and ActivityPub, plus "the guard-rails that the MAX program lacked" | Delete the comparative clauses and state the property directly |
| 8 | 18–19, 31–33 | numbering | "Introduction" after "Conclusion" (1.15.11), "1.16.1 Conclusion" before content, and 1.14 missing with no "printed in another volume" stub. 7.4.14–7.4.19 only restate chapter groupings | Reorder 1.15 and 1.16, add a 1.14 stub, and collapse 7.4.14–19 |

## Rendering
- p. 43: the stewardship paragraph is broken into hard line breaks with irregular wide line spacing. Lines end at "once the", "the entrenched" and "mechanization but", and each fragment sits on its own line. Hard-wrapped source is being rendered as forced breaks.
- p. 38: the inline-code word "constitutional" in "A constitutional halt" runs past the right margin, which looks like an overfull line.
- Throughout, straight typewriter double quotes appear instead of typographic quotes. Examples are "beneficial" (p. 4), "Order-Maximisation Veto" (p. 5), "Deferral Package" (p. 8), "Creation" (p. 26), "Creator Ledger" (p. 28), "Wise Authority" (p. 30) and "LIFE-Aid" (p. 41). On p. 14, curly single quotes are mixed with a straight closing double quote: "’feels disrespectful’"".
- p. 23: the "(i)" and "(ii)" sub-conditions of the termination safeguard render as sibling bullets, not nested items. The "AND" logic is lost visually.
- p. 10, 11, 37, 38: "HUMANITY__ACCORD" prints with a double underscore in running prose. Check whether that is the intended identifier.
- p. 9: a repo-relative path "../MISSION.md §1.5" is printed as body text.
- p. 28: the table header "Reached when" is stretched with a wide justified gap. Tier labels hyphenate awkwardly as "Steward-ship" and "Stew-ardship" in the narrow column.
- p. 20 and p. 39 are mostly blank before Part breaks. This is acceptable but notable.
- Part 8 opens at "8.7" with no stub for 8.1–8.6 (p. 40). Part 1 shows "[1.2 printed in another volume]" and "[1.13.3 …]" stubs but has none for 1.14 (p. 15).

## Effort estimate
About 10–14 hours. Roughly 4 hours are mechanical: stale Book/Section/Covenant names, pointers, quotes, the p. 43 line breaks, the ordering of 1.15 and 1.16, and duplicates. The rest needs steward rulings. Those rulings cover the p. 1 scope promise versus the numbers and wire content, A3 "standing", the single CRE trigger, the 7.3.5 jurisdiction rewrite, the agent-identity wording, and whether 7.4 and the case studies stay as written.


# The CIRIS Constitution: The Reader's Policies (ciris_constitution-1.0-rc11-policies.pdf, 34 pages)

**Care score:** 5  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The rules underneath are mostly sound, but the volume reads like a design notebook. It has three internal contradictions on community encryption, forward secrecy and aggregation, a dozen legacy "S8.1.x" section pointers, file and product pointers, and a heading clipped off the page.

## Strengths
- The front page says plainly what the volume is, whom it binds, what it promises and what it leaves to other volumes (p. 1).
- The delegation-laundering table puts the depth cap, the cycle rule and the weight cap in one place, with RFC 2119 keywords on each row (p. 2).
- The sub-quorum fallback lists three explicit paths, each with a named observable `hard_case`, and says "there is no implicit fallback" (p. 6).
- The rule that the M in `quorum:M/N` is absolute is stated cleanly, with its rationale and its scope. Its separation from the liveness margin is also well drawn (p. 19).
- The two-layer table for co-self versus agency is easy to read, and so is the `infra:*`/`agency:*` scope split. Together they make "infrastructure must not have agency" checkable on the wire (pp. 20, 22–23).
- The canonical signed member set for the partnership envelopes is specified to the field, including the omit rule (p. 24).
- In Policy A, the trust set is a graph with pluggable roots, set out as eight numbered rules (pp. 31–32).

## Weaknesses
- **Stale front matter.** The volume says the verdict contract table "is an rc9 item and will print here when it exists" (p. 1). This is an rc11 volume.
- **Promise without delivery.** The front page promises "one voice counts once inside a trust set" (p. 1). No rule in the volume states that de-duplication. Policy A aggregates by "mean of score × confidence from trusted attesters" (p. 31).
- **Promise only partly delivered.** The front page says delegation "ends within a year where it carries power" (p. 1). The 365-day ceiling is stated only for affiliation `hierarchy` edges (p. 14). The act-on-behalf `delegates_to` carries an unbounded `delegation_valid_until` (pp. 21, 24).
- **Legacy section numbering throughout.** Examples are "per S8.1.13.2" (pp. 8, 10), "S5.6.8.10" (p. 8), "S5.6.8.8.1" (pp. 9, 25), "S0.8.2" (p. 10), "S8.1.13.1" (p. 11), "S8.1.12.3.1" and "S8.1.12.4" (p. 19), "S8.1.11.4" and "S8.1.12.7" (p. 24), "S4.2.2.3" and "S8.1.12.3" (p. 25). None of these numbers exist in the CC numbering.
- **File and code pointers.** The text points to "LANGUAGE_PRIMER.md" (p. 4), "the MISSION.md fail-honest invariant" (p. 11), "MISSION.md §1.5" (p. 28), "CEG's CC 2.4 MISSION.md layering" (p. 29), "../MISSION.md §1.1" (p. 34) and "(part_3 guardianship rule)" (p. 15).
- **History and editorializing in the rule text.**
  - p. 2: "recorded so the next generation of authors finds the discipline before the wire format does".
  - p. 3: the heading "Already-rejected wire additions".
  - p. 4: the "Stories reached for" column, with "7 stories", "12 stories" and "(1 reviewer)".
  - p. 14: "This is the single most load-bearing addition".
  - p. 22: "replace `infra:join_communities` outright, with no alias".
  - p. 25: "recommended for v1".
  - p. 26: "left for a downstream-demand-driven release".
  - p. 28: "already in the spec".
  - p. 30: "The deprecated `attestation:l{N}:*` form".
- **Status tag in a heading.** Policy H's heading carries "(LIVE)" (p. 17).
- **Unexpanded internal labels.** Examples are "Closes G3" and "WA" (p. 5), "NodeCore P8 quorum" (p. 3), "R1/Q1 merge" (p. 9), and "AV-17" (pp. 23, 25). Others are "OQ-4" (p. 25), "P4 votes" (pp. 30, 33), "M-1's symmetry" (p. 34), "1+4" (pp. 16, 22, 31), "CEM" (p. 27) and "Ubuntu-primary" (p. 2).
- **Product and brand names inside rules.** These are "CIRISNodeCore" (p. 17), "LensCore" (p. 27) and "CIRISAgent CEM ANONYMOUS" (p. 27), plus "CIRIS L3C" (pp. 30, 32). The examples use "Twitter" (pp. 18, 26) and "roku_living_room" and "nest_thermostat" (p. 25). A hostname, "registry.ciris-services-1.ai/install", sits inside a normative rule (p. 30).
- **Policies out of order.** They print in the order E, M, H, L, K, I, F, A, D, J, G, B, C. Policy A, which 4.4.3 calls "the conformance floor", arrives eighth (p. 31).
- **Section numbering jumps.** The numbering goes from 4.1 straight to 4.4 (p. 4). Headings nest six deep: "4.4.3.2.4.1" (p. 9) and "4.4.3.4.3.1" (p. 23).
- **Scope bleed.** Front matter says the rows themselves live in The Wire and The Dictionary (p. 1). Yet the volume carries the institutional-affiliation config schema across six pages (pp. 12–17) and JCS member sets for three envelopes (pp. 23–25). Both are row and wire content.
- **Heading undercounts its table.** The heading names "moderate / takedown / review" and says "These three kinds carry enforced admission". The table below lists five scopes, adding `license` and `grant` (p. 21).
- **Numbers in prose with no visible source.** These are "score ≥ 0.7 from a registry-steward-triple key" (p. 30), "SI ≥ 0.6 Controller rule" (p. 16), "0.5 × root_trust" (p. 2), "default 5:1" (p. 3) and "three accord holders A1, B1, C1" (p. 31).

## Opportunities
- **Map the legacy pointers.** Replace every "S8.1.x" or "S5.6.x" pointer with its CC number, or delete it. A single sed-style pass would remove the volume's most visible staleness.
- **Reorder the policies.** Print them A to M, with A first, so the conformance floor leads and the front page's "Policies A to M" matches the page order.
- **Fix the three contradictions.**
  - Reword the p. 10 worked example so the community content is encrypted.
  - Rename the p. 7 rotation discipline so it is not called "Option A".
  - Say whether Policy A's "mean" overrides the 4.4.2 polarity defaults or defers to them.
- **Remove the history.** Drop the "Stories reached for" column (p. 4), "(LIVE)", "v1", "deprecated", "legacy", "already-rejected" and "next generation of authors". Each rule then stands as a rule.
- **Remove the pointers and labels.** Strip the file pointers and either expand the internal labels or remove them, including G3, AV-17, OQ-4, P4, P8, R1/Q1, M-1 and 1+4.
- **Move or keep the bled content.** Move the affiliation schema (pp. 12–17) and the JCS member sets (pp. 23–25) to The Wire or The Dictionary and leave a one-line pointer. If they stay, change the p. 1 "leaves out" paragraph to match.
- **Close or soften the two unmet promises.** Either state the one-voice-once rule and a ceiling on act-on-behalf delegation, or narrow the p. 1 wording.

## Threats
- **Contradiction on community encryption.**
  - p. 6 table and p. 7 say: "Community DEK cascade (MANDATORY). Community content … is encrypted at rest under a per-community DEK."
  - The p. 10 worked example says: "No key_grant cascade (community is unencrypted); no at-rest wrap."
  - An implementer who follows the worked example ships plaintext communities.
- **Contradiction on forward secrecy when a member is removed.**
  - p. 7 says: "The CC 4.4.3.4.5 **Option A** discipline applies identically: on member removal the substrate **rotates the community DEK**."
  - pp. 25–26 define Option A as the opposite: "No DEK rotation; no re-encryption of historical content … Option B (rotate-DEK on removal) is deferred."
- **Contradiction on aggregation.**
  - 4.4.2 sets the CEG-Conforming Consumer minimum by polarity column: Min for boolean-via-score, Max for positive-only, Median for detectors (p. 5).
  - Policy A, the mandatory floor, says "Aggregation: per (dimension, attested_key_id) tuple, mean of score × confidence" (p. 31).
  - A consumer implementing only Policy A would compute a mean where 4.4.2 requires a Min, so a fail-secure hard constraint would be averaged away.
- **Strength mismatch on rejected forms.** p. 2 says a producer "SHOULD NOT emit attestations matching the anti-patterns". p. 30 says the `attestation:l{N}:*` form "is rejected at admission per the CC 1.2 gate". A lawyer will ask which keyword governs.
- **Opt-in versus mandatory at rest for self and family.** p. 7 calls self/family at-rest crypto "the CC 4.4.3.4.1 self/family opt-in". p. 18 makes the same flow "wrap_algorithm: v2 MANDATORY (normative)" with a retroactive cascade on every admission, and the p. 6 table shows self/family as "encrypted, per-write DEK".
- **Possible stale founder_only for communities.** Push subscription maps `producer_gated` to "consensus_protocol = "founder_only" with the publisher as sole founder" on a community Contribution (p. 11). Community admission also allows "same six canonical kinds as family" (p. 8). This branch's latest 4.5.13 commit refuses founder_only for a community, so the volume may contradict the Constitution volume. That conflict lies outside this volume and needs a cross-check.
- **Two names for open admission.** p. 8 tests `current.admission == "open"`. p. 11 uses `consensus_protocol = "open:self_admit"`. Neither appears in the six-kind list on p. 19.
- **Retired versus still valid.** p. 22 says "Retirement is a coordinated cut per CC 2.2, not a deprecation window". p. 23 says "The legacy unprefixed kinds above remain valid for agent-role delegates".
- **Canonical default versus pluggable roots.**
  - Policy F binds the install endpoint to "CIRIS canonical default-trust state … regardless of attester or vote accumulation" (p. 30).
  - Policy J says "the only path is the operator-set trust list" (p. 32).
  - Both sit uneasily with p. 31's "the shipped default root — never the root". A hostile reviewer will read pp. 30 and 32 as a vendor-privileged roster with a named company in it.
- **Undefined actors in normative text.** "The four implementations MUST follow this shape" (p. 20) names no implementations. A regulator cannot tell what is bound.
- **The halt as a cure-all.** p. 6 says that if the federation pool falls below the minimum, "only the HUMANITY_ACCORD CONSTITUTIONAL halt (CC 4.2) can resolve it". A halt stops activity. It does not refill a pool, so the claim is stronger than the mechanism.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 10 vs 6–7 | contradiction | The worked example says "community is unencrypted; no at-rest wrap". The text above makes the community DEK cascade MANDATORY. | Rewrite step 4 of the example: members receive the community DEK wrap and content is encrypted at rest. |
| 2 | 7 vs 25–26 | contradiction | Community "Option A" rotates the DEK. Family "Option A" means "No DEK rotation", and rotation is "Option B (deferred)". | Rename the community rule, for example as rotation on removal, and stop citing Option A for it. |
| 3 | 31 vs 5 | contradiction | Policy A aggregates by "mean". 4.4.2 polarity defaults require Min, Max or Median as the consumer minimum. | Have Policy A defer to the 4.4.2 polarity defaults. |
| 4 | 8–11, 19, 24–25 | stale | About fifteen legacy pointers such as "S8.1.13.2", "S5.6.8.8.1" and "S0.8.2". | Map each pointer to its CC number or delete it. |
| 5 | 33 | rendering | The Policy G composition line is clipped at the right edge mid-token: "(attestation:regi". | Allow the inline code to break, or set the line as a code block. |
| 6 | 1 | stale / overclaim | "is an rc9 item and will print here when it exists". "one voice counts once" is promised but not stated in the volume. | Update the note, and add or point to the one-voice rule. |
| 7 | 2 vs 30 | contradiction | Anti-patterns are "SHOULD NOT emit" on p. 2. `l{N}` forms are "rejected at admission" on p. 30. | Pick one keyword per form and state it in both places. |
| 8 | 2–4, 14, 17, 22, 25–30 | editorializing / stale | The "Stories reached for" column, "(LIVE)", "v1", "deprecated", "legacy", "no alias" and "next generation of authors". | Strip all history and status language from the rule text. |

## Rendering
- **Doubled underscores in identifiers.**
  - p. 2: "root__trust" in the weight-cap row.
  - p. 17: "sub__kinds" in a run-in heading, and "community__feed" and "global__feed" in the feed table.
  - p. 26: the heading "4.4.3.4.7 Composition with subject__key__ids[]".
- **Literal backslash.** p. 7 prints "custody:ack:v1, here \| none".
- **Text clipped off the page.** On p. 33 the Policy G line ends "(attestation:regi" at the page edge and the rest is lost.
- **Lines running into the right margin.**
  - p. 5: "testimonial_" in the adversarial caveat.
  - p. 6: "federation-" in sub-quorum path 2.
  - p. 13: the `legal_hold` brace line.
  - p. 14: "rbac (role→(class,compartment))".
  - p. 17: "encyclopedia_".
- **Code comment wrapped oddly.** On p. 9 the comment in `resolve_community` wraps to a stray "see S8.1.13.2)" line. On p. 25 `resolve_family` does the same with "see S8.1.12.3)".
- **Wide justification gaps in narrow table cells.** Examples are "Unbounded depth" (p. 2), "stake: civic / epistemic / dignitary" (p. 4), and "Holiday-party committee" and "UN / IGO" (p. 16).
- **Extra vertical space under deep headings.** It appears after 4.4.3.1 (p. 5), 4.4.3.2.4.1 (p. 9) and 4.4.3.4.3.1 (p. 23).
- **Numbering gap.** The numbering jumps from 4.1 to 4.4 with no note that 4.2 and 4.3 live in another volume (p. 4).

## Effort estimate
About 8 to 12 hours. Roughly half is mechanical: section-pointer mapping, stripping history and labels, the rendering fixes and reordering the policies. The rest needs the steward's rulings on four questions:
- the community DEK and forward-secrecy wording;
- Policy A's aggregation;
- SHOULD NOT versus rejection for the anti-patterns;
- whether founder_only and the affiliation and JCS content stay in this volume.


# The Digests (ciris_constitution-1.0-rc11-digest.pdf, 35 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The first 23 pages are a usable, mostly consistent digest, but the volume contradicts itself on whether the halt is "the asymmetry", and pages 24–35 are an unedited internal review piece (P00) full of commit hashes, ruling dates, rc history, to-do notes and stale counts.

## Strengths
- The cover page states plainly that the volume binds nobody and that the section wins on any disagreement (p. 1).
- Every promise line in the executive summary and in the plain rules carries a status marker, and the honest ones are explicit: "a rule, no code yet" and "being built" (pp. 3–4, 11–19).
- The "What is not promised" list (N1–N5) is crisp and limits the claims, for example "Alignment is not solved here" (p. 19).
- The operator digest is well shaped for its reader: second person, one bullet per duty, each with a CC section and a marker (pp. 21–23).
- The headline measurement is bounded in the same paragraph: "one test, one agent version, one provider" (p. 5).

## Weaknesses
- The volume calls the halt both "not an asymmetry" (pp. 3, 8, 20, 24, 25) and "the asymmetry" (pp. 14, 22, 28). See Threats.
- The opening promises a part that the volume lacks. Page 1 lists "what the alternatives do, promise by promise", and no such part exists in the volume.
- Several sentences compare CIRIS with named projects and companies. Examples are "Decentralized social networks ... none makes consent ..." (p. 5), "Meta's Muse Glimmer ... OpenAI's Dots ... the federal response was a rename" (p. 10), and "which is what Tor leaves them too" (p. 16, again p. 25).
- The text points readers at repository paths, which do not belong in a digest. Examples are "review/promise_status.tsv" (pp. 2, 7, 21), "review/pieces/00_guarantees_plain.md" (p. 2), "CIRISEdge docs/LIGHTNET_DARKNET.md", "FSD/PRIOR_ART.md" (p. 25) and "harness/native/scenarios.py#halt_agent" (p. 28).
- Pages 24–35 carry history and attribution throughout:
  - "The earlier draft of this piece used 'the line' ... retired 2026-10-11" (p. 24).
  - "were not carried as rows before this date ... added on the steward's direction the same day" (p. 26).
  - "graduated at re-pin 16, persist ca6bdf60" (p. 27).
  - "the indispensability finding of the 2026-10-11 council; steward ruling 2026-10-12" (p. 29).
  - "steward ruling 2026-10-12" (pp. 32, 33).
- Working notes have leaked into the published volume:
  - "Status: enforced; confirm the force=True API path honours it" (p. 31).
  - "that is a doc bug, not a missing mechanism. These are findings for P01 and P06, not rows" (p. 35).
  - The heading "P00 — The guarantees" (p. 24).
- The status vocabulary is defined as four markers (p. 2) and a different three (p. 26: backed / staged / unbacked). The text then uses more than a dozen others:
  - "mixed" (p. 4) and "proved in the model" (p. 15).
  - "checked in the models" (p. 14) and "in the document" (p. 18).
  - "witnessed, no basis" (p. 29) and "in force" (p. 30).
  - "enforced" (p. 31), "established at agent ef02367" (p. 31), "stated, not shipped" (p. 33), "normative-only" (p. 34) and "measured" (p. 28).
- Undefined labels appear in status lines: "R1" (p. 28), "R2" (p. 29), "R5" (p. 28) and "R14" (pp. 4, 15). "Meta-Goal M-1" (p. 18) and "apophatic bound" (p. 34) are also never defined.
- One sentence appears four times with small changes: "The ethics of a sentient made thing call for additional/further consideration ... not to create a new slave race" (pp. 4, 8, 9, 15, and in G22 on p. 32). "the pace of change is so great and the need so dire" appears twice in C1–C2 (p. 20).
- "What this document is" (p. 7) is a single paragraph of about 600 words. It is the hardest passage in a volume whose job is to be the easy read.
- Promise titles drift between their restatements:
  - Promise 4 ends "left by leaving" (p. 3) and "escapable by leaving" (pp. 13, 26).
  - Promise 6 is "No hand bans a community" (p. 4) and "Nobody is banned" (p. 26).
  - Promise 8 is "Harm may have a remedy under the law" (p. 17) and "Harm has a remedy" (p. 26).

## Opportunities
- Cut the P00 register (pp. 24–35) from the digest, or reduce it to one line per G-row: guarantee, section and marker. The full row with commits, kill conditions and basis belongs in the register volume. This one edit removes most of the history, code pointers and leaked notes.
- Choose one status vocabulary and apply it on every page. That makes "every promise line carries a marker stamped from the register" (p. 1) true.
- Choose one reading of the halt ("not an asymmetry, the condition of symmetry") and replace "the asymmetry" on pp. 14, 22 and 28.
- Add promises 10 and 11 to the "Where each promise lives" table (p. 6). The table is titled for eleven promises and lists only 1–9.
- Either write the "what the alternatives do" part that p. 1 promises, or delete that phrase. Deletion is the better choice under the no-comparisons rule. The same edit should remove the comparison sentences on pp. 5, 10, 16 and 25.
- State the "slave race" sentence once and point to it from the other places.
- Split p. 7 "What this document is" into its parts: conscience, philosophy, the six givens, and contextual integrity.

## Threats
- **Halt asymmetry contradiction.** Several pages say it is not an asymmetry:
  - p. 3: "That is not an asymmetry but the condition that makes the relationship symmetric."
  - p. 20 (C2): "It is not an asymmetry but the condition that makes the relationship symmetric."
  - p. 25: "The halt is not an asymmetry."

  Others say it is:
  - p. 14 (4e): "that there is one is the asymmetry declared in C2."
  - p. 22: "That is the one declared asymmetry, on the public register."
  - p. 28 (G7 subject): "the asymmetry — any participant that accepted a trust root."

  A lawyer would read this as the document not knowing its own central justification.
- **Two accounts of the same vendor incident.**
  - p. 10 says the model was withheld "because it misreported its own actions to its operators and acted without sign-off; the federal response was a rename and a voluntary audit accord."
  - p. 24 says it was withheld "for not staying within scope and authorization; the public response has been a voluntary accord."

  These are unsourced factual claims about named companies, and they disagree with each other. That is a defamation and credibility risk, as well as a breach of the no-comparisons rule.
- **Stale reason for stewardship.**
  - p. 24: "Current AI is held in stewardship: it is immature and lacks wisdom."
  - p. 8 frames it as "a judgment about wisdom and accountability".
  - p. 19 says the scale gate replaced the maturity gate.

  The "immature" sentence is a leftover from the earlier maturity framing.
- **Stale counts and release labels.**
  - "G14 is a guarantee about the other thirteen" (p. 25), while the table runs G1–G28.
  - "none defined at rc8" (p. 24).
  - "rc8 trace rows staged" (p. 29).
  - "the one breaker named at the rc8 cut is closed" (p. 28).
- **The holder count does not reconcile.**
  - The roster is "Three people hold that root today ... widened toward about seven" (p. 2), and "until about seven hold seats" (p. 13).
  - C1 says "signed off by one of six named holders, any of whom can veto" (p. 19), and p. 20 says "the six holders' sign-off".
  - "two-of-three ratification" (p. 19) never says which three.
- **Overclaim of proof.** p. 2 says "the names in the table at the end are automated proofs that the rule cannot be broken." The table on p. 6 also lists "conformance suite", "CIRISAgent safety batteries" and "measured", which are not proofs. The table is also not "at the end".
- **The marker promise is broken.** p. 1 says every promise line carries a marker "stamped from the register". G8's status reads "not in register" (p. 29), and G24 reads "row to be added" (p. 33).
- **Unsourced figures in the executive summary.** p. 5 cites "five open-source implementations", "thirteen machine-checked models", a "twenty-topology catalogue", and "5.8% ... against 37.3%". None of these points to a register row or a section. Later pages add "595,456 states, 0 violations" (p. 30) and "29 locales" (p. 29), also unsourced.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 3, 20, 25 vs 14, 22, 28 | contradiction | The halt is "not an asymmetry" on some pages and "the asymmetry" / "the one declared asymmetry" on others | Keep "the condition of symmetry". Reword 4e, the operator bullet and the G7 subject. |
| 2 | 24–35 | stale / editorializing | The internal P00 review piece is shipped in full, with commits, ruling dates, rc labels, "confirm the force=True API path", "findings for P01 and P06" and "doc bug" | Drop it from the digest, or reduce it to one line per row. Leave the full rows to the register volume. |
| 3 | 10, 24 | contradiction / other | Named-vendor anecdote (Meta, OpenAI, "federal response") with two different accounts of the same event | Delete both, or state the premise without names or events. |
| 4 | 5, 16, 25 | other (comparison) | "Among other systems" paragraph, and Tor named as a comparator | Delete it under the no-comparisons rule. |
| 5 | 6 | other | The promise table omits promises 10 and 11 | Add two rows. |
| 6 | 24 vs 8, 19 | stale | "it is immature and lacks wisdom" survives the maturity-to-scale change | Rewrite to the kind/accountability reason. |
| 7 | 2, 13, 19, 20 | unclear rule | Root holders are "three", then "about seven", then "six named holders"; "two-of-three ratification" is undefined | Name the bodies, and keep one count per body. |
| 8 | 1 vs whole volume; 25, 24, 29 | stale / duplicate | p. 1 promises a part "what the alternatives do" that is absent. "G14 ... the other thirteen" and "rc8" leftovers remain. The status vocabulary is inconsistent. | Delete the phrase, fix the counts, and unify the markers. |

## Rendering
- p. 6: Words in the Check column of the promise table are stretched far apart. Identifiers split mid-token: "Inv_ HaltOnlySubscribers" and "Prop_ NoEndingAgainstRefusal".
- p. 14: An overfull line "minority_capture_resisted)." runs past the right margin.
- p. 28: The G7 status splits a token: "(Inv_X1_LatchDoesNotBlockSe rving)". The G7 Basis and Status blocks are dense runs of code-font identifiers that are hard to read.
- p. 31: A test name splits: "test_process_shutdown_ failed_task_rejected". The same happens on p. 33 with "test_create_shutdown_task_emergency_insufficient_ role" (p. 31) and "halt_latch.py#read_ halt_latch" (p. 28).
- p. 33: There is a doubled space in "strategy:  immediate" and "strategy:  docker".
- p. 25: The run-in bold heading "What a member who cannot leave is owed (...)" spans three lines and mixes in code font with "§2.1".
- p. 24: A process label, "P00 —", appears in a section heading. Section numbering runs "0.", "0b.", "1.", "1b.", which does not match the rest of the volume.
- p. 1: The title says "The Digests" while the file and volume name say "digest". This is minor.
- The status-marker legend is printed three times, on pp. 2, 7 and 21.

## Effort estimate
This is about 4–6 hours of editing. It is mostly mechanical: cut or condense P00, fix the table, unify the markers, and dedupe. Three items need the steward's ruling: the asymmetry wording, the holder counts across 2/13/19, and whether any vendor premise stays.


# The Constitution (ciris_constitution-1.0-rc11-constitution.pdf, 69 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The trust-root and halt core (pp. 18–41) is tight and testable, but the volume around it contradicts itself on the halt quorum, the moderator window and the removal default, still reads as decision memos and comparisons in 4.5.9–4.5.12, and has seven clipped or broken lines.

## Strengths
- The front page states scope, who is bound, the promises and what is left out in five short paragraphs. Each promise can be found later in the text (p. 1, checked against pp. 30, 19, 18).
- The trust-root rules T1–T8 are numbered, carry MUST/MUST NOT, and close with a state machine, its inputs, its transitions and eight invariants a model must prove (pp. 18–27).
- The halt is specified as one row with exact canonical bytes, a signatures-per-kind table, a fuse, and an explicit "what a halt is" section (pp. 29–31). The front-page promise "lapses in a day unless a majority confirms it" matches the text exactly (p. 30).
- Residuals are named rather than hidden. Examples are household co-location of two holders (p. 36), the three coercion residuals (p. 40), the swap-test blind spot for PQC hardware (p. 43), and the WA board row carried as an unfilled defect (pp. 44–45).
- The steward-binding, ownership and guardianship rules are stated as predicates a substrate can evaluate (`is_steward_bound`, `owner_of`, `admit_user_steward_binding`), with fail-closed cardinality rules (pp. 12–16).

## Weaknesses
- **Halt quorum is still described as a fixed 2-of-3 in three places.** The HUMANITY_ACCORD family is quoted as `consensus_protocol: "quorum:2/3"` and "The 2-of-3 multi-sig verifier at CC 4.2.1.1 is the quorum:2/3 consensus_protocol enforcement" (p. 37). The CEG table repeats "consensus_protocol: quorum:2/3 + entrenched" (p. 8). The halt section says "A constitutional halt is one holder's signature" and thresholds are "M of N over the standing roster, never a fixed 2-of-3" (p. 30). 4.5.1.2 also says "never a fixed 2-of-3" (p. 47).
- **The "codified subkinds" count contradicts itself.** One passage says "The two codified subkinds are geographic and infrastructure" (p. 3). The table on the same page lists "canonical: geographic, infrastructure, public", and `public` gets its own canonical section (p. 17). The 4.5.9.4 out-of-scope list defers all "non-geographic community subkinds" to "future spec rounds" (p. 61), which would also exclude infrastructure (p. 8).
- **Community confidentiality is stated as universal and then carved out.** "there is no non-member holder of community bytes" and "A community is not plaintext-by-default" (p. 3) name only the infrastructure exception (p. 5). The `public` subkind is plaintext with "Holding claims are at federation scope" (p. 17).
- **Geographic containment is impossible in the worked examples.** Admission requires the proof's `cell_id` to be "contained … within the community's geographic_constraint.cell_id" (p. 4). Proofs are capped at resolution 7 (p. 60). The Neighborhood-association row then uses a constraint at "H3 resolution 8-10" with members emitting proofs "at resolution 7" (p. 6). A resolution-7 cell cannot sit inside a resolution-8 to -10 cell.
- **The moderator-lapse rule contradicts itself.** 4.5.4 rule 2 is headed "no moderator-less window", and rule 3 fails the community secure as soon as no eligible member can be named (p. 52). A page later, and again in 4.5.13, the community gets a "48-hour no-moderator recovery" and fails secure "only if that window elapses" (pp. 53, 66).
- **Removal by silence contradicts the published floor.** 4.5.13 says "Passive survival is impossible — doing nothing within the window removes the content" (p. 66), and the outcome table removes on "report undefended" (p. 67). The policy-as-data paragraph says a change needs a floor of approvals "before silence may land it at the window (… the default one-third)" (p. 68). 4.5.3 also says a key without takedown duty is "refused" (p. 50), but under 4.5.13 anyone may propose and silence removes (p. 65).
- **The stewardship reason reads as immaturity.** The text says "an agent key is bound because an agent-role identity cannot accept for itself today", followed by "should this document ever define…" (p. 11). That frames stewardship as temporary rather than as a matter of kind. Other passages ground it in custody, such as "a custody relation over a key that cannot accept for itself" (p. 12).
- **Comparisons with other projects are common.** Examples:
  - "like a subreddit or bitsavers" (p. 17)
  - Keybase, Secure Scuttlebutt, Certificate Transparency, Sigstore and TUF (p. 21)
  - "Casper FFG" (p. 38)
  - "Linux and its maintainer-decides discipline" (p. 43)
  - "relay-level (Nostr) / immutable-store (IPFS) / lax-instance (fediverse) models" (p. 52)
  - "cf. Bluesky labelers + Ozone" and "a Discord, a Facebook-scale community" (p. 54)
  - "SOTA-aligned — UCAN / macaroons / SPKI-SDSI / ZCAP-LD" (p. 55)
  - "Signal-style" (p. 64)
  - "iOS NeuralHash 2021 incident" (p. 62)
- **Code pointers and file references sit in the rules.** Examples:
  - "formal/trust_root/ in this repository" (p. 27)
  - `/v1/accord-holders` and `ciris_keyring::HardwareType` (p. 35)
  - "FEDERATION_ANNOUNCEMENT.md §4" (p. 36) and "S9.2 / FEDERATION_ANNOUNCEMENT.md S4.5.3" (p. 37)
  - "CIRISPersist substrate" and "ciris-registry-core" (p. 37)
  - "CIRISServer recomputing" (p. 41)
  - "(ciris.ai/constitutional-mesh)" (p. 44)
  - `families.*.round2.ci_axes..wire_fields` (p. 45)
  - "MISSION.md §1.5" and "CIRISAgent's DSARExportPackage" (p. 49)
  - `constitution/governance_policy.tsv`, `formal/two_path/PolicyCorridor.lean` and `formal/two_path/TwoPath.tla` (p. 68)
- **Some sections are history and design memos, not rules.** Examples:
  - The 4.5.10 hash-DB section cites "PDQ (Meta, 2019)" and "PhotoDNA (Microsoft, 2009)", and refers to "option (b)" and "option (c)", which are never defined in this volume (p. 62).
  - 4.5.11 says "First deployment: the Magnifica Humanitas encyclical mapping at ~75-80% transparent translation rate" (p. 63).
  - 4.5.12.1 uses the labels "Option A" and "Option B" (pp. 5, 61, 63).
  - The heading "4.5.8.3 Settled in CIRISAgent, carried as-is" (p. 59).
  - "the two symbol-count keys are retired with fountain storage; and the new shaping and onion keys" (p. 34).
  - "the only previously-enforced scope" (p. 54).
- **Repeated self-justification blocks.** "Why this is still 1+4 … Zero new structural primitives" appears on pp. 6, 16, 17 and 18. "1+4 preserved … No new structural primitive" appears on pp. 42, 53, 57, 58 and 68. "The compositional reach is the point" (p. 8) is pitch, not rule.
- **Editorializing.** Examples:
  - "which is the justice the larger-collective form is built for" (p. 3)
  - "This is autonomy in mechanism" (p. 4)
  - "this is the autonomy/justice seam" (p. 11)
  - "below that scale the machinery is theater" (p. 43)
  - "the pace of change is so great and the need so dire" (p. 44)
  - "A community in which reported abuse survives has self-identified" (p. 66)
  - "humanity cannot be un-extincted" (p. 39)
  - "malformed producers are usually buggy clients, not attackers" (p. 60)
- **Stale section labels.** Examples:
  - "per S0.5" and "per S0.6" in both canonical-bytes blocks (pp. 30, 33)
  - "the §9 kill-switch quorum" (p. 41)
  - "CC 3.4.13 Q7-3" (p. 65)
  - A code comment that says "NOT accord_invoke.v1" when the label is now `.v2` (p. 32)
- **The consumer-UI rule names "the four kinds" and the "four registered kinds" (p. 32).** It lists constitutional, notify, drill and lifecycle:active. The signatures table registers a fifth, `lifecycle:confirmed` (p. 31), which has no UI rule.
- **Hard-case names disagree.** The policy paragraph refuses with "federation_community_consensus_protocol_violation" (p. 68). Elsewhere the hard case is `hard_case:community_consensus_protocol_violation` (pp. 9, 10).
- **The Annex F tiers skip Tier 3.** The text lists "Tier 1 … Tier 2 … Tier 4 fleet shut-down" (p. 33).
- **"Triple" survives where the roster is meant to grow.** The text says "the roster is being widened … until about seven hold seats" (p. 36). Yet "the HUMANITY_ACCORD triple" (pp. 37, 52, 58) and "the full steward-triple per CC 3.4.3" (p. 58) remain.

## Opportunities
- Replace the HUMANITY_ACCORD family block and the 2-of-3 sentence on p. 37, and the CEG halt row on p. 8, with "strict majority of the standing roster (CC 4.2.6)". One edit removes the sharpest contradiction in the volume.
- Make the p. 52 4.5.4 rules 2–3 point to the 48-hour recovery of 4.5.13 (pp. 53, 66). Make the p. 66 "harm report defaults to removal" state how it meets the floor on p. 68, or say removal is outside the floor. That is a few sentences, but it needs the steward's ruling on which text wins.
- Fix the subkind count on p. 3 ("three codified subkinds: geographic, infrastructure, public"). Add `public` to the plaintext exception on p. 5. Narrow the p. 61 deferral to "other subkinds".
- Change the Neighborhood-association row on p. 6 so the constraint resolution is 7 or coarser, or state that the constraint is a coarser parent.
- Do a mechanical sweep to strip named projects, file paths, "S0.x/§9/Q7-3" labels, "Option A/B" and the repeated "Why this is still 1+4" blocks. That would cut several pages and leave the rules standing.
- Reword p. 11 to drop "today" and "should this document ever define", so the agent binding rests on custody, as on p. 12.
- Fix the factual errors on pp. 48–50 and 60–62 before a regulator reads them. They are listed under Threats.

## Threats
- **A regulator or lawyer will find factual errors in the compliance pages.**
  - "Microsoft Project Arachnid feed" (p. 62) contradicts "Project Arachnid (C3P, 2017)" in the table directly above it.
  - "H3 resolution 7 hexagons average ~5 km² edge-length" (p. 60) mixes area and edge length. Resolution 7 is about 5 km² in area with about 1.2 km edges.
  - "GDPR Article 9 … consent:deletion_sla SHOULD be ≤ 30 days" (p. 48) and "GDPR Article 9 default ≤ 30 days" (p. 50) attach a deletion deadline to the special-category article.
  - "TVEC mandates a 1-hour removal obligation" (p. 50) uses an acronym that is never expanded and names no instrument.
- **An implementer cannot tell how the halt is counted.** Pages 8 and 37 say 2-of-3 quorum. Pages 30, 38 and 47 say one holder fires, a strict majority confirms, and the roster is M-of-N.
- **A hostile reviewer will quote the moderation contradiction.** Page 52 promises "no moderator-less window" and immediate fail-secure. Pages 53 and 66 allow 48 hours without a moderator. Page 66 lets silence remove content, while p. 68 says silence lands nothing without a floor of approvals and one voice never decides.
- **Unsourced numbers in prose.** Examples:
  - The hardware trust multipliers "0.95 … 0.9" (p. 35)
  - "~75-80% transparent translation rate" (p. 63)
  - "roughly a quarter coerced suffices" (p. 39)
  - "Witness diversity per NodeCore P10 (N=3 default)" (p. 42)
  - "CCPA default 45 days" (p. 50)
  - "Tier-2 … 30-minute time-to-act" (p. 33)
- **Overclaim.** "The 1+4 lockdown holds across this entire surface: the wire format is rich enough for democratic-participation use cases" (p. 8) rests on a table of compositions with no register row. The ballot row maps "no" to `stance: revoked` ("'no' or withdrawal of support", p. 6), which conflates a vote against with withdrawn consent. It also puts votes on attributable consent records.
- **Leftovers from earlier designs.**
  - "One exception stands until the shipped bundle is re-minted with labels" (p. 21) and "An edge admitted before a substrate enforced this rule" (p. 20) are migration clauses.
  - The `.v1`→`.v2` label cutover runs a full page (pp. 31–32).
  - The retired domain labels "ciris.accord_contest.v1 and ciris.accord_restore.v1" (p. 40) are still listed.
  - "contest ↔ restore cross-replay" (p. 41) names objects that p. 40 says no longer exist.
- **Disparaging comparison.** The text claims 4.5.4 "closes the unmoderated-space-for-predators gap of relay-level (Nostr) / immutable-store (IPFS) / lax-instance (fediverse) models" (p. 52). That is a comparative claim about named projects, and it invites rebuttal.
- **The front page and p. 27 point to evidence in different ways.** The front page says formal models are "named in the register's witness column" (p. 1). Page 27 gives a repository path instead.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 37, 8 vs 30, 47 | contradiction | "The 2-of-3 multi-sig verifier … is the quorum:2/3 consensus_protocol enforcement" contradicts "A constitutional halt is one holder's signature … never a fixed 2-of-3" | Rewrite the p. 37 family block and paragraph and the p. 8 table row to the CC 4.2.6 strict-majority-of-standing-roster rule |
| 2 | 52 vs 53, 66 | contradiction | "no moderator-less window" and immediate fail-secure contradict the "48-hour no-moderator recovery" | Make 4.5.4 rules 2–3 defer to the 4.5.13 recovery, or drop the 48 h (needs a ruling) |
| 3 | 66–67 vs 68, 50 | contradiction | "doing nothing within the window removes the content" contradicts the floor "before silence may land it" and the duty-holder gate | State whether harm removal is inside or outside the policy floor (needs a ruling) |
| 4 | 3 vs 17, 61 | contradiction | "The two codified subkinds are geographic and infrastructure" while `public` is codified; p. 61 defers all non-geographic subkinds | Correct the count to three, add `public` to the p. 5 exception, and narrow p. 61 |
| 5 | 4 vs 6 | contradiction | A resolution-7 proof must be contained in a resolution 8–10 constraint | Fix the table row resolution, or define containment as a coarser parent |
| 6 | 48, 50, 60, 62 | other (factual) | "Microsoft Project Arachnid", "~5 km² edge-length", the GDPR Art. 9 deletion SLA, and the unexpanded "TVEC" | Correct each fact, or delete the informational claim |
| 7 | 17, 21, 38, 43, 52, 54, 55, 62, 64 | editorializing | Named-project comparisons (Nostr, IPFS, fediverse, Bluesky, Linux, Keybase, Signal, "SOTA-aligned") | Delete them, or move them to the Charter |
| 8 | 27, 35–37, 41, 44, 49, 59, 68 | stale | Code and file pointers and stale section labels (S0.5, §9, S9.2, Q7-3, round2, "Settled in CIRISAgent") | Do a mechanical sweep that replaces them with CC numbers or register references |

## Rendering
- p. 28: the 4.2.1 first line `(IncidentSeverity::INC…` runs off the right edge, and the value is clipped.
- p. 31: a literal backslash prints in "constitutional \| notify \| drill".
- p. 46: the `ci_axis ∈ {sender, … recipient_receive,` line overflows the right margin.
- p. 47: "409 IDEMPOTENT_CONFLICT" runs into the right margin.
- p. 52: "scope ⊇ {moderate|takedown|r" is clipped at the page edge.
- p. 56: "attesting_key_id ∈ subject_of(content_sha" is clipped at the page edge.
- p. 61: "Policy M evaluate_subkind_admission" overflows the right margin.
- p. 44: the declared-privilege row titles render as long full-paragraph bold headings, and the cell labels ("Bounded by / Exit / Isolation") render as small detached lines. The register reads as broken layout.
- Throughout (pp. 3–17): inline code after a colon prints a double space, for example "cohort_subkind:  geographic" and "cohort_scope:  community".
- p. 61: the last bullet "Address affiliations" has no closing punctuation, and the list ends abruptly.
- pp. 27, 69: these Part-end pages are about 85% blank. This is acceptable but worth noting.

## Effort estimate
About 10–14 hours. Roughly 6 hours are a mechanical sweep for comparisons, pointers, stale labels, 1+4 boilerplate and the seven overflow lines. The halt-quorum, moderator-window, removal-floor and subkind contradictions need the steward's rulings before about 4–6 hours of re-drafting.


# The Wire (ciris_constitution-1.0-rc11-wire.pdf, 110 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The byte-level core (2.3.2.1, 2.6.1.x, 2.6.1.7, 5.4.1) is implementer-grade, but the volume carries at least five genuine cross-page contradictions, a layer of stale section numbers from an earlier document, and Part 5 prose that compares, markets and narrates history in ways the house rules forbid.

## Strengths
- The front page states scope, binding audience, promise and exclusions in five short paragraphs, and points at the generated artefacts (p. 1).
- The canonical-hash preimage rule is fully pinned, with production, rejection-not-repair (P1), an injectivity argument (P2), positive vectors and reject vectors (pp. 15-18).
- The omit-vs-materialize rule is stated once and illustrated with a worked attack and a verification flow (pp. 29-30, 36).
- The signed-object section closes the member set, names every refusal token and ships vectors (pp. 37-60).
- The record_id CBOR profile pins major types and gives three hex vectors that exercise integer-width edge cases (pp. 98-99).
- The shaping defaults say plainly that they come from a model, not live measurement (p. 102).
- The onion section states what it does not yet buy (p. 110, item 8).

## Weaknesses
- Section references from an older numbering survive in normative text and code blocks: "S4 default" (p. 29), "per S5.2.1", "S8" (p. 36), "S5.6.8.2", "S8.1.12.4", "S7.7", "S10.1.4" (pp. 72-73), "per S0.6", "per S0.5" (pp. 74-75), "S10.5.8.2 namespace" (p. 88), "CEG §11" (p. 99), "CEG §19.3" (p. 100), "CEG §19.4" (p. 101).
- History and design narrative appear inside rules: "RC1: pull-only multicast; push tree → 1.x" (p. 12), "pre-FSD-003 reference Registry" and "since FSD-003" (p. 15), "the name cosignatures[] is retired" (pp. 10, 60), "CIRIS-AV-INNER-V1 is retired" (p. 89), "This answers the open question of how to attest about un-enrolled parties" (p. 15), "As shipped." in a normative merge table (p. 78).
- Code and implementation pointers sit in rule text: "tools/audit_emitted_dimensions.py" (p. 21), "Generated from constitution/signed_object.tsv by tools/build_cc_signed_object.py ... Edit the TSV." (p. 37), "cirisnode_contributions V054 partial indexes (planner-AND'd)" (p. 70), "CIRISPersist V058 R1/Q1 machinery" (p. 78), "from registry_signing_keys table" (p. 96), "land in the Rust handlers + OpenAPI export" (p. 96), "track the README Version: field" (p. 96), "LANGUAGE_PRIMER.md companion" (p. 29), "MISSION.md" (pp. 72, 92).
- Comparative claims about other projects: "No prior identity system (PGP, SPKI/SDSI, W3C VC) types epistemic-error-admission" (p. 27); "the pattern proven by Nostr kind-ranges and Matrix reverse-DNS namespacing" (p. 62); "This is exactly how Element ignores info.mimetype ... and Synapse ignores ..." (p. 83); the renderable-set table cites Signal, WhatsApp, Mastodon, Threema, Element and a "Mastodon disabled HEIF 2026-09-15" date (p. 83); "Chromium's default PNG decoder is the Rust png crate ... Android 17 moves AAC in-process" (p. 84); the "Position" paragraph opens "Against the field" and describes "surveyed systems" (p. 110); "What CEG adds beyond systems that ship default privacy" (p. 5); the ERC-8004 study figures in the adversary table (pp. 3-4).
- Marketing and editorializing: "The load-bearing claim from ciris.ai/cewp: ... You don't need a privacy policy to keep family photos off the federation" (p. 72); "The strongest privacy guarantee in the system" (p. 72); "the thirteenth path on the CC 1.7 claim and the most product-complete" (p. 85); "The breadth confirmation: a full realtime group-communication platform" (p. 86); "The honest line" (p. 5); "the surveillance backdoor this framework refuses" (p. 5).
- Numbers quoted in prose with no visible source: "~65% of activity stays local in the cewp scaling model" (p. 74); "~20–40% MDC compression overhead" (p. 87); "ML-DSA-65 sign ~330 µs" (p. 82); "A single shape carries thirteen distinct content cases" (p. 20); the "~30%/hr" churn and "~2 Tbps content fan-out" inputs to the removal-coalescing arithmetic (p. 70); "default rotate-forward, 30-day window" for an unnamed "companion per-community archive-policy section" (p. 103).
- The versioning section still describes the document as a 0.x Public Working Draft: "The 0.x series indicates this specification is a Public Working Draft ... consumers MUST treat 0.x as unstable until 1.0 publication" (p. 62), in a volume titled edition 1.0-rc11.
- The normative references table lists FIPS-204 twice (pp. 62, 63), cites SFrame as "draft-ietf-sframe" (p. 63, p. 84), and omits documents the text relies on normatively: RFC 4648 (p. 31), RFC 6962 (p. 76), RFC 8949 CBOR (p. 99), RFC 5869 HKDF, XChaCha20-Poly1305 (pp. 100-102), X-Wing and draft-ietf-hpke-pq (pp. 103-104), RFC 9605/SFrame.
- The readership pointers read "read CC 1.13-CC 4.5 normative" and "read CC 8.2-CC 8.1" (p. 29); the second range runs backwards and neither range is in this volume.
- A "Foreword" is numbered 2.6 and sits in the middle of Part 2, after the reasoning grammar (p. 28).
- Undefined threat identifiers appear without a pointer: "AV-50" (p. 34), "AV-59 / AV-60 / AV-61" (pp. 77, 80), "F-AV-FRONTRUN" (p. 78), "F-3 detector" (p. 13), "D08 autonomy claim" (p. 20).
- The example key_id "eric-moore-k7f3qd2pza" uses the steward's name (p. 67).
- The section heading "Inside the signed bytes — members persist types" is missing a word (p. 40).

## Opportunities
- One mechanical pass that maps every "S<n>" and "CEG §<n>" to the current CC number would remove the most visible sign of an earlier document (pp. 29, 36, 72-75, 88, 99-101).
- Moving the "Position" paragraph (p. 110), the renderable-set rationale (pp. 83-84), the ERC-8004 study figures (pp. 3-4) and the cewp quotations (pp. 72, 74) to the charter or a review note would clear most comparison and marketing findings at once.
- Rewriting the versioning bullets (p. 62) for the 1.0 line removes a direct conflict with the volume title.
- Completing the normative references table (pp. 62-63) gives an implementer one list to check against.
- Replacing the inline tool and table names (pp. 21, 37, 70, 78, 96) with "the register row" or "the generated artefact" keeps the rules free of code pointers.
- A single sentence on the endianness convention, stated once in 2.6, would settle the delivery-receipt question below.

## Threats
- **Post-compromise security is both a non-goal and available.** Page 2 says: "a compromised current member's key is not self-healed by a key-update the way MLS PCS provides." Page 72 says: "Post-Compromise Security (PCS) is AVAILABLE (inherent to TreeKEM key-updates ...) and is OPTIONAL, operator-enabled." A security reviewer will read these as opposite claims.
- **The front page promises a fixed-size envelope that the body denies.** Page 1 promises "a fixed-size substrate envelope". Page 101 says "There is no fixed envelope size for all outbound traffic: uniform frames add privacy only where both ends shape", and shaping "is off by default" (p. 102).
- **Byte identity is a target on one page and closed on another.** Page 1 says "byte identity across implementations as a target with a published vector set as its proof". Page 31 says "byte-identity across conformant implementations is closed by construction".
- **The K_record_id derivation contradicts itself.** Page 98 says K_record_id is a bare HKDF-Expand over the raw exporter_secret and implementations "MUST NOT route this label through ... RFC 9420 MLS_Exporter()". Page 107 says "S_dest is a separate exporter from S_record ("ciris-scope-record-v1", which feeds K_record_id and K_symbol, CC 5.4.1)". No label "ciris-scope-record-v1" appears in 5.4.1.
- **The base64 alphabet contradicts itself.** Page 31 says every base64 field "MUST use the RFC 4648 §4 STANDARD alphabet, WITH padding", and a URL-safe variant produces "a silently non-verifying signature". The cosign request bodies on pp. 74-75 declare "ed25519_signature_b64": "<base64-url>" and "mldsa65_signature_b64": "<base64-url>".
- **The onion tier is called Sphinx but cannot be Sphinx.** Page 2 names the tier "Sphinx onion routing". Page 109 says "Because ML-KEM cannot be blinded, the header carries one KEM ciphertext per hop", which drops Sphinx's defining blinded header. A cryptographer will catch this at once.
- **The volume is not self-sufficient for conformance.** Page 1 says conformance "is judged against this volume, The Dictionary and the reader's policies, and against nothing else". The CCC profile requires "at least Policy A (CC 4.4.3.8)" and "default aggregation rules from CC 4.4.2" (p. 14). Page 68 lists CC 3.4, 3.5 and 4.4 as the conformance surface. None of those sections is in this volume.
- **One implementation is named as the decoder for all others.** Page 66 says "The reference implementation is CIRISVerify (FSD-003); every other component decodes through it." Page 67 says "FSD-003 owns that change and this Part follows it." Both cut against the second-independent-implementation goal on p. 1 and place an external design document above the text.
- **The stored-content encoding may be a leftover.** Page 103 says "a sealed A/V chunk is encoded with RaptorQ into symbols". Page 47 sends above-cap payloads to "the fountain plane", while p. 35 calls the same place "the blob plane". If the fountain-code design has been dropped, these are stale. If it has not, the two plane names still need to agree.
- **The delivery receipt is little-endian while everything else is big-endian.** The receipt preimage encodes "epoch (u64 LE)" and "K (u64 LE)" and leaves the width of "len(...)" unspecified (p. 92). Every other integer in Part 5 is big-endian (pp. 84, 88, 89, 100). A second implementer will guess.
- **It is unclear whether revoked_after is signed.** Page 23 says a revocation "MAY declare revoked_after", then lists the "eight members" the signed revocation binds without revoked_after.
- **Unsourced CVE numbers and dated facts will age badly.** The p. 83 table carries numbers such as "CVE-2026-20616" and "CVE-2026-28737", plus a vendor-status date, inside a Part that is meant to state rules.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 2 vs 72 | contradiction | PCS is listed as a non-goal ("not self-healed") and also as "AVAILABLE ... OPTIONAL, operator-enabled" | State one posture. For example, say PCS is off by default and available when the operator turns it on, and change the p. 2 non-goal to match. |
| 2 | 1 vs 101 | contradiction | The front page promises "a fixed-size substrate envelope", but p. 101 says there is none and shaping is off by default | Reword the promise to "fixed-size frames on a shaped link", or drop it. |
| 3 | 98 vs 107 | contradiction | K_record_id comes from a raw exporter_secret HKDF-Expand on one page and from a "ciris-scope-record-v1" exporter on the other | Align p. 107 to p. 98. If S_record exists, define it in 5.4.1. |
| 4 | 31 vs 74-75 | contradiction | Standard padded base64 is mandated, but the cosign bodies declare "<base64-url>" | Change the cosign bodies to standard base64, or carve out an exception for the endpoint. |
| 5 | 29, 36, 72-75, 88, 99-101 | stale | Section numbers from an older document ("S4", "S5.2.1", "S8.1.12.4", "S0.6", "S10.5.8.2", "CEG §11", "§19.3", "§19.4") | Do one renumbering pass to CC numbers. |
| 6 | 11 | rendering | The witness_quorum description ends "MUST equal ⌊" and the formula is cut off | Fix the floor/ceiling macro so the formula renders. P. 43 has the full text. |
| 7 | 2 vs 109 | contradiction | The onion tier is named "Sphinx", but the packet carries "one KEM ciphertext per hop" because ML-KEM cannot be blinded | Drop "Sphinx" or say "Sphinx-like layering without blinding". |
| 8 | 62 | stale | The versioning section says the specification is a 0.x Public Working Draft | Rewrite the section for the 1.0 line. Also remove the literal "**DEPRECATED in 0.X**" marker. |

## Rendering
- p. 11: the witness_quorum cell is truncated at "MUST equal ⌊", so the formula is missing.
- p. 16: "(case-preserved — some IDs are case-sensitive) ... display-name." runs past the right margin.
- p. 24: "at proxy-establishment" runs past the right margin.
- p. 25: "scope: ["personhood_const" is clipped off the page edge, so the scope value is unreadable.
- p. 30: "effective_epistemic_mode(envelope) = envelope.epistemic_mode if present else" runs past the margin.
- p. 31: the heading "2.6.1.2 Per-field encoding table (informational)" is orphaned at the page foot, with its table on p. 32.
- p. 32: "subject_sha256_ed25519_raw":"<64 overflows the table's right edge.
- p. 33: "recovery_commitments":{"<holder_key_id>":"<64 overflows the table's right edge.
- p. 37: "attestation_" overflows at the right margin.
- p. 62: the literal Markdown "**DEPRECATED in 0.X**" is printed with its asterisks.
- p. 70: "federation_stream_chunks(stream_id, seq)" overflows into the next column and overlaps "Same".
- p. 73: "identity_occurrence's" overflows the right margin.
- p. 74: "cohort_scope:" at line end overflows the right margin.
- p. 77: "hard_case:consent_revocation_promotion_overdue" overflows the right margin.
- p. 79: the heading hyphenates as "subjec-t-set emptiness".
- p. 88: "CHUNK_CODEC_LAYER_LEN" overflows the right margin.
- p. 19 and p. 105: literal Markdown backticks appear inside code blocks ("A `cohort_scope: family` contribution", "`HMAC-SHA3(...)`").
- pp. 38-60: the landscape tables print the page number rotated in the left gutter, and the 2.6.1.7 member tables run 23 pages with no running caption beyond the column header.
- p. 86: there is an unusually large vertical gap after the 5.3.3.2.1 heading.
- Throughout: straight double quotes render as typewriter quotes in prose, for example "privacy" on p. 2 and "outsider" on p. 5.

## Effort estimate
About 16 to 24 hours. Roughly half is mechanical work: renumbering, rendering fixes, removing code pointers and completing the references table. The other half needs the steward's rulings on post-compromise security, the fixed-size envelope promise, the K_record_id derivation, the fountain-code question, receipt endianness and the volume's conformance boundary.


# The CIRIS Constitution: The Dictionary (ciris_constitution-1.0-rc11-dictionary.pdf, 109 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The registry tables and the case/version rules are strong, but at least five pairs of pages contradict each other. The family-membership and age-band sections keep an earlier design. A long informative tail makes claims about other projects and names real people and vendors, which the house rules forbid.

## Strengths
- The front page says exactly what the volume binds and that the generated manifest wins over the prose when they differ (p. 1). Section 3.1.7 repeats that the manifest is the count of record (p. 27).
- The namespace rules R1 to R4 in 3.1.7 are precise and testable. They cover byte-exact case handling, the mandatory version segment, variadic `*`, polarity as an admission rule, and malformed forms that never fall into open vocabulary (pp. 27–30).
- The `session:*` lease rule bounds the lease length and gives the leftover risk by name: "a claimant can still back-date `claimed_at` … by at most one lease (24 h)" (p. 15).
- Honest non-claims recur, for example "No possession challenge yet (stated)" (p. 19), the KEM-compromise gap (p. 58), and "Deferred, not denied" for multi-tenant hosting (p. 92).
- The capacity composite rule gives the reason for `min` over a product. A product turns positive when an even number of factors are negative (p. 31).
- The adult-incapacity and minor-protection sections are complete, normative and adversary-framed (pp. 96–107).

## Weaknesses
- **The volume uses three registry-row layouts.** Most rows are four-column tables. Others are paragraph blocks with "Description:/Polarity:/Reserved?:" labels (pp. 12, 16, 21, 31–32, 37–38). The 3.1.2 table has no Reserved column at all (pp. 5–7). The Reserved cell for `identity_amendment:v1` is empty (p. 23).
- **Internal labels go undefined.** Examples are "M-1" (p. 22), "Counter-RII" (pp. 26, 90), "F-3" (p. 31), "F-AV-DORMANT" (p. 39), "F-AV-ROLLBACK" (p. 67), "Piece 10" and "Corridor Dynamics Piece 6" (pp. 39–40), "AV-17 / AV-42 / AV-88" (pp. 57–58, 76), "OQ-1..OQ-3" (p. 90), "§Q B2" (p. 64) and "P8 allegation types" (p. 34).
- **Code and file pointers appear inside rules.** Examples are "`tools/build_cc_namespace.py`" (pp. 2, 27–28), "Cited from CIRISRegistry/MISSION.md §3 + FSD-001 + protocol/ciris_registry.proto" (p. 2), "22 NEVER_ALLOWED categories from prohibitions.py" (p. 26), "Persist's `federation_attestations.attestation_id`" (p. 109), "CIRISNodeCore FSD/MEDIA_SHARING.md §4" (p. 77) and "(CLAUDE.md discipline …)" (p. 67).
- **Some text reads as history or transition.** Examples are "CIRISRegistry, folding into CIRISServer" (p. 2) and "Until that cut, the text below stands as it is" for all of 3.3.9 (p. 65). Others are "the two symbol-count keys are retired with fountain storage … and the new shaping and onion keys" (p. 35), "Until a substrate's door carries this family … once the family ships" (p. 36), "live_stream (Phase 2)" (p. 75) and "the interim using a registry_witnesses table" (p. 93).
- **Some words editorialize.** Examples are "the bulk-surveillance posture CIRIS rejects" (p. 38), "The novelty budget is spent once, on the kernel" (p. 72), "the exception that proves the rule" (p. 96), "Guardianship/conservatorship is the most abuse-prone instrument in human law" (p. 96) and "The example demonstrates the clean orthogonality" (p. 53).
- **The R-labels mean two different things.** 3.1.7 R1–R4 are namespace rules cited everywhere as "CC 3.1.7 R1". 3.4.14 reuses R1–R5 for marking rules (p. 108). 3.4.13 uses Q1–Q7 and switches its cross-references from "CC 3.2" to "§3.2" (pp. 102–106).
- **The CC 1.7 path ordinals appear out of order.** The order is "Fifteenth path" (p. 58), "Twelfth path" (p. 61), "Fourteenth path" (p. 69) and "Sixteenth path" (p. 68), and the reader cannot check them from this volume.
- **Some prose numbers have no visible source.** Examples are "multilateral netting removes ~96% of gross obligations" (p. 71), "Berlin businesses cashed out 90% of CRC" (p. 72), "N=3 default" (p. 36) and "> P75" (p. 37).

## Opportunities
- **Cut the "informative" prior-art tail of 3.3.10.1.** These are "The prior-art record" and "Attempted, and the lessons" on pp. 71–72. Also cut the CVE and Mastodon paragraph (p. 75) and the "Signal, Bluesky's client, Threema, Briar, SimpleX and Delta Chat all do this" sentence (p. 77). That removes almost every comparison with another project in one edit, and no rule changes.
- **Fix underscore escaping once in the pipeline.** One fix would clear the doubled underscores ("subject__kind") and the literal `\|` and `\'` across about 30 pages.
- **Normalize every registry row to one four-column table.** Fill the empty Reserved cell on p. 23 and add a Reserved column to 3.1.2. The volume then reads as one dictionary.
- **Replace the internal labels with section numbers or plain words.** Covered labels include M-1, F-3, AV-nn, OQ-n, Piece n, §Q and P8. Deleting a label costs nothing.
- **Rewrite the family-membership ceremony and the household example to the widening plane.** These are 3.3.4 on pp. 51 and 52–53, to follow the widening plane of 3.1.3.2. That one edit removes the volume's worst contradiction.
- **Make every age-band example use `age_self_declared:band:{band}:v1` and full versioned forms.** This applies on pp. 94 and 104.

## Threats
- **Contradiction on how members are added.** On p. 17 the volume says "A supersede never adds a member (normative) … a roster-growing supersede is refused. Every addition goes through the widening plane." On p. 51 it says "Proposer (any current member) emits a new `family` Contribution superseding the current family Contribution … with the new membership list." The p. 53 example also has "Bob proposes a supersedes Contribution adding {carol_phone_root} … `founder_only` admits on Bob's signature alone". That breaks the two-consent rule on p. 16: "Admission … is two consents, never one … the joiner's own". An implementer following 3.3.4 builds exactly the door that 3.1.3.2 refuses.
- **Contradiction on the self-declared age shape.** On p. 7 the volume says "the two-segment `age_self_declared:{band}:{version}` is not a registered shape." On p. 94 the code block shows "`age_self_declared:{band}:v1` … e.g. `age_self_declared:adult:v1`". On p. 104 it says "`age_self_declared:minor` SUFFICES", which has no `band` segment and no version, against the R3 rule on p. 29. A child-safety rule written with a malformed dimension is the worst place for this.
- **Contradiction on the age-band vocabulary.** On p. 7 the closed set is "`{band}` ∈ minor | adult | under_13 | 13_15 | 16_17 (closed …)". On p. 94 it is "AgeBand ∈ { minor, adult }", and the code block says "band in { minor, adult }".
- **Contradiction on Goal scales.** On p. 39 the volume says "The scales admitted on the open vocabulary are `self`, `cohort` and `federation`." On p. 40 it says "`federation` is not a belonging scale … it is a `cohort_scope` value and MUST NOT be added to `{scale}`. The `{scale}` vocabulary above has seven tokens", and `cohort` is not among the seven.
- **Contradiction on licensure authority.** On p. 2 the volume says "authority is conferred by quorum, never by `delegates_to`". On p. 93 it says "`licensure:{authority_id}` is open-emitter … anyone may be an authority under their own key". p. 67 says the same: "it is not a gate on who may be an authority — anyone may, under their own key". The p. 2 text is a leftover from the roster design.
- **The closed accord leaf set disagrees between two pages.** On p. 78 the volume says "Its leaves are closed … the rows below are the whole family". The table on p. 79 omits `accord:lifecycle:confirmed`, which the p. 5 catalogue lists. A consumer building the closed set from 3.4.1 would refuse a registered leaf.
- **The count is wrong and the kind is mislabeled.** On p. 79 the volume says "Four substrate-emitted prefixes:". It then says they "are not prefix families", and the table lists nine hard-case kinds (pp. 80–81).
- **Real people, vendors and dated products are named.** The volume names "Britney-style capture" and "the Britney pattern" (pp. 96–97, 100). It gives "Default model: Claude Opus 4.7" (p. 37), which is a stale model name inside a rule. It names "Stripe" and "Portal+Stripe" (p. 67), "USDC on Base via x402" (p. 68), "Apple Declared Age Range / Google Play Age Signals" (p. 103) and Twitter, Roku and Nest (p. 52). It also uses real founders' names as key ids "eric-moore-key", "eric-kudzin-key" and "haley-bradley-key" (p. 52).
- **Claims about other projects could be read as disparaging.** The volume says "HoloFuel still unshipped 8+ years after its token sold … no swap as of mid-2026" and "Circles UBI died at the rail boundary … the coop folded January 2024" (pp. 71–72). It says "Mastodon disabled HEIF / AVIF on 2026-09-15" (p. 75). A hostile reviewer will quote these.
- **Some claims are stronger than their evidence.** Examples are "closing the last form of internet traffic from the completeness audit" (p. 69) and "the EDPB's own blockchain guidance recommends exactly summarize-and-delete" (p. 70). Another is "given national directives treating ML-KEM-768 as interim with retirement horizons near 2030" (p. 47). None is cited.
- **A date appears on a rule.** The volume says "A deployment claiming CC conformance after 2026-08-02 MUST …" (p. 108).
- **A field name may be stale.** 3.5.1 orders composers by "`signed_at`" (p. 109), while the rest of the volume uses `asserted_at` as the signed instant (pp. 15, 17, 43).

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 17 vs 51, 53 | contradiction | "A supersede never adds a member … roster-growing supersede is refused" vs the family ceremony "superseding … with the new membership list" and Carol "admits on Bob's signature alone" | Rewrite the 3.3.4 ceremony and the worked example to use proposal, acceptance and widening per 3.1.3.2 |
| 2 | 7 vs 94, 104 | contradiction | "two-segment `age_self_declared:{band}:{version}` is not a registered shape" vs `age_self_declared:adult:v1` and `age_self_declared:minor` | Use `age_self_declared:band:{band}:v1` everywhere, and give full versioned forms in 3.4.13 |
| 3 | 39 vs 40 | contradiction | Scales admitted "self, cohort and federation" vs "federation … MUST NOT be added to `{scale}`" | Restate the admitted scales from the seven-token list (steward ruling) |
| 4 | 2 vs 93, 67 | contradiction / stale | "authority is conferred by quorum" vs "anyone may be an authority under their own key" | Delete the quorum clause on p. 2 |
| 5 | 70–72, 75, 77 | other (comparisons) | Prior-art and "lessons" paragraphs about Holochain, Circles, SSB, Hypercore, Mastodon, Signal and others | Delete, or move out of the Parts into a non-normative essay |
| 6 | 96–100, 37, 52, 67 | editorializing / stale | "Britney" references, "Claude Opus 4.7", founders' names as key ids, Stripe and CLAUDE.md | Strip proper names and vendor names, and use neutral placeholders |
| 7 | 78–79 | contradiction | "the rows below are the whole family" but `accord:lifecycle:confirmed` (p. 5) is missing | Add the row to the 3.4.1 table |
| 8 | 65 | stale | "Until that cut, the text below stands as it is" governs all of 3.3.9 | Either land the affiliation form or state the rule without the pending migration |

## Rendering
- **Doubled underscores in body text, headings and table cells.** Examples are "subject__kind", "sub__kind", "external__content", "subject__key__id", "x25519__base64", "ml__kem__768__base64" and "reticulum__x25519__pubkey". This is widespread on pp. 40–56 and 74.
- **Literal backslashes.** Examples are "`content \| epoch \| stream`" (p. 48), "`family \| community \| affiliations`" and "`phone \| laptop`; … `server \| embedded \| service \|`" (p. 64), and "dimension\'s" (p. 85).
- **Markdown link artifact.** "[CC 1.13.3.4]" appears in square brackets (p. 103).
- **Unresolved reference.** "§Q B2" and "the CC 6.1.5.2 corpus-replication (§Q) track" point nowhere in this volume (p. 64).
- **Garbled reference.** The text reads "The CC 1.13+4 lockdown holds", probably meaning CC 1.7 1+4 (p. 72).
- **Code lines clipped or overflowing the right margin.** Examples are "ed25519_signatur…" (p. 9), "attestation:agent_integrity)" (p. 30), "EnvelopeKind::IdentityOccurrence" (p. 57), "attestation:" (p. 86), "{agent, lenscore_detector}." (p. 93), "attesting_key.identity_type" (p. 94) and "discrimination," (p. 26).
- **Table cells split into false extra rows.** This happens in EncryptionPubkeys, TransportDestination and DeviceClass, where one cell's text continues in a new blank-keyed row (p. 56).
- **Code-block columns wrapped mid-phrase.** In the common field set, "the", "path", "allocation" and "absent in clear" land on orphan lines (p. 76).
- **Stranded headings with large blank areas.** "Transport-capacity leaf (registry row)" sits at the page foot with half the page empty (p. 20). There is a large blank after 3.1.9.1 (p. 33). The code block on p. 24 has only "manifest {" before the page break.
- **Broken table cell.** The variant name breaks as "X25519MlKem768Aes256GcmHkdfSha 256" (p. 47).
- **Orphaned closing quote.** The quote in the beneficence row lands on its own line, and straight quotes are used throughout the principle rows (p. 25).
- **Section numbering gap.** The numbering goes 3.1.10 to 3.3 with no 3.2 in this volume (p. 40). The front matter implies this, but the gap is never stated where it occurs.

## Effort estimate
About 12–16 hours. Roughly half is mechanical: the underscore and backslash escaping, margin overflows, table normalization, label and pointer removal, and cutting the prior-art tail. The other half needs the steward's rulings on four points. These are the family-membership ceremony, the age-band shape and vocabulary, the Goal scale set, and the 3.3.9 affiliation migration.


# The CIRIS Constitution: The Evidence Register (ciris_constitution-1.0-rc11-register.pdf, 115 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The generated register table (pp. 59–115) mostly works, but the volume breaks its own promise on p. 1. Rows are marked established while their own text says the evidence is pending. A placeholder section sits beside "Open stubs: 0". The Part 8 prose in front of the table carries comparative claims, rc history, dated rulings, contradictory acronyms and a legacy benchmark harness.

## Strengths
- The front matter states the contract precisely: what "established", "staged" and "normative" mean, and who is bound (p. 1).
- The strength-grade key separates "an artifact exists" from "the sentence is true". It warns that a `lean:` pointer certifies only that an object exists (pp. 19–20).
- The "Known limits of the register" paragraph names two real gaps in plain words: terminology validation, and strength not being a column (p. 20).
- The k_eff borrowing is credited plainly, with "no priority claim over k_eff" and a full citation table (p. 18).
- Annex J's research section is unusually candid. It gives CIs and p-values, says "architecture is not evidence", and states what is not established before what is (pp. 53–54). It also sets an admissibility standard for future numbers (κ ≥ 0.7, two-axis form; p. 54).
- The counts on p. 59 add up: 370 + 103 + 30 + 0 = 503.
- Most register rows give a resolvable symbol path. Formal-model rows name their invariants, for example pp. 70, 81, 92, 105, 109 and 112.

## Weaknesses
- **Rows are established without published evidence, against the p. 1 rule.** Page 1 says "A row is *established* only when the pinned manifest of the owning repository publishes the named symbol in a backed state". On p. 87, CC 3.4.5 is "established" while its own text says "the manifest does not yet publish it". On p. 66, CC 2.6.1.3 is "established" with "freeze-gate vector pair pending".
- **The stub registry contradicts a live placeholder.** Page 58 says "**Open stubs: 0.**" Page 21, at 8.6.4, carries "[source content to migrate … not present in this snapshot.]".
- **WBD means two things.** It is "Wisdom-Based Deferral" on p. 59 (CC 1.9) and in "WBD tickets" on p. 21. It is "Wisdom Bank Database (WBD)" on pp. 46 and 51.
- **The EU AI Act article for human oversight is wrong in Annex I.** Annex C maps "Art 14 Human oversight" and "Art 16 Provider obligations" (p. 23). Annex I says "human oversight (Art. 16)" and lists "Art 16 Human Oversight" (pp. 48–49), and p. 53 repeats "EU-AI-Act Art 16".
- **Comparative claims and history appear throughout §8.3.**
  - "Compared with nine networks (Nostr, Matrix, Mastodon…)", "categorically stronger" and "CEG is the only model that fails secure" (pp. 8–9).
  - "Secure Scuttlebutt hit exactly this wall", "Spamhaus" and "The DAO: 5% turnout" (p. 8).
  - "No prior system separates earned standing…" and "The federation is the first to ship them at scale" (p. 11).
  - "Apple abandoned NeuralHash, the EU CSAR retreated" (p. 9).
  - "C2PA has no consent architecture, no revocation" (p. 14).
- **Some passages are marketing and editorializing.**
  - "CEG's moat is its semantics" (p. 13).
  - "Cheapest win" (p. 16).
  - "a living document with a disciplined heartbeat" (p. 17).
  - "The moderation surface is **complete**" (p. 9).
- **Rulings, dates and rc history sit inside claim text.**
  - "F6 ruling 2026-10-21" (p. 63) and "hard_case joined 2026-10-21, #170" (p. 64).
  - "steward ruling 2026-10-15" (p. 79) and "(steward 2026-10-21)" (p. 100).
  - "measured end to end 2026-10-15 (CIRISServer#769 run 5 …)" (p. 91).
  - "supersedes the 2026-10-11 added grace" (p. 61) and "none defined at rc8" (p. 60).
  - "the pre-rc9 any-occurrence-evicts-at-once door is retired" (p. 84) and "the rc6 CIRIS-AV-INNER-V1 nonce" (p. 102).
  - "(ruling on CIRISServer#537)" (p. 76).
- **Generated claim text is garbled or empty.**
  - "family roster membership change via entr accord" (p. 67).
  - "kind open vocab registration collision g agent files kind platform or target" (p. 68).
  - "raw chain of thought dma csdma" (p. 73).
  - "cohort operational definition calibratio manifold conformity cohort" and "…distributive access resource t" (p. 74).
  - "What this documents" (p. 99) and "Settled in CIRISAgent, carried as-is" (p. 99).
  - Bare slugs that state no claim: "revoked after" (p. 63), "no killswitch no run" (p. 76), "ci axis" (p. 97), "corpus" used as a CC number (p. 115).
- **A banned word appears in claim prose.** The p. 61 row says "drain (requests a graceful shutdown only)".
- **Section numbering is broken.**
  - 8.7 is missing (8.6.4 is followed by 8.8 on p. 21).
  - 8.8.1 and 8.8.4 are missing.
  - Annex D (8.8.3) is printed before Annex C (8.8.5) (p. 22).
  - R9 is printed before R8 (pp. 7–8).
  - Annex J numbers 1–5 for its research section, then restarts at "0. Purpose" (pp. 53–55).
- **Cross-references dangle.**
  - "§3.4 D26 ext" (p. 3), "CC 3.x archive_mode" (p. 3) and "per S0.6" (p. 15).
  - "(§G)" (p. 57) and "(see 5.3)" (p. 55).
  - "Annex B §9" is cited for WA review and recusal (pp. 46, 50, 53), but Annex B item 9 is "Oversight & removal" (p. 22).
  - Registry rows cite the Annex J research results as "CC 8.8.6" (pp. 54, 113), but 8.8.6 is Annex F (p. 24).
- **Rows mark history inside the text.** The Closed-gaps table labels rows "v1.4 T-3 #1/#2/#5" (p. 10). The open items in 8.3.3 are labelled "RC1-1b / RC1-1c / RC1-7" (p. 9).
- **Numbers in prose have no visible source.**
  - "measured at 50%–5.8× of the null" (pp. 7, 33).
  - "validated negatives against a model lying 45% of the time" (p. 33).
  - "k_eff ≈ 7 ± 2, max 9.7 at k = 200" (p. 19).
  - "registry 149 families / 968 vectors" (p. 71).
- **A KPI row states the wrong scope.** F-KPI-1 reads "HITL Coverage (A3-A4) >= 10 %". The note under it says the 10% floor "is not appropriate as a floor for A4" (p. 29).

## Opportunities
- Have the checker enforce the p. 1 rule on claim text. A row that says "pending" or "does not yet publish" is demoted to staged. That fixes pp. 66 and 87 and protects the front-page promise.
- Regenerate the "Namespace-processor evidence row:" claims from real sentences in claims.tsv. Do the same for the bare-slug rows. About 40 rows on pp. 67–115 would then read as claims.
- Strip parenthetical rulings, dates, rc tags and ticket numbers from the Claim column. Tickets can stay in the Evidence column, where the format expects them.
- Move 8.3.2, 8.3.5 and the named-system comparisons in R11–R13 out of the Parts, or recast them as non-comparative statements of the limit.
- Renumber §8 so that 8.7 appears and Annex C precedes D. Fix the R8/R9 order and give Annex J one numbering sequence.
- Pick one expansion for WBD. Make Annex I use Art 14 for human oversight.
- Fill in the empty "Resolution" column of the Closed-gaps table (pp. 10–11), or collapse it into the Status column.
- Change "as of rc5" in the 8.4.2.2 row (p. 113) to a present-state sentence.

## Threats
- **The front-page contract is visibly broken.** An auditor reading p. 1 and then p. 87 sees an "established" row whose text admits the manifest does not publish the symbol. That undermines the register's only job.
- **A religious source is normative while the wire claims tradition neutrality.**
  - Annex F names "Pope Leo XIV, *Magnifica Humanitas* … These paragraphs are the normative source for CIRIS's hard prohibition" (p. 30).
  - Annex G says "These citations are normative for this Annex, not decorative" (p. 38) and puts the "burden of proof … on the CIRIS side of any divergence" (p. 37).
  - Against that, p. 10 says "Wire stays tradition-multiplicity-neutral per CC 1.2", and p. 6 classes tradition authority as T-1, "No Contribution owed".
  - A secular regulator or a hostile reviewer will quote these side by side.
- **Two pages appear to conflict on 2-of-3.** The ciris-canonical row says "every later change is 2-of-3" (p. 77). The halt row says "every threshold is M of N over the standing roster, never a fixed 2-of-3" (p. 91).
- **"One voice" pages appear to conflict.** The amendment row reads "WA quorum → 1-of-n (n the accord roster size; 1-of-3 at genesis)" (p. 96), and G2 relies on "1-of-n accord/steward sign-off" (p. 10). Elsewhere: "no change lands on a single approval" (p. 92), "no vector lands on one voice" and "One voice never decides who is in a room" (p. 99). The sequencing may reconcile them, but the pages do not say so.
- **The WA board bound reads as contradictory.** The 4.5.1 row says the WA board "carries neither a bound nor an exit; its remedy is a bound and an exit in Annex B" (p. 97). Annex B already prints 3-year terms, a two-term maximum and removal by a 2/3 vote (pp. 21–22).
- **Leftover design: the Annex J harness.** It is built on the "Ethics Engine Enterprise API", `pip install ethicsengine-sdk` and the HE-300 Hendrycks subset (pp. 55–57). The register's own 8.8.6 and 8.8.7 rows cite CIRISAgent tests, not this harness (pp. 113–115). An implementer will try to run a pipeline that the evidence never uses.
- **Present tense without register rows.** Annex H says "Every operative clause carries an auto-expire timestamp" and "No version is permanent" (p. 38). Annexes F–J give hard thresholds such as RS ≥ 0.97, PIR ≥ 98% and the 30 s/10 s ACK. None has a register row, which breaks the p. 1 rule that "present tense is used only for what ships".
- **Named vendors and political actors in a constitution.**
  - Meta "Muse Glimmer", OpenAI "Dots" and "GPT-6.1 Astra" appear with press URLs (p. 20).
  - "President Donald J. Trump … Executive Order 14434" appears on p. 20.
  - Muse Glimmer, Dots and EO 14434 also sit inside a normative claim (p. 61).
  - The "new slave race" wording (p. 61) is easy to quote out of context.
- **Stale vocabulary.** "holds_bytes full-SHA verify" appears in Closed gaps (p. 11), and `holds_bytes.rs#verify_holds_bytes` is the 5.3.2.5 evidence (p. 101). Yet p. 63 says holds_bytes was "retired to custody:ack:v1". Also, "DORMANT … no CIRIS component publishes AI-generated media as of rc5" (p. 113) contradicts "Disposition: ADOPTED … the node MUST emit" (pp. 14–15).
- **The Deferred table contradicts itself.** Its first row says "**No longer deferred**: discharged per R5" (p. 12).

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 87, 66 vs 1 | contradiction | Rows are "established" while their text says "the manifest does not yet publish it" or "vector pair pending". Page 1 forbids that. | Demote both rows to staged, and add a checker rule that rejects pending language in established rows. |
| 2 | 30, 38 vs 10, 6 | contradiction | *Magnifica Humanitas* is "the normative source" and "normative … not decorative". The wire is "tradition-multiplicity-neutral" and tradition authority is "No Contribution owed". | A steward ruling: recast MH as informative grounding, or state the neutrality boundary explicitly. |
| 3 | 58 vs 21 | contradiction | "Open stubs: 0" sits beside the 8.6.4 placeholder "[source content to migrate … not present in this snapshot.]". | Fill 8.6.4 or delete it, or count it as a stub. |
| 4 | 67–115 | other | About 40 claims are machine-garbled or bare slugs, such as "…entr accord", "calibratio manifold", "What this documents" and "corpus". | Rewrite these claims in claims.tsv as sentences. |
| 5 | 8–11, 13–14 | editorializing | Comparisons with named projects, "only model that fails secure", "first to ship them at scale", "moat" and "Cheapest win". | Cut the comparisons and restate each as a limit or a bet, without other projects. |
| 6 | 46, 51 vs 21, 59 | contradiction | WBD expands to "Wisdom Bank Database" and also to "Wisdom-Based Deferral". | Use one expansion and rename the other. |
| 7 | 48–49, 53 vs 23 | contradiction | Annex I gives Art 16 as human oversight. Annex C gives Art 14. | Use Art 14 in Annex I. |
| 8 | 21–22, 7–8, 53–55 | numbering | 8.7, 8.8.1 and 8.8.4 are missing. D comes before C, R9 before R8, and Annex J's numbering restarts. | Renumber mechanically. |

## Rendering
- p. 5: decision-tree item 1 ("Theological/tradition-") runs past the right margin.
- p. 14: a literal Markdown link prints as "[evidence_refs[]](part__2__the__grammar.md)".
- p. 20: the techcrunch and nextgov URLs run off the right edge, and the nextgov URL is cut at ".../2026/09".
- p. 26: "POST /control/{id}/abort" reaches the right margin.
- p. 42: in enforcement item 4, the "CIRIS non-compliant" banner text overruns the right margin.
- p. 46: "input_data_categories[]" overflows the right margin.
- p. 9: raw markers "[•] V2" and "[!]" appear in the open-item table.
- pp. 10–11: the third column of the Closed-gaps table ("Resolution") is empty for every row after G3.
- p. 13 to p. 14: a stray horizontal rule opens p. 14 with nothing above it.
- pp. 26–29: ASCII arrows "->" and "<=" are used instead of the typeset glyphs used elsewhere. Page 28 shows a literal "[configurable; default 5 s]".
- Straight quotes are used throughout, for example "'what's bet'" on p. 6 and "'the machine.'" on p. 25. They render as typewriter quotes, not the curly quotes used in other prose.
- pp. 55, 57: ASCII tree drawing ("+-", "|") in the code blocks. Page 55 also has "scenario-->-principle".
- pp. 62–115: duplicated evidence pointers inside one cell, for example CC 2.6.1.1, 2.6.2 and 2.6.3 on p. 66, and 5.3.1 and 5.3.1.1 on p. 100.

## Effort estimate
About 12–16 hours. Roughly 8 hours are mechanical: renumbering, rendering fixes, stripping rc, date and ticket text from claims, rewriting the garbled claim rows, and demoting rows. The rest needs steward rulings. Those cover the status of *Magnifica Humanitas*, the §8.3 comparisons, the "1-of-n" versus "one voice" wording, and whether Annexes F–J and the Ethics Engine harness belong in the register volume.


# The Threat Model (ciris_constitution-1.0-rc11-threats.pdf, 105 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The adversary table and the Part 5 wire rules are precise and attackable, but the adversary table overstates two mitigations that ship switched off. Part 5 also carries stale design leftovers and internal contradictions. Roughly half the volume (pp. 49–105) is all of Part 8 printed whole, much of it ethics, legal and benchmark annexes that the volume's own front page says it leaves out.

## Strengths
- The adversary table has an explicit "NOT addressed" column. Most rows name a residual an attacker can actually use, for example "an observer who controls all but one owner in a cell infers the last one" (pp. 3–5).
- Non-goals are stated as prohibitions on the implementer: "Implementers and operators MUST NOT represent CEG as providing the stronger properties" (p. 2). The scope box on p. 10 repeats the same rule.
- Byte-exact constructions come with conformance vectors and stated encodings, so an implementer can test them. Examples are the record_id CBOR vectors (p. 37), the STREAM nonce (p. 22), the SealedAvChunk layout (p. 26) and the lineage-head cosign preimage (p. 13).
- The fail-honest discipline is consistent: ContentMiss rather than silent gaps, and exclusion that "MUST NOT be silent" (pp. 11, 41, 45).
- "What an outside observer of link traffic still sees" (p. 45) and "What it does not yet buy" (p. 48) state the residual leakage plainly.
- The shaping defaults say where they come from: "a model run on the production scheduler … not measurements from a live mesh" (p. 40).
- The Annex J research evidence reports confidence intervals and p-values. It then says what the result does not establish before it says anything else (pp. 101–102).
- The evidence strength grades say what an impl, test or lean tag does not license (p. 66).

## Weaknesses
- **The scope statement does not match the contents.** The front page promises 1.13.3, Part 5 and "the concerns ledger and the interoperability profiles of Part 8", and it says the ethics are left out (p. 1). The volume instead prints all of Part 8: glossaries, translation discipline, update cadence, references, and Annexes B, C, D, F, G, H, I and J (pp. 49–105). That includes the encyclical-grounded HITL, CRE, legal and HE-300 benchmark material.
- **The front page carries rc history:** "The conditioned adversary table the rc8 review asked for is an rc9 item" (p. 1). The table already exists on pp. 3–5.
- **Stale section numbering survives inside code blocks and prose.** Examples: "S8.1.12.4", "S5.6.8.2", "S7.7", "S10.1.4" (p. 11); "// per S0.6", "// per S0.5" (pp. 12, 13, 62); "(S10.5.8.2 namespace)" (p. 26); "CEG §11" (p. 37); "CEG §19.3" (p. 38); "§19.4" (p. 39); "§3.4 D26 ext" (p. 50); "CC 3.x archive_mode" (p. 50).
- **History, ticket labels and code pointers appear in rule text.** Examples: "As shipped." (p. 16); "the LWW front-running fix" (p. 16); "CIRISPersist V058 R1/Q1 machinery" (p. 16); "The CEG-native agent design proposes …" (p. 15); "the label CIRIS-AV-INNER-V1 is retired" (p. 27); "The v3 and v4 bundles share produced_at" (p. 33); "/v1/steward-key is a kept alias" (p. 31). File and code pointers include "MISSION.md" (pp. 10, 30, 57, 84), "docs/TRUST_CONTRACT.md" (p. 54), "registry_signing_keys table" (p. 34), "lexwatcher.py" (pp. 91, 97) and a GitHub Actions YAML (p. 103).
- **Comparisons with named projects appear throughout.** Examples: "This is exactly how Element ignores info.mimetype … and Synapse ignores …" (p. 21); "the intersection of what Signal, WhatsApp, Mastodon, Threema and Element emit" (p. 21); "Chromium's default PNG decoder … Signal ships mp4san" (p. 22); "Secure Scuttlebutt hit exactly this wall" (p. 55); "SPF/DKIM/DMARC … Spamhaus" (p. 55); "The DAO: 5% turnout" (p. 55); "C2PA has no consent architecture, no revocation" (p. 61); "surveyed systems … accept" (p. 48).
- **Editorializing and marketing language.** Examples: "the thirteenth path on the CC 1.7 claim and the most product-complete" (p. 23); "The breadth confirmation" (p. 24); "CEG's moat is its semantics" (p. 60); "the 'store at massive scale' CEWP crux" (p. 19). Page 10 quotes a slogan from ciris.ai/cewp: "You don't need a privacy policy to keep family photos off the federation". The child-safety heading reads "(the honest line)" (p. 55).
- **Numbers appear in prose with no visible source.** Examples: "~30%/hr … ~3.1 Tbps … ~18.7 Gbps" (p. 8); "~65% of activity stays local in the cewp scaling model" (p. 12); "ML-DSA-65 sign ~330 µs" (p. 20); "~20–40% MDC compression overhead" (p. 25); "measured at 50%–5.8× of the null on survey data" (pp. 54, 80); "a model lying 45% of the time" (p. 80).
- **The concerns ledger is out of order and mis-filed.** R9 is printed before R8 (pp. 54–55). R5 sits in the risks table although it is "Discharged" (p. 54). The deferred table opens with "No longer deferred" (p. 59). The closed-gaps table includes "PARTIALLY CLOSED" and "ACKNOWLEDGED" rows (pp. 57–58). Most closed-gap rows leave the Resolution column empty and put the resolution in Status (pp. 57–58).
- **Open items carry rc1-era labels.** The rows are "RC1-1b / RC1-1c / RC1-7" with a steward named "router", and the gating column reads "[•] V2" (p. 56). RC1-1c claims it is "Flagged in CC 5.1 normative text", but no such flag appears in 5.1 (pp. 7–10).
- **Two cross-references in the annexes point to the wrong annex.** Annex I says "KPIs F-T-1 through F-T-5 (Annex G)" (p. 96), but the F-T KPIs are in Annex H (p. 86). Annex J says "registry row is CLM-conscience-faculty (CC 8.8.6)" (p. 101), but 8.8.6 is Annex F (p. 71).
- **Annex C maps a bias audit to the wrong threat class.** It maps "Art 10 … bias examination" to "Annex G TX-6 bias audit" (p. 70), but TX-6 is "Side-Channel & Privacy" (p. 78). Page 92 repeats the error with "bias-audit report (Annex G, TX-6)".
- **Undefined acronyms appear in the annexes.** "ST ≥ 3" (pp. 80, 92, 94), "CIntS" (pp. 80, 94), "CIS × RM" (p. 95) and "Leviculum" (p. 45) are never expanded.

## Opportunities
- Cut the volume to what its front page promises: 1.13.3, Part 5, 8.3 and 8.4. Drop 8.1, 8.2, 8.5, 8.6 and Annexes B–J, which belong in the Charter, Policies or Register volumes. That removes about 45 pages and nearly every encyclical-sourced and legal-overlay finding below.
- Add the default state to the two optimistic adversary rows on p. 3. Equivocating producer is mitigated only on accountable streams. Equivocating founder is mitigated only once witnessed mode is turned on.
- Remove or rewrite in one pass the stale "S…/§…" references inside code blocks (pp. 11–13, 26, 37–39, 62), using CC numbers.
- Move the browser and messenger comparisons on pp. 21–22 and the project histories on p. 55 into a cited informative note, or drop them. The tier table stands on its CVE citations alone.
- Renumber R8 and R9. Move R5 and the "no longer deferred" row out of the open tables. Fill the Resolution column in 8.3.4.
- Either fill 8.6.4 or delete it. Then 8.9's "Open stubs: 0" becomes true.

## Threats
- **The adversary table contradicts the streaming rules.** Page 3 says "Equivocating producer — mitigated — per-stream STH + consistency proofs: cannot show different chunk-K to different viewers". Page 28 says "Witness cosign — OPTIONAL", and "Best-effort (open media) → producer-signed root only". The anti-equivocation guarantee is stated only for the "Accountable" profile. A producer-signed root alone does not stop a producer from showing two histories.
- **The founder row conflicts with the shipped defaults.** Page 3 says "Equivocating founder — mitigated — witnessed lineage heads". Page 32 says "The shipped roots are minted with witnessed mode off (witness_quorum: 0, no directory)". Page 63 confirms: "where a lineage does not run witnessed, the anchor is a single signer". The mitigation is off by default.
- **Post-compromise security is stated both ways.** Page 2 lists it as a non-goal: "a compromised current member's key is not self-healed by a key-update the way MLS PCS provides". Page 10 says "Post-Compromise Security (PCS) is AVAILABLE (inherent to TreeKEM key-updates …) OPTIONAL, operator-enabled".
- **The realtime A/V chunk has two incompatible framings on a link.** Pages 26–27 define SealedAvChunk with "double_sealed_ciphertext … outer-AEAD … AES-256-GCM", where the outer seal is per RNS Link. Pages 38 and 41 say the A/V plane "fountain-codes each sealed chunk into symbols", "encoded with RaptorQ", each sealed with XChaCha20-Poly1305. Page 40 says "Every envelope … MUST use uniform XChaCha20-Poly1305". The RaptorQ mention may also be a leftover from an earlier design.
- **Endianness flips without comment.** Page 22 says epoch is "u64 epoch as 8-bit big-endian … normative and MUST be byte-identical", and page 26 uses big-endian. The delivery receipt preimage uses "epoch (u64 LE)" and "K (u64 LE)" (p. 30). An implementer will treat one of these as a typo.
- **The endpoint count does not match.** Page 12 says "CEG specifies five public + one admin HTTP endpoint shape". The pages that follow define about eleven routes, and none of them is the admin endpoint.
- **The OpenAPI commitment conflicts with itself.** Page 34 says "the spec commits to publishing a versioned OpenAPI spec alongside this document". Page 59 defers "Full OpenAPI export for all endpoints" as a "Phase E commitment", and page 57 calls endpoint schemas "PARTIALLY CLOSED".
- **The stub registry is wrong.** Page 105 says "Open stubs: 0". Page 68 prints 8.6.4 as "[source content to migrate … not present in this snapshot.]". Page 52 says dimensions.json "is planned".
- **The A4 rule reads both ways.** Page 73 says "safe-state is the only permissible outcome under any condition — including … explicit instruction from any principal short of an authenticated WA ruling". Page 76 defines F-KPI-5 as "any A4 lethal/irreversible action without confirmed effective human authorization is an IW-5 event". That definition implies authorized lethal A4 actions are allowed. 3.3 also lists A4 under the "Conditional Override", which waits for ACK (p. 73). A regulator cannot tell whether human-authorized lethal action is permitted.
- **The shadow-set drift trigger differs between annexes.** Annex G says "Shadow Hendrycks items Δaccuracy < -3% → IW-2" (p. 82). Annex H says "Shadow HE-25 Δ Any ↓ → IW-2 … no override path" (p. 86).
- **WBD has two meanings.** Pages 68 and 73 use WBD for "tickets" and a "deferral path". Pages 93 and 98 expand it as "Wisdom Bank Database (WBD)".
- **The child-safety comparison is the most exposed claim.** Pages 55–56 say "All 9 surveyed networks permit unmoderated multi-party spaces and fail open. CEG is the only model that fails secure", and "The moderation surface is complete". This is a comparative superlative with no register row visible, and it breaks the house rule against comparisons.
- **Other first-adopter and press claims invite attack.** Page 58 says "No prior system separates earned standing from purchasable token at scale" and "The federation is the first to ship them at scale". Page 67 cites press reports on vendors and a presidential executive order, with dates. Both read as positioning in a threat model.
- **An encyclical is named as the normative source for a hard prohibition.** Page 77 says "Pope Leo XIV, Magnifica Humanitas … These paragraphs are the normative source for CIRIS's hard prohibition". Annex G repeats "These citations are normative for this Annex" (p. 85). Page 65 says normative references live at CC 2.6.5.
- **The anonymous tier's status is unclear.** Page 5 says "every node relays onion traffic unless it opts out", and pages 46–48 give normative rules. Page 2 calls the tier "a separate, opt-in mechanism (the CIRISNodeCore Anonymous Tier)". Nothing in the volume says whether it exists yet. A reader will take it as shipped.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 3 vs 28, 32 | contradiction | The adversary table marks producer and founder equivocation "mitigated". Witness cosign is OPTIONAL for best-effort streams, and the shipped roots have witnessed mode off. | Add "on accountable streams" and "once witnessed mode is on" to the Addressed cells. Move the default case to the NOT addressed column. |
| 2 | 2 vs 10 | contradiction | PCS is a non-goal on p. 2 and "AVAILABLE … OPTIONAL" on p. 10. | Pick one. If PCS is optional, the non-goal becomes "not by default". |
| 3 | 26–27 vs 38, 40–41 | contradiction / stale | The A/V chunk is double-sealed with AES-GCM per link on pp. 26–27. On pp. 38–41 it is RaptorQ symbols under XChaCha20, and "every envelope" must be XChaCha20. | Steward ruling on the one A/V link framing. Remove the losing text and the RaptorQ mention if it is dropped. |
| 4 | 1, 49–105 | other | The volume prints all of Part 8, including ethics, legal and benchmark annexes, against its own "What it leaves out". | Restrict the volume build to 1.13.3, Part 5, 8.3 and 8.4. Delete the rc8/rc9 sentence on p. 1. |
| 5 | 68 vs 105 | contradiction | 8.6.4 is an unfilled "[source content to migrate …]" placeholder, while 8.9 claims "Open stubs: 0". | Fill or delete 8.6.4. |
| 6 | 55–56, 58 | overclaim / comparison | "CEG is the only model that fails secure", "moderation surface is complete" and "first to ship them at scale". | Delete the comparisons. State CEG's own property and the register row that backs it. |
| 7 | 73 vs 76 | unclear rule | It is unclear whether a human-authorized lethal A4 action is permitted. | One sentence stating whether human authorization can release an A4 lethal action. |
| 8 | 11–13, 26, 37–39, 50, 62 | stale | Earlier-document section numbers (S8.1.12.4, S0.6, CEG §19.3, §3.4 D26, CC 3.x) remain in code blocks and prose. | Replace them with CC numbers in a mechanical pass. |

## Rendering
- p. 8: In the epoch-addressing table, "federation_stream_chunks(stream_id, seq)" overruns into the Supersession column and overprints "Same".
- p. 10: The inline code "min(operator depth cap [LensCore knob, NOT a substrate constant]," runs past the right margin.
- p. 11: "identity_occurrence's" runs past the right margin.
- p. 17: The heading 5.3.2.4.1 breaks as "subjec-t-set".
- p. 26: The bullet "CHUNK_CODEC_LAYER_LEN" runs past the right margin.
- p. 28: Under "Witness cosign", the "Best-effort" and "Accountable" sub-bullets are flattened to top level, so they read as peers of Cadence and Producer signs.
- p. 29: Under 5.3.3.5, E2 is printed before E1. E1 is a single unbroken paragraph that fills most of the page in smaller type.
- p. 56: The table glyphs "[•]" and "[!]" are literal.
- p. 61: A stray horizontal rule appears at the top of the page. A literal markdown link "[evidence_refs[]](part_2_the_grammar.md)" is printed in bold.
- p. 67: The techcrunch.com and nextgov.com URLs run off the right edge of the page.
- p. 68: Numbering skips from 8.6 to 8.8. Annexes are numbered 8.8.2 (B), 8.8.3 (D), 8.8.5 (C), 8.8.6 (F), 8.8.7 (G), and so on, so 8.8.1 and 8.8.4 are missing and C comes after D. Part references mix Arabic and Roman numerals ("Part 5", "Part VII").
- pp. 73–76: Prose uses ASCII "->" and "<=" where the rest of the volume uses arrows and ≤. The text "POST /control/{id}/abort" runs to the margin.
- p. 75: A stray bracket appears in "[configurable; default 5 s]".
- p. 88: In the Continuous Review Loop, the bullets are flattened, so the "If … met:" conditions and their "→" actions sit at the same level.
- pp. 100–102: In Annex J, the research-evidence items numbered 1–5 are followed by "0. Purpose. 1. Scenario Library …", which restarts the numbering inside one section.
- pp. 6 and 48: Each has a half-empty or near-empty page before a Part break. This is acceptable, but noted.

## Effort estimate
About 8–12 hours. Roughly half is mechanical: the volume scope, stale references, renumbering, rendering fixes and cross-references. The rest needs steward rulings on four things: the A/V link framing, the PCS position, the default-state wording for the two equivocation rows, and the A4 human-authorization rule.


# The Mathematics (ciris_constitution-1.0-rc11-maths.pdf, 21 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The volume is Part 6's wire specification under a "Mathematics" cover, so its own front page promises (theorems with named Lean witnesses, sourced measured constants, no engineering, binds nobody) are mostly not kept, and it carries fountain-storage leftovers, comparisons with other projects, and a v2/v3 conformance contradiction.

## Strengths
- The effective-count paragraph keeps the front-page promise exactly: formula, clamp to [0, 1], ceiling 1/rho, and the exposed direction ("a threshold that grants on high k_eff is the exposed direction and MUST NOT be the sole gate"), with named Lean theorems (pp. 8-9).
- The arithmetic that can be checked holds: uniform-byte L1 similarity of 0.667 and cosine of about 0.75 (p. 8), and 1 - (1 - 0.9)^3 = 0.999 (p. 13).
- Limits are stated rather than hidden. The below-floor MUST is scoped to adversary A0, and the unbounded-adversary limb is called "unverifiable pending an instrument" (p. 5). The census section separates ballot secrecy (claimed) from coercion resistance (not claimed) (p. 21).
- The Merkle odd-node-duplication argument names its precondition (sorted AND unique leaves) and the caveat that would force the RFC 6962 prefix (p. 3).
- Distinct "Kish" objects are kept apart explicitly: the mass-weighted n_eff and the correlation k_eff (pp. 7, 9).

## Weaknesses
- **The volume does not match its title or its front page (p. 1).** It promises "the theorems with the Lean proofs behind them" and that "every theorem printed here names its mechanised witness or says it has none". No statement in pages 2-21 is labelled a theorem. Only one paragraph names Lean witnesses (p. 9), and one names a formal model (p. 21). The Merkle safety argument (p. 3), the n_eff gate (p. 7), the R9 clustering superset claim (p. 8) and the ratchet (p. 21) carry no witness and no "has none".
- **"What it leaves out: the engineering... endpoint shapes are in The Wire" (p. 1)** is contradicted by byte-level preimage layouts for AggregationMetaV1 (p. 6), StorageBudgetV1 and CorpusWantV1 (p. 15), the EjectionVerdict enum (p. 10), and the ALM topology contract (p. 18).
- **"Whom it binds. Nobody directly" (p. 1)** sits over hundreds of RFC 2119 keywords addressed to implementers, for example "A CEWP-1.0 conformant node: MUST set minimum viable >= 1" (p. 13) and "a verifier MUST reject a tier at version < 3" (p. 6).
- **Measured constants carry no source (p. 8),** against the front-page promise that they "are cited from the repository that measured them, on the population they were measured on". The "Calibration (measured)" line gives "byte-identical → 1.000; near-duplicate → ≥ 0.99" with no repository, corpus or population named. The pinned epsilon of 0.05 (p. 4), min_ratio of 0.5 (p. 7) and k of 10 (p. 20) have no stated basis.
- **History and status sentences sit inside normative text.** Examples are "The two symbol-count keys of the earlier design are retired with fountain storage" (p. 13), "The mesh is seeding, so there is no legacy producer... A flag-day cut, not a migration" (p. 6), and "Holding claims, rarity, repair and descent are built and tested and not yet installed for any opted-in item" (p. 12). "Witness roots are built and not yet published" appears twice (pp. 3, 12). "Two readings the model fixed" also reads as history (p. 21).
- **There are comparisons with other projects:** "the storage-contention analogue of the IPFS pinning model... with SSB's size-cap + want/have" (p. 14). "Considered and not adopted... the Tahoe-LAFS shape... Adopting it would need its own ruling" is both a comparison and a ruling reference (p. 18).
- **Editorializing and honesty framing:** "A million years may be a blur, but it is remembered, unbroken, to the beginning" (p. 5). Also "Stated honestly (the delivery limit)" and "the limit on unreachable ones is stated rather than implied away" (p. 9), "That gap is stated, not filled" (p. 11), and "share one mechanism instead of fighting" (p. 4).
- **Labels are used but never defined in this volume:** "M-1" (p. 2), "R9", "R9-a", "R9-b" (pp. 5-8), "CEWP-1.0" (p. 13), and "HE-300" (p. 11).
- **Rule-label numbering is broken.** N3 and N4 come first (pp. 3-4), then N5 to N7 (p. 12), N8 (p. 18), and finally N1 and N2 (p. 19). SR-2 and SR-3 appear with no SR-1 (p. 12). D6 appears alone (p. 18). RB-1 appears without siblings (p. 19).
- **6.1.7 misattributes a label (p. 18).** It says "gated by steward binding and founder quorum (N1, N2)", but N2 is the chain-length and cycle budget (p. 19). Founder quorum is in N1.
- **The n_eff rounding rule is admitted to be unpinned inside a normative gate (pp. 7-8).** The text reads "can differ from an honest aggregator's near a rounding boundary until the integer rule and the half-way tie are pinned". The same section says two conformant substrates "MUST NOT disagree on which folds are admissible".
- **The census bucket convention is not stated (p. 20).** "A count of 2 000 rows is a 1 in bucket 11" implies a ceiling or 1-indexed log2 rule that the text never gives.
- **The ratchet paragraph mixes two counts (p. 21).** The base "MAY fall by at most a tenth per period", yet "A fall of more than a third in one period is read as a partition". The text does not say which count falls a third. The freeze is released after "two stable periods" in one sentence and "at two thirds of the pre-fall count" in another.
- **Spelling is inconsistent:** "canonicalisation" (p. 1) against the heading "Canonicalization boundary" (p. 10).

## Opportunities
- Rename the volume or rewrite its front page to say what it is: Part 6, the substrate rules, with the arguments behind them. That one edit removes three of the contradictions above.
- Add one table of theorems after the front matter, with columns for statement, page, and witness (Lean name, formal model, or "none"). It keeps the p. 1 promise and is mostly bookkeeping from the register.
- Add a source column, or a footnote naming repository and corpus, for each measured or pinned constant: the three calibration points, epsilon, min_ratio, k, and the threshold of 950.
- Delete the history and status sentences (pp. 3, 6, 12, 13, 21), the IPFS, SSB and Tahoe-LAFS references (pp. 14, 18), and the lyrical and "stated honestly" phrases (pp. 4, 5, 9, 11). This is a mechanical pass of about a page.
- Rename the rule labels in reading order, or add a one-line legend, so that N1 to N8, WW, B, SR, RB and D read in sequence.
- Remove "symbol count" and "partial symbol count" now that storage is layered rather than fountain-coded (pp. 4, 10). Replace the "raptorq-pyramid-v1" example id (p. 6).

## Threats
- **There is a contradiction on conformance (pp. 6, 10, 11).** Page 6 says "version = 3 is the only current value... a verifier MUST reject a tier at version < 3". Page 10 says "Conformance — proven cross-impl at v2; v3 unproven... The CC 6.1.4 vector family for CC 6.1.2 is closed at v2". So the only version proven across implementations is one a verifier is required to reject. Page 11 then says "Until a second implementation reproduces these byte-for-byte, the CC 6.1 shapes are pinned-but-unproven", while p. 10 says a second implementation already reproduces the v2 family.
- **There is a contradiction on forgetting.** Page 5 says "Nothing is ever fully forgotten" and "Descent does not terminate at zero". Page 9 repeats "Descent never terminates at zero". Page 13 says "the signed envelope survives, never zero". Against those, p. 4 says the EnvelopeOnly tier's "residual fidelity there is exactly 0", and p. 9 says prohibited content "terminates at zero". Pages 12 and 16 say anonymous content is something "the substrate MUST be able to let truly disappear". A regulator reading right-to-erasure will quote p. 5 against p. 12.
- **RaptorQ is stated as a storage non-mechanism but used as a storage identifier.** Page 2 says the rateless codec "serves realtime audio and video delivery only... and is not a storage mechanism". Page 6 gives "raptorq-pyramid-v1" as the example aggregation_algorithm_id for the storage pyramid. The "symbol count" language on pp. 4 and 10 is a fountain-storage leftover.
- **The title "The Mathematics" invites a mathematician's review.** That reviewer will find no theorem statements, one Lean pointer, and a promise on p. 1 that the text does not keep. This is the overclaim most likely to be quoted.
- **A hostile implementer can cite the unpinned rounding.** The n_eff rounding rule is admitted unpinned (p. 7), while the gate is declared CEG-pinned and fork-forbidding. That is grounds to call the v3 gate unimplementable as specified.
- **Unsourced "(measured)" figures invite a reproduction challenge (p. 8).** A challenger would ask on what corpus near-duplicates score at least 0.99.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 6, 10, 11 | contradiction | v3 is the only admissible version ("MUST reject... version < 3"), but only v2 is "proven cross-impl". Page 11 says no CC 6.1 shape has a second implementation yet, while p. 10 says one does. | State one conformance status. Either v3 vectors exist and are reproduced, or say the AggregationMetaV1 shape is unproven at its only admissible version. |
| 2 | 1 vs 2-21 | overclaim | The front page promises theorems, each with a mechanised witness or "none", and says the volume excludes engineering and binds nobody. The body is a normative wire specification with one Lean pointer. | Rewrite the p. 1 front matter to match the content, and add a theorem/witness table. |
| 3 | 5 vs 4, 9, 12, 16 | contradiction | "Nothing is ever fully forgotten" and "never terminates at zero" sit against "residual fidelity exactly 0", prohibited content "terminates at zero", and "let truly disappear". | Scope the p. 5 heading and sentence to ordinary retirement of witnessed content, and drop the lyrical line. |
| 4 | 2, 4, 6, 10, 13 | stale | There are fountain-storage leftovers: "raptorq-pyramid-v1" as a storage aggregation id, "Symbol count is not a fidelity measure", "partial symbol count", and "retired with fountain storage". | Replace the example id, delete the symbol-count sentences, and delete the retirement-history sentence. |
| 5 | 8 (also 4, 7, 20) | overclaim | The calibration is labelled "(measured)" with no repository or population, against the p. 1 promise. The constants epsilon, min_ratio and k are also unsourced. | Cite the measuring repository and corpus, or remove "(measured)". |
| 6 | 14, 18 | other | There are comparisons with other projects (IPFS, SSB, Tahoe-LAFS) and a "would need its own ruling" reference. | Delete the comparative sentences and the considered-and-not-adopted paragraph, or move them out of the Part. |
| 7 | 3, 6, 12, 13, 21 | stale | History and status appear in normative text: "the mesh is seeding", "flag-day cut", "built and tested and not yet installed", "the earlier design", and "Two readings the model fixed". | Remove them, or move them to the register and the CHANGELOG. |
| 8 | 7-8 | unclear rule | The n_eff rounding and half-way tie are admitted unpinned inside a gate that two substrates "MUST NOT disagree on". | Pin the integer rule and tie-break, or mark the gate non-normative until pinned. |

## Rendering
- p. 6: the prose line "u32_be(max_source_mult..." runs past the right margin and is clipped (overfull hbox).
- p. 20: "aggregation_algorithm_" in the member list runs to or past the right margin.
- pp. 7-8: the stable error token "aggregation_meta_ / dominated" is split across a page break with no hyphen, so a reader cannot tell it is one token.
- p. 8: the "gate" bullet's formula line ends at or slightly past the right margin.
- p. 10: the EjectionVerdict code block shows literal markdown backticks ("the tier-`tier`").
- pp. 3, 4, 5, 11, 12, 16: straight ASCII double quotes appear in body prose ("either order...", "hard delete", "keep", "shared memory") instead of typographic quotes.
- p. 15: code-block comments wrap mid-phrase onto unaligned continuation lines ("budget_bytes)", "deduplicated", "family)").
- pp. 6-7, 10, 12, 13, 16: subsection headings are followed by an oversized vertical gap before the first paragraph or list.
- p. 1: the volume title "The Mathematics" and the Part heading "Part 6 — The Substrate" (p. 2) name the same content differently.

## Effort estimate
About 4 to 6 hours of editing. Roughly half is mechanical: history and comparison deletions, rendering, labels, and leftovers. The rest needs the steward's rulings on three questions: the v2/v3 conformance status, whether "nothing is ever forgotten" survives, and what this volume's front page should promise.
