/-
  KeyOfIssuer.lean — a statement's key is a key of its issuer, or the statement waits

  The rule. CC 2.6.1.7 of the CIRIS Constitution at tag v1.0-rc21 (commit b016df4), applied as step 8 of
  the verification order of CC 2.6.1.8: a statement's key MUST be a key of its `iss`. The text lists four
  ways, and the TLA+ model `formal/key_of_iss/KeyOfIss.tla` of the Constitution names them (a) to (d):
    (a) genesis     `kid` is the thumbprint inside `iss`, the identity's genesis key.
    (b) rotation    the reader holds a record of the key whose own `iss` is the statement's, and that record
                    reaches the genesis key's record through rotation records. A link is held, is a key record
                    of the same `iss` that covers the rotation's instant, carries its own key's statement, and
                    the rotation carries the new key's and the predecessor's statements. A rival (a second
                    rotation of the predecessor to another key, voiced by both, naming a record of the
                    predecessor that covers it) hands on nothing.
    (c) seat        the bundle in force of the accord lineage seats it for `iss`. The statement names the
                    bundle; it waits while that bundle or one before it is not held, and the seat ends at the
                    first later bundle in force that does not seat the key.
    (d) occurrence  a held `identity:occurrence` of `iss` binds it: voiced by a key of `iss` (by (a) or (b))
                    and by the bound key itself, not evicted by an eviction a key of its `iss` signs, and never
                    a machine's key under a person's identity.
  A row one needs and does not hold (a link, a voice, the bundle) answers Waiting. Otherwise Invalid.

  The model. A row is its content: `W.row r` is the content of the row with digest `r`. The reader holds a
  list of items: statements, each one voice `v` over one row `r`, and bundles of the one lineage, bundle `m`
  following bundle `m - 1`. A row's voices are the statements held over it. Every rule reads the list only
  through membership. A chain is followed for at most `d` links, as the TLA+ model's depth.

  Proved here.
    verdict_valid_iff          Valid exactly when one of the four ways holds over the held rows
    valid_is_key_of_iss        soundness: Valid implies the key is a key of `iss` by one of the four ways
    key_of_iss_is_valid        the converse
    valid_rotation_link_held   a chain that reaches holds its first link, with the link's voice and the rotation's two
    waiting_not_invalid        any way that waits keeps the verdict from Invalid
    chain_waits_not_invalid    a held record of the key whose chain waits, at any depth: never Invalid
    missing_link_waits         a record of the key whose named predecessor is not held: never Invalid
    missing_voice_waits        the link held but one of the three voices not held: never Invalid
    missing_bundle_waits       the named bundle, or one before it, not held: never Invalid
    stays_waiting_without_link with the link still missing and no other way offered, no rows make it Valid
    waiting_to_valid_new_way   from Waiting, a Valid after more rows is a way the earlier rows did not give
    other_way_counterexample   "rows without the missing link never give Valid" is false as stated: a bundle
                               that seats the key does it, by way (c)
    seat_end_not_monotone      a Valid by seat turns Invalid when a later bundle unseats the key
    no_record_invalid          step 8 alone answers Invalid for a key no held row names; step 6 waits first
    verdict_function           the verdict is a function of the set of items held
    verdict_perm               and so the same for every arrival order

  What this file does not show, and where it differs from the TLA+ model.
    - A chain follows the record path the text names ("that record reaches the genesis key's record"). The
      TLA+ model recurses on the predecessor's key and reads any held record of it. The two agree where a key
      has one record of its `iss`; a renewal, which would give it two, is modelled in neither.
    - A seat ends for good at the first later placed bundle that does not seat the key, as the text says. The
      TLA+ model reads only the bundle in force now, so a key unseated and seated again would stand again
      there. Its three-bundle lineage cannot show the difference. One lineage only; bundle `m` follows `m - 1`.
    - Not modelled, as in the TLA+ model: `revoked_after` and its detail `rotation_after_revocation`, the
      rotation that names both rivals, renewal, an occurrence's own window over the statement's instant, the
      two admission paths of CC 3.3.6.4 (read here as a voice that is a key of `iss`), and whether a bundle
      counts. A chain longer than `d` links answers Invalid, as there.
    - Step 8 is read alone. A key no held row names answers Invalid here, as `Best({})` does in the TLA+
      model; in the verification order step 6 has already waited for the key's record (`no_record_invalid`).
    - Valid is not monotone in the rows held: a rival, an eviction or a later bundle ends it
      (`seat_end_not_monotone`). What is monotone is the other direction: every Valid is a way whose rows are
      all held, so a missing row's absence is never overcome except by a way that does not need it.

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core. Imports nothing.
-/

namespace KeyOfIssuer

inductive Kind | keyRec | occ | ev
deriving DecidableEq

/-- A row: a key record (`keyRec`), an occurrence (`occ`) or an eviction (`ev`). `k` is the key the record
    is of or the occurrence binds; `tgt` is the record a rotation names, or the occurrence an eviction ends. -/
structure Row where
  kind : Kind
  k : Nat
  iss : Nat
  asserted : Nat
  validUntil : Nat
  tgt : Option Nat
deriving DecidableEq

structure Bundle where
  seat : Nat → Option Nat

structure World where
  row : Nat → Row
  gen : Nat → Nat
  machine : Nat → Bool
  person : Nat → Bool
  bun : Nat → Bundle

inductive Item
  | stmt (r v : Nat)
  | bundle (b : Nat)
deriving DecidableEq

structure Stmt where
  kid : Nat
  iss : Nat
  bun : Option Nat

inductive V | valid | waiting | invalid
deriving DecidableEq

/-! ## The verdict -/

def voiced (H : List Item) (r v : Nat) : Bool := decide (Item.stmt r v ∈ H)

def isStmtOf (r : Nat) : Item → Bool
  | .stmt q _ => q == r
  | .bundle _ => false

def heldRow (H : List Item) (r : Nat) : Bool := H.any (isStmtOf r)

def covers (p : Row) (t : Nat) : Bool := decide (p.asserted ≤ t) && decide (t < p.validUntil)

/-- The best answer over the items: Valid if one gives Valid, else Waiting if one waits, else Invalid. -/
def best (H : List Item) (f : Item → V) : V :=
  if H.any (fun x => f x == .valid) then .valid
  else if H.any (fun x => f x == .waiting) then .waiting else .invalid

def join : V → V → V
  | .valid, _ => .valid
  | _, .valid => .valid
  | .waiting, _ => .waiting
  | _, .waiting => .waiting
  | _, _ => .invalid

def rivalAt (W : World) (H : List Item) (pk k : Nat) : Item → Bool
  | .stmt q _ =>
    match (W.row q).tgt with
    | some t => (W.row q).kind == .keyRec && (W.row q).k != pk && (W.row q).k != k
        && voiced H q (W.row q).k && voiced H q pk
        && (W.row t).k == pk && voiced H t pk && covers (W.row t) (W.row q).asserted
    | none => false
  | .bundle _ => false

def rival (W : World) (H : List Item) (pk k : Nat) : Bool := H.any (rivalAt W H pk k)

/-- Does record `r` reach the genesis key of `i` through at most `n` rotation links? -/
def link (W : World) (H : List Item) (i : Nat) : Nat → Nat → V
  | 0, _ => .invalid
  | n + 1, r =>
    match (W.row r).tgt with
    | none => .invalid
    | some t =>
      if heldRow H t = false then .waiting
      else if ((W.row t).kind == .keyRec && (W.row t).iss == i && covers (W.row t) (W.row r).asserted) = false
        then .invalid
      else if voiced H t (W.row t).k = false then .waiting
      else if voiced H r (W.row r).k = false then .waiting
      else if voiced H r (W.row t).k = false then .waiting
      else if rival W H (W.row t).k (W.row r).k = true then .invalid
      else if (W.row t).k = W.gen i then .valid
      else link W H i n t

def chainAt (W : World) (H : List Item) (d k i : Nat) : Item → V
  | .stmt r _ =>
    if ((W.row r).kind == .keyRec && (W.row r).k == k && (W.row r).iss == i) = true then link W H i d r
    else .invalid
  | .bundle _ => .invalid

/-- Ways (a) and (b), computed. -/
def chainV (W : World) (H : List Item) (d k i : Nat) : V :=
  if k = W.gen i then .valid else best H (chainAt W H d k i)

def placed (H : List Item) (b : Nat) : Bool := (List.range (b + 1)).all (fun m => decide (Item.bundle m ∈ H))

def unseats (W : World) (H : List Item) (b i k : Nat) : Item → Bool
  | .bundle m => decide (b < m) && placed H m && (W.bun m).seat i != some k
  | .stmt _ _ => false

/-- Way (c), computed. -/
def seatV (W : World) (H : List Item) (s : Stmt) : V :=
  match s.bun with
  | none => .invalid
  | some b =>
    if placed H b = false then .waiting
    else if ((W.bun b).seat s.iss == some s.kid && !(H.any (unseats W H b s.iss s.kid))) = true then .valid
    else .invalid

def evictsAt (W : World) (H : List Item) (d r : Nat) : Item → Bool
  | .stmt q v => (W.row q).kind == .ev && (W.row q).tgt == some r && chainV W H d v (W.row q).iss == .valid
  | .bundle _ => false

def identVoice (W : World) (H : List Item) (d r k i : Nat) : Item → Bool
  | .stmt q v => q == r && v != k && chainV W H d v i == .valid
  | .bundle _ => false

def occAt (W : World) (H : List Item) (d k i : Nat) : Item → V
  | .stmt r _ =>
    if ((W.row r).kind == .occ && (W.row r).k == k && (W.row r).iss == i) = false then .invalid
    else if (W.machine k && W.person i) = true then .invalid
    else if H.any (evictsAt W H d r) = true then .invalid
    else if H.any (identVoice W H d r k i) = false then .waiting
    else if voiced H r k = false then .waiting
    else .valid
  | .bundle _ => .invalid

/-- Way (d), computed. -/
def occV (W : World) (H : List Item) (d k i : Nat) : V := best H (occAt W H d k i)

/-- Step 8: the best of the four ways. -/
def verdict (W : World) (d : Nat) (H : List Item) (s : Stmt) : V :=
  join (chainV W H d s.kid s.iss) (join (seatV W H s) (occV W H d s.kid s.iss))

/-! ## The four ways, stated over membership alone -/

def Held (H : List Item) (r : Nat) : Prop := ∃ v, Item.stmt r v ∈ H

def Covers (p : Row) (t : Nat) : Prop := p.asserted ≤ t ∧ t < p.validUntil

/-- A rival of a rotation from `pk` to `k`: a rotation of `pk` to a third key, voiced by that key and by
    `pk`, naming a record of `pk` voiced by `pk` that covers it. -/
def Rival (W : World) (H : List Item) (pk k : Nat) : Prop :=
  ∃ q t, (W.row q).tgt = some t ∧ (W.row q).kind = .keyRec ∧ (W.row q).k ≠ pk ∧ (W.row q).k ≠ k ∧
    Item.stmt q (W.row q).k ∈ H ∧ Item.stmt q pk ∈ H ∧ (W.row t).k = pk ∧ Item.stmt t pk ∈ H ∧
    Covers (W.row t) (W.row q).asserted

/-- One rotation link from record `r` back to record `t`: `r` names `t`, `t` is a key record of `i` that
    covers `r`'s instant and is held with its own key's statement, `r` is held with the statements of its
    key and of `t`'s key, and no rival hands `t`'s key elsewhere. -/
def Link (W : World) (H : List Item) (i r t : Nat) : Prop :=
  (W.row r).tgt = some t ∧ (W.row t).kind = .keyRec ∧ (W.row t).iss = i ∧ Covers (W.row t) (W.row r).asserted ∧
    Item.stmt t (W.row t).k ∈ H ∧ Item.stmt r (W.row r).k ∈ H ∧ Item.stmt r (W.row t).k ∈ H ∧
    ¬ Rival W H (W.row t).k (W.row r).k

/-- Record `r` reaches the genesis key of `i` in at most `n` links, every link held with its voices. -/
inductive Reaches (W : World) (H : List Item) (i : Nat) : Nat → Nat → Prop
  | last {n r t : Nat} : Link W H i r t → (W.row t).k = W.gen i → Reaches W H i (n + 1) r
  | step {n r t : Nat} : Link W H i r t → Reaches W H i n t → Reaches W H i (n + 1) r

/-- Ways (a) and (b): `k` is a key of `i` by genesis or by a held rotation chain. -/
def KeyOfChain (W : World) (H : List Item) (d k i : Nat) : Prop :=
  k = W.gen i ∨ ∃ r, Held H r ∧ (W.row r).kind = .keyRec ∧ (W.row r).k = k ∧ (W.row r).iss = i ∧ Reaches W H i d r

def Placed (H : List Item) (b : Nat) : Prop := ∀ m, m ≤ b → Item.bundle m ∈ H

def Evicted (W : World) (H : List Item) (d r : Nat) : Prop :=
  ∃ q v, Item.stmt q v ∈ H ∧ (W.row q).kind = .ev ∧ (W.row q).tgt = some r ∧ KeyOfChain W H d v (W.row q).iss

/-- The four ways of CC 2.6.1.7. -/
inductive KeyOf (W : World) (d : Nat) (H : List Item) (s : Stmt) : Prop
  | genesis : s.kid = W.gen s.iss → KeyOf W d H s
  | rotation (r : Nat) : Held H r → (W.row r).kind = .keyRec → (W.row r).k = s.kid → (W.row r).iss = s.iss →
      Reaches W H s.iss d r → KeyOf W d H s
  | seat (b : Nat) : s.bun = some b → Placed H b → (W.bun b).seat s.iss = some s.kid →
      (∀ m, b < m → Placed H m → (W.bun m).seat s.iss = some s.kid) → KeyOf W d H s
  | occurrence (r : Nat) : Held H r → (W.row r).kind = .occ → (W.row r).k = s.kid → (W.row r).iss = s.iss →
      ¬ (W.machine s.kid = true ∧ W.person s.iss = true) → ¬ Evicted W H d r →
      (∃ v, v ≠ s.kid ∧ Item.stmt r v ∈ H ∧ KeyOfChain W H d v s.iss) →
      Item.stmt r s.kid ∈ H → KeyOf W d H s

/-! ## Lemmas on the three answers -/

theorem best_valid (H : List Item) (f : Item → V) : best H f = .valid ↔ ∃ x ∈ H, f x = .valid := by
  unfold best
  constructor
  · intro h
    cases h1 : H.any (fun x => f x == .valid)
    · cases h2 : H.any (fun x => f x == .waiting) <;> simp [h1, h2] at h
    · obtain ⟨x, hx, hf⟩ := List.any_eq_true.1 h1
      exact ⟨x, hx, by simpa using hf⟩
  · rintro ⟨x, hx, hf⟩
    have : H.any (fun x => f x == .valid) = true := List.any_eq_true.2 ⟨x, hx, by simp [hf]⟩
    simp [this]

theorem best_ne_invalid (H : List Item) (f : Item → V) (x : Item) (hx : x ∈ H) (hw : f x = .waiting) :
    best H f ≠ .invalid := by
  unfold best
  have : H.any (fun x => f x == .waiting) = true := List.any_eq_true.2 ⟨x, hx, by simp [hw]⟩
  cases h1 : H.any (fun x => f x == .valid) <;> simp [this]

theorem join_valid (a b : V) : join a b = .valid ↔ a = .valid ∨ b = .valid := by
  cases a <;> cases b <;> simp [join]

theorem join_ne_invalid_left (a b : V) (h : a ≠ .invalid) : join a b ≠ .invalid := by
  cases a <;> cases b <;> simp [join] at h ⊢

theorem join_ne_invalid_right (a b : V) (h : b ≠ .invalid) : join a b ≠ .invalid := by
  cases a <;> cases b <;> simp [join] at h ⊢

theorem if_false_valid {b : Bool} {x y : V} (h : (if b = false then x else y) = .valid) (hx : x ≠ .valid) :
    b = true ∧ y = .valid := by
  cases b
  · exact absurd h hx
  · exact ⟨rfl, h⟩

theorem if_true_valid {b : Bool} {x y : V} (h : (if b = true then x else y) = .valid) (hx : x ≠ .valid) :
    b = false ∧ y = .valid := by
  cases b
  · exact ⟨rfl, h⟩
  · exact absurd h hx

theorem voiced_iff (H : List Item) (r v : Nat) : voiced H r v = true ↔ Item.stmt r v ∈ H := by
  simp [voiced]

theorem heldRow_iff (H : List Item) (r : Nat) : heldRow H r = true ↔ Held H r := by
  unfold heldRow Held
  rw [List.any_eq_true]
  constructor
  · rintro ⟨x, hx, h⟩
    cases x with
    | stmt q v => simp [isStmtOf] at h; subst h; exact ⟨v, hx⟩
    | bundle _ => simp [isStmtOf] at h
  · rintro ⟨v, hv⟩; exact ⟨_, hv, by simp [isStmtOf]⟩

theorem covers_iff (p : Row) (t : Nat) : covers p t = true ↔ Covers p t := by
  simp [covers, Covers]

theorem rival_iff (W : World) (H : List Item) (pk k : Nat) : rival W H pk k = true ↔ Rival W H pk k := by
  unfold rival Rival
  rw [List.any_eq_true]
  constructor
  · rintro ⟨x, _, h⟩
    cases x with
    | bundle _ => simp [rivalAt] at h
    | stmt q v =>
      simp only [rivalAt] at h
      split at h
      · rename_i t ht
        simp [voiced, covers] at h
        obtain ⟨⟨⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩, h7⟩, h8, h9⟩ := h
        exact ⟨q, t, ht, h1, h2, h3, h4, h5, h6, h7, h8, h9⟩
      · simp at h
  · rintro ⟨q, t, ht, h1, h2, h3, h4, h5, h6, h7, h8, h9⟩
    refine ⟨.stmt q (W.row q).k, h4, ?_⟩
    simp only [rivalAt, ht]
    simp [voiced, covers, h1, h2, h3, h4, h5, h6, h7, h8, h9]

theorem link_valid_iff (W : World) (H : List Item) (i : Nat) :
    ∀ n r, link W H i n r = .valid ↔ Reaches W H i n r := by
  intro n
  induction n with
  | zero => intro r; simp only [link]; constructor <;> intro h <;> cases h
  | succ n ih =>
    intro r
    simp only [link]
    constructor
    · intro h
      split at h
      · cases h
      · rename_i t ht
        obtain ⟨hh, h⟩ := if_false_valid h (by simp)
        obtain ⟨hc, h⟩ := if_false_valid h (by simp)
        obtain ⟨hv1, h⟩ := if_false_valid h (by simp)
        obtain ⟨hv2, h⟩ := if_false_valid h (by simp)
        obtain ⟨hv3, h⟩ := if_false_valid h (by simp)
        have hc' := hc
        simp [covers] at hc'
        obtain ⟨⟨hk, hi⟩, hcov⟩ := hc'
        by_cases hr : rival W H (W.row t).k (W.row r).k = true
        · simp [hr] at h
        · simp only [hr] at h
          have hl : Link W H i r t := ⟨ht, hk, hi, hcov, (voiced_iff _ _ _).1 hv1, (voiced_iff _ _ _).1 hv2,
            (voiced_iff _ _ _).1 hv3, fun hR => hr ((rival_iff _ _ _ _).2 hR)⟩
          by_cases hg : (W.row t).k = W.gen i
          · exact Reaches.last hl hg
          · simp [hg] at h; exact Reaches.step hl ((ih t).1 h)
    · intro h
      have key : ∀ t, Link W H i r t → ((W.row t).k = W.gen i ∨ link W H i n t = .valid) →
          link W H i (n + 1) r = .valid := by
        intro t hl hnext
        obtain ⟨ht, hk, hi, hcov, hv1, hv2, hv3, hnr⟩ := hl
        simp only [link, ht]
        have hh : heldRow H t = true := (heldRow_iff _ _).2 ⟨_, hv1⟩
        have hc : ((W.row t).kind == .keyRec && (W.row t).iss == i && covers (W.row t) (W.row r).asserted) = true := by
          simp [hk, hi, (covers_iff _ _).2 hcov]
        have hr : rival W H (W.row t).k (W.row r).k = false := by
          cases h' : rival W H (W.row t).k (W.row r).k
          · rfl
          · exact absurd ((rival_iff _ _ _ _).1 h') hnr
        simp only [hh, hc, (voiced_iff _ _ _).2 hv1, (voiced_iff _ _ _).2 hv2, (voiced_iff _ _ _).2 hv3, hr]
        by_cases hg : (W.row t).k = W.gen i
        · simp [hg]
        · rcases hnext with h1 | h1
          · exact absurd h1 hg
          · simp [hg, h1]
      cases h with
      | last hl hg => exact key _ hl (Or.inl hg)
      | step hl hn => exact key _ hl (Or.inr ((ih _).2 hn))

theorem chainV_valid_iff (W : World) (H : List Item) (d k i : Nat) :
    chainV W H d k i = .valid ↔ KeyOfChain W H d k i := by
  unfold chainV KeyOfChain
  by_cases hg : k = W.gen i
  · simp [hg]
  · simp only [hg, ite_false, false_or]
    rw [best_valid]
    constructor
    · rintro ⟨x, hx, h⟩
      cases x with
      | bundle _ => simp [chainAt] at h
      | stmt r v =>
        simp only [chainAt] at h
        split at h
        · rename_i hc
          simp at hc
          obtain ⟨⟨h1, h2⟩, h3⟩ := hc
          exact ⟨r, ⟨v, hx⟩, h1, h2, h3, (link_valid_iff _ _ _ _ _).1 h⟩
        · cases h
    · rintro ⟨r, ⟨v, hv⟩, h1, h2, h3, h4⟩
      refine ⟨.stmt r v, hv, ?_⟩
      simp only [chainAt]
      simp [h1, h2, h3]
      exact (link_valid_iff _ _ _ _ _).2 h4

theorem placed_iff (H : List Item) (b : Nat) : placed H b = true ↔ Placed H b := by
  simp only [placed, List.all_eq_true, List.mem_range, decide_eq_true_eq, Placed]
  constructor
  · intro h m hm; exact h m (by omega)
  · intro h m hm; exact h m (by omega)

theorem seatV_valid_iff (W : World) (H : List Item) (s : Stmt) :
    seatV W H s = .valid ↔ ∃ b, s.bun = some b ∧ Placed H b ∧ (W.bun b).seat s.iss = some s.kid ∧
      (∀ m, b < m → Placed H m → (W.bun m).seat s.iss = some s.kid) := by
  unfold seatV
  cases hb : s.bun with
  | none => simp
  | some b =>
    simp only [Option.some.injEq, exists_eq_left']
    by_cases hp : placed H b = true
    · have hp' := (placed_iff H b).1 hp
      simp only [hp, Bool.true_eq_false, ite_false]
      have hu : H.any (unseats W H b s.iss s.kid) = false ↔
          ∀ m, b < m → Placed H m → (W.bun m).seat s.iss = some s.kid := by
        constructor
        · intro h m hm hpm
          have hin : Item.bundle m ∈ H := hpm m (Nat.le_refl m)
          have := List.any_eq_false.1 h _ hin
          simp [unseats, hm, (placed_iff H m).2 hpm] at this
          exact this
        · intro h
          apply List.any_eq_false.2
          intro x _
          cases x with
          | stmt _ _ => simp [unseats]
          | bundle m =>
            simp only [unseats]
            by_cases hm : b < m
            · by_cases hpm : placed H m = true
              · simp [hm, hpm, h m hm ((placed_iff H m).1 hpm)]
              · simp [hpm]
            · simp [hm]
      constructor
      · intro h
        split at h
        · rename_i hc
          simp at hc
          exact ⟨hp', hc.1, hu.1 (by simpa using hc.2)⟩
        · cases h
      · rintro ⟨_, h1, h2⟩
        have := hu.2 h2
        simp [h1, this]
    · simp only [Bool.not_eq_true] at hp
      simp only [hp, ite_true]
      constructor
      · intro h; cases h
      · rintro ⟨h1, _⟩
        have := (placed_iff H b).2 h1
        rw [hp] at this; cases this

theorem evicted_iff (W : World) (H : List Item) (d r : Nat) :
    H.any (evictsAt W H d r) = true ↔ Evicted W H d r := by
  rw [List.any_eq_true]
  unfold Evicted
  constructor
  · rintro ⟨x, hx, h⟩
    cases x with
    | bundle _ => simp [evictsAt] at h
    | stmt q v =>
      simp only [evictsAt] at h
      simp at h
      obtain ⟨⟨h1, h2⟩, h3⟩ := h
      exact ⟨q, v, hx, h1, h2, (chainV_valid_iff _ _ _ _ _).1 h3⟩
  · rintro ⟨q, v, hx, h1, h2, h3⟩
    refine ⟨.stmt q v, hx, ?_⟩
    simp only [evictsAt]
    simp [h1, h2, (chainV_valid_iff _ _ _ _ _).2 h3]

theorem identVoice_iff (W : World) (H : List Item) (d r k i : Nat) :
    H.any (identVoice W H d r k i) = true ↔ ∃ v, v ≠ k ∧ Item.stmt r v ∈ H ∧ KeyOfChain W H d v i := by
  rw [List.any_eq_true]
  constructor
  · rintro ⟨x, hx, h⟩
    cases x with
    | bundle _ => simp [identVoice] at h
    | stmt q v =>
      simp only [identVoice] at h
      simp at h
      obtain ⟨⟨h1, h2⟩, h3⟩ := h
      subst h1
      exact ⟨v, h2, hx, (chainV_valid_iff _ _ _ _ _).1 h3⟩
  · rintro ⟨v, h1, h2, h3⟩
    refine ⟨.stmt r v, h2, ?_⟩
    simp only [identVoice]
    simp [h1, (chainV_valid_iff _ _ _ _ _).2 h3]

theorem occV_valid_iff (W : World) (H : List Item) (d k i : Nat) :
    occV W H d k i = .valid ↔ ∃ r, Held H r ∧ (W.row r).kind = .occ ∧ (W.row r).k = k ∧ (W.row r).iss = i ∧
      ¬ (W.machine k = true ∧ W.person i = true) ∧ ¬ Evicted W H d r ∧
      (∃ v, v ≠ k ∧ Item.stmt r v ∈ H ∧ KeyOfChain W H d v i) ∧ Item.stmt r k ∈ H := by
  unfold occV
  rw [best_valid]
  constructor
  · rintro ⟨x, hx, h⟩
    cases x with
    | bundle _ => simp [occAt] at h
    | stmt r v =>
      simp only [occAt] at h
      obtain ⟨hc, h⟩ := if_false_valid h (by simp)
      obtain ⟨hm, h⟩ := if_true_valid h (by simp)
      obtain ⟨he, h⟩ := if_true_valid h (by simp)
      obtain ⟨hiv, h⟩ := if_false_valid h (by simp)
      obtain ⟨hv, _⟩ := if_false_valid h (by simp)
      simp at hc
      obtain ⟨⟨h1, h2⟩, h3⟩ := hc
      refine ⟨r, ⟨v, hx⟩, h1, h2, h3, ?_, ?_, (identVoice_iff _ _ _ _ _ _).1 hiv, (voiced_iff _ _ _).1 hv⟩
      · rintro ⟨a, b⟩; simp [a, b] at hm
      · intro hE; rw [(evicted_iff _ _ _ _).2 hE] at he; cases he
  · rintro ⟨r, ⟨v, hv⟩, h1, h2, h3, hm, he, hiv, hk⟩
    refine ⟨.stmt r v, hv, ?_⟩
    have hm' : (W.machine k && W.person i) = false := by
      cases h1' : W.machine k <;> cases h2' : W.person i <;> simp_all
    have he' : H.any (evictsAt W H d r) = false := by
      cases h' : H.any (evictsAt W H d r)
      · rfl
      · exact absurd ((evicted_iff _ _ _ _).1 h') he
    simp only [occAt]
    simp [h1, h2, h3, hm', he', (identVoice_iff _ _ _ _ _ _).2 hiv, (voiced_iff _ _ _).2 hk]

/-! ## Soundness and its converse -/

/-- Valid exactly when the key is a key of `iss` by one of the four ways. -/
theorem verdict_valid_iff (W : World) (d : Nat) (H : List Item) (s : Stmt) :
    verdict W d H s = .valid ↔ KeyOf W d H s := by
  unfold verdict
  rw [join_valid, join_valid, chainV_valid_iff, seatV_valid_iff, occV_valid_iff]
  constructor
  · rintro (h | h | h)
    · rcases h with h | ⟨r, h1, h2, h3, h4, h5⟩
      · exact KeyOf.genesis h
      · exact KeyOf.rotation r h1 h2 h3 h4 h5
    · obtain ⟨b, h1, h2, h3, h4⟩ := h; exact KeyOf.seat b h1 h2 h3 h4
    · obtain ⟨r, h1, h2, h3, h4, h5, h6, h7, h8⟩ := h; exact KeyOf.occurrence r h1 h2 h3 h4 h5 h6 h7 h8
  · intro h
    cases h with
    | genesis h => exact Or.inl (Or.inl h)
    | rotation r h1 h2 h3 h4 h5 => exact Or.inl (Or.inr ⟨r, h1, h2, h3, h4, h5⟩)
    | seat b h1 h2 h3 h4 => exact Or.inr (Or.inl ⟨b, h1, h2, h3, h4⟩)
    | occurrence r h1 h2 h3 h4 h5 h6 h7 h8 => exact Or.inr (Or.inr ⟨r, h1, h2, h3, h4, h5, h6, h7, h8⟩)

/-- Soundness: no statement is Valid unless its key is a key of `iss` by one of the four ways. -/
theorem valid_is_key_of_iss (W : World) (d : Nat) (H : List Item) (s : Stmt)
    (h : verdict W d H s = .valid) : KeyOf W d H s := (verdict_valid_iff W d H s).1 h

theorem key_of_iss_is_valid (W : World) (d : Nat) (H : List Item) (s : Stmt)
    (h : KeyOf W d H s) : verdict W d H s = .valid := (verdict_valid_iff W d H s).2 h

/-- A chain that reaches holds its first link, with the link's own voice and both voices of the rotation. -/
theorem valid_rotation_link_held (W : World) (H : List Item) (i n r : Nat) (h : Reaches W H i n r) :
    ∃ t, (W.row r).tgt = some t ∧ Item.stmt t (W.row t).k ∈ H ∧ Item.stmt r (W.row r).k ∈ H ∧
      Item.stmt r (W.row t).k ∈ H := by
  cases h with
  | last hl _ => exact ⟨_, hl.1, hl.2.2.2.2.1, hl.2.2.2.2.2.1, hl.2.2.2.2.2.2.1⟩
  | step hl _ => exact ⟨_, hl.1, hl.2.2.2.2.1, hl.2.2.2.2.2.1, hl.2.2.2.2.2.2.1⟩

/-! ## A missing link waits -/

/-- Any way that waits keeps the verdict from Invalid. -/
theorem waiting_not_invalid (W : World) (d : Nat) (H : List Item) (s : Stmt)
    (h : chainV W H d s.kid s.iss = .waiting ∨ seatV W H s = .waiting ∨ occV W H d s.kid s.iss = .waiting) :
    verdict W d H s ≠ .invalid := by
  unfold verdict
  rcases h with h | h | h
  · exact join_ne_invalid_left _ _ (by rw [h]; simp)
  · exact join_ne_invalid_right _ _ (join_ne_invalid_left _ _ (by rw [h]; simp))
  · exact join_ne_invalid_right _ _ (join_ne_invalid_right _ _ (by rw [h]; simp))

/-- A held record of the key under `iss` whose chain waits, at whatever depth the missing row is. -/
theorem chain_waits_not_invalid (W : World) (d : Nat) (H : List Item) (s : Stmt) (r v : Nat)
    (hx : Item.stmt r v ∈ H) (hk : (W.row r).kind = .keyRec) (hkid : (W.row r).k = s.kid)
    (hi : (W.row r).iss = s.iss) (hw : link W H s.iss d r = .waiting) : verdict W d H s ≠ .invalid := by
  by_cases hg : s.kid = W.gen s.iss
  · intro hv
    have : verdict W d H s = .valid := key_of_iss_is_valid _ _ _ _ (KeyOf.genesis hg)
    rw [this] at hv; cases hv
  · apply join_ne_invalid_left
    unfold chainV
    simp only [hg, ite_false]
    exact best_ne_invalid H _ _ hx (by simp [chainAt, hk, hkid, hi, hw])

/-- A record of the key whose named predecessor record is not held: Waiting (or Valid by another way),
    never Invalid. -/
theorem missing_link_waits (W : World) (d : Nat) (H : List Item) (s : Stmt) (r v t : Nat)
    (hx : Item.stmt r v ∈ H) (hk : (W.row r).kind = .keyRec) (hkid : (W.row r).k = s.kid)
    (hi : (W.row r).iss = s.iss) (ht : (W.row r).tgt = some t) (hnot : ¬ Held H t) (hd : 0 < d) :
    verdict W d H s ≠ .invalid := by
  obtain ⟨n, rfl⟩ : ∃ n, d = n + 1 := ⟨d - 1, by omega⟩
  apply chain_waits_not_invalid W _ H s r v hx hk hkid hi
  have : heldRow H t = false := by
    cases h' : heldRow H t
    · rfl
    · exact absurd ((heldRow_iff _ _).1 h') hnot
  simp [link, ht, this]

/-- The link is held, a key record of `iss` covering the rotation, but one of the three voices is not held:
    the link's own key, the new key, or the predecessor on the rotation. Never Invalid. -/
theorem missing_voice_waits (W : World) (d : Nat) (H : List Item) (s : Stmt) (r v t : Nat)
    (hx : Item.stmt r v ∈ H) (hk : (W.row r).kind = .keyRec) (hkid : (W.row r).k = s.kid)
    (hi : (W.row r).iss = s.iss) (ht : (W.row r).tgt = some t) (hheld : Held H t)
    (htk : (W.row t).kind = .keyRec) (hti : (W.row t).iss = s.iss) (hcov : Covers (W.row t) (W.row r).asserted)
    (hmiss : Item.stmt t (W.row t).k ∉ H ∨ Item.stmt r (W.row r).k ∉ H ∨ Item.stmt r (W.row t).k ∉ H)
    (hd : 0 < d) : verdict W d H s ≠ .invalid := by
  obtain ⟨n, rfl⟩ : ∃ n, d = n + 1 := ⟨d - 1, by omega⟩
  apply chain_waits_not_invalid W _ H s r v hx hk hkid hi
  have hh : heldRow H t = true := (heldRow_iff _ _).2 hheld
  have hc : ((W.row t).kind == .keyRec && (W.row t).iss == s.iss && covers (W.row t) (W.row r).asserted) = true := by
    simp [htk, hti, (covers_iff _ _).2 hcov]
  simp only [link, ht, hh, hc]
  rcases hmiss with h | h | h
  · have : voiced H t (W.row t).k = false := by simpa [voiced] using h
    simp [this]
  · have : voiced H r (W.row r).k = false := by simpa [voiced] using h
    by_cases h1 : voiced H t (W.row t).k = true <;> simp [h1, this]
  · have : voiced H r (W.row t).k = false := by simpa [voiced] using h
    by_cases h1 : voiced H t (W.row t).k = true <;> by_cases h2 : voiced H r (W.row r).k = true <;>
      simp [h1, h2, this]

/-- The statement names a bundle that is not placed (it or one before it not held): never Invalid. -/
theorem missing_bundle_waits (W : World) (d : Nat) (H : List Item) (s : Stmt) (b : Nat)
    (hb : s.bun = some b) (hnot : ¬ Placed H b) : verdict W d H s ≠ .invalid := by
  apply waiting_not_invalid
  right; left
  have : placed H b = false := by
    cases h' : placed H b
    · rfl
    · exact absurd ((placed_iff _ _).1 h') hnot
  simp [seatV, hb, this]

/-! ## Waiting turns Valid only when a row a way needs arrives -/

/-- With the link still missing and no other way offered, no rows make the statement Valid: the key is not
    the genesis key, the statement names no bundle, no occurrence of the key under `iss` is held, and every
    held record of the key under `iss` names the record `t`, which no held statement is over. -/
theorem stays_waiting_without_link (W : World) (d : Nat) (H M : List Item) (s : Stmt) (t : Nat)
    (hg : s.kid ≠ W.gen s.iss) (hb : s.bun = none)
    (hocc : ∀ r, Held (H ++ M) r → (W.row r).kind = .occ → (W.row r).k = s.kid → (W.row r).iss ≠ s.iss)
    (hrec : ∀ r, Held (H ++ M) r → (W.row r).kind = .keyRec → (W.row r).k = s.kid → (W.row r).iss = s.iss →
      (W.row r).tgt = some t)
    (hH : ¬ Held H t) (hM : ¬ Held M t) : verdict W d (H ++ M) s ≠ .valid := by
  intro hv
  cases valid_is_key_of_iss W d _ s hv with
  | genesis h => exact hg h
  | seat b h1 _ _ _ => rw [hb] at h1; cases h1
  | occurrence r h1 h2 h3 h4 _ _ _ _ => exact hocc r h1 h2 h3 h4
  | rotation r h1 h2 h3 h4 h5 =>
    have ht := hrec r h1 h2 h3 h4
    obtain ⟨t', ht', hv1, _⟩ := valid_rotation_link_held W _ _ _ _ h5
    rw [ht] at ht'
    cases ht'
    rcases List.mem_append.1 hv1 with h | h
    · exact hH ⟨_, h⟩
    · exact hM ⟨_, h⟩

/-- From Waiting, a Valid after more rows is a way that the earlier rows did not give. -/
theorem waiting_to_valid_new_way (W : World) (d : Nat) (H M : List Item) (s : Stmt)
    (hw : verdict W d H s = .waiting) (hv : verdict W d (H ++ M) s = .valid) :
    ¬ KeyOf W d H s ∧ KeyOf W d (H ++ M) s := by
  refine ⟨fun h => ?_, valid_is_key_of_iss W d _ s hv⟩
  rw [key_of_iss_is_valid W d H s h] at hw; cases hw

/-! ## Witnesses -/

/-- Identity 0 has genesis key 0. Row 0 is its genesis record; row 1 rotates it to key 1; bundle 0 seats
    key 1 for identity 0; bundle 1 seats nobody. -/
def W0 : World where
  row := fun r => match r with
    | 0 => ⟨.keyRec, 0, 0, 0, 2, none⟩
    | _ => ⟨.keyRec, 1, 0, 1, 4, some 0⟩
  gen := fun _ => 0
  machine := fun _ => false
  person := fun _ => true
  bun := fun b => match b with
    | 0 => ⟨fun i => if i = 0 then some 1 else none⟩
    | _ => ⟨fun _ => none⟩

/-- The rotation to key 1 is held with both its voices; the genesis record it names is not. -/
def H0 : List Item := [.stmt 1 1, .stmt 1 0]

def S1 : Stmt := ⟨1, 0, some 0⟩

/-- "From Waiting, rows that do not include the missing link never give Valid" is false as stated: the
    statement waits on row 0 (and on bundle 0), and bundle 0 alone, with row 0 still missing, makes it Valid
    by way (c). The faithful form is `stays_waiting_without_link`, which rules the other ways out. -/
theorem other_way_counterexample :
    verdict W0 3 H0 S1 = .waiting ∧ ¬ Held [Item.bundle 0] 0 ∧ ¬ Held H0 0 ∧
      verdict W0 3 (H0 ++ [.bundle 0]) S1 = .valid := by
  refine ⟨by decide, ?_, ?_, by decide⟩
  · rintro ⟨v, hv⟩; simp at hv
  · rintro ⟨v, hv⟩; simp [H0] at hv

/-- Valid is not kept under more rows: a later bundle that does not seat the key ends a seat. A rival or an
    eviction does the same, by their definitions. -/
theorem seat_end_not_monotone :
    verdict W0 3 [.bundle 0] S1 = .valid ∧ verdict W0 3 [.bundle 0, .bundle 1] S1 = .invalid := by
  decide

/-- Step 8 alone answers Invalid for a key no held row names: the reader holds nothing, and the key is not
    the genesis key. In the verification order the statement has already waited at step 6 for its key's
    record, so step 8 is reached only once a record of the key is held. With the chain held it is Valid. -/
theorem no_record_invalid : verdict W0 3 [] ⟨1, 0, none⟩ = .invalid ∧
    verdict W0 3 [.stmt 0 0, .stmt 1 1, .stmt 1 0] ⟨1, 0, none⟩ = .valid := by
  decide

/-! ## A function of the set held -/

def Same (H H' : List Item) : Prop := ∀ x, x ∈ H ↔ x ∈ H'

theorem any_same {H H' : List Item} (hs : Same H H') {f g : Item → Bool} (hfg : ∀ x, f x = g x) :
    H.any f = H'.any g := by
  apply Bool.eq_iff_iff.2
  simp only [List.any_eq_true]
  constructor
  · rintro ⟨x, hx, h⟩; exact ⟨x, (hs x).1 hx, by rw [← hfg]; exact h⟩
  · rintro ⟨x, hx, h⟩; exact ⟨x, (hs x).2 hx, by rw [hfg]; exact h⟩

theorem best_same {H H' : List Item} (hs : Same H H') {f g : Item → V} (hfg : ∀ x, f x = g x) :
    best H f = best H' g := by
  unfold best
  rw [any_same hs (g := fun x => g x == .valid) (fun x => by rw [hfg]),
      any_same hs (g := fun x => g x == .waiting) (fun x => by rw [hfg])]

theorem voiced_same {H H' : List Item} (hs : Same H H') (r v : Nat) : voiced H r v = voiced H' r v := by
  unfold voiced; exact decide_eq_decide.2 (hs _)

theorem heldRow_same {H H' : List Item} (hs : Same H H') (r : Nat) : heldRow H r = heldRow H' r :=
  any_same hs (fun _ => rfl)

theorem rival_same (W : World) {H H' : List Item} (hs : Same H H') (pk k : Nat) :
    rival W H pk k = rival W H' pk k := by
  apply any_same hs
  intro x
  cases x with
  | bundle _ => rfl
  | stmt q _ =>
    simp only [rivalAt]
    split <;> simp only [voiced_same hs]

theorem link_same (W : World) {H H' : List Item} (hs : Same H H') (i : Nat) :
    ∀ n r, link W H i n r = link W H' i n r := by
  intro n
  induction n with
  | zero => intro r; rfl
  | succ n ih =>
    intro r
    simp only [link]
    split
    · rfl
    · simp only [heldRow_same hs, voiced_same hs, rival_same W hs, ih]

theorem chainV_same (W : World) {H H' : List Item} (hs : Same H H') (d k i : Nat) :
    chainV W H d k i = chainV W H' d k i := by
  unfold chainV
  rw [best_same hs (g := chainAt W H' d k i)]
  intro x
  cases x with
  | bundle _ => rfl
  | stmt r _ => simp only [chainAt, link_same W hs]

theorem placed_same {H H' : List Item} (hs : Same H H') (b : Nat) : placed H b = placed H' b := by
  unfold placed
  congr 1
  funext m
  exact decide_eq_decide.2 (hs _)

theorem seatV_same (W : World) {H H' : List Item} (hs : Same H H') (s : Stmt) :
    seatV W H s = seatV W H' s := by
  unfold seatV
  split
  · rfl
  · rw [placed_same hs, any_same hs (g := unseats W H' _ s.iss s.kid)]
    intro x
    cases x with
    | stmt _ _ => rfl
    | bundle m => simp only [unseats, placed_same hs]

theorem occV_same (W : World) {H H' : List Item} (hs : Same H H') (d k i : Nat) :
    occV W H d k i = occV W H' d k i := by
  unfold occV
  apply best_same hs
  intro x
  cases x with
  | bundle _ => rfl
  | stmt r _ =>
    simp only [occAt]
    rw [any_same hs (g := evictsAt W H' d r), any_same hs (g := identVoice W H' d r k i), voiced_same hs]
    · intro y; cases y with
      | bundle _ => rfl
      | stmt q v => simp only [identVoice, chainV_same W hs]
    · intro y; cases y with
      | bundle _ => rfl
      | stmt q v => simp only [evictsAt, chainV_same W hs]

/-- The verdict reads the held items only through membership. -/
theorem verdict_function (W : World) (d : Nat) {H H' : List Item} (hs : ∀ x, x ∈ H ↔ x ∈ H') (s : Stmt) :
    verdict W d H s = verdict W d H' s := by
  unfold verdict
  rw [chainV_same W hs, seatV_same W hs, occV_same W hs]

/-- The same items in any arrival order give the same verdict. -/
theorem verdict_perm (W : World) (d : Nat) {H H' : List Item} (h : H.Perm H') (s : Stmt) :
    verdict W d H s = verdict W d H' s :=
  verdict_function W d (fun _ => h.mem_iff) s

end KeyOfIssuer

#print axioms KeyOfIssuer.verdict_valid_iff
#print axioms KeyOfIssuer.valid_is_key_of_iss
#print axioms KeyOfIssuer.key_of_iss_is_valid
#print axioms KeyOfIssuer.valid_rotation_link_held
#print axioms KeyOfIssuer.waiting_not_invalid
#print axioms KeyOfIssuer.chain_waits_not_invalid
#print axioms KeyOfIssuer.missing_link_waits
#print axioms KeyOfIssuer.missing_voice_waits
#print axioms KeyOfIssuer.missing_bundle_waits
#print axioms KeyOfIssuer.stays_waiting_without_link
#print axioms KeyOfIssuer.waiting_to_valid_new_way
#print axioms KeyOfIssuer.other_way_counterexample
#print axioms KeyOfIssuer.seat_end_not_monotone
#print axioms KeyOfIssuer.no_record_invalid
#print axioms KeyOfIssuer.verdict_function
#print axioms KeyOfIssuer.verdict_perm
