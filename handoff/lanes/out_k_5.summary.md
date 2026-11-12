# Lane K, share 5: summary

| rule key | statements read | major new | major known | minor new | minor known |
|---|---|---|---|---|---|
| trust_fold | 105 | 2 | 0 | 2 | 3 |
| owner_binding | 81 | 0 | 1 | 1 | 1 |
| withdraw | 60 | 3 | 1 | 2 | 0 |
| registration | 48 | 2 | 1 | 0 | 1 |
| freshness | 44 | 1 | 1 | 1 | 3 |
| trace | 26 | 0 | 0 | 1 | 0 |
| other:family-registration | 19 | 1 | 0 | 0 | 0 |
| standing | 9 | 0 | 0 | 1 | 0 |
| settlement | 7 | 0 | 0 | 0 | 0 |
| total | 399 | 9 | 4 | 8 | 8 |

## Major new findings

**trust_fold** (3.2,4.4.3.8,4.2.1; actor)

- CC 3.2: "A portable root minted by any trio enters via delegation. The shipped default enters via ceremony."
- CC 4.4.3.8: "It is minted by the [CC 4.2.1](#4.2.1) conferral ceremony and owes nothing to any prior root."
- Who mints a portable root and on which plane: CC 3.2 T2 says any trio, entering by delegation; CC 4.4.3.8 and CC 4.2.1 say the conferral ceremony, a co-scrub by a strict majority of the standing accord roster. CC 3.2 T2 itself says root identity is conferred by ceremony, so the rest of the text supports side B.

**trust_fold** (3.2,4.4.3.8,5.3.4; scope)

- CC 3.2: "Consumers pin `community_key_id: ciris-canonical` and resolve the live member set via `resolve_community`"
- CC 4.4.3.8: "That names the founders of `ciris-canonical`, who are the three accord holders `A1`, `B1`, `C1`"
- Whose signatures the shipped default pin trusts: CC 3.2 (and CC 5.3.4) resolve the live member set, which by CC 3.2 includes serve nodes seated as role member; CC 4.4.3.8 says the pin names the founders and never a serving install's key. The same paragraph also writes the pin as a policy value where CC 4.4.3.8 says the set is the reader's own acceptance edges and nothing else. CC 3.2 "Infrastructure does not vote" supports the founders reading.

**withdraw** (2.4.1.1,3.2; condition)

- CC 2.4.1.1: "A node MUST admit a `withdraws` against a target row `T` when one line of this table holds"
- CC 3.2: "A node MUST reject a rule-2 or rule-4 `withdraws` against a live owner-binding unless it carries a `wa_adjudication_ref`."
- The home table gives rule 2 one condition (the kept list) and says a node MUST admit when a line holds. CC 3.2 adds a second condition for one family. Built from CC 2.4.1.1 alone, a node admits a compromised node key's withdrawal of its own owner. CC 3.2 is the specific rule; the home neither states nor cites the gate.

**withdraw** (2.4.1.1,3.3.14; condition)

- CC 2.4.1.1: "Its later `withdraws` against any row carrying that hash in `subject_key_ids` is admitted under rule 3."
- CC 3.3.14: "The proxy attaches only after that out-of-band establishment, reaches no row on the kept list of CC 2.4.1.1, and is suspended while two bindings for the same person compete."
- CC 2.4.1.1 lets the data-holding agent set the proxy up by its own delegates_to and admits its later withdrawal with no further test. CC 3.3.14 adds two conditions: identity established out of band first, and suspension while bindings compete. A withdrawal is admitted on one reading and refused on the other. Beside C276, which covers the binding and not the proxy's conditions.

**withdraw** (3.2; manifests/transitions.json; data:condition)

- CC 3.2: "A node MUST reject a rule-2 or rule-4 `withdraws` against a live owner-binding unless it carries a `wa_adjudication_ref`."
- manifests/transitions.json (ownership:{relation}:{target_kind}:{version}, withdraw): "when(verb=withdraw,has=wa_adjudication_ref) one wa_adjudication:{state}@admitted[id=ref:wa_adjudication_ref] else refuse"
- The data puts the recovery guard on the ownership:* mirror row and fires it only when the reference is present; the owner-binding itself (self:delegates_to) has one transition, authorize, and no withdraw, supersede or lapse. The text's gate (a subject or delegate withdrawal with no reference is refused) and the owner's own withdrawal are not in the data.

**registration** (3.4.7.3,3.4.7.1,4.5.8.4; exception)

- CC 3.4.7.3: "A `federation_keys` key whose `identity_type` set contains `node` MUST NOT also contain `agent` or `user`."
- CC 4.5.8.4: "Forbid any cohabitation at the wire layer (substrate enforces gates by membership; constitutional/substrate cohabitation discipline is consumer/operator policy per CC 4.5.8.1)"
- CC 4.5.8.4 lists, under what the role-set rule does not do, forbidding any cohabitation, and leaves the discipline to operator policy. CC 3.4.7.1 and CC 3.4.7.3 Clause A forbid one pair with MUST NOT. A key record carrying node with agent is admitted on one reading and refused on the other. Clause A is the later and specific rule, and CC 3.2 leans on it.

**registration** (2.6.1.7,2.6.8; number)

- CC 2.6.1.7: "the fingerprint the first ten lowercase base32 characters of sha256(ed25519 public key)"
- CC 2.6.8: "SHOULD raise the fingerprint length (16 characters, 80 bits, moves the bound to 2⁴⁰)"
- The format is stated as ten characters, normative, in CC 2.6.8 and in the signed-object table; the same paragraph of CC 2.6.8 tells a large deployment to use sixteen. A verifier that recomputes ten characters refuses a sixteen-character id. Nothing says how a reader learns which length a label uses.

**freshness** (3.1.3.2,4.5.13,2.6.7; instant)

- CC 3.1.3.2: "Expiry is judged on the instants the parties signed, never on a receiver's clock."
- CC 4.5.13: "Every window of this table is measured by each node from the instant it first held the proposal, never from a signed instant of the proposer or of a cosigner."
- Opposite clocks for a membership change. CC 3.1.3.2 concludes that every node gives the same verdict for the same rows; CC 4.5.13 (whose table has the invite and removal windows) concludes that two nodes may close a window at different moments, and adds that the first-held instant is what every window in this document runs from. That last sentence also contradicts CC 2.6.7 (W runs from the signed asserted_at) and CC 3.2 T4a (the attach window runs from a cosignature's signed_at). If the proposal's signed expiry and the policy window are two things, neither section says so.

**other:family-registration** (3.1.7; condition)

- CC 3.1.7: "A substrate observing emission on a family with no registry row (provisional or ratified) MUST surface it as a conformance failure (`namespace_family_unregistered`), never admit-and-wait."
- CC 3.1.7: "An unregistered family has no owning component, no polarity and no reserved rule, so a consumer resolving its authority falls through to the producer-steward default."
- What a node does with a row on a family that has no registry row. R2 says it never admits under a defaulted authority; R1 says its authority resolves to the producer-steward default, and "Where the fallback remains" keeps that default for an open-vocabulary space it does not define (an unrowed family, or the open leaves of a registered one). R1 also calls an ungated family described only in CC 3.3 conformant though unregistered. The row is admitted on one reading and refused on the other. The closed-stem passages support refusal.

## Keys not finished

None left unread. Read more lightly than the rest: the adult-incapacity statements under owner_binding (CC 3.4.12, about 35 statements; I relied on C011 to C020 already covering that section), and the data comparison, which I made only against transitions.json, constants.tsv and namespace_registry.json. I did not compare against reactions.json, family_model.json cells or signed_object.cddl beyond spot checks.

## Method notes

Statements counted are the non-family rows of each key; family rows were read as context only. About 45 statements had no entry phrase that still matches the text; I found those by gist. Checked and found consistent with the text: the kept list against the withdraw roles in transitions.json (author only for every kept family; no withdraw transition for key:revocation, key_grant or occurrence revocation), W = 259,200 s, the nine owning components. Known conflicts I looked for and found already repaired in the text, so not reported: C166, C244, C252, C253, C265, C269, C281. Settlement: 7 statements, no finding.
