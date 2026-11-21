/-
  Admission.lean — code, profile and action admission are one seat walk; the voice count is what differs

  CC 2.7.11 (`kernel-admission`, constitution/part_2_the_grammar.md of the Constitution at tag v1.0-rc21,
  commit b016df4) states one admission over three scopes: a change to what an agent is (its profile), to
  what a node runs (code) and to what an agent is about to do (an action). The Constitution's model of it is
  `formal/admission/` at the same tag: `admission.py`, `check_admission.py` and `admission_expected.tsv`
  (14 properties, 92 cases, 48 planted breaks, 12 arrival orders). Its README ends: "That code and profile
  admission is the kernel's seat walk at one voice, and action admission the same walk at a count, is argued
  here and run, not proved in Lean." This file is that proof, and the 14 properties as theorems.

  THE STANDING DELEGATION (Constitution rc22, commit 4040d0b). CC 2.7.11 "Derived trust" now reads: an agent
  acts under standing delegations, and the person who signed one approves no single act under it. Its
  owner-binding delegates it the role its template defines, and under that it does any act that needs no role.
  An act that needs a role needs a live delegation whose scope names that role (CC 4.5.5 (b)). Only an act that
  no delegation covers needs the approving row that names its fingerprint. admission.py at 4040d0b
  (`delegated`, `may_effect`) has 14 properties over 97 cases with 49 plants; the new plant is
  `delegation_any_scope`. Here `mayEffect` takes the act's authority as one of three (`Auth`): none, `under` a
  delegation for a duty, or `claims` an approving row; the profile and code scopes and the dispatch are as at
  v1.0-rc21. A `withdraws` naming the delegation ends it whoever signed it, as admission.py reads it.

  THE ONE WALK (Part 1). `walk` is built from two pieces of the kernel and nothing else:
    * standing: `Causal.reaches`, the bounded walk that `Kernel.means_is_seat_walk` and
      `TwoMechanisms.claim_is_one_voice_consent` identify with the walk of one-voice seats;
    * the voices: `Consent.bodyConsents`, the count of distinct members' signatures carried on one row
      (`Consent.count_of_one_is_one_row` makes a count of one with one member the one-key case).
  A row admits a target when it is held, names the target exactly, is live, and some body it is a consent of
  has its stander reached from the root within the body's depth and its voices met at the body's count.
  A body is (stander, voices, need, depth).

  THE THREE SCOPES (Parts 2 to 4) are transcribed from admission.py as it is written (`one`, `admit`, `may`,
  `submit`, `halted`, `authorized`, `chain`, `load`, `may_dispatch`, `trust_of`, `may_effect`), with no
  reference to `walk`. Then:
    `code_is_walk`     a unit row admits at a host iff it is the walk from the host owner over `admission`
                       edges signed by persons, depth 5, with body (author, [author], 1, 5) for a row that
                       names no effect, (author, [author], 1, 0) for one that does, and
                       (group, members at the head, max 2 need, 5) for a counted row;
    `profile_is_walk`  an `identity_amendment` link counts iff it is the walk from the agent's steward over
                       its seats, depth 1, with body (approver, [approver], 1, 1);
    `action_is_walk`   a dispatch passes iff it is the walk from the agent itself, depth 0, with body
                       (agent, the four faculties, 4, 0);
    `three_admissions_one_walk` the three together.

  WHAT THE CLAIM NEEDS, STATED PLAINLY. The claim holds in this form, with two qualifications the README's
  sentence does not carry; neither is weakened here, each is a theorem.
    (1) Code admission is the walk at one voice only for a unit that names no effect, or for the host
        owner's own row on its own host (that row's walk has depth 0: the owner alone). A unit that names an
        effect, admitted by anyone else, is the walk at a COUNT of at least two persons (`code_effect_body`,
        `p4_effect_needs_count_or_owner`). This is CC 2.7.11's own table ("one person for a unit that only
        computes, or on a host that person owns; otherwise a count of persons"); the README's sentence omits it.
    (2) The action scope differs from the other two in more than the count: its root and stander are the
        agent's own key at depth 0, and its voices are the four faculties, which are not keys and not
        persons. A dispatch needs no person's row at all (`action_needs_no_person`: a world in which no key is
        a person, and a dispatch passes), and neither does an effect that needs no role, done under the role
        the owner-binding delegates (`effect_needs_no_person`). An action is rooted in a person only where an
        objection is discharged (`p9_discharge_by_person`) or the act claims authority, which it now does by
        one of two arms (`p11_authority_rooted_in_person`): a live delegation whose scope names the act's
        duty, signed by a person seated over THIS agent, who approves no single act under it
        (`p11_delegation_needs_no_approval`); or, for an act no delegation covers, an approving row naming
        the fingerprint, signed by a person seated over the agent THAT ROW names, which admission.py does not
        check is this agent. Against v1.0-rc21 this changes no case of `action_needs_no_person`: the
        dispatches that need no person are the same. What changes is where the person of a role act stands:
        at the grant of the delegation, not at each act. So "the same walk at a count" is true of the
        definition and the count; "differing only in the voice count" is not: the three differ in root,
        depth and kind of voice as well, and that is what `three_admissions_one_walk` states.

  THE FOURTEEN PROPERTIES (Part 5), each as theorems over the transcription, for every world, not the 97 cases:
    P1 `p1_runs_needs_admission`, `p1_issuer_reached`, `p1_no_owner_runs_nothing`
    P2 `p2_digest_bound`, `p2_changed_unit`
    P3 `p3_program_issues_nothing`, `p3_program_edges_carry_nothing`, `p3_program_voice_not_counted`
    P4 `p4_effect_needs_count_or_owner`, `p4_owner_row_self`, `p4_one_member_not_a_count`,
       `p4_head_not_held`, `p4_compute_one_person`
    P5 `p5_lease`, `p5_stops_within_one_lease`
    P6 `p6_author_withdrawal_ends`, `p6_forward`, `p6_forward_runs`, `p6_count_withdrawn_by_count`
    P7 `p7_halt_stops_effects`, `p7_compute_unhalted`, `p7_halter_is_holder`, `p7_lone_halt_lapses`,
       `p7_one_holder_does_not_resume`, `p7_programs_do_not_resume`
    P8 `p8_attenuate`, `p8_submit_receiver`
    P9 `p9_needs_four_passes`, `p9_changed_call`, `p9_objection_discharged`, `p9_discharge_by_person`,
       `p9_objection_carried`, `p9_approval_bound`
    P10 `p10_chain_unique`, `p10_loads_unique`, `p10_chain_authorized`, `p10_base_is_template`,
       `p10_fork_stops`, `p10_program_approval`, `p10_unanchored`
    P11 `p11_least`, `p11_own_trust_not_enough`, `p11_effect_gate`, `p11_trusted_needs_no_declaration`,
       `p11_no_role_reads_no_authority`, `p11_delegation_needs_no_approval`, `p11_delegation_needs`,
       `p11_delegation_licenses`, `p11_scope_must_name_duty` (the plant `delegation_any_scope` refuted;
       `delegation_any_scope_differs` shows a world where the plant's reading licenses and the rule does not),
       `p11_withdrawn_delegation`, `p11_program_delegation`, `p11_other_agent_delegation`,
       `p11_authority_rooted_in_person`
    P12 `p12_runs_perm`, `p12_may_perm`, `p12_loads_perm`, `p12_dispatch_perm`, `p12_effect_perm`
    P13 `profile_is_walk`, `code_is_walk`, `p13_one_voice_clauses`
    P14 `p14_build_runs`, `p14_unblessed_runs_nothing`
  Every property is stated. Three rest on a hypothesis that is not a theorem of Lean, and say so: P2 and P9
  take the digest and the fingerprint (SHA-256 over bytes or over a CDE encoding) to be injective, and P10
  reads the profile digest SHA-256(["CEG-profile/2", d0, ..., dn]) as the list of link digests, which is the
  same assumption. Collision resistance is not provable in Lean; it is a hypothesis of each such theorem.
  P12 is proved for every permutation, where the model runs twelve.

  WHERE THE TRANSCRIPTION READS A SET, NOT A FIRST ROW. admission.py takes the first matching row in five
  places (`kind_of`, `owner_of`, `steward`, `template`, a roster `heads[0]`), the first pass record in
  `may_effect`, and the last data row of an id in `trust_of`. Over a set of rows a first row is not defined;
  here each is "some held row". Where the world holds one such row, as every case of check_admission.py
  does, the two agree. Where it holds two, admission.py's answer depends on the order of the list and this
  one does not. The holders of the halt are read from one `bundle` row (admission.py takes the union of all
  bundles); a key's identity type is the predicate `person`. A row's fields `author` and `head` are one sum,
  so `admission_unit_malformed` cannot be written; a capability outside the closed seven cannot be written.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports Consent.lean.
-/

import Consent

namespace Kernel

namespace Admission

open Causal

/-! ## Part 0. Two counting facts -/

/-- A list without repeats, every element of which is in `m`, is no longer than `m`. -/
theorem nodup_len_le {α : Type} [DecidableEq α] :
    ∀ (l m : List α), l.Nodup → (∀ x, x ∈ l → x ∈ m) → l.length ≤ m.length
  | [], _, _, _ => Nat.zero_le _
  | x :: xs, m, hn, hs => by
    have hx : x ∈ m := hs x (List.mem_cons_self _ _)
    have hnd := List.nodup_cons.1 hn
    have ih := nodup_len_le xs (m.erase x) hnd.2 (fun y hy =>
      (List.mem_erase_of_ne (fun (e : y = x) => hnd.1 (e ▸ hy))).2 (hs y (List.mem_cons_of_mem _ hy)))
    have hl := List.length_erase_of_mem hx
    have hp : 0 < m.length := List.length_pos.2 (List.ne_nil_of_mem hx)
    simp only [List.length_cons]; omega

/-- A list without repeats whose elements are all one key has at most one element. -/
theorem nodup_one {α : Type} (a : α) : ∀ (l : List α), l.Nodup → (∀ x, x ∈ l → x = a) → l.length ≤ 1
  | [], _, _ => Nat.zero_le _
  | [_], _, _ => Nat.le_refl _
  | x :: y :: _, hn, h => by
    have hx := h x (List.mem_cons_self _ _)
    have hy := h y (List.mem_cons_of_mem _ (List.mem_cons_self _ _))
    exact absurd (List.mem_cons_self y _) (hx.trans hy.symm ▸ (List.nodup_cons.1 hn).1)

/-- The agent's four faculties (CC 3.1.5.3): faculties of the agent, not keys. -/
inductive Fac
  | entropy | coherence | optimizationVeto | epistemicHumility
  deriving DecidableEq

def Fac.all : List Fac := [.entropy, .coherence, .optimizationVeto, .epistemicHumility]

theorem Fac.mem_all (f : Fac) : f ∈ Fac.all := by cases f <;> decide

theorem Fac.all_nodup : Fac.all.Nodup := by decide

/-- Four distinct faculties are all of them. -/
theorem four_is_all (l : List Fac) (hn : l.Nodup) (h4 : 4 ≤ l.length) (f : Fac) : f ∈ l := by
  if hf : f ∈ l then exact hf else
  have := nodup_len_le l (Fac.all.erase f) hn (fun x hx =>
    (List.mem_erase_of_ne (fun (e : x = f) => hf (e ▸ hx))).2 (Fac.mem_all x))
  have hl := List.length_erase_of_mem (Fac.mem_all f)
  simp [Fac.all] at hl this
  omega

theorem reaches_le {K : Type} (E : K → K → Prop) (o : K) (n : Nat) (k : K) (h : reaches E o n k) :
    ∀ m, n ≤ m → reaches E o m k := by
  intro m hm
  induction m with
  | zero => have : n = 0 := by omega
            subst this; exact h
  | succ m ih =>
    if e : n = m + 1 then exact e ▸ h else exact Or.inl (ih (by omega))

/-! ## Part 1. The one walk -/

/-- What a row is a consent of: whose standing the walk reads (`stander`), the voices it counts, the count it
    asks, and how deep the walk to the stander may go. -/
structure Body (K V : Type) where
  stander : K
  voices : List V
  need : Nat
  depth : Nat

section Walk

variable {K V Row T : Type}

/-- A voice of body `b`: one of its voices, of the kind that may speak (`eligible`). -/
def member (eligible : V → Prop) (b : Body K V) (v : V) : Prop := v ∈ b.voices ∧ eligible v

/-- **The one walk.** Row `o` admits target `t` from `root`: it is held (`P`), names `t` exactly, is live,
    and for some body it is a consent of, the root's walk over `E` reaches the body's stander within the
    body's depth (`Causal.reaches`), and the voices carried on the row meet the body's count
    (`Consent.bodyConsents`). -/
def walk (E : K → K → Prop) (root : K) (eligible : V → Prop) (P : Row → Prop)
    (names : Row → T → Prop) (live : Row → Prop) (body : Row → Body K V → Prop)
    (cosigns : Row → V → Prop) (t : T) (o : Row) : Prop :=
  P o ∧ names o t ∧ live o ∧ ∃ b, body o b ∧ reaches E root b.depth b.stander ∧
    Consent.bodyConsents (member eligible) Body.need cosigns P b o

/-- **One voice is a count of one.** At a body with one voice and a count of one, the count is that voice's
    own signature, and it must be a voice that may speak (`Consent.count_of_one_is_one_row`). -/
theorem one_voice_is_one_signature (eligible : V → Prop) (cosigns : Row → V → Prop) (P : Row → Prop)
    (a : V) (s : K) (d : Nat) (o : Row) :
    Consent.bodyConsents (member eligible) Body.need cosigns P (⟨s, [a], 1, d⟩ : Body K V) o ↔
      P o ∧ eligible a ∧ cosigns o a := by
  by_cases he : eligible a
  · rw [Consent.count_of_one_is_one_row (member eligible) Body.need cosigns P _ o a
      (fun k => ⟨fun h => List.mem_singleton.1 h.1, fun e => by subst e; exact ⟨List.mem_singleton_self _, he⟩⟩) rfl]
    exact ⟨fun ⟨h1, h2⟩ => ⟨h1, he, h2⟩, fun ⟨h1, _, h2⟩ => ⟨h1, h2⟩⟩
  · constructor
    · intro ⟨_, l, _, hn, hl⟩
      match l, hn, hl with
      | [], hn, _ => exact absurd hn (by simp)
      | v :: _, _, hl =>
        have ⟨⟨hm, hv⟩, _⟩ := hl v (List.mem_cons_self _ _)
        exact absurd (List.mem_singleton.1 hm ▸ hv) he
    · intro ⟨_, h, _⟩; exact absurd h he

/-- **A count of two is never one voice** (`Consent.one_voice_is_not_a_count`). -/
theorem count_not_one_voice (eligible : V → Prop) (cosigns : Row → V → Prop) (P : Row → Prop)
    (b : Body K V) (o : Row) (h2 : 2 ≤ b.need) (a : V) (h1 : ∀ v, cosigns o v → v = a) :
    ¬ Consent.bodyConsents (member eligible) Body.need cosigns P b o :=
  Consent.one_voice_is_not_a_count (member eligible) Body.need cosigns P b o h2
    (fun _ _ _ _ c c' => (h1 _ c).trans (h1 _ c').symm)

/-- **P13, the shared clauses.** At a one-voice body the walk is exactly: held, names the target, live, the
    stander reached within the depth, the voice may speak, the voice signed. Every scope at one voice reads
    these clauses and no others. -/
theorem p13_one_voice_clauses (E : K → K → Prop) (root : K) (eligible : V → Prop) (P : Row → Prop)
    (names : Row → T → Prop) (live : Row → Prop) (cosigns : Row → V → Prop) (t : T) (o : Row)
    (s : K) (a : V) (d : Nat) :
    walk E root eligible P names live (fun _ b => b = ⟨s, [a], 1, d⟩) cosigns t o ↔
      P o ∧ names o t ∧ live o ∧ reaches E root d s ∧ eligible a ∧ cosigns o a := by
  constructor
  · intro ⟨h1, h2, h3, b, hb, hr, hc⟩
    subst hb
    have := (one_voice_is_one_signature eligible cosigns P a s d o).1 hc
    exact ⟨h1, h2, h3, hr, this.2.1, this.2.2⟩
  · intro ⟨h1, h2, h3, hr, he, hc⟩
    exact ⟨h1, h2, h3, _, rfl, hr, (one_voice_is_one_signature eligible cosigns P a s d o).2 ⟨h1, he, hc⟩⟩

end Walk

/-! ## Part 2. The code scope (admission.py `one`, `admit`, `may`, `submit`, `halted`) -/

/-- The closed seven (CC 2.7.11). -/
inductive Cap
  | compute | read | netSend | submit | sign | storeWrite | actuate
  deriving DecidableEq

/-- The last five are effects. -/
def Cap.effect : Cap → Prop
  | .compute => False
  | .read => False
  | _ => True

/-- An `admission:unit` row is one person's (`author`) or counted over a roster head (`head`). -/
inductive Iss (N Id : Type)
  | author (k : N)
  | head (h : Id)

structure UnitRow (N Dig Id : Type) where
  id : Id
  unit : Dig
  caps : List Cap
  start : Nat        -- asserted_at
  ends : Nat        -- valid_until
  self : Bool        -- the row's cohort_scope is `self`
  iss : Iss N Id

/-- The rows of admission.py's code scope. -/
inductive CRow (N Dig Id : Type)
  | owns (host owner : N)
  | edge (src dst : N) (admission : Bool)
  | roster (id : Id) (group : N) (members : List N) (need : Nat)
  | build (units : List Dig) (blessed : Bool)
  | unit (u : UnitRow N Dig Id)
  | stmt (of : Id) (signer : N)
  | withdraw (id of : Id) (head : Option Id)
  | bundle (holders : List N)
  | halt (id : Id) (signer : N)
  | life (id of : Id) (resume : Bool)

/-- A row with the instant the host first held it. -/
structure Ent (N Dig Id : Type) where
  t : Nat
  r : CRow N Dig Id

def DEPTH : Nat := 5      -- the walk's cap of five hops (CC 4.1.1)
def LEASE : Nat := 24     -- unit_lease_max_secs, in the model's hours
def FUSE : Nat := 24      -- halt_fuse_secs, in the model's hours
def FLOOR : Nat := 2      -- one voice is not a count (CC 2.7.5)

section Code

variable {N Dig Id : Type} (person : N → Prop) (accord : N)

abbrev Held (N Dig Id : Type) := Ent N Dig Id → Prop

def has (S : Held N Dig Id) (r : CRow N Dig Id) : Prop := ∃ t, S ⟨t, r⟩

/-- `held(R, now)`. -/
def held (W : List (Ent N Dig Id)) (now : Nat) : Held N Dig Id := fun e => e ∈ W ∧ e.t ≤ now

/-- `owner_of`: the person a host's owner-binding names. -/
def owner (S : Held N Dig Id) (host k : N) : Prop := person k ∧ has S (.owns host k)

/-- An edge of the walk: an acceptance edge listing `admission`, signed by a person. -/
def edgeE (S : Held N Dig Id) (m k : N) : Prop := person m ∧ has S (.edge m k true)

/-- `reach`: the host owner's own walk, five hops. -/
def reached (S : Held N Dig Id) (host k : N) : Prop :=
  ∃ o, owner person S host o ∧ reaches (edgeE person S) o DEPTH k

/-- `voices`: the persons whose statements over row `rid` are held. -/
def voices (S : Held N Dig Id) (rid : Id) (v : N) : Prop := person v ∧ has S (.stmt rid v)

/-- `count`, at one head: at least max(2, need) distinct members of the head, each with a statement. -/
def countAt (S : Held N Dig Id) (m : List N) (n : Nat) (rid : Id) : Prop :=
  ∃ l : List N, l.Nodup ∧ max FLOOR n ≤ l.length ∧ ∀ v, v ∈ l → v ∈ m ∧ voices person S rid v

def countMet (S : Held N Dig Id) (h rid : Id) : Prop :=
  ∃ g m n, has S (.roster h g m n) ∧ countAt person S m n rid

def effectful (u : UnitRow N Dig Id) : Prop := ∃ c, c ∈ u.caps ∧ c.effect

/-- `static`: a capability, a lease of at most LEASE, and one person's effect row at `self` scope. -/
def static (u : UnitRow N Dig Id) : Prop :=
  u.caps ≠ [] ∧ u.start < u.ends ∧ u.ends - u.start ≤ LEASE ∧
    ∀ a, u.iss = .author a → effectful u → u.self = true

/-- `withdrawn`: by its author's statement, or by the same count at the same head. -/
def withdrawn (S : Held N Dig Id) (u : UnitRow N Dig Id) : Prop :=
  ∃ wid hd, has S (.withdraw wid u.id hd) ∧
    match u.iss with
    | .author a => voices person S wid a
    | .head h => hd = some h ∧ countMet person S h wid

def leaseOK (now : Nat) (e : Ent N Dig Id) (u : UnitRow N Dig Id) : Prop :=
  u.start ≤ now ∧ now < u.ends ∧ now < e.t + LEASE

/-- The issuer clauses of `one`. -/
def issuerStands (S : Held N Dig Id) (host : N) (u : UnitRow N Dig Id) : Prop :=
  match u.iss with
  | .author a => voices person S u.id a ∧ reached person S host a ∧ (effectful u → owner person S host a)
  | .head h => ∃ g m n, has S (.roster h g m n) ∧ reached person S host g ∧ countAt person S m n u.id

/-- `one(...) == "admit"`. -/
def rowAdmits (S : Held N Dig Id) (host : N) (now : Nat) (e : Ent N Dig Id) (u : UnitRow N Dig Id) : Prop :=
  S e ∧ e.r = .unit u ∧ static u ∧ issuerStands person S host u ∧ leaseOK now e u ∧ ¬ withdrawn person S u

/-- `built_in`. -/
def builtIn (S : Held N Dig Id) (d : Dig) : Prop := ∃ us, has S (.build us true) ∧ d ∈ us

/-- The capabilities `admit` returns: every capability under the build, else the union over admitting rows. -/
def caps (W : List (Ent N Dig Id)) (host : N) (d : Dig) (now : Nat) (c : Cap) : Prop :=
  builtIn (held W now) d ∨ ∃ e u, rowAdmits person (held W now) host now e u ∧ u.unit = d ∧ c ∈ u.caps

/-- `admit(...)[0] == "admit"`. -/
def runs (W : List (Ent N Dig Id)) (host : N) (d : Dig) (now : Nat) : Prop :=
  builtIn (held W now) d ∨ ∃ e u, rowAdmits person (held W now) host now e u ∧ u.unit = d

/-- A strict majority of the holders `hs`, among keys `vs`. -/
def majority (hs : List N) (vs : N → Prop) : Prop :=
  ∃ l : List N, l.Nodup ∧ hs.length < 2 * l.length ∧ ∀ v, v ∈ l → vs v ∧ v ∈ hs

/-- `halted`: a holder's halt, received where the owner held an edge to the accord, not resumed by a
    majority, and within its fuse or confirmed by a majority before the fuse. -/
def halted (S : Held N Dig Id) (host : N) (now : Nat) : Prop :=
  ∃ hs hid hb th, has S (.bundle hs) ∧ S ⟨th, .halt hid hb⟩ ∧ hb ∈ hs ∧
    (∃ o te cls, owner person S host o ∧ S ⟨te, .edge o accord cls⟩ ∧ te ≤ th) ∧
    ¬ (∃ lid, has S (.life lid hid true) ∧ majority hs (voices person S lid)) ∧
    (now < th + FUSE ∨
      ∃ lid, has S (.life lid hid false) ∧ majority hs (fun v => ∃ ts, S ⟨ts, .stmt lid v⟩ ∧ ts < th + FUSE))

/-- `may`: the host's gate before a unit does `cap`. -/
def may (W : List (Ent N Dig Id)) (host : N) (d : Dig) (cap : Cap) (now : Nat)
    (parent : Option (List Cap)) : Prop :=
  caps person W host d now cap ∧ (∀ p, parent = some p → cap ∈ p) ∧
    (cap.effect → ¬ halted person accord (held W now) host now)

/-- `submit`: the receiving host runs a submitted unit by its own admission. -/
def submit (W : List (Ent N Dig Id)) (_sender receiver : N) (d : Dig) (now : Nat) : Prop :=
  runs person W receiver d now

/-! ### The code scope is the walk -/

/-- The body a unit row is a consent of. -/
def codeBody (S : Held N Dig Id) (e : Ent N Dig Id) (b : Body N N) : Prop :=
  ∃ u, e.r = .unit u ∧
    match u.iss with
    | .author a => (¬ effectful u ∧ b = ⟨a, [a], 1, DEPTH⟩) ∨ (effectful u ∧ b = ⟨a, [a], 1, 0⟩)
    | .head h => ∃ g m n, has S (.roster h g m n) ∧ b = ⟨g, m, max FLOOR n, DEPTH⟩

def codeNames (e : Ent N Dig Id) (d : Dig) : Prop := ∃ u, e.r = .unit u ∧ u.unit = d

def codeLive (S : Held N Dig Id) (now : Nat) (e : Ent N Dig Id) : Prop :=
  ∃ u, e.r = .unit u ∧ static u ∧ leaseOK now e u ∧ ¬ withdrawn person S u

def codeSigns (S : Held N Dig Id) (e : Ent N Dig Id) (v : N) : Prop := ∃ u, e.r = .unit u ∧ has S (.stmt u.id v)

theorem unit_inj {u u' : UnitRow N Dig Id} (h : CRow.unit u = CRow.unit u') : u = u' := by injection h

/-- **Code admission is the walk.** A unit row admits digest `d` at a host iff, for some owner of the host,
    it is the walk from that owner over persons' `admission` edges, at the body `codeBody` gives it. -/
theorem code_is_walk (S : Held N Dig Id) (host : N) (now : Nat) (e : Ent N Dig Id) (d : Dig) :
    (∃ u, rowAdmits person S host now e u ∧ u.unit = d) ↔
      ∃ o, owner person S host o ∧
        walk (edgeE person S) o person S codeNames (codeLive person S now) (codeBody S) (codeSigns S) d e := by
  constructor
  · intro ⟨u, ⟨hS, hr, hst, his, hl, hw⟩, hd⟩
    have names : codeNames e d := ⟨u, hr, hd⟩
    have live : codeLive person S now e := ⟨u, hr, hst, hl, hw⟩
    unfold issuerStands at his
    unfold codeBody
    cases hiss : u.iss with
    | author a =>
      rw [hiss] at his
      have ⟨⟨hp, hsg⟩, ⟨o, ho, hro⟩, hown⟩ := his
      have sig : Consent.bodyConsents (member person) Body.need (codeSigns S) S
          (⟨a, [a], 1, 0⟩ : Body N N) e := (one_voice_is_one_signature person (codeSigns S) S a a 0 e).2
          ⟨hS, hp, u, hr, hsg⟩
      have sig' : Consent.bodyConsents (member person) Body.need (codeSigns S) S
          (⟨a, [a], 1, DEPTH⟩ : Body N N) e := (one_voice_is_one_signature person (codeSigns S) S a a DEPTH e).2
          ⟨hS, hp, u, hr, hsg⟩
      by_cases hef : effectful u
      · exact ⟨a, hown hef, hS, names, live, (⟨a, [a], 1, 0⟩ : Body N N),
          ⟨u, hr, by rw [hiss]; exact Or.inr ⟨hef, rfl⟩⟩, (rfl : a = a), sig⟩
      · exact ⟨o, ho, hS, names, live, (⟨a, [a], 1, DEPTH⟩ : Body N N),
          ⟨u, hr, by rw [hiss]; exact Or.inl ⟨hef, rfl⟩⟩, hro, sig'⟩
    | head h =>
      rw [hiss] at his
      have ⟨g, m, n, hrost, ⟨o, ho, hro⟩, l, hnd, hlen, hl'⟩ := his
      refine ⟨o, ho, hS, names, live, ⟨g, m, max FLOOR n, DEPTH⟩, ⟨u, hr, by rw [hiss]; exact ⟨g, m, n, hrost, rfl⟩⟩,
        hro, hS, l, hnd, hlen, fun v hv => ?_⟩
      have ⟨h1, h2, h3⟩ := hl' v hv
      exact ⟨⟨h1, h2⟩, u, hr, h3⟩
  · intro ⟨o, ho, hS, ⟨u, hr, hd⟩, ⟨u1, hr1, hst, hl, hw⟩, b, ⟨u2, hr2, hb⟩, hro, hc⟩
    have e1 : u1 = u := unit_inj (hr1.symm.trans hr)
    have e2 : u2 = u := unit_inj (hr2.symm.trans hr)
    rw [e1] at hst hl hw
    rw [e2] at hb
    refine ⟨u, ⟨hS, hr, hst, ?_, hl, hw⟩, hd⟩
    unfold issuerStands
    cases hiss : u.iss with
    | author a =>
      rw [hiss] at hb
      have reach0 : ∀ d, b = ⟨a, [a], 1, d⟩ → voices person S u.id a := by
        intro d hbd
        subst hbd
        have ⟨_, hp, u', hr', hsg⟩ := (one_voice_is_one_signature person (codeSigns S) S a a d e).1 hc
        exact ⟨hp, unit_inj (hr'.symm.trans hr) ▸ hsg⟩
      cases hb with
      | inl hb =>
        have ⟨hef, hbd⟩ := hb
        refine ⟨reach0 _ hbd, ⟨o, ho, ?_⟩, fun x => absurd x hef⟩
        subst hbd; exact hro
      | inr hb =>
        have ⟨_, hbd⟩ := hb
        have hv := reach0 _ hbd
        subst hbd
        have hao : a = o := hro
        subst hao
        exact ⟨hv, ⟨a, ho, reaches_le _ a 0 a rfl DEPTH (Nat.zero_le _)⟩, fun _ => ho⟩
    | head h =>
      rw [hiss] at hb
      have ⟨g, m, n, hrost, hbd⟩ := hb
      subst hbd
      have ⟨_, l, hnd, hlen, hl'⟩ := hc
      refine ⟨g, m, n, hrost, ⟨o, ho, hro⟩, l, hnd, hlen, fun v hv => ?_⟩
      have ⟨⟨h1, h2⟩, u', hr', h3⟩ := hl' v hv
      exact ⟨h1, h2, unit_inj (hr'.symm.trans hr) ▸ h3⟩

/-- **Qualification (1).** The body of a code row: one voice and a count of one for one person's row, at the
    full depth when it names no effect and at depth 0 (the stander is the root, the owner itself) when it
    does; and a count of at least two for a counted row. -/
theorem code_effect_body (S : Held N Dig Id) (e : Ent N Dig Id) (b : Body N N) (h : codeBody S e b) :
    (b.need = 1 ∧ b.voices.length = 1 ∧ (∀ u, e.r = .unit u → effectful u → b.depth = 0)) ∨ 2 ≤ b.need := by
  have ⟨u, hr, hb⟩ := h
  cases hiss : u.iss with
  | author a =>
    rw [hiss] at hb
    refine Or.inl ?_
    cases hb with
    | inl hb =>
      rw [hb.2]
      exact ⟨rfl, rfl, fun u' hr' hef => absurd (unit_inj (hr.symm.trans hr') ▸ hef) hb.1⟩
    | inr hb => rw [hb.2]; exact ⟨rfl, rfl, fun _ _ _ => rfl⟩
  | head h =>
    rw [hiss] at hb
    have ⟨_, _, n, _, hbd⟩ := hb
    subst hbd
    exact Or.inr (by simp [FLOOR]; omega)

end Code

/-! ## Part 3. The profile scope (admission.py `authorized`, `chain`, `load`) and the action scope
    (`may_dispatch`, `trust_of`, `may_effect`) -/

structure Link (N Dig Id : Type) where
  id : Id
  agent : N
  digest : Dig
  prev : Option Id
  byResp : Id

structure Review (Dig Id L : Type) where
  id : Id
  thought : Id
  fp : Dig
  passed : Bool
  facs : List Fac
  discharges : List (Id × Id)
  considered : List Id
  derived : List L

/-- The rows of the agent's scopes. -/
inductive GRow (N Dig Id L D : Type)
  | bind (agent steward : N)
  | seat (agent wa conferrer : N)
  | resp (id : Id) (agent : N) (approved : Bool) (signer : N) (digest : Option Dig) (fp : Option Dig)
  | template (agent : N) (digest : Dig) (attested : Bool)
  | amend (a : Link N Dig Id)
  | review (p : Review Dig Id L)
  | data (id : Id) (trust : Nat) (label : L) (names : List Id)
  | ack (of : Dig) (signer : N)
  | deleg (id : Id) (agent : N) (signer : N) (scope : List D)   -- a `delegates_to` onto `agent`
  | withdraw (of : Id)                                          -- a `withdraws` naming row `of`

/-- What an act claims as its authority (admission.py `may_effect`'s `under`/`duty` and `claims`): nothing (an
    act that needs no role, done under the role the agent's owner-binding delegates it), a standing delegation
    and the duty the act needs, or an approving row. The model reads `under` before `claims`; here the two arms
    are one sum. -/
inductive Auth (Id D : Type)
  | none
  | under (rid : Id) (duty : D)
  | claims (c : Id)

section Agent

variable {N Dig Id L D : Type} (person : N → Prop)

abbrev GSet (N Dig Id L D : Type) := GRow N Dig Id L D → Prop

/-- `authorized`: the cited response is held, approved, about this agent, signed by a person who is the
    agent's steward or seated by the steward, and carries the amendment's exact digest. -/
def authorized (S : GSet N Dig Id L D) (a : Link N Dig Id) : Prop :=
  ∃ b fp st, S (.resp a.byResp a.agent true b (some a.digest) fp) ∧ person b ∧ S (.bind a.agent st) ∧
    (b = st ∨ S (.seat a.agent b st))

/-- A candidate for the link after `cur`: held, authorized, naming `cur`; the base also approves the attested
    template's exact digest. -/
def step (S : GSet N Dig Id L D) (agent : N) (cur : Option Id) (a : Link N Dig Id) : Prop :=
  S (.amend a) ∧ a.agent = agent ∧ authorized person S a ∧ a.prev = cur ∧
    (cur = none → ∃ tpl, S (.template agent tpl true) ∧ a.digest = tpl)

/-- `chain`: from no predecessor, the one candidate at each link; it stops where there is none or two. -/
inductive IsChain (S : GSet N Dig Id L D) (agent : N) : Option Id → List (Link N Dig Id) → Prop
  | stop (cur : Option Id) :
      (¬ ∃ a, step person S agent cur a ∧ ∀ b, step person S agent cur b → b = a) → IsChain S agent cur []
  | next (cur : Option Id) (a : Link N Dig Id) (l : List (Link N Dig Id)) :
      step person S agent cur a → (∀ b, step person S agent cur b → b = a) →
      IsChain S agent (some a.id) l → IsChain S agent cur (a :: l)

/-- A base link is held. -/
def anchored (S : GSet N Dig Id L D) (agent : N) : Prop :=
  ∃ a, step person S agent none a ∧ ∀ b, step person S agent none b → b = a

/-- `load`: anchored, the agent loads exactly the digests its chain derives (the profile digest read as that
    list: SHA-256 assumed injective); unanchored, the attested template alone. -/
def loads (S : GSet N Dig Id L D) (agent : N) (loaded : List Dig) : Prop :=
  (anchored person S agent ∧ ∃ l, IsChain person S agent none l ∧ loaded = l.map Link.digest) ∨
  (¬ anchored person S agent ∧ ∃ tpl, S (.template agent tpl true) ∧ loaded = [tpl])

/-- `trusted_evidence`: an approving response by a person seated over the agent, or its steward. -/
def trusted (S : GSet N Dig Id L D) (rid : Id) : Prop :=
  ∃ ag b d fp, S (.resp rid ag true b d fp) ∧ person b ∧ ((∃ c, S (.seat ag b c)) ∨ S (.bind ag b))

/-- `may_dispatch`, over the recomputed fingerprint `fp`. -/
def dispatch (S : GSet N Dig Id L D) (th : Id) (fp : Dig) (approvedBy : Option Id) : Prop :=
  (∃ p : Review Dig Id L, S (.review p) ∧ p.thought = th ∧ p.fp = fp ∧ p.passed = true ∧
    (∀ f : Fac, f ∈ p.facs) ∧
    (∀ o : Review Dig Id L, S (.review o) → o.thought = th → o.passed = false → o.fp = fp →
      ∃ ev, (o.id, ev) ∈ p.discharges ∧ trusted person S ev) ∧
    (∀ o : Review Dig Id L, S (.review o) → o.thought = th → o.passed = false → o.fp ≠ fp →
      o.id ∈ p.considered)) ∧
  (∀ g, approvedBy = some g → ∃ ag b d, S (.resp g ag true b d (some fp)))

/-- `a` is `r` or a row `r` derives from, through the held data rows. -/
inductive From (S : GSet N Dig Id L D) : Id → Id → Prop
  | refl (r : Id) : From S r r
  | step (r a b : Id) (tr : Nat) (lb : L) (ns : List Id) :
      From S r a → S (.data a tr lb ns) → b ∈ ns → From S r b

def VERIFIED : Nat := 1

/-- `trust_of(r) ≥ v`: the least trust over `r` and everything it derives from is at least `v`. -/
def trustAtLeast (S : GSet N Dig Id L D) (r : Id) (v : Nat) : Prop :=
  ∀ a tr lb ns, From S r a → S (.data a tr lb ns) → v ≤ tr

def untrustedLabel (S : GSet N Dig Id L D) (r : Id) (lb : L) : Prop :=
  ∃ a tr ns, From S r a ∧ S (.data a tr lb ns) ∧ tr < VERIFIED

/-- `delegated` (CC 4.5.5 (b)): a `delegates_to` row `rid` onto this agent, signed by a person seated over it
    (a seat over the agent, or its steward), with no `withdraws` naming it held, whose scope names the duty. -/
def delegated (S : GSet N Dig Id L D) (agent : N) (rid : Id) (duty : D) : Prop :=
  ∃ b sc, S (.deleg rid agent b sc) ∧ person b ∧ ((∃ c, S (.seat agent b c)) ∨ S (.bind agent b)) ∧
    ¬ S (.withdraw rid) ∧ duty ∈ sc

/-- The authority arm of `may_effect`: none asked; the standing delegation; or the approving row naming the
    fingerprint. -/
def authorityOK (S : GSet N Dig Id L D) (agent : N) (fp : Dig) : Auth Id D → Prop
  | .none => True
  | .under rid duty => delegated person S agent rid duty
  | .claims c => ∃ ag ok b d, S (.resp c ag ok b d (some fp)) ∧ trusted person S c

/-- `may_effect` (Constitution 4040d0b). -/
def mayEffect (S : GSet N Dig Id L D) (agent : N) (th : Id) (fp : Dig) (args : Id) (auth : Auth Id D)
    (binds : List N) : Prop :=
  (∃ p : Review Dig Id L, S (.review p) ∧ p.thought = th ∧ p.passed = true ∧ p.fp = fp ∧
    (¬ trustAtLeast S args VERIFIED → ∀ lb, untrustedLabel S args lb → lb ∈ p.derived)) ∧
  authorityOK person S agent fp auth ∧
  (∀ k, k ∈ binds → S (.ack fp k))

/-! ### The profile scope is the walk at one voice -/

def profNames (a : Link N Dig Id) (o : GRow N Dig Id L D) (_ : Unit) : Prop :=
  ∃ b fp, o = .resp a.byResp a.agent true b (some a.digest) fp

def profBody (a : Link N Dig Id) (o : GRow N Dig Id L D) (bd : Body N N) : Prop :=
  ∃ b fp, o = .resp a.byResp a.agent true b (some a.digest) fp ∧ bd = ⟨b, [b], 1, 1⟩

def profSigns (o : GRow N Dig Id L D) (v : N) : Prop := ∃ i ag ok d fp, o = .resp i ag ok v d fp

/-- **Profile admission is the walk at one voice.** A link counts iff, for the agent's steward, its
    approving response is the walk from the steward over the steward's seats over the agent, depth 1, at the
    one-voice body of the response's signer. -/
theorem profile_is_walk (S : GSet N Dig Id L D) (a : Link N Dig Id) :
    authorized person S a ↔ ∃ st, S (.bind a.agent st) ∧ ∃ o,
      walk (fun m k => S (.seat a.agent k m)) st person S (profNames a) (fun _ => True) (profBody a)
        profSigns () o := by
  constructor
  · intro ⟨b, fp, st, hr, hp, hbd, hs⟩
    refine ⟨st, hbd, _, hr, ⟨b, fp, rfl⟩, trivial, ⟨b, [b], 1, 1⟩, ⟨b, fp, rfl, rfl⟩, ?_,
      (one_voice_is_one_signature person profSigns S b b 1 _).2 ⟨hr, hp, _, _, _, _, _, rfl⟩⟩
    cases hs with
    | inl e => exact Or.inl e
    | inr hs => exact Or.inr ⟨st, rfl, hs⟩
  · intro ⟨st, hbd, o, hS, _, _, bd, ⟨b, fp, ho, hb⟩, hro, hc⟩
    subst ho; subst hb
    have ⟨_, hp, _⟩ := (one_voice_is_one_signature person profSigns S b b 1 _).1 hc
    refine ⟨b, fp, st, hS, hp, hbd, ?_⟩
    cases hro with
    | inl e => exact Or.inl e
    | inr h => have ⟨m, hm, he⟩ := h; exact Or.inr (hm ▸ he)

/-! ### The action scope is the walk at a count of four -/

def actNames (th : Id) (o : GRow N Dig Id L D) (fp : Dig) : Prop :=
  ∃ p : Review Dig Id L, o = .review p ∧ p.thought = th ∧ p.fp = fp ∧ p.passed = true

def actLive (S : GSet N Dig Id L D) (th : Id) (fp : Dig) (g : Option Id) (o : GRow N Dig Id L D) : Prop :=
  (∃ p : Review Dig Id L, o = .review p ∧
    (∀ o : Review Dig Id L, S (.review o) → o.thought = th → o.passed = false → o.fp = fp →
      ∃ ev, (o.id, ev) ∈ p.discharges ∧ trusted person S ev) ∧
    (∀ o : Review Dig Id L, S (.review o) → o.thought = th → o.passed = false → o.fp ≠ fp →
      o.id ∈ p.considered)) ∧
  (∀ g', g = some g' → ∃ ag b d, S (.resp g' ag true b d (some fp)))

def actSigns (o : GRow N Dig Id L D) (f : Fac) : Prop := ∃ p : Review Dig Id L, o = .review p ∧ f ∈ p.facs

theorem review_inj {p q : Review Dig Id L} (h : (GRow.review p : GRow N Dig Id L D) = GRow.review q) : p = q := by
  injection h

/-- **Action admission is the walk at a count.** A dispatch passes iff a pass record is the walk from the
    agent `ag` itself at depth 0, with the four faculties as its voices and a count of four. -/
theorem action_is_walk (S : GSet N Dig Id L D) (ag : N) (th : Id) (fp : Dig) (g : Option Id) :
    dispatch person S th fp g ↔ ∃ o,
      walk (fun _ _ => False) ag (fun _ => True) S (actNames th) (actLive person S th fp g)
        (fun _ b => b = (⟨ag, Fac.all, 4, 0⟩ : Body N Fac)) actSigns fp o := by
  constructor
  · intro ⟨⟨p, hS, ht, hf, hpass, hall, hob, hcon⟩, happ⟩
    refine ⟨_, hS, ⟨p, rfl, ht, hf, hpass⟩, ⟨⟨p, rfl, hob, hcon⟩, happ⟩, _, rfl, rfl, hS, Fac.all,
      Fac.all_nodup, Nat.le_refl _, fun f hf' => ⟨⟨hf', trivial⟩, p, rfl, hall f⟩⟩
  · intro ⟨o, hS, ⟨p, ho, ht, hf, hpass⟩, ⟨⟨p', ho', hob, hcon⟩, happ⟩, b, hb, _, _, l, hnd, hlen, hl⟩
    subst ho; subst hb
    have e : p' = p := review_inj ho'.symm
    subst e
    refine ⟨⟨p', hS, ht, hf, hpass, fun f => ?_, hob, hcon⟩, happ⟩
    have ⟨_, q, hq, hfq⟩ := hl f (four_is_all l hnd hlen f)
    exact review_inj hq ▸ hfq

/-- **Qualification (2).** The action scope needs no person. With no key a person, a world holding one pass
    record of all four faculties dispatches: the review record is under the agent's own key and binds only
    its own dispatch (CC 2.7.11, "Action"). Unchanged by the standing delegation of 4040d0b, which reads only
    at the effect gate (`effect_needs_no_person`, `p11_authority_rooted_in_person`). -/
theorem action_needs_no_person :
    dispatch (N := Unit) (Dig := Unit) (Id := Unit) (L := Unit) (D := Unit) (fun _ => False)
      (fun r => r = .review ⟨(), (), (), true, Fac.all, [], [], []⟩) () () none := by
  refine ⟨⟨⟨(), (), (), true, Fac.all, [], [], []⟩, rfl, rfl, rfl, rfl, Fac.mem_all, ?_, ?_⟩, ?_⟩
  · intro o ho _ hp _
    have := review_inj ho
    subst this; exact absurd hp (by decide)
  · intro o ho _ hp _
    have := review_inj ho
    subst this; exact absurd hp (by decide)
  · intro g hg; exact absurd hg (by simp)

end Agent

/-! ## Part 4. The three admissions are one walk -/

/-- **The three admissions are instances of one walk.** Code admission at a host, profile admission of a link
    and action admission of a dispatch are each `walk`, and differ in the body: one voice and a count of one
    for profile (depth 1 from the steward) and for one person's code row (depth 5 from the host owner, depth
    0 when it names an effect), a count of at least two for a counted code row, and the four faculties at a
    count of four for an action (depth 0 from the agent itself). -/
theorem three_admissions_one_walk {N Dig Id L D : Type} (person : N → Prop)
    (S : Held N Dig Id) (host : N) (now : Nat) (e : Ent N Dig Id) (d : Dig)
    (G : GSet N Dig Id L D) (a : Link N Dig Id) (ag : N) (th : Id) (fp : Dig) (g : Option Id) :
    ((∃ u, rowAdmits person S host now e u ∧ u.unit = d) ↔
      ∃ o, owner person S host o ∧
        walk (edgeE person S) o person S codeNames (codeLive person S now) (codeBody S) (codeSigns S) d e) ∧
    (∀ b, codeBody S e b → (b.need = 1 ∧ b.voices.length = 1) ∨ 2 ≤ b.need) ∧
    (authorized person G a ↔ ∃ st, G (.bind a.agent st) ∧ ∃ o,
      walk (fun m k => G (.seat a.agent k m)) st person G (profNames a) (fun _ => True) (profBody a)
        profSigns () o) ∧
    (∀ (o : GRow N Dig Id L D) b, profBody a o b → b.need = 1 ∧ b.voices.length = 1) ∧
    (dispatch person G th fp g ↔ ∃ o,
      walk (fun _ _ => False) ag (fun _ => True) G (actNames th) (actLive person G th fp g)
        (fun _ b => b = (⟨ag, Fac.all, 4, 0⟩ : Body N Fac)) actSigns fp o) ∧
    (⟨ag, Fac.all, 4, 0⟩ : Body N Fac).need = 4 :=
  ⟨code_is_walk person S host now e d,
   fun b hb => (code_effect_body S e b hb).elim (fun h => Or.inl ⟨h.1, h.2.1⟩) Or.inr,
   profile_is_walk person G a,
   fun _ _ ⟨_, _, _, hb⟩ => hb ▸ ⟨rfl, rfl⟩,
   action_is_walk person G ag th fp g,
   rfl⟩

/-! ## Part 5. The fourteen properties -/

section Props

variable {N Dig Id : Type} (person : N → Prop) (accord : N)

/-! ### P1 nothing runs without an admitted digest -/

theorem p1_runs_needs_admission (W : List (Ent N Dig Id)) (host : N) (d : Dig) (now : Nat)
    (h : runs person W host d now) :
    builtIn (held W now) d ∨ ∃ e u, held W now e ∧ e.r = .unit u ∧ u.unit = d ∧ static u ∧
      issuerStands person (held W now) host u ∧ leaseOK now e u :=
  h.elim Or.inl fun ⟨e, u, ⟨h1, h2, h3, h4, h5, _⟩, hd⟩ => Or.inr ⟨e, u, h1, h2, hd, h3, h4, h5⟩

/-- The issuer, or the group a counted row names, is reached by the host owner's own walk. -/
theorem p1_issuer_reached (S : Held N Dig Id) (host : N) (now : Nat) (e : Ent N Dig Id) (u : UnitRow N Dig Id)
    (h : rowAdmits person S host now e u) :
    (∀ a, u.iss = .author a → reached person S host a) ∧
    (∀ hd, u.iss = .head hd → ∃ g m n, has S (.roster hd g m n) ∧ reached person S host g) := by
  have his := h.2.2.2.1
  unfold issuerStands at his
  refine ⟨fun a ha => ?_, fun hd ha => ?_⟩
  · rw [ha] at his; exact his.2.1
  · rw [ha] at his; have ⟨g, m, n, h1, h2, _⟩ := his; exact ⟨g, m, n, h1, h2⟩

/-- A host with no owner-binding runs nothing beyond its attested build. -/
theorem p1_no_owner_runs_nothing (W : List (Ent N Dig Id)) (host : N) (d : Dig) (now : Nat)
    (hno : ∀ k, ¬ owner person (held W now) host k) (hb : ¬ builtIn (held W now) d) :
    ¬ runs person W host d now := by
  intro h
  cases h with
  | inl h => exact hb h
  | inr h =>
    have ⟨e, u, hu, _⟩ := h
    have ⟨ha, hh⟩ := p1_issuer_reached person _ host now e u hu
    cases hiss : u.iss with
    | author a => have ⟨o, ho, _⟩ := ha a hiss; exact hno o ho
    | head hd => have ⟨_, _, _, _, o, ho, _⟩ := hh hd hiss; exact hno o ho

/-! ### P2 a changed unit has no admission -/

theorem p2_digest_bound (W : List (Ent N Dig Id)) (host : N) (d : Dig) (now : Nat)
    (hrows : ∀ e u, held W now e → e.r = .unit u → u.unit ≠ d) (hb : ¬ builtIn (held W now) d) :
    ¬ runs person W host d now := by
  intro h
  cases h with
  | inl h => exact hb h
  | inr h => have ⟨e, u, hu, hd⟩ := h; exact hrows e u hu.1 hu.2.1 hd

/-- With the digest injective (SHA-256 assumed collision-free), a unit whose bytes differ from every
    admitted unit's has no admission. -/
theorem p2_changed_unit {B : Type} (dOf : B → Dig) (hinj : ∀ x y, dOf x = dOf y → x = y)
    (W : List (Ent N Dig Id)) (host : N) (now : Nat) (bs : List B) (b' : B) (hb' : b' ∉ bs)
    (hrows : ∀ e u, held W now e → e.r = .unit u → ∃ b, b ∈ bs ∧ u.unit = dOf b)
    (hbuild : ¬ builtIn (held W now) (dOf b')) :
    ¬ runs person W host (dOf b') now :=
  p2_digest_bound person W host (dOf b') now (fun e u he hr hd =>
    let ⟨b, hb, hu⟩ := hrows e u he hr
    hb' (hinj b b' (hu.symm.trans hd) ▸ hb)) hbuild

/-! ### P3 a program's key admits nothing -/

theorem p3_program_issues_nothing (S : Held N Dig Id) (host : N) (now : Nat) (e : Ent N Dig Id)
    (u : UnitRow N Dig Id) (a : N) (ha : u.iss = .author a) (hp : ¬ person a) :
    ¬ rowAdmits person S host now e u := by
  intro h
  have his := h.2.2.2.1
  unfold issuerStands at his
  rw [ha] at his
  exact hp his.1.1

/-- Edges signed by programs carry nothing: dropping them changes no key's standing at any host. -/
theorem p3_program_edges_carry_nothing (S : Held N Dig Id) (host k : N) :
    reached person S host k ↔
      reached person (fun e => S e ∧ ∀ m k' b, e.r = .edge m k' b → person m) host k := by
  have ho : ∀ x, owner person S host x ↔
      owner person (fun e => S e ∧ ∀ m k' b, e.r = .edge m k' b → person m) host x :=
    fun x => ⟨fun ⟨hp, t, ht⟩ => ⟨hp, t, ht, fun _ _ _ h => by cases h⟩, fun ⟨hp, t, ht, _⟩ => ⟨hp, t, ht⟩⟩
  have he : edgeE person S =
      edgeE person (fun e => S e ∧ ∀ m k' b, e.r = .edge m k' b → person m) :=
    funext fun m => funext fun k' => propext
      ⟨fun ⟨hp, t, ht⟩ => ⟨hp, t, ht, fun m' _ _ h => by cases h; exact hp⟩,
       fun ⟨hp, t, ht, _⟩ => ⟨hp, t, ht⟩⟩
  unfold reached
  rw [← he]
  exact ⟨fun ⟨o, h1, h2⟩ => ⟨o, (ho o).1 h1, h2⟩, fun ⟨o, h1, h2⟩ => ⟨o, (ho o).2 h1, h2⟩⟩

/-- A count is met only by persons' statements: statements by programs, in any number, are no voice. -/
theorem p3_program_voice_not_counted (S : Held N Dig Id) (m : List N) (n : Nat) (rid : Id) :
    countAt person S m n rid ↔
      countAt person (fun e => S e ∧ ∀ i v, e.r = .stmt i v → person v) m n rid := by
  unfold countAt voices has
  constructor
  · intro ⟨l, h1, h2, h3⟩
    refine ⟨l, h1, h2, fun v hv => ?_⟩
    have ⟨a, b, t, c⟩ := h3 v hv
    exact ⟨a, b, t, c, fun _ _ h => by cases h; exact b⟩
  · intro ⟨l, h1, h2, h3⟩
    exact ⟨l, h1, h2, fun v hv => let ⟨a, b, t, c, _⟩ := h3 v hv; ⟨a, b, t, c⟩⟩

/-! ### P4 an effect-capable unit needs the count, or the host's own owner on that host -/

theorem p4_effect_needs_count_or_owner (S : Held N Dig Id) (host : N) (now : Nat) (e : Ent N Dig Id)
    (u : UnitRow N Dig Id) (h : rowAdmits person S host now e u) (hef : effectful u) :
    (∃ a, u.iss = .author a ∧ owner person S host a ∧ u.self = true) ∨
    (∃ hd g m n, u.iss = .head hd ∧ has S (.roster hd g m n) ∧
      ∃ l : List N, l.Nodup ∧ 2 ≤ l.length ∧ ∀ v, v ∈ l → v ∈ m ∧ person v ∧ has S (.stmt u.id v)) := by
  have ⟨_, _, hst, his, _⟩ := h
  unfold issuerStands at his
  cases hiss : u.iss with
  | author a =>
    rw [hiss] at his
    exact Or.inl ⟨a, rfl, his.2.2 hef, hst.2.2.2 a hiss hef⟩
  | head hd =>
    rw [hiss] at his
    have ⟨g, m, n, hr, _, l, hnd, hlen, hl⟩ := his
    exact Or.inr ⟨hd, g, m, n, rfl, hr, l, hnd, by simp [FLOOR] at hlen; omega, hl⟩

/-- One person's row that names an effect at any scope but `self` is Invalid. -/
theorem p4_owner_row_self (u : UnitRow N Dig Id) (a : N) (ha : u.iss = .author a) (hef : effectful u)
    (hs : u.self = false) : ¬ static u :=
  fun h => by have := h.2.2.2 a ha hef; rw [hs] at this; exact absurd this (by decide)

/-- One member is not a count, whatever the group declares. -/
theorem p4_one_member_not_a_count (S : Held N Dig Id) (m : List N) (n : Nat) (rid : Id) (a : N)
    (h1 : ∀ v, voices person S rid v → v = a) : ¬ countAt person S m n rid := by
  intro ⟨l, hnd, hlen, hl⟩
  have := nodup_one a l hnd (fun v hv => h1 v (hl v hv).2)
  simp [FLOOR] at hlen; omega

/-- A counted row whose head is not held admits nothing (it waits). -/
theorem p4_head_not_held (S : Held N Dig Id) (host : N) (now : Nat) (e : Ent N Dig Id)
    (u : UnitRow N Dig Id) (hd : Id) (ha : u.iss = .head hd) (hn : ∀ g m n, ¬ has S (.roster hd g m n)) :
    ¬ rowAdmits person S host now e u := by
  intro h
  have his := h.2.2.2.1
  unfold issuerStands at his
  rw [ha] at his
  have ⟨g, m, n, hr, _⟩ := his
  exact hn g m n hr

/-- A unit that only computes may be one person's: the owner's walk reaching a signing person admits it. -/
theorem p4_compute_one_person (S : Held N Dig Id) (host : N) (now : Nat) (e : Ent N Dig Id)
    (u : UnitRow N Dig Id) (a : N) (hS : S e) (hr : e.r = .unit u) (ha : u.iss = .author a)
    (hst : static u) (hef : ¬ effectful u) (hv : voices person S u.id a) (hre : reached person S host a)
    (hl : leaseOK now e u) (hw : ¬ withdrawn person S u) : rowAdmits person S host now e u := by
  refine ⟨hS, hr, hst, ?_, hl, hw⟩
  unfold issuerStands; rw [ha]; exact ⟨hv, hre, fun x => absurd x hef⟩

/-! ### P5 a lease ends execution on the host's own clock -/

theorem p5_lease (S : Held N Dig Id) (host : N) (now : Nat) (e : Ent N Dig Id) (u : UnitRow N Dig Id)
    (h : rowAdmits person S host now e u) :
    u.start ≤ now ∧ now < u.ends ∧ now < e.t + LEASE ∧ u.ends - u.start ≤ LEASE :=
  ⟨h.2.2.2.2.1.1, h.2.2.2.2.1.2.1, h.2.2.2.2.1.2.2, h.2.2.1.2.2.1⟩

/-- A host that hears nothing more stops within one lease: once every unit row naming `d` was first held
    LEASE or more before `now`, the unit does not run (outside its build). -/
theorem p5_stops_within_one_lease (W : List (Ent N Dig Id)) (host : N) (d : Dig) (now : Nat)
    (hold : ∀ e u, held W now e → e.r = .unit u → u.unit = d → e.t + LEASE ≤ now)
    (hb : ¬ builtIn (held W now) d) : ¬ runs person W host d now := by
  intro h
  cases h with
  | inl h => exact hb h
  | inr h =>
    have ⟨e, u, hu, hd⟩ := h
    have := hold e u hu.1 hu.2.1 hd
    have := hu.2.2.2.2.1.2.2
    omega

/-! ### P6 a withdrawal ends it forward -/

theorem p6_author_withdrawal_ends (S : Held N Dig Id) (host : N) (now : Nat) (e : Ent N Dig Id)
    (u : UnitRow N Dig Id) (a : N) (ha : u.iss = .author a) (wid : Id) (hd : Option Id)
    (hw : has S (.withdraw wid u.id hd)) (hv : voices person S wid a) : ¬ rowAdmits person S host now e u :=
  fun h => h.2.2.2.2.2 ⟨wid, hd, hw, by rw [ha]; exact hv⟩

/-- Withdrawals, and any rows, first held after `now` change nothing at `now`: a withdrawal reaches forward
    from the host's receipt of it. -/
theorem p6_forward (W L : List (Ent N Dig Id)) (now : Nat) (hL : ∀ e, e ∈ L → now < e.t) :
    held (W ++ L) now = held W now := by
  funext e
  apply propext
  unfold held
  constructor
  · intro ⟨hm, ht⟩
    cases List.mem_append.1 hm with
    | inl h => exact ⟨h, ht⟩
    | inr h => have := hL e h; omega
  · intro ⟨hm, ht⟩; exact ⟨List.mem_append.2 (Or.inl hm), ht⟩

/-- So the unit runs, or may act, at `now` exactly as it did before any later row arrived. -/
theorem p6_forward_runs (W L : List (Ent N Dig Id)) (host : N) (d : Dig) (now : Nat)
    (hL : ∀ e, e ∈ L → now < e.t) : runs person (W ++ L) host d now ↔ runs person W host d now := by
  unfold runs; rw [p6_forward W L now hL]

/-- A counted admission is withdrawn only by the count at its own head; a stranger's withdrawal of an
    authored row is no voice of its author. -/
theorem p6_count_withdrawn_by_count (S : Held N Dig Id) (u : UnitRow N Dig Id) (h : withdrawn person S u) :
    (∀ a, u.iss = .author a → ∃ wid hd, has S (.withdraw wid u.id hd) ∧ person a ∧ has S (.stmt wid a)) ∧
    (∀ hd, u.iss = .head hd → ∃ wid, has S (.withdraw wid u.id (some hd)) ∧ countMet person S hd wid) := by
  have ⟨wid, hd', hw, hm⟩ := h
  refine ⟨fun a ha => ?_, fun hd ha => ?_⟩
  · rw [ha] at hm; exact ⟨wid, hd', hw, hm⟩
  · rw [ha] at hm; exact ⟨wid, hm.1 ▸ hw, hm.2⟩

/-! ### P7 a halt stops every effect from receipt -/

theorem p7_halt_stops_effects (W : List (Ent N Dig Id)) (host : N) (d : Dig) (cap : Cap) (now : Nat)
    (p : Option (List Cap)) (h : may person accord W host d cap now p) (hc : cap.effect) :
    ¬ halted person accord (held W now) host now := h.2.2 hc

/-- Computing and reading continue: the gate for a capability that is not an effect does not read the halt. -/
theorem p7_compute_unhalted (W : List (Ent N Dig Id)) (host : N) (d : Dig) (cap : Cap) (now : Nat)
    (p : Option (List Cap)) (hc : ¬ cap.effect) :
    may person accord W host d cap now p ↔ caps person W host d now cap ∧ ∀ q, p = some q → cap ∈ q :=
  ⟨fun h => ⟨h.1, h.2.1⟩, fun h => ⟨h.1, h.2, fun x => absurd x hc⟩⟩

/-- Only a holder's halt latches: a stranger's halt stops nothing. -/
theorem p7_halter_is_holder (S : Held N Dig Id) (host : N) (now : Nat) (h : halted person accord S host now) :
    ∃ hs hid hb th, has S (.bundle hs) ∧ S ⟨th, .halt hid hb⟩ ∧ hb ∈ hs :=
  let ⟨hs, hid, hb, th, h1, h2, h3, _⟩ := h
  ⟨hs, hid, hb, th, h1, h2, h3⟩

/-- A lone halt lapses at its fuse: with no confirmation held, a halt latches only within FUSE of receipt. -/
theorem p7_lone_halt_lapses (S : Held N Dig Id) (host : N) (now : Nat)
    (hno : ∀ lid hid, ¬ has S (.life lid hid false)) (h : halted person accord S host now) :
    ∃ hid hb th, S ⟨th, .halt hid hb⟩ ∧ now < th + FUSE := by
  have ⟨_, hid, hb, th, _, h2, _, _, _, h6⟩ := h
  cases h6 with
  | inl h6 => exact ⟨hid, hb, th, h2, h6⟩
  | inr h6 => have ⟨lid, hl, _⟩ := h6; exact absurd hl (hno lid hid)

/-- One holder resumes nothing where there are two holders or more. -/
theorem p7_one_holder_does_not_resume (hs : List N) (vs : N → Prop) (a : N) (h1 : ∀ v, vs v → v = a)
    (h2 : 2 ≤ hs.length) : ¬ majority hs vs := by
  intro ⟨l, hnd, hlt, hl⟩
  have := nodup_one a l hnd (fun v hv => h1 v (hl v hv).1)
  omega

/-- Programs do not resume: with no person's statement on the resumption, no majority. -/
theorem p7_programs_do_not_resume (S : Held N Dig Id) (hs : List N) (lid : Id)
    (hp : ∀ v, has S (.stmt lid v) → ¬ person v) : ¬ majority hs (voices person S lid) := by
  intro ⟨l, _, hlt, hl⟩
  match l, hlt, hl with
  | [], hlt, _ => exact absurd hlt (by simp)
  | v :: _, _, hl => have ⟨⟨hpv, hv⟩, _⟩ := hl v (List.mem_cons_self _ _); exact hp v hv hpv

/-! ### P8 capabilities only attenuate -/

theorem p8_attenuate (W : List (Ent N Dig Id)) (host : N) (d : Dig) (cap : Cap) (now : Nat) (p : List Cap)
    (h : may person accord W host d cap now (some p)) : cap ∈ p ∧ caps person W host d now cap :=
  ⟨h.2.1 p rfl, h.1⟩

/-- A submitted unit runs only by the receiving host's own admission; the sender's standing carries nothing. -/
theorem p8_submit_receiver (W : List (Ent N Dig Id)) (s s' r : N) (d : Dig) (now : Nat) :
    (submit person W s r d now ↔ runs person W r d now) ∧ (submit person W s r d now ↔ submit person W s' r d now) :=
  ⟨Iff.rfl, Iff.rfl⟩

/-! ### P14 a unit of the attested build runs under the build alone -/

theorem p14_build_runs (W : List (Ent N Dig Id)) (host : N) (d : Dig) (now : Nat)
    (h : builtIn (held W now) d) : runs person W host d now ∧ ∀ c, caps person W host d now c :=
  ⟨Or.inl h, fun _ => Or.inl h⟩

theorem p14_unblessed_runs_nothing (W : List (Ent N Dig Id)) (host : N) (d : Dig) (now : Nat)
    (hb : ∀ us, has (held W now) (.build us true) → d ∉ us)
    (hrows : ∀ e u, held W now e → e.r = .unit u → u.unit ≠ d) : ¬ runs person W host d now :=
  p2_digest_bound person W host d now hrows (fun ⟨us, h1, h2⟩ => hb us h1 h2)

/-! ### P12 every answer is the same in every arrival order (code scope) -/

theorem held_perm (W W' : List (Ent N Dig Id)) (h : W.Perm W') (now : Nat) : held W now = held W' now :=
  funext fun _ => propext ⟨fun ⟨a, b⟩ => ⟨h.mem_iff.1 a, b⟩, fun ⟨a, b⟩ => ⟨h.mem_iff.2 a, b⟩⟩

theorem p12_runs_perm (W W' : List (Ent N Dig Id)) (h : W.Perm W') (host : N) (d : Dig) (now : Nat) :
    runs person W host d now ↔ runs person W' host d now := by
  unfold runs; rw [held_perm W W' h now]

theorem p12_may_perm (W W' : List (Ent N Dig Id)) (h : W.Perm W') (host : N) (d : Dig) (cap : Cap)
    (now : Nat) (p : Option (List Cap)) :
    may person accord W host d cap now p ↔ may person accord W' host d cap now p := by
  unfold may caps; rw [held_perm W W' h now]

end Props

section PropsAgent

variable {N Dig Id L D : Type} (person : N → Prop)

/-! ### P9 dispatch executes only the reviewed fingerprint -/

theorem p9_needs_four_passes (S : GSet N Dig Id L D) (th : Id) (fp : Dig) (g : Option Id)
    (h : dispatch person S th fp g) :
    ∃ p : Review Dig Id L, S (.review p) ∧ p.thought = th ∧ p.fp = fp ∧ p.passed = true ∧ ∀ f, f ∈ p.facs :=
  let ⟨⟨p, h1, h2, h3, h4, h5, _⟩, _⟩ := h
  ⟨p, h1, h2, h3, h4, h5⟩

/-- With the fingerprint injective (SHA-256 over the call's CDE encoding assumed collision-free), a changed
    call has no record: what executes is what was reviewed. -/
theorem p9_changed_call {C : Type} (fpOf : C → Dig) (hinj : ∀ x y, fpOf x = fpOf y → x = y)
    (S : GSet N Dig Id L D) (th : Id) (c c' : C) (hc : c' ≠ c) (g : Option Id)
    (hrec : ∀ p : Review Dig Id L, S (.review p) → p.thought = th → p.passed = true → p.fp = fpOf c) :
    ¬ dispatch person S th (fpOf c') g := by
  intro h
  have ⟨p, h1, h2, h3, h4, _⟩ := p9_needs_four_passes person S th _ g h
  exact hc (hinj c' c (h3.symm.trans (hrec p h1 h2 h4)))

theorem p9_objection_discharged (S : GSet N Dig Id L D) (th : Id) (fp : Dig) (g : Option Id)
    (h : dispatch person S th fp g) (o : Review Dig Id L) (ho : S (.review o)) (ht : o.thought = th)
    (hp : o.passed = false) (hf : o.fp = fp) :
    ∃ p : Review Dig Id L, S (.review p) ∧ p.fp = fp ∧ ∃ ev, (o.id, ev) ∈ p.discharges ∧ trusted person S ev :=
  let ⟨⟨p, h1, _, h3, _, _, h6, _⟩, _⟩ := h
  ⟨p, h1, h3, h6 o ho ht hp hf⟩

/-- The drafter's own word discharges nothing: a row discharges only when a person signed it. -/
theorem p9_discharge_by_person (S : GSet N Dig Id L D) (ev : Id) (h : trusted person S ev) :
    ∃ ag b d fp, S (.resp ev ag true b d fp) ∧ person b :=
  let ⟨ag, b, d, fp, h1, h2, _⟩ := h
  ⟨ag, b, d, fp, h1, h2⟩

theorem p9_objection_carried (S : GSet N Dig Id L D) (th : Id) (fp : Dig) (g : Option Id)
    (h : dispatch person S th fp g) :
    ∃ p : Review Dig Id L, S (.review p) ∧ p.fp = fp ∧ ∀ o : Review Dig Id L, S (.review o) →
      o.thought = th → o.passed = false → o.fp ≠ fp → o.id ∈ p.considered :=
  let ⟨⟨p, h1, _, h3, _, _, _, h7⟩, _⟩ := h
  ⟨p, h1, h3, h7⟩

theorem p9_approval_bound (S : GSet N Dig Id L D) (th : Id) (fp : Dig) (g : Id)
    (h : dispatch person S th fp (some g)) : ∃ ag b d, S (.resp g ag true b d (some fp)) :=
  h.2 g rfl

/-! ### P10 a profile loads only when its derived digest matches -/

theorem p10_chain_unique (S : GSet N Dig Id L D) (agent : N) :
    ∀ cur l l', IsChain person S agent cur l → IsChain person S agent cur l' → l = l' := by
  intro cur l l' h
  induction h generalizing l' with
  | stop cur hn =>
    intro h'
    cases h' with
    | stop => rfl
    | next _ a _ hs hu _ => exact absurd ⟨a, hs, hu⟩ hn
  | next cur a l hs hu _ ih =>
    intro h'
    cases h' with
    | stop _ hn => exact absurd ⟨a, hs, hu⟩ hn
    | next _ a' l'' hs' _ hc' =>
      have e : a' = a := hu a' hs'
      subst e
      rw [ih l'' hc']

/-- Exactly one list of digests loads: the same digests in another order, an extra amendment, or one less do
    not. -/
theorem p10_loads_unique (S : GSet N Dig Id L D) (agent : N) (x y : List Dig)
    (hx : loads person S agent x) (hy : loads person S agent y)
    (htpl : ∀ t t', S (.template agent t true) → S (.template agent t' true) → t = t') : x = y := by
  rcases hx with ⟨ha, l, hl, rfl⟩ | ⟨hna, t, ht, rfl⟩ <;> rcases hy with ⟨ha', l', hl', rfl⟩ | ⟨hna', t', ht', rfl⟩
  · rw [p10_chain_unique person S agent none l l' hl hl']
  · exact absurd ha hna'
  · exact absurd ha' hna
  · rw [htpl t t' ht ht']

/-- Every link the chain counts is held and authorized: approved by a person who is the steward or seated by
    it, with the link's exact digest. An amendment approved by the agent's own key counts for nothing. -/
theorem p10_chain_authorized (S : GSet N Dig Id L D) (agent : N) :
    ∀ cur l, IsChain person S agent cur l → ∀ a, a ∈ l → S (.amend a) ∧ authorized person S a := by
  intro cur l h
  induction h with
  | stop => intro a ha; exact absurd ha (List.not_mem_nil a)
  | next _ a _ hs _ _ ih =>
    intro b hb
    cases List.mem_cons.1 hb with
    | inl e => subst e; exact ⟨hs.1, hs.2.2.1⟩
    | inr h => exact ih b h

/-- The base link approves the attested template's exact digest. -/
theorem p10_base_is_template (S : GSet N Dig Id L D) (agent : N) (a : Link N Dig Id) (l : List (Link N Dig Id))
    (h : IsChain person S agent none (a :: l)) : ∃ tpl, S (.template agent tpl true) ∧ a.digest = tpl := by
  cases h with
  | next _ _ _ hs _ _ => exact hs.2.2.2.2 rfl

/-- A fork counts neither branch: where two links name one predecessor, the chain stops before them. -/
theorem p10_fork_stops (S : GSet N Dig Id L D) (agent : N) (cur : Option Id) (a b : Link N Dig Id)
    (ha : step person S agent cur a) (hb : step person S agent cur b) (hne : a ≠ b) (l : List (Link N Dig Id))
    (h : IsChain person S agent cur l) : l = [] := by
  cases h with
  | stop => rfl
  | next _ c _ _ hu _ => exact absurd ((hu a ha).trans (hu b hb).symm) hne

/-- A response signed by a program's key authorizes nothing. -/
theorem p10_program_approval (S : GSet N Dig Id L D) (a : Link N Dig Id)
    (hp : ∀ b fp, S (.resp a.byResp a.agent true b (some a.digest) fp) → ¬ person b) :
    ¬ authorized person S a :=
  fun ⟨b, fp, _, h1, h2, _⟩ => hp b fp h1 h2

/-- With no base link the attested template alone loads, and no amendment counts. -/
theorem p10_unanchored (S : GSet N Dig Id L D) (agent : N) (hna : ¬ anchored person S agent) (x : List Dig) :
    loads person S agent x ↔ ∃ tpl, S (.template agent tpl true) ∧ x = [tpl] :=
  ⟨fun h => h.elim (fun h => absurd h.1 hna) (fun h => h.2), fun h => Or.inr ⟨hna, h⟩⟩

/-! ### P11 a result is no more trusted than what it derives from -/

theorem p11_least (S : GSet N Dig Id L D) (r : Id) (v : Nat) :
    trustAtLeast S r v ↔ ∀ a tr lb ns, From S r a → S (.data a tr lb ns) → v ≤ tr := Iff.rfl

/-- Trust is not declared by the row: a row whose own trust is VERIFIED but which derives from an untrusted
    row is untrusted. -/
theorem p11_own_trust_not_enough (S : GSet N Dig Id L D) (r a : Id) (tr : Nat) (lb : L) (ns : List Id)
    (hf : From S r a) (ha : S (.data a tr lb ns)) (ht : tr < VERIFIED) : ¬ trustAtLeast S r VERIFIED :=
  fun h => absurd (h a tr lb ns hf ha) (by omega)

/-- The effect gate: the pass record declares every untrusted kind the arguments derive from; claimed
    authority needs the approving row naming the fingerprint; a row binding others needs their
    acknowledgements. -/
theorem p11_effect_gate (S : GSet N Dig Id L D) (agent : N) (th : Id) (fp : Dig) (args : Id)
    (auth : Auth Id D) (binds : List N) (h : mayEffect person S agent th fp args auth binds) :
    (∃ p : Review Dig Id L, S (.review p) ∧ p.fp = fp ∧ ∀ lb, untrustedLabel S args lb → lb ∈ p.derived) ∧
    authorityOK person S agent fp auth ∧
    (∀ k, k ∈ binds → S (.ack fp k)) := by
  have ⟨⟨p, h1, _, _, h4, h5⟩, h6, h7⟩ := h
  refine ⟨⟨p, h1, h4, fun lb hl => ?_⟩, h6, h7⟩
  have ⟨a, tr, ns, hf, hd, ht⟩ := hl
  exact h5 (p11_own_trust_not_enough S args a tr lb ns hf hd ht) lb hl

/-- Trusted arguments need no declaration. -/
theorem p11_trusted_needs_no_declaration (S : GSet N Dig Id L D) (args : Id) (h : trustAtLeast S args VERIFIED)
    (lb : L) : ¬ untrustedLabel S args lb :=
  fun ⟨a, tr, ns, hf, hd, ht⟩ => p11_own_trust_not_enough S args a tr lb ns hf hd ht h

/-! ### P11, the standing delegation (Constitution 4040d0b; CC 2.7.11 "Derived trust", CC 4.5.5 (b)) -/

/-- An act that needs no role reads no authority row: it is done under the role the owner-binding delegates. -/
theorem p11_no_role_reads_no_authority (S : GSet N Dig Id L D) (agent : N) (th : Id) (fp : Dig) (args : Id)
    (binds : List N) :
    mayEffect person S agent th fp args .none binds ↔
      (∃ p : Review Dig Id L, S (.review p) ∧ p.thought = th ∧ p.passed = true ∧ p.fp = fp ∧
        (¬ trustAtLeast S args VERIFIED → ∀ lb, untrustedLabel S args lb → lb ∈ p.derived)) ∧
      (∀ k, k ∈ binds → S (.ack fp k)) :=
  ⟨fun ⟨a, _, c⟩ => ⟨a, c⟩, fun ⟨a, c⟩ => ⟨a, trivial, c⟩⟩

/-- A row that is a `deferral:response`. -/
def isResp (r : GRow N Dig Id L D) : Prop := ∃ i ag ok b d f, r = .resp i ag ok b d f

/-- The held rows with every response taken out. -/
def noResp (S : GSet N Dig Id L D) : GSet N Dig Id L D := fun r => S r ∧ ¬ isResp r

theorem from_noResp (S : GSet N Dig Id L D) (x y : Id) : From (noResp S) x y ↔ From S x y := by
  constructor
  · intro hf
    induction hf with
    | refl => exact From.refl _
    | step a c tr lb ns _ hd hc ih => exact From.step _ a c tr lb ns ih hd.1 hc
  · intro hf
    induction hf with
    | refl => exact From.refl _
    | step a c tr lb ns _ hd hc ih =>
      exact From.step _ a c tr lb ns ih ⟨hd, fun ⟨_, _, _, _, _, _, e⟩ => by cases e⟩ hc

/-- **An act within a standing delegation needs no approval of its own.** Under a delegation the gate reads no
    `deferral:response` at all: take every response out of the held rows and the answer is the same. The
    delegation's signer approves no single act under it. -/
theorem p11_delegation_needs_no_approval (S : GSet N Dig Id L D) (agent : N) (th : Id) (fp : Dig) (args : Id)
    (rid : Id) (duty : D) (binds : List N) :
    mayEffect person S agent th fp args (.under rid duty) binds ↔
      mayEffect person (noResp S) agent th fp args (.under rid duty) binds := by
  have nr : ∀ r, ¬ isResp r → (noResp S r ↔ S r) := fun r h => ⟨And.left, fun x => ⟨x, h⟩⟩
  have hrv : ∀ p, noResp S (.review p) ↔ S (.review p) :=
    fun p => nr _ (fun ⟨_, _, _, _, _, _, e⟩ => by cases e)
  have hda : ∀ a tr lb ns, noResp S (.data a tr lb ns) ↔ S (.data a tr lb ns) :=
    fun _ _ _ _ => nr _ (fun ⟨_, _, _, _, _, _, e⟩ => by cases e)
  have hdl : ∀ b sc, noResp S (.deleg rid agent b sc) ↔ S (.deleg rid agent b sc) :=
    fun _ _ => nr _ (fun ⟨_, _, _, _, _, _, e⟩ => by cases e)
  have hse : ∀ b c, noResp S (.seat agent b c) ↔ S (.seat agent b c) :=
    fun _ _ => nr _ (fun ⟨_, _, _, _, _, _, e⟩ => by cases e)
  have hbi : ∀ b, noResp S (.bind agent b) ↔ S (.bind agent b) :=
    fun _ => nr _ (fun ⟨_, _, _, _, _, _, e⟩ => by cases e)
  have hwd : noResp S (.withdraw rid) ↔ S (.withdraw rid) := nr _ (fun ⟨_, _, _, _, _, _, e⟩ => by cases e)
  have hak : ∀ k, noResp S (.ack fp k) ↔ S (.ack fp k) := fun _ => nr _ (fun ⟨_, _, _, _, _, _, e⟩ => by cases e)
  have htr : trustAtLeast (noResp S) args VERIFIED ↔ trustAtLeast S args VERIFIED := by
    unfold trustAtLeast
    exact ⟨fun h a tr lb ns hf hd => h a tr lb ns ((from_noResp S _ _).2 hf) ((hda _ _ _ _).2 hd),
      fun h a tr lb ns hf hd => h a tr lb ns ((from_noResp S _ _).1 hf) ((hda _ _ _ _).1 hd)⟩
  have hul : ∀ lb, untrustedLabel (noResp S) args lb ↔ untrustedLabel S args lb := by
    intro lb
    unfold untrustedLabel
    exact ⟨fun ⟨a, tr, ns, hf, hd, ht⟩ => ⟨a, tr, ns, (from_noResp S _ _).1 hf, (hda _ _ _ _).1 hd, ht⟩,
      fun ⟨a, tr, ns, hf, hd, ht⟩ => ⟨a, tr, ns, (from_noResp S _ _).2 hf, (hda _ _ _ _).2 hd, ht⟩⟩
  unfold mayEffect authorityOK delegated
  simp only [hrv, hdl, hse, hbi, hwd, hak, htr, hul]

/-- What a delegation arm needs, all of it: a delegation onto this agent, signed by a person seated over it, not
    withdrawn, whose scope names the act's duty. -/
theorem p11_delegation_needs (S : GSet N Dig Id L D) (agent : N) (th : Id) (fp : Dig) (args : Id) (rid : Id)
    (duty : D) (binds : List N) (h : mayEffect person S agent th fp args (.under rid duty) binds) :
    ∃ b sc, S (.deleg rid agent b sc) ∧ person b ∧ ((∃ c, S (.seat agent b c)) ∨ S (.bind agent b)) ∧
      ¬ S (.withdraw rid) ∧ duty ∈ sc :=
  h.2.1

/-- **The plant `delegation_any_scope`, refuted.** A delegation whose scope does not name the act's duty licenses
    nothing: a delegation of `moderate` is no authority for a `takedown`. -/
theorem p11_scope_must_name_duty (S : GSet N Dig Id L D) (agent : N) (th : Id) (fp : Dig) (args : Id) (rid : Id)
    (duty : D) (binds : List N) (hs : ∀ b sc, S (.deleg rid agent b sc) → duty ∉ sc) :
    ¬ mayEffect person S agent th fp args (.under rid duty) binds :=
  fun h =>
    let ⟨b, sc, h1, _, _, _, h5⟩ := p11_delegation_needs person S agent th fp args rid duty binds h
    hs b sc h1 h5

/-- A withdrawn delegation licenses nothing. -/
theorem p11_withdrawn_delegation (S : GSet N Dig Id L D) (agent : N) (th : Id) (fp : Dig) (args : Id)
    (rid : Id) (duty : D) (binds : List N) (hw : S (.withdraw rid)) :
    ¬ mayEffect person S agent th fp args (.under rid duty) binds :=
  fun h =>
    let ⟨_, _, _, _, _, h4, _⟩ := p11_delegation_needs person S agent th fp args rid duty binds h
    h4 hw

/-- A delegation signed by a program's key licenses nothing. -/
theorem p11_program_delegation (S : GSet N Dig Id L D) (agent : N) (th : Id) (fp : Dig) (args : Id)
    (rid : Id) (duty : D) (binds : List N) (hp : ∀ b sc, S (.deleg rid agent b sc) → ¬ person b) :
    ¬ mayEffect person S agent th fp args (.under rid duty) binds :=
  fun h =>
    let ⟨b, sc, h1, h2, _⟩ := p11_delegation_needs person S agent th fp args rid duty binds h
    hp b sc h1 h2

/-- A delegation onto another agent licenses nothing for this one. -/
theorem p11_other_agent_delegation (S : GSet N Dig Id L D) (agent : N) (th : Id) (fp : Dig) (args : Id)
    (rid : Id) (duty : D) (binds : List N) (ho : ∀ a' b sc, S (.deleg rid a' b sc) → a' ≠ agent) :
    ¬ mayEffect person S agent th fp args (.under rid duty) binds :=
  fun h =>
    let ⟨b, sc, h1, _⟩ := p11_delegation_needs person S agent th fp args rid duty binds h
    ho agent b sc h1 rfl

/-- An act within a live delegation of its duty is licensed by the pass record, the delegation and the
    acknowledgements alone. -/
theorem p11_delegation_licenses (S : GSet N Dig Id L D) (agent : N) (th : Id) (fp : Dig) (args : Id)
    (rid : Id) (duty : D) (binds : List N) (p : Review Dig Id L) (hp : S (.review p)) (ht : p.thought = th)
    (hps : p.passed = true) (hf : p.fp = fp) (hdecl : ∀ lb, untrustedLabel S args lb → lb ∈ p.derived)
    (hd : delegated person S agent rid duty) (hack : ∀ k, k ∈ binds → S (.ack fp k)) :
    mayEffect person S agent th fp args (.under rid duty) binds :=
  ⟨⟨p, hp, ht, hps, hf, fun _ => hdecl⟩, hd, hack⟩

/-- **Authority claimed is rooted in a person.** An act that claims authority, by either arm, rests on a row a
    person signed: the delegation's signer, seated over this agent; or the approving row's signer, seated over
    the agent that row names. -/
theorem p11_authority_rooted_in_person (S : GSet N Dig Id L D) (agent : N) (th : Id) (fp : Dig) (args : Id)
    (auth : Auth Id D) (binds : List N) (hauth : auth ≠ .none)
    (h : mayEffect person S agent th fp args auth binds) :
    ∃ b, person b ∧
      ((∃ rid duty sc, auth = .under rid duty ∧ S (.deleg rid agent b sc) ∧
          ((∃ c, S (.seat agent b c)) ∨ S (.bind agent b))) ∨
       (∃ c ag d f, auth = .claims c ∧ S (.resp c ag true b d f) ∧
          ((∃ c', S (.seat ag b c')) ∨ S (.bind ag b)))) := by
  have ha := h.2.1
  cases auth with
  | none => exact absurd rfl hauth
  | under rid duty =>
    have ⟨b, sc, h1, h2, h3, _⟩ := ha
    exact ⟨b, h2, Or.inl ⟨rid, duty, sc, rfl, h1, h3⟩⟩
  | claims c =>
    have ⟨_, _, _, _, _, ⟨ag, b, d, f, h1, h2, h3⟩⟩ := ha
    exact ⟨b, h2, Or.inr ⟨c, ag, d, f, rfl, h1, h3⟩⟩

/-- The plant's reading (`delegation_any_scope`): the same check with the scope not read. -/
def delegatedAnyScope (S : GSet N Dig Id L D) (agent : N) (rid : Id) : Prop :=
  ∃ b sc, S (.deleg rid agent b sc) ∧ person b ∧ ((∃ c, S (.seat agent b c)) ∨ S (.bind agent b)) ∧
    ¬ S (.withdraw rid)

end PropsAgent

/-- **The plant tells.** In a world with one live delegation of `moderate` (`true`) by the agent's steward, the
    plant's reading licenses a `takedown` (`false`) under it, and the rule does not. -/
theorem delegation_any_scope_differs :
    delegatedAnyScope (N := Unit) (Dig := Unit) (Id := Unit) (L := Unit) (fun _ => True)
        (fun r => r = .deleg () () () [true] ∨ r = .bind () ()) () () ∧
      ¬ delegated (N := Unit) (Dig := Unit) (Id := Unit) (L := Unit) (fun _ => True)
        (fun r => r = .deleg () () () [true] ∨ r = .bind () ()) () () false := by
  refine ⟨⟨(), [true], Or.inl rfl, trivial, Or.inr (Or.inr rfl), fun h => ?_⟩, ?_⟩
  · cases h with
    | inl h => cases h
    | inr h => cases h
  · intro ⟨_, sc, h1, _, _, _, h5⟩
    cases h1 with
    | inl h => cases h; exact absurd h5 (by decide)
    | inr h => cases h

/-- **Qualification (2), as revised.** An effect that needs no role needs no person either: with no key a person
    and no delegation or approving row held, a pass record licenses it. -/
theorem effect_needs_no_person :
    mayEffect (N := Unit) (Dig := Unit) (Id := Unit) (L := Unit) (D := Unit) (fun _ => False)
      (fun r => r = .review ⟨(), (), (), true, Fac.all, [], [], []⟩) () () () () .none [] := by
  refine ⟨⟨⟨(), (), (), true, Fac.all, [], [], []⟩, rfl, rfl, rfl, rfl, fun _ lb hl => ?_⟩, trivial,
    fun k hk => absurd hk (List.not_mem_nil k)⟩
  have ⟨_, _, _, _, hd, _⟩ := hl
  cases hd

section PropsAgent2

variable {N Dig Id L D : Type} (person : N → Prop)

/-! ### P12 every answer is the same in every arrival order (agent scopes) -/

theorem set_perm {α β : Type} (F : (α → Prop) → β) (l l' : List α) (h : l.Perm l') :
    F (fun r => r ∈ l) = F (fun r => r ∈ l') := by
  have : (fun r => r ∈ l) = (fun r => r ∈ l') := funext fun _ => propext h.mem_iff
  rw [this]

theorem p12_loads_perm (l l' : List (GRow N Dig Id L D)) (h : l.Perm l') (agent : N) (x : List Dig) :
    loads person (fun r => r ∈ l) agent x ↔ loads person (fun r => r ∈ l') agent x := by
  rw [set_perm (fun S => loads person S agent x) l l' h]

theorem p12_dispatch_perm (l l' : List (GRow N Dig Id L D)) (h : l.Perm l') (th : Id) (fp : Dig) (g : Option Id) :
    dispatch person (fun r => r ∈ l) th fp g ↔ dispatch person (fun r => r ∈ l') th fp g := by
  rw [set_perm (fun S => dispatch person S th fp g) l l' h]

theorem p12_effect_perm (l l' : List (GRow N Dig Id L D)) (h : l.Perm l') (agent : N) (th : Id) (fp : Dig)
    (args : Id) (auth : Auth Id D) (binds : List N) :
    mayEffect person (fun r => r ∈ l) agent th fp args auth binds ↔
      mayEffect person (fun r => r ∈ l') agent th fp args auth binds := by
  rw [set_perm (fun S => mayEffect person S agent th fp args auth binds) l l' h]

end PropsAgent2

end Admission

#print axioms Admission.nodup_len_le
#print axioms Admission.four_is_all
#print axioms Admission.one_voice_is_one_signature
#print axioms Admission.count_not_one_voice
#print axioms Admission.p13_one_voice_clauses
#print axioms Admission.code_is_walk
#print axioms Admission.code_effect_body
#print axioms Admission.profile_is_walk
#print axioms Admission.action_is_walk
#print axioms Admission.action_needs_no_person
#print axioms Admission.three_admissions_one_walk
#print axioms Admission.p1_runs_needs_admission
#print axioms Admission.p1_issuer_reached
#print axioms Admission.p1_no_owner_runs_nothing
#print axioms Admission.p2_digest_bound
#print axioms Admission.p2_changed_unit
#print axioms Admission.p3_program_issues_nothing
#print axioms Admission.p3_program_edges_carry_nothing
#print axioms Admission.p3_program_voice_not_counted
#print axioms Admission.p4_effect_needs_count_or_owner
#print axioms Admission.p4_owner_row_self
#print axioms Admission.p4_one_member_not_a_count
#print axioms Admission.p4_head_not_held
#print axioms Admission.p4_compute_one_person
#print axioms Admission.p5_lease
#print axioms Admission.p5_stops_within_one_lease
#print axioms Admission.p6_author_withdrawal_ends
#print axioms Admission.p6_forward
#print axioms Admission.p6_forward_runs
#print axioms Admission.p6_count_withdrawn_by_count
#print axioms Admission.p7_halt_stops_effects
#print axioms Admission.p7_compute_unhalted
#print axioms Admission.p7_halter_is_holder
#print axioms Admission.p7_lone_halt_lapses
#print axioms Admission.p7_one_holder_does_not_resume
#print axioms Admission.p7_programs_do_not_resume
#print axioms Admission.p8_attenuate
#print axioms Admission.p8_submit_receiver
#print axioms Admission.p9_needs_four_passes
#print axioms Admission.p9_changed_call
#print axioms Admission.p9_objection_discharged
#print axioms Admission.p9_discharge_by_person
#print axioms Admission.p9_objection_carried
#print axioms Admission.p9_approval_bound
#print axioms Admission.p10_chain_unique
#print axioms Admission.p10_loads_unique
#print axioms Admission.p10_chain_authorized
#print axioms Admission.p10_base_is_template
#print axioms Admission.p10_fork_stops
#print axioms Admission.p10_program_approval
#print axioms Admission.p10_unanchored
#print axioms Admission.p11_least
#print axioms Admission.p11_own_trust_not_enough
#print axioms Admission.p11_effect_gate
#print axioms Admission.p11_trusted_needs_no_declaration
#print axioms Admission.p11_no_role_reads_no_authority
#print axioms Admission.from_noResp
#print axioms Admission.p11_delegation_needs_no_approval
#print axioms Admission.p11_delegation_needs
#print axioms Admission.p11_scope_must_name_duty
#print axioms Admission.p11_withdrawn_delegation
#print axioms Admission.p11_program_delegation
#print axioms Admission.p11_other_agent_delegation
#print axioms Admission.p11_delegation_licenses
#print axioms Admission.p11_authority_rooted_in_person
#print axioms Admission.delegation_any_scope_differs
#print axioms Admission.effect_needs_no_person
#print axioms Admission.p12_runs_perm
#print axioms Admission.p12_may_perm
#print axioms Admission.p12_loads_perm
#print axioms Admission.p12_dispatch_perm
#print axioms Admission.p12_effect_perm
#print axioms Admission.p14_build_runs
#print axioms Admission.p14_unblessed_runs_nothing

end Kernel
