# `formal/authority_tree` — licensure, grant and delegation enumerated to closure

Vendored from CIRISRegistry `formal/authority_tree/authority_tree.py` at `1553d68`
(FSD-005 §5), because the Registry folds into CIRISServer and the Constitution carries its own
witnesses. The Registry's nine invariants are kept as written; a tenth, the term, is added here.

**What it models.** CC 2.4.1.2.1: a key comes to hold something in exactly three ways, and only
one chains. A licence (an authority confers standing) and a grant (an owner confers access) are
leaves. A delegation (a principal confers agency) chains, attenuated, depth-capped, revocable per
link, and now term-bound. The module is a state machine over `delegates_to` links plus who holds a
licence under the one authority and a grant over the one asset; every reachable state of three
universes is enumerated and every invariant checked in each.

| Invariant | What it says | CC |
|---|---|---|
| I1 attenuation | a chain's effective scope is the intersection along it; no link widens | 4.4.3.4.3 |
| I2 depth cap | nothing is conferred through more than 5 links; a sixth is refused at the door | 4.1.1 |
| I3 cascade | withdrawing a link removes exactly the authority derived through it | 4.4.3.4.3 |
| I4 licence closure | holding a licence never confers issuing one | 2.4.1.2.1 |
| I5 grant closure | holding a grant never confers re-granting | 2.4.1.2.1 |
| I6 enforced admission | every admitted leaf resolves to its authority or owner through live links | 4.4.3.4.3 |
| I7 sub_delegation | a chain continues only under a link that carries `sub_delegation` | 4.4.3.4.3 |
| I8 acyclic | the live delegation graph has no cycle across distinct keys; a self-edge is the charter form | 4.1.1 |
| I9 determinism | the authority a key holds depends on the live rows, not the order they arrived | 4.4.3.4.3 |
| **I10 term** | every live scope-bearing link carries a term within the ceiling; a perpetual link or one past it is refused at the door; expiry is a withdrawal, so its cascade is I3 | 4.4.3.2.8 |

**Measured** (`python3 authority_tree.py`, 2 m 26 s): general universe, four keys, every
action interleaved, two links, four terms offered at the door: 595,456 states, 4,142,080 leaves
admitted, 21,620,736 refusals, 1,167,360 withdrawals checked for cascade, 0 violations;
delegation-only universe at three links: 17,098 states, depth 3, 0 violations; depth chain:
links admitted 4096/2304/1024/400/144 at depths 1 to 5, 4,096 refused past the cap, 0 conferred
past it. `CLOSED`.

**Dye test.** `python3 authority_tree.py --no-term-rule` admits a perpetual link and exits 2 with
`VIOLATION: I10 term 0 on a live link`. A gate that has never fired has never gated.

**What it does not model.** Time as a clock (a term is a count the door checks and expiry is the
withdrawal action); the trust plane (charter self-edges are outside the cycle check by
construction); more than two links with leaves interleaved (exceeds the memory budget and is not
claimed). The wire's `delegation_valid_until` arithmetic (365 × 86 400 s) is the implementation's,
under CLM-delegation-term.
