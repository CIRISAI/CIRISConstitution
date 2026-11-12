# `formal/owner_binding` — who owns a key

**The point.** Every `node` and `agent` key is held by one person, named in one signed row (CC 3.2 "Who owns a
key"). The rule has two halves. A node refuses a second owner when the binding is admitted, and a reader that
finds two owners reads none. The first half depends on the order rows arrive in, and the text does not say what
becomes of a refused binding or whether a binding after a handover needs the node's cosign. This model runs each
reading over every order of arrival and shows which holds together.

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
| O4 | the owner changes from X only when X's withdrawal is held, never because a binding arrived |
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
| fold | unowned | O4 |

One reading holds O1 to O6: a refused binding is offered again, and every binding onto an unowned key carries
the node's cosign. A refusal that is final leaves two nodes with the same rows reading different owners, since a
new owner's binding that arrives ahead of the old owner's withdrawal is lost. A cosign asked only of the first
binding opens a released key to the first claimant, which CC 3.2 refuses for an unclaimed node.

**The one named breaker.** No reading holds O4 and O7 together. If the node's own key cosigns for two owners, a
door that refuses the second keeps whichever arrived first, and two nodes differ for good. A reader that counts
both agrees everywhere and un-owns the key on the second cosign. CC 3.2 states both halves. The check pins what
each reading gives up, so a change to the rule shows here (conflict C557 of `formal/derivation/text_conflicts.tsv`).

**What it does not model.** Lapse by `delegation_valid_until` (a withdrawal stands for it); who may be an owner
(the `user` role and the age band, `formal/age_assurance`); the audience of each re-signed row (`formal/mesh_net`);
the steward-binding gate on admission (`formal/membership`).

Run: `python3 formal/owner_binding/owner_binding_model.py --check`
