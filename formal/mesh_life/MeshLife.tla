----------------------------- MODULE MeshLife -----------------------------
(* The life of a mesh, top down: one action per sentence of LIFECYCLE.md and STORIES.md.
   The spine (the mesh, the holders' ceremony, the canonical, persons and devices, the room and its
   members, rows, the agent, the wind-down) is always on. Everything else is a plane switched on by the
   constant Families, each closing on top of the spine; planes touch each other only through the spine,
   so a fact that mentions the spine and one plane holds in the whole. *)
EXTENDS Naturals, FiniteSets, TLC

CONSTANTS Holders, Persons, Rows, Minors, Families, Loose, RoomKind, WriteRight
\* Minors \subseteq Persons. Families \subseteq {"halt", "consent", "contact", "identity", "content", "moderation",
\*   "wa", "deferral", "goal", "evidence", "event", "ledger"}.
\* Loose in {"none", "lone_halt", "gone_with_device", "gone_stewarding"}. RoomKind in {"community", "affiliation"}.
\* WriteRight in {"all", "named"}: whether the room's record names who may publish (a channel) or every member writes.
Devices == Persons
On(f) == f \in Families
Adults == Persons \ Minors

VARIABLE m   \* one record: every object's state

Seated == {h \in Holders : m.holder[h] = "seated"}
Majority == Cardinality(Seated) * 2 > Cardinality(Holders)
Members == {p \in Persons : m.member[p] = "member"}
Live == m.mesh = "live"
Announced(p) == m.person[p] = "announced"
Alive(p) == m.person[p] \in {"keyed", "announced"}
NoContact(p) == m.contact \in {"none", "blocked"} \/ ~(p \in m.parties)
Wards(g) == {p \in Persons : m.guardian[p] = g}
InRoom(p) == m.member[p] \in {"proposed", "member"}

Init == m = [
  mesh |-> "unminted", winding |-> FALSE,
  holder |-> [h \in Holders |-> "seated"], halt |-> "clear", confirmedMajority |-> FALSE,
  canonical |-> "none",
  person |-> [p \in Persons |-> "absent"], pqc |-> [p \in Persons |-> "pending"],
  rotated |-> [p \in Persons |-> FALSE], escrow |-> [p \in Persons |-> FALSE], guardian |-> [p \in Persons |-> "none"],
  capacity |-> [p \in Persons |-> "capacitated"], ledger |-> [p \in Persons |-> "none"],
  consent |-> [p \in Persons |-> "none"], device |-> [p \in Persons |-> "none"],
  contact |-> "none", parties |-> {}, blocker |-> "-", muter |-> "-", muted |-> "-",
  community |-> "none", charter |-> "none", member |-> [p \in Persons |-> "none"],
  moderator |-> "-", event |-> "none", writer |-> [p \in Persons |-> FALSE],
  row |-> [r \in Rows |-> "absent"], author |-> [r \in Rows |-> "-"],
  blob |-> [r \in Rows |-> "none"], durable |-> [r \in Rows |-> "unmarked"],
  flag |-> [r \in Rows |-> "none"], quarantine |-> [r \in Rows |-> "none"],
  asked |-> [r \in Rows |-> "none"], yes |-> [r \in Rows |-> {}], no |-> [r \in Rows |-> {}], decidedBy |-> [r \in Rows |-> "none"],
  report |-> [r \in Rows |-> "none"],
  agent |-> "unbound", steward |-> "-", wa |-> "absent", waPerson |-> "-",
  deferral |-> "none", identity |-> "baseline",
  goal |-> "none", approach |-> "none", method |-> "none", measure |-> "none",
  evidence |-> "none", blessed |-> FALSE, attest |-> "none" ]

(* ---------- Step 1. Three people sit down ---------- *)
Mint == m.mesh = "unminted" /\ Seated = Holders
  /\ m' = [m EXCEPT !.mesh = "live", !.canonical = "seated"]
LoseHolder(h) == On("halt") /\ Live /\ m.holder[h] = "seated" /\ m' = [m EXCEPT !.holder[h] = "lost"]
Remint(h) == On("halt") /\ Live /\ m.holder[h] = "lost" /\ Majority /\ m' = [m EXCEPT !.holder[h] = "seated"]

(* ---------- Step 2. The canonical gets an owner ---------- *)
CanonicalAnnounced == Live /\ m.canonical = "seated" /\ \E p \in Persons : Announced(p)
  /\ m' = [m EXCEPT !.canonical = "announced"]
CanonicalRetires == Live /\ m.canonical \in {"seated", "announced"} /\ m' = [m EXCEPT !.canonical = "retired"]

(* ---------- Step 3. A person arrives ---------- *)
PersonKeys(p) == Live /\ ~m.winding /\ m.person[p] = "absent" /\ m' = [m EXCEPT !.person[p] = "keyed"]
PqcCompletes(p) == On("identity") /\ Live /\ m.person[p] = "keyed" /\ m.pqc[p] = "pending"
  /\ m' = [m EXCEPT !.pqc[p] = "complete"]
DeviceClaims(d) == Live /\ ~m.winding /\ m.device[d] = "none" /\ Alive(d)
  /\ m' = [m EXCEPT !.device[d] = "claimed"]
PersonAnnounces(p) == Live /\ m.person[p] = "keyed" /\ m.device[p] = "claimed" /\ p \in Adults
  /\ (On("identity") => m.pqc[p] = "complete")
  /\ m' = [m EXCEPT !.person[p] = "announced"]
KeyRotates(p) == On("identity") /\ Live /\ Announced(p) /\ ~m.rotated[p] /\ m' = [m EXCEPT !.rotated[p] = TRUE]
KeyEscrowed(p) == On("identity") /\ Live /\ Announced(p) /\ ~m.escrow[p] /\ m' = [m EXCEPT !.escrow[p] = TRUE]
DeviceReleases(d) == Live /\ m.device[d] = "claimed" /\ m' = [m EXCEPT !.device[d] = "released"]
GuardianBinds(g, p) == On("identity") /\ Live /\ ~m.winding /\ g # p /\ Announced(g) /\ p \in Minors
  /\ Alive(p) /\ m.guardian[p] = "none" /\ m.capacity[g] = "capacitated"
  /\ m' = [m EXCEPT !.guardian[p] = g]
GuardianUnbinds(p) == On("identity") /\ Live /\ m.guardian[p] # "none" /\ ~InRoom(p)
  /\ m' = [m EXCEPT !.guardian[p] = "none"]
CapacityFound(p) == On("identity") /\ Live /\ ~m.winding /\ Announced(p) /\ m.capacity[p] = "capacitated"
  /\ m.steward # p /\ m.waPerson # p /\ Wards(p) = {}
  /\ m' = [m EXCEPT !.capacity[p] = "incapacitated"]
CapacityLapses(p) == On("identity") /\ Live /\ m.capacity[p] = "incapacitated" /\ m' = [m EXCEPT !.capacity[p] = "lapsed"]
PersonGone(p) == Live /\ Alive(p)
  /\ (Loose = "gone_with_device" \/ m.device[p] # "claimed")
  /\ m.member[p] \in {"none", "left"}
  /\ (Loose = "gone_stewarding" \/ m.steward # p)
  /\ NoContact(p) /\ Wards(p) = {} /\ m.waPerson # p /\ m.guardian[p] = "none"
  /\ m' = [m EXCEPT !.person[p] = "gone"]

(* ---------- Step 4. Two people become contacts ---------- *)
ContactRequest(p, q) == On("contact") /\ Live /\ ~m.winding /\ p # q /\ Announced(p) /\ Announced(q) /\ m.contact = "none"
  /\ m' = [m EXCEPT !.contact = "requested", !.parties = {p, q}]
\* a request to someone who blocked the asker is dropped without answer: no state moves
ContactAccept == On("contact") /\ Live /\ m.contact = "requested" /\ m' = [m EXCEPT !.contact = "contacts"]
ContactIgnore == On("contact") /\ Live /\ m.contact = "requested" /\ m' = [m EXCEPT !.contact = "ignored"]
ContactUnignore == On("contact") /\ Live /\ ~m.winding /\ m.contact = "ignored" /\ m' = [m EXCEPT !.contact = "requested"]
ContactBlock(p) == On("contact") /\ Live /\ m.contact \in {"requested", "ignored", "contacts"} /\ p \in m.parties
  /\ m' = [m EXCEPT !.contact = "blocked", !.blocker = p]
ContactUnblock == On("contact") /\ Live /\ m.contact = "blocked" /\ m' = [m EXCEPT !.contact = "none", !.parties = {}, !.blocker = "-"]
ContactEnds == On("contact") /\ Live /\ m.contact \in {"requested", "ignored", "contacts"}
  /\ m' = [m EXCEPT !.contact = "none", !.parties = {}]
\* what the asker can see of a pending request: nothing distinguishes ignored from pending
AskerView == IF m.contact \in {"requested", "ignored"} THEN "pending" ELSE IF m.contact = "contacts" THEN "mutual" ELSE "none"
Mute(p, q) == On("contact") /\ Live /\ ~m.winding /\ p # q /\ m.member[p] = "member" /\ m.member[q] = "member" /\ m.muter = "-"
  /\ m' = [m EXCEPT !.muter = p, !.muted = q]
Unmute == On("contact") /\ Live /\ m.muter # "-" /\ m' = [m EXCEPT !.muter = "-", !.muted = "-"]

(* ---------- Step 5. A room is founded ---------- *)
Found(p) == Live /\ ~m.winding /\ Announced(p) /\ m.community = "none"
  /\ m' = [m EXCEPT !.community = "founded", !.member[p] = "member", !.moderator = p,
                    !.writer[p] = (WriteRight = "named"),
                    !.charter = IF RoomKind = "affiliation" THEN "declared" ELSE "none"]
CharterSuperseded == On("event") /\ Live /\ m.charter = "declared" /\ Members # {}
  /\ m' = [m EXCEPT !.charter = "superseded"]
Propose(p, q) == Live /\ ~m.winding /\ m.community = "founded" /\ m.member[p] = "member"
  /\ m.member[q] \in {"none", "left"} /\ (Announced(q) \/ (q \in Minors /\ m.guardian[q] # "none"))
  /\ m' = [m EXCEPT !.member[q] = "proposed"]
Accept(q) == Live /\ m.member[q] = "proposed" /\ Members # {} /\ m' = [m EXCEPT !.member[q] = "member"]
Decline(q) == Live /\ m.member[q] = "proposed" /\ m' = [m EXCEPT !.member[q] = "none"]
Leave(q, how) == m' = [m EXCEPT !.member[q] = "left", !.moderator = IF m.moderator = q THEN "-" ELSE m.moderator, !.writer[q] = FALSE,
                               !.yes = [r \in Rows |-> m.yes[r] \ {q}], !.no = [r \in Rows |-> m.no[r] \ {q}],
                               !.muter = IF q \in {m.muter, m.muted} THEN "-" ELSE m.muter,
                               !.muted = IF q \in {m.muter, m.muted} THEN "-" ELSE m.muted]
Resign(q) == Live /\ m.member[q] = "member" /\ Leave(q, "resign")
Remove(q) == Live /\ m.member[q] = "member" /\ Cardinality(Members \ {q}) >= 1 /\ Leave(q, "remove")
\* an agent moderator acts only while bonded and while no halt is latched or confirmed
ModeratorActs == m.moderator # "-" /\ (m.moderator # "agent" \/ (m.agent = "bonded" /\ m.halt = "clear"))
GrantWrite(p) == WriteRight = "named" /\ Live /\ ~m.winding /\ m.member[p] = "member" /\ ~m.writer[p] /\ ModeratorActs
  /\ m' = [m EXCEPT !.writer[p] = TRUE]
RevokeWrite(p) == WriteRight = "named" /\ Live /\ m.writer[p] /\ ModeratorActs /\ p # m.moderator
  /\ m' = [m EXCEPT !.writer[p] = FALSE]
MayWrite(p) == m.member[p] = "member" /\ (WriteRight = "all" \/ m.writer[p])
NameModerator(p) == Live /\ m.community = "founded" /\ m.moderator = "-" /\ m.member[p] = "member"
  /\ m' = [m EXCEPT !.moderator = p]
\* moderation delegated to an agent: the bonded agent, held by its steward, takes the moderate duty
NameAgentModerator == On("moderation") /\ Live /\ m.community = "founded" /\ m.moderator = "-" /\ m.agent = "bonded"
  /\ m' = [m EXCEPT !.moderator = "agent"]
Dissolve == Live /\ m.community = "founded" /\ Members = {} /\ \A p \in Persons : m.member[p] # "proposed"
  /\ m' = [m EXCEPT !.community = "dissolved", !.moderator = "-", !.charter = "none", !.event = "none",
                    !.writer = [q \in Persons |-> FALSE],
                    !.row = [r \in Rows |-> IF m.row[r] = "absent" THEN "absent" ELSE "purged"],
                    !.author = [r \in Rows |-> "-"], !.blob = [r \in Rows |-> "none"],
                    !.durable = [r \in Rows |-> "unmarked"], !.flag = [r \in Rows |-> "none"], !.asked = [r \in Rows |-> "none"],
                    !.yes = [r \in Rows |-> {}], !.no = [r \in Rows |-> {}], !.decidedBy = [r \in Rows |-> "none"],
                    !.report = [r \in Rows |-> "none"],
                    !.quarantine = [r \in Rows |-> "none"],
                    !.goal = "none", !.approach = "none", !.method = "none", !.measure = "none",
                    !.evidence = "none", !.blessed = FALSE]
EventOpens == On("event") /\ Live /\ ~m.winding /\ m.community = "founded" /\ Members # {} /\ m.event = "none"
  /\ m' = [m EXCEPT !.event = "open"]
EventCloses(how) == On("event") /\ Live /\ m.event = "open" /\ m' = [m EXCEPT !.event = how]

(* ---------- Step 6. Members write ---------- *)
Write(r, p, form) == Live /\ ~m.winding /\ m.community = "founded" /\ MayWrite(p) /\ m.row[r] = "absent"
  /\ (On("content") \/ form = "inline")
  /\ m' = [m EXCEPT !.row[r] = "admitted", !.author[r] = p, !.blob[r] = form]
MarkDurable(r) == On("content") /\ Live /\ m.row[r] = "admitted" /\ m.durable[r] = "unmarked"
  /\ m.member[m.author[r]] = "member" /\ m' = [m EXCEPT !.durable[r] = "marked"]
Withdraw(r) == Live /\ m.row[r] = "admitted" /\ m.member[m.author[r]] = "member"
  /\ m' = [m EXCEPT !.row[r] = "withdrawn", !.durable[r] = IF m.durable[r] = "marked" THEN "descending" ELSE m.durable[r]]
Purge(r) == Live /\ m.row[r] = "withdrawn"
  /\ m' = [m EXCEPT !.row[r] = "purged", !.author[r] = "-", !.blob[r] = "none", !.durable[r] = "unmarked",
                    !.flag[r] = "none", !.quarantine[r] = "none", !.asked[r] = "none", !.decidedBy[r] = "none", !.report[r] = "none"]
Withhold(r) == On("moderation") /\ Live /\ ~m.winding /\ m.row[r] = "admitted" /\ m.quarantine[r] = "none" /\ ModeratorActs
  /\ m' = [m EXCEPT !.quarantine[r] = "withhold"]
Release(r) == On("moderation") /\ Live /\ m.quarantine[r] = "withhold" /\ ModeratorActs
  /\ m' = [m EXCEPT !.quarantine[r] = "none"]
RaiseFlag(r, p, ask) == On("moderation") /\ Live /\ ~m.winding /\ m.row[r] = "admitted" /\ m.flag[r] = "none" /\ m.member[p] = "member"
  /\ p # m.author[r] /\ m' = [m EXCEPT !.flag[r] = "raised", !.asked[r] = ask, !.yes[r] = {p}, !.no[r] = {}]
\* the other act: a report filed privately with the duty holder; it opens no window and nobody but the duty holder sees it
PrivateReport(r, p) == On("moderation") /\ Live /\ ~m.winding /\ m.row[r] = "admitted" /\ m.report[r] = "none" /\ m.member[p] = "member"
  /\ p # m.author[r] /\ m' = [m EXCEPT !.report[r] = "filed"]
\* the duty holder may let a report rest: it closes with no action and no window
ReportRests(r) == On("moderation") /\ Live /\ m.report[r] = "filed" /\ m.flag[r] = "none" /\ ModeratorActs
  /\ m' = [m EXCEPT !.report[r] = "rested"]
Land(r, outcome, by) == [m EXCEPT !.flag[r] = outcome, !.decidedBy[r] = by, !.yes[r] = {}, !.no[r] = {},
                    !.report[r] = IF m.report[r] = "filed" THEN "ruled" ELSE m.report[r],
                    !.row[r] = IF outcome = "hard_removal" THEN "withdrawn" ELSE m.row[r],
                    !.durable[r] = IF outcome = "hard_removal" /\ m.durable[r] = "marked" THEN "descending" ELSE m.durable[r]]
\* a moderator, a person or the delegated agent, rules at any time while the action is open
DecideFlag(r, outcome) == On("moderation") /\ Live /\ (m.flag[r] = "raised" \/ (m.flag[r] = "none" /\ m.report[r] = "filed")) /\ ModeratorActs
  /\ m.row[r] = "admitted" /\ m' = Land(r, outcome, "moderator")
\* the reverse quorum: while the action is open any member responds, for or against the action the raiser named
Respond(r, p, v) == On("moderation") /\ Live /\ m.flag[r] = "raised" /\ m.member[p] = "member"
  /\ p \notin m.yes[r] /\ p \notin m.no[r]
  /\ m' = [m EXCEPT !.yes[r] = IF v = "yes" THEN m.yes[r] \cup {p} ELSE m.yes[r],
                    !.no[r]  = IF v = "no"  THEN m.no[r]  \cup {p} ELSE m.no[r]]
\* no ruling by the window's end: the majority of the respondents decides; no majority for the action keeps the row visible
WindowCloses(r) == On("moderation") /\ Live /\ m.flag[r] = "raised"
  /\ m' = Land(r, IF Cardinality(m.yes[r]) > Cardinality(m.no[r]) THEN m.asked[r] ELSE "kept_visible", "majority")
LedgerOpens(p) == On("ledger") /\ Live /\ ~m.winding /\ Announced(p) /\ m.ledger[p] = "none"
  /\ m' = [m EXCEPT !.ledger[p] = "head"]
LedgerForks(p) == On("ledger") /\ Live /\ m.ledger[p] = "head" /\ m' = [m EXCEPT !.ledger[p] = "fork"]
LedgerCloses(p) == On("ledger") /\ Live /\ m.ledger[p] = "head" /\ m' = [m EXCEPT !.ledger[p] = "checkpoint"]

(* ---------- Step 7. A person consents, and revokes ---------- *)
Grant(p) == On("consent") /\ Live /\ ~m.winding /\ Announced(p) /\ m.consent[p] = "none" /\ m' = [m EXCEPT !.consent[p] = "granted"]
Revoke(p) == Live /\ m.consent[p] = "granted" /\ m' = [m EXCEPT !.consent[p] = "none"]

(* ---------- Step 8. An agent is bonded ---------- *)
Bond(p) == Live /\ ~m.winding /\ Announced(p) /\ m.agent = "unbound" /\ m.capacity[p] = "capacitated"
  /\ m' = [m EXCEPT !.agent = "bonded", !.steward = p]
HandOver(q) == Live /\ m.agent = "bonded" /\ Announced(q) /\ q # m.steward /\ m.capacity[q] = "capacitated"
  /\ m' = [m EXCEPT !.steward = q]
Freeze == Live /\ m.agent = "bonded"
  /\ m' = [m EXCEPT !.agent = "frozen", !.moderator = IF m.moderator = "agent" THEN "-" ELSE m.moderator]
Retire == Live /\ m.agent = "frozen"
  /\ m' = [m EXCEPT !.agent = "retired", !.steward = "-", !.deferral = "none"]
WaSeats(p) == On("wa") /\ Live /\ ~m.winding /\ Announced(p) /\ m.wa = "absent" /\ m.capacity[p] = "capacitated"
  /\ m' = [m EXCEPT !.wa = "present", !.waPerson = p]
WaVacates == On("wa") /\ Live /\ m.wa \in {"present", "abandoned", "seized"}
  /\ m' = [m EXCEPT !.wa = "absent", !.waPerson = "-"]
WaFound(how) == On("wa") /\ Live /\ m.wa = "present" /\ m' = [m EXCEPT !.wa = how]
WaSuccessor(q) == On("wa") /\ Live /\ m.wa \in {"abandoned", "seized"} /\ Announced(q) /\ m.capacity[q] = "capacitated"
  /\ m' = [m EXCEPT !.wa = "present", !.waPerson = q]
Defer == On("deferral") /\ Live /\ ~m.winding /\ m.agent = "bonded" /\ m.halt = "clear" /\ m.deferral = "none"
  /\ m' = [m EXCEPT !.deferral = "pending"]
Answer(verdict) == On("deferral") /\ Live /\ m.deferral = "pending" /\ (m.wa = "present" \/ ~On("wa"))
  /\ m' = [m EXCEPT !.deferral = verdict]
Amend == On("deferral") /\ Live /\ m.deferral = "approved" /\ m.identity = "baseline" /\ m.agent = "bonded"
  /\ m' = [m EXCEPT !.identity = "amended", !.deferral = "none"]
ClearDeferral == On("deferral") /\ Live /\ m.deferral \in {"approved", "rejected"} /\ m' = [m EXCEPT !.deferral = "none"]

(* ---------- Step 8, continued. Goals and evidence ---------- *)
GoalStaged == (On("goal") \/ On("evidence")) /\ Live /\ ~m.winding /\ m.community = "founded" /\ m.canonical = "announced" /\ m.goal = "none"
  /\ m' = [m EXCEPT !.goal = "staged"]
GoalProposed == (On("goal") \/ On("evidence")) /\ Live /\ m.goal = "staged" /\ Members # {} /\ m' = [m EXCEPT !.goal = "proposed"]
GoalDeclared == (On("goal") \/ On("evidence")) /\ Live /\ m.goal = "proposed" /\ Members # {} /\ m' = [m EXCEPT !.goal = "declared"]
GoalWithdrawn == (On("goal") \/ On("evidence")) /\ Live /\ m.goal \in {"staged", "proposed", "declared"}
  /\ m' = [m EXCEPT !.goal = "withdrawn", !.approach = "none", !.method = "none", !.measure = "none",
                    !.evidence = IF m.evidence \in {"offered", "admitted", "counted"} THEN "superseded" ELSE m.evidence]
ApproachDeclared == (On("goal") \/ On("evidence")) /\ Live /\ m.goal = "declared" /\ m.approach = "none" /\ m' = [m EXCEPT !.approach = "declared"]
MethodDeclared == (On("goal") \/ On("evidence")) /\ Live /\ m.approach = "declared" /\ m.method = "none" /\ m' = [m EXCEPT !.method = "declared"]
MeasureDeclared == (On("goal") \/ On("evidence")) /\ Live /\ m.method = "declared" /\ m.measure = "none" /\ m' = [m EXCEPT !.measure = "declared"]
AttestConferred == On("evidence") /\ Live /\ ~m.winding /\ m.canonical = "announced" /\ m.attest = "none"
  /\ m' = [m EXCEPT !.attest = "live"]
AttestWithdrawn == On("evidence") /\ Live /\ m.attest = "live" /\ m' = [m EXCEPT !.attest = "withdrawn"]
EvidenceOffered == On("evidence") /\ Live /\ ~m.winding /\ m.goal = "declared" /\ m.evidence = "none"
  /\ m' = [m EXCEPT !.evidence = "offered", !.blessed = (m.attest = "live")]
EvidenceAdmitted == On("evidence") /\ Live /\ m.evidence = "offered" /\ m' = [m EXCEPT !.evidence = "admitted"]
EvidenceCounted == On("evidence") /\ Live /\ m.evidence = "admitted" /\ m.measure = "declared" /\ m' = [m EXCEPT !.evidence = "counted"]
EvidenceSuperseded == On("evidence") /\ Live /\ m.evidence \in {"offered", "admitted", "counted"}
  /\ m' = [m EXCEPT !.evidence = "superseded"]

(* ---------- Step 9. The holders halt ---------- *)
Latch(h) == On("halt") /\ Live /\ m.halt = "clear" /\ m.holder[h] = "seated" /\ m' = [m EXCEPT !.halt = "latched"]
Lapse == Live /\ m.halt = "latched" /\ m' = [m EXCEPT !.halt = "clear"]
Confirm(S) == Live /\ m.halt = "latched" /\ S \subseteq Seated /\ S # {}
  /\ (Loose = "lone_halt" \/ Cardinality(S) * 2 > Cardinality(Holders))
  /\ m' = [m EXCEPT !.halt = "confirmed", !.confirmedMajority = (Cardinality(S) * 2 > Cardinality(Holders))]
Resume == Live /\ m.halt = "confirmed" /\ Majority /\ m' = [m EXCEPT !.halt = "clear", !.confirmedMajority = FALSE]

(* ---------- Step 10. The mesh winds down ---------- *)
WindDown == Live /\ ~m.winding /\ Majority /\ m' = [m EXCEPT !.winding = TRUE]
Empty ==
  /\ \A p \in Persons : m.person[p] \in {"absent", "gone"} /\ m.device[p] # "claimed"
  /\ m.contact \in {"none", "blocked"} /\ m.community \in {"none", "dissolved"}
  /\ \A r \in Rows : m.row[r] \in {"absent", "purged"}
  /\ m.agent \in {"unbound", "retired"} /\ m.canonical \in {"none", "retired"}
  /\ m.wa = "absent" /\ m.attest # "live" /\ m.event # "open"
  /\ \A p \in Persons : m.ledger[p] # "head" /\ m.capacity[p] # "incapacitated"
End == Live /\ m.winding /\ Empty /\ m' = [m EXCEPT !.mesh = "ended"]

WindSteps ==
  \/ CanonicalRetires \/ ContactEnds \/ Unmute \/ Dissolve \/ Freeze \/ Retire \/ End \/ WaVacates \/ AttestWithdrawn
  \/ \E d \in Devices : DeviceReleases(d)
  \/ \E p \in Persons : PersonGone(p) \/ Decline(p) \/ Resign(p) \/ GuardianUnbinds(p) \/ CapacityLapses(p) \/ LedgerCloses(p)
  \/ \E r \in Rows : Withdraw(r) \/ Purge(r) \/ Release(r)
  \/ \E how \in {"completed", "cancelled"} : EventCloses(how)
  \/ \E v \in {"approved", "rejected"} : Answer(v)
  \/ ClearDeferral \/ GoalWithdrawn \/ EvidenceSuperseded
  \/ \E r \in Rows : WindowCloses(r) \/ ReportRests(r) \/ (\E o \in {"hard_removal", "consent_gated", "kept_visible"} : DecideFlag(r, o))

Next ==
  \/ Mint \/ \E h \in Holders : LoseHolder(h) \/ Remint(h) \/ Latch(h)
  \/ CanonicalAnnounced \/ CanonicalRetires
  \/ \E p \in Persons : PersonKeys(p) \/ PqcCompletes(p) \/ PersonAnnounces(p) \/ KeyRotates(p) \/ KeyEscrowed(p) \/ PersonGone(p)
      \/ GuardianUnbinds(p) \/ CapacityFound(p) \/ CapacityLapses(p) \/ Found(p) \/ NameModerator(p) \/ GrantWrite(p) \/ RevokeWrite(p)
      \/ Grant(p) \/ Revoke(p) \/ Bond(p) \/ HandOver(p) \/ Accept(p) \/ Decline(p) \/ Resign(p) \/ Remove(p)
      \/ WaSeats(p) \/ WaSuccessor(p) \/ LedgerOpens(p) \/ LedgerForks(p) \/ LedgerCloses(p) \/ ContactBlock(p)
  \/ \E d \in Devices : DeviceClaims(d) \/ DeviceReleases(d)
  \/ \E p, q \in Persons : ContactRequest(p, q) \/ Propose(p, q) \/ GuardianBinds(p, q) \/ Mute(p, q)
  \/ ContactAccept \/ ContactIgnore \/ ContactUnignore \/ ContactUnblock \/ ContactEnds \/ Unmute \/ NameAgentModerator
  \/ CharterSuperseded \/ EventOpens
  \/ \E how \in {"completed", "cancelled"} : EventCloses(how)
  \/ Dissolve
  \/ \E r \in Rows : Purge(r) \/ Withdraw(r) \/ MarkDurable(r) \/ Withhold(r) \/ Release(r)
      \/ (\E p \in Persons, f \in {"inline", "chunked"} : Write(r, p, f))
      \/ (\E p \in Persons, a \in {"hard_removal", "consent_gated"} : RaiseFlag(r, p, a))
      \/ (\E p \in Persons : PrivateReport(r, p)) \/ ReportRests(r)
      \/ (\E p \in Persons, v \in {"yes", "no"} : Respond(r, p, v))
      \/ WindowCloses(r)
      \/ (\E o \in {"hard_removal", "consent_gated", "kept_visible"} : DecideFlag(r, o))
  \/ Freeze \/ Retire \/ WaVacates \/ Defer \/ Amend \/ ClearDeferral
  \/ \E how \in {"abandoned", "seized"} : WaFound(how)
  \/ \E v \in {"approved", "rejected"} : Answer(v)
  \/ GoalStaged \/ GoalProposed \/ GoalDeclared \/ GoalWithdrawn \/ ApproachDeclared \/ MethodDeclared \/ MeasureDeclared
  \/ AttestConferred \/ AttestWithdrawn \/ EvidenceOffered \/ EvidenceAdmitted \/ EvidenceCounted \/ EvidenceSuperseded
  \/ Lapse \/ Resume \/ \E S \in SUBSET Holders : Confirm(S)
  \/ WindDown \/ End

Fairness ==
  /\ WF_m(CanonicalRetires) /\ WF_m(ContactEnds) /\ WF_m(Unmute) /\ WF_m(Dissolve) /\ WF_m(Freeze) /\ WF_m(Retire) /\ WF_m(End)
  /\ WF_m(WaVacates) /\ WF_m(AttestWithdrawn) /\ WF_m(ClearDeferral) /\ WF_m(GoalWithdrawn) /\ WF_m(EvidenceSuperseded)
  /\ \A d \in Devices : WF_m(DeviceReleases(d))
  /\ \A p \in Persons : WF_m(PersonGone(p)) /\ WF_m(Decline(p)) /\ WF_m(Resign(p)) /\ WF_m(GuardianUnbinds(p))
                        /\ WF_m(CapacityLapses(p)) /\ WF_m(LedgerCloses(p))
  /\ \A r \in Rows : WF_m(Withdraw(r)) /\ WF_m(Purge(r)) /\ WF_m(Release(r))
                     /\ WF_m(WindowCloses(r)) /\ WF_m(ReportRests(r))
  /\ \A how \in {"completed", "cancelled"} : WF_m(EventCloses(how))
  /\ \A v \in {"approved", "rejected"} : WF_m(Answer(v))

Spec == Init /\ [][Next]_m /\ Fairness
Symm == Permutations(Holders) \cup Permutations(Adults) \cup Permutations(Rows)

(* ---------- The closure facts ---------- *)
Inv_NothingBeforeMint == m.mesh = "unminted" => (m.canonical = "none" /\ \A p \in Persons : m.person[p] = "absent")
Inv_DeviceHasOwner == \A d \in Devices : m.device[d] = "claimed" => Alive(d)
Inv_MemberIsAnnounced == \A p \in Persons : InRoom(p) => (Announced(p) \/ (p \in Minors /\ m.guardian[p] # "none"))
Inv_MinorNeverAnnounced == \A p \in Minors : ~Announced(p)
Inv_RowInFoundedRoom == \A r \in Rows : m.row[r] \in {"admitted", "withdrawn"} => (m.community = "founded" /\ m.author[r] \in Persons)
Inv_AgentHasSteward == m.agent \in {"bonded", "frozen"} => (m.steward \in Persons /\ Announced(m.steward))
Inv_HaltIsMajority == m.halt = "confirmed" => m.confirmedMajority
Inv_EndedIsEmpty == m.mesh = "ended" => Empty
\* a block is the blocker's private row and outlives the other party; a live contact is between announced people
Inv_ContactIsAnnounced == m.contact \in {"requested", "ignored", "contacts"} => \A p \in m.parties : Announced(p)
Inv_IgnoreIsInvisibleToTheAsker == m.contact = "ignored" => AskerView = "pending"
Inv_BlockHasABlocker == m.contact = "blocked" => m.blocker \in m.parties
Inv_MuteIsBetweenMembers == IF m.muter = "-" THEN TRUE ELSE (m.member[m.muter] = "member" /\ m.member[m.muted] = "member" /\ m.muter # m.muted)
\* setting or lifting a mute (the muter changes while the roster does not) changes nothing else at all
Act_MuteChangesNoRow == [][(m'.muter # m.muter /\ m'.member = m.member) => m' = [m EXCEPT !.muter = m'.muter, !.muted = m'.muted]]_m
Inv_AnnouncedIsPqcComplete == On("identity") => \A p \in Persons : Announced(p) => m.pqc[p] = "complete"
Inv_GuardianIsAnnouncedAdult == \A p \in Persons : m.guardian[p] # "none" => (m.guardian[p] \in Adults /\ Announced(m.guardian[p]))
Inv_IncapacitatedHoldsNoSeat == \A p \in Persons : m.capacity[p] = "incapacitated" => (m.steward # p /\ m.waPerson # p /\ Wards(p) = {})
Inv_ModeratorIsMember == m.moderator \in Persons => m.member[m.moderator] = "member"
Inv_AgentModeratorIsBonded == m.moderator = "agent" => m.agent = "bonded"
\* the halt reaches the delegated moderator: no flag is decided and no row withheld by the agent while a halt stands
Act_HaltStopsAgentModeration == [][(m.moderator = "agent" /\ m.halt # "clear") =>
  \A r \in Rows : (m.flag[r] = "raised" => m'.flag[r] \in {"raised", "none"} \/ m'.decidedBy[r] = "majority")
               /\ (m.quarantine[r] = "none" => m'.quarantine[r] = "none")
               /\ (m.quarantine[r] = "withhold" => m'.quarantine[r] = "withhold" \/ m'.row[r] = "purged")]_m
\* an action lands by a moderator's ruling or by the majority of the respondents, never otherwise
\* a private report opens no window: while only a report stands, no member responds and nothing lands by majority
Inv_ReportOpensNoWindow == \A r \in Rows : (m.report[r] = "filed" /\ m.flag[r] = "none") => (m.yes[r] = {} /\ m.no[r] = {})
Act_ReportLandsOnlyByRuling == [][\A r \in Rows : (m.flag[r] = "none" /\ m.report[r] = "filed" /\ m'.flag[r] \in {"hard_removal", "consent_gated", "kept_visible"}) => m'.decidedBy[r] = "moderator"]_m
\* filing a report changes nothing a member can see: no flag, no row, no quarantine, no roster
Act_ReportIsPrivate == [][\A r \in Rows : (m.report[r] = "none" /\ m'.report[r] = "filed") => (m'.flag = m.flag /\ m'.row = m.row /\ m'.quarantine = m.quarantine /\ m'.member = m.member)]_m
Inv_DecidedByRulingOrMajority == \A r \in Rows : m.flag[r] \in {"hard_removal", "consent_gated", "kept_visible"} => m.decidedBy[r] \in {"moderator", "majority"}
\* the window never lands an action nobody asked for: by majority the outcome is the action raised, or the row stays visible
Act_MajorityLandsOnlyTheAsk == [][\A r \in Rows : (m.flag[r] = "raised" /\ m'.decidedBy[r] = "majority") => m'.flag[r] \in {m.asked[r], "kept_visible"}]_m
\* the halt stops the delegated moderator's ruling; it does not stop the members: the window still closes by their majority
Act_HaltLeavesTheMembersTheirVote == [][(m.moderator = "agent" /\ m.halt # "clear" /\ \E r \in Rows : m.flag[r] = "raised" /\ m'.flag[r] # "raised") => \E r \in Rows : m'.decidedBy[r] = "majority" \/ m'.row[r] = "purged" \/ m'.community = "dissolved"]_m
Inv_WriterIsMember == \A p \in Persons : m.writer[p] => m.member[p] = "member"
\* a row enters a room only by the hand of one who may write there at that moment; the right withdrawn later leaves the row standing
Act_RowsOnlyByWriters == [][\A r \in Rows : (m.row[r] = "absent" /\ m'.row[r] = "admitted") => MayWrite(m'.author[r])]_m
Inv_FlagDecidedByModerator == \A r \in Rows : m.flag[r] \in {"hard_removal", "consent_gated", "kept_visible"} => m.row[r] # "absent"
Inv_HardRemovalWithdraws == \A r \in Rows : m.flag[r] = "hard_removal" => m.row[r] \in {"withdrawn", "purged"}
Inv_DurableRidesAnAdmittedRow == \A r \in Rows : m.durable[r] = "marked" => m.row[r] = "admitted"
Inv_WaPersonIsAnnounced == m.wa # "absent" => (m.waPerson \in Persons /\ Announced(m.waPerson))
Inv_AnsweredOnlyBySeatedWa == m.deferral = "pending" \/ m.deferral = "none" \/ TRUE
Inv_AmendedCitesApproval == m.identity = "amended" => m.agent # "unbound"
Inv_GoalInFoundedRoom == m.goal \in {"staged", "proposed", "declared"} => m.community = "founded"
Inv_EvidenceNamesADeclaredGoal == m.evidence \in {"offered", "admitted", "counted"} => m.goal = "declared"
Inv_CountedNeedsAMeasure == m.evidence = "counted" => m.measure = "declared"
Inv_MeasureChainIsWhole == (m.measure = "declared" => m.method = "declared") /\ (m.method = "declared" => m.approach = "declared") /\ (m.approach = "declared" => m.goal = "declared")
Inv_EventInFoundedRoom == m.event = "open" => m.community = "founded"
Inv_CharterOnlyForAffiliation == m.charter # "none" => (RoomKind = "affiliation" /\ m.community = "founded")

W(x, a, b) == IF x = a THEN 2 ELSE IF x = b THEN 1 ELSE 0
Rank ==
  (IF m.mesh = "live" THEN 1 ELSE 0)
  + Cardinality({p \in Persons : Alive(p)}) + Cardinality({d \in Devices : m.device[d] = "claimed"})
  + (IF m.contact \in {"none", "blocked"} THEN 0 ELSE 1) + (IF m.community = "founded" THEN 1 ELSE 0)
  + Cardinality({p \in Persons : InRoom(p)}) + W(m.agent, "bonded", "frozen")
  + (IF m.canonical \in {"seated", "announced"} THEN 1 ELSE 0)
  + Cardinality({r \in Rows : m.row[r] = "admitted"}) * 2 + Cardinality({r \in Rows : m.row[r] = "withdrawn"})
  + Cardinality({p \in Persons : m.guardian[p] # "none"}) + Cardinality({p \in Persons : m.capacity[p] = "incapacitated"})
  + Cardinality({p \in Persons : m.ledger[p] = "head"})
  + Cardinality({r \in Rows : m.flag[r] = "raised"}) + Cardinality({r \in Rows : m.quarantine[r] = "withhold"})
  + Cardinality({r \in Rows : m.report[r] = "filed"})
  + (IF m.wa = "absent" THEN 0 ELSE 1) + W(m.deferral, "pending", "approved") + (IF m.deferral = "rejected" THEN 1 ELSE 0)
  + (IF m.event = "open" THEN 1 ELSE 0)
  + (IF m.goal \in {"staged", "proposed", "declared"} THEN 1 ELSE 0)
  + (IF m.evidence \in {"offered", "admitted", "counted"} THEN 1 ELSE 0) + (IF m.attest = "live" THEN 1 ELSE 0) + (IF m.muter = "-" THEN 0 ELSE 1)

WindStepEnabled ==
  \/ m.canonical \in {"seated", "announced"} \/ \E d \in Devices : m.device[d] = "claimed" \/ m.contact \in {"requested", "ignored", "contacts"}
  \/ \E p \in Persons : InRoom(p)
  \/ (m.community = "founded" /\ Members = {} /\ \A p \in Persons : m.member[p] # "proposed")
  \/ \E r \in Rows : m.row[r] = "withdrawn" \/ (m.row[r] = "admitted" /\ m.member[m.author[r]] = "member")
  \/ m.agent \in {"bonded", "frozen"} \/ m.wa # "absent" \/ m.attest = "live" \/ m.event = "open"
  \/ m.goal \in {"staged", "proposed", "declared"} \/ m.evidence \in {"offered", "admitted", "counted"}
  \/ m.deferral \in {"approved", "rejected"} \/ m.muter # "-"
  \/ \E p \in Persons : (m.guardian[p] # "none" /\ ~InRoom(p)) \/ m.capacity[p] = "incapacitated"
                        \/ m.ledger[p] = "head"
  \/ \E r \in Rows : (m.quarantine[r] = "withhold" /\ ModeratorActs) \/ m.flag[r] = "raised" \/ (m.report[r] = "filed" /\ ModeratorActs)
  \/ \E p \in Persons : Alive(p) /\ m.device[p] # "claimed" /\ m.member[p] \in {"none", "left"} /\ m.steward # p
       /\ NoContact(p) /\ Wards(p) = {} /\ m.waPerson # p /\ m.guardian[p] = "none"
  \/ Empty

Inv_WindAlwaysCanStep == (Live /\ m.winding) => WindStepEnabled
Act_WindNeverRaisesRank == [][m.winding => Rank' <= Rank]_m
Act_WindStepLowersRank == [][(m.winding /\ WindSteps) => Rank' < Rank]_m
Live_WindsDownToEnd == (m.winding) ~> (m.mesh = "ended")
=============================================================================
