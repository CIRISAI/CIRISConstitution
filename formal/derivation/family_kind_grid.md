### GRID
Counts are families whose verb list includes that verb (a family counts in several columns). Last column is families per kind. Totals: 189 families, THING 89, ACCOUNT 100; 13 families maintain the Record relation (the +1 is a relation, not a kind: those rows are Facts or Rules about the record, with erasure none or legal hold and a byte-equal projection). No family carries a row of another kind at the v61 head: the six earlier `carries` labels were a derived aggregate, a body that carries content, or a precondition that reads another row, and the table now records those as `reference` with a mode (`pre:` or `carry:`) rather than as the verb.

| kind | attest | authorize | replace | withdraw | recant | carries | families |
|---|---|---|---|---|---|---|---|
| Priorities | 5 | 0 | 0 | 5 | 3 | 0 | 5 |
| Rules | 34 | 2 | 16 | 29 | 3 | 0 | 36 |
| Manner | 3 | 0 | 1 | 3 | 1 | 0 | 3 |
| Identity | 16 | 3 | 10 | 12 | 0 | 0 | 19 |
| Confidence | 15 | 0 | 2 | 14 | 10 | 0 | 15 |
| Facts | 69 | 0 | 27 | 60 | 27 | 0 | 69 |
| Circumstances | 13 | 0 | 11 | 8 | 0 | 0 | 13 |
| Process | 13 | 0 | 5 | 5 | 0 | 0 | 13 |
| Model | 5 | 0 | 0 | 5 | 5 | 0 | 5 |
| Structure | 8 | 0 | 2 | 7 | 5 | 0 | 8 |
| Premises | 3 | 0 | 2 | 3 | 1 | 0 | 3 |

The profile each kind admits, and the carries firewall, are checked as a machine in [`../family_model/`](../family_model/): every row above must fit its kind's profile, and the registry's own occupancy is the evidence the profiles rest on (authorize only under Rules, Identity and Process; thing-or-account a function of kind).

### EMPTY
- (Priorities, authorize): principled. A weighting is scored, never delegated; delegating who-goes-first would itself be a Rules grant.
- (Priorities, replace): mostly principled. Votes and credits accrue rather than supersede; a versioned priority order would be the one exception, and none is minted.
- (Priorities, carries): gap. Slashing or revocation arriving as a credit change is exactly carries, and no family names it.
- (Manner, authorize): principled. Nobody delegates register or tone.
- (Manner, carries): gap. A rating (Rules) arriving as a content warning (Manner) is the designed pipeline, unexpressed.
- (Identity, recant): principled. Names are replaced or revoked, not confessed wrong; key:revocation carries the negative.
- (Identity, carries): principled. A change smuggled in as a renaming is the kind-laundering CEG firewalls.
- (Confidence, authorize): principled. The no-self-emit rule makes confidence attested by others, never conferred.
- (Facts, authorize): principled. A fact is not a permission.
- (Facts, carries): gap, the loudest. The README's own canonical example (a changed assumption arriving as changed Facts) has no family; detection and ratchet readings are the nearest and are attest-only.
- (Circumstances, authorize): principled.
- (Circumstances, recant): principled. Telemetry is overtaken by the next reading, not recanted.
- (Circumstances, carries): small gap. A reachability observation arriving as a liveness verdict is carries in all but name.
- (Process, authorize): gap. The right to advance a lifecycle (confirm a halt, run a decay stage) is real but lives in Rules families (trust:{job}).
- (Process, recant): principled. A step taken is superseded by the next state, not unsaid.
- (Process, carries): gap by construction. Ceremony steps arriving as membership changes are carries; classifying membership and lineage_witness as Rules folded it away.
- (Model, authorize): principled.
- (Model, replace): gap. A newer judge model or DMA version superseding a verdict is natural and no family versions it.
- (Model, carries): gap. A DMA verdict arriving as a conscience verdict (Structure) is the agent's designed pipeline, unexpressed on the wire.
- (Structure, authorize): principled. The gate's verdict is never delegated; the authority to halt is conferred through Rules, and the halt itself is a pre-signed attest.
- (Structure, carries): gap, same pair as Model/carries from the other side.
- (Premises, authorize): principled.
- (Premises, carries): gap, the same hole as Facts/carries seen from the source kind.
- (Record, authorize): principled. The past is not delegated; cosigning a log head is a witness attest.

Two readings stand out. The authorize column is confined to Rules and Identity, which matches delegates_to being a permission-or-identity edge. The carries column is almost empty (6 of 169 families), consistent with CEG firewalling carries, but it means the grammar's carries verb lives in consumer composition rather than in the namespace, so the namespace cannot be derived from the full grid without also naming where carries is computed.
