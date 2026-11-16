# Text proposals from the ceremony

Each gap the procedure (`CEREMONY.md`) or the model (`check_ceremony.py`, `Cutover.tla`) found, with the sentence
the Parts would need. **DERIVED** means it follows from the text and the rulings, and is safe to land. **NEEDS
RULING** means it is a choice. The DERIVED ones are also given as a unified diff against the Parts
(`text_proposals.diff`, beside the delivery), each sentence appended after the anchor quoted here, so no paragraph
is reflowed.

## DERIVED

**T1. CC 2.6.1.12, after "Receipts and custody acknowledgements signed by others keep their earlier form, under the
same rule."** Found by F1 and F3.

> An earlier-form object is in that past only when a row of this form in the past names it or a `carried` root in
> the past holds it, so a scope's root holds every earlier-form object of the scope. An earlier-form object signed
> after its scope's acknowledgement, and outside the past, counts at a node only until that node holds the ceremony
> row. Its signer signs it again in this form.

Why: an earlier-form object names nothing by digest (CC 2.6.1.12), so an earlier row's own references never extend
the past. The plant `inner_names` shows the other reading accepts a row no root holds.

**T3. CC 2.4.1.1, after "Its holder carries the key over by signing a record of this form, so the ceremony ends no
key and gives no other key a power over it."** Found by P7 and P8.

> A record of this form carries an earlier key when it names that key's earlier record and holds the same two
> halves, or when it names that record as a rotation does. Rows in the ceremony row's past that name the earlier key
> then name the key it is carried to. Two records that carry one earlier key, neither naming the other, carry it to
> neither until a row names both.

Why: the ruling that holders carry their keys over, and that the displayed identity becomes the composite thumbprint
at the ceremony (CC 2.6.1.7), say a key keeps its standing across the cut. Nothing says how a reader ties the
composite key to the earlier one. Without it, the plant `no_continuity` leaves an agent with no steward from its
record of this form on, and every roster, seat and owner-binding in the past binds nobody after. The last sentence
is the rotation rule already in CC 2.4.1.1, applied here (F6).

**T4. CC 2.4.1.1, replace "A key is live at an instant when one of its records covers that instant and the key has
not revoked itself by then ([CC 2.7.5](#2.7.5)). It has ended when every one of its records has ended. No row of
another key enters that reading, so no third party ends a key and no third party revives one."** Found by F13.

> A key is live at an instant when one of its records covers that instant and no revocation by one of the three
> revokers above has taken effect by then ([CC 2.7.5](#2.7.5)). It has ended when every one of its records has ended.
> No other row enters that reading, so no third party ends a key and no third party revives one.

Why: the paragraph before it names three revokers, the owner and the seating roster among them, and KERNEL.md runs
all three. The liveness sentence reads the key's own revocation only, so an owner's revocation of its agent's key
leaves the key live (F13). The correction makes the sentence fit the three revokers.

**T5. CC 2.6.1.11, after "A verifier follows `prev` to the head and reports a fork as a fork. With no state of its
own it holds the tips, waiting."** Found by P6.

> Under two ceremony rows, a reader with no acknowledgement of either accepts an earlier-form object only where it is
> in the past of both. A reader that holds the pin of one holds the other void ([CC 2.7.8](#2.7.8)).

Why: "the ceremony row's past" is undefined under two tips. CC 2.7.8 reads a roster under tips as what is common to
them, and a reader's acknowledgement voids a sibling. The plant `fork_union` lets a forged row widen the past.

**T7. CC 3.3.6.2, after "A seat switches handshake once, and one handshake runs on a link."** Found by P5, F4, F5,
and by the store's run on its current release, where a seat alone published the both-keys binding and was admitted.

> A node of this form takes a seat's `transit_xwing_pubkey` only from a re-bind counted by the accord's holders or
> from the bundle's `serve_transport_destinations`. The two carry the same key, and a seat's own binding that carries
> another is not honoured. The ceremony row names each seat's re-bind, so the re-bind is in its past.

Why: "Its own early rotation is refused" and "moves by `transport:canonical_rebind`" (CC 3.3.6.2) mean no seat
chooses its own transit key. The plant `seat_alone_td` shows the other reading gives a seat two keys.

**T9. CC 4.2.1.1, after "A sealed row that is stolen and published is a **false halt**, which is recoverable by
resumption below; a halt that cannot be fired is not."** Found by F2.

> A halt sealed in the earlier form and published after the ceremony row is refused
> ([CC 2.6.1.12](part_2_the_grammar.md#2.6.1.12)), so each holder seals its halt again in this form before that row.

Why: a sealed earlier-form halt is outside the ceremony row's past by construction. A holder who relies on it after
the cut holds a halt that cannot be fired, the one failure the halt exists to prevent.

**T10. CC 4.2.1.3, after "The halt latch clears on local verification and does not require replication reach."**
Found by F15 and the TLA+ twin `ResumeNeedsHonoured`.

> A latch set before the ceremony row stands after it, and a resumption of this form ends it by `resumes_halt_id`,
> whatever the form of the halt it names ([CC 2.6.1.12](part_2_the_grammar.md#2.6.1.12)).

Why: the latch is the node's own, and its one exit is the named resumption (CC 4.2.1.3). Read otherwise, a halt fired
in the window either clears at the cut (twin `CutClears`, no resumption) or can never clear (twin
`ResumeNeedsHonoured`, a stranded latch).

**T12. CC 3.2, after "Wherever this Constitution says a node accepts, trusts or un-trusts a root, or holds an
acceptance edge, the act and the edge are its owner's, and the node reads them."** Found by F9.

> An acceptance edge of the earlier form outside the ceremony row's past roots nothing after it
> ([CC 2.6.1.12](part_2_the_grammar.md#2.6.1.12)). The owner signs the edge again in this form, naming the ceremony
> row.

Why: it is the cutover rule applied to the edge. It matters because the halt's reach and an agent's capability both
read this edge (CC 4.2.1, CC 3.2 T3).

**T13. CC 4.2.6, after "The forward form of the three objects waits on the implementer's submission, and their
earlier form is [CC 8.11.22](part_8_appendices.md#8.11.22)."**

> Until that form is stated, no roster change and no recovery can be signed after the ceremony row.

Why: a recovery is a new version of the roster record (CC 4.2.6), and after the cut only this form is written.

**T14. CC 2.6.1.11, after "Two snapshots of one signer with one `seq` and different content are contested, and
neither counts."** Found by F10.

> A key of the earlier form is named in an entry by the composite thumbprint of its two halves, so a later record of
> those halves is named by the same entry.

Why: CC 2.6.1.7 makes the composite thumbprint a key's displayed identity from the ceremony row. A snapshot that
named an earlier key by its earlier id would miss a later record of the same halves.

**T16. CC 5.3.4, after "The node's own rotation door enforces it: a rotation that would retire the pinned pair
before its replacement is Rooted on every node is refused."**

> At the ceremony row the earlier pair is retired on every node at once, since a node that has not upgraded is off
> the mesh ([CC 3.3.6.2](part_3_the_namespace.md#3.3.6.2)). The rule binds a rotation within one handshake.

Why: read literally, the overlap rule forbids the hard cut, since the replacement is never Rooted on a node that has
not upgraded.

**T18. CC 3.2, after "A person's next device takes its first binding by **Adding a device**, below."** Found by F14.

> An owner-binding of the earlier form outside the ceremony row's past ([CC 2.6.1.12](part_2_the_grammar.md#2.6.1.12))
> binds nothing after it, and the owner and the key sign it again in this form.

Why: an agent whose earlier binding is not carried has no steward from the ceremony row on, until the binding of this
form (F14).

**Also seen, not in the diff.** CC 3.2 says "A `user` key and an accord holder's key ([CC 4.2.3]) are each a person's
hybrid key". In this form each is a composite key (CC 2.6.1.7). The word is a residue for whoever edits that
paragraph next.

## NEEDS RULING

**R1. Which scopes the ceremony carries (CC 2.6.1.12).** The text says "each scope the ceremony carries over" and
names only the revocation scope. A sentence is needed, and its content is a choice: what history survives the cut.

> The ceremony carries over the revocation scope, the provenance log and every scope a seated serve node holds, and
> a community whose rows no seat holds carries its own scope by an acknowledgement its count signs before the
> ceremony row.

Recommendation: this sentence. A community that does not is founded again in this form by its members (CC 3.1.3.2).

**R2. The ceremony row's count (CC 2.6.1.11, CC 5.3.4).** Every holder (a holder can block, F7) or a strict majority
(an absent holder's commitment cannot be restated by others).

> The ceremony row is a fresh genesis: every holder signs it, and it restates each holder's recovery commitment under
> the holder's composite key.

Recommendation: this sentence.

**R3. No effect without a way back on a row the cut may void (CC 2.6.1.12).** Found by F3.

> A node SHOULD NOT take an effect it cannot undo on an earlier-form object signed after its scope's acknowledgement
> until it holds the ceremony row.

Recommendation: this sentence, or a quiet point in the procedure alone.

**R4. Holders sign in this form only, once their records exist (CC 4.2.1.3).** Found by the TLA+ finding
`Inv_ResumeStable`: a resumption counted on an earlier-form statement before the ceremony row loses its count after
the latch has cleared.

> From its key record of this form on, a holder signs every confirmation and resumption in this form.

Recommendation: this sentence.

**R5. Custody when the same halves are carried over (CC 4.2.3).** Found by F11.

> A holder whose earlier key ever held both halves on one device carries it over by a rotation to fresh halves.

Recommendation: this sentence. Without it the custody rule is met in the record and not in fact.
