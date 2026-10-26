# The Wire (ciris_constitution-1.0-rc12-wire.pdf, 109 pages)

**Care score:** 4
**One-line verdict:** A second producer cannot pick one signing input or one record-id derivation from this volume until several page-to-page contradictions are ruled; large stretches of the grammar are usable only after that.

## Strengths
- Omit-vs-materialize, relay preservation, and the three JCS gaps JCS does not pin are stated as MUSTs, with a worked non-malicious failure (pp. 28–30, 35).
- The signed-object refusal door is a closed token set (p. 36), and the seven-member row mirror is enumerated (pp. 37–38).
- Canonical-hash wire form, preimage, reject vectors, and the no-repair rule (P1–P3) are specified tightly enough to implement (pp. 14–17).
- The adversary table separates “addressed” from “not addressed” instead of implying a single privacy property (pp. 3–4).
- Section 2.6.9.1 states that conformance is the RFC 2119 surface and that philosophy is not binding (p. 67).

## Weaknesses
- The CC 2.1 table that “consolidates” every envelope field (p. 6) has no `cohort_scope` row (pp. 6–12), while p. 17 lists `cohort_scope` as one of “exactly those in the CC 2.1 table,” and p. 38 makes it REQUIRED in the signed mirror with “no wire default.”
- The p. 32 catalog says `community_id` admission “rejects if `cohort_scope == community`” and omits `affiliations`; pp. 7 and 47 require the field iff scope is `community` or `affiliations`.
- `subject_key_ids: null or []` is “status-quo” (p. 18) while an explicit JSON null on an optional member “is refused” (p. 29). The mirror always carries an array, possibly empty (p. 38); the beside-column is absent when empty (p. 53). Three shapes for one meaning.
- “The canonical form is the array” and “a bare token is admitted as the one-element array” while “admission normalises nothing in the signed bytes” (p. 40, repeated p. 60). Both spellings remain valid signed bytes (p. 31). “Canonical” is not one byte string.
- Normative pseudocode for structural invisibility covers only `cohort_scope in {self, family}` (p. 71). Prose says CC 5.2 “forbids any holding claim leaving a bounded cohort, unconditionally” (p. 33) and extends the audience rule to `community | affiliations` (p. 72).
- Section 2.6 is titled “Foreword” and sits after the grammar it introduces (p. 27). Canonicalization, the 1 MiB cap, and the signing rules are subsections of that heading.
- Rule 0 says rules 1–4 “below do not reach it” (p. 23); those rules are on p. 22.
- Consent revocation “Default window: 24 hours (operator-tunable)” and, in the same section, “the 24-hour SLA” (p. 76).
- Freshness is specified on `signed_at` (p. 64). Attestation rows sign `asserted_at` / `scrub_timestamp` (pp. 39, 56). `signed_at` is not an attestation envelope member. STH cosign skew is against the STH’s `signed_at` (p. 64); lineage-head cosign skew is against the Registry clock (p. 74).
- Receipt `epoch` and `K` are `u64 LE` (p. 91). Stream nonce `epoch_be8` is big-endian (pp. 70, 83). The text warns that a BE/LE mix on the nonce is a silent whole-stream failure (p. 83) and does not point that warning at the receipt.
- Reassembly needs “≥ K valid symbols” (p. 102). K is “the stream’s, not substrate constants” (p. 101) and is not in the symbol envelope (pp. 99–100).
- p. 103 commits cover leaves with `HMAC-SHA3(...)` and does not pin SHA3-256 vs SHA3-512, unlike `HMAC-SHA3-256` on p. 98.
- Most named refusal tokens in the body (`attestation_type_unregistered`, `asserted_at_stale`, `federation_malformed_row`, `trust_root_head_stale`, and the census tokens) are not in the HTTP error table that “all error responses MUST conform to” (pp. 96–97). Only `federation_envelope_too_large` is mapped.
- `GET /v1/rotation-history` is one sentence with no schema (p. 95). Section 5.3.5 sends the implementer to an OpenAPI document “alongside this one” (p. 95) for the endpoints this volume says they build from (p. 1).
- Normative sections carry rationale, deployment status, and comparison. Examples: “the way MLS PCS provides” (p. 2); “the shipped roots run with witnessed mode off until it is turned on” (p. 3); “the surveillance backdoor this framework refuses” and “What CEG adds beyond systems that ship default privacy” (p. 5); “requires the founder’s explicit ratification” (p. 19); “mechanized in coherence-ratchet” (p. 4); “CEWP crux” (p. 80) and “CEWP substrate” (p. 103), an undefined leftover name; “Stewarded by Eric Moore” (p. 1).
- Bandwidth figures are not derivable from stated inputs: “~30%/hr”, “≈ 83 epochs/s”, “~3.1 Tbps”, “~2 Tbps content fan-out”, “~18.7 Gbps” (p. 69). “ML-DSA-65 sign ~330 µs” (p. 80) has no source. Unverifiable from here, not treated as invented.
- H3 resolution 7 is “~5 km2 edge-length” (p. 63). Square kilometres are area, not edge length. The same page’s “~5 km²” community example treats the figure as area (p. 64).

## Opportunities
- Add the missing `cohort_scope` row to the CC 2.1 table and delete or correct every “CC 2.1” cite in the signed-object tables for members that table does not define (`for_key_id`, `period`, `return_token`, and the rest of pp. 42–45).
- Strike `additional_scrubs` from the omit-vs-materialize catalog (p. 32) or mark the column “not canonical bytes,” matching pp. 9 and 54.
- Pick one `K_record_id` / `K_symbol` derivation, delete the other two labels, and make p. 105’s “CC 5.4.1” parenthetical match the text it cites.
- Replace `<base64-url>` in the cosign examples (pp. 73–74) with the RFC 4648 §4 spelling already required (p. 30), or change the pin if URL-safe is the intent. One ruling.
- In the p. 32 catalog, reject missing `community_id` for `affiliations` as well as `community`.
- Split the p. 90 E1 paragraph back into numbered MUSTs (seal, route-fetch, who may relay, what is not a fallback) so each obligation has one scope.
- Move “shipped roots… witnessed mode off” (pp. 3, 93) and the child-safety / opt-in essay (p. 5) out of this volume’s normative pages, leaving the byte rule and a pointer. That matches p. 1’s own split: bytes here, whether a MUST has shipped in the register, reasons in the charter.

## Threats
- Page 1 promises “One envelope, one signing input, one signature construction.” Witness STH cosign signs a labeled `sha256(...)` preimage (p. 73). Page 88 also requires “canonical bytes per CC 2.6.1 JCS for the envelope-bearing wrapper.” A delivery receipt signs a length-prefixed image, not JCS (p. 91). A key-plane revocation binds explicit JSON nulls inside `revocation_envelope` (p. 22) while the attestation rule refuses null (p. 29). A hostile implementer can claim conformance to either construction.
- `K_record_id` is bare `HKDF-SHA256-Expand` over the raw exporter secret with info `"ciris-edge/scope-privacy/record-id/v1"`, and “MUST NOT route this label through RFC 9420 `MLS_Exporter()`” (p. 97). Page 105 says `S_record` (`MLS-Exporter("ciris-scope-record-v1")`) “feeds `K_record_id` and `K_symbol`, CC 5.4.1.” CC 5.4.1 does not contain that label. Page 99 says both “HKDF-SHA256-Expand over the group’s raw `exporter_secret`” and “derive `K_symbol` from the MLS exporter” with label `ciris-edge/scope-privacy/symbol/v1`. Those are the two operations p. 97 says must not be confused. Byte identity of `record_id` (p. 97) is not implementable as written.
- “Rekey conforms to MLS TreeKEM (RFC 9420, normative)” (p. 70) and the references row says the rekey “conforms to MLS TreeKEM” (p. 61). The same subsection: “the flat per-member cascade (O(N)…)” and “The substrate MUST select per deployment” between multicast TreeKEM and flat unicast (p. 70). One of those MUSTs is false.
- “community content is sealed” (p. 5) against “the only plaintext bodies are those of authorized infrastructure communities and public rooms” (p. 72). A public room is a community (p. 11, `community:listing:v1`). A regulator can quote either sentence.
- `additional_scrubs` “travels beside the signed object, never inside it, since a cosignature cannot be inside the bytes it signs” (p. 9; also pp. 36, 54). The canonical-bytes catalog’s “Canonical when explicit” cell is `"additional_scrubs":[{...}]` (p. 32), i.e. inside the JCS object. Following the catalog breaks every cosigned signature; following p. 9 makes the catalog a trap.
- “RFC 4648 §4 STANDARD alphabet, WITH padding” (p. 30) against request bodies typed `"<base64-url>"` for the same signature fields (pp. 73–74). The spec itself says a URL-safe alphabet “produces different signed bytes and a silently non-verifying signature” (p. 30).
- Normative crypto depends on unversioned drafts (`draft-connolly-cfrg-xwing-kem`, `draft-ietf-hpke-pq`, `draft-irtf-cfrg-xchacha`, pp. 62, 102). Whether those drafts still say what this text claims is unverifiable from here.
- The email conformance row’s abbreviated wire form is `04481a02...98d0a263f` (p. 16). The hex printed beside it ends in `8d0a263f`, not `98d0a263f`. Copying the wire-form column mints a wrong vector.
- Page 1 says this volume does not state “whether a given MUST has shipped, which is the register’s.” Pages 3 and 93 state that the shipped roots run with witnessed mode off and give the charter values “when witnessed mode is turned on.” That is a snapshot a later deploy will falsify inside the adversary model.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 97, 99, 105 | contradiction | `K_record_id` / `K_symbol`: bare HKDF-Expand + `"ciris-edge/scope-privacy/record-id/v1"` and “MUST NOT” use `MLS_Exporter()` (p. 97); same page 99 also derives `K_symbol` via the MLS exporter and label `ciris-edge/scope-privacy/symbol/v1`; p. 105 feeds both keys from `MLS-Exporter("ciris-scope-record-v1")` and cites 5.4.1, which has neither label. | One derivation, one label, delete the other two; fix the 5.4.1 cross-cite. |
| 2 | 9, 32, 54 | contradiction | Cosignatures “never inside” the signed object (p. 9) but the canonical-when-explicit catalog emits `"additional_scrubs":[...]` as envelope bytes (p. 32). | Remove that catalog row from the JCS table; point at the beside-row table (p. 54). |
| 3 | 61, 70 | contradiction | Rekey “conforms to MLS TreeKEM” and the substrate “MUST select” flat unicast cascade vs TreeKEM. | State which construction is the wire conformance target; demote the other to a non-wire deployment note, or drop “conforms to TreeKEM” if the flat path remains conformant. |
| 4 | 30, 73 | contradiction | Standard padded base64 is mandatory; cosign examples say `base64-url`. | One alphabet in the pin and in the examples. |
| 5 | 5, 72 | contradiction | “community content is sealed” vs public-room (and infrastructure-community) bodies left plaintext. | Name the exception on p. 5 in the same words as p. 72, or delete one claim. |
| 6 | 17, 50 | contradiction | `subject_kind` “is NOT an envelope-level field” and “lives inside the Contribution payload” (p. 17); p. 50 puts `subject_kind` and “the per-family payloads of CC 3.3” in the signed envelope. | One sentence: payload member inside `attestation_envelope`, or a separate object. Strike the other. |
| 7 | 6–12, 17, 38 | unclear rule | Visibility’s field, `cohort_scope`, is absent from the table that claims to list every envelope field, and is REQUIRED with no wire default in the mirror. | Add the row (closed set of seven, no default) to the CC 2.1 table. |
| 8 | 73, 88, 91 | unclear rule | STH witness signs `sha256` of a labeled line image (p. 73); p. 88 also requires JCS “for the envelope-bearing wrapper.” Receipt signing bytes are a third construction (p. 91). Page 1’s “one signature construction” does not say these are out of scope. | For each object, one preimage, and a sentence on p. 1 that Part 5 framing objects are not that preimage. |

## Rendering
- p. 24: normative example clipped at `"personhood_consti` with no continuation before “Reuses the existing structural primitive”.
- p. 16: hex and wire-form columns broken across lines; email wire-form abbreviation `...98d0a263f` does not match the hex ending `8d0a263f` in the same row. Other wire forms use `...` so the column is not copyable.
- p. 14: the `canonical:sha256:ff7c...` example is line-broken inside the hex.
- p. 28: illustration JSON is line-broken inside the `dimension` string.
- pp. 3–4: adversary-table cells hyphenate mid-word (`ob-server`, `re-ceiver`, `sub-strate`, `pro-ducer`).
- p. 42: quorum formula rendered as `floor(|witnesses|/2)+1` where p. 10 uses `⌊|witnesses|/2⌋ + 1`.
- p. 68: vocab token printed as `X25519MlKe m768Aes256GcmHkdfSha256` (space inside the identifier). Confirm this is not only an extraction wrap; if the PDF breaks the token, it will be copied wrong.
- p. 69: the epoch-axis table cell runs together as `federation_stream_chunks(stream_id,` immediately followed by `Same rotation_chain` from the next column.
- pp. 89–90: E1’s normative rules are one run-on “Behavior” paragraph (route fetch, seal, LXMF exclusion, relay key), not a list.
- p. 59: table break leaves a page with a single member row.
- No literal `**` or stray `\`, and none of the banned words (humane, dignified, graceful, farewell, “last word”) seen.

## Effort estimate
About 16–24 hours: a few hours of mechanical table and cross-cite repair, and the rest waiting on steward rulings (which key derivation, which signature preimage, which base64, whether public-room bodies are plaintext, where `subject_kind` sits) before those sentences can be edited without inventing a third rule.

<!-- model x-ai/grok-4.7; 109 pages; prompt_tokens 86988; completion_tokens 26224; 301s -->
