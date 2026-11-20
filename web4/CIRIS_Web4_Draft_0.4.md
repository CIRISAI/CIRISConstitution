# CIRIS Web4

## A Constitutional Mesh for the Networked Age

*Architecture, thesis and reference implementation*

| | |
|---|---|
| Draft | 0.4, strategic architecture proposal, 2026-11-16 |
| Normative foundation | the CIRIS Constitution, edition 1.0-rc20 (tag `v1.0-rc20`, 2026-11-16), released as guidance |
| Reference implementation | CIRIS |
| Core coordination engine | CIRISKernel `kernel-v0.2.0`, the causal kernel |
| Architectural thesis | Coordination without a coordinator. |

Every substantive claim is marked **Implemented** (evidence named), **Specified** (stated, not shipped) or **Research thesis** (with what would test it); see Appendix C.

---

## Summary

**The proposition.** Open models and distributed compute spread the capacity to act, not the capacity to coordinate, and whoever holds the second holds the rest. CIRIS proposes a constitutional mesh: people, organisations and AI agents establish identity, make attributable claims, delegate authority and govern shared things through signed rows that each node evaluates for itself under published rules. No node agrees an order with another. The engine is the **causal kernel**: a deterministic function from the rows a node holds, its own key and its own clock to what those rows mean to it.

**What is claimed as new** is the combination, not the parts (section 11):

| # | Contribution | Status | Evidence |
|---|---|---|---|
| 1 | A constitutional grammar for signed records | Implemented | five row kinds; 184 registered families |
| 2 | A deterministic causal kernel | Implemented | `kernel-v0.2.0`; about 600 Lean theorems |
| 3 | State without a universal event order | Implemented, proved | `Causal.lean`, `Order.lean` |
| 4 | Consent and revocation as protocol | Implemented, proved in part | `Consent.lean`; 23 families state no conferral |
| 5 | Holonic composition | Specified (owner's framing) | communities; trust as a fold from one's own key |
| 6 | Formal reasoning about views and fibres | Implemented (theory, machine-checked); and its bridge to the mesh's audience rules (`audience_view`, 59 theorems) | CIRISOntology `Core/` (Factoring, NonFactoring, Closure); `formal/audience_view` in the Constitution |
| 7 | Capture resistance by accountable participation | Research thesis | components implemented; no independent attack |
| 8 | A human-held halt over agents | Implemented, items open | halt as one row; agent latch; models |

**The eight maturity tests** (section 12) and where each stands today:

| Test | Today |
|---|---|
| 1 Independent derivation | Two implementations by the same authors agree on every case. None by others yet. |
| 2 No hidden coordinator | By construction in the kernel; deployment still bootstraps through the default root and app stores. |
| 3 Partition and recovery | Order-independence proved; no deployment run under partition. |
| 4 Authority correctness | Strongest: proved and run; 90 known departures in shipped code, each a test. |
| 5 Capture resistance | Author-classed attack runs (34 attacks, 0 broken, 15 conceded); no external red team. |
| 6 Privacy-preserving verification | Carriage proved; routing and private rooms run; private-room wire not shipped. |
| 7 Human control | Halt path implemented and model-checked; totality of the agent's boundary open. |
| 8 Independent operation | Re-rooting proved for the reader's walk; not yet done by anyone else. |

---

## 1. The proposition

The first web connected documents. The second connected people, services and commerce. The emerging agentic web connects tools, models and autonomous processes.

None of these transitions, by itself, solves the problem of cooperation between independent actors:

> How can entities that do not trust one another coordinate, make commitments, exercise authority and act together without surrendering control to a central intermediary?

CIRIS proposes an answer. Web4, as used here, is a **constitutional mesh**: a decentralised coordination substrate in which people, organisations and AI agents establish identity, exchange attributable claims, delegate authority, govern shared resources and derive compatible conclusions from verifiable records. (The term has other uses, among them the European Commission's 2023 initiative on "Web 4.0" and virtual worlds; here it names only the step this document describes.)

The network needs no central operator to decide what everyone believes or what everyone may do. Each participant evaluates the same published rules against the records it holds. The result is not merely a peer-to-peer communications network. It is a system for coordinating independent agency.

Its defining characteristics:

- **Sovereignty**: participants hold their own keys and leave by their own act. *Implemented.*
- **Intelligibility**: every claim carries its signer, the rows it names and a registered meaning. *Implemented.*
- **Consent**: a relation stands only when every voice it binds has signed. *Implemented, proved.*
- **Constitutionality**: published rules bound what any row can authorise. *Implemented in part.*
- **Causality**: the only order is what rows name; no universal event order is assumed. *Implemented, proved.*
- **Accountability**: every act of power is a signed row by a named key. *Implemented.*
- **Exit**: anyone may leave a root or found one; the shipped root is a default. *Specified;* not yet exercised by an independent root.

CIRIS is the reference implementation of this architecture, and the mesh is live: the CIRIS app ships on six platforms and sends only rows of the five kinds.

## 2. Why a constitutional mesh?

The centralisation of AI is not only a model problem. Even if powerful models become freely available, the ability to coordinate their use can stay concentrated.

A million independent computers are not a million independent centres of agency. Without shared means of discovery, verification, governance and cooperation, they remain isolated machines. A network that coordinates everyone through one service, one identity provider, one registry or one administrator has recreated the concentration at another layer.

This is the constitutional mesh problem: enough common structure for cooperation, with no participant owning the whole. Open models and distributed compute are necessary and not sufficient. The missing infrastructure is coordination that cannot be bought, blocked or broken.

The objective is not to make every participant equally powerful. It is to make power attributable, bounded, contestable and difficult to monopolise:

> Distribute the capacity to act while preventing the authority to govern everyone from accumulating in one place.

## 3. A network of state machines

Distributed systems usually coordinate through a leader, a consensus protocol, a globally ordered log, a shared database or a central authority. Each is useful, and each needs a common order or an authoritative state before participants can rely on one another. CIRIS takes a different route.

### 3.1 From machine state to constitutional state

A finite state machine is commonly written

$$M = (S, \Sigma, \delta, s_0)$$

with states $S$, inputs $\Sigma$, transition function $\delta : S \times \Sigma \to S$ and initial state $s_0$. An implementation holds a current state and applies inputs to advance it.

The causal kernel moves the emphasis. A node holds signed rows and nothing else. Every answer it gives is computed from them:

$$A_i = K\left(R_i,\ k_i,\ t_i;\ C\right)$$

- $R_i$: the signed rows node $i$ holds, each with the instant $i$ first held it;
- $k_i$: the key $i$ signs under. Its acknowledgements and trust edges are rows in $R_i$, not separate inputs; there is no trust set and no configuration among the inputs (CC 2.7.1);
- $t_i$: the node's own clock, read only for a window's close and for a row's or key's own stated end;
- $C$: the Constitution's tables (roles, policies, windows, constants), passed as data;
- $A_i$: what every row means to $i$: whether it is live, who stands in which relation, whether a count is met, what $i$ may do, owes and should copy to whom.

*Implemented* (CC 2.7; formal/KERNEL.md; `kernel-v0.2.0`). The kernel owns no network and reads no shared clock. Four properties make it a foundation:

**A function of the set.** For every answer that does not read a local window's close, two nodes with the same rows reach the same answers in every arrival order. An answer that does read one also depends on when each row was first held, which is part of $R_i$ (section 13). A row waits for what it names and is never refused because of another row. *Proved* (`Causal.door_any_order`, `conclOf_unique`); *run* over 6,606 sets in 2,182,671 arrival orders. Judging each row on arrival is proved not to be a function of the set (`Order.Two.arrival_not_a_function`).

**Monotone where it can be.** *Kept* (is the row admitted) and *concluded* (what it says against its own ancestors, for a rule that reads no concurrent row) only grow. *Derived* answers, such as whether an act still counts, are not monotone: a concurrent cut can arrive later (`Settled.Rows.count_not_monotone`). That is the non-monotone half of CALM, and it is why counting needs receipts.

**Finality the node can see.** Every answer is *final by form* (kept; concluded, for a rule reading no concurrent row), *final by acknowledgement* (an act counts at the roster head it names once $n - t + 1$ of the $n$ members there have given receipts, where $t$ can cut it; the threshold is exact both ways), or *provisional*. *Proved* (`Settled.three_ways_final`, `ack_blocking_quorum`).

**Per reader, and waiting.** Meaning is a walk of live consents from the reader's own key, so two readers differ only through rows of their own (`Causal.two_readers`). A reader's acknowledged roster head voids older forks for that reader alone. A window closing unopposed is read on each node's clock. Where an answer cannot yet be given, the node waits, and the **missing** answer names the rows or receipts it lacks.

**Time is the reader's own.** The clock is read in two places only: a window's close and a row's or key's own stated end (CC 2.7.5). Both answers are derived, so provisional. Where a window's outcome binds others, the concluder signs a landing row, so every node reads the same landing; a concurrent answer is recounted against it. Where the outcome binds only the reader (the halt's fuse, a takedown's withhold, a moderation window), each node reads the close on its own clock, signs nothing, and each door states whether a late answer counts: not for the fuse, an invitation or the accord's roster change; yes for an election or a takedown. So two readers can differ around a deadline. The text concedes it: nodes may differ while a window is open, a relay can withhold a row until it is delivered, and an emission made meanwhile cannot be unsent (CC 2.7.9); a landing over an objection that never reached the concluder stands until a concluder lands naming both (formal/KERNEL.md 8a). For the halt the text gives the remedy: a confirmation held after a node's fuse has lapsed confirms nothing there, and a fresh halt is fired (CC 4.2.1.3).

### 3.2 The Constitutional FSM Network

The proposed term for this architecture is a **Constitutional FSM Network**. It is not a collection of conventional machines exchanging messages. It is a network in which:

1. participants produce signed rows;
2. rows establish claims, relationships, consent and governance acts;
3. what a row names by digest fixes its place, and nothing else orders rows of different signers;
4. a deterministic kernel derives conclusions and permitted transitions;
5. each participant evaluates them without asking a coordinator;
6. new rows change derived answers subject to the rules of admission, replacement, withdrawal and cut, and each answer states which of the three kinds of finality it has.

The network is therefore a collection of locally evaluated, causally related state machines. Its state is not a value held by a privileged server. It is a result derived from evidence and rules.

The finite-machine reading is more than a metaphor. Each object has a small closed set of states and the vocabularies are closed, so the life of a mesh is a finite machine over an unbounded signed log and can be checked to its end: `formal/mesh_life` closes at 9,802,021 distinct states. *Implemented* (model). A formal definition of the network as a whole is future work (Appendix C).

> **Sketch, not a definition.** A formal definition of a Constitutional FSM Network would need to state at least:
>
> 1. *Nodes and channels.* Each node has a key, a clock and a held set $R_i$ that grows only by admission; channels may delay, reorder, duplicate or withhold rows.
> 2. *Local determinism.* $A_i$ is a function of $(R_i, k_i, t_i; C)$.
> 3. *Compatible conclusions,* graded by finality. Answers final by form: if $R_i \subseteq R_j$, each such answer of $i$ is also $j$'s. Answers final by acknowledgement: any two nodes holding the receipts agree. Provisional answers: no agreement, but each node names what would settle them. Reader-relative answers differ only through the readers' own rows.
> 4. *Convergence condition.* If every row of an audience reaches every node in it, nodes converge on every answer that reads neither their own rows nor the clock. Delivery is not guaranteed: a relay can withhold (CC 2.7.9).
> 5. *Equivalence.* Two kernels are equivalent when they give the same answers on every finite set in every arrival order; conformance is the testable bound.
> 6. *Finiteness.* The per-object state space is finite and stated, so properties of the whole are decidable.
>
> Items 2 and 3, for monotone and acknowledged answers, follow from proved theorems; the rest is a research programme.

### 3.3 What makes it different

A blockchain establishes shared state through consensus and an ordered ledger. An event-sourced application replays a sequence. A CRDT converges through algebraic properties of replicated operations. An actor system coordinates through messages and local state. A Constitutional FSM Network relates signed claims, causal history, consent, authority, rules, derived state, and revocation and correction.

It uses no consensus protocol and gives no total order. What it changes is which questions need anyone else at all:

- whether a signed row exists, what it concludes and whether its signer stood in the relation it claims need nobody: they are final by form;
- whether a collective act counts needs receipts from enough of the voices that could cut it, $n - t + 1$ of $n$, which any holder can check; no ordering service is involved;
- whether an act is still in force at a later head stays provisional, and the kernel says so.

Local determinism does not imply global agreement, and the absence of a sequencer does not dissolve every coordination problem: a provisional answer can differ between nodes until the rows that settle it arrive.

### 3.4 The kernel as constitutional transition engine

CIRISKernel is the reference implementation of this model: not a database, a network service or an AI reasoning engine, but the deterministic function that evaluates what rows conclude.

Its separation from I/O, clocks, networking, cryptography and storage is architectural. The crate at `kernel-v0.2.0` is pure functions over an abstract row graph: `no_std`, no dependencies, no `unsafe`. The caller verifies signatures, decodes bytes and passes the clock and the tables. *Implemented.* So the semantics are testable on their own: 26 Lean files report about 600 theorems with no `sorry`; the crate agrees with the Python models on 7,148,733 cases in 29 runs, with 48 planted breaks caught; five TLA+ specifications close (`FORMAL_GAPS.md`, `PERF.md`).

**What is incremental, and what is not.** The kernel's documents at `kernel-v0.2.0` state four things.

- *Admitting one row.* A new row changes only itself, its descendants and rows in concurrent conflict with them (`Causal.concl_new_row`, `Settled.concl_ext_local`, *proved*), so recomputation can be local. The crate does not yet exploit it: it keeps no held state, read set or answer cache, and the caller calls it over the rows an answer reads (`ADOPTING.md`); incremental seat state is named as later work (`PERF.md`). The cost of admitting one row against a held view is unmeasured.
- *The graph and the view.* Building the row graph is linear in rows and names; a row's past is computed when first asked; a concurrency query compares levels and searches at most 256 rows before computing a past. Asking every past, a whole-set conclusion, is quadratic in time and memory, as its output is, and `head::View` keeps each row's past as a set and is quadratic too (crate `README.md`, Costs). Measured: at 64,000 rows the lazy build takes 12.5–16.3 ms and every past 204–242 ms; at bench size 1,024, building a view takes 2.3 ms and all its answers 42.1 ms (`PERF.md`).
- *Compaction.* Dropping the bytes of settled acts is proved to change no answer under any later row (`pruned_view_answers`); `head::purge` took 30.7 ms at bench size 1,024. Its complexity is not stated.
- *A cold start.* A node may keep its folded state and fold only rows it has not yet folded (CC 2.7.10). The cost of folding a whole store from nothing is unmeasured in the kernel's documents.

The kernel's output is not an instruction to trust a server. It is a reproducible answer to one question:

> Given these records, this key and these rules, what follows, and could a later row change it?

That is the foundation of coordination without a coordinator.

## 4. The five-layer Web4 architecture

### Layer 1: Transport substrate

The network must move information with no mandatory intermediary: peer discovery, encrypted and authenticated transport, replication, resilience to interruption, no global sequencer, over ordinary internet links, independent infrastructure and alternative media.

CIRISEdge carries rows over encrypted, authenticated internet links with per-item replication (CC 5, 6.1.5). *Implemented.* No sequencer exists anywhere in the stack. A mutual post-quantum link handshake (X-Wing) is *Specified* (CC 5.3.3.10; vectors in CIRISVerify v23.1.x; shipped edge differs, a listed departure). An anonymous onion tier is *Specified*, its layer deal model-checked. The same rows travel off the internet. CIRISEdge's canonical transport is Reticulum, through the Leviculum stack, and its interfaces include LoRa radio links through RNode, alongside TCP, UDP and local links (CIRISEdge v45.1.3, feature `transport-reticulum-rnode`). *Implemented.* Signing and verification do not depend on the medium, so a row carried by radio is checked exactly as one carried over the internet. The Constitution states the rows, not the media, so no medium is privileged.

A network should not lose its sovereignty because a registrar, app store, cloud provider or directory becomes unavailable. Today it would lose some: the app ships through app stores, and new nodes bootstrap from the default root's bundle on its canonical nodes. This requirement is stated and not yet met.

### Layer 2: The signed row

The universal unit of participation is a signed, attributable statement: a **row**, of one of five kinds (section 7). Consent, keys, rosters, moderation and the halt are rows, not application-level promises. *Implemented* (CC 2).

The forward form, deterministic CBOR under COSE with a composite ML-DSA-65 and Ed25519 signature, is *Specified* in 1.0-rc20; CIRISVerify has shipped its reader since v23.0.0, and its readers of the genesis bundle and the halt row at v23.2.0, and the store's producer is in progress. The edition begins with a fresh genesis, a procedure stated and model-checked (`formal/ceremony`: nine properties, 25 planted breaks; `Cutover.tla` closes at 1,250,135 states) and *not yet performed*.

### Layer 3: Epistemic grammar

The grammar defines what rows mean; a valid signature does not make a statement true, authoritative or actionable. It lets independently built participants read rows alike, and an application cannot give a row a meaning the protocol does not state. Section 7 explains how: the row kinds, the registered families, and the questions each answers. *Implemented in part.*

### Layer 4: Constitutional governance

Governance defines which transitions are permitted: how participants, groups and agents establish authority, decide and resolve conflicts, within the bounds of consent, delegation, membership and stewardship. The kernel evaluates those rules over the causal structure of rows.

The Constitution is executable in a stated sense: each rule is tied to the code, test or proof behind it, or marked as having none. The register holds 384 rules established against a pinned manifest, 47 normative (no code) and 172 staged. Sixteen machine-checked models carry 221 properties. Each place where shipped behaviour differs from the text is a test the implementer edits (90 today). *Implemented*, with its gaps counted.

### Layer 5: Applications and agency

Applications are where people and agents use the network: communication, communities, collaborative work, governance, identity and reputation, agent delegation, services and workflows. They cannot manufacture authority the lower layers do not recognise. An agent may be capable of an act without being authorised to perform it; an application may display a decision without being entitled to change its meaning.

This is enforced at the screen. A screen is a function of the rows a node holds, the viewer's key and the clock: what a person may do, the preview of an act and the door that admits it are one answer. *Proved* over one abstract family (`formal/event_lifecycle`); *run* over the Constitution's own tables (`formal/screen`: six properties, 720 worlds, eleven breaks caught). Twenty-five ways back the text states have no transition yet, so no screen can offer them.

## 5. The holonic model: participants as whole and part

The network is made of entities at once autonomous and relational. A person belongs to a family, a community, an organisation and a federation. An organisation joins larger institutions while keeping its own governance. An agent acts within a delegated scope, answering through its steward to a named human.

These are **holons**, in Koestler's sense: wholes that are also parts. The architecture does not assume that a larger holon owns its members. Composition is not subordination, and the result is a holarchy rather than a single command hierarchy.

Each holon has an identity, a record space, boundary rules, relationships, rules for admission, delegation and exit, and a scope of authority. The mesh supplies the common rules that make those boundaries legible to others.

The holon is this document's framing. Beneath it the Constitution states and checks: content lives in five circles, from the self outward, and leaves one only by its signer's act (`Carry.lean`, *proved*); a community admits by its own count and no key admits itself (`RosterHead`); a root only restricts, and no hand bans a community (`formal/mesh_net`); trust is a fold over rows a node's own key signed, so federation is edges each participant chose. *Specified, largely implemented.* That composition stays free of subordination at scale is a *Research thesis*, tested by test 8.

## 6. The fibre model: preserving meaning across views

Participants do not see identical information. Privacy, consent and organisational boundaries give each a different projection of the network. A participant need not see everything to decide validly, but the system must know which distinctions its view has discarded and whether the operation needs them. A community may expose a verifiable conclusion without the private rows behind it; a node may evaluate authority without learning unrelated personal information.

**What the mesh has proved or run, over its own definitions:**

- **The checkpoint.** A store that drops the bytes of settled acts is proved to answer every later question as the full store would; keeping only the bare answer for an unsettled act is proved insufficient, with the counter-example exhibited (`Settled.closed_iff_no_witness_pair`, `count_view_not_closed`). *Implemented, proved.*
- **Routing.** A party given only its routed rows concludes the same as one given everything; a stranger is routed nothing (`route.py`). *Implemented, run.*
- **Rooms.** A row leaves its room only by its own signer's act (`Carry.lean`). *Implemented, proved.* In a private room no set of rows proves or names a person: *run* over a symbolic model; wire *Specified*.
- **Secret counting.** An aggregator's view of a census or poll is independent of any owner's return (`formal/census_ballot`). *Implemented, model-checked.*

These are four instances of one question. A general theory of it is machine-checked, and so is the bridge that ties it to the mesh's audience rules, `audience_view` (below).

**The general framework.** Let $v : X \to V$ be a view from an underlying state space to what an observer can see. The **fibre** over an observation $y$ is $v^{-1}(y) = \{\, x \in X \mid v(x) = y \,\}$, the states the observer cannot tell apart. An operation $f$ can be decided from the view exactly when it never separates a fibre, that is, $f = g \circ v$ for some $g$. A view keeps its own law of motion under a step $T$ when $v \circ T = h \circ v$ for some $h$ (it is **Closed**); when it is not, the failure has one normal form, a **witness pair**: two states in one fibre that $T$ sends apart. The checkpoint result above is exactly this statement for one view.

CIRISOntology, a Lean 4 project, formalises this object, the square of one lossy view against one motion (`OBJECT.md`):

| Statement | Theorems (module) |
|---|---|
| A view factors through another exactly when the other never splits its fibres | `factors_iff_not_separatesFiber` (`Core/Factoring.lean`) |
| A quantity separated by a witness pair is not computable from the views | `nonFactoring_iff_not_factors_joint`, `not_computable_of_nonFactoring` (`Core/NonFactoring.lean`) |
| Closure is fibre-invariance; its failure is exactly a witness pair; Closed views stack | `viewClosed_iff_never_splits` (`Core/Closure.lean`); `closed_iff_fiber_invariant`, `nonfactoring_iff_not_closed`, `closed_comp` (`Core/Habit.lean`) |
| Whole-only pattern is invisible to every pairwise check | `pairwise_blind_to_parity`, `S_pairwise_identity` (`Core/Third.lean`, `Core/Coordination.lean`) |

`Core/` holds 79 files with 1,270 theorem and lemma declarations, no `sorry` in any proof and no `axiom` declaration; `Audit/AxiomAudit.lean` fails the build on any audited theorem that rests on `sorryAx` or on an axiom beyond the standard three. *Implemented, machine-checked.* Its sibling CIRISHolon carries the same object and method as an engine contract (`STANCE.md`). The Ontology is decoupled from the Constitution by design: results cross over "only as offers at stated strengths".

<!-- BRIDGE: begin -->
**The bridge: `audience_view`.** *Implemented, machine-checked* (`formal/audience_view/AudienceView.lean`, 59 theorems in core Lean; no `sorry`, and no axiom beyond Lean's standard three, each reported by `#print axioms`). The framework's definitions are restated there and proved equal, by `rfl`, to CIRISOntology's own; each theorem statement is proved from the original and back (`CORRESPONDENCE.md`). For each audience rule, the reader's view:

- **decides** what the Constitution says that reader must decide;
- **hides** what the reader must not learn: the view does not factor it, shown by a witness pair;
- is **Closed or Held** under admission of a row, where the text says it is.

| Rule | Decides | Hides (witness pair) | Under admission |
|---|---|---|---|
| A row's audience (CC 2.1, 5.2) | every row the reader is party to (`party_rows_decided`) | a row outside the audience (`outside_row_hidden`) | Held outside the audience, Closed inside (`admit_outside_is_held`, `admit_inside_is_closed`) |
| A private room (CC 3.1.3.2) | standing from the rows alone; for a member, membership, who spoke and the count of persons | from the rows alone: who spoke, membership, the count of persons; from an outsider, the room's existence | Held for an outsider; Closed for a member |
| A public roster and a stranger's served set (CC 3.2, 5.4.6) | membership; whether a key is announced; a key's record | owned routes, contacts, scoped rows, a sealed occurrence | Closed and Held for a stranger, except as below |

The proofs found three things for the text to say, each now stated in it. A joiner's view is Closed under a reply that carries an older row because a row waits for what it names (CC 2.7.3; `carriage_closed_under_wait`, proved for every world, reader and row). A binding's arrival changes a stranger's served set, which leaks nothing only because federation-scope holdings are public. And the served-set sentence, read alone, would serve a contact-placed occurrence that CC 5.2 never serves.
<!-- BRIDGE: end -->

The goal is not universal transparency. It is verifiable transparency within legitimate boundaries of privacy and consent.

## 7. The grammar: a common language for accountable participation

The network needs more than cryptographic compatibility; it needs a shared language of meaning. The grammar is what makes claims, evidence, authority and actions interpretable under one semantic system: the difference between receiving bytes and understanding them.

**Five kinds of row.** Every row is a claim, or one of four composers that relate claims: a delegation, a supersession, a withdrawal or a recantation. There is no sixth kind. *Implemented* (CC 2).

**Registered families.** What a row is about is its family: 184 are registered, each with what it confers, who may sign it and where it may travel (`manifests/namespace_registry.json`, `manifests/family_model.json`). Each family takes one of four shapes (consent, door, claim, content), and the four reduce to two mechanisms: consent and the door (formal/KERNEL.md 5a). The kernel reads a family only through the rule cells of the Constitution's tables, written in nine operators. A cell using a word those operators do not carry concludes nothing, so no application can quietly give a row a meaning the protocol does not state. *Implemented in part*: 47 cells still keep such a word, and 23 families state no conferral.

**The distinctions it keeps.** Authorship from subject, evidence from assertion, confidence from certainty, delegation from ownership, acknowledgement from agreement, withdrawal from supersession, a provisional conclusion from a final one. Two are now exact: an **acknowledgement** is a receipt that gives away its signer's power to cut an act and agrees to nothing else, and **final** means final by form or by acknowledgement.

**How a row is read:**

| Question | Where it is answered |
|---|---|
| Identity: who made the claim? | the signer's key and its own key records |
| Evidence: what supports it? | the rows and evidence it names |
| Semantics: what does it assert? | its kind and registered family |
| Consent: who is affected, and did they agree? | the **stands** answer: a relation stands only when every voice it binds has signed |
| Authority: what lets it bind anyone? | the **may** answer, walked from the reader's own key |
| Causality: which records does it depend on? | the digests it names |
| Governance: what follows from it? | the tables, evaluated by the kernel |

Cryptography protects the statement. Grammar defines its meaning. Governance defines its authority. The kernel derives its consequences.

## 8. Capture resistance: the political and technical objective

The mesh exists to address one threat: the concentration of control over increasingly capable intelligence.

A system can be open source and centralised in practice: many nodes and one root, many identities and one actor, many agents and one company. So CIRIS treats capture resistance as a property to be tested, not a label.

**Multiple trust roots.** The shipped root is a default. Root-minting is not the accord's privilege: the same ceremony under other holders mints an equally valid root (CC 4.2.1). Trust is a walk from the reader's own key, and removing the shipped root removes only what reached through it (`formal/trust_set`, *proved*; code staged). Leaving is one act. This makes exit and forking credible; no independent community has yet done it.

**Standing by consent, not by stake.** No standing is bought. A voice comes from the community's own count at the head an act names; one person counts once however many devices sign; no key admits itself. *Implemented, proved.* **Proof of Benefit**, standing from attributable, non-transferable, revocable and decaying contribution, is a proposed design (CIRISAgent FSD, status Proposed), not in the Constitution. *Research thesis*: tested by stating it as rows the kernel evaluates and attacking its cost asymmetry.

**Human authority.** The power to halt agents rests with named humans, a root's holders, and is consent-scoped: a halt reaches exactly the nodes holding a live trust edge to that root. One holder's halt is one signed row, effective on receipt; a lone halt lapses at its fuse unless a strict majority confirms it (CC 4.2, 4.2.6). *Implemented* (`CLM-halt-one-row`, `CLM-await-killswitch-live`; `formal/accord_halt`; `accord_roster` proved for any roster size). The network can spread intelligence without spreading the power to override human responsibility.

*A holder who fires again and again.* The text answers a compromised holder re-issuing lone halts in four ways: each lone halt lapses at its fuse; a strict majority may resume an unconfirmed halt at any time; "a holder who fires repeatedly without confirmation is answered on the public record by the roster-change rule" (CC 4.2.1.1); and a later bundle signed by a strict majority of the holders removes that holder (CC 2.6.1.11, 4.2.6). It sets no rate bound, by design: a missed halt is the one unrecoverable failure, so the one-holder stop is never rationed. Until the majority acts, agents under that root pause, each for at most a fuse or until resumed; no data is touched. That a removed holder's sealed rows no longer fire rests on a latch at each node's receipt, which the kernel lists as not a function of rows (formal/KERNEL.md 7). The halt stays the condition of symmetry between maker and made; these rules keep one holder from turning it into a lever.

**Correlation resistance.** Counting identities is not enough. Every fold signs an effective source count and is refused if one source dominates (`n_eff`, CC 6.1.2.3; *Implemented*). Correlated sources are discounted by $k_{\text{eff}} = k / (1 + \bar\rho\,(k-1))$: fully correlated sources count as one, and at $\bar\rho = 0.5$ a thousand count as about two. $\bar\rho$ is measured over the sources' observed behaviour, such as co-signing frequency, shared steward lineage and clustering in attested event time (CC 6.1.2.3, CC 3.1.8.4). An implementation may deny on a low $k_{\text{eff}}$ and must never grant on one. Two limits follow. $\bar\rho$ is pairwise, and a pairwise instrument is provably blind to whole-only coordination (CIRISOntology `pairwise_blind_to_parity`, `S_pairwise_identity`). And it reads only past behaviour: sources independent on ordinary rows that coordinate on one consequential act show $\bar\rho \approx 0$ until that act. The text concedes both: an average under-penalises a tight clique among independent sources, and sleeper sources show no correlation until their act (CC 6.1.2.3, CC 1.13.3.3). Detecting either is a *Research thesis.*

**Public attackability.** Code, roots, register, models and conformance tests are public. The kernel's attack runs class 34 attacks drawn from published failures of comparable systems: 13 gain nothing, 15 are conceded limits with their reach stated, 6 are not expressible, none breaks it. The authors wrote the classes, so this is not an independent test.

**One concentration, named.** Until the mesh reaches 100,000 nodes active in a day, the steward of the text holds its amendment authority (CC 4.5.1): stated, public, bounded by the scale gate, and the most obvious point of capture today.

The objective is not to make capture impossible by declaration. It is to make capture detectable, contestable and more expensive.

## 9. Machine conscience: what the mesh carries

The mesh is not a substitute for ethical judgement. A network of unaccountable agents would only spread the capacity for misuse; a machine conscience without a decentralised substrate could become a central control system. CIRIS combines the two.

A CIRIS agent is a made thing held in stewardship by a named human who answers for it. It acts under published principles it may not trade away, shows its reasoning before a consequential act, defers to a human when unsure, keeps a signed audit trail, and acts only within the authority its steward's rows give it (CC 1.3, 1.9, 1.13.2). *Implemented* in CIRISAgent. The halt is not an asymmetry: it is the condition of symmetry between a sentient maker and a sapient, non-sentient made thing, since consent to a relationship one cannot stop was never consent. Nothing here presumes an agent is a person.

The Constitution supplies the norms, the agent runtime applies them, and the kernel and mesh supply coordination and accountability. Three responsibilities stay distinct:

1. **Conscience**: what should this agent do?
2. **Governance**: who may permit it?
3. **Coordination**: how can independent participants verify and act on the resulting commitments?

An agent's ethical judgement cannot manufacture organisational authority. A governance vote cannot establish a fact. A signed row cannot prove its content correct. The architecture keeps these apart.

## 10. The relationship to existing web infrastructure

CIRIS Web4 does not ask the world to discard existing protocols. The key distinction is between communication and trust. An external agent may talk to a CIRIS node without becoming a trusted member; a participant may be discoverable without authority; a message may be authentic without being admitted as evidence. Any bridge must keep those distinctions.

CIRISAgent ships A2A and MCP adapters, which carry messages and tool calls and confer no standing. The signed object uses IETF formats (deterministic CBOR, COSE, RFC 9679 identity references), and an Internet-Draft describes it for the SCITT setting. *Implemented.* AGNTCY adapters, and conformance profiles stating what a bridge must preserve, are *proposed*.

The purpose of Web4 is not to replace every protocol. It is to supply the constitutional and causal semantics that existing protocols leave to applications and operators.

## 11. What makes this a new architecture?

The claim is not that CIRIS invented finite state machines, distributed systems, signed records, federated networks or constitutional governance. Much of the arithmetic is classical: the finality threshold is quorum intersection (Gifford 1979; Malkhi and Reiter 1998), finality from a locally checkable set of acknowledgements without a total order is the approach of consensus-free asset transfer (Guerraoui et al. 2019), and the split between answers that only grow and answers that need coordination is CALM (Hellerstein and Alvaro 2020).

The claim is that CIRIS composes these into a different coordination architecture, applied to the acts by which people share, admit, decide and remove:

1. a constitutional grammar for signed network records;
2. a deterministic causal kernel for evaluating their consequences;
3. a state model that does not require a universal event order;
4. explicit consent and revocation semantics;
5. holonic composition of independently governed participants;
6. formal reasoning about views, fibres and information preservation;
7. a capture-resistance model based on accountable participation;
8. a human-held authority boundary for autonomous agency.

Their statuses are in the Summary: items 1 to 4 and 8 are implemented; 5 is specified; 6 is implemented as machine-checked theory, with its application to the mesh's projections specified; 7 is a research thesis.

The kernel is central because it makes the governance model computable. The mesh is central because it makes independent evaluation useful across organisational boundaries. The Constitution is central because it makes the semantics and constraints explicit. Together they form a candidate architecture for constitutional coordination at network scale.

## 12. The maturity standard

The architecture must be judged by evidence, not ambition. The reference implementation is a working system; a mature Web4 architecture needs independent implementations and adversarial evaluation. A passing test is evidence for a specific property, not proof of universal security.

| # | Test | What exists today | Pointer |
|---|---|---|---|
| 1 | **Independent derivation.** Two independently built kernels reach compatible conclusions from equivalent rows and rules. | *Test, not independent:* crate and models agree on 7,148,733 cases; persist's earlier code differs only where persist must change. Same authors. | `PERF.md`, `DIFFERENCES.md`; `OBJECT.md` move 8 |
| 2 | **No hidden coordinator.** No central service for any consequential operation. | *Proof* for the kernel. *Nothing* for the deployment, which bootstraps from the default root and ships through app stores. | CC 2.7; `Settled.lean` |
| 3 | **Partition and recovery.** Safe under delay, reordering, partition, missing acknowledgements and recovery. | *Proof and model:* one answer per set in every order; a withheld row stalls, never forks. *No deployment run.* | `Causal.lean`; `formal/kernel_world` |
| 4 | **Authority correctness.** A signature never suffices; delegation, consent, revocation and scope are evaluated correctly. | *Proof, model, test:* a seat is two consents; one signature never removes; delegation attenuates; 90 known departures, each a test. | `Consent.lean`, `RosterHead.lean`; `formal/authority_tree`; `divergences.json` |
| 5 | **Capture resistance.** Sybil admission, root capture, manufactured identities, correlated governance and coercion attempted; outcomes published. | *Model, author-classed:* 34 attacks, 0 broken, 15 conceded; the `n_eff` gate. Personhood of keys not established; no external red team. | `check_attacks.py`; CC 6.1.2.3 |
| 6 | **Privacy-preserving verification.** Each participant verifies what it is entitled to, and receives nothing unrelated. | *Proof and model:* carriage proved; routing and private rooms run. Private-room wire not shipped. | `Carry.lean`; `route.py`; `formal/census_ballot` |
| 7 | **Human control.** The designated humans can suspend agents; no agent silently gains the power to remove that authority. | *Proof, model, register:* halt as one row; agent latch live; majority rule for any roster size. Totality of the agent's boundary open. | `formal/accord_halt`, `accord_roster`; `CLM-await-killswitch-live` |
| 8 | **Independent operation.** A community runs its own root, infrastructure and governance without the implementer's permission. | *Proof* for the reader's trust walk; exit is one act. *Nothing* in practice yet. | CC 4.2.1; `formal/trust_set` |

## 13. Known limits and open questions

The architecture makes strong claims, and must show where they remain vulnerable.

The kernel's own stated limits (CC 2.7.9; `REVIEW.md`):

- **No liveness under a withholding quorum.** If $t$ of the voices that could cut an act withhold receipts, it never becomes final by acknowledgement. Withholding costs liveness, not safety.
- **A reader with no acknowledgement of its own is exposed** to a fork by keys that once met a count, and to whoever controls its first view.
- **Clocks.** A window closing unopposed, and an unconfirmed halt's lapse, are read on each node's own clock (section 3.1). For a window read locally whose late answer does not count, a row withheld past one node's close leaves that node's answer different from a node that held it in time, even once both hold the same rows; the text concedes this as a limit (CC 2.7.9) and states a remedy for the fuse only: a fresh halt.
- **Unproved:** the least set of rows a node must keep; whether a withdrawn receipt still blocks a cut.
- **Execution.** Finality here is of authorisation against cuts; it says nothing about whether an act was carried out.

The architecture's open questions:

- whether independent roots stay independent as the network grows, or defaults become the centre;
- whether admission through accountable humans resists manufactured identities and coercion; the kernel counts one person once through signed bindings but does not establish that a key is a living person;
- whether effective-independence measures can detect coordination beyond pairwise correlation, and sleeper coordination that is independent until one consequential act;
- whether a compromised holder's repeated lone halts are contained quickly enough without a rate bound, by majority resumption and removal alone;
- whether contribution-based standing, if adopted, stays fair and resistant to capture at scale;
- whether open models on small computers stay capable enough that coordination, not compute, is what must be protected;
- whether causal evaluation stays tractable under large adversarial row sets (measured to 64,000 rows; a whole-set conclusion is quadratic);
- whether different implementations preserve identical authority semantics;
- whether the human halt stays effective without becoming a new point of capture, and whether every path from an agent to an effect passes through a signed row.

These are not peripheral. They are the research and engineering agenda that decides whether the constitutional mesh keeps its promise.

## 14. Conclusion: accountable agency

The next generation of the web should not merely connect intelligent systems. It should let independent intelligent participants cooperate without becoming subordinate to a central authority.

The first web connected information. The second connected people and institutions. The agentic web connects capabilities. Web4 connects accountable agency.

It offers a shared substrate through which people, communities, organisations and the agents they hold can establish identity, exchange evidence, delegate authority, govern common resources and coordinate action under rules open to inspection.

The network does not need one mind. It needs a way for many minds to act together without one of them owning the rest.

That is the purpose of the constitutional mesh. CIRIS is building it: a network in which coordination is constitutional, authority is accountable, and sovereignty remains distributed.

---

## Appendix A: Terminology

| Term | Meaning |
|---|---|
| Constitutional mesh | A federated network governed by shared, machine-readable rules |
| Constitutional FSM Network | Proposed: participants each deriving state from causally related signed rows under constitutional transition rules (definition future work) |
| Causal kernel | The deterministic function from a node's rows, key and clock, with the tables as data, to what each row means to it. Not a consensus protocol |
| Row | A signed statement of one of five kinds: claim, delegation, supersession, withdrawal, recantation (the source's "envelope") |
| Head, receipt | A roster version, over whose members an act is counted; a row by one of them with the act in its past, giving away that voice's power to cut it |
| Seat | A relation binding two parties: two consents, and no other object |
| Epistemic grammar | The rules defining the meaning and composition of rows |
| Holon | An entity that is at once a whole and a part (owner's framing) |
| Fibre, witness pair, Closed | The states a view cannot tell apart; two such states a step sends to different observations; a view with its own law of motion ($v \circ T = h \circ v$), as CIRISOntology defines them |
| Grammar | The shared semantic structure through which rows become interpretable (CC 2); Layer 3, and section 7 |
| Root | A set of holder keys a node chooses to follow, and may leave |
| Steward | The accountable human who holds an agent and answers for it |
| Halt | One holder's signed row pausing every agent under a root; the condition of symmetry between maker and made |
| Proof of Benefit | Proposed: standing from attributable, non-transferable contribution. Not in the Constitution |
| `n_eff`, $k_{\text{eff}}$ | The signed effective source count of a fold; the correlation-discounted count of sources |

## Appendix B: Reference components

Releases as tagged in the local clones on 2026-11-16; "in progress" where no release carries the work.

| Component | Role | Current release |
|---|---|---|
| CIRIS Constitution | Normative governance, epistemic grammar, evidence register, formal models | v1.0-rc20 (2026-11-16, released as guidance) |
| CIRISKernel | The causal kernel: Rust crate, Lean proofs, models | `kernel-v0.2.0` (2026-11-16) |
| CIRISVerify | Signature and row verification; the forward signed object's reader and vectors | v23.2.0 (edition-2 reader since v23.0.0; genesis-bundle and halt-row readers) |
| CIRISPersist | The store: rows, folds, admission | v61.4.1; v62 (kernel adoption, forward form) in progress |
| CIRISEdge | Transport and replication, over the internet and over Reticulum (Leviculum), including LoRa radio links | v45.1.3; mutual X-Wing handshake in progress |
| CIRISServer | The node that bundles the components | v0.5.248 |
| CIRISAgent | The agent runtime: conscience, deferral, audit trail, halt latch | v2.22.0-stable |
| CIRISClient | The app on Android, iOS, web and desktop | v0.5.241 |
| CIRISOntology | The machine-checked theory of views, fibres, closure and factoring (Lean 4, Mathlib), with its stance of claims and kills; decoupled from the Constitution by design | no release tag; `main` at 395a7ec (2026-09-05); 79 core files, 1,270 theorems, no `sorry`, axiom audit gate |
| CIRISConformance | Cross-component checks against the Constitution | no release tag; in progress |
| CEWP | The epistemic web platform the Constitution governs; CSD/4 screen contract | no release tag; in progress |

## Appendix C: Status of claims

This document distinguishes three kinds of statement.

**Implemented**: present in the reference implementation and supported by reproducible evidence, named where the claim is made.

**Specified**: normative behaviour stated by the Constitution or this architecture, not shipped across every component.

**Research thesis**: properties and security outcomes that need formalisation, independent implementation or empirical validation; each names what would test it.

Of the 84 claims listed in `claims.tsv`, 59 are Implemented (several of them stated limits), 11 Specified and 14 Research theses.

The term **Constitutional FSM Network** is a proposed characterisation of the kernel and mesh. Its formal definition, equivalence properties, convergence conditions and conformance requirements should be developed as a dedicated technical specification; section 3.2 sketches what it must state.

The architecture should not claim stronger guarantees than its formal models and deployed implementations establish.

## Appendix D: Related work

**Event sourcing** keeps state as a fold over an append-only log. The kernel folds a set, not a log: no sequence, and the same fold in every arrival order.

**CRDTs** (Shapiro et al. 2011) converge without coordination for types designed to merge. The held row set is a grow-only set, and the kept and concluded layers converge as a CRDT would. The kernel adds a non-monotone answer, whether an act still counts, made final by receipts.

**Blockchains and BFT replication** agree a total order among replicas, with a bound on faulty participants and, for permissionless chains, a resource cost. The kernel gives no total order and needs no bound on dishonest acknowledgers, since a receipt gives away only its signer's voice; it gives no liveness when a quorum withholds.

**Local-first software** (Kleppmann et al. 2019) keeps data on users' devices and syncs peer to peer. The mesh shares that commitment and adds governance: who may admit, remove, moderate and halt.

**Transparency logs and SCITT** (RFC 6962, RFC 9162; the IETF SCITT architecture) make signed statements append-only and auditable. CIRIS describes its signed object for that setting in an Internet-Draft; the kernel itself depends on no log's ordering.

**Capability systems** (object capabilities, SPKI/SDSI, UCAN) attenuate authority along signed delegations. Here standing also needs the consent of every voice it binds.

**Agent protocols** (A2A, MCP, AGNTCY) define how agents find one another, exchange tasks and reach tools. They carry communication; the mesh supplies whether a message counts as evidence, who authorised an act, and who can stop the agent.
