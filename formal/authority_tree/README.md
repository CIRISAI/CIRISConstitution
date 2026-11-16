# `formal/authority_tree` — licensure, grant and delegation enumerated to closure

Vendored from CIRISRegistry `formal/authority_tree/authority_tree.py` at `1553d68`
(FSD-005 §5), because the Registry folds into CIRISServer and the Constitution carries its own
witnesses. The Registry's nine invariants are kept as written; a tenth, the term, is added here.

**What it models.** CC 2.4.1.3: a key comes to hold something in exactly three ways, and only
one chains. A licence (an authority confers standing) and a grant (an owner confers access) are
leaves. A delegation (a principal confers agency) chains, attenuated, depth-capped, revocable per
link, and now term-bound. The module is a state machine over `delegates_to` links plus who holds a
licence under the one authority and a grant over the one asset; every reachable state of three
universes is enumerated and every invariant checked in each.

| Invariant | What it says | CC |
|---|---|---|
| I1 attenuation | a chain's effective scope is the intersection along it; no link widens | 4.4.3.19 |
| I2 depth cap | nothing is conferred through more than 5 links; a sixth is refused at the door | 4.1.1 |
| I3 cascade | withdrawing a link removes exactly the authority derived through it | 4.4.3.19 |
| I4 licence closure | holding a licence never confers issuing one | 2.4.1.3 |
| I5 grant closure | holding a grant never confers re-granting | 2.4.1.3 |
| I6 enforced admission | every admitted leaf resolves to its authority or owner through live links | 4.4.3.19 |
| I7 sub_delegation | a chain continues only under a link that carries `sub_delegation` | 4.4.3.19 |
| I8 a cycle visited once | no link is refused for closing a cycle; every walk from every key terminates and passes no key twice; a walk that may revisit keys holds nothing more; a key reaches the same keys without the links into it, which close every cycle through it; a self-edge is the charter form | 4.1.1, 2.7.5 |
| I9 determinism | the authority a key holds depends on the live rows, not the order they arrived | 4.4.3.19 |
| **I10 term** | every live scope-bearing link carries a term within the ceiling; a perpetual link or one past it is refused at the door; expiry is a withdrawal, so its cascade is I3 | 4.4.3.12 |

**Measured** (`python3 authority_tree.py`, 7 m 07 s): general universe, four keys, every
action interleaved, two links, four terms offered at the door: 833,536 states, 5,647,360 leaves
admitted, 29,933,568 refusals, 1,635,840 withdrawals checked for cascade, 104,448 links admitted
that close a cycle, 0 violations; delegation-only universe at three links: 37,465 states, depth 3,
14,508 cycle-closing links admitted, 0 violations; depth chain:
links admitted 4096/2304/1024/400/144 at depths 1 to 5, 4,096 refused past the cap, 0 conferred
past it. `CLOSED`.

**Dye test.** `python3 authority_tree.py --no-term-rule` admits a perpetual link and exits 2 with
`VIOLATION: I10 term 0 on a live link`. A gate that has never fired has never gated.

**I8 plants.** `--plant-revisit` lets the walk pass a key it has passed; it exits 2 with
`VIOLATION: I8 walk from A passes a key twice` on the first two-key cycle. `--plant-refuse-cycle`
makes the door refuse the link that closes a cycle; the door is compared with the rule at every
offer, and it exits 2 with `VIOLATION: I8 the door refused a link the rule admits`.

**I2 and I8 bound every walk.** The cap bounds a walk's length, and a walk that passes no key twice
cannot go round a cycle. So every walk terminates with cycles present, and a cycle adds no reach.
The model has no weights: the aggregate-weight cap of CC 4.1.1 is not checked here.

**What it does not model.** Time as a clock (a term is a count the door checks and expiry is the
withdrawal action); the trust plane (charter self-edges are outside the walk by
construction); weights; more than two links with leaves interleaved (exceeds the memory budget and is not
claimed). The wire's `delegation_valid_until` arithmetic (365 × 86 400 s) is the implementation's,
under CLM-delegation-term.
