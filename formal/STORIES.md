# The things in a mesh, each with its own story

[`mesh_life/LIFECYCLE.md`](mesh_life/LIFECYCLE.md) tells the life of the mesh in ten steps. This file tells the life of each thing that appears along the way, in the same voice. Every story says what the thing is, how it is born, the states it can be in (**bold**, the names of [`STATE_TABLE.tsv`](STATE_TABLE.tsv)), what moves it from one state to the next, how it ends, and which model proves it. A story with no model yet says so.

Read it top down. Nothing in a later story is born before the step that introduces it.

---

## Step 1 — three people sit down

### The mesh
A mesh is what three people make when they perform the genesis ceremony. It is **unminted** until they do, **live** from the moment the bundle exists, and **ended** when, after the holders decide to wind down, nothing is left alive in it. Nothing is born before the mint and nothing is born after the decision to wind down. *Proved by `mesh_life`.*

### The bundle
The bundle is the one thing the ceremony produces: the charter, the three holders' key records, the first canonical's key and signed route, the consensus rule, and the holders' authorizations over all of it. It is pinned by its fingerprint, which is published with the release and baked into every conformant build. Names inside it are names, not anchors; the fingerprint is the anchor. A bundle is re-minted by a fresh ceremony (every holder signs) or amended by a majority with the members carried byte for byte and a higher version; two verifying bundles at the same version with different fingerprints are equivocation and fail closed. *Proved by `trust_root` (the standing a node reaches from it) and `accord_roster` (the majority arithmetic).*

### A holder
A holder is a person seated in the bundle, holding their own key on their own hardware. A holder is **honest**, or has been **censored**, **lost** or **coerced**; the design never knows which, so it is built so that any one of those cannot move the root alone. A lost holder is replaced by a majority of the others re-minting. *Proved by `accord_roster` (a strict majority is needed to seize, for any roster size) and `accord_halt`.*

### The root, as a node sees it
Every node forms its own verdict about the root: **NotRooted**, **Stalled** or **Rooted**. It roots when it holds the bundle under its anchor, the lineage head is **witnessed_fresh**, and the attach window has not passed; it stalls when the head goes **stale**; a **frozen** head never un-roots it, because a root is valid until revoked, never until a timer lapses. A node-bearing seat never moves a verdict by its own signature. *Proved by `trust_root`.*

### The halt
The halt is the holders' one power that points outward. It is **not_halted** until one seated holder latches it; a lone latch is **latched_lone** and lapses at the fuse; a majority confirms it and it is **confirmed** until a majority resumes. Every agent that accepted a root is inside its reach; a halt keeps state and destroys nothing. It is the condition of symmetry between maker and made, not an asymmetry. *Proved by `accord_halt` (the fuse and the majority) and `guarantees` (whom it reaches, and that leaving a root ends the reach).*

### The canonical, and any serve seat
A serve seat is a node the bundle or a later grant seats to serve. It is **not_serving** until its owner is announced, because a named human must answer for it; then **serving**; it stops when the binding is withdrawn or the seat lapses. A canonical is one source of route rows and never a required party: two people with no canonical anywhere still reach each other. *Proved by `mesh_life` (a canonical serves only once announced).*

### A relay, for the anonymous tier
Every node that runs the substrate relays onion traffic for others unless it opts out. It is **not_capable** until it carries a hop key, then **relaying**; a non-seat may be **opted_out**; a seat or a node holding the steward's relay role is **conferred**. Each period the relays are dealt into three layers, conferred first, with a cap on the unconferred in each layer and a floor of three; a layer below the floor makes the tier unavailable for that period. *Proved by `onion_layers`.*

---

## Step 2 — the canonical gets an owner

### The owner binding
An owner binding is a person's signed statement that a node is theirs. Carried at federation scope it is an announcement: the node is on the person's public roster and strangers can reach it. Carried below federation it is private: the node exists for the person and their cohorts only. A seat must have an announced owner to serve. *Text (CC 3.2, 5.4.6); carried by `mesh_life` as the announce step.*

---

## Step 3 — a person arrives

### A person
A person is a federation key and the devices bound to it. They are **absent** until they make a key, then keyed; **announced** once an owner binding of theirs is at federation scope; **gone** only when every device is released, they are in no room, steward no agent and hold no contact. A person's rows outlive them where the record must stand. *Carried by `mesh_life`.*

### A key in a person's roster
A person's keys form their self roster, one key per device. A key is held by its **owner**, or by a **thief**, or is **lost**. A new key is **proposed_add** by the roster and becomes a **member**; an eviction is **proposed_evict** and the key is **evicted** under the roster's quorum; a thief cannot evict the others and a lost key is recoverable. Revocation is **revoked_after** an instant or **revoked_all**; a key's post-quantum half is **pending** until the second half is registered, then **complete**; succession is **committed** then **rotated**; a key may be **escrowed**. *Proved by `self_roster` at three and four keys; the post-quantum half, rotation and escrow by `mesh_life` (identity family).*

### A device
A device boots **unclaimed** with a node key of its own and becomes **claimed** by its owner's pen with the bundle's anchor and a claim PIN; its occurrence is **pending** until the owner approves it, then **owned**. A second device joins by a device-join request on the first-contact plane: **requested**, **approved** by the owner on a device they already own (two rows in one approval, a matching code the owner's own device derives), **joined**. A device is **announced** or **unannounced** by its owner's choice, one node at a time. It is released when lost, evicted or retired. *Proved by `self_roster` (the roster) and CIRISServer `formal/add_device` (the join); carried by `mesh_life`.*

---

## Step 4 — two people become contacts

### A contact
A contact begins when one announced person asks another. The request crosses a forwarder sealed, carrying the asker's own grant and route; the other accepts with their own grant and route, and the two go direct. The replication consent between their nodes is **none** until then and **granted** after. The forwarder serves key records and unowned routes openly, never an owned route, holds no grant, and keeps about the pair only that a link crossed it or a sealed envelope waited in its mailbox. The asked person may **ignore** the request instead: a private, local, undoable act the asker is never told of, which looks to the asker exactly like a request still pending, because a visible refusal would tell everyone that one person refused another. Either party may **block** the other, privately: further requests from the blocked key are dropped without answer, the forwarder learns nothing, and the blocker lifts it. Either side ends a contact. *Proved by `contact` (the forwarder) and `mesh_life` (the contact plane: an ignored request is indistinguishable from a pending one to the asker; a block is one party's own act).*

### A rendezvous route
An anonymous peer has no announcement. Each hour it publishes a rendezvous route under a fresh key: the route to its mailbox at a serve seat, sealed per hop. The row supersedes the previous hour's and is purgeable after its validity; it is never a durable record. Anyone may send to it; nobody learns the peer's address; a contact with an anonymous peer never goes direct. *Text (CC 5.4.6 item 6 and 9); the layer deal is `onion_layers`. No table row yet.*

---

## Step 5 — a room is founded

### A room
A room, a family or community or affiliation, is **formed** when its founding record seats its first member. It names a **moderator**; a moderator may **lapse**, be **merit_promoted**, or be replaced through a **recovery_48h** window and a **candidacy_24h**, and when none of that produces one the room is **fail_secure**. A change to its quorum is **held** until the protocol applies it. It is **federating** or not by its own declaration. A room whose last member leaves is dissolved and what it held is purged. *Proved by `membership` (the ceremony), `mesh_net` (who may hold its content, that a private room is invisible), `affiliation` (the two regimes of an affiliation).*

### A member
A person is **proposed** by a member, is **accepted_awaiting_group** once they say yes, and is a **member** when the group's protocol admits them; or they are **declined**, which is terminal for that proposal. A member is **removed** by the others under the protocol, never by one hand alone, or **resigned** by their own. A departed member is re-seated only by a new proposal. *Proved by `membership`.*

### An affiliation
An affiliation is a room that acts as one voice: a business, a court, a school. Its charter is **declared** at creation and **superseded** by its officers under its protocol. As a body it never retracts a statement about itself; its path is reconsideration and the reader's composition. Its charter names its succession or its dissolution instant, and when its last deciding seat lapses with neither, it is dissolved. *Proved by `affiliation`; the charter's declaration and supersession by `mesh_life` (room governance family).*

### A standing, over a row that names a person
A row at a bounded scope may name only keys within its audience: members by the roster fold at the row's instant, or the key the family delivers it to. The person named always sees that the row exists. They retract peer speech about themselves; they only contest a duty-holder's record, an authority's act or a cosigned act; an affiliation retracts nothing. A warning said as speech is retractable, a warning filed with the named moderator is not. *Proved by `standing`.*

### A mute
A member may mute another member: a private filter in their own reader. It changes nothing in the room, not a row, not the roster, not the other's standing; the muted member is not told. The one thing a mute never hides is a row that names the muter, because a statement about a person is always visible to that person. The muter lifts it. *Proved by `mesh_life` (contact plane: a mute changes no row and no roster).*

### An objection, and a moderation outcome
A vote on a pending act is a **proposal** (the proposer's own row, which counts as its approval), an **assent**, or an objection **raised**. A moderation case ends as **hard_removal**, **consent_gated** or **kept_visible**: by a moderator's or steward's signature within two days, else by a live majority. *Proved by `membership` (the cosigned acts) and `mesh_life` (content family): a flag is decided by the moderator, and a hard removal withdraws the row as a duty-holder's record.*

---

## Step 6 — members write

### A row
A row is one signed statement. It is written at the **local** tier, signature deferred, and promoted to the **federation** tier under a hybrid signature. Once admitted it is **admitted** until its producer **supersedes** it, **recants** it, the right hand **withdraws** it under the five rules, or a cosigned takedown **tombstones** it by digest. It carries a scope from **self** to **federation** and never a wider one than its cohort. A withdrawn row never comes back; an adverse record about a person is never withdrawn by that person. *Proved by `withdraws_admission`; carried by `mesh_life`.*

### A blob
A blob is the bytes a row carries or names. It is **inline** at or below the cap and **chunked** above it. It is **held** by every node in its audience that acknowledged custody, **custody_received** once the author has the receipt, **withdrawn** when no device serves it, and **purged** by a bytes-plane tombstone that every byte door honours. An owner may **mark** it durable with a target holder count; it is **at_target** when enough hold it, **below_floor** when repair runs, and **descending** when the owner un-marks or withdraws it. *Proved by `mesh_net` (who may hold it) and `mesh_life` (content family: the form, the durable mark, its descent).*

### A ledger
An owner's ledger is a chain of their own rows in their own order. It advances by **head**, is sealed by **checkpoint**, is **promoted** when its net settles on a rail, and a **fork** is evidence against the owner, slashed rather than prevented. *Proved by `mesh_life` (room governance family): head, checkpoint, close, fork.*

### An event
An organiser's event is **open**, then **completed** or **cancelled**, or **superseded** by a later record. *Proved by `mesh_life` (room governance family).*

---

## Step 7 — a person consents, and revokes

### A consent
A subject's consent over a scope is **granted** by the subject, **revoked** by the subject at any time, or **expired** by the clock. A revocation is a boundary, not an erasure: what was captured before it stands, nothing is captured after it, and capture resumes only on a fresh grant. Backdating is bounded by the window. An agent's memory of a person decays in steps: **identity_severed**, **patterns_anonymized**, **complete**. The node owner's grant over trace capture is **granted** or **bounded** by a revocation. *Proved by `consent`.*

---

## Step 8 — an agent is bonded

### An agent
An agent is a made thing with a key that cannot accept for itself. It is **unbound** until an announced person bonds it, **bonded** while the steward's bond is live and reviewed, **lapsed** when the bond is not renewed, and then it stops. While bonded it is **acting** unless a latched halt makes it **refusing**, which is one terminal result, never a crash. The halt reaches it because it accepted a root; it can leave the root in one step and no later halt reaches it. Its identity is **baseline** until an **amended** record cites an approved deferral. *Proved by `guarantees` (every promise reaches it alike; the halt as the condition of symmetry) and `reciprocity` (why it is bound at all).*

### A deferral, and the Wise Authority
When an agent cannot decide it defers: the deferral is **pending** and the agent is inactive on the issue until a seated Wise Authority answers **approved** or **rejected**. A Wise Authority is **absent** or **present**; a quorum of them may find a seat an **abandonment**, a **seizure**, or name a **successor**. *Proved by `mesh_life` (agent governance family): the seat, its abandonment or seizure and the successor, the deferral answered only by a seated authority, the amendment after an approval.*

### Retirement
Retiring an agent runs one way through seven rows: **decided**, **frozen**, **secrets_destroyed**, **handed_over**, **notified**, **custodian_minted**, **retired**. It can be cancelled only before frozen; the seal is opened by one row; custody passes only to the named custodian; a walk-away keeps the record; a refusal stands. *Proved by `retirement`.*

### A goal
A community's goal tree is **staged** by the canonical as stamped, unsigned rows, **proposed** when a founder scrubs it, and **declared** when the founder quorum cosigns it under the community's protocol. Its declarer may **supersede**, **withdraw** or **recant** it. An approach, a method at a substrate rung, and a progress measure are each **declared** under it. *Proved by `mesh_life` (goal family): staged, proposed, declared, withdrawn; approach, method and measure in that order.*

### Evidence
Evidence of work is **offered** by a node holding the attest duty, naming a declared goal, approach or method; it is **admitted** when the blob's digest matches the row; it is **counted** when a declared progress measure cites it; it is **reference_unresolved** while no holder serves the blob; and a re-post **supersedes** it. A reader holds it **blessed** when the emitter sits on a live attest delegation from a root the reader trusts, else **unblessed**. *Proved by `mesh_life` (goal family): evidence names a declared goal, is counted only by a measure, and is blessed exactly when the attest duty was live.*

---

## Step 9 — the holders decide, and so does everyone else

### A decision
Every governance change takes one shape: enact at once above one threshold, or cancel within a window above a lower one; an approval floor before silence may land anything; no instant change. *Proved by `two_path`.*

### A delegation
A principal's delegation to another is **live** from admission, **withdrawn** by the principal with a cascade down the chain, **expired** at its term, or **refused** at the door when the delegator lacks the authority. It attenuates, is capped, and expires; it carries a scope of **license** or **grant**, and a licence and a grant never chain. *Proved by `authority_tree`.*

### A licence
An authority's licence over a subject is **held** from the licensure row, **suspended** by a bounded revocation, **revoked** by a full one, and **contested** by the subject's reconsideration. A reader **honours** it only where the reader's own trust walk reaches the issuer for that class; otherwise it is **not_trusted**. A licence confers no trust by itself. *Proved by `authority_tree` and `trust_set`.*

### A key grant
A wrapped key is **held** by its recipient, one row per recipient, **rotated** by a superseding row in the rotation chain, **expired** with its term or epoch, and **onward_refused** when the issuer holds the key but neither the asset nor a grant-scoped delegation. *Text (CC 3.3.2); the door is `mesh_net`'s audience rule.*

### A guardian, and an age
A guardian's bond over a child is **none** or **bound**; an age is **none** or **assured** by a declaration or an assurance row. A minor's node carries no federation binding. *Proved by `mesh_life` (identity family): a guardian is an announced adult, a minor is never announced and sits in a room only while bound.*

### A capacity finding
A person's capacity under a declared domain is **capacitated**, **incapacitated**, **reversible_pending**, **reversible_excluded** or **lapsed**, always from a row under the trusted tier, never from a score. *Proved by `mesh_life` (identity family): while the finding stands the person stewards no agent, holds no seat and no ward.*

### A quarantine
A slash-duty holder's quarantine of a row is **withhold** or **release**; at a tie, withhold wins. *Proved by `mesh_life` (content family).*

### The census, and a secret poll
Each period every owner's one-hot report is split into two shares; a return is **pending** until both aggregators accept the same token, **accepted** when the proof passes and it is counted once, **refused** otherwise. A composite is **withheld** below the floor of k owners and **published** when the two partials add with enough sources and no one over half the mass. The base **ratchets** with the expected-active count, is **floored** when the floor binds, and **freezes** when a fall looks like a partition. A poll is **closed**, **open** inside the padded cells where no outsider can see it, and **decided** against the base of its period. *Proved by `census_ballot`.*

---

## Step 10 — the mesh winds down

When a majority of the holders decides, nothing new is born. Every story above runs to its own end: members resign and rooms dissolve, rows are withdrawn and purged, devices are released, agents are frozen and retired, consents are revoked, the canonical retires, people are gone. When nothing is left, the mesh has ended, and the record of what it was stands where the rules say it must. *Proved by `mesh_life`: once the holders decide, the mesh always ends.*

---

## What a social network needs, and where each is

The things people do on a social network, each mapped to the story and the rule that carries it. Where something is a reader's own choice and not a row, it says so.

| what people do | what it is here | where |
|---|---|---|
| find someone | an announced person's federation id; the public roster is exactly the devices they chose to announce | step 3; CC 5.4.6 |
| add a contact, be added, accept, ignore, block | the contact: request, acceptance, private ignore, private block | step 4; CC 5.4.6; `contact`, `mesh_life` |
| message someone | a pair room between contacts, sealed end to end, direct after consent | step 4, step 5; CC 5.4.6 |
| join a group, be invited, leave, be removed | the membership ceremony: proposal, acceptance, decline, resignation, removal by the others | step 5; CC 3.1.3.2; `membership` |
| follow a public page or channel | a public community: founded by anyone, open admission, discoverable by its listing row, plaintext at the Commons tier | step 5; CC 3.1.3.2 (public rooms) |
| post, reply, react, thread | rows in a room; a reply is a row that names the row it answers; a reaction is a score on a row | step 6; CC 3.1.9, 2.1 |
| share media, go live | blobs inline or chunked; streams and calls under the A/V seal | step 6; CC 2.6.1.3, 5.3.3 |
| repost to a wider audience | not possible by reference: a row cannot be carried beyond its cohort; the author posts again at the wider scope | CC 5.2 (scope follows the cohort) |
| edit, delete | supersede, withdraw, purge; a withdrawn row never comes back | step 6; CC 2.4.1.1 |
| post something that disappears | a row with an expiry, purged after it | step 6; CC 3.3.5 |
| mute someone | the reader's private filter; never hides a row about you from you | step 5; CC 4.4 |
| report someone, appeal | a flag to the named moderator; the outcome; reconsideration by the person named | steps 5, 6; CC 4.5.4, 4.5.5; `standing`, `mesh_life` |
| warn others about someone | said as speech, retractable by the person named; filed with the moderator, a duty-holder's record | CC 4.5.5; `standing` |
| rate a business, review a place | a score about an affiliation, which never retracts it and contests by reconsideration | CC 4.4.3.2.8; `affiliation` |
| see who said what about you | the read over every row that names you | CC 3.4.5 |
| choose what your feed shows | the reader's own composition and filters, stackable and swappable, never a ranking of persons by what they are | CC 4.4; `trust_set` |
| verify who someone is | the key fingerprint in the id, the contact code across a table, the licence a reader honours only through its own trust | CC 2.6.8; `trust_set` |
| protect a child | a minor never announces; a guardian's bond; age assurance | step 3; CC 3.4.13 |
| control what is captured about you | consent granted and revoked as rows the subject signs; a revocation is a boundary | step 7; CC 3.3.1; `consent` |
| export or delete your account | the read over your own rows; every device released, every room left, every row withdrawn, the person gone | step 3, step 10; CC 3.4.5 |
| be found by strangers, or not | announce a device, or do not; an anonymous peer at a rendezvous route | step 3; CC 5.4.6 |
| events, groups that end | an event opened and closed; a room that dissolves when its last member leaves | steps 5; CC 3.3.8 |
| pay, tip, settle | the owner's ledger and settlement on rails, never a balance as substrate state | step 6; CC 3.3.10 |
| ads, engagement ranking | none: there is no operator with a feed to sell; the reader composes | CC 4.4 |

Two of these are not yet rows the table knows: the reaction as a named row kind (today a score on a row) and the pair room as its own object (today a family of two). They go on the list below.

## Are we exhaustive?

Every variable of the state table is carried by a model, the spine or a chapter: 77 of 77, gated by `tools/check_lifecycle_coverage.py`. What the table itself does not yet name, and so no coverage number sees: the bundle's amendment, the rendezvous route, the first-contact request as its own object, the stream and its chunks, the key grant's rotation chain, the reaction as a row kind, the pair room as its own object. Those are the next rows to add to the table, each with its sentence in a story and its action in a model.
