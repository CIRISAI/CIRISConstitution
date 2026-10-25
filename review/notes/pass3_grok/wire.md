# The Wire (ciris_constitution-1.0-rc11-wire.pdf, 110 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The volume promises one signing input and byte identity, but several normative passages specify two different byte strings for the same object.

## Strengths
- Signed, beside, and local placement is a closed vocabulary, and shape refusals at the signed-object door name a closed reason set (p. 37).
- Date-time and hex forms are reject-on-deviation, not advice: consumers MUST reject non-canonical forms when verifying (p. 61).
- The 1 MiB bound is defined on JCS bytes, with a separate intake ceiling so a receiver is not told to buffer unbounded input to measure it (pp. 34–35).

## Weaknesses
- CC 2.1 says field semantics are "consolidated here once" (p. 7), then CC 2.6.1.7 adds a second, longer member set (census, capacity, observation, charter) that CC 2.1 never lists (pp. 41–53).
- `subject_key_ids` is "member absent" when omitted (p. 32) and "Always present in the mirror, an empty array when there is no subject" (p. 39). Those are different JCS bytes.
- The omit-vs-materialize examples sign a flat object with top-level `attesting_key_id` and no `row`, no `asserted_at`, no `cohort_scope` (p. 29). CC 2.6.1.7 requires the mirror and `asserted_at` inside `attestation_envelope` (pp. 37–40). The example would be refused `envelope_member_missing`.
- Structural invisibility is normatively self|family only: "cohort_scope: self OR cohort_scope: family" (p. 72). The same primitive is then applied to community: "self/family and community/affiliations content alike emit holding claims only within the cohort (CC 5.2" (p. 99), and p. 5 says "self / family / community is never advertised to outsiders".
- At-rest encryption is both conditional and unconditional on one page: "WHEN self/family at-rest encryption is enabled" and, later, "when self/family at-rest encryption is enabled" (p. 73), against "it is always on" and "no operator switch turns that off" (p. 73).
- Delivery-receipt inner bytes use "epoch (u64 LE)" and "K (u64 LE)" (p. 92). Every other pinned integer in this volume is big-endian, including "epoch_be8 = the u64 epoch as 8-byte big-endian" (p. 84) and "u32_be" / "u16_be" (pp. 98–106).
- STH and lineage-head examples label signatures `"<base64-url>"` (pp. 74–75). The pin is "RFC 4648 §4 STANDARD alphabet, WITH padding" (p. 31). URL-safe versus standard is called out there as a silent verify failure.
- Key-record PQC is "REQUIRED once hybrid-complete" (p. 59). Later, "no hybrid-pending accommodation" and "There is no require_hybrid: false posture" (p. 80), and writes are "only at algorithm: hybrid" (p. 67).
- Rule 0 says "rules 1–4 below do not reach it" (p. 24). Rules 1–4 are above that sentence.
- "CC 3.4.4–3.4.2" (p. 2) is a reversed range.
- "a serve node MAY NOT" opt out of onion relay (p. 108). "MAY NOT" is not an RFC 2119 keyword; p. 5 says the same node "cannot opt out".
- CC 1.13.3.4 is marked normative and then argues policy: "teenager in a hostile household", "surveillance backdoor this framework refuses", "The honest line" (p. 5), and "This boundary is provisional" (p. 6). The volume's own cover says reasons belong to the charter (p. 1).
- "This answers the open question of how to attest about un-enrolled parties" (p. 15) is drafting history, not a rule.
- Symbol AEAD framing is specified twice, in full, at CC 5.4.2 and again at CC 5.4.3 (pp. 99–100 and pp. 102–103).

## Opportunities
- Make CC 2.6.1.7 the only member-presence table and reduce CC 2.1 to a pointer, so `subject_key_ids`, `asserted_at`, and the row mirror cannot diverge from the worked examples.
- Delete one of the two `K_record_id` derivations (p. 98 versus p. 106) and one of the two at-rest sentences on p. 73; each deletion is a ruling, not a new mechanism.
- Strike the ERC-8004 study, percentages, prices, and bibliographic citation from the adversary table (pp. 3–4) and leave the adversary class. Same cut for "DigiNotar" (p. 23), "the way MLS PCS provides" (p. 2), and "Tor v3 / I2P b33" (p. 109).
- Add one line to CC 5.3.6.1: admission tokens (`attestation_type_unregistered`, `federation_set_semantics_unsorted`, `asserted_at_stale`, and the rest of p. 37) are not HTTP codes, or map them. The error table (pp. 97–98) currently looks closed and is not.
- Replace "MAY NOT" (p. 108) with "MUST NOT". Point CC 5.4.3 at CC 5.4.2 instead of repeating the KDF.

## Threats
- A second implementation measured against "byte identity" (p. 1) can follow p. 29, p. 32, p. 74, or p. 92 and fail vectors generated from pp. 37–40, p. 31, and p. 84, and both sides can claim conformance.
- `K_record_id` is two algorithms. P. 98: bare HKDF-Expand over the raw exporter secret, info `"ciris-edge/scope-privacy/record-id/v1"`, and "MUST NOT route this label through RFC 9420 MLS_Exporter()". P. 106: `S_record` (`"ciris-scope-record-v1"`) "feeds K_record_id and K_symbol". Same name, different bytes, silent partition of holders (the failure CC 5.4.1 itself describes).
- Privacy claims a regulator can set against each other: non-goal "Relationship-existence privacy" because "family_id / community_id ride the envelope" (p. 2); "community is never advertised to outsiders" (p. 5); `community:listing:v1` "advertises the room" (p. 13); CC 5.2's MUST is only self|family (p. 72); CC 5.4.2 cites CC 5.2 for community and affiliations (p. 99).
- P. 1 leaves "whether a given MUST has shipped" to the register. P. 94 states shipped fact: "The shipped roots are minted with witnessed mode off (witness_quorum: 0". P. 4 repeats it in the adversary table. That is an earlier-design leftover sitting in the wire contract.
- The adversary table asserts external empirical findings — "3 %, 4 % and 15 %", "73.6 %, 59.2 % and 90.6 %", "$0.055, $0.0042 and $0.0027", and a named 2026 arXiv paper (pp. 3–4) — with no register row in this volume. Same class of unsourced magnitude: "~3.1 Tbps", "~65% of activity stays local" (pp. 70, 74), "~330 µs" (p. 82), "~20–40%" (p. 87).
- "One envelope, one signing input, one signature construction" (p. 1) is false of the volume: JCS(`attestation_envelope`) (p. 37), `sha256("ciris.sth_cosign.v1\n"||...)` (p. 75), a different lineage-head label (p. 75), and length-prefixed receipt bytes (p. 92).
- Roadmap residue in normative transport: "Relay / fan-out tree → 1.x" (pp. 86, 90), "/v1/steward-key is a kept alias" (p. 93), and "the open transport question" (p. 71).

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 98, 106 | contradiction | `K_record_id` is HKDF-Expand(raw `exporter_secret`, `"ciris-edge/scope-privacy/record-id/v1"`) and MUST NOT use `MLS_Exporter()` (p. 98); p. 106 says MLS-Exporter `"ciris-scope-record-v1"` "feeds K_record_id and K_symbol". | Keep one derivation. Delete the other sentence. Point CC 5.4.2 at the survivor. |
| 2 | 29, 37–40 | contradiction | Worked signing bytes are a flat object including `attesting_key_id` and omitting `row` and `asserted_at`. The signed object is `attestation_envelope` with a required seven-member `row` mirror and required `asserted_at`. | Replace the p. 29 objects with envelopes that match CC 2.6.1.7, or label them non-signing illustrations and say they are not canonical bytes. |
| 3 | 32, 39 | contradiction | Catalog: omitted `subject_key_ids` means "member absent". Mirror rule: "Always present in the mirror, an empty array when there is no subject". | One presence rule. If the mirror always carries `[]`, delete the "member absent" row. |
| 4 | 5, 72, 99 | contradiction | CC 5.2 MUST covers only "self OR family" (p. 72). P. 5 adds community. P. 99 says community and affiliations "alike" fall under CC 5.2. | State the scope list once. Make the other two sentences cite it without adding scopes. |
| 5 | 73 | contradiction | "WHEN self/family at-rest encryption is enabled" versus "always on" and "no operator switch turns that off". P. 72 also allows the invisibility claim "even when the at-rest bytes are plaintext". | Delete either the conditional or the "always on" sentence so a substrate has one branch. |
| 6 | 3–4 | editorializing | Normative adversary cells cite ERC-8004 rates, dollar costs, and "Xiong, X., Li, Z., Wei, W., Wang, Q., Knottenbelt, W., & Wang, Z. (2026) ... arXiv:2606.26028". Comparative claim plus attribution plus dates. | Remove the study, the percentages, and the citation. Leave the adversary class and the in-spec rule. |
| 7 | 31, 74–75 | contradiction | Byte fields "MUST use the RFC 4648 §4 STANDARD alphabet, WITH padding". Endpoint examples say `"<base64-url>"` for Ed25519, ML-DSA-65, and consistency-proof path elements. | Pick §4 or §5 in both places. One spelling in the request bodies. |
| 8 | 84, 92 | contradiction | Receipt signing bytes encode `epoch` and `K` as "u64 LE". The stream nonce the receipt is about encodes epoch as `epoch_be8`. | Either name LE as the single exception in CC 2.6.1.1.1, or change the receipt to big-endian. Do not leave both unmarked. |

## Rendering
- P. 22: the authority-source example is clipped mid-token and the string is never closed: `scope: ["personhood_consti` then "Reuses the existing structural primitive".
- Pp. 67, 70, 84, 89: exponents appear in the text as ordinary integers — "near 225 keys ... not 250", "216 identities" ... "240", "N = 106", "hard ceiling 232 -1", "MAX_CHUNKS_PER_EPOCH = 224 (~16.7M", "below 232". The parentheticals only match 2^25, 2^50, 2^16, 2^40, 10^6, 2^32−1, and 2^24. A copy-paste from this text layer implements the wrong constant. Same glyph loss on "km2" / "m2" (p. 64).
- P. 69: the vocab identifier is broken across lines inside the token (`X25519MlKe` / `m768Aes256GcmHkdfSha256`), so a reader cannot see whether a hyphen was inserted.
- P. 17: conformance-vector digests are wrapped mid-hex inside table cells; the email row's abbreviated tail `98d0a263f` does not match the 8-character ending of the full digest printed above it (`8d0a263f`).
- P. 2: duplicated word in a normative sentence, "family content content-holding confidentiality".
- No literal `**`, no empty section, no banned word (humane, dignified, graceful, farewell, "last word").

## Effort estimate
About a day of steward rulings on which byte string wins (defects 1–5 and 7–8), plus a few hours of mechanical cuts (ERC-8004 cells, clipped example, "MAY NOT", duplicate KDF, exponent markup).

<!-- model x-ai/grok-4.7; 110 pages; prompt_tokens 86970; completion_tokens 22480; 250s -->
