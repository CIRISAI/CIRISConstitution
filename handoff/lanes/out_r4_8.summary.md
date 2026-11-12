# Fourth reading, share 8: summary

Share: 8 rule keys, 425 inventory statements (family scope included).

## The three numbers

- New major findings, text against text: **1**
- New major findings, text against data: **0**
- Statements opened in the text: **422**; read by gist only: **3**

The three read by gist only are in CC 5.3.3.2.3 (rule key `admission_order` ×1, `conformance` ×2): the order in which a receiver accepts a stream binding, the closed list of `av_binding_*` refusal tokens, and the known-answer vectors (publisher `node-kat-a`). The inventory rows carry no entry phrase and the section's long paragraph was opened only at the relay and receiver steps.

How the rest was opened: 372 statements were found by their entry phrase and read in their paragraph; 41 had no entry phrase and were found by matching the gist against the lines of their section; 12 were found by hand search (nine of them read, three above not).

## Per rule key

| rule key | statements | findings | major new | major known | minor new | minor known |
|---|---|---|---|---|---|---|
| admission_order | 141 | 6 | 1 | 0 | 5 | 0 |
| conformance | 113 | 3 | 0 | 0 | 3 | 0 |
| amendment | 79 | 8 | 0 | 2 | 5 | 1 |
| licensure | 54 | 2 | 0 | 0 | 2 | 0 |
| endpoint | 30 | 1 | 0 | 0 | 1 | 0 |
| other:client | 6 | 0 | 0 | 0 | 0 | 0 |
| other:public-transparency | 1 | 0 | 0 | 0 | 0 | 0 |
| other:local-act | 1 | 0 | 0 | 0 | 0 | 0 |
| **total** | **425** | **20** | **1** | **2** | **16** | **1** |

Of the 16 new minor findings, 4 are text against data (`data:` kinds) and 12 are text against text.

## The major new finding, in full

**admission_order — CC 3.1.3 against CC 4.5.13 (condition).**
CC 3.1.3, the `ballot:moderator` row: "a ballot naming an unknown election id or a non-member is refused".
CC 4.5.13: "A node stores every ballot and acceptance it receives rather than refusing a late one."

An election is named by what a node holds: its id is the digest of the community id and the last seating row. A node that has not yet received that seating row cannot derive the id of the election a ballot names. Under CC 3.1.3 it refuses the ballot, and the row does not say the refusal is retryable. Under CC 4.5.13 it stores it. CC 4.5.13 is the home and states the principle the refusal breaks: "The seat is a function of the rows held and never of their arrival". A node built from CC 3.1.3 alone can end up without ballots that its peers hold, and then cannot admit the winner's acceptance, which is admitted only when the node holds the bound ballot set. The CC 8.10 card for `ballot:moderator` guards the ranks only (each a member) and carries no guard on the election id, so the data follows CC 4.5.13. Confidence: medium. A reader who takes "refused" here as "refused for now" resolves it; the text does not say so, and the neighbouring membership refusals in CC 3.1.3.2 mark each retryable refusal by name.

## Major findings already known

- **C319** (open with the steward), amendment: reported because two further statements take opposite sides. CC 1.2 "anyone may publish a rule set and admit a new prefix" against CC 4.5.1 "Rule-layer changes (new prefixes, …) route through" the five steps. CC 5.3.2.4.4 ("new families … ship continuously") sits with CC 1.2; CC 3.1.7 and CC 4.5.6 sit with registration first.
- **C157**, amendment: still present. The scale gate is "measured by the census", and CC 6.1.9 defines no agent count, 24-hour window or production class.

## Known conflicts checked and found repaired in the text or data

These were in the table as still present and are no longer at fault, so they are not in the TSV: C092 (count of enforced-admission kinds, CC 4.4.3.4.3), C148 ("MAY NOT", CC 5.4.6), C313 (Annex D-1 trigger), C368 (CC 4.5.9.1 first sentence), C402 (election id in CC 3.1.3), C409 and C418 (geographic constraint finer than resolution 7), C417 (hold on a signature shortfall in the CC 4.4.3.2.3 gate), C040 at CC 5.3.4 ("three named holders"). C398 is repaired on the card by removing the licence guard altogether; the residue is reported as a minor `data:condition` row.

## Looked at and not reported

- CC 7.3.3 Stewardship Tier arithmetic (bands, the worked examples, the RM ≥ 4 trigger) is consistent with itself and with Annex D as it now reads.
- CC 2.4 "admitted only once its signer's key-claim row is held" against the digest-only revocation of CC 2.4.1.1 and the `hard_case:admin_action` gate of CC 3.1.9.4: different keys (the subject's, the delegation's), no conflict.
- CC 3.2 T1 and CC 4.4.3.8 on the federation floor ("live" against "valid" external root): same rule.
- CC 5.3.6.1 `X-RateLimit-Reset` "(seconds-until-reset epoch)" is ambiguous within one phrase (a count of seconds or an epoch instant); there is no second statement to set against it, so it is noted here only.
- CC 8.8.2 Annex B item 11 gives the Wise Authority charter its own amendment rule (two thirds of the WA plus 45 days of comment); Part 8 is outside this share's inventory and it was not compared with CC 4.5.1.

## Keys not finished

None. All eight keys were read through.
