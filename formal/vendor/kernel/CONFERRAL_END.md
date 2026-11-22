# The causal end of a conferral: what persist v62.0 should put on the wire

Model: `models/tla/ConferralEnd.tla` with its configurations. Run by `tools/tla_check.sh` (small) and
`tools/tla_check.sh --large`. No instant is read anywhere; the only order is what rows name.

The rule under test is CC 2.4.1.1 as ruled ("A withdraws row retires its target as a cut does (CC 2.7.7). An
act under the target that the withdrawal has among its ancestors stands. One that has the withdrawal in its
own past, or is concurrent with it, does not count."). It is read the way the Constitution intends it
(2026-11-21): an end is FORWARD. A concurrent act counted at its own head and is not in force afterwards, and
nothing the end does voids an act at the act's own head. CC 4.5.5 adds: "Acts already taken under the duty
stand."

## Recommendation for Eric

**Weak + acts name their head + ender's-side receipts** (receipts counted wherever they are held, not only in
the end's past). Ship it in v62.0. It has three parts:

1. **Every act names the head it is at** (`refs.head`). Persist's choice (a): one payload builder, so it is
   cheap at the 47 producer sites. This gives "valid when made": an act counts at its own head, a late
   arrival or a re-fold gets the same answer, and as-of walks keep a resigned official's verdicts.
2. **The 10 ending sites name `h_e`**, the head the end acts from.
3. **One receipt producer.** A clean Ack of an act by the ender's side keeps that act in force after `h_e`.
   This gives CC 4.5.5 its durable half: a withhold or an attestation stays in force after a moderator resigns
   or a worker's grant is rotated, if the body receipted it. Who may receipt (section G):
   - the conferrer, which for a count is the count, a bulk receipt included;
   - a single co-holder;
   - a receipter the grant names.

   Never the act's own signer, and never a node. A count end carries a `lifts` flag: set for a compromise, so
   that no single receipt survives it; unset for a rotation. A self end cannot lift anything.

Not needed: `under`, `prev`, `ack`. Do not stay on instants for v62.0. The model finds no answer persist needs
that this combination does not give, and two that instants cannot give without arrival order: the late act
and the re-fold.

The candidates compared (the four you asked me to choose among, and the two halves of the recommendation on their own):

| Candidate | Valid when made | Durable effects stay in force (CC 4.5.5) | Wire |
|---|---|---|---|
| weak, acts naming nothing (persist today) | **no**: undecidable (section A) | no | 10 sites |
| weak + ender's receipts, acts naming nothing | only for an act whose receipt is in the end's past (the receipt gives it ancestry before the end); every other act stays undecidable | yes, for receipted acts | 10 sites + 1 receipt producer |
| weak + acts name their head | yes | no: every act of the ended standing is out of force from `h_e` | 10 + 47 sites (one builder) |
| **weak + heads + ender's receipts** | yes | **yes**, for receipted acts | 10 + 47 sites (one builder) + 1 receipt producer |
| weak + `under` + ack set | yes, but only with heads on acts | only for acts the ender holds and lists; the end grows with the history | 10 + 47 sites; the end grows with the history |
| stay on instants | by instant, which the Constitution rules out for verdicts | | none now |

## The rules (E1 to E8), as checked

- **E1. The end names its head.** An ending row names `h_e`: the newest head its signer holds of the ledger
  the ended acts name. The end concludes nothing if a newer head is in its own past.
- **E2. Forward.** An act whose named head is `h_e`, older than `h_e`, or concurrent with it, counts at its own
  head and is not in force from `h_e` on. The end never voids it (`Inv_ForwardNeverVoidsAtOwnHead`,
  `Inv_EndNeverUnmakes`).
- **E3. Later heads.** An act whose named head has `h_e` in its past finds the standing ended there and does
  not count. Rule 6's one say is the exception: if the ender holds a clean receipt of the act concurrent with
  the end, the act counts at its own head and is still not in force (`Inv_OneSay`). A forward end is never
  blocked (`Inv_NotInForceFromEnd`).
- **E4. Naming the end.** An act with the end in its causal past does not count (`Inv_NamingEndVoid`).
- **E5. Concluding.** The end concludes as a cut under its signer's own standing at `h_e`.
  - A holder's withdrawal of its own acceptance is signed by the consent-giver alone and needs no count.
  - A conferrer's withdrawal of its own offer is signed by the offer's signer, or by the count at `h_e` for a
    counted offer.
  - CC 2.7.8's line applies to the end as to any counted cut over roster heads.
- **E6. Reach.** The end reaches only acts exercised under the target, deputies transitively. It never reaches
  the member set or n at any head (`Inv_MembersByPast`).
- **E7. ANY-STANDING.** Nothing binds an act to one standing. An act that another live standing of its signer
  authorises at its head stands on that standing.
- **E8. Receipts.** An act at a head not later than `h_e`, not naming the end, stays in force when a clean
  receipt of it by the ender's side is held and does not have the end in its past (`RSCOPE = "any"`). A
  receipt never revives an act at a later head or one naming the end (`Inv_ReceiptForwardOnly`). It changes
  force only, never a count (`Inv_ReceiptsChangeOnlyForce`). A receipt by a key removed concurrently counts
  for nothing.
- **Not the line for authored acts.** CC 2.7.8's line voids counted acts naming an older head. It must not be
  applied to authored acts that name their head (section C).
- **Exercised acts stay off the seat's slot** (section F).

## The model

Fixed and in every row's past:
- an offer by A to B, and B's acceptance `acc`;
- head H0: a roster version, a genesis-bundle version, or the binding row;
- with `WithTie`, an independent grant `accD` to B from D.

Signed in any order, each naming only rows already signed:

| Row | What it is |
|---|---|
| H1 | a later head (absent for an owner binding) |
| b1, b2 | B's acts on two devices, each naming the head it is at, an old one included; `under` and `prev` are read only by the full reading; an act may cite the end; one may be a deputy edge |
| u1 | an **uncited** act: it names nothing |
| c1 | the deputy's act |
| E | the end, by A (a count end, with or without `lifts`) or by B (a self end: a resignation), naming `h_e`, an `ack` of acts and the receipts it names |
| Q1, Q2 | receipts by A (the conferrer; for a count, the count), D (a single co-holder), R (a receipter the grant names) or B, on two devices, each naming one act and its signer's previous receipt on that device (its own series), and optionally the end |
| Rm | a removal of the ender's key or of D's |
| Rx | the body's end of R's receipter seat, naming R's receipts it has seen |
| a2 | B's re-acceptance |

Node 1 takes the rows in every order the door allows. So an act can arrive long after the end is held, at a
node that never saw it. Node 2 takes them in one fixed order. Node 1 may acknowledge H1.

For every act, at every held set, the spec computes four answers side by side, each as ⟨counts at its own
head, in force from `h_e` on⟩:

| Reading | What it carries |
|---|---|
| **full** | the proposal: `under`, `prev`, `ack` |
| **set** | an `ack` set, no `prev` |
| **weak** | acts name their head; no `under` or `prev` |
| **weakR** | weak + the ender's receipts |

| Run | Constants | Distinct states, diameter, time |
|---|---|---|
| small (CI) | 2 acts of B on 2 devices, H0 and H1, an end by A or B with or without `lifts`, one receipt by A, D, R or B, the receipter's end | 1,170,592, 15, 90 s |
| large (local) | + the uncited act, a removal of the ender's or D's key; no receipter | 11,917,636, 17, 24 min |

Plants, each caught at both bounds:

| Plant | Caught as |
|---|---|
| `members` (`_plant.cfg`): the end applied to the member set | `Inv_MembersByPast` |
| `say`: the ender's clean receipt ignored | `Inv_OneSay` |
| `naming`: naming the end read as concurrent | `Inv_NamingEndVoid` |
| `arrival`: an answer latched on arrival (no re-fold) | `Inv_Fold` |
| `converge`: the same latch, checked between nodes | `Inv_NodesAgree` |
| `own_head`: the end voids an act at its own head | `Inv_ForwardNeverVoidsAtOwnHead` |
| `receipts`: a receipt in the end's past ignored | `Inv_ReceiptedStays` |
| `self`: the grantee's own receipt keeps its own act in force | `Inv_NotInForceFromEnd` |
| `selflift`: a self end carrying `lifts` lifts the co-holders' receipts | `Inv_ReceiptedStays` |
| `after_rx`: a receipter's receipt made after its seat ended still keeps | `Inv_NotInForceFromEnd` |
| `bulk_after`: a receipt with the end in its past (a bulk receipt after the end) keeps | `Inv_NotInForceFromEnd` |

Documented configurations, outside both runs. Those marked FAIL fail on purpose; each records a difference
with TLC's trace.

| Configuration | Result | What it shows |
|---|---|---|
| `_prev` | FAIL `Inv_SetAgreesAll` | the one effect of `prev` |
| `_weak_seen` | FAIL `Inv_WeakAgreesSeen` | weak drops force for acts the end saw |
| `_weak_reaccept` | FAIL `Inv_WeakAgreesReaccept` | ANY over a re-acceptance |
| `_tie_any` | FAIL `Inv_EndReachesWhatNamesIt` | the tie |
| `_tie_bound` | passes | |
| `_line_tips` | FAIL `Inv_TargetCannotVoidEnd` | guard (b) |
| `_line_acts` | FAIL `Inv_AsOfStands` | the line applied to authored acts |
| `_receipts_resign` | FAIL `Inv_ResignNeedsNoCooperation` | receipts counted only in the end's past |
| `_receipts_any` | FAIL `Inv_EnderDecidesForce` | receipts counted wherever held |
| `_receipts_past_rotation` | FAIL `Inv_RotationKeepsReceipted` | receipts counted only in the end's past also lose a co-holder's receipt at a rotation |
| `_receipts_past_sound` | passes | the main invariants but those, under `RSCOPE = "past"` (the main configuration runs `"any"`, the recommended scope), and without `Inv_ReceipterBeforeStands`, which also needs a receipt the end does not name; 1,170,592 states |
| `_who_none` | FAIL `Inv_RotationKeepsReceipted` | (d): only the count's receipts; a rotation lifts the co-holder's receipt |
| `_receipt_removed` | passes | one act, two chained receipts, removals of the ender's or D's key; 2,677,518 states |
| `_reaccept` | passes | the main invariants with B's re-acceptance (`Inv_ReacceptUntouched`); 2,439,732 states |
| `_owner` | passes | one head only, the uncited act included; 93,951 states |

## A. Persist's question: acts that name nothing

**Persist's own words: the answer is (a). The act names its head, which its node knows.** (b), a head derived
by the reader from the rows that cite the act, does not decide it. (c), a head recorded at admission, is
arrival order and is ruled out.

What the model shows for an uncited act u1 (no head, no names) under the weak reading:
- **The hypothesis holds for force.** u1 is concurrent with every end. Once the end is held it is out of
  force, whether it was signed before or after the end (`Inv_NotInForceFromEnd`). For "in force now?" the 47
  producers need nothing.
- **"Valid when made" is undecidable, and the model shows it literally.** A history where u1 is signed before
  E and one where it is signed after E are the same TLC state: the held rows are a set and u1's row is
  identical in both. No reading over rows can tell them apart, so no rule can decide whether u1 preceded the
  end.
- **(b) fails.** A counted row R at head h that cites u1 bounds u1 from above: u1 was made no later than h.
  It does not bound it from below, and it is per citing row: two counted rows at different heads give u1 two
  "heads". The reader can decide "may R use u1 at h?" (no, if h is later than `h_e` or R has the end in its
  past). It cannot decide "was u1 valid when made?", which is what persist's four cases ask:
  1. a late arrival;
  2. a re-fold;
  3. an as-of walk over a resigned official's verdict;
  4. an attestation consumed long after its grant ended.
- **A receipt gives u1 ancestry relative to the end** (the receipt names u1). That decides "still in force",
  not "valid when made": an unreceipted u1 is still undecidable.

With (a), the model gives persist's required cases:

| Case | Result |
|---|---|
| An act naming a head, arriving after the end is held at a node that never saw it | Admitted. The door needs only what it names, and refusing it would be arrival order. Its answer is the set function: counted at its own head if that head is not later than `h_e`, out of force; and the same as at node 2, which held it earlier (`Inv_NodesAgree`, `Inv_Fold`; plant `arrival`). |
| The same act re-folded after the end | The same answer. The end never changes what counted at a head not later than `h_e` (`Inv_EndNeverUnmakes`). |
| An act naming a head newer than `h_e` | Does not count (E3), unless the ender's own concurrent receipt gives it one say: counted at its head, out of force. |
| A signer whose node was behind: it names old head H0, made after the end was published elsewhere | Counts at H0 and is out of force from `h_e`. It can't be told from an honest act made at H0 before H1, and no rule should try: see section C on the line. |
| An as-of walk | A verdict counted at its head stays counted for every reader (`Inv_AsOfStands`). |

## B. Weak + ender's receipts

**1. Is it sound?** Yes, with receipts counted wherever held (`RSCOPE = "any"`). The main invariants hold
under both scopes (the main configuration runs `any`; `_receipts_past_sound` runs `past`). Receipts never touch whether the end counts, so nothing reopens
what `Inv_TargetCannotVoidEnd` or the line guards. The cases:

| Case | Result |
|---|---|
| A receipt concurrent with the end | `past`: it keeps nothing (one say still applies to a later-head act). `any`: it keeps the act in force. Trace `_receipts_any`: b1, A's receipt Q1 of b1, A's end E naming neither. |
| A receipt by a key later removed | A removal concurrent with the receipt voids it, and the act loses force; one in the removal's past stands (`_receipt_removed`, 1,340,098 states). |
| Two receipt chains, one per ender-side device | Each chain is its own signer's series. Under `past` the end keeps only the chain it names; under `any` both count. Nothing is lost or forged either way: the grantee can't fork the ender's chain. |
| A receipt naming an act signed after the end | Impossible for a receipt in the end's past: it would make the end its own ancestor. A receipt that names the end is excluded under both scopes. A receipt of an act at a later head never revives it (`Inv_ReceiptForwardOnly`). |
| A grantee who is also on the ender's side | Its receipts never count for its own acts (plant `self`, caught). |

**2. Does it need `under`?** No. Under ANY-STANDING, an act grant D authorises stays counted and in force on
D's grant whatever A's side does. A's receipt matters only against A's end. Trace `_tie_bound`: grants A and
D, A ends, A's side receipted the act; it holds every main invariant. Which standing an act used is not needed
to decide whether an end keeps it.

**3. Who may receipt?** The conferrer and the co-holders, never the grantee. With `RSCOPE = "past"` (only
receipts the end names), a resignation lifts every co-holder's receipt the resignee chooses not to name. Trace
`_receipts_resign`: D's receipt Q1 of b1; B resigns naming nothing; b1 loses force. So the Constitution's hope,
that a resignation needs no cooperation from the one leaving, needs `RSCOPE = "any"`. That has one price,
found as `_receipts_any`: a receipt the ender does not have in its past keeps an act in force against the
ender. It is acceptable, because the exposure is bounded:
- only acts at a head not later than `h_e`, not naming the end;
- only by the conferrer or a co-holder, whose own standing covers the act;
- never by the grantee;
- never by a removed key.

The residual risk is a colluding co-holder receipting, concurrently, an act the grantee signed after the end
at an old head. Without instants that is indistinguishable from an honest receipt. CC 4.5.5 points the same
way.

**4. Cost.** The 10 ending sites name `h_e`, and one receipt producer signs ordinary Acks. With
`RSCOPE = "any"` the end need not name receipts at all, and the receipt chain is optional. Receipts need
nothing on the 47 acts. "Valid when made" does need heads on the acts (section A), which persist has chosen.

**Heads or receipts?** Both, for different halves. "Counted at its own head" gives "valid when made", so a
resigned official's verdict still reads as a verdict. Receipts decide only "still in force" for durable
effects such as a withhold. `Inv_ReceiptsChangeOnlyForce` checks that receipts never change a count.

## C. The reader's line is not for authored acts, and not for tips

Applied to an authored act that names its head (`_line_acts`), CC 2.7.8's line voids, for a reader that
acknowledged H1, every act at H0 that H1 does not have in its past. That is every honest act made at H0, with
no end anywhere. Trace: b1 at H0, H1, the reader acknowledges H1, b1 void. That destroys "valid when made" for
as-of walks.

So the line stays what it is: a rule for counted rows (versions, votes, cuts, the end itself). An authored act
that names its head for E2 and E3 is not a counted act for CC 2.7.8.

Guard (b), the line moved onto series tips, lets the target void its own end (`_line_tips`):
1. b1, then b2;
2. the end acks b1;
3. a reader acknowledges b2;
4. the end is void for that reader.

Drop it.

## D. Root grants and owner bindings

**A root grant.** Its heads are the genesis bundle's versions, and `h_e` is the newest bundle version the
ender holds. In the model, H0 and H1 play the bundle versions; nothing changes.

**An owner binding** (two keys, no roster). Persist leans to "the binding row itself is the head". The model
does not disagree (`_owner`: one head, the uncited act included, every main invariant holds):
- there is only one head, so E3 never applies;
- every act concurrent with the end counts at the binding's head and is out of force from the end on;
- receipts keep the receipted ones in force.

The limit to state: with one head, "valid when made" for an act concurrent with the end is always yes. A
device that never saw the end can keep signing acts that count at the binding's head, though never in force.
That is the most a two-key standing can say without instants. The end's own row as a degenerate head gives
the same answers.

**Bundle standing** (an accord holder's standing is a bundle with an object id). Under the weak readings
nothing names the standing. The seat walk at the act's head finds it, and the answers are those above. Only
the full proposal's `under` would need an object-id form.

## E. The earlier questions, briefly (unchanged by this round)

**The five cases.** "Count" is whether the act counts at its own head; "force" is whether it is in force from
`h_e` on.

| Case | Count | Force |
|---|---|---|
| In the end's past | yes | yes under full and set; no under weak; yes under weakR if receipted |
| Concurrent, at or before `h_e` | yes | no, unless receipted |
| Concurrent, at a later head | no (one say: yes) | no |
| Naming the end | no | no |
| The end and a concurrent removal of the ender's key | the end changes nothing (`Inv_RemovalVoidsEnd`) | |

Withdraw and re-accept on two devices:
- full: acts under `a2` are untouched;
- weak: ANY over `a2` (`_weak_reaccept`);
- a counted scope still needs a version listing the key again (`readmission_needed`, `leaving_binds_by_past`).

**Backdating.**
- A grantee who never cites the end counts only at heads not later than `h_e`, never in force. A vote at an
  old head forks the newer one, and CC 2.7.8 bounds that version for readers who acknowledged the newer head.
- An ender who acks nothing reads every act as concurrent.
- An ender who acks an old tip keeps only what lies behind that tip.
- An ender who names an old head reaches the heads in between. E1, one say and the line on the end bound it.

**Convergence.** Every answer is a set function of the held rows and the reader's own acknowledgement.

**The members hazard.** Caught.

**`prev`.** Not needed. It differs from an ack set only when a device cites the end and then stops citing it,
and a forked `prev` gives the grantee the same effect, so readers can't rely on it. Cost per reference is 32
bytes:

| Design | Cost |
|---|---|
| `prev` + `ack` of tips | 32 B per act, plus 32 B per tip |
| `ack` set, no `prev` | 32 B × the history the ender holds |
| weak | 32 B per end |

## F. Exercised acts on the seat's slot

The slot ("seat", k, s, o) holds offers and acceptances only (`seat.py`). Its cut has no heads:
- `Seat.lean` `rowVoided` and `outsider_row_never_counts`;
- `cut.rs`.

Put exercised acts there, and an unseat voids every concurrent act at its own head: the `own_head` plant. The
holder rule (`Cut::holder`, `holder_both_or_neither`) would also read two concurrent device acts as `Conflict`.
No proof assumes acts are absent, because none puts them there. Keep them off.

## G. Who receipts

The case is a conferrer that is a COUNT: a root grant whose conferrer is the bundle's holders at 2 of 3, and a
CI worker attesting builds. A counted receipt for every build will not happen.

In the model:
- A is the body's count, and its receipts are counted rows: a bulk receipt is the same rule applied to each
  act it names.
- D is a single co-holder.
- R is a receipter the grant names. Its seat is conferred by the body, which ends it with Rx.
- B is the grantee.

An end by A is a count end and may carry `lifts`; an end by B is a self end. The main configuration runs all
of it at 1,170,592 states.

**(a) One holder's receipt, refined.** The refinement holds and does not bring back `_receipts_resign`:

| End | What a single co-holder's clean receipt does | Checked by |
|---|---|---|
| A self end (a resignation, one's own withdrawal) | keeps the act in force | `Inv_ResignNeedsNoCooperation` |
| A count end without `lifts` (a rotation) | keeps the act in force | `Inv_RotationKeepsReceipted` |
| A count end with `lifts` (a compromise) | keeps nothing; only the count's own receipts keep anything | `Inv_CountEndLiftsSingles` |

A self end cannot lift co-holders' receipts. The plant `selflift`, a resignation carrying `lifts` that is
honoured, is caught as `Inv_ReceiptedStays`.

The price is now only this: one holder keeps an act in force against a rotation, which by its own flag says
the grant was not compromised. If the receipting holder is the one compromised, the body removes that key, and
a receipt not in the removal's past counts for nothing (`_receipt_removed`).

**(b) The grant names a receipter.** This is a delegation of acknowledging: the body confers it and can end
it.
- R's receipts made before the body ends R's seat (in Rx's past) stand (`Inv_ReceipterBeforeStands`).
- A receipt that names Rx keeps nothing (`Inv_ReceipterAfterItsEndNothing`; the plant `after_rx` is caught).
- A receipt concurrent with Rx counts. Like any act concurrent with an end, it cannot be told from one made
  before it.
- A count end with `lifts` overrides R as it overrides D.

**(c) A serve seat (a node) receipts.** Rule it out. A node is never anyone's consent, so a node's receipt is
either its owner's, which is (b) with the owner as receipter, or nobody's. It adds nothing over (b).

**(d) Nothing is durable past the end of a root grant.** Then a rotation lifts everything. In
`ConferralEnd_who_none.cfg`, `Inv_RotationKeepsReceipted` fails: a co-holder's receipt does not survive a
rotation. Every attestation must then be re-signed after every rotation, which is the cost (d) puts on the
worker.

**A lone duty holder in a room.** Nobody else holds the seat, so there is no D.
- **The members' count receipting in bulk before the end works.** It is the count's own receipt.
- **A bulk receipt after the end is excluded:** a receipt with the end in its past keeps nothing
  (`Inv_ReceiptAfterEndNothing`; the plant `bulk_after` is caught).
- But a count round has to happen before the resignation, which does not wait for one.
- **(b) is the cheaper answer:** the room names a receipter, such as its owner or a second seat. That
  receipter receipts as acts happen, needs no count, and is ended by the body like any seat.

**Recommendation: (a) refined + (b).**
- Single co-holders' receipts count against self ends and against rotations.
- A count end that carries `lifts` overrides them.
- A grant may name a receipter: a seat or the worker's owner. For a root grant, that is the CI worker's
  owner or an attestation-receipter seat. For a lone duty holder, it is the room's named receipter.
- Not (c), and not (d).

Wire cost:
- a `lifts` flag on count ending rows, which are among the 10 ending sites;
- an optional receipter field on the grant (the offer);
- receipts by the receipter, from the same one receipt producer.

## For the Constitution to vendor

> **CC 2.4.1.1, the end of a conferral.** Every act names the head it is at. An ending row (a withdrawal of an
> acceptance, a holder's or a count's withdrawal of an offer, an unseat, a resignation) names the head it acts
> from. That is the newest head its signer holds, and the end concludes nothing if a newer head is in its own
> past. The end concludes as a cut under its signer's own standing at that head: one's own acceptance needs
> only its own signature. It reaches only the acts exercised under its target, deputies transitively, and
> never the member set at any head. An act that has the end in its past does not count. Any other act under
> the target counts at its own head if that head is the end's or older, or concurrent with it, and from the
> end's head on it is not in force. An act at a later head finds the standing ended and does not count, unless
> the ender holds a clean receipt of it concurrent with the end; then the ender has no say on it at that head
> (CC 2.7.7 rule 6). An act stays in force after the end when the conferrer or a co-holder of the body it was
> done for, or a receipter the grant names, not its own signer and not a node, holds a clean receipt of it that does not have the end in its past (CC 4.5.5).
> A co-holder's or a named receipter's receipt counts against a resignation and against a rotation; a
> count's end that lifts receipts (a compromise) leaves in force only what the count itself receipted. A
> receipter's receipt made after the body ended its seat counts for nothing.
> An act that another live standing of its signer authorises at its head stands on that standing. The
> reader's line (CC 2.7.8) applies to the end as to any counted cut, and not to an authored act.
