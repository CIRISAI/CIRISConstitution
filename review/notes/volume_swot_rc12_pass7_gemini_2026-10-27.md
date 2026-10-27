# RC12 volume review — pass 7, Gemini 4 Argon on the rc12 volumes after M16, 2026-10-27

**What this is.** The same brief, the nine volumes rebuilt from rc12 at `f7d2af2` (after M16 and the pass-6 rulings landed in `f0b6328`, edge's R103/R104 answers in `81746c7`, and the match-vector repair), read by `google/gemini-4-argon` over OpenRouter, nine calls in parallel, `tools/review_volume_external.py --max-tokens 60000`. Reports: `review/notes/pass7_gemini/<volume>.md`; every finding checked against the source by nine in-house verifiers with the added question of whether a confirmed finding is a regression, i.e. a defect M16 claimed to fix: `review/notes/pass7_gemini/verify_<volume>.md`.

**Cost and size.** 511,526 prompt tokens, 28,184 completion tokens, every call under 60 seconds; about $1.40 at the posted rates.

| Volume | Pages | Pass 5 (Gemini, rc11) | Pass 6 (Grok, rc12) | Pass 7 (Gemini, rc12 after M16) |
|---|---|---|---|---|
| Charter | 39 | 3 | 4 | 3 |
| Constitution | 68 | 3 | 4 | 3 |
| Wire | 109 | 3 | 4 | 3 |
| Dictionary | 110 | 3 | 4 | 3 |
| Reader's Policies | 35 | 3 | 4 | 3 |
| Mathematics | 21 | 3 | 4 | **2** |
| Evidence Register | 131 | 3 | 4 | 3 |
| Threat Model | 47 | 4 | 4 | 3 |
| Digest | 34 | 3 | 4 | 3 |

The first 2 of any volume, and the Threat Model's first 3 from Gemini. Every verifier answers the same question the same way: the volume reads better than at pass 6, because the pass-6 confirmed lists are gone from the source and Gemini names the surfaces that were contradictory (the signing input, the record-id chain, the receipt bytes, the polarity rows, the census preimages, the promise markers) as strengths. What Gemini finds is smaller-grained: reference hygiene, residue of transitional language, a handful of new rulings, and six regressions of M16 itself.

## The regressions M16 left (six, one of them serious)

1. **The `deferral:response` row in Part 3 was mangled** by the table fold that landed pass-6 item 18: a split on `|` that did not respect the escaped `\|` inside the cell, so the row lost its polarity cell and the generated registry carried the row's prose as its polarity, which opened the matcher's score gate for that family. **Fixed and regenerated in `056d886`** before this note; the lesson is in the build-pipeline memory.
2. **7.2.2's termination-safeguard sub-bullets still render flat**: M16 reindented them, but the converter never nests a bullet under a bullet. → P, one branch in `tools/_md2latex.py` or a four-line prose rewrite.
3. **The A/V symbol seal**: pass 6 asked that `part_5:764`'s XChaCha attribution be fixed; M16 fixed the attribution sentence and 81746c7 kept 5.4.2's symbol AEAD as the planned target, so the text now says three things about the A/V plane (AES-256-GCM at every layer; a symbol unit sealed under K_symbol with XChaCha; fragmentation only for the scope-privacy plane). → **R114.**
4. **Implementation-name residue** in the Policies (Verify / Registry / NodeCore in rule prose that pass 6 listed and M16 only partly role-worded). → M17.
5. **Digest tokens**: a persist commit hash in G7, "rc8" in G9, "One page" in the operator digest's lead. → M17.
6. **Mathematics items claimed by the pass-5 landing and never applied**, re-claimed by M16: `mass_to_fixed` without a tie rule (M12), calibration-to-register (M12), the `appended in version order … appended in version order` tautology at `part_6:77` (M15); and M16's own closing of the 6.1.3 separator list, which now names the inverse of the Part. → **R113** for the rounding rule, M17 for the rest.

## What is new and confirmed, by volume (M17 unless marked)

- **Charter:** the 0.1 % operations levy named twice with no base, collector or holder (→ **R110**); three "(CIRIS editorial — not reproduced Accord text)" parentheticals; RATCHET uncited with an unattributed quote; `actor_user_id` with no home in any Part; Annex B and D cited by letter only; four consecutive transitional sections at 1.15.10/1.15.11/1.16/1.16.1 (a cut question → R, low).
- **Constitution:** `part_3:714` and `:1165` still call the accord family `quorum:2/3` where 4.2.6 rules majority (the real half of the pass-6 misread); 4.5.13 promises "the table below" and the volume never renders it; "amendment authority rests with the founder, and with any accord-holder" at `part_4:1273` now diverges from STEWARDSHIP.md's one actor (M16 landed the one, not the other).
- **Wire:** E2's unconditional "multicast is pull-only, no relay or fan-out tree" against 2.1's `push` delivery mode (two-clause scoping); a mangled citation at `part_1:248` in the sentence M16 rewrote; three history phrases. Carried rulings: the Welcome inviter signature ML-DSA-65 alone (R89, two passes old; edge says deliberate → state the exception as a rule with its reason, **R115**); the onion layout against the staged tier (keep as planned, with R54's words).
- **Dictionary:** the `key_grant` struct's rotation chain and "supersedes the prior grant" against the rc7 row rule that a same-identity re-emission is idempotent and never removes a wrap (→ **R111**); the dangling `registry_witnesses` pointer; transitional language residue. Aside: the generated matcher refuses the bare wire strings `deferral:request:v1`, `deferral:response:approved:v1` and `identity_amendment:v1` (it reads the trailing version as a literal segment) and the vectors pin that refusal as expected → P, generator.
- **Reader's Policies:** 4.4.3.8's root-attachment sentence omits the `trust:accepts:v1` marker (the one finding that could mislead an implementer into a capability edge the cycle check refuses); three resolvers still walk a `supersedes` chain over a `community` Contribution after the roster became a `prev_head_digest`-chained row (→ persist's shape, **R117**).
- **Mathematics:** "Until the seat order is a signed row", the last roadmap clause in the volume (→ **R112**); `mass_to_fixed` takes a real with no tie rule while the pinned verifier signs `n_eff` as round-to-nearest over f64 and the text promises floor over committed integers (→ **R113**); the separator list; the `part_6:77` tautology; two measurement figures with no register row.
- **Evidence Register:** the stale "149 families / 968 vectors" in the 3.1.4 row (the manifests say 188 / 1236); the non-existent "Introduction's Liability section" and `CC 3.x`; two measured figures that are "not yet a register row" (need a RATCHET ticket to stage); five jargon-bearing claim summaries; four ASCII arrows in Annex F; five `[CC 2.4]` links pointing at Part 3.
- **Threat Model:** the broken link in 1.13.3.4 (survived one full edit of the line and the link checker, since it is a well-formed link to the wrong anchor); two acronyms and three temporal phrases; the symbol seal (regression 3).
- **Digest:** the "safety emergency" qualifier that only the Digest carries (→ **R116**); the triplicated preamble across the three pieces (a cut question, → R116); the G-table hygiene sweep.

## Rejected this pass

The KDF-hash "inconsistency" and the witnessed-mode "exposure" in the Threat Model; the depth-cap "contradiction" and `lenscore_detector` in the Policies; the WA-threshold "contradiction" and the `graceful` test symbols in the Register; the `roles` sorting and the four dependency mentions in the Wire; three Dictionary items; the Digest's G25/G26 half of item 2. Every rejected item is a misread of two rules as one, or a ruled matter.

## Rulings this pass asks for

| # | Volume | Question | Default |
|---|---|---|---|
| R110 | Charter | the 0.1 % operations levy (1.13.6 bug bounty; 7.x reward programme): no base, collector or holder anywhere | cut the number; "rewards are funded by the operator and disclosed annually" |
| R111 | Dictionary | `key_grant`'s rotation chain and "supersedes the prior grant" vs the rc7 row rule (idempotent re-emission, a wrap is never removed) | the row rule wins; the struct's supersession wording goes |
| R112 | Maths | "Until the seat order is a signed row" | state the limit as the rule: the door checks that each recipient is a seat; the expected per-seat share is a statistical check |
| R113 | Maths | `mass_to_fixed` without a tie rule; the verifier rounds `n_eff` to nearest over f64 while the text says floor over committed integers | the text's integer rule wins (R57 precedent): define the mass as an integer quantity, pin the tie, and ask Verify to match (ticket) |
| R114 | Wire/Threats (edge) | with fountain coding gone, does the A/V plane fragment into symbols at all? | no: the chunk rides whole under E1; 5.4.2 is retargeted to the scope-privacy plane alone, and the A/V sentences there go |
| R115 | Wire (edge) | R89 carried: the MLS Welcome's inviter signature is ML-DSA-65 alone | state the single-primitive exception as a rule with edge's reason |
| R116 | Digest | the "safety emergency" qualifier only the Digest carries; the preamble repeated across the three pieces | drop the qualifier; one preamble, in the plain piece |
| R117 | Policies (persist) | the roster resolvers walk a `supersedes` chain where the roster is a `prev_head_digest`-chained row | walk the lineage to the T6 head; "latest" is the head |

## What to do before the rc12 cut

Land M17, about forty-five mechanical items listed in the verify files with file:line, as one batch with the same file-set ownership and the same regression review as M16, plus the two pipeline items (nested bullets; the matcher's trailing-version read). Then cut. The rulings above are each one sentence; R114 and R115 wait on edge, R117 on persist, and none of them blocks a cut as guidance.
