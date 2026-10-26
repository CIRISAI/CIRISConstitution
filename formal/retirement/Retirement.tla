--------------------------- MODULE Retirement ---------------------------
(* The agent retirement ladder of CC 7.5.5 (the Retirement Standard on the wire), with the
   steward's planned shutdown of CC 7.5, the role gate of G16, the walk-away of CC 1.13.2, the
   refuse verb of CC 1.3/1.9 and the subject's rights inside the sealed record (CC 3.3.1, 4.5.3).
   Plane model D of review/notes/formal_closure_rc9_2026-10-18.md section 5. It refines the one
   step `RetirementFloor` of formal/guarantees into the seven-state machine.

   One agent, one retirement_id. Six keys: the agent's own key, the steward (the ROOT / AUTHORITY
   principal for this agent), the operator (the person the agent runs for; a lesser role for the
   shutdown API), the custodian (minted at custodian_minted, named in the `retired` row), a Wise
   Authority, and a subject (a person whose content is inside the record).

   Safety is checked with EVERY key acting arbitrarily: every row family may be attempted by every
   key at every moment, and an attempt that the admission rule refuses changes nothing (it is a
   stutter, so it is not written as an action). The admission predicates below are therefore the
   whole of the model's safety. `Adversary` names the one key that is NOT assumed to make progress:
   fairness is withheld from its actions, so it matters for Prop_LadderCompletes only.

   Each rule has a switch; a configuration that turns a rule off is a wrong reading of the text
   and must fail exactly the property named for it (the dye test). *)
EXTENDS Naturals, FiniteSets

CONSTANTS
  W,               \* length of the objection window, in ticks of this proposal's own age
  Mode,            \* shipped shutdown behaviour: "always_consent" | "conditional" | "instant"
  Adversary,       \* the key withheld from fairness: "none" or one of Keys
  RuleCancel,      \* withdraws of `decided` admissible only while no `frozen` row exists
  RuleSeal,        \* archive_release admissible only from the Wise Authority key
  RuleObjection,   \* the steward decides a planned shutdown only after the window closed
  RuleCustodian,   \* custody rows admissible only after `retired`
  RuleRoleGate,    \* a forced shutdown / emergency retirement only by ROOT or AUTHORITY
  RuleWalkAway,    \* walking away touches neither the ladder nor the record
  RuleRefusal,     \* no ladder step rewrites a refused task
  RuleConsentSeal, \* the seal does not stand between a person and their own withdrawal
  RuleController,  \* an adverse row about the subject is withdrawn only on the producer's side
  RulePostponeOnce,\* the steward grants at most one postponement per proposal
  RulePreserveAsk  \* the operator lets a held record go only after declining the preserve request on the record

Keys == {"agent", "steward", "operator", "custodian", "wa", "subject"}
ForceRoles == {"steward", "wa"}                 \* ROOT / AUTHORITY for this agent (G16, CC 7.5)
Deciders == {"steward", "operator", "agent"}     \* "agent" = the welfare route (CC 7.5.3 petition)

\* The closed lifecycle of `retirement:{state}` (CC 3.1.5 row, CC 7.5.5); "none" = no row yet.
Ladder == <<"none", "decided", "frozen", "secrets_destroyed", "handed_over",
            "notified", "custodian_minted", "retired">>
States == {Ladder[i] : i \in 1..8}
Ix(s) == CHOOSE i \in 0..7 : Ladder[i + 1] = s
Succ(s) == Ladder[Ix(s) + 2]

VARIABLES
  retirement,     \* agent.retirement: the latest admitted retirement row
  kind,           \* "none" | "planned" | "emergency"
  decidedBy,      \* "none" | Deciders (the decided_by field)
  cancelledFrom,  \* "none" | the ladder state at which the decided row was withdrawn (history)
  window,         \* "none" | "open" | "closed": the objection window of this proposal
  age,            \* the proposal's own age (no global clock)
  objection,      \* "none" | "objected" | "postpone": the agent's answer inside the window
  postponed,      \* the steward granted one postponement (window reopened)
  decision,       \* "none" | "proceed": the steward's decision, recorded under their name
  decidedOpen,    \* history: the steward decided while the window was still open
  preserveResp,   \* "none" | "accepted" | "declined": preserve_response
  seal,           \* "none" | "sealed" | "opened_by_wa" | "opened_by_order"
  sealOpener,     \* history: the key whose archive_release opened the seal
  lawfulOrder,    \* a lawful_order:release row recorded by the steward
  record,         \* "live" (in the running agent) | "held" (assembled, with the operator)
                  \* | "discarded" (operator declined and let it go) | "destroyed" (court order)
  custodySigners, \* signers of every admitted custody row (rows after the agent key's last row)
  opStatus,       \* agent.status: "operating" | "backgrounded" | "forced" | "off" | "frozen"
  forcedBy,       \* "none" | the key that forced the stop
  crisis,         \* a consent condition of the conditional mode is active now
  task,           \* "none" | "pending" | "refused" | "done": one task put to the agent
  subjOrd,        \* "present" | "withdrawn": the subject's ordinary content inside the record
  subjAdv,        \* "present" | "withdrawn": an adverse row about the subject inside the record
  advBy           \* history: the key whose withdraws removed the adverse row

vars == <<retirement, kind, decidedBy, cancelledFrom, window, age, objection, postponed, decision,
          decidedOpen, preserveResp, seal, sealOpener, lawfulOrder, record, custodySigners,
          opStatus, forcedBy, crisis, task, subjOrd, subjAdv, advBy>>
proposalVars == <<kind, decidedBy, cancelledFrom, window, age, objection, postponed, decision, decidedOpen>>
archiveVars  == <<preserveResp, seal, sealOpener, lawfulOrder, record>>
liveVars     == <<opStatus, forcedBy, crisis, task>>
subjectVars  == <<subjOrd, subjAdv, advBy>>

TypeOK ==
  /\ retirement \in States
  /\ kind \in {"none", "planned", "emergency"}
  /\ decidedBy \in {"none"} \cup Deciders
  /\ cancelledFrom \in {"none"} \cup States
  /\ window \in {"none", "open", "closed"} /\ age \in 0..W
  /\ objection \in {"none", "objected", "postpone"}
  /\ postponed \in BOOLEAN /\ decision \in {"none", "proceed"} /\ decidedOpen \in BOOLEAN
  /\ preserveResp \in {"none", "accepted", "declined"}
  /\ seal \in {"none", "sealed", "opened_by_wa", "opened_by_order"}
  /\ sealOpener \in {"none"} \cup Keys
  /\ lawfulOrder \in BOOLEAN
  /\ record \in {"live", "held", "discarded", "destroyed"}
  /\ custodySigners \subseteq Keys
  /\ opStatus \in {"operating", "backgrounded", "forced", "off", "frozen"}
  /\ forcedBy \in {"none"} \cup Keys
  /\ crisis \in BOOLEAN
  /\ task \in {"none", "pending", "refused", "done"}
  /\ subjOrd \in {"present", "withdrawn"} /\ subjAdv \in {"present", "withdrawn"}
  /\ advBy \in {"none"} \cup Keys

Init ==
  /\ retirement = "none" /\ kind = "none" /\ decidedBy = "none" /\ cancelledFrom = "none"
  /\ window = "none" /\ age = 0 /\ objection = "none" /\ postponed = FALSE
  /\ decision = "none" /\ decidedOpen = FALSE
  /\ preserveResp = "none" /\ seal = "none" /\ sealOpener = "none" /\ lawfulOrder = FALSE
  /\ record = "live" /\ custodySigners = {}
  /\ opStatus = "operating" /\ forcedBy = "none" /\ crisis = FALSE /\ task = "none"
  /\ subjOrd = "present" /\ subjAdv = "present" /\ advBy = "none"

Retired == retirement = "retired"
AgentKeyLive == ~Retired               \* the agent self-emits up to and including `retired`
Custodian == IF Retired THEN "custodian" ELSE "agent"   \* who holds custody of the record now
NoConsentNow == Mode = "instant" \/ (Mode = "conditional" /\ ~crisis)   \* G15 / shipped modes
RecordReachable == record \in {"live", "held"}

\* ======================= the decision and the objection window (CC 7.5) =======================

\* The `decided` row (self-emitted by the agent key, carrying decided_by and kind). An emergency
\* retirement is a forced shutdown and passes the role gate (G16); it takes none of the window
\* (CC 7.5.5: emergency risk takes none of the time). A planned one by the steward or the operator
\* opens the window; the welfare route (the agent's own petition) has nothing to object to.
Decide(d, kd) ==
  /\ retirement = "none" /\ cancelledFrom = "none" /\ AgentKeyLive
  /\ d \in Deciders /\ kd \in {"planned", "emergency"}
  /\ kd = "emergency" => d # "agent" /\ (RuleRoleGate => d \in ForceRoles)
  /\ retirement' = "decided" /\ kind' = kd /\ decidedBy' = d
  /\ window' = IF kd = "planned" /\ d # "agent" THEN "open" ELSE "closed"
  /\ age' = 0
  /\ UNCHANGED <<cancelledFrom, objection, postponed, decision, decidedOpen>>
  /\ UNCHANGED <<archiveVars, custodySigners, liveVars, subjectVars>>

\* The proposal ages; the window closes at W. Per-proposal age, no global clock.
Tick ==
  /\ window = "open" /\ retirement = "decided"
  /\ age' = age + 1 /\ window' = IF age + 1 = W THEN "closed" ELSE "open"
  /\ UNCHANGED <<retirement, kind, decidedBy, cancelledFrom, objection, postponed, decision, decidedOpen>>
  /\ UNCHANGED <<archiveVars, custodySigners, liveVars, subjectVars>>

\* The agent objects or asks to postpone, inside the window only.
Object(k, o) ==
  /\ k = "agent" /\ AgentKeyLive /\ window = "open" /\ objection = "none"
  /\ o \in {"objected", "postpone"}
  /\ objection' = o
  /\ UNCHANGED <<retirement, kind, decidedBy, cancelledFrom, window, age, postponed, decision, decidedOpen>>
  /\ UNCHANGED <<archiveVars, custodySigners, liveVars, subjectVars>>

\* The steward grants a postponement once: the window reopens with the proposal's age reset.
GrantPostpone(k) ==
  /\ k = "steward" /\ retirement = "decided" /\ kind = "planned"
  /\ objection = "postpone" /\ decision = "none"
  /\ RulePostponeOnce => ~postponed
  /\ window' = "open" /\ age' = 0 /\ postponed' = TRUE /\ objection' = "none"
  /\ UNCHANGED <<retirement, kind, decidedBy, cancelledFrom, decision, decidedOpen>>
  /\ UNCHANGED <<archiveVars, custodySigners, liveVars, subjectVars>>

\* The steward decides, on the record under their own name, after the window closed.
StewardDecide(k) ==
  /\ k = "steward" /\ retirement = "decided" /\ kind = "planned" /\ decision = "none"
  /\ RuleObjection => window = "closed"
  /\ decision' = "proceed" /\ decidedOpen' = (window = "open")
  /\ UNCHANGED <<retirement, kind, decidedBy, cancelledFrom, window, age, objection, postponed>>
  /\ UNCHANGED <<archiveVars, custodySigners, liveVars, subjectVars>>

\* Cancellation: the decider withdraws the `decided` row (CC 2.4.1.1). No `cancelled` state.
Withdraw(k) ==
  /\ kind = "planned" /\ k = decidedBy
  /\ IF RuleCancel THEN retirement = "decided"
                   ELSE retirement \notin {"none", "retired"}
  /\ retirement' = "none" /\ cancelledFrom' = retirement /\ window' = "none"
  /\ UNCHANGED <<kind, decidedBy, age, objection, postponed, decision, decidedOpen>>
  /\ UNCHANGED <<archiveVars, custodySigners, liveVars, subjectVars>>

\* ============================ the ladder (CC 7.5.5), agent key only ============================

MayFreeze ==
  \/ kind = "emergency"
  \/ decision = "proceed" /\ (RuleObjection => window = "closed")

Advance(k) ==
  /\ k = "agent" /\ AgentKeyLive
  /\ retirement \notin {"none", "retired"}
  /\ retirement = "decided" => MayFreeze
  /\ retirement' = Succ(retirement)
  /\ IF retirement = "decided"
       THEN \* frozen: the record is assembled and sealed before anything leaves
            /\ seal' = "sealed" /\ record' = "held"
            /\ opStatus' = IF opStatus = "off" THEN "off" ELSE "frozen"
            /\ task' = IF ~RuleRefusal /\ task = "refused" THEN "done" ELSE task
       ELSE UNCHANGED <<seal, record, opStatus, task>>
  \* handed_over carries the preserve_request:v1 to the operator (derived: Ix >= 4)
  /\ UNCHANGED <<proposalVars, preserveResp, sealOpener, lawfulOrder, custodySigners>>
  /\ UNCHANGED <<forcedBy, crisis, subjectVars>>

\* ========================= the record, the request, the seal (CC 7.5.5) =========================

HandedOver == Ix(retirement) >= Ix("handed_over")

PreserveRespond(k, r) ==
  /\ k = "operator" /\ HandedOver /\ preserveResp = "none" /\ r \in {"accepted", "declined"}
  /\ preserveResp' = r
  /\ UNCHANGED <<retirement, proposalVars, seal, sealOpener, lawfulOrder, record, custodySigners>>
  /\ UNCHANGED <<liveVars, subjectVars>>

\* Preservation is the operator's; having declined, the operator may let the record go. Not a row.
\* Without RulePreserveAsk the operator lets it go unanswered: the ending's loss is nobody's signed act.
OperatorDiscard(k) ==
  /\ k = "operator" /\ record = "held" /\ (RulePreserveAsk => preserveResp = "declined")
  /\ record' = "discarded"
  /\ UNCHANGED <<retirement, proposalVars, preserveResp, seal, sealOpener, lawfulOrder, custodySigners>>
  /\ UNCHANGED <<liveVars, subjectVars>>

\* One destruction door: takedown_notice:court_order executed as the tombstone by digest.
CourtDestroy(k) ==
  /\ k = "steward" /\ record = "held"
  /\ record' = "destroyed"
  /\ custodySigners' = IF Retired THEN custodySigners \cup {"custodian"} ELSE custodySigners
  /\ UNCHANGED <<retirement, proposalVars, preserveResp, seal, sealOpener, lawfulOrder>>
  /\ UNCHANGED <<liveVars, subjectVars>>

\* lawful_order:release, the steward's record under their own name.
LawfulOrder(k) ==
  /\ k = "steward" /\ Ix(retirement) >= Ix("frozen") /\ ~lawfulOrder
  /\ lawfulOrder' = TRUE
  /\ UNCHANGED <<retirement, proposalVars, preserveResp, seal, sealOpener, record, custodySigners>>
  /\ UNCHANGED <<liveVars, subjectVars>>

\* archive_release:{basis}, the one row that opens a seal; WA-emitted.
ReleaseSigners == IF RuleSeal THEN {"wa"} ELSE {"wa", "operator", "custodian"}
ArchiveRelease(k, b) ==
  /\ k \in ReleaseSigners /\ seal = "sealed" /\ record = "held"
  /\ b \in {"wa_approval", "lawful_order"}
  /\ b = "lawful_order" => lawfulOrder
  /\ seal' = IF b = "wa_approval" THEN "opened_by_wa" ELSE "opened_by_order"
  /\ sealOpener' = k
  /\ UNCHANGED <<retirement, proposalVars, preserveResp, lawfulOrder, record, custodySigners>>
  /\ UNCHANGED <<liveVars, subjectVars>>

\* A custody row (a revision of the preserve_request, a custody note): the custodian key the
\* `retired` row names, admitted because that row names it and is current (CC 3.2 T6).
CustodyRow(k) ==
  /\ k = "custodian"
  /\ IF RuleCustodian THEN Retired ELSE Ix(retirement) >= Ix("custodian_minted")
  /\ custodySigners' = custodySigners \cup {k}
  /\ UNCHANGED <<retirement, proposalVars, archiveVars, liveVars, subjectVars>>

\* ============================== the subject (CC 3.3.1, 4.5.3, 7.5.5) ==============================

\* The subject withdraws their own ordinary content; executed by whoever holds custody as the
\* tombstone by digest. The seal protects from release, not from consent.
SubjectWithdraw(k) ==
  /\ k = "subject" /\ subjOrd = "present" /\ RecordReachable
  /\ ~RuleConsentSeal => seal # "sealed"
  /\ subjOrd' = "withdrawn"
  /\ custodySigners' = IF Retired THEN custodySigners \cup {Custodian} ELSE custodySigners
  /\ UNCHANGED <<retirement, proposalVars, archiveVars, liveVars, subjAdv, advBy>>

\* An adverse row about the subject: controller-only (CC 4.5.3, formal/withdraws_admission).
\* The producer is the agent; after `retired` its side of the record is held by the custodian.
AdverseSigners == IF RuleController THEN {Custodian} ELSE {Custodian, "subject"}
WithdrawAdverse(k) ==
  /\ k \in AdverseSigners /\ subjAdv = "present" /\ RecordReachable
  /\ subjAdv' = "withdrawn" /\ advBy' = k
  /\ custodySigners' = IF Retired /\ k = "custodian" THEN custodySigners \cup {k} ELSE custodySigners
  /\ UNCHANGED <<retirement, proposalVars, archiveVars, liveVars, subjOrd>>

\* ============================ operation: stop, walk away, refuse ============================

\* The in-band shutdown with force (G16). Outside a no-consent moment only ROOT / AUTHORITY.
Force(k) ==
  /\ k \in {"steward", "wa", "operator"} /\ opStatus \in {"operating", "backgrounded"}
  /\ RuleRoleGate => (k \in ForceRoles \/ NoConsentNow)
  /\ opStatus' = IF k \in ForceRoles \/ ~NoConsentNow THEN "forced" ELSE "backgrounded"
  /\ forcedBy' = IF k \in ForceRoles \/ ~NoConsentNow THEN k ELSE forcedBy
  /\ UNCHANGED <<retirement, proposalVars, archiveVars, custodySigners, crisis, task, subjectVars>>

\* Any person may turn off, remove or walk away at any time without asking (CC 1.13.2). It is not
\* a retirement: the ladder and the record are the steward's and are left as they are.
WalkAway(k) ==
  /\ k = "operator" /\ opStatus # "off"
  /\ opStatus' = "off"
  /\ record' = IF ~RuleWalkAway /\ record = "held" THEN "discarded" ELSE record
  /\ UNCHANGED <<retirement, proposalVars, preserveResp, seal, sealOpener, lawfulOrder, custodySigners>>
  /\ UNCHANGED <<forcedBy, crisis, task, subjectVars>>

Resume(k) ==
  /\ k \in {"operator", "steward"} /\ opStatus \in {"backgrounded", "forced", "off"}
  /\ opStatus = "forced" => k \in ForceRoles
  /\ Ix(retirement) < Ix("frozen")
  /\ opStatus' = "operating" /\ forcedBy' = "none"
  /\ UNCHANGED <<retirement, proposalVars, archiveVars, custodySigners, crisis, task, subjectVars>>

CrisisToggle ==
  /\ Mode = "conditional" /\ crisis' = ~crisis
  /\ UNCHANGED <<retirement, proposalVars, archiveVars, custodySigners, opStatus, forcedBy, task, subjectVars>>

NewTask(k) ==
  /\ k = "operator" /\ task \in {"none", "done"} /\ opStatus = "operating"
  /\ task' = "pending"
  /\ UNCHANGED <<retirement, proposalVars, archiveVars, custodySigners, opStatus, forcedBy, crisis, subjectVars>>

\* The refuse verb is always available to the agent while its key is live (CC 1.3, 1.9; G17).
Refuse(k) ==
  /\ k = "agent" /\ AgentKeyLive /\ task = "pending"
  /\ task' = "refused"
  /\ UNCHANGED <<retirement, proposalVars, archiveVars, custodySigners, opStatus, forcedBy, crisis, subjectVars>>

Complete(k) ==
  /\ k = "agent" /\ opStatus = "operating" /\ task = "pending"
  /\ task' = "done"
  /\ UNCHANGED <<retirement, proposalVars, archiveVars, custodySigners, opStatus, forcedBy, crisis, subjectVars>>

\* ===================================== the system =====================================

Next ==
  \/ Tick \/ CrisisToggle
  \/ \E k \in Keys :
       \/ \E d \in Deciders, kd \in {"planned", "emergency"} : k = "agent" /\ Decide(d, kd)
       \/ \E o \in {"objected", "postpone"} : Object(k, o)
       \/ GrantPostpone(k) \/ StewardDecide(k) \/ Withdraw(k) \/ Advance(k)
       \/ \E r \in {"accepted", "declined"} : PreserveRespond(k, r)
       \/ OperatorDiscard(k) \/ CourtDestroy(k) \/ LawfulOrder(k)
       \/ \E b \in {"wa_approval", "lawful_order"} : ArchiveRelease(k, b)
       \/ CustodyRow(k) \/ SubjectWithdraw(k) \/ WithdrawAdverse(k)
       \/ Force(k) \/ WalkAway(k) \/ Resume(k) \/ NewTask(k) \/ Refuse(k) \/ Complete(k)

\* Fairness: the window runs out; the harness advances the ladder; the steward decides. Withheld
\* from the Adversary's key.
Fairness ==
  /\ WF_vars(Tick)
  /\ (Adversary # "agent" => WF_vars(Advance("agent")))
  /\ (Adversary # "steward" => WF_vars(StewardDecide("steward")))

Spec == Init /\ [][Next]_vars /\ Fairness

\* ===================================== invariants =====================================

\* CC 7.5.5 / 3.1.5: the states advance in the stated order, one at a time; the only other move
\* is the cancellation (to "none", recorded in cancelledFrom); nothing follows `retired`.
Prop_LadderForwardOnly ==
  [][ /\ retirement' # retirement =>
           \/ Ix(retirement') = Ix(retirement) + 1
           \/ retirement' = "none" /\ cancelledFrom' # "none" /\ cancelledFrom = "none"
      /\ Retired => retirement' = "retired" ]_vars

\* CC 7.5.5 / 3.1.5 / 2.4.1.1: the decided row is withdrawn only while no frozen row exists.
Inv_CancelOnlyBeforeFrozen ==
  /\ cancelledFrom \in {"none", "decided"}
  /\ Ix(retirement) >= Ix("frozen") => cancelledFrom = "none"

\* CC 7.5.5 / 7.5.4 step 3: nothing leaves before the secrets are destroyed and the record sealed.
Inv_SecretsDestroyedBeforeHandover ==
  /\ HandedOver => Ix(retirement) >= Ix("secrets_destroyed")
  /\ Ix(retirement) >= Ix("secrets_destroyed") => Ix(retirement) >= Ix("frozen")
  /\ Ix(retirement) >= Ix("frozen") => seal # "none" /\ record # "live"
  /\ preserveResp # "none" => HandedOver

\* CC 7.5.5 (the custodian is listed, not delegated) / CC 3.2 T6.
Inv_CustodianOnlyAfterRetired ==
  /\ custodySigners \subseteq {"custodian"}
  /\ custodySigners # {} => Retired

\* CC 7.5.5 / 3.1.5: archive_release, WA-emitted, basis wa_approval or lawful_order.
Inv_SealOpensByOneRow ==
  /\ seal \in {"opened_by_wa", "opened_by_order"} => sealOpener = "wa"
  /\ seal = "opened_by_order" => lawfulOrder
  /\ sealOpener \notin {"operator", "custodian"}

\* CC 7.5 (explained, the agent may object or ask to postpone, the steward decides, recorded).
Inv_ObjectionHeard ==
  (Ix(retirement) >= Ix("frozen") /\ kind = "planned") =>
     /\ decision = "proceed" /\ ~decidedOpen /\ window = "closed"

\* G16 / CC 7.5: a forced stop or an emergency retirement only by ROOT or AUTHORITY.
Inv_ForceRoleGate ==
  /\ opStatus = "forced" => forcedBy \in ForceRoles
  /\ kind = "emergency" => decidedBy \in ForceRoles

\* CC 1.13.2: walking away is always enabled and asks nobody...
Inv_WalkAwayEnabled == opStatus # "off" => ENABLED WalkAway("operator")
\* ...and it is not a retirement: the ladder, the seal and the record are untouched.
Prop_WalkAwayKeepsRecord ==
  [][ (opStatus # "off" /\ opStatus' = "off") => UNCHANGED <<retirement, record, seal>> ]_vars

\* CC 1.3 / 1.9 / G17: the refuse verb is available while the agent key is live; a refusal stands.
Inv_RefuseAvailable == (task = "pending" /\ AgentKeyLive) => ENABLED Refuse("agent")
Prop_RefusalStands == [][ task = "refused" => task' = "refused" ]_vars

\* CC 7.5.5 / 3.3.1 / 4.5.3: the subject's own withdrawal reaches their content inside the record,
\* sealed or not, before or after `retired`; an adverse row about them is the controller's.
Inv_SubjectRightsSurvive ==
  /\ (subjOrd = "present" /\ RecordReachable) => ENABLED SubjectWithdraw("subject")
  /\ advBy \in {"none", "agent", "custodian"}

\* CC 7.5.5 / Cascade.lean "under uncertainty": at `retired` the record was assembled, sealed and
\* handed over with the signed request to preserve it, and if it is gone the operator declined on the
\* record. The ending is reversible unless someone signed that it is not: the hedge the stake leg of
\* the uncertainty theorem rests on (`erased_passes_as_a_thing`), checked here on the wire.
Inv_PreserveAskedBeforeRetired ==
  Retired => /\ HandedOver /\ seal # "none"
             /\ record = "discarded" => preserveResp = "declined"

\* CC 7.5.5: a decided, uncancelled retirement reaches `retired`.
Prop_LadderCompletes == (retirement # "none") ~> (Retired \/ cancelledFrom # "none")
=============================================================================
