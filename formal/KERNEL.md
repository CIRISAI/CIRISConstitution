# The kernel

One function. A node gives it the rows it holds or has been offered, the present instant and its own key. It
returns what every row means to this node, what the node may do, what it owes, and what to copy to whom.
Everything else a node does is storage, transport or presentation.

This page is the specification an implementation builds to. Each statement is marked:
**proved** (Lean, `formal/causal_order`), **run** (executed over every case to a bound, `formal/causal_kernel`,
`formal/roster_fork`, `formal/kernel_lib`), **measured** (counted from the rule tables or the reported decision
sites, `formal/derivation`), or **open**.

## 1. Inputs

| Input | What it is |
|---|---|
| rows | the signed rows the node holds or has been offered, each with the instant the node first saw it |
| now | the node's own clock |
| own key | the key the node signs under |

There is no trust set among the inputs. Who a node trusts is a fold over the rows its own key signed
(CC 4.4.3.8). **proved**: `Causal.two_readers`, `no_own_edge_no_reach`.

Config is not an input. A value that binds others is a row signed by whoever decided it. A value that binds
only the node is a row under the node's own key. **measured**: 174 decision sites on the kernel's side read
config today. **open**: the constants are not yet all in `constitution/constants.tsv`.

## 2. The only order is what rows name

A row names other rows by digest: the row it answers, the head it extends, the proposal it votes on. That
relation is well-founded, since a digest cannot name a row that names it back. There is no sequencer, no
ranking by signed instant and no ranking by digest.

Two rows where neither names the other, directly or through others, are **concurrent**.

Judging each row as it arrives, against what was admitted so far, is not a function of the rows.
**proved**: `Order.Two.arrival_not_a_function`. **run**: seventeen cases from the rule tables each give two
results from one set (`formal/derivation/order/witnesses.tsv`).

## 3. Three layers

| Layer | Reads | Property |
|---|---|---|
| **kept** | the row alone, and whether the rows it names are kept | the least set closed under the door; the same in every arrival order; a row waits for what it names and is never refused for another row |
| **concluded** | the row against its ancestors | one solution, negation and counts allowed; final once the row is kept, for a rule that reads no row concurrent with it |
| **derived** | conclusions over a set of rows | a function of the kept set, the node's key and, in one place, now |

**proved**: `kept_is_least`, `door_any_order`, `close_saturated`, `door_spec`, `door_perm`, `conclOf_unique`,
`concl_final`, `concl_new_row`. That each layer is a function of the set it reads follows from how it is defined;
the content is in these: the door stops and ends at one set in every order, and the conclusion has one solution.
**run**: 6,606 sets of up to six rows in 2,182,671 arrival orders, one answer each. That is the bound the
continuous build runs; `--bound 5` is a shorter run of the same check.

Only the first two layers are final. A derived answer can be changed by a later row. **run**: after a counting
cut on a slot, no key changed that slot but one that may cut it. A key whose standing has ended can still
change what a reader with no acknowledgement of its own concludes (8a).

## 4. Operators

Every rule cell is written in these.

| Operator | What it does |
|---|---|
| select | rows matching a pattern on their fields |
| group and reduce | the least, the greatest, the one distinct value, the count of distinct values, or the sum; a tie between two different rows is refused, never broken by position |
| interval | whether a value lies between an opening and a closing |
| table cell | the value a typed table gives for a key |
| bounded repeat | a step applied until nothing changes |
| closure over what rows name | the past of a row; no cell needs more |
| integer arithmetic | an opening plus a duration, a fraction of a base; no floating point |
| join on a named row | two rows that name the same row; one cell uses it |
| result assembly | a verdict for each element, or a set of effects |

The first six are in `formal/kernel_lib`. **run**: six models rewritten with the first five agree with their
originals on 400,300 comparisons, and the closure agrees with a hand-written definition on 15,864.

**One language.** `tools/kx.py` is one expression language over these operators, and `tools/kx_prelude.kx`
writes each of the eight named answers once in it. `tools/kx_translate.py` translates the cells of the five
authoring grammars and the policy table. **measured** (`tools/kx_check.py`, on the repository's own text):

| Grammar | Translated in full | Translated with a word dropped |
|---|---|---|
| guards | 43 | 14 |
| folds | 162 | 28 |
| changes | 31 | 31 |
| reactions | 61 | 50 |
| policy text cells | 16 | 39 |

Every translation agrees with a reference reading on generated row sets, and the policy rows agree with the
policy table's own vectors. Four of the five grammars had a parser and no evaluator, so for those the reference
reading is this work's own and agreement shows the translation matches that reading, not the text. A cell that
uses a word the translation does not carry is not counted as translated. The dropped words are listed as
data, among them `@decision`, `@count`, `@seating` and `@prior`, which no text defines.

The check holds these counts, and each may only fall (`tools/kx_maxima.tsv`). For an order it holds the total
and the count across signers. The count of one signer's own rows is shown and not held, since a cell moving
into it from the count across signers is the intended movement.

| Count | Now |
|---|---|
| a cell orders rows of different signers by a signed instant | 0 |
| a cell orders rows of different signers by a digest or a key id | 0 |
| a cell orders one signer's own rows by a signed instant | 102 |
| a cell orders one signer's own rows by a digest | 94 |
| a cell compares the signed instants of two rows | 15 |
| a cell reads arrival outside a clock | 1 |
| floating point in a cell | 9 |
| a fold a reaction calls and no cell defines | 11 |
| a refusal on a clause that reads another row | 4 |
| a count over the set its own outcome changes | 11 |
| a cell with a dropped word | 126 |

One voice may order its own rows. The fold default (CC 3.5.1) evaluates each signer's chain on its own: between
two acts of one kind by one signer on one named row, the later signed instant wins and the lower row id breaks
a tie. A signer who back-dates changes only what the signer itself says, so the two rows for one signer's own rows
are allowed and are counted only to keep them in view. The two rows for different signers contradict
section 2, since they order rows by a value one of the signers chose, and are held at zero. A cell counts as one signer's own only when its expression fixes the
signer in the group it orders; any other cell counts as across signers. A session's key names the self, so
its claims count as one voice's own (section 5). No cell orders across signers. A trace-consent grant, the two
halves of a partnership, a key revocation, a licence, a quarantine marker and the winner's acceptance are each
decided by a party's own rows, a count or a fixed order on kinds (section 6). A listing is not a ranking: the
moderator ballot's shown order and the roster's member order give each row a position that no operator reads, so
no row is picked or removed by it. The check reads that from the cell's expression, and the same comparison read
as a pick is counted across signers. **measured**.

## 5. Named answers

Eight. Each is a composition of the operators, and each role, window, policy and constant is data.

| Answer | Question | Layer |
|---|---|---|
| **state** | is this row live: admitted, withdrawn, recanted, superseded | derived: the order on kinds is read over rows concurrent on one target, so a later retraction changes it |
| **stands** | does this key hold this relation over this object | derived: a bounded walk of live edges |
| **tally** | is this count met, over the head it names | derived |
| **may** | may this key do this act on this target; if not, which row is missing and who could sign it | derived |
| **audience** | who is this row for | derived: a row's audience includes that of every row naming it, and such a row may come later |
| **missing** | which rows does this conclusion depend on that are not held | kept |
| **owed** | what must this node now emit or do | derived |
| **window** | has this window closed, and with what outcome | derived; the one answer that reads now |

**stands.** One act: a voice consents to what binds it. A relation stands when every voice it binds has a
concluded consent, the consents are tied by one naming the other, none is withdrawn by its own signer, and no
cut removes it. The number of voices is not a parameter; it is read off who the relation binds. A permission
gives something of the signer's own and binds nobody else, so one row carries it. A duty binds the one who
places it and the one who carries it, so it takes two consents. That pair is the **seat**: it is two consents
and not a second object, and it stands the same whichever of the two signed first. Nobody is bound by the rows
of others, any bound voice ends it alone, and no third key ends it without a cut. **proved**
(`Consent.lean`): `silent_voice_not_bound`, `unbound_rows_change_nothing`, `only_bound_voices_end`,
`one_voice_one_row`, `two_voices_two_rows`, `seat_is_two_consents`, `holder_first_stands`. Where a body places the duty,
the body is one party and its consent is a count of its members' signatures on the row. **proved**:
`count_needs_holder`, `one_voice_is_not_a_count`, `count_of_one_is_one_row`. A signature is part of the row, so
a count once met is final: no member's later row lowers it, and only the holder's own withdrawal or a cut ends
the duty. **proved**: `count_is_final_against_members`, `only_holder_or_cut_ends`, `holder_still_ends_its_own`.
A member who changes its mind signs a new counted act, or answers through a window under recount. The members
are those at the head the row names. **proved** (`RosterHead.lean`): `membersAt_function`,
`counted_over_named_head`, `no_self_admission`. The rule that a member may withdraw a counted
voice is rejected, since it lets one signature unseat a member. The file keeps it under `Rejected`, with its
counter-model.

Who may place a duty is one parameter with three values: the object's own key, a key holding a seat that may
confer, or a group whose count is met. A key
stands when a bounded walk of live seats leads to it from a root. For what a row means to this node the root is
the node's own key. **proved**: `no_offer_no_seat`, `no_acceptance_no_seat`, `third_key_cannot_end`,
`only_withdrawals_and_cuts_end`, `means_is_seat_walk`. **run**: 2,727 sets in 587,536 arrival orders.

The 23 role names of the tables are not 23 things. **run** (`formal/causal_kernel/role_shapes.tsv`): the seat
covers 18 of them, three are read off the row judged (`author`, `self`, `subject`), `winner` is a tally, and
`tally` fits none because its holders are drawn from a group secret that is not a row. Appointed `moderate`,
`review`, `slash` and `takedown` are one seat with four scopes. `owner` and the steward of an agent are one
seat. `member`, an accord holder and a key of a self roster are one counted seat over three objects. `serve` is
two seats required together, which is a question for **may**.
The text states the second consent wherever it places a duty: a delegation that carries a scope seats its
delegate only with the delegate's own signature (CC 4.4.3.4.3), and a custodian holds custody only with its own
(CC 7.5.5). Those two sentences cover the fourteen rows that stated a conferral and no acceptance. Three places
need none and say why: a node in an infrastructure community, a key of a person's own roster, and a device
under its owner. **open**: how the second signature travels and from when a delegation without it stops
seating are not settled. **measured** (`manifests/family_model.json`, `formal/derivation/confers_text.tsv`): what a family confers is
stated for 159 of 184 families. 134 claim and content families take one default, that a claim seats no one
(CC 3.4.5.1). Twenty consents take their seat from `family_shapes.tsv`, and five families have a sentence of
their own. **open**: 25 families confer nothing that a sentence states: 21 doors, three consents the shape
table cannot run, and the consent prefix. Which segment of a family's name binds a key is filled for 155
families; 29 have a segment that names another row and no word yet says so. Which answers read a family's
rows is filled for all 184 from the expression language: every family is read by **state** and **stands**
through the default fold, a default checked for none of the 83 that take it, and 41 are also read by another
answer. A row that must equal its own recomputation is stated for three families (CC 6.1.9) and for no other.

**may.** The door, the control a person is offered and the gate on serving a row are one answer
(`manifests/transitions.json` states it so). A refusal is a named missing row. **open**: guards are typed on 26
of 459 transitions, and "receive" is not yet a verb of the table.

**missing and copying.** A row moves to a peer because that peer must conclude something and lacks it. What
to send is what lies among the ancestors of what the peer must conclude, within the row's audience. This is
the closure a store already computes for its own retention, evaluated for the other party. **run** (`formal/causal_kernel/route.py`): a
party given only its routed rows concludes the same as a party given everything, and a stranger is routed
nothing. That holds only with one rule added: a row carries its audience to the rows it names, when it is
concluded, sits in the same room and its signer is already in the named row's audience. Without it a joiner can
never keep its own admission. With it, a reply carries the message it answers to a later joiner. A row leaves
its room only by its own signer's act: a row that names it from another room carries it only when the same key
signed both (CC 5.2). No member carries another member's signed row out. **proved** (`Carry.lean`):
`nothing_leaves`, `others_elsewhere_change_nothing`, `author_carries`, `same_room_unchanged`. The cost: a cut
that names a row of another room waits until that row's signer carries it. What must not travel is proof of
who said it or of who is in the room, which is section 7b. **measured** (`formal/derivation/placement_text.tsv`): no placement cell
is empty. Of 184 families, 147 take the one default, the scope each row carries with the audience CC 5.2 gives
it, and 21 are placed by a sentence of their own. **open**: the default is stated once for all families and is
checked for none of the 147. The copy rule is a row of that table.

**window.** A row opens a clock. An answering row closes it, or time does, and the table states the outcome at
the close. A window names its opener and the acknowledgement by which the concluding party first held it. Where the
outcome binds others, the concluder signs it as a landing row naming that acknowledgement and its own head.
Where it binds only the reader, each node reads it on its own clock and signs nothing. **measured**: 19
clock entries have this shape, 16 of them counted from receipt. The other 21 are a row stating its own end,
read from the row alone against now.

A landing that states an outcome its own past does not give concludes nothing. An answer concurrent with the
landing is **recounted**: it is counted with the landing's past, and the landing stands only if the table still
gives the outcome it stated. **run** (`formal/causal_kernel/window_adversary.tsv`): against the three windows
of the text, twenty checks of what each exists to prevent. Recount breaks none. The check that a thief does
not evict alone holds against an owner who signs anything inside the window; an owner who signs nothing
looks lost. A landing that voids concurrent
answers breaks seven, a thief evicting alone among them. An answer that contests any landing breaks two.
**proved**: `Recount.dishonest_never_stands`, `stands_is_table_over_all_not_late`, and `quorum_closed_final` (a
landing with a strict majority behind it is final where no key has answered both ways), and
for the two rejected rules `ruleI_concluder_decides`, `ruleII_never_final`. What recount costs: a lone landing is never final against a key that can still sign, and the
window's length is the concluder's own word.

**The door's parameters.** One door runs every policy row and every clock that takes answers. **run**
(`formal/causal_kernel/door.py`, `check_door.py`, `doors.tsv`): all eighteen policy rows, ten clocks and a deferral's own end run on
the window's own receipt, landing and recount, as instances at rooms of three and four keys. Each gives one
answer in every arrival order, the recount agrees with the policy table's own vectors and with the ranked
count, and every deliberate break is caught. The policy table states the count, the floor and the length. The door needs five more things. The reactions
table now states the first two as a `land` clause on each window, each cell quoting its sentence:

| Parameter | Why it matters |
|---|---|
| who concludes, and with which row | if a holder lands the halt's lapse, one holder lying about its clock lapses it at every node; if each node lands its own, only that node's does |
| whether a late answer counts | a confirmation after the fuse has lapsed confirms nothing |
| whether the opening act is in force while the window is open | a halt is, a moderation proposal is not; not yet run |
| the joiner's own yes as a voice of the floor | without it an invitation by one member of two never lands |
| the threshold as the room's declared protocol | a removal is cosigned under the room's own protocol |

**measured**: all thirteen answerable windows state their concluder, and the invitation's expiry does. The
decider closes an agent's objection window at retirement by the `decided` row, which names the objection
(CC 7.5.5). **run**: a `decided` row that leaves out an objection the agent made concludes nothing, and the
agent's own landing closes nothing. Where the text has
each node read the close on its own clock, the cell says `local` and nothing is signed: the moderation window,
a harm report, a person's own roster and the halt's fuse (CC 4.5.13, CC 3.3.6.3). A late answer is closed for
the fuse, an invitation and the accord's roster change, and counts for an election and a takedown. The last
three parameters are still in no cell. `doors.tsv` lists 73 things the tables do not state, 15 of them on the four
doors of the poll, the adjudication and the deferral.

Six of the nineteen clocks are not doors: two freshness checks, two of the node's own storage and liveness, and
two duty deadlines that take no answers.

**Two notions of time.** A row's own stated end, read from the row against now, and a window with a landing.
**run** (`formal/causal_kernel/check_time.py`, eleven readings over 86 worlds of two rows): these two replace
the freshness window, by the cut, and an invitation's expiry, by a window that shuts out a late acceptance. A
registered name is held by what the registrations name (CC 4.5.1.3). Two readings are not covered. A cosignature
is attached against the node's clock at first receipt, which the two notions cover only if the cosignature
states its own end. That one is **open**. A session goes to the earliest claimed instant among one
person's own devices (CC 3.1.3.1). This is the one ranking by a signed instant that is kept, and on purpose:
both claimants are one person's keys, so it is one voice ordering its own rows, and a back-dated claim gains at
most one lease against that person's other devices.

## 5a. Two mechanisms, four shapes

Every row family is one of four shapes: a **consent**, a **door**, a **claim** or **content**. A roster is a
consent given by a count, and an acknowledgement is a claim. **measured**
(`formal/derivation/family_shapes.tsv`, `formal/causal_kernel/check_shapes.py`): of the 184 families, 110 are
claims, 24 content, 24 doors, 16 consents and 7 both a consent and a door. Three fit none.

The four are labels over two mechanisms. Removing the shapes in order, three orders leave the same two:
consent and the door. Content is carried by consent, since its audience is the holders of a roster and its
life is the **state** answer. A claim is carried by consent, since what it means to a reader is the reader's
own one-voice consent, walked from the reader's key. Nothing else reads now, so the door stays. Nothing else
makes an offer stand, so consent stays. **proved** (`TwoMechanisms.lean`): a claim is the reader's one-voice consents walked, in full; content's
audience is read off roster heads and naming rows, for the three audiences of section 7. That the door reads
now, and that consent is no window's outcome, are proved on stated models. The sorting of the families into
shapes is **measured**.

| | Families |
|---|---|
| every parameter traced to a table cell or a quoted sentence | 171 |
| a guessed parameter | 0 |
| cannot run | 13 |

No parameter is guessed. Key revocation states its three revokers (CC 2.4.1.1): the key's own revocation and
the roster's count are **run**, and the owner's revocation of a key it owns is **open**, since no seat ends
another key's seat here. Nineteen content
families take their audience from the default placement, the scope each row carries, and state none of their own. Each family that cannot run lacks one thing, named in the table:
two are doors with no row in `doors.tsv`, two are consents with no stated conferrer or signer, five are census
families whose count is drawn from a group secret that is not a row, and four are labels or prefixes that
confer nothing. A family is counted as traced when its
own parameters are; most door rows still rest on parameters the tables do not state (section 5). **open**.

## 6. Conflict between concurrent rows

1. **Different kinds on one target** are decided by a fixed order on kinds. **proved**: `wins_unique`.
2. **The same kind on one slot**: both or neither. No rule that cannot tell two rows apart can pick one.
   **proved**: `holder_both_or_neither`.
3. **A row that names both may decide.** **proved**: `Slot.descendant_decides`.
4. **The cut.** A row on a slot by whoever may conclude it. Once it counts, rows on that slot concurrent with
   it do not count; rows in its past stand; rows that name it are judged at the head they name. A removal is a
   cut on a key and a deciding row is a cut on a contest. **run**: 4,898 sets in 440,291 orders.
5. **Equal standing.** Two cuts by keys of equal standing that undo each other stay contested. What settles it
   is a voice the other cannot remove. **run**. So no slot that matters may be held on one signature: that is a
   requirement on the tables, and nothing yet checks them for it. **open**.

A row of a removed key counts when the removal has it among its ancestors: something the removal can see had
already named it. **proved**: `only_removals_stop_counting`, `sign_after_removal_never_counts`.

## 7. The roster is the one ledger

A group's roster is a lineage: each version names the heads it extends and is counted over their members.
Every other row takes its place from the roster head it names. Nothing else is ordered.

Two versions of one head wait. The roster is then the members common to all tips, until a version naming the
tips makes one head again. **run** (`formal/roster_fork/fork_check.py`): over every set of up to three
versions an adversary below the count can cause, in three settings under two counting protocols, the roster is
a function of the set, no removed key is listed, and a removal naming an old head gains nothing. Four further
protocols were run once at the same bound and are not in the check.

**proved** (`RosterHead.lean`): the members at a head are a function of the head, its signatures and its past
(`membersAt_function`, `standing_final`). A removal is a later counted version and changes the members there,
not at the old head. A member's own leaving binds the same way, by causal past. Where the count asks two or
more, one key's rows remove nobody: a member leaves only by its own withdrawal or by the signatures of two
distinct members (`one_signature_never_removes`). A removed key counts again only after a version lists it
again (`readmission_needed`). Two concurrent versions of one head are not decided there; they wait as tips.

An adversary holding the count of an old head signs a valid version alone. A witnessed lineage answers that
(CC 3.2 T6), and it is each reader's own trust that decides whose witnesses count.

The text states the rule (CC 3.2 T6). **open, on the wire**: a roster version names one head today and must be
able to name several; the store's shape is an optional list of further heads beside the one it names now.

**One mechanism, five instances.** A person's keys, a voice's room keys, a room, the accord and an
infrastructure community are this one roster with parameters read from the policy table and the text. **run**
(`formal/causal_kernel/check_rosters.py`): 77 properties that each instance's own model or text claims, in every
arrival order to a cap, each with a deliberate break that is caught. The plain mechanism was wrong in four
places and a stated parameter restores each: a floor of two voices under every protocol, the joiner's yes
counted, an acceptance spent once its key has left, and the lone path kept to a person's roster. Two limits:
the accord's rule that a removed holder no longer fires needs a latch at the node's receipt, which is not a
function of the rows, and the parameters for removing a key from a voice are guessed.

A public room's roster is public (CC 3.2). A post is proved outside the room only with the rows that seat its
author, and anyone who asks a member's node reads them. So an audience is the members of a roster, everyone, or one named key.
An invitation goes to a key the roster's open offer names.

## 7a. A writer's keys are a fold

Who is entitled to a wrap of which key is seats and cuts. The epoch is the count of the writer's mint rows, and
a rotation is due when a holder of the current key is no longer entitled. None of the writer's state resists
being a fold over its own rows, on one condition: each write and each mint names the head of the membership
rows the writer held. **run** (`formal/causal_kernel/keyplane.py`): 402,950 comparisons with
`formal/key_plane`, none differ. It also found that a re-admitted member's second live device is not wrapped at
the seat.

## 7b. A private room seats voices

A community declares itself in its founding row: `membership` is `private` or `public`, and an absent member
reads `public`. A room goes from private to public and never back. A self room and a family are seated by
identity keys. The rule is CC 3.1.3.2, and the kernel is not changed by it: a room key is a key.

In a private room the roster seats a **voice**, never an identity. A voice is a small counted roster of **room
keys**, one for each device, made for that room only, and every row of the room is signed under a room key, a
duty holder's verdict included. That a voice is a given person's is the **binding**. It is never a row and
nobody signs it. It is made for one addressee, who can check it and cannot prove it to anyone else. The seat
row of a room key carries a commitment to its person, and a binding that does not open it is refused.

No answer of section 5 reads a binding. It is read to show a member who spoke, to check a joiner before a
widening, and to count persons.

All of this is **run** (`formal/causal_kernel/check_roomkey.py`). Nothing in this section is proved in Lean,
and the verdicts on the binding are symbolic: a fact has a set of parties able to make it, and a party is
convinced when nobody but the person named could have.

- **The kernel does not care which key.** Every named answer for one room of 34 rows is the same over voices as
  over identity keys, under a renaming that reverses the order of the names: 691 sets of rows, 22,468 answers in
  two arrival orders. Who is entitled to a wrap is the same over 1,791 sequences of membership acts.
- **One person, one voice.** A tally over voices equals the count of persons in each of 1,728 ways for the
  devices of three persons to vote; a count of keys is wrong in 1,216. A person already seated gains a second
  voice only when every signer of that admission did not check the binding.
- **The binding.** Of five ways to make it, the planned one (two encapsulations and no signature) and a
  designated-verifier signature are authentic inside and deniable outside: 0 of 180 coalitions forge, 0 of 14
  prove anything. An identity signature, sealed or plain, lets 14 of 14 prove it. A code under the room's shared
  key is forged by 168 of 180.
- **A count of persons waits.** It is missing at a node for exactly the bindings that node lacks, over 20,736
  pairs of nodes, and no two nodes holding every binding disagree. Without the commitment two members who share
  a key make honest nodes count differently in 108 of 243 votes. With it none do: the node told otherwise
  waits and names the key. A withheld binding is a stall at that node and never a fork.
- **What a holder of rows can prove.** Under identity keys a reply carried elsewhere brings 15 rows of roster
  ancestry and proves all four members. Under room keys none of 657 sets of rows of the room proves or names a
  person, and a custody claim names none.
- **An identity signature on any one kind of row undoes it.** Speech, a vote, a roster event, an acceptance, an
  acknowledgement or a window row signed under an identity key lets between 8 and 14 of 14 coalitions prove
  something about another person.
- **Detection.** The owner-binding of a node's room key is a row of the room, read by any holder of the rows.
  The detector's seat is conferred inside the room by the act that enables the list, and no outside root is on
  the walk to it. The notice is admitted when its signer owns the detecting key by that row. The record names
  no person, and withdrawing the enabling ends the seat.
- **The declaration.** An absent member reads public; a founding row of a self room or a family that declares
  is refused; `private` on a body that is public by function is refused; of 434 sequences of later declarations
  none goes from public to private.

**open**: the wire. The commitment, the two encapsulations, the key pair kept for bindings and the sealed
invitation are planned for a later edition and are the implementer's (CC 3.1.3.2). **open**: no proof. The
statements above are runs to a bound over a symbolic model.

What a private room does not give, each marked as the check marks it:

| Limit | How known |
|---|---|
| Deniability against a verifier who cheats, with a post-quantum key exchange, is conjectured and not proved | stated; the run shows only that a challenge its maker cannot open would make the confirmation transferable |
| A member cooperating live with an outsider can prove what it sees | **run**: the outsider supplies the challenge and is convinced |
| A member's word is always possible; what is removed is the proof | stated |
| One signed row by the person outside the room, tying the room key to themself, makes that person's history in the room provable | **run**: eleven rows of one member, and no other member's |
| A room already signed under identity keys stays provable | **run**: all four members; a later declaration of private concludes nothing |
| A removed member keeps the bindings it was given | **run** |
| Custody claims and delivery still reach a node; a network observer learns which nodes receive a room's rows unless delivery goes by the anonymous tier | **run** for the claim, which names no person; the network is outside the model |
| A new key record appears when someone joins | **run**: each admission seats a key the head it names does not seat |
| Erasure by person finds a person's room rows only through that person's own devices | stated |
| A private room is out of reach of an order naming a person, except by testimony or by a member's device | **run**: no set of rows of the room names or proves a member |

## 8. What the kernel does not give

- **No finality across readers.** Two nodes with the same rows conclude the same. A settled slot can be
  reopened by a key with standing on it. Finality is each reader's, from what it has itself acknowledged.
- **No conclusion from silence without a clock.** A window closing unopposed, and the lapse of an unconfirmed
  halt, are read on the node's own clock. Nodes may differ while a window is open.
- **No decision that is not a function of rows.** Link and load decisions, retries, rendering and the prose
  rules given to a model stay outside.

## 8a. Attacked

`formal/causal_kernel/check_attacks.py` runs thirty-four attacks, thirty-three of them drawn from the published
failures of comparable systems, as 126 scenarios in 116,943 arrival orders: every order of a scenario of up to
seven rows, and a fixed sample of a thousand above that. **run**: thirteen gain the attacker nothing, none gains
what this page does not concede, fifteen are the limits below, and six cannot be expressed without a second
implementation, a byte form, a storage model or a request protocol. The class each attack must fall in was
written by the authors of the rules, so this check confirms what they expected and is no independent test.

Eight attacks did gain something before these rules were added. Each rule is part of the kernel and **run**.
Each is **proved** over the definitions of the earlier proof files (`formal/causal_order/Harden.lean`,
`Harden2.lean`, `Harden3.lean`, and `Reader.lean` for a reader's own line as the kernel runs it), within the
limits that folder's README lists.

- a row of a key whose seat was ended counts in a window only if the ending row has it in its past;
- a landing that does not stand says nothing against one that does;
- a cosignature is a voice only for a row counted over a head the cosignature itself names;
- an offer conferred by a count is ended by its holder or by a count, never by its proposer alone;
- among several founding keys one founder's unseat concludes nothing, and a founder's own offers live only
  while that founder's seat does;
- a row that names another adds its audience to it only if it is concluded, its signer was already in that
  audience, and it sits in the same room or is signed by the named row's own signer;
- the holders of a counted scope are the keys common to the tips;
- a counted row counts only if every counted row it is built on counts.

**A reader's own line.** A reader that has acknowledged a head does not let a line from below that head
displace it: for that reader such a line is void, however many rows it has. A sibling of the acknowledged head
waits as a tip, and a version naming both is accepted. This is each reader's own, and it ranks no line for
anyone else.

**No line wins by being longer.** A rule was tried under which a counted row left behind every counted act
that named only older heads. It is not part of the kernel. Under it a seated key and a removed key, signing two
rows, out-run the honest line and list the removed key again; and applied to a window, a majority voids a
present moderator's answer. Both are run as the reason (`checkpoint.py`, off unless asked for). Nothing is
ordered except by what rows name.

What that leaves, each **run** with its witness:

| Limit | Who can use it | How far it reaches, and what ends it |
|---|---|---|
| A fork on a past head by a past count | keys that met the count at any past head (one seated key and one removed key suffice) | unlists members, never lists one; for a reader with no acknowledgement until a counted row names both tips, counted over the common keys (the forger alone here: for good); a reader that acknowledged an honest row counted over a newer head is not moved; from the head the newest honest row is counted over, every reader until the honest line has one more counted row |
| A relay choosing the order of delivery | a relay ordering delivery; no key | until the withheld row is delivered; an emission made meanwhile cannot be unsent |
| A landed window reopened | one key counted at the opener's head that still holds its seat | no deadline; until a concluder signs a landing naming both, which must state the flipped outcome; the checkpoint is not applied to window answers |
| A landing over an objection that never reached the concluder | a relay between objector and concluder; no key | as long as the eclipse; ends when any concluder lands naming both |
| The concluder's own clock | any one key holding the concluder's seat | a lone window has no length against a lying concluder; ends when the target or a counted key signs and a landing names both |
| A stale proposal forcing the tips to wait | a member below the count holding a stale honest proposal on any past head | one flood per pocketed proposal; each ends with a merge by the count; a reader that acknowledged a merge is not moved by a later flood from below it |
| An invariant of the form "at least one" | two honest keys acting concurrently | 'at least one' is kept by no rule of the kernel; for a community the text gives the way back: with no duty holder left the room locks and the members' count seats one (CC 4.5.4) |
| A fork by the count of an old head | keys that met the count at an old head, signing one version | only against a reader with no acknowledgement of its own: its roster is the keys common to the two lines (nobody), for good |
| The same, by leaked keys of removed members | whoever holds removed keys that once met a count | only against a reader with no acknowledgement of its own, as test 18 |
| A new reader's first view | whoever controls a new reader's first view | until the reader withdraws its own rows; its own acknowledgement makes the wrong head stick |
| A row withheld from some | the cut's own signer, or a relay, by omission | as long as the row is withheld; a row cited from another room is carried only by its own signer, so a cut that names one waits until then |
| Rows signed to no purpose | any key at all, one signature a row | no answer moves; storage and read time grow without a bound in the kernel |
| History carried by a reply | any one member, by replying | intended carriage, row by row; cannot be undone |
| One conferring seat seating many | one seated key whose seat may confer | one row seats any number of keys; ends with one withdrawal by its conferrer |
| A line of several rows forged by a past count | keys that met the count at an old head, signing any number of rows | (a) a reader that acknowledged the honest head: nothing, the forged line is void whole (HOLDS for it). (b) a reader with none: plain tips-wait; no row is stale, the members are the keys common to the tips (the forger alone when it is on both lines), for good; a removed key is never listed |

Four of the fifteen are forms of one attack, a fork signed by keys that once met a count.

Two costs of the reader's line are stated here because no attack names them. An honest admission signed
offline on an old head is behind the line of a reader that has acknowledged a newer head, so for that reader
it is void, and so is a version built on it; it must be signed again on the newer head, or that reader and the
others differ for good. And whoever may end a moderator's seat can, by ending it, stop that moderator's answers
that the ending row has not seen from counting.

## 9. What stands between this and a build

| Item | Kind | Where |
|---|---|---|
| Which rows seat which key in which role: what 21 doors and 4 other families confer, 29 name segments that point at another row, the 23 roles as one walk | table data | `manifests/family_model.json` |
| Four guard clauses still refuse a row for another row; their sentences do not say what happens to the row | table data | `manifests/transitions.json` |
| A count taken when the fold is evaluated has no solution. It has left the policy table; eleven fold cells of other families still read `@decision` or `@count` | table data | `formal/derivation/fold_text.tsv` |
| A roster version naming several heads: an optional list beside the head it names now | wire | agreed with the store |
| One acknowledgement of a head covering everything beneath it, in place of one for each row | wire | agreed with the store |
| The default audience checked family by family for the 147 that take it; the transport reading placement and the copy rule as the `missing` answer | table data, with transport | `manifests/family_model.json` |
| Three door parameters in no cell: whether the opening act is in force while its window is open, the joiner's yes as a voice, the threshold as the room's protocol; and 73 things `doors.tsv` lists as stated by no table | table data | `manifests/reactions.json`, `formal/causal_kernel/doors.tsv` |
| 126 cells with a word the expression language does not carry, and eleven folds a reaction calls that no cell defines | table data | `tools/kx_maxima.tsv` |
| Constants out of config | table data | `constitution/constants.tsv` |
| How a second consent travels, and from when a delegation without one stops seating | wire | the implementers |
| The owner's revocation of a key, an election's tie and the older models, each against the rules as they stand | model | `formal/` |
| The signer gate written over the library | code | `tools/check_signer_gate.py` |
