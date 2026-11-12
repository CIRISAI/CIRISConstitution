**`consent:state:{stance}`** — Rules, thing

| Transition | Who signs | Policy | Widens | Confirm | Way back |
|---|---|---|---|---|---|
| attest | owner, self | selfAct | true (by_scope) | true (if_widens) | withdraw |
| withdraw | author, subject | selfAct | false | false | attest |
| supersede | author | selfAct | true (by_scope_change) | true (if_widens) | supersede |

Count: `none`

Change:
- attest: `expired: by=substrate, reach=other_attester, link=ranked:consent_supersedes` (CC 3.3.1)

Fold:
- `pick=rank(revoked>granted)` (CC 3.3.1)
- `@stance=revoked: cut=boundary(asserted_at)` (CC 3.3.1)
- `@stance=revoked: cut=boundary(asserted_at),terminal` (CC 4.4.3.5.5)
- `@stance=revoked: cut=terminal` (CC 4.4.3.5.5)
- `pick=max(asserted_at); by=reader` (CC 4.4.3.5)
- `reads=own&signer:subject|proxy` (CC 4.4.3.5.5)
- `absent=unspecified` (CC 4.4.3.5.5)
- `pick=max(asserted_at)` (CC 4.4.3.5.5)
- `result=state(granted|revoked|expired|unspecified)` (CC 4.4.3.5.5)

In time:
- [granted] expiry optional `valid_until` (CC 3.3.1, CC 4.4.3.5.5)
- [granted] on close(expiry) unless superseded(self): read lapsed, emit `consent:state:expired` by identity:substrate_persist (CC 3.3.1, CC 4.4.3.5.5)
- [granted] expiry optional `valid_until` default `consent_temporary_ttl_secs` (CC 4.4.3.5.6)
