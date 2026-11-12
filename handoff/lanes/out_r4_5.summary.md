# Fourth reading, share 5: summary

Output: `out_r4_5.tsv` beside this file, 38 findings. Head read: rc19 at 05cbcc8. Known table read: C001 to C435.

## The three numbers

- New major findings, text against text: **5**
- New major findings, text against data: **11**
- Statements opened in the text: **419** of 425. Read by gist only, or with the paragraph only partly read: **6**

## Per rule key

| rule key | statements | findings | major new | minor new | major known | minor known |
|---|---|---|---|---|---|---|
| audience | 178 | 14 | 7 (2 text, 5 data) | 3 | 3 | 1 |
| supersede | 100 | 13 | 7 (1 text, 6 data) | 3 | 2 | 1 |
| agent_identity | 65 | 5 | 2 (2 text) | 2 | 1 | 0 |
| placement | 52 | 3 | 0 | 3 | 0 | 0 |
| other:family-registration | 19 | 3 | 0 | 2 | 1 | 0 |
| projection | 10 | 0 | 0 | 0 | 0 | 0 |
| other:cell-containment | 1 | 0 | 0 | 0 | 0 | 0 |
| total | 425 | 38 | 16 | 13 | 7 | 2 |

Known findings reported: C240, C383, C384, C274 (audience); C332, C333, C386 (supersede); C290 (agent_identity); C319 (family-registration). C383, C384, C386, C333, C290 and C240 are still present. C332 and C319 are open with the steward and are listed because this reading reached them independently.

Known conflicts in this share that I found already repaired in the text or data, and so did not report: C291 (CC 5.2 enforcement block now names the allow list), C295 (CC 3.3.6.2), C380 (CC 4.4.3.2.7 first bullet), C382 (the listing row of CC 3.1.1), C385 (CC 3.3.9 now defers to the merge of CC 5.3.2.3), C299 (the tripwire wording of CC 1.13.3.4 and CC 3.1.3.4), and the attest half of C369 and C374 (the supersede half is new, below).

## Major new findings, text against text

1. **audience: an infrastructure community's holding claims.** CC 3.1.3.3 rule (1) places a custody report at federation scope "for Commons and `public` content" only, and "refuses a report whose scope is not its content's". CC 5.2 and CC 1.13.3.4 put an authorized infrastructure community's holding claims at federation scope together with the public room's. A reader of rule (1) refuses the report that a reader of CC 5.2 emits. CC 4.4.3.2.1 supports CC 5.2.

2. **audience: a server node with no `cohorts` member.** CC 6.1.5.3 says a server "has an allow list of only the cohorts it was set up to serve". The class default of CC 3.3.7, repeated later in CC 6.1.5.3, withholds only self and family content, so every community and affiliation of the owner replicates onto the server. The two give different holdings. Near C381, which asks about agents; not the same point.

3. **supersede: dropping a family member by a supersedes.** CC 3.3.4 item 1: "A `family` Contribution that supersedes the current one may change metadata or drop members and never adds one." CC 4.4.3.4.2 and CC 4.4.3.2.3: a membership change, removal included, "is never a single-signer `supersedes` Contribution"; the same item of CC 3.3.4 then gives removal as a cosigned `membership:removal` or a resignation. A reader of the first sentence lets one signer remove a member. The rest of the document, and the model cell ("typed record supersede only"), support CC 4.4.3.4.2.

4. **agent_identity: where a lapsed Wise Authority's deferral goes.** CC 4.3 rule 1 and the `deferral:request` row of CC 3.1.9.3: "on window expiry it re-routes to the live quorum". CC 4.3 seat rule, Withdrawal: it "re-routes under rule 1 to the party's other live seats and, with none, to the conferrer". The seat rule also says there is no roster of Wise Authorities. A reader of rule 1 routes an agent's deferral to a body its steward never seated; a reader of the seat rule returns it to the steward.

5. **agent_identity: `consent:partnered` is not a registered leaf.** CC 1.13.2 ("`consent:partnered` is theirs to revoke"), CC 4.4.3.4.3, CC 2.1, CC 4.5.1.1 and CC 5.3.2.2 name a dimension `consent:partnered` or `consent:partnered:{user_key}`. The closed leaf set of CC 3.3.1 has no such leaf (the pair is `consent:partnership_grant` and `consent:partnership_accept`; `partnered` is a kind of `consent:stream`), and "a leaf with no named emitter class is unregistered, and a consumer MUST reject it". A node following CC 5.3.2.2 emits a row that a node following CC 3.3.1 rejects, and the act by which a person ends an agent's partnership has two names.

## Major new findings, text against data

6. **audience: `session:{kind}`.** CC 3.1.3.1 sets the projection ceiling at `Cohort`, "normative — not a default". The model's placement cell lets the signer choose the commons, where the replication cell serves the row to everyone. The cell is marked a gap.

7. **audience: `deferral:request`.** CC 3.1.9.3: the audience is the cell, "never a federation broadcast". The placement cell admits commons, and the CC 8.10 card shows attest widening by scope.

8. **audience: `membership:{stage}` in a public room.** CC 3.2 and the CC 5.2 table: a roster is never enumerable outside its cohort, "a public room's included". The replication cell's audience is `may_receive_group_plane`, noted "public group: everyone".

9. **audience: `identity:occurrence`.** CC 5.4.6 withholds an occurrence row whose attester's owner-binding is not announced, and holds an unannounced identity's occurrence with the owner's nodes and the contact alone. The replication cell's audience is "key-plane reach", noted "the carrier: everyone".

10. **audience: `census:member:share`.** CC 3.1.3: "reach is the named tally member only". The replication cell keeps the default audience (cohort plus subjects) under an `addressed` placement. The same fault as C383 on the sibling family.

11. **supersede: `rendezvous:route`.** CC 3.1.4 gives each period a fresh rendezvous key that is attester and subject of its row, and says "each period's row `supersedes` the previous one in the same lineage". The transition lets only the prior row's author supersede (as the CC 2.4.1 gloss does), so a kernel run from the data refuses every period's successor. The supersedes link also ties one period's key to the next.

12. **supersede: `goal:{scale}` has no recant.** CC 3.1.9.7: a Goal is "disowned by `recants`". The verb cell (source cc-table) and the transitions carry attest, supersede and withdraw only; the cell's own code reading records "+recant".

13. **supersede: `need:{domain}:{kind}` has no recant.** CC 3.1.9.3: "`recants` if misstated". Same fault as 12.

14. **supersede: a group's Goal.** CC 3.1.9.7: a group's "`supersedes`, `withdraws` and `recants` stand only when they too are cosigned under the same protocol". The model has cosign_rule none and one-signer supersede and withdraw for `goal:{scale}`, and likewise for approach, method and progress_measure.

15. **supersede: `census:composite:{class}`.** CC 3.1.3 refuses "a second composite for the class and period, from any seat". The transitions and the CC 8.10 card give the signing seat a supersede and a withdraw. `census:partial:{class}` carries the same supersede against "one per (seat, class, period)".

16. **supersede: `transport:canonical_rebind`.** CC 3.1.3: "never a single holder". The attest transition is now cosigned, but the supersede transition beside it is still author and selfAct, in the data and on the CC 8.10 card.

## Notes for whoever verifies

- Findings 6, 7 and the three minor placement findings rest on model cells whose source is `gap` ("signer-chosen, no per-family constraint"). They are differences between a value the text states and a cell that states none, not two stated values. I have marked 6 and 7 major because a kernel executing the cell would serve the row to everyone.
- Finding 9 depends on what "key-plane reach" means in the store. If the key plane already applies the serve-side dependency closure of CC 5.4.6, the cell's note ("the carrier: everyone") is the only fault and the finding is minor.
- Finding 2 is medium confidence: "the cohorts it was set up to serve" may be meant as a description of the `cohorts` member and not of the default when the member is absent.
- Data-side quotes for transitions are descriptions of the cell (roles, policy), not verbatim JSON. Text-side quotes were checked verbatim against the Parts by script.

## Keys not finished

None. Six statements were read by gist only or with their paragraph only partly read:

- audience: CC 2.4.1.1 (rosters and roster-removal rows addressed by key_id), CC 2.6.1.8 (a disclosure set is bytes, fetched under the audience's consent edge), CC 3.2 (the `mesh_config` restriction on what subscribers carry: read where CC 3.2 restates it, not at its home)
- supersede: CC 2.1 (a change to the witness directory is a charter re-scrub), CC 2.4.1.1 (`revoked_after` only lowers), CC 5.3.3.2.3 (a receiver keeps the two newest binding epochs)

The projection and cell-containment keys were read in full and compared with the model's projection cells; nothing to report.
