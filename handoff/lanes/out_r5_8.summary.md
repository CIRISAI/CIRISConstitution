# Fifth reading, share 8: summary

Share: 8 rule keys, 425 statements of `rule_inventory.tsv` (family scope included). Head 1ee1bcf, branch rc19.

## The three numbers

- New major findings, text against text: **3** (standing proposal against the 30-day expiry; hop-key reuse list; the Catastrophic-Risk Evaluation opened by tier in Annex I).
- New major findings, text against data: **1** (key:revocation attest role `self`), reported with a stated doubt about the role token.
- Statements opened in the text: **395**. Read by gist only: **30**.

## Per rule key

| rule key | statements | opened | gist only | major new | major known | minor new | minor known |
|---|---|---|---|---|---|---|---|
| admission_order | 141 | 136 | 5 | 3 | 1 (C498) | 6 | 1 (C118) |
| conformance | 113 | 99 | 14 | 0 | 0 | 2 | 0 |
| amendment | 79 | 78 | 1 | 0 | 1 (C157) | 2 | 1 (C089) |
| licensure | 54 | 45 | 9 | 1 | 0 | 0 | 0 |
| endpoint | 30 | 29 | 1 | 0 | 0 | 2 | 0 |
| other:client | 6 | 6 | 0 | 0 | 0 | 1 | 0 |
| other:public-transparency | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| other:local-act | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| total | 425 | 395 | 30 | 4 | 2 | 13 | 2 |

21 findings: 6 major (4 new, 2 known), 15 minor (13 new, 2 known).

## Major new findings in full

1. **A standing proposal and the 30-day expiry (admission_order; CC 3.2 against CC 3.1.3.2).**
   CC 3.2: "The founder's standing **`membership:proposal:v1`** is then addressed to any requester". CC 3.1.3.2: "`expires_at` is REQUIRED on a proposal, after its `asserted_at` and at most 30 days later", and an acceptance of an expired proposal is terminal (`membership_proposal_expired`); `constants.tsv` carries the cap as `membership_proposal_max_secs`. No sentence exempts the standing proposal of an open room or says it is re-signed. One implementer admits a joiner against a founder's offer of any age; another refuses every joiner after day 30 until the founder signs a new one, and an open room whose founder has left closes. Nothing in the text decides.

2. **What a hop key may not equal (admission_order; CC 3.3.6.2 against itself).**
   "the hop key is distinct from the transit pair and from every other key on the same signed row. A binding that reuses one is refused." against "A half equal to either half of `transit_kex_pubkeys`, to the transport x25519 or ed25519, or to the signer's pinned keys is refused". The content KEM pair of CC 3.3.6.1 (`encryption_pubkeys`) rides the same occurrence row and is in the first sentence's reach and not in the second's list. The transit pair has the same gap between its rule (which names the content KEM keys) and its in-row list (which does not). One door refuses the row and another admits it. No reuse token is in any manifest, so the data does not settle it.

3. **The Catastrophic-Risk Evaluation opened by tier (licensure key, the Part 7 formula rows; CC 7.3.3 against CC 8.8.9).**
   CC 7.3.3: "That is the one trigger ... and the Stewardship Tier never triggers it" (RM ≥ 4). CC 8.8.9 (Annex I): "the CRE Protocol (Annex D) must re-evaluate any ST ≥ 3 deployment with network-facing components before the next F-Audit cycle", and its sector table caps Critical Infrastructure autonomy "at **A2** unless CRE passes". A deployment at ST 3 with RM 3 is evaluated under the annex and never under Part 7. CC 8.8.3 now agrees with Part 7, so C313 is repaired there and is not reported; this is a second annex the repair did not reach.

4. **Who may sign a key revocation (admission_order; text against data).**
   CC 2.4.1.1 carries a `revoking_key_id` distinct from the revoked key and treats self-revocation as one case ("recognised when the revoker's own key digests to the subject"); CC 3.1.3 judges "the revoker's authority ... without the subject's record". `manifests/transitions.json` gives the key:revocation attest the single role `self` (from `transition_text.tsv`, cited to CC 2.4.1.1). If `self` means signer equals subject, as it does on session and census:share, a kernel executing the table refuses every revocation but a key's own. If the token means the revoker's own key there is no finding; the doubt is stated in the row.

## Known majors still present

- **C498** (CC 3.1.3 against CC 4.5.13): the ballot row still refuses a ballot naming an unknown election id or a non-member, where the home stores every ballot. The transitions guard follows CC 3.1.3.
- **C157** (CC 4.5.1 against CC 6.1.9): the scale gate is still measured by a census count the census does not define.

## Checked and not reported

- C313 (CC 8.8.3 trigger): repaired in CC 8.8.3.
- C402 (election id): CC 3.1.3 now reads as CC 4.5.13 does.
- The data differences on goal:{scale}, evidence, consent:community_trust, accord:lifecycle, deferral:response, census rows and mesh_config are already C446, C467 to C469, C496, C378, C435, C457, C489, C398, C347, C348, C383, C470, C509; I saw each still present in the data and did not repeat them.
- The Stewardship Tier arithmetic of CC 7.3.3 (formula, bands, worked examples) is consistent with itself.
- The census rows (k floor, expected-active, partial checks) read consistently across CC 3.1.3 and CC 6.1.9 apart from what C154, C156 and C350 already hold.

## Read by gist only (30)

- admission_order (5): CC 3.2 [the minor-steward owner-binding rule], CC 5.3.3.2.3 (three: binding acceptance order, relay verification, receiver verification), CC 5.3.3.5 (dialler check).
- amendment (1): CC 2.6.1.8 (a candidate may move signed bytes; read beside CC 2.6.4, which I opened).
- conformance (14): CC 2.6.1.7 (two, on the vectors), CC 2.6.1.8, CC 3.1.3.2 (persist enforces joiner consent), CC 3.2 (archive_mode), CC 4.4.3.4.3 (three), CC 4.4.3.8, CC 5.2, CC 5.3.3.2.1, CC 5.3.3.2.3 (two), CC 5.3.3.2.5.
- licensure (9): CC 2.1 (two capacity members), CC 2.6.1.7 (capacity members), CC 3.2 (duty-scope floor), CC 4.4.3.4.3 (two), CC 4.4.3.8 (three).
- endpoint (1): CC 4.4.3.8 (/v1/accord-holders as projection; its CC 5.3.4 twin was opened).

## Keys not finished

None. The conformance key is a set of unrelated statements that share a word; it was read for pairs across its own rows and against the other keys, not as one rule.
