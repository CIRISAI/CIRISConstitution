# Lane K, share 4: one rule, every statement of it

Statements read: 399 (every non-family row of the eleven keys; family rows read as context). Findings: 39.

| rule key | statements | major new | major known | minor new | minor known |
|---|---|---|---|---|---|
| conformance | 106 | 1 | 0 | 6 | 0 |
| amendment | 73 | 0 | 2 | 4 | 1 |
| key_plane | 62 | 1 | 1 | 5 | 0 |
| agent_identity | 53 | 1 | 0 | 4 | 0 |
| minor_floor | 45 | 3 | 1 | 1 | 0 |
| reserved_prefix | 23 | 2 | 0 | 1 | 0 |
| policy_row | 20 | 0 | 0 | 3 | 2 |
| other:choice-item | 13 | 0 | 0 | 0 | 0 |
| other:list-of-record | 2 | 0 | 0 | 0 | 0 |
| other:public-transparency | 1 | 0 | 0 | 0 | 0 |
| other:local-act | 1 | 0 | 0 | 0 | 0 |
| **total** | 399 | 8 | 4 | 24 | 3 |

Known ids met again: C002, C087, C089, C115, C139, C157, C284.

## Major new findings

### conformance (CC 3.1.7), kind exception

- A. CC 3.1.7: A producer MUST NOT ship a dimension family this Part does not register.
- B. CC 3.1.7: The ProducerSteward fallback remains only for the open-vocabulary space this Part deliberately leaves open.
- One sentence forbids shipping any unregistered family and a neighbour orders a substrate to fail emission on a family with no registry row (namespace_family_unregistered); two others keep an admissible open vocabulary and the x_private range. A reader of the first refuses a party's own unregistered dimension, a reader of the second admits it under the producer-steward fallback. The closing paragraph of CC 3.1.7 (open vocabulary is for a party's own dimensions, never a shipped component's) supports the second, with the MUST NOT bound to shipped components.

### key_plane (CC 5.2, CC 4.4.3.4.1), kind scope

- A. CC 5.2: or each `member.key_id` in the named family's roster (family).
- B. CC 4.4.3.4.1: At every sealed write the substrate wraps the content's DEK to every current recipient occurrence and emits one `key_grant` row per wrap.
- CC 5.2 wraps a family write once per member key and names the wrap target by key id; CC 4.4.3.4.1 (the cascade's home) wraps to every occurrence of every recipient, and CC 5.2's own next paragraph says the target is the occurrence's encryption_pubkeys, never a signing key. Under the first a family member's second device reads nothing. The home supports per occurrence.

### agent_identity (CC 1.16.5, CC 4.3), kind actor

- A. CC 1.16.5: Appointment, rotation, recusal, and appeals are external to this system’s control and follow explicit anti-capture rules.
- B. CC 4.3: A seat over one party's deferrals is conferred by that party in a signed row and by nobody else;
- Who answers an agent's deferral: Wise Authorities appointed under the Annex B charter, outside the system (CC 1.16.5, CC 1.9 'designated'), or whoever the agent's steward seated by a delegates_to, and the steward itself where no seat row exists (CC 4.3). CC 4.3 says 'the charter governs the designated body' and does not say how that body relates to a conferred seat. The CC 4.5.1 register also records 'none' as the exit from the WA relation, while CC 4.3 lets the conferrer end a seat by withdraws. CC 4.3 is the normative, wire-checked rule.

### minor_floor (CC 3.4.13, CC 3.2), kind condition

- A. CC 3.4.13: So a person with no assurance on record uses their own and their family's scopes freely
- B. CC 3.2: **No minor `user` identity operates without a live adult steward.**
- A person with no age assurance reads as under 13 (the fail-secure rule), hence a minor. CC 3.2 and CC 3.4.13 Q4 ('A guardian-less minor goes dark for general operation') stop a minor with no guardian from operating; the fail-secure paragraph lets the same person use self and family scope freely with no guardian. One build blocks every unassured new user, the other does not. The fail-secure paragraph is the newer ruling (C001) and reads the guardian rule as binding an attested minor.

### minor_floor (CC 5.4.6, CC 4.5.13), kind condition

- A. CC 5.4.6: So a node whose owner resolves to the `minor` band MUST NOT carry a federation-scope owner-binding, and admission MUST refuse the promotion.
- B. CC 4.5.13: **Announcing starts on,** its cost on screen.
- With no assurance on record an owner resolves to under_13, which implies minor (CC 3.4.13), so admission refuses the federation-scope binding for every person who has not yet shown a provider-rung signal; CC 4.5.13 has announcing on by default 'for nearly everyone'. Whether 'resolves to the minor band' means attested as a minor, or includes the fail-secure default, is unstated and decides who is reachable.

### minor_floor (CC 3.4.13, CC 4.3), kind actor

- A. CC 3.4.13: fail-secure MUST mean the report reaches a standing Wise-Authority / mandated-report endpoint via WBD even with no guardian present
- B. CC 4.3: there is no roster of permitted Wise Authorities and a substrate checks none.
- The help floor requires a standing Wise Authority that receives a child's report with no guardian present. CC 4.3 seats a Wise Authority only by the deferring party's own row, or for a ward by whoever holds the binding, and keeps no standing body on the wire. For a child whose guardian is the threat, no rule says who the standing receiver is or who seated it.

### reserved_prefix (CC 4.4.3.8, CC 3.1.9.2), kind data:scope

- A. CC 4.4.3.8: Every reserved-prefix role — `trusted_publisher` reserving `content_rating:*`
- B. data: manifests/namespace_registry.json: content_rating:{scheme}:{rating} has reserved false and no reserved_rule
- CC 4.4.3.8 and CC 3.2 treat content_rating:* as a reserved prefix whose emitter role is conferred by delegation, and CC 3.4.7 has a substrate reject a reserved-prefix row from any other key. The registry, which CC 3.1.7 makes the enforcement surface, carries the family unreserved, so a matcher built from it admits a rating from any key. The CC 3.1.9.2 catalogue row speaks of 'the trusted-publisher emitter rule' and CC 3.4 lists no such reservation.

### reserved_prefix (CC 3.4.7.1, CC 4.4.3.8), kind condition

- A. CC 3.4.7.1: A key satisfies a reserved-prefix gate iff the required role is one of its held roles.
- B. CC 4.4.3.8: leaving a reserved-prefix role with **no** named plane leaves it self-assertable, which is the hole this rule closes.
- One test is set membership in the key's identity_type, which CC 3.4.5 calls self-asserted; the other requires a live delegates_to from a root the asking node trusts, resolved at use. The registry's detector rule reads 'identity_type contains lenscore_detector'. A substrate built from CC 3.4.7.1 alone admits a detection:* row from any key that lists the role. CC 3.2 and CC 4.4.3.8 support the delegation test.

## Notes on method

- Every quote in the TSV was checked by script to stand verbatim in the Part file today and to be 30 words or fewer. A side beginning `data:` names a data file and its value. One side_b (C157) is a description in brackets, since that conflict is an absence in CC 6.1.9.
- Statements with no `entry_phrase` (about 40, mostly in CC 2.6.1.8, CC 4.4.3.4.3, CC 5.2, CC 5.3.3.2.x) were found by gist in their section.
- `other:choice-item` (13 statements): compared with `manifests/choice_item.cddl` (four kinds, five answer states, three provenances) and with the `widens`, `undo` and `confirm` cells of all 455 transitions in `manifests/transitions.json`. Text and data agree: confirm is true exactly where a transition widens or has no undo. No finding.
- `other:list-of-record`, `other:public-transparency`, `other:local-act`: read, no finding.
- `conformance` is a mixed key (vectors, profiles, pins, privacy representation). Most of its statements have no second statement of the same rule; the findings are where two do.
- Compared with data: `constitution/governance_policy.tsv`, `constitution/constants.tsv`, `constitution/consensus_protocols.tsv`, `manifests/namespace_registry.json`, `manifests/transitions.json`, `manifests/choice_item.cddl`. Not compared: `manifests/reactions.json` and `manifests/signed_object.cddl` beyond the two envelope members cited.

## Keys not finished

None. All eleven keys were read through once. The reading of `conformance` statements under CC 5.3.3.2.x (A/V chunk vectors) and CC 6.1.x (pin lines) was against their neighbours in the same key only, not against the vector files.
