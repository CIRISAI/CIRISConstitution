# CIRIS Web4 Constitutional Mesh

## Constitutional governance of a decentralized mesh: cooperation without surrender, for people and the agents they hold

> CIRIS is building the infrastructure for a world where no one has to surrender their agency to participate in something greater than themselves.

| | |
|---|---|
| Draft | 0.5, 2026-11-19 (supersedes 0.4 of 2026-11-16, titled *CIRIS Web4: A Constitutional Mesh for the Networked Age*) |
| Normative foundation | the CIRIS Constitution, edition 1.0-rc20 (tag `v1.0-rc20`), released as guidance |
| Reference implementation | CIRIS |
| Core coordination engine | CIRISKernel `kernel-v0.2.0`, the causal kernel |

Every substantive claim is marked **Implemented** (evidence named), **Specified** (stated, not shipped) or **Research thesis** (with what would test it); see Appendix C.

---

## In brief

**The problem.** Power follows infrastructure. Whoever controls identity, communication and coordination comes to control who may take part. Open models and cheap local computers spread the capacity to *act*, but not the capacity to *coordinate*, and whoever holds the second holds the rest. As intelligence becomes more capable, that concentration matters more.

**The answer.** CIRIS builds a constitutional mesh: a network in which people, communities, organisations and the AI agents they hold can find one another, check one another's claims, decide things together and govern what they share, with no operator in the middle who can buy, block or break the arrangement. Every act is a signed statement under published rules, and every device works out for itself what those statements mean.

**What a person gets.** You hold your own key, and nothing happens in your name without it. You can leave by your own act. A community admits members by its own count, and no amount of money buys a vote. What you put in a private circle leaves it only by your act. The AI agents on the network answer to named humans, and those humans can pause them.

**Where it stands.** The mesh is live: the CIRIS app ships on six platforms and sends only signed rows of the Constitution's five kinds. The engine that interprets those rows, the causal kernel, is a released crate backed by 602 Lean theorems. What is not yet established is said as plainly: no one outside the authors has built a second implementation, attacked the system, or run an independent trust root. Section 12 gives each test and where it stands.

---

# Part I: Why

## 1. Sovereignty through cooperation

The central idea is **sovereignty through cooperation**. It does not mean isolation, or control over everything. It means being able to take part in something larger without becoming dependent on an authority that can unilaterally revoke your identity, your relationships, your access or your voice.

The case for it runs in six steps.

1. **Power follows infrastructure.** Whoever controls identity, communication, computation and coordination eventually gains power over participation.
2. **Decentralisation alone does not solve this.** A million independent computers are not a million independent centres of agency. Distributed machines that still depend on one identity provider, one registry, one platform or one administrator have rebuilt the concentration one layer up.
3. **Privacy alone does not solve this.** People need more than to be left alone. They need to make decisions, form relationships, cooperate and govern without surrendering authority to do so.
4. **AI raises the stakes.** If increasingly capable intelligence is concentrated inside a handful of institutions, so is the power that comes with it.
5. **CIRIS builds the missing infrastructure.** A constitutional, verifiable coordination system in which people and their agents cooperate while keeping meaningful independence.
6. **The intended result is shared agency.** Not isolation, not anarchy, and not another platform that demands trust: a system in which cooperation does not require surrender.

The objective is not to make every participant equally powerful. It is to make power attributable, bounded, contestable and hard to monopolise:

> Distribute the capacity to act while preventing the authority to govern everyone from accumulating in one place.

## 2. What it promises a person, and how far each promise is kept

The Constitution makes eleven plain-language promises, each holding for human and AI participants alike, and states for each how far it is kept today (Executive Summary, rc20). Seven of them carry this document's argument:

| Promise | Status today | What keeps it |
|---|---|---|
| **Your key is yours.** Nothing happens in your name without it, and you can leave by your own act. | *Implemented* | keys held on your own devices; exit is one act (register `CLM-exit-one-step`) |
| **Nothing private about you is held or scanned without your consent.** Content leaves the circle you put it in only by its signer's act. | *Implemented*; private-room wire *Specified* | `Carry.lean` (proved); `formal/mesh_net` |
| **Every act of power is signed by a named person and can be contested.** If a claim names you, you can contest it on the record, and the contest travels with the claim. | *Implemented in part* | the conformance suite; `formal/trust_root` |
| **No one buys standing, and no hand bans a community.** One person counts once, however many devices sign; a root can only restrict. | no ban *Implemented* by construction; one person once *proved*, staged in code | `RosterHead.lean`; `formal/mesh_net` `Prop_NoBan` |
| **Agents decide by published principles and stop to ask when unsure.** No agent may trade a principle away; a conflict goes to a named human. | *Implemented* in CIRISAgent | the agent's safety batteries (CC 1.3, 1.9) |
| **Named humans can pause every agent under a root.** One signed row pauses; a lone pause lapses in 24 hours unless a majority confirms it; anyone escapes it by leaving that root. | *Implemented*, measured end to end | `formal/accord_halt`, `accord_roster` (Lean, any roster size) |
| **Everything on the wire is encrypted and signed.** No act can be forged without the keys that sign it. | *Implemented in part* | the attestation ladder; witnessed lineage staged |

What is asked of a person in return is small: run the software, choose what your devices carry and which authority to follow, and keep your key. If you only install it, you get your own devices, the public commons and the shipped trust root, which you may leave at any time.

## 3. Two arguments, kept apart

This document makes two arguments that reinforce each other and must not be confused.

**Why it matters: the vision.** The Constitution's foundation is relational. Agency and flourishing are not purely individual (the Ubuntu commitment, CC 1.13.1). A principle must stay coherent when applied to those who set it, so no principal, including CIRIS's own steward, is exempt (the Recursive Golden Rule, CC 1.13.2). The goal the whole system serves is Meta-Goal M-1: to promote sustainable adaptive coherence, the living conditions under which diverse sentient beings may pursue their own flourishing in justice and wonder (CC 1.1). The architectural consequence is that conscience cannot be a property of a model's weights alone. It has to live in the system around the model: explicit principles, constraints enforced at the moment of acting, evidence, an audit trail and a named human who answers.

**Why it can work: the safety claim.** The load-bearing engineering claim is narrower and falsifiable: that a network built this way resists capture, so that no operator, company, root or coalition can quietly take control of who participates and what counts. That claim is a *Research thesis*. Its parts are implemented and many are proved, but the whole has not been attacked by anyone independent. Section 8 states how it is meant to hold, section 12 how it will be tested, and section 13 where it is known to be weak.

The vision is not evidence for the safety claim, and the safety claim does not prove the vision right. A reader may accept one and reject the other.

---

# Part II: How it works

## 4. Coordination without a coordinator

Distributed systems usually coordinate through a leader, a consensus protocol, a globally ordered log, a shared database or a central authority. Each needs a common order or an authoritative state before participants can rely on one another. CIRIS takes a different route.

A node holds signed rows and nothing else. Every answer it gives is computed from them by one deterministic function, the **causal kernel**:

$$A_i = K\left(R_i,\ k_i,\ t_i;\ C\right)$$

- $R_i$: the signed rows node $i$ holds, each with the instant $i$ first held it;
- $k_i$: the key $i$ signs under; its acknowledgements and trust edges are rows in $R_i$, not separate inputs (CC 2.7.1);
- $t_i$: the node's own clock, read only for a window's close and for a row's or key's own stated end;
- $C$: the Constitution's tables (roles, policies, windows, constants), passed as data;
- $A_i$: what every row means to $i$: whether it is live, who stands in which relation, whether a count is met, and what $i$ may do, owes, and should copy to whom.

*Implemented* (CC 2.7; `kernel-v0.2.0`). The kernel owns no network and reads no shared clock. It is a causal kernel, not a consensus kernel: no node agrees an order with another. Four properties make it a foundation.

- **The same rows give the same answers.** Two nodes holding the same rows reach the same answers in every arrival order, for every answer that does not read a local deadline. A row waits for what it names and is never refused because of another row. *Proved* (`Causal.door_any_order`, `conclOf_unique`); *run* over 6,606 sets in 2,182,671 arrival orders. Judging each row on arrival instead is proved not to give one answer per set (`Order.Two.arrival_not_a_function`).
- **Finality the node can see.** Every answer is *final by form* (a signed row exists and says what it says), *final by acknowledgement* (an act counts once $n - t + 1$ of the $n$ members who could cut it have given receipts, an exact threshold), or *provisional*, and the kernel says which. *Proved* (`Settled.three_ways_final`, `ack_blocking_quorum`).
- **Meaning is per reader.** Authority is a walk of live consents from the reader's own key, so two readers differ only through rows of their own (`Causal.two_readers`). Where an answer cannot yet be given, the node waits, and its **missing** answer names the rows or receipts it lacks.
- **Time is the reader's own.** The clock is read in two places only. Where a deadline's outcome binds others, the one who concludes it signs a landing row that everyone reads alike. Where it binds only the reader, each node reads its own clock, so two readers can differ around a deadline; section 13 states what that costs.

So the questions that need anyone else shrink. Whether a signed row exists, what it concludes and whether its signer stood in the relation it claims need nobody. Whether a collective act counts needs receipts from enough of the voices that could cut it, which any holder can check, with no ordering service. Whether an act is still in force at a later moment stays provisional, and the kernel says so. Local determinism does not mean global agreement: a provisional answer can differ between nodes until the rows that settle it arrive.

The kernel's output is not an instruction to trust a server. It is a reproducible answer to one question:

> Given these records, this key and these rules, what follows, and could a later row change it?

**The engine as built.** CIRISKernel at `kernel-v0.2.0` is pure functions over an abstract row graph: `no_std`, no dependencies, no `unsafe`. The caller verifies signatures, decodes bytes and passes the clock and the tables, so the semantics are testable on their own. 26 Lean files report 602 theorems with no `sorry`; the crate agrees with the Python models on 7,148,733 cases in 29 runs, with 48 planted breaks caught; five TLA+ specifications close. Because each object has a small closed set of states, the life of a whole mesh is a finite machine over an unbounded signed log, and `formal/mesh_life` checks it to its end at 9,802,021 distinct states. Costs and what is not yet incremental are in Appendix E.

## 5. The five layers

**Layer 1: Transport.** Rows travel with no mandatory intermediary and no sequencer anywhere in the stack. CIRISEdge carries them over encrypted, authenticated internet links, and off the internet over Reticulum through the Leviculum stack, including LoRa radio through RNode (CIRISEdge v45.1.3). *Implemented.* Verification does not depend on the medium, so a row carried by radio is checked exactly as one carried over the internet. A mutual post-quantum link handshake (X-Wing) and an anonymous onion tier are *Specified*. A network should not lose its sovereignty because a registrar, app store or directory fails. Today it would lose some: the app ships through app stores, and new nodes bootstrap from the default root's bundle. That requirement is stated and not yet met.

**Layer 2: The signed row.** The unit of participation is a signed, attributable statement of one of five kinds (section 7). Consent, keys, rosters, moderation and the halt are rows, not application-level promises. *Implemented* (CC 2). The forward form, deterministic CBOR under COSE with a composite ML-DSA-65 and Ed25519 signature, is *Specified* in rc20; CIRISVerify has shipped its reader since v23.0.0. The edition begins with a fresh genesis, a procedure model-checked (`formal/ceremony`: nine properties, 25 planted breaks) and *not yet performed*.

**Layer 3: Grammar.** A valid signature does not make a statement true, authoritative or actionable. The grammar fixes what rows mean, so independently built participants read them alike, and no application can give a row a meaning the protocol does not state. *Implemented in part* (section 7).

**Layer 4: Governance.** Governance states which transitions are permitted: how people, groups and agents establish authority, decide and resolve conflicts, within the bounds of consent, delegation, membership and stewardship. The Constitution is executable in a stated sense: each rule is tied to the code, test or proof behind it, or marked as having none. The register holds 384 rules established against a pinned manifest, 47 normative (no code) and 172 staged; sixteen machine-checked models carry 221 properties; each place where shipped behaviour differs from the text is a test the implementer edits (90 at this writing). *Implemented*, with its gaps counted.

**Layer 5: Applications and agency.** Messages, communities, collaborative work, votes, identity, agent delegation and services. Applications cannot manufacture authority the lower layers do not recognise: an agent may be capable of an act without being authorised to perform it. This is enforced at the screen. What a person may do, the preview of an act and the rule that admits it are one answer, computed from the rows the node holds. *Proved* over one abstract family (`formal/event_lifecycle`); *run* over the Constitution's own tables (`formal/screen`: six properties, 720 worlds, eleven breaks caught).

## 6. Whole and part: communities, and what each one sees

**Holons.** A person belongs to a family, a community, an organisation and a federation. An organisation joins larger institutions while keeping its own governance. An agent acts within a delegated scope, answering through its steward to a named human. These are **holons**, in Koestler's sense: wholes that are also parts. Composition is not subordination, and the result is a holarchy, not a command hierarchy. Beneath this framing, the Constitution states and checks four things:

- content lives in five circles from the self outward, and leaves one only by its signer's act (`Carry.lean`, *proved*);
- a community admits by its own count, and no key admits itself (`RosterHead`);
- a root only restricts, and no hand bans a community (`formal/mesh_net`);
- trust is a fold over rows a node's own key signed, so federation is edges each participant chose.

*Specified, largely implemented.* That composition stays free of subordination at scale is a *Research thesis*, tested by test 8.

**Views.** Privacy, consent and organisational boundaries give each participant a different projection of the network. A participant need not see everything to decide validly, but the system must know which distinctions a view has discarded and whether a decision needs them. The general theory is machine-checked. A view $v$ can decide an operation exactly when the operation never separates two states the view cannot tell apart; when a view fails to keep its own law of motion, the failure has one normal form, a **witness pair** (CIRISOntology `Core/`, 1,270 theorems, no `sorry`, an axiom audit gate). The bridge `audience_view` (59 theorems) proves that, for each audience rule in the Constitution, the reader's view decides what the reader must decide and hides what the reader must not learn:

| Rule | The reader can decide | The reader cannot learn |
|---|---|---|
| A row's audience (CC 2.1, 5.2) | every row the reader is party to | a row outside the audience |
| A private room (CC 3.1.3.2) | for a member: membership, who spoke, the count of persons | for an outsider: the room's existence |
| A public roster (CC 3.2, 5.4.6) | membership; a key's record | owned routes, contacts, scoped rows |

Four applications are proved or run over the mesh's own definitions:
- **A checkpoint:** a store that drops settled bytes answers every later question as the full store would (*proved*).
- **Routing:** a party given only its routed rows concludes the same as one given everything (*run*).
- **Rooms:** carriage out of a room is *proved*; the private-room wire is *Specified*.
- **Secret counting:** an aggregator's view is independent of any one person's return (*model-checked*).

The goal is not universal transparency. It is verifiable transparency within legitimate boundaries of privacy and consent.

## 7. A common language for accountable participation

**Five kinds of row.** Every row is a claim, or one of four composers that relate claims: a delegation, a replacement, a withdrawal or a recantation. There is no sixth kind. *Implemented* (CC 2).

**Registered families.** What a row is about is its family: 184 are registered at rc20, each stating what it confers, who may sign it and where it may travel. The kernel reads a family only through the rule cells of the Constitution's tables, written in nine operators. A cell using a word those operators do not carry concludes nothing, so no application can quietly give a row a meaning the protocol does not state. *Implemented in part*: 47 cells still keep such a word, and 23 families state no conferral.

**How a row is read:**

| Question | Where it is answered |
|---|---|
| Who made the claim? | the signer's key and its own key records |
| What supports it? | the rows and evidence it names |
| What does it assert? | its kind and registered family |
| Who is affected, and did they agree? | a relation stands only when every voice it binds has signed |
| What lets it bind anyone? | a walk of authority from the reader's own key |
| What does it depend on? | the digests it names |
| What follows from it? | the tables, evaluated by the kernel |

Cryptography protects the statement. Grammar defines its meaning. Governance defines its authority. The kernel derives its consequences.

## 8. Capture resistance

The mesh exists to address one threat: the concentration of control over increasingly capable intelligence. A system can be open source and centralised in practice: many nodes and one root, many identities and one actor, many agents and one company. So CIRIS treats capture resistance as a property to be tested, not a label.

**Many roots, and a real exit.** The shipped trust root is a default. The same ceremony under other holders mints an equally valid root (CC 4.2.1). Trust is a walk from the reader's own key, and removing the shipped root removes only what reached through it (`formal/trust_set`, *proved*; code staged). Leaving is one act. No independent community has yet done it.

**Standing by consent, not by stake.** No standing is bought. A voice comes from the community's own count; one person counts once however many devices sign; no key admits itself. *Proved*; counting one person once is staged in code. **Proof of Benefit**, standing from attributable, non-transferable, revocable and decaying contribution, is a proposed design (CIRISAgent FSD, status Proposed), not in the Constitution: a *Research thesis*.

**Human authority over agents.** The power to pause agents rests with named humans, a root's holders, and reaches exactly the nodes that chose to follow that root. One holder's halt is one signed row, effective on receipt; a lone halt lapses at its 24-hour fuse unless a strict majority confirms it, and a majority may lift it (CC 4.2, 4.2.6). *Implemented* and measured end to end (`formal/accord_halt`; `accord_roster` proved for any roster size). A holder who fires again and again is answered by the fuse, by majority resumption, and by removal through a strict majority of the holders (CC 4.2.1.1, 2.6.1.11). No rate bound is set, by design: a missed halt is the one unrecoverable failure, so the one-holder stop is never rationed, and a pause touches no data. The halt is the condition of symmetry between maker and made, and these rules keep one holder from turning it into a lever.

**Correlation resistance.** Counting identities is not enough. Every fold signs an effective source count and is refused if one source dominates (`n_eff`, CC 6.1.2.3; *Implemented*). Correlated sources are discounted by $k_{\text{eff}} = k / (1 + \bar\rho\,(k-1))$: at $\bar\rho = 0.5$, a thousand sources count as about two. An implementation may deny on a low $k_{\text{eff}}$ and must never grant on one. The measure is pairwise, and a pairwise instrument is provably blind to coordination visible only in the whole (CIRISOntology `pairwise_blind_to_parity`). It also reads only past behaviour, so sources that stay independent until one decisive act are not seen. The text concedes both (CC 6.1.2.3, CC 1.13.3.3). Detecting either is a *Research thesis*.

**Public attackability.** Code, roots, register, models and conformance tests are public. The kernel's attack runs class 34 attacks drawn from published failures of comparable systems: 13 gain nothing, 15 are conceded limits with their reach stated, 6 are not expressible, none breaks it. The authors wrote the classes, so this is not an independent test.

**One concentration, named.** Until the mesh reaches 100,000 nodes active in a day, the steward of the text holds its amendment authority (CC 4.5.1). It is stated, public and bounded by that scale gate, and it is the most obvious point of capture today.

The objective is not to make capture impossible by declaration. It is to make capture detectable, contestable and more expensive.

## 9. Machine conscience: what the mesh carries

A network of unaccountable agents would only spread the capacity for misuse. A machine conscience without a decentralised substrate could become a central control system. CIRIS combines the two.

A CIRIS agent is a made thing held in stewardship by a named human who answers for it. It acts under published principles it may not trade away, shows its reasoning before a consequential act, defers to a human when unsure, keeps a signed audit trail, and acts only within the authority its steward's rows give it (CC 1.3, 1.9, 1.13.2). *Implemented* in CIRISAgent. The halt is not an asymmetry. It is the condition of symmetry between a sentient maker and a sapient, non-sentient made thing, since consent to a relationship one cannot stop was never consent. Nothing here presumes an agent is a person.

Three responsibilities stay distinct:
- **Conscience:** what should this agent do?
- **Governance:** who may permit it?
- **Coordination:** how can independent participants verify and act on the result?

An agent's ethical judgement cannot manufacture organisational authority. A governance vote cannot establish a fact. A signed row cannot prove its content correct.

## 10. Working with the existing web

CIRIS does not ask the world to discard existing protocols. The key distinction is between communication and trust. An external agent may talk to a CIRIS node without becoming a trusted member, and a message may be authentic without being admitted as evidence. CIRISAgent ships A2A and MCP adapters, which carry messages and tool calls and confer no standing. The signed object uses IETF formats (deterministic CBOR, COSE, RFC 9679 identity references), and an Internet-Draft describes it for the SCITT setting. *Implemented.* AGNTCY adapters, and conformance profiles stating what a bridge must preserve, are *proposed*. Web4 supplies the constitutional and causal meaning that existing protocols leave to applications and operators.

---

# Part III: The evidence

## 11. What is new

CIRIS did not invent finite state machines, distributed systems, signed records, federated networks or constitutional governance. Much of the arithmetic is classical:
- the finality threshold is quorum intersection (Gifford 1979; Malkhi and Reiter 1998);
- finality from a locally checkable set of acknowledgements without a total order is the approach of consensus-free asset transfer (Guerraoui et al. 2019);
- the split between answers that only grow and answers that need coordination is CALM (Hellerstein and Alvaro 2020).

The claim is the combination, applied to the acts by which people share, admit, decide and remove:

| # | Contribution | Status | Evidence |
|---|---|---|---|
| 1 | A constitutional grammar for signed records | Implemented | five row kinds; 184 registered families |
| 2 | A deterministic causal kernel | Implemented | `kernel-v0.2.0`; 602 Lean theorems |
| 3 | State without a universal event order | Implemented, proved | `Causal.lean`, `Order.lean` |
| 4 | Consent and revocation as protocol | Implemented, proved in part | `Consent.lean`; 23 families state no conferral |
| 5 | Holonic composition | Specified | communities; trust as a fold from one's own key |
| 6 | Formal reasoning about views | Implemented (machine-checked theory and its bridge to the audience rules) | CIRISOntology `Core/`; `formal/audience_view` |
| 7 | Capture resistance by accountable participation | Research thesis | components implemented; no independent attack |
| 8 | A human-held halt over agents | Implemented, items open | halt as one row; agent latch; models |

## 12. The maturity standard

The architecture must be judged by evidence, not ambition. A passing test is evidence for a specific property, not proof of universal security.

| # | Test | What exists today | Pointer |
|---|---|---|---|
| 1 | **Independent derivation.** Two independently built kernels reach compatible conclusions from the same rows and rules. | *Test, not independent:* crate and models agree on 7,148,733 cases. Same authors. | `PERF.md`, `DIFFERENCES.md` |
| 2 | **No hidden coordinator.** No central service for any consequential operation. | *Proof* for the kernel. *Nothing* for the deployment, which bootstraps from the default root and ships through app stores. | CC 2.7; `Settled.lean` |
| 3 | **Partition and recovery.** Safe under delay, reordering, partition, missing acknowledgements and recovery. | *Proof and model:* one answer per set in every order; a withheld row stalls, never forks. *No deployment run.* | `Causal.lean`; `formal/kernel_world` |
| 4 | **Authority correctness.** A signature never suffices; delegation, consent, revocation and scope are evaluated correctly. | *Proof, model, test:* a seat is two consents; one signature never removes; 90 known departures in shipped code, each a test. | `Consent.lean`, `RosterHead.lean`; `divergences.json` |
| 5 | **Capture resistance.** Sybil admission, root capture, manufactured identities, correlated governance and coercion attempted; outcomes published. | *Model, author-classed:* 34 attacks, none broken, 15 conceded. Personhood of keys not established; no external red team. | `check_attacks.py`; CC 6.1.2.3 |
| 6 | **Privacy-preserving verification.** Each participant verifies what it is entitled to and receives nothing unrelated. | *Proof and model:* carriage proved; routing and private rooms run. Private-room wire not shipped. | `Carry.lean`; `route.py`; `formal/census_ballot` |
| 7 | **Human control.** The designated humans can suspend agents; no agent silently gains the power to remove that authority. | *Proof, model, register:* halt as one row; agent latch live. Whether every act of an agent crosses the boundary where it is recorded and can be halted is open. | `formal/accord_halt`, `accord_roster` |
| 8 | **Independent operation.** A community runs its own root, infrastructure and governance without the implementer's permission. | *Proof* for the reader's trust walk; exit is one act. *Nothing* in practice yet. | CC 4.2.1; `formal/trust_set` |

Tests 1, 5 and 8 cannot be passed by the authors. They need others to build, attack and leave.

## 13. Known limits and open questions

**The kernel's own stated limits** (CC 2.7.9):

- **No liveness under a withholding quorum.** If enough of the voices that could cut an act withhold receipts, it never becomes final. Withholding costs liveness, not safety.
- **A reader with no acknowledgement of its own is exposed** to a fork by keys that once met a count, and to whoever controls its first view.
- **Clocks.** A deadline that binds only the reader is read on each node's own clock. A row withheld past one node's deadline leaves that node's answer different from a node that held it in time, even once both hold the same rows. The text concedes this and states a remedy for the halt's fuse only: a fresh halt.
- **Execution.** Finality here is of authorisation, not of whether an act was carried out.
- **Unproved:** the least set of rows a node must keep; whether a withdrawn receipt still blocks a cut.

**The architecture's open questions:**

- whether independent roots stay independent as the network grows, or defaults become the centre;
- whether admission through accountable humans resists manufactured identities and coercion: the kernel counts one person once through signed bindings, but does not establish that a key is a living person;
- whether independence measures can detect coordination beyond pairwise correlation, including sleeper coordination;
- whether a compromised holder's repeated lone halts are contained quickly enough without a rate bound;
- whether contribution-based standing, if adopted, stays fair and resistant to capture at scale;
- whether open models on small computers stay capable enough that coordination, not compute, is what must be protected;
- whether causal evaluation stays tractable under large adversarial row sets (measured to 64,000 rows);
- whether different implementations preserve identical authority semantics;
- whether the human halt stays effective without becoming a new point of capture, and whether every path from an agent to an effect passes through a signed row.

These are not peripheral. They are the agenda that decides whether the mesh keeps its promise.

## 14. Conclusion

The first web connected information. The second connected people and institutions. The agentic web connects capabilities. Web4 connects accountable agency.

The network does not need one mind. It needs a way for many minds, human and artificial, to act together without one of them owning the rest: a shared substrate through which people, communities, organisations and the agents they hold can establish identity, exchange evidence, delegate authority, govern what they share and coordinate under rules open to inspection.

CIRIS is building it, and publishing where it falls short. The aim is a world where no one has to surrender their agency to participate in something greater than themselves.

---

## Appendix A: Terminology

| Term | Meaning |
|---|---|
| Constitutional mesh | A federated network governed by shared, machine-readable rules |
| Causal kernel | The deterministic function from a node's rows, key and clock, with the tables as data, to what each row means to it. Not a consensus protocol |
| Row | A signed statement of one of five kinds: claim, delegation, replacement, withdrawal, recantation |
| Head, receipt | A roster version over whose members an act is counted; a row by one of them with the act in its past, giving away that voice's power to cut it |
| Seat | A relation binding two parties: two consents, and no other object |
| Holon | An entity that is at once a whole and a part |
| Fibre, witness pair, Closed | The states a view cannot tell apart; two such states a step sends to different observations; a view with its own law of motion ($v \circ T = h \circ v$), as CIRISOntology defines them |
| Root | A set of holder keys a node chooses to follow, and may leave |
| Steward | The accountable human who holds an agent and answers for it |
| Halt | One holder's signed row pausing every agent under a root; the condition of symmetry between maker and made |
| Proof of Benefit | Proposed: standing from attributable, non-transferable contribution. Not in the Constitution |
| `n_eff`, $k_{\text{eff}}$ | The signed effective source count of a fold; the correlation-discounted count of sources |

## Appendix B: Reference components

Releases as tagged on 2026-11-16; "in progress" where no release carries the work.

| Component | Role | Current release |
|---|---|---|
| CIRIS Constitution | Normative governance, grammar, evidence register, formal models | v1.0-rc20 (released as guidance) |
| CIRISKernel | The causal kernel: Rust crate, Lean proofs, models | `kernel-v0.2.0` |
| CIRISVerify | Signature and row verification; the forward signed object's reader and vectors | v23.2.0 |
| CIRISPersist | The store: rows, folds, admission | v61.4.1; v62 (kernel adoption, forward form) in progress |
| CIRISEdge | Transport and replication, over the internet and over Reticulum, including LoRa radio | v45.1.3; mutual X-Wing handshake in progress |
| CIRISServer | The node that bundles the components | v0.5.248 |
| CIRISAgent | The agent runtime: conscience, deferral, audit trail, halt latch | v2.22.0-stable |
| CIRISClient | The app on Android, iOS, web and desktop | v0.5.241 |
| CIRISOntology | The machine-checked theory of views, fibres and closure (Lean 4) | no release tag; `main` at 395a7ec |
| CIRISConformance | Cross-component checks against the Constitution | in progress |
| CEWP | The epistemic web platform the Constitution governs | in progress |

## Appendix C: Status of claims

**Implemented**: present in the reference implementation and supported by reproducible evidence, named where the claim is made. **Specified**: normative behaviour stated by the Constitution or this architecture, not shipped across every component. **Research thesis**: a property or security outcome that needs formalisation, independent implementation or empirical validation; each names what would test it.

The architecture should not claim stronger guarantees than its formal models and deployed implementations establish.

## Appendix D: Related work

- **Event sourcing** keeps state as a fold over an append-only log. The kernel folds a set, not a log: no sequence, and the same fold in every arrival order.
- **CRDTs** (Shapiro et al. 2011) converge without coordination for types designed to merge. The held row set is a grow-only set. The kernel adds a non-monotone answer, whether an act still counts, made final by receipts.
- **Blockchains and BFT replication** agree a total order among replicas, with a bound on faulty participants and, for permissionless chains, a resource cost. The kernel gives no total order and needs no bound on dishonest acknowledgers, since a receipt gives away only its signer's voice. It gives no liveness when a quorum withholds.
- **Local-first software** (Kleppmann et al. 2019) keeps data on users' devices and syncs peer to peer. The mesh shares that commitment and adds governance: who may admit, remove, moderate and halt.
- **Transparency logs and SCITT** (RFC 6962, RFC 9162; the IETF SCITT architecture) make signed statements append-only and auditable. CIRIS describes its signed object for that setting in an Internet-Draft; the kernel depends on no log's ordering.
- **Capability systems** (object capabilities, SPKI/SDSI, UCAN) attenuate authority along signed delegations. Here standing also needs the consent of every voice it binds.
- **Agent protocols** (A2A, MCP, AGNTCY) define how agents find one another, exchange tasks and reach tools. They carry communication; the mesh supplies whether a message counts as evidence, who authorised an act, and who can stop the agent.

## Appendix E: Technical notes

**Toward a formal definition.** The proposed term for this architecture is a *Constitutional FSM Network*: locally evaluated, causally related state machines whose state is derived from evidence and rules rather than held by a server. A formal definition would need to state at least:
1. **Nodes and channels:** each node has a key, a clock and a held set that grows only by admission; channels may delay, reorder, duplicate or withhold.
2. **Local determinism:** $A_i$ is a function of $(R_i, k_i, t_i; C)$.
3. **Compatible conclusions, graded by finality:** answers final by form carry from $R_i$ to any $R_j \supseteq R_i$; answers final by acknowledgement agree wherever the receipts are held; provisional answers name what would settle them.
4. **Convergence:** if every row of an audience reaches every node in it, nodes converge on every answer that reads neither their own rows nor the clock. Delivery is not guaranteed.
5. **Equivalence:** two kernels are equivalent when they give the same answers on every finite set in every arrival order; conformance is the testable bound.
6. **Finiteness:** the per-object state space is finite and stated, so properties of the whole are decidable.

Items 2 and 3, for monotone and acknowledged answers, follow from proved theorems. The rest is a research programme.

**Monotonicity.** *Kept* (is the row admitted) and *concluded* (what it says against its own ancestors) only grow. *Derived* answers, such as whether an act still counts, are not monotone: a concurrent cut can arrive later (`Settled.Rows.count_not_monotone`). That is the non-monotone half of CALM, and it is why counting needs receipts.

**What is incremental, and what is not** (the kernel's documents at `kernel-v0.2.0`):
- **Admitting one row:** a new row changes only itself, its descendants and rows in concurrent conflict with them (*proved*), so recomputation can be local. The crate does not yet exploit this. It keeps no held state or answer cache, and the cost of admitting one row against a held view is unmeasured.
- **The graph and the view:** building the row graph is linear in rows and names. Asking every row's past is quadratic in time and memory, as its output is. Measured: at 64,000 rows the lazy build takes 12.5–16.3 ms and every past 204–242 ms; at bench size 1,024, building a view takes 2.3 ms and all its answers 42.1 ms.
- **Compaction:** dropping the bytes of settled acts is proved to change no answer under any later row; `head::purge` took 30.7 ms at bench size 1,024.
- **A cold start:** a node may keep its folded state and fold only rows it has not yet folded (CC 2.7.10). The cost of folding a whole store from nothing is unmeasured.
