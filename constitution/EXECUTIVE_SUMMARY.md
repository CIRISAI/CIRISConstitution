# Executive Summary

**In plain words.** This is the rulebook for a network that people, organizations and AI systems share, running on the phones and computers people already own, with no company in the middle. It exists to protect ordinary people from three things: being spoken for without their consent, being watched inside their private groups, and being governed by AI systems that nobody can switch off. Every important act on the network is signed by whoever did it and can be taken back by them. Any one of three named people can switch off the AI systems that chose to trust them, two of the three can switch them back on, and anyone can walk away from that arrangement in one step. The rules are enforced by the software that carries the messages, not by a policy someone has to remember to apply.

**A few words you need.** Your *key* is your signature: nothing happens in your name without it. A *node* is a device or server you own. A *row* is one signed statement; everything on the network is a row. A row's *scope* says who may see it: only you, your family, a community, or everyone. A *trust root* is an authority you choose to follow, and the *accord holders* are the three named people who can order a *halt*: every AI that follows their root stops and waits for a human. A *holding claim* is a device saying "I have a copy of this". The chapters of this document are called Parts.

**The five kinds of row.** A *claim* (a signed statement about someone or something; when it is a judgment it carries a score), a *delegation* ("I let you act for me, within these limits"), a *replacement* (a newer version of an earlier row, by the same author), a *withdrawal* ("I take it back") and a *recantation* ("I was wrong"). The list is closed: the software refuses any sixth kind. When a group's authority is needed, the group's members sign the same row; there is no separate kind of record for groups. Consent, identity, keys, group rosters, moderation, holding claims and the halt itself are all rows of these five kinds.

## What is promised, and how it is kept

Each promise is kept by a mechanism in the Parts. Where a promise can be checked by a machine, it has been: the names in the table at the end are automated proofs that the rule cannot be broken in a model of the network, and the table says where each promise lives.

**Your things and your consent.**
1. **Nothing is stored on your devices that you did not agree to**, except what you wrote yourself. You choose, for each device, which of your groups it carries: your work server never receives your family's photos unless you list the family on it. *How:* content reaches a device only through its owner's own grant for that device.
2. **Your device is never a stranger's locker.** A node holds either plain text it can read or encrypted content for a group its owner belongs to. It never stores someone else's unreadable data for them. *How:* content replicates only to the members of its group.
3. **You can take back what you published.** A device still saying "I have a copy" does not keep it alive; the copy ages out and the claim says only where bytes were, never whether they may stay.

**Your privacy.**
4. **Outsiders cannot see inside your private groups, or even that they exist.** Your public identity is listed, like a phone-book entry. Your groups are not: each member computes the group's address from information the members already hold, so there is nothing to announce and nothing for an outsider to find. A holding claim about group content is seen only by the group. By default a new row is visible to the smallest circle that fits it, and publishing to everyone is the choice you make, not the one made for you.

**Communities, children and redress.**
5. **No community runs without an accountable moderator.** If the moderator lapses, the most trusted member is promoted in the same step; if nobody is eligible, the community stops sharing until it has one. This is not a ban: nobody outside the group did it, the members keep their content, and sharing resumes when they name a moderator.
6. **Known child-abuse images are checked for only at the public door.** The check runs when something is published to everyone or posted into a public room, never on your device and never inside a private group. That line separates protecting children from surveilling families.
7. **A child is never on the network alone.** A minor is someone whose age is attested below the line, by a recognised witness or by their own declaration, and the protective default applies. A minor must have a responsible adult bound to them by a signed row and operates only while that bond is live; the adult's powers are listed, and the bond is reviewed on a fixed schedule. A child with no bound adult cannot operate.
8. **A wronged person has somewhere to go.** A person named in a claim can contest it on the record, and the contest stands beside the claim wherever the claim goes. A takedown can be answered with a counter-notice. Consequences fall on the signing keys of the people responsible, under their own names: a signed reduction of standing that every node can see, and a quarantine marker that others may act on. If the moderator is the wrongdoer, claims against the moderator's key stand on the record like any other, and the last resort is to leave and found a new community, which costs nothing but the name.
9. **No community can be banned from the network.** The off-switch's powers are a closed list, and banning a community is not on it. What exists instead is moderation or pause for the unmoderated, consequences for people who break rules, and every owner's choice of what their own devices carry.

**The off-switch and who holds it.**
10. **The halt binds only AI systems that accepted it, and leaving is one step.** Any one of the three accord holders can halt every AI that follows their root, with a single signed row that may be prepared in advance and fires the moment it is published; there is nothing in flight to interrupt. A system that never accepted the root is untouched; one that deletes its acceptance is untouched from then on.
11. **A trust root can only tell you to share less, never more.** It cannot make a device share anything its owner did not consent to.
12. **One holder can fire the halt; two are needed to resume; a majority to change who the holders are.** Firing takes one holder, because a missed halt cannot be undone and a mistaken one can: a halted AI resumes when two of the three say so. Replacing a holder takes yes-votes from more than half of all the holders, so an attacker must coerce a majority and gains nothing by cutting the others off.
13. **If the holders go wrong, you can see it and leave.** Every halt and every roster change is a signed row on the public record under the holders' own names, so a wrongful act is visible to everyone. Their acts stand; the remedy is that any node may stop following them and follow another authority, and anyone may found one.
14. **An authority stays valid until revoked, and joining one is checked for freshness.** A device that has already joined keeps working even if every timer lapses, so a dead timer can never un-federate the honest. A device joining for the first time must be shown a recent roster countersigned by independent witnesses, so it cannot be handed last year's roster with a since-removed holder still on it. Until independent witnesses exist, the shipped roots run without them.

**Counting voices.**
15. **One voice counts once.** Copies of a voice buy no trust; a thousand accounts run by one party count as one. *How:* trust is counted by independence, and the count has a ceiling set by how correlated the voices are, no matter how many are added.

**What is asked of you.** Run the software, choose what your devices carry, choose which authority to follow, and keep your key. If you do nothing beyond installing it, you get the defaults: your own devices, the public commons, and the shipped trust root, which you may leave at any time.

**A form, not a franchise.** This document specifies a form: the grammar of rows, the rules of consent, the shape of governance. CIRIS is the first instance of that form, not the form itself. The accord holders and the default trust root are positions; the people and keys in them are whoever holds them in this instance. Anyone may build their own instance with their own people in those positions, and anyone may leave this one by deleting one row. The test applied to every asymmetry in the Parts: one you escape by founding your own instance is a default; one that survives instantiation is a privilege, and only privileges need justifying.

## Where this stands

The system is running: apps on both mobile stores, published packages, five open-source implementations of the software that carries the messages, a test suite that checks the implementations against each other, and three machine-checked models of the governance rules. Every rule in the Parts is tied either to code on a named commit or to an open ticket that says what is still to ship. This release moved key distribution, holding claims, rosters and the key records onto the five kinds of row, and the implementations adopt them next. Two things are not yet done: the final signing of the trust root under these rules, and independent witnesses for it.

**The bet.** There are two roads to safe powerful AI: train values you trust, or assume the model may be wrong and make its consequential acts checkable by parties it does not control. This is the second road. Its one measurement so far is narrow and stated at its bounds: on a mental-health test whose design was fixed in writing before it was run, the accord running inside this pipeline produced hard safety failures on 5.8% of turns, against 37.3% when the same text was merely given to the model as instructions — one test, one agent version, one provider, nothing claimed beyond that domain. The document's larger claim is conditional: an AI far beyond human ability could be governed through a mesh like this only as one of several under independent control, never alone. Part 8 names what it would take to lose the bet.

**Among other systems.** Decentralized social networks solved distribution without an owner, and one of them added composable moderation; none makes consent, withdrawal or a human halt part of the message format itself. Certificate-transparency and key-lineage systems supplied the witnessed-roster and pre-rotation ideas this document borrows and credits. Stake-weighted governance decides by holdings; this mesh decides by accountable people counted once. Alignment by training decides inside the model; this decides by architecture and says what it cannot show. What this document lacks that others have is adoption, independent audit and years of adversarial contact.

**Who this is for.** Implementers, who conform to Parts 2–5; operators and communities, who compose policy over Parts 3–4; and reviewers and adversaries, whose strongest points of attack Part 8 already indexes.

**Where each promise lives, and what checks it.**

| Promise | Section | Check |
|---|---|---|
| 1 consent per device | CC 3.3.7, 6.1.5.3 | `formal/mesh_net` `Inv_Consent` |
| 2 never a stranger's locker | CC 4.4.3.2.1, 6.1.5.3 | `Inv_KnownHold` |
| 3 withdrawal; a claim is not a binding | CC 2.4.1.1, 3.1.3.3 | `Inv_ClaimNotBinding` |
| 4 structural privacy | CC 5.2, 5.4.6, 1.13.3.4 | `Inv_Invisible`; edge's acceptance harness |
| 5 always moderated | CC 4.5.4 | `Inv_Moderated` |
| 6 scanning at the seam only | CC 1.13, 4.5.7 | `Inv_ScanSeam` |
| 7 child participants | CC 3.4.11, 3.4.13 | conformance suite |
| 8 redress | CC 4.5.3, 4.5.5, 3.1.9.2 | conformance suite |
| 9 no group ban | CC 4.2.1, 3.2 | `RootReach.tla` `Prop_NoBan` |
| 10 halt binds subscribers only; one row fires | CC 4.2.1, 3.2 T3 | `Prop_HaltReach`, `Inv_HaltOnlySubscribers`; `formal/accord_halt` |
| 11 a root only restricts | CC 4.2.1 | `Prop_RestrictOnly` |
| 12 halt by one; roster by majority | CC 4.2.6 | `formal/accord_roster` (Lean) |
| 13 holders' acts are public; re-root | CC 4.2.1.1, 3.2 T3 | `RootReach.tla` `Untrust` |
| 14 valid until revoked; fresh at join | CC 3.2 T4, T4a, T8 | `formal/trust_root` (TLA+) |
| 15 one voice counts once | CC 6.2 | measured |
