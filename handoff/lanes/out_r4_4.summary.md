# Fourth reading, share 4: summary

Head 05cbcc8, branch rc19. Seven rule keys, 425 statements. Output: `out_r4_4.tsv` beside this file (27 findings).

## The three numbers

- New major findings, text against text: **2**
- New major findings, text against data: **3**
- Statements opened in the text: **343**; read by gist only: **82**

## Per rule key

| Rule key | Statements | Opened | Gist only | Major new | Major known | Minor new | Minor known |
|---|---|---|---|---|---|---|---|
| transport | 191 | 173 | 18 | 2 | 5 | 5 | 1 |
| erasure | 95 | 75 | 20 | 1 | 4 | 2 | 1 |
| halt | 61 | 47 | 14 | 1 | 0 | 2 | 0 |
| standing | 48 | 35 | 13 | 0 | 0 | 1 | 0 |
| settlement | 20 | 6 | 14 | 1 | 0 | 1 | 0 |
| other:composition | 8 | 5 | 3 | 0 | 0 | 0 | 0 |
| other:relief-never-expand | 2 | 2 | 0 | 0 | 0 | 0 | 0 |
| **Total** | **425** | **343** | **82** | **5** | **9** | **11** | **2** |

Findings: 14 major (5 new, 9 known), 13 minor (11 new, 2 known).

## Major new findings in full

1. **transport, text against text (CC 3.3.6.2, CC 4.4.3.2.4.1 against CC 5.4.6): who may be served an owned node's route.**
   CC 3.3.6.2 makes the signed `transport_destination` binding a federation-wide directory row carried in the identity occurrence: "The announce app-data MAY carry it for self-authenticating discovery, and the directory holds it as the durable source of truth." CC 4.4.3.2.4.1 resolves every member's address from it, and CC 5.4.6 item 6 has a sender build onion headers "from the directory's hop keys", which sit on that binding. CC 5.4.6 first contact says the opposite for an owned node: "An owned node's signed route is handed by its owner and never served by a forwarder" and "The served set is this and nothing more, an owned node's route never among it", while the same paragraph serves identity occurrences openly. One implementer serves the binding to any asker; the other withholds it from all but a contact or a referred stranger. Not in the conflict table (C147 and C294 touch the paragraph but not this).

2. **transport, text against data (CC 3.1.4, CC 5.4.6 item 6 against family_model.json and the CC 8.10 card): the rendezvous row cannot supersede.**
   CC 3.1.4 signs each period's `rendezvous:route` row with a fresh key ("attester = subject = the period's rendezvous key") and also says "each period's row `supersedes` the previous one in the same lineage". The data admits a supersede only from the same attester (`"supersedes": "same_attester"`; card: supersede by author), as CC 2.4.1 defines the verb. The next hour's row is signed by a different key, so the supersedes clause cannot be followed. Expiry at `valid_until` does the work in practice.

3. **erasure, text against text (CC 3.3.5 against CC 3.3.1 D1): what is owed by the end of the deletion window.**
   CC 3.3.5: "Subject withdraws; producer must initiate deletion within sla window". CC 3.3.1 D1: "A producer has proven deletion iff, before the deadline, the row was withdrawn, superseded, or hard-deleted", and CC 2.4.1.1 "deletes within it and keeps no copy". A producer that has only begun at the deadline conforms to CC 3.3.5 and is in breach under D1. D1, CC 2.4.1.1 and the reaction data support "done".

4. **halt, text against data (CC 4.2.1.3, CC 3.4.1 against family_model.json): the resumption's cosign cell reads none.**
   CC 4.2.1.3: "It is a cosigned row by a strict majority of the standing roster", "never a lone signature". The `accord:lifecycle:{kind}` row's `cosign_rule` cell (source code-v61) is `none`. The same row's count cell and the transition case (leaf=active: cosigned `accord_majority`) agree with the text, so the data disagrees with itself; a reader of the cosign cell admits a one-holder resumption.

5. **settlement, text against data (CC 3.3.1 D3, CC 3.3.5.1 against family_model.json): who may sign a slashing verdict.**
   The text puts a slashing verdict with an adjudicating body ("remain CC 4.3 WA-quorum or per-node acts"; "follows on WA quorum"; CC 2.4.1.1 calls it a duty-holder's record). The `slashing:{outcome}` row (code-v61) reads signer `any_registered`, cosign none, governance none, and the home row in CC 3.1.9.2 names no signer. A store built from the data admits a lone key's verdict.

## Known conflicts reported (still present)

- C336 (with C315, C335; open with the steward): member relays in a call against "no relay tree".
- C341: `link_seq` per link against per link and stream (CC 5.3.3.2.5).
- C342: the trailer and the 148-byte budget are the first submitted form (CC 5.3.3.2.3).
- C151: "every announced node" relays against item 4's owner-bound relay set (CC 5.4.6).
- C369: partly repaired; the `transport:canonical_rebind` supersede transition still reads author, selfAct.
- C304: repaired in CC 4.4.3.5.2; the same fault stands in the CC 4.5.2.2 compliance row.
- C228: the trace's `dsar (trace corpus hard delete)` route still in the data.
- C370: the kept list now names the quarantine marker; the data still lets the subject withdraw it.
- C377: close-of-window `destroy_bytes` with no `unless` for a reversal, now on all four windowed bases.
- C047 (minor): the hard-delete mapping names none of N5's gates. C337 (minor): chat on a shaped link.

## Known conflicts found repaired while reading (not reported)

C061 (CC 6.1.2.2 now lists five bases), C074 and C075 (CC 5.4.3 item 1), C136 (no auto-grant wording), C302 (CC 7.5.5), C307 (steward_purge case in the transition), C376 (all four withhold clocks), C378 and C435 (no expiry on `accord:lifecycle:{kind}` in the reactions).

## Read by gist only (82 statements)

- transport (18): CC 2.1 (3), 2.2 (1), 2.3.3 (1), 2.6.8 (1), 3.2 DNS sentence (1), 4.4.3.2.6 (1), 4.4.3.4.3 (1), 5.1 (1), 5.3.4 (4; only the opening sentence of the paragraph was read), 6.1.5 (1), 6.1.5.2 (2), 6.1.9 (1).
- erasure (20): CC 2.1 (1), 2.6.1.8 (4), 3.1.3.3 (1), 3.1.5 (1), 3.2 (1), 3.3.2 (1), 3.3.3 (1), 3.4.12 (1), 4.4.3.2.8 retention matrix (1), 4.5.9.3 (1), 6.1.2 fabric-node sentence (1), 6.1.5.2 (3), 6.1.5.3 (1), 6.1.9 (1), 7.5.4 (1).
- halt (14): CC 1.5 (1), 4.2.1.2 (7), 4.4.3.4.2.1 (1), 4.5.1 (3), 4.5.13 (1), 7.3.4 (1).
- standing (13): CC 1.13.2 (1), 2.6.1.7 (1), 3.1.1 (1), 3.1.2.1 (1), 3.1.3.2 publish right (3; the words were not found by search), 3.1.9.4 (1), 3.2 node and agent key rows (2), 3.3.6.3 (1), 4.4.3.2.8 designated officials (1), 4.5.13 standing projection (1).
- settlement (14): CC 1.2 (1), 3.1.3 (2), 3.2 (2), 3.3.10 (2), 3.3.10.1 (3), 3.3.12 (1), 4.4.1 (1), 4.4.3.10 (1), 6.1.5.2 (1).
- other:composition (3): CC 3.1.1 (1), 3.1.5.5 (1), 3.1.9.2 (1).

## Keys not finished

None left unread. The settlement key was mostly read by gist (its statements are near-identical "never sole evidence for slashing" clauses); its one major finding comes from the data comparison. Data was compared for the transport, rendezvous, accord, takedown, consent deletion, kept-list, slashing and mesh_config families; the `signed_object.cddl` was not opened.
