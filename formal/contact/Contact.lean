/-!
# Contact: what the relay learns when two peers become contacts

Two peers become contacts in three moves: a request, an acceptance, and, when both are
announced and behind NATs, a punch that brings their link direct. A relay (the canonical)
carries the request to a peer it can reach. The question is what the relay may hold and
serve, and what it learns.

Two designs are compared under one event vocabulary.

* `relayGated`: the contact grant crosses the relay as a plaintext federation row, the relay
  holds it, and the relay serves an owned node's route to a peer only when it holds the
  owner's grant naming that peer.
* `ownerHanded`: the request and the acceptance are sealed end to end; each carries its
  sender's own route; the relay forwards sealed bytes and serves no owned node's route to
  anyone.

A peer is `announced` (its owner binding is at federation scope; it has a signed route) or
`anonymous` (reached only at a published rendezvous; it has no route to hand and no address
to learn).

Theorems, in order: in both designs a route reaches a peer only from its owner and only to
a peer the owner addressed; an anonymous peer's route and address are never held by anyone;
a direct path forms only between two announced peers who both consented; under `ownerHanded`
the relay holds no pair record at all; under `relayGated` it holds both grants of every
pair whose consent crossed it, an anonymous peer's pseudonymous grant included; and both
designs complete the contact.
-/

inductive Design | relayGated | ownerHanded
deriving DecidableEq, Repr

/-- What a relay may come to hold. `linkAt` and `mailbox` are the ephemeral facts a
forwarder cannot avoid (a link crossed it; a packet reached a mailbox it keeps); `grant` is a
durable signed statement that one peer consented to another. -/
inductive Knowledge
  | linkAt (a b : Nat)     -- a link between a and b crossed the relay
  | mailbox (r : Nat)      -- a packet reached the rendezvous mailbox r
  | grant (a b : Nat)      -- a's signed grant naming b, held as a row
deriving DecidableEq, Repr

def Knowledge.isPairRecord : Knowledge → Bool
  | .grant _ _ => true
  | _ => false

inductive Event
  | request (a b : Nat)    -- a asks b for contact
  | accept (b a : Nat)     -- b accepts a's request
  | fetch (a b : Nat)      -- a asks the relay for b's route
  | punch (a b : Nat)      -- a and b bring their link direct
deriving DecidableEq, Repr

structure State where
  relay : List Knowledge          -- what the relay holds
  holds : List (Nat × Nat)        -- (x, y): x holds y's signed route
  consented : List (Nat × Nat)    -- (y, x): y's grant names x
  addr : List (Nat × Nat)         -- (x, y): x holds y's reflexive address
deriving Repr

structure World where
  anon : Nat → Bool

def State.empty : State := ⟨[], [], [], []⟩

/-- The relay's unavoidable fact about a delivery: a link, or a mailbox drop. -/
def carried (w : World) (a b : Nat) : Knowledge :=
  if w.anon b then .mailbox b else .linkAt a b

/-- A peer hands its route only if it has one: an anonymous peer hands nothing. -/
def hand (w : World) (owner to : Nat) (h : List (Nat × Nat)) : List (Nat × Nat) :=
  if w.anon owner then h else (to, owner) :: h

def step (d : Design) (w : World) (s : State) : Event → State
  | .request a b =>
    let relay := carried w a b :: (if d = .relayGated then .grant a b :: s.relay else s.relay)
    let holds := if d = .ownerHanded then hand w a b s.holds else s.holds
    { s with relay, holds, consented := (a, b) :: s.consented }
  | .accept b a =>
    if (a, b) ∈ s.consented then
      let relay := carried w b a :: (if d = .relayGated then .grant b a :: s.relay else s.relay)
      let holds := if d = .ownerHanded then hand w b a s.holds else s.holds
      { s with relay, holds, consented := (b, a) :: s.consented }
    else s
  | .fetch a b =>
    if d = .relayGated ∧ .grant b a ∈ s.relay then { s with holds := hand w b a s.holds } else s
  | .punch a b =>
    if ¬ w.anon a ∧ ¬ w.anon b ∧ (a, b) ∈ s.consented ∧ (b, a) ∈ s.consented
        ∧ (a, b) ∈ s.holds ∧ (b, a) ∈ s.holds then
      { s with addr := (a, b) :: (b, a) :: s.addr }
    else s

def run (d : Design) (w : World) (es : List Event) : State := es.foldl (step d w) State.empty

/-- x can reach y: it holds y's route, or y is anonymous and reached at its rendezvous. -/
def reaches (w : World) (s : State) (x y : Nat) : Bool := (x, y) ∈ s.holds || w.anon y

/-! ## The invariant every design keeps -/

structure Inv (w : World) (s : State) : Prop where
  routeFromOwner : ∀ x y, (x, y) ∈ s.holds → (y, x) ∈ s.consented
  anonHandsNothing : ∀ x y, (x, y) ∈ s.holds → w.anon y = false
  grantIsConsent : ∀ a b, Knowledge.grant a b ∈ s.relay → (a, b) ∈ s.consented
  addrMutual : ∀ x y, (x, y) ∈ s.addr →
    w.anon x = false ∧ w.anon y = false ∧ (x, y) ∈ s.consented ∧ (y, x) ∈ s.consented

theorem inv_empty (w : World) : Inv w State.empty := by
  constructor <;> intro _ _ h <;> simp_all [State.empty]

theorem inv_step (d : Design) (w : World) (s : State) (e : Event) (hi : Inv w s) :
    Inv w (step d w s e) := by
  obtain ⟨h1, h2, h3, h4⟩ := hi
  cases e with
  | request a b =>
    constructor
    · intro x y hx
      simp only [step] at hx ⊢
      split at hx
      · simp only [hand] at hx; split at hx
        · exact List.mem_cons_of_mem _ (h1 x y hx)
        · rcases List.mem_cons.mp hx with h | h
          · cases h; exact List.mem_cons.mpr (Or.inl rfl)
          · exact List.mem_cons_of_mem _ (h1 x y h)
      · exact List.mem_cons_of_mem _ (h1 x y hx)
    · intro x y hx
      simp only [step] at hx
      split at hx
      · simp only [hand] at hx; split at hx
        · exact h2 x y hx
        · rcases List.mem_cons.mp hx with h | h
          · cases h; simpa using ‹¬ w.anon a = true›
          · exact h2 x y h
      · exact h2 x y hx
    · intro a' b' hg
      simp only [step] at hg ⊢
      rcases List.mem_cons.mp hg with h | h
      · simp [carried] at h; split at h <;> simp_all
      · split at h
        · rcases List.mem_cons.mp h with h' | h'
          · cases h'; exact List.mem_cons.mpr (Or.inl rfl)
          · exact List.mem_cons_of_mem _ (h3 _ _ h')
        · exact List.mem_cons_of_mem _ (h3 _ _ h)
    · intro x y hx
      simp only [step] at hx ⊢
      obtain ⟨p, q, r, t⟩ := h4 x y hx
      exact ⟨p, q, List.mem_cons_of_mem _ r, List.mem_cons_of_mem _ t⟩
  | accept b a =>
    simp only [step]
    split
    · constructor
      · intro x y hx
        simp only at hx ⊢
        split at hx
        · simp only [hand] at hx; split at hx
          · exact List.mem_cons_of_mem _ (h1 x y hx)
          · rcases List.mem_cons.mp hx with h | h
            · cases h; exact List.mem_cons.mpr (Or.inl rfl)
            · exact List.mem_cons_of_mem _ (h1 x y h)
        · exact List.mem_cons_of_mem _ (h1 x y hx)
      · intro x y hx
        simp only at hx
        split at hx
        · simp only [hand] at hx; split at hx
          · exact h2 x y hx
          · rcases List.mem_cons.mp hx with h | h
            · cases h; simpa using ‹¬ w.anon b = true›
            · exact h2 x y h
        · exact h2 x y hx
      · intro a' b' hg
        simp only at hg ⊢
        rcases List.mem_cons.mp hg with h | h
        · simp [carried] at h; split at h <;> simp_all
        · split at h
          · rcases List.mem_cons.mp h with h' | h'
            · cases h'; exact List.mem_cons.mpr (Or.inl rfl)
            · exact List.mem_cons_of_mem _ (h3 _ _ h')
          · exact List.mem_cons_of_mem _ (h3 _ _ h)
      · intro x y hx
        simp only at hx ⊢
        obtain ⟨p, q, r, t⟩ := h4 x y hx
        exact ⟨p, q, List.mem_cons_of_mem _ r, List.mem_cons_of_mem _ t⟩
    · exact ⟨h1, h2, h3, h4⟩
  | fetch a b =>
    simp only [step]
    split
    · rename_i hg
      constructor
      · intro x y hx
        simp only [hand] at hx; split at hx
        · exact h1 x y hx
        · rcases List.mem_cons.mp hx with h | h
          · cases h; exact h3 _ _ hg.2
          · exact h1 x y h
      · intro x y hx
        simp only [hand] at hx; split at hx
        · exact h2 x y hx
        · rcases List.mem_cons.mp hx with h | h
          · cases h; simpa using ‹¬ w.anon b = true›
          · exact h2 x y h
      · exact h3
      · exact h4
    · exact ⟨h1, h2, h3, h4⟩
  | punch a b =>
    simp only [step]
    split
    · rename_i hp
      refine ⟨h1, h2, h3, ?_⟩
      intro x y hx
      simp only at hx
      rcases List.mem_cons.mp hx with h | h
      · cases h
        exact ⟨by simpa using hp.1, by simpa using hp.2.1, hp.2.2.1, hp.2.2.2.1⟩
      · rcases List.mem_cons.mp h with h' | h'
        · cases h'
          exact ⟨by simpa using hp.2.1, by simpa using hp.1, hp.2.2.2.1, hp.2.2.1⟩
        · exact h4 x y h'
    · exact ⟨h1, h2, h3, h4⟩

theorem inv_run (d : Design) (w : World) (es : List Event) : Inv w (run d w es) := by
  unfold run
  suffices h : ∀ s, Inv w s → Inv w (es.foldl (step d w) s) from h _ (inv_empty w)
  induction es with
  | nil => intro s hs; simpa using hs
  | cons e es ih => intro s hs; exact ih _ (inv_step d w s e hs)

/-- A route reaches a peer only from its owner, and only a peer the owner addressed. -/
theorem route_only_from_its_owner (d : Design) (w : World) (es : List Event) (x y : Nat)
    (h : (x, y) ∈ (run d w es).holds) : (y, x) ∈ (run d w es).consented :=
  (inv_run d w es).routeFromOwner x y h

/-- Nobody ever holds an anonymous peer's route. -/
theorem anonymous_route_never_held (d : Design) (w : World) (es : List Event) (x y : Nat)
    (h : (x, y) ∈ (run d w es).holds) : w.anon y = false :=
  (inv_run d w es).anonHandsNothing x y h

/-- A direct path forms only between two announced peers who both consented. -/
theorem direct_only_mutual_and_announced (d : Design) (w : World) (es : List Event) (x y : Nat)
    (h : (x, y) ∈ (run d w es).addr) :
    w.anon x = false ∧ w.anon y = false
      ∧ (x, y) ∈ (run d w es).consented ∧ (y, x) ∈ (run d w es).consented :=
  (inv_run d w es).addrMutual x y h

/-- Nobody ever holds an anonymous peer's address. -/
theorem anonymous_address_never_held (d : Design) (w : World) (es : List Event) (x y : Nat)
    (h : (x, y) ∈ (run d w es).addr) : w.anon y = false :=
  ((inv_run d w es).addrMutual x y h).2.1

/-! ## Where the designs part -/

/-- Under `ownerHanded` the relay never holds a pair record, whatever happens. -/
theorem owner_handed_relay_holds_no_pair (w : World) (es : List Event) :
    ∀ k ∈ (run .ownerHanded w es).relay, k.isPairRecord = false := by
  unfold run
  suffices h : ∀ s, (∀ k ∈ s.relay, k.isPairRecord = false) →
      ∀ k ∈ (es.foldl (step .ownerHanded w) s).relay, k.isPairRecord = false from
    h _ (by simp [State.empty])
  induction es with
  | nil => intro s hs; simpa using hs
  | cons e es ih =>
    intro s hs
    apply ih
    intro k hk
    cases e with
    | request a b =>
      simp only [step] at hk
      rcases List.mem_cons.mp hk with h | h
      · subst h; simp [carried]; split <;> rfl
      · simp at h; exact hs k h
    | accept b a =>
      simp only [step] at hk
      split at hk
      · rcases List.mem_cons.mp hk with h | h
        · subst h; simp [carried]; split <;> rfl
        · simp at h; exact hs k h
      · exact hs k hk
    | fetch a b => simp only [step] at hk; split at hk <;> exact hs k hk
    | punch a b => simp only [step] at hk; split at hk <;> exact hs k hk

/-! ## The worked contacts

Peers 1 and 2 are announced; peer 7 is anonymous. -/

def world : World := ⟨fun n => n == 7⟩

def twoAnnounced : List Event := [.request 1 2, .accept 2 1, .fetch 1 2, .fetch 2 1, .punch 1 2]
def oneAnonymous : List Event := [.request 7 2, .accept 2 7, .fetch 7 2, .fetch 2 7, .punch 7 2]

/-- Under `relayGated` the relay ends up holding both grants of the pair. -/
theorem relay_gated_holds_the_pair :
    Knowledge.grant 1 2 ∈ (run .relayGated world twoAnnounced).relay
      ∧ Knowledge.grant 2 1 ∈ (run .relayGated world twoAnnounced).relay := by decide

/-- Under `relayGated` the anonymous peer's pseudonymous grant sits at the relay too. -/
theorem relay_gated_learns_the_pseudonym_graph :
    Knowledge.grant 7 2 ∈ (run .relayGated world oneAnonymous).relay := by decide

/-- Under `ownerHanded` the relay holds the two unavoidable facts and nothing else. -/
theorem owner_handed_two_announced :
    (run .ownerHanded world twoAnnounced).relay = [.linkAt 2 1, .linkAt 1 2] := by decide

theorem owner_handed_one_anonymous :
    (run .ownerHanded world oneAnonymous).relay = [.mailbox 7, .linkAt 7 2] := by decide

/-- Both designs complete the contact: each side reaches the other, and the announced pair
goes direct. -/
def completes (d : Design) (es : List Event) (x y : Nat) : Bool :=
  reaches world (run d world es) x y && reaches world (run d world es) y x

theorem both_complete_two_announced :
    completes .relayGated twoAnnounced 1 2 ∧ completes .ownerHanded twoAnnounced 1 2
      ∧ (1, 2) ∈ (run .relayGated world twoAnnounced).addr
      ∧ (1, 2) ∈ (run .ownerHanded world twoAnnounced).addr := by decide

theorem both_complete_one_anonymous :
    completes .relayGated oneAnonymous 7 2 ∧ completes .ownerHanded oneAnonymous 7 2
      ∧ (run .relayGated world oneAnonymous).addr = []
      ∧ (run .ownerHanded world oneAnonymous).addr = [] := by decide

/-- Without the acceptance nothing moves: no route, no address, under either design. -/
def unanswered : List Event := [.request 1 2, .fetch 1 2, .fetch 2 1, .punch 1 2]

theorem no_consent_no_route :
    (run .relayGated world unanswered).holds = [(2, 1)]
      ∧ (run .ownerHanded world unanswered).holds = [(2, 1)]
      ∧ (run .relayGated world unanswered).addr = []
      ∧ (run .ownerHanded world unanswered).addr = [] := by decide
