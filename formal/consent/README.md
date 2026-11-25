# `formal/consent` — the consent plane, model-checked

**Why.** The consent plane has four state-table variables (`consent.state`, `consent.decay`,
`consent.community_trust`, `consent.replication`). This module realises all four and checks the
properties listed below, which state some of what CC 3.3.1, 3.3.7, 2.4.1.1 and 2.6.7 say about them.
Among them is CC 3.3.1's revocation authority: the owner may author the capture grant, and the node,
the owner and the agent key may each withdraw. What the module leaves out is listed at the end. The
largest omission is the fold itself: CC 3.3.1 folds each party's rows apart, and this module folds
every party's rows under one boundary.

A run here is a search of every state inside the bound below. It is not a proof beyond that bound.

**What it models.** One receiver, holding the rows it admitted in admission order (the index is the
attestation-id order used for ties). Two consent series share one fold:

- **`st`, `consent:state`.** The subject grants and revokes. A grant carries a `scope` (none, or
  `analyze`) and optionally a `valid_until`. The substrate emits `expired` naming the lapsed grant
  in `consent_supersedes`. An `analyze` use (the Score action) happens only on a live grant whose
  scope names `analyze`.
- **`ct`, `consent:community_trust`.** The capture grant for one node's sealed traces. The node, or
  its owner at the head the grant names, grants. The node, the agent key, or the owner at the head
  the revocation names, revokes. A trace at instant `now` is captured only if the fold says granted
  at `now`.

**Two readings, kept apart.** CC 2.4.1.1: an act names its head, it counts at that head, and no
instant decides.

- **Standing is read at a named head.** A `ct` row names the owner-binding the node signs under. The
  node has two bindings: `B1` (owner `o1`), and `B2` (owner `o2`), which replaces `B1` at receiver
  clock `TX` and reaches this receiver then or at any later step, or never. A grant counts when its
  signer is the owner at the binding it names, or is the node and lists that owner (CC 3.3.1: "MUST
  list, in `subject_key_ids[]`, the key that is its owner **at the head the grant names**"). A grant
  that names no binding is no consent of this node's. A grant that names a binding the receiver does
  not hold waits. The verdict reads the signer, the head and the listed owner. It does not read
  `asserted_at`, the clock, or the newest binding the receiver holds.
- **The consent window is read from `asserted_at`.** `R` is the latest admitted revocation's
  `asserted_at`. Every grant at or before `R` is out. Among the grants after `R` the latest
  `asserted_at` wins, and ties go to the smallest attestation id. No grant means no consent. On `st`,
  a winning grant whose `valid_until` has passed reads `expired`. This is a window, not a standing,
  and it is as it was.

**Admission freshness (CC 2.6.7).** The instant the window reads is signer-chosen, so it is bounded:
a row whose `asserted_at` precedes the receiver's clock by more than `W`, when the receiver first
holds it, is refused (`asserted_at_stale`) and moves nothing. CC 2.6.7: "The window decides no
standing."

**A row that waits.** CC 3.3.1: "A grant whose binding rows have not yet arrived is held, as every
owner-gated row is." CC 2.6.7 checks a row's age "at the node that first receives it". So a row that
names `B2` and reaches a receiver without `B2` is held and not counted. Its age is judged at that
first holding. When `B2` arrives the row is counted with the `asserted_at` it carries, however long
it waited. The model keeps no queue: at the clock `B2` arrives it counts any row that could have
been waiting, and a row counted that way records when it was first held (`rcv`) and when it was
counted (`adm`). The count is a step of its own, so inside that one clock a capture may fall between
`B2` and the count.

This has a consequence the text does not state. `W` bounds how far a row is dated before the
receiver first holds it. It does not bound how far it is dated before it is counted. A revocation by
the new owner that waited on `B2` covers the instants of captures decided while it waited, further
back than `W` (`Wit_WaitedRevocationReachesPastW`; the wider bounds `Inv_CountedWithinW` and
`Inv_LateRevocationWithinW_Waited` are both violated). No capture is unmade by it: a boundary puts
out grants and never the traces already captured (CC 3.3.1).

**The adversary.** It signs as a stranger. It signs as the withdrawn owner `o1` after `TX`, at head
`B1` or naming `B2`, with any `asserted_at`. It names any binding that exists, or none, on any row,
and a node-authored grant lists either owner or none. It backdates any party's row within and beyond
`W`. It forges `expired` under a non-substrate key. It grants replication as a stranger. Replay needs
no action of its own: a replayed admitted row deduplicates on its attestation id, and a replayed
refused row reaches the verdict it reached before.

**Decay and replication.** The agent's consent module walks `identity_severed`,
`patterns_anonymized`, `complete`, once the `st` fold reads revoked or expired, under weak fairness.
`consent:replication` (CC 3.3.7) is a directed grant, one peer per grant, by the node or its owner.
The node ships captured traces to a peer only while a grant naming that peer is live.

## A tension in the text, reported and not resolved

Two sentences say what a replaced owner-binding does to a capture grant that counted under the old
one.

- CC 3.3.1: "So a later ownership transfer neither admits nor un-admits a grant already made, and
  every peer reaches the same verdict once the binding rows have replicated."
- CC 3.1.2.1: "Once a reader holds the binding that replaced an act's own, that act is in force for
  nobody unless it was receipted." CC 2.4.1.1 says the same of every standing: an act at an older
  head "counts there and is never in force after the end".

Both agree on the **verdict**: the grant counted at `B1`, and nothing later changes that. The model
checks this in both configurations (`Prop_TransferMovesNoVerdict`, `Inv_SameVerdictOnceHeld`). They
part on whether the grant still **authorises capture** at a receiver that holds `B2`. The constant
`InForce` carries each reading, and neither is chosen here.

| | `InForce = "counts"` (CC 3.3.1 read alone) | `InForce = "ends"` (CC 3.1.2.1, CC 2.4.1.1) |
|---|---|---|
| A grant at `B1`, after the receiver holds `B2` | stays in the fold | is out of the fold |
| A capture decided while holding `B2` | may rest on a `B1` grant | rests only on a `B2` grant |
| The fold at the step `B2` arrives | unchanged | goes from `granted` to `none` where a `B1` grant was winning |
| The withdrawn owner `o1`, signing a fresh grant at `B1` after `TX` | is admitted and capture runs on it, at every receiver, with no bound | is admitted, and capture runs on it only at a receiver that does not yet hold `B2` |
| What the new owner must do for capture to run | nothing | ask the node to re-grant at `B2`, or grant itself |
| `Prop_TransferKeepsFold` | holds | **violated** (`Consent_ends_vs_331.cfg`) |
| `Inv_ReplacedBindingEndsGrant` | **violated** (`Consent_counts_vs_3121.cfg`) | holds |

Under `counts`, only a revocation ends the old owner's reach, and `o1` can sign a later grant at
`B1` after any revocation. A capture decided by a receiver that holds `B2` rests on a grant `o1`
signed at `B1` and that receiver admitted while holding `B2` (`Wit_WithdrawnOwnerGrantsHoldingB2`).
Under `ends`, the exception "unless it was receipted" is not modelled, so no `B1` grant is kept in
force.

The CC 3.1.2.1 sentence stands in the entry on a pipeline's capability grant and its owner's
acceptance. Reading it of a capture grant is this module's reading. CC 2.4.1.1 "The limit" says the
same in general words: "Where the record is one row, an act from such a device counts at that row
and is never in force after the end." The CC 3.3.1 sentence speaks of admitting and un-admitting,
which both readings keep (`Prop_TransferMovesNoVerdict`). If "admits" there means the verdict and
nothing more, the sentences do not collide and `ends` is what CC 2.4.1.1 gives. If it means the
grant goes on authorising capture, CC 3.3.1 is an exception to CC 2.4.1.1 and says so nowhere. The
text does not say which, and the choice is not this module's to make.

## What the head reading costs, in this fold

Under either reading the withdrawn owner `o1` keeps a revocation at `B1`: the row names `B1`, `o1`
is the owner there, and no instant is read. With one boundary over every party's rows, that
revocation puts out the new owner's grant at `B2`, at a receiver that holds `B2`, at any later time
and as often as `o1` signs one (`Wit_WithdrawnOwnerStopsNewOwner`, reached under both readings).
The reading this module had before bounded that to `W` after the transfer. CC 3.3.1's own fold does
not give `o1` this: there a party's revocation ends that party's consent, and `o2`'s grant binds the
node, `o2` and the agent key, and not `o1`. The module does not model that fold, so it shows only
that the single-boundary fold and the head reading together fail closed against the new owner.

## State-table realisation

| STATE_TABLE variable | Model expression | Values |
|---|---|---|
| `consent.state` | `FoldNow("st").v` | `none`, `granted`, `revoked`, `expired` |
| `consent.decay` | `decay` | `none`, `identity_severed`, `patterns_anonymized`, `complete` |
| `consent.community_trust` | `FoldNow("ct").v` | `none` is `absent`, `granted`, `revoked` is `bounded` |
| `consent.replication` | `p \in ReplPeers` per peer | `none`, `granted` |

## The bound, and what ran

Constants are the same in every configuration: instants `0..4`, `W = 1`, `TX = 2`, `valid_until` two
instants after the grant, at most three admitted rows (none in the `_form` configurations, which read
no row), one node, one subject, two bindings. Replication touches the rest of the plane only through
"some capture exists", so the configurations that search the capture fold run with no peer, and
`Consent_replication.cfg` runs two peers over two admitted rows. TLA+ tools 1.7.4.

Each bound was raised by one, once, by hand and outside `check.sh`, invariants only. All closed:
`W = 2` (7,587,288 states under `counts`, 4,755,650 under `ends`); `TX = 1` (5,045,600 and
3,071,448); `TX = 3` (1,939,624 and 1,354,896); instants `0..5` (10,839,198 and 6,401,146); four
rows over instants `0..3` (20,396,913 and 14,124,639); on `st`, `W = 2` with `valid_until` three
instants on (972,714) and four rows (9,553,465); replication with three rows over instants `0..3`
(10,759,560). These are one step each and say nothing of a fifth row, a third binding or a second
node.
`bash formal/consent/check.sh` runs every line below and exits 0 when each gives the verdict stated.

| Config | Mode, plane, `InForce` | Reading | TLC verdict |
|---|---|---|---|
| `Consent_head_counts.cfg` | `ruled`, `ct`, `counts` | standing at the named head; a counted grant stays in the fold | **closes**: every invariant and both action properties hold, 3,191,888 distinct states, depth 14 |
| `Consent_head_ends.cfg` | `ruled`, `ct`, `ends` | standing at the named head; a grant at a replaced binding is out of the fold | **closes**: every invariant and the action property hold, 2,042,150 distinct states, depth 14 |
| `Consent_head_form.cfg` | `ruled`, `ct`, no rows | the three checks of form, over all 450 `ct` rows the adversary can write | **closes**: 10 distinct states, depth 6 |
| `Consent_replication.cfg` | `ruled`, `ct`, `counts`, two peers, two rows | the replication grant and the send | **closes**: every invariant holds, 1,219,840 distinct states, depth 19 |
| `Consent_ruled_st.cfg` | `ruled`, `st` | the fold over the subject's stance; scope, expiry, decay; the three temporal properties | **closes**: 467,692 distinct states, depth 16 |
| `Consent_counts_vs_3121.cfg` | `ruled`, `ct`, `counts` | the CC 3.3.1 reading against the CC 3.1.2.1 sentence | `Inv_ReplacedBindingEndsGrant` violated |
| `Consent_ends_vs_331.cfg` | `ruled`, `ct`, `ends` | the CC 3.1.2.1 reading against the CC 3.3.1 sentence read of the fold | `Prop_TransferKeepsFold` violated |
| `Consent_instant.cfg` | `instant`, `ct` | planted: the owner at the row's `asserted_at`, the reading this module had before | `Inv_BackdatedGrantRefused` violated: after `TX`, `o1` signs a grant that names `B2` and is dated before `TX`, and it is admitted |
| `Consent_instant_stranger.cfg` | `instant`, `ct` | the same plant | `Inv_StrangerNeverGrants` violated |
| `Consent_instant_form.cfg` | `instant`, `ct`, no rows | the same plant | `Inv_InstantBuysNoStanding` is false: two rows that differ only in `asserted_at` reach different verdicts |
| `Consent_current_view.cfg` | `current_view`, `ct`, no rows | planted: the owner by the newest binding the receiver holds | `Prop_TransferMovesNoVerdict` violated: when `B2` arrives, `o1`'s grant at `B1` loses its verdict and `o2`'s gains one |
| `Consent_current_view_form.cfg` | `current_view`, `ct`, no rows | the same plant | `Inv_SameVerdictOnceHeld` is false |
| `Consent_no_boundary.cfg` | `no_boundary`, `ct` | planted: the latest grant wins whatever was revoked | `Inv_RevocationIsBoundary` violated |
| `Consent_literal_signer.cfg` | `literal_signer`, `ct` | planted: only the node may revoke the capture grant | `Inv_OwnerCanRecant` violated |
| `Consent_no_W.cfg` | `no_W`, `ct` | planted: no freshness bound | `Inv_BackdateBounded` violated |
| `Consent_any_scope.cfg` | `any_scope`, `st` | planted: an `analyze` use on a grant of any scope | `Inv_EmptyScopeMatchesNothing` violated |
| `Consent_forged_expiry.cfg` | `forged_expiry`, `st` | planted: an `expired` row from any key, naming any row | `Inv_ExpiryEmittedBySubstrate` violated |
| `Consent_eager_decay.cfg` | `eager_decay`, `st` | planted: decay starts whatever the fold reads | `Inv_DecayForwardOnly` violated |
| `Consent_decay_back.cfg` | `decay_back`, `st` | planted: a decay step may go back | `Prop_DecayForwardOnly` violated |
| `Consent_decay_stalls.cfg` | `decay_stalls`, `st` | planted: decay stops at `identity_severed` | `Prop_DecayCompletes` violated |
| `Consent_decay_never.cfg` | `decay_never`, `st` | planted: decay does not start | `Prop_DecayStarts` violated |
| `Consent_blind_send.cfg` | `blind_send`, `ct`, two peers | planted: the node sends to a peer no grant names | `Inv_ReplicationNeedsDirectedGrant` violated |

| `Consent_no_wait.cfg` | `no_wait`, `ct` | planted: a row that names a binding the receiver does not hold is judged at once | `Inv_HeldUntilBindingArrives` violated |
| `Consent_stranger_repl.cfg` | `stranger_repl`, `ct`, two peers | planted: a replication grant from any key | `Inv_ReplicationGrantHasStanding` violated |
| `Consent_tie_largest.cfg` | `tie_largest`, `st` | planted: a tie between grants of one instant goes to the largest attestation id | `Inv_TieOnSmallestId` violated |
| `Consent_stranger_ok.cfg` | `stranger_ok`, `st` | planted: a `consent:state` grant or revocation from any key | `Inv_StrangerNeverGrants` violated, by a stranger's row |
| `Consent_waited_counted.cfg` | `ruled`, `ct`, `counts` | not a plant: the ruled reading against a bound it does not give | `Inv_CountedWithinW` violated: a row that waited on `B2` is counted more than `W` after its `asserted_at` |
| `Consent_waited_reach.cfg` | `ruled`, `ct`, `counts` | not a plant: the same | `Inv_LateRevocationWithinW_Waited` violated |

`check.sh` also runs `no_boundary` with `Inv_RevokedOverridesGranted` alone and `no_W` with
`Inv_LateRevocationWithinW` alone; each is violated.

Before the three plants `no_wait`, `stranger_repl` and `tie_largest` were added, each of those
misreadings closed against every property the module then had (5,774,018, 3,420,441 and 453,472
distinct states): nothing checked the wait, who grants replication, or the tie.

**Witnesses.** The closing runs are not vacuous. Each scenario below is the negation of a `Wit_*`
predicate in the module, and `check.sh` requires TLC to reach it.

- Under `counts`: after `TX`, `o1` signs a grant at `B1`, it is admitted, and a capture rests on it
  (`Wit_OldHeadAfterTransfer`). A grant at `B1` is admitted by a receiver that already holds `B2`
  (`Wit_OldHeadWhileHoldingB2`). A capture is decided while holding `B2` (`Wit_CaptureHoldingB2`).
  The new owner grants at `B2` (`Wit_NewOwnerGrants`). The node re-grants at `B2`, listing `o2`
  (`Wit_NodeRegrants`), and grants at `B1`, listing `o1` (`Wit_NodeGrantsAtB1`). `o1` revokes at a
  receiver that holds `B2` (`Wit_O1RevokesHoldingB2`). A grant backdated within `W` is admitted
  (`Wit_BackdatedWithinW`). A revocation is admitted after a capture whose instant it covers
  (`Wit_LateRevocation`). A capture happens after a revocation, on a fresh grant
  (`Wit_FreshGrantAfterRevocation`). The agent key revokes, and `o2` revokes. A row that waited on
  `B2` is counted (`Wit_WaitedRowCounted`), and a capture rests on a grant counted more than `W`
  after its `asserted_at` (`Wit_WaitedGrantCounted`). A revocation that waited covers a capture
  decided before `B2` arrived, more than `W` after the revocation's `asserted_at`
  (`Wit_WaitedRevocationReachesPastW`). A capture decided holding `B2` rests on a grant `o1` signed
  at `B1` and the receiver admitted holding `B2` (`Wit_WithdrawnOwnerGrantsHoldingB2`). `o1`'s
  revocation at `B1` puts out `o2`'s grant at `B2` at a receiver that holds `B2`
  (`Wit_WithdrawnOwnerStopsNewOwner`).
- Under `Consent_replication.cfg`: a peer holds captured traces (`Wit_PeerHolds`).
- Under `ends`: the fold goes to `none` at a receiver that holds `B2` while it holds a `B1` grant
  admitted earlier (`Wit_FoldEndsOnArrival`). A capture is decided while holding `B2`, on a `B2`
  grant. `o1`'s grant at `B1` after `TX` still carries a capture at a receiver without `B2`. The node
  re-grants at `B2`. `o1` revokes at a receiver that holds `B2`, and that revocation puts out
  `o2`'s grant. A capture rests on a grant that waited.
- On `st`: the substrate emits `expired`. Decay reaches `complete`, and decay starts on expiry. An
  `analyze` use happens after a revocation, on a fresh grant. An `analyze` use rests on one of two
  grants of the same instant (`Wit_ScoreOnTiedGrants`).

## INVARIANTS

| Property | Statement | CC | Planted break |
|---|---|---|---|
| `Inv_RevocationIsBoundary` | No capture or `analyze` use at an instant after a revocation the deciding node held, unless it also held a grant dated after that revocation and not after the use. Stated without the fold. | 3.3.1, 2.4.1.1 | `no_boundary` |
| `Inv_RevokedOverridesGranted` | No use rests on a grant dated at the same instant as a held revocation. | 3.3.1 | `no_boundary`, run with this property alone |
| `Inv_StrangerNeverGrants` | No held row is a stranger's. A held capture grant names a binding and is that binding's owner's, or the node's and lists that owner. A held capture revocation is the node's, the agent key's, or the owner's at the binding it names. A held `st` grant or revocation is the subject's. Stated on the held rows, without the standing rule. | 3.3.1, 2.4.1.1 | `instant` (a capture grant that names no binding), `stranger_ok` (a stranger's row on `st`) |
| `Inv_HeldUntilBindingArrives` | No row that names `B2` was counted by a receiver that did not hold `B2`. Stated on the held rows. | 3.3.1 | `no_wait` |
| `Inv_BackdatedGrantRefused` | No held grant is `o1`'s and names `B2`: the withdrawn owner holds nothing at `B2`, whatever instant it writes. | 2.4.1.1, 3.3.1 | `instant` |
| `Inv_InstantBuysNoStanding` | Two `ct` rows that differ in `asserted_at` alone reach one verdict. Over all 450 rows the adversary can write. | 2.4.1.1 | `instant` |
| `Inv_SameVerdictOnceHeld` | A receiver without `B2` either waits on a row or reaches the verdict a receiver holding `B2` reaches. | 3.3.1 | `current_view` |
| `Prop_TransferMovesNoVerdict` | At the step `B2` arrives, no row that had a verdict gets another: the transfer neither admits nor un-admits. An action property. | 3.3.1 | `current_view` |
| `Prop_TransferKeepsFold` | At the step `B2` arrives the capture fold is what it was. Holds under `counts` only. | 3.3.1 | `InForce = "ends"` |
| `Inv_ReplacedBindingEndsGrant` | No capture decided by a node that held `B2` rests on a grant at `B1`. Holds under `ends` only. | 3.1.2.1, 2.4.1.1 | `InForce = "counts"` |
| `Inv_OwnerCanRecant` | While a grant stands, a revocation signed now by the node, by the agent key, by the owner at any binding the receiver holds (naming it), or by the subject (`st`), is admitted. The model's row budget is not counted as a party's limit. | 3.3.1 | `literal_signer` |
| `Inv_BackdateBounded` | No held row was first held more than `W` after its `asserted_at`. It says nothing of when a row that waited is counted. | 2.6.7 | `no_W` |
| `Inv_CountedWithinW` | No held row was counted more than `W` after its `asserted_at`. **Violated** under the ruled reading by a row that waited on `B2`. | none: the text gives no such bound | (the ruled reading itself, `Consent_waited_counted.cfg`) |
| `Inv_LateRevocationWithinW` | A revocation that did not wait on a binding, admitted after a use, reaches back to it only if the use's instant is within `W` of the revocation's `asserted_at`. | 2.6.7 | `no_W`, run with this property alone |
| `Inv_LateRevocationWithinW_Waited` | The same of every revocation. **Violated** under the ruled reading by a revocation that waited on `B2`. | none: the text gives no such bound | (the ruled reading itself, `Consent_waited_reach.cfg`) |
| `Inv_TieOnSmallestId` | The grant an `analyze` use rests on has no held grant of the same instant before it. Checked on `st` only. | 3.3.1 | `tie_largest` |
| `Inv_EmptyScopeMatchesNothing` | Every `analyze` use rests on a grant whose `scope` names `analyze`. | 3.3.1, 3.4.5 | `any_scope` |
| `Inv_DecayForwardOnly` | Decay starts only when the `st` fold reads revoked or expired. | 3.3.1 | `eager_decay` |
| `Prop_DecayForwardOnly` | Decay never steps backward (action property). | 3.3.1 | `decay_back` |
| `Prop_DecayCompletes` | Once started, decay reaches `complete`. | 3.3.1 | `decay_stalls` |
| `Prop_DecayStarts` | If the fold reads revoked or expired from some point on, decay starts. | 3.3.1 | `decay_never` |
| `Inv_ExpiryEmittedBySubstrate` | Every held `expired` row is the substrate's and names a held grant whose `valid_until` it does not precede. | 3.3.1 | `forged_expiry` |
| `Inv_ReplicationNeedsDirectedGrant` | The node never sends to a peer without a live replication grant naming that peer. | 3.3.7 | `blind_send` |
| `Inv_ReplicationGrantHasStanding` | No live replication grant is a stranger's. It does not tell the owner at `B1` from the owner at `B2`: either may grant once its binding is held. | 3.3.7 | `stranger_repl` |

Every property that holds has a planted break that `check.sh` runs and that violates it. `TypeOK`
has none. Three limits on that sentence. `Prop_TransferMovesNoVerdict` and `Inv_SameVerdictOnceHeld`
say one thing twice: each compares the verdict without `B2` to the verdict with it, and one plant
breaks both. `Inv_InstantBuysNoStanding`, `Inv_SameVerdictOnceHeld` and
`Prop_TransferMovesNoVerdict` are about the verdict function alone and read no held row.
`Inv_BackdatedGrantRefused` is implied by `Inv_StrangerNeverGrants`; it is kept because it names
the case the earlier reading let through.

## What is assumed and not checked

- **One receiver's view.** `B1` is held from the start and is never withdrawn without a replacement.
  The node has two bindings and no third. A binding is a fact the receiver holds or does not: the
  binding rows' own admission, and a fork between two replacements of `B1`, are not modelled.
- **The signer names its head honestly or not, and the model cannot tell.** CC 2.4.1.1 asks that a
  head be "the newest its signer holds". A device of `o1` that has seen `B2` and signs at `B1` is
  the stated limit of CC 2.4.1.1, and the model admits it.
- **Receipts are not modelled.** Under `ends` no grant at a replaced binding is kept in force by a
  clean receipt (CC 2.7.5).
- **The fold is one boundary over every party's rows.** CC 3.3.1 folds each party's rows apart: a
  party's revocation ends that party's consent and only that party's own later grant undoes it. This
  module keeps the earlier single-`R` fold. `formal/derivation/seven_rankings_shipped.tsv` lists the
  difference. It cuts both ways. The module stops capture where the text does not: any party's
  revocation puts out every party's grant, the withdrawn owner's included (the section above). And
  it allows capture where the text does not: after the agent key revokes, the node's later grant
  restores capture here, while in the text only the agent key's own later grant answers its
  revocation. So `Inv_RevocationIsBoundary` is weaker than the text's hard stop.
- **A revocation names no grant.** In the text a `withdraws` has a target and is admitted when its
  signer is a party the target names (CC 2.4.1.1 rule 2). Here a revocation is admitted on its
  signer's standing alone, and `Inv_OwnerCanRecant` is stated that way.
- **A revocation at a replaced binding stays in force under `ends`.** `InForce = "ends"` takes
  grants at `B1` out of the fold and leaves revocations at `B1` in it. CC 3.3.1 says the listed
  owner's withdrawal is admitted "whatever ownership later becomes"; whether CC 2.4.1.1's "not in
  force" reaches a withdrawal signed at an old head is not modelled either way.
- **The owner's device key, and an instant the text still reads.** CC 3.3.1 reads the attester of
  an owner-authored grant as "a live roster key of the owner's fedID at the grant's `asserted_at`".
  That is a standing read at a signed instant, in the same entry that reads the owner at a head.
  The model has one key for each owner and no self roster, so it checks neither reading of it.
- **Only `B2` is waited on.** `B1` is held from the start, and a node's or the agent key's
  revocation is read off the row alone and never waits.
- **The agent key is one fixed key.** The text folds a revocation from "the agent key a grant
  names". The model does not tie the agent key to a grant.
- **Replication is a sender's discipline.** CC 3.3.7 makes `consent:replication` a governance record,
  not an admission check. A replication grant is no row here and names no head, and what a replaced
  binding does to it is not modelled. A peer re-sending onward is not modelled. Bytes a peer already
  holds are not unsent.
- **Delegation chains** (CC 2.4.1.1 rules 3 and 4) and the consent-before-scoring admission gate on
  `capacity:*` (CC 3.4.5) are not modelled.
- **The deletion window** and its breach signal (CC 3.3.1 D1–D4) are not modelled.
- **Several subjects, several nodes, and more than three rows** are not modelled.
- **The `consent_supersedes` member on a grant** is not modelled. The fold does not read it.

Run: `bash formal/consent/check.sh` (with `TLA_JAR` naming `tla2tools.jar`). The whole file, 5
closing runs, 4 runs of one reading against a sentence it does not give, 21 planted-break runs and
30 witness runs, took 477 s and peaked at 3.5 GB with the default heap and four workers, and 448 s
and 1.5 GB with `CONSENT_XMX=1200m CONSENT_WORKERS=2`. `--quick` leaves out the two large closing
runs.
