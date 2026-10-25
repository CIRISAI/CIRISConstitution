# The Threat Model (ciris_constitution-1.0-rc11-threats.pdf, 48 pages)

**Care score:** 5  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** Conflicting cryptographic instructions, bootstrap rules and security assurances require a reconciliation pass before this can serve as an implementation contract.

## Strengths
- The adversary table distinguishes mitigations from residual exposure, including single-signer roots and captured trusted attesters (pp. 3–5).
- Bootstrap authenticity is explicitly distinguished from internal consistency: an unanchored consumer “MUST NOT promote anything” to a trust root (p. 31).
- The shaping discussion identifies its results as model outputs, “not measurements from a live mesh,” and the onion profile discloses small anonymity sets and rendezvous packet counting (pp. 40, 47).

## Weaknesses
- The key schedule contradicts itself: record keys derive from the “raw group exporter_secret,” expressly not `MLS_Exporter()`, on p. 36; p. 44 instead names a separate `S_record` exporter feeding those keys. Implementations following the two passages will derive different bytes.
- At-rest encryption is conditional in executable-looking instructions—“WHEN self/family at-rest encryption is enabled”—but the same page says “it is always on” and “no operator switch turns that off” (p. 11).
- The DEK description first says the group exporter secret “is the epoch DEK,” then defines a per-stream HKDF derivation and says the exporter secret “is never wrapped.” The later explanation does not remove the earlier incompatible instruction (p. 9).
- The bootstrap example specifies `"version": 1` and omits `serve_transport_destinations`, while the normative discussion specifies version 4 and includes that member in the authorization preimage (pp. 31–33).
- The introduction promises the concerns ledger and interoperability profiles of Part 8, but this volume ends at §5.4.6 without either (pp. 1, 48).
- Unsourced numerical claims include “realistic audience churn (~30%/hr)” and bandwidth estimates (p. 8), “~65% of activity stays local” (p. 12), signing at “~330 µs” (p. 20), and “~20–40% MDC compression overhead” (p. 25). The model latency results have a narrative description but no identifiable run or register row here (p. 40). The ERC-8004 figures do name a study; that citation is unverifiable from here, not evidence of fabrication (pp. 3–4).

## Opportunities
- Reconcile each duplicated security rule into one authoritative formulation, then make the surrounding prose refer to it. The immediate targets are key derivation, encryption enablement, bootstrap exceptions and revocation timing (pp. 9, 11, 15–16, 29, 33, 36, 44).
- Update the bootstrap JSON and chunk-layout examples to match their normative requirements; this would remove avoidable implementation guesswork without changing policy (pp. 26–27, 31–33).
- Remove release-history language such as “is retired,” “V1 lock,” “final-genesis assembler,” and the v3/v4 deployment sequence; retain only the applicable rules (pp. 27, 33).
- Replace marketing and comparisons with bounded statements. Examples include “What CEG adds beyond systems…” and “recovers the…child-safety catches” (p. 5), the promotional quotation from `ciris.ai/cewp` (p. 10), “most product-complete” (p. 23), “breadth confirmation” (p. 24), and “the classical darknet bootstrap problem dissolves” (p. 48). The MLS comparison on p. 2 also violates the stated no-comparison rule.
- Move implementation pointers and development commentary out of the Parts: `formal/` (p. 1), “mechanized in coherence-ratchet” (p. 4), repeated CIRISVerify vector-publication pointers (pp. 9, 27, 37, 44), and the “CHECK-arm migration” discussion (p. 31). Identify the existing register evidence for empirical claims instead.

## Threats
- A security reviewer can challenge “producer cannot show different chunk-K to different subscribers” (p. 27): roots appear every K chunks or T seconds, but witnesses cosign only “per-epoch” (p. 28), and time-based rotation is optional (p. 8). The text does not establish its claimed short equivocation bound.
- A lawyer could read the revocation section as promising propagation protection it does not supply. It allows unsigned transit for a default 24 hours and an “overdue-flagged” terminal state (p. 15), then says the shared flag closes the window while federation peers continue propagating data (p. 16). Detection is not delivery.
- An implementer could produce incompatible cryptography while following explicit normative instructions on both pp. 36 and 44.
- The delivery-receipt checks establish a signed statement referencing a published root, not receipt of chunk bytes. Nevertheless, the text says the receipt “proves the subscriber received bytes” (p. 30).
- Privacy assurances exceed their qualifications: “The wire learns nothing…at any setting” (p. 40) conflicts with the expressly observable setup, link existence and shaping status (p. 39). The concluding claim that an election’s occurrence is invisible also outruns the admitted group-existence inference from traffic analysis (pp. 46, 48).

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 36, 38, 44 | contradiction | Raw `exporter_secret` derivation, with an express ban on `MLS_Exporter()`, conflicts with the separate `S_record` exporter said to feed `K_record_id` and `K_symbol`. | Have the steward select the intended existing schedule; align formulas, descriptions and vectors. |
| 2 | 11 | contradiction | “WHEN…encryption is enabled” and “when…enabled” conflict with “always on” and “no operator switch.” | Remove the conditional deployment path if the unconditional mandate governs. |
| 3 | 29, 33 | contradiction | P. 29 permits an unsealed route request and signed route/key response before the handshake. P. 33 says the bundle is the “only seed” before a sealed link, except pairing. P. 29 also calls both the route request and KEX the first frame. | State one bootstrap sequence and its exhaustive exceptions consistently. |
| 4 | 8, 27–28 | overclaim | Anti-equivocation is stated categorically, but witness cadence is per epoch rather than per signed-root interval; epoch duration need not be bounded by T. | State the actual witnessed checkpoint guarantee and reconcile the existing cadence rules. |
| 5 | 15–16 | unclear rule | The window is operator-tunable, then repeatedly fixed at 24 hours; overdue flagging is called enforcement and a conformant terminal state despite the promotion obligation. | Specify the controlling deadline and distinguish breach reporting from successful promotion. |
| 6 | 26–27 | unclear rule | The chunk layout carries neither `last_flag` nor `link_seq`, although the inner and outer nonce derivations require them. No recovery rule is given here. | Identify where each input is carried or obtained in the existing framing, including reconnect and stored-chunk paths. |
| 7 | 7 | contradiction | The hyphenated algorithm alias “MUST be rejected,” but transitional acceptance “MAY” be enabled by a flag. | State whether the transition is an explicit conformance exception or remove it; eliminate the unspecified “next MINOR” sunset. |
| 8 | 30 | overclaim | Signature and published-root checks are described as proof of receiving chunk bytes; even inclusion checking is only recommended. | Describe the result as a validated subscriber acknowledgement, not cryptographic proof of byte delivery. |

## Rendering
- The p. 8 addressing-axis table visibly collides across columns: `federation_stream_chunks(stream_id, seq)` runs into the supersession entry beginning “Same rotation_chain.”
- The heading “5.3.3.8 What the streaming surface documents” is stranded at the bottom of p. 30; its entire body starts on p. 31.
- Long section headings break words awkwardly: “subjec-t-set” across lines on p. 17 and “hy-brid-pending” on p. 18.
- The supplied page text does not permit reliable verification of glyph loss, clipping or actual font size; no additional visual defects are asserted.

## Effort estimate
Approximately 24–36 hours of editing and conformance-example checking, with steward rulings needed on the conflicting security rules; layout, stale references and promotional prose are mechanical cleanup.

<!-- model openai/gpt-6-astra-pro; 48 pages; prompt_tokens 131041; completion_tokens 5225; 61s -->
