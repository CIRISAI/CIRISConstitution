# Fifth reading, share 9: summary

Head 1ee1bcf, branch rc19. Seven rule keys, 425 statements, 25 findings.

## The three numbers

- New major findings, text against text: **3**
- New major findings, text against data: **0**
- Statements opened in the text: **420**; read by gist only: **5**

## Per rule key

| rule key | statements | findings | major new | minor new | major known | minor known |
|---|---|---|---|---|---|---|
| trust_fold | 137 | 11 | 2 | 6 | 2 (C499, C507) | 1 (C001) |
| principle | 121 | 1 | 0 | 1 | 0 | 0 |
| signature | 75 | 6 | 0 | 2 | 4 (C442, C287, C055, C307) | 0 |
| minor_floor | 52 | 5 | 1 | 0 | 3 (C002, C316, C422) | 1 (C423) |
| announce | 37 | 2 | 0 | 0 | 1 (C132) | 1 (C142) |
| other:session-claim | 2 | 0 | 0 | 0 | 0 | 0 |
| other:dsar-export | 1 | 0 | 0 | 0 | 0 | 0 |
| **total** | **425** | **25** | **3** | **9** | **10** | **3** |

The trust_fold row for the halt's reach instant was found while reading the `principle` key
(CC 4.2) and is filed under trust_fold, where the CC 3.2 statement sits.

## Major new findings in full

**1. The instant a halt's reach is judged at (trust_fold; CC 3.2 against CC 4.2.1).**
CC 3.2 T8, in the inputs of the standing verdict: "the halt latch **as it reaches this node**
(CC 4.2.1: a live accord edge at the halt's `asserted_at`)". CC 4.2.1: "A halt is active at a
node from the instant the node's store admits the row and latches. The signer-chosen
`asserted_at` plays no part". A node whose owner cut the edge after the halt was signed and
before it arrived is bound under the T8 wording and free under CC 4.2.1; a sealed halt signed
long before an edge was written goes the other way. C033 records this wording as removed from
CC 4.2.1; it survives in CC 3.2. CC 4.2.1, 4.2.1.1 and 4.4.3.8 support the latch. Confidence
high.

**2. Whether a directory collapse detaches an attached node (trust_fold; CC 3.2 against
itself).** T8 lists among the `NotRooted` cases "the head de-witnessed (its counted witnesses
revoked before their `signed_at`, or the directory collapsed to non-independent keys)", and as
a transition "a new witnessed head that removes a leg — a charter re-scrub dropping the recovery
commitment, a directory collapse — (`→ NotRooted`)". T6 judges independence at the
cosignature's `signed_at` ("a later change of role neither voids an earlier cosignature nor
validates one"), verifies a head against its parent's directory, has the holder of a witnessed
head refuse an unwitnessed one, and says a witness's leaving is "a harder attach, never a
detached node (T4)". The charter guard in CC 8.10 refuses a re-scrub that lists a founder or a
member as witness. So no row sequence the rest of the section admits reaches the collapse case
for an attached node: one reader detaches every attached node, the other keeps them `Rooted` on
the last witnessed head. T4, T4a and the nearest-verifying-ancestor input support the second.
Confidence medium.

**3. A witness row says adult and the person declares minor (minor_floor; CC 3.4.11 against
CC 3.4.13).** CC 3.4.11: "MUST union both prefixes and take the **highest** level on record. A
witness-emitted `age_assurance:*` (provider/government) **OUTRANKS** a subject
`age_self_declared:*`." CC 3.4.13 Q3: "`age_self_declared:band:minor:v1` suffices. A child MUST
NEVER be forced through provider/government assurance merely to be protected. This is a
down-ratchet only: self-declaration MAY lower access / raise protection". Since the band is the
identity's across its roster, a child on an adult-assured identity is read adult by the first
and protected by the second. The data is split the same way: the fold cell of
`age_assurance:{level}:{band}:{version}` is `pick=rank(government>provider>self)`, and
`formal/age_assurance` says "a declaration can lower the band and never raise it". CC 3.4.11
wants the lowering stated. Confidence medium.

## Known conflicts still present

- To fix in the data, still present: C499 (acceptance edge signer reads `self (node -> root)`,
  and the CC 8.10 card's authorize row), C507 (one `withdraw` for every `trust` job, open to the
  subject), C307 (one `selfAct` attest for every `takedown_notice` basis, `steward_purge`
  included), C422 and C423 (signer cells of the two age families).
- To fix from the text, still present: C442 (the halt's signature preimage against
  JCS of the envelope), C316 (an unassured person and the guardianship rule).
- Held or proposed, still present: C287, C055, C132, C142.
- For Eric, reported because a reader meets it: C002 (one guardian against M-of-N).
- C001's wording survives in one gloss, CC 3.4.12 ("protectively to `minor`").
- Checked and found repaired: C500 (no attach clock on an accepted edge in
  `manifests/reactions.json`), C454 (CC 3.3.6.2 now states the owned-node exception), C317
  (CC 3.4.13 and CC 5.4.6 now let an unassured owner announce).

## Read by gist only (5)

- principle: CC 3.2 "the substrate records an adjudication finding; it never makes one"; the
  Part 5 preamble statement on honest misses; the Part 7 preamble statement on M-1 (3).
- signature: CC 4.4.3.4.3, a user `identity_key` is hybrid and hardware-rooted (1).
- announce: CC 5.3.3.5 E3, entitlement against reachability (1).

Long paragraphs of CC 3.4.13, 5.4.6 and 1.7 were read to about 3,000 characters where the
statement's phrase fell inside that span.

## Keys not finished

None.
