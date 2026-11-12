# Lane T4: C381 to C470 (90 rows classified; range C381 to C470)

## By kind

- Rules: 27
- Circumstances: 18
- Identity: 18
- Structure: 9
- Model: 8
- Facts: 3
- Confidence: 3
- Priorities: 2
- Process: 2

## By record

- no: 73
- yes: 17

## By class

- drift: 38
- data-store: 19
- data-repo: 15
- none: 10
- interaction: 8

## By mechanism

- signer: 18
- audience: 13
- guard: 13
- wire: 11
- fold: 9
- clock: 8
- count: 7
- lifecycle: 5
- erasure: 3
- change: 3

## By model

- family_model: 18
- consent: 8
- membership: 7
- age_assurance: 5
- mesh_net: 4
- authority_tree: 4
- new:key_epoch: 4
- affiliation: 3
- census_ballot: 3
- new:stream_chunks: 3
- new:signed_object: 3
- anonymous: 3
- standing: 2
- new:merge_policy: 2
- new:takedown: 2
- new:report_window: 2
- moderator_election: 2
- self_roster: 2
- new:pqc_admission: 2
- accord_halt: 2
- two_path: 1
- moderation_lift: 1
- trust_root: 1
- new:partnership_pair: 1
- trust_set: 1
- retirement: 1
- new:owner_binding: 1
- contact: 1
- new:deletion_window: 1

## By would_catch

- yes: 76
- no: 10
- partly: 4

## Properties under each new model

### new:deletion_window

- C456: A producer is in breach exactly when the window has passed with the row still present, whatever it had begun.

### new:key_epoch

- C404: A joiner holds no key for an epoch before its admission unless the publisher signed a re-share.
- C405: A new member's grant of the current epoch key is emitted at the minter's next sealed write, not at admission.
- C407: The archive mode in force for a room is derivable from rows every member holds.

### new:merge_policy

- C385: For a licence the more restrictive state stands after merge, whatever the asserted instants or ids of the rows.
- C420: A stale active licence row never overwrites a revocation after merge.

### new:owner_binding

- C452: A node with one owner and two live owner-signed rows reads steward-bound exactly as it does with one row.

### new:partnership_pair

- C416: In each partnership half subject_key_id names the other party, and ratification pairs the two halves on that member.

### new:pqc_admission


### new:report_window

- C390: Content with a removal majority and no keep-decision at window close is in exactly one state, removed or held behind consent, and that state is fixed by rule.
- C391: A report filed privately with the duty holder never starts a removal window.

### new:signed_object

- C438: Every signed row carries its row mirror, and no signer member sits at the top level of a partnership half.
- C442: Every row signature, an accord invocation's included, verifies over the JCS of the envelope and no other preimage.
- C443: A derived row id is a well-formed attestation_id under the signed object's type, by a stated fold from the digest.

### new:stream_chunks

- C433: A receipt on a best-effort stream is admitted against a producer-signed root with no witness cosignature.
- C441: A sealed chunk has one name for the life of its stream, and an append that collides with it is refused across an epoch roll.
- C444: A receipt over a root that was never published is refused, not merely advised against.

### new:takedown

- C389: The CommunityStandards withhold window is 30 days and no operator setting changes it.
- C395: Every takedown notice is signed by a key holding the takedown duty, and a node key holds no judgment duty.
