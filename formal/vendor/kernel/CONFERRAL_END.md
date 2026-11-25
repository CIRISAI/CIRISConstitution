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
  A receipt, once sent, is never withdrawn (the Constitution's ruling of 2026-11-23): a row withdrawing one is
  refused at the door, and if one were held nothing reads it (case `receipt_never_withdrawn`). The ruling
  rests on reading the rules, not on a run: the TLA+ spec has no such row. Read otherwise, the ender's
  withdrawal of its own receipt would take back its one say (E3) and change a count, and a single receipter
  could drop what only a count end with `lifts` may. A single key's mistaken receipt is undone by the count's
  end with `lifts` or by a removal of that key concurrent with the receipt. A count's own mistaken receipt
  has no undo in this rule.
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

## H. Conformance fixtures for persist

The fixture is `crates/ciris-kernel/tests/fixtures/conferral_end.json`, in the kernel's fixture format. It has
35 cases and 51 act answers. Each act has `counted`, `in_force` and the `rule` that decides it, and 12 rules
appear.

The same cases are a plain table, one line per act, in `conferral_end.tsv` next to it. That is the
Constitution's case table for CC 2.4.1.1. The text of rc22 3a8a033 is checked against the model in
`CONFERRAL_END_TEXT_CHECK.md`.

It is generated by `tools/kernel_fixtures.py` from the reference `models/causal_kernel/conferral_end.py`, which
is the weakR reading of this spec, and checked in three ways:
- `check_conferral_end.py` checks the hand-written answer of every case in every arrival order;
- `kernel_fixtures --check` checks that the fixture is current;
- `tools/conferral_xcheck.py`, run by `tools/tla_check.sh`, compares the reference with this spec over every
  state of `ConferralEnd_xcheck_all.cfg` and `ConferralEnd_xcheck_none.cfg`. There, `DUMPANS` puts the spec's
  own answer in the state.

Over those two configurations and two larger ones run once (`_xcheck_removal`: the uncited act and key
removals; `_xcheck_two`: two acts on two devices), the reference and the spec agree on 101,522 act answers
at 60,082 distinct held states. While I built it they disagreed once, on 170 answers in `_xcheck_two`, and
the spec was wrong. Its weak readings read a receipt's past, and the one say's concurrency, through acts'
`prev` edges and the end's `ack`, which the weak wire does not carry. In the trace, b1 cites the end and b2
has `prev` b1, so a receipt of b2 looked as if it had the end in its past. The spec now reads each
reading's own past (`AncV`: full, `set` without act `prev`, weak without act `prev` or the end's `ack`). That
changed no earlier conclusion. It did bring out one more difference between the full and weak readings,
which the large run found and `Inv_WeakAgrees*` now excludes by name (`AckCut`). Under full, an act the end
acks is in the past of a removal that names the end, so a removal of the grantee's key does not cut it. Under
weak the end acks nothing, so the removal cuts it unless the removal names the act itself.

The cases:
- persist's six;
- the receipt cases: after a self end, after a rotation, lifted by a compromise, a self end that cannot lift,
  a receipt after the end, the receipter before and after its seat's end, the grantee's own receipt, a
  receipt by a removed key, and (d);
- acts that name no head (marked `refused` in the fixture: the text refuses them at the door);
- the base cases, one say, naming the end, the tie, the re-acceptance and the deputy;
- the end's own voids: a stale head, the line, and a removed key.

## I. Room content: the end names the rows held good (a proposal, checked by run)

This section checks a proposal the Constitution made on 2026-11-22 (second form). It is not a ruling, and it
is checked by an exhaustive run in Python, not by TLC: `ConferralEnd.tla` has one end per run and no row that
adds tips, so two ends and growing tips are outside it.

**The problem.** After a member's seat ends:
- reading the room's content by `in_force` hides that member's whole unreceipted history;
- reading it by `counted` lets them keep adding rows at the last head they sat at, which no rule can tell from
  an honest late row;
- a receipt per content row by co-members is a signed "seen" per member per row.

**The proposal**, as it stood after persist and Edge read their code against it:
1. A content row (a message, a file placement, a reaction, an edit or a retraction of one) is an act under its
   signer's membership. On the wire each is a composer its author signs. It names its roster head and, in
   `prev`, its author's current newest content rows in the room: a set of predecessors. One identity key is
   held on all of a person's devices, so a series forks routinely, and a row naming both branches joins them.
2. The row that ends the seat (a counted removal, or the member's own resignation) names in `trusted_through`
   the newest rows of the member its signers hold good: the tips, a set (the text caps it at 64).
3. The end never waits on a tip. It concludes on its own terms; a tip not yet held keeps nothing until it
   arrives, and one that never arrives keeps nothing.
4. After the end, a content row of the member is in the room's content when it is a held tip or an ancestor of
   one along `prev` among its author's own rows. Every other row of theirs counts at its own head and is not
   in the content.
5. Tips only grow: a later counted row of the body may name further tips, and the kept set is the union.
6. No co-member receipts content.

**Is this the form section C dropped?** No. The dropped form (guard (b), `_line_tips`) moved the READER'S LINE
onto series tips: a reader that acknowledged a newer tip of the target's series held void an end that acked an
older one, so the target could void its own end by signing one more row. Here the tips are named by the ender
inside the end row, no reader's acknowledgement of a tip is read, and no end is voided by a tip. That failure
does not carry over. The proposal is the spec's full reading (the end's `ack` and the acts' `prev`) applied to
content: section E already says "an ender who acks an old tip keeps only what lies behind that tip".

**The reference and the run.** `models/causal_kernel/conferral_content.py` is the reference, and
`check_conferral_content.py` (a `./check.sh` step) checks it:
- 56 cases with a hand-written answer for every content row, each in every arrival order;
- every history of up to four rows: 850,987 histories, 3,569,415 extensions compared, over three sets of
  roster heads (the member seated throughout; admitted again at the second head, with a co-member also
  signing; seated, not listed, admitted again, one row shallower).
  A history has up to three content rows on two keys of the member, each naming up to two earlier ones as
  predecessors, or retracting one; up to two ends (a removal or a resignation, at either head, with up to
  two tips, optionally stale or naming the earlier end); and one row adding tips. A tip or a predecessor is a
  row signed earlier, since an id fixes its row; it need not be held, and every history is also read with
  each one of its content rows not held. Run once by hand at five rows with one key: 4,244,169 histories,
  17,759,924 extensions, nothing found;
- three plants, each caught.

**What the run found.**

1. **The union read literally lets an ended member add content for ever.** Point 3 says "every tip named". If
   the member's own ends are among those read, then after a removal that kept m1 the member signs m2 and a
   resignation at the head it last sat at, naming m2 and not the removal. That resignation is concurrent with
   the removal and counts at its head like any act there, so m2 enters the content (fixture case
   `removal_then_backdated_resignation_union`; plant `union`). The same holds with no removal at all: a second
   resignation naming more (plant `count_first_self_union`).

   The reference's default, `count_first`, closes it:
   - where a counted end counts, only the count's tips are read: the union over every counted end and every
     counted row adding tips;
   - the member's own ends are read only where no counted end counts, and then a row stays only where EVERY
     one of them holds it good, so a further resignation can take rows out and never add one;
   - a row adding tips signed by the member is never read (plant: caught);
   - after a resignation with no counted end, a counted row adding tips adds to what the member held good:
     the member's own tips are still read (`resignation_then_counted_tips`), and a further resignation narrows
     only those, never what the counted row named (`resignation_counted_tips_then_narrowing`).

   With that, `cannot_add` holds over the whole run: once an end counts, nothing the member signs afterwards
   puts a row into the room's content. No content row it signs later is ever in, and no end or tips row it
   signs brings an earlier row in.

2. **Whether an end counts must depend on its own causal past alone.** A first draft voided the member's own
   end where it named a head later than another end's. The run found the member reviving a row that way: it
   resigns at H1, signs a1 naming that resignation (not counted, E4), the count names a1 as a tip, and the
   member then signs a second resignation at H0, which voided the first and brought a1 into the content. The
   rule is gone. An end is void only for a stale head (E1) or for a counting end of the seat in its own past,
   and neither changes when rows arrive. An extra end of the member's own only ever takes rows out.

3. **Does monotone growth close?** The tips do: a counted row adding tips never takes a row out and changes no
   count (`tips_grow`, every extension). The content as a whole does not only grow, for two reasons that are
   E3, not the tips:
   - a further counted end at an older head takes out rows at later heads, and nothing else (`further_end`);
   - the member's own backdated end at an older head takes its own kept rows at later heads out. Among
     extensions by the member alone this happened 784 times, always by `E3.later_head`, and nothing else but the member's own
     retraction ever took out a row the count held good (`word_stands`). Section E lists this under backdating; the reader's
     line bounds it, and the line is not in this run.

4. **Two concurrent ends naming different tips.** Under `count_first` both are the count's word and the kept
   set is their union (`two_removals_different_tips`). Nothing waits, and the answer is a function of the held
   rows. That the two removals are also two tips of the roster is the line's business, as for any counted row.

5. **Nothing waits on content.** A tip does not make an end wait, and a predecessor does not make a content
   row wait. The run reads every history with each one of its content rows not held. `cannot_add` holds
   there too, a late row's arrival never takes a row out unless it is a retraction of that row, and it
   changes no count (`arrival_grows`). The answer is the same in every arrival order once the rows are held
   (`tip_arrives_after_end`, `middle_of_chain_arrives`). With a predecessor in the middle of a chain not
   held, what lies behind it is not kept until it arrives (`middle_of_chain_not_held`). That an ended member
   cannot supply a different row for an id already named rests on the id being a digest of the row; the run
   takes it as given and does not check it. What the unwaited form admits:
   - an end naming a tip that never arrives keeps nothing, and no rule tells it from an end that names none
     (`end_names_tip_never_held`). A node must keep the end's tips to apply a late arrival;
   - a resigning member may name a tip it has signed and not published, and publish it later with a chain
     behind it. Those rows were signed before the resignation that names them, at heads the member sat at;
     the member cannot choose them afterwards. Under a waiting end they would have had to arrive first.
   - naming a tip never makes it count: a tip at a head later than `h_e`, or one that has the end in its
     past, stays out (`tip_at_later_head`).

6. **Predecessors as a set.** The walk from a tip follows every `prev` that is a row of the same key, so a row
   that names two branches keeps both under one tip (`fork_rejoined`), and an end may name several tips of
   one key (`fork_both_branches_named`). Nothing new opens: a row signed later is never an ancestor of a tip
   named earlier. A predecessor that is another key's row is not followed.

7. **A composer does not follow its target.** An edit or a retraction is a content row and is kept only where
   a tip holds it good. If "a composer on a kept row follows its target" meant it is kept because its target
   is, an ended member would rewrite its kept posts for ever (`kept_post_edited_after_end`: the edit is out,
   the post stays as the count held it good).

   A retraction is the exception, by the Constitution's ruling of 2026-11-22: an author's retraction of its own
   row takes effect whenever it is signed. The retraction row itself is out like any row no tip names, and its
   target leaves the content all the same (`kept_post_retracted_after_end`, rule `W.retracted`). It holds
   whether or not the retraction counts as an act under the ended seat, only for the row's own key, and a
   retraction of a retraction restores nothing. The run checks that a retraction never puts a row into the
   content (`retract_removes`).

8. **The costs are as the proposal states them**, each a fixture case:
   - a row in flight when the removers signed is out for everyone until a counted row names it
     (`removal_in_flight_row`, `in_flight_row_named_later`);
   - a key the enders never saw sign has its whole series out until named (`second_key_never_seen`);
   - in a forked series only the named branches stay (`fork_of_one_series`); a branch the enders did not hold
     waits for a later counted row.

**The node-local fallback** (a row a reader held before it held the end stays shown to that reader) is not part
of the proposal, and the reference keeps it apart (`shown_first_held`).
- It is the spec's `arrival` plant: an answer latched on arrival, which `Inv_Fold` and `Inv_NodesAgree` exist
  to catch. In 24 of the 56 cases two arrival orders of one set of rows show different rooms.
- In 24 cases it shows a row the proposal keeps out. That includes a row the member signed after the removal
  that reached a node before the removal did, so it does not keep such rows out "everywhere": it keeps them
  out only at nodes the end reached first.
- A node that folds again from its rows (a cold start, a checkpoint) loses the order unless it stores it.
- It breaks no count and neither bit of the model if it is kept as a third, local bit that nothing else reads.
  If anything reads it (a tally, a further row, a key wrap), nodes diverge in effect.

9. **A member seated again: seat by seat.** A seat is one stay, from the roster version that admits the
   member to the end of that stay. A content row and an end belong to the seat of the head they name, a row
   adding tips to the seat of the end it extends, and each seat's content is judged by that seat's own ends
   and tips alone. Checked over histories with a second seat:
   - a row at the re-admitting head is in the content, with no end of that seat (`rejoin_and_post`);
   - the head a row names decides: a row signed after the re-admission that names the old head is a row of
     the old seat and is out (`stale_device_after_rejoin`);
   - a re-admission restores nothing (`rejoin_restores_nothing`);
   - the walk from a tip does not cross seats. Rejoining, posting a row that names left-out rows as its
     predecessors and leaving with that row as the tip brings nothing back
     (`second_seat_tip_reaches_left_out_row`). `cannot_add` holds per seat over the whole run;
   - a row naming a head at which the member does not sit belongs to no seat and does not count
     (`row_between_seats`, rule `no_seat`);
   - a counted row may still add tips for the first end after the rejoin (`keeps_first_end_after_rejoin`);
     a tip that points at a row of another seat holds nothing good (`first_end_names_second_seat_row`);
   - a retraction is read across seats (`retract_old_post_after_rejoin`).

10. **"The member's own" is by member, not by key.** A predecessor signed by another key of the same member is
    followed, and a retraction from a second device takes effect (`prev_across_the_members_keys`,
    `retraction_from_a_second_device`). A co-member's row is never followed and a co-member's retraction is
    not read; in the run a co-member's row changes no answer (`co_member_inert`).

**For the Constitution to settle; the run does not.**
- Which `merge`. The run supports `count_first`; `union` is unsafe.
- A row adding tips is a counted row of the room. The Constitution has said it names the head it is counted
  over and the end it extends. The reference carries that head and no rule reads it; the reader's line on it
  is not in this run.
- A resignation's tips are the member's own word about its own rows. That is harmless here, since those rows
  were signed at heads it sat at, and a second resignation can only remove.

**Not modelled here:** receipts together with tips; the reader's line on an end; key removals; more than two
seats; more than one room.

## J. One row that needs two standings

A node that is its owner's by an owner binding and holds a duty by a root grant signs one row (a build row).
CC 3.1.2.1 has it name the bundle in force, and says a new owner must accept the grant "before it confers for
acts under the new binding". With one head named, nothing places the act against a re-binding.

`models/causal_kernel/check_conferral_two.py` judges the act under each record with the reference of sections
A to H and joins the answers bit by bit: the act counts for an owner when it counts under the grant and under
a binding of that owner, and it is in force when it is in force under both.

- The grant: head G0 (the bundle in force) and the count's end EG.
- The binding: B0 (the node is O1's), B1 (a re-binding to O2, naming B0), B2 (a re-binding back to O1, naming
  B1). Each re-binding ends the binding before it.
- A0, A1, A2: the owner's acceptance of the grant under B0, B1, B2.

Each history fixes, for every act, how far along B1, A1, B2, A2 its signer had got when it signed, which the
graph does not show. An honest node names the newest row of its reading that it holds. A backdating node
names what it would have named under an earlier binding. Every set of rows a reader may hold is judged: 1,344
histories, 238,140 states over the five readings, about 12 s.

| Reading | What the act names beside the grant's head | What an acceptance names | Result |
|---|---|---|---|
| `one` | nothing | its binding | breaks five properties |
| `named` | the binding row it is under | its binding | breaks `consent` |
| `named_acc` | B0, or under a re-binding the owner's acceptance | its binding | holds all seven |
| `acc` | always the owner's acceptance | its binding | holds all seven |
| `acc_bare` | always the owner's acceptance | the grant only | breaks four once an owner is bound a second time |

The seven properties:
- `old_owner`: an honest act signed holding a re-binding does not count under a binding before it. Under
  `one` it does: the act does not name B1, so it is concurrent with the re-binding and counts at B0.
- `consent`: an act counts under a binding only if its signer held that binding's acceptance when it signed.
  Under `one` and `named`, an act signed before the acceptance counts for the new owner once the reader holds
  the acceptance: a later acceptance adopts acts the new owner never saw.
- `one_owner`: no act counts for both owners. Under `one` an act signed before the re-binding does.
- `kept`: an honest act signed under an accepted binding counts under it once the reader holds what its
  signer held.
- `backdated`: a backdated act counts under no later binding than the one it names, and is in force under
  that one only by its owner's own receipt. It still counts there, out of force: the limit section D states
  for any two-key standing.
- `ended`: an honest act, not receipted, is in force for nobody once the reader holds the re-binding that
  ended its binding. A later binding to the same owner restores nothing.
- `grant_end`: once the reader holds EG, an act the count did not receipt is in force for neither owner.

**The rule the run supports (`acc`).** A row signed under a root grant names the bundle in force and the
acceptance of that grant it stands on. The acceptance names the owner binding it is made under. An act that
names a binding row itself, or the bundle alone, stands on no acceptance and counts for nobody. The
Constitution has ruled that "before" is meant (2026-11-23), which excludes `named`.

**Why the acceptance names its binding.** With one re-binding, `acc_bare` holds all seven properties: the two
owners have different acceptances and the act names one of them. It breaks when O1 is bound again (B2). O1's
one acceptance then serves both of its bindings, and a reader cannot tell an act signed before B1 from one
signed after B2: the first comes back in force (`ended`), and so does a backdated one. If O1 instead signs a
fresh acceptance that names no binding, no reader can say which of O1's two acceptances belongs to which
binding without an order the graph does not give. That second point is an argument, not part of the run.

"The binding in the act's causal past" is not a separate option. A row has in its past only what it, or a row
it names, names. So the binding is in an act's past only when the act names it or names a row that does.

**Fixture.** `crates/ciris-kernel/tests/fixtures/conferral_two.json` has 11 cases under `acc`, each with a
hand-written answer per act and owner that the run must give. No Rust test reads it. It is for Verify's
standing walk and an adopter's own code.

**For the crate.** No new code: a caller runs `conferral::answers` once for the grant and once per binding,
and joins the answers bit by bit.

**Limits.** This is a Python run over the reference, not a TLA+ configuration. It has one grant head, two
re-bindings, at most two acts, and one receipt per record (the first owner's, and the count's). Not modelled:
the new owner declining or withdrawing its acceptance, a grant end concurrent with a new bundle version, a
new bundle version at all, the reader's line, a receipt by the second owner.

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
