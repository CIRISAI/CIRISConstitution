# `formal/membership` — the membership ceremony, model-checked

**Why.** Plane model B of `review/notes/formal_closure_rc9_2026-10-18.md` §5. The membership plane of
`formal/STATE_TABLE.tsv` was text-only: `member.stage` (none, proposed, accepted_awaiting_group,
declined, member, removed, resigned), `group.quorum_change` (none, held, applied) and `group.formed`
had no model. This module states the ceremony of CC 3.1.3.2 and the consensus protocols of CC 3.3.4
as one state machine and checks the properties the text promises.

**What it models.** One family or community, four keys: three listed on the founding record and one
spare. A founding record seats a listed key iff it signed it (CC 3.1.3.2 *Founding*). After that, the
rows of CC 3.1.3.2 are actions:

- a `membership:proposal` to one key K, by an active founder under `founder_only` and otherwise by any
  active member, with a window of two ticks to its `expires_at`;
- K's `membership:acceptance` (restating a role) or `membership:decline`, only while the proposal is
  open, and never both;
- the inviter's `withdraws` of the proposal;
- a cosigned `membership:widening` or `membership:removal`: one primary signer, cosigners added one at
  a time, judged under the protocol on the roster as it stood when the primary signed (CC 3.2 T6:
  each change is covered by a cosigned `group:roster` version);
- `membership:resignation` by the leaving member alone.

A held change lands when the protocol is met. Otherwise it expires after its hold window, which is
the "configurable window — operator policy" of CC 3.3.4. Protocols are `founder_only` (any active
founder), `unanimous`, `majority` (more than half the roster, the target counted) and `quorum:M/N`
(M absolute, CC 4.4.3.4.2.1). An adversary holds one key from the start and signs anything that key
may sign. Honest keys sign a removal only of that key, so any removal of an honest member is the
adversary's alone. Time is per object: each proposal and each held change carries its own age, and
one tick ages all of them together. There is no clock variable.

The bound: two proposals and two roster changes per behaviour, at most two proposals per invitee,
two roles. Only the current proposal to a key is remembered. A new proposal to K waits until no
change on K is held, so a held widening always names K's current proposal. The coerced key ranges
over one listed key and the spare; the listed keys other than the sole founder are symmetric in every
configuration.

**Mapping to `STATE_TABLE.tsv`.** `group.formed` is `formed`. `member.stage` is the definition
`Stage(k)`, computed from `active`, `prop[k].status`, `slot[k]` and `left[k]`. `group.quorum_change`
is `QuorumChange`: held while any `slot[k]` is held, applied once any change has landed (`applied`).
`TypeOK` checks that both definitions stay inside the table's states.

**Twelve configurations, one module.** TLC 2.19 (rev 5a47802), four workers, run 2026-10-18.
Each configuration checks every property below. A twin changes one rule switch, named in its file's
first line.

| Config | Rule / adversary | Expectation | TLC verdict |
|---|---|---|---|
| `founder_only` | ruled; founder k1; a non-founder coerced | every property holds | **closes**, 3,209,876 states |
| `unanimous` | ruled; any key coerced | every property holds | **closes**, 3,510,314 states |
| `majority` | ruled; any key coerced | every property holds | **closes**, 3,514,458 states |
| `quorum2of3` | ruled, M = 2; any key coerced | every property holds | **closes**, 3,495,550 states |
| `founder_only_coerced` | ruled; the founder coerced | one founder removes alone: the stated bound | `Inv_CoercedCannotRemoveHonest` violated in 3 steps |
| `unanimous_two` | unanimous removal read as "every other member" | at two members either removes the other | `Inv_CoercedCannotRemoveHonest` violated in 4 steps |
| `any_member_removes` | a removal lands on its primary alone | the coerced key evicts an honest member | `Inv_QuorumGovernsRoster` violated in 3 steps, the same step `Inv_CoercedCannotRemoveHonest` fails |
| `no_binding` | the widening reads any acceptance K ever signed | a seat from a mismatched acceptance | `Inv_AcceptanceBindsOneProposal` violated in 6 steps |
| `unspent` | admission (1)–(4) read literally | a resigned member is re-seated on the old acceptance | `Inv_LeavingNotUndone` violated in 10 steps |
| `stale_founder` | founder standing read off the founding record | a founder who resigned re-seats itself alone | `Inv_NoSelfAdmission` violated in 6 steps |
| `founding_unsigned` | the founding record seats every listed key | a listed key seated without signing | `Inv_JoinerConsented` violated in 1 step |
| `no_hold_expiry` | a held change never expires | a removal below quorum is held forever | `Prop_HeldChangeResolves` violated (stutters) |

EXACTNESS_PLACEHOLDER

**What the runs forced into the rule, each found as a counterexample first.**

1. **A proposal seats at most once** (the `unspent` twin). CC 3.1.3.2 *Admission* (1)–(4) do not say
   that a widening spends its proposal. The counterexample: K accepts, a widening seats K, K resigns,
   and within the same 30-day window a second widening re-seats K on the same acceptance. The ruled
   door also refuses a widening whose proposal already seated someone.
2. **Unanimous removal needs every other member, and those others must be a strict majority of the
   roster** (the `unanimous_two` twin). Read as "every current member", the target must sign its own
   removal, so nobody can be removed, the coerced key included. Read as "every member but the
   target", a two-member group lets either member remove the other alone. The first full unanimous
   run failed this way: one honest member resigns, and the coerced key removes the remaining honest
   member. The ruled reading removes nobody at two members, which is a stalemate. At three or more
   members, the signatures of every member but the target suffice.
3. **Founder standing is judged on the roster at the instant, never on the founding record** (the
   `stale_founder` twin). CC 3.3.4 says "Original founders are the sole admission authority". Read as
   the founding record, a founder who resigned can propose to itself, accept, and widen alone under
   `founder_only`.
4. **A held change needs a hold window** (the `no_hold_expiry` twin). CC 3.3.4 leaves the window to
   operator policy. Without one, a change below the protocol, such as the coerced key's removal of an
   honest member, stays held for ever.
5. **The landing step must be identified by the landing action.** An earlier version detected a
   landing from the slot clearing. That version reported a false violation when a held removal of a
   key that had resigned expired after another change had landed. This was a defect of the model, not
   of the rule, and is recorded so the action invariants are read as checks on `Land`.

**The properties.** Every `Inv_` property over a landing is an action invariant, checked on every
step through `PROPERTIES`. `Inv_ExpiryBound`, `Inv_JoinerConsented` and `Inv_ResignationEnabled` are
state invariants, and `Prop_HeldChangeResolves` is a liveness property under fairness of time only:
ticks keep coming and a due object expires. No signer is ever required to act.

| Property | What it states | CC |
|---|---|---|
| `Inv_JoinerConsented` | every seated key is seated on its own signature: the founding record it signed, or an acceptance of the proposal its widening names | 3.1.3.2 (the ruling; *Founding*) |
| `Inv_AcceptanceBindsOneProposal` | a widening lands only on an acceptance of the very proposal it names (the `proposal_hash`), with the same role, the widening signed by the proposal's `expires_at`, the proposal not withdrawn | 3.1.3.2 (registry row; *Admission* (1)–(4)) |
| `Inv_DeclineTerminal` | a declined proposal never seats; asking again is a new proposal | 3.1.3.2 (*Decline, withdrawal, expiry*) |
| `Inv_NoSelfAdmission` | no key is seated on rows it alone signed; founding is the stated exception | 3.1.3.2 (the ruling; *Founding*) |
| `Inv_QuorumGovernsRoster` | every widening and removal that lands meets the protocol on the roster at the row's instant | 3.1.3.2 (*The proposal is an invitation*), 3.3.4, 3.2 T6 |
| `Inv_CoercedCannotRemoveHonest` | one coerced key never removes an honest member; under `founder_only` a coerced founder can, and that is the stated bound | 3.3.4 (`ConsensusProtocol` kinds) |
| `Inv_ResignationEnabled` | a member can resign, alone, in every state | 3.1.3.2 (registry row: "a resignation is signed by the leaving member") |
| `Inv_LeavingNotUndone` | after a resignation or removal, a key is seated again only on a proposal issued after it left | 3.1.3.2 (*Decline, withdrawal, expiry*: "leaving stays the member's own forward-only `withdraws`") |
| `Inv_ExpiryBound` | no proposal is open past its window and no change is held past its window | 3.1.3.2 (`expires_at` ≤ 30 days), 3.3.4 (the pending window) |
| `Prop_HeldChangeResolves` | a held quorum change applies or expires | 3.3.4 step 2; `group.quorum_change` |

**What it does not model.**

- `weighted:{rubric}` and `custom:` protocols, and protocol amendment or entrenchment (CC 3.3.4).
- The `infrastructure` subkind: admission over the founder subset, node seats with no acceptance, and
  the T7 recovery widening (CC 3.2). The geographic `location_proof` gate (CC 4.4.3.2.3).
- `admission: open` on a `public` community, where the standing proposal resolves its subject at
  acceptance (CC 3.2).
- Role changes for an active member, promotion to founder, and supersedes that change metadata or
  drop members (CC 3.1.3.2 *A supersede never adds a member*).
- Two or more coerced keys, and invitees the adversary controls. With one coerced key, a vote cast
  after its signer left cannot decide anything, so cosigners here are limited to keys still seated.
- Out-of-order replication across nodes. There is one door, and every row reaches it in the order
  signed.
- The moderator plane (`group.moderator`, `group.federating`, CC 4.5.4), which stays with
  `formal/mesh_net`. DEK re-wrap and `key_grant` on admission and removal (CC 3.3.4 steps 3–4).
- Concurrent proposals to one key while a change on that key is held (the bound above).

Run: `java -cp tla2tools.jar tlc2.TLC -workers auto -metadir /tmp/tlc -deadlock -config Membership_<cfg>.cfg Membership.tla`.
A ruled configuration runs in about five minutes with `-Xmx3g`, and a twin runs in seconds.
