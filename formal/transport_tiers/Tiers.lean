/-!
# Tiers: what each traffic tier carries, and for whom

Three tiers: `base` (the slow shaped links of CC 5.4.3), `seat` (the fast shaped class between
two serve seats, CIRISConstitution#200), `bulk` (unshaped: chunked blobs, streams, calls).

The first half states the tiers as they stand: a link runs at the lower of two offers, the seat
rate needs a seat at both ends, and past eight links a shaping peer is refused for rows and
offered bulk.

The second half asks who may carry what. A node stands in one of three relations to a frame.
`endpoint`: it is one of the two parties. `offered`: it said yes to carrying (a contact that
offers relay, a serve seat, a tier relay that did not opt out). `stranger`: it said nothing.

Two rules are compared under one vocabulary.

* `currentAllows`: CC 5.4.6 today. Where no direct path exists a forwarder carries any link
  ciphertext, a room body or a stream included, and its only say is whether to forward at all.
* `proposedAllows`: a stranger carries only what is consent-free, and only on the base tier.

A payload is consent-free when it holds nothing a person wrote, names no third person, is of
bounded size and asks no custody. The theorems: everything a person needs in order to reach a
consent is consent-free, so the rule has no chicken-and-egg; a stranger under the proposed rule
carries nothing else; the current rule has a stranger carry a room body; and reading the rule
as "the base tier carries only this", endpoints included, takes contacts' own rows off shaping.
-/

/-! ## The tiers as they stand -/

inductive Tier | base | seat | bulk
  deriving DecidableEq, Repr

/-- Budget classes in order of rate, lowest first. -/
inductive Class | off | phoneCellular | phoneWifi | home | server
  deriving DecidableEq, Repr

def Class.rank : Class → Nat
  | .off => 0 | .phoneCellular => 1 | .phoneWifi => 2 | .home => 3 | .server => 4

/-- The byte budget per link (CC 5.4.3 table). -/
def Class.budget : Class → Nat
  | .off => 0 | .phoneCellular => 350 | .phoneWifi => 1400 | .home => 2800 | .server => 7000

/-- The real-frame share at ρ = 1/2. -/
def Class.realBytes (c : Class) : Nat := c.budget / 2

/-- A link runs at the lower of the two offers. -/
def negotiate (a b : Class) : Class := if a.rank ≤ b.rank then a else b

theorem negotiate_is_lower (a b : Class) :
    (negotiate a b).rank = min a.rank b.rank := by
  cases a <;> cases b <;> decide

/-- One end at `off` leaves the link unshaped: both directions or neither. -/
theorem off_at_either_end (a : Class) : negotiate a .off = .off := by
  cases a <;> decide

/-- Which tier a link runs on, given whether each end holds a serve seat and the offers. -/
def linkTier (seatA seatB : Bool) (a b : Class) : Tier :=
  if negotiate a b = .off then .bulk
  else if seatA && seatB then .seat
  else .base

theorem seat_needs_both (sa sb : Bool) (a b : Class) :
    linkTier sa sb a b = .seat → sa = true ∧ sb = true := by
  cases sa <;> cases sb <;> cases a <;> cases b <;> decide

/-- The bound: eight shaped links at the full class rate. -/
def bound : Nat := 8

inductive Admit | shapedRows | refusedOfferedBulk
  deriving DecidableEq, Repr

/-- A further shaping peer, with `held` shaped links already up and `reserve` held for layers.
    Seat links sit outside this count. -/
def admitShaping (held reserve : Nat) : Admit :=
  if held + reserve < bound then .shapedRows else .refusedOfferedBulk

theorem ninth_is_refused : admitShaping 8 0 = .refusedOfferedBulk := rfl
theorem eighth_is_admitted : admitShaping 7 0 = .shapedRows := rfl
theorem reserve_takes_slots : admitShaping 4 4 = .refusedOfferedBulk := rfl

/-! ## Who may carry what -/

inductive Carrier | endpoint | offered | stranger
  deriving DecidableEq, Repr

inductive Payload
  -- the hop's own machinery
  | cover | kex | routeFetch
  -- public, self-authenticating, about the signer alone
  | keyRecord | keyRevocation | occurrence | allegiance | unownedRoute
  -- asks and answers: sealed, one addressee, nothing typed
  | deviceJoin | contactAsk | contactAnswer | invite | inviteAnswer | groupKeyWrap
  -- safety rows every node must be able to pass on
  | halt | tombstone
  -- what a person or a room says
  | personRow | roomBody | smallImage | onionPacket
  -- the bulk plane
  | blob | media
  deriving DecidableEq, Repr

structure Traits where
  /-- holds words or pictures a person wrote -/
  authored : Bool
  /-- names a person other than the signer and the addressee -/
  namesOther : Bool
  /-- fixed, small size, so a carrier can check it without opening it -/
  bounded : Bool
  /-- asks someone to hold it past forwarding -/
  custody : Bool
  deriving DecidableEq, Repr

def traits : Payload → Traits
  | .cover | .kex | .routeFetch | .keyRecord | .keyRevocation | .occurrence
  | .allegiance | .unownedRoute | .deviceJoin | .contactAsk | .contactAnswer
  | .invite | .inviteAnswer | .groupKeyWrap | .halt | .tombstone =>
      ⟨false, false, true, false⟩
  | .personRow | .roomBody | .smallImage => ⟨true, true, false, true⟩
  | .onionPacket => ⟨true, false, true, false⟩
  | .blob | .media => ⟨true, true, false, true⟩

/-- No one is owed a consent to carry it. -/
def consentFree (p : Payload) : Bool :=
  let t := traits p
  !t.authored && !t.namesOther && t.bounded && !t.custody

/-- The bulk plane: never on a shaped link (CC 5.4.3, two planes). -/
def bulkOnly : Payload → Bool
  | .blob | .media => true
  | _ => false

/-- A shaped link never carries bulk; a bulk link carries nothing the row plane needs shaped
    for a stranger. A seat link is between seats, which have offered. -/
def planeFits (t : Tier) (p : Payload) : Bool :=
  match t with
  | .base | .seat => !bulkOnly p
  | .bulk => true

/-- CC 5.4.6 as it stands: where no direct path exists a forwarder carries link ciphertext, and
    it cannot tell a room body from a replication round. -/
def currentAllows (t : Tier) (c : Carrier) (p : Payload) : Bool :=
  match c with
  | .endpoint | .offered | .stranger => planeFits t p

/-- The proposed rule: a stranger carries what is consent-free, on the base tier, and nothing
    else. An endpoint or a carrier that said yes keeps what it has today. -/
def proposedAllows (t : Tier) (c : Carrier) (p : Payload) : Bool :=
  match c with
  | .endpoint | .offered => planeFits t p
  | .stranger => t == .base && consentFree p

/-- The strict reading: the base tier carries only the consent-free set, for everyone. -/
def strictAllows (t : Tier) (c : Carrier) (p : Payload) : Bool :=
  match t with
  | .base => consentFree p
  | _ => proposedAllows t c p

/-! ### The current state -/

/-- Today a stranger carries a room body and a call, neither of which is consent-free. -/
theorem current_stranger_carries_room_body :
    currentAllows .base .stranger .roomBody = true ∧ consentFree .roomBody = false := by
  decide

theorem current_stranger_carries_media :
    currentAllows .bulk .stranger .media = true ∧ consentFree .media = false := by
  decide

/-! ### The proposed rule -/

/-- A stranger carries only the consent-free set, and only on the base tier. -/
theorem stranger_only_consent_free (t : Tier) (p : Payload) :
    proposedAllows t .stranger p = true → t = .base ∧ consentFree p = true := by
  cases t <;> cases p <;> decide

/-- Bulk and seat traffic need a yes from whoever carries them. -/
theorem carrying_bulk_needs_a_yes (p : Payload) :
    proposedAllows .bulk .stranger p = false := by
  cases p <;> decide

theorem carrying_a_room_body_needs_a_yes :
    proposedAllows .base .stranger .roomBody = false ∧
    proposedAllows .base .offered .roomBody = true := by
  decide

/-- The rule takes nothing from the two people talking, or from a carrier that said yes. -/
theorem endpoints_keep_everything (t : Tier) (p : Payload) :
    currentAllows t .endpoint p = proposedAllows t .endpoint p ∧
    currentAllows t .offered p = proposedAllows t .offered p := by
  cases t <;> cases p <;> decide

/-- The new rule only ever narrows. -/
theorem proposed_narrows_current (t : Tier) (c : Carrier) (p : Payload) :
    proposedAllows t c p = true → currentAllows t c p = true := by
  cases t <;> cases c <;> cases p <;> decide

/-! ### No chicken-and-egg: every road to a consent is consent-free -/

def firstContact : List Payload :=
  [.routeFetch, .kex, .keyRecord, .occurrence, .allegiance, .contactAsk, .contactAnswer]

def addDevice : List Payload := [.kex, .keyRecord, .deviceJoin]

def joinRoom : List Payload := [.kex, .keyRecord, .invite, .inviteAnswer, .groupKeyWrap]

def stopEverything : List Payload := [.halt]

def revokeAKey : List Payload := [.keyRevocation, .tombstone]

def roads : List (List Payload) :=
  [firstContact, addDevice, joinRoom, stopEverything, revokeAKey]

/-- Strangers alone can carry every road to its end, on the base tier. -/
theorem every_road_runs_on_strangers :
    roads.all (fun r => r.all (proposedAllows .base .stranger)) = true := by
  decide

/-- Nor does any road ask for the bulk plane or the seat tier. -/
theorem every_road_is_consent_free :
    roads.all (fun r => r.all consentFree) = true := by
  decide

/-! ### The strict reading -/

/-- If the base tier carried only the consent-free set for everyone, two contacts' own message
    could not ride a shaped link at all. -/
theorem strict_takes_rows_off_shaping :
    strictAllows .base .endpoint .personRow = false ∧
    proposedAllows .base .endpoint .personRow = true := by
  decide

/-- Off the base tier a pair of ordinary peers has only the unshaped link, since they hold no
    seats: what shaping hid about their traffic is then visible on that link. -/
theorem ordinary_pair_has_no_seat_link (a b : Class) :
    linkTier false false a b ≠ .seat := by
  cases a <;> cases b <;> decide

/-! ### Reach on the base tier -/

/-- Peers at level `d` under `seats` canonicals: each canonical gives all `bound` links down,
    and every peer below gives seven, keeping one up. -/
def level (seats d : Nat) : Nat := seats * bound * 7 ^ d

def reach (seats d : Nat) : Nat := (List.range (d + 1)).foldr (fun i n => level seats i + n) 0

theorem reach_three_near_term : reach 3 3 = 9600 := by decide
theorem reach_nine_one_level : reach 9 1 = 576 := by decide
theorem reach_nine_four_levels : reach 9 4 = 201672 := by decide
theorem reach_nine_five_levels : reach 9 5 = 1411776 := by decide

/-- A row up to a canonical and down again crosses one more link than twice the level. -/
def hops (dA dB : Nat) : Nat := (dA + 1) + (dB + 1)

/-- Mean seconds on the wire at the Poisson timer's mean per hop (CC 5.4.3). -/
def meanWait (meanPerHop dA dB : Nat) : Nat := meanPerHop * hops dA dB

theorem home_four_levels_each_way : meanWait 4 4 4 = 40 := by decide
theorem wifi_four_levels_each_way : meanWait 8 4 4 = 80 := by decide

/-! ### Reach is not capacity

Everything that crosses between levels passes a canonical's links, so the canonicals' real-frame
share bounds the mesh-wide rate of routed asks. Flooding is worse: every node carries every ask,
so one peer's link rate bounds the whole mesh. -/

/-- Assumed size of a sealed ask with its key material (not pinned anywhere yet). -/
def askBytes : Nat := 8192

/-- Asks per second through `seats` canonicals, each with `bound` links at the server class. -/
def routedAsksPerSecond (seats : Nat) : Nat :=
  seats * bound * Class.server.realBytes / askBytes

theorem routed_three_canonicals : routedAsksPerSecond 3 = 10 := by decide
theorem routed_nine_canonicals : routedAsksPerSecond 9 = 30 := by decide

/-- Flooded, the whole mesh shares a home link: under one ask every five seconds. -/
theorem flooded_home_link : Class.home.realBytes * 5 / askBytes = 0 := by decide
theorem flooded_home_link_six_seconds : Class.home.realBytes * 6 / askBytes = 1 := by decide

/-- Seconds to copy every key record of `people` over one link, at `recordBytes` each. -/
def fullKeyCopySeconds (people recordBytes : Nat) (c : Class) : Nat :=
  people * recordBytes / c.realBytes

/-- Ten days at home rate for 200,000 people: the key plane cannot be pushed whole here. -/
theorem key_plane_whole_takes_ten_days :
    fullKeyCopySeconds 200000 6000 .home = 857142 := by decide
