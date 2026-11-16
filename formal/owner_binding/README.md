# `formal/owner_binding` — who owns a key

**The point.** Every `node` and `agent` key is held by one person, named in one signed row (CC 3.2 "Who owns a
key"). The rule has two halves. The text once had a node refuse a second owner when the binding was admitted, which depends on the order rows
arrive in. This model runs that door under four readings and the fold that replaced it, over every order of
arrival, and shows which holds together.

**The model.** `owner_binding_model.py`. One key. The rows are an owner-binding (by one of three owners, cosigned
by the node's key or not, at `self` or wider), an owner's withdrawal, and an `identity_occurrence`. A node takes
them in some order and reads `owner_of` after each.

| Reading | Choices |
|---|---|
| what becomes of a refused binding | `final`: dropped. `again`: offered again when the rows held change. `fold`: nothing is refused, and the reader counts the live cosigned bindings |
| which bindings need the node's cosign | `first`: only the first a node ever admits. `unowned`: every binding onto a key with no live owner |

**What is checked**, over every set of up to four rows in every order (47,296 runs for each reading):

| | Property |
|---|---|
| O1 | a node never reads two owners |
| O2 | the owner's own re-signed rows at wider scopes change nothing |
| O3 | an occurrence row changes nothing |
| O4 | ownership passes from X to another owner only when X's withdrawal is held; a second binding may leave the key with no owner and never hands it to its signer |
| O5 | a binding the node's key did not cosign never makes its signer the owner |
| O6 | two nodes offered the same rows read the same owner, whatever the order |
| O7 | the same, where the node's key cosigned two bindings for one unowned period |
| O8 | a reader that holds two live owners reads none and never picks one |

**What it found.**

| Refusal | Cosign | Gives up |
|---|---|---|
| final | first | O2, O5, O6, O7 |
| final | unowned | O2, O6, O7 |
| again | first | O5, O6, O7 |
| again | unowned | O7 |
| fold | unowned | nothing |

The fold holds all eight, and it is the rule (CC 3.2, the steward's ruling of 2026-11-12): nothing is refused and forgotten; only a binding the node's own key cosigned counts; one counted owner is the owner and any other count is none. A stranger's binding is held and counts for nothing. During a handover the key is briefly unowned if the new owner's binding is held before the old owner's withdrawal.

Every reading with a door that refuses gives something up. A refusal that is final leaves two nodes with the same rows reading different owners. A cosign asked only of the first binding opens a released key to the first claimant. And where the node's own key cosigns for two owners, a door keeps whichever arrived first, so two nodes differ for good; the fold reads no owner at both. The check pins what each door reading gives up, so the reason the door went is on record (conflict C557).

**Steward-bound: one owner, or a set of guardians.** A second section reads `is_steward_bound` over every set of up
to four rows about one subject, in every order (1,551 runs). The subject is a `node`, an `agent` or a minor's `user`
key. A binding is by one of two adults or by a person a row on record places in a minor band, and each may be withdrawn.

| | Property | Planted break |
|---|---|---|
| S1 | a minor with two live guardian bindings is steward-bound: the bindings are read as a set | `single_for_minor` |
| S2 | a minor with no live guardian binding is not steward-bound | `withdrawal_ignored` |
| S3 | a binding by a person a row on record places in a minor band binds nothing, so a minor owns no node or agent | `minor_may_own` |
| S4 | a node or an agent with two live owners is not steward-bound: the single-owner rule stands | `set_for_node` |
| S5 | the reading is a function of the rows held, whatever the order | `first_arrival` |

All five hold and every plant is caught. The minor-band test reads the band row, another row, so it sits in the
reading and not at the binding's door: a minor's binding is held and counts for nothing, as a stranger's does. An
owner with no band row on record counts, as CC 3.4.13's fail-secure rule lets an unassured owner announce a node.

**What it does not model.** Lapse by `delegation_valid_until` (a withdrawal stands for it); how a band comes to
be on record (`formal/age_assurance`); the audience of each re-signed row (`formal/mesh_net`);
the steward-binding gate on admission (`formal/membership`).

Run: `python3 formal/owner_binding/owner_binding_model.py --check`
