# `formal/trust_root`: the CC 3.2 T8 standing verdict, model-checked

**What this is.** A TLA+ model of the standing verdict `V(rows, t)` that CC 3.2 T8 states as a
normative state machine: `Rooted`, `Stalled` or `NotRooted`, over the rows a node holds and a
signer-stamped instant. It carries the T8 invariants as properties TLC checks, a planted fault for
each that the named invariant must catch, and a witness for each corner the invariants speak of. It
is the evidence for the register row `CLM-standing-verdict`.

**What it models.** One evaluating node and one root. The root is the lineage of a genesis bundle
(T5). Its head is the bundle in force, and a later bundle naming `prev` moves it (T6). There is no
separate head object and nothing cosigns one.

| Input (T8) | In the model |
|---|---|
| The lineage's heads | `held`: the genesis `g` (version 1), `a2` (version 2, on `g`), with `Fork` a second bundle `b2` at version 2 on `g`, and with `Deep` a third version `a3` on `a2`. A later bundle is an amend carrying the statements of a strict majority of the holders (`sig`), or one holder's recovery (`rec`). A bundle's own instant is its version less one |
| The Receipts held for each | `rN`: how many distinct services' Receipts for a bundle count, up to the quorum; `rAt`: the issue instant of the newest. Of `NServices` services, all but `Faulty` register one bundle for each version, so two bundles at one version both reach the quorum only through a faulty service |
| The bundle in force: `holders`, `charter` | `Holders`, the same in every bundle; `Named`: the genesis charter names the services, or names none. The fork bundle `b2` always names services of its own, and those have always issued their Receipts for it. `cur` is the bundle in force for this node |
| `revoked_after` bounds | `krev`: of each holder's genesis key; `orev`: of the key that signed the acceptance edge. Bounds only lower. With `Uncountable`, a service's key is revoked below a Receipt it issued and that Receipt falls out of the count (`Uncount`) |
| The acceptance edge and the head it names | `edge`: none, present, withdrawn, recanted or tombstoned; `edgeHead`; `edgeAt`, the edge's own signed instant, within `Skew` of the clock at admission |
| *t* | every instant: `VAt(t)` is checked for all `t` in `0..MaxT`. `clock` is the evaluating clock, which `VAt` never reads |
| Each seat's `identity_type`, the halt latch, an `infrastructure` room's founder margin | arguments of the verdict, not state: an invariant quantifies over every value of each (i, v, T7) |

`Rooted` needs a live edge, a bundle of the lineage that verifies, and a strict majority of the
holders live. A holder is live at `t` while the key the bundle in force seats for it has no
revocation in effect: `t` is before its genesis key's bound, or the bundle in force descends from its
recovery. `Stalled` is the same with fewer live holders. Everything else is `NotRooted`.

The attach-time clauses guard one action, `Attach`, and nothing else reads them: the head is
receipted by a quorum of the services its predecessor's charter names, its newest Receipt is within
`AttachWindow` before the edge's own instant, the lineage is not frozen, and no later receipted head
is held. Where no services are named the edge names the anchored head, the genesis.

After the edge is written the node follows the lineage. It adopts a later bundle that is counted and,
where the predecessor names services, receipted. It adopts none on a frozen lineage. It falls back to
the nearest ancestor that still verifies when a lowered `revoked_after` unmakes the count of the
bundle it stands on.

**What it checks.** Four configurations close on every row below: `TrustRootVerdict.cfg` (services
named, two versions with the fork and one faulty service), `TrustRootVerdict_revoked.cfg` (a Receipt
may fall out of the count), `TrustRootVerdict_deep.cfg` (a third version) and
`TrustRootVerdict_anchored.cfg` (no services named, three versions with the fork).

| Property | The sentence of the text it checks |
|---|---|
| `Inv_i` | (i) "A seat whose `identity_type` at seating includes `node` never moves a state by its own signature." Whatever bundles such a seat has signed, the bundle in force and the freeze are the same |
| `Inv_ii`, `Prop_ii` | (ii) "V(rows, *t*) is constant on every interval of *t* that contains no `effective_at` and no `revoked_after` of any row — a lapsed timer (drill staleness, an expired `attach_window_secs`, a missed `receipt_cadence_secs`) never moves `Rooted` or `Stalled` to `NotRooted`." `Inv_ii`: `VAt(t) = VAt(t+1)` unless a bound sits at `t+1`, and V is the same whatever the clock reads. `Prop_ii`: a step that moves only the clock moves no verdict |
| `Inv_iii` | (iii) "A key revocation reaches behind only through its `revoked_after` bound, per (viii)." A bundle whose statements were each made before their signer's bound keeps its count |
| `Prop_iv` | (iv) "The edge-written transition is enabled only on a head whose counted Receipts are fresh and at least `receipt_quorum`. A stale or under-quorum head never yields `Rooted` on attach." Freshness is read against the edge's own instant; with no services named the edge names the anchored head |
| `Inv_v` | (v) "A `constitutional` halt moves no state here: *V* at *t* is the same with and without a latched halt, whatever roster rows land between." |
| `Inv_vi`, `Prop_vi` | (vi) "Deleting the acceptance edge is sufficient for `NotRooted` from any state, and from `NotRooted` *for want of an edge* nothing but a new edge naming a head re-enters `Rooted`." The deletion is enabled in every state with an edge |
| `Inv_vii` | (vii) "V(rows, *t*) is independent of the order in which the rows arrived — the fold commutes." The head the node reached row by row equals a fold over the rows it holds, outside the two corners of Readings 1 and 2 |
| `Inv_viii` | (viii) "A `revoked_after` lowered below a receipted head's `asserted_at` is applied at read time, fail-closed … V(rows ∪ {*v*}, *t*) equals V over the rows with *h* and every head descending from *h* removed, for all *t*. The lineage's current head is the latest receipted head that still verifies, and the signer leaves the live holders from the bound onward." |
| `Inv_T7` | T7, *Scope*: "It is no leg of any root's standing, and T8 never reads it." V is the same whatever the founder margin of an `infrastructure` room is |
| `Inv_T4`, `Prop_T4` | T8, `NotRooted`: "Each attach-time clause is never a leg of V for a node already attached (T4)." A step that changes only the clock and the Receipts never moves `Rooted` or `Stalled` to `NotRooted` |
| `Inv_Stalled` | T8, `Stalled`: "every leg of `Rooted` holds except the holders' margin: fewer of the bundle's holders are live than a strict majority." |
| `Inv_RecoverEnabled` | T8, *Transitions*: "a holder's recovery, a later bundle under its recovery key, that restores the majority (`Stalled → Rooted`)" |
| `Inv_EndNoInstant` | T8: "The end of a standing enters V by the head its row names, never by an instant." Once the edge is ended V is `NotRooted` at every *t*, the instants before the end among them |
| `Inv_PredecessorSet`, `Prop_PredecessorSet` | T6: "A Receipt for a head is verified against the `transparency_services` of that head's **predecessor** … A later head is never verified against its own charter, which a fork head chooses." |
| `Inv_ForkNeverFreezes` | T6: "a fork attempt never freezes the lineage." |
| `Inv_FreezeAdoptionOnly`, `Prop_FreezeAdoptionOnly` | T6: "The freeze suspends **head adoption only**. `withdraws`, `recants`, tombstones, `revoked_after` bounds and the halt latch … keep landing." |
| `Inv_NoServicesNoReceipt` | T6: "A charter that carries none of them **names no services**, and no Receipt counts." |

**The planted faults.** `Plant` names one deliberately wrong reading. Each configuration below sets
one and must fail the property beside it; `run.sh` refuses any other outcome.

| Configuration `TrustRootVerdict_plant_…` | The wrong reading | Caught by |
|---|---|---|
| `seat_counts` | a node-bearing seat's statement over a bundle is counted with the holders' | `Inv_i` |
| `aging_detaches` | an attached node is `NotRooted` once its head's Receipts are older than the window on its own clock | `Prop_T4` |
| `revocation_reaches_behind` | a key revocation unmakes every statement of the key, whatever its bound | `Inv_iii` |
| `fresh_by_clock` | freshness is read against the evaluating clock, not the edge's own signed instant | `Prop_iv` |
| `attach_under_quorum` | the edge is written on a head with fewer counted Receipts than `receipt_quorum` | `Prop_iv` |
| `halt_folds` | a latched `constitutional` halt is a leg of the verdict | `Inv_v` |
| `end_by_instant` | the end of the edge is read by its instant, so V stays `Rooted` at instants before it | `Inv_EndNoInstant` |
| `first_seen_wins` | with no services named, of two counted bundles on one predecessor the first seen is adopted | `Inv_vii` |
| `unmade_head_stays` | a head whose count a lowered `revoked_after` unmade stays the bundle in force | `Inv_viii` |
| `founder_margin` | `Stalled` is fed by the founder margin of an `infrastructure` room | `Inv_T7` |
| `own_charter` | a head's Receipts are verified against the services its own charter names | `Prop_PredecessorSet` |
| `fork_freezes` | a fork attempt, a counted head that is not receipted, freezes the lineage | `Inv_ForkNeverFreezes` |
| `freeze_blocks_ends` | a frozen lineage holds back withdrawals and key revocations as well as head adoption | `Inv_FreezeAdoptionOnly` |
| `unnamed_receipts_count` | Receipts count although the charter names no services | `Inv_NoServicesNoReceipt` |

**The witnesses.** `TrustRootWitness.tla` states the negation of each corner the invariants speak
of, and `run.sh` requires TLC to reach every one: `Rooted`, `Stalled`, `Stalled` at the edge's
own instant, `Rooted` again by a recovery, a later head adopted, a fall back to an ancestor, a lineage
with no verifying bundle, an edge whose signer is revoked, an attached node on a frozen lineage, a
fork attempt beside a receipted head, an attached node still `Rooted` on stale Receipts and on a head
that lost its quorum, tips that wait where no services are named, Receipts held and not counted, and
the third version in force.

## Readings

Places where the text of CC 3.2 admits two readings, or where two of its sentences cannot both
hold. The model takes the reading named first. The text is unchanged.

1. **(vii) against the freeze.** (vii): "V(rows, *t*) is independent of the order in which the rows
   arrived — the fold commutes — so it is byte-equal on every node holding the same rows." T6: "It
   MUST NOT adopt a new head for that lineage until the adjudication plane rules … A consumer
   already attached keeps its current state on its current head." A node that adopted `a2` before
   `b2` was receipted stands on `a2`. A node that received both sets of Receipts first stands on
   `g`. They hold the same rows. Where `a2` is a recovery the two verdicts differ, `Rooted` and
   `Stalled`. The model keeps the head each node reached, as T6 says, and checks (vii) outside a
   frozen lineage. `TrustRootVerdict_reading_vii_freeze.cfg` runs (vii) with no exception and fails
   on this case.
2. **(vii) against an attach-time clause.** (viii): "The lineage's current head is the latest
   receipted head that still verifies." T8, `NotRooted`: "At attach time only, it also includes a
   head whose Receipts fall out of the count … Each attach-time clause is never a leg of V for a
   node already attached (T4)." A node that adopted a head on a quorum keeps it when a service's key
   is revoked below its Receipt. A node that receives the revocation first never adopts it. The
   model keeps the adopted head (T4) and checks (vii) outside this case too.
   `TrustRootVerdict_reading_vii_uncount.cfg` runs (vii) with no exception and fails on it.
3. **(viii), which heads are removed.** (viii): "V(rows ∪ {*v*}, *t*) equals V over the rows with
   *h* and every head descending from *h* removed." CC 2.6.1.11: "a statement whose `iat` disagrees
   is Invalid on its own, and the bundle is counted on the statements that remain." The model
   removes *h* only where its count fails on the statements that remain. A consequence follows for
   the first bundle, which "counts when every holder it lists has a valid statement over it". One
   holder's key revoked with no bound ("Absent member = revoke-all", CC 2.4.1.1) unmakes the genesis
   and every head after it, and every node on the lineage is `NotRooted`. T8's transition for the
   same row is "a key revocation or `revoked_after` crossing that leaves fewer live holders than a
   strict majority (`Rooted → Stalled`)". No recovery bundle restores a lineage whose genesis is
   unmade. The witness `Wit_LineageUnmade` is this state.
4. **The edge's signer.** T8, `NotRooted`: "the edge's signer past its effective `revoked_after`".
   CC 2.4.1.1: "a claim signed by K is valid iff its `asserted_at` precedes `K.revoked_after`". The
   model reads the second: the edge counts iff its own instant precedes the bound, at every *t*. The
   other reading makes V `NotRooted` from the bound onward and `Rooted` before it.
5. **The instants V reads.** T8: "The only instants V reads are a key revocation's `revoked_after`
   bound and a row's own stated end." (ii): "constant on every interval of *t* that contains no
   `effective_at` and no `revoked_after` of any row". No row among T8's inputs is given a stated
   end, and `effective_at` is an instant the first sentence excludes. The model reads `revoked_after`
   bounds only.
6. **Whose charter names the services at attach.** T4a: "Receipts for it from `receipt_quorum`
   distinct services its charter names." T6: "A later head is never verified against its own
   charter, which a fork head chooses." The model reads the predecessor's charter everywhere.
7. **A Receipt issued after the edge's own instant.** T6: fresh "when its newest counted Receipt was
   issued within `attach_window_secs` before the attaching edge's own signed instant". An edge
   signed before the newest Receipt was issued is then not fresh by the letter. The model keeps one
   instant for each bundle and refuses that attach, which is the stricter reading.
8. **How long a freeze lasts.** T6: "until the adjudication plane rules". (viii) removes a head a
   lowered bound unmade. The model reads the freeze from the rows: it ends when one of the two heads
   no longer verifies or is no longer receipted. Adjudication is not modelled.
9. **(viii) names a receipted head.** Where no services are named no head is receipted. The model
   applies (viii) to every head.
10. **Tips where no services are named.** T6: "the two heads then wait as tips." CC 2.6.1.11: a
    reader "acts on what every tip names, the holders and seats common to them". The model reads
    this as standing on the bundle the tips share, whichever tip arrived first, which is what (vii)
    needs.

## What it does not model

- **A lagging head** (T6, consequence ii). "A Receipt on one is kept and does not count toward the
  head's quorum, so attaching on it goes stale through the T4a freshness gate" leaves open whether
  such an attach is refused as stale or as unreceipted. The cadence is not in the model.
- **(iii), first sentence.** "A `withdraws` or a resignation reaches acts by the head it names." The
  holders are the same in every bundle here, so no holder's seat ends. The end the model has is the
  acceptance edge's, checked by `Inv_EndNoInstant`.
- **A change of the named services by a later bundle.** Every chain the model reaches is judged by
  the genesis charter's set. The predecessor rule is exercised by the fork bundle, which names
  services of its own.
- **Which service issued which Receipt.** Receipts are counted, up to the quorum. Independence of a
  service is by construction, and the charter legs (a recovery commitment for each holder, the
  scope) are constant: "no counted bundle makes this move".
- **An out-of-band anchor on a later head**, a holder added or removed by an amend, a revocation of
  a recovered key, a second edge to another lineage, and a row's stated end.
- One instant is kept for each bundle's Receipts. When a Receipt falls out of the count the
  bundle's instant is unknown until a service issues again, so the model refuses some attaches a
  node would allow and allows none a node would refuse. Where no services are named, Receipts are
  issued for the genesis only.
- The bounds: three holders, three services, three instants, a window and a skew of one tick, two
  key revocation rows of holders and the edge's signer, and one Receipt that falls out of the count.

## Run it

```
TLA2TOOLS=/path/to/tla2tools.jar ./run.sh
```

It runs the four closing configurations, the fourteen planted faults, the two runs of the rejected
reading and the witnesses, and exits 1 on any outcome but the expected one. The CI job
(`.github/workflows/formal.yml`) runs the same script. On the shared build machine run it through
the scheduler: `grace-sched run --owner CIRISConstitution -- env TLA2TOOLS=… ./run.sh`.

## Status

TLC 2.19, eight workers, an 800 MB heap, through the scheduler on a loaded machine.

| Configuration | Distinct states | Depth | Time | Result |
|---|---|---|---|---|
| `TrustRootVerdict.cfg` | 471,462 | 16 | 14 min (4 min 10 s on a quieter run) | closes, no violation |
| `TrustRootVerdict_revoked.cfg` | 63,591 | 14 | 57 s | closes, no violation |
| `TrustRootVerdict_anchored.cfg` | 138,207 | 12 | 6 min 17 s | closes, no violation |
| `TrustRootVerdict_deep.cfg` | 257,919 | 16 | 4 min 33 s | closes, no violation |

931,179 distinct states in all. Each of the fourteen planted faults is caught by the property named
beside it, within 15,000 states and four seconds. Both runs of the rejected reading fail
`Inv_vii_Unconditional`, at 66,932 and 9,790 states, on the traces Readings 1 and 2 describe. Every
witness is reached. No run found a state the text's rules do not cover; what the runs did find is
in *Readings*. Keep TLC's state files out of the tree: `run.sh` writes them to a temporary
directory and removes it.
