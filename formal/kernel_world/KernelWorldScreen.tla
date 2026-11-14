---------------------------- MODULE KernelWorldScreen ----------------------------
(* The screen, in the same world as the kernel.

   A screen is a function of the node's answer, the reader's standing and the outcome of the
   read (manifests/ui_primitives.json). This module puts a screen on each node of the adversarial
   world: a read that may be idle, pending, failed or answered; the state the reader is shown;
   and one act the reader is offered, the objection that lifts a moderator's act (CC 4.5.13).
   The reader is a member seated before the act.

   The laws of the screen standard are stated as invariants and checked in every reachable
   state, together with the one that ties the screen to the kernel: what the screen offers is
   what the kernel would admit.

   Rows: NW, a windowed notice; Lift, the member's objection. Standing is judged at signed
   instants, trusted within the freshness bound F (KernelWorldSigned). *)
EXTENDS Integers

CONSTANTS Nodes, T, W, F, OfferBy, TrackSeen
VARIABLES now, stamp, real, held, read, seen

Rows == {"NW", "Lift"}
None == -1
vars == <<now, stamp, real, held, read, seen>>

Signed(r) == stamp[r] # None
Has(n, r) == held[n][r] # None
At(n, r)  == held[n][r]
Fresh(n, r) == Has(n, r) /\ At(n, r) - stamp[r] <= F
Lifted(n) == Has(n, "NW") /\ Fresh(n, "Lift") /\ stamp["Lift"] < stamp["NW"] + W
DestroyedHere(n) == /\ Has(n, "NW") /\ At(n, "NW") + W <= now
                    /\ ~(Lifted(n) /\ At(n, "Lift") < At(n, "NW") + W)

(* what the kernel concludes at a node *)
View(n) == IF ~Has(n, "NW") THEN "populated"
           ELSE IF Lifted(n) THEN (IF DestroyedHere(n) THEN "not_on_this_node" ELSE "populated")
           ELSE IF DestroyedHere(n) THEN "gone" ELSE "withheld"

(* what the reader is shown: the read's outcome first, then the kernel's conclusion *)
Screen(n) == CASE read[n] = "idle"    -> "idle"
               [] read[n] = "pending" -> "loading"
               [] read[n] = "failed"  -> "error"
               [] OTHER               -> View(n)
Answered == {"populated", "withheld", "gone", "not_on_this_node"}
States == Answered \cup {"idle", "loading", "error"}

(* the one act offered: object to the moderator's act *)
WindowOpen(n) == IF OfferBy = "signed" THEN now < stamp["NW"] + W      \* the instant every node reads the same
                 ELSE now < At(n, "NW") + W                            \* this node's own clock
Present(n)  == read[n] = "ok" /\ View(n) = "withheld"
Enabled(n)  == Present(n) /\ WindowOpen(n) /\ ~Signed("Lift")
Reason(n)   == IF ~WindowOpen(n) THEN "window_closed" ELSE IF Signed("Lift") THEN "already_objected" ELSE "none"
Offer(n)    == IF ~Present(n) THEN "absent" ELSE IF Enabled(n) THEN "enabled" ELSE Reason(n)   \* disabled, with its reason

Mark == IF TrackSeen THEN seen \cup {Screen(m) : m \in Nodes} \cup {Offer(m) : m \in Nodes} ELSE seen

Init == /\ now = 0 /\ stamp = [r \in Rows |-> None] /\ real = [r \in Rows |-> None]
        /\ held = [n \in Nodes |-> [r \in Rows |-> None]] /\ read = [n \in Nodes |-> "idle"] /\ seen = {}
SignNotice(s) == /\ ~Signed("NW") /\ s \in 0..now
                 /\ stamp' = [stamp EXCEPT !["NW"] = s] /\ real' = [real EXCEPT !["NW"] = now]
                 /\ UNCHANGED <<now, held, read>> /\ seen' = Mark
(* the reader takes the act the screen offers: the objection is signed now and held here *)
Take(n) == /\ Enabled(n)
           /\ stamp' = [stamp EXCEPT !["Lift"] = now] /\ real' = [real EXCEPT !["Lift"] = now]
           /\ held' = [held EXCEPT ![n]["Lift"] = now]
           /\ UNCHANGED <<now, read>> /\ seen' = Mark
Deliver(n, r) == /\ Signed(r) /\ ~Has(n, r) /\ held' = [held EXCEPT ![n][r] = now]
                 /\ UNCHANGED <<now, stamp, real, read>> /\ seen' = Mark
Ask(n)    == read[n] # "pending" /\ read' = [read EXCEPT ![n] = "pending"] /\ UNCHANGED <<now, stamp, real, held>> /\ seen' = Mark
Answer(n) == read[n] = "pending" /\ read' = [read EXCEPT ![n] = "ok"]      /\ UNCHANGED <<now, stamp, real, held>> /\ seen' = Mark
Fail(n)   == read[n] = "pending" /\ read' = [read EXCEPT ![n] = "failed"]  /\ UNCHANGED <<now, stamp, real, held>> /\ seen' = Mark
Tick == now < T /\ now' = now + 1 /\ UNCHANGED <<stamp, real, held, read>> /\ seen' = Mark
Next == \/ Tick \/ (\E s \in 0..T : SignNotice(s))
        \/ (\E n \in Nodes : Take(n) \/ Ask(n) \/ Answer(n) \/ Fail(n) \/ (\E r \in Rows : Deliver(n, r)))
Spec == Init /\ [][Next]_vars

(* ---- the laws of the screen standard ---- *)
(* L2: a state block is in exactly one of its declared states *)
Law_OneState == \A n \in Nodes : Screen(n) \in States
(* L3: an answer is drawn only when the node answered; an error only when the read failed *)
Law_HonestZero == \A n \in Nodes : /\ (Screen(n) \in Answered => read[n] = "ok")
                                   /\ (Screen(n) = "error" <=> read[n] = "failed")
                                   /\ (Screen(n) = "loading" <=> read[n] = "pending")
(* L5: an act that is present and disabled names its reason *)
Law_ReasonedRefusal == \A n \in Nodes : (Present(n) /\ ~Enabled(n)) => Reason(n) # "none"
(* a cover always has the notice behind it, so it can say on what ground, who acted and until when *)
Law_CoverHasNotice == \A n \in Nodes : Screen(n) = "withheld" => Has(n, "NW")
(* a node never shows as present what it destroyed *)
Law_DestroyedIsNeverShown == \A n \in Nodes : (read[n] = "ok" /\ DestroyedHere(n)) => Screen(n) \in {"gone", "not_on_this_node"}

(* ---- the law that ties the screen to the kernel ---- *)
(* what the screen offers, the kernel would admit: an objection taken now would count *)
Law_OfferedIsAdmitted == \A n \in Nodes : Enabled(n) => now < stamp["NW"] + W
(* and taking it has its effect at once at the node where it was taken *)
Law_TakenTakesEffect == \A n \in Nodes : (Has(n, "Lift") /\ At(n, "Lift") = real["Lift"] /\ Has(n, "NW") /\ read[n] = "ok")
                                           => Screen(n) \in {"populated", "not_on_this_node"}

(* L9: nothing declared is unreachable. The negation is checked and must fail. *)
All == States \cup {"absent", "enabled", "window_closed", "already_objected"}
NotAllSeen == seen # All
================================================================================
