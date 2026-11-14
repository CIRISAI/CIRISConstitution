--------------------------- MODULE KernelWorldSigned ---------------------------
(* The same world, with the instant a row is signed kept apart from the instant a node holds it.

   KernelWorld showed two nodes that hold the same rows and differ in standing for good, because
   a lift was judged against each node's own clock. Here standing is judged at signed instants,
   which every node reads the same, and a signed instant is trusted only when the row was first
   held within the freshness bound F of it. A node's own clock decides only when the node
   destroys the bytes it holds.

   A signer may date a row earlier than it is signed. The schedule is free: any signed row may
   reach any node at any later instant. Rows: NW, a windowed notice; Lift, the members' lift. *)
EXTENDS Integers

CONSTANTS Nodes, T, W, F
VARIABLES now, stamp, real, held

Rows == {"NW", "Lift"}
None == -1

Signed(r) == stamp[r] # None
Has(n, r) == held[n][r] # None
At(n, r)  == held[n][r]

(* a row's signed instant is trusted at a node only if the node held it within F of that instant *)
Fresh(n, r) == Has(n, r) /\ At(n, r) - stamp[r] <= F
(* the lift counts when it is dated inside the act's window, on signed instants alone *)
Lifted(n) == Has(n, "NW") /\ Fresh(n, "Lift") /\ stamp["Lift"] < stamp["NW"] + W

(* the node's own clock: it destroyed the bytes if no counted lift was held when its window closed *)
DestroyedHere(n) == /\ Has(n, "NW") /\ At(n, "NW") + W <= now
                    /\ ~(Lifted(n) /\ At(n, "Lift") < At(n, "NW") + W)

Screen(n) == IF ~Has(n, "NW") THEN "populated"
             ELSE IF Lifted(n) THEN (IF DestroyedHere(n) THEN "not_on_this_node" ELSE "populated")
             ELSE IF DestroyedHere(n) THEN "gone" ELSE "withheld"
ScreenStates == {"populated", "withheld", "gone", "not_on_this_node"}

Init == /\ now = 0 /\ stamp = [r \in Rows |-> None] /\ real = [r \in Rows |-> None]
        /\ held = [n \in Nodes |-> [r \in Rows |-> None]]
Sign(r, s) == /\ ~Signed(r) /\ s \in 0..now          \* dated now or earlier
              /\ stamp' = [stamp EXCEPT ![r] = s] /\ real' = [real EXCEPT ![r] = now]
              /\ UNCHANGED <<now, held>>
Deliver(n, r) == /\ Signed(r) /\ ~Has(n, r)
                 /\ held' = [held EXCEPT ![n][r] = now] /\ UNCHANGED <<now, stamp, real>>
Tick == now < T /\ now' = now + 1 /\ UNCHANGED <<stamp, real, held>>
Next == Tick \/ (\E r \in Rows, s \in 0..T : Sign(r, s)) \/ (\E n \in Nodes, r \in Rows : Deliver(n, r))
Spec == Init /\ [][Next]_<<now, stamp, real, held>>

Inv_Total == \A n \in Nodes : Screen(n) \in ScreenStates

(* the same rows give the same standing, at every instant and not only once windows close *)
SameRows(m, n) == \A r \in Rows : Has(m, r) <=> Has(n, r)
Inv_SameRowsSameStanding == \A m, n \in Nodes : SameRows(m, n) => (Lifted(m) <=> Lifted(n))

(* a lift signed more than F after the instant it claims counts at no node *)
Inv_BackdatingIsBounded == \A n \in Nodes : Lifted(n) => real["Lift"] - stamp["Lift"] <= F

(* a node never shows as present what it destroyed *)
Inv_DestroyedIsNeverShown == \A n \in Nodes : DestroyedHere(n) => Screen(n) \in {"gone", "not_on_this_node"}
================================================================================
