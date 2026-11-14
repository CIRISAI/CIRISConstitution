/-
  formal/standing/Standing.lean — standing over a row that names another person

  CC 2.1: a key listed in subject_key_ids holds consent authority over the row (it may withdraw it
  and emit consent about it). CC 3.4.5: the subject of a row holds standing to file reconsideration
  and is promised a read over the rows it is party to. CC 6.1.5.3 / 5.2: a bounded cohort's rows
  reach its members and nobody else. CC 2.4.1.1: a subject may not withdraw an adverse record about
  itself (capacity, detection, licensure, revocation; the accountability record), only contest it;
  a cosigned row is undone only cosigned (Rule 0).

  The question this file settles: whom may a row at a bounded scope name? Three admission policies
  are compared on one world: the loose reading (any key), the strict reading (only the producer),
  and the audience rule (only keys the row reaches: members of the cohort by the roster fold at the
  row's instant, or the key the family delivers the row to). The audience rule is the one under
  which standing always comes with reach and a community can still speak about its own members.

  The second question, the steward's (2026-11-01): when is retraction by the person named not
  available? Three kinds of statement about a person are told apart: an authority's act under a
  declared legal-weight class (a conviction, a licence), a duty-holder's record on the accountability
  trail (a harm report and the action on it, a hard case, a slashing verdict, a measured capacity),
  and peer speech. A person retracts peer speech about themself and only contests the other two; an
  affiliation never retracts a statement about itself. The good-faith warning has a channel the
  accused cannot close: filed with the room's named moderator it is a duty-holder's record.

  The third question: once the person named has taken peer speech back, who still reads it? Three
  answers are compared: nobody, the room with the retraction beside it, and the speaker alone. The
  speaker alone is the one under which the retraction removes something and the speaker keeps
  their own words, which they may still file with a duty-holder (CC 2.4.1.1, 6.1.5).

  Core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core.
-/

namespace Standing

abbrev Key := Nat
abbrev Instant := Nat

inductive Kind | scores | delegatesTo | cosigned
  deriving DecidableEq, Repr

/-- the three kinds of statement about a person (CC 2.4.1.1, 4.5.5):
    * `peer` — one party's own claim or opinion about another, under no duty;
    * `dutyRecord` — a record made under a named duty on the accountability trail: a harm report
      filed with the named moderator and the action on it, a hard case, a slashing verdict, a
      measured capacity or detection;
    * `authorityAct` — an act of a body under a declared legal-weight class: a conviction, a
      licence, a revocation. -/
inductive Statement | peer | dutyRecord | authorityAct
  deriving DecidableEq, Repr

/-- whose standing applies: a person has consent over what is said about them; an affiliation
    (a business, a court, a professional body) has duties and no such consent (CC 4.4.3.12) -/
inductive SubjectKind | person | affiliation
  deriving DecidableEq, Repr

/-- a cohort is its roster fold: who is a member at an instant (CC 3.1.3.2; the same fold every
    bounded-scope door uses) -/
structure Cohort where
  members : Instant → List Key

structure Row where
  producer : Key
  cohort : Nat                 -- 0 = federation (everyone); n ≥ 1 indexes a bounded cohort
  instant : Instant            -- asserted_at
  kind : Kind
  subjects : List Key          -- subject_key_ids
  deliveredTo : List Key       -- the key the family delivers the row to (invitee, recipient, own node)
  statement : Statement        -- what kind of statement about its subject the row is
  subjectKind : SubjectKind    -- whether the named subject is a person or an affiliation
  reporterShielded : Bool      -- a duty-holder's record may shield the reporter's identity and content
  deriving Repr

structure World where
  everyone : List Key
  cohorts : List Cohort

def membersAt (w : World) (c : Nat) (t : Instant) : List Key :=
  match w.cohorts.get? (c - 1) with
  | some co => co.members t
  | none => []

/-- who the row reaches: everyone at federation scope; at a bounded scope the cohort's members at
    the row's instant, plus the key the family delivers it to -/
def audience (w : World) (r : Row) : List Key :=
  (if r.cohort = 0 then w.everyone else membersAt w r.cohort r.instant) ++ r.deliveredTo

def reaches (w : World) (r : Row) (k : Key) : Bool := (audience w r).contains k

/-- consent standing: the key is a listed subject (CC 2.1) -/
def hasStanding (r : Row) (k : Key) : Bool := r.subjects.contains k

/-! ## Three admission policies for a row naming another person -/

/-- the loose reading: any key may be named at any scope -/
def admitLoose (_ : World) (_ : Row) : Bool := true

/-- the strict reading: at a bounded scope a row names nobody but its producer -/
def admitStrict (_ : World) (r : Row) : Bool :=
  r.cohort = 0 || r.subjects.all (fun s => s == r.producer)

/-- the audience rule: every named subject is within the row's audience -/
def admitAudience (w : World) (r : Row) : Bool := r.subjects.all (fun s => reaches w r s)

/-! ## What a subject may do with a row about it -/

/-- the "unless" (CC 2.4.1.1): the producer withdraws its own row always; a named person
    withdraws peer speech about themself (rule 2), and only contests a duty-holder's record, an
    authority's act, or a cosigned act (Rule 0); an affiliation never withdraws a statement about
    itself -/
def mayWithdraw (r : Row) (k : Key) : Bool :=
  k == r.producer ||
  (hasStanding r k && r.subjectKind == .person && r.statement == .peer && r.kind != .cosigned)

/-- the second inviolable, refined: the person named always sees that the record exists, its kind,
    its consequence and who answers for it … -/
def seesExistence (w : World) (r : Row) (k : Key) : Bool := reaches w r k
/-- … and sees its full content and author unless a duty-holder's record shields the reporter -/
def seesContent (w : World) (r : Row) (k : Key) : Bool :=
  reaches w r k && !(r.statement == .dutyRecord && r.reporterShielded)

/-- contest: every subject, always (CC 3.4.5 reconsideration) -/
def mayContest (r : Row) (k : Key) : Bool := hasStanding r k

/-! ## Theorems -/

/-- under the audience rule, standing always comes with reach: a subject of an admitted row can
    see the row it may withdraw or contest (CC 3.4.5's promise, kept by construction) -/
theorem standing_reaches (w : World) (r : Row) (k : Key)
    (h : admitAudience w r = true) (hs : hasStanding r k = true) : reaches w r k = true := by
  unfold admitAudience at h; unfold hasStanding at hs
  have := List.all_eq_true.mp h k (List.mem_of_elem_eq_true hs)
  simpa using this

/-- a subject's contest path is never closed by the kind of row: whatever the row is, a listed
    subject may contest it -/
theorem contest_always_open (r : Row) (k : Key) (hs : hasStanding r k = true) :
    mayContest r k = true := hs

/-- a duty-holder's record is contest-only for the person named -/
theorem duty_record_is_contest_only (r : Row) (k : Key) (hd : r.statement = .dutyRecord)
    (hk : k ≠ r.producer) : mayWithdraw r k = false := by
  unfold mayWithdraw; simp [hd, hk]

/-- an authority's act is contest-only for the person named -/
theorem authority_act_is_contest_only (r : Row) (k : Key) (ha : r.statement = .authorityAct)
    (hk : k ≠ r.producer) : mayWithdraw r k = false := by
  unfold mayWithdraw; simp [ha, hk]

/-- an affiliation never retracts a statement about itself, whatever the statement is -/
theorem affiliation_never_retracts (r : Row) (k : Key) (ha : r.subjectKind = .affiliation)
    (hk : k ≠ r.producer) : mayWithdraw r k = false := by
  unfold mayWithdraw; simp [ha, hk]

/-- a person retracts peer speech about themself: consent prevails between equals -/
theorem person_retracts_peer_speech (r : Row) (k : Key) (hs : hasStanding r k = true)
    (hp : r.subjectKind = .person) (hpe : r.statement = .peer) (hc : r.kind ≠ .cosigned) :
    mayWithdraw r k = true := by
  unfold mayWithdraw; simp [hs, hp, hpe, hc]

/-- the person named always sees that a record about them exists, under the audience rule -/
theorem named_person_sees_existence (w : World) (r : Row) (k : Key)
    (h : admitAudience w r = true) (hs : hasStanding r k = true) : seesExistence w r k = true :=
  standing_reaches w r k h hs

/-- content is withheld from the person named only where a duty-holder's record shields its
    reporter: peer speech and an authority's act are always fully visible -/
theorem content_withheld_only_by_a_shielded_duty_record (w : World) (r : Row) (k : Key)
    (h : seesExistence w r k = true) (hn : r.statement ≠ .dutyRecord) : seesContent w r k = true := by
  unfold seesContent; unfold seesExistence at h; simp [h, hn]

/-! ## The good-faith warning channel (CC 4.5.5)

  The same warning can be made two ways. As peer speech it is the person's to retract. Filed with
  the room's named moderator it is a duty-holder's record: the accused cannot close it, can contest
  it, and sees that it exists and what follows from it, while the reporter may be shielded. -/

/-- file a warning as a harm report with the named moderator: the same subject, now a duty record -/
def asReport (r : Row) (moderator : Key) (shield : Bool) : Row :=
  { r with producer := moderator, statement := .dutyRecord, reporterShielded := shield }

/-- the channel is never closed by the accused: a filed report is contest-only for them -/
theorem warning_channel_not_closable (r : Row) (m k : Key) (shield : Bool) (hk : k ≠ m) :
    mayWithdraw (asReport r m shield) k = false := by
  unfold asReport; exact duty_record_is_contest_only _ k rfl hk

/-- and never closed to the accused: they may always contest it -/
theorem warning_channel_contestable (r : Row) (m : Key) (shield : Bool) (k : Key)
    (hs : hasStanding r k = true) : mayContest (asReport r m shield) k = true := by
  unfold asReport mayContest hasStanding at *; simpa using hs

/-- the filed report reaches the accused exactly where the warning would have: filing changes the
    duty, not the audience -/
theorem report_reaches_where_the_warning_did (w : World) (r : Row) (m : Key) (shield : Bool) (k : Key) :
    reaches w (asReport r m shield) k = reaches w r k := rfl

/-- a cosigned row is undone only cosigned: a listed subject alone cannot withdraw it -/
theorem cosigned_undone_only_cosigned (r : Row) (k : Key) (hc : r.kind = .cosigned)
    (hk : k ≠ r.producer) : mayWithdraw r k = false := by
  unfold mayWithdraw; simp [hc, hk]

/-! ## What stays after a retraction (CC 2.4.1.1, 6.1.5)

  A retraction by the person named is a signed row beside the one it retires. Three answers to who
  reads the retired row's content afterwards: nobody, everyone the row reached, or the speaker. -/

inductive Keep | nobody | room | speaker
  deriving DecidableEq, Repr

/-- who reads the content of `r`: before a retraction, whoever the row reaches; after it, nobody,
    whoever it reached (the retraction shown beside it), or the speaker alone at self scope -/
def readsContent (p : Keep) (w : World) (r : Row) (retracted : Bool) (k : Key) : Bool :=
  if retracted then
    match p with
    | .nobody => false
    | .room => reaches w r k
    | .speaker => k == r.producer
  else reaches w r k

/-- shown to the room beside its retraction, the row is read by exactly those who read it before:
    the retraction removes nothing and is a label -/
theorem shown_retraction_removes_nothing (w : World) (r : Row) (k : Key) :
    readsContent .room w r true k = readsContent .room w r false k := by
  simp [readsContent]

/-- kept by nobody, the retraction takes the speaker's own words from the speaker -/
theorem kept_by_nobody_takes_the_speakers_words (w : World) (r : Row) :
    readsContent .nobody w r true r.producer = false := by
  simp [readsContent]

/-- kept by the speaker, the content leaves everyone else the row reached, the person named
    included -/
theorem retraction_clears_the_audience (w : World) (r : Row) (k : Key) (hk : k ≠ r.producer) :
    readsContent .speaker w r true k = false := by
  simp [readsContent, hk]

/-- and the speaker keeps their own words -/
theorem speaker_keeps_own_words (w : World) (r : Row) :
    readsContent .speaker w r true r.producer = true := by
  simp [readsContent]

/-- the kept copy can still be filed: the report made from it is a duty-holder's record the
    person who retracted the speech cannot close -/
theorem kept_copy_is_fileable (w : World) (r : Row) (m k : Key) (shield : Bool) (hk : k ≠ m) :
    readsContent .speaker w r true r.producer = true ∧ mayWithdraw (asReport r m shield) k = false :=
  ⟨speaker_keeps_own_words w r, warning_channel_not_closable r m k shield hk⟩

/-! ## The worked world

  Everyone = keys 1..9. Cohort 1 is a community whose roster is {1, 2, 3} until instant 5, when 3
  is removed, leaving {1, 2}. Key 7 belongs to no cohort. Key 9 is a stranger invited by 1. -/

def room : Cohort := ⟨fun t => if t < 5 then [1, 2, 3] else [1, 2]⟩
def w : World := ⟨[1, 2, 3, 4, 5, 6, 7, 8, 9], [room]⟩

/-- member 1 scores member 2 inside the room, at instant 6 -/
def scoreAbout2 : Row := ⟨1, 1, 6, .scores, [2], [], .peer, .person, false⟩
/-- member 1 scores 3 at instant 6, after 3 was removed -/
def scoreAbout3Late : Row := ⟨1, 1, 6, .scores, [3], [], .peer, .person, false⟩
/-- member 1 scores 3 at instant 4, while 3 was a member -/
def scoreAbout3Early : Row := ⟨1, 1, 4, .scores, [3], [], .peer, .person, false⟩
/-- member 1 names outsider 7 inside the room, nothing delivered to 7 -/
def about7 : Row := ⟨1, 1, 6, .scores, [7], [], .peer, .person, false⟩
/-- a proposal: member 1 invites stranger 9, the family delivering the row to 9 -/
def proposalTo9 : Row := ⟨1, 1, 6, .scores, [9], [9], .peer, .person, false⟩
/-- a hard_case about member 2, filed by 1 -/
def hardCaseAbout2 : Row := ⟨1, 1, 6, .scores, [2], [], .dutyRecord, .person, false⟩
/-- the room removes 3: a cosigned row naming 3 -/
def removal3 : Row := ⟨1, 1, 5, .cosigned, [3], [], .peer, .person, false⟩
/-! The four scenarios. Key 4 is the room's named moderator; key 8 is a business (an affiliation)
    that is a member of the room; key 5 is a court (an affiliation). -/
/-- 1. a conviction: the court's act about member 2 -/
def conviction2 : Row := ⟨5, 0, 6, .scores, [2], [], .authorityAct, .person, false⟩
/-- 2. a bad review of the business by member 1 -/
def reviewOf8 : Row := ⟨1, 1, 6, .scores, [8], [], .peer, .affiliation, false⟩
/-- 3. malicious gossip: member 1 about member 2 -/
def gossipAbout2 : Row := ⟨1, 1, 6, .scores, [2], [], .peer, .person, false⟩
/-- 4a. a warning about member 2 made as peer speech by member 1 -/
def warningAbout2 : Row := ⟨1, 1, 6, .scores, [2], [], .peer, .person, false⟩
/-- 4b. the same warning filed with the named moderator (key 4), reporter shielded -/
def reportAbout2 : Row := asReport warningAbout2 4 true

/-- the audience rule lets a community speak about its own members -/
theorem audience_admits_a_score_about_a_member : admitAudience w scoreAbout2 = true := by decide
/-- the strict reading forbids it: a community could score nobody but the scorer -/
theorem strict_refuses_a_score_about_a_member : admitStrict w scoreAbout2 = false := by decide
/-- the loose reading admits a row whose subject can never see it: standing without reach -/
theorem loose_gives_standing_without_reach :
    admitLoose w about7 = true ∧ hasStanding about7 7 = true ∧ reaches w about7 7 = false := by decide
/-- the audience rule refuses that row -/
theorem audience_refuses_the_unreachable_subject : admitAudience w about7 = false := by decide
/-- the delivered key is within the audience: an invitee may be named -/
theorem invitee_is_reached : admitAudience w proposalTo9 = true ∧ reaches w proposalTo9 9 = true := by decide
/-- membership is judged at the row's instant: a member removed before it is outside -/
theorem removed_before_the_instant_is_outside :
    admitAudience w scoreAbout3Late = false ∧ admitAudience w scoreAbout3Early = true := by decide
/-- a subject of an admitted row may withdraw an ordinary score and only contest a hard_case -/
theorem subject_withdraws_a_score_contests_a_hard_case :
    mayWithdraw scoreAbout2 2 = true ∧ mayWithdraw hardCaseAbout2 2 = false ∧ mayContest hardCaseAbout2 2 = true := by decide
/-- the removed member cannot withdraw the cosigned removal, and may contest it -/
theorem removal_is_contested_not_withdrawn :
    mayWithdraw removal3 3 = false ∧ mayContest removal3 3 = true := by decide

/-- 1. the convicted person contests and cannot retract; the court may withdraw its own act -/
theorem conviction_is_contest_only :
    mayWithdraw conviction2 2 = false ∧ mayContest conviction2 2 = true ∧ mayWithdraw conviction2 5 = true := by decide
/-- 2. the business never retracts the review; it contests, and the reviewer is attributed -/
theorem business_never_retracts_a_review :
    mayWithdraw reviewOf8 8 = false ∧ mayContest reviewOf8 8 = true ∧ reviewOf8.producer = 1 := by decide
/-- 3. the person retracts gossip about themself, and may also contest it -/
theorem gossip_is_retractable :
    mayWithdraw gossipAbout2 2 = true ∧ mayContest gossipAbout2 2 = true := by decide
/-- 4. the warning as peer speech is retractable by the accused; filed with the moderator it is not,
    the accused still contests it, still sees that it exists, and does not see the shielded reporter -/
theorem warning_peer_retractable_report_not :
    mayWithdraw warningAbout2 2 = true ∧
    mayWithdraw reportAbout2 2 = false ∧ mayContest reportAbout2 2 = true ∧
    seesExistence w reportAbout2 2 = true ∧ seesContent w reportAbout2 2 = false ∧
    admitAudience w reportAbout2 = true := by decide

/-- 5. member 2 retracts member 1's warning. Kept by the speaker: 1 still holds it, 2 no longer
    reads it, and 1 may file it with the moderator, where 2 cannot close it. Shown to the room, 2
    would still read it. Kept by nobody, 1 would hold nothing to file. -/
theorem retracted_warning_is_kept_and_fileable :
    mayWithdraw warningAbout2 2 = true ∧
    readsContent .speaker w warningAbout2 true 1 = true ∧
    readsContent .speaker w warningAbout2 true 2 = false ∧
    mayWithdraw reportAbout2 2 = false ∧
    readsContent .room w warningAbout2 true 2 = true ∧
    readsContent .nobody w warningAbout2 true 1 = false := by decide

end Standing
