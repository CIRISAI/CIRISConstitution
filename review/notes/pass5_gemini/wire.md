# The Wire (ciris_constitution-1.0-rc11-wire.pdf, 110 pages)

**Care score:** 3  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The core wire, canonicalization, and cryptographic specifications are exceptionally tight and backed by concrete test vectors, but an internal contradiction on base64 alphabets, conflicting multicast topologies, and several stale database/code artifacts need cleanup before 1.0.

## Strengths
- **Explicit adversary model and bounded privacy claims:** Section 1.13.3 (pp. 2–6) clearly delineates what CEG protects and what it does not (e.g., traffic analysis, communication graph, PCS), preventing operator overclaims.
- **Byte-exact determinism and test vectors:** Canonicalization gaps left open by RFC 8785 JCS (set vs. sequence array sorting, byte encodings, timestamps, IEEE-754 number totality) are explicitly closed (pp. 30–35), and concrete conformance/reject vectors are provided inline for canonical-hash preimages (pp. 17–18) and CBOR `record_id` derivations (p. 99).
- **Single-source signed-object schema:** The comprehensive 23-page member placement table in 2.6.1.7 (pp. 37–60) is generated from the same source as the CDDL and JSON schemas, eliminating spec-vs-manifest drift on envelope structure.
- **Clear cryptographic domain separation:** Every HKDF, HMAC, and signature preimage pins its exact ASCII domain-separation label, endianness (`u64_be` vs `u64_le`), and concatenation rules (pp. 69–71, 75, 84, 89, 91, 98, 100, 103, 106).

## Weaknesses
- **Base64 alphabet contradiction:** Section 2.6.1.1.1 (p. 31) mandates that "every field documented as base64 MUST use the RFC 4648 §4 STANDARD alphabet, WITH padding," but the endpoint schemas in 5.3.1 (pp. 74–75) specify `"<base64-url>"` for `ed25519_signature_b64`, `mldsa65_signature_b64`, and `consistency_proof_path_b64`.
- **Contradiction on multicast relay / SFU topology:** Section 5.3.3.2 (p. 86) states that for large realtime groups (`≫50`), transport is "pull-only ContentFetch (CC 5.3.3.5 E2), as for broadcast; no selective-forwarding relay role," and 5.3.3.5 E2 (p. 90) states "There is no relay or fan-out tree." Yet 5.3.3.2.2 (p. 87) refers to "(direct Reticulum Links / SFU at scale)", and 5.3.3.2.1 (p. 86) and 5.3.3.2.3 (p. 88) design clear-metadata `codec_id`/`ChunkLayer` headers specifically so "a relay drops by `(codec_id, layer)`" when "fanning out chunks."
- **Envelope member placement and nullability mismatches between 2.1, 2.4.2, and 2.6.1.7:**
  - In 2.1 (p. 7) and 2.4.2 (p. 27), `attesting_key_id` and `attested_key_id` are listed as substrate fields outside `attestation_envelope` (or top-level in the 2.6.1.1 example on p. 29), whereas the normative 2.6.1.7 table (p. 38) puts them inside `attestation_envelope.row` (`row.attesting_key_id`, `row.attested_key_id`).
  - The 2.4.2 wire-shape code block (p. 28) shows `"oversight_mode": "<HITL | HOTL | HOOTL | null>"` and `null` as an allowed wire value for `occurrence_*`, directly violating 2.6.1.1.1 (p. 31), which rules that "an explicit JSON `null` on any optional envelope member is refused as malformed... `envelope_member_null`."
- **Duplicate specification of A/V symbol AEAD framing:** The `symbol_key` HKDF-SHA3-256 derivation and `symbol_envelope` XChaCha20-Poly1305 structure are specified in 5.4.2 (pp. 99–100) and then repeated almost verbatim in 5.4.3 (p. 102).
- **Duplicate entries in the 2.6.1.7 table:** `halt_fuse_secs` appears both under "members persist types" (p. 42) and under "members this text types and persist carries untyped" (p. 49).
- **Comparative claims about external projects:** Violating the house rule against comparative claims, 1.13.3.4 (p. 5) claims "What CEG adds beyond systems that ship default privacy with no in-network governance is fails-secure governance...", and 5.3.2.6 (p. 83) makes comparative capability claims about Signal (`"Signal’s webpsan"`) and Apple (`"iOS has no WebM / Opus playback"`).
- **Marketing citations and self-congratulatory editorializing:**
  - Section 5.2 (pp. 72–74) repeatedly cites marketing copy (`"The load-bearing claim from ciris.ai/cewp"`, `"the cewp privacy promise"`, `"Locality dividend (cewp claim): the structural invisibility mechanism is why ~65% of activity stays local in the cewp scaling model"`).
  - Section 5.3.3.2 (p. 85) editorializes: `"this is the thirteenth path on the CC 1.7 claim and the most product-complete"`.
- **Stale design history and migration notes in normative text:**
  - Section 2.3.2 (p. 15): `"This answers the open question of how to attest about un-enrolled parties..."`
  - Section 2.6.1.1 (p. 29): `"# Producer A -- omits epistemic_mode (relies on S4 default)"` ("S4" is a leftover section numbering artifact).
  - Section 2.6.1.2 (p. 32): `"an edge admitted before the member was required stays valid, T4"`.
  - Section 5.3.3 (p. 83): `"with the new CC 5.3.3 streaming endpoint set"` (also on p. 13).
  - Section 5.3.3.8 (p. 92): `"(the streaming-chunk store + the parallel CHECK-arm migration)"`.
- **Code/implementation leakage:** Section 2.1 (p. 8) defines `occurrence_id` format `"per the agent’s AGENT_OCCURRENCE_ID env var"`; 5.1 (p. 72) refers to `"[LensCore knob, NOT a substrate constant]"`; 5.4.6 (p. 107) notes `"Per-destination announce control is a small Leviculum substrate extension"`.
- **Unsourced quantitative claims in prose:**
  - Section 5.1 (p. 70): `"at N = 10^6 and realistic audience churn (~30%/hr), one rotation per departure ≈ 83 epochs/s → a flat-unicast cascade of ~3.1 Tbps — exceeding the ~2 Tbps content fan-out itself."` (Packet/grant sizes and stream bitrates behind the 3.1 Tbps and 2 Tbps numbers are not shown.)
  - Section 5.2 (p. 74): `"why ~65% of activity stays local in the cewp scaling model"`.
  - Section 5.3.2.4.5 (p. 81): `"ML-DSA-65 sign ~330 µs"` (no hardware baseline cited).
- **Incomplete key-revocation wire specification:** Section 2.4 (p. 21) and 2.4.1.1 (p. 23) state that a key revocation is a `key:revocation:v1` row on the attestation plane and that "The signed revocation binds eight members — `revocation_id`, `revoked_key_id` (string or null), `revoked_key_sha256_ed25519_raw`, `revoking_key_id`, `reason` (string or null), `revoked_at`, `effective_at`, `scrub_timestamp`." None of these eight members appear in the 2.6.1.7 signed-object table, `scrub_timestamp` is explicitly declared to be *outside* the signed bytes in 2.6.1.7 (p. 57), and allowing `(string or null)` contradicts the `envelope_member_null` rule of 2.6.1.1.1 (p. 31).

## Opportunities
- **Unify the envelope examples with 2.6.1.7:** Updating the JSON snippets in 2.4.2 (p. 27) and 2.6.1.1 (p. 29) to include the `row` mirror object and removing `| null` from the 2.4.2 type comments will prevent implementers from building against an outdated pre-mirror envelope shape and hitting `envelope_member_missing` or `envelope_member_null` at the gate.
- **Deduplicate 5.4.2 and 5.4.3:** Merging the repeated `symbol_key` / `symbol_envelope` block in 5.4.3 (p. 102) into a single pointer back to 5.4.2 (p. 100) cuts a page of redundant normative text that could otherwise drift.
- **Strip `ciris.ai/cewp` and implementation pointers:** A quick pass on 5.1–5.3 to remove references to `ciris.ai/cewp`, `CHECK-arm migration`, `AGENT_OCCURRENCE_ID`, and `Leviculum` will bring Part 5 up to the clean, timeless standard of 2.6.1.7.

## Threats
- **Silent signature verification failure on STH and lineage-head cosigning (p. 31 vs. pp. 74–75):** An implementer following the global rule in 2.6.1.1.1 (standard base64 with padding) will emit `+`, `/`, and `=` in `/v1/transparency/sth/cosign`, while a server implementing the endpoint schema in 5.3.1 (`<base64-url>`) will reject or mis-decode the signatures.
- **Implementer confusion over `key:revocation:v1` signing input (p. 23 vs. pp. 31, 37, 57):** An implementer building key revocation from 2.4.1.1 (p. 23) will serialize ` null` for absent `revoked_key_id`/`reason` and include `scrub_timestamp` inside the signed object, which a conformant 2.6.1.7 ingest gate will reject with `envelope_member_null` while stripping `scrub_timestamp` to the `beside:signature` container.
- **Envelope mirror discrepancy (pp. 27, 29 vs. pp. 37–40):** Because 2.4.2 and 2.6.1.1 show `attestation_envelope` without the mandatory `row` mirror object (or with `attesting_key_id` at the top level of the JSON rather than under `row`), a developer reading sequentially from 2.1 through 2.6.1.1 will write a non-conformant serializer before reaching 2.6.1.7 on p. 37.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 31, 74–75 | contradiction | 2.6.1.1.1 mandates RFC 4648 §4 standard base64 with padding for all base64 fields, but 5.3.1 specifies `<base64-url>` for STH and lineage-head cosignature fields. | Change `<base64-url>` in both 5.3.1 JSON schemas (pp. 74–75) to `<base64>` per CC 2.6.1.1.1. |
| 2 | 23, 31, 37, 57 | contradiction | 2.4.1.1 says `key:revocation:v1` binds `revoked_key_id (string or null)`, `reason (string or null)`, and `scrub_timestamp`, contradicting 2.6.1.1.1 (no explicit JSON `null` on optional members) and 2.6.1.7 (`scrub_timestamp` is outside signed bytes). | Align 2.4.1.1's `key:revocation:v1` member list with the 2.6.1.7 envelope contract (omit optional fields when unset; keep `scrub_timestamp` beside the row). |
| 3 | 27–29, 37–40 | contradiction | 2.4.2 and 2.6.1.1 show `attestation_envelope` without the required `row` mirror object and show `null` as a valid wire value for optional fields in 2.4.2, contradicting 2.6.1.1.1 and 2.6.1.7. | Update the JSON examples in 2.4.2 and 2.6.1.1 to match the 2.6.1.7 schema and remove `\| null` from 2.4.2's optional field comments. |
| 4 | 86–88, 90 | contradiction | 5.3.3.2 (p. 86) and 5.3.3.5 E2 (p. 90) forbid relays/SFUs for multicast ("pull-only ContentFetch... no selective-forwarding relay role"), while 5.3.3.2.1–5.3.3.2.3 (pp. 86–88) assume an SFU/relay dropping chunks by clear `codec_id`/`ChunkLayer`. | Clarify in 5.3.3.2.1–5.3.3.2.4 whether chunk-dropping is performed by the sender (as in 5.3.3.2.4) or a relay, and remove `" / SFU at scale"` on p. 87 if E2 is strictly pull-only. |
| 5 | 42, 49 | duplicate | `halt_fuse_secs` is listed twice in the 2.6.1.7 signed-object table: once as `signed:envelope` (p. 42) and once as `signed:envelope-extra` (p. 49). | Remove the duplicate `halt_fuse_secs` entry from the underlying `signed_object` data file so it appears in only one placement category. |
| 6 | 99–100, 102 | duplicate | The `symbol_key` derivation and `symbol_envelope` framing in 5.4.2 (pp. 99–100) are duplicated in 5.4.3 (p. 102). | Replace the repeated code block and KDF rules in 5.4.3 (p. 102) with a cross-reference to 5.4.2. |
| 7 | 72–74 | editorializing | Section 5.2 repeatedly cites `ciris.ai/cewp` marketing copy and an unsourced `~65%` scaling-model figure inside normative substrate rules. | Rewrite the opening of 5.2 and the "Locality dividend" paragraph to state the rule directly without citing `ciris.ai/cewp` or the unbacked 65% figure. |
| 8 | 5, 15, 29, 83, 85, 92, 107 | stale | Leftover design history, code pointers, and comparative claims (`"S4 default"`, `"the open question"`, `"thirteenth path... most product-complete"`, `"CHECK-arm migration"`, `"Leviculum"`, `"Signal’s webpsan"`). | Strip historical/code/comparative phrasing in a mechanical copy-edit pass. |

## Rendering
- **p. 25:** Code span in prose overflows the right margin and is clipped mid-word: `scope: ["personhood_consti`.
- **p. 29:** Two JSON code lines in 2.6.1.1 wrap mid-token (`"licensure:CA_medical_board` wraps `","score":0.8}` onto the next line with an awkward indent).
- **pp. 32–33:** In the 2.6.1.2 table, long JSON literals in the rightmost column (`"subject_sha256_ed25519_raw":"<64 lowercase hex>"` on p. 32; `"recovery_commitments":{"<holder_key_id>":"<64 lowercase hex>"}` and `"witnesses":[<SignedKeyRecord>, ...]` on p. 33) overflow their column width.
- **p. 69:** The CamelCase identifier `X25519MlKem768Aes256GcmHkdfSha256` is broken across lines without a hyphen (`X25519MlKe` / `m768Aes256GcmHkdfSha256`).
- **p. 70:** In the first table of 5.1, `federation_stream_chunks(stream_id,` in the "Where it lives" column overflows into the adjacent "Supersession" column (`Same rotation_chain`).
- **pp. 71, 73, 75, 93:** Long lines inside verbatim/code blocks wrap mid-statement with arbitrary indentation (e.g., `DEK(stream_id, epoch) = ...` on p. 71; `# current occurrence's encryption_pubkeys (CC` / `3.3.6.1)` on p. 73; `"prior_head_digest_sha256_hex"` on p. 75; `"serve_transport_destinations"` and `"attestations"` on p. 93).

## Effort estimate
About 4–6 hours of editing: 3 hours of mechanical cleanup (fixing the `<base64-url>` strings, deduplicating `halt_fuse_secs` and 5.4.2/5.4.3, updating 2.4.2/2.6.1.1 examples, and stripping stale/marketing prose and line-overflows) plus 1–2 hours requiring the steward's ruling on the `key:revocation:v1` member placement (p. 23 vs. 2.6.1.7) and the role of relay chunk-dropping vs. E2 pull-only multicast (pp. 86–90).

<!-- model google/gemini-4-argon; 110 pages; prompt_tokens 90627; completion_tokens 4475; 64s -->
