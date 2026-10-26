# The Reader's Policies (ciris_constitution-1.0-rc11-policies.pdf, 35 pages)

**Care score:** 4  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** The aggregation, quorum, and ladder rules are usable, but the volume cannot ship while two normative partnership algorithms disagree, conformance is stated two ways, and ticket residue plus legal overclaim sit in the rule text.

## Strengths
- Polarity defaults are a closed table with an aggregation per column, including detector median (p. 5).
- `quorum:M/N` is pinned as absolute-M, with the 2-of-3-grown-to-5 case written out, and distinguished from the T7 liveness margin (p. 20).
- Policy I separates mechanism prefixes from L1–L5 rendering in a two-column table and a `ladder_verdict` function (pp. 30–31).
- Member removal has one canonical statement, with per-write DEK stop-wrap for self/family and epoch rotation for community/affiliations (p. 26).

## Weaknesses
- Page 1 binds every composing consumer and says a consumer "may not skip the ones marked normative." Page 4 says a conforming consumer "MUST implement at least Policy A; the others are RECOMMENDED." Policy M is then headed "(normative)" and its DEK cascade is "MANDATORY, not opt-in" (pp. 6–7); Policy L's v2 wrap is "(normative)" (p. 18).
- Page 1 promises "a licence and a grant never chain." The `grant` row allows issuance where the delegator "holds a grant-scoped delegation over" the asset (p. 22).
- `admit_community_change` rejects a new member unless `acceptance_admits` (p. 8). The Austin worked example cites that section, shows only `current_member_sigs`, and still "admit"s (p. 10).
- Page 27: admission "emits hard_case:consent_sla_breach clock-start if Alice committed consent:deletion_sla." Page 28 emits that same row only "if now > deadline and completion is None."
- Partnership grant/accept are `attestation_type: "scores"` with `subject_key_ids` and no `stance` (pp. 24–25). `ratified_pair` requires `subject_kind == "consent_record"`, `stance == "granted"`, and singular `subject_key_id` / `target_key_id` (pp. 28–29). Page 30 then composes PARTNERED as `consent:partnership_grant` + `consent:partnership_accept`.
- Unprefixed scopes are "exact-string matched" and also "the agency:* / infra:network_presence equivalents" (p. 23), while the login grant uses unprefixed `network_presence` on the agent (pp. 21, 24) and the `agency:*` list has no `network_presence` or `sub_delegation` (p. 23).
- Page 1 says each policy states inputs and output. Policy B is two sentences; Policy C names "confidence decay per hop" and gives no decay (pp. 34–35).
- "Closes G3" (p. 5) and "M-1's symmetry is structural, not bolted on" (p. 35) are ticket leftovers. Section 4.1.5 is a history of "7 stories", "12 stories", "10 stories", "(1 reviewer)" (p. 4). "Per Miranda Fricker's epistemic injustice" (p. 4) is a ruling attribution. "The recants distinction matters CC 2.4.1.3" drops "per" (p. 3).
- Page 34 cites CC 4.4.1 for "cw_class:* declarations from low-attestation-density cohorts MUST NOT be downweighted." CC 4.4.1 names only `testimonial_witness:*` and `non_maleficence:*` (p. 5).
- "In a CEG/RET stack member resolution replaces DNS+IP" and "the DNS-free resolution" (p. 9) sit beside the install endpoint "registry.ciris-services-1.ai/install" (p. 31). Score "≥ 0.7" (p. 31) has no source in this volume.
- 4.4.3.2.8 is an essay: "the kibbutz catch", "the operator the seed lacked", "Why this is still 1+4" (pp. 13, 17). The same slogan returns at pp. 22 and 32. "This gives a persecuted community a cryptographic home" (p. 6) and "structural rather than rhetorical" (p. 32) are marketing. "honestly applied" (p. 30) editorializes a gate.

## Opportunities
- Make page 1's conformance sentence match page 4, or mark which starred "(normative)" blocks a Policy-A-only consumer must still run. One sentence removes the bind conflict.
- Pick one partnership record shape and delete the other query. The p. 30 table already names grant/accept; `ratified_pair` should select those dimensions, or the JCS member set should grow `stance` / `consent_record` — the steward has to say which bytes are signed.
- Delete the Austin example's admit line or add the acceptance row the gate requires (p. 10). Point the SLA sentence on p. 27 at the deadline watcher instead of redefining the row.
- Strike "Closes G3", "M-1", the story counts, and the Fricker attribution; keep the three bullets as RFC 2119 MUST NOT / SHOULD. Cut "1+4 preserved" and the "Why this is still 1+4" close (p. 17).
- Replace "honors HIPAA", "a FISA/NSL gag complies", and "GDPR Art 17(3)… exemptions" with "a consumer may declare a profile; this text does not determine legal compliance."
- Give Policy B and Policy C the same input/output paragraph page 1 promises, or stop calling them reference policies.

## Threats
- A lawyer will treat "Honors the HIPAA minimum-necessary standard (45 CFR 164.502(b))" (p. 14), "a FISA/NSL gag complies via USA-FREEDOM-style aggregate banding rather than unlawful real-time emission" (p. 15), and the GDPR Art. 17 exemption claim (p. 13) as compliance opinions the text cannot support. "chinese-wall pattern" (p. 14) is the phrase a reviewer will quote.
- An implementer who hybrid-signs the p. 24 member set will never satisfy `ratified_pair` (pp. 28–29). That is a false interop pin, not a style issue.
- "Any one signatory revokes → the contract Contribution is evicted" (p. 29), stated as consumer MUST, will be read as a legal-validity rule even with the aside that legal validity is "consumer-side."
- Absolute-M (a 5-member `quorum:2/3` still admits on 2 signatures, p. 20) plus a configurable depth cap "above the CC 4.1.1 default-5" (p. 14) against a page-1 promise of "the delegation graph's depth cap" gives a hostile reviewer a governance hole the anti-pattern section claimed to close (p. 2 weight cap is only SHOULD, while p. 1 states a weight cap as a promise).
- Three open-admission spellings — `admission == "open"` (p. 9), `consensus_protocol = "open:self_admit"` (p. 11), and no `open:self_admit` arm in the family match (p. 19) — plus `license` scope vs prose "licence" (pp. 1, 22) will fail exact-string verifiers.
- `HUMANITY_ACCORD` (pp. 6, 19) and `humanity-accord` (pp. 20, 32) are not obviously one identifier.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | 24 vs 28–30 | contradiction | Scores grant/accept with `subject_key_ids` and no `stance` cannot match `ratified_pair`'s `consent_record` + `stance == "granted"` + `subject_key_id`. Page 30 describes the scores dimensions. | Steward picks one shape; rewrite the other algorithm and the JCS set to it. |
| 2 | 1 vs 4, 6–7, 18 | contradiction | "may not skip the ones marked normative" vs "MUST implement at least Policy A; the others are RECOMMENDED," while M and L are marked normative/MANDATORY. | One conformance sentence. Say which M/L MUSTs bind a Policy-A-only consumer. |
| 3 | 1 vs 22; 21–23 | contradiction | "a grant never chain[s]" vs "grant-scoped delegation." Exact-string scopes vs "legacy unprefixed kinds … are the agency:* / infra:network_presence equivalents," with `network_presence` on the agent login grant and absent from `agency:*`. | State whether grant authority chains. Publish one scope table: token, class, equivalent, or delete "equivalents." |
| 4 | 8 vs 10 | contradiction | Gate requires `acceptance_admits` for every new member; the geographic example admits Alice on majority signatures alone. | Add the acceptance row or stop claiming the example passed 4.4.3.2.3. |
| 5 | 27 vs 28 | contradiction | Same `hard_case:consent_sla_breach` is a clock-start at admission and a post-deadline breach. | One emission rule. Rename the clock-start if both events are wanted. |
| 6 | 5, 35, 4 | stale | "Closes G3"; "M-1's symmetry"; "7 stories" / "12 stories" / "(1 reviewer)". | Delete ticket ids and story counts. Leave the rule. |
| 7 | 13–15 | overclaim | "Honors the HIPAA minimum-necessary standard"; FISA/NSL gag "complies"; GDPR Art. 17 exemptions as what the gate does. | Name the config fields. Do not say they satisfy the statute. |
| 8 | 34 vs 5; 9 vs 31 | overclaim | `cw_class:*` non-downweight pinned to 4.4.1, which does not mention it. "DNS-free" resolution vs `registry.ciris-services-1.ai/install`. Unsourced "≥ 0.7". | Cite the row that names `cw_class`, or drop the MUST. Drop the hostname or the DNS-free claim. Show the register row for 0.7 or mark it a default. |

## Rendering
- p. 34: `attestation:registry_consensus` is clipped to "attestation:regi" at the line break in the Policy G sentence.
- pp. 28–29: `.first` is swallowed into the comments ("subject signing for self.first", "producer signing.first"), so the normative query does not show the selector.
- pp. 18–19: identifier broken with a space, "X25519MlKem768Aes256 GcmHkdfSha256".
- p. 9 and pp. 26–27: `resolve_community` / `resolve_family` / `resolve_self` lines break inside the call (`== C` then `).where`, and "see CC 4.4.3.2.3" sits inside the pseudocode).
- p. 13: vocabulary token split across lines as `culturally_` / `restricted`.
- p. 16: the holiday-committee / UN table wraps mid-token ("ST/SGB/" "2007/6", "consensus_" "protocol").
- p. 22: extra ")" at the end of the `license` cell ("is stated there)").
- p. 25: comment points canonical kinds at "CC 4.4.3.4.3.1", which is the JCS section; the kinds are in 4.4.3.4.3.

## Effort estimate
About two to three days, and it is not mechanical: partnership bytes, the conformance floor, and whether a grant chains need the steward's rulings before the contradictory passages can be cut to one rule.

<!-- model x-ai/grok-4.7; 35 pages; prompt_tokens 29111; completion_tokens 16204; 178s -->
