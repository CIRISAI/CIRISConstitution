---------------------------- MODULE OnionLayers ----------------------------
(* CC 5.4.6 item 4 — the per-period onion layer deal, as coded in CIRISEdge
   src/transport/onion_layers.rs#deal_layers and witnessed there over the CSD/4 catalogue.

   Inputs are the fold: the set of relays that passed the five-leg membership predicate
   (`is_relay`), split into the seat-like (serve seats and steward-conferred infra:relay
   standings) and the others; the cap factor C; and the rank H(key_id ‖ period). H is a
   hash the model cannot compute, so it is left as ANY injective ranking: every property
   below holds for every possible hash and every period. Two nodes are modelled as two
   computations of the deal from the same fold; their equality is the checked statement
   of CLM-onion-layer-deal. A hostile subset of the others is chosen freely, so the
   hostile-share bound is checked against every adversary placement. *)
EXTENDS Naturals, Sequences, FiniteSets
CONSTANTS SeatLike, Others, C
Relays == SeatLike \cup Others
N == Cardinality(Relays)
Layers == 0..2
ASSUME SeatLike \cap Others = {} /\ C \in Nat /\ N >= 1

\* Every ordering of the relays: the hash, abstracted. Built recursively (N! sequences),
\* never by filtering the N^N functions.
RECURSIVE PermsOf(_)
PermsOf(S) == IF S = {} THEN {<< >>}
              ELSE UNION {{<<x>> \o p : p \in PermsOf(S \ {x})} : x \in S}
Rankings == PermsOf(Relays)
Pos(x, r) == CHOOSE i \in 1..Len(r) : r[i] = x
\* Seat-like first, then by rank (the Rust sort key (!seat_like, H, key_id)).
Key(x, r) == (IF x \in SeatLike THEN 0 ELSE N) + Pos(x, r)
\* Insertion sort by Key: with injective keys the result is the unique sorted order,
\* whatever order the set is walked in (the "two nodes, two arrival orders" case).
RECURSIVE Insert(_, _, _)
Insert(x, s, r) == IF Len(s) = 0 THEN <<x>>
                   ELSE IF Key(x, r) < Key(Head(s), r) THEN <<x>> \o s
                   ELSE <<Head(s)>> \o Insert(x, Tail(s), r)
RECURSIVE SortSet(_, _)
SortSet(S, r) == IF S = {} THEN << >>
                 ELSE LET x == CHOOSE x \in S : TRUE IN Insert(x, SortSet(S \ {x}, r), r)
Sorted(r) == SortSet(Relays, r)

Empty == [layers |-> [l \in Layers |-> << >>], seats |-> [l \in Layers |-> 0],
          non |-> [l \in Layers |-> 0], capped |-> {}]

\* The deal: one pass over the sorted sequence (seat-like come first, so this is the
\* Rust code's two passes), round-robin, the cap room checked from the next layer on.
RECURSIVE DealFrom(_, _, _, _)
DealFrom(s, i, st, nxt) ==
  IF i > Len(s) THEN st
  ELSE LET x == s[i] IN
    IF x \in SeatLike THEN
      DealFrom(s, i + 1, [st EXCEPT !.layers[nxt] = Append(@, x), !.seats[nxt] = @ + 1],
               (nxt + 1) % 3)
    ELSE LET room == {k \in 0..2 : st.non[(nxt + k) % 3] < C * st.seats[(nxt + k) % 3]} IN
      IF room = {} THEN DealFrom(s, i + 1, [st EXCEPT !.capped = @ \cup {x}], nxt)
      ELSE LET k == CHOOSE k \in room : \A k2 \in room : k <= k2
               l == (nxt + k) % 3 IN
        DealFrom(s, i + 1, [st EXCEPT !.layers[l] = Append(@, x), !.non[l] = @ + 1],
                 (l + 1) % 3)
Deal(r) == DealFrom(Sorted(r), 1, Empty, 0)
Members(d, l) == {d.layers[l][i] : i \in 1..Len(d.layers[l])}
Available(d) == \A l \in Layers : Len(d.layers[l]) >= 3

VARIABLES rank, hostile, viewA, viewB
vars == <<rank, hostile, viewA, viewB>>

Init == /\ rank \in Rankings
        /\ hostile \in SUBSET Others
        /\ viewA = Deal(rank)
        /\ viewB = Deal(rank)

\* A new period: a new rank; each node recomputes from the same fold. The adversary
\* may re-place itself among the others at any time.
NewPeriod == /\ rank' \in Rankings
             /\ viewA' = Deal(rank')
             /\ viewB' = Deal(rank')
             /\ UNCHANGED hostile
Replace == /\ hostile' \in SUBSET Others
           /\ UNCHANGED <<rank, viewA, viewB>>
Next == NewPeriod \/ Replace
Spec == Init /\ [][Next]_vars

\* CLM-onion-layer-deal: two nodes holding the same rows deal identical layers.
Inv_DealDeterministic == viewA = viewB

\* The cap, and what it buys: in every layer the others number at most C × seat-like, so
\* for ANY hostile placement among the others, hostile × (1 + C) ≤ C × layer size, i.e. the
\* hostile share of a layer is at most C / (1 + C).
Inv_HostileShareBound ==
  \A l \in Layers :
    /\ viewA.non[l] <= C * viewA.seats[l]
    /\ Cardinality(hostile \cap Members(viewA, l)) * (1 + C) <= C * Len(viewA.layers[l])

\* Never worse: every seat-like relay is dealt (none is capped), the seat-like are spread
\* evenly (layers differ by at most one), and every relay is dealt or capped, never lost.
Inv_NeverWorse ==
  /\ \A x \in SeatLike : \E l \in Layers : x \in Members(viewA, l)
  /\ \A l1, l2 \in Layers : viewA.seats[l1] <= viewA.seats[l2] + 1
  /\ (UNION {Members(viewA, l) : l \in Layers}) \cup viewA.capped = Relays
  /\ viewA.capped \subseteq Others

\* The floor is honest: the tier is available iff every layer has three members, and
\* availability needs a seat-like member in every layer (a layer with none has cap 0).
Prop_FloorHonest ==
  /\ Available(viewA) <=> (\A l \in Layers : Len(viewA.layers[l]) >= 3)
  /\ Available(viewA) => (\A l \in Layers : viewA.seats[l] >= 1)
  /\ Available(viewA) => Cardinality(SeatLike) >= 3
=============================================================================
