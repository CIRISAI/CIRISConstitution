# Lane T, range C141 to C287 (147 rows)

## By kind

- Rules: 34
- Manner: 31
- Model: 17
- Circumstances: 16
- Facts: 16
- Identity: 14
- Structure: 12
- Process: 4
- Confidence: 3

## By record

- no: 133
- yes: 14

## By class

- drift: 92
- none: 32
- gap: 11
- interaction: 9
- data-repo: 2
- data-store: 1

## By mechanism

- other: 38
- guard: 23
- audience: 20
- wire: 18
- count: 13
- signer: 10
- change: 9
- clock: 8
- fold: 6
- erasure: 2

## By model

- new:text_lint: 34
- new:wire_codec: 11
- mesh_net: 9
- new:owner_binding: 8
- consent: 7
- new:key_cascade: 6
- self_roster: 6
- withdraws_admission: 6
- onion_layers: 5
- trust_root: 5
- census_ballot: 4
- new:namespace_matcher: 4
- authority_tree: 4
- affiliation: 4
- trust_set: 4
- mesh_life: 3
- new:capacity_gate: 3
- moderator_election: 3
- standing: 3
- two_path: 3
- membership: 2
- accord_halt: 2
- family_model: 2
- event_lifecycle: 1
- anonymous: 1
- contact: 1
- new:rendezvous_mailbox: 1
- new:takedown: 1
- accord_roster: 1
- new:deferral: 1
- guarantees: 1
- new:deletion_window: 1

## By would_catch

- yes: 77
- no: 43
- partly: 27

## Properties under each new model

### new:text_lint (34 findings)

- no model reads these (wording, citation, count or status): C148, C149, C153, C162, C168, C175, C176, C177, C184, C185, C186, C193, C194, C195, C200, C220, C224, C225, C233, C235, C236, C237, C242, C243, C250, C251, C257, C258, C261, C263, C270, C273, C277, C282

### new:wire_codec (11 findings)

- C167 (partly): Each FedCode kind maps to exactly one value of one named vocabulary.
- C221 (partly): A relay that re-serialises changes no signing byte.
- C222 (partly): An intake refusal made before the parse completes carries the same token as the canonical-bytes refusal.
- C223 (yes): An envelope of exactly 1 MiB of canonical bytes is admitted and one byte more is refused.
- C231 (partly): The set of refusal tokens is closed and every token the text names is in it.
- C232 (yes): The key record's member set is closed and holds no hardware class outside the attestation evidence.
- C241 (yes): Every member the text names is a member of the signed-object table.
- C259 (yes): A row of any attestation type may carry a reference to another row, with composer meaning on the three composers alone.
- C264 (partly): Every signed member has exactly one row that gives its meaning.
- no model reads these (wording, citation, count or status): C146, C239

### new:owner_binding (8 findings)

- C204 (yes): The accountable-root predicate holds for an adult user key that is not steward-bound and for a steward-bound key, so a seated holder always satisfies it.
- C208 (yes): An identity occurrence never makes a key steward-bound, and the steward fold reads owner-bindings alone.
- C209 (partly): The steward predicate is membership of a set that has at most one member.
- C210 (yes): Custody is single-valued while agency delegation may have several parents.
- C244 (yes): Ownership moves by withdraw-then-rebind or supersede-then-rebind, and at most one live owner-binding holds at any instant.
- C247 (yes): An identity occurrence never makes a key steward-bound, and the steward fold reads owner-bindings alone.
- C248 (yes): A node takes part in normal operation only after the claim that binds it to its owner.
- C253 (yes): A minor's node never carries an owner-binding at federation scope.

### new:key_cascade (6 findings)

- C158 (yes): Every self and family write is sealed under a fresh key, so a removal needs no rotation.
- C159 (yes): A wrap's recipient is always an occurrence encryption key and never an identity key.
- C160 (yes): At community and affiliations a joiner reads no earlier epoch, and at self and family admission re-keys the walk.
- C169 (yes): No wrapped key is admitted under the v1 suite on any axis.
- C170 (yes): A withdraws or recants that names a key grant is refused.
- C280 (yes): A key grant is a scores row of the key-grant family, one per recipient, with no discriminator of its own.

### new:namespace_matcher (4 findings)

- C178 (yes): An exempt family is admitted with or without a tail.
- C179 (partly): An ungated family may be admitted without a registry row, and a gated family never.
- C180 (partly): Every gated stem of the manifest fits the definition of gated, and an unclaimed leaf under it is refused.
- C256 (yes): A score is admitted only if it lies in the polarity class the registry gives its family.

### new:capacity_gate (3 findings)

- C181 (partly): No read rule of the substrate redacts a capacity row.
- no model reads these (wording, citation, count or status): C182, C187

### new:rendezvous_mailbox (1 findings)

- C150 (partly): Every bound a mailbox cites resolves to a stated number.

### new:takedown (1 findings)

- C171 (yes): A Dmca512 withhold reverses at ten days counted from each holder's tombstone.

### new:deferral (1 findings)

- C234 (partly): A deferral trigger stops the action in question and leaves the agent running on everything else.

### new:deletion_window (1 findings)

- C272 (yes): A deletion window is judged on the row that carries it, and a breach is that row still present after its deadline.
