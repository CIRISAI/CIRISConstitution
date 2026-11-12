**`membership:{stage}`** — Rules, thing

| Transition | Who signs | Policy | Widens | Confirm | Way back |
|---|---|---|---|---|---|
| attest | founder, member, self (proposal: founder, member; acceptance: self; decline: self; widening: member; removal: member; resignation: self) | cosigned `cosigned_act` | true (always) | true (always) | withdraw |
| withdraw | member | cosigned | false | false | attest |
| supersede | member | cosigned | false | false | supersede |

Count: `leaf=proposal|acceptance|decline => none ; leaf=resignation => none ; leaf=removal & group=affiliations & seats=one => affiliation_member_action@subject_group ; cosigned_act@subject_group` (CC 3.1.3.2, CC 4.4.3.2.8)

Guard:
- attest: `each(subject) when(leaf=widening,not member(key,object)) (one membership:acceptance@admitted[signer=key,object=object] as A & no membership:widening@admitted[ref:*=A.id] else refuse+community_consensus_protocol_violation)` (CC 3.1.3.2)
- attest: `each(subject) when(leaf=widening,not member(key,object)) (one membership:acceptance@admitted[signer=key,object=object] as A & one membership:proposal@admitted[id=A.ref:*,val:expires_at>=A.val:asserted_at,val:expires_at>=val:asserted_at] as P else refuse(membership_proposal_expired)+community_consensus_protocol_violation & no membership:decline@admitted[signer=key,ref:*=P.id] else refuse(membership_declined)+community_consensus_protocol_violation)` (CC 4.4.3.2.3)
- attest: `each(subject) when(leaf=widening,not member(key,object)) (one membership:acceptance@admitted[signer=key,object=object] as A & one membership:proposal@admitted[id=A.ref:*] as P else refuse(membership_proposal_expired)+community_consensus_protocol_violation & no membership:decline@admitted[signer=key,ref:*=P.id] else refuse(membership_declined)+community_consensus_protocol_violation)` (CC 3.1.3.2)
- attest: `each(subject) when(leaf=widening,not member(key,object)) one membership:acceptance@admitted[signer=key,object=object,val:role=val:role] as A else refuse(membership_acceptance_mismatch)+community_consensus_protocol_violation` (CC 3.1.3.2, CC 4.4.3.2.3, CC 4.4.3.2.5, CC 4.4.3.4.2)
- attest: `each(subject) when(leaf=widening,type(key,node)) one key:record@landed[attested=key] else refuse` (CC 3.1.3.2)
- attest: `when(leaf=acceptance|decline) no membership:acceptance|membership:decline@admitted[signer=signer,ref:*=ref:*] else refuse(membership_reply_conflict)+community_consensus_protocol_violation` (CC 3.1.3.2)
- attest: `when(leaf=widening) (one trust:confers@landed[attested=signer,val:scope=object] else refuse & type(signer,user) else refuse & not type(signer,node) else refuse)` (CC 3.1.3.2, CC 3.2)

Change:
- attest: `removal[axis:stream]: key=rotate_epoch` (CC 4.4.3.2.6)
- attest: `removal[last:seat]: cascade=group:roster/over:withdrawn` (CC 4.4.3.2.8)
- attest: `removal[scope:community|affiliations]: key=rotate_epoch` (CC 4.4.3.2.6, CC 3.2, CC 4.4.3.2.2, CC 4.4.3.4.5)
- attest: `removal[scope:self|family]: key=stop_wrap` (CC 4.4.3.4.2, CC 3.3.4, CC 4.4.3.4.5)
- attest: `resignation[ephemeral&last:member]: cascade=group:roster/over:withdrawn` (CC 5.3.3.2)
- attest: `resignation[last:seat]: cascade=group:roster/over:withdrawn` (CC 4.4.3.2.8)
- attest: `resignation[scope:self|family]: key=stop_wrap` (CC 3.3.4)
- attest: `widening[scope:community|affiliations]: key=next_seal` (CC 4.4.3.2.1, CC 4.4.3.2.5, CC 4.4.3.4.1, CC 2.1, CC 4.4.3.2.6)
- attest: `widening[scope:self|family]: key=rekey_walk` (CC 3.3.4, CC 4.4.3.4.1, CC 4.4.3.4.2)
- attest: `widening[stalled&recovery]: field=members:grow_signed, field=M:frozen, field=consensus_protocol:frozen, field=admission_quorum_basis:frozen, field=cohort_subkind:frozen` (CC 3.2)
- attest: `widening[stalled&recovery]: field=members:grow_signed` (CC 3.1.3.2)

Fold:
- `@stage=acceptance|decline: key=proposal_id,attesting_key_id; pick=once` (CC 3.1.3.2)
- `@stage=resignation: cut=forward; feeds=group:roster` (CC 3.1.3.2)
- `feeds=group:roster` (CC 4.4.3.2.4, CC 4.4.3.4.4)
- `@stage=removal: over=others@decision/person` (CC 3.1.3.2, CC 4.5.13)
- `@cohort_subkind=infrastructure: over=founders@decision/person` (CC 3.2, CC 4.4.3.2.4.1)
- `@cohort_subkind=infrastructure: over=founders@decision/person; reads=own&direct` (CC 3.2)
- `reads=own&direct` (CC 3.3.9, CC 6.1.8)
- `@group_kind=affiliation: over=deciding_seats@decision/person` (CC 4.4.3.2.8)
- `@stage=removal: bound=raise_only(revision); pick=max(quorum_weight),max(asserted_at),min(content_hash)` (CC 5.3.2.3)

In time:
- clock `W` = `admission_freshness_window_secs` (CC 2.6.7)
- on close(W) unless fold(signer_seated): read stale (CC 2.6.7)
- [proposal] expiry required `expires_at` max `membership_proposal_max_secs` (CC 4.4.3.2.3, CC 3.1.3.2)
- [proposal] on close(expiry): read closed (CC 4.4.3.2.3, CC 3.1.3.2)
- @family on admitted(self): emit `hard_case:family_membership_change` by identity:substrate_persist, emit `key_grant:content` by identity:substrate_persist (CC 4.4.3.4.2)

Body: `group_kind`, `role`, `proposal_hash`, `expires_at`
