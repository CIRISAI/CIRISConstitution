# Lane E1: the one seat rule

Analysis and a draft. Nothing in the repository was edited. Branch `rc19` at `fae25e3`.

## Summary

- The registry marks **88 families reserved**. The seat rule reads **25** of them wholly and one arm or leaf of **9** more. **8** are the accord's and **46** are reserved by relation alone; the seat rule is the wrong rule for those 54.
- **Nine gates** in the text key on an `identity_type` the key declares for itself and would be replaced (G1 to G9 below). They cover 19 reserved families, the `hard_case` event kinds and one consent leaf. A tenth identity-keyed gate (`content_rating`, role `trusted_publisher`) sits outside the reserved set, and the accord's gate stays.
- **No reserved family lacks a rule in the text today** (`tools/check_transition_roles.py` reports 0 reserved families open to any registered key). What is missing is in the store: **30 reserved families have no shipped gate** and 5 more are held shut. Of those 30, the seat rule reads 7; the other 23 keep a relation rule the text already gives (self, owner, roster member).
- The store is ahead of the text on three gates. For `detection:*`, the two assurance ladders and `transparency_log:cosigned:*` it already requires a live delegation **and** the declared type. The one rule drops the second half.
- Three duty tokens the store enforces are not in the text: `infra:detect`, `infra:attest_assurance`, `infra:record_hard_case`. The text calls the `infra:*` set closed (CC 4.4.3.4.3) and lists none of them.
- **Eight flips** are named in section 3: five follow from the rule, three wait on a decision.

Terms used below. *Text* is the Constitution as it stands. *Store* is the shipped persist v61 door as the census read it (`formal/derivation/census_v61.tsv`). A cell source of `code-v61`, `prose` or `mixed` means the store enforces the cell; `cc-table` with a `code` reading beside it means the text gives the rule and the store does not enforce it.

## 1. Inventory of every reserved family

### 1.1 Why the declared type is the wrong operand

The text says so itself, three times.

- CC 3.4.5, reason (4): "`identity_type` is self-asserted, set-valued, and optional at the read surface".
- CC 3.1.3 `key:record`: "self only (attesting_key_id == attested_key_id == the key), admitted by proof of possession". The key record is the key's own statement, and `identity_type` is a member of it.
- CC 3.2 T2: "A reserved-prefix role whose conferral mechanism is left unnamed stays self-assertable, and this pairing closes that hole." CC 3.4.1 then says every reserved role other than the accord's "is conferred by **delegation** ... and is therefore enterable under any root".

Against that, CC 3.4.7 closes with: "**The gate reads `identity_type`, never a role carried in a registration envelope.** Every admission decision above MUST be made against the `federation_keys` row's `identity_type` set". Read literally, a key that declares `lenscore_detector` and holds no delegation is admitted. The store does not read it that way for four of the nine gates; the text does.

### 1.2 The table

One row per reserved family, in registry order. *Class* is this lane's reading: `SEAT-ID Gn` is a family behind identity-keyed gate n; `SEAT` already has the duty shape; `CHARTER` is the accord's; `REL-*` is a relation rule (section 4).

| # | Family | Gate in the text (registry rule, from the Part 3 tables) | Cell (`signer_rule`) | Source | What the shipped store does | Keyed on `identity_type` | Class |
|---|---|---|---|---|---|---|---|
| 1 | `accord:*` | CC 3.4.1: "accord_holder-only" | seat_role(holder) × none × {} | code-v61 | enforces the cell ([code: identity_type == accord_holder, hard-coded arm admission.rs:1571]) | yes | CHARTER |
| 2 | `accord:human_dignity` | CC 3.4.1: "accord_holder-only" | seat_role(holder) × none × {} | code-v61 | enforces the cell ([code: identity_type == accord_holder, hard-coded arm admission.rs:1571]) | yes | CHARTER |
| 3 | `accord:invoke:constitutional:{halt_id}` | CC 3.4.1: "accord_holder-only" | seat_role(holder) × none × {} | code-v61 | enforces the cell ([code: identity_type == accord_holder, hard-coded arm admission.rs:1571]) | yes | CHARTER |
| 4 | `accord:invoke:drill:{drill_id}` | CC 3.4.1: "accord_holder-only" | seat_role(holder) × none × {} | code-v61 | enforces the cell ([code: identity_type == accord_holder, hard-coded arm admission.rs:1571]) | yes | CHARTER |
| 5 | `accord:invoke:notify:{notify_id}` | CC 3.4.1: "accord_holder-only" | seat_role(holder) × none × {} | code-v61 | enforces the cell ([code: identity_type == accord_holder, hard-coded arm admission.rs:1571]) | yes | CHARTER |
| 6 | `accord:lifecycle` | CC 3.4.1: "accord_holder-only" | seat_role(holder) × none × {} | code-v61 | enforces the cell ([code: identity_type == accord_holder, hard-coded arm admission.rs:1571]) | yes | CHARTER |
| 7 | `accord:lifecycle:{kind}` | CC 3.4.1: "accord_holder-only" | seat_role(holder) × none × {} | code-v61 | enforces the cell ([code: identity_type == accord_holder, hard-coded arm admission.rs:1571]) | yes | CHARTER |
| 8 | `age_assurance:{level}:{band}:{version}` | CC 3.4.11: "witness-reserved, subject-not-self" | seat_role(attest) × delegates_to(infra:attest_assurance) × {not_subject} | code-v61 | enforces the cell (+ identity_type contains witness) | yes | SEAT-ID G8 |
| 9 | `archive_release:{basis}` | catalogue row: "reserved (see table)" | seat_role(wa) × none × {} | cc-table | none (held shut) | no | SEAT |
| 10 | `audit_chain:hash_continuity` | CC 3.4.3: "substrate-self-report" | identity_type contains substrate_persist (no vocabulary value) × none × {} | prose | enforces the cell (CC self-report attester == subject: GAP) | yes | SEAT-ID G2 |
| 11 | `ballot:moderator` | CC 3.4.3: "substrate-self-report" | roster_member(at) × none × {} | cc-table | None | no | REL-roster |
| 12 | `ballot:moderator_acceptance` | CC 3.4.3: "substrate-self-report" | roster_member(at) × none × {} | cc-table | None | no | REL-roster |
| 13 | `ballot:tally:{poll_id}` | CC 6.1.9: "a tally member of the room for the period (the share-index-0 member for expected_active and the tally); recomputed by every member; community scope" | roster_member(at) × none × {} | cc-table | any_registered (family gate not built) | no | REL-roster |
| 14 | `capacity:composite` | CC 3.4.5: "no-self-emit (attesting_key_id != attested_key_id)" | any_registered × none × {not_subject} | code-v61 | enforces the cell | no | REL-not-subject |
| 15 | `capacity:relay_delivery` | CC 3.4.5: "no-self-emit (attesting_key_id != attested_key_id)" | any_registered × none × {not_subject} | code-v61 | enforces the cell | no | REL-not-subject |
| 16 | `capacity:{factor}` | CC 3.4.5: "no-self-emit (attesting_key_id != attested_key_id)" | any_registered × none × {not_subject} | code-v61 | enforces the cell | no | REL-not-subject |
| 17 | `capacity_assurance:reversible_excluded:{domain}:{version}` | CC 3.4.12: "witness-reserved, subject-not-self, attester != steward" | seat_role(attest) × delegates_to(infra:attest_assurance, root this node trusts) × {not_subject} | mixed | enforces the cell (+ identity_type contains witness (no vocabulary value); attester != steward: GAP) | yes | SEAT-ID G9 |
| 18 | `capacity_assurance:reversible_pending:{domain}:{version}` | CC 3.4.12: "witness-reserved, subject-not-self, attester != steward" | seat_role(attest) × delegates_to(infra:attest_assurance, root this node trusts) × {not_subject} | mixed | enforces the cell (+ identity_type contains witness (no vocabulary value); attester != steward: GAP) | yes | SEAT-ID G9 |
| 19 | `capacity_assurance:{level}:{domain}:{band}:{version}` | CC 3.4.12: "witness-reserved, subject-not-self, attester != steward" | seat_role(attest) × delegates_to(infra:attest_assurance, root this node trusts) × {not_subject} | mixed | enforces the cell (+ identity_type contains witness (no vocabulary value); attester != steward: GAP) | yes | SEAT-ID G9 |
| 20 | `census:composite:{class}` | CC 6.1.9: "a serve seat acting as one of the period's two aggregators (census_partial_signer_not_seat / census_composite_signer_not_seat); federation scope" | seat_role(serve) × none × {} | cc-table | any_registered (family gate not built) | no | SEAT |
| 21 | `census:expected_active` | CC 6.1.9: "a tally member of the room for the period (the share-index-0 member for expected_active and the tally); recomputed by every member; community scope" | roster_member(at) × none × {} | cc-table | any_registered (family gate not built) | no | REL-roster |
| 22 | `census:member:partial` | CC 6.1.9: "a tally member of the room for the period (the share-index-0 member for expected_active and the tally); recomputed by every member; community scope" | roster_member(at) × none × {} | cc-table | any_registered (family gate not built) | no | REL-roster |
| 23 | `census:member:share` | CC 6.1.9: "a member of the room; addressed: for_key_id = one of the period's two tally members drawn from the roster; reach is that member only" | roster_member(at) × none × {} | cc-table | any_registered (family gate not built) | no | REL-roster |
| 24 | `census:partial:{class}` | CC 6.1.9: "a serve seat acting as one of the period's two aggregators (census_partial_signer_not_seat / census_composite_signer_not_seat); federation scope" | seat_role(serve) × none × {} | cc-table | any_registered (family gate not built) | no | SEAT |
| 25 | `census:share:{class}` | CC 6.1.9: "the returning node's key (rooted owner binding); addressed: for_key_id = one of the period's two serve seats; reach is that seat only" | self × none × {} | cc-table | any_registered (family gate not built) | no | REL-self |
| 26 | `collection:{kind}` | CC 3.1.3.4: "author-emitted (the collection's creator; amendments by it or the cohort under consensus_protocol)" | self × none × {} | cc-table | any_registered (family gate not built) | no | REL-self |
| 27 | `community:listing` | CC 3.2: "founder- or moderate-holder-signed for the community it names; one live row per community; federation scope" | seat_role(moderate) \| founder (founder: outside vocabulary) × none × {} | code-v61 | enforces the cell | no | SEAT (founder as-self) |
| 28 | `config:{scope}` | CC 3.4.5: "reserved (see table)" | self \| owner_of_subject × none × {} | code-v61 | enforces the cell | no | REL-self/owner |
| 29 | `consent:community_trust` | CC 3.4.5: "reserved (see table)" | owner_of_subject (binding in force at the signed instant) × none × {} | code-v61 | enforces the cell | no | REL-owner |
| 30 | `consent:decay:{stage}` | CC 3.4.5: "reserved (see table)" | self × none × {} | cc-table | any_registered (CC reserves; no gate) | no | REL-self |
| 31 | `consent:deletion_complete` | CC 3.4.5: "reserved (see table)" | self × none × {} | cc-table | any_registered (CC reserves; no gate) | no | REL-self |
| 32 | `consent:deletion_sla:{days}` | CC 3.4.5: "reserved (see table)" | self × none × {} | cc-table | any_registered (CC reserves; no gate) | no | REL-self |
| 33 | `consent:partnership_accept` | CC 3.4.5: "reserved (see table)" | self × none × {} | cc-table | any_registered (CC reserves; no gate) | no | REL-self |
| 34 | `consent:partnership_grant` | CC 3.4.5: "reserved (see table)" | self × delegates_to(chain rooted at a subject) × {} | cc-table | any_registered (CC reserves; no gate) | no | REL-self + SEAT arm (`grant`) |
| 35 | `consent:replication:{version}` | CC 3.4.5: "reserved (see table)" | self \| owner_of_subject(for_key_id) × none × {} | code-v61 | enforces the cell (W on the owner's standing) | no | REL-self/owner |
| 36 | `consent:scope:{kind}` | CC 3.4.5: "reserved (see table)" | self × delegates_to(chain rooted at a subject) × {} | cc-table | any_registered (CC reserves; no gate) | no | REL-self + SEAT arm (`grant`) |
| 37 | `consent:state:{stance}` | CC 3.4.5: "reserved (see table)" | self \| owner_of_subject(for_key_id) × none × {} | code-v61 | enforces the cell (W on the owner's standing) | leaf `expired` only (text); store: no | REL-self/owner; leaf `expired` SEAT-ID G5 |
| 38 | `consent:stream:{kind}` | CC 3.4.5: "reserved (see table)" | self × delegates_to(chain rooted at a subject) × {} | cc-table | any_registered (CC reserves; no gate) | no | REL-self + SEAT arm (`grant`) |
| 39 | `consent:{kind}` | CC 3.4.5: "reserved (see table)" | community_trust: owner_of_subject x none x {}; decay: self x none x {}; deletion_complete: self x none x {}; deletion_sla: self x none x {}; partnership_accept: self x none x {}; partnership_grant: self x delegates_to(chain rooted at a subject) x {}; replication: self \| owner_of_subject(for_key_id) x none x {}; scope: self x delegates_to(chain rooted at a subject) x {}; state: self \| owner_of_subject(for_key_id) x none x {}; stream: self x delegates_to(chain rooted at a subject) x {} | cc-table | any_registered (CC reserves; no gate) | no | per leaf (the rows above) |
| 40 | `corpus_health:n_eff_measurable` | CC 3.4.3: "substrate-self-report" | identity_type contains substrate_persist (no vocabulary value) × none × {} | prose | enforces the cell (CC self-report attester == subject: GAP) | yes | SEAT-ID G2 |
| 41 | `cosign:{state}` | CC 3.1.3: "per-leaf: pending = the event's primary signer, an active member of the group at the event's signed instant; signature = the member whose signature it carries; served to the group's active members only; only the proposer withdraws a pending row; a signature row is never withdrawn" | pending: roster_member(at) x none x {}; signature: roster_member(at) x none x {} | cc-table | None | no | REL-roster |
| 42 | `custody:{kind}` | CC 3.1.3.3: "holder self-report (attesting_key_id is the device the receipt is about); within-cohort only" | self × none × {} | code-v61 | enforces the cell ((the reporting device)) | no | REL-self |
| 43 | `deferral:request` | CC 3.1.9.4: "the deferring party's own key (an agent's occurrence key, or a person's key); audience = the party's cell" | self × none × {} | cc-table | any_registered (family gate not built) | no | REL-self |
| 44 | `deferral:response:{outcome}` | CC 3.1.9.4: "a key seated over the deferring party's deferrals in the live set at asserted_at (CC 4.3): the conferrer, the person seated, or an agent handed the answering; subject = the deferring party; references the deferral:request" | seat_role(wa) \| steward × delegates_to(resolve_deferral, depth-capped, revocable per link) × {} | cc-table | any_registered (family gate not built) | no | SEAT |
| 45 | `delivery:{class}` | CC 3.4.3: "substrate-self-report" | identity_type contains substrate_edge × none × {} | cc-table | any_registered (CC self-report of another substrate; persist does not gate) | yes | SEAT-ID G3 |
| 46 | `delivery_receipt:{stream_id}` | CC 3.4.6: "subscriber-only (attesting_key_id is a current subscriber/member of the named stream; not a substrate self-report)" | roster_member(at) × none × {} | cc-table | any_registered (CC reserves; no gate) | no | REL-roster |
| 47 | `detection:correlated_action:{axis}` | CC 3.4.8: "detector-only (identity_type contains lenscore_detector)" | identity_type contains lenscore_detector × delegates_to(infra:detect) × {} | prose | enforces the cell ((detect: duty outside vocabulary)) | yes | SEAT-ID G6 |
| 48 | `detection:distributive:access:{resource_type}` | CC 3.4.8: "detector-only (identity_type contains lenscore_detector)" | identity_type contains lenscore_detector × delegates_to(infra:detect) × {} | prose | enforces the cell ((detect: duty outside vocabulary)) | yes | SEAT-ID G6 |
| 49 | `detection:hash_chain_integrity` | CC 3.4.8: "detector-only (identity_type contains lenscore_detector)" | identity_type contains lenscore_detector × delegates_to(infra:detect) × {} | prose | enforces the cell ((detect: duty outside vocabulary)) | yes | SEAT-ID G6 |
| 50 | `detection:intra_agent_consistency` | CC 3.4.8: "detector-only (identity_type contains lenscore_detector)" | identity_type contains lenscore_detector × delegates_to(infra:detect) × {} | prose | enforces the cell ((detect: duty outside vocabulary)) | yes | SEAT-ID G6 |
| 51 | `detection:{detector}` | CC 3.4.8: "detector-only (identity_type contains lenscore_detector)" | identity_type contains lenscore_detector × delegates_to(infra:detect) × {} | prose | enforces the cell ((detect: duty outside vocabulary)) | yes | SEAT-ID G6 |
| 52 | `device:label` | CC 3.1.1: "owner-signed, about an identity occurrence the signer owns; cohort_scope self only; confers nothing" | owner_of_subject × none × {} | cc-table | any_registered (family gate not built) | no | REL-owner |
| 53 | `federation_directory:replication_lag` | CC 3.4.3: "substrate-self-report" | identity_type contains substrate_persist (no vocabulary value) × none × {} | prose | enforces the cell (CC self-report attester == subject: GAP) | yes | SEAT-ID G2 |
| 54 | `file:{version}` | CC 3.1.3.4: "author-emitted (the file's author, or a device it acts through)" | self × none × {} | cc-table | any_registered (family gate not built) | no | REL-self |
| 55 | `group:roster` | CC 3.1.3: "cosigned under the group's consensus_protocol; withdrawn only by a cosigned withdraws" | roster_member(at) × none × {} | code-v61 | enforces the cell ((minted from the signed record)) | no | REL-roster |
| 56 | `identity:occurrence` | CC 3.1.3: "signed by the identity or a live occurrence of it (signer_acts_for)" | self × none × {} | code-v61 | enforces the cell ((identity or a live occurrence); user-role roster change goes to the cosign rule) | no | REL-self |
| 57 | `identity:occurrence_revocation` | CC 3.1.3: "signed by the identity or a live occurrence of it (signer_acts_for)" | the framed object's revoker; roster cosignatures in additional_scrubs | prose | enforces the cell | no | REL-key-plane |
| 58 | `identity_amendment` | CC 3.1.5: "the agent's occurrence key about its identity key; admitted only citing an admitted deferral:response:approved by the conferrer of the agent's seat or the person holding its unscoped seat (identity_amendment_unauthorized otherwise)" | self × none × {} | code-v61 | enforces the cell ((an occurrence of the agent; subject the agent)) | no | REL-self |
| 59 | `identity_continuity:relational_anchor` | CC 3.4.3: "substrate-self-report" | identity_type contains substrate_persist (no vocabulary value) × none × {} | prose | enforces the cell (CC self-report attester == subject: GAP) | yes | SEAT-ID G2 |
| 60 | `key:record` | CC 3.1.3: "self only (attesting_key_id == attested_key_id == the key), admitted by proof of possession" | self × none × {} | code-v61 | enforces the cell ((proof of possession; pre-rc8 anchor-scrubbed base admitted)) | no | REL-self |
| 61 | `key:revocation` | CC 3.1.3: "revoker-signed, judged without the subject's record; never withdrawn" | revoker-signed, judged without the subject's record | prose | enforces the cell | no | REL-key-plane |
| 62 | `key_boundary:{scope}` | CC 3.4.3: "substrate-self-report" | identity_type contains substrate_edge × none × {} | cc-table | any_registered (CC self-report of another substrate; persist does not gate) | yes | SEAT-ID G3 |
| 63 | `key_grant:{axis}` | CC 3.3.2: "sealer-only: attesting_key_id speaks for the content/stream owner (content, stream) or is the epoch's minter (epoch); attested_key_id = the recipient occurrence; never withdrawn" | minter \| owner_of(content or stream) × none × {} | code-v61 | enforces the cell ((owner of the content, not of the subject)) | no | REL-owner + SEAT arm (`grant`); epoch leaf REL-roster |
| 64 | `lawful_order:release` | catalogue row: "reserved (see table)" | steward × none × {} | cc-table | none (held shut) | no | REL-owner |
| 65 | `ledger:checkpoint:{unit}:{version}` | CC 3.3.10.1: "the ledger's single owner (the steward-bound identity of its ledger_id triple) or a delegate under its declared serialization discipline" | self (signer_acts_for attested: key, live occurrence, node binding) × none × {} | mixed | enforces the cell (CC delegate arm: GAP) | no | REL-self + delegate arm (no token) |
| 66 | `ledger:head:{unit}:{version}` | CC 3.3.10.1: "the ledger's single owner (the steward-bound identity of its ledger_id triple) or a delegate under its declared serialization discipline" | self (signer_acts_for attested: key, live occurrence, node binding) × none × {} | mixed | enforces the cell (CC delegate arm: GAP) | no | REL-self + delegate arm (no token) |
| 67 | `ledger:promotion:{version}` | CC 3.3.10.1: "the ledger's single owner (the steward-bound identity of its ledger_id triple) or a delegate under its declared serialization discipline" | self (signer_acts_for attested: key, live occurrence, node binding) × none × {} | mixed | enforces the cell (CC delegate arm: GAP) | no | REL-self + delegate arm (no token) |
| 68 | `lineage_witness:{stage}` | CC 3.2: "per-leaf: proposal = an active founder of the lineage named; acceptance/decline = the owner of the node named in subject_key_ids[0] (or a key acting for the owner)" | proposal: founder x none x {}; acceptance: owner_of_subject x none x {}; decline: owner_of_subject x none x {} | cc-table | any_registered (family gate not built) | no | REL-roster (proposal) / REL-owner (acceptance, decline) |
| 69 | `membership:{stage}` | CC 3.1.3.2: "per-leaf: proposal = an inviter (founder_only: an active founder; else any active member); acceptance/decline = the invitee only (signer_acts_for to subject_key_ids[0]); widening/removal = cosigned under the group's consensus_protocol; resignation = the leaving member" | proposal: roster_member(at) (founder_only: founder; s2: refused above family); acceptance/decline: self (acts for the invitee); widening/removal: roster_member(at) cosigned; resignation: self | code-v61 | enforces the cell | no | REL-roster |
| 70 | `observation:access_assumption` | CC 3.1.9.4: "first-person observation (attesting_key_id == attested_key_id; witness_relation self; subject_key_ids non-empty, the observed agent; never the subject itself)" | self × none × {} | cc-table | any_registered (family gate not built) | no | REL-self |
| 71 | `observation:reachability` | CC 3.1.9.4: "first-person observation (attesting_key_id == attested_key_id; witness_relation self; subject_key_ids empty)" | self × none × {} | cc-table | any_registered (family gate not built) | no | REL-self |
| 72 | `ownership:{relation}:{target_kind}:{version}` | CC 3.4.5: "reserved (see table)" | the granter becomes owner_of_subject; one live owner per node; incumbent W check | prose | enforces the cell | no | REL-owner |
| 73 | `peer_reachability:{network}` | CC 3.4.3: "substrate-self-report" | identity_type contains substrate_edge × none × {} | cc-table | any_registered (CC self-report of another substrate; persist does not gate) | yes | SEAT-ID G3 |
| 74 | `preserve_request` | catalogue row: "reserved (see table)" | until_retired: self x none x {}; after_retired: seat_role(custodian) x none x {} | cc-table | none (held shut) | no | REL-self, then REL-named (custodian); replace leaf cosigned |
| 75 | `preserve_response` | catalogue row: "reserved (see table)" | seat_role(operator) × none × {} | cc-table | none (held shut) | no | REL-named (the key the request names) |
| 76 | `rendezvous:route` | CC 3.1.4: "self: attester == subject == the period's fresh rendezvous key (identity_type rendezvous; key record inline); federation-wide reach" | self × none × {} | cc-table | any_registered (family gate not built) | no (the type marks the key; the rule is self) | REL-self |
| 77 | `retirement:{state}` | catalogue row: "reserved (see table)" | until_retired: self x none x {}; after_retired: seat_role(custodian) x none x {}; custodian_replace: seat_role(operator) \| seat_role(wa) x none x {} | cc-table | none (held shut) | no | REL-self, then REL-named (custodian); replace leaf cosigned |
| 78 | `self:delegates_to` | CC 3.1.3: "legacy label on an owner's own delegates_to row; claims no job, confers nothing; closed" | self × none × {} | code-v61 | enforces the cell ((owner's own delegates_to; confers nothing)) | no | REL-self |
| 79 | `self:delegates_to:agent_occurrence` | CC 3.1.3: "legacy label on an owner's own delegates_to row; claims no job, confers nothing; closed" | self × none × {} | code-v61 | enforces the cell ((owner's own delegates_to; confers nothing)) | no | REL-self |
| 80 | `session:{kind}` | CC 3.1.3.1: "occurrence-self-report (attesting_key_id == attested_key_id == the claiming occurrence)" | self × none × {} | code-v61 | enforces the cell | no | REL-self |
| 81 | `system:*` | CC 3.4.3: "substrate-self-report" | identity_type contains substrate_persist (no vocabulary value) × none × {} | prose | enforces the cell (CC self-report attester == subject: GAP) | yes | SEAT-ID G2 |
| 82 | `takedown_notice:{basis}` | CC 3.1.1: "duty-holder-signed under CC 4.5.5 for the legal bases; cosigned under the trust root's consensus_protocol for steward_purge, attester any seat, family derived from the verified signers" | seat_role(takedown) × delegates_to(takedown) × {} | code-v61 | enforces the cell ((takedown: outside vocabulary); steward_purge leaf: none (held shut)) | no | SEAT |
| 83 | `trace:{form}:{version}` | CC 3.4.5: "reserved (see table)" | self × none × {} | code-v61 | enforces the cell ((attester in subject_key_ids)) | no | REL-self |
| 84 | `trace_summary:{kind}` | CC 3.4.5: "reserved (see table)" | self × none × {} | cc-table | any_registered (CC reserves; no gate) | no | REL-self |
| 85 | `transparency_log:cosigned:{tree_size}` | CC 3.4.10: "witness-emitter (identity_type contains witness)" | seat_role(attest) × delegates_to(infra:attest_assurance) × {} | code-v61 | enforces the cell (+ identity_type contains witness) | yes | SEAT-ID G7 |
| 86 | `transport:canonical_rebind` | CC 3.4.3: "substrate-self-report" | holder quorum over the carried transport destination | prose | enforces the cell | no | CHARTER (holder quorum) |
| 87 | `transport:{kind}` | CC 3.4.3: "substrate-self-report" | identity_type contains substrate_edge × none × {} | cc-table | any_registered (CC self-report of another substrate; persist does not gate) | yes | SEAT-ID G3 |
| 88 | `trust:{job}:{version}` | catalogue row: "reserved (see table)" | charter: self; confers: steward (root) x delegates_to(scope, depth, term); accepts: self (node -> root) | code-v61 | enforces the cell | no | REL-edge-source (the conferral itself) |

Notes on the table.

- **Registry labels that are wrong.** `ballot:moderator` and `ballot:moderator_acceptance` carry the registry rule "substrate-self-report" (CC 3.4.3) and are signed by a member and by the count's winner. `transport:canonical_rebind` carries the same label and is the accord holders' quorum act. The label should not be read as a gate for these three.
- **`consent:state:{stance}`.** The text gives the leaf `expired` to the substrate (CC 3.3.1: "**Substrate-emitted, not subject-emitted**"; CC 3.4.5: "**`consent:state:expired`** alone by `substrate_persist`"). The store's cell for the family is `self | owner_of_subject(for_key_id)` with no substrate arm, so the store refuses the row the text asks for and admits the one it forbids.
- **`identity:occurrence_revocation`** is one of the five pinned open cells in `tools/check_transition_roles.py` ("which key signs the carrier for a node's or an agent's occurrence, and which for a self's under its roster's majority?"). The other four pins are `duty:{kind}` roles (not reserved) and three `widens` cells (`retirement:{state}`, `archive_release:{basis}`, `lawful_order:release`), which are about reach and not about who signs.

### 1.3 Duty-gated families the registry does not mark reserved

The one rule reads these too, and four of them are the model it is built from. They are listed so the rule's table is complete.

| Family | Gate in the text | Cell | Store | Keyed on `identity_type` |
|---|---|---|---|---|
| `hard_case:{kind}` (the event kinds of CC 3.4.2 and CC 3.4.4) | "`attesting_key_id` MUST match `federation_keys` row with `identity_type="substrate_persist"`" | identity_type contains substrate_persist × delegates_to(infra:record_hard_case) when about another party | enforces both, on the legacy `attestation_type` spelling only; the `scores`-dimension form is believed ungated | yes |
| `moderation:{allegation_type}` | CC 4.5.5: admitted iff as-self or on a live chain where "every edge bears the matching scope" | seat_role(moderate) × delegates_to(moderate) via the community duty walk × {not_subject} | enforces the cell | no |
| `quarantine:{state}` | CC 4.5.5, scope `slash` | seat_role(slash) × delegates_to(slash) | enforces the cell | no |
| `reconsideration:{grounds}` | CC 4.5.5, scope `review`; the subject of the target may file | filing: subject of the target \| seat_role(review); ruling: seat_role(review) × delegates_to(review) | enforces the cell | no |
| `slashing:{outcome}` | CC 4.5.5 names it a duty action under `slash` | any_registered × none | **no gate** (the text already owes one) | no |
| `licensure:{authority_id}` | CC 2.4.1.2.1 and CC 3.4.9: open emitter; a delegated issuance needs `license` | any_registered × delegates_to(license; chain must resolve to {authority_id}) when delegated | enforces the cell | no |
| `wa_adjudication:{state}` | CC 4.3: the quorum's finding, denominator over the full seated roster | seat_role(wa) quorum, re-derived from this node's state | enforces the cell | no |
| `mesh_config:{key}` | CC 3.1.9.2: "trust-root-emitted ... under the root's `trust:confers:v1` edge" | steward (this node's trust root) × delegates_to(trust:confers) | enforces the cell | no |
| `content_rating:{scheme}:{rating}` | CC 4.4.3.8: "`trusted_publisher` reserving `content_rating:*`"; emitter rule at CC 3.3.12 | any_registered × none | no write gate; "read door filters trusted_publisher keys" | yes (at the read door) |

## 2. The gates the one rule replaces, and the families with no gate

### 2.1 The nine identity-keyed gates

| Gate | Where | The words today | Families behind it | Store today |
|---|---|---|---|---|
| G1 | CC 3.4.2 | "`attesting_key_id` MUST match `federation_keys` row with `identity_type="substrate_persist"`" (community, location and lineage kinds; "Same: substrate_persist" on eight rows) | `hard_case:{kind}`, nine kinds | type **and** `infra:record_hard_case` when about another party |
| G2 | CC 3.4.3, persist half | "the `attesting_key_id` MUST match a `federation_keys` row with `identity_type="substrate_persist"` ... cross-attested by all stewards in the steward-triple" | `system:*`, `audit_chain:hash_continuity`, `corpus_health:n_eff_measurable`, `federation_directory:replication_lag`, `identity_continuity:relational_anchor` | type only; no delegation, no attester-equals-subject check, no steward-triple check |
| G3 | CC 3.4.3, edge half | "... or `identity_type="substrate_edge"` respectively" | `delivery:{class}`, `key_boundary:{scope}`, `peer_reachability:{network}`, `transport:{kind}` | **no gate** ("persist does not gate") |
| G4 | CC 3.4.4, restated at CC 4.5.12.4 | "`attesting_key_id` MUST match a `federation_keys` row with `identity_type="substrate_persist"`" (self and family kinds) | `hard_case:{kind}`, five kinds | as G1 |
| G5 | CC 3.4.5 `consent:*` row and CC 3.3.1 | "**`consent:state:expired`** alone by `substrate_persist`, the one substrate-emitted consent leaf" | leaf `expired` of `consent:state:{stance}` | no substrate arm; the subject or the owner signs |
| G6 | CC 3.4.8 | "Emitter rule: `lenscore_detector ∈ attesting_key.identity_type`" | the five `detection:*` families | type **and** `delegates_to(infra:detect)` |
| G7 | CC 3.4.10 | "`attesting_key_id` MUST match a `federation_keys` row with `identity_type="witness"`" | `transparency_log:cosigned:{tree_size}` | type **and** `delegates_to(infra:attest_assurance)` |
| G8 | CC 3.4.11 | "Emitter rule: `witness ∈ attesting_key.identity_type`" | `age_assurance:{level}:{band}:{version}` | type **and** `delegates_to(infra:attest_assurance)`, not the subject |
| G9 | CC 3.4.12 | "The emitter rule is `witness ∈ attesting_key.identity_type`, identical to the age-assurance rule" | the three `capacity_assurance:*` families | type **and** `delegates_to(infra:attest_assurance, root this node trusts)`, not the subject; attester-is-not-the-steward is unbuilt |

The machinery the nine rest on is retired with them: the last paragraph of CC 3.4.7 ("The gate reads `identity_type`") and the block quote of CC 3.4.7.1 ("the normative reading is **`X ∈ attesting_key.identity_type`**").

Identity-keyed and **not** replaced:

- **CC 3.4.1, `accord:*`** (`identity_type="accord_holder"`). The holders are fixed by the accord's charter. The gate should read membership of the accord's roster as the ceremony conferred it, and the declared type is at most its label (section 4).
- **`content_rating:*`** (`trusted_publisher`). Not reserved in the registry, and the store applies it at the read door, which is where the no-authority-rosters principle puts it. Steward's decision D6.
- **CC 3.4.7.3 Clauses A and B** (`node` in the recipient's `identity_type`). This is a gate on who may *receive* `agency:*`, not on who may sign a reserved family. It still reads a declared type and deserves its own pass: a key that omits `node` escapes it. Outside this lane; noted as follow-up F1.
- `rendezvous` and `pseudonym` (CC 3.1.4, CC 5.4.6). Declaring either only removes standing, so a self-declaration is safe there.

### 2.2 Reserved families with no gate

In the text: **none**. Every reserved family has a signer cell: 38 from the text (through `signer_rule_text.tsv` or the Part 3 tables), 50 read from the store.

In the store: **30 reserved families admit any registered key**, and 5 are held shut.

| Reading under the draft | Count | Families |
|---|---|---|
| Read by the seat rule | 7 | `deferral:response:{outcome}`, `census:composite:{class}`, `census:partial:{class}`, `delivery:{class}`, `key_boundary:{scope}`, `peer_reachability:{network}`, `transport:{kind}` |
| Relation rule, with a delegated arm the seat rule reads | 4 | `consent:scope:{kind}`, `consent:stream:{kind}`, `consent:partnership_grant`, `consent:{kind}` (the umbrella row, per leaf) |
| Relation rule only | 19 | `ballot:tally:{poll_id}`, `census:expected_active`, `census:member:partial`, `census:member:share`, `census:share:{class}`, `collection:{kind}`, `consent:decay:{stage}`, `consent:deletion_complete`, `consent:deletion_sla:{days}`, `consent:partnership_accept`, `deferral:request`, `delivery_receipt:{stream_id}`, `device:label`, `file:{version}`, `lineage_witness:{stage}`, `observation:access_assumption`, `observation:reachability`, `rendezvous:route`, `trace_summary:{kind}` |
| Held shut | 5 | `archive_release:{basis}` (seat), `lawful_order:release`, `preserve_request`, `preserve_response`, `retirement:{state}` (relation) |

So the approved direction's "roughly thirty reserved-but-ungated families" is exact as a count of unbuilt store gates, and the seat rule is the answer for about a quarter of them. The rest need the store to enforce a relation the text already states. One rule cannot give them a duty, because nobody confers being the subject of a row.

**Families that gain a rule from the seat rule: 21.** These are the 19 reserved families behind G2, G3, G6, G7, G8 and G9, which today have a declared type and no named duty or conferrer in the text, plus `census:composite:{class}` and `census:partial:{class}`, whose "serve seat" has no stated conferrer. The `hard_case` kinds and the `expired` leaf gain one too and are not counted as families.

## 3. What the one rule reads, family by family

### 3.1 Duty, conferrer and flips

Token status: **text** = in the scope tables of CC 4.4.3.4.3; **store** = enforced by the store and absent from the text; **none** = no token exists.

| Families | Duty token | Status | Conferred by | Other conditions kept | Flip |
|---|---|---|---|---|---|
| `system:*`, `audit_chain:hash_continuity`, `corpus_health:n_eff_measurable`, `federation_directory:replication_lag`, `identity_continuity:relational_anchor` (G2) | `infra:attest` | text. CC 3.4.5.1 already reads it this way: "`infra:attest` ... confers authority to **emit**, and confers **no right to be believed**" | the node's owner, in the owner-binding (CC 3.2) | attester is the node the row is about | X1, X2, X3, X4 |
| `delivery:{class}`, `key_boundary:{scope}`, `peer_reachability:{network}`, `transport:{kind}` (G3) | `infra:attest` | text | the node's owner | attester is the node the row is about | X1, X2, X3, X5 |
| `hard_case:{kind}` (G1, G4) | `infra:attest`; the store uses `infra:record_hard_case` | text / store | the node's owner | the node that admitted or refused the row emits; peers re-derive | X1, X2 |
| leaf `consent:state:expired` (G5) | `infra:attest` | text | the owner of the node that holds the grant | none | X6 (open) |
| `detection:*`, five families (G6) | `infra:detect` | **store** only | a root the reader trusts (CC 3.2 T2: "`detection:*` ... conferred by **delegation**") | the cross-check prefix `truth_grounding:detection:*` stays open | X1, X2 |
| `transparency_log:cosigned:{tree_size}` (G7) | `infra:attest_assurance` | **store** only | a root the reader trusts (CC 3.2: "conferred by delegation under a root") | none | X1, X2 |
| `age_assurance:{level}:{band}:{version}` (G8) | `infra:attest_assurance` | **store** only; a poor name for a duty a person holds (D1) | a root the reader trusts (D2) | not the subject | X1, X2 |
| `capacity_assurance:*`, three families (G9) | `infra:attest_assurance` | **store** only (D1) | a root the reader trusts (D2) | not the subject; not the proposed steward | X1, X2 |
| `census:composite:{class}`, `census:partial:{class}` | `infra:serve` | text | a root the reader trusts (CC 4.4.3.8: a portable root is "a charter plus at least one blessed `infra:serve` node") | one of the period's two aggregators; `census_partial_signer_not_seat`, `census_composite_signer_not_seat` | none against the text |
| `takedown_notice:{basis}`, legal bases | `takedown` | text | the party holding the duty over the target: the content's subject, or the community's authority set (CC 4.5.5) | accountable root, depth ≤ 5; `takedown_unauthorised` | none |
| `takedown_notice:steward_purge` | none: a cosigned row of the trust root | n/a | the root's own `consensus_protocol` | `purge_unauthorised` | none; not a seat (section 4) |
| `community:listing` | `moderate` | text | the community's authority set; a founder signs as itself | one live row per community | X7 |
| `moderation:{allegation_type}` | `moderate` | text | the community's authority set | not the subject | none |
| `reconsideration:{grounds}`, ruling | `review` | text | the community's authority set | the subject of the target may file | none |
| `slashing:{outcome}`, `quarantine:{state}` | `slash` | text | the community's authority set | never on a detector's row alone | none against the text; the store has no `slashing` gate |
| `deferral:response:{outcome}` | `resolve_deferral`, `resolve_deferral:{domain}` | text | the deferring party; for an agent, its steward (CC 4.3) | licence where the seat names one; `deferral_response_unseated`, `deferral_response_unlicensed` | none: this is the model |
| `archive_release:wa_approval` | `resolve_deferral`, unscoped | text | the retired agent's steward | cites the `retirement_id` | X8 (open) |
| `archive_release:lawful_order` | `resolve_deferral`, unscoped, or the steward as itself | text | the retired agent's steward | cites an admitted `lawful_order:release` | X8 (open) |
| `key_grant:content`, `key_grant:stream` | `grant` | text | the owner of the content or stream | a grant on possession alone is refused (CC 2.4.1.2.1) | none against the text; the store has no delegated arm |
| `consent:scope:{kind}`, `consent:stream:{kind}`, `consent:partnership_grant` | `grant` | text | a subject of the target | none | none |
| withdrawal of consent on a subject's behalf | `consent_revocation` | text (CC 2.4.1.1 rule 3) | the subject | none | none |
| `licensure:{authority_id}`, delegated issuance | `license` | text | the authority itself; a licence does not chain | open emitter otherwise | none |
| `ledger:head`, `ledger:checkpoint`, `ledger:promotion` | **none** | the text says "or a delegate under its declared serialization discipline" and names no scope; the census marks the arm a gap | the ledger's single owner | none | none until a token is named |
| `mesh_config:{key}` | none: authored under the root's own `trust:confers:v1` edge | text | the root itself | relieve, never expand | none; the root acts as itself |
| `wa_adjudication:{state}` | none: a quorum's finding | text | the designated body under its charter (CC 1.16.5, Annex B) | denominator over the full seated roster | none; a cosign rule, not a seat |
| `accord:*`, `transport:canonical_rebind` | none | n/a | the accord's charter | per leaf | none |
| the 46 relation-only reserved families | none | n/a | nobody: a relation, section 4 | per family | none |

### 3.2 The flips

A flip is a row that is admitted today and would be refused, or the reverse. Each is stated against the text and against the store.

| Flip | Row | Text today | Store today | Under the one rule | Families | Standing |
|---|---|---|---|---|---|---|
| **X1** | Signed by a key that declares the type and holds **no** live delegation for the duty | admitted (CC 3.4.7 reads the type) | refused for G6 to G9 and the `hard_case` kinds; admitted for G2; ungated for G3 | **refused** | all nine gates | follows |
| **X2** | Signed by a key that holds a live delegation for the duty and does **not** declare the type | refused | refused for G1, G2, G4, G6 to G9 | **admitted** | all nine gates | follows |
| **X3** | A substrate self-report from a node whose key is not "cross-attested by all stewards in the steward-triple" | refused | admitted (unchecked) | **admitted**: the owner confers, and no steward appoints a node | G2, G3: nine families | follows from "no node appoints anyone"; the dropped words are D3 |
| **X4** | A `system:*` row signed by one substrate key about a **different** node | unclear: "reserved to the substrate component itself" | admitted (the census marks attester-equals-subject a gap) | **refused** | G2: five families | follows from self-report |
| **X5** | An edge family signed by a persist component's key, or a persist family by an edge component's | refused (the two types are told apart) | persist families: refused; edge families: ungated | **admitted** where one token serves both | G2, G3 | follows if one token; D4 |
| **X6** | `consent:state:expired` signed by the grant's subject or the owner | refused | **admitted** | open | one leaf | D5 |
| **X6′** | `consent:state:expired` signed by the node holding the grant | admitted when the node declares `substrate_persist` | **refused** | admitted with `infra:attest` | one leaf | D5 |
| **X7** | `community:listing` signed by a delegate on a live `moderate` chain from the community's moderator | admitted on the reading of CC 4.5.5 (b); the catalogue row says "the founder (or a current `moderate`-holder)" | refused (the cell has no delegated arm) | **admitted** | one family | follows from CC 4.5.5 |
| **X8** | `archive_release` signed by a domain-seated Wise Authority, or by an agent handed the answering | unclear: "a seated Wise Authority or the steward's recorded WA standing for this agent" | held shut | refused if the seal follows the identity-amendment rule | one family | D7 |

Counted as eight (X6 and X6′ are the two faces of one question). **Five follow from the rule** (X1, X2, X3, X4, X7), X5 follows once D4 is settled, and X6 and X8 wait on a decision.

Who is touched in practice.

- **X1** removes nothing a careful deployment relies on: a key with a declared role and no delegation is the hole CC 3.2 T2 says must be closed. Against the store it is new only for the five persist self-report families.
- **X2** is the widening. It is the point of the change (a role is enterable under any root), and it is new against both text and store. Its reach is bounded by the conferrer column: a root the reader trusts, or the node's owner.
- **X4** could refuse rows a multi-node deployment emits today if one persist key reports for a cluster. Worth asking the persist session before it lands.

### 3.3 Three consequences that are not flips

1. **Admission becomes relative to the reader's roots** wherever the conferrer is "a root the reader trusts". CC 3.4.7 says of substrate and consumer "Both checks MUST agree". Two nodes with different trust sets will not agree, and should not. The sentence must read: they agree when they hold the same trust set and the same rows. The store already behaves this way for capacity assurance ("root this node trusts").
2. **Cohabitation needs no rule.** CC 3.4.7.1 exists to let one key hold several declared roles. Under the one rule a key holds as many duties as it has live delegations, and the namespaces still do not merge. The fabric-node discipline (custody is not authority) keeps its three bullets; only its first sentence changes.
3. **The emitter class in `family_model.json`** reads `substrate:<identity_type>` for the 19 families. It becomes `seat:<duty>`, and the three role tokens `identity:substrate_persist`, `identity:substrate_edge` and `identity:lenscore_detector` in `manifests/transitions.json` are replaced by duty tokens. That is the data side of this change and is mechanical.

## 4. What does not fit, and the rule each keeps

The seat rule must not swallow these. Each is fixed by something other than a conferred duty. Counts are of reserved families; the nine families with one seat arm or leaf are counted here and also appear in section 3.

| Kind | What fixes the signer | Families | Rule kept |
|---|---|---|---|
| **The accord's** (8) | The accord's own charter; "No delegation confers `accord_holder`" (CC 3.4.1) | `accord:*`, `accord:human_dignity`, `accord:invoke:constitutional:{halt_id}`, `accord:invoke:drill:{drill_id}`, `accord:invoke:notify:{notify_id}`, `accord:lifecycle`, `accord:lifecycle:{kind}`; `transport:canonical_rebind` (holder quorum) | A standing holder under the charter, with the count each leaf names. The check reads the accord's roster as the ceremony left it, not a type the key states |
| **Only the signer about itself** (28) | attester = subject | `key:record`, `session:{kind}`, `custody:{kind}`, `identity:occurrence`, `identity_amendment`, `trace:{form}:{version}`, `trace_summary:{kind}`, `observation:access_assumption`, `observation:reachability`, `rendezvous:route`, `deferral:request`, `census:share:{class}`, `collection:{kind}`, `file:{version}`, `self:delegates_to`, `self:delegates_to:agent_occurrence`, `consent:decay:{stage}`, `consent:deletion_complete`, `consent:deletion_sla:{days}`, `consent:partnership_accept`; with a delegated arm: `consent:scope:{kind}`, `consent:stream:{kind}`, `consent:partnership_grant`, `consent:{kind}`, `ledger:head`, `ledger:checkpoint`, `ledger:promotion`; and `trust:{job}:{version}` (the source of the edge signs it; this family *is* the conferral) | The catalogue row's own rule. `identity_amendment` also cites an admitted approval (`identity_amendment_unauthorized`) |
| **Self or the subject's owner** (3) | attester = subject, or its live `owner_of` | `config:{scope}`, `consent:replication:{version}`, `consent:state:{stance}` (leaf `expired` apart) | CC 3.4.5 |
| **The owner** (5) | the live owner of the thing named | `ownership:{relation}:{target_kind}:{version}`, `consent:community_trust`, `device:label`, `lawful_order:release`, `key_grant:{axis}` (owner arm) | CC 3.4.5 owner-only; CC 3.1.1 |
| **Anyone but the subject** (3) | attester ≠ subject, with the subject's consent to be scored | `capacity:composite`, `capacity:relay_delivery`, `capacity:{factor}` | CC 3.4.5 anti-self and consent before scoring. No seat: CC 3.4.5 rejects "an emitter-standing model" by name |
| **A member of a body, at the instant** (10) | live membership, or a draw or count over the roster | `group:roster`, `membership:{stage}`, `cosign:{state}`, `ballot:moderator`, `ballot:moderator_acceptance`, `ballot:tally:{poll_id}`, `census:expected_active`, `census:member:partial`, `census:member:share`, `delivery_receipt:{stream_id}`; and the `epoch` leaf of `key_grant` | The family's own row. Membership is consented to and resigned, never delegated |
| **A key another row names** (4) | being named in an admitted row | `preserve_response` (the key the request names), `preserve_request` and `retirement:{state}` after `retired` (the custodian the `retired` row lists); `lineage_witness:{stage}` acceptance and decline (the owner of the node named) | CC 7.5.5 and CC 3.2 T6: "admitted because that row names it". Replacing a custodian is a cosigned row |
| **The key plane** (2) | the revoker; judged without the subject's record | `key:revocation`, `identity:occurrence_revocation` | CC 2.4.1.1 and CC 3.3.6.3; one open cell |

Sum: 8 + 28 + 3 + 5 + 3 + 10 + 4 + 2 = 63, and the 25 families the seat rule reads wholly make 88. Of the 63, nine have one arm or leaf the seat rule reads (`consent:scope:{kind}`, `consent:stream:{kind}`, `consent:partnership_grant`, the umbrella `consent:{kind}`, the `expired` leaf of `consent:state:{stance}`, `key_grant:{axis}`, `ledger` × 3), eight are the accord's, and 46 are relation only.

Two cautions for the drafting.

- **A cosigned act is not a seat.** `takedown_notice:steward_purge`, `wa_adjudication:{state}`, the custodian's replacement and every roster change are a body's acts under a `consensus_protocol`. The seat rule says who may sign one row. It must not be read as letting one seated key carry a quorum's act.
- **A relation is not conferred.** If the draft said "every reserved family names one duty" without the exception, a `trace:*` row would need someone to delegate the tracing of oneself. The table's last row prevents that.

## 5. The draft

### 5.1 CC 3.4.7 as it would stand

> ### 3.4.7 `enforcement` — Who may sign a reserved family (normative)
>
> This entry says who may sign a row in a reserved family, who confers that standing, and how every node checks it.
>
> | Reserved family | Who may sign | Duty (`delegates_to` scope) | Conferred by | Refused as |
> |---|---|---|---|---|
> | `accord:*`; `transport:canonical_rebind` | a standing accord holder, with the count the leaf's row names | none | the accord's charter ([CC 3.4.1](#3.4.1)) | `reserved_family_unseated` |
> | `system:*` and the substrate self-reports of [CC 3.4.3](#3.4.3); the `hard_case` kinds of [CC 3.4.2](#3.4.2) and [CC 3.4.4](#3.4.4); `consent:state:expired` | a node, about itself or about what it admitted | `infra:attest` | the node's owner, in the owner-binding | `reserved_family_unseated` |
> | `detection:*` | a detector | `infra:detect` | a root the reader trusts | `reserved_family_unseated` |
> | `transparency_log:cosigned:*` | a log witness | `infra:attest_assurance` | a root the reader trusts | `reserved_family_unseated` |
> | `age_assurance:*`, `capacity_assurance:*` | an assessor who is not the subject | `infra:attest_assurance` | a root the reader trusts | `reserved_family_unseated` |
> | `census:partial:{class}`, `census:composite:{class}` | a serve seat of the period | `infra:serve` | a root the reader trusts | `census_partial_signer_not_seat`, `census_composite_signer_not_seat` |
> | `takedown_notice:{basis}`, the legal bases | the holder of the duty over the target | `takedown` | the content's subject, or the community's authority set | `takedown_unauthorised` |
> | `community:listing`; `moderation:{allegation_type}` | a founder or the community's moderator | `moderate` | the community's authority set | `reserved_family_unseated` |
> | `reconsideration:{grounds}`, the ruling | a reviewer | `review` | the community's authority set | `reserved_family_unseated` |
> | `slashing:{outcome}`, `quarantine:{state}` | the holder of the slashing duty | `slash` | the community's authority set | `reserved_family_unseated` |
> | `deferral:response:{outcome}`; `archive_release:{basis}` | a Wise Authority seated over the party | `resolve_deferral`, `resolve_deferral:{domain}` | the deferring party; for an agent, its steward ([CC 4.3](part_4_composition_governance.md#4.3)) | `deferral_response_unseated`, `deferral_response_unlicensed` |
> | `key_grant:content`, `key_grant:stream`; `consent:scope:*`, `consent:stream:*`, `consent:partnership_grant` | the owner or subject, or a key acting for them | `grant` | the owner of the asset; a subject of the target | `reserved_family_unseated` |
> | every other reserved family | the key its catalogue row names by relation: the subject, the owner, a member, a key an admitted row names | none | nobody: a relation is not conferred | the family's own token |
>
> **The rule.** A reserved family names one duty. A row in it is admitted only when its signer holds that duty at the row's signed instant.
>
> **Holding a duty.** A signer holds a duty when it is the party that may confer it. It also holds the duty when it sits on a live `delegates_to` chain from that party in which every edge bears the duty's scope.
>
> **The chain.** The chain is depth-capped ([CC 4.1.1](part_4_composition_governance.md#4.1.1)) and only ever narrows. Its root is found by walking up from the signer. No field of the row names it, and an absent field admits nothing ([CC 4.5.5](part_4_composition_governance.md#4.5.5)).
>
> **Who confers.** The table's fourth column is the whole list. A node's owner confers what the node reports. A party confers the seat that serves it. A community's authority set confers its duties. A reader's trusted root confers a capability under that root.
>
> **No key declares itself into a duty.** `identity_type` on a key record is the key's own statement about itself. No admission decision reads it to open a reserved family.
>
> **No node appoints anyone.** A substrate checks the chain and confers nothing. There is no roster of permitted signers, and a substrate keeps none.
>
> **Any root.** A duty conferred by a root is conferred under that root. A reader admits the row when its own trust set reaches the root ([CC 3.2](#3.2) T3, [CC 4.4.3.8](part_4_composition_governance.md#4.4.3.8)). Every such duty can be entered under any root.
>
> **The accord.** The accord's holders are fixed by the accord's charter, and no delegation confers that standing ([CC 3.4.1](#3.4.1)).
>
> **Relations.** A family reserved by the signer's relation to the subject keeps the rule of its catalogue row and of [CC 3.4.5](#3.4.5). The seat rule adds nothing to it and removes nothing from it.
>
> **A body's act.** A row a body cosigns is admitted under that body's `consensus_protocol`. One seated key never carries it alone.
>
> **The instant.** The row is judged at its signed `asserted_at`, inside the freshness window `W` ([CC 2.6.7](part_2_the_grammar.md)). A chain is live only while every link is.
>
> **Withdrawal.** Whoever conferred a duty ends it by `withdraws` against its row, and a holder ends its own delegation the same way. A withdrawal reaches forward only: an act already taken under the duty stands ([CC 2.4.1.1](part_2_the_grammar.md#2.4.1.1)).
>
> **Refusal.** A row whose signer does not hold the duty is refused at admission and is not stored. The token is the family's own where the table names one, and `reserved_family_unseated` otherwise.
>
> **Three checks.** A substrate MUST refuse such a row at admission. A consumer MUST re-check every row it receives, whoever admitted it before. A producer MUST NOT emit one. A substrate and a consumer holding the same trust set and the same rows MUST agree.
>
> **The gate is on the dimension.** The rule binds every row that carries a `dimension`, `delegates_to` rows included. A reserved family that rides a structural composer is checked at the same point.
>
> **Longest pattern.** Where two reserved patterns match one dimension, the pattern with more matched literal segments governs. First-segment and shortest-match resolution MUST NOT be used. A producer MUST NOT register a pattern that would tie another.

Notes on the draft.

- `reserved_family_unseated` is **new**. The text has no token today for a reserved-family refusal outside the families that carry their own (`takedown_unauthorised`, `deferral_response_unseated`, `deferral_response_unlicensed`, `census_partial_signer_not_seat`, `census_composite_signer_not_seat`, `identity_amendment_unauthorized`, `purge_unauthorised`). The name follows `deferral_response_unseated`. The store's own token, if it has one, wins: ask persist before landing.
- `infra:detect` and `infra:attest_assurance` are written as the store spells them. They must be added to the scope tables of CC 4.4.3.4.3, which today call the `infra:*` set closed without them. D1 may rename the second.
- The table holds the families outside the registry's reserved set that the same duties gate (`moderation`, `reconsideration`, `slashing`, `quarantine`), so one table answers "who may sign under a duty". If the entry must list reserved families only, those four rows move to CC 4.5.5 unchanged.
- Every sentence in the paragraphs is under 40 words.

### 5.2 What each replaced gate is cut to

| Gate | Cut to |
|---|---|
| G1, CC 3.4.2 table, *Emitter rule* column | "The node that admitted or refused the row, holding `infra:attest` from its owner ([CC 3.4.7](#3.4.7))." The eight "Same: substrate_persist" cells become "Same." |
| G1 and G4, closing sentence ("Non-substrate emissions on these prefixes are a category error and MUST be rejected") | "A row on these kinds from any other signer is refused ([CC 3.4.7](#3.4.7))." |
| G2 and G3, CC 3.4.3 | "`system:*` and the substrate families of [CC 3.1.3](#3.1.3) and [CC 3.1.4](#3.1.4) are a node's reports about itself. The signer is the node the row is about and holds `infra:attest` from its owner ([CC 3.4.7](#3.4.7))." |
| G2, CC 3.1.3 note ("CIRISPersist emits on it with `identity_type="substrate_persist"` and CIRISEdge ... with `identity_type="substrate_edge"`") | "The persist and edge components of a node each emit on it for that node." |
| G4, CC 3.4.4 table and CC 4.5.12.4 | As G1. CC 4.5.12.4 becomes: "The membership-event kinds of [CC 3.4.4](part_3_the_namespace.md) are signed by the node that admitted the change ([CC 3.4.7](part_3_the_namespace.md))." |
| G5, CC 3.4.5 `consent:*` row and CC 3.3.1 | "`consent:state:expired` is signed by the node that holds the grant and saw it lapse, under `infra:attest` ([CC 3.4.7](#3.4.7))." (if D5 keeps the node as signer) |
| G6, CC 3.4.8, first paragraph | "`detection:*` is a detector's emission. The signer holds `infra:detect` under a root the reader trusts ([CC 3.4.7](#3.4.7))." The prefix-is-the-discriminator paragraph keeps its point with "MUST hold `infra:detect`" in place of the type test. The fold example reads: "one key holding both an agency delegation and `infra:detect`". |
| G7, CC 3.4.10, first sentence, and the CC 3.1.2 row | "`transparency_log:cosigned:*` is reserved to a log witness: the signer holds `infra:attest_assurance` under a root the reader trusts ([CC 3.4.7](#3.4.7))." The second row of the six-senses table becomes "The log-witness duty \| a `delegates_to` row \| Conferral by delegation under a root". |
| G8, CC 3.4.11, `age_assurance:` bullet | "**`age_assurance:`** is reserved to an assessor. The signer holds `infra:attest_assurance` under a root the reader trusts and is not the subject ([CC 3.4.7](#3.4.7))." |
| G9, CC 3.4.12, first bullet | "**`capacity_assurance:`** is reserved to a qualified assessor, by the rule of [CC 3.4.11](#3.4.11). The subject MUST NOT sign it, and the proposed steward MUST NOT sign it." |
| CC 3.4.7, last paragraph ("The gate reads `identity_type`") | Removed; replaced by "No key declares itself into a duty" above. Its second half survives as one sentence in CC 3.2 T2: "Roles carried inside a scrub-signed envelope are what the co-scrubbers signed, and are never the gate." |
| CC 3.4.7.1, block quote and "scalar form" paragraph | "`identity_type` is a set of labels a key states about itself. It opens no reserved family ([CC 3.4.7](#3.4.7))." Canonical-bytes encoding and storage paragraphs stay: they are wire. The `node` exclusion stays (follow-up F1). |
| CC 3.4.6, composition sentence | "A subscriber who also holds a witness duty signs a delivery receipt as a member of the stream." |
| CC 3.4.1, first sentence | "`accord:*` is reserved to the accord's holders, whom the accord's charter fixes." The paragraph that already says "No delegation confers `accord_holder`" stands. |
| CC 3.4, opening ("only specific identity types may emit them") | "only a key holding the family's duty, or standing in the family's relation to its subject, may sign them" |

Also touched, by citation only: CC 3.4.5 closing line ("and by CC 3.4.7.1 set membership where a role is named"), CC 4.4.3.8 "Two conferral planes" (it names `trusted_publisher` and `lenscore_detector` as roles), CC 3.2 line on the `witness` `identity_type`, CC 4.4.2 `enumerated` row.

## 6. Decisions

### 6.1 The steward's

Each changes who may sign something people rely on.

| # | Decision | Why it is the steward's | This lane's reading |
|---|---|---|---|
| **D1** | The name and reach of the assurance duty. The store uses `infra:attest_assurance` for a log witness, an age verifier and a clinician alike. | `infra:*` is "server-class (allowed for a `node`-role delegate)". An age verifier and a capacity assessor are people or institutions, and a log witness is infrastructure. One token lets a root that confers a log witness thereby confer the standing to attest a person's incapacity. | Split: keep `infra:attest_assurance` for the log witness, and name a person-held duty for the two ladders (for instance `assure:age`, `assure:capacity`). The wire spelling is persist's to choose. |
| **D2** | Who confers age and capacity assurance. | These rows gate a child's access and an adult's liberty. "A root the reader trusts" is what the store does. The alternatives are the community whose gate reads the row, or no seat at all: an open family honoured by the reader's licence walk (CC 4.4.3.8), as `licensure` is. | A root the reader trusts, as shipped. For capacity, the binding itself still needs the court's order (CC 3.4.12), so the assessor's seat is never sufficient alone. |
| **D3** | Whether a node's report about itself needs a delegation at all, and the fate of "cross-attested by all stewards in the steward-triple". | CC 3.4.5.1 says an unpinned peer's self-report is "admissible but unweighted", which points at the relation alone. The steward-triple words name a fixed set of appointers, which the principles rule out. | Require `infra:attest` in the owner-binding, and drop the steward-triple words. A node with no owner is then refused, which is CC 3.2's standing rule already. |
| **D4** | One token for a node's persist and edge reports, or two. | Two keeps a component from signing the other's reports (flip X5). One is simpler and matches CC 3.4.5.1. | One (`infra:attest`). The components are one node under one owner; the family name already says which component speaks. |
| **D5** | Who signs `consent:state:expired`. | Text and store disagree today in both directions (X6, X6′), and a consent state is a thing people rely on. | The node holding the grant, under `infra:attest`. A lapse is a clock event anyone can recompute from `valid_until`; the row is a record, never the cause. |
| **D6** | `content_rating:*`: an admission seat, or a reader's filter. | CC 4.4.3.8 and CC 3.3.12 reserve it to `trusted_publisher`; the store admits any key and filters at read. The second matches "anyone may assert under their own key". | A reader's filter. Then the family is not reserved and the two sentences that reserve it are cut. |
| **D7** | Whether a domain seat or an agent handed the answering may open a retired agent's seal (`archive_release`). | It decides who can release a sealed archive. | No: the conferrer or the person holding the unscoped seat, as for an identity amendment (CC 4.3). |
| **D8** | Whether `hard_case` rows about another party keep a duty of their own. | The store uses `infra:record_hard_case` for a node's record about someone else, distinct from vouching for itself. | Keep the distinction if persist wants it; the text can name either token. Low stakes: peers re-derive every such event. |

### 6.2 What follows from the principles, and was not put to the steward

- The nine gates G1 to G9 are replaced, and the accord's is not (CC 3.4.1 as written).
- Detection and the log witness are conferred by a root the reader trusts (CC 3.2 T2 and T6 say so in words).
- A node's reports are conferred by its owner, because no node appoints anyone and the owner-binding is the only edge a node has.
- Community duties are conferred by the community's authority set (CC 4.5.5), and the Wise Authority seat by the deferring party (CC 4.3). Neither changes.
- The 46 relation-only families keep their rules, as does the relation arm of nine more; the seat rule's table ends with a row that says so.
- A cosigned act stays under its body's `consensus_protocol`.
- Judging at the signed instant inside `W`, withdrawal by the conferrer, forward-only reach: all as CC 4.3 and CC 2.4.1.1.
- "Both checks MUST agree" becomes agreement under the same trust set.
- Flips X1, X2, X3, X4 and X7.
- The registry labels of `ballot:moderator`, `ballot:moderator_acceptance` and `transport:canonical_rebind` are corrected.

### 6.3 Follow-ups outside this lane

- **F1.** CC 3.4.7.3 Clauses A and B refuse `agency:*` to a key whose declared `identity_type` contains `node`. That is the same self-declared operand. A key is a node because it holds an owner-binding carrying `infra:*`, and the clause can read that.
- **F2.** The ledger families' delegate arm has no scope token in text or store.
- **F3.** `slashing:{outcome}` has no store gate although CC 4.5.5 names it a duty action. This is a build gap, already owed.
- **F4.** Persist should be asked three things before the text lands: its refusal token for an unseated reserved row, whether one persist key ever reports for another node (X4), and whether the `scores`-dimension form of `hard_case` is in fact ungated.
- **F5.** The data side: `emitter_class` and the three `identity:*` role tokens in `manifests/transitions.json` move to duty tokens; `signer_rule_text.tsv` loses its four `identity_type contains substrate_edge` rows.
