/-!
# The life of an event: view, queue, row, view

CC 4.5.13 (rc17): an epistemic web client renders two served shapes, the view (an object's rows and
the atoms folded from them) and the queue (the items awaiting the person's hand). This model says
how the one makes the other, and proves it closes.

**The queue is the door run forwards.** For an object the person can see, the node knows the
object's family, its lifecycle state, and the person's standing toward it: the roles the held rows
give them (author, subject, member, moderator, founder, steward, holder, witness). The family's
lifecycle is a list of transitions, each a verb with the state it leaves, the state it reaches,
the roles that may sign it, the governance policy it runs under, whether it widens and whether it
has a way back. The queue is exactly the
transitions enabled for this viewer in this state, one item each, and an item's writes are the
row that transition signs. The admission door is the same predicate: a row is admitted when its
signer held a role the transition names in the state the object was in. So the queue can never
offer what the door would refuse, and the door never admits what the queue would not have offered.

In holon terms: a view is a unit (an admitted object), its rows and atoms are its bonds, and the
queue is the set of rewrites this holder may perform; answering an item performs the rewrite and
the next view shows it. In the CEWPOS algebra: P7 shows the state, P9 is an enabled rewrite, P8 is
an enabled rewrite that widens or has no way back, P4 is the row the rewrite wrote, P3 and P11 are
the bonds.
-/

inductive Role
  | author | subject | member | moderator | founder | steward | holder | witness
  deriving DecidableEq, Repr

inductive Verb
  | attest | withdraw | recant | supersede | authorize | carry | vote | cosign | accept
  deriving DecidableEq, Repr

inductive Policy
  | selfAct      -- one voice of one, no window
  | twoPath      -- enact / cancel / floor / window (CC 4.5.13)
  | mirror       -- one acts, the window decides (moderation, halt)
  | cosigned     -- a quorum of signatures
  | ranked       -- the moderator election
  deriving DecidableEq, Repr

/-- A transition of a family's lifecycle. -/
structure Transition where
  verb : Verb
  from_ : String
  to : String
  roles : List Role          -- any one of these may sign it
  policy : Policy
  widens : Bool              -- the row reaches someone the state before it did not
  undo : Bool                -- the lifecycle offers a way back from the state it reaches
  deriving DecidableEq, Repr

structure Family where
  name : String
  transitions : List Transition
  deriving Repr

/-- A view: one object as the node serves it. -/
structure View where
  family : Family
  state : String

/-- A person's standing toward the object, folded from held rows. -/
structure Standing where
  roles : List Role
  deriving DecidableEq, Repr

/-- The door: may this signer, with this standing, perform this transition on this view? -/
def admits (v : View) (s : Standing) (t : Transition) : Bool :=
  t.from_ == v.state && s.roles.any (fun r => t.roles.contains r)

/-- The enabled transitions: the door run forwards over the family's lifecycle. -/
def enabled (v : View) (s : Standing) : List Transition :=
  v.family.transitions.filter (admits v s)

/-- An item of the queue (the data of manifests/choice_item.cddl, reduced to what matters here). -/
structure Item where
  verb : Verb
  policy : Policy
  confirm : Bool             -- P8 before signing
  writes : Transition
  deriving DecidableEq, Repr

def toItem (t : Transition) : Item := ⟨t.verb, t.policy, t.widens || !t.undo, t⟩

/-- The queue a node serves this person for this view. -/
def queue (v : View) (s : Standing) : List Item := (enabled v s).map toItem

/-- Answering an item performs its rewrite: the next view. -/
def answer (v : View) (i : Item) : View := { v with state := i.writes.to }

/-! ## What is proved -/

/-- Soundness: every item in the queue is a transition the door admits for this person. -/
theorem queue_sound (v : View) (s : Standing) (i : Item) (h : i ∈ queue v s) :
    admits v s i.writes = true := by
  unfold queue at h
  obtain ⟨t, ht, rfl⟩ := List.mem_map.mp h
  exact (List.mem_filter.mp ht).2

/-- Completeness: every transition the door would admit for this person is in the queue. -/
theorem queue_complete (v : View) (s : Standing) (t : Transition)
    (hmem : t ∈ v.family.transitions) (h : admits v s t = true) : toItem t ∈ queue v s := by
  unfold queue
  exact List.mem_map.mpr ⟨t, List.mem_filter.mpr ⟨hmem, h⟩, rfl⟩

/-- The door and the queue are one predicate: a row is admitted iff its item was offered. -/
theorem door_is_queue (v : View) (s : Standing) (t : Transition) (hmem : t ∈ v.family.transitions) :
    admits v s t = true ↔ toItem t ∈ queue v s :=
  ⟨queue_complete v s t hmem, fun h => by
    unfold queue at h
    obtain ⟨t', ht', heq⟩ := List.mem_map.mp h
    have : t' = t := by
      have := congrArg Item.writes heq
      simpa [toItem] using this
    subst this
    exact (List.mem_filter.mp ht').2⟩

/-- No standing, no queue: a stranger sees no action on an object whose transitions all name a role. -/
theorem stranger_sees_nothing (v : View) (h : ∀ t ∈ v.family.transitions, t.roles ≠ []) :
    queue v ⟨[]⟩ = [] := by
  unfold queue enabled
  have : v.family.transitions.filter (admits v ⟨[]⟩) = [] := by
    apply List.filter_eq_nil_iff.mpr
    intro t _
    simp [admits]
  simp [this]

/-- The life closes: after an item is answered, the view is in the state the item reached, and an
    item that moved the state is no longer in the queue (its `from` no longer holds). -/
theorem answered_item_leaves_queue (v : View) (s : Standing) (i : Item)
    (h : i ∈ queue v s) (hmove : i.writes.from_ ≠ i.writes.to) :
    i ∉ queue (answer v i) s := by
  intro h'
  have hs := queue_sound (answer v i) s i h'
  simp only [admits, answer, Bool.and_eq_true, beq_iff_eq] at hs
  exact hmove hs.1

/-- The confirm test is one lookup (P8): an item is confirmed before it is signed exactly when its
    row widens or has no way back. -/
theorem confirm_is_lookup (v : View) (s : Standing) (i : Item) (h : i ∈ queue v s) :
    i.confirm = (i.writes.widens || !i.writes.undo) := by
  unfold queue at h
  obtain ⟨t, _, rfl⟩ := List.mem_map.mp h
  rfl

/-- Widening items are confirmed before they are signed. -/
theorem widening_is_confirmed (v : View) (s : Standing) (i : Item) (h : i ∈ queue v s)
    (hw : i.writes.widens = true) : i.confirm = true := by
  rw [confirm_is_lookup v s i h, hw]; rfl

/-- An item with no way back is confirmed before it is signed, narrowing or not. -/
theorem no_way_back_is_confirmed (v : View) (s : Standing) (i : Item) (h : i ∈ queue v s)
    (hu : i.writes.undo = false) : i.confirm = true := by
  rw [confirm_is_lookup v s i h, hu]; simp

/-- An exit takes one step: an item that does not widen and has a way back is never confirmed. -/
theorem exit_is_one_step (v : View) (s : Standing) (i : Item) (h : i ∈ queue v s)
    (hw : i.writes.widens = false) (hu : i.writes.undo = true) : i.confirm = false := by
  rw [confirm_is_lookup v s i h, hw, hu]; rfl

/-! ## Preview is execution: the queue, the preview and the door are one function -/

/-- The door executed: the view after a row for transition `t` is admitted, or nothing. -/
def execute (v : View) (s : Standing) (t : Transition) : Option View :=
  if admits v s t then some { v with state := t.to } else none

/-- Preview equals execution: for every item in the queue, the view the item previews (`answer`) is
    exactly the view the door produces when the row arrives. There is no second function to disagree. -/
theorem preview_is_execution (v : View) (s : Standing) (i : Item) (h : i ∈ queue v s) :
    execute v s i.writes = some (answer v i) := by
  simp [execute, queue_sound v s i h, answer]

/-- A row whose item was not offered produces nothing at the door: the preview of a refusal is a refusal. -/
theorem refused_previews_nothing (v : View) (s : Standing) (t : Transition)
    (hmem : t ∈ v.family.transitions) (h : toItem t ∉ queue v s) : execute v s t = none := by
  have : admits v s t = false := by
    cases hc : admits v s t
    · rfl
    · exact absurd (queue_complete v s t hmem hc) h
  simp [execute, this]

/-! ## A worked family: a room's post, from the text -/

def postFamily : Family := {
  name := "scores (a room post)",
  transitions := [
    ⟨.attest,   "none",      "live",      [.member], .selfAct, true,  true  ⟩,   -- a member posts (widens: leaves the person)
    ⟨.withdraw, "live",      "withdrawn", [.author], .selfAct, false, true  ⟩,   -- the author withdraws (narrows: one step)
    ⟨.recant,   "live",      "recanted",  [.author], .selfAct, false, true  ⟩,
    ⟨.vote,     "live",      "live",      [.member], .twoPath, false, true  ⟩,   -- a member raises or answers a flag
    ⟨.withdraw, "live",      "withheld",  [.moderator, .steward], .mirror, false, true ⟩,  -- a moderator withholds
    ⟨.cosign,   "withheld",  "removed",   [.member], .twoPath, false, false ⟩   -- the room decides under the floor (no way back)
  ] }

def live : View := ⟨postFamily, "live"⟩

/-- The author of a live post sees withdraw, recant and vote; never the moderator's withhold. -/
theorem author_queue :
    (queue live ⟨[.author, .member]⟩).map Item.verb = [.withdraw, .recant, .vote] := by decide

/-- A plain member sees only the vote. -/
theorem member_queue : (queue live ⟨[.member]⟩).map Item.verb = [.vote] := by decide

/-- A moderator who is not a member of the room sees the withhold and nothing else. -/
theorem moderator_queue : (queue live ⟨[.moderator]⟩).map Item.verb = [.withdraw] := by decide

/-- A stranger sees nothing. -/
theorem stranger_queue : queue live ⟨[]⟩ = [] := by decide

/-- After the author withdraws, the post is withdrawn and the author's queue is empty. -/
theorem after_withdraw :
    queue (answer live (toItem ⟨.withdraw, "live", "withdrawn", [.author], .selfAct, false, true⟩)) ⟨[.author, .member]⟩ = [] := by
  decide

/-- The author's three exits take one step each; the room's removal, which narrows and has no way
    back, is confirmed. -/
theorem author_exits_one_step :
    (queue live ⟨[.author, .member]⟩).map Item.confirm = [false, false, false] := by decide

theorem removal_is_confirmed :
    (queue ⟨postFamily, "withheld"⟩ ⟨[.member]⟩).map Item.confirm = [true] := by decide
