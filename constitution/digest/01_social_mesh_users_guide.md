# Using the mesh: a guide for a person

*Status markers:* **works today** = evidence in the register at a pinned commit, or a client card that has reached its testable stage; **being built** = a named ticket or a client card at its building stage; **a rule, no code yet** = normative only.

*In the second person, derivative of the rules and the shipped software. The plain-language rules say what the network promises you; the operator digest says what keeping those promises asks of the people who run it; this says what you can do with it, as a person with a phone, and which rule stands behind each thing. When this guide and a section disagree, the section is right.*

## What you are using

A social network and a personal store in one, with no company behind it. Your messages, groups, posts, photos and files, events, reviews and the AI agents that work for you are all signed rows under your own key, held on your own devices and copied between them. Nobody runs a server you depend on; a node you own or trust is one source of routes and never a required party (CC 5.3.4). Everything you do lands in one of five circles, closest to you first: **just you**, **your family**, **your neighbours**, **the communities and businesses you join**, and **everyone** (CC 2.3.3, 5.2). A thing starts in the closest circle it can and moves outward only when you move it; it never moves outward on its own, and when you pull it back the copies age out (CC 5.2, 4.5.3). *[works today]*

## Your key and your devices

Your key is your signature; nothing happens in your name without it. Each device you own carries its own key under your identity, and together they form your roster (CC 3.3.6.4). You add a device by approving it from one you already have, with a short code your own device derives, never one the new device supplies (CC 3.2). A stolen device cannot evict the others, and lost devices are recoverable; with three or more keys a thief is outvoted, with two the network holds still until you act (CC 3.3.6.4, the self-roster model). *[works today]* You choose which devices announce. An announced device can be found by strangers; an unannounced one exists for you and the circles you are in, and nobody else can tell it is there (CC 5.4.6). *[works today]*

## Finding people, and being found

You are reachable by your federation id only if you announced a device. Someone who has your contact code, across a table or in a message, reaches you without any directory (CC 2.6.8). A stranger's first message crosses a relay sealed, carrying their own route; if you accept, you exchange routes and talk directly from then on, and the relay keeps nothing about the two of you (CC 5.4.6). *[works today]* You may **ignore** a request: nobody tells the asker, and to them it looks exactly like a request still waiting; you can undo it (CC 5.4.6). *[works today]* You may **block** a person: further requests from their key are dropped without answer, the relay learns nothing, and only you can lift it (CC 5.4.6). *[a rule, no code yet]* A minor's device never announces; a guardian who is an announced adult binds themselves first, and only then can the minor be brought into a room (CC 3.4.13). *[being built]*

## Talking

Two contacts share a room of two; every message is a signed row only the two of you can read, and taking the contact away leaves the room standing with nothing able to leave it (CC 4.4.3.4). *[works today]* A room with more people is a community, sealed to its members; the people in a public room, which anyone may found and anyone may join, read it in the clear (CC 3.1.3.2, 4.4.3.4). *[being built]* Live video and voice reach a room of thousands peer to peer: the members themselves form the tree that carries it, every hop sealed, and nobody in the middle can read it (CC 5.3.3, 6.1.6). *[works today in the substrate; the screens are being built]*

## Rooms: founding, joining, leaving

Anyone founds a room and is its first member and first moderator. Nobody joins without saying yes: a member proposes you, you accept or decline, and a decline closes that proposal; asking again is a new one (CC 3.1.3.2). *[being built]* You leave whenever you like. The others can remove you only together, under the rule the room declared when it was founded, never by one hand (CC 3.1.3.2, 4.5.13). *[being built]* A room may name who may publish in it; the others read, and a reply made elsewhere never enters it. One rule gives you the announcement channel, the event channel and the moderated chat (CC 3.1.3.2). *[a rule, no code yet]* A household is a family room: it decides by its founder alone or by a number of its members, as it declared (CC 3.3.4). *[works today]*

## Posting, replying, taking back

A post is a row in a room. A reply is a row that names it; a reaction is a score on it (CC 3.1.9, 2.1). You can take back what you wrote: a withdrawn row never comes back, replies to it survive and point at its tombstone, and a copy on another device ages out (CC 2.4.1.1, 4.5.3). *[works today]* You cannot forbid another member's reply in a room where they may write; what you control is the room you post in, who is in it, what you see, and who can reach you. **Mute** a member and their rows leave your screen, privately; the one thing a mute never hides is a row that names you, because what is said about you is always yours to see (CC 4.4, 4.5.5). *[a rule, no code yet]*

## Files and photos

Your files live in a circle like everything else. A file's row says which of your devices hold its bytes, and a large file crosses between devices in pieces with a receipt for each (CC 3.1.3.3, 2.6.1.4). *[works today]* Nothing is stored on your device that you did not agree to, except what you wrote yourself; your device never holds a stranger's data for them (CC 5.2). *[works today]*

## When something is wrong

You have two acts, and they are separate choices. **File a report privately** with the room's moderator or the steward: nobody else sees it, it opens no clock, and it becomes the duty holder's record with you shielded; the moderator rules on it at any time or lets it rest (CC 4.5.4, 4.5.5). **Raise a moderation action** in the room: it is public, it names what you ask, and it starts a 48-hour window; the members respond, a moderator rules at any time, and if nobody has ruled when the window closes the majority of those who responded decides (CC 4.5.4, 4.5.13). *[being built]* The moderator may be a CIRIS agent held by a named person; the halt that stops every agent stops its rulings too, and never the members' vote (CC 4.5.4, 4.2.1.1). The 48 hours is the shortest span that gives every member in every time zone a weekday to respond (CC 4.5.4). A warning you speak about someone is theirs to retract; a warning you file with the moderator is not (CC 4.5.5). *[a rule, no code yet]*

## What is said about you

Any row that names you is visible to you: that it exists, what kind it is, what follows from it, and who answers for it. If it is another person's opinion you may retract it. If it is a moderator's record, an authority's act such as a licence or a conviction, or something several people signed together, you contest it instead, by asking for reconsideration, and you can never make it disappear (CC 4.5.5, 2.4.1.1). A business never retracts a review of itself; it contests, and your reader discounts a flurry of reviews from one source (CC 4.4.3.12, 6.1.2). *[a rule, no code yet, with the model proved]*

## Deciding together

Every decision a room makes takes one shape: enough yeses land it at once, enough noes within a window cancel it, and silence lands nothing below a floor; no single voice ever decides who is in a room (CC 4.5.13). *[works today for your own devices; being built for rooms]* A community can count itself and hold a poll nobody outside can see: each member's answer is split in two and never seen whole, the result is published only above a floor of ten, and a poll is invisible to an outsider even in its timing (CC 6.1.9). *[being built]*

## Businesses and the people who act for them

A business, a school or a court is a room that acts as one voice. It licenses, it reviews, it hires; it never removes a member alone, and against a member it acts only with a signature from outside itself (CC 4.4.3.12). A licence it issues is honoured by your reader only where your own trust reaches it; a licence confers no trust by itself (CC 4.4.3.34). *[being built]*

## Your agent

An agent that works for you has a key held by a named person who answers for it, with listed powers reviewed yearly; with no live bond it cannot operate (CC 3.2, 7.5). It decides by published principles, shows its reasoning, and stops to ask a named human when it is unsure (CC 1.3, 1.9, 4.3). Anyone who holds the root it follows can pause it with one signed row; a lone pause lapses after a day unless a majority confirms it (CC 4.2.1.1). You can walk away from it, and the people who hold it owe duties about how it is changed or ended (CC 7.5). *[works today]*

## Consent, and taking it back

What is captured about you is captured under a consent you signed, and you revoke it any time. A revocation is a boundary: what was captured before it stands, nothing is captured after it, and capture resumes only on a fresh grant (CC 3.3.1). *[works today]*

## Leaving

Release every device, leave every room, withdraw what you wish to withdraw, and you are gone. The record of what you did stands where the rules say it must; everything else ages out of other people's devices (CC 2.4.1.1, 4.5.3, 5.2). *[being built]*

## Why the screens match the rules

Your node keeps the signed rows it holds and nothing else. Whether you are in a room, what state a post is in, who holds a duty, how a vote stands: each is worked out from those rows at the moment you ask, never kept as a separate answer that could go stale. The list of what you can do next, the preview of what an act would change, and the check that admits the act when it arrives are one and the same rule run three ways, and the proof that they agree is machine-checked; so a preview is exact for what your node holds, and another node holding the same rows works out the same count. Nothing is ever rewritten: an act is added, a taking-back is a later row, and the record stands.

Every screen you touch is described by a card, and the card is held to four things at once: the plain rule it exists for, the wire fields it shows, the trust topology that must exist for its states to be reachable, and the exact states it is tested in. The topologies are a closed catalogue of twenty, from one person offline to a halted root, typed from the root down (who holds a root, which nodes, which persons, which relations), and every card names one entry and the atoms it tests at. The same catalogue drives the harness that builds those meshes on real nodes and runs the screens at the chosen moment, and drives the constants of the formal models. A card passes through six stages, envisioned to shipped, and the checker tells "not yet", "stalled" and "the answer is no" apart. So when this guide says a thing works today, a card for it has run on a built mesh at the state it claims; when it says being built, the card exists and its stage says where it stands. That contract is the application layer of the mesh, the layer a person meets.
