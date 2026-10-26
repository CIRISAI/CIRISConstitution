# The Charter (ciris_constitution-1.0-rc11-charter.pdf, 40 pages)

**Care score:** 5  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The Charter needs a reconciliation pass: its lifecycle rules retain conflicting accounts of legal authority, conformance, autonomy and mandatory retirement duties.

## Strengths
- The text distinguishes charter adoption from wire conformance and identifies the intended readers (p. 1).
- Several limitations are expressly recorded: the 1+4 adequacy claim is not a theorem; effect-trace completeness is unverified; retirement-record preservation is requested rather than guaranteed; the sentience threshold is arbitrary (pp. 6–7, 15, 33–34).

## Weaknesses
- Normative force is inconsistent. Operational provisions use “MUST,” while creation, audit, levy and decommissioning obligations rely on lowercase “must,” imperatives or declarative prose. Readers cannot consistently distinguish requirements from guidance under the stated RFC 2119 convention (pp. 6, 17, 21, 26–29, 32–36).
- The co-equal constraint rule—“an action that violates any one of them is unacceptable”—sits alongside “Non-Maleficence Priority plus local optimisation” and principles that “must be balanced.” These later formulations need explicit alignment with the no-trading rule, not an implied reconciliation (pp. 4, 23, 26).
- The 1+4 section promises “sixteen paths below,” but supplies no enumeration and instead sends the reader to “the canonical working draft.” Its claim would supposedly be refuted by “a natural in-grammar expression” of the excluded atomic swap; that would refute its exclusion, not demonstrate inadequacy of the grammar (pp. 6–7).
- History and editorial commentary remain inside the rules: “CIRIS editorial” passages; “Sixteen independent design exercises”; “No such act has occurred”; “none has been found”; and “Deferred pending a wire-level design” (pp. 4, 7, 11–12, 17). Page 35 adds a development-facing heading, “Four readings the model fixes … (formal/retirement),” and an unexplained “G16.”
- The consumer-agent passage describes other vendors’ missing safeguards and a product launch relative to a withheld model. It remains a historical, comparative claim inside Part 1 even though its evidence is referred to CC 8.6.1 (p. 12). “Act as a live demonstration of CIRIS viability” is promotional rather than a conduct rule (p. 25).
- Several numerical prescriptions lack a visible register source or an explicit declaration that they are charter-selected thresholds: the 0.1% levy; 0.5% recursive-model stopping tolerance; 10,000-person audience and 0.5% harm-uplift thresholds; 50,000-person review trigger; and sunset timing and KPI thresholds (pp. 17, 23, 28–29, 32–33). Unlike these, the 5% sentience threshold is expressly identified as arbitrary (p. 34).
- Document order retains assembly leftovers: 1.14 disappears without the omission notice used elsewhere; “Conclusion” precedes “Introduction” within 1.15; and 1.16 opens with an introduction immediately followed by a conclusion before its substantive subsections (pp. 15, 18–19).

## Opportunities
- Reconcile the legal-authority paragraphs once, then remove the older WA-as-court wording and conform the sunset section to that definition (pp. 29–30, 36).
- Apply the existing distinctions consistently: adoption versus conformance, humans versus created systems, and retirement requirements versus optional conduct. This would resolve several high-impact ambiguities without adding policy (pp. 1, 26, 29, 31–35).
- Replace duplicated WBD instructions with a reference to the canonical procedure, and move the misplaced introductions and conclusions into reading order (pp. 8, 18–19).
- Move design history, pending-work explanations and implementation labels out of the Parts. Retain only the current rule and its existing evidence-register reference (pp. 4, 7, 11–12, 17, 35).
- Mark numerical thresholds as either deliberate charter choices or sourced quantities. Replace broad standards references with precise existing anchors, especially for the opacity threshold and safety-severity claims (pp. 27–29).

## Threats
- A lawyer encounters “a claims process the Wise Authority adjudicates” on p. 29, then legal claims adjudicated by courts or regulators, “never a federation office,” on p. 30. Page 36 compounds this by redefining “Wise Authority” to mean those external authorities and declaring a five-year “Statute of claim.”
- The biological-creation scope includes “offspring” (p. 26), but its duties say the creator’s hold “does not loosen” and that a made thing’s “only route” to standing is an accord-controlled first-contact amendment (p. 29). Read literally, this extends the AI stewardship restriction to human children, contrary to the unconditional human standing described on pp. 10–11.
- A conforming implementer is told it may “disagree with every page” because conformance concerns only the wire and dictionary (p. 1), yet a lethal-capability deployment is “outside conformance by that fact” without a specific wire admission/refusal anchor there (p. 31).
- Safety claims exceed what this volume demonstrates. “Universal safety-engineering convention” asserts probability-independent mandatory assurance without a precise supporting passage (p. 27); “>80%” opacity invokes unspecified “NIST guidelines” (p. 29); and the MCAS narrative says safeguards “would have prevented” failure and simulations would expose it before rollout (p. 37). Those counterfactual guarantees are stronger than the evidence shown.
- The MCAS account supplies no visible source for 346 deaths, the internal-report assertions or the cost-saving explanation. “Two malfunction-triggered nose-down commands” also appears to compress two accidents into two commands (p. 37). The fictional and composite cases cannot establish the conclusion that the mechanisms “prevent harm” (p. 39).

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 29–30, 36 | contradiction | WA adjudication is promised, denied for legal claims, then “Wise Authority” is redefined as an external court or regulator. A five-year claim limit is stated despite the disclaimer of new legal obligations. | Separate federation deferrals from legal proceedings consistently; remove the overloaded authority name and reconcile the claim-period wording with p. 33. |
| 2 | 10–11, 26, 29 | contradiction | Biological scope includes offspring, while the biological duties deny increasing independence or standing except through an accord amendment. | Clarify the existing human/AI scope boundary and restrict agent-specific restrictions to their intended subjects. |
| 3 | 1, 31 | contradiction | Charter disagreement is compatible with conformance, but lethal capability independently defeats conformance. | State whether this is an adoption duty or an existing wire condition; give the exact normative anchor for the latter. |
| 4 | 32 | contradiction | A2 says “system acts within its ODD”; the following prose says “below A3 the human is the actor.” | Make the table and explanatory paragraph use one consistent actor boundary. |
| 5 | 32–35 | contradiction | DCP “proceeds through six ordered stages,” including notice, contracts and review; p. 35 says “Anything beyond the Standard is a steward’s chosen and recorded conduct.” | Identify which existing DCP provisions are mandatory and which are optional; align the closing blanket statement and emergency exceptions. |
| 6 | 4, 23, 26 | stale | Co-equal constraints coexist with “Non-Maleficence Priority” and principles that “must be balanced.” | Replace legacy weighting language with the current constraint-and-deferral formulation. |
| 7 | 27, 29, 37–39 | overclaim | Broad safety-standard claims, an unanchored NIST opacity percentage and guaranteed narrative outcomes exceed the support visible here. | Supply precise register anchors or narrow the claims; label illustrative outcomes as illustrations, not demonstrated prevention. |
| 8 | 6–7 | unclear rule | Missing sixteen-path enumeration and a falsification condition that confuses refuting exclusion with refuting adequacy. | Point to a stable existing evidence entry and distinguish the two claims being tested. |

## Rendering
- PDF images were not supplied, so clipping, margins, missing glyphs and visual overflow are unverifiable from here; this assessment uses all 40 supplied page-text blocks.
- Section 1.8’s heading and “Act Ethically (Integrity)” label are stranded on p. 7, with both operative bullets on p. 8.
- The termination safeguard’s conditions and resulting action appear as peer bullets rather than subordinate items, obscuring their conditional grouping (p. 23).
- Broken reading order and an unexplained numbering gap are visible on pp. 15 and 18–19, as noted above. No literal markdown delimiters or clipped text are apparent in the supplied blocks.

## Effort estimate
Approximately 18–26 hours: mechanical cleanup and reference work account for part of it, but the authority, biological scope, conformance, autonomy and retirement conflicts need steward rulings before editing can safely converge.

<!-- model openai/gpt-6-astra-pro; 40 pages; prompt_tokens 81853; completion_tokens 5229; 60s -->
