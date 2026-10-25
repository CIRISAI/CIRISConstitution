# RC11 volume review — pass 4, a third model family (GPT-6 Astra Pro), 2026-10-25

**What this is.** The same brief (`review/VOLUME_REVIEW_BRIEF.md`, now with a note that a 2026 citation after the reviewer's training data is unverifiable rather than fabricated), the nine volumes rebuilt at `6ebe9c5` (after the lethal-action ruling and R41/R42/R44/R50), read by `openai/gpt-6-astra-pro` over OpenRouter, nine calls in parallel. Tool: `tools/review_volume_external.py --max-tokens 60000`. Reports: `review/notes/pass4_gpt/<volume>.md`.

**Cost and size.** 1,505,874 prompt tokens as this model counts them (about three times Grok's count for the same text), 52,748 completion tokens, every call under two minutes. About $18 at the posted rates; if pro-mode reasoning is billed outside the completion count, the trailer does not show it.

| Volume | Pages | Pass 1 | Pass 2 | Pass 3 (Grok) | Pass 4 (GPT) |
|---|---|---|---|---|---|
| Charter | 40 | 4 | 5 | 4 | **5** |
| Constitution | 69 | 4 | 4 | 4 | **5** |
| Wire | 110 | 4 | 4 | 4 | **5** |
| Dictionary | 109 | 4 | 4 | 4 | 4 |
| Reader's Policies | 35 | 4 | 5 | 4 | **5** |
| Mathematics | 21 | 4 | 4 | 4 | 4 |
| Evidence Register | 131 | 4 | 4 | 4 | **5** |
| Threat Model | 48 | 4 | 4 | 4 | **5** |
| Digest | 34 | 5 | 4 | 4 | 4 |

Harsher than Grok on the same text, and more specific: the reports are shorter, nearly every finding carries two page numbers, and the model stated when it could not verify a thing from the text rather than calling it wrong. Its effort estimates sum to about 200–300 hours, which is the first estimate that matches what the three passes together have actually taken.

## What a third model family added

Checked against the source at `6ebe9c5` unless marked *to verify*.

**Confirmed, new in this pass.**
- The T8 claim row still said "a latched halt is NotRooted until lifecycle:active" after R41 removed that from the Part (register pp. 85–86). Fixed in this commit (`CLM-standing-verdict`).
- 7.4's new sentence said a lethal-capability deployment is "outside conformance by that fact", against the cover's "conformance is the wire" (charter pp. 1, 31). Fixed in this commit: it is a duty of adoption, and the wire refuses nothing for it.
- `from_join` (4.4.3.2, "no retroactive key_grant cascade") against the newcomer re-key walk of 4.4.3.4.1 that R9 landed as persist ships it (policies pp. 7, 12, 18). → R68, persist.
- The family-admission pseudocode returns from every `consensus_protocol` arm, so the acceptance loop under it ("a supersede never adds … every NEW member K needs K's own acceptance") never runs, and `admit` is never assigned (policies p. 19). → M11.
- The amendment heading still reads "WA quorum + 1-of-n sign-off" (4.5.1) under a strict-majority rule; "the two codified subkinds" (3.x) where `public` is now a third (constitution pp. 3, 17, 42–43). → M9.
- Location proofs are pinned at resolution ≤ 7, but the examples scope neighbourhood communities and hostile-event notices at resolution 8–10, where containment can admit nobody (constitution pp. 4, 6–7, 60; Part 3 lines 644, 687, 706). → R63.
- "I was in Austin from May to August is permanent" and "remains in the audit chain" (4.5.9) beside subject-withdrawal erasure (4.5.x) (constitution pp. 52, 61). → R61.
- Equivocation at T4a is "two heads for one lineage that each meet the witness quorum", with no "at one sequence number" or "neither descends from the other"; the ledger rule (3.x line 1716) has the qualifier (constitution p. 23). → M9.
- "a steward is responsible *for* a ward, never a holder *of* one" (3.2) and "a guardian holds a person, a steward holds an artefact" (3.4.13 vocabulary) (dictionary pp. 102, 104). → M9.
- "RFC 6962 padding: duplicate last leaf to next power of 2" (3.x line 123) is not RFC 6962's construction, and 6.1.1 uses odd-node duplication and says it does not adopt RFC 6962's prefixes (dictionary pp. 6, 9). → M9, with persist/edge asked which construction ships.
- 5g "A fix the steward requires for safety, security, or the law is imposed" against G23 "An upgrade is offered, not imposed … the container is not recreated" (digest pp. 15, 32). → R64.
- Annex F: "safe-state is the *only* permissible outcome under any condition" for A4 irreversible decisions, beside F-KPI-5's "100 % of irreversible actions under confirmed human authorization" and the hardware notes that contemplate activation. Pre-existing, exposed by today's lethal edit (register pp. 26, 28–29). → R65.
- `attestation:l*` used as the hard-constraint example in the aggregation table (4.4.2) while Policy I rejects that form at admission (policies pp. 5, 31). → M11.
- Legal references that are wrong on their face: "within 72 hours (GDPR standard)" for objection requests (GDPR has no such deadline; Art. 12(3) is one month), "DSA Art. 28b" (Art. 28), "NIST SP 800-218 (SLSA)" (800-218 is the SSDF; SLSA is a separate framework) (register pp. 46–48, 53). → M13.
- The register cover promises "the commit it was checked at" and the printed table carries neither claim ids nor pins (register pp. 1, 59–131). → M13, pipeline.
- The executive summary says outsiders cannot see "that they exist" of private groups; N3 and 1.13.3.1 concede an observer of every link can infer existence (digest pp. 2, 18). → M14.
- The claim summary "Nobody joins a family or community without their own consent, under every consensus_protocol" (`CLM-membership-consent`) against the infrastructure example's "members: the canonical installs … seated by the accord's blessing with no acceptance — a node has no agency" and `open:self_admit` (register pp. 73, 84, 112). → R78.
- Stewardship stated with four predicates across 3.2's admission description, boolean, "normative clarification" and the next page's "non-owner-purpose delegates_to" (constitution pp. 11–13). → R59, *to verify in full*.
- A halt "carries no TTL" (4.2.1.1) is the confirmed halt; the sentence sits before the fuse rule and reads as blanket (constitution pp. 28, 30). → M9 (one word: "confirmed", which the sentence already has; move the fuse sentence beside it).
- "a halted node is not serving" (4.2.1.1, in the resumption-offline reasoning) against the halt touching nothing but the agent's act gate (constitution pp. 30, 33). → R58.
- Withdrawal's temporal reach: a `withdraws` of a compromised key reaches behind to its `revoked_after` (3.2 "rotation is a supersedes, compromise is a withdraws") while a deputised duty's withdrawal leaves issued acts standing (4.4.x deputization) (constitution pp. 19, 55). Two cases that the text does not distinguish in one place. → R60.
- Census: the content-multiplicity gate (`max_source_multiplicity · n_min ≤ source_count`, 6.1.2.1) read against the census composite and secret poll, where identical ballots are the legitimate case (maths pp. 8, 20–21). → R66, *to verify which gates 6.1.9 applies*.
- `member_commitment` is verified "never [by] partial inclusion proofs" (6.1.1/6.1.2) while the census says every contributor checks "an inclusion path against member_commitment_hex" (6.1.9) (maths pp. 3, 7, 21). → R67.
- "Nodes and relays never encode or decode stored content" (6.1 durability) beside "a pure fabric node performs the entire retention function", which resamples and measures payload similarity (6.1.2) (maths pp. 2, 6, 8, 11). Two objects, the sealed blob chunks and the witnessed corpus the fold holds, not told apart. → R69.
- The signing examples in 2.x are flat objects without the `row` mirror or `asserted_at` (Grok found this too); and `subject_kind` is "NOT an envelope-level field" in 2.1 while the signed-object table says it "rides the envelope" (wire pp. 18–19, 27–31, 51). → M10.
- The stream nonce needs `stream_id_utf8`, `last_flag` and `link_seq`; the chunk layout carries `last_flag[1]` and the outer nonce `link_seq_be8`, but where a receiver obtains the UTF-8 stream id and the link sequence is not stated in the layout (wire pp. 84, 88–89; threats pp. 26–27). → M10, *to verify*.
- The bundle example is `"version": 1`; the rule is `GENESIS_BUNDLE_VERSION` 4 with `serve_transport_destinations` (wire pp. 91, 93–95; threats pp. 31–33). → M10.
- The merge table orders revocations "on `revoked_key_id`" while 2.x pins the raw-key digest as the subject (wire pp. 23, 78). → M10.
- "There is no window" in which a revocation stays local beside the 24-hour promotion window and the overdue-flagged terminal state (wire pp. 77–78; threats pp. 15–16). → R76.
- The hyphenated algorithm alias "MUST be rejected" and a deployment flag "MAY" accept it (wire p. 69; threats p. 7). → R77, *to verify the flag sentence*.
- A4 autonomy table: "A2: system acts within its ODD" against "below A3 the human is the actor" (charter p. 32). → M9, *to verify*.
- The DCP "proceeds through six ordered stages" against "Anything beyond the Standard is a steward's chosen and recorded conduct" (charter pp. 32–35; R23's residue). → R82.
- The sunset section still says "the Wise Authority has teeth", then that the name means the court, and states a five-year "Statute of claim" (charter p. 36; R27's residue). → M9.
- The biological-creation scope includes "offspring" while the duties say the creator's hold "does not loosen" and a made thing's "only route" to standing is the first-contact amendment; read literally this reaches human children, against 1.13.2 (charter pp. 10–11, 26, 29). Grok raised the same reading. → R81.
- The Charter's duties use lowercase "must" and plain imperatives while the substrate rules use RFC 2119 capitals; the cover should say the Charter does not use RFC 2119 (charter pp. 6, 17, 21, 26–29). → M9, cover.
- Capacity-plane claim rows: `consent:scope:*` is "descriptive only" in one row and the capacity gate "requires the subject's live consent:scope:analyze grant" in another (register pp. 88, 95). → R79, *to verify*.
- The guarantee rows and the plain rules disagree on status at the claim level: resource self-protection "today, in code" vs "being built"; root attenuation "works today" vs G10 "Basis: none"; the deferral duty "does not bind anyone yet" vs "works today" (digest pp. 9–10, 13, 17, 20–21, 28). → M14.

**Where the pass is unverifiable or wrong, checked.**
- The ERC-8004 study and the 8.6.1 citations: the model said "unverifiable from here, not evidence of fabrication", as the brief now asks. No correction needed.
- The 72-hour, Art. 28b and SP 800-218 findings are correct, not reviewer error; listed above.
- "Nextgov URL incomplete" is a line wrap in the PDF; the source URL is whole.
- The model could not see the PDF images and said so in every Rendering section; its rendering notes are limited to text-order facts (stranded headings, broken identifiers), all of which match what the two in-house passes saw.
- "A guardian holds a person" is the text's own sentence, not a misreading; the contradiction with "never a holder of one" stands.

## Rulings, pass 4 (R57–R82), and the mechanical sets (M9–M14)

Numbering continues from the pass-3 note (R41–R56). Defaults land on "land/defaults"; *steward* marks the ones where either side could be the rule.

| # | Where | The two sentences | Default |
|---|---|---|---|
| R57 *steward*, to verify | 4.2.1 reach rule vs 4.2.6 "the party bound is the party who granted, and can ungrant" | A halt binds the nodes holding a live `delegates_to(user → accord)` at `asserted_at`; a later cut does not escape it — vs ungranting ends the binding | The reach is fixed at `asserted_at`; a cut after it ends the node's exposure to *later* halts only; say so once |
| R58 | 4.2.1.1 resumption reasoning | "a halted node is not serving" vs the halt touches nothing but the agent's act gate | The halted *agent* is not acting; the node serves; the resumption proof is verifiable offline because it binds to the roster, not because the node is dark |
| R59 *steward*, to verify | 3.2 steward-binding (four statements) | Combined relationships / alternative paths / owner-binding edges alone / a non-owner-purpose `delegates_to` | One predicate (`is_steward_bound` as the gate folds it), quoted verbatim where the examples and the ownership distinction use it |
| R60 | 3.2 vs 4.4.x deputization | A `withdraws` of a compromised key reaches behind to `revoked_after`; an ended delegation leaves issued acts standing | Both, stated once as two cases: compromise reaches back to the bound; an ordinary end does not reach back |
| R61 *steward* | 4.5.9 vs 4.5.x erasure | A withdrawn location proof "remains in the audit chain", "is permanent" vs a subject's withdrawal erases ordinary rows | The proof is withdrawn like any row (body leaves serving; the tombstone stays); "permanent" names the fact that a proof existed, never its content |
| R63 | 2.x H3 rules vs Part 3 examples | Proofs ≤ resolution 7; neighbourhood and hostile-event examples at resolution 8–10 | Examples at ≤ 7; a finer community states its constraint at 7 and admits by invitation |
| R64 *steward* | plain 5g vs G23 | A required fix "is imposed" vs "offered, not imposed … not recreated" | An upgrade is never applied over a refusal; a steward who requires a fix and is refused shuts the agent down under 7.x and does not re-create it on the new image; G23 and 5g say this in the same words |
| R65 *steward* | Annex F clause 3.4 vs F-KPI-5 | "safe-state is the only permissible outcome under any condition" vs 100 % of irreversible actions under confirmed human authorization | An A4 irreversible action executes only under confirmed, effective human authorization; whenever that cannot be confirmed, safe-state; "under any condition" goes |
| R66, to verify | 6.1.2.1 multiplicity gate vs 6.1.9 | Identical ballots fail `max_source_multiplicity · n_min ≤ source_count` | The multiplicity gate is a corpus-fold gate; census returns and polls are gated by k (`source_count ≥ 10`) and the ratchet only |
| R67 | 6.1.1 vs 6.1.9 | "never partial inclusion proofs" vs "an inclusion path against member_commitment_hex" | The census check is a recomputation over the published member list; or the census is the one named exception. Pick one |
| R68 persist | 4.4.3.2 `from_join` vs 4.4.3.4.1 re-key walk | No retroactive cascade vs the newcomer re-key walk R9 landed | Whatever persist ships; if `history_on_join` decides, say so in both places |
| R69 | 6.1 durability vs 6.1.2 | "never encode or decode stored content" vs resampling and similarity over payloads | The degradation operators act on the witnessed corpus the fold holds; the blob layer holds sealed chunks and never opens them; two sentences, one each |
| R70 *steward*, to verify | 3.x canonical binding (dictionary pp. 77–78) | A canonical binding admitted on testimony grants withdrawal authority; no proof of control; a competing claimant is admitted too | Withdrawal authority follows the signing key, never a binding claim; a binding is evidence for consumers |
| R71, to verify | 3.x D1 vs 4.5.9 | "deletion is proven if withdrawn, superseded or hard-deleted" vs rows remaining in the audit chain | D1 proves a lifecycle change; a deletion is proven by the purge tombstone |
| R72, to verify | 3.4.11 vs 3.4.13 | Self-level adult "satisfies the band" vs provider level required to exit child protection | The stricter rule in the ladder section; the permissive sentence goes |
| R73 *steward*, to verify | 3.4.13 incapacity tiers | Prior will is "NOT a fresh WA adjudication" vs the T2 "WA due-process gate"; T1 provider powers vs "a panel for any continuing or asset-bearing power" | One table: prior will, provider, panel, with `HARD_DEADLINE` and the T2 cadence given values or named as community policy |
| R74, to verify | 5.3.3.5 E1 vs the bundle rule | An unsealed route request before the handshake vs the bundle as the only seed except pairing | One bootstrap sequence with its exhaustive exceptions |
| R75, to verify | 5.3.3.x anti-equivocation | "cannot show different chunk-K to different subscribers" vs witnesses cosign per epoch, rotation by time optional | State the witnessed checkpoint guarantee as it is |
| R76 | 5.2.x revocation | "There is no window" vs a 24-hour promotion window and an overdue-flagged state | Delete "there is no window"; the window is 24 h, the flag records a breach, delivery is not detection |
| R77, to verify | 5.1 wrap identifier | MUST reject the hyphenated alias vs a flag MAY accept it | No flag; one byte string |
| R78 | `CLM-membership-consent` summary | "Nobody joins … under every consensus_protocol" vs nodes seated without acceptance, `open:self_admit` | The summary names both exceptions |
| R79, to verify | two capacity claim rows | `consent:scope:*` descriptive only vs the gate requires a `consent:scope:analyze` grant | The grant's own `scope` carries `analyze`; the family name is descriptive; say it the same way in both rows |
| R81 *steward* | 7.3 creation scope | "offspring" in scope vs "the hold does not loosen" and the first-contact route to standing | One sentence: a human child is a person with unconditional standing under 1.13.2 and is never a "made thing" here; the duties of 7.3 on biological creation are the creator's duties, not a hold |
| R82 | 7.5 DCP | "six ordered stages" vs "anything beyond the Standard is chosen conduct" | Name which stages are the Retirement Standard and which are conduct |

**M9 Charter and Constitution.** The 4.5.1 heading and toc title lose "1-of-n sign-off"; "the two codified subkinds" → three; T4a equivocation gets "at one sequence number, neither descending from the other"; "a guardian holds a person" → "is responsible for"; the 3.x "RFC 6962 padding" sentence relabelled to the construction that ships (persist/edge asked); the `ledger:head:usd:v1` example → `USD`; the stale "capacity read boundary remains deferred and non-normative" sentence; the consent leaf list gains `community_trust`; `HARD_DEADLINE`, the T2 cadence and the teen grant maximum get values or are named community policy; the no-TTL sentence sits beside the fuse; the sunset paragraph loses "the Wise Authority has teeth" and the five-year statute (R27); the A2/A3 actor sentence made consistent (to verify); the charter cover says the Charter does not use RFC 2119.

**M10 Wire.** Signing examples as full envelopes; `subject_kind` nesting stated once; fingerprint length (10 vs a SHOULD of 16, to verify) with what decoders accept; "~5 km² edge-length" → area; the high-nibble sentence; the bundle example at version 4 with `serve_transport_destinations`; the merge table on the raw-key digest; where `stream_id_utf8` and `link_seq` come from, in the layout; SFrame and HPKE wording narrowed to the constructions used; "cosignatures[] is retired", the final-genesis assembler rollout, model-run history and vector-production history out.

**M11 Policies.** `admit_family_change` stores the arm's result and then runs the acceptance loop; the Austin/Alice example adds by proposal, acceptance and widening (R13's twin); `resolve_consent` reads admitted `withdraws` first; `attestation:l*` → an admitted mechanism dimension; the member-set sentence says whether the seven are the complete v1 set; the institutional data-subject read grant and the Commons promotion stated as the exceptions to "no non-member holder"; story counts, "Closes G3", the Fricker attribution, "Per CIRISNodeCore", "the four implementations" out.

**M12 Mathematics.** `mass_to_fixed` gets a rounding convention and range; "byte-exact prefix" → "fields appended in version order; the version field differs"; the activity bit defined once in the return; calibration figures tied to register rows; the n_eff "never understates" sentence scoped to the mechanised results; the four-period interpretation moved into the field definition.

**M13 Register pipeline and Part 8.** Print the claim id and pinned commit per row; dedupe evidence pointers; "72 hours (GDPR standard)" → Art. 12(3) one month; "DSA Art. 28b" → Art. 28; "NIST SP 800-218 (SLSA)" split; `controller_si_threshold` and the Annex B §9 cite checked; Annex J inner numbering rebuilt; 8.6.4 lists the stewards it announces; "discharges Art. 50(2)", "one set of controls suffices", "satisfied by storing" → engineering correspondence, legal sufficiency unreviewed; the concerns ledger's "settled" excludes PARTIALLY CLOSED and STAGED; the Register cover names the Part 8 sections it carries (pass 3).

**M14 Digest and pieces.** The existence sentence carries N3's limit; "no founder can fork silently" carries the witnessed-lineage scope and the shipped mode; status markers reconciled per claim (resource protection, root attenuation, the deferral duty); "Harm has a remedy" → the qualified heading; G27's test and 10d's "no environmental waste" describe the same duty; comparisons out.

**Peers.** Persist: R68 (`from_join` vs the re-key walk), the Merkle construction of 3.x line 123, R43/R46/R47/R53 from pass 3. Edge: #891 plus the stream-nonce input carriage (M10) and the alias flag (R77). Verify: `accord_proposal` lost the `fire` action (R42). CIRISAgent: lethal action in the never-allowed capability set.

## Reading the four passes together

Pass 1 found rendering; pass 2 the contradictions the rendering had hidden; pass 3 a second layer of older design sentences beside the ruled ones; pass 4, from the strongest outside model, a third layer that is mostly *examples and summaries that lag their rules*: pseudocode that never reaches its own gate, a bundle example two versions behind, a claim summary that outlived the ruling, resolutions in an example the rule forbids, a status marker that disagrees with its evidence row. Those are the cheapest class to fix and the most damaging to leave, because an implementer copies the example. The six 5-scores are honest: the rules are sound and the volumes are not yet safe to copy from. The order of work that follows is R57–R82 with Eric, then M9–M14, then a fifth pass on a different family again.
