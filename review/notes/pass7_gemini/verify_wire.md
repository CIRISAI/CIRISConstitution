# Gemini pass-7 Wire report: verification against rc12 source

Checked against branch rc12 at f7d2af2 (source) and volumes/ciris_constitution-1.0-rc12-wire.pdf (built 2026-10-26 20:44, after f7d2af2; 112 pages, so the page numbers in the report are the current build). P1 = constitution/part_1_foundation.md, P2 = constitution/part_2_the_grammar.md, P5 = constitution/part_5_transport_substrate.md. Prior = review/notes/pass6_grok/verify_wire.md (items by number), review/notes/volume_swot_rc12_pass6_grok_2026-10-26.md, and the pass-5 note review/notes/volume_swot_rc11_pass5_gemini_2026-10-25.md where a pass-7 item traces to it.

Report: review/notes/pass7_gemini/wire.md
Care score: 3 (Gemini's pass-5 score for this volume was also 3; Grok pass 6 gave 4)
Verdict paragraph (verbatim): "A battle-hardened, byte-exact protocol specification whose cryptographic and canonicalization surfaces are exceptionally clear, but which needs a targeted pass to resolve an E2E multicast contradiction, specify the inner onion-packet wire layout, and clean up a few rendering and house-rule glitches."

Dispositions: M = mechanical fix, R = needs the steward's (or an implementer's) ruling, P = pipeline/renderer, X = reject.

## Defect 1 (W2, Opp 2, Threat 1): onion packet has no byte layout, KDF label or AEAD suite while relaying is a conformance gate

(a) The Anonymous Tier paragraph in 5.4.6 fixes the packet only as "a layered packet of fixed length" with one KEM ciphertext per hop, and no offset table, frame size, KDF label or AEAD is given anywhere in the volume, while `seat_opted_out` / `seat_without_hop_key` are stated as conformance tokens.
(b) CONFIRMED as a fact of the text; the framing ("unimplementable mandatory requirement") misses that the tier is staged, not shipped.
(c) P5:872: "An onion packet is a layered packet of fixed length in which each hop's layer is encapsulated to that hop's X-Wing onion hop key ([CC 3.3.6.2]) and protected by a key derived from that encapsulation; each hop removes one layer and learns only the next hop. ... Because ML-KEM cannot be blinded, the header carries one KEM ciphertext per hop." P5:870: "a serve node MAY NOT: a seat carrying the marker is out of conformance as `seat_opted_out`, and a seat without a valid hop key as `seat_without_hop_key`." Register: CLM-onion-relay-mandatory, CLM-onion-hop-key, CLM-onion-route, CLM-onion-layer-deal are all `staged:CIRISConstitution#172` (constitution/claims.tsv:488–492); only CLM-onion-layer-model has evidence (the TLA/Lean deal model).
(d) Pass 6: not raised in the wire or threats verification. Pass 5: not raised. The rc10 ruling recorded the anonymous tier as PLANNED. Neither f0b6328 nor 81746c7 touched this paragraph. Not a regression.
(e) R. The house practice elsewhere (5.4.2's symbol AEAD: key derivation ships, the AEAD is a staged content path on CIRISEdge#651) is that the register, not the Part, says what has shipped; the cover says so ("whether a given MUST has shipped, which is the register's"). The steward decides whether the Part should say in one sentence that the packet's byte layout is pinned when #172 lands (no ticket link in a Part under the 1.0 prep rule), or whether the register row is enough. Gemini's "5.4.6.3–6" are not subsections; the tier is one bold paragraph with a numbered list inside 5.4.6 `announce-suppress`.

## Defect 2 (W1, Opp 1): 5.3.3.5 E2 "Multicast is pull-only ... no relay or fan-out tree" against 2.1 `delivery_mode: push`, 5.3.3.2's direct-link push row, and the 5.3.3.4 fan-out invariant

(a) E2 is stated unconditionally and denies any fan-out, while 2.1 defines a `push` delivery mode whose meaning is substrate fan-out per 5.3.3.4, 5.3.3.4 defines `fan_out(C) = entitled(C) ∩ reachable(now)` and a push-retry rule, and 5.3.3.2's profile table (which says it "extends CC 5.3.3.5") gives the small-group realtime profile as direct-link push.
(b) CONFIRMED (sentence-level). The reconciliation Gemini proposes is already the text's intent: pull-only applies to broadcast and large groups, and "fan-out tree" in E2 means a relay tree while "fan_out" in E3 and 5.3.3.4 means the target set. E2's first clause does not say so.
(c) P5:468: "| **E2 — pull-only** | Multicast is **pull-only**: producer seals chunks under the epoch DEK → emits holding claims at the stream's scope → subscribers pull via the existing `ContentFetch` path. There is no relay or fan-out tree. |". P2:72: "`push` = substrate fans out to the live-delivery set per [CC 5.3.3.4] `fan_out = entitled ∩ reachable`." P5:366: "| **Realtime small/medium group** (calls, huddles, ≤ ~50) | symmetric mesh | **direct Reticulum Links between participants** (low-latency push; no relay tree needed at small N) |". P5:460: "**Fan-out invariant: `fan_out(C) = entitled(C) ∩ reachable(now)`**." P5:464: "substrate does NOT keep retrying push".
(d) Pass 6: not raised (the only E2-area item was 26, E1 as a run-on cell). Pass 5: the adjacent relay/SFU contradiction (pass-5 wire defect 4, threats defect 4) → R87 "no relay under pull-only fan-out", landed 2efa68e; R87 settled the relay side and did not touch the push-mode side. The E2 sentence itself dates from the pass-4 landing (3334fae, 2026-10-25). Not a regression.
(e) M. Scope E2's first sentence: broadcast and large-group multicast is pull-only with no relay tree; the small-group realtime profile of 5.3.3.2 pushes on direct links; `fan_out` in E3 names the delivery set, never a relay topology.

## Defect 3 (Threat 2): 5.4.4 inviter signature is ML-DSA-65 alone while every other signature construction in the volume is bound-hybrid

(a) The Welcome inviter signs `encap_signing_bytes` with ML-DSA-65 only; 2.6.5 [hybrid-sig], 5.3.2.4.3.1, the 5.3.1 cosigns (P5:155, 187) and the 5.3.3.6 receipt are all Ed25519 + ML-DSA-65 bound, and 5.4.4 states no reason for the single primitive.
(b) CONFIRMED. The 5.3.2.4.3.1 mandate is written for federation-tier attestation admission gates, so it is not a literal contradiction with a transport-ceremony signature; but the volume gives no rule for why this one signature drops the classical half, and the stated rationale for hybrid (a future break of one primitive) applies to the inviter's authentication exactly.
(c) P5:797: "**Inviter signature.** The inviter MUST sign the encapsulation bytes with ML-DSA-65 over the following length-delimited encoding (no `algorithm` field):". P5:785: "it is provided out-of-band by an **ML-DSA-65 signature from the inviter** over the encapsulation bytes (below)." P2:802: "[hybrid-sig] | The **bound-hybrid signature**: Ed25519 ... and ML-DSA-65 ... both halves verified at every federation-tier admission gate and on the store path".
(d) Pass 5 raised it (threats defect 5) → **R89 (edge)**: "Edge says why; the text then either states the exception as a rule or the signature becomes hybrid." Pass 6 did not repeat it. R89 has no recorded answer; the edge-answers commit 81746c7 covers R103/R104 only and neither it nor f0b6328 touched 5.4.4 (0 lines in either diff). Not a regression; an open ruling two passes old. The rc8 book-state note (review/notes/book_state_rc8_2026-10-14.md:1028, 1096) also records that the signed bytes carry no domain label, group id, epoch or invitee key, which Gemini did not notice and which is the stronger version of the same finding.
(e) R (R89, edge). Chase the answer or rule it in-house: make it hybrid, or state the single-primitive exception as a rule with its reason.

## Defect 4 (Rendering p. 5): broken markdown link rendered literally in 1.13.3.4

(a) The sentence in 1.13.3.4 carries a mangled fragment `.4.3.4](part_4_composition_governance.md#4.4.3.4))` after the 4.4.3.2.1 citation; the PDF prints it verbatim (confirmed on the rendered page).
(b) CONFIRMED.
(c) P1:248: "...the one exception being authorized infrastructure communities and public rooms, whose bodies are plaintext and whose holding claims sit at federation scope ([CC 4.4.3.2.1](part_4_composition_governance.md#4.4.3.2.1)).4.3.4](part_4_composition_governance.md#4.4.3.4)) — where, for `self`, ..."
(d) Pass 6: not raised as such; pass-6 item 17 asked for exactly this sentence to be rewritten ("name the exception in 1.13.3.4 in 5.2's words") and M16 (f0b6328) landed that rewrite. The mangled fragment first appears at 2efa68e (the pass-5 landing; absent at 2efa68e^), and f0b6328 rewrote the sentence around it and kept it. Not a regression by the strict test (M16 did not introduce it), but M16 edited this sentence under a claimed fix and left a visible defect in it. The same defect is reported in pass7_gemini/threats.md defect 2. tools/check_links.py did not catch it because the fragment is not a link.
(e) M. Replace the fragment with "([CC 4.4.3.2.1], [CC 4.4.3.4])" or drop the second citation.

## Defect 5 (Rendering p. 24): `scope: ["personhood_consti` clipped at the right margin

(a) The inline code span in 2.4.1.2 runs off the margin; confirmed on the rendered page.
(b) CONFIRMED.
(c) P2:317 (source intact): "`scope: ["personhood_constitutive_by_attestation"]`".
(d) Flagged in passes 3, 4, 5 and 6 (pass-6 item 33; SWOT line 162 "overfull inline-code spans still clip"). Not claimed fixed by M16. Not a regression.
(e) P (renderer: allow a break inside a long code span), or an M that shortens the example token.

## Defect 6 (Rendering p. 32): two cells of the 2.6.1.2 catalogue overflow the "Canonical when explicit" column

(a) `"subject_sha256_ed25519_raw":"<64 lowercase hex>"` and `"recovery_commitments":{"<holder_key_id>":"<64 lowercase hex>"}` run past the column; confirmed on the rendered page.
(b) CONFIRMED.
(c) P2:481 and P2:486 (source intact; the strings have no break opportunity).
(d) Pass-6 item 34 flagged the same class (hex and JSON wraps inside table cells, then pp. 14, 16, 28) without these two cells. Not a regression.
(e) P (break opportunities inside code in table cells), or M (shorten the two placeholders).

## Defect 7 (W3): `SignedKeyRecord.roles` as a `beside` set is not said to be sorted, so `bundle_fingerprint` over the JCS bundle could diverge

(a) The report says 2.6.1.7 does not state whether beside-placed set arrays are sorted at emission.
(b) FALSE. The rule paragraph under the key-record table states it for every set-kind member of that table regardless of placement, with a refusal token, and `roles` is in that table with Array = set.
(c) P2:739: "**Rules this table carries.** A set-kind array is sorted **and** unique, refused otherwise as `federation_set_semantics_unsorted` with the member named; a relay never re-sorts it, since re-sorting would move signed bytes." P2:734: "| `roles` | beside | `[* tstr]` | set | OPTIONAL | [] | ...". The rule has been in the text since b6c8935 (2026-10-18), before pass 6.
(d) Pass 6: not raised. Not a regression.
(e) X. (An optional half-sentence in 5.3.4 noting that `holders[]` carries admitted records, hence sorted sets, would close the reader's path; not required.)

## Defect 8 (W4): drafting-history phrasing in normative definitions

### 8a. 2.1 `listed`: "the new CC 5.3.3 streaming endpoint set"
(a) The row's last sentence calls the 5.3.3 endpoint set "new".
(b) CONFIRMED.
(c) P2:73: "Composes with [CC 4.4.3.2] Policy M community membership and the new [CC 5.3.3] streaming endpoint set."
(d) Not raised by pass 5 or 6 (the pass-5 residue checker has no pattern for "new"); pass-6 item 22 listed other history residue. Not a regression.
(e) M: drop "new".

### 8b. 2.3 intro: "The baseline envelope encoded producer authority alone; `subject_key_ids` adds the missing half"
(a) History-of-design phrasing in the 2.3 lead (Gemini places it in 2.3.5; the sentence is under the 2.3 heading, before 2.3.1).
(b) CONFIRMED.
(c) P2:107: "The baseline envelope encoded **producer authority** alone (`attesting_key_id`); `subject_key_ids` adds the missing half — **subject authority** —".
(d) Not raised before. Not a regression.
(e) M: "`attesting_key_id` carries producer authority; `subject_key_ids` carries subject authority."

### 8c. 2.4.1.1 rules table row 4: "(existing primitive, new admission path)"
(a) The row's meaning column carries a drafting note.
(b) CONFIRMED.
(c) P2:303: "| 4 | `issuer` holds valid `delegates_to → any of 1-3` | Delegated revocation (existing primitive, new admission path) |".
(d) Not raised before. Not a regression.
(e) M: "Delegated revocation".

## Defect 9 (W5): comparative claims naming external projects

### 9a. 1.13.3.1 "the way MLS PCS provides"
(a) The PCS bullet compares the stream's forward-only choice to MLS post-compromise security.
(b) CONFIRMED (as a prior-raised editorial item).
(c) P1:219: "but a *compromised current member's* key is not self-healed by a key-update the way MLS PCS provides."
(d) Pass-6 item 22 raised it (and passes 3–5 before), disposition "R for the editorial cuts"; no ruling recorded, M16 did not claim it. Not a regression.
(e) R (carried from pass 6). MLS is the volume's own key-agreement dependency (RFC 9420 is normative in 5.1), so the sentence is a comparison with a dependency, not a peer product; the steward may keep it.

### 9b–9e. Rust/Python `surrogatepass` (2.3.2.1), "(S2, Geohash)" (2.6.6.3), "iOS has no WebM / Opus playback" (5.3.2.6 table), "interoperability with Python RNS" and "a standard LXMF client" (5.3.3.5 E1)
(a) All five phrases are present in source: P2:149, P2:843, P5:309, P5:476, P5:485.
(b) MATTER-OF-TASTE. None is a peer-project comparison under the house rule as encoded (tools/check_stale_refs.py "comparisons" class: named peer projects and products; the run on rc12 reports 0 lines). Rust/Python illustrate why `utf8(id)` must be total; S2/Geohash sit in a "What the H3 rule does NOT do" scope note; the iOS cell is the rationale column of the codec-tier table; Python RNS and LXMF are the transport the Part is built on (Reticulum), named as interoperability constraints, not comparisons.
(d) Not raised before. Not a regression.
(e) X.

## Rendering p. 29: 2.6.1.1 code block wraps mid-token

(a) The two one-line JSON examples wrap at `"licensure:CA_medical_board\n ","score":0.8}`; confirmed on the rendered page.
(b) CONFIRMED.
(c) P2:425 and P2:428 (source intact, one line each).
(d) Pass-6 item 34 class (JSON wraps inside code). Not a regression.
(e) P (the renderer breaks long code lines without a continuation marker), or M (break the examples across lines in source, since they are marked "not canonical bytes").

## Rendering p. 71: 5.1 rotation-axis table, `federation_stream_chunks(stream_id,` collides with the next column

(a) The "Where it lives" cell overflows into "Supersession"; confirmed on the rendered page.
(b) CONFIRMED.
(c) P5:28 (source intact).
(d) Pass-6 item 37 (then p. 69) and SWOT line 162 ("the four-column table at part_5:28"); flagged since pass 3. Not a regression.
(e) P (row-block path for this table), or M (`federation_stream_chunks` on its own line in the cell).

## Rendering p. 72: 5.1 "Per-stream DEK under the group exporter" code block wraps mid-argument

(a) The first line of the HKDF block is longer than the code column and wraps to a second line with `length = 32),` under the opening; confirmed on the rendered page.
(b) CONFIRMED.
(c) P5:47: "DEK(stream_id, epoch) = HKDF-SHA256( ikm  = MLS-Exporter(label = \"ciris-stream-dek/v1\", context = \"\", length = 32)," (one 117-character source line).
(d) Not raised before; this block is in the text 81746c7 kept when it landed R103 ("the key mechanism by content class"), and the block itself predates it. Not a regression.
(e) M (break the `ikm` argument across two source lines); the renderer cannot do better with a line that long.

## Not defects, noted for the record

- The report's placement "2.3.5" for the baseline-envelope sentence is 2.3's lead (P2:107); "5.4.6.3–6" do not exist as numbered subsections.
- The strengths the report credits (2.6.1.1.1's three determinism rules, the 2.6.1.7 generated tables, the 2.6.1.3 contract-vs-intake bound, the inline vectors) are the surfaces pass 6 found contradictory (items 1, 3, 9, 10, 14, 15, 18); those landed in M16 and 81746c7 and Gemini reads them as clear.

## Summary

15 findings: 13 CONFIRMED, 1 FALSE (roles sorting, stated at P2:739), 1 MATTER-OF-TASTE (the four dependency mentions), 0 ALREADY-FIXED-IN-SOURCE, 0 REGRESSION. Dispositions: M 5 (E2 scoping; the p. 5 link; the three history phrases), R 3 (onion layout vs the staged tier; the Welcome inviter signature, open as R89 since pass 5 with no edge answer; "the way MLS PCS provides", carried from pass 6), P 5 (the five renderer items, four of them flagged since pass 3), X 2.
Top three: (1) R89, the ML-DSA-only Welcome signature, two passes old and unanswered, and the one finding with a security edge; (2) E2's unconditional "Multicast is pull-only ... no relay or fan-out tree" against 2.1's `push` mode, a two-clause scoping fix; (3) the mangled citation at P1:248 in the sentence M16 rewrote under pass-6 item 17. The volume reads better than at pass 6: Grok's 30 confirmed items were contradictions in the signing input, the record-id derivation, the receipt's byte order, the base64 alphabet and the 2.1 member set; Gemini finds none of those and names them as strengths. Its substantive list is three items, two of them already open rulings (R89; the staged onion tier) and one a wording scope, plus renderer residue every pass has flagged. The care score stayed at 3 because Gemini's scale rewards a closed implementable spec and the onion tier is written as normative text without its bytes.
