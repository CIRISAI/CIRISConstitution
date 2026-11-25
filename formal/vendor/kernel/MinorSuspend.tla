----------------------------- MODULE MinorSuspend -----------------------------
(* The current age band about T at an act's own instant, which decides whether T's duty seat counts for
   the act X or is held suspended ("seated but not counted while the band reads minor"). Companion of
   MinorVoid.tla (the void is a property of the appointment's history) and StandingProtection.tla (the same
   band function, read on the rows held now). The band function below is the one both specs use.
   Source: CC 3.4.11 at v1.0-rc21 (Constitution commit b016df4), "Read-union - witness outranks subject",
   CC 3.4.13's fail-secure rule, CC 3.5.1 rules 2 and 3, and CC 2.4.1.1, as the Constitution ruled them on
   2026-11-20 (Eric's ruling on age rows):
   - no expiry: an age row stands until its own signer supersedes or retracts it, or a row that outranks it
     lands; expires_at never changes the band, and no clock is read for it;
   - per signer the newest row stands, at one instant the lowest id (CC 3.5.1 rules 2 and 3); in a reading
     at an act's instant t only rows dated <= t count, and a retraction counts only if dated <= t;
   - the subject's own younger self-declaration lowers the band whenever it is made; a self-declared adult
     raises nothing;
   - a higher assurance level outranks a lower one, whatever the dates;
   - the bands are a ladder, under_13 < 13_15 < 16_17 < adult, and minor is the coarse reading of the first
     three; between assured rows at the same level, the row with the later asserted_at stands, and at the
     same instant the younger band stands (one comparison, as the Constitution accepted it; a later older band
     lifting an earlier younger one and a later younger band winning are both "the later row stands").
   A person with no current row reads none and is not suspended.
   Rows: T's self-declared 13_15 at 1 and adult at 3; witness 1 (provider) under_13 at 1, and adult (id 12)
   and 16_17 (id 13) both at 4, a same-signer tie the lower id wins; witness 2 (provider) adult at 1 and at 2;
   and with W = 3, witness 3 (government) 16_17 at 5 and adult at 6. The ladder's own cases (each adjacent band
   step in both date orders and at one instant, and the 15-then-19 case) are checked as a table,
   Inv_Ladder*. Retractions: of T's minor, dated 2; of witness
   2's adult at 2, dated 3; with W = 3, of witness 3's minor, dated 6. An act X is offered dated at each instant
   1..N. Rows arrive in ANY order, a retraction possibly BEFORE the row it names, and the node's clock ticks.
   The node keeps each signer's rows and the retractions it has seen (target, date) INCREMENTALLY and
   re-reads every held X on each arrival.
   MUT = TRUE plants the break: the read is judged at the reader's clock, now, instead of X's asserted_at
   (which rows and retractions it counts). EQ_PLANT = TRUE plants the earlier equal-level rule, "at an equal
   level the younger band wins whatever the dates" (MinorSuspend_plant_equal_level_minor_wins.cfg). *)
EXTENDS Naturals, FiniteSets
CONSTANTS MUT, EQ_PLANT, W, N
TMax == N + 1
Times == 0..TMax
Signers == 0..W                                   \* 0 is T itself (the self rung)
Witnesses == 1..W
Level(s) == IF s = 3 THEN 2 ELSE 1                \* witness 3 is government, the others provider
\* the band ladder; minor is the coarse reading of the first three
Bands == <<"under_13", "13_15", "16_17", "adult">>
Rank(b) == CASE b = "under_13" -> 0 [] b = "13_15" -> 1 [] b = "16_17" -> 2 [] OTHER -> 3
MinorBands == {"under_13", "13_15", "16_17"}
Coarse(b) == IF b \in MinorBands THEN "minor" ELSE b
Youngest(S) == CHOOSE b \in S : \A c \in S : Rank(b) <= Rank(c)
Row(k, b, s, at, id, tgt) == [k |-> k, band |-> b, s |-> s, at |-> at, id |-> id, tgt |-> tgt]
AgeRows == {Row("self", "13_15", 0, 1, 1, 0), Row("self", "adult", 0, 3, 2, 0),
            Row("assured", "under_13", 1, 1, 11, 0), Row("assured", "adult", 1, 4, 12, 0), Row("assured", "16_17", 1, 4, 13, 0),
            Row("assured", "adult", 2, 1, 21, 0), Row("assured", "adult", 2, 2, 22, 0)}
           \cup (IF W >= 3 THEN {Row("assured", "16_17", 3, 5, 31, 0), Row("assured", "adult", 3, 6, 32, 0)} ELSE {})
RetDate(id) == CASE id = 1 -> 2 [] id = 22 -> 3 [] OTHER -> 6
RetractRows == {Row("retract", "-", 9, RetDate(r.id), 100 + r.id, r.id) : r \in {q \in AgeRows : q.id \in {1, 22, 31}}}
XRows == {Row("X", "-", 9, t, 200 + t, 0) : t \in 1..N}
Rows == AgeRows \cup RetractRows \cup XRows
IsMinor(r) == r \in AgeRows /\ r.band \in MinorBands

\* ---- the band function (shared with StandingProtection.tla) ----
\* rows: [Signers -> set of that signer's age rows]; rets: set of <<target id, retraction's asserted_at>>
Forever == 1000                                   \* a standing reading counts every held row and retraction
Counted(rets, r, t) == r.at <= t /\ ~\E p \in rets : p[1] = r.id /\ p[2] <= t
Max(S) == CHOOSE a \in S : \A b \in S : b <= a
Min(S) == CHOOSE a \in S : \A b \in S : a <= b
\* the signer's current row at t, as a set of at most one row: its newest counted row, the lowest id at a tie
CurrentAt(S, rets, t) ==
  LET C == {r \in S : Counted(rets, r, t)}
  IN IF C = {} THEN {}
     ELSE LET m == Max({r.at : r \in C})
          IN {CHOOSE r \in C : r.at = m /\ r.id = Min({q.id : q \in {q2 \in C : q2.at = m}})}
SignerBandAt(S, rets, t) == LET cur == CurrentAt(S, rets, t) IN IF cur = {} THEN "none" ELSE (CHOOSE r \in cur : TRUE).band
\* the current rows of the witnesses at the highest level that has one
TopRows(rows, rets, t) ==
  LET present == {w \in Witnesses : CurrentAt(rows[w], rets, t) # {}}
      top == IF present = {} THEN 0 ELSE Max({Level(w) : w \in present})
  IN UNION {CurrentAt(rows[w], rets, t) : w \in {v \in present : Level(v) = top}}
\* among them one comparison: the row with the later asserted_at stands; at the same instant, the younger band
\* stands. A row stands when it is at least as late as every other and, at its instant, no younger.
StandsOver(r, q) == q.at < r.at \/ (q.at = r.at /\ Rank(r.band) <= Rank(q.band))
LadderBand(tr) ==
  IF tr = {} THEN "none"
  ELSE IF EQ_PLANT THEN Youngest({r.band : r \in tr})
  ELSE (CHOOSE r \in tr : \A q \in tr : StandsOver(r, q)).band
WitnessBandAt(rows, rets, t) == LadderBand(TopRows(rows, rets, t))
\* across the rungs: the subject's current minor band lowers the witnesses' reading and never raises it
BandAt(rows, rets, t) ==
  LET sb == SignerBandAt(rows[0], rets, t)
      wb == WitnessBandAt(rows, rets, t)
  IN IF sb \in MinorBands /\ (wb = "none" \/ Rank(sb) < Rank(wb)) THEN sb ELSE wb
CoarseBandAt(rows, rets, t) == Coarse(BandAt(rows, rets, t))
\* ---- end of the band function ----

\* The set function, read straight from the held set H
RowsOf(H) == [s \in Signers |-> {r \in H \cap AgeRows : r.s = s}]
RetsOf(H) == {<<x.tgt, x.at>> : x \in H \cap RetractRows}
Suspended(H, t) == CoarseBandAt(RowsOf(H), RetsOf(H), t) = "minor"
SB(H, s, t) == SignerBandAt(RowsOf(H)[s], RetsOf(H), t)
Top(H, t) == TopRows(RowsOf(H), RetsOf(H), t)
\* The void of a duty appointment dated t (MinorVoid.tla, as ruled): any minor row ever held, and no
\* un-retracted assured adult proof dated before t
Retracted(H, r) == \E x \in H \cap RetractRows : x.tgt = r.id
VoidAt(H, t) == (\E r \in H : IsMinor(r)) /\
                ~\E r \in H \cap AgeRows : r.k = "assured" /\ r.band = "adult" /\ r.at < t /\ ~Retracted(H, r)

VARIABLES held, rows, rets, susp, now
vars == <<held, rows, rets, susp, now>>

\* the node's reading of X over what it kept, at its clock c
Judge(rs, rt, x, c) == CoarseBandAt(rs, rt, IF MUT THEN c ELSE x.at) = "minor"

Init == /\ held = {} /\ rows = [s \in Signers |-> {}] /\ rets = {}
        /\ susp = [x \in XRows |-> FALSE] /\ now = 0

Offer(r) == /\ r \notin held
            /\ held' = held \cup {r}
            /\ rows' = [s \in Signers |-> IF r \in AgeRows /\ r.s = s THEN rows[s] \cup {r} ELSE rows[s]]
            /\ rets' = IF r.k = "retract" THEN rets \cup {<<r.tgt, r.at>>} ELSE rets
            /\ susp' = [x \in XRows |-> x \in held' /\ Judge(rows', rets', x, now)]
            /\ UNCHANGED now
Tick == now < TMax /\ now' = now + 1 /\ UNCHANGED <<held, rows, rets, susp>>
Done == held = Rows /\ now = TMax /\ UNCHANGED vars
Next == (\E r \in Rows : Offer(r)) \/ Tick \/ Done
Spec == Init /\ [][Next]_vars

HeldX == held \cap XRows
\* S1 node agreement: a node holding the same rows and reading at any reader clock c concludes the same
Inv_NodesAgree == \A x \in HeldX, c \in Times : susp[x] = Judge(RowsOf(held), RetsOf(held), x, c)
\* S2 order-independence: what the node kept as rows arrived, in every order, a retraction before its row
\* included, is what the held set says, and the kept reading is the set function at X's asserted_at
Inv_StoreFold == rows = RowsOf(held) /\ rets = RetsOf(held)
Inv_Fold == \A x \in HeldX : susp[x] = Suspended(held, x.at)
\* S3 a row or a retraction dated after t is not yet anyone's word at t (a withdrawal reaches forward only)
Inv_LaterRowsNotYet == \A x \in HeldX : susp[x] = Suspended({r \in held : r.at <= x.at}, x.at)
\* S4 a retraction counted at t takes its row out: dropping both changes nothing at t
Inv_RetractedOut == \A x \in HeldX : \A q \in held \cap RetractRows :
                      q.at <= x.at => susp[x] = Suspended({r \in held : r.id # q.tgt /\ r # q}, x.at)
\* S5 per signer the newest row stands: dropping a signer's older row changes nothing when a newer row of the
\* same signer is counted at t (a minor graduates by a newer adult row from the same signer)
Inv_NewestStands == \A x \in HeldX : \A r1, r2 \in held \cap AgeRows :
                      (r1.s = r2.s /\ r1.at < r2.at /\ Counted(RetsOf(held), r2, x.at))
                        => susp[x] = Suspended(held \ {r1}, x.at)
\* S6 at one instant the lowest id stands (CC 3.5.1 rule 3): dropping the higher id changes nothing
Inv_TieLowestIdWins == \A x \in HeldX : \A r1, r2 \in held \cap AgeRows :
                         (r1.s = r2.s /\ r1.at = r2.at /\ r1.id < r2.id /\ Counted(RetsOf(held), r1, x.at))
                           => susp[x] = Suspended(held \ {r2}, x.at)
\* S7 graduation does not touch the void: a minor row whose signer's current row at t is a newer adult row
\* still voids a duty appointment dated t that no un-retracted assured adult proof precedes
Inv_GraduationLeavesVoid ==
  \A x \in HeldX : \A m \in held :
    (IsMinor(m) /\ SB(held, m.s, x.at) = "adult"
       /\ ~\E r \in held \cap AgeRows : r.k = "assured" /\ r.band = "adult" /\ r.at < x.at /\ ~Retracted(held, r))
      => VoidAt(held, x.at)
\* S8 the subject's minor lowers and never raises: whenever the witnesses alone read minor, or the subject's
\* current row is minor, T reads minor; a self-declared adult alone reads no band
Inv_SelfNeverRaises == \A x \in HeldX : (Coarse(WitnessBandAt(RowsOf(held), RetsOf(held), x.at)) = "minor"
                                           \/ Coarse(SB(held, 0, x.at)) = "minor") => susp[x]
Inv_SelfAdultAloneIsNone == \A t \in 1..N :
                              BandAt([s \in Signers |-> IF s = 0 THEN RowsOf(held)[0] ELSE {}], RetsOf(held), t) # "adult"
\* S9 a higher level outranks a lower one, whatever the dates: with the subject not minor, dropping every row
\* of a witness whose level is below a witness with a current row changes nothing
Inv_HigherLevelOutranks ==
  \A x \in HeldX : \A w, v \in Witnesses :
    (Level(w) < Level(v) /\ SB(held, v, x.at) # "none" /\ Coarse(SB(held, 0, x.at)) # "minor")
      => susp[x] = Suspended({r \in held : ~(r \in AgeRows /\ r.s = w)}, x.at)
\* S10 at the top level date order decides. A later assured adult lifts: with the subject not minor, a top
\* current adult row dated after every top current minor row leaves T not suspended
Inv_LaterAssuredAdultLifts ==
  \A x \in HeldX : (Coarse(SB(held, 0, x.at)) # "minor" /\ \E a \in Top(held, x.at) :
                      a.band = "adult" /\ \A m \in Top(held, x.at) : m.band \in MinorBands => m.at < a.at) => ~susp[x]
\* S11 a contradiction goes to minor: a top current minor row dated at or after every top current adult row
\* suspends
Inv_ContradictionMinorWins ==
  \A x \in HeldX : (\E m \in Top(held, x.at) : m.band \in MinorBands /\ \A a \in Top(held, x.at) : a.band = "adult" => a.at <= m.at)
                     => susp[x]
\* S12 the explicit case: two top current rows of different signers at one instant, one minor and one adult,
\* and no top adult row later: minor wins
Inv_SameInstantMinorWins ==
  \A x \in HeldX : (\E m, a \in Top(held, x.at) : m.band \in MinorBands /\ a.band = "adult" /\ m.s # a.s /\ m.at = a.at
                       /\ \A b \in Top(held, x.at) : b.band = "adult" => b.at <= m.at) => susp[x]
\* S13 a suspension needs a minor row held (the void's clause 1); a person with no age row is never suspended
Inv_SuspendedNeedsMinorRow == \A x \in HeldX : susp[x] => \E r \in held : IsMinor(r)
\* S14 the ladder, as a table over two providers at one level (witnesses 1 and 2) and no subject row: for each
\* adjacent band step (younger y, older o) a later o lifts y, a later y wins, and at one instant y wins; the
\* 15-then-19 case (13_15 at 15 by one provider, adult at 19 by another) reads adult; the coarse reading of
\* each is minor exactly when the band is below adult. The table is constant, so it is read at the initial
\* state only (AtStart), once per run
AtStart == held = {} /\ now = 0
Steps == {<<"under_13", "13_15">>, <<"13_15", "16_17">>, <<"16_17", "adult">>}
Pair(b1, t1, b2, t2) == [s \in Signers |-> IF s = 1 THEN {Row("assured", b1, 1, t1, 901, 0)}
                                         ELSE IF s = 2 THEN {Row("assured", b2, 2, t2, 902, 0)} ELSE {}]
PairBand(b1, t1, b2, t2) == BandAt(Pair(b1, t1, b2, t2), {}, Forever)
Inv_LadderLaterOlderLifts == AtStart => \A st \in Steps : PairBand(st[1], 1, st[2], 2) = st[2]
Inv_LadderLaterYoungerWins == AtStart => \A st \in Steps : PairBand(st[2], 1, st[1], 2) = st[1]
Inv_LadderSameInstantYoungerWins == AtStart => \A st \in Steps : PairBand(st[1], 1, st[2], 1) = st[1] /\ PairBand(st[2], 1, st[1], 1) = st[1]
Inv_Ladder15Then19 == AtStart => PairBand("13_15", 15, "adult", 19) = "adult" /\ Coarse(PairBand("13_15", 15, "adult", 19)) = "adult"
\* the one comparison, as consequences: between two rows at one level the later stands whatever their bands,
\* and at one instant the younger stands
Inv_LaterAssuredStands == AtStart => \A b1, b2 \in {"under_13", "13_15", "16_17", "adult"} :
                            PairBand(b1, 1, b2, 2) = b2 /\ PairBand(b2, 1, b1, 2) = b1
Inv_SameInstantYoungerStands == AtStart => \A b1, b2 \in {"under_13", "13_15", "16_17", "adult"} :
                                  PairBand(b1, 1, b2, 1) = IF Rank(b1) <= Rank(b2) THEN b1 ELSE b2
Inv_LadderCoarse == AtStart => \A st \in Steps : \A o \in {<<1, 2>>, <<2, 1>>, <<1, 1>>} :
                      (Coarse(PairBand(st[1], o[1], st[2], o[2])) = "minor") = (PairBand(st[1], o[1], st[2], o[2]) \in MinorBands)
==========================================================================
