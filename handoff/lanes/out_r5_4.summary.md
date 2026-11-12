# Fifth reading, share 4: summary

Head 1ee1bcf, branch rc19. Seven rule keys, 425 statements, 39 findings.

## The three numbers

- New major findings, text against text: **4**
- New major findings, text against data: **0**
- Statements opened in the text: **420** of 425; read by gist only: **5**

## Per rule key

| Rule key | Statements | Findings | Major new | Major known | Minor new | Minor known |
|---|---|---|---|---|---|---|
| transport | 191 | 16 | 1 | 2 | 7 | 6 |
| erasure | 95 | 8 | 1 | 3 | 3 | 1 |
| halt | 61 | 7 | 1 | 2 | 3 | 1 |
| standing | 48 | 3 | 0 | 0 | 3 | 0 |
| settlement | 20 | 4 | 1 | 1 | 1 | 1 |
| other:composition | 8 | 0 | 0 | 0 | 0 | 0 |
| other:relief-never-expand | 2 | 1 | 0 | 1 | 0 | 0 |
| **Total** | **425** | **39** | **4** | **9** | **17** | **9** |

Of the 39, 25 are text against text and 14 are text against data. All 14 data findings are either
known (9) or new and minor (5).

## The major new findings in full

**1. transport, CC 5.3.3.5 E1 items 5 and 6: may a dialler that holds only an announce seal?**
Item 5 serves the pre-seal route fetch to "two strangers on a bare mesh, each holding only the
other's announce", and CC 5.3.4 repeats it ("a dialler holding only a stranger's announce receives
that key's own hybrid-signed route row as the link's first frame"). Item 6 then requires the
dialler to bind the received record to something it held before dialling (the commitment of the
code that named the key, a record from the key plane, or a Rooted binding) and says "a dialler
holding none of these fails closed". A dialler holding only an announce holds none of them. The
last sentence of item 6 ("The exchange itself is post-quantum against a passive adversary whatever
the dialler held") reads as if the exchange goes on. One implementer seals to a stranger known only
by announce and the other refuses. Nothing else in the text decides.

**2. erasure, CC 4.4.3.5.2 against CC 3.3.1 D1: does the subject's own withdrawal discharge the
producer?** The deletion clock starts when the subject emits `consent:state:revoked` "or an
admitted `withdraws`" against the target `T`. The breach is defined as the window passed and `T`
"still present with none of the three composers against it". The subject's withdrawal is itself a
`withdraws` against `T`, so read literally a clock started by a withdrawal can never end in a
breach. CC 3.3.1 step 5 ("Producer withdraws, supersedes or hard-deletes the row within the
window") means the producer's own act. `manifests/reactions.json` copies the literal reading: the
`sla` clock starts on "withdrawn of target" and the breach is emitted unless "withdrawn of target".
The two readings differ on whether a producer who does nothing after a subject's withdrawal is
ever flagged.

**3. halt, CC 2.6.7 against CC 4.2.1.1, 4.2.1 and 2.4: a future-dated halt row.** CC 2.6.7 states
with no exception that an attestation whose `asserted_at` is more than five minutes in the future
"MUST" be rejected as malformed. CC 4.2.1 says of the halt that "the signer-chosen `asserted_at`
plays no part", CC 4.2.1.1 that "a future-dated one cannot buy a longer pause", and CC 2.4 that the
kill switch depends on no plane gate "beyond verifying those bytes and the holder roster". One
reader's node latches on a future-dated halt and the other's refuses the row. This is the sibling
of C036 (what holds past `valid_until`, open with the steward) on the other signed instant. The
family model's freshness cell for `accord:invoke:constitutional:{halt_id}` is the generic one
(future skew of at most five minutes), so the data follows CC 2.6.7.

**4. settlement, CC 3.1.9.2 against CC 3.3.10.1, 3.3.5.1 and 3.3.1 D3: the grounds of a slashing
verdict.** The registry row for `slashing:{outcome}` says it "Only fires on documented
Method-execution spoofing or the `moderation:{allegation_type}` allegation types above", and those
types are a closed five. CC 3.3.10.1 sends a proven ledger fork to the same verdict "against the
posted stake", CC 3.3.5.1 sends exchange non-delivery to "a proven_rogue slashing:{outcome}", and
CC 3.3.1 D3 names a deletion-window breach as evidence toward "slashing verdicts". A door built
from the registry row refuses those verdicts. A door built from the other three sections admits
them, and a bond is forfeited.

## Known conflicts found still present

| Id | Where | State |
|---|---|---|
| C335 (C315, C336) | relay tree for live media | open with the steward, reported as it would be found anyway |
| C036 | halt `valid_until` | open with the steward |
| C304 | CC 4.5.2.2 Article 17 row | the pseudocode is repaired, the compliance table row is not |
| C341 | `link_seq` per link or per (link, stream) | still present |
| C342 | A/V trailer, first form against shipping form | still present |
| C151 | which nodes are onion relays | proposed, not applied |
| C143 | phone relay default, "unmetered" against "Wi-Fi" | settled, both wordings stand |
| C062 | "purge" for an immediate-removal takedown | repaired in CC 4.5.3, not in CC 6.1.2.2 |
| C373 | guard contact against no direct contact | read as no conflict; reported for the overlap |
| C377 | destroy at the close of the withhold clock with no `unless` | still present, now on four leaves |
| C453 | no `legal_hold` or `erasure_exempt` in the data | still present |
| C378 (C435) | expiry on `accord:lifecycle` | still present |
| C457 | `accord:lifecycle:{kind}` cosign cell reads none | still present; count cell and transitions agree with the text |
| C447 (C458) | `slashing:{outcome}` signed by any registered key | still present |
| C363 | ledger delegate clause | gone from the registry, still in the family model's reserved cell |
| C471 | `transport:canonical_rebind` supersede by its author alone | still present |
| C466 | `rendezvous:route` supersede transition | text repaired, data not |
| C509 | durable `mesh_config` on one steward signature | still present |

Known conflicts checked and found repaired, so not reported: C295, C302, C374, C376, C393, C455,
C456, C478, C495, the text side of C379, and the active-leaf guard of C489.

## Keys not finished

None. Every key was read to the end.

## Read by gist only (5 statements)

The entry phrase did not locate these and a search of the section did not find their words today.

- transport, CC 3.2: "All resolution is key_id to signed transport_destination to Reticulum; DNS is never part of the trust or addressing chain"
- transport, CC 4.4.3.4.3: "Each occurrence binds a transport_destination; the app is reachable on RET as the user occurrence"
- erasure, CC 3.2: "The audit chain keeps the tombstone of a withdrawn location_proof, never the cell" (its restatements in CC 3.3.3 and CC 4.5.9.3 were opened)
- standing, CC 2.6.1.7: "roles is an optional set beside the key record and is also carried inside the signed registration_envelope"
- standing, CC 3.2: "A resignation leaving exactly M founders stalls the root; recovery is the conferring body's conferral of a replacement founder, never lowering M" (the T7 paragraphs it summarises were opened)

## Notes for whoever merges

- 83 of the 425 statements have an empty or stale `entry_phrase` in
  `formal/derivation/rule_entries.tsv` (46 of them in transport, mostly CC 5.3.3.5, 5.3.3.2.3 and
  CC 3.2 "Adding a device"). I read those sections whole instead.
- Several inventory gists are older than the text: CC 2.1 `deletion_window` ("absent means the
  family's default"; the text now says no family default exists), CC 4.5.3 item 2 ("SHOULD cease
  serving"), CC 4.5.13 ("merit auto-promotion"), CC 3.3.1 D3 ("WA-quorum"), CC 5.4.6 ("answering
  relays in any position"). None is a conflict in the text today.
- Two of the five new minor data findings are a manifest disagreeing with another manifest, with
  the text on the side of `transitions.json`: the lifecycle cell of
  `accord:invoke:constitutional:{halt_id}` in the family model, and the guard typed on the
  `transport:{kind}` card for a rule that belongs to `identity:occurrence`.
