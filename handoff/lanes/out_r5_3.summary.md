# Fifth reading, share 3 (lane r5-3): summary

Head 1ee1bcf, branch rc19. Output: `out_r5_3.tsv` (41 findings). Conflict table checked through C512.

## The three numbers

- New major findings, text against text: **3**
- New major findings, text against data: **3**
- Statements opened in the text: **409** of 425; read by gist only: **16**

## Per rule key

| rule key | statements | findings | major new | major known | minor new | minor known |
|---|---|---|---|---|---|---|
| signer | 201 | 22 | 4 | 10 | 6 | 2 |
| owner_binding | 93 | 5 | 1 | 0 | 3 | 1 |
| freshness | 61 | 9 | 1 | 3 | 3 | 2 |
| steward | 47 | 1 | 0 | 0 | 1 | 0 |
| legal_hold | 16 | 3 | 0 | 2 | 1 | 0 |
| other:keep | 4 | 0 | 0 | 0 | 0 | 0 |
| other:asymmetry-register | 2 | 1 | 0 | 0 | 0 | 1 |
| other:generated-from-data | 1 | 0 | 0 | 0 | 0 | 0 |
| total | 425 | 41 | 6 | 15 | 14 | 6 |

## Major new findings in full

**Text against text**

1. **signer: `retirement:custodian_minted` is one leaf for two acts with two signers (CC 3.1.5, CC 7.5.5).**
   CC 3.1.5 lists `custodian_minted` as a rung of the agent's own ladder before `retired` and says the
   ladder is "Self-emitted up to `retired` (attester = the agent key)"; formal/retirement mints the first
   custodian at that rung. CC 7.5.5 and the last cell of the same registry row make
   `retirement:custodian_minted:v1` the row by which "the operator holding the record and the Wise
   Authority name a successor", cosigned and citing the `retired` row. Nothing on the wire separates the
   rung from the replacement. A door built from CC 7.5.5 refuses the agent's own rung; one built from the
   state list admits an agent-signed `custodian_minted`.

2. **owner_binding: which capacity rung a provisional (T1) adult-incapacity binding needs (CC 3.4.12).**
   "Any continuing or high-scope domain (`financial`, `medical`, `digital_identity`) requires the
   **`panel` rung**." The T1 row admits "a single `provider`-rung capacity attestation **plus** the
   adjudicated binding" with enumerated health and asset-preservation powers, and the admission predicate
   asks only for a live `incapacitated` row for one domain at any level. One implementer refuses a T1
   binding scoped to `medical` without a panel; the other admits it on one clinician plus the order.

3. **freshness: whether a halt revokes (CC 3.4.1 against CC 3.2 T4).**
   CC 3.4.1: "Revocation rides the tombstone, `withdraws`/`recants`, supersession, or the halt latch, and
   nothing else." CC 3.2 T4: a root "is never revoked by a halt, which reaches an agent's act gate and no
   root". A consumer built from CC 3.4.1 drops the validity of a root, key or conferral on a halt. CC 3.2
   and CC 4.2.1.1 (a halt disrupts no data and is read by the act gate only) support T4.

**Text against data**

4. **signer: the count rule on `custodian_minted` (CC 8.10 card, manifests/transitions.json).**
   `leaf=custodian_minted => custodian_replace` sends every row of that leaf to the operator-and-WA 2/2
   row. The agent's own ladder rung of the same name (CC 3.1.5) is then counted as a replacement. Same
   root as finding 1; the data follows CC 7.5.5.

5. **signer: `consent:partnership_grant` signer cell (manifests/family_model.json).** The text side of
   C360 was repaired: CC 3.4.5 now reads "by the granting user as `attesting_key_id`". The cc-table cell
   still carries `via: delegates_to(chain rooted at a subject)` with the qualifier "a subject of the
   target, or a chain rooted at one", so a delegate may sign a partnership grant under the data.

6. **signer: `takedown_notice:{basis}` signer cell (manifests/family_model.json).** The CC 4.5.5
   duty-holder table gives three signers: the content's authoritative subject set as-self, a named
   `takedown` holder, and on a hash match the owner of the detecting node (CC 4.5.3). The cell, citing
   CC 4.5.5 as agreeing, is `seat_role(takedown)` via `delegates_to(takedown)`: a subject's own notice
   and the node owner's notice are refused under the data.

## Known findings still present

- C368: CC 4.5.9.4 still admits a "delegates_to proxy chain" for a location proof; CC 4.5.9.1 is repaired.
- C033: marked already fixed, but CC 3.2 T8 still reads the halt latch at "the halt's `asserted_at`".
- C387, C365 (and C388), C445 (and C484), C446, C422 (and C364), C448, C366, C449 (and C485, C497),
  C496, C372, C453, C323, C474, C122, C119, C085: fault unchanged in the text or the data.
- Open with the steward and reported because this reading reached them independently: C117, C395, C312.
- Not reported because found repaired: C363 (the registry rule for ledger rows now reads "a delegation
  confers no write"), C107 (the CC 3.1.3.2 sentence is gone), C360 text side.

## Read by gist only (16 statements)

- signer (7): CC 3.1.3.2 membership proposal and acceptance signers (2); CC 3.2 infrastructure trust-root
  community and public-community founding (2); CC 3.2 owner as `attesting_key_id` and the guardian's
  signature (2); CC 4.4.3.4.3 moderation admission restatement (1).
- owner_binding (1): CC 3.1.3.2 owner-binding placement (the sentence no longer exists; see C107).
- freshness (5): four CC 2.6.1.7 table rows (asserted_at, valid_until, scrub_timestamp twice); CC 3.2
  geographic admission on a location proof.
- steward (2): CC 3.2 founders of ciris-canonical; CC 4.4.3.8 cold-start restatement.
- other:generated-from-data (1): CC 2.6.1.7 one-source claim; the table, CDDL and JSON were not
  compared member by member.

## Keys not finished

None. Limits: the family cards of CC 8.10 were read for retirement only; elsewhere the comparison used
`family_model.json` signer and freshness cells, `transitions.json` for retirement, and the default row.
`reactions.json` and `signed_object.cddl` were not compared for these keys.
