# Lane T-3 summary: C288 to C380 (93 rows)


## By kind

- Rules: 28
- Identity: 16
- Circumstances: 15
- Structure: 10
- Model: 10
- Process: 7
- Facts: 5
- Priorities: 1
- Manner: 1

## By record

- no: 64
- yes: 29

## By class

- drift: 41
- none: 21
- data-repo: 16
- interaction: 10
- data-store: 4
- gap: 1

## By mechanism

- guard: 18
- audience: 16
- signer: 13
- count: 9
- clock: 9
- change: 7
- fold: 7
- wire: 6
- erasure: 4
- other: 2
- lifecycle: 2

## By model

- new:signer_gate: 9
- new:takedown: 8
- withdraws_admission: 6
- consent: 6
- new:key_cascade: 5
- mesh_net: 5
- new:namespace_gate: 5
- new:wire_shape: 5
- transport_tiers: 4
- census_ballot: 4
- accord_roster: 3
- trust_set: 3
- alm: 3
- age_assurance: 3
- new:supersede_rule: 3
- two_path: 3
- authority_tree: 2
- new:publish_seam: 2
- new:deletion_window: 2
- accord_halt: 2
- self_roster: 2
- new:partnership_pair: 2
- new:cre_trigger: 1
- standing: 1
- new:stream_receipt: 1
- retirement: 1
- affiliation: 1
- anonymous: 1

## By would_catch

- yes: 68
- no: 20
- partly: 5

## Properties under each new model


### new:signer_gate (9)

- C288: An accord holder's key signs only the families the enumeration of CC 4.2.1 lists, so every registered accord family is either in the enumeration or has no admissible signer.
- C321: No key record holds the node type together with agent or user.
- C323: A content-rating row is admitted only from a key that holds the trusted-publisher role by delegation.
- C324: A reserved-prefix row is admitted only when the role was conferred by delegation; listing the role on one's own key record confers nothing.
- C359: A key record is admitted only under its own key by possession; an anchor's scrub is a cosignature and never the base signature.
- C363: No delegate writes a ledger row; only the ledger's single owner does.
- C365: A watchlist is enabled or disabled only by a key holding the group's moderate or takedown authority.
- C366: A petition is the petitioner's own row, and each of the other three adjudication states is admitted only from the seated quorum.
- C368: A location proof is admitted only under the subject's own signature; no delegation mints one.

### new:takedown (8)

- C302: A court-order notice reaches the bytes plane only and never carries the dwell or the selection digest of a steward purge.
- C303, C306: (no conflict found; no property)
- C307: A steward-purge notice is admitted only when cosigned under the trust root's consensus protocol, never on one voice.
- C312: Bytes under a live legal hold are never destroyed, and an immediate-removal notice always destroys on receipt: the two cannot both hold for one object.
- C375: The withhold window of each windowed basis is the one fixed number of days the home section gives, and no operator sets it.
- C376: Every windowed basis stops serving on admission, runs its window, and destroys the bytes at its close.
- C377: Bytes withheld under a windowed notice are not destroyed at the close of the window if a reversal was admitted inside it.

### new:key_cascade (5)

- C291: A node denied for a cohort by its owner's allow list never receives a key for that cohort.
- C311: Every wrap of a content key is made by the sealer to a current recipient occurrence, and no member's substrate re-wraps.
- C326, C327, C330: A key grant that names the recipient occurrence as its attested key is admitted at the content's scope.

### new:namespace_gate (5)

- C296: (no conflict found; no property)
- C319: A row of a family with no registry row is never admitted.
- C320, C328: A row whose dimension does not resolve through the registry is refused at admission, on all five row types.
- C343: Every dimension the text permits a producer to emit matches a registered shape and is admitted.

### new:wire_shape (5)

- C322: A label's fingerprint recomputes from its key at one fixed length, so a verifier never meets a label it cannot check.
- C341: No outer nonce repeats under one link key.
- C342: The trailer a relay cuts from a chunk is the trailer the publisher signed, byte for byte, in the shipping form.
- C356: A membership proposal without an expiry instant is refused.
- C357: (no conflict found; no property)

### new:supersede_rule (3)

- C332: A replacing row signed by someone other than the prior row's attester is admitted only where a named rule allows it, so a guardian is never displaced by a stranger's row.
- C333: A replacing row signed by someone other than the prior row's attester is admitted only where a named rule allows it.
- C334: A widening leaves the narrower row standing beside it and retires nothing.

### new:publish_seam (2)

- C298: Every item that becomes public was hash-matched at the seam it crossed, whether or not the receiving group enabled a list.
- C299: Matching runs only at a promotion into the Commons or a post into a public room, and never inside a private cohort.

### new:deletion_window (2)

- C304, C305: A deletion is in breach whenever its window has closed and the row is still present with none of the three composers against it, whatever completion row was emitted.

### new:partnership_pair (2)

- C360: A standalone partnership grant signed by the granting party and naming only the partner is admitted.
- C361: A grant and an acceptance built as the text directs always ratify as a pair.

### new:cre_trigger (1)

- C313: A Catastrophic-Risk Evaluation opens exactly when a system is assessed at RM 4 or above.

### new:stream_receipt (1)

- C358: A receipt on a stream that is not accountable is admitted against a published head without a witness cosignature.

## Notes

- Class follows the verifier's verdict: "no conflict on reading" is none; "to fix from the text" is drift; "to fix in the data" is data-repo or data-store by the resolution's own words; the fourteen "for Eric" rows are interaction, except C288, read as a gap (the enumeration is silent on two registered families).
- Mixed data rows, filed by the first fault named: C364 (registry string is this repository's; the signer cell is the shipped store's), C366 (signer cell is the store's; the derived policy is this repository's), C367 (verbs and transitions are this repository's; the lifecycle cell records an unbuilt family in the store).
- Duplicates in the range: C304/C305; C315/C335/C336; C320/C328; C326/C327/C330; C369/C374 (and C164 outside the range).
- C310 is classed none yet marked partly: a halt model with per-node latch ids would show the residue the verifier names (nodes latching different ids).
- Model choices that are judgement calls: C309 and C372 sit in `consent` because it holds the backdating window W; C369/C374 sit in `accord_roster` for the threshold, though a per-transition policy check in `two_path` would catch them as well; C290 and C318 sit in `authority_tree` as the nearest home of a conferred seat, which it does not yet model.
