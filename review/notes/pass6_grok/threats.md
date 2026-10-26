# The Threat Model (ciris_constitution-1.0-rc12-threats.pdf, 47 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The non-goals are unusually explicit, but endianness, the Anonymous Tier claim, and a load-bearing CEWP leftover would not survive a hostile implementer, and the voice breaks the house rules on many pages.

## Strengths
- Non-goals are listed before the defences, each with a residual, and the text forbids representing CEG as providing the stronger properties (pp. 2–4).
- Shipped trust roots with witnessed mode off are stated as the current condition, not implied (p. 3, p. 31).
- The three “witness” constructions are distinguished and forbidden to be substituted for one another (p. 41).
- Fail-secure key exclusion is required to emit `hard_case:recipient_excluded` into the cohort, not to skip silently (pp. 9–10).

## Weaknesses
- Delivery-receipt inner bytes use “epoch (u64 LE)” and “K (u64 LE)” (p. 29). Chunk sealing says “epoch_be8 = the u64 epoch as 8-byte big-endian” and calls that “the CC 5.3.3.1 encoding” (p. 21; restated p. 8).
- Page 5 requires the Anonymous Tier for “unobservability against a global passive adversary at federation scope.” Page 46 says what the tier “does not yet buy,” including a relay that “can count the packets” and an anonymity set that “is small.” Shaping, called a prerequisite on p. 46, “is off by default” (p. 38).
- “The epoch-DEK key_grant cascade MUST wrap the DEK with wrap_algorithm: v2” (p. 6). “An unrecorded live call wraps nothing” (p. 8). The exception is not in the MUST.
- “No reachable holder MUST resolve to a ContentMiss” (p. 40) is ambiguous RFC 2119 English.
- Federation witness commits to “count mod target_rate” and makes “deviation from the constant tick” “a federation-tier slashing condition” (p. 41). `target_rate` is never defined; what is slashed is not said. The same paragraph uses “HMAC-SHA3”; p. 36 pins “HMAC-SHA3-256”.
- “cewp-key-grant/v1” is a literal KDF input that “MUST be used exactly as written” (p. 6, p. 21). “CEWP” also appears as “the ‘store at massive scale’ CEWP crux” (p. 17), “CEWP realtime A/V” (p. 24), and “the CEWP substrate” (p. 41). “the label CIRIS-AV-INNER-V1 is retired” (p. 26) is history.
- “keeps push-mode multicast relay/fan-out pull-only in 1.0” and “the parallel CHECK-arm migration” (p. 30) are process notes. Page 23 says “The low-latency realtime profile (direct Reticulum Links) is in 1.0 scope.”
- Comparative and editorial sentences: “the way MLS PCS provides” (p. 2); “beyond systems that ship default privacy with no in-network governance” and “The honest line:” (p. 5); “as in IETF Media over QUIC, CMAF, and MLS + SFrame” (p. 26); “a standard LXMF client” and “Python RNS” (p. 28); “What is distinctive is that the corner’s two known prices are bought back rather than paid” (p. 47).
- Unsourced figures: “~30%/hr”, “~3.1 Tbps”, “~2 Tbps content fan-out” (p. 7); “ML-DSA-65 sign ~330 µs” (p. 18); “~20–40% MDC compression overhead” (p. 24). Unverifiable from here. “The wire learns nothing from a shaped link at any setting” (p. 39) is stronger than the model narrative above it.
- “CC 3.4.4–3.4.2” runs backwards (p. 2). `hard_case` is pointed at both CC 3.4.4 (p. 9) and CC 3.4.2 (p. 12). “named as a bet, CC 8.3.1 R14” and “coherence-ratchet” (p. 3) are not rules. Title page attributes the volume: “Stewarded by Eric Moore” (p. 1).

## Opportunities
- One endianness sentence, applied to the receipt bytes on p. 29, removes an interoperability fork.
- Replace the p. 5 “MUST layer the Anonymous Tier” sentence so it cannot be read as delivering what p. 46 denies; point at the residuals already written there.
- Add the p. 8 “wraps nothing” case to the p. 6 MUST, or the MUST will be cited against the exception.
- Rewrite p. 40 as “If no holder is reachable, the consumer MUST treat the fetch as ContentMiss.”
- Delete p. 30’s scope-pointer paragraph, the “retired” sentence on p. 26, and the comparative sentences listed above. Do not silently rename `cewp-key-grant/v1`; a steward has to rule whether that pinned literal stays.
- Break the E1 wall (pp. 27–28) into numbered MUST/MUST NOT sentences. Schemas deferred to “a versioned OpenAPI document alongside this one” (p. 33) leave the endpoint section incomplete for an implementer.

## Threats
- A receipt written LE will not verify against a BE epoch, and both encodings are normative.
- A regulator can quote p. 5’s global-passive-adversary MUST against p. 46’s “does not yet buy” and p. 38’s shaping default. The same page says CEG “does not claim to detect harmful content inside private cohorts” and that the promotion tripwire “recovers the spreading-correlated child-safety catches” (p. 5).
- Page 5: “every link is attributed to a key” and anonymity “never means an unattributed sender.” Page 46: “the storage node sees the last relay, never the publisher.”
- Shipped roots run “with witnessed mode off” and “witness_quorum: 0” (p. 31). That is disclosed, and it is still a single-signer anchor until an amendment that is not in force.
- “by reduction to XChaCha20-Poly1305 IND-CCA + HKDF-SHA3” (p. 37) and “under the IND of HMAC-SHA3” (p. 41) assert proofs this volume does not contain. Normative HPKE text cites unstable drafts, “draft-connolly-cfrg-xwing-kem” and “draft-ietf-hpke-pq”, with no revision (p. 40).
- “The substrate MUST select per deployment based on whether the transport multicasts” (p. 8) uses “multicast” for TreeKEM commit delivery. Page 27: “Multicast is pull-only” and “There is no relay or fan-out tree.”

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 21, 29 | contradiction | Stream epoch is “8-byte big-endian”; receipt signing bytes say “epoch (u64 LE)” and “K (u64 LE)”. | One endianness rule; make the receipt match 5.3.3.1. |
| 2 | 5, 38, 46 | overclaim | Tier is required for GPA unobservability; shaping is off by default; the tier “does not yet buy” a small anonymity set or relay packet counts. | State only the residuals p. 46 already lists. |
| 3 | 6, 8 | contradiction | Cascade “MUST wrap” with v2; an unrecorded live call “wraps nothing.” | Put the kept-stream exception in the MUST. |
| 4 | 40 | unclear rule | “No reachable holder MUST resolve to a ContentMiss.” | Rewrite so MUST applies to the no-holder case only. |
| 5 | 41 | unclear rule | `target_rate` undefined; slashing has no object; “HMAC-SHA3” vs “HMAC-SHA3-256”. | Define the quantity and the algorithm, or delete the formula and the slashing sentence. |
| 6 | 6, 21, 26 | stale | Load-bearing `cewp-key-grant/v1`; “CIRIS-AV-INNER-V1 is retired.” | Keep or replace the KDF literal only by ruling; delete the retirement narrative. |
| 7 | 2, 5, 26, 28, 47 | editorializing | Comparisons with MLS PCS, other privacy systems, MoQ/CMAF, LXMF, Python RNS, and the anonymity trilemma. | Cut the comparisons; leave the rule. |
| 8 | 39 | overclaim | “The wire learns nothing from a shaped link at any setting.” | Replace with the limits the informative model already states. |

## Rendering
- Normative vocab token broken by a space: “X25519MlKe m768Aes256GcmHkdfSha256” (p. 6).
- Epoch-axis table columns run together: “federation_stream_chunks(stream_id, seq) Same rotation_chain” (p. 7).
- Adversary table is cramped across pp. 3–4; extracted cross-reference “CC 8.6. 1” (p. 3) and “CC 4. 4.3.4” (p. 15).
- JSON example breaks a quoted string across lines (p. 12).
- Error-table header hyphenates as “HTTP sta- tus” (pp. 34–35).
- E1 is one unbroken normative paragraph spanning pp. 27–28.
- No literal `**` or `\`, no empty sections, no clipped code block seen. Ordinary hyphenation elsewhere is not counted.

## Effort estimate
About two to three days: comparative and process sentences can be cut mechanically, but endianness, the wrap exception, the Anonymous Tier claim, `target_rate`/slashing, and whether `cewp-key-grant/v1` may change need the steward’s rulings.

<!-- model x-ai/grok-4.7; 47 pages; prompt_tokens 43111; completion_tokens 16723; 195s -->
