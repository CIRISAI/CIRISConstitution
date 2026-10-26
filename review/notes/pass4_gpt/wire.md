# The Wire (ciris_constitution-1.0-rc11-wire.pdf, 110 pages)

**Care score:** 5  (1 = ship as is, 5 = needs a rewrite pass before 1.0)  
**One-line verdict:** The implementer-facing contract needs a reconciliation pass: competing key derivations, incompatible encoding instructions, incomplete chunk framing and retained migration prose undermine its promise of independent interoperability.

## Strengths
- The signed-object tables distinguish signed members, replicated columns, signatures and local state, and name admission failures (pp. 37–60).
- The text supplies testable requirements for envelope size, malformed inputs, content verification and bootstrap anchoring (pp. 34–37, 61, 82, 93–94).

## Weaknesses
- **The signing examples do not satisfy the later signing contract.** The example labelled “Wire shape” lacks the mandatory `row` mirror and `asserted_at`, and offers explicit null values (pp. 27–28); the later rules require those members and refuse optional-member nulls (pp. 31, 37–40). The canonicalization examples likewise put signer identifiers directly in the envelope (p. 29).
- **Payload placement remains contradictory.** `subject_kind` “is NOT an envelope-level field” (pp. 18–19), but the signed-object table says “including subject_kind and the per-family payloads … rides the envelope” (p. 51). An implementer needs one explicit nesting rule.
- **The central privacy implementation still contains an obsolete conditional.** “WHEN self/family at-rest encryption is enabled for the deployment” conflicts with “it is always on … no operator switch turns that off,” on the same page (p. 73).
- **A key-format recommendation changes a normative format without specifying interoperability.** The fingerprint is “the first 10 base32 characters” (p. 67), but deployments “SHOULD raise the fingerprint length” to 16 characters (p. 68). The decoder and registration rules do not explain which lengths they accept.
- **H3 precision is misstated.** “~5 km² edge-length” confuses area with length; the same page alternately identifies the high nibble as mode value “1” and “8” (p. 64). The stronger assurance that a malformed client “cannot publish a precise location” also exceeds a gate that only limits the declared H3 resolution.
- **History, attribution and implementation status remain inside the Parts.** Examples include “the shipped roots run with witnessed mode off” (p. 3), “mechanized in coherence-ratchet … not yet measured” (p. 4), “This answers the open question” (p. 15), “the name cosignatures[] is retired” (pp. 10, 61), the reference implementation’s vector-production history (p. 61), the “final-genesis assembler” rollout account (p. 95), and model-run history (p. 102).
- **Comparisons and promotional passages violate the stated house rules.** These include the MLS comparison (p. 2), ERC-8004 comparison table (pp. 3–4), “What CEG adds beyond systems that ship default privacy” (p. 5), the attributed website promise “the wire format can’t carry them” (p. 72), “the most product-complete” and “breadth confirmation” passages (pp. 85–86), and “the classical darknet bootstrap problem dissolves” (p. 110).
- **Several quantitative claims lack a visible supporting result or register row.** Examples are “thirteen distinct content cases” (p. 20), “realistic audience churn (~30%/hr)” and the resulting bandwidth estimates (p. 70), “~65% of activity stays local” (p. 74), ML-DSA signing at “~330 µs” (p. 82), “~20–40% MDC compression overhead” (p. 87), and detailed scheduler latency results (p. 102). The ERC-8004 figures do name a publication; that citation is **unverifiable from here**, not evidence of fabrication (pp. 3–4).

## Opportunities
- Reconcile each byte-level rule against the signed-object tables, then replace the earlier examples with complete conforming examples. This would remove contradictory teaching material without changing policy (pp. 27–40, 51).
- State each key derivation and binary layout once, with other sections referring to that definition. In particular, settle the exporter input and specify where receivers obtain every nonce input (pp. 84–89, 98, 106).
- Remove conditional and transitional wording that contradicts unconditional requirements; retain any intended exception explicitly in the governing rule (pp. 69, 73).
- Move implementation status, rollout accounts, model results and project comparisons out of the Parts. Keep normative constants here, with the supporting register references where required (pp. 3–5, 61, 70–74, 82–87, 95, 102, 109–110).
- Reflow the overflowing examples and tables, and eliminate the nearly empty continuation page. This would recover readability without substantive revision (pp. 25, 32–33, 60, 70).

## Threats
- **Independent implementations can derive different secrets while following explicit instructions.** Page 98 requires raw `exporter_secret` and forbids `MLS_Exporter()` for `K_record_id`; page 106 introduces an MLS exporter output as the source feeding that key. This is a direct interoperability blocker, not explanatory imprecision.
- **The purported byte-complete stream specification leaves decryption inputs unresolved.** The nonce uses `stream_id_utf8` and `last_flag` (p. 84), while the header carries a raw 32-byte stream identifier and no final-chunk flag (p. 88). The outer nonce additionally requires `link_seq`, whose carriage is not specified in that layout (p. 89).
- **The privacy claims invite an avoidable hostile reading.** Clear `record_id` and `symbol_index` fields “reveal nothing” (p. 100), although repeated tags and indices disclose equality and ordering. “The wire learns nothing … at any setting” (p. 102) is broader than the observable-link limits already stated on p. 101. The concluding claim that structural invisibility “hides the election” (p. 110) needs the same observer qualification as the traffic-analysis concession on p. 108.
- **The consent discussion claims more closure than its enforcement establishes.** “There is no window” in which revocation remains local while peers continue propagating data (p. 78) sits beside a default 24-hour promotion window and an “overdue-flagged” terminal state (p. 77). A flag documents failure; it does not itself establish that peers received the revocation.
- **Standards-conformance claims need narrower wording or complete profiles.** The text calls sealing conformant to SFrame while prescribing its own binding and nonce construction (p. 84), and calls the Welcome wrap RFC 9180 HPKE while replacing the suite identifier used in labelled derivation with a custom literal (pp. 103–104). A cryptographic reviewer will ask exactly which standard requirements remain unchanged.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 98, 106 | contradiction | `K_record_id` uses “raw group exporter_secret” and “MUST NOT” use `MLS_Exporter()`, but `S_record`, an exporter output, later “feeds K_record_id and K_symbol.” | Steward selects the intended derivation; make both sections and their known-answer vectors describe that exact construction. |
| 2 | 27–31, 37–40 | contradiction | Published envelope examples omit mandatory signed members and advertise null values that admission must reject. | Replace with complete examples using the required mirror and instants; show omission rather than null. |
| 3 | 84, 88–89 | unclear rule | Nonce derivation needs a UTF-8 stream identifier, final-chunk flag and link sequence; the published layout does not establish all of those inputs. | Specify the existing intended representation and carriage of every nonce input, then give one complete encode/decode vector. |
| 4 | 31, 74–75 | contradiction | “Every field documented as base64 MUST use” the standard padded alphabet; cosign requests specify `"<base64-url>"` for signatures and proof paths. | Choose the intended encoding and align endpoint examples, validators and vectors. |
| 5 | 73 | contradiction | Encryption is conditional in pseudocode and surrounding prose, but also “always on” with no operator switch. | Remove the obsolete conditional if the unconditional rule governs; otherwise obtain an explicit steward ruling. |
| 6 | 69 | contradiction | Consumers “MUST accept only this byte string” and “MUST” reject aliases, but a deployment flag “MAY” accept the hyphenated alias. | Resolve whether alias acceptance is conformant; remove the migration account or state the exception unambiguously. |
| 7 | 23, 78 | stale | Revocation ordering must key on the raw-key digest (p. 23), but the merge table still specifies ordering “on revoked_key_id” (p. 78). | Update the merge definition to the authoritative subject identifier and check all associated examples. |
| 8 | 91, 93–95 | stale | Bundle example says `"version": 1`; the operative section specifies version 4 and an additional authorized member. Page 95 also calls pairing the “one other way” to obtain a pre-seal pair, despite the pre-seal route fetch on p. 91. | Update the complete bundle example and reconcile the bootstrap-path inventory with E1. |

## Rendering
- Page 25: the authority-source example ends mid-token at `["personhood_consti`, losing the rest of the scope value and sentence.
- Page 32: the explicit `subject_sha256_ed25519_raw` example overruns its table column and breaks the quoted value across lines.
- Page 33: the `recovery_commitments` example similarly overruns the final column.
- Page 70: the `federation_stream_chunks(stream_id, seq)` entry runs into the supersession column; “Same rotation_chain” collides with it.
- Page 60: a single continuation-table row occupies an otherwise largely empty page.
- These findings use the supplied page-by-page rendering text; font size, page-edge clipping and missing glyphs cannot be independently checked without the PDF image.

## Effort estimate
Approximately 32–48 hours for technical reconciliation, example regeneration and layout correction; the cryptographic derivation, compatibility and bootstrap conflicts need steward rulings before the remaining work becomes mechanical.

<!-- model openai/gpt-6-astra-pro; 110 pages; prompt_tokens 262521; completion_tokens 7355; 109s -->
