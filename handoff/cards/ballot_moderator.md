**`ballot:moderator`** — Structure, thing

| Transition | Who signs | Policy | Widens | Confirm | Way back |
|---|---|---|---|---|---|
| attest | member | ranked `moderator_election` | true | true (always) | withdraw |
| withdraw | author | selfAct | false | false | attest |

Count: `moderator_election@subject_group` (CC 4.5.13)

Guard:
- attest: `each(val:ranks) member(key,object) else refuse` (CC 3.1.3)

Fold:
- `key=election_id,person; pick=agree; over=live@count/person` (CC 3.1.3)
- `order=max(moderation_track_record),min(admission_order),min(key_id)` (CC 4.5.4)
- `combine=policy(moderator_election)` (CC 4.5.13)
- `over=live@count/person` (CC 4.5.13)
- `test=voices>=min(2,n) ?seated:open` (CC 4.5.13)

In time:
- clock `window` = `moderator_election.window_secs` (CC 4.5.13)

Body: `ranking` (text only), `salt`
