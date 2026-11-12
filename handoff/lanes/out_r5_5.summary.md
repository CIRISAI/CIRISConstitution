# Fifth reading, share 5: summary

Head 1ee1bcf, branch rc19. Seven rule keys, 425 inventory statements. Output: `out_r5_5.tsv` beside this file (39 findings).

## The three numbers

- New major findings, text against text: **3**
- New major findings, text against data: **2**
- Statements opened in the text: **424 of 425**; read by gist only: **1** (CC 2.4.1.1, "rosters list members by key_id and roster-removal rows are addressed by key_id": no entry phrase, and I did not find the sentence in the section; the same fact is stated in CC 5.3.2.3, which I read).

For CC 3.1.7 (family registration) the entry phrases resolved to the wrong paragraphs, so I read the whole section directly.

## Per rule key

| rule key | statements | findings | major new | major known | minor new | minor known |
|---|---|---|---|---|---|---|
| audience | 178 | 13 | 3 (2 text, 1 data) | 6 (1 text, 5 data) | 3 | 1 |
| supersede | 100 | 16 | 2 (1 text, 1 data) | 5 (1 text, 4 data) | 8 (6 text, 2 data) | 1 |
| agent_identity | 65 | 8 | 0 | 3 (2 text, 1 data) | 4 | 1 |
| placement | 52 | 1 | 0 | 0 | 1 | 0 |
| other:family-registration | 19 | 0 | 0 | 0 | 0 | 0 |
| projection | 10 | 1 | 0 | 1 (data) | 0 | 0 |
| other:cell-containment | 1 | 0 | 0 | 0 | 0 | 0 |
| total | 425 | 39 | 5 | 15 | 16 | 3 |

## Major new findings in full

**1. A non-public licence is re-emitted by naming its readers as subjects (text against text; CC 2.4.1.2.1 against CC 2.1).**
CC 2.4.1.2.1: "They are re-emitted as new rows, signed and cosigned again, with the readers in `subject_key_ids`." CC 2.1: "At a targeted scope the keys a row lists in `subject_key_ids` are keys within the row's audience and no others." The readers are outside the roster by the section's own words ("never by widening the roster"). CC 2.1 refuses a targeted row that names a key outside its audience (`subject_outside_audience`), lists the families that deliver outside a cohort (a proposal's invitee, a key grant's recipient, the owner's node) without licensure, and makes `subject_key_ids` the party the row is about, with a subject's standing to retract. One implementer refuses the re-emitted licence; the other delivers it and gives each reader a subject's standing over it. CC 2.1 and CC 5.2 are the home of the audience rule.

**2. Who reads a public room's content (text against text; CC 4.4.3.2.1 against CC 3.2 and the CC 5.2 table).**
CC 4.4.3.2.1 readers cell: "anyone who joins (open admission); replicated to the roster's nodes". CC 3.2: "a non-member reads the listing and may read the content by asking a member's node". The lead sentence of CC 5.2 ("served to a node in its audience and to no other") reads with the first, its own table row with the second. A node built from the tier table refuses a non-member's read; one built from CC 3.2 serves it. C292 settled a different pair (crypto tier against audience). CC 3.2 is the home of the public room.

**3. Who may sign and amend a room's listing (text against text; CC 3.1.1 against CC 3.2 and CC 2.4.1).**
CC 3.1.1 emitter cell: "signed by the founder (or a current `moderate`-holder) of the community it names; one live row per community". CC 3.2: "The listing is the founder's own row". A rename is a `supersedes`, which CC 2.4.1 gives to the same attester, so under CC 3.1.1 a moderator's rename of the founder's row is either refused or a second live row. The data takes CC 3.1.1 for attest (founder, moderate) and CC 2.4.1 for supersede (author only).

**4. The roster row of a public group reaches everyone (text against data; CC 3.2 against `manifests/family_model.json`).**
CC 3.2: "there is no member-level listing, and a roster is never enumerable outside its cohort, a public room's included". `group:roster` replication.audience note: "may_receive_group_plane (public group: everyone; private: members' nodes, live invitees, named member)". The same fault as C463, on the sibling family that C463 does not name, and on the row that is the roster.

**5. A charter's signer alone replaces the witness directory (text against data; CC 2.1 and CC 3.2 T6 against `manifests/transitions.json`).**
CC 2.1: "A change is a charter re-scrub, witnessed by the directory before it." The supersede transition of `trust:{job}:{version}` has roles author, policy selfAct and an empty guard; the one charter guard (witness independence) sits on authorize only. Nothing in the data asks the prior directory's witness, nor the `lineage_witness` acceptance CC 3.2 requires of a newly listed key.

## Known conflicts still present

Text: C240 (group existence and size observable, proposed and not applied), C290 (charter-appointed Wise Authorities against a seat conferred by the deferring party), C474 (`consent:partnered`, now in CC 1.13.2 only), C333 (same-attester supersession; minor), C274 (the phrase "provenance-visible discovery" is still in CC 3.2; minor), C329 (CC 3.3.6 still says an agent occurrence speaks as the identity; minor), C332 (guardian supersession, open with the steward, reached independently).

Data: C331, C383 (with C465), C384, C463, C464, C469, C470, C471, C386, C412, and C398 in a changed form (the over-broad licence guard on `deferral:response` was removed and nothing replaced it, so neither refusal of CC 4.3 is in the transition).

## Known conflicts I found repaired

C291 and C311 (the CC 5.2 enforcement block now reads through the allow list and occurrences), C295 (CC 3.3.6.2 lists the four things that cross before Rooted), C380 (CC 4.4.3.2.7 no re-emit), C385 and C420 (CC 3.3.9 uses the monotonic merge), C413 and C427 (CC 4.4.3.5.5 boundary fold), C455 and C466 in the text (a route row supersedes nothing; the transition remains, reported as a minor), C467 and C468 (recant is now on goal and need), C473 (deferral re-routing), C072.

## Notes on judgement

- Placement cells with source `gap` ("signer-chosen, no per-family constraint") were not reported against text that fixes a scope, following the table's own reading of C461 and C462.
- Five of the minor new findings repeat minors of the fourth reading that were not entered in the table (only its majors were): the two in agent_identity marked so, and in supersede the `org_membership` merge, `rotation_chain`, and the partnership fold.
- Keys not finished: none.
