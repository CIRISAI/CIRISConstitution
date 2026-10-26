# The Threat Model (ciris_constitution-1.0-rc11-threats.pdf, 48 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The wire sections are usable after a cleanup, but the volume contradicts itself on the privacy claim it invites reviewers to attack, and it breaks the house rules on comparison, attribution, and marketing.

## Strengths
- Non-goals are stated before positive claims, and "privacy" is limited to two named properties (p. 2).
- The adversary table has an explicit "NOT addressed" column, including single-signer roots while witnessed mode is off (pp. 3–5).
- Several identifiers are pinned to exact bytes, with conformance vectors printed in the volume (pp. 36–37).
- The three "witness" constructions are distinguished and forbidden to substitute for each other (p. 42).

## Weaknesses
- Global-passive-adversary unobservability is assigned to the Anonymous Tier (p. 2: "full sender/receiver unobservability at that scope is a separate, opt-in mechanism"; p. 5: a deployment that needs that model "MUST layer the Anonymous Tier"), while the tier itself does not provide it (p. 39: "Link setup stays observable"; p. 44: an observer still sees "the identity of the node that opened each link"; p. 47: "A relay can count the packets sent to one rendezvous in a period" and "with few users per relay the anonymity set is small").
- At-rest encryption is three different rules on one page: "WHEN self/family at-rest encryption is enabled", "always on … no operator switch turns that off", and invisibility "holds even when the at-rest bytes are plaintext" (p. 11).
- Delivery-receipt fields are little-endian — "epoch (u64 LE)", "K (u64 LE)" (p. 30) — while epoch and chunk sequence are big-endian everywhere else ("epoch_be8", p. 9; "u64 big-endian", p. 26).
- The adversary table cites another project and a paper, with figures that have no source in this volume: "3 %, 4 % and 15 %", "Xiong, X., Li, Z., … arXiv:2606.26028" (p. 3); "73.6 %, 59.2 % and 90.6 %", "$0.055, $0.0042 and $0.0027; same study" (p. 4). Same class of breach: "the way MLS PCS provides" (p. 2), "Megolm shape" (p. 7), "Sideband and the like" (p. 28), "Tor v3 / I2P b33" and "Vasserman et al., CCS 2009" (pp. 45, 47).
- Marketing and status sit in normative text: "You don't need a privacy policy … the wire format can't carry them" (p. 10), against p. 2's statement that group existence and churn are observable; "the thirteenth path … and the most product-complete" (p. 24); "This boundary is provisional" (p. 6); "named as a bet" (p. 4).
- Cover promises are not in the volume. Page 1 says the volume contains "the concerns ledger and the interoperability profiles of Part 8", that "the record of what was attacked and found is kept, including the attacks that succeeded", and that missing code is marked in "the register". The body is 1.13.3 plus Part 5 only. "formal/" (p. 1) is a code pointer.
- Unsourced or undefined quantities: "~65% of activity" (p. 12); "~3.1 Tbps", "~18.7 Gbps" (p. 8); "~330 µs" (p. 20); "~20–40%" (p. 25); shaping latencies "about 1.6 s", "about 380 s mean and 910 s" from "a model run on the production scheduler" (p. 40). "target_rate" is never defined, and the cover commitment is "HMAC-SHA3" with no digest length (p. 42), against HMAC-SHA3-256 elsewhere (p. 37).
- "Levicium" (p. 44) is not a name used anywhere else in the volume. "deviation from the constant tick is a federation-tier slashing condition" (p. 43) names a penalty this volume never defines; p. 15 says a different overdue signal is "not a slashing trigger".

## Opportunities
- Replace the GPA sentences on pp. 2 and 5 with the limits already written on pp. 46–47, so the opt-in is not described as full unobservability.
- One steward sentence on p. 11: delete either the "WHEN enabled" branch and the plaintext sentence, or the "always on" sentence.
- One sentence at p. 30 stating the receipt integer endianness, matching p. 26 or explicitly departing from it.
- Delete the ERC-8004 citation, percentages, and dollar figures (pp. 3–4), the ciris.ai block quote (p. 10), and the "thirteenth path" / "product-complete" sentence (p. 24). Keep the CEG-native addressed / not-addressed lines.
- Delete the second copy of the symbol-key formula (pp. 40–41); p. 38 already states it. Fix the LaTeX so identifiers and 10^6 cannot break (pp. 7–8).

## Threats
- A regulator or plaintiff can treat p. 5 and p. 10 as a privacy and child-safety warranty ("recovers the spreading-correlated child-safety catches … without scanning content that stays within its cohort") that pp. 2, 39, and 47 withdraw. The volume also tells operators to "State both the default protection and its residual limit in any user-facing privacy representation" (p. 5) while its own strongest sentences do not.
- An implementer cannot implement p. 11 or p. 30 without guessing. The canonical wrap name is broken across a line as "X25519MlKe m768Aes256GcmHkdfSha256" (p. 7), and the same page forbids any other spelling.
- Page 1 tells reviewers to attack "the single-signer transparency logs" first. Page 32 then states the shipped roots "are minted with witnessed mode off" and that attachment is by pinned fingerprint. "Mitigated" in the addressed column (p. 3) depends on a mode the document says is off.
- "draft-ietf-sframe" (p. 22) and "CIRIS-AV-INNER-V1 is retired" (p. 27) read as leftovers. A reviewer who knows the published SFrame RFC will treat the normative citation as stale. "→ 1.x" inside normative transport profiles (pp. 24, 28) is a release plan, not a rule.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 2, 5, 39, 44, 47 | contradiction | Anonymous Tier is the mechanism for "full sender/receiver unobservability" against an adversary "who observes every network link", but link setup, opener identity, and rendezvous counts remain visible, and the anonymity set "is small". | Make pp. 2 and 5 state only what pp. 46–47 already limit. |
| 2 | 11 | contradiction | "WHEN … enabled" vs "always on … no operator switch" vs "even when the at-rest bytes are plaintext". | One rule. Delete the other two sentences and align the pseudocode. |
| 3 | 3–4 | editorializing | ERC-8004 comparison, author list, arXiv id, and percentages/prices with no register row in this volume. | Delete the study. Leave the CEG rule in the "Addressed" cell. |
| 4 | 30 vs 9, 26 | contradiction | Receipt epoch and K are "u64 LE"; stream epoch and chunk_seq are big-endian. | One endianness, stated once. |
| 5 | 7–8 | rendering | Identifier split mid-token; "N = 106" where the arithmetic is 10^6 (83/s at 30%/hr); epoch-axis table cells collided ("Same rotation_chain" inside the location column). | Unbreakable identifiers, real superscripts, a table that does not merge columns. |
| 6 | 10 vs 2 | overclaim | "the wire format can't carry them in the first place" vs family_id on the envelope and observable membership churn. | Cut the quote. Point at 1.13.3.1. |
| 7 | 1 | overclaim | Promises Part 8, an attack record "including the attacks that succeeded", and a register of rules with no code. None of that is in these 48 pages. "formal/" is a path. | Rewrite the cover to name only 1.13.3 and Part 5, or bind the missing material. |
| 8 | 38, 40–41 | duplicate | The symbol_key / symbol_envelope formula is printed twice, byte for byte. | Keep 5.4.2; 5.4.3 should cite it. |

## Rendering
- p. 1: title broken as "The Threat / Model".
- p. 7: vocabulary token split, "X25519MlKe" / "m768Aes256GcmHkdfSha256".
- p. 8: "N = 106" twice; the 83 epochs/s and 18.7 Gbps figures only match 10^6. Epoch-axis table columns overlap; "su-persession" hyphenated. "CC 4." / "4.3.4" split on p. 16 is the same class of break.
- pp. 3–5: adversary table overfull; row labels and both result columns wrap mid-word ("Compromised substrate node", "Equivocating producer", "Placeholder identity").
- p. 21: render-tier table overfull; conditions break mid-phrase ("AVIF, HEIC / HEIF, JXL," / "WebM, MOV…").
- pp. 28–29: E1 is one unbroken paragraph across the page boundary.
- pp. 35–36: error-code column broken ("SIGNATURE_VERIFICATION_" / "FAILED", "WITNESS_DIRECTORY_" / "UNAVAILABLE", "HTTP sta-" / "tus").
- No literal `**` or stray backslashes seen. No empty heading. Code and the three CBOR vectors (p. 37) are complete.

## Effort estimate
About two to three days: a day of mechanical cuts, deduplication, and LaTeX fixes, and a day of steward rulings on the encryption switch, the Anonymous Tier claim, and receipt endianness.

<!-- model x-ai/grok-4.7; 48 pages; prompt_tokens 43273; completion_tokens 15542; 184s -->
