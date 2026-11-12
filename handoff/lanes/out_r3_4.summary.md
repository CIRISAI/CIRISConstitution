# Third reading, share 4: summary

Head 87c1730, branch rc19. Read-only. Findings: `out_r3_4.tsv` beside this file (46 rows).
Every text quote in the TSV was checked by script as a verbatim substring of today's Part file.

## Per rule key

| rule key | statements read | findings | major new | major known | minor new | minor known |
|---|---|---|---|---|---|---|
| transport | 191 | 21 | 2 | 4 | 11 | 4 |
| erasure | 95 | 12 | 3 | 2 | 5 | 2 |
| halt | 61 | 6 | 1 | 1 | 4 | 0 |
| standing | 48 | 4 | 0 | 0 | 4 | 0 |
| settlement | 20 | 0 | 0 | 0 | 0 | 0 |
| other:composition | 8 | 1 | 0 | 0 | 1 | 0 |
| other:relief-never-expand | 2 | 2 | 1 | 0 | 0 | 1 |
| **total** | **425** | **46** | **7** | **7** | **25** | **7** |

`family`-scope rows were compared as full members. Data compared: `manifests/reactions.json`,
`manifests/transitions.json`, `manifests/family_model.json`, `constitution/constants.tsv`,
`constitution/governance_policy.tsv`, the CC 8.10 cards for `accord:*`, `takedown_notice:{basis}`,
`custody:{kind}`, `rendezvous:route`, `transport:*`, and `formal/accord_halt` with its README.

## Major new findings

1. **transport, CC 5.4.6 item 4 against item 10 (the anonymous node's guard).** Item 4: "Hop one
   is a sticky guard chosen from the sender's own consented contacts that offer relay". Item 10: "a
   route it holds for an announced contact is the exit of its circuit, never a destination it
   dials", and such a contact "never goes direct". The guard is a standing direct link, and the
   guard sees the address. A reader of item 10 gives every anonymous node a serve seat as guard; a
   reader of item 4 lets a contact who knows the anonymous identity learn its address.

2. **transport, data: `transport:canonical_rebind` is admitted on one holder's row.**
   `manifests/transitions.json` and the CC 8.10 card give the attest transition policy `selfAct`
   with no policy row and Count `None`. CC 3.1.3, 3.3.6.2 and 5.3.4 make the re-bind a quorum act
   at the accord charter's threshold, "never a single holder", refused below it as
   `transport_rebind_without_holder_quorum`. "by=cosigned" appears only as a change item.

3. **erasure, CC 3.3.2 against CC 4.5.3 (withhold windows).** The `LegalBasis` table gives
   `CommunityStandards` an "operator-set window" and `OsaIllegalContent` "OSA-defined timelines".
   CC 4.5.3 (the home) and `constants.tsv` fix 30 days and 14 days. A holder deletes a withheld
   copy on a different day under each. C171 repaired only the `Dmca512` row.

4. **erasure, data: three of the four withhold windows have no reaction.** `reactions.json` has
   stop-serving, the withhold clock and the delete for leaf `Dmca512` only. `constants.tsv` holds
   the windows for `DsaArticle16`, `OsaIllegalContent` and `CommunityStandards`, and nothing reads
   them. A node executing the data does nothing on those three bases.

5. **erasure, data: the delete at the close of the withhold window has no reversal condition.**
   CC 4.5.3: on a reversal inside the window "serving resumes, the hard-delete sweep skips them".
   The reaction on close(withhold) is `destroy_bytes`, force must, with no `unless`; stop-serving
   has no reversal either. A node executing the data deletes bytes the text keeps.

6. **halt, data: the heartbeat's expiry sits on the confirmation and the resumption.**
   `reactions.json` and the CC 8.10 card give `accord:lifecycle:{kind}` (no leaf named) "expiry
   required `valid_until` max `accord_heartbeat_max_secs`; on close: read stale". CC 3.4.1 puts the
   90-day refresh on the heartbeat, family `accord:lifecycle`, "a different row", whose own card
   has no expiry. CC 4.2.1.3: "A confirmed halt carries no TTL". A node executing the card reads a
   confirmation stale within 90 days.

7. **other:relief-never-expand, CC 6.1.5.1 and CC 4.2.1.4 against CC 4.2.1 rule (3).** CC 6.1.5.1:
   the mesh-config plane is "steward-authored, time-limited"; CC 4.2.1.4 says a root's relief
   expires. Rule (3) bounds only the threshold-1 emergency form (TTL at most 72 h) and says "The
   root's own quorum MAY establish a durable setting directly". `reactions.json` follows rule (3):
   expiry is required for the `emergency` leaf alone. A reader of CC 6.1.5.1 refuses a durable row.

## Known conflicts whose stale wording is still in the text

- **C341** (`link_seq` per link against per `(link, stream)`, CC 5.3.3.2.5): both sentences still there.
- **C342** (trailer v1 layout against the shipping v2 form, CC 5.3.3.2.3): still there; waits on vectors.
- **C304**: the CC 4.4.3.5.2 watcher is fixed; the GDPR Article 17 row of CC 4.5.2.2 still reads
  "producer emits `consent:deletion_complete` OR substrate emits `hard_case:deletion_window_breach`".
- **C305**: the residue in `reactions.json` is still there (the target's withdrawal both starts the
  clock and excuses the breach).
- **C151**: "Every node relays" (CC 1.13.3.3) and "Every announced node" (CC 5.4.6 item 1) still there.
- **C079**: `shaping.node_cap_bytes_per_s` still in the three key lists, still undefined in CC 5.4.3.
- **C062**: CC 4.5.3 is fixed; CC 6.1.2.2 still says "the purge" for an immediate-removal notice (left on purpose).
- **C315 / C335 / C336** (relay tree for a live stream): held for Eric, all sides still there; two
  further pairs reported (CC 6.1.6 against CC 5.3.3.2.3; the tree assigned to the Anonymous Tier,
  which carries no stream).
- **C036** (halt row past `valid_until`): held for Eric; the reactions manifest and the card
  already say "expiry none", and the family-model cell says "expires_at honoured".
- **C312** (legal hold against an immediate-removal notice): held for Eric, unchanged.

Checked and found fixed, so not reported: C033, C047, C060, C064, C144, C147, C152, C295, C302,
C307 (transitions now carry the cosigned case for `steward_purge`), C345.

## Notes on the halt model

`formal/accord_halt` and its README agree with CC 4.2.1 and CC 4.2.1.1 as they stand: reach judged
at each node's latch instant, fuse counted from receipt, a confirmed halt ended only by a majority
resumption, a majority able to resume an unconfirmed halt. The one stale statement of reach is in
the text, CC 4.2 ("when it is fired"), reported as minor. The model has no `valid_until`, so it
does not decide C036.

## Limits

No key is unfinished. Read from the inventory gist and not from today's words, because
`rule_entries.tsv` has no entry and the statement sits in a long paragraph or table I did not
open in full: the CC 2.1 table rows (transport 172 to 174, erasure 71, halt 22 and 46), the
planned CC 2.6.1.8 erasability statements (erasure 11 to 14), the CC 3.2 founder and node-standing
statements (standing 8, 9, 19 to 22, 43, 44; settlement 2 and 7), CC 4.4.3.4.3 (standing 5, 6) and
CC 5.3.3.2.2. CC 5.3.4 was read in the three paragraphs the entries point to, not whole. The
settlement key gave no finding; its slashing "never sole evidence" statements agree with each
other in every place read.
