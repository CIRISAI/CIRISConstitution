# Pass-6 (Grok 4.7) Mathematics report — verification against rc12 source

**Report:** review/notes/pass6_grok/maths.md. **Care score recorded:** 4.
**Grok's verdict paragraph (recorded):** "The substrate rules are mostly stated as checkable predicates with explicit limits, but several of those statements contradict each other and two normative byte layouts are broken, so this volume needs steward rulings before 1.0."
**Verifier's reading of the verdict:** the "two broken byte layouts" are PDF line-wrap artefacts, not source defects. The contradictions are mostly real; five of them are pass-3 M4 items that were planned on 2026-10-25 and never landed in the source, and R51 is likewise unlanded.

Source: P6 = `constitution/part_6_the_coherence_mathematics.md`; CB = `formal/census_ballot/CensusBallot.tla`; P3 = `constitution/part_3_the_namespace.md`.
Dispositions: M = mechanical fix, R = steward ruling, P = pipeline, X = reject.

## CONFIRMED

1. **k_eff: deny-threshold "safe" vs "MUST NOT gate"** (Top #1).
   - Source: P6:126. Quote: "A threshold that **denies** on low `k_eff` is therefore safe, while a threshold that **grants** on high `k_eff` is the exposed direction and MUST NOT be the sole gate for any capability." Same paragraph, last sentence: "This document states **no operating band** for `ρ̄`, for `k_eff` or for any ratio derived from them, and an implementation MUST NOT gate on one."
   - Note: Grok's quote is a paraphrase (the ban is on gating on an *operating band*, not literally "on k_eff"), but a deny threshold is a band, so the conflict stands. The no-gate sentence dates from RC3 (71ab0a5, 2026-08-01); the deny-is-safe sentence arrived with the rc11 Part 6 cut (b79dbea).
   - Earlier: pass3 Grok obliquely (threats: the Lean witness is k_eff, "which MUST NOT be a gate").
   - Disposition: **R** (does a deny-only threshold stand? if yes, a one-sentence M: "pins no band; an implementation MAY deny on low k_eff at a threshold of its own and MUST NOT grant on it").

2. **Withdrawn "then none" vs the gist survives** (Top #2).
   - Source: P6:170 "an item that is un-marked, or withdrawn, **descends** — fewer holders, then none ([CC 6.1.2.2])" vs P6:176 "**Revocation does not require destroying the collective gist**" and P6:132 "`descend` past the noise floor yields the blur, never an empty/destroyed object."
   - Earlier: pass3 #5 → planned as M4 ("the chunk set of a withdrawn item descends to zero holders; the collective gist of witnessed content is a different object"). **Not landed.**
   - Disposition: **M** (the M4 wording; the 6.1.2.2 cite is the misdirection, cite the chunk layer instead).

3. **"Every CC 6.1 object never instantiates a CC 2.1 Contribution / never enters JCS" vs "the composite is a CC 2.1 scores row"** (Top #3).
   - Source: P6:159 vs P6:309.
   - Earlier: pass3 #2 (R51 ruled: census shares, composites and ballots are JCS Part 2 rows; the 6.1.2–6.1.4 preimages are binary), pass4 #4, pass5 threats. R51 **not landed** in 6.1.3.
   - Disposition: **M** under R51.

4. **Ratchet: tenth-clip vs third-fall** (Top #5).
   - Source: P6:313 "it falls by at most a tenth per period (a larger fall is clipped to that tenth) ... A fall of more than a third in one period is read as a partition".
   - Model check: the fall is measured on the raw composite, not the base. CB:212 `fall == ~frozen /\ ea * FreezeDen < prevEA * (FreezeDen - FreezeNum)`; README:25–26 "a one-period fall of the composite by more than one third freezes it". Prose is ambiguous; should say "a fall of the count".
   - Earlier: none. Disposition: **M**.
   - **Adjacent mismatch found while checking (new):** prose P6:313 says the freeze holds "until two consecutive periods each return at least two thirds of the pre-fall count" (from a9b6777), but the model releases after ONE recovered period (CB:213 `recovered == frozen /\ ea * FreezeDen >= freezeRef * (FreezeDen - FreezeNum)`, CB:245–248 the normal step ends the freeze; README "the freeze is released by recovery to ⅔ of the pre-fall composite"), and the paragraph's own last sentence (P6:317) says "the freeze released at two thirds of the pre-fall count" with no second period. Disposition: **R** (one period or two), then model or prose follows.

5. **`retention_priority` in the freeze-gate vector list** (Top #7).
   - Source: P6:166 "the holding claim and compress request of [CC 6.1.5] + `retention_priority`" vs P6:162 "**`retention_priority`** (never on the wire) are edge-internal" and MUST NOT be over-pinned; P6:179 PIN line "`retention_priority` = **edge-internal** (never on the wire)". The chain manifest keys `retention_priority` to 6.1.3 only.
   - Earlier: none. Disposition: **M** (drop it from the gate list, or label it a recommendation vector).

6. **"The only path from measurement to action is the mesh-config plane"** (Top #6).
   - Source: P6:13 (unqualified "action") and P6:184 ("Measurement changes a node's behaviour through exactly one path") vs P6:302 (the census "supplies the expected-active base that [4.5.13] counts governance against") and P6:313 ("the base and every narrowing relief freeze").
   - Partly confirmed: 6.1.5.1's node-behaviour phrasing is defensible; the 6.1 intro's "action" is not. Also "narrowing relief" occurs nowhere else in the constitution or the model (the model freezes the base only; `grep -rn narrowing constitution/` finds no definition).
   - Earlier: none. Disposition: **M** (qualify the intro to node behaviour; define or drop "narrowing relief").

7. **`hard_case:*` called a "reserved-prefix candidate"** (Threats).
   - Source: P6:32 "surface them as a `hard_case:*` ([CC 3.4] reserved-prefix candidate)". `hard_case:{kind}` is registered as **Open vocabulary** at P3:519 (section 3.1.9.4), not 3.4, and is not a candidate.
   - Earlier: none. Disposition: **M** (drop "candidate", fix the cite).

8. **6.1.7 cites N1/N2 as gating "the mechanisms of this Part"**.
   - Source: P6:292 "gated by steward binding and founder quorum (N1) and the chain-length and cycle budget (N2)" vs N1/N2 defined at P6:298–299 for `recursive_trust_bootstrap` only. Forward reference plus overgeneralisation.
   - Earlier: none. Disposition: **M** (minor: "trust discovery gated by ...").

9. **Pass-3 M4 leftovers still in source** (each previously raised, none landed):
   - "etc." in the normative separator list — P6:160. pass3. **M**.
   - "is said to be —" dangling — P6:134. pass3 #7. **M**.
   - "rounded to a grid of max(k, two significant figures)" — P6:312. pass3 #8. **M**.
   - "CEWP-1.0" undefined in the volume — P6:184. pass3, pass5 #6. **M**.
   - Lean and `formal/` paths in prose — P6:126 (`lean:coherence-ratchet:Core.BaseIdentity`, `Core.SignalSourceDiscount.clique_neutralization`), P6:317 (`formal/census_ballot`); the cover (R52, landed) now says the register pins them. pass3, pass5 #5. **M**.
   - "verified by an unspecified upstream tier" — P6:286. pass3 (M4 list). **M**.
   - "why v3 exists" design history — P6:120. pass4. **M** (trivial).

10. **Rendering** (all **P**):
   - `max_source_mult` clipped and `)` dropped at a line break — source P6:76 is an intact prose sentence with inline code. pass3 #6, pass4 #8, pass5 #8. **P**.
   - `budget_bytes)` on its own line in the StorageBudgetV1 block; "NEVER self/ family" split in CorpusWantV1 — source P6:213, P6:233 comments intact. pass3, pass4, pass5. **P**.
   - "1/N2" for `1/N²` — source P6:45 `T·(1 + 1/N + 1/N² + …)`; confirmed by pdftotext on volumes/ciris_constitution-1.0-rc12-maths.pdf ("1/N + 1/N2 + ..."). New. **P** (glyph map; the rc9 commit da37578 mapped superscripts 0–3 for pdflatex, ² evidently not on this path).
   - "≠" printed as "=" plus combining long solidus — source P6:298 `trust ≠ membership`, `TRUST≠MEMBERSHIP`; confirmed in the rc12 maths PDF and also in the rc12 wire PDF, so systemic. `tools/_md2latex.py:332` maps ≠ → `$\neq$` but the output shows the mapping is not reached for this text. New. **P**.

11. **Integer dominance test** (Opportunity).
   - Source: P6:111 `n_eff ≥ min_ratio · source_count` with pinned `min_ratio = 0.5`; `n_eff * 2 >= source_count` is exactly equivalent over integers and matches the no-IEEE-754 rule at P6:114. New. **M**.

## FALSE / MATTER-OF-TASTE / REJECT

12. **Privacy "overclaim" from sender-chosen seats** (Top #4, Threats). **FALSE** as framed.
   - Secrecy holds for any pair that does not both collude (CB `Inv_SharePrivacy`, conditional on the two aggregators not both colluding; formal/ADEQUACY.md A18). A sender choosing its own pair exposes only its own return; what weakens is the expected per-seat share check, which P6:317 states in terms ("a statistical check, not an enforced one").
   - Real residue (minor, **M**): P6:308 "two serve seats per period" vs P6:317 "the pair of seats for a period is the sender's choice among seats" — if there are exactly two seats there is no choice. The model README:19 draws federation seats by `H(period ‖ class)`, which the prose never states. One sentence on the draw and the gap, placed with the opening claim.
   - Earlier: pass4 questioned the strength of the directory-count bound (adjacent).

13. **"Stuffing ceiling, enforced" beside "colluding aggregators can invent tokens"** (Threats). **X**. Different claims: the per-return validity proof caps one return at one count per bucket; aggregator forgery is a separate attack bounded by the directory's bucketed count. Not a contradiction. pass4 raised the bound's strength.

14. **Normative pins with no derivation in the volume** (ε = 0.05, min_ratio = 0.5, 0.950 / ≥ 0.99, k = 10, "nine instances with eight twins"). **MATTER-OF-TASTE / X**; pass3 raised; the cover says the register pins them. Arithmetic checked: mean |Δ| of two uniform bytes = 85.33, 1 − 85.33/255 = 0.665 (text's ≈ 0.667 acceptable); cosine of independent all-positive byte vectors = E[x]²/E[x²] ≈ 0.7485 (text ≈ 0.75 correct); Kish `k/(1 + ρ̄(k−1))` and ceiling `k_eff ≤ 1/ρ̄` correct; inverse-Simpson `(Σm)²/Σm²` correct, 90 % single source → floor 1 correct; "nine instances, eight twins" matches ADEQUACY A18 and formal/census_ballot/README.md (20 cfgs = 9 ruled instances + 8 twins + 3 reachability dyes).

15. **R9, HE-300, "LP pair-pinning gate" leftovers** (Threats). **MATTER-OF-TASTE**; pass3 raised HE-300 as undefined (P6:166). HE-300 is cited as what Annex J is, which is a legitimate cross-reference; "R9" is a named residual, used consistently. Optional M.

16. **"With a holder a whole copy" missing words** (Weaknesses). **MATTER-OF-TASTE**; P6:191 is a terse but grammatical absolute clause ("With a holder [being] a whole copy, an item is recoverable while at least one holder is live"). Optional M ("Each holder holds a whole copy, so ...").

17. **Redundancy keys refused "until" their consumer ships** (Threats, P6:188 "whose consumer arrives with the durability tier (until it does, rule (2) refuses them)"). **X** for this pass; pass4 raised it; a known planned state the text states truthfully. R if the steward wants the keys out of the list until shipped.

18. **"Effective-count discount advertised as a mechanised result that binds by being true (p. 1) and then withdrawn as a gate (p. 8)"** (Threats). Folds into item 1; pass3 raised. The cover is accurate (a theorem binds by being true; the text still pins no band). **R** via item 1.

19. **"Code and model paths after p. 1 says the register pins the repositories"** — covered in item 9; the cover's R52 fix landed (cover now names the implementer and the register), the body paths did not move. **M**.

## Summary

Seven of eight top defects confirmed (#1, #2, #3, #5, #6 partly, #7, #8); #4 is false as a privacy claim and survives only as a two-sentence wording tension. Five confirmed items plus the leftovers list are pass-3 M4 fixes planned on 2026-10-25 and never applied to Part 6, and R51 is likewise unlanded.
New this pass: the `retention_priority` gate-list conflict, the stale `hard_case` "candidate" (wrong section too), two glyph failures (² and ≠, the latter systemic across volumes), and a prose-vs-model mismatch on the freeze release (two periods in prose, one in the model) that needs a steward's word.

**Counts:** 11 CONFIRMED groups (8 single findings + the 7-item M4 leftovers group + 4 rendering items + 1 opportunity); 1 FALSE; 4 MATTER-OF-TASTE; 3 REJECT/folded. Dispositions: R 2 (k_eff band; freeze release one vs two periods), M 18 items, P 4, X 3.
