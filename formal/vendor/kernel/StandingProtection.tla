-------------------------- MODULE StandingProtection --------------------------
(* The standing protections keyed to a minor band, read on the person's CURRENT band from the rows held NOW,
   with MinorSuspend.tla's band function (BandAt at t = Forever: every held row and every held retraction
   counts). As the Constitution ruled them on 2026-11-20 (Eric's rulings), against v1.0-rc21 (commit b016df4):
   - CC 5.4.6 (part 5 line 1081: "the promotion concludes nothing while that row stands"; rc22 is to read
     "while that person's band reads minor"): a federation-scope owner-binding B concludes nothing while the
     band reads minor. A minor row its own signer has superseded no longer stands; one outranked by a higher
     level no longer decides; a later assured adult at the same level lifts an earlier minor; the subject's
     minor and a contradiction (a minor at or after the latest adult at the top level) still block; a
     withdrawal restores.
   - CC 3.2 line 961 ("A binding whose owner a row on record places in a minor band counts for nothing"):
     K's owner-binding counts for nothing at EVERY scope while the band reads minor and counts again when it
     reads adult; no carve-out by scope.
   - CC 3.2, the guardianship rule: a guardianship is a standing relation on the current band; it ends when
     the band reads adult, which needs an assured row, since a self-declaration never raises.
   No expiry: an age row stands until its own signer supersedes or retracts it, or a row that outranks it
   lands; expires_at changes nothing, and no node clock is read. So nodes holding the same rows agree.
   Bands are MinorSuspend's ladder (under_13 < 13_15 < 16_17 < adult); every relation here reads the coarse
   band, minor for the first three.
   Rows about one person K: the owner-binding B at federation scope; witness 1 (provider) 13_15 at 15;
   witness 2 (provider) adult at 15 and at 19; witness 3 (government) adult at 4; K's own self-declared minor
   at 5 (under_13), retracted at 6; and with LARGE, witness 1's adult at 20, K's self-declared adult at 21, and the
   retraction of witness 3's adult at 22. K's self-scope owner-binding and a guardian's steward-binding over K
   are held throughout. Two nodes each take the rows in ANY order, a retraction possibly before its row, keep a
   running summary (each signer's rows, the retractions seen), and re-read all three relations on every
   arrival.
   MUT = TRUE plants the break: the announcement is judged once, when the binding arrives, and never read
   again. EQ_PLANT = TRUE plants the earlier equal-level rule, "at an equal level minor wins whatever the
   dates" (StandingProtection_plant_equal_level_minor_wins.cfg): the 13_15 at 15 by one provider then the
   adult at 19 by another must read adult. *)
EXTENDS Naturals, FiniteSets
CONSTANTS MUT, EQ_PLANT, LARGE
Nodes == {1, 2}
MS == INSTANCE MinorSuspend WITH MUT <- FALSE, EQ_PLANT <- EQ_PLANT, W <- 3, N <- 1, held <- {}, rows <- <<>>,
                                rets <- {}, susp <- <<>>, now <- 0
Signers == MS!Signers
Row(k, b, s, at, id, tgt) == MS!Row(k, b, s, at, id, tgt)
Bind == Row("binding", "-", 9, 2, 500, 0)
AgeRows == {Row("assured", "13_15", 1, 15, 11, 0), Row("assured", "adult", 2, 15, 21, 0),
            Row("assured", "adult", 2, 19, 22, 0), Row("assured", "adult", 3, 4, 32, 0),
            Row("self", "under_13", 0, 5, 1, 0)}
           \cup (IF LARGE THEN {Row("assured", "adult", 1, 20, 12, 0), Row("self", "adult", 0, 21, 2, 0)} ELSE {})
RetractRows == {Row("retract", "-", 9, 6, 101, 1)} \cup (IF LARGE THEN {Row("retract", "-", 9, 22, 132, 32)} ELSE {})
Rows == {Bind} \cup AgeRows \cup RetractRows
IsMinor(r) == r \in AgeRows /\ r.band \in MS!MinorBands

\* the set function: the person's current band from the rows held now
RowsOf(H) == [s \in Signers |-> {r \in H \cap AgeRows : r.s = s}]
RetsOf(H) == {<<x.tgt, x.at>> : x \in H \cap RetractRows}
\* the coarse reading (minor for any band below adult) of the ladder band
HeldBand(H) == MS!CoarseBandAt(RowsOf(H), RetsOf(H), MS!Forever)
SB(H, s) == MS!Coarse(MS!SignerBandAt(RowsOf(H)[s], RetsOf(H), MS!Forever))
Top(H) == MS!TopRows(RowsOf(H), RetsOf(H), MS!Forever)
Announced(H) == Bind \in H /\ HeldBand(H) # "minor"
\* the self-scope owner-binding counts while the band does not read minor; the guardianship stands while it
\* does not read adult
OwnerCounts(H) == HeldBand(H) # "minor"
GuardLive(H) == HeldBand(H) # "adult"
Retracted(H, r) == \E x \in H \cap RetractRows : x.tgt = r.id
\* the void (MinorVoid.tla, as ruled) of a duty appointment dated t: any minor row ever held counts,
\* superseded, outranked or retracted, and no un-retracted assured adult proof is dated before t
LiveProofBefore(H, t) == \E r \in H \cap AgeRows : r.k = "assured" /\ r.band = "adult" /\ r.at < t /\ ~Retracted(H, r)
VoidAt(H, t) == (\E r \in H : IsMinor(r)) /\ ~LiveProofBefore(H, t)

VARIABLES held, rows, rets, ann, own, guard
vars == <<held, rows, rets, ann, own, guard>>

Init == /\ held = [n \in Nodes |-> {}] /\ rows = [n \in Nodes |-> [s \in Signers |-> {}]]
        /\ rets = [n \in Nodes |-> {}] /\ ann = [n \in Nodes |-> FALSE]
        /\ own = [n \in Nodes |-> TRUE] /\ guard = [n \in Nodes |-> TRUE]

Offer(n, r) ==
  /\ r \notin held[n]
  /\ held' = [held EXCEPT ![n] = @ \cup {r}]
  /\ rows' = [rows EXCEPT ![n] = [s \in Signers |-> IF r \in AgeRows /\ r.s = s THEN @[s] \cup {r} ELSE @[s]]]
  /\ rets' = [rets EXCEPT ![n] = IF r \in RetractRows THEN @ \cup {<<r.tgt, r.at>>} ELSE @]
  /\ LET band == MS!CoarseBandAt(rows'[n], rets'[n], MS!Forever)
     IN /\ ann' = [ann EXCEPT ![n] = IF ~MUT \/ r = Bind THEN Bind \in held'[n] /\ band # "minor" ELSE @]
        /\ own' = [own EXCEPT ![n] = band # "minor"]
        /\ guard' = [guard EXCEPT ![n] = band # "adult"]
Done == (\A n \in Nodes : held[n] = Rows) /\ UNCHANGED vars
Next == (\E n \in Nodes, r \in Rows : Offer(n, r)) \/ Done
Spec == Init /\ [][Next]_vars

\* P1 two nodes holding the same rows agree on all three relations, whatever order each took them in
Inv_NodesAgree == held[1] = held[2] => (ann[1] = ann[2] /\ own[1] = own[2] /\ guard[1] = guard[2])
\* P2 what each node kept as rows arrived is the set function of the rows held now
Inv_Fold == \A n \in Nodes : ann[n] = Announced(held[n]) /\ own[n] = OwnerCounts(held[n]) /\ guard[n] = GuardLive(held[n])
\* P3 no order leaves a person announced whose current band reads minor
Inv_NoMinorAnnounced == \A n \in Nodes : ann[n] => HeldBand(held[n]) # "minor"
\* P4 supersession lifts: a minor row whose signer holds a newer, unretracted row no longer stands, so
\* dropping it changes nothing
Inv_SupersededLifts ==
  \A n \in Nodes : \A m \in held[n] : (IsMinor(m) /\ \E a \in held[n] \cap AgeRows : a.s = m.s /\ a.at > m.at /\ ~Retracted(held[n], a))
    => ann[n] = Announced(held[n] \ {m})
\* P5 outranking lifts, whatever the dates: with the subject's current row not minor, the rows of a witness
\* below a witness with a current row decide nothing
Inv_OutrankedLifts ==
  \A n \in Nodes : \A w, v \in MS!Witnesses :
    (MS!Level(w) < MS!Level(v) /\ SB(held[n], v) # "none" /\ SB(held[n], 0) # "minor")
      => ann[n] = Announced({r \in held[n] : ~(r \in AgeRows /\ r.s = w)})
\* P6 the subject's own minor self-declaration blocks, whenever it was made
Inv_SelfLowerBlocks == \A n \in Nodes : SB(held[n], 0) = "minor" => ~ann[n]
\* P7 a later assured adult lifts: with the subject not minor, a top current adult row dated after every top
\* current minor row lets the bound node announce (the 15-then-19 case)
Inv_LaterAssuredAdultLifts ==
  \A n \in Nodes : (Bind \in held[n] /\ SB(held[n], 0) # "minor"
                      /\ \E a \in Top(held[n]) : a.band = "adult" /\ \A m \in Top(held[n]) : m.band \in MS!MinorBands => m.at < a.at)
                     => ann[n]
\* P8 a contradiction blocks: a top current minor row dated at or after every top current adult row, the
\* same instant from different signers included
Inv_ContradictionBlocks ==
  \A n \in Nodes : (\E m \in Top(held[n]) : m.band \in MS!MinorBands /\ \A a \in Top(held[n]) : a.band = "adult" => a.at <= m.at)
                     => ~ann[n]
Inv_SameInstantBlocks ==
  \A n \in Nodes : (\E m, a \in Top(held[n]) : m.band \in MS!MinorBands /\ a.band = "adult" /\ m.s # a.s /\ m.at = a.at
                       /\ \A b \in Top(held[n]) : b.band = "adult" => b.at <= m.at) => ~ann[n]
\* P9 the void reads what the standing protection lets go: while the person is announced, any held minor row
\* (superseded, outranked or retracted) with no un-retracted proof before it still voids a duty appointment
\* dated at its instant
Inv_VoidKeepsWhatStandingLifts ==
  \A n \in Nodes : \A m \in held[n] : (ann[n] /\ IsMinor(m) /\ ~LiveProofBefore(held[n], m.at)) => VoidAt(held[n], m.at)
\* Witness for P9: StandingProtection_void_witness.cfg checks this, and TLC reports a node announced while it
\* holds a minor row
NoMinorRowWhileAnnounced == \A n \in Nodes : ann[n] => ~\E m \in held[n] : IsMinor(m)
\* P10 no carve-out by scope (CC 3.2 l.961): the federation-scope binding counts exactly when the self-scope
\* binding does, and the self-scope binding counts for nothing while the band reads minor
Inv_NoScopeCarveOut == \A n \in Nodes : (Bind \in held[n] => ann[n] = own[n]) /\ (HeldBand(held[n]) = "minor" => ~own[n])
\* P11 the guardianship ends only when the band reads adult, which needs an assured (witness) current row
Inv_GuardEndsOnlyByAssurance == \A n \in Nodes : ~guard[n] => \E w \in MS!Witnesses : SB(held[n], w) = "adult"
\* P12 a self-declaration never ends the guardianship: the subject's own rows alone keep it standing
Inv_SelfDeclarationKeepsGuardian ==
  \A n \in Nodes : GuardLive({r \in held[n] : r \in RetractRows \/ (r \in AgeRows /\ r.s = 0)})
\* P13 the person is always under a guardian or counted as an owner, never neither; both while no band is read
Inv_GuardOrOwner == \A n \in Nodes : guard[n] \/ own[n]
\* P14 a minor row arriving that makes the band read minor pulls the announcement back
Prop_MinorPullsBack ==
  [][\A n \in Nodes : ((held'[n] \ held[n]) \cap AgeRows # {} /\ HeldBand(held'[n]) = "minor") => ~ann'[n]]_vars
\* P15 a withdrawal after which the band no longer reads minor restores the announcement
Prop_WithdrawalRestores ==
  [][\A n \in Nodes : ((held'[n] \ held[n]) \cap RetractRows # {} /\ Bind \in held'[n] /\ HeldBand(held'[n]) # "minor")
                        => ann'[n]]_vars
==========================================================================
