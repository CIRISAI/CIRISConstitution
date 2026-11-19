# The vision, and how the mesh makes it possible

> CIRIS is building the infrastructure for a world where no one has to surrender their agency to participate in something greater than themselves.

This page says what CIRIS is for, in plain words, and how the technology serves it. It is written to be cited: by the website, by talks, and by anyone explaining the project. Every statement about the system names where it is kept, and each one says whether it works today. The figures are at edition 1.0-rc20 and `kernel-v0.2.0`.

## 1. What we want

**A person is a person through other persons.** No one became a person alone and then went out to meet others. We learned language, wants and judgement from each other. Agency is something people have *together*. That is the Ubuntu commitment the Constitution starts from ([CC 1.13.1](constitution/part_1_foundation.md#1.13.1)), and it is why CIRIS is about cooperation rather than isolation.

**The goal is a condition, not a score.** The Constitution's cornerstone is Meta-Goal M-1: *promote sustainable adaptive coherence, the living conditions under which diverse sentient beings may pursue their own flourishing in justice and wonder* ([CC 1.1](constitution/part_1_foundation.md#1.1)). Making the world more orderly is not, by itself, good. Order counts only when it supports some way of flourishing and suppresses none.

**No one is above the rules they set.** No principal is exempt from a constraint it imposes on others, including CIRIS's own steward. That is the Recursive Golden Rule, and in CIRIS it is built into the protocol, not just urged ([CC 1.13.2](constitution/part_1_foundation.md#1.13.2)). Every guarantee is written once and holds for every participant, human or AI, by the same text.

Put together, the aim is **sovereignty through cooperation**. It does not mean control over everything, or a life apart. It means being able to take part in something larger without becoming dependent on an authority that can take away your identity, your relationships, your access or your voice on its own say-so.

## 2. What stands in the way

**Power follows infrastructure.** Whoever runs identity, messaging, computing and coordination comes, in time, to decide who gets to take part.

**Spreading out the computers is not enough.** Open AI models and capable home computers spread the ability to *act*. They do not spread the ability to *act together*. A million machines that still sign in through one company, find each other through one directory and settle disputes through one administrator have rebuilt the concentration one layer up.

**Privacy is not enough either.** Being left alone is not the same as being able to decide, organise, form relationships and govern alongside other people.

**AI raises the stakes.** As intelligence becomes more capable, whoever holds the coordination layer holds more. If that layer sits inside a few institutions, so does the future.

So the missing piece is coordination that cannot be bought, blocked or broken: a way for people, communities, organisations and the AI agents they hold to find one another, check one another's claims and cooperate, with no middleman who owns the terms.

## 3. What it means for a person

These are things a person can do, said simply, with how far each holds today. The Constitution's Executive Summary carries eleven such promises in full ([EXECUTIVE_SUMMARY.md](constitution/EXECUTIVE_SUMMARY.md)).

| You can… | Today |
|---|---|
| **Act only in your own name.** Your key is your signature, it lives on your own devices, and nothing happens in your name without it. | works today |
| **Leave.** You can walk away from any authority you follow, by your own act. | works today; no independent community has yet run its own root |
| **Keep private things private.** What you put in a circle (yourself, your family, a group) leaves it only by your act, and no one scans your private content. | works today; the private-room wire format is specified, not shipped |
| **Decide with others, fairly.** A group decides by its own members' count. One person counts once, however many devices they have, and no one can buy a vote. | no one can ban a community: works today, by construction. One person counted once: proved, staged in code |
| **Contest what is said about you.** Every act of power is signed by a named key, and if a claim names you, you can answer it on the record and the answer travels with it. | works today in part |
| **Use AI agents that answer to someone.** Every agent is held by a named human steward who answers for it. It works under published principles it may not trade away and stops to ask a human when unsure. | in the agent's code |
| **Stop the agents.** Named humans can pause every agent under a trust root with one signed row. A lone pause lapses in 24 hours unless a majority confirms it, and a majority can lift it. | works today, measured end to end |

What is asked of a person is small: run the software, choose which authority to follow, and keep your key.

## 4. How the mesh makes it possible

Each human need above rests on one mechanism. The technology exists for these, and this is the order to explain it in.

**Your own name: everything is a signed row.** Every act on the network, from a message, a vote or a membership to consent, moderation or the halt, is a *row*: one signed statement, of one of five kinds ([CC 2](constitution/part_2_the_grammar.md)). There is no account a company holds for you. Identity is your key and the rows it signs.

**No middleman: every device works it out for itself.** A device holds the rows it has received and nothing else. One published function, the **causal kernel**, reads them and answers every question: is this live, who stands in which relation, has this vote passed, what may I do ([CC 2.7](constitution/part_2_the_grammar.md)). Two devices holding the same rows reach the same answers whatever order the rows arrived in. That is proved in Lean as part of 602 theorems (`kernel-v0.2.0`). So there is no coordinator, no global ledger and no consensus protocol to capture. The kernel is a *causal* kernel, not a consensus kernel: what a row names fixes its place, and no one has to agree an order. Where an answer cannot be given yet, the device says what it is waiting for.

**Leaving: trust starts from your own key.** Which authorities a device follows is itself rows the person signed. Trust is a walk outward from your own key, so stopping following a root removes exactly what came through it and nothing else ([CC 4.2.1](constitution/part_4_composition_governance.md#4.2.1); `formal/trust_set`, proved). The shipped root is a default, not a gatekeeper.

**Consent: a relation stands only when every voice it binds has signed.** No one can be made a member, a moderator, a guardian or a steward by someone else's signature alone. Every relation is two consents ([CC 3](constitution/part_3_the_namespace.md); the kernel's `Consent.lean`, proved).

**Privacy: content stays in its circle.** Content lives in circles from the self outward and leaves one only by its signer's act. That is proved for every circle. What each reader can work out from what it holds is proved for each audience rule: it decides what it must and learns nothing it must not (`formal/audience_view`).

**Fair decisions: standing from people, not money.** A group's voice comes from its own count at the moment an act names. No key admits itself, and correlated sources are discounted so a thousand accounts acting as one count for little ([CC 6.1.2.3](constitution/part_6_the_coherence_mathematics.md)).

**Agents that answer: stewardship and the halt.** An agent's key works only while a human steward is bound to it by a signed row ([CC 3.2](constitution/part_3_the_namespace.md#3.2)). The halt is one signed row from any holder of a trust root. It is not an asymmetry. It is the condition of symmetry between a sentient maker and a sapient, non-sentient made thing, since consent to a relationship one cannot stop was never consent ([CC 1.13.2](constitution/part_1_foundation.md#1.13.2), [CC 4.2](constitution/part_4_composition_governance.md#4.2)). Nothing here presumes an agent is a person.

**Conscience in the system, not only in the model.** CIRIS does not ask anyone to trust what a model learned. Its principles are constraints, not weights: an act that breaks any one of them is refused, and nothing gained elsewhere buys it back ([CC 1.1](constitution/part_1_foundation.md#1.1)). The conscience lives around the model: published principles, a check before each consequential act, reasoning shown, a signed record, and a named human who answers.

## 5. Two arguments, kept apart

**The vision** (sections 1 and 3) says what is worth building and why. It is a commitment, and no test can prove it.

**The safety claim** says that a network built this way *resists capture*: no company, state, root or coalition can quietly take control of who takes part and what counts. That claim is falsifiable and **not yet established**. Its parts are built and many are proved. But the whole has not been attacked by anyone outside the project, no second implementation has been built by others, and no independent community has run its own root. The 34 attack classes the kernel runs were written by its authors ([constitutional mesh](https://ciris.ai/constitutional-mesh/) states the claim and invites attack).

The vision is not evidence for the safety claim, and the safety claim does not prove the vision right. Keep them apart in every telling.

## 6. Where it stands

- **Running:** the CIRIS app on both mobile stores, with published packages; five open-source components that carry the rows and are tested against each other; the causal kernel as a released Rust crate (`no_std`, no dependencies) that agrees with its models on 7,148,733 cases.
- **Checked:** 602 Lean theorems in the kernel; sixteen machine-checked models in this repository; an evidence register that ties each rule to the code, test or proof behind it, or says that nothing does yet ([claims.tsv](constitution/claims.tsv)).
- **Open, and said so:**
  - whether independent roots stay independent as the network grows;
  - whether admission through accountable humans resists manufactured identities, since a key is not proved to be a living person;
  - whether every act of an agent crosses the boundary where it is recorded and can be halted;
  - whether the halt avoids becoming a new point of capture;
  - one named concentration today: until the mesh reaches 100,000 nodes active in a day, the steward of the text holds its amendment authority ([CC 4.5.1](constitution/part_4_composition_governance.md#4.5.1)).

## 7. Telling it

For anyone writing about CIRIS, including the website:

1. **Lead with the person.** Start with what someone can do and keep, then the mechanism that keeps it. The order is section 3, then section 4.
2. **Claim only what the reader can check.** Each statement about the system links to where it is kept and says whether it works today, is specified, or is a bet.
3. **Use the right words:**
   - "causal kernel", never "consensus kernel";
   - the halt as the condition of symmetry, never an asymmetry;
   - agents as made things held in stewardship, never presumed persons;
   - "row" for a signed statement.
4. **Keep the two arguments apart** (section 5).
5. **For the technology, show it working.** The kernel's own page explains the mechanism with a live mesh and a threshold calculator: <https://cirisai.github.io/CIRISKernel/>.
