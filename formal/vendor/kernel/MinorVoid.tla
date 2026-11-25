------------------------------ MODULE MinorVoid ------------------------------
(* The void of a duty appointment made to a minor (CC 3.2 at v1.0-rc21, Constitution commit b016df4, the
   user-target admission rule: "A duty-scoped delegates_to D onto T is void when both of the following hold:
   1. a minor-band age row about T is held, assured or age_self_declared, live or retracted; 2. no assured
   adult age row about T (the age_assurance:* rung) is dated before D's asserted_at." As ruled on 2026-11-20
   (Eric's decision), clause 2 reads "no UN-RETRACTED assured adult age row": a retracted adult proof proves
   nothing, so its retraction voids an appointment already seated, the one case where a retraction reaches
   back. The same paragraph:
   "The rule is a fold over the held rows, so every node reaches the same answer in any order of arrival.
   Backdating D can only void it, a retracted minor row still counts, and a self-declared adult lifts
   nothing." The reason is minor_appointment_void, CC 2.7.3).
   One target T. Its age rows: T's own age_self_declared minor at 1 and adult at 2 (the adult replaces the
   minor in T's own series), and for each witness w in 1..W an age_assurance minor at w (expiring at w + 1)
   and an age_assurance adult at w + 1 (expiring at w + 3), the adult replacing the minor in w's series. The
   retractions: of every minor row, and of witness 1's adult row.
   The duty edge D is offered dated at each instant 1..N: one row per date, the same appointment backdated
   or not. Rows arrive in ANY order, and the node's clock ticks between arrivals.
   The node keeps its verdict INCREMENTALLY, as a store does: a running "a minor row was seen" and the set of
   assured adult proofs (date, expiry) it has seen, and on every arrival it re-folds every held D (persist
   declares the fold read key:<T>, so a row about T re-folds the edge). Checked: the stored verdict is the
   set function of the held rows; a node that held the same rows and folded them at any other instant
   concludes the same; a D dated earlier is void whenever a later-dated one is; a retraction changes no
   verdict; a self-declared adult lifts nothing; a minor row superseded by its signer's newer adult row
   still voids; a later adult proof never revives a void D.
   EXPIRY = TRUE adds the reading "and unexpired at D's asserted_at" to clause 2 (persist's K2-fix14); the
   rc21 text has no such clause, and with it Inv_BackdateOnlyVoids fails (MinorVoid_expiry.cfg).
   RETRACTED_ADULT_LIFTS = FALSE is the ruled reading, the one check.sh runs: a retracted adult proof is no
   proof, and only retractions of minor rows are irrelevant. TRUE, the earlier reading (a held proof lifts the
   void whether or not its witness withdrew it), is now a second plant that TLC must catch
   (MinorVoid_plant_retracted_adult_lifts.cfg). A retraction may arrive before the row it names.
   MUT = TRUE plants the break of persist's K2-fix11: the adult proof is judged unexpired at the node's own
   clock, now, instead of at D's asserted_at. *)
EXTENDS Naturals, FiniteSets
CONSTANTS MUT, EXPIRY, RETRACTED_ADULT_LIFTS, W, N
TMax == N + 2
Times == 0..TMax
\* a row: k is "self" | "assured" | "retract" | "D"; s the signer (0 is T itself); at its asserted_at;
\* exp its expires_at (0: none); id its digest; tgt the id a retraction names (0: none)
Row(k, b, s, at, exp, id, tgt) == [k |-> k, band |-> b, s |-> s, at |-> at, exp |-> exp, id |-> id, tgt |-> tgt]
SelfRows == {Row("self", "minor", 0, 1, 0, 1, 0), Row("self", "adult", 0, 2, 0, 2, 0)}
WitRows == {Row("assured", "minor", w, w, w + 1, 2 * w + 1, 0) : w \in 1..W}
             \cup {Row("assured", "adult", w, w + 1, w + 3, 2 * w + 2, 0) : w \in 1..W}
AgeRows == SelfRows \cup WitRows
IsMinor(r) == r \in AgeRows /\ r.band = "minor"
RetractRows == {Row("retract", "-", 0, 3, 0, 100 + m.id, m.id) : m \in {r \in AgeRows : IsMinor(r) \/ r.id = 4}}
DRows == {Row("D", "-", 9, t, 0, 200 + t, 0) : t \in 1..N}
Rows == AgeRows \cup RetractRows \cup DRows
SelfAdultRows == {r \in SelfRows : r.band = "adult"}
Unexpired(exp, t) == exp = 0 \/ exp > t

\* The rule, read from the held set H (CC 3.2 clauses 1 and 2)
Retracted(H, r) == \E x \in H : x.k = "retract" /\ x.tgt = r.id
\* the assured adult rows of H that can stand as a proof
Proofs(H) == {r \in H : r.k = "assured" /\ r.band = "adult" /\ (RETRACTED_ADULT_LIFTS \/ ~Retracted(H, r))}
ProofAt(H, t) == \E r \in Proofs(H) : r.at < t /\ (EXPIRY => Unexpired(r.exp, t))
Void(H, d) == (\E r \in H : IsMinor(r)) /\ ~ProofAt(H, d.at)

\* The node's judgement over its running summary, at its clock t
Counts(p, d, t) == p[1] < d.at /\ (IF MUT THEN Unexpired(p[2], t) ELSE (EXPIRY => Unexpired(p[2], d.at)))
Judge(minor, proofs, d, t) == minor /\ ~\E p \in proofs : Counts(p, d, t)
\* another node holding H that folds it all at its instant t
JudgeAll(H, d, t) == Judge(\E r \in H : IsMinor(r),
                           {<<r.at, r.exp, r.id>> : r \in Proofs(H)}, d, t)

VARIABLES held, minorSeen, proofs, retired, void, now
vars == <<held, minorSeen, proofs, retired, void, now>>

Init == held = {} /\ minorSeen = FALSE /\ proofs = {} /\ retired = {} /\ void = [d \in DRows |-> FALSE] /\ now = 0

Offer(r) == /\ r \notin held
            /\ held' = held \cup {r}
            /\ minorSeen' = (minorSeen \/ IsMinor(r))
            /\ retired' = IF r.k = "retract" THEN retired \cup {r.tgt} ELSE retired
            /\ proofs' = {p \in proofs \cup (IF r.k = "assured" /\ r.band = "adult" THEN {<<r.at, r.exp, r.id>>} ELSE {}) :
                           RETRACTED_ADULT_LIFTS \/ p[3] \notin retired'}
            /\ void' = [d \in DRows |-> d \in held' /\ Judge(minorSeen', proofs', d, now)]
            /\ UNCHANGED now
Tick == now < TMax /\ now' = now + 1 /\ UNCHANGED <<held, minorSeen, proofs, retired, void>>
Done == held = Rows /\ now = TMax /\ UNCHANGED vars
Next == (\E r \in Rows : Offer(r)) \/ Tick \/ Done
Spec == Init /\ [][Next]_vars

HeldD == held \cap DRows
\* V1 two nodes holding the same rows at different instants conclude the same: this node's verdict is what a
\* node folding the same held set at any instant t concludes
Inv_NodesAgree == \A d \in HeldD, t \in Times : void[d] = JudgeAll(held, d, t)
\* V2 order-independence: the verdict kept incrementally, in every arrival order, is the set function
Inv_Fold == \A d \in HeldD : void[d] = Void(held, d)
\* V3 backdating D can only void it, never lift a void
Inv_BackdateOnlyVoids == \A d1, d2 \in HeldD : d1.at < d2.at /\ void[d2] => void[d1]
\* V4 a retracted minor row still counts: no retraction (under the variant, no retraction of a minor row)
\* changes any verdict, and a minor row whose retraction is held voids D when no assured adult proof precedes it
Irrelevant == IF RETRACTED_ADULT_LIFTS THEN RetractRows
              ELSE {x \in RetractRows : \E m \in AgeRows : IsMinor(m) /\ m.id = x.tgt}
Inv_RetractionChangesNothing == \A d \in HeldD : void[d] = JudgeAll(held \ Irrelevant, d, now)
Inv_RetractedMinorCounts == \A d \in HeldD : \A m \in held :
                              (IsMinor(m) /\ \E x \in held : x.tgt = m.id /\ ~ProofAt(held, d.at)) => void[d]
\* V5 a self-declared adult row never lifts the void
Inv_SelfAdultLiftsNothing == \A d \in HeldD : JudgeAll(held \ SelfAdultRows, d, now) => void[d]
\* V6 a minor row superseded by its own signer's newer adult row still voids (the current reading is
\* newest-per-signer; the void reads every minor row ever held)
Inv_SupersededMinorStillVoids ==
  \A d \in HeldD : \A m \in held :
    (IsMinor(m) /\ (\E a \in held : a \in AgeRows /\ a.s = m.s /\ a.band = "adult" /\ a.at > m.at)
       /\ ~ProofAt(held, d.at)) => void[d]
\* V8 (the ruling) a retracted assured adult proof does not lift the void: with a minor row held and no
\* un-retracted proof before D, D is void even when a retracted proof dated before it is held
LiveProofAt(H, t) == \E r \in H : r.k = "assured" /\ r.band = "adult" /\ r.at < t /\ ~Retracted(H, r)
                                  /\ (EXPIRY => Unexpired(r.exp, t))
Inv_RetractedProofLiftsNothing == \A d \in HeldD : ((\E m \in held : IsMinor(m)) /\ ~LiveProofAt(held, d.at)) => void[d]
\* V9 the retraction of the adult proof arriving after D was seated voids D
Prop_LateRetractionVoids ==
  [][\A d \in HeldD : (~void[d] /\ (\E x \in (held' \ held) \cap RetractRows : \E a \in held : a.id = x.tgt /\ a.k = "assured")
                          /\ (\E m \in held' : IsMinor(m)) /\ ~LiveProofAt(held', d.at)) => void'[d]]_vars
\* V7 a later adult proof (dated at or after D) never revives a void D
Prop_LaterProofNoRevive ==
  [][\A d \in HeldD : (void[d] /\ \A r \in held' \ held : r.k = "assured" /\ r.band = "adult" /\ r.at >= d.at)
                        => void'[d]]_vars
==========================================================================
