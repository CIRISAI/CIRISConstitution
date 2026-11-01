----------------------------- MODULE MeshLife -----------------------------
(* The life of a mesh, top down: one action per sentence of LIFECYCLE.md. *)
EXTENDS Naturals, FiniteSets, TLC

CONSTANTS Holders, Persons, Rows, Loose
\* Loose in {"none", "lone_halt", "gone_with_device", "gone_stewarding"}.
\* One device per person in this bound: a device is named by its owner.
Devices == Persons
Owner(d) == d

VARIABLES mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties,
          community, member, row, rowAuthor, consent, agent, steward, winding

vars == <<mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties,
          community, member, row, rowAuthor, consent, agent, steward, winding>>

Seated == {h \in Holders : holder[h] = "seated"}
Majority == Cardinality(Seated) * 2 > Cardinality(Holders)
Members == {p \in Persons : member[p] = "member"}
DevicesOf(p) == {p}
Live == mesh = "live"
Announced(p) == person[p] = "announced"
NoContact(p) == ~(p \in contactParties)

Init ==
  /\ mesh = "unminted"
  /\ holder = [h \in Holders |-> "seated"]
  /\ halt = "clear" /\ confirmedMajority = FALSE
  /\ canonical = "none"
  /\ person = [p \in Persons |-> "absent"]
  /\ device = [d \in Devices |-> "none"]
  /\ contact = "none" /\ contactParties = {}
  /\ community = "none"
  /\ member = [p \in Persons |-> "none"]
  /\ row = [r \in Rows |-> "absent"] /\ rowAuthor = [r \in Rows |-> "-"]
  /\ consent = [p \in Persons |-> "none"]
  /\ agent = "unbound" /\ steward = "-"
  /\ winding = FALSE

(* 1. Three people sit down *)
Mint ==
  /\ mesh = "unminted" /\ Seated = Holders
  /\ mesh' = "live" /\ canonical' = "seated"
  /\ UNCHANGED <<holder, halt, confirmedMajority, person, device, contact, contactParties, community, member, row, rowAuthor, consent, agent, steward, winding>>

LoseHolder(h) ==
  /\ Live /\ holder[h] = "seated"
  /\ holder' = [holder EXCEPT ![h] = "lost"]
  /\ UNCHANGED <<mesh, halt, confirmedMajority, canonical, person, device, contact, contactParties, community, member, row, rowAuthor, consent, agent, steward, winding>>

Remint(h) ==
  /\ Live /\ holder[h] = "lost" /\ Majority
  /\ holder' = [holder EXCEPT ![h] = "seated"]
  /\ UNCHANGED <<mesh, halt, confirmedMajority, canonical, person, device, contact, contactParties, community, member, row, rowAuthor, consent, agent, steward, winding>>

(* 2. The canonical gets an owner *)
CanonicalAnnounced ==
  /\ Live /\ canonical = "seated" /\ \E p \in Persons : Announced(p)
  /\ canonical' = "announced"
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, person, device, contact, contactParties, community, member, row, rowAuthor, consent, agent, steward, winding>>

CanonicalRetires ==
  /\ Live /\ canonical \in {"seated", "announced"}
  /\ canonical' = "retired"
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, person, device, contact, contactParties, community, member, row, rowAuthor, consent, agent, steward, winding>>

(* 3. A person arrives *)
PersonKeys(p) ==
  /\ Live /\ ~winding /\ person[p] = "absent"
  /\ person' = [person EXCEPT ![p] = "keyed"]
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, device, contact, contactParties, community, member, row, rowAuthor, consent, agent, steward, winding>>

DeviceClaims(d) ==
  /\ Live /\ ~winding /\ device[d] = "none" /\ person[Owner(d)] \in {"keyed", "announced"}
  /\ device' = [device EXCEPT ![d] = "claimed"]
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, contact, contactParties, community, member, row, rowAuthor, consent, agent, steward, winding>>

PersonAnnounces(p) ==
  /\ Live /\ person[p] = "keyed" /\ \E d \in DevicesOf(p) : device[d] = "claimed"
  /\ person' = [person EXCEPT ![p] = "announced"]
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, device, contact, contactParties, community, member, row, rowAuthor, consent, agent, steward, winding>>

DeviceReleases(d) ==
  /\ Live /\ device[d] = "claimed"
  /\ device' = [device EXCEPT ![d] = "released"]
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, contact, contactParties, community, member, row, rowAuthor, consent, agent, steward, winding>>

PersonGone(p) ==
  /\ Live /\ person[p] \in {"keyed", "announced"}
  /\ Loose = "gone_with_device" \/ \A d \in DevicesOf(p) : device[d] # "claimed"
  /\ member[p] \in {"none", "left"}
  /\ Loose = "gone_stewarding" \/ steward # p
  /\ NoContact(p)
  /\ person' = [person EXCEPT ![p] = "gone"]
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, device, contact, contactParties, community, member, row, rowAuthor, consent, agent, steward, winding>>

(* 4. Two people become contacts *)
ContactRequest(p, q) ==
  /\ Live /\ ~winding /\ p # q /\ Announced(p) /\ Announced(q) /\ contact = "none"
  /\ contact' = "requested" /\ contactParties' = {p, q}
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, community, member, row, rowAuthor, consent, agent, steward, winding>>

ContactAccept ==
  /\ Live /\ contact = "requested"
  /\ contact' = "contacts" /\ UNCHANGED contactParties
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, community, member, row, rowAuthor, consent, agent, steward, winding>>

ContactEnds ==
  /\ Live /\ contact # "none"
  /\ contact' = "none" /\ contactParties' = {}
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, community, member, row, rowAuthor, consent, agent, steward, winding>>

(* 5. A room is founded *)
Found(p) ==
  /\ Live /\ ~winding /\ Announced(p) /\ community = "none"
  /\ community' = "founded" /\ member' = [member EXCEPT ![p] = "member"]
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties, row, rowAuthor, consent, agent, steward, winding>>

Propose(p, q) ==
  /\ Live /\ ~winding /\ community = "founded" /\ member[p] = "member" /\ member[q] \in {"none", "left"}
  /\ Announced(q)
  /\ member' = [member EXCEPT ![q] = "proposed"]
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties, community, row, rowAuthor, consent, agent, steward, winding>>

Accept(q) ==
  /\ Live /\ member[q] = "proposed" /\ Members # {}
  /\ member' = [member EXCEPT ![q] = "member"]
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties, community, row, rowAuthor, consent, agent, steward, winding>>

Decline(q) ==
  /\ Live /\ member[q] = "proposed"
  /\ member' = [member EXCEPT ![q] = "none"]
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties, community, row, rowAuthor, consent, agent, steward, winding>>

Resign(q) ==
  /\ Live /\ member[q] = "member"
  /\ member' = [member EXCEPT ![q] = "left"]
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties, community, row, rowAuthor, consent, agent, steward, winding>>

Remove(q) ==
  /\ Live /\ member[q] = "member" /\ Cardinality(Members \ {q}) >= 1
  /\ member' = [member EXCEPT ![q] = "left"]
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties, community, row, rowAuthor, consent, agent, steward, winding>>

Dissolve ==
  /\ Live /\ community = "founded" /\ Members = {} /\ \A p \in Persons : member[p] # "proposed"
  /\ community' = "dissolved"
  /\ row' = [r \in Rows |-> IF row[r] = "absent" THEN "absent" ELSE "purged"] /\ rowAuthor' = [r \in Rows |-> "-"]
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties, member, consent, agent, steward, winding>>

(* 6. Members write *)
Write(r, p) ==
  /\ Live /\ ~winding /\ community = "founded" /\ member[p] = "member" /\ row[r] = "absent"
  /\ row' = [row EXCEPT ![r] = "admitted"] /\ rowAuthor' = [rowAuthor EXCEPT ![r] = p]
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties, community, member, consent, agent, steward, winding>>

Withdraw(r) ==
  /\ Live /\ row[r] = "admitted" /\ member[rowAuthor[r]] = "member"
  /\ row' = [row EXCEPT ![r] = "withdrawn"]
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties, community, member, rowAuthor, consent, agent, steward, winding>>

Purge(r) ==
  /\ Live /\ row[r] = "withdrawn"
  /\ row' = [row EXCEPT ![r] = "purged"] /\ rowAuthor' = [rowAuthor EXCEPT ![r] = "-"]
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties, community, member, consent, agent, steward, winding>>

(* 7. A person consents, and revokes *)
Grant(p) ==
  /\ Live /\ ~winding /\ Announced(p) /\ consent[p] = "none"
  /\ consent' = [consent EXCEPT ![p] = "granted"]
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties, community, member, row, rowAuthor, agent, steward, winding>>

Revoke(p) ==
  /\ Live /\ consent[p] = "granted"
  /\ consent' = [consent EXCEPT ![p] = "none"]
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties, community, member, row, rowAuthor, agent, steward, winding>>

(* 8. An agent is bonded *)
Bond(p) ==
  /\ Live /\ ~winding /\ Announced(p) /\ agent = "unbound"
  /\ agent' = "bonded" /\ steward' = p
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties, community, member, row, rowAuthor, consent, winding>>

HandOver(q) ==
  /\ Live /\ agent = "bonded" /\ Announced(q) /\ q # steward
  /\ steward' = q
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties, community, member, row, rowAuthor, consent, agent, winding>>

Freeze ==
  /\ Live /\ agent = "bonded"
  /\ agent' = "frozen"
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties, community, member, row, rowAuthor, consent, steward, winding>>

Retire ==
  /\ Live /\ agent = "frozen"
  /\ agent' = "retired" /\ steward' = "-"
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties, community, member, row, rowAuthor, consent, winding>>

(* 9. The holders halt *)
Latch(h) ==
  /\ Live /\ halt = "clear" /\ holder[h] = "seated"
  /\ halt' = "latched" /\ UNCHANGED confirmedMajority
  /\ UNCHANGED <<mesh, holder, canonical, person, device, contact, contactParties, community, member, row, rowAuthor, consent, agent, steward, winding>>

Lapse ==
  /\ Live /\ halt = "latched"
  /\ halt' = "clear" /\ UNCHANGED confirmedMajority
  /\ UNCHANGED <<mesh, holder, canonical, person, device, contact, contactParties, community, member, row, rowAuthor, consent, agent, steward, winding>>

Confirm(S) ==
  /\ Live /\ halt = "latched" /\ S \subseteq Seated /\ S # {}
  /\ Loose = "lone_halt" \/ Cardinality(S) * 2 > Cardinality(Holders)
  /\ halt' = "confirmed" /\ confirmedMajority' = (Cardinality(S) * 2 > Cardinality(Holders))
  /\ UNCHANGED <<mesh, holder, canonical, person, device, contact, contactParties, community, member, row, rowAuthor, consent, agent, steward, winding>>

Resume ==
  /\ Live /\ halt = "confirmed" /\ Majority
  /\ halt' = "clear" /\ confirmedMajority' = FALSE
  /\ UNCHANGED <<mesh, holder, canonical, person, device, contact, contactParties, community, member, row, rowAuthor, consent, agent, steward, winding>>

(* 10. The mesh winds down *)
WindDown ==
  /\ Live /\ ~winding /\ Majority
  /\ winding' = TRUE
  /\ UNCHANGED <<mesh, holder, halt, confirmedMajority, canonical, person, device, contact, contactParties, community, member, row, rowAuthor, consent, agent, steward>>

Empty ==
  /\ \A p \in Persons : person[p] \in {"absent", "gone"}
  /\ \A d \in Devices : device[d] # "claimed"
  /\ contact = "none"
  /\ community \in {"none", "dissolved"}
  /\ \A r \in Rows : row[r] \in {"absent", "purged"}
  /\ agent \in {"unbound", "retired"}
  /\ canonical \in {"none", "retired"}

End ==
  /\ Live /\ winding /\ Empty
  /\ mesh' = "ended"
  /\ UNCHANGED <<holder, halt, confirmedMajority, canonical, person, device, contact, contactParties, community, member, row, rowAuthor, consent, agent, steward, winding>>

WindSteps ==
  \/ CanonicalRetires \/ \E d \in Devices : DeviceReleases(d) \/ \E p \in Persons : PersonGone(p)
  \/ ContactEnds \/ \E q \in Persons : Decline(q) \/ Resign(q) \/ Dissolve
  \/ \E r \in Rows : Withdraw(r) \/ Purge(r) \/ Freeze \/ Retire \/ End

Next ==
  \/ Mint \/ \E h \in Holders : LoseHolder(h) \/ Remint(h) \/ Latch(h)
  \/ CanonicalAnnounced \/ CanonicalRetires
  \/ \E p \in Persons : PersonKeys(p) \/ PersonAnnounces(p) \/ PersonGone(p) \/ Found(p)
                        \/ Grant(p) \/ Revoke(p) \/ Bond(p) \/ HandOver(p)
                        \/ Accept(p) \/ Decline(p) \/ Resign(p) \/ Remove(p)
  \/ \E d \in Devices : DeviceClaims(d) \/ DeviceReleases(d)
  \/ \E p, q \in Persons : ContactRequest(p, q) \/ Propose(p, q)
  \/ ContactAccept \/ ContactEnds
  \/ Dissolve \/ \E r \in Rows : Purge(r) \/ Withdraw(r) \/ \E p \in Persons : Write(r, p)
  \/ Freeze \/ Retire \/ Lapse \/ Resume \/ \E S \in SUBSET Holders : Confirm(S)
  \/ WindDown \/ End

Fairness ==
  /\ WF_vars(CanonicalRetires) /\ WF_vars(ContactEnds) /\ WF_vars(Dissolve)
  /\ WF_vars(Freeze) /\ WF_vars(Retire) /\ WF_vars(End)
  /\ \A d \in Devices : WF_vars(DeviceReleases(d))
  /\ \A p \in Persons : WF_vars(PersonGone(p)) /\ WF_vars(Decline(p)) /\ WF_vars(Resign(p))
  /\ \A r \in Rows : WF_vars(Withdraw(r)) /\ WF_vars(Purge(r))

Spec == Init /\ [][Next]_vars /\ Fairness

Symm == Permutations(Holders) \cup Permutations(Persons) \cup Permutations(Rows)

(* The closure facts *)
Inv_NothingBeforeMint == mesh = "unminted" => (canonical = "none" /\ \A p \in Persons : person[p] = "absent")
Inv_DeviceHasOwner == \A d \in Devices : device[d] = "claimed" => person[Owner(d)] \in {"keyed", "announced"}
Inv_MemberIsAnnounced == \A p \in Persons : member[p] \in {"member", "proposed"} => Announced(p)
Inv_RowInFoundedRoom == \A r \in Rows : row[r] \in {"admitted", "withdrawn"} => (community = "founded" /\ rowAuthor[r] \in Persons)
Inv_AgentHasSteward == agent \in {"bonded", "frozen"} => (steward \in Persons /\ Announced(steward))
Inv_HaltIsMajority == halt = "confirmed" => confirmedMajority
Inv_EndedIsEmpty == mesh = "ended" => Empty
Inv_ContactIsAnnounced == \A p \in contactParties : Announced(p)

(* Progress, as checked facts: while winding no step raises the rank, every wind-down step lowers it,
   and while winding and not empty some wind-down step is enabled. With weak fairness of the wind-down
   steps these three give Live_WindsDownToEnd; the small bound checks that property directly. *)
W(x, a, b) == IF x = a THEN 2 ELSE IF x = b THEN 1 ELSE 0
Rank ==
  (IF mesh = "live" THEN 1 ELSE 0)
  + Cardinality({p \in Persons : person[p] \in {"keyed", "announced"}})
  + Cardinality({d \in Devices : device[d] = "claimed"})
  + (IF contact = "none" THEN 0 ELSE 1)
  + (IF community = "founded" THEN 1 ELSE 0)
  + Cardinality({p \in Persons : member[p] \in {"proposed", "member"}})
  + W(agent, "bonded", "frozen")
  + (IF canonical \in {"seated", "announced"} THEN 1 ELSE 0)
  + Cardinality({r \in Rows : row[r] = "admitted"}) * 2 + Cardinality({r \in Rows : row[r] = "withdrawn"})

WindStepEnabled ==
  \/ canonical \in {"seated", "announced"}
  \/ \E d \in Devices : device[d] = "claimed"
  \/ contact # "none"
  \/ \E p \in Persons : member[p] \in {"proposed", "member"}
  \/ community = "founded" /\ Members = {} /\ \A p \in Persons : member[p] # "proposed"
  \/ \E r \in Rows : row[r] = "withdrawn" \/ (row[r] = "admitted" /\ member[rowAuthor[r]] = "member")
  \/ agent \in {"bonded", "frozen"}
  \/ \E p \in Persons : person[p] \in {"keyed", "announced"} /\ device[p] # "claimed"
       /\ member[p] \in {"none", "left"} /\ steward # p /\ NoContact(p)
  \/ Empty

Inv_WindAlwaysCanStep == (Live /\ winding) => WindStepEnabled
Act_WindNeverRaisesRank == [][winding => Rank' <= Rank]_vars
Act_WindStepLowersRank == [][(winding /\ WindSteps) => Rank' < Rank]_vars

Live_WindsDownToEnd == (winding) ~> (mesh = "ended")
=============================================================================
