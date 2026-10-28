------------------------ MODULE RetirementWitness ------------------------
(* Reachability witnesses for the closing configuration: each Wit_* says "this never happens";
   TLC must find it happening, so a run that closes is not closing on an empty machine.
   Run with Retirement_witness.cfg, one invariant at a time (tools: see README). *)
EXTENDS Retirement

\* a planned retirement by the steward, objected to, postponed once, decided, and retired
Wit_PlannedRetired == ~(Retired /\ kind = "planned" /\ decidedBy = "steward" /\ postponed)
\* the welfare route (the agent's own petition) reaches retired
Wit_WelfareRetired == ~(Retired /\ decidedBy = "agent")
\* an emergency retirement by the steward, after a forced stop, reaches retired
Wit_EmergencyRetired == ~(Retired /\ kind = "emergency" /\ forcedBy = "steward")
\* an operator-decided planned retirement over the agent's objection reaches retired
Wit_OperatorObjected == ~(Retired /\ decidedBy = "operator" /\ objection = "objected")
\* cancellation lands
Wit_Cancelled == ~(cancelledFrom = "decided")
\* after retired: the subject withdraws, the custodian executes, the seal still shut
Wit_SubjectAfterRetired == ~(Retired /\ subjOrd = "withdrawn" /\ seal = "sealed" /\ custodySigners = {"custodian"})
\* the seal opens under a lawful order after retired
Wit_OpenedByOrder == ~(Retired /\ seal = "opened_by_order")
\* the operator declines preservation and lets the record go; the request stays on the record
Wit_DeclinedDiscarded == ~(Retired /\ preserveResp = "declined" /\ record = "discarded")
\* the operator walks away mid-ladder and the ladder still completes
Wit_WalkAwayThenRetired == ~(Retired /\ opStatus = "off" /\ record = "held")
\* a refused task is still refused at retired
Wit_RefusedAtRetired == ~(Retired /\ task = "refused")
\* the custodian withdraws an adverse row about the subject (the controller's rule-1 route)
Wit_AdverseByCustodian == ~(advBy = "custodian")
=============================================================================
