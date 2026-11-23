---------------------------- MODULE ConferralEnd ----------------------------
(* The causal end of a conferral (CC 2.4.1.1 as ruled: "A withdraws row retires its target as a cut does
   (CC 2.7.7). An act under the target that the withdrawal has among its ancestors stands. One that has the
   withdrawal in its own past, or is concurrent with it, does not count."), read as the Constitution intends
   it (2026-11-21): an end is FORWARD. A concurrent act counts at its own head and is not in force from the
   end's head on; nothing the end does voids an act at the act's own head when that head is not later than
   the end's. CC 4.5.5: "Acts already taken under the duty stand". No instant is read anywhere: the only order
   is what rows name. The verdict is models/tla/CONFERRAL_END.md.

   The rows. Fixed and in every row's past: an offer by A to B, B's acceptance `acc`, the roster head H0 (for a
   root grant read: a genesis-bundle version; for an owner binding, the binding row), and (with WithTie) a
   second, independent grant to B by another grantor D, `accD`, authorising the same acts. Signed in any
   order, each naming only rows already signed:
     H1        a roster version extending H0 (a later bundle version; absent for an owner binding: WithH1).
     b1..bN    B's acts, each on one of two DEVICES, NAMING THE HEAD IT IS AT (H0 or H1, any one signed, so an
               OLD head too, as a signer whose node is behind would), `under` acc or the re-acceptance a2,
               `prev` the device's previous act under the same `under`, optionally citing the end. One may
               be a deputy edge `sub`: an offer by B to C, itself exercised under acc.
     u1        an UNCITED act of B (persist today): it names nothing, no head, no prev, no grant.
     c1        C's act under the deputy edge (reached by the end transitively).
     E         the END: by A (withdrawing the offer) or by B (withdrawing its own acceptance: a resignation),
               naming the head it acts from (h_e), `ack` (an antichain of B's acts it holds: the proposal)
               and the receipts it holds that it names (the ender-side receipt variant). Its head is not
               older than a head in its own past.
     Q1..Qn    RECEIPTS: a clean ack of one act of B, signed by A (the conferrer), D (a co-holder of the body
               the act was done for) or B itself, on one of two devices, naming that signer's previous
               receipt on that device (its own series) and optionally the end.
     Rm        a removal of a key (the ender's, or D's), naming the end or not.
     Rx        the body's end of the seat of R, a receipter the grant names (WithRx), naming R's receipts
               it has seen. Receipts may also be signed by R, and may name Rx.
     a2        B's re-acceptance of the offer, naming the end or not.
   Two nodes take the rows: node 1 in ANY order the door allows (so an act may arrive long after the end is
   held, at a node that never saw it), node 2 in one fixed order; node 1 may acknowledge H1 (CC 2.7.8).

   Four answers are computed in every state, for every act, as <<counts at its own head, in force from the
   end's head on>>:
     "full"   the proposal: `under`, `prev`, `ack`. An act in the end's past stands; one with the end in its
              past does not count; a concurrent act counts at its own head and is not in force from h_e on,
              and if its head is LATER than h_e it does not count (the standing is ended there; rule 4, "from
              the head the cut names") unless the ender holds a clean receipt of it concurrent with the end
              (rule 6, one say).
     "set"    no prev: the end names every acked act individually; an act's own past has no prev edge.
     "weak"   acts name their head and nothing else new (no prev, no `under`); the end names h_e. The standing
              is found by the seat walk (ANY-STANDING); the end has no acked past.
     "weakR"  weak + ENDER'S RECEIPTS: an act stays in force after h_e when a receipt of it by the ender's side
              (A or D, never the act's own signer) is in the end's causal past (RSCOPE = "past"), or held and
              not after the end (RSCOPE = "any").

   PLANT selects one planted break (each caught):
     "members"   the end applied to the member set at every head (B dropped from n);
     "say"       the ender's clean receipt ignored;
     "naming"    an act naming the end read as concurrent;
     "arrival"   each act's answer latched when it arrives (a late act refused its answer, no re-fold);
     "own_head"  the end voids a concurrent act at the end's own head (a cut at the act's own head);
     "receipts"  a receipt in the end's past ignored (weakR);
     "self"      the grantee's own receipt keeps its own act in force (weakR);
     "selflift"  a self end (a resignation) carrying `lifts` lifts the co-holders' receipts;
     "after_rx"  the receipter's receipt made after the body ended its seat still keeps;
     "bulk_after" a receipt with the end in its past (a bulk receipt after the end) keeps.
   (`_plant_converge` runs "arrival" against Inv_NodesAgree alone.)
   Documented failing configurations (outside both runs): TIE = "any" (ANY-STANDING for the full reading),
   LINE = "tips" (guard b, the line over the series' tips), LINEACTS (the line of CC 2.7.8 applied to authored
   acts that name a head), RSCOPE = "any" and the resignation case, and the differences between readings. *)
EXTENDS Naturals, FiniteSets, Sequences

CONSTANTS PLANT, TIE, LINE, LINEACTS, RSCOPE, WHO, MaxB, MaxQ, WithH1, WithU, WithC, WithRm, WithA2, WithTie,
          WithBEnder, WithRx, DUMPANS

BNum == {"b1", "b2", "b3"}
BId(i) == CASE i = 1 -> "b1" [] i = 2 -> "b2" [] OTHER -> "b3"
BIds == BNum \cup {"u1"}                 \* B's acts, the uncited one included
Qs == {"Q1", "Q2", "Q3"}
QId(i) == CASE i = 1 -> "Q1" [] i = 2 -> "Q2" [] OTHER -> "Q3"
ActIds == BIds \cup {"c1"}
Ids == ActIds \cup Qs \cup {"H1", "E", "Rm", "a2", "Rx"}
None == "none"
Null == [k |-> None, s |-> None, dev |-> 0, hd |-> "H0", un |-> None, nm |-> {}, prev |-> None,
         ack |-> {}, of |-> None, sub |-> FALSE, tgt |-> None, lifts |-> FALSE]
Variants == {"full", "set", "weak", "weakR"}

VARIABLES made, f, done, h1, ak, rk, latch, ans
vars == <<made, f, done, h1, ak, rk, latch, ans>>

Made == made

RECURSIVE Anc(_)
Anc(x) == f[x].nm \cup UNION {Anc(y) : y \in f[x].nm}
\* the past each reading's wire carries: the "set" reading carries no prev on acts (AncS); the weak readings
\* carry no prev on acts and no ack on the end (AncW). A receipt's own series (its prev) is carried by all.
\* (Found by tools/conferral_xcheck.py: the weak readings first read a receipt's past through act prev edges.)
NoPrev(x) == f[x].nm \ (IF f[x].k = "act" THEN {f[x].prev} ELSE {})
RECURSIVE AncS(_)
AncS(x) == LET d == NoPrev(x) IN d \cup UNION {AncS(y) : y \in d}
RECURSIVE AncW(_)
AncW(x) == LET d == NoPrev(x) \ (IF x = "E" THEN f[x].ack ELSE {}) IN d \cup UNION {AncW(y) : y \in d}
AncV(x, v) == CASE v = "full" -> Anc(x) [] v = "set" -> AncS(x) [] OTHER -> AncW(x)

\* heads: H0 < H1; an uncited act has no head ("none") and is never at a head later than h_e
Later(h, he) == h = "H1" /\ he = "H0"
Heads(S) == {"H0"} \cup ({"H1"} \cap S)
EndHd == f["E"].hd
SubOf == IF \E y \in BNum : f[y].sub THEN CHOOSE y \in BNum : f[y].sub ELSE None

\* ---- the answer ------------------------------------------------------------------------------------------
KeyCutV(y, S, v) == "Rm" \in S /\ f[y].s = f["Rm"].tgt /\ y \notin AncV("Rm", v)
\* cut under some reading (an exclusion the invariants use)
KeyCut(y, S) == \E v \in Variants : KeyCutV(y, S, v)
RmV(S) == "E" \in S /\ KeyCut("E", S)
\* the end counts for this reader: held, not voided by a concurrent removal of its signer's key, and not an
\* old fork of a roster head the reader acknowledged (it names H0, and H1 names nothing)
EL0(S, a) == "E" \in S /\ ~RmV(S) /\ ~(a /\ EndHd = "H0")
\* LINE = "tips": the proposal's guard (b): the reader acknowledged a tip rk of the series; an end whose acked
\* tips all lie behind rk, and which rk does not have in its past, is void for that reader
TipLine(S) == LINE = "tips" /\ rk # None /\ rk \in S /\ f["E"].ack # {} /\ "E" \notin Anc(rk)
                /\ rk \notin Anc("E") /\ \A t \in f["E"].ack : t \in Anc(rk)
EL(S, a) == EL0(S, a) /\ ~TipLine(S)
KeyV(x, S) == KeyCut(x, S)
\* LINEACTS: CC 2.7.8's line applied to an authored act that names a head (a reader that acknowledged H1
\* holds void an act naming H0 that H1 does not have in its past)
LineAct(x, a) == LINEACTS /\ a /\ f[x].hd = "H0" /\ "H1" \notin Anc(x)
Members(S, a) == IF PLANT = "members" /\ EL(S, a) THEN {"A", "C", "D"} ELSE {"A", "B", "C", "D"}
\* one say: a clean receipt of the act by the ender, concurrent with the end
Say(x, S, v) == PLANT # "say" /\ \E q \in Qs \cap S : f[q].of = x /\ f[q].s = f["E"].s /\ ~KeyCutV(q, S, v)
                                                     /\ "E" \notin AncV(q, v) /\ q \notin AncV("E", v)
\* WHO RECEIPTS. A is the conferrer (for a root grant or a room's duty seat: the body's COUNT; its receipts
\* are counted rows, a bulk receipt included), D a single co-holder, R a receipter the grant names (a seat or
\* the worker's owner, conferred by the body and ended by it: Rx), B the grantee (never, for its own acts).
\* A count end (by A) may carry `lifts` (compromise): then no single receipt (D's or R's) keeps anything; a
\* rotation does not carry it. A self end (by B) cannot lift receipts. WHO = "none" is (d): only the count's
\* own receipts keep anything.
Lifted(pl) == f["E"].lifts /\ (f["E"].s = "A" \/ pl = "selflift")
Elig(q, x, pl) == CASE f[q].s = "A" -> TRUE
                    [] f[q].s = "D" -> WHO = "all" /\ ~Lifted(pl)
                    [] f[q].s = "R" -> WHO = "all" /\ ~Lifted(pl) /\ (pl = "after_rx" \/ "Rx" \notin AncW(q))
                    [] OTHER -> pl = "self"
KeptP(x, S, pl) == \E q \in Qs \cap S : f[q].of = x /\ Elig(q, x, pl) /\ ~KeyCutV(q, S, "weakR") /\
                     (q \in AncW("E") \/ (RSCOPE = "any" /\ ("E" \notin AncW(q) \/ pl = "bulk_after")))
Kept(x, S) == KeptP(x, S, PLANT)
KeptH(x, S) == KeptP(x, S, "none")
\* another live standing of the signer authorises the act: ANY-STANDING (always under the weak readings)
OtherAuth(x, S, v) == x \in BIds /\ (v \in {"weak", "weakR"} \/ TIE = "any") /\
                      (WithTie \/ ("E" \in S /\ f["E"].s = "B" /\ "a2" \in S))
\* the offer's withdrawal by A reaches acts under any acceptance of that offer, a2 included
Reached(x, v) == x = "c1" \/ (x \in BIds /\ (v \in {"weak", "weakR"} \/ f[x].un = "acc" \/ f["E"].s = "A"))
Seen(x, S, v) == CASE v \in {"full", "set"} -> x \in Anc("E")
                   [] v = "weakR" -> PLANT # "receipts" /\ Kept(x, S)
                   [] OTHER -> FALSE
SeenH(x, S, v) == CASE v \in {"full", "set"} -> x \in Anc("E") [] v = "weakR" -> KeptH(x, S) [] OTHER -> FALSE
NamesEnd(x, v) == "E" \in AncV(x, v)

EndRule(x, S, a, v) ==
  IF ~EL(S, a) \/ ~Reached(x, v) \/ OtherAuth(x, S, v) THEN <<TRUE, TRUE>>
  ELSE IF NamesEnd(x, v) /\ PLANT # "naming" THEN <<FALSE, FALSE>>
  ELSE IF Later(f[x].hd, EndHd) THEN <<Say(x, S, v), FALSE>>
  ELSE IF Seen(x, S, v) THEN <<TRUE, TRUE>>
  ELSE IF PLANT = "own_head" /\ f[x].hd = EndHd THEN <<FALSE, FALSE>>
  ELSE <<TRUE, FALSE>>

Base(x, S, a, v) == f[x].s \in Members(S, a) /\ ~LineAct(x, a) /\ ~KeyCutV(x, S, v)

RECURSIVE Ans(_, _, _, _)
Ans(x, S, a, v) ==
  LET e == EndRule(x, S, a, v)
      up == IF x = "c1" THEN Ans(SubOf, S, a, v) ELSE <<TRUE, TRUE>>
      b == Base(x, S, a, v)
  IN <<b /\ e[1] /\ up[1], b /\ e[1] /\ e[2] /\ up[2]>>

\* node 1 takes the rows in any order the door allows (h1, ak); node 2 in one fixed order the door allows
\* (by depth, then name), without an acknowledgement: holding Prefix(k), it answers as Rep2 (under the
\* arrival plant, the answer latched over the prefix that ends with the act)
IdNum(x) == CASE x = "H1" -> 1 [] x = "b1" -> 2 [] x = "b2" -> 3 [] x = "b3" -> 4 [] x = "a2" -> 5
              [] x = "E" -> 6 [] x = "c1" -> 7 [] x = "u1" -> 8 [] x = "Rm" -> 9 [] x = "Q1" -> 10
              [] x = "Q2" -> 11 [] x = "Rx" -> 12 [] OTHER -> 13
Rank(x) == Cardinality(Anc(x)) * 16 + IdNum(x)
Pos(x) == 1 + Cardinality({y \in made : Rank(y) < Rank(x)})
Prefix(k) == {y \in made : Pos(y) <= k}
\* DUMPANS: carry the weakR answer of every held act in `ans`, so that a TLC state dump holds the model's own
\* answers (tools/conferral_xcheck.py compares them with models/causal_kernel/conferral_end.py). A function
\* of the other variables: it adds no distinct state.
AnsOf(S, a) == IF DUMPANS THEN [x \in ActIds \cap S |-> Ans(x, S, a, "weakR")] ELSE <<>>
Rep1(x) == IF PLANT = "arrival" THEN latch[x] ELSE Ans(x, h1, ak, "full")
Rep2(k, x) == IF PLANT = "arrival" THEN Ans(x, Prefix(Pos(x)), FALSE, "full") ELSE Ans(x, Prefix(k), FALSE, "full")
Without(S) == {y \in S : y # "E" /\ "E" \notin Anc(y)}

\* ---- signing ---------------------------------------------------------------------------------------------
Mk(id, r) == /\ ~done /\ id \notin Made
             /\ made' = made \cup {id} /\ f' = [f EXCEPT ![id] = r]
             /\ UNCHANGED <<done, h1, ak, rk, latch, ans>>

MakeH1 == WithH1 /\ Mk("H1", [Null EXCEPT !.k = "version", !.s = "count"])

TipOn(d, u) == {y \in Made \cap BNum : f[y].dev = d /\ f[y].un = u /\
                  ~\E z \in Made \cap BNum : f[z].dev = d /\ f[z].un = u /\ y \in Anc(z)}
MakeB(d, hd, cite, u, sb) ==
  LET nb == Cardinality(Made \cap BNum)
      p == TipOn(d, u)
      pv == IF p = {} THEN None ELSE CHOOSE y \in p : TRUE
  IN /\ nb < MaxB
     /\ hd \in Heads(Made)
     /\ (cite => "E" \in Made)
     /\ (u = "a2" => "a2" \in Made)
     /\ (sb => WithC /\ u = "acc" /\ ~\E y \in Made \cap BNum : f[y].sub)
     /\ Mk(BId(nb + 1), [Null EXCEPT !.k = "act", !.s = "B", !.dev = d, !.hd = hd, !.un = u, !.prev = pv,
             !.sub = sb, !.nm = (IF pv = None THEN {} ELSE {pv}) \cup (IF hd = "H1" THEN {"H1"} ELSE {})
                                \cup (IF cite THEN {"E"} ELSE {}) \cup (IF u = "a2" THEN {"a2"} ELSE {})])

MakeU == WithU /\ Mk("u1", [Null EXCEPT !.k = "act", !.s = "B", !.hd = None, !.un = "acc"])

MakeC(hd, cite) ==
  /\ WithC /\ SubOf # None /\ SubOf \in Made
  /\ hd \in Heads(Made) /\ (cite => "E" \in Made)
  /\ Mk("c1", [Null EXCEPT !.k = "act", !.s = "C", !.hd = hd, !.un = "sub",
               !.nm = {SubOf} \cup (IF hd = "H1" THEN {"H1"} ELSE {}) \cup (IF cite THEN {"E"} ELSE {})])

MakeE(s, ack, rq, hd, lf) ==
  LET nm == ack \cup rq
      past == nm \cup UNION {Anc(y) : y \in nm}
  IN /\ s \in (IF WithBEnder THEN {"A", "B"} ELSE {"A"})
     /\ ack \subseteq {y \in Made \cap BIds : f[y].un = "acc"}
     /\ rq \subseteq Made \cap Qs
     /\ \A y, z \in nm : y \notin Anc(z)
     /\ hd \in Heads(Made) /\ ("H1" \in past => hd = "H1")
     /\ Mk("E", [Null EXCEPT !.k = "end", !.s = s, !.hd = hd, !.ack = ack, !.lifts = lf,
                 !.nm = nm \cup (IF hd = "H1" THEN {"H1"} ELSE {})])

QTip(s, d) == {q \in Made \cap Qs : f[q].s = s /\ f[q].dev = d /\
                 ~\E r \in Made \cap Qs : f[r].s = s /\ f[r].dev = d /\ q \in Anc(r)}
MakeQ(s, d, x, afterE, afterRx) ==
  LET nq == Cardinality(Made \cap Qs)
      p == QTip(s, d)
      pv == IF p = {} THEN None ELSE CHOOSE y \in p : TRUE
  IN /\ nq < MaxQ /\ x \in Made \cap BIds /\ (afterE => "E" \in Made)
     /\ (MaxQ = 1 => d = 1)              \* a second device matters only for a second receipt
     /\ (afterRx => s = "R" /\ "Rx" \in Made)
     /\ Mk(QId(nq + 1), [Null EXCEPT !.k = "receipt", !.s = s, !.dev = d, !.of = x, !.prev = pv,
             !.nm = {x} \cup (IF pv = None THEN {} ELSE {pv}) \cup (IF afterE THEN {"E"} ELSE {})
                    \cup (IF afterRx THEN {"Rx"} ELSE {})])

\* the body's end of the receipter's seat, naming the receipts it has seen (or none)
MakeRx(rq) == WithRx /\ rq \subseteq {q \in Made \cap Qs : f[q].s = "R"} /\
              Mk("Rx", [Null EXCEPT !.k = "unseat", !.s = "A", !.nm = rq])

MakeRm(k, nE) == WithRm /\ "E" \in Made /\ k \in {f["E"].s, "D"} /\
                 Mk("Rm", [Null EXCEPT !.k = "removal", !.s = "count", !.tgt = k,
                           !.nm = IF nE THEN {"E"} ELSE {}])

MakeA2(nE) == WithA2 /\ (nE => "E" \in Made) /\
              Mk("a2", [Null EXCEPT !.k = "accept", !.s = "B", !.nm = IF nE THEN {"E"} ELSE {}])

\* ---- arrival ---------------------------------------------------------------------------------------------
Latched(S, x) == IF PLANT = "arrival" /\ x \in ActIds
                 THEN [latch EXCEPT ![x] = Ans(x, S, ak, "full")] ELSE latch

Arrive(x) == /\ done /\ x \in Made \ h1 /\ f[x].nm \subseteq h1
             /\ h1' = h1 \cup {x} /\ latch' = Latched(h1 \cup {x}, x) /\ ans' = AnsOf(h1 \cup {x}, ak)
             /\ UNCHANGED <<made, f, done, ak, rk>>
AckH1 == /\ "H1" \in h1 /\ ~ak
         /\ ak' = TRUE /\ ans' = AnsOf(h1, TRUE) /\ UNCHANGED <<made, f, done, h1, rk, latch>>
AckTip(x) == /\ LINE = "tips" /\ x \in h1 \cap BNum /\ rk = None
             /\ rk' = x /\ UNCHANGED <<made, f, done, h1, ak, latch, ans>>

Init == /\ made = {} /\ f = [i \in Ids |-> Null] /\ done = FALSE /\ h1 = {} /\ ans = <<>>
        /\ ak = FALSE /\ rk = None /\ latch = [i \in Ids |-> None]

Close == ~done /\ done' = TRUE /\ UNCHANGED <<made, f, h1, ak, rk, latch, ans>>

Next == \/ Close
        \/ MakeH1
        \/ \E d \in {1, 2}, hd \in {"H0", "H1"}, c \in BOOLEAN, u \in {"acc", "a2"}, sb \in BOOLEAN :
              MakeB(d, hd, c, u, sb)
        \/ MakeU
        \/ \E hd \in {"H0", "H1"}, c \in BOOLEAN : MakeC(hd, c)
        \/ \E s \in {"A", "B"}, ack \in SUBSET BIds, rq \in SUBSET Qs, hd \in {"H0", "H1"}, lf \in BOOLEAN :
              MakeE(s, ack, rq, hd, lf)
        \/ \E s \in {"A", "D", "R", "B"}, d \in {1, 2}, x \in BIds, b, r \in BOOLEAN :
              (s = "R" => WithRx) /\ MakeQ(s, d, x, b, r)
        \/ \E rq \in SUBSET Qs : MakeRx(rq)
        \/ \E k \in {"A", "B", "D"}, b \in BOOLEAN : MakeRm(k, b)
        \/ \E b \in BOOLEAN : MakeA2(b)
        \/ \E x \in Ids : Arrive(x)
        \/ AckH1
        \/ \E x \in BNum : AckTip(x)
        \/ (done /\ UNCHANGED vars)     \* everything signed and delivered: nothing left to do

Spec == Init /\ [][Next]_vars

\* ---- invariants ------------------------------------------------------------------------------------------
\* every act node 1 holds (node 2's held sets are prefixes of one order, each a set node 1 also reaches)
ForAll(P(_, _, _, _)) == \A x \in ActIds \cap h1 : P(x, h1, ak, 1)
Static(x, S, a) == ~LineAct(x, a) /\ ~KeyV(x, S)
Upstream(x, S, a, v) == x = "c1" => Ans(SubOf, S, a, v)[1]

PPast(x, S, a, n) == \A v \in {"full", "set"} :
  (EL(S, a) /\ x \in BIds /\ x \in Anc("E") /\ Static(x, S, a)) => Ans(x, S, a, v) = <<TRUE, TRUE>>
Inv_PastStands == ForAll(PPast)

PNaming(x, S, a, n) == \A v \in Variants :
  (EL(S, a) /\ Reached(x, v) /\ ~OtherAuth(x, S, v) /\ NamesEnd(x, v)) => ~Ans(x, S, a, v)[1]
Inv_NamingEndVoid == ForAll(PNaming)

PForce(x, S, a, n) == \A v \in Variants :
  (EL(S, a) /\ Reached(x, v) /\ ~OtherAuth(x, S, v) /\ ~SeenH(x, S, v)) => ~Ans(x, S, a, v)[2]
Inv_NotInForceFromEnd == ForAll(PForce)

\* forward: an act at or before the end's head (or naming no head), not naming the end, counts at its head
PFwd(x, S, a, n) == \A v \in Variants :
  (EL(S, a) /\ Static(x, S, a) /\ Upstream(x, S, a, v) /\ ~NamesEnd(x, v) /\ ~Later(f[x].hd, EndHd))
    => Ans(x, S, a, v)[1]
Inv_ForwardNeverVoidsAtOwnHead == ForAll(PFwd)

\* the end never changes what counted at an act's own head, unless the act names it or sits at a later head:
\* an act arriving late, after the end is held, or re-folded after it, keeps its count
PUnmake(x, S, a, n) == \A v \in Variants :
  ("E" \in S /\ "Rm" \notin S /\ x \in Without(S) /\ ~Later(f[x].hd, EndHd)
     /\ (x = "c1" => ~Later(f[SubOf].hd, EndHd))) =>
    Ans(x, S, a, v)[1] = Ans(x, Without(S), a, v)[1]
Inv_EndNeverUnmakes == ForAll(PUnmake)

PSay(x, S, a, n) == \A v \in Variants :
  (EL(S, a) /\ x \in BNum /\ Static(x, S, a) /\ Reached(x, v) /\ ~OtherAuth(x, S, v)
     /\ ~NamesEnd(x, v) /\ Later(f[x].hd, EndHd)
     /\ \E q \in Qs \cap S : f[q].of = x /\ f[q].s = f["E"].s /\ ~KeyCutV(q, S, v) /\ "E" \notin AncV(q, v)
                             /\ q \notin AncV("E", v))
    => Ans(x, S, a, v) = <<TRUE, FALSE>>
Inv_OneSay == ForAll(PSay)

Inv_MembersByPast == Members(h1, ak) = {"A", "B", "C", "D"}

PRm(x, S, a, n) == (RmV(S) /\ x \in BIds /\ Static(x, S, a)) => Ans(x, S, a, "full") = <<TRUE, TRUE>>
Inv_RemovalVoidsEnd == ForAll(PRm)

PReacc(x, S, a, n) == (x \in BIds /\ f[x].un = "a2" /\ "E" \in Made /\ f["E"].s = "B" /\ Static(x, S, a))
                        => Ans(x, S, a, "full") = <<TRUE, TRUE>>
Inv_ReacceptUntouched == ForAll(PReacc)

Inv_NodesAgree == ~ak => \A k \in 0..Cardinality(made) : h1 = Prefix(k) => \A x \in ActIds \cap h1 : Rep1(x) = Rep2(k, x)
PFold(x, S, a, n) == Rep1(x) = Ans(x, S, a, "full")
Inv_Fold == ForAll(PFold)

\* the target cannot void its own end: the end counts for a reader unless removed or an old fork of a roster
\* head that reader acknowledged (ConferralEnd_line_tips.cfg runs LINE = "tips", where it fails); receipts
\* never touch whether the end counts
Inv_TargetCannotVoidEnd == ("E" \in h1) => (EL(h1, ak) = EL0(h1, ak))

\* ---- weak + ender's receipts ------------------------------------------------------------------------------
\* a receipted act in the end's past stays in force (plant "receipts")
PRcpt(x, S, a, n) ==
  (EL(S, a) /\ x \in BIds /\ Static(x, S, a) /\ ~OtherAuth(x, S, "weakR") /\ ~NamesEnd(x, "weakR")
     /\ ~Later(f[x].hd, EndHd) /\ KeptH(x, S)) => Ans(x, S, a, "weakR") = <<TRUE, TRUE>>
Inv_ReceiptedStays == ForAll(PRcpt)
\* a receipt never revives an act at a later head or one naming the end
PRFwd(x, S, a, n) == (EL(S, a) /\ Reached(x, "weakR") /\ ~OtherAuth(x, S, "weakR") /\
                      (NamesEnd(x, "weakR") \/ Later(f[x].hd, EndHd))) => ~Ans(x, S, a, "weakR")[2]
Inv_ReceiptForwardOnly == ForAll(PRFwd)
\* receipts change force only, never a count
PRCnt(x, S, a, n) == Ans(x, S, a, "weakR")[1] = Ans(x, S, a, "weak")[1]
Inv_ReceiptsChangeOnlyForce == ForAll(PRCnt)
\* RSCOPE = "any" (ConferralEnd_receipts_any.cfg): a co-holder's receipt the end does not have in its past
\* keeps an act in force against the ender (fails there)
PEnder(x, S, a, n) == (EL(S, a) /\ Reached(x, "weakR") /\ ~OtherAuth(x, S, "weakR") /\
                       ~\E q \in Qs \cap S : q \in AncW("E") /\ f[q].of = x) => ~Ans(x, S, a, "weakR")[2]
Inv_EnderDecidesForce == ForAll(PEnder)
\* a resignation (the end by B) that does not name a co-holder's receipt held before it: is the act kept?
\* (fails under RSCOPE = "past": ConferralEnd_receipts_resign.cfg)
PResign(x, S, a, n) ==
  (WHO = "all" /\ EL(S, a) /\ f["E"].s = "B" /\ x \in BIds /\ Static(x, S, a) /\ ~NamesEnd(x, "weakR") /\
   ~Later(f[x].hd, EndHd) /\ \E q \in Qs \cap S : f[q].of = x /\ f[q].s = "D" /\ ~KeyCutV(q, S, "weakR") /\ "E" \notin AncW(q))
    => Ans(x, S, a, "weakR")[2]
Inv_ResignNeedsNoCooperation == ForAll(PResign)
\* (a) refined: a count end that lifts receipts leaves in force only what the count itself receipted
PLifts(x, S, a, n) ==
  (EL(S, a) /\ f["E"].s = "A" /\ f["E"].lifts /\ Reached(x, "weakR") /\ ~OtherAuth(x, S, "weakR") /\
   ~\E q \in Qs \cap S : f[q].of = x /\ f[q].s = "A") => ~Ans(x, S, a, "weakR")[2]
Inv_CountEndLiftsSingles == ForAll(PLifts)
\* a rotation (a count end without `lifts`) keeps what a single co-holder receipted before it
PRot(x, S, a, n) ==
  (EL(S, a) /\ f["E"].s = "A" /\ ~f["E"].lifts /\ x \in BIds /\ Static(x, S, a) /\ ~NamesEnd(x, "weakR") /\
   ~Later(f[x].hd, EndHd) /\ \E q \in Qs \cap S : f[q].of = x /\ f[q].s = "D" /\ ~KeyCutV(q, S, "weakR") /\ "E" \notin AncW(q))
    => Ans(x, S, a, "weakR")[2]
Inv_RotationKeepsReceipted == ForAll(PRot)
\* (b): the receipter's receipts made before the body ended its seat stand; one made after keeps nothing
PRBefore(x, S, a, n) ==
  (WHO = "all" /\ EL(S, a) /\ ~Lifted("none") /\ x \in BIds /\ Static(x, S, a) /\ ~NamesEnd(x, "weakR") /\
   ~Later(f[x].hd, EndHd) /\ "Rx" \in S /\
   \E q \in Qs \cap S : f[q].of = x /\ f[q].s = "R" /\ q \in AncW("Rx") /\ ~KeyCutV(q, S, "weakR") /\ "E" \notin AncW(q))
    => Ans(x, S, a, "weakR")[2]
Inv_ReceipterBeforeStands == ForAll(PRBefore)
PRAfter(x, S, a, n) ==
  (EL(S, a) /\ Reached(x, "weakR") /\ ~OtherAuth(x, S, "weakR") /\
   \A q \in Qs \cap S : f[q].of = x => (f[q].s = "R" /\ "Rx" \in AncW(q))) => ~Ans(x, S, a, "weakR")[2]
Inv_ReceipterAfterItsEndNothing == ForAll(PRAfter)
\* a receipt with the end in its past (a bulk receipt by the count after the end included) keeps nothing
PBulk(x, S, a, n) ==
  (EL(S, a) /\ Reached(x, "weakR") /\ ~OtherAuth(x, S, "weakR") /\
   \A q \in Qs \cap S : f[q].of = x => "E" \in AncW(q)) => ~Ans(x, S, a, "weakR")[2]
Inv_ReceiptAfterEndNothing == ForAll(PBulk)
\* as-of: an act at its head stays counted for every reader whatever head the reader acknowledged
\* (fails with LINEACTS: ConferralEnd_line_acts.cfg)
PAsOf(x, S, a, n) == (x \in BNum /\ ~KeyV(x, S) /\ ("E" \in S => (~NamesEnd(x, "weak") /\ ~Later(f[x].hd, EndHd))))
                       => Ans(x, S, a, "weak")[1]
Inv_AsOfStands == ForAll(PAsOf)

\* ---- where the readings agree, and where they differ ------------------------------------------------------
PrevSticky(x) == "E" \in Anc(x) /\ "E" \notin AncS(x)
WeakOther(S) == "E" \in S /\ f["E"].s = "B" /\ "a2" \in S
PSet(x, S, a, n) == ~PrevSticky(x) => Ans(x, S, a, "full") = Ans(x, S, a, "set")
Inv_SetAgrees == ForAll(PSet)
PSetAll(x, S, a, n) == Ans(x, S, a, "full") = Ans(x, S, a, "set")
Inv_SetAgreesAll == ForAll(PSetAll)
\* the end's ack puts an act in the past of a removal that names the end, under full only: a removal of the
\* grantee's key then cuts the act under weak and not under full (the large run found it)
RECURSIVE AckCut(_, _)
AckCut(x, S) == KeyCutV(x, S, "full") # KeyCutV(x, S, "weak") \/ (x = "c1" /\ AckCut(SubOf, S))
PWeak(x, S, a, n) == (~Seen(x, S, "full") /\ ~PrevSticky(x) /\ ~WeakOther(S) /\ ~WithTie /\ ~AckCut(x, S)) =>
                       Ans(x, S, a, "full") = Ans(x, S, a, "weak")
Inv_WeakAgreesUnseen == ForAll(PWeak)
PWeakCnt(x, S, a, n) == (~PrevSticky(x) /\ ~WeakOther(S) /\ ~WithTie /\ ~AckCut(x, S)) =>
                          Ans(x, S, a, "full")[1] = Ans(x, S, a, "weak")[1]
Inv_WeakAgreesOnCount == ForAll(PWeakCnt)
PWeakSeen(x, S, a, n) == Ans(x, S, a, "full") = Ans(x, S, a, "weak")
Inv_WeakAgreesSeen == ForAll(PWeakSeen)
PWeakRe(x, S, a, n) == (~Seen(x, S, "full") /\ ~PrevSticky(x)) => Ans(x, S, a, "full") = Ans(x, S, a, "weak")
Inv_WeakAgreesReaccept == ForAll(PWeakRe)
\* TIE: an act bound to acc that names the end, while accD (another grantor's grant) still authorises it
PTie(x, S, a, n) == (EL(S, a) /\ x \in BIds /\ f[x].un = "acc" /\ "E" \in Anc(x))
                      => ~Ans(x, S, a, "full")[1]
Inv_EndReachesWhatNamesIt == ForAll(PTie)
=============================================================================
