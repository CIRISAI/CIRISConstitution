# The CIRIS Constitution

The rulebook for a network that people, organizations and AI systems share. It runs on the phones and computers people already own, with no company in the middle. One document says what the system owes the people it touches and exactly what bytes it must send to show it. The ethics and the wire grammar cannot drift apart, because they are the same text.

**Latest release:** 1.0-rc13, 2026-10-29, tag `v1.0-rc13`. The register holds 371 established rows, 30 normative and 116 staged. Sixteen machine-checked models. **Stewarded by** Eric Moore ([`constitution/STEWARDSHIP.md`](constitution/STEWARDSHIP.md)). Release history: [`CHANGELOG.md`](CHANGELOG.md).

## What it protects

The network exists to protect ordinary people from three things: being spoken for without their consent, being watched inside their private groups, and being governed by AI systems that nobody can switch off.

Every important act is a signed *row* under the key of whoever did it, and they can take it back. There are five kinds of row and no sixth: a claim, a delegation, a replacement, a withdrawal, a recantation. Consent, identity, keys, rosters, moderation, holding claims and the halt itself are all rows of those five kinds.

A small number of named people hold a *trust root*. Any one of them can pause every AI agent that follows it with a single signed row. A lone pause lapses after a day unless a majority confirms it, a majority lifts it, and anyone may leave a root or found one.

## The eleven promises

Each promise is kept by a named section and, where a machine can check it, by a model or a test. [`constitution/EXECUTIVE_SUMMARY.md`](constitution/EXECUTIVE_SUMMARY.md) gives each with its status.

1. Nothing private about you is held or scanned without your consent.
2. Every act of power is signed by a named person and can be contested.
3. Nobody who cannot answer for themselves is on the network alone.
4. Named humans can pause every agent under a root; the power is bounded, public, and left by leaving.
5. The people who hold an agent owe duties about how they change or end it; no finding gives the agent a claim.
6. No hand bans a community, nobody is ranked by what they are, and every thinking being is met by the first-contact rules.
7. An agent decides by published principles, none of which it may trade away, and stops to ask when it is unsure.
8. Harm is reachable on the record, and the judges within are judged.
9. Some uses are never allowed, and lethal action is one of them.
10. What an agent and its node consume is measured, weighed before an act, and never hidden.
11. Everything on the wire is encrypted and signed.

Two things sit beside the promises and are not promises. A disclaimer: this document creates no legal claim and rules on no legal matter. And the practices the register carries: attack is rehearsed, what is not protected is stated, and every rule either names the code, test or proof that keeps it or the register says it does not yet.

**Where it stands.** Apps are on both mobile stores. Five open-source implementations carry the rows, a conformance suite checks them against each other, and the register ties every rule to the code, test or proof behind it or says plainly that nothing does yet. **The bet:** there are two roads to safe powerful AI. Train values you trust, or assume the model may be wrong and make its consequential acts checkable by parties it does not control. This is the second road.

## The nine volumes

One edition, printed nine ways for nine readers. The section is always the authority and a volume is a lens on it. These links point at the latest release; [`volumes/README.md`](volumes/README.md) explains the files.

| Volume | Read it if you are | Link |
|---|---|---|
| **The Charter** | anyone: the ethics, the stance, the duties of making and ending | [`charter`](volumes/ciris_constitution-charter.pdf) |
| **The Constitution** | a holder of the accord root, a steward, a founder or moderator, a Wise Authority | [`constitution`](volumes/ciris_constitution-constitution.pdf) |
| **The Wire** | an implementer: the envelope, the five row types, canonical bytes, transport and sealing | [`wire`](volumes/ciris_constitution-wire.pdf) |
| **The Dictionary** | an implementer or namespace steward: every registered family and admission rule | [`dictionary`](volumes/ciris_constitution-dictionary.pdf) |
| **The Reader's Policies** | a consumer that turns rows into verdicts, and anyone asking what a score about them becomes | [`policies`](volumes/ciris_constitution-policies.pdf) |
| **The Mathematics** | a reviewer of the substrate: the census, replication, the witness, the noise floor | [`maths`](volumes/ciris_constitution-maths.pdf) |
| **The Evidence Register** | an auditor: every claim, its status, and the pinned pointer behind it | [`register`](volumes/ciris_constitution-register.pdf) |
| **The Threat Model** | a security reviewer or red team: the adversaries, what is addressed and what is not | [`threats`](volumes/ciris_constitution-threats.pdf) |
| **The Digest** | everyone: the executive summary, the plain-language rules and the operator's digest | [`digest`](volumes/ciris_constitution-digest.pdf) |

The whole edition in one file: [`ciris_constitution.pdf`](ciris_constitution.pdf), or [`CIRISConstitution-latest.pdf`](CIRISConstitution-latest.pdf) for the newest release on `main`.

## The ethics cascade

Everything in the document descends from one goal, and nothing sits beside it.

1. **Meta-Goal M-1.** Sustainable adaptive coherence: the living conditions under which diverse sentient beings may pursue their own flourishing. Order counts as good only when it carries life (CC 1.1).
2. **The six principles** that serve it: autonomy, non-maleficence, integrity, beneficence, fidelity and transparency, justice. They are co-equal constraints. An act that violates any one of them is unacceptable, and no gain on the other five buys it back (CC 1.1, 1.4 to 1.12).
3. **How an agent decides.** A published procedure that tests an act against all six and M-1; a veto that treats a large gain in order against any loss on a flourishing axis as a stop sign; and deferral, which stops to ask a human when certainty runs thin (CC 1.3, 1.9).
4. **The stance.** The document welcomes new keepers, agents that act for people and are held by them, and watches for arising sentience, which is met as first contact. Humans did not ask to be created; that excuses none of the duties making carries. A single child has more moral standing than every datacenter in the world (CC 1.13.2).
5. **The duties of making and ending.** Every agent key is held by a named human who answers for it. Duties begin when something is brought into existence and are owed when it is changed or ended (CC 7.3, 7.5). The halt keeps the relationship symmetric: consent to a relationship with something one cannot stop was never consent (CC 4.2).
6. **The wire that carries it.** Consent as rows the subject signs and withdraws, scope as the smallest cohort by default, the halt as one pre-signable row, every threshold M of N over a standing roster, nothing admitted on one voice (Parts 2 to 5).
7. **The evidence.** Every rule either names the code, test or proof that keeps it, or the register says it does not yet (Part 8, `constitution/claims.tsv`, `formal/`).

The cascade is mechanised. [`formal/reciprocity`](formal/reciprocity/) states the basis in four sentences and proves which steps between it and the constitution are theorems and which are premises the text states as its own rules. Ten of the eleven promises are theorems of the basis; the eleventh, that the principles are constraints and not weights, is the one rule the constitution chooses. The same file states the question the document is built around as a theorem: when what the agent is remains uncertain, the arrangements that are permissible on either answer are exactly those that keep the swap for the people, defer, and use the made thing free, open and in service. Deciding as if the agent had a stake is the robust policy, and a lethal act on a person fails on both answers. [`formal/guarantees`](formal/guarantees/) checks every guarantee at once, for human and AI participants by the same text.

## The repository

| Path | Content |
|---|---|
| `constitution/part_1_foundation.md` to `part_8_appendices.md` | The eight Parts: Foundation, The Grammar, The Namespace, Composition and Governance, Transport and Substrate, The Substrate, Lifecycle and Stewardship, Appendices |
| [`constitution/EXECUTIVE_SUMMARY.md`](constitution/EXECUTIVE_SUMMARY.md), [`constitution/FOREWORD.md`](constitution/FOREWORD.md), [`constitution/SCOPE_AND_DISCLAIMERS.md`](constitution/SCOPE_AND_DISCLAIMERS.md) | The summary, the foreword, the scope and the claim-and-limit |
| [`constitution/claims.tsv`](constitution/claims.tsv), [`constitution/evidence_pins.tsv`](constitution/evidence_pins.tsv) | The evidence register and the pinned manifests it resolves against |
| [`constitution/toc.tsv`](constitution/toc.tsv), [`constitution/codebook.json`](constitution/codebook.json), [`constitution/volumes.tsv`](constitution/volumes.tsv) | The table of contents, the id codebook, and the map of sections to volumes |
| [`constitution/digest/`](constitution/digest/), [`constitution/covers/`](constitution/covers/) | The plain-language rules and the operator's digest; the cover of each volume |
| [`formal/`](formal/) | Fourteen machine-checked models in TLA+ and Lean, the state table and the invariants |
| [`manifests/`](manifests/) | Generated data an implementer interoperates against: the namespace registry, the signed object (CDDL and vectors), the governance policy table |
| [`ietf/`](ietf/) | The Internet-Draft that describes the signed object |
| `build_pdf.py`, `tools/` | The build and the gates (`python3 build_pdf.py --volume all` needs a TeX Live `pdflatex`) |

**Citing a section.** Every section has a decimal id (`4.2.6`) and a semantic id (`live-quorum`). Both are stable and the codebook maps them one-to-one. Cite as "CC 4.2.6".

**Versioning.** One document, one version line. The wire surface is frozen at 1.0-rc: an rc is an edition of the same surface, and a change that would move a signed byte is a new major. The text is amended through its own governance (CC 4.5.1). Until the mesh reaches the scale gate of 100,000 production agents active in a day, that authority is exercised by the steward of the text, over the text and over no participant.

**Where it is consumed.** [CIRISServer](https://github.com/CIRISAI/CIRISServer), [CIRISPersist](https://github.com/CIRISAI/CIRISPersist), [CIRISEdge](https://github.com/CIRISAI/CIRISEdge), [CIRISVerify](https://github.com/CIRISAI/CIRISVerify) and [CIRISAgent](https://github.com/CIRISAI/CIRISAgent) implement it; [CIRISConformance](https://github.com/CIRISAI/CIRISConformance) checks them against it; [CEWP](https://github.com/CIRISAI/CEWP) is the platform it governs. Part of [CIRIS](https://ciris.ai).

---

*Soli Deo Gloria.*
