# Fifth reading, share 2: wire, registration, media

Branch rc19 at 1ee1bcf. Output: `out_r5_2.tsv` beside this file (39 findings).

## The three numbers

- New major findings, text against text: **2**
- New major findings, text against data: **1**
- Statements opened in the text: **425 of 429**; read by gist only: **4**

## Per rule key

| Rule key | Statements | Findings | Major new | Major known | Minor new | Minor known |
|---|---|---|---|---|---|---|
| wire | 324 | 27 | 0 | 7 | 19 | 1 |
| registration | 60 | 7 | 2 | 1 | 2 | 2 |
| media | 45 | 5 | 1 | 2 | 2 | 0 |
| total | 429 | 39 | 3 | 10 | 23 | 3 |

## Major new findings in full

### 1. registration: is holding a role enough to emit under its reserved prefix? (text against text)

- CC 3.4.7.1: "Holding the role is necessary and never sufficient: every reserved role but `accord_holder` is conferred by a live `delegates_to`", resolved at use against a root the evaluating node trusts.
- CC 4.5.8.1: "Set membership grants the wire-level *right* to emit per held role". CC 3.4.7 likewise makes "every admission decision" one "against the `federation_keys` row's `identity_type` set" and names no second condition.

A key whose record lists the role, but whose conferral is absent, expired or under a root the node does not trust, is admitted by a reader of 3.4.7 and 4.5.8.1 and refused by a reader of 3.4.7.1. CC 3.2 T2 and the data (signer_rule `seat_role(...)` via `delegates_to(...)`, read from the shipped store) support 3.4.7.1. This is the same family as C401, which found the same split between 3.4.3 and 3.4.7.1. It is borderline between a shorter restatement and a conflict; I report it because "grants the right" asserts the sufficiency that 3.4.7.1 denies.

### 2. registration: the build check on an identity occurrence is not in the data (text against data)

- CC 3.3.6: "At admission the cited provenance row MUST exist and be Rooted on the receiving node and its manifest hash MUST equal `build_manifest_hash`."
- `manifests/transitions.json`, identity:occurrence, attest: the guard list is empty (source generic). `formal/derivation/guard_text.tsv` has no identity:occurrence row, and the CC 8.10 card lists no guard.

The text refuses an occurrence that names a build whose provenance row is missing, not Rooted or of another hash. A kernel that executes the data admits it. A minor text finding sits beside it: CC 3.3.6.2 keeps cross-row checks out of occurrence admission because the verdict would depend on arrival order, and this check is one.

### 3. media: what the plaintext of a live_stream chunk is (text against text)

- CC 3.3.13: "each chunk is one fMP4 segment (`moof` + `mdat`), independently hashable, ordered by sequence number; `codec` is stream-level, once", and the init segment followed by the chunks is a valid `video/mp4`.
- CC 5.3.3.2.1: the realtime chunk payload codec is "application-defined and opaque to the substrate", tagged per chunk by `codec_id` and `ChunkLayer`. CC 5.3.3.2.3 limits a frame's plaintext to 252 bytes on a base link, and CC 5.3.3.2 makes a call's stream a `live_stream` whose live and stored chunks are "the same sealed object".

A receiver built to 3.3.13 expects fMP4 segments. A publisher built to 5.3.3.2.x sends per-layer codec units, which are not fMP4 segments and whose concatenation is not a file. Neither decodes the other, and the recording rule of 3.3.13 and CC 5.1 does not hold for layered chunks. Nothing in Parts 5 or 6 mentions fMP4, so the text does not say which form a call uses.

## Known conflicts still present

| Id | Rule key | Status in the table | What is still there |
|---|---|---|---|
| C169 | wire | held | v1 wrap string in the CC 3.3.2 table against "v2 only" |
| C341 | wire | to fix from the text | `link_seq` per link against per link and stream |
| C342 | wire | to fix from the text | the trailer laid out is not the shipping form |
| C441 | wire | open | chunk counter reset per epoch against the `(stream_id, seq)` guard |
| C442 | wire | to fix from the text | accord preimages against "JCS and nothing else" |
| C443 | wire | to fix from the text | carrier row id: digest against uuid |
| C444 (also C510) | wire | to fix in the data | receipt guard is advisory where the text refuses |
| C359 | registration | to fix from the text | an anchor as base signer of a key record |
| C315 | media | for Eric | layer-selecting relays in a call |
| C404 | media | for Eric | what a joiner of a kept stream receives |

Three more known ones are reported as minor because the words still differ, though the table has them settled or read as no conflict: C221, C224 and C425.

## Known conflicts I found fixed

- C322: the 16-character fingerprint SHOULD is gone from CC 2.6.8.
- C321: CC 4.5.8.4 now carries the node carve-out.
- C343: CC 3.4.11 now says a rung carries no further qualifier.
- C167: CC 2.6.8 now says three kinds are identity types and two are rostered subject kinds.
- C358, data side: the receipt guard no longer demands a cosigned head. What remains is C444.

## Statements read by gist only (4)

I could not find the sentence by its entry phrase or by search:

- wire, CC 2.1: an explicit null `subject_key_ids` is refused.
- wire, CC 2.4.1: the delegated scope rides the `scope` member, never `delegated_scope[]`.
- registration, CC 2.4.1.1: `canonical_binding` promotes a hash for rule 2.
- registration, CC 5.2: an at-rest recipient needs an occurrence carrying `encryption_pubkeys`.

## Keys not finished

None. Three checks were partial:

- The key-plane member table of `registration_envelope` is not enumerated in CC 2.6.1.7, so the key record's inner members were compared only at the outer shape.
- `manifests/reactions.json` and `manifests/governance_policy.json` hold nothing I could tie to these three keys; I did not search them exhaustively.
- CC 5.4.6 (43 kB) and CC 5.4.3 (21 kB) were read at the paragraphs that carry this share's statements, not end to end.
