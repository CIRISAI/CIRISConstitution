# Third reading, share 3: summary

Branch rc19 at 87c1730. 425 statements read across 8 rule keys, `family` scope rows included as full members. Compared with manifests/family_model.json, transitions.json, reactions.json, namespace_registry.json, constitution/constants.tsv and the CC 8.10 family cards. 41 findings: 19 major (13 new, 6 known) and 22 minor (20 new, 2 known).

| rule key | statements | major new | major known | minor new | minor known |
|---|---|---|---|---|---|
| signer | 201 | 11 | 2 | 9 | 0 |
| owner_binding | 93 | 1 | 1 | 3 | 0 |
| freshness | 61 | 1 | 1 | 3 | 1 |
| steward | 47 | 0 | 1 | 3 | 1 |
| legal_hold | 16 | 0 | 1 | 1 | 0 |
| other:keep | 4 | 0 | 0 | 0 | 0 |
| other:asymmetry-register | 2 | 0 | 0 | 1 | 0 |
| other:generated-from-data | 1 | 0 | 0 | 0 | 0 |

## Major new findings in full

### signer — CC 3.4.5,4.4.3.4.3.1 (actor)

- A: CC 3.4.5: `consent:partnership_grant` MUST be emitted by a `subject_key_id` of the target Contribution or a `delegates_to` chain rooted at one
- B: CC 4.4.3.4.3.1: **the partner** — the OTHER party (agent occurrence for `grant`, user identity for `accept`); singular, non-empty
- The emitter gate of CC 3.4.5 wants the grant signed by a key in its own subject ids; the member table of CC 4.4.3.4.3.1 puts only the partner there, so the user who signs is never a subject and the gate refuses every grant. CC 4.4.3.5.3 ratified_pair is written to the second shape.

### signer — CC 3.3.5,4.4.3.4.3.1 (term)

- A: CC 3.3.5: subject_key_id: key_id // the subject declaring stance (federation_keys
- B: CC 4.4.3.4.3.1: subject_key_id: <the partner key: agent occurrence (grant) | user identity (accept)>
- Same root as the row above: on the grant half `subject_key_id` is the declaring subject in CC 3.3.5 and the other party in CC 4.4.3.4.3.1. `ratified_pair` (CC 4.4.3.5.3) requires grant.subject_key_id == accept.attesting_key_id, which a row built to CC 3.3.5 never meets.

### signer — CC 3.3.7,6.1.5.3 (actor)

- A: CC 3.3.7: Pinning `self` is what forecloses a third party forging a grant in G's name, since only G signs with G's key as the attested-intent-holder.
- B: CC 6.1.5.3: is the `cohorts` member of the owner's `consent:replication` grant for that node
- CC 3.3.7 admits a replication grant only from the granting node's own key; CC 6.1.5.3 and CC 3.3.6.3 (any live roster key signs every owner act, consent included) make it the owner's grant for the node. The family model (code-v61) and the CC 8.10 card admit both: `replication: owner, self`. A node built to CC 3.3.7 alone refuses the owner-signed grant that sets the per-node allow list.

### signer — CC 3.1.3,3.3.10.1 (data:exception)

- A: CC 3.1.3: **Yes:** the ledger's single owner (the steward-bound identity of its `ledger_id` triple); no delegate writes
- B: data manifests/namespace_registry.json: the ledger's single owner (the steward-bound identity of its ledger_id triple) or a delegate under its declared serialization discipline
- The registry reserved_rule of ledger:head, ledger:checkpoint and ledger:promotion still admits a delegate; CC 3.1.3 and CC 3.3.10.1 clause 3 (a `delegates_to` edge confers no write on a ledger) refuse one. The family model notes "CC delegate arm: GAP". The text is the later and consistent side; the registry rule is stale.

### signer — CC 3.4.11,3.1.2 (data:actor)

- A: CC 3.4.11: Admitted iff the signer acts for the subject (the subject's own occurrence or an admitted occurrence of it).
- B: data manifests/namespace_registry.json: subject-or-steward-signed, not open-sender; no {level} token
- Three answers to who may declare a person's age band: the text says the subject's own occurrences only; the registry gated-stem rule adds the steward; the family model cell (code-v61) and the transitions row say any registered key (`any_registered`, role `registered`). The band sets the protections applied to that person.

### signer — CC 3.1.9.4,4.5.7 (data:actor)

- A: CC 3.1.9.4: Enable/disable is signed by the CC 4.5.5 `moderate`/`takedown` authority and revocable by `withdraws`
- B: data manifests/namespace_registry.json: "prefix": "watchlist:{id}",
- Text: only the moderate or takedown authority of a group turns a watchlist on for it. The registry row (next member `reserved: false`), the family model signer cell `any_registered` (code-v61), the transitions row and the CC 8.10 card (attest: `registered`) let any registered key attest one, and the reactions manifest then auto-fires the matcher. The registry row has `reserved: false` (the CC 3.1.9.4 table has no emitter column, as in C323).

### signer — CC 3.1.9.4 (data:actor)

- A: CC 3.1.9.4: `petition` is the petitioner's own row that opens the ownership-reclaim ceremony
- B: data manifests/family_model.json: seat_role(wa) quorum, re-derived from this node's state
- The model and transitions give one signer rule for every wa_adjudication state (role `wa`); under it the petitioner cannot file the petition leaf that CC 3.1.9.4 and CC 3.2 make the petitioner's own. The transitions row also gives the attest policy as `selfAct` (one voice) where the text says the other three states are quorum-emitted over the full seated roster.

### signer — CC 3.1.5,7.5.5 (data:exception)

- A: CC 3.1.5: **A planned retirement is cancelled by the decider `withdraws`-ing the `decided` row**
- B: data manifests/family_model.json: none (held shut)
- CC 3.1.5 and CC 7.5.5 reading (1) give two withdrawers of the `decided` row (the key named in `decided_by`, and the agent key) while no `frozen` row exists. The retirement:{state} lifecycle cell is "none (held shut)" and transitions.json has an attest transition only, so a system built from the data cannot cancel a planned retirement.

### signer — CC 4.5.9.1,4.5.9.3 (exception)

- A: CC 4.5.9.1: or by a `delegates_to` chain with `scope: [consent_revocation]` — the substrate has no path to mint a location_proof on behalf of a key without an explicit signature
- B: CC 4.5.9.3: - **Opt-in** (CC 4.5.9.1): the claim exists only because the subject signed and emitted it
- CC 4.5.9.1 lets a holder of a `consent_revocation` delegation emit a location proof for the subject; CC 4.5.9.3 says only the subject's signature brings one into being, and CC 2.4.1.1 gives that scope to the rule-3 proxy for withdrawing only. Under the first a proxy (typically the agent holding the data) can state where a person is; under the second it cannot.

### signer — CC 3.1.3,5.3.4 (data:number)

- A: CC 3.1.3: **Yes — the accord holders, cosigned at the charter's M**; never a single holder, never the node itself
- B: data manifests/family_model.json: holder quorum over the carried transport destination
- The text and the family model signer and cosign cells make transport:canonical_rebind a quorum act. manifests/transitions.json and the CC 8.10 card (which CC 8.10 calls this document's statement of the value) give its attest transition role `holder`, policy `selfAct`: one voice. Under the card a single accord holder re-binds a seated serve node's transport. Same fault as C307 for the steward_purge leaf.

### signer — CC 3.1.9.2,2.4.1.1 (data:actor)

- A: CC 3.1.9.2: Subject-scoped quarantine marker: **slash-duty-holder-only** emitter.
- B: data manifests/family_model.json: {attester, subject} (+ producer's owner, consent proxy rule 3, delegate rule 4: outside vocabulary)
- The quarantine:{state} lifecycle cell (code-v61), the transitions row and the CC 8.10 card let the subject of a quarantine marker withdraw it (`withdraw: author, subject`). The text gives the marker plane to the slash-duty holder alone and CC 2.4.1.1 "admits no subject-side removal of an adverse row"; quarantine is not among the families the `adverse` departure reason moves. The same default lets the subject withdraw a wa_adjudication finding and a mesh_config row. Belongs to the withdraw key as well.

### owner_binding — CC 3.2 (data:actor)

- A: CC 3.2: It is cosigned under that affiliation's protocol
- B: data manifests/family_model.json: affiliation named must admit the owner
- For an agent held for an organisation the text requires the owner-binding to carry the affiliation's quorum; the ownership family's cosign cell is `none` (code-v61), its authorize transition is one voice (`selfAct`, role owner), and the placement cell reads the affiliation as only having to admit the owner. departure_reasons.json lists the cell as open. One steward's signature binds the organisation under the data and does not under the text.

### freshness — CC 2.6.7,2.4.1.2.1,4.3 (data:instant)

- A: CC 2.6.7: a licence (`licensure:*`), a deferral response, the epoch-axis membership check — is judged at its signed `asserted_at`
- B: data manifests/family_model.json: receipt future-skew <=5 min, us resolution (check_instant_binding); no W; s3: signed instants .sssZ only (signed_instant_form_violation)
- The freshness cells of licensure:{authority_id}, deferral:response:{outcome} and membership:{stage} are the default row: judged at receipt, no W (source generic). CC 2.6.7, CC 2.4.1.2.1 ("never at receipt") and CC 4.3 judge these rows at the signed instant and bound them by W. A licence issued before its authority's chain link was withdrawn stands under the text and is judged against today's chain under the cell. Bears on C117.

## Known conflicts met again

- C288 (signer, major): Known, still there and marked for Eric: the enumeration of CC 4.2.1 lists lifecycle rows but not `accord:human_dignity`; the model gives every accord:* family the signer `seat_role(holder)`. C051 is the same enumeration against the CC 4.2.6 roster-change objects.
- C307 (signer, major): Known (to fix in the data) and still there: transitions.json gives takedown_notice:{basis} one attest transition, role `takedown`, policy selfAct, for every basis; no cosigned policy for the steward_purge leaf.
- C208 (owner_binding, major): Known and held (ask persist), still there: CC 3.2 and the definition in CC 3.4.7.3 read the steward from the one live owner-binding and nothing else; the Cardinality paragraph of CC 3.4.7.3 keeps a second, occurrence anchor, under which an agent may act through a node of a person who holds no owner-binding on it. C209 (`steward_of ==` in the fenced line) goes with it.
- C117 (freshness, major): Known, open and still there: CC 2.6.7 refuses every chain-judged row older than 72 h; CC 3.3.6.3 and CC 3.3.4 ("A signature by a member still standing counts at any age") apply W only to a signer that has lost standing at receipt. The model cells for consent:state, consent:replication, key_grant and ownership follow the second ("W on the owner's standing").
- C118 (freshness, minor): Known (no conflict on reading): the session claim is the stated exception to the every-consumer future bound. Still worded so that its parenthesis reads as general. The session:{kind} freshness cell is the default "judged at receipt", which does not carry the exception.
- C197 (steward, major): Known and held, still there: one paragraph of CC 5.3.4 puts every charter or roster change at unanimity; the same section, CC 3.2 T4a/T6 and CC 4.2.6 put charter re-scrubs and roster changes at a strict majority. constants.tsv `charter_change_threshold` records the strict majority (settled_from C197), so the data now disagrees with the unanimity sentence.
- C151 (steward, minor): Known (proposed, not applied): item 4 of the anonymous tier defines the relay set for a period from nodes owner-bound under a root in the genesis charter set, while the default-behaviour text speaks of every announced node relaying with no cap. Still as it was.
- C312 (legal_hold, major): Known and marked for Eric, still there: a record under a legal hold that is also hit by an immediate-removal basis or a root's purge is pinned by one sentence and destroyed by the other; neither names the other.

## Conflict-table rows checked and found fixed in the text (not reported in the TSV)

- C309: CC 4.5.13 now scopes the first-held clock to "every window of this section's table" and adds "A window another section defines runs from the instant that section names".
- C107: CC 3.1.3.2 now reads "The owner-binding is written at `self` scope and only its audience reads it."
- C166: CC 2.6.8 now has the unowned node send a device-join request; the pending identity_occurrence wording is gone.
- C244: CC 7.5.7 now reads "withdrawn, superseded or lapsed before the new owner binds".
- C196: CC 5.3.4 "What a consumer pins" no longer calls the id an anchor.

## How the reading was done, and its limits

- Each statement was read from its inventory gist and its entry phrase; the section text was then opened for every pair that looked as if it could differ, and every quote in the TSV was checked by script to be verbatim in the text or the data file named.
- signer: the 187 family statements were compared with one another by family, then against the signer cell, the transitions row and the CC 8.10 card of each family. Most data findings share one cause: a cell sourced `code-v61` records that the shipped store enforces no signer rule (`any_registered`) where the text states one, or a transitions row gives `selfAct` where the text gives a quorum.
- owner_binding and steward: the long runs in CC 3.4.12, CC 3.2 and CC 5.3.4 were compared statement against statement from the entry phrases; the fenced predicate of CC 3.4.12 was not re-derived line by line against its prose (C012, C013, C019 already cover it).
- other:keep (4 statements) and other:generated-from-data (1 statement): no finding. manifests/signed_object.cddl was not diffed against the CC 2.6.1.7 table; the build is said to do that.
- No key was left unfinished.

## Points a settler may want first

- The partnership pair (two rows) is one fault: CC 3.3.5 and CC 3.4.5 put the declaring subject in `subject_key_id`, CC 4.4.3.4.3.1 and CC 4.4.3.5.3 put the partner there.
- Three transitions rows give one voice to an act the text makes a quorum's: takedown_notice steward_purge (C307), transport:canonical_rebind, wa_adjudication.
- The default withdraw roles `author, subject` reach families whose rows are adverse to their subject (quarantine, wa_adjudication).
- The freshness default (judged at receipt, no W) sits on licensure, deferral:response and membership, which CC 2.6.7 names as judged at the signed instant; this is the data side of C117.
