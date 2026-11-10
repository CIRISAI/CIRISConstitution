/-!
# The member relay tree (CC 6.1.6), layered

CC 6.1.6 pins the tree as a contract: a pure, deterministic, integer-only function of the signed
snapshot (capacity ads clamped before scoring, trust, reachability, locality), the publisher the
stream key binding names at depth zero, forwarders and seats never in the tree. CC 5.3.3.2 gives
every sealed A/V chunk a clear layer header, so a member may ask for one layer.

This file states the tree and then the two additions the steward asked for (2026-11-08):

* **per-layer parents and sibling pull** — a member may take each layer from a different parent,
  and a chunk its parent did not deliver it pulls from a sibling, so a phone streams once through
  low-bandwidth peers that each carry a layer, and the stream reassembles where the layers meet;
* **the presence floor** — every codec class defines a floor layer small enough that budget ÷
  senders stays above it for the whole call, so nobody is ever excluded for bandwidth: quality
  falls, presence does not.

Two configurations are compared under one vocabulary: `today` (one parent, whole chunks, no pull)
and `layered` (per-layer parents, sibling pull, the floor). The structural theorems are proved on
a worked instance by `decide`; the quantitative ones are general. The companion
`alm_model.py` carries the same numbers to any input. Core Lean 4, no Mathlib.
-/

/-! ## The snapshot and the tree -/

/-- A signed capacity advertisement as the scorer sees it (CC 6.1.6 N8). -/
structure Ad where
  id : Nat
  uplink : Nat        -- self-asserted, clamped to `cap` before scoring
  verified : Bool     -- hybrid-verified by the scorer itself
  reachable : Bool    -- an ephemeral planner input, never attested
  seat : Bool         -- a serve seat or forwarder: never a member of the tree
  deriving DecidableEq, Repr

structure Snapshot where
  publisher : Nat     -- the key the stream binding names: the only member at depth zero
  cap : Nat           -- the pinned per-identity clamp
  fanout : Nat        -- children per parent (edge-internal; CC 6.1.6 pins no number)
  ads : List Ad
  deriving Repr

def Ad.score (cap : Nat) (a : Ad) : Nat := min a.uplink cap

/-- Who may be in the tree: verified, reachable, not a seat. -/
def candidates (s : Snapshot) : List Ad :=
  s.ads.filter (fun a => a.verified && a.reachable && !a.seat)

/-- The canonical order: score descending, then id ascending. Sorting first is what makes the
    tree a function of the snapshot and not of the order the ads arrived in. `a` comes before `b`
    when its clamped score is higher, or equal with the lower id. -/
def before (cap : Nat) (a b : Ad) : Bool :=
  a.score cap > b.score cap || (a.score cap = b.score cap && a.id ≤ b.id)

/-- Insertion sort, structurally recursive so that `decide` can run it. -/
def insertBy (cap : Nat) (a : Ad) : List Ad → List Ad
  | [] => [a]
  | b :: rest => if before cap a b then a :: b :: rest else b :: insertBy cap a rest

def sortBy (cap : Nat) : List Ad → List Ad
  | [] => []
  | a :: rest => insertBy cap a (sortBy cap rest)

def ordered (s : Snapshot) : List Ad := sortBy s.cap (candidates s)

structure Placed where
  id : Nat
  parent : Nat
  depth : Nat
  deriving DecidableEq, Repr

def childCount (pl : List Placed) (m : Nat) : Nat := (pl.filter (fun p => p.parent = m && p.id ≠ m)).length

/-- The tree: the publisher first at depth zero; every candidate, in canonical order, hangs
    under the earliest-placed member with a free slot. -/
def place (s : Snapshot) : List Placed :=
  (ordered s).foldl (fun pl a =>
    if a.id = s.publisher then pl else
    match pl.find? (fun p => childCount pl p.id < s.fanout) with
    | some p => pl ++ [⟨a.id, p.id, p.depth + 1⟩]
    | none => pl) [⟨s.publisher, s.publisher, 0⟩]

def parentOf (s : Snapshot) (m : Nat) : Option Nat :=
  (place s).find? (fun p => p.id = m) |>.map (·.parent)

def depthOf (s : Snapshot) (m : Nat) : Option Nat :=
  (place s).find? (fun p => p.id = m) |>.map (·.depth)

/-! ## A worked instance: a phone publishes to seven members and a seat -/

def ad (id uplink : Nat) (reachable : Bool := true) (seat : Bool := false) (verified : Bool := true) : Ad :=
  ⟨id, uplink, verified, reachable, seat⟩

/-- Alice's phone (id 1) publishes; Bob (2) and Carol (3) are homes; Dave (4), Erin (5), Frank (6),
    Grace (7) are phones, Frank on Wi-Fi with more uplink than the others; 9 is a serve seat; 8 is
    an unverified ad; the clamp is 10 and the fan-out 2, so the tree has depth. -/
def inst : Snapshot :=
  { publisher := 1, cap := 10, fanout := 2,
    ads := [ad 4 2, ad 2 50, ad 9 100 true true, ad 6 3, ad 3 40, ad 8 100 true false false, ad 5 2, ad 7 2, ad 1 1] }

/-- The same snapshot with the ads in another order. -/
def instShuffled : Snapshot := { inst with ads := inst.ads.reverse }

/-- Byte-equal inputs, byte-equal tree, whatever order the ads arrived in (CC 6.1.6). -/
theorem tree_permutation_invariant : place inst = place instShuffled := by decide

/-- Exactly one member sits at depth zero, and it is the publisher. -/
theorem publisher_is_the_only_root :
    (place inst).filter (fun p => p.depth = 0) = [⟨1, 1, 0⟩] := by decide

/-- The seat and the unverified ad are nowhere in the tree, as members or as parents. -/
theorem seats_and_unverified_outside :
    ((place inst).any (fun p => p.id = 9 || p.id = 8 || p.parent = 9 || p.parent = 8)) = false := by decide

/-- Every member but the publisher hangs one deeper than its parent: no cycles. -/
theorem child_one_deeper :
    ((place inst).all (fun c => c.id = 1 ||
      (place inst).any (fun p => p.id = c.parent && c.depth = p.depth + 1))) = true := by decide

/-- The clamp before scoring: an uplink of 50 and one of 40 score alike at cap 10, so Bob and
    Carol are ordered by id and neither buys the first slot with a number (N8). -/
theorem clamp_before_scoring : (ad 2 50).score 10 = (ad 3 40).score 10 := by decide

/-! ## Per-layer parents

A layer is a separate subscription. `placeLayer` scores by the uplink a member offers for that
layer (a home offers both, a phone offers only the base), so a member's parent may differ by
layer; the stream reassembles where a member holds every layer it asked for. -/

/-- A phone offers uplink for the base layer only; for an enhancement layer it offers none, so it
    sorts last and the homes become the parents; it still subscribes. -/
def offered (a : Ad) (layer : Nat) : Ad := if layer = 0 || a.uplink ≥ 10 then a else { a with uplink := 0 }

def layerSnapshot (s : Snapshot) (layer : Nat) : Snapshot :=
  { s with ads := s.ads.map (fun a => offered a layer) }

def parentIn (s : Snapshot) (layer m : Nat) : Option Nat := parentOf (layerSnapshot s layer) m

/-- Erin takes the base layer from Carol and the enhancement layer from Bob: two parents, and the
    stream reassembles at Erin where the layers meet. -/
theorem per_layer_parents_differ :
    parentIn inst 0 5 = some 3 ∧ parentIn inst 1 5 = some 2 := by decide

/-- A phone is never anyone's parent for the enhancement layer: it does not offer it. -/
theorem phones_carry_the_base_only :
    ((place (layerSnapshot inst 1)).all (fun p => p.parent = 1 || p.parent = 2 || p.parent = 3)) = true := by
  decide

/-! ## Sibling pull: completeness under loss

A push delivers a chunk from parent to child; a loss drops one delivery. Under `today` a member
holds only what its parent delivered. Under `layered` a round of pull lets a member take any chunk
a sibling (same parent) holds. Holdings are chunk lists per member. -/

structure Loss where
  member : Nat
  chunk : Nat
  deriving DecidableEq, Repr

def chunks : List Nat := [0, 1, 2, 3]

/-- What a member's parent pushed to it: every chunk the parent holds, less the losses. -/
def pushed (held : Nat → List Nat) (pl : List Placed) (losses : List Loss) (m : Nat) : List Nat :=
  match pl.find? (fun p => p.id = m) with
  | none => []
  | some p => if p.id = p.parent then held m else
      (held p.parent).filter (fun c => !(losses.contains ⟨m, c⟩))

/-- Push level by level: a member at depth d receives in round d. -/
def pushAll (s : Snapshot) (losses : List Loss) : Nat → List Nat
  | m =>
    let pl := place s
    let rec go (fuel : Nat) (held : Nat → List Nat) : Nat → List Nat :=
      match fuel with
      | 0 => held
      | fuel + 1 => go fuel (fun x => pushed held pl losses x)
    go 4 (fun x => if x = s.publisher then chunks else []) m

/-- One round of sibling pull: a member gains every chunk any sibling holds. -/
def pullRound (s : Snapshot) (held : Nat → List Nat) : Nat → List Nat
  | m =>
    let pl := place s
    match pl.find? (fun p => p.id = m) with
    | none => held m
    | some p =>
      let sibs := pl.filter (fun q => q.parent = p.parent && q.id ≠ m && q.id ≠ q.parent)
      chunks.filter (fun c => (held m).contains c || sibs.any (fun q => (held q.id).contains c))

/-- One chunk lost on the way to Dave, another on the way to Frank; both hang under Bob. -/
def losses : List Loss := [⟨4, 2⟩, ⟨6, 1⟩]

theorem dave_and_frank_are_siblings : parentOf inst 4 = some 2 ∧ parentOf inst 6 = some 2 := by decide

/-- Today: a lost chunk stays lost. -/
theorem today_loss_is_final :
    pushAll inst losses 4 = [0, 1, 3] ∧ pushAll inst losses 6 = [0, 2, 3] := by decide

/-- Layered: one round of sibling pull restores both. -/
theorem sibling_pull_completes :
    pullRound inst (pushAll inst losses) 4 = chunks ∧ pullRound inst (pushAll inst losses) 6 = chunks := by
  decide

/-! ## The quantitative side (general)

Loss compounds along a path of whole chunks; a refetch costs the loss rate in bytes; rateless
repair under the seal costs a fixed share. The presence floor keeps every sender live. -/

/-- End-to-end loss in permille along `d` hops at per-hop loss `p` permille. -/
def e2eLossPermille (p d : Nat) : Nat := (1000 ^ d - (1000 - p) ^ d) / 1000 ^ (d - 1)

theorem one_percent_five_hops : e2eLossPermille 10 5 = 49 := by decide
theorem three_percent_five_hops : e2eLossPermille 30 5 = 141 := by decide
theorem five_percent_five_hops : e2eLossPermille 50 5 = 226 := by decide
theorem ten_percent_eight_hops : e2eLossPermille 100 8 = 569 := by decide

/-- The fixed cost of rateless repair under the seal, in permille of the stream. -/
def ratelessOverheadPermille : Nat := 100

/-- Refetch is the cheaper repair at one percent per hop out to eight hops. -/
theorem refetch_cheaper_at_one_percent :
    (List.range 8).all (fun d => e2eLossPermille 10 (d + 1) < ratelessOverheadPermille) = true := by decide

/-- Rateless is the cheaper repair at five percent per hop from three hops on. -/
theorem rateless_cheaper_at_five_percent_past_two_hops :
    (List.range 6).all (fun d => e2eLossPermille 50 (d + 3) > ratelessOverheadPermille) = true := by decide

/-- A publisher's upload today at fan-out `k` against the stream rate; striped, once. -/
def uploadToday (fanout rate : Nat) : Nat := fanout * rate
def uploadStriped (rate : Nat) : Nat := rate

theorem striped_upload_is_once (fanout rate : Nat) (h : 1 ≤ fanout) :
    uploadStriped rate ≤ uploadToday fanout rate := by
  simp [uploadStriped, uploadToday]; exact Nat.le_mul_of_pos_left rate h

/-- How many senders stay live when each costs at least `floor` bytes per second of a `budget`. -/
def liveSenders (budget floor : Nat) : Nat := budget / floor

/-- The presence floor keeps everyone: `n` senders at the floor fit the budget, so all `n` are live. -/
theorem presence_floor_keeps_everyone (n budget floor : Nat) (hf : 0 < floor) (h : n * floor ≤ budget) :
    n ≤ liveSenders budget floor := by
  unfold liveSenders; exact (Nat.le_div_iff_mul_le hf).mpr h

/-- Ten thousand senders at a 32 B/s presence tile need 320 kB/s: a Wi-Fi or home link. -/
theorem ten_thousand_live_on_wifi : liveSenders 625000 32 = 19531 := by decide
theorem ten_thousand_do_not_fit_cellular : liveSenders 62500 32 = 1953 := by decide
theorem twelve_senders_today_on_cellular : liveSenders 62500 5000 = 12 := by decide

