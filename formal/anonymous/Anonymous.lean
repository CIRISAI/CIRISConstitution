/-!
# Anonymous participation: what an anonymous identity can do, what links it to a person,
# and what still stops abuse

CC 5.4.6 item 1 (rc17): using the Anonymous Tier and being anonymous are one thing, a mode of a
node. An anonymous node is a separate dedicated identity, announces nothing, publishes at
federation scope through the tier under fresh pseudonyms, is reached only at its rendezvous, is
anonymous from its first run or never, and joins rooms only once rooms ride the tier.

The model is a trace of events over a small world of persons, nodes, pseudonyms, rooms and
readers. Each event has a guard (the text's rule) and an effect (the rows it writes). A trace is
run by applying every event whose guard holds and dropping the rest, so every theorem is about
every trace, including adversarial ones.

Proved: an anonymous node never announces and nobody ever holds its route or address; no row links
an anonymous identity to an announced one except the person's own proof under both keys; an
anonymous node is in a room only when rooms ride the tier; a pseudonym holds no duty, no seat
and no vote, so pseudonyms are free to mint and worth nothing to mint; the admission gates, a
reader's block and a moderator's tombstone act on a pseudonym's rows exactly as on anyone's; a
relay on a route learns one neighbour, and the mailbox seat learns a count.
-/

inductive Kind | announced | anonymous
  deriving DecidableEq, Repr

structure Node where
  id : Nat
  owner : Nat          -- the person
  kind : Kind
  deriving DecidableEq, Repr

/-- A publication key of an anonymous node: fresh per item, no occurrence, no standing. -/
structure Pseud where
  id : Nat
  node : Nat
  deriving DecidableEq, Repr

/-- Who signs a row. -/
inductive Signer
  | node (n : Nat)
  | pseud (p : Nat)
  deriving DecidableEq, Repr

inductive Row
  | announce (n : Nat)                         -- owner binding at federation scope
  | route (holder n : Nat)                     -- holder holds n's signed route
  | contact (a b : Nat)                        -- a direct link between two nodes
  | member (n room : Nat) (viaTier : Bool)     -- n sits in room, over the tier or not
  | publication (by_ : Signer) (item : Nat) (prohibited : Bool)
  | link (anon ann : Nat) (bothSigned : Bool)  -- a row saying anon and ann are one person
  | duty (holder : Signer) (room : Nat)        -- moderate / takedown / review
  | vote (by_ : Signer) (room : Nat)
  | seat (n : Nat)                             -- a serve seat
  | block (reader : Nat) (who : Signer)        -- reader-side, private
  | tombstone (item : Nat)                     -- a moderator's takedown by digest
  deriving DecidableEq, Repr

structure World where
  nodes : List Node
  pseuds : List Pseud
  roomsRideTheTier : Bool
  /-- whether an anonymous identity (a node, never a pseudonym) may hold a duty -/
  anonDuty : Bool
  /-- the public rooms: open admission at the Commons tier -/
  publicRooms : List Nat := []
  deriving Repr

def World.kindOf (w : World) (n : Nat) : Option Kind :=
  (w.nodes.find? (fun x => x.id = n)).map (·.kind)

def World.isAnnouncedNode (w : World) (n : Nat) : Bool := w.kindOf n = some .announced
def World.isAnonNode (w : World) (n : Nat) : Bool := w.kindOf n = some .anonymous
def World.pseudOf (w : World) (p : Nat) : Option Nat :=
  (w.pseuds.find? (fun x => x.id = p)).map (·.node)

inductive Event
  | announce (n : Nat)
  | fetchRoute (holder n : Nat)
  | directContact (a b : Nat)
  | joinRoom (n room : Nat) (viaTier : Bool)
  | publishAsNode (n item : Nat) (prohibited : Bool)
  | publishViaTier (p item : Nat) (prohibited : Bool)
  | prove (anon ann : Nat)                     -- the person's own act under both keys
  | forgeLink (anon ann : Nat)                 -- anyone's attempt to assert the link
  | appoint (holder : Signer) (room : Nat)
  | castVote (by_ : Signer) (room : Nat)
  | confer (n : Nat)
  | blockSigner (reader : Nat) (who : Signer)
  | takedown (item : Nat)
  deriving DecidableEq, Repr

abbrev State := List Row

def announced (s : State) (n : Nat) : Prop := Row.announce n ∈ s
instance (s : State) (n : Nat) : Decidable (announced s n) := inferInstanceAs (Decidable (_ ∈ _))

def memberOf (s : State) (n room : Nat) : Prop := ∃ via, Row.member n room via ∈ s
instance (s : State) (n room : Nat) : Decidable (memberOf s n room) :=
  if h : Row.member n room true ∈ s ∨ Row.member n room false ∈ s then
    isTrue (by rcases h with h | h <;> exact ⟨_, h⟩)
  else isFalse (by rintro ⟨via, hv⟩; cases via <;> exact h (by simp [hv]))

/-- The guard of each event: the text's rule. -/
def ok (w : World) (s : State) : Event → Bool
  | .announce n => w.isAnnouncedNode n                     -- an anonymous node never announces
  | .fetchRoute _ n => decide (announced s n)              -- a route is served only for an announced node
  | .directContact a b => decide (announced s a) && decide (announced s b)  -- item 10
  | .joinRoom n room viaTier =>
      if w.publicRooms.contains room then decide (announced s n)  -- a public room admits announced keys only
      else if w.isAnonNode n then viaTier && w.roomsRideTheTier  -- rooms only once they ride the tier
      else true
  | .publishAsNode n _ _ => w.isAnnouncedNode n            -- an anonymous node publishes only via the tier
  | .publishViaTier p _ _ =>
      match w.pseudOf p with
      | some n => w.isAnonNode n                           -- a pseudonym belongs to an anonymous node
      | none => false
  | .prove anon ann => w.isAnonNode anon && w.isAnnouncedNode ann
  | .forgeLink _ _ => true                                 -- anyone may try
  | .appoint holder room =>
      match holder with
      | .pseud _ => false                                  -- a pseudonym has no standing
      | .node n => decide (memberOf s n room) &&
          (w.isAnnouncedNode n || (w.anonDuty && w.isAnonNode n))  -- a member; anonymous only if allowed
  | .castVote by_ room =>
      match by_ with
      | .pseud _ => false                                  -- a pseudonym is not a member
      | .node n => decide (memberOf s n room)
  | .confer n => w.isAnnouncedNode n                       -- a seat has an announced owner
  | .blockSigner _ _ => true
  | .takedown _ => true

/-- The admission gate every publication meets, blind to who signed it. -/
def admits (prohibited : Bool) : Bool := !prohibited

/-- The one row an event writes, if any. -/
def added : Event → Option Row
  | .announce n => some (.announce n)
  | .fetchRoute h n => some (.route h n)
  | .directContact a b => some (.contact a b)
  | .joinRoom n room via => some (.member n room via)
  | .publishAsNode n item pr => if admits pr then some (.publication (.node n) item pr) else none
  | .publishViaTier p item pr => if admits pr then some (.publication (.pseud p) item pr) else none
  | .prove anon ann => some (.link anon ann true)
  | .forgeLink anon ann => some (.link anon ann false)   -- lands signed by one key only
  | .appoint h room => some (.duty h room)
  | .castVote b room => some (.vote b room)
  | .confer n => some (.seat n)
  | .blockSigner r who => some (.block r who)
  | .takedown item => some (.tombstone item)

def effect (s : State) (e : Event) : State := (added e).toList ++ s

def step (w : World) (s : State) (e : Event) : State :=
  if ok w s e then effect s e else s

def run (w : World) (es : List Event) : State := es.foldl (step w) []

/-! ## The invariant, by induction over every trace -/

theorem inv_run (w : World) (P : State → Prop) (h0 : P [])
    (hstep : ∀ s e, P s → ok w s e = true → P (effect s e)) :
    ∀ es, P (run w es) := by
  intro es
  suffices h : ∀ s, P s → P (es.foldl (step w) s) from h [] h0
  induction es with
  | nil => intro s hs; exact hs
  | cons e es ih =>
    intro s hs
    simp only [List.foldl]
    apply ih
    unfold step
    split
    · exact hstep s e hs (by assumption)
    · exact hs

/-- Everything the text promises about anonymous participation, as one invariant. -/
structure Inv (w : World) (s : State) : Prop where
  announce_is_announced : ∀ m, Row.announce m ∈ s → w.isAnnouncedNode m = true
  route_is_announced : ∀ h n, Row.route h n ∈ s → w.isAnnouncedNode n = true
  contact_is_announced : ∀ a b, Row.contact a b ∈ s → w.isAnnouncedNode a = true ∧ w.isAnnouncedNode b = true
  anon_room_via_tier : ∀ n room via, w.isAnonNode n = true → Row.member n room via ∈ s →
      via = true ∧ w.roomsRideTheTier = true
  link_is_proof : ∀ a b, Row.link a b true ∈ s → w.isAnonNode a = true ∧ w.isAnnouncedNode b = true
  pseud_no_duty : ∀ p room, Row.duty (.pseud p) room ∈ s → False
  pseud_no_vote : ∀ p room, Row.vote (.pseud p) room ∈ s → False
  seat_is_announced : ∀ n, Row.seat n ∈ s → w.isAnnouncedNode n = true
  duty_holder : ∀ n room, Row.duty (.node n) room ∈ s →
      memberOf s n room ∧ (w.isAnnouncedNode n = true ∨ (w.anonDuty = true ∧ w.isAnonNode n = true))
  public_is_announced : ∀ n room via, w.publicRooms.contains room = true →
      Row.member n room via ∈ s → w.isAnnouncedNode n = true

theorem kind_exclusive (w : World) (n : Nat) :
    w.isAnonNode n = true → w.isAnnouncedNode n = true → False := by
  simp only [World.isAnonNode, World.isAnnouncedNode]
  intro h1 h2
  rw [decide_eq_true_iff] at h1 h2
  rw [h1] at h2; cases h2

theorem inv_holds (w : World) (es : List Event) : Inv w (run w es) := by
  apply inv_run
  · exact Inv.mk (fun _ h => nomatch h) (fun _ _ h => nomatch h) (fun _ _ h => nomatch h)
      (fun _ _ _ _ h => nomatch h) (fun _ _ h => nomatch h) (fun _ _ h => nomatch h)
      (fun _ _ h => nomatch h) (fun _ h => nomatch h) (fun _ _ h => nomatch h)
      (fun _ _ _ _ h => nomatch h)
  · intro s e hP hok
    obtain ⟨h1, h2, h3, h4, h5, h6, h7, h8, h9, h10⟩ := hP
    -- membership only grows
    have memGrow : ∀ n room, memberOf s n room → memberOf (effect s e) n room := by
      intro n room ⟨via, hv⟩; exact ⟨via, by simp [effect, hv]⟩
    -- the row the event writes, if any
    have key : ∀ r, r ∈ effect s e → r ∈ s ∨ added e = some r := by
      intro r hr
      simp only [effect, List.mem_append] at hr
      rcases hr with hr | hr
      · right; cases h : added e <;> simp [h] at hr; exact hr ▸ rfl
      · left; exact hr
    refine Inv.mk (fun m hm => ?_) (fun h n hm => ?_) (fun a b hm => ?_)
      (fun n room via hanon hm => ?_) (fun a b hm => ?_) (fun p room hm => ?_)
      (fun p room hm => ?_) (fun n hm => ?_) (fun n room hm => ?_) (fun n room via hpub hm => ?_)
    all_goals rcases key _ hm with h | h
    -- old rows: the hypothesis
    all_goals first
      | exact h1 _ h
      | exact h2 _ _ h
      | exact h3 _ _ h
      | exact h4 _ _ _ hanon h
      | exact h5 _ _ h
      | exact h6 _ _ h
      | exact h7 _ _ h
      | exact h8 _ h
      | exact ⟨memGrow _ _ (h9 _ _ h).1, (h9 _ _ h).2⟩
      | exact h10 _ _ _ hpub h
      | skip
    -- the new row: by the guard
    all_goals cases e <;> simp only [added] at h
    all_goals first
      | (split at h <;> cases h)
      | skip
    all_goals (try cases h)
    all_goals first
      | (simp [ok] at hok; exact hok)
      | skip
    all_goals first
      | (simp only [ok, decide_eq_true_eq] at hok; exact h1 _ hok)
      | (simp only [ok, Bool.and_eq_true, decide_eq_true_eq] at hok; exact ⟨h1 _ hok.1, h1 _ hok.2⟩)
      | (simp only [ok] at hok
         split at hok
         all_goals first
           | exact (kind_exclusive w _ hanon (h1 _ (by simpa using hok))).elim
           | (rw [if_pos hanon] at hok; simpa using hok)
           | (rcases hok with h' | h'
              · rw [hanon] at h'; cases h'
              · exact h')
           | simpa [hanon] using hok)
      | (simp only [ok] at hok
         split at hok
         all_goals first
           | exact h1 _ (by simpa using hok)
           | exact absurd (by simpa using hpub : room ∈ w.publicRooms) ‹_›)
      | (simp only [ok, Bool.and_eq_true, decide_eq_true_eq] at hok
         exact ⟨memGrow _ _ hok.1, by simpa [Bool.or_eq_true, Bool.and_eq_true] using hok.2⟩)
      | simp [ok] at hok

/-! ### Corollaries, in the text's words -/

/-- An anonymous node never announces. -/
theorem anon_never_announced (w : World) (es : List Event) (n : Nat)
    (hn : w.isAnonNode n = true) : Row.announce n ∉ run w es := fun h =>
  kind_exclusive w n hn ((inv_holds w es).announce_is_announced n h)

/-- Nobody ever holds an anonymous node's route. -/
theorem anon_route_never_held (w : World) (es : List Event) (h n : Nat)
    (hn : w.isAnonNode n = true) : Row.route h n ∉ run w es := fun hm =>
  kind_exclusive w n hn ((inv_holds w es).route_is_announced h n hm)

/-- An anonymous node is never in a direct contact (item 10). -/
theorem anon_never_direct (w : World) (es : List Event) (a b : Nat)
    (ha : w.isAnonNode a = true) : Row.contact a b ∉ run w es := fun hm =>
  kind_exclusive w a ha ((inv_holds w es).contact_is_announced a b hm).1

/-- Until rooms ride the tier, an anonymous node is in no room at all. -/
theorem anon_in_no_room_until_then (w : World) (es : List Event) (n room : Nat) (via : Bool)
    (hw : w.roomsRideTheTier = false) (hn : w.isAnonNode n = true) :
    Row.member n room via ∉ run w es := fun hm => by
  have := ((inv_holds w es).anon_room_via_tier n room via hn hm).2
  rw [hw] at this; cases this

/-- Once rooms ride the tier, an anonymous node's room membership is always over the tier. -/
theorem anon_room_always_via_tier (w : World) (es : List Event) (n room : Nat)
    (hn : w.isAnonNode n = true) : Row.member n room false ∉ run w es := fun hm => by
  have := ((inv_holds w es).anon_room_via_tier n room false hn hm).1
  cases this

/-- No row links an anonymous identity to a person but the person's own proof under both keys:
    a both-signed link names an anonymous node and an announced one, and only `prove` writes it. -/
theorem link_only_by_proof (w : World) (es : List Event) (a b : Nat) :
    Row.link a b true ∈ run w es → w.isAnonNode a = true ∧ w.isAnnouncedNode b = true :=
  (inv_holds w es).link_is_proof a b

theorem forged_link_is_one_signature (w : World) (s : State) (a b : Nat) :
    step w s (.forgeLink a b) = .link a b false :: s := by
  simp [step, ok, effect, added]

/-- A pseudonym holds no duty and casts no vote: free to mint, worth nothing to mint. -/
theorem pseud_holds_nothing (w : World) (es : List Event) (p room : Nat) :
    Row.duty (.pseud p) room ∉ run w es ∧ Row.vote (.pseud p) room ∉ run w es :=
  ⟨(inv_holds w es).pseud_no_duty p room, (inv_holds w es).pseud_no_vote p room⟩

/-- A seat belongs to an announced node, never an anonymous one. -/
theorem seat_never_anonymous (w : World) (es : List Event) (n : Nat)
    (hn : w.isAnonNode n = true) : Row.seat n ∉ run w es := fun hm =>
  kind_exclusive w n hn ((inv_holds w es).seat_is_announced n hm)

/-! ### Abuse controls are blind to who signed -/

/-- The admission gate refuses prohibited content from a pseudonym as from a node. -/
theorem gate_blind_to_signer (w : World) (s : State) (p n item : Nat) :
    step w s (.publishViaTier p item true) = s ∧ step w s (.publishAsNode n item true) = s := by
  constructor <;> simp [step, effect, added, admits]

/-- What a reader sees of a signer's item: nothing after a block, nothing tombstoned. -/
def visible (s : State) (reader : Nat) (by_ : Signer) (item : Nat) : Prop :=
  Row.publication by_ item false ∈ s ∧ Row.block reader by_ ∉ s ∧ Row.tombstone item ∉ s

theorem block_hides_pseudonym (s : State) (reader p item : Nat) :
    ¬ visible (.block reader (.pseud p) :: s) reader (.pseud p) item := by
  intro ⟨_, hb, _⟩; exact hb (List.mem_cons_self _ _)

theorem tombstone_hides_item (s : State) (reader : Nat) (by_ : Signer) (item : Nat) :
    ¬ visible (.tombstone item :: s) reader by_ item := by
  intro ⟨_, _, ht⟩; exact ht (List.mem_cons_self _ _)

/-! ### What a relay learns -/

/-- A hop sees the one before and the one after, never both ends. -/
def learns (route : List Nat) (i : Nat) : List Nat :=
  (route.get? (i - 1)).toList ++ (route.get? (i + 1)).toList

theorem no_hop_sees_both_ends (pub h1 h2 h3 store : Nat) :
    (learns [pub, h1, h2, h3, store] 1 = [pub, h2]) ∧
    (learns [pub, h1, h2, h3, store] 2 = [h1, h3]) ∧
    (learns [pub, h1, h2, h3, store] 3 = [h2, store]) := by
  simp [learns]

/-- The mailbox seat learns a count of packets per period for one rendezvous (item 8). -/
def mailboxLearns (packets : List Nat) : Nat := packets.length

/-! ### Can anonymous participants form a room at all?

CC 4.5.4: a community operates only while at least one member holds the live `moderate` duty.
A room whose every member is anonymous therefore operates only if an anonymous identity may hold
the duty. -/

def allAnonymous (w : World) (s : State) (room : Nat) : Prop :=
  ∀ n via, Row.member n room via ∈ s → w.isAnonNode n = true

/-- The existence gate of CC 4.5.4: some member holds the duty. -/
def operates (s : State) (room : Nat) : Prop := ∃ h, Row.duty h room ∈ s

/-- Without anonymous duty holders, a room of anonymous members never operates, on any trace:
    its only candidates are its members, all anonymous, and a pseudonym holds nothing. -/
theorem all_anonymous_room_needs_anonymous_moderator (w : World) (es : List Event) (room : Nat)
    (hno : w.anonDuty = false) (hall : allAnonymous w (run w es) room) :
    ¬ operates (run w es) room := by
  rintro ⟨h, hd⟩
  have inv := inv_holds w es
  cases h with
  | pseud p => exact inv.pseud_no_duty p room hd
  | node n =>
    obtain ⟨⟨via, hv⟩, hk⟩ := inv.duty_holder n room hd
    have hanon := hall n via hv
    rcases hk with hann | ⟨hd', _⟩
    · exact kind_exclusive w n hanon hann
    · rw [hno] at hd'; cases hd'

/-- With anonymous duty holders allowed and rooms riding the tier, a room of one anonymous
    member can be founded and operates: the founder appoints itself, as any founder does. -/
def wAnon : World :=
  { nodes := [⟨1, 10, .anonymous⟩], pseuds := [], roomsRideTheTier := true, anonDuty := true }

theorem anonymous_room_operates :
    operates (run wAnon [.joinRoom 1 7 true, .appoint (.node 1) 7]) 7 := by
  refine ⟨.node 1, ?_⟩
  decide

/-- And the holder of that duty is a persistent anonymous identity, never a pseudonym; so it
    can be blocked, its actions contested, its duty revoked by the room, exactly as any holder. -/
theorem anonymous_moderator_is_an_identity (w : World) (es : List Event) (room : Nat)
    (h : operates (run w es) room) : ∃ n, Row.duty (.node n) room ∈ run w es := by
  obtain ⟨holder, hd⟩ := h
  cases holder with
  | pseud p => exact absurd hd ((inv_holds w es).pseud_no_duty p room)
  | node n => exact ⟨n, hd⟩

/-- No unannounced identity, anonymous or merely unannounced, ever sits in a public room. -/
theorem public_room_needs_announce (w : World) (es : List Event) (n room : Nat) (via : Bool)
    (hpub : w.publicRooms.contains room = true) (hn : w.isAnonNode n = true) :
    Row.member n room via ∉ run w es := fun hm =>
  kind_exclusive w n hn ((inv_holds w es).public_is_announced n room via hpub hm)

/-! ### No ungoverned room: a lapse is answered by the room's own appointment

CC 4.5.4 rule 2: when the holder of `moderate` lapses, the member with the best standing is
appointed by the room's own act, deterministically. Here the candidate is the member with the
lowest key id who may hold the duty (announced, or anonymous where the world allows it) and is
not the one who lapsed; the real rule orders by track record first, which the model abstracts. -/

def mayHold (w : World) (n : Nat) : Bool :=
  w.isAnnouncedNode n || (w.anonDuty && w.isAnonNode n)

/-- The members of a room, as node ids, from the rows held. -/
def membersOf (s : State) (room : Nat) : List Nat :=
  s.filterMap (fun r => match r with
    | .member n rm _ => if rm = room then some n else none
    | _ => none)

/-- The proper candidates after `lost` lapsed: members who may hold the duty, `lost` excluded. -/
def candidates (w : World) (s : State) (room lost : Nat) : List Nat :=
  (membersOf s room).filter (fun n => mayHold w n && n != lost)

def pick (w : World) (s : State) (room lost : Nat) : Option Nat :=
  (candidates w s room lost).min?

/-- The lapse of a duty holder, answered in the same step by the room's appointment of the pick. -/
def lapse (w : World) (s : State) (room lost : Nat) : State :=
  let s' := s.filter (fun r => r != .duty (.node lost) room)
  match pick w s room lost with
  | some n => .duty (.node n) room :: s'
  | none => s'

/-- A room whose holder lapses is never left ungoverned while a proper candidate exists. -/
theorem lapse_never_leaves_a_gap (w : World) (s : State) (room lost : Nat)
    (h : pick w s room lost = some n) : operates (lapse w s room lost) room := by
  refine ⟨.node n, ?_⟩
  simp [lapse, h]

/-- And the appointee is a proper candidate: a member who may hold the duty, not the one lost. -/
theorem pick_is_candidate (w : World) (s : State) (room lost n : Nat)
    (h : pick w s room lost = some n) : n ∈ candidates w s room lost :=
  List.min?_mem (fun a b => by rw [Nat.min_def]; split <;> simp) h

/-- Only when no proper candidate exists does the room fall to the 48 h recovery of CC 4.5.13. -/
theorem gap_only_without_candidate (w : World) (s : State) (room lost : Nat)
    (hno : ∀ h, Row.duty h room ∈ s → h = .node lost) (h : pick w s room lost = none) :
    ¬ operates (lapse w s room lost) room := by
  rintro ⟨hd, hm⟩
  simp only [lapse, h] at hm
  have := List.mem_filter.mp hm
  have heq := hno hd this.1
  subst heq
  simp at this
