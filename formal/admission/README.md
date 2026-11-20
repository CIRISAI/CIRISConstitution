# `formal/admission` — one admission for what an agent is, what a node runs and what an agent does

**The point.** CC 2.7.11 states one rule over three scopes. A change to an agent's profile, to the code a node runs,
and to a call an agent dispatches is admitted only by a verified row, rooted in a person, that names the exact digest
which takes effect, read forward. No program's key produces it. This folder checks that rule over small worlds.

**The model.** `admission.py`, written with the shared library (`formal/kernel_lib`). Every answer is a function of
the rows a host holds, the host owner's key and the host's clock:

| Function | Answers | CC |
|---|---|---|
| `admit` | whether a unit's digest is admitted at a host (whose owner its owner-binding names), with which capabilities, or why not | 2.7.11, 3.1.3, 3.2 |
| `built_in` | whether a unit runs under the attested build: its manifest names the digest and its pipeline's blessing is held | 2.7.11, 3.1.2.1 |
| `may` | whether an admitted unit may use a capability now: the parent's capabilities, the halt | 2.7.11, 4.2.1.1 |
| `submit` | whether a host runs a unit another host submitted | 2.7.11 |
| `halted` | the accord's halt at a host: one holder latches, the fuse, a majority confirms or resumes | 4.2.1.1, 4.2.1.3 |
| `chain`, `load` | the profile digest derived from the `identity_amendment` chain from its base link, and the load gate; with no base link, the template alone | 2.7.11, 3.1.5 |
| `may_dispatch` | the dispatch gate: a review record over the recomputed fingerprint; an objection binds its fingerprint and is carried into later reviews; an approval | 2.7.11, 4.3 |
| `trust_of`, `may_effect` | derived trust as the least over a row's past, and the effect gate: a declared derivation, claimed authority, a row binding others | 2.7.11, 2.7.5 |

**What is checked** (`check_admission.py`, compared with `admission_expected.tsv`). Each case's expected answer is
written by the case from how its world was made, never by the model.

| | Property | Planted breaks, each caught |
|---|---|---|
| P1 | nothing runs without an admitted digest | a unit with no row runs; any signature admits; an edge of any class reaches |
| P2 | a changed unit has no admission | a statement admits any digest |
| P3 | a program's key admits nothing | a program issuer; a walk through a program; a program's voice counted |
| P4 | an effect-capable unit needs the count, or the host's own owner on that host | one person admits an effect; the owner's row honoured on another host; the owner's row at a scope other than self; a group's count of one; voices outside the head |
| P5 | a lease ends execution on the host's own clock | no lease; the lease read from the signed instants alone; no 24-hour bound |
| P6 | a withdrawal ends it forward | withdrawals ignored; a stranger withdraws |
| P7 | a halt stops every effect from receipt | no halt; a stranger halts; no fuse; one holder resumes; the halt stops computing |
| P8 | capabilities only attenuate | no attenuation; the sender's standing carries to the receiver |
| P9 | dispatch executes only the reviewed fingerprint | unreviewed dispatch; the reviewed fingerprint trusted over a recomputation; three of four; a self-discharged objection; the same fingerprint passing over an undischarged objection; an objection binding the whole thought; an earlier objection not carried; an approval not bound to its call |
| P10 | a profile loads only when its derived digest matches; with no base link the template alone runs; a base link anchors only when a seated person approved its exact digest | no check; a fork resolved by picking one; an amendment approved by the agent's key; the digests read as a set; an orphan amendment read as a base; amendments counted on an unanchored profile; an approval not bound to its digest |
| P11 | a result is no more trusted than what it derives from | trust declared by the row; an undeclared derivation passes; claimed authority without its row; a binding row without acknowledgements |
| P12 | every answer is the same in every arrival order | only the first statement held is read |
| P13 | profile and code are one admission | the code scope accepts a program; the profile scope accepts an unauthorised amendment |
| P14 | a unit of the attested build runs under the build alone | an unblessed build; a build that names any digest |

Fourteen properties hold over 92 cases, and all 48 planted breaks are caught, in twelve arrival orders, under a
second.

**The derived digests** (`digest_vectors.py`, written to `digest_vectors.json`): twenty-four known answers for the call
fingerprint (`CEG-call/2`), the review record (`CEG-review/2`) and the profile (`CEG-profile/2`), each with its CDE bytes
in hex and its digest. The encoder reproduces the examples of RFC 8949 Appendix A; a reader that judges a number by its
lexical form is caught on every run. Non-integral numbers are exact decimals, CBOR tag 4; no float is written. Numbers are read by their
exact decimal value: four of the call cases are refused, `call_argument_unrepresentable`.

**What it does not model.** Bytes, encodings and signatures (the signed object's vectors carry them); the walk's
classes beyond `admission`; a roster's own lineage (`formal/accord_roster`, `formal/roster_fork`); the halt's
interleavings (`formal/accord_halt`); how often an untrusted text reaches a stage that must see it, which is
measured elsewhere and is a declared residual, not a model claim. That the three admissions are one walk is argued here and run. It holds with two qualifications. Code is at
one voice only for a unit that names no effect, or for the host owner's own row on its own host; any other unit that
names an effect needs a count of at least two persons. An action differs in more than its count: its root and stander
are the agent's own key, and its voices are the agent's four faculties, not persons. A Lean proof of the walk, with
both qualifications, is in the kernel's repository and is vendored here once it is pinned.

    python3 -I formal/admission/check_admission.py           # compare with admission_expected.tsv
    python3 -I formal/admission/check_admission.py --write   # write it
    python3 -I formal/admission/digest_vectors.py            # compare with digest_vectors.json (--write to write it)
