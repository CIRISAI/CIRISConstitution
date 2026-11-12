# Lane T1 summary: C001 to C140 (140 rows)


## By kind

- Manner: 39
- Rules: 22
- Facts: 21
- Circumstances: 16
- Model: 12
- Structure: 10
- Identity: 6
- Premises: 4
- Process: 4
- Confidence: 4
- Priorities: 2

## By record

- no: 123
- yes: 17

## By class

- drift: 85
- none: 32
- gap: 13
- interaction: 8
- data-repo: 2

## By mechanism

- other: 45
- guard: 22
- clock: 17
- count: 12
- wire: 10
- change: 8
- signer: 7
- fold: 6
- erasure: 6
- audience: 5
- lifecycle: 2

## By model

- none: 32
- authority_tree: 12
- new:incapacity_binding: 9
- accord_roster: 8
- new:link_shaping: 8
- membership: 8
- new:guardianship: 6
- trust_root: 6
- new:freshness_window: 6
- two_path: 5
- accord_halt: 5
- new:takedown: 5
- new:privilege_register: 5
- new:stream_keys: 5
- new:owner_binding: 4
- new:descent_floor: 3
- age_assurance: 2
- cewp_node: 2
- mesh_life: 1
- transport_tiers: 1
- withdraws_admission: 1
- standing: 1
- trust_set: 1
- moderator_election: 1
- new:moderation_window: 1
- affiliation: 1
- event_lifecycle: 1

## By would_catch

- no: 66
- yes: 56
- partly: 18

## Properties under each new model


### new:incapacity_binding (7 with a property; 9 findings)

- C011 (yes): No incapacity binding is plenary, whatever a policy sets.
- C012 (yes): The capacity assessor is neither the steward nor the petitioner.
- C013 (yes): A binding with no champion distinct from steward, assessor and petitioner, or with a minor as steward, is refused.
- C014 (partly): The emergency doctrine is tier T0 and gives no steward standing; reversible_pending is admissible from T1.
- C016 (partly): With no capacity row on record the person reads as having capacity.
- C017 (partly): A binding row that names no petitioner is refused.
- C019 (yes): A binding whose valid_until outruns the review cadence, or whose attester is the steward or the petitioner, is refused.

### new:link_shaping (7 with a property; 8 findings)

- C073 (yes): The frame and the device class are fixed for the fleet; a node sets only whether it offers shaping.
- C074 (yes): A node with shaping off gives a shaped link at its device class to a peer that asks.
- C075 (yes): Every class of the budget table, seat included, is an offer.
- C076 (yes): A peer past the eight-link bound is admitted by displacement or refused, never run below its class.
- C077 (partly): The hold after the last real frame is the operator's value with a ten-minute default, never a ceiling.
- C078 (partly): Large is more than 64 KiB by the file's whole size, a bound apart from the 1 MiB envelope cap.
- C079 (partly): Every named configuration key bounds a quantity some section defines.

### new:stream_keys (5 with a property; 5 findings)

- C113 (yes): The epoch DEK is derived from the exporter secret, and the exporter secret is never wrapped.
- C114 (partly): A stream is kept by the producer's choice, read from history_on_join full or from the wraps.
- C115 (yes): A stream epoch advances on every add; the community epoch DEK rotates on removal and never on admission.
- C116 (yes): The community epoch DEK is wrapped to every current member; a stream DEK is wrapped only for a kept stream.
- C131 (yes): Every case, separator or ordering variant of a wrap_algorithm string is refused as unknown.

### new:guardianship (4 with a property; 6 findings)

- C002 (yes): A minor may hold a set of live guardians, and a per-act co-sign counts M of that set.
- C003 (yes): A community-scope act by an identity read at 13 to 15 is admitted only with a guardian's co-sign, whatever envelope is set.
- C004 (yes): A guardian's own exit takes one signature; adding or removing another guardian is never a lone act.
- C010 (yes): Any one guardian narrows a widening the set co-signed; widening again takes the set.

### new:takedown (4 with a property; 5 findings)

- C060 (yes): No holder serves the bytes while an admitted notice stands.
- C061 (yes): Every basis marked Immediate is destroyed on receipt at every holder, on the storage side as on the serving side.
- C062 (partly): An immediate-removal notice destroys on receipt; a steward_purge dwells W before hard deletion.
- C064 (partly): A duty-holder's takedown and a steward_purge differ in admission, reach and timing.

### new:owner_binding (4 with a property; 4 findings)

- C107 (yes): An owner binding written at self may be re-signed wider as a second row, and a serve-seat node's or an open joiner's stands at federation scope.
- C132 (yes): Un-announcing retires the federation row and leaves the self row as it was.
- C133 (yes): owner_of folds every live binding; an announcement supersedes none of the narrower rows.
- C134 (yes): A peer holds every owner binding whose scope it is in: federation for a stranger, the group's for a group peer, the addressed one for a contact.

### new:freshness_window (4 with a property; 6 findings)

- C117 (yes): A chain-judged row older than W is refused whatever its signer's standing.
- C119 (partly): A row whose asserted_at is past the future bound is refused under one named token.
- C121 (yes): The freshness window is 72 hours for every row; only a proposal's own window_until reaches seven days.
- C122 (partly): No rule reads a clock other than a peer's own synchronised UTC clock.

### new:descent_floor (3 with a property; 3 findings)

- C046 (yes): An item exactly at the threshold reads below the floor; the predicate has two values.
- C047 (yes): Revocation forces an item below the floor unless it is erasure-exempt, under legal hold, or the signer's kept copy at self scope.
- C049 (yes): Every EjectionVerdict value has a disposition.

### new:privilege_register (2 with a property; 5 findings)

- C081 (partly): Every revision condition names its mechanical evaluator.
- C085 (yes): The register holds two kinds of entry: privileges with all four cells, and entrenched structure listed for visibility.

### new:moderation_window (1 with a property; 1 findings)

- C137 (yes): A private report opens no window; only an action raised in the room defaults to removal at the window's end.

## Notes

- `none` in the model column marks a citation, a term or a presentation finding that no model reads.
- Rows whose resolution reads "settled from the text" with both sides standing in their own case (C004, C010, C041, C051, C074, C102, C117, C121) are classed interaction.
- C080 and C099 are register rows of this repository behind a consistent text (data-repo). C136 is classed drift for the text finding; its remaining stale side is a register row.
- No row in this range is data-store.
