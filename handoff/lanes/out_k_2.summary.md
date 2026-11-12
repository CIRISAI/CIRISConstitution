# Lane K share 2: summary

| rule key | statements read | major new | major known | minor new | minor known |
|---|---|---|---|---|---|
| transport | 186 of 186 | 4 | 0 | 8 | 4 |
| transparency_log | 60 of 60 | 0 | 0 | 6 | 1 |
| admission_order | 53 of 53 | 0 | 0 | 4 | 0 |
| announce | 33 of 33 | 0 | 1 | 2 | 1 |
| moderation | 28 of 28 | 0 | 1 | 2 | 0 |
| subject | 21 of 21 | 2 | 0 | 1 | 0 |
| signer | 14 of 14 | 1 | 0 | 0 | 0 |
| other:asymmetry-register | 2 of 2 | 0 | 0 | 0 | 1 |
| other:inventory | 2 of 2 | 0 | 0 | 0 | 0 |
| total | 399 | 7 | 2 | 23 | 7 |

## Major new findings

- **transport** (5.3.3.5,5.3.3.4, exception). CC 5.3.3.5: "There is no relay tree; the small-group realtime profile of [CC 5.3.3.2](#5.3.3.2) pushes on direct links" against CC 5.3.3.4: "A member MAY take each layer of a stream from a different parent of the member relay tree". E2, E1 sentence 1, the CC 5.3.3.2 profile table and CC 2.1 deny any media relay role in realtime delivery; CC 5.3.3.4, 5.3.3.2.3 (member relay verifies and forwards chunks) and 5.4.6 (the tree's relays) build one. One implementer ships direct links only, the other a forwarding tree. The later-written sections (binding, trailer, layered multipath) support the tree.

- **transport** (2.1,5.3.3.2.3, exception). CC 2.1: "on direct links and never through a relay tree" against CC 5.3.3.2.3: "A member relay forwards a binding it has verified to every other leg, and only when the binding's publisher is the peer it heard it from". Same rule as the row above, read from the grammar side: CC 2.1 says push never crosses a relay tree; the chunk format defines what a member relay forwards and when. Push through a member relay is either forbidden or specified.

- **transport** (5.4.3, scope). CC 5.4.3: "Chat and files ride a shaped link only when one end of it is shaped-only." against CC 5.4.3: "A shaped link carries rows: statements, posts, messages, reactions, the small images that fit the budget, and the control traffic of the planes.". Between two offering nodes that hold a shaped link, one paragraph sends chat over the unshaped link beside it and the other (with item 4, "ordinary rows are shaped") puts messages on the shaped link. Whether a message between two servers is covered differs. The carriage paragraph is the more specific.

- **transport** (5.4.6, condition). CC 5.4.6: "a scoped body MAY ride the members' **identity-plane link** on three terms" against CC 5.4.6: "crosses a forwarder only one that has said yes, a consented contact or, as last resort, a serve seat; a stranger is offered none". The first paragraph lets a room body cross any non-member transport node between two members on three terms, none of them the node's consent; "Who carries what" adds that the forwarder must be a carrier that said yes. Two phones behind NATs with only a stranger between them exchange a room body under one reading and not the other. The later paragraph and CC 5.4.3 support the consent condition.

- **subject** (2.1,3.1.3, exception). CC 2.1: "A targeted row naming a third party in `attested_key_id` is refused at admission" against CC 3.1.3: "`attested_key_id` is the recipient occurrence; the envelope carries the key's identity on that axis and the wrap". A key grant is a scores row placed at the content's scope, signed by the sealer, with the recipient in attested_key_id: a third party there. CC 2.1 states one exception to the producer rule (delegates_to) and the next paragraph puts a key grant's recipient among subject_key_ids. Read from CC 2.1 alone a community key grant is refused. family_model.json records the grant as an exception ("attested = recipient occurrence"), which supports CC 3.1.3.

- **subject** (2.1, data:condition). CC 2.1: "A row naming a key outside its audience is refused `subject_outside_audience`." against data family_default_row.json: "in_audience": "no". The default subject_rule of every family (157 of 184 cells, source code-v61) reads in_audience "no" and the default replication audience is cohort_plus_subjects: the shipped store admits a targeted row naming an outsider and serves it to them. The text (CC 2.1, CC 5.2) refuses the row. No departure reason or conflict row records the difference.

- **signer** (4.4.3.4.3,4.5.13, actor). CC 4.4.3.4.3: "their **agent** (the agent's local key) are two occurrences of one user identity that share one **Self DEK**" against CC 4.5.13: "An agent signs no item of a person's queue: the person's choices are the person's.". CC 3.3.6.3 defines the roster as the identity_occurrence rows under the fedID and lets "any live roster key" sign as the fedID for every owner act (consent, owner-binding, root acceptance, approving a device), and CC 4.5.13 counts a vote signed by any key of the fedID. If the agent's key is an occurrence of the user, it signs all of these. CC 4.5.13, CC 4.3 and CC 3.3.6.3 ("an agent's occurrence is single-signer") deny it. The denial is the later text and the one CC 1.13.2 supports.

## Keys not finished

None: every key of the share was read.
