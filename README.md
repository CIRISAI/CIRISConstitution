# The CIRIS Constitution

The rulebook for a network that people, organizations and AI systems share, running on the phones and computers people already own, with no company in the middle. One text says what the system owes the people it touches and exactly what bytes it must send to show it, so the ethics and the wire cannot drift apart.

**The mesh is live.** The CIRIS app is on Google Play and the App Store, and runs on Android, iOS, the web, Linux, macOS and Windows, in 29 languages. It implements this document: every row it sends is one of the five kinds below, under the key of the person who sent it. Five open-source components together carry the rows and a conformance suite checks them against each other.

**What it is for.** Messages, groups, posts, photos and files, events, reviews of the businesses around you, and AI agents that work for you: a social network and a personal store in one, with no operator. It lets you make and coordinate decisions with others, by votes that no single voice can carry and polls nobody outside can see. It streams live video and chat to groups of thousands peer to peer, through an application-layer multicast mesh the members themselves form, without giving up privacy or the community's ability to moderate. Your things live on your own devices and copy between them, in five circles from just you outward: you, your family, your neighbours, the communities and businesses you join, everyone. Nothing leaves a circle unless you move it, and a stranger reaches you only if you chose to be found. Ignore, block and mute are yours and private. Each thing people do on a social network, and the rule that carries it, is listed in [`formal/STORIES.md`](formal/STORIES.md).

**This tree:** 1.0-rc18, open; the re-cut of the decimals on the state processor's spine ([#203](https://github.com/CIRISAI/CIRISConstitution/issues/203)) belongs to this edition and has not begun. **Latest release:** 1.0-rc17, the long-term-support edition, 2026-11-10, tag `v1.0-rc17`. The register ties every rule to the code, test or proof behind it or says plainly that nothing does yet: 393 established rows, 47 normative, 152 staged. Sixteen machine-checked models carrying 216 properties, the life of a mesh told as one story whose model closes, and one state processor whose preview is proved equal to its door ([`formal/`](formal/)). **Steward:** Eric Moore ([`constitution/STEWARDSHIP.md`](constitution/STEWARDSHIP.md)). Releases: [`CHANGELOG.md`](CHANGELOG.md).

## What it protects

Three things: being spoken for without your consent, being watched inside your private groups, and being governed by AI systems nobody can switch off.

Every act is a signed *row* under the key of whoever did it, and they can take it back. There are five kinds of row and no sixth: a claim, a delegation, a replacement, a withdrawal, a recantation. Consent, identity, keys, rosters, moderation, holding claims and the halt itself are rows of those five kinds.

A node holds rows and nothing else. Who you are to a room, what state a post is in, who holds a duty: every such answer is folded from the rows the node holds, never stored beside them, so there is no second copy of anything to drift. The list of what a person may do next, the preview of what an act would change, and the door that admits the act when it arrives are one function run three ways, proved equal; the whole life of a mesh is a finite machine over an unbounded signed log, so every question about it is decidable and has been model-checked.

A few named people hold a *trust root*. Any one of them can pause every AI agent that follows it with one signed row. A lone pause lapses after a day unless a majority confirms it, a majority lifts it, and anyone may leave a root or found one. The halt is what makes the relationship between maker and made symmetric: consent to something you cannot stop was never consent.

## The eleven promises

Each is kept by a named section and, where a machine can check it, by a model or a test ([`constitution/EXECUTIVE_SUMMARY.md`](constitution/EXECUTIVE_SUMMARY.md) gives each with its status).

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

This document creates no legal claim and rules on no legal matter. The bet behind it: there are two roads to safe powerful AI, train values you trust, or assume the model may be wrong and make its consequential acts refusable, attributable and stoppable by construction. This is the second road, and it is built so that an unaccountable AI cannot take part.

## Read it

One edition, printed nine ways for nine readers. The section is always the authority; a volume is a lens on it. The links point at the latest release ([`volumes/README.md`](volumes/README.md) explains the files).

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
| **The Digest** | everyone: the executive summary, the plain-language rules, the user's guide to the mesh and the operator's digest | [`digest`](volumes/ciris_constitution-digest.pdf) |

The whole edition in one file: [`ciris_constitution.pdf`](ciris_constitution.pdf), or [`CIRISConstitution-latest.pdf`](CIRISConstitution-latest.pdf) for the newest release on `main`. The ethics it descends from, in one page: [`formal/reciprocity`](formal/reciprocity/) states the basis in four sentences and proves which steps from it to the rules are theorems.

## The repository

| Path | Content |
|---|---|
| `constitution/part_1_foundation.md` to `part_8_appendices.md` | The eight Parts: Foundation, The Grammar, The Namespace, Composition and Governance, Transport and Substrate, The Substrate, Lifecycle and Stewardship, Appendices |
| [`constitution/EXECUTIVE_SUMMARY.md`](constitution/EXECUTIVE_SUMMARY.md), [`constitution/FOREWORD.md`](constitution/FOREWORD.md), [`constitution/SCOPE_AND_DISCLAIMERS.md`](constitution/SCOPE_AND_DISCLAIMERS.md) | The summary, the foreword, the scope and the claim-and-limit |
| [`constitution/claims.tsv`](constitution/claims.tsv), [`constitution/evidence_pins.tsv`](constitution/evidence_pins.tsv) | The evidence register and the pinned manifests it resolves against |
| [`constitution/toc.tsv`](constitution/toc.tsv), [`constitution/codebook.json`](constitution/codebook.json), [`constitution/volumes.tsv`](constitution/volumes.tsv) | The table of contents, the id codebook, and the map of sections to volumes |
| [`constitution/digest/`](constitution/digest/), [`constitution/covers/`](constitution/covers/) | The plain-language rules, the user's guide to the mesh and the operator's digest; the cover of each volume |
| [`formal/`](formal/) | The life of a mesh as one story and one model that closes, the chapter models in TLA+ and Lean, the state table, the invariants and the stories |
| [`manifests/`](manifests/) | Generated data an implementer interoperates against: the namespace registry, the signed object (CDDL and vectors), the governance policy table, the family model (draft) |
| [`ietf/`](ietf/) | The Internet-Draft that describes the signed object |
| `build_pdf.py`, `tools/` | The build and the gates (`python3 build_pdf.py --volume all` needs a TeX Live `pdflatex`) |

**Citing.** Every section has a decimal id (`4.2.6`) and a semantic id (`live-quorum`); both are stable and the codebook maps them one to one. Cite as "CC 4.2.6".

**Versioning.** One document, one version line. The wire surface is frozen at 1.0-rc: an rc is an edition of the same surface, and a change that would move a signed byte is a new major. The text is amended through its own governance (CC 4.5.1); until the mesh reaches the scale gate of 100,000 production agents active in a day, the steward exercises that authority over the text.

**The layer a person meets.** Every screen of the app is described by a card held to four things at once: the plain rule it exists for, the wire fields it shows, the trust topology that must exist for its states to be reachable, and the states it is tested in. The topologies are a closed catalogue of twenty, typed from the root down, that drives the harness building those meshes on real nodes, the client's checker, and the constants of the formal models ([`formal/cewp_node/`](formal/cewp_node/)). A card passes six stages, envisioned to shipped, and the checker tells "not yet", "stalled" and "the answer is no" apart. That contract, CSD/4, is the application layer of the mesh.

**Where it is consumed.** [CIRISServer](https://github.com/CIRISAI/CIRISServer), [CIRISPersist](https://github.com/CIRISAI/CIRISPersist), [CIRISEdge](https://github.com/CIRISAI/CIRISEdge), [CIRISVerify](https://github.com/CIRISAI/CIRISVerify) and [CIRISAgent](https://github.com/CIRISAI/CIRISAgent) implement it; [CIRISConformance](https://github.com/CIRISAI/CIRISConformance) checks them against it; [CEWP](https://github.com/CIRISAI/CEWP) is the platform it governs. Part of [CIRIS](https://ciris.ai).

---

*Soli Deo Gloria.*
