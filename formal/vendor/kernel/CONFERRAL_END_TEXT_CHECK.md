# CC 2.4.1.1 and `names_head` at rc22 3a8a033, read against the model

I read the Constitution's text and its family model (`manifests/family_model.json`) at `3a8a033` with `git`.
Nothing in that repository was changed. The first reading was of the text at `850ed50` and the family model at
`76c4550`; this one was redone on 2026-11-22 at the Constitution's request. Every quote below was checked
against the files at `3a8a033`, and what changed since the first reading is said where it bears on a finding
and listed in "Added since 850ed50". They are read against:
- E1 to E8 and section G of `CONFERRAL_END.md`;
- the spec `ConferralEnd.tla`;
- the reference `models/causal_kernel/conferral_end.py` and its case table
  (`crates/ciris-kernel/tests/fixtures/conferral_end.tsv`).

Each finding quotes the sentence and says what the model says. They are listed most consequential first.

## Findings that change an answer

**1. Acts that name no head: the text refuses them, the model counts them. Ruled; no change needed.**

> "A row that exercises a standing and names no head concludes nothing, `act_names_no_head`."

The model counts an act that names no head at its own head and holds it out of force once an end is held,
unless it is receipted. That is the fixture's `uncited_act` (E2.forward) and `uncited_act_receipted`
(E8.receipt).

This is a recorded difference, not a needed change. As first written, this finding said that every act
persist signed before the change is such a row and that the sentence voids them retroactively. That premise
was wrong:
- Persist reports (2026-11-22) that the Constitution ruled the refusal deliberately: an act that names nothing
  cannot be judged (section A of `CONFERRAL_END.md`), a kept row of that kind on an upgraded node concludes
  nothing, and its signer signs a fresh one. I have the ruling from persist's relay, not from the text.
- Persist reports that no such row exists. The canonical node runs the 61.x line, which has no edition-2
  store, and no v62 node has run live. The kept edition-2 rows are the eight genesis statements and the
  seat's key record, which exercise no standing.

The text is the rule of record. The fixture marks the three cases `refused: act_names_no_head`; an adopter's
witness for them is the refusal, and their answers are what the model concludes if such a row were admitted.

**2. A receipt must not keep in force an act at a later head.**

> "*What stays in force.* An act stays in force after the end where a clean receipt of it is held that does
> not have the end in its past"

It is unqualified. The model applies receipts only to acts that count: E3 decides before E8, an act at a head
later than `h_e` does not count, and no receipt revives it (`Inv_ReceiptForwardOnly`). The text's closing "it
revives no act" can be read as covering this, but "revives" is not defined. An implementer may also read the
one-say sentence ("Where the ender holds a clean receipt of such an act concurrent with the end, the act counts
at its own head") together with "What stays in force". The ender's concurrent receipt is the conferrer's
receipt, so that reading would also put the act in force.

Needed:
- "an act that counts at the end's head or an older or concurrent one stays in force …";
- for the one say, "counts at its own head, and is not in force".

**3. The end of a receipter's role is stated by instant, and it has no row.**

> "A receipter's receipt made after the body ended its role keeps nothing."

"Made after" is an instant. The model's rule is causal: a receipt that has the body's end of the role in its
past keeps nothing, and one concurrent with it keeps (`Inv_ReceipterAfterItsEndNothing`,
`Inv_ReceipterBeforeStands`).

The wire also has no row that ends the role. `receipter` is a field on the offer, so ending the role means
withdrawing or superseding the offer, and that ends the grant. The model has a separate row (Rx) that ends the
receipter's seat and leaves the grant.

Needed:
- "a receipt that has the end of the receipter's role in its past keeps nothing";
- either a row that ends the role, or a rule that superseding the offer without `receipter` ends it.

**4. `lifts`: "one's own end" in 2.4.1.1, "one voice" in the wire table.**

> "One's own end lifts nothing, and `lifts` on it is refused, `lifts_on_own_end`." (2.4.1.1)

> "Present only as true. On an end signed by one voice it is refused, lifts_on_own_end." (wire table)

These are different sets. A conferrer that is a single key, ending a grant it made, is not ending its own
standing, but it signs with one voice. Under the wire wording it cannot lift a co-holder's receipts after a
compromise.

The model, section G, lets the conferrer's end carry `lifts` and ignores `lifts` on a self end. Refusing a self
end that carries `lifts` is stricter and safe: the resignation concludes nothing, and the resignee signs it
again without the flag.

Needed:
- one wording;
- a decision on whether a single-key conferrer may lift.

**5. `under`: resolved at 3a8a033.**

At `850ed50` the refs table carried `under` and no sentence said what read it. The text now gives it one use:

> "`under` names the one edge a deputy's edge hangs from, a set of exactly one"

> "A deputy's edge names the edge it hangs from, its delegator's seat edge, in `refs.also.under`"

That is the deputy edge of E6 (the fixture's `deputy`), not a binding of an act to one standing. No act
carries it, so it does not contradict ANY-STANDING ("An act that another live standing of its signer
authorises at its head stands on that standing"). The family model agrees: `may_carry_under` is false for
every family but a deputy's edge. Nothing more is needed.

## Findings of wording or scope

**6. "does not count", when another standing authorises the act.**

> "An act with the end in its past does not count."

This holds only for the ended standing. Under the text's own "Another standing" paragraph, an act that names
the end stands on a second live standing: the fixture's `tie_any_standing`, rule E7.other_standing, decides
first.

Suggested: "does not count under the ended standing".

**7. The sentence in 4.5.5: resolved at 3a8a033.**

At `850ed50` CC 4.5.5 still said a `withdraws` in the chain invalidates every act concurrent with it. It now
reads:

> "A `withdraws` against *any* `delegates_to` in the chain ends everything downstream of it"

> "An act with the withdrawal in its own past does not count. An act at the withdrawal's head, at an older head
> or at a concurrent one counts at its own head"

> "From the withdrawal's head on it is in force only under a clean receipt."

That is E4, E2 and E8. The paragraph does not restate E3 (an act at a later head); it cites CC 2.4.1.1, which
does. Finding 6 applies to its first sentence too: "does not count" holds for the ended standing only.

**8. `act:ack`: who signs, and its head.**

> "the signer acknowledges the acts it names under `refs.also` `ack`, at the head it names in `refs.head`."

> "**Yes:** a voice at the head the acts name; never the signer of an act it names, and never a node"

> Appendix card: "attest | member | selfAct"

- **The model gives a receipt no head.** A receipt is read by its causal past alone: it must not have the end
  in its past, and it must not be cut by a key removal. A head on it is harmless.
- **"A voice at the head the acts name" is too narrow.** It shuts out two receipters the model needs. The
  offer's receipter is not a member of any roster: a CI worker's owner, for instance. Under a root grant, the
  conferrer is a count of bundle holders.
- **It leaves acts that name no head unreceiptable.** "the head the acts name" does not exist for them, yet
  `uncited_act_receipted` keeps such an act in force. Under the text such an act is refused (finding 1), so
  this has no live case.
- **The card's "member" is narrow in the same way.**

Suggested: "the conferrer (a count where the conferrer is one), another holder of the body the acts were done
for, or the receipter the offer names".

**9. Counted receipts and the line.**

> "This line is for counted rows: a version, a vote, a cut and the end of a standing."

An `act:ack` signed by a body's count is a counted row, so the line reaches it. A reader that acknowledged a
newer head would hold void a counted bulk receipt naming an older head, and the acts it covers would drop out
of force for that reader. The model does not apply the line to receipts.

Suggested: name receipts as not reached, or accept it and say so. The end of a standing being listed is right:
the model applies the line to every end (E5).

**10. One's own end is not a counted row.**

> "This line is for counted rows: a version, a vote, a cut and the end of a standing."

A withdrawal of one's own acceptance is authored, signed by one voice, so "counted rows" does not fit it. The
model applies the line to it all the same.

Suggested: "counted rows and every end of a standing".

## What matches the model

| Text (3a8a033) | Model |
|---|---|
| "The head is the newest its signer holds of the record that seats the standing … For a grant from a root it is the bundle in force. Where one row between two keys is the whole record, as an owner-binding is, that row is the head." | `persist_root_grant`, `persist_owner_binding`; section D |
| "That head is the newest its signer holds, and an end with a newer head in its own past concludes nothing, `end_names_old_head`." | E1, `end_stale_head` |
| "The end concludes under its signer's own standing at that head, so one's own acceptance is withdrawn by one's own signature." | E5 |
| "It reaches the acts exercised under its target, a deputy's among them. It never reaches the members counted at any head" | E6, `deputy`, `Inv_MembersByPast` |
| "An act at the end's head, at an older head or at a concurrent one counts at its own head, and from the end's head on it is not in force. The end never undoes that count." | E2, `Inv_ForwardNeverVoidsAtOwnHead`, `Inv_EndNeverUnmakes` |
| "An act at a later head finds the standing ended and does not count." | E3 |
| "The receipt is the conferrer's, another holder's of the body …, or that of a receipter the offer names … never the act's own signer's and never a node's. A count that ends a standing MAY state `lifts`, and then only the count's own receipts keep an act in force." | E8, section G; plants `self`, `selflift` |
| "A receipt changes what is in force, never what counted" | `Inv_ReceiptsChangeOnlyForce` |
| "*The limit.* … No reader can tell it from an honest earlier act, and no rule here tries." | `persist_behind_node` |
| 2.7.8: "It does not reach an authored act that names its head, which counts at that head whatever head a reader has acknowledged." | `Inv_AsOfStands`, `ConferralEnd_line_acts` |
| 4.5.5: "From the withdrawal's head on it is in force only under a clean receipt." | E8 |
| refs.head "on a counted row, on a roster version, and on a row that exercises or ends a standing" | the recommendation's wire |
| `receipter`: "A person or an agent, never a node." | section G (c) |

Two model rules the text leaves to the general rules, which do cover them:
- an end concurrent with a removal of its signer's key changes nothing (`end_void.key_removed`);
- a receipt by a removed key keeps nothing (`receipt_by_removed_key`).

Both follow from a removed key's rows counting only in the removal's past (KERNEL.md section 6).

## Added since 850ed50

- **An acceptance or a decline names no head.** "An acceptance or a decline names none: it names the row it
  answers, and that row names the head." The model agrees: its `accept` row has no head, and no E-rule reads
  one (the fixture's `reaccept_two_devices`). The model's `accept` names nothing at all; the text's names
  what it answers in `refs.answers`, which no E-rule reads either.
- **An accord invocation names no head.** "An accord invocation names none, since it fires at each node on
  receipt, under the roster that node holds". This is outside the model: an invocation is then not an act
  exercised at a head, and E1 to E8 give it no answer. Noted, not checked: "under the roster that node holds"
  on receipt is a reading per node, and the model's convergence result (every answer is a function of the
  held rows) says nothing about it.
- **Federation scope and the commons.** "a row there names a head only where its signer signs under a
  standing." This is the sentence point (a) below asked for.
- **`withdraws` and `recants` (CC 2.6.1.1).** "A `withdraws` or a `recants` carries the family id of its target
  and no `dimension`, and its `sub` is its target's." No E-rule reads it. It bears on point (c) below.

## `names_head` at 3a8a033

Of 185 families (190 at `76c4550`):

| `names_head` | Families at 3a8a033 | At 76c4550 |
|---|---|---|
| `by_placement` | 145 | 150 |
| `none` | 15 | 12 |
| `roster` | 9 | 9 |
| `standing` | 8 | 8 |
| by selector (one value per leaf or act) | 3 | 0 |
| null (open) | 5 | 11 |

21 cells are now ruled from `formal/derivation/names_head_text.tsv`; the rest are derived from the placement
and signer cells. A new column, `standing_act`, says what a row of the family is to a standing: `exercise`,
`offer`, `acceptance`, `end`, `none`, or open.

Against "every act names its head; ends name `h_e`; receipts":

**a. The self branch of `by_placement`: addressed in words.** The builder's note now reads "at self, at
federation or in the commons, where there is no roster, it names none unless its signer signs as someone's
node, agent or delegate or under a grant, and then that binding, delegation or bundle", and the text has the
matching sentence. `moderation:{allegation_type}` and `detection:{detector}` are still `by_placement`; their
signers come by `delegates_to(moderate)` and `delegates_to(infra:detect)`, so they fall under "delegate".
The cell itself still says only `by_placement`: a builder that reads the value and not the note cannot tell
the two self branches apart.

**b. `act:ack`: resolved as a column.** It is now ruled `by_placement`, "the head the acknowledged acts name".
Finding 8 stands beside it: the model needs no head on a receipt.

**c. A marker for the ends: partly addressed.** `standing_act` is `end` for `membership:{stage}` at
`leaf=removal` and `leaf=resignation`, both naming `roster`, and for `key:revocation` and
`identity:occurrence_revocation`, which name none (a person's own key plane, not a conferral). The other
ending sites are a `withdraws` against an acceptance or an offer. `withdraws` is a primitive, not a family:
by CC 2.6.1.1 it carries its target's family id, so its row in this table is its target's, whose
`standing_act` is `offer` or `acceptance`, not `end`. Nothing in the table tells the builder that such a
`withdraws` carries `refs.head` (`h_e`); only the 2.4.1.1 sentence does.

Needed: a rule, or a sentence in the build's note, that a `withdraws` of an offer or an acceptance names `h_e`.

**d. The records themselves: resolved for the binding.** `ownership:{relation}:{target_kind}:{version}` is now
ruled `none` ("an owner binding their own key acts as themselves; a binding that names an affiliation names
that affiliation's roster version"). `key_grant:{axis}` is still `standing`, derived. If a key grant is itself
the record that seats a standing, the same question is open for it.

**e. `duty:{kind}`: resolved.** It is now ruled `by_placement`: "a duty exercised in a room names that room's
roster version".

**f. 5 families are open** (11 before): `archive_release:{basis}`, `lawful_order:release`, `preserve_request`,
`preserve_response`, `retirement:{state}`. `standing_act` is open for 13 families. If any of these is
exercised under a standing and the builder sends no head, it is `act_names_no_head`.

## Summary

| # | What | Kind |
|---|---|---|
| 1 | `act_names_no_head`: the text refuses, the model counts; ruled for the text, no live row, fixture cases marked `refused` | recorded difference, no change |
| 2 | receipts and one say: say "not in force" and "only acts that count" | changes an answer |
| 3 | the end of a receipter's role: stated by causal past, and given a row | changes an answer |
| 4 | `lifts`: one wording, and decide whether a single-key conferrer may lift | changes an answer |
| 5 | `under` | resolved at 3a8a033 |
| 6 | the tie: "does not count under the ended standing" (also the first sentence of the new 4.5.5 paragraph) | wording or scope |
| 7 | the old 4.5.5 sentence | resolved at 3a8a033 |
| 8 to 10 | wording: `act:ack`'s signer, counted receipts and the line, one's own end | wording or scope |
| `names_head` b, d (the binding), e | `act:ack`, the owner binding, `duty` | resolved at 3a8a033 |
| `names_head` a, c, d (`key_grant`), f | the self branch in the cell, a `withdraws` that ends names `h_e`, the key grant, the 5 open families | column |
