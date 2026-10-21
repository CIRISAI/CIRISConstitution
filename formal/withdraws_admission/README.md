# `formal/withdraws_admission` — who may erase a row about a subject, model-checked

**Why.** Building the Article 17 erasure route ruled on 2026-10-15 (CIRISConstitution#174, CC 4.5.3),
persist found that two sentences of rc8 collide: CC 2.4.1.1's anti-Goodhart carve-out says a
subject-authority path (rules 2–4) MUST NOT withdraw a third-party `capacity:*` / `detection:*`
row about itself, while the new 4.5.3 paragraph said a `detection:*` row is erased by the subject's
own `withdraws` under rule 2 or rule 3. Both go through persist's one `withdraws` door, so one
sentence had to yield. This module decides which, mechanically.

**What it models.** One producer (the detector operator, the data controller) authors a row of each
kind about each of four subjects: a keyed human, a keyed agent, an un-enrolled human (canonical
hash) and an un-enrolled agent (a bot a friendly node fronts). Two kinds: `ordinary`, and
`detection` standing for the whole adverse class (capacity, licensure, revocation share it). Actions:
the node establishes a rule-3 proxy chain for an un-enrolled subject (no judgment modelled); the
producer withdraws (rule 1); the keyed subject withdraws (rule 2); the proxy withdraws (rule 3); and,
in the shipped-v57 configuration only, the node hard-deletes under a node-local basis never served
to peers. Rule 4 inherits 1–3 and adds nothing to the question.

**Four configurations, one module.**

| Config | Reading of the carve-out for adverse rows | Result |
|---|---|---|
| `WithdrawsAdmission_controller.cfg` | rules 2–4 never reach an adverse row; the controller withdraws it under rule 1 on the subject's request, or refuses with reason (Art. 17(3)) | **closes**: every invariant holds, 3,600 distinct states |
| `WithdrawsAdmission_proxy.cfg` | rule 3 only, for a subject who proved identity out of band (persist's narrow reading of 4.5.3) | `Inv_AntiGoodhart` violated in 2 steps: proxy established for the un-enrolled human, the proxy withdraws the detection row about them |
| `WithdrawsAdmission_literal.cfg` | the carve-out lifted for detection rows (4.5.3 read literally) | `Inv_AntiGoodhart` violated in 1 step: the keyed human withdraws the detection row about themselves |
| `WithdrawsAdmission_local.cfg` | the v57 shipped shape: node-local hard delete, header never served | `Inv_OneDoor` violated in 1 step: a row is gone from one node and its tombstone reached no peer |

**The invariants.** `Inv_AntiGoodhart` (an adverse row about a subject is removed only by its
producer, CC 2.4.1.1); `Inv_OneDoor` (whatever is erased anywhere is erased by a `withdraws` whose
tombstone by digest reached the peers, CC 4.5.3 / #165); `Inv_ErasureReachable` (for every standing
row about a natural person some admitted `withdraws` is enabled now, the controller's at least);
`Inv_SubjectRouteOrdinary` (the subject's own route, rules 2–3, reaches every ordinary row about a
person: a keyed person by their own signature, an un-enrolled person through a proxy once one
exists, CC 1c); `Inv_AgentCannotLaunder` (an agent never clears its own adverse record by any path
a friendly node can open for it); `TypeOK`.

**What it says.** The only reading under which the carve-out, the one door and reachability all hold
is the controller-only one: for an adverse row, the subject's Article 17 request is executed by the
row's producer under rule 1, with the Art. 17(3) refusal-with-reason the compliance table already
provides, and never by the subject's own key or a proxy. The subject's own route (rules 2–3) stays
the route for every ordinary row about them, and the contest path for an adverse row stays
`reconsideration:{grounds}` (CC 4.5.5). The 4.5.3 sentence that named rules 2 and 3 for detection
rows is the one that yields.

**What it does not model.** The controller refusing in bad faith (the contest path is 4.5.5, not this
module); a steward purge of a row whose producer is gone (CC 4.5.3, the cosigned takedown); rule 4;
the deletion window and its breach hard case (CC 4.4.3.5.2).

Run: `java -cp tla2tools.jar tlc2.TLC -workers auto -metadir /tmp/tlc -deadlock -config WithdrawsAdmission_<cfg>.cfg WithdrawsAdmission.tla` (TLA+ tools 1.7.4; each finishes in seconds).

## The third row kind (2026-10-21, CIRISConstitution#170)

`hard_case` was added to `Kinds` and to `Adverse`: an equivocation proof (`hard_case:lineage_equivocation`) or a
liveness transition (`community_liveness_stalled` / `_restored`) is an adverse row about a root, and the only
purge door over that root's rows is the root's own quorum — the subject. The four configurations give the same
verdicts as before (controller closes at 422,401 states; proxy and literal fail `Inv_AntiGoodhart`; local fails
`Inv_OneDoor`), so the rule extends unchanged: no subject-side path removes an adverse row, and the producer —
the substrate, under rule 1 — is the only one that withdraws it (or recants a false one). That is the model's
answer to #170: `hard_case:*` joins the unpurgeable accountability set of CC 2.4.1.1, and persist's purge door
refuses it by family like the five already listed.
