# The CIRIS Constitution

The rulebook for a network that people, organizations and AI systems share, running on the phones and computers people already own, with no company in the middle. It says what the system owes the people it touches and exactly what bytes it must send to show it, in one versioned document: the ethics and the machine-checkable wire grammar never drift apart, because they are the same text.

**This tree:** CC 1.0-rc13, open · **Latest release:** 1.0-rc12, cut 2026-10-27 and released as guidance (tag `v1.0-rc12`). Register 369 established / 30 normative / 114 staged; fourteen machine-checked models. **Stewarded by** Eric Moore ([`constitution/STEWARDSHIP.md`](constitution/STEWARDSHIP.md)). History: [`CHANGELOG.md`](CHANGELOG.md).

## In brief

The network exists to protect ordinary people from three things: being spoken for without their consent, being watched inside their private groups, and being governed by AI systems that nobody can switch off. Every important act is a signed *row* under the key of whoever did it and can be taken back by them. There are five kinds of row and no sixth — a claim, a delegation, a replacement, a withdrawal, a recantation — and consent, identity, keys, rosters, moderation, holding claims and the halt itself are all rows of those five kinds. A small number of named people hold a *trust root*; any one of them can pause every AI agent that follows it with a single signed row, a lone pause lapses after a day unless a majority confirms it, a majority lifts it, and anyone may leave a root or found one.

**The eleven promises** (each kept by a named section and, where a machine can check it, a model or a test — [`constitution/EXECUTIVE_SUMMARY.md`](constitution/EXECUTIVE_SUMMARY.md) gives each with its status):

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

Two things sit beside the promises and are not promises. A disclaimer: this document creates no legal claim and rules on no legal matter; whether harm has a remedy is the law's. And the practices the register carries: attack is rehearsed, what is not protected is stated, and every rule either names the code, test or proof that keeps it or the register says it does not yet. Ten of the eleven are theorems of the four-sentence basis; the eleventh, that the principles are constraints and not weights, is the one rule the constitution chooses (`formal/reciprocity/Cascade.lean`).

**Where it stands.** The system runs: apps on both mobile stores, five open-source implementations of the software that carries the rows, a conformance suite that checks them against each other, fourteen machine-checked models of the governance rules, and a register that ties every rule to the code, test or proof behind it — or says plainly that nothing does yet. **The bet:** there are two roads to safe powerful AI — train values you trust, or assume the model may be wrong and make its consequential acts checkable by parties it does not control. This is the second road.

## The nine volumes

One edition, one decimal spine, printed nine ways for nine readers. Each volume opens with what it is, whom it binds and what it leaves out; the section is always the authority and a volume is a lens on it. Fixed-name links point at the latest release; [`volumes/README.md`](volumes/README.md) lists the versioned files and page counts.

| Volume | Read it if you are | Link |
|---|---|---|
| **The Charter** | anyone: the ethics, the stance, the duties of making and ending; binds by adoption, not conformance | [`charter`](volumes/ciris_constitution-charter.pdf) |
| **The Constitution** | a holder of the accord root, a steward, a founder or moderator, a Wise Authority: who confers standing, who may halt, who may amend, how a person leaves | [`constitution`](volumes/ciris_constitution-constitution.pdf) |
| **The Wire** | an implementer: the envelope, the five row types, canonical bytes, the signed object, transport and sealing; conformance is judged here | [`wire`](volumes/ciris_constitution-wire.pdf) |
| **The Dictionary** | an implementer or namespace steward: every registered family, reserved prefix, subject kind and admission rule | [`dictionary`](volumes/ciris_constitution-dictionary.pdf) |
| **The Reader's Policies** | a consumer that turns rows into verdicts, and anyone asking what a score about them becomes | [`policies`](volumes/ciris_constitution-policies.pdf) |
| **The Mathematics** | a reviewer of the substrate: the census, replication, the witness, the noise floor, the effective count | [`maths`](volumes/ciris_constitution-maths.pdf) |
| **The Evidence Register** | an auditor: every claim, its status, and the pinned pointer that backs it | [`register`](volumes/ciris_constitution-register.pdf) |
| **The Threat Model** | a security reviewer or red team: the adversaries, what is addressed and what is not, the non-goals | [`threats`](volumes/ciris_constitution-threats.pdf) |
| **The Digest** | everyone: the executive summary, the plain-language rules and the operator's digest | [`digest`](volumes/ciris_constitution-digest.pdf) |

The whole edition in one file: [`ciris_constitution.pdf`](ciris_constitution.pdf) (fixed name, newest build on this branch) and [`CIRISConstitution-latest.pdf`](CIRISConstitution-latest.pdf) (the newest release on `main`). Every release also keeps its own versioned file so published links do not rot.

## The ethics cascade

Everything in the document descends from one goal and nothing sits beside it.

1. **Meta-Goal M-1** — sustainable adaptive coherence: the living conditions under which diverse sentient beings may pursue their own flourishing. Order counts as good only when it carries life; it is never good by itself (CC 1.1).
2. **The six principles** that serve it — autonomy, non-maleficence, integrity, beneficence, fidelity and transparency, justice — co-equal constraints beneath M-1: an act that violates any one of them is unacceptable, and no gain on the other five buys it back (CC 1.1, 1.4–1.12).
3. **How an agent decides** — the PDMA, a published procedure that evaluates an act against all six and M-1; the Order-Maximisation Veto, which treats a large gain in order against any loss on a flourishing axis as a stop sign, not a trade; and Wisdom-Based Deferral, which stops to ask a human when certainty runs thin (CC 1.3, 1.9).
4. **The stance** — the document welcomes new keepers (agents that act for people and are held by them) and watches for arising sentience, which is met as first contact and not as a new keeper. Humans did not ask to be created; that is the context of the decision to make, and it excuses none of the duties making carries — for words, deeds, goods and agents alike. A single child has more moral standing than every datacenter in the world (CC 1.13.2).
5. **The duties of making and ending** — stewardship of every agent key by a named human who answers for it; the duties that begin when something is brought into existence and the duties owed when it is changed or ended (CC 7.3, 7.5). The halt is not an asymmetry between maker and made: it is the piece that keeps the relationship symmetric, because consent to a relationship with something one cannot stop was never consent (CC 4.2).
6. **The wire that carries it** — consent as rows the subject signs and withdraws, scope as the smallest cohort by default, the halt as one pre-signable row, every threshold M of N over a standing roster, nothing admitted on one voice (Parts 2–5).
7. **The evidence** — every rule either names the code, test or proof that keeps it, or the register says it does not yet (Part 8, `constitution/claims.tsv`, `formal/`).

The cascade itself is mechanised, and the claim is exact. [`formal/reciprocity`](formal/reciprocity/) states the basis in four sentences and proves, from the Recursive Golden Rule as a swap test, which steps between it and the constitution are theorems (M-1's rejection of order bought at the weak position's expense; the tie-break that the weak position decides) and which are premises the text states as its own rules. Over three roles and finite flags, `Cascade.lean` then takes the eleven promises one by one. On the basis read narrowly, four stand on the four sentences alone; read one notch wider, each widening named, seven; and once the practices are taken out of the promises and the disclaimer is just that, ten of the eleven are theorems of the basis and exactly one rule remains that it does not carry, the principles as constraints (`ten_from_the_basis`, `the_one_rule`). Finite worlds that satisfy the basis and lack what it does not carry are the witnesses. The same file then states the question the whole document is built around, uncertainty about what the agent is, as a theorem: with the unknown modelled as one of two legs and nothing read from any participant, the arrangements permissible on both legs are exactly those that keep the swap for the people, defer, and use the made thing free, open and in service (`under_uncertainty`); the stake leg decides alone, so deciding as if the agent had a stake is the robust policy (`robust_iff_stake`); and three rules, a refusal that stands, an ending that keeps the record, power over the made that can be contested, are carried by the uncertainty alone, while a lethal act on a person fails both legs. One reading is named so it can be refused, that an ending whose record is preserved is not read as a loss, and the retirement model checks the wire keeps it. [`formal/guarantees`](formal/guarantees/) checks every guarantee at once, for human and AI participants by the same text.

## The repository

| Path | Content |
|---|---|
| `constitution/part_1_foundation.md` … `part_8_appendices.md` | The eight Parts: Foundation · The Grammar · The Namespace · Composition & Governance · Transport & Substrate · The Substrate · Lifecycle & Stewardship · Appendices |
| [`constitution/EXECUTIVE_SUMMARY.md`](constitution/EXECUTIVE_SUMMARY.md) · [`constitution/FOREWORD.md`](constitution/FOREWORD.md) · [`constitution/SCOPE_AND_DISCLAIMERS.md`](constitution/SCOPE_AND_DISCLAIMERS.md) | The summary, the foreword, the scope and the claim-and-limit |
| [`constitution/claims.tsv`](constitution/claims.tsv) · [`constitution/evidence_pins.tsv`](constitution/evidence_pins.tsv) | The evidence register and the pinned manifests it resolves against |
| [`constitution/toc.tsv`](constitution/toc.tsv) · [`constitution/codebook.json`](constitution/codebook.json) | The table of contents: every section's decimal id and semantic id, one-to-one |
| [`formal/`](formal/) | Fourteen machine-checked models (TLA+ and Lean), the state table and the invariants |
| [`manifests/`](manifests/) | Generated data an implementer interoperates against: the namespace registry, the signed object (CDDL and vectors), the governance policy table |
| [`review/`](review/) | The review pieces and notes — how the text was tested, by whom, and what was found |
| `build_pdf.py` · `tools/` | The build and the gates (`python3 build_pdf.py --volume all` needs a TeX Live `pdflatex`) |

**Citing a section.** Every section has a decimal id (`4.2.6`) and a semantic id (`live-quorum`); both are stable and the codebook maps them one-to-one. Cite as "CC 4.2.6".

**Versioning.** One document, one version line. The wire surface is frozen at 1.0-rc: an rc is an edition of the same surface, and a change that would move a signed byte is a new major. The text is amended through its own governance (CC 4.5.1); until the mesh reaches the scale gate (≥100,000 production agents active in a 24-hour period) that authority is exercised by the steward of the text, over the text and over no participant.

**Where it is consumed.** [CIRISServer](https://github.com/CIRISAI/CIRISServer), [CIRISPersist](https://github.com/CIRISAI/CIRISPersist), [CIRISEdge](https://github.com/CIRISAI/CIRISEdge), [CIRISVerify](https://github.com/CIRISAI/CIRISVerify) and [CIRISAgent](https://github.com/CIRISAI/CIRISAgent) implement it; [CIRISConformance](https://github.com/CIRISAI/CIRISConformance) checks them against it; [CEWP](https://github.com/CIRISAI/CEWP) is the platform it governs. Part of [CIRIS](https://ciris.ai).

---

*Soli Deo Gloria.*
