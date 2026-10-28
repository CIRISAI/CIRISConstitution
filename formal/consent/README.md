# `formal/consent` — the consent plane, model-checked

**Why.** The consent plane
had four state-table variables (`consent.state`, `consent.decay`, `consent.community_trust`,
`consent.replication`) and no model. This module realises all four and checks the rules CC 3.3.1,
3.3.7, 2.4.1.1 and 2.6.7 state about them. It also checks CC 3.3.1's revocation
authority: the owner may author the capture grant, and the node, the owner and the
agent key are each listed so that each may withdraw.

**What it models.** One receiver, holding the rows it admitted in admission order (the index is
the attestation-id order used for ties). Two consent series share one fold:

- **`st`, `consent:state`.** The subject grants and revokes. A grant carries a `scope` (none, or
  `analyze`) and optionally a `valid_until`. The substrate emits `expired` naming the lapsed grant
  in `consent_supersedes`. An `analyze` use (the Score action) happens only on a live grant whose
  scope names `analyze`.
- **`ct`, `consent:community_trust`.** The capture grant for one node's sealed traces. The node,
  or its owner at the grant's `asserted_at`, grants. The node, that owner or the agent key revokes.
  A trace at instant `now` is captured only if the fold says granted at `now`.

**The fold (CC 3.3.1).** `R` is the latest admitted revocation's `asserted_at`. Every grant at or
before `R` is out. Among the grants after `R`, the latest `asserted_at` wins, and ties go to the
smallest attestation id. No grant means no consent. On `st`, a winning grant whose `valid_until`
has passed reads `expired`.

**Admission (CC 2.6.7, CC 3.3.1).** A row is judged at its signed `asserted_at`. A row whose
`asserted_at` precedes the receiver's clock by more than `W` is refused (`asserted_at_stale`). A
refused row moves nothing, so the model has no transition for it. Ownership passes from `o1` to
`o2` at instant `TX`. `o1` is the withdrawn signer: its rows dated before `TX` keep standing, and
its rows dated at or after `TX` have none.

**The adversary.** It signs as a stranger. It signs as `o1` after `TX` with `asserted_at`
backdated before `TX`. It backdates any party's row within and beyond `W`. It forges `expired`
under a non-substrate key. It grants replication as a stranger. Replay needs no action of its own:
a replayed admitted row deduplicates on its attestation id, and a replayed refused row is judged
again at a later clock, where it is still stale and its standing is unchanged.

**Decay and replication.** The agent's consent module walks `identity_severed`,
`patterns_anonymized`, `complete`, once the `st` fold reads revoked or expired, under weak
fairness. `consent:replication` (CC 3.3.7) is a directed grant, one peer per grant, by the node or
its owner. The node ships captured traces to a peer only while a grant naming that peer is live.

**State-table realisation.**

| STATE_TABLE variable | Model expression | Values |
|---|---|---|
| `consent.state` | `FoldNow("st").v` | `none`, `granted`, `revoked`, `expired` |
| `consent.decay` | `decay` | `none`, `identity_severed`, `patterns_anonymized`, `complete` |
| `consent.community_trust` | `FoldNow("ct").v` | `none` is `absent`, `granted`, `revoked` is `bounded` |
| `consent.replication` | `p \in replLive` per peer | `none`, `granted` |

**Configurations.** Constants are the same in all five: instants `0..4`, `W = 1`, `TX = 2`,
`valid_until` two instants after the grant, at most three admitted rows. TLA+ tools 1.7.4.

| Config | Mode, planes | Reading | TLC verdict |
|---|---|---|---|
| `Consent_ruled_ct.cfg` | `ruled`, `ct` | the CC 3.3.1 fold and standing, the CC 2.6.7 bound; capture and replication | **closes**: every invariant holds, 4,210,336 distinct states, depth 19 |
| `Consent_ruled_st.cfg` | `ruled`, `st` | the same fold over the subject's stance; scope, expiry, decay; the three temporal properties | **closes**: every invariant and property holds, 467,692 distinct states, depth 16 |
| `Consent_no_boundary.cfg` | `no_boundary`, `ct` | the latest grant wins whatever was revoked | `Inv_RevocationIsBoundary` violated in 3 steps: `o1` grants at 0, `o1` revokes at 0, a trace is captured at 0 |
| `Consent_literal_signer.cfg` | `literal_signer`, `ct` | only the node may revoke the capture grant | `Inv_OwnerCanRecant` violated in 1 step: `o1` grants at 0, and `o1` then has no admissible revocation |
| `Consent_no_W.cfg` | `no_W`, `ct` | no freshness bound | `Inv_BackdateBounded` violated in 5 steps: the clock reaches 3, `o1` signs a grant dated 0, it is admitted, a trace is captured at 3 on it |

**What each twin breaks, exactly.** Each twin was rerun with its named property removed.

- `literal_signer` then closes (2,086,608 distinct states). It breaks only `Inv_OwnerCanRecant`.
- `no_boundary` also breaks `Inv_RevokedOverridesGranted`, the equal-instant case of the
  boundary. With both removed it closes (10,163,392 distinct states).
- `no_W` also breaks `Inv_LateRevocationWithinW`, the same bound read from the revocation side.
  With both removed it closes (15,462,256 distinct states).

**Witnesses.** The closing runs are not vacuous. Each scenario below is the negation of a `Wit_*`
predicate in the module, and TLC reaches it under the CC reading.

- `o1` signs after `TX` with a grant dated before `TX`, within `W`, and a capture rests on it.
  This is the honest divergence CC 2.6.7 states.
- A revocation is admitted after a capture whose instant it covers.
- A capture happens after a revocation, on a fresh grant.
- The agent key revokes. The new owner `o2` revokes.
- A peer holds captured traces.
- The substrate emits `expired`.
- Decay reaches `complete`, and decay starts on expiry.
- An `analyze` use happens after a revocation, on a fresh grant.

## INVARIANTS

| Property | Statement | CC |
|---|---|---|
| `Inv_RevocationIsBoundary` | No capture or `analyze` use at an instant after a revocation the deciding node held, unless it also held a grant dated after that revocation and not after the use. Stated without the fold. | 3.3.1 (`community_trust` fold), 2.4.1.1 rules 2–4 |
| `Inv_RevokedOverridesGranted` | No use rests on a grant dated at the same instant as a held revocation. | 3.3.1 (`revoked` overrides `granted`; grants at or before `R` are out) |
| `Inv_StrangerNeverGrants` | No held row is a stranger's. A held capture grant is the node's or its owner's at the grant's `asserted_at`. A held `st` grant or revocation is the subject's. | 3.3.1 (emitter classes; "neither the node nor its owner … MUST NOT be folded") |
| `Inv_OwnerCanRecant` | While a grant stands, a revocation signed now by the node, the current owner or the agent key (`ct`), or by the subject (`st`), is admitted. The model's row budget is not counted as a party's limit. | 3.3.1 ("the node's owner MUST always be able to revoke") |
| `Inv_BackdateBounded` | No capture rests on a row from the withdrawn signer `o1` admitted at or after `TX + W`. | 2.6.7 (a withdrawn delegate keeps at most `W` of backdatable authority) |
| `Inv_LateRevocationWithinW` | A revocation admitted after a use reaches back to it only if the use's instant is within `W` of the revocation's `asserted_at`. | 2.6.7 (a withdrawal takes full effect everywhere within `W`) |
| `Inv_EmptyScopeMatchesNothing` | Every `analyze` use rests on a grant whose `scope` names `analyze`. | 3.3.1 (`consent:scope`), 3.4.5 |
| `Inv_DecayForwardOnly` | Decay starts only when the `st` fold reads revoked or expired. | 3.3.1 (`consent:decay:{stage}`) |
| `Prop_DecayForwardOnly` | Decay never steps backward (action property). | 3.3.1 |
| `Prop_DecayCompletes` | Once started, decay reaches `complete`. | 3.3.1 |
| `Prop_DecayStarts` | If the fold reads revoked or expired from some point on, decay starts. | 3.3.1 |
| `Inv_ExpiryEmittedBySubstrate` | Every held `expired` row is the substrate's and names a held grant whose `valid_until` it does not precede. | 3.3.1 (`consent:state:expired`, substrate-emitted, `consent_supersedes`) |
| `Inv_ReplicationNeedsDirectedGrant` | The node never sends to a peer without a live replication grant naming that peer. | 3.3.7 |

**What it does not model.**

- **Replication is a sender's discipline.** CC 3.3.7 makes `consent:replication` a governance
  record, not an admission check. `Inv_ReplicationNeedsDirectedGrant` therefore holds for a
  conforming sender by construction. A peer re-sending onward is not modelled. Bytes a peer
  already holds are not unsent (CC 3.3.7).
- **Delegation chains** (CC 2.4.1.1 rules 3 and 4), held rows whose owner-binding rows have not
  arrived, and the consent-before-scoring admission gate on `capacity:*` (CC 3.4.5) are not
  modelled.
- **The deletion window** and its breach signal (CC 3.3.1 D1–D4) are not modelled.
- **Several subjects, several nodes, and more than three rows** are not modelled. The fold is per
  series, so one subject and one node cover its logic.
- **The `consent_supersedes` member on a grant** is not modelled. The fold does not read it (CC
  4.5.1.1 op split), so it carries audit, not consent.

Run: `java -cp tla2tools.jar tlc2.TLC -workers 4 -metadir /tmp/tlc -deadlock -config Consent_<cfg>.cfg Consent.tla`. The `ruled_ct` run takes about two minutes. The others finish in seconds.
