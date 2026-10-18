---------------------------- MODULE SelfRoster ----------------------------
(* Key states under one self: the devices that can sign for an identity, who holds each,
   and the policy under which one device may evict another or add a new one.

   The steward's invariant (2026-10-16): with three or more keypairs under a self, a stolen
   device cannot on its own kick the other devices off, yet two lost devices are recoverable
   from the one that remains. Possession and authentication are kept apart: a device is HELD
   by the owner, by a thief, or by nobody (lost); a holder can ACT on it only if they can
   authenticate on it (the owner always; a thief only when StolenAuth is TRUE, the worst case).
   Data at rest is not modelled; this is the policy layer only.

   Two paths, the steward's "quorum rules and reverse quorum applied to the self":
     the QUORUM path - a proposal approved by a strict majority of the roster lands at once;
     the LONE path   - a proposal by one device lands when its window closes unless a strict
                       majority of the OTHER members (target included) object -- the CC reverse
                       quorum (objection:{state}, CC 3.1.9.2) applied to the self -- AND, for an
                       eviction, only if the target was SILENT for the whole window: a device that
                       signed anything since the proposal is not lost, and is evictable only by
                       quorum. Votes from a key no longer on the roster are void.
   Three findings of earlier runs are now rules: without the silence rule a thief's lone
   eviction landed on a present owner whose devices had not yet objected when the window closed;
   an owner device proposing to evict another owner device gave a thief the vote it needed, so an
   owner proposes only against what it lost or had stolen; and an approval kept from a device
   evicted meanwhile made a thief's second eviction a majority of a smaller roster.
   Mode: "unilateral" (any authenticated member acts at once), "quorum" (quorum path only),
   "reverse" (lone path only), "combined" (both; the ruled shape).
   Adding a device goes through the same policy, or a thief would mint a majority.
   OwnerPresent: TRUE means the owner's devices act every tick (and so object to what they
   dislike); FALSE is the owner away for a whole window, the stated residual.
   Time is per proposal: a window is Window ticks of its own age; there is no global clock. *)
EXTENDS Naturals, FiniteSets

CONSTANTS Devices, Initial, Mode, Window, StolenAuth, MaxStolen, MaxLost, OwnerPresent
ASSUME Mode \in {"unilateral", "quorum", "reverse", "combined"}
ASSUME Initial \subseteq Devices

Holders == {"owner", "thief", "lost"}

VARIABLES member, holder, pending, acted, started, stolen, lostN, wrong
vars == <<member, holder, pending, acted, started, stolen, lostN, wrong>>

Spare == Devices \ member
Authenticated(d) == holder[d] = "owner" \/ (holder[d] = "thief" /\ StolenAuth)
OwnerHeld == {d \in member : holder[d] = "owner"}
ThiefHeld == {d \in member : holder[d] = "thief"}
LostHeld  == {d \in member : holder[d] = "lost"}
Majority(S, n) == Cardinality(S) * 2 > n

Init == /\ member = Initial /\ holder = [d \in Devices |-> "owner"]
        /\ pending = {} /\ acted = {} /\ started = FALSE
        /\ stolen = 0 /\ lostN = 0 /\ wrong = FALSE

(* ---- adversary: positions itself before the owner starts acting ---- *)
Steal(d) == /\ ~started /\ d \in member /\ holder[d] = "owner" /\ stolen < MaxStolen
            /\ holder' = [holder EXCEPT ![d] = "thief"] /\ stolen' = stolen + 1
            /\ UNCHANGED <<member, pending, acted, started, lostN, wrong>>
Lose(d)  == /\ ~started /\ d \in member /\ holder[d] = "owner" /\ lostN < MaxLost
            /\ holder' = [holder EXCEPT ![d] = "lost"] /\ lostN' = lostN + 1
            /\ UNCHANGED <<member, pending, acted, started, stolen, wrong>>

(* ---- what a device's holder wants ---- *)
Wants(d, p) == IF holder[d] = "owner"
                 THEN (p.kind = "evict" /\ holder[p.target] # "owner") \/ (p.kind = "add" /\ holder[p.by] = "owner")
                 ELSE (p.kind = "evict" /\ holder[p.target] = "owner") \/ (p.kind = "add" /\ holder[p.by] = "thief")

LiveVotes(S) == S \intersect member                        \* a vote from an evicted key is void
QuorumLands(p) == Majority(LiveVotes(p.approvers) \cup {p.by}, Cardinality(member))
LoneLands(p)   == /\ p.age >= Window
                  /\ ~Majority(LiveVotes(p.objectors), Cardinality(member \ {p.by}))
                  /\ (p.kind = "add" \/ ~p.spoke)         \* an evicted target was silent all window
Lands(p) == CASE Mode = "unilateral" -> TRUE
              [] Mode = "quorum"     -> QuorumLands(p)
              [] Mode = "reverse"    -> LoneLands(p)
              [] Mode = "combined"   -> QuorumLands(p) \/ LoneLands(p)

(* Any signed act by a device answers every pending proposal (approve what its holder wants,
   object to what they do not) and, if the device is itself a target, proves it is not lost. *)
Answered(d, P) == {[p EXCEPT !.approvers = IF d # p.by /\ Wants(d, p) THEN @ \cup {d} ELSE @,
                             !.objectors = IF d # p.by /\ ~Wants(d, p) THEN @ \cup {d} ELSE @,
                             !.spoke = @ \/ p.target = d] : p \in P}

Propose(kind, by, target) ==
    /\ by \in member /\ Authenticated(by)
    /\ IF kind = "evict" THEN target \in member /\ target # by ELSE target \in Spare
    /\ holder[by] = "owner" => (kind = "add" \/ holder[target] # "owner")   \* an owner evicts only what it lost or had stolen
    /\ ~\E p \in pending : p.kind = kind /\ p.target = target
    /\ ~\E p \in pending : p.by = by                                        \* one open proposal per proposer
    /\ pending' = Answered(by, pending) \cup {[kind |-> kind, target |-> target, by |-> by, age |-> 0,
                                               approvers |-> {}, objectors |-> {}, spoke |-> FALSE]}
    /\ acted' = acted \cup {by} /\ started' = TRUE
    /\ UNCHANGED <<member, holder, stolen, lostN, wrong>>

React(d) == /\ d \in member /\ Authenticated(d)
            /\ pending' = Answered(d, pending)
            /\ acted' = acted \cup {d}
            /\ UNCHANGED <<member, holder, started, stolen, lostN, wrong>>

Execute(p) == /\ p \in pending /\ Lands(p)
              /\ member' = IF p.kind = "evict" THEN member \ {p.target} ELSE member \cup {p.target}
              /\ holder' = IF p.kind = "evict" THEN holder ELSE [holder EXCEPT ![p.target] = holder[p.by]]
              /\ wrong'  = (wrong \/ (p.kind = "evict" /\ holder[p.by] = "thief" /\ holder[p.target] = "owner"))
              /\ pending' = {q \in pending : q # p /\ q.target # p.target /\ q.by # p.target}
              /\ UNCHANGED <<acted, started, stolen, lostN>>

(* A tick ages every open window. A present owner used every device during the tick. *)
Tick == /\ \E p \in pending : p.age < Window
        /\ OwnerPresent => OwnerHeld \subseteq acted
        /\ pending' = {[p EXCEPT !.age = IF @ < Window THEN @ + 1 ELSE @] : p \in pending}
        /\ acted' = {}
        /\ UNCHANGED <<member, holder, started, stolen, lostN, wrong>>

Honest == \/ \E by \in member, t \in Devices : Propose("evict", by, t) \/ Propose("add", by, t)
          \/ \E d \in Devices : React(d)
          \/ \E p \in pending : Execute(p)
Adversary == \E d \in Devices : Steal(d) \/ Lose(d)
Next == Honest \/ Adversary \/ Tick

OwnerStep == \/ \E by \in OwnerHeld, t \in Devices : Propose("evict", by, t) \/ Propose("add", by, t)
             \/ \E d \in OwnerHeld : React(d) /\ d \notin acted
             \/ \E p \in pending : Execute(p)
Spec == Init /\ [][Next]_vars /\ WF_vars(OwnerStep) /\ WF_vars(Tick)

-----------------------------------------------------------------------------
TypeOK == /\ member \subseteq Devices /\ holder \in [Devices -> Holders]
          /\ wrong \in BOOLEAN /\ acted \subseteq Devices /\ started \in BOOLEAN

(* First clause: a stolen device never evicts an owner-held device on its own. *)
Inv_ThiefCannotEvictHonest == ~wrong

(* The thief never assembles a majority of the roster while the owner still holds a device. *)
Inv_ThiefNeverMajority == OwnerHeld # {} => ~Majority(ThiefHeld, Cardinality(member))
(* The self survives: the owner never holds no key at all. Fails only where it must: one key, stolen
   (CC 3.3.6.3: at one key a theft is the loss of the self; the other properties are vacuous there). *)
Inv_SelfSurvives == OwnerHeld # {}

(* Second clause: from any device the owner still holds, every lost device and every stolen
   one eventually leaves the roster and the owner holds two devices again. *)
Recovered == LostHeld = {} /\ ThiefHeld = {} /\ Cardinality(OwnerHeld) >= 2
Prop_LostRecoverable == []( (OwnerHeld # {} /\ started) => <>Recovered )
(* Trace-witness helper, used only by dump_traces.py: checking this as an invariant makes TLC print
   the shortest behaviour that spends the whole adversary budget and still reaches Recovered: the landing
   trace persist replays. *)
Inv_NotRecovered == ~(Recovered /\ started /\ stolen = MaxStolen /\ lostN = MaxLost)
=============================================================================
