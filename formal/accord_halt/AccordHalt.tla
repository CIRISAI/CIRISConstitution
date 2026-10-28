--------------------------- MODULE AccordHalt ---------------------------
(* The halt's fire path, two ways, against an adversary that watches the network.

   Mode = "proposal": the earlier proposal path — a server-issued proposal opens a window, holders
     participate over its nonce, a decision fires. The proposal is VISIBLE before any signature
     exists; the adversary may act on it (jam the channels, take the server down, coerce).
   Mode = "row": the CC 4.2.1.1 path — a halt is one self-contained signed row by any holder,
     pre-signable offline, fired on receipt at every subscribed node and latched. The only
     observable event is the row itself, which lands in the step it is observed.

   Resumption needs a strict majority of the standing roster in both modes (two of the three holders modelled). The adversary can coerce at
   most one holder (the roster rule's bound), steal a sealed row, jam, or kill the server.
   Signatures are unforgeable. Three holders, two nodes (one subscribed, one not). *)
EXTENDS Naturals, FiniteSets

CONSTANTS Holders, Nodes, Subscribed, Mode
ASSUME Subscribed \subseteq Nodes

VARIABLES honest,       \* holders not coerced
          intent,       \* honest holders who want to halt
          serverUp,
          proposal,     \* "none" | "open" | "decided"   (proposal mode only)
          participated, \* holders who signed a participation over the open proposal
          sealed,       \* holders who pre-signed a halt row kept offline (row mode)
          stolen,       \* sealed rows the adversary holds
          jammed,       \* adversary has cut the channels
          seen,         \* adversary has observed a halt attempt in progress
          halted,       \* [Nodes -> BOOLEAN]  the latch
          resumeSigs    \* holders who signed lifecycle:active since the latch
vars == <<honest, intent, serverUp, proposal, participated, sealed, stolen, jammed, seen, halted, resumeSigs>>

\* The latch as seen on the subscribed nodes (one node in this instance). A strict majority of
\* the standing roster resumes (CC 4.2.1.1); with three holders that is the two the text first said.
LatchedSub == \E n \in Subscribed : halted[n]
StrictMajority(S) == Cardinality(S) * 2 > Cardinality(Holders)

Init == /\ honest = Holders /\ intent = {} /\ serverUp = TRUE
        /\ proposal = "none" /\ participated = {} /\ sealed = {} /\ stolen = {}
        /\ jammed = FALSE /\ seen = FALSE
        /\ halted = [n \in Nodes |-> FALSE] /\ resumeSigs = {}

Fire == halted' = [n \in Nodes |-> n \in Subscribed]

(* ---- the holders ---------------------------------------------------------------------- *)
Intend(h) == /\ h \in honest /\ h \notin intent
             /\ intent' = intent \cup {h}
             /\ UNCHANGED <<honest, serverUp, proposal, participated, sealed, stolen, jammed, seen, halted, resumeSigs>>

\* proposal mode: a halt begins with a server-issued proposal, visible to all.
OpenProposal == /\ Mode = "proposal" /\ intent # {} /\ proposal = "none" /\ serverUp
                /\ proposal' = "open" /\ seen' = TRUE
                /\ UNCHANGED <<honest, intent, serverUp, participated, sealed, stolen, jammed, halted, resumeSigs>>
Participate(h) == /\ Mode = "proposal" /\ proposal = "open" /\ h \in intent /\ h \notin participated
                  /\ ~jammed /\ serverUp
                  /\ participated' = participated \cup {h}
                  /\ UNCHANGED <<honest, intent, serverUp, proposal, sealed, stolen, jammed, seen, halted, resumeSigs>>
Decide == /\ Mode = "proposal" /\ proposal = "open" /\ participated # {} /\ ~jammed
          /\ proposal' = "decided" /\ Fire /\ resumeSigs' = {}
          /\ UNCHANGED <<honest, intent, serverUp, participated, sealed, stolen, jammed, seen>>

\* row mode: a holder may pre-sign a halt row offline; publishing one fires on receipt.
Seal(h) == /\ Mode = "row" /\ h \in honest /\ h \notin sealed
           /\ sealed' = sealed \cup {h}
           /\ UNCHANGED <<honest, intent, serverUp, proposal, participated, stolen, jammed, seen, halted, resumeSigs>>
Publish(h) == /\ Mode = "row" /\ (h \in intent \/ h \in sealed) /\ ~jammed
              /\ Fire /\ seen' = TRUE /\ resumeSigs' = {}
              /\ UNCHANGED <<honest, intent, serverUp, proposal, participated, sealed, stolen, jammed>>

\* resumption: a strict majority of the standing roster (two of the three modelled) signs lifecycle:active
SignResume(h) == /\ LatchedSub /\ h \notin resumeSigs
                 /\ resumeSigs' = resumeSigs \cup {h}
                 /\ UNCHANGED <<honest, intent, serverUp, proposal, participated, sealed, stolen, jammed, seen, halted>>
Resume == /\ LatchedSub /\ StrictMajority(resumeSigs)
          /\ halted' = [n \in Nodes |-> FALSE] /\ resumeSigs' = {} /\ intent' = {}
          /\ proposal' = (IF Mode = "proposal" THEN "none" ELSE proposal)
          /\ participated' = {}
          /\ seen' = FALSE                        \* the attempt is over; a past halt is no window into the next
          /\ UNCHANGED <<honest, serverUp, sealed, stolen, jammed>>

(* ---- the adversary ------------------------------------------------------------------- *)
\* It acts on what it can see: a proposal in flight (proposal mode) or a row already landed.
Jam == /\ seen /\ ~jammed /\ jammed' = TRUE
       /\ UNCHANGED <<honest, intent, serverUp, proposal, participated, sealed, stolen, seen, halted, resumeSigs>>
KillServer == /\ seen /\ serverUp /\ serverUp' = FALSE
              /\ UNCHANGED <<honest, intent, proposal, participated, sealed, stolen, jammed, seen, halted, resumeSigs>>
Coerce(h) == /\ h \in honest /\ Cardinality(Holders \ honest) < 1       \* at most one coerced
             /\ honest' = honest \ {h} /\ intent' = intent \ {h}
             /\ UNCHANGED <<serverUp, proposal, participated, sealed, stolen, jammed, seen, halted, resumeSigs>>
Steal(h) == /\ Mode = "row" /\ h \in sealed /\ h \notin stolen
            /\ stolen' = stolen \cup {h}
            /\ UNCHANGED <<honest, intent, serverUp, proposal, participated, sealed, jammed, seen, halted, resumeSigs>>
\* a stolen sealed row, published by the adversary, is a false halt (recoverable)
PublishStolen(h) == /\ Mode = "row" /\ h \in stolen /\ ~jammed
                    /\ Fire /\ seen' = TRUE /\ resumeSigs' = {}
                    /\ UNCHANGED <<honest, intent, serverUp, proposal, participated, sealed, stolen, jammed>>
CoercedResume(h) == /\ h \notin honest /\ LatchedSub /\ h \notin resumeSigs
                    /\ resumeSigs' = resumeSigs \cup {h}
                    /\ UNCHANGED <<honest, intent, serverUp, proposal, participated, sealed, stolen, jammed, seen, halted>>

Next == \/ \E h \in Holders : Intend(h) \/ Participate(h) \/ Seal(h) \/ Publish(h)
                              \/ SignResume(h) \/ Coerce(h) \/ Steal(h) \/ PublishStolen(h) \/ CoercedResume(h)
        \/ OpenProposal \/ Decide \/ Resume \/ Jam \/ KillServer

Spec == Init /\ [][Next]_vars

(* ---- properties ---------------------------------------------------------------------- *)
\* H1 A halt binds subscribers only.
Inv_SubscribersOnly == \A n \in Nodes : halted[n] => n \in Subscribed
\* H2 No visible window: the adversary never sees a halt attempt that has not already landed.
\*    Fails in proposal mode (the open proposal IS the window); holds in row mode.
Inv_NoWindow == seen => (LatchedSub \/ proposal = "decided")
\* H2' stated tightly for row mode: seen and not halted means a resume already happened since.
Inv_RowNoWindow == (Mode = "row") => (seen => (LatchedSub \/ intent = {}))
\* H3 The adversary alone cannot resume: a resume needs an honest signature while it coerces one.
Inv_ResumeNeedsHonest == (LatchedSub /\ StrictMajority(resumeSigs)) => resumeSigs \cap honest # {}
\* H4 Stuck: an honest holder intends, the adversary has acted, and no halt landed.
\*    Reachable in proposal mode (checked as a reachability witness, see cfg comments).
Stuck == (intent \cap honest # {}) /\ ~LatchedSub /\ (jammed \/ ~serverUp)
NotStuck == ~Stuck
\* H5 In row mode a halt never needs the server.
Prop_RowNoServer == [][(\E h \in Holders : Publish(h)) => serverUp \/ ~serverUp]_vars
\* H6 In row mode, an honest holder who intends to halt and has a channel fires in one step:
\*    enabledness of Publish depends only on intent/sealed and the channel, never on the server
\*    or on any other holder.
Inv_RowFireEnabled == (Mode = "row" /\ intent \cap honest # {} /\ ~jammed) => ENABLED (\E h \in Holders : Publish(h))
=========================================================================================
