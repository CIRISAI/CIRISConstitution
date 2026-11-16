--------------------------- MODULE AccordBundle ---------------------------
(* The accord's roster as a lineage of genesis bundles (CC 2.6.1.11, CC 4.2.6, CC 5.3.4).

   A roster change is a later bundle. It names the bundle in force as prev and counts at a strict
   majority of the predecessor's holders, plus each holder it adds and each holder whose recovery
   commitment it changes. Each holder's statement over the bundle is its proof of life and its yes.

   A recovery is a later bundle signed by the recovering holder's recovery key ALONE. It is the one
   exception to the count. The key must be the one the commitment in force commits to (CC 3.2 T3).
   It changes that holder's signing key and next recovery commitment, and nothing else. The next
   commitment differs from the one it spends, and a spent commitment never returns: every commitment
   a recovery has used is spent along the whole lineage. A recovery key never becomes a seat's key.

   A commitment is identified with the recovery key it commits to (the hash is injective), so
   `com[s] = r` reads "the commitment in force for s commits to r".

   The world: holders A, B, C at the genesis; D may be added; A may recover (its signing keys A0, A1,
   A2 and recovery keys RA0, RA1, RA2); B may re-commit (RB0 to RB1). Any holder signs anything; the
   reader's rule is what is checked. The adversary may steal A's signing key in force, and may steal a
   recovery key once a recovery has spent it. It seats its own key, "Xs" when it used a signing key
   and "Xp" when it used a spent recovery key.

   Planted breaks are constants; each twin configuration turns one on and fails its own invariant. *)
EXTENDS Naturals, FiniteSets

CONSTANTS MaxVer,
          NoCount,          \* a change counts on any one predecessor holder
          OtherSeat,        \* a recovery may change another seat too
          SpentReturns,     \* the next commitment need only differ from the one spent
          RecKeyAsSeat,     \* a recovery may name a recovery key as the new signing key
          AnyKeyRecovers,   \* a recovery is accepted under any key, the commitment unchecked
          SpentKeyRecovers, \* a recovery is accepted under any commitment ever named for the seat
          RotateNoVoice,    \* a roster change re-seats a holder at a new key without that holder's statement
          SeatRetired       \* a bundle seats a holder at a key its lineage retired, or at its in-force recovery key

Seats   == {"A", "B", "C", "D"}
ASign   == {"A0", "A1", "A2"}
ARec    == {"RA0", "RA1", "RA2"}
RecKeys == ARec \cup {"RB0", "RB1", "RC0", "RD0"}
NONE    == "none"

VARIABLES key,    \* [Seats -> signing key | NONE]: the holders of the bundle in force and their keys
          com,    \* [Seats -> recovery key committed to | NONE]
          spent,  \* the commitments a counted recovery has used, along the lineage
          named,  \* every commitment any bundle of the lineage has named for A
          ver,    \* the version of the bundle in force
          adv,    \* the keys the adversary holds
          last,   \* the last counted bundle, read by the invariants
          left    \* every key a holder was seated at and left: with spent, the lineage's retired keys
vars == <<key, com, spent, named, ver, adv, last, left>>

Holders(k) == {s \in Seats : k[s] # NONE}
CurKeys(k) == {k[s] : s \in Holders(k)}

Init == /\ key = [s \in Seats |-> CASE s = "A" -> "A0" [] s = "B" -> "B0" [] s = "C" -> "C0" [] OTHER -> NONE]
        /\ com = [s \in Seats |-> CASE s = "A" -> "RA0" [] s = "B" -> "RB0" [] s = "C" -> "RC0" [] OTHER -> NONE]
        /\ spent = {} /\ named = {"RA0"} /\ ver = 1 /\ adv = {} /\ left = {}
        /\ last = [kind |-> "genesis", S |-> {}, pk |-> key, pc |-> com, nk |-> key, nc |-> com,
                   rk |-> NONE, spentBefore |-> {}]

Land(kind, S, nk, nc, rk, sp2) ==
  /\ key' = nk /\ com' = nc /\ spent' = sp2 /\ ver' = ver + 1
  /\ named' = named \cup {nc["A"]}
  /\ left' = left \cup {key[s] : s \in {x \in Seats : key[x] # NONE /\ nk[x] # NONE /\ nk[x] # key[x]}}
  /\ last' = [kind |-> kind, S |-> S, pk |-> key, pc |-> com, nk |-> nk, nc |-> nc,
              rk |-> rk, spentBefore |-> spent]
  /\ UNCHANGED adv

\* a holder re-seated at a new key: the key may not be one the lineage retired, nor the in-force recovery key
Moved(nk) == {s \in Seats : key[s] # NONE /\ nk[s] # NONE /\ nk[s] # key[s]}
NotRetired(nk) == \A s \in Moved(nk) : (nk[s] \notin left \cup spent /\ nk[s] # com[s]) \/ SeatRetired

(* ---- a roster change: a later bundle counted at a strict majority of the predecessor ---------- *)
Added(nk) == {s \in Seats : key[s] = NONE /\ nk[s] # NONE}
Recommitted(nk, nc) == {s \in Seats : key[s] # NONE /\ nk[s] # NONE /\ nc[s] # com[s]}

ChangeCounts(nk, nc, S) ==
  /\ (Cardinality(S \cap CurKeys(key)) * 2 > Cardinality(Holders(key)) \/ (NoCount /\ S \cap CurKeys(key) # {}))
  /\ \A s \in Added(nk) \cup Recommitted(nk, nc) : nk[s] \in S
  /\ \A s \in Seats : nc[s] \notin spent
  /\ NotRetired(nk)
  /\ \A s \in Moved(nk) : key[s] \in S \/ RotateNoVoice     \* routine rotation: the holder's own voice, current key

\* the shapes a change takes here: add D, remove C, re-commit B, and the adversary's seat for A
ChangeTo(op) ==
  CASE op = "addD"      -> <<[key EXCEPT !["D"] = "D0"], [com EXCEPT !["D"] = "RD0"]>>
    [] op = "removeC"   -> <<[key EXCEPT !["C"] = NONE], [com EXCEPT !["C"] = NONE]>>
    [] op = "recommitB" -> <<key, [com EXCEPT !["B"] = "RB1"]>>
    [] op = "seatX"     -> <<[key EXCEPT !["A"] = "Xs"], com>>
    [] op = "rotA0"     -> <<[key EXCEPT !["A"] = "A0"], com>>
    [] op = "rotA1"     -> <<[key EXCEPT !["A"] = "A1"], com>>
    [] op = "rotRA"     -> <<[key EXCEPT !["A"] = com["A"]], com>>

Signable == CurKeys(key) \cup {"D0"} \cup adv
Change(op, S) ==
  LET nk == ChangeTo(op)[1]  nc == ChangeTo(op)[2] IN
  /\ ver < MaxVer
  /\ nk # key \/ nc # com
  /\ S \subseteq (IF op = "seatX" THEN adv ELSE Signable)
  /\ (op \in {"seatX", "rotA0", "rotA1", "rotRA"} => key["A"] # NONE)
  /\ ChangeCounts(nk, nc, S)
  /\ Land("change", S, nk, nc, NONE, spent)

(* ---- a recovery: the recovery key alone, one seat ------------------------------------------- *)
RecoveryCounts(rk, nk, nc, other) ==
  /\ \/ rk = com["A"]
     \/ AnyKeyRecovers
     \/ (SpentKeyRecovers /\ rk \in named)
  /\ ~other \/ OtherSeat
  /\ nk # key["A"] /\ nk # rk
  /\ nk \notin left \/ SeatRetired
  /\ nk \notin RecKeys \/ RecKeyAsSeat
  /\ nc # com["A"] /\ nc # rk
  /\ nc \notin spent \/ SpentReturns

\* an honest recovery by A, or any shape presented under a recovery key A holds
Recover(rk, nk, nc, other) ==
  LET k2 == [key EXCEPT !["A"] = nk]
      c2 == IF other THEN [com EXCEPT !["A"] = nc, !["B"] = "RB1"] ELSE [com EXCEPT !["A"] = nc] IN
  /\ ver < MaxVer /\ key["A"] # NONE
  /\ RecoveryCounts(rk, nk, nc, other)
  /\ Land("recovery", {rk}, k2, c2, rk, spent \cup {com["A"]})

HonestRecover == \E rk \in ARec, nk \in ASign \cup ARec, nc \in ARec, other \in BOOLEAN :
                   Recover(rk, nk, nc, other)
AdvRecover == \E rk \in adv, nc \in ARec :
                Recover(rk, IF rk \in ASign THEN "Xs" ELSE "Xp", nc, FALSE)

(* ---- the adversary ---------------------------------------------------------------------- *)
StealSign == /\ key["A"] \in ASign /\ key["A"] \notin adv
             /\ adv' = adv \cup {key["A"]} /\ UNCHANGED <<key, com, spent, named, ver, last, left>>
StealSpent == \E r \in spent : /\ r \notin adv
                               /\ adv' = adv \cup {r} /\ UNCHANGED <<key, com, spent, named, ver, last, left>>

Next == \/ \E op \in {"addD", "removeC", "recommitB", "seatX", "rotA0", "rotA1", "rotRA"}, S \in SUBSET Signable : Change(op, S)
        \/ HonestRecover \/ AdvRecover \/ StealSign \/ StealSpent
Spec == Init /\ [][Next]_vars

(* ---- invariants ---------------------------------------------------------------------------- *)
TypeOK == /\ key \in [Seats -> ASign \cup ARec \cup {"B0", "C0", "D0", "Xs", "Xp", NONE}]
          /\ com \in [Seats -> RecKeys \cup {NONE}]

\* B1 No change without the count: a strict majority of the predecessor's holders, and every holder
\*    it adds or re-commits, signed it.
PrevHolders == {s \in Seats : last.pk[s] # NONE}
Inv_ChangeCounted ==
  last.kind = "change" =>
    /\ Cardinality(last.S \cap {last.pk[s] : s \in PrevHolders}) * 2 > Cardinality(PrevHolders)
    /\ \A s \in Seats : (last.pk[s] = NONE /\ last.nk[s] # NONE) => last.nk[s] \in last.S
    /\ \A s \in PrevHolders : (last.nk[s] # NONE /\ last.nc[s] # last.pc[s]) => last.nk[s] \in last.S

\* B2 A recovery changes only its own seat, under the one key the commitment in force commits to.
Inv_RecoveryOwnSeat ==
  last.kind = "recovery" =>
    /\ \A s \in Seats \ {"A"} : last.nk[s] = last.pk[s] /\ last.nc[s] = last.pc[s]
    /\ last.S = {last.rk} /\ last.rk = last.pc["A"]

\* B3 A spent commitment is never accepted again, across any sequence of bundles: none is in force,
\*    and no counted recovery used one.
Inv_SpentNeverReturns ==
  /\ \A s \in Seats : com[s] \notin spent
  /\ last.kind = "recovery" => last.rk \notin last.spentBefore

\* B4 The recovery key never becomes a seat's key.
Inv_RecKeyNeverSeat == \A s \in Seats : key[s] \notin RecKeys

\* B5 An adversary holding a holder's signing key cannot recover that seat without its recovery key.
Inv_SignKeyCannotRecover == \A s \in Seats : key[s] # "Xs"

\* B6 An adversary holding a spent recovery key gains nothing.
Inv_SpentKeyGainsNothing == \A s \in Seats : key[s] # "Xp"

\* B7 A roster change re-seats a holder at a new key only with that holder's statement under its current key.
Inv_RotationConsented ==
  last.kind = "change" =>
    \A s \in Seats : (last.pk[s] # NONE /\ last.nk[s] # NONE /\ last.nk[s] # last.pk[s]) => last.pk[s] \in last.S

\* B8 No bundle seats a holder at a key its lineage retired (a key it left, or a spent recovery key), nor at its
\*    in-force recovery key.
Inv_NoRetiredSeat == \A s \in Seats : key[s] \notin left \cup spent

\* Witnesses that the paths are reached, each checked to FAIL: a holder recovers twice, a holder is
\* added, a re-commitment lands, and the adversary holds a spent recovery key.
NotRecoveredTwice == Cardinality(spent) < 2
NotRotated == ~(last.kind = "change" /\ last.pk["A"] # NONE /\ last.nk["A"] # NONE /\ last.nk["A"] # last.pk["A"])
NotAdded == key["D"] = NONE
NotRecommitted == com["B"] = "RB0"
NoSpentKeyStolen == adv \cap ARec = {}
=============================================================================
