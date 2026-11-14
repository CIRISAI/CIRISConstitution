------------------------------ MODULE KernelWorld ------------------------------
(* A world for the kernel: nodes that hold rows, and a schedule that is the adversary's.

   The kernel is one function. It takes the rows a node holds, each with the instant the node
   first held it, and gives what the node shows (a screen state of manifests/ui_primitives.json)
   and what it must do. This module puts that function in a world where any row may reach any
   node at any instant in any order, and asks what is true in every reachable state.

   The rows here are those of one blob under takedown (CC 4.5.3, CC 4.5.13):
     NW   a notice on a windowed basis      NI    a notice on an immediate basis
     Rev  a reversal                        Lift  the members' lift of a moderator's act
     Hold a legal hold                      HoldEnd  the hold lifted
   A node keeps no state but the rows and their first-held instants: destruction is read from
   them, so the record of an irreversible act is not a second store. *)
EXTENDS Integers, FiniteSets

CONSTANTS Nodes, Rows, T, W
VARIABLES now, held, seen

None == -1
Inf  == T + 10
Notices == Rows \cap {"NW", "NI"}
Undoers == Rows \cap {"Rev", "Lift"}

Has(n, r) == r \in Rows /\ held[n][r] # None
At(n, r)  == held[n][r]

UnderHold(n, t) == Has(n, "Hold") /\ At(n, "Hold") <= t
                   /\ (~Has(n, "HoldEnd") \/ t < At(n, "HoldEnd"))
HoldOver(n) == IF Has(n, "HoldEnd") THEN At(n, "HoldEnd") ELSE Inf

Undone(n, r) == r = "NW" /\ \E u \in Undoers :
                  Has(n, u) /\ At(n, u) < At(n, r) + W   \* held before the window closes, even before the notice
Natural(n, r) == IF r = "NI" THEN At(n, r) ELSE IF Undone(n, r) THEN Inf ELSE At(n, r) + W
DestroyAt(n, r) == LET d == Natural(n, r) IN
                   IF d = Inf THEN Inf ELSE IF UnderHold(n, d) THEN HoldOver(n) ELSE d

Destroyed(n) == \E r \in Notices : Has(n, r) /\ DestroyAt(n, r) <= now
Covered(n)   == ~Destroyed(n) /\ \E r \in Notices : Has(n, r) /\ ~Undone(n, r)
(* a reversal voids the notice whenever it is held, so the row regains its standing (CC 4.5.3) *)
Voided(n)    == \A r \in Notices : Has(n, r) => (r = "NW" /\ Has(n, "Rev"))

Screen(n) == IF Destroyed(n) THEN (IF Voided(n) THEN "not_on_this_node" ELSE "gone")
             ELSE IF Covered(n) THEN "withheld" ELSE "populated"

ScreenStates == {"populated", "withheld", "gone", "not_on_this_node"}

Init == now = 0 /\ held = [n \in Nodes |-> [r \in Rows |-> None]] /\ seen = {}
Deliver(n, r) == /\ held[n][r] = None
                 /\ (r = "HoldEnd" => TRUE)
                 /\ held' = [held EXCEPT ![n][r] = now]
                 /\ UNCHANGED now
                 /\ seen' = seen \cup {Screen(m) : m \in Nodes}
Tick == now < T /\ now' = now + 1 /\ UNCHANGED held /\ seen' = seen \cup {Screen(m) : m \in Nodes}
Next == Tick \/ \E n \in Nodes, r \in Rows : Deliver(n, r)
Spec == Init /\ [][Next]_<<now, held, seen>>

(* ---- what must hold in every reachable state ---- *)
Inv_Total == \A n \in Nodes : Screen(n) \in ScreenStates
(* the cover can always say on what ground, who acted and when the window closes *)
Inv_CoverHasNotice == \A n \in Nodes : Screen(n) = "withheld" => \E r \in Notices : Has(n, r)
(* a held blob is not destroyed while its hold is live *)
Inv_HoldKeeps == \A n \in Nodes : (UnderHold(n, now) /\ \A r \in Notices : Has(n, r) => At(n, r) >= At(n, "Hold"))
                                  => ~Destroyed(n)
(* an immediate notice is never shown: the instant it is held the blob is covered or gone *)
Inv_ImmediateNeverShown == \A n \in Nodes : Has(n, "NI") => Screen(n) # "populated"
(* the same rows first held at the same instants give the same screen *)
Inv_SameInputsSameScreen == \A m, n \in Nodes : held[m] = held[n] => Screen(m) = Screen(n)

(* ---- the question the world asks: do the same ROWS give the same standing? ---- *)
Settled == \A n \in Nodes, r \in Notices : Has(n, r) => At(n, r) + W <= now   \* every window has closed
SameRows(m, n) == \A r \in Rows : Has(m, r) <=> Has(n, r)
Stands(n) == Screen(n) \in {"populated", "not_on_this_node"}
Inv_SameRowsSameStanding == \A m, n \in Nodes : (Settled /\ SameRows(m, n)) => (Stands(m) <=> Stands(n))

(* every screen state is reached: the negation is checked and must fail *)
NotAllSeen == seen # ScreenStates
================================================================================
