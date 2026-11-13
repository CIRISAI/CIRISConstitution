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

Every rule cell is written in these. **measured**: 205 of 211 fold-cell parts, all 43 guard clauses and the 39
clock and expiry entries map onto them. **run**: six models rewritten with the first five agree with their
originals on 400,300 comparisons.

| Operator | What it does |
|---|---|
| select | rows matching a pattern on their fields |
| group and reduce | the least, the greatest, the one distinct value, the count of distinct values, or the sum; a tie between two different rows is refused, never broken by position |
| interval | whether a value lies between an opening and a closing |
| table cell | the value a typed table gives for a key |
| bounded repeat | a step applied until nothing changes |
| closure over what rows name | ancestors, concurrency, the frontier of a set |

All six are in `formal/kernel_lib`. **run**: the closure agrees with a hand-written definition on 15,864 comparisons.

## 5. Named answers

Eight. Each is a composition of the operators, and each role, window, policy and constant is data.

| Answer | Question | Layer |
|---|---|---|
| **state** | is this row live: admitted, withdrawn, recanted, superseded | derived: the order on kinds is read over rows concurrent on one target, so a later retraction changes it |
| **stands** | does this key hold this relation over this object | derived: a bounded walk of live edges |
| **tally** | is this count met, over the head it names | derived |
| **may** | may this key do this act on this target; if not, which row is missing and who could sign it | derived |
| **audience** | who is this row for | concluded |
| **missing** | which rows does this conclusion depend on that are not held | kept |
| **owed** | what must this node now emit or do | derived |
| **window** | has this window closed, and with what outcome | derived; the one answer that reads now |

**stands.** One shape, the **seat**. A key holds a seat in a scope over an object when a conferrer's offer
names it and the key's own acceptance names that offer, and neither has been withdrawn by its own signer, and
no cut removes it. Two voices: neither side alone makes a seat, either side alone ends it, and no third key
ends it without a cut. One row is both voices only when a key seats itself. The conferrer is one parameter with
three values: the object's own key, a key holding a seat that may confer, or a group whose count is met. A key
stands when a bounded walk of live seats leads to it from a root. For what a row means to this node the root is
the node's own key. **proved**: `no_offer_no_seat`, `no_acceptance_no_seat`, `third_key_cannot_end`,
`only_withdrawals_and_cuts_end`, `means_is_seat_walk`. **run**: 2,727 sets in 587,536 arrival orders.

The 23 role names of the tables are not 23 things. **run** (`formal/causal_kernel/role_shapes.tsv`): the seat
covers 18 of them, three are read off the row judged (`author`, `self`, `subject`), `winner` is a tally, and
`tally` fits none because its holders are drawn from a group secret that is not a row. Appointed `moderate`,
`review`, `slash` and `takedown` are one seat with four scopes. `owner` and the steward of an agent are one
seat. `member`, an accord holder and a key of a self roster are one counted seat over three objects. `serve` is
two seats required together, which is a question for **may**.
**open**: in 14 of 17 partly fitting rows the text states the conferral and no acceptance row. The `confers`
and `binds_segment` columns are still empty.

**may.** The door, the control a person is offered and the gate on serving a row are one answer
(`manifests/transitions.json` states it so). A refusal is a named missing row. **open**: guards are typed on 26
of 459 transitions, and "receive" is not yet a verb of the table.

**missing and copying.** A row moves to a peer because that peer must conclude something and lacks it. What
to send is what lies among the ancestors of what the peer must conclude, within the row's audience. This is
the closure a store already computes for its own retention, evaluated for the other party. **run** (`formal/causal_kernel/route.py`): a
party given only its routed rows concludes the same as a party given everything, and a stranger is routed
nothing. That holds only with one rule added: a row's audience includes the audience of every row that names
it. Without it a joiner can never keep its own admission. With it, a reply carries the message it answers to a
later joiner. That carriage of content is intended (CC 3.1.3.2). What must not travel is proof of who said it or
of who is in the room, which is section 7b. **open**: the placement cell is empty for 156 of 184 families and
no cell states the copy rule.

**window.** A row opens a clock. An answering row closes it, or time does, and the table states the outcome at
the close. A window names its opener and the acknowledgement by which the concluding party first held it. The
concluder signs the outcome as a landing row naming that acknowledgement and its own head. **measured**: 19
clock entries have this shape, 16 of them counted from receipt. The other 20 are a row stating its own end,
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

An adversary holding the count of an old head signs a valid version alone. A witnessed lineage answers that
(CC 3.2 T6), and it is each reader's own trust that decides whose witnesses count.

The text states the rule (CC 3.2 T6). **open, on the wire**: a roster version names one head today and must be
able to name several; the store's shape is an optional list of further heads beside the one it names now.

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
seven rows, and a fixed sample of a thousand above that. **run**: twelve gain the attacker nothing, none gains
what this page does not concede, sixteen are the limits below, and six cannot be expressed without a second
implementation, a byte form, a storage model or a request protocol. The class each attack must fall in was
written by the authors of the rules, so this check confirms what they expected and is no independent test.

Eight attacks did gain something before these rules were added. Each rule is part of the kernel and **run**.
Each is **proved** over the definitions of the earlier proof files (`formal/causal_order/Harden.lean`,
`Harden2.lean`, `Harden3.lean`), within the limits that folder's README lists. One of them matters here: the
reader's line is proved with the rejected rule of the next paragraph still inside its operator, so for that
rule the proof and the code do not yet say the same thing. **open**.

- a row of a key whose seat was ended counts in a window only if the ending row has it in its past;
- a landing that does not stand says nothing against one that does;
- a cosignature is a voice only for a row counted over a head the cosignature itself names;
- an offer conferred by a count is ended by its holder or by a count, never by its proposer alone;
- among several founding keys one founder's unseat concludes nothing, and a founder's own offers live only
  while that founder's seat does;
- a row that names another adds its audience to it only if it is concluded and its signer was already in that
  audience;
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
| An invariant of the form "at least one" | two honest keys acting concurrently | 'at least one' is kept by no rule; an emptied founder set has no recovery in the kernel |
| A fork by the count of an old head | keys that met the count at an old head, signing one version | only against a reader with no acknowledgement of its own: its roster is the keys common to the two lines (nobody), for good |
| The same, by leaked keys of removed members | whoever holds removed keys that once met a count | only against a reader with no acknowledgement of its own, as test 18 |
| A new reader's first view | whoever controls a new reader's first view | until the reader withdraws its own rows; its own acknowledgement makes the wrong head stick |
| A row withheld from some | the cut's own signer, or a relay, by omission | as long as the row is withheld; any holder may serve it |
| Rows signed to no purpose | any key at all, one signature a row | no answer moves; storage and read time grow without a bound in the kernel |
| A row carried on by naming it | a key already in the row's audience (a member, or a former member for rows of its time) | intended carriage: to a later joiner or to another group, with the named row's ancestry; cannot be undone |
| History carried by a reply | any one member, by replying | intended carriage, row by row; cannot be undone |
| One conferring seat seating many | one seated key whose seat may confer | one row seats any number of keys; ends with one withdrawal by its conferrer |
| A line of several rows forged by a past count | keys that met the count at an old head, signing any number of rows | (a) a reader that acknowledged the honest head: nothing, the forged line is void whole (HOLDS for it). (b) a reader with none: plain tips-wait; no row is stale, the members are the keys common to the tips (the forger alone when it is on both lines), for good; a removed key is never listed |

Four of the sixteen are forms of one attack, a fork signed by keys that once met a count.

Two costs of the reader's line are stated here because no attack names them. An honest admission signed
offline on an old head is behind the line of a reader that has acknowledged a newer head, so for that reader
it is void, and so is a version built on it; it must be signed again on the newer head, or that reader and the
others differ for good. And whoever may end a moderator's seat can, by ending it, stop that moderator's answers
that the ending row has not seen from counting.

## 9. What stands between this and a build

| Item | Kind | Where |
|---|---|---|
| Which rows seat which key in which role: `confers`, `binds_segment`, the 23 roles as one walk | table data | `manifests/family_model.json` |
| Twelve guards that refuse a row for another row become folds | table data | `manifests/transitions.json` |
| A count taken when the fold is evaluated has no solution. It has left the policy table; fourteen fold cells of other families still read `@decision` or `@count` | table data | `formal/derivation/fold_text.tsv` |
| A roster version naming several heads: an optional list beside the head it names now | wire | agreed with the store |
| One acknowledgement of a head covering everything beneath it, in place of one for each row | wire | agreed with the store |
| Placement and the copy rule as the `missing` answer | table data, with transport | `manifests/family_model.json` |
| A landing row for each window, and who may sign it | table data | `manifests/reactions.json` |
| Constants out of config | table data | `constitution/constants.tsv` |
| An acceptance row for each seat the text confers without one | rule | the Parts |
| The cut's terms for each slot transcribed into the proof | proof | `formal/causal_order` |
| A rule that keeps at least one founder, or a stated way back when none is left | rule | the Parts |
| The signer gate written over the library | code | `tools/check_signer_gate.py` |
