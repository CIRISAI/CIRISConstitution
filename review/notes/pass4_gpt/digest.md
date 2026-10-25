# The Digests (ciris_constitution-1.0-rc11-digest.pdf, 34 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The summaries and register describe materially different guarantees, so this volume needs reconciliation before readers can safely rely on its status labels.

## Strengths
- The authority rule is explicit: nobody is bound by the digest, and disagreement with a binding section makes “the digest … a defect” (p. 1).
- The fuller text supplies limits missing from shorter summaries: traffic-analysis exclusions, witnessed-mode restrictions, and the distinction between constitutional accountability and legal remedies (pp. 16, 18).
- Register entries expose implementation gaps, including identity-edit bypasses and upgrade paths that bypass refusal (pp. 31–32).

## Weaknesses
- Upgrade authority changes between sections: “a fix … is imposed” in rule 5g, but G23 promises “offered, not imposed” and treats recreation after rejection as falsification (pp. 15, 32).
- The executive summary says outsiders cannot see private groups “or that they exist”; N3 expressly says an observer of every link can discover their existence (pp. 2, 18).
- “Present tense only for what ships” and “a promise only where the wire enforces it” do not describe the volume’s actual practice: numerous promises are labelled normative-only or being built (pp. 1, 7, 17–18).
- The register’s promise index says “Harm has a remedy,” replacing the carefully qualified “may have a claim under the law” with an unconditional assurance (pp. 25, 16).
- “The one-page versions” introduces a 34-page volume; the operator digest calls itself “One page” but occupies three pages (pp. 1, 20–22). Much of the space repeats philosophical justification rather than shortening the rules.

## Opportunities
- Reconcile each summary against its corresponding register row, then use identical qualifications wherever the same guarantee appears. This would remove the conflicting upgrade, privacy and implementation claims without changing policy (pp. 2–4, 10–18, 25–33).
- Separate current operation from future duties consistently. In particular, retain the existing “does not bind anyone yet” qualification wherever the second-direction deferral rule is summarised (pp. 9, 21, 28).
- Remove draft history, ruling attributions and repeated philosophical argument from the reader-facing digest; retain binding-section references and necessary status distinctions (pp. 7–10, 19, 23–25, 27–32).
- Supply a visible source identifier for the mental-health result of “5.8%” versus “37.3%,” and register references for the implementation/model/topology counts. Their supporting sources are not visible here; the figures are unverifiable from here (p. 5).

## Threats
- A privacy or security reviewer can quote the executive summary against the document’s own exclusions: “no founder can fork a lineage silently” versus “the shipped roots run with witnessed mode off” (pp. 4, 18). The shorter version omits the condition that makes the claim defensible.
- An implementer cannot determine whether refusing an upgrade prevents replacement or merely records disagreement before a steward imposes it (pp. 15, 32).
- The status scheme risks appearing promotional rather than evidential. Root attenuation is “works today” in the operator digest but has “Basis: none” in G10; resource self-protection is presented as available “today, in code” but later marked “being built” (pp. 20, 28; pp. 10, 17).
- Prohibited comparisons remain explicit: “none makes consent, withdrawal or a human halt part of the message format itself,” references to what Tor leaves available, and claims about other vendors’ agents (pp. 5, 10, 15, 23–24).
- “Ending an agent leaves no environmental waste” exceeds its visible falsification test: G27 tests whether hardware or data was discarded **without a record**, not whether waste occurred (pp. 17, 33).

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 15, 32 | contradiction | Rule 5g allows an imposed safety/security/legal fix; G23 says upgrades are “not imposed” and rejects any recreation after refusal. | Check the binding section and align G23’s guarantee, exceptions and falsification test with it. |
| 2 | 2, 10, 18, 26 | overclaim | The executive summary and G3 promise group-existence secrecy; rule 1d and N3 concede traffic can reveal existence. | State the existing non-announcement guarantee and traffic-analysis limitation together wherever summarised. |
| 3 | 4, 18, 33 | overclaim | The executive summary promises no silent lineage fork without qualification; rule 11b limits this to witnessed lineages and says shipped roots have witnessing off. | Carry the accountable-stream/witnessed-lineage scope and shipped-mode qualification into the summary and G28 status. |
| 4 | 9, 21, 28 | contradiction | The steward’s duty not to sign reasoning they cannot evaluate “does not bind anyone yet” on p. 9; p. 21 presents it as a current instruction marked “works today.” | Make all three descriptions agree on whether this is current or future, using the binding rule. |
| 5 | 1, 7, 10, 13, 17, 20, 28, 31 | contradiction | Status claims conflict: resource protection is current on p. 10 but being built on p. 17; root attenuation works on p. 20 but is modelled/no-basis on pp. 13, 28; the identity guarantee has a stated bypass on p. 31. | Reconcile status at the individual-claim level; explicitly qualify gaps rather than attaching a broad “works today” label. Revise the introductory description of what counts as a promise accordingly. |
| 6 | 16, 25 | stale | “Harm has a remedy” in the promise index drops the legal qualification used by rule 8a and G25. | Replace the index wording with the qualified promise heading already used on p. 16. |
| 7 | 5, 10, 15, 23–28, 31–32 | editorializing | Comparisons, draft history and attributions remain: “none …,” “Tor included,” “none defined at rc8,” “retired 2026-10-11,” “on the steward’s direction,” and dated “steward ruling” notes. | Remove comparisons and historical/attribution commentary; state only the current rule, its limit and its evidence status. |
| 8 | 17, 33 | overclaim | “No environmental waste” is not established by a test for unrecorded disposal. | Make the guarantee and falsification condition describe the same existing duty; refer any substantive ambiguity to the steward. |

## Rendering
- G7’s identifier is broken into `Inv_X1_LatchDoesNotBlockSe` and `rving`, making an evidence reference difficult to transcribe (p. 27).
- The standalone heading “G12” is stranded at the bottom of p. 28; its entire entry begins on p. 29.
- G1’s status is isolated on the following page, and G5’s falsification sentence breaks after “comes up for,” separating both entries from their concluding status information (pp. 25–27).
- These observations are limited to the supplied page-marked text; clipping, glyph fidelity and table overflow cannot be confirmed without the rendered PDF.

## Effort estimate
Approximately 12–18 hours of editing and a rendered-PDF check, mostly mechanical reconciliation and deletion, with steward rulings needed where upgrade authority, current deferral duties or guarantee scope cannot be settled from the binding sections.

<!-- model openai/gpt-6-astra-pro; 34 pages; prompt_tokens 98184; completion_tokens 5326; 72s -->
