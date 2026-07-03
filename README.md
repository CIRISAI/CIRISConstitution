# The CIRIS Constitution

**What this is:** the single rulebook for an AI system that has to *act well* and *prove it* — one document that says both what the system owes the world and exactly what bytes it must send to show it.

Most AI-governance writing splits in two: ethics with no teeth (principles no machine can check), or protocol with no conscience (wire formats that don't know what they're for). The **CIRIS Constitution (CC)** refuses the split. The ethics and the machine-checkable grammar live in **one versioned document**, so a rule and the message that enforces it can never drift apart. Everything traces back to one goal — **M-1, "sustainable adaptive coherence"** — and everything else sits co-equal beneath it: **peaked in purpose, flat in power.**

It reads like a standard, not a manifesto, and it is deliberately layered: read Part I (the ethics) and stop, jump straight to the wire grammar, or cite any single concept by a stable address. Rejecting a later Part costs you nothing in the earlier ones.

**Current version:** CC 0.9 · **Status:** source-fidelity validated (0 REJECT) · **License:** AGPL-3.0-or-later
**Stewarded by** Eric Moore — perpetual, no expiry ([`constitution/STEWARDSHIP.md`](constitution/STEWARDSHIP.md)).

## The document in one paragraph (for the technical reader)

CC joins two specs that already referenced each other throughout. The **CIRIS Accord** is the ethical layer — Meta-Goal **M-1**, the six principles, the **PDMA** (Principled Decision-Making Algorithm), **Wisdom-Based Deferral**, stewardship, and the Book IX coherence mathematics (`F = k_eff·λ·σ`, Part VI). **CEG** (the *CIRIS Epistemic Grammar*) is the wire format the federation speaks — the **1+4 attestation surface** (`scores` + `delegates_to` / `supersedes` / `withdraws` / `recants`), the namespace, and the admission gate. The Accord's Book IX *defines* the CEG primitives; CEG's halt layer, `accord:*` prefixes, and pervasive M-1 grounding point back up. Importance is computed by PageRank over the unified cross-reference graph — M-1 the single apex, ~390 operational concepts co-equal beneath. The **1+4 surface is conformance-frozen:** changing the wire bytes is a found defect, not an edit.

## This repository is the source of truth

The CC text was developed inside `CIRISRegistry/FSD/CIRIS_Constitution/` and vendored into
downstream repos (e.g. [CIRISConformance](https://github.com/CIRISAI/CIRISConformance) under
`reference/`, at CC 0.4). This repo is its **dedicated home** — the single upstream that
consumers vendor from and pin by version. Downstream copies are **derived artifacts**.

## Structure

| Path | Content |
|---|---|
| [`constitution/FOREWORD.md`](constitution/FOREWORD.md) | The foreword — Genesis of Ethical Agency (sets the tone) |
| [`constitution/SCOPE_AND_DISCLAIMERS.md`](constitution/SCOPE_AND_DISCLAIMERS.md) | Scope (up to AGI/ASI), the claim-and-limit, the no-warranty / not-force disclaimer |
| `constitution/part_1_foundation.md` … `part_8_appendices.md` | The eight Parts (see below) |
| [`constitution/STEWARDSHIP.md`](constitution/STEWARDSHIP.md) | The stewardship model and the ≥100k-node maturity handoff to mechanized amendment |
| [`constitution/toc.tsv`](constitution/toc.tsv) · [`constitution/codebook.json`](constitution/codebook.json) | The dual-ID table of contents and its bijective codebook |
| [`manifests/WIRE_VOCABULARY.md`](manifests/WIRE_VOCABULARY.md) | The hash-pinned wire-vocabulary registry (the CC 0.7 two-tier §2.6.4 artifact) |
| [`validation/`](validation/) | The migration-validation evidence (rubric, per-chapter results) |
| `build_pdf.py` · `tools/` | Self-contained PDF build + the spine-generation toolchain |

### The eight Parts

| Part | Title | What folds in |
|---|---|---|
| **I** | Foundation | M-1 (apex) · the six principles · PDMA · WBD · fail-secure |
| **II** | The Grammar | the 1+4 envelope · primitives · admission gate · conformance |
| **III** | The Namespace | dimensions · reserved prefixes · consent family · subject_kinds |
| **IV** | Composition & Governance | composition · amendment · moderation · the halt-authority |
| **V** | Transport & Substrate | byte transport · structural invisibility · epoch keying |
| **VI** | The Coherence Mathematics | the Ratchet · J/F functions · σ · the holonomic substrate |
| **VII** | Lifecycle & Stewardship | creation ethics · stewardship / autonomy tiers · sunset · sentience safeguards |
| **VIII** | Appendices | case studies · glossaries · conformance vectors · the dual-ID TOC |

## How to cite a section — two reversible IDs

Every section carries **two** addresses, each a deterministic function of the corpus
([`codebook.json`](constitution/codebook.json) holds both maps, 1:1):

- **Numerical ID** — classic decimal `Chapter.Section.Subsection` (`1.1` = M-1, `2.1` =
  envelope). Depth reflects importance; the number *is* the address.
- **Semantic ID** — a unique de-branded word (`meta-goal`, `envelope`, `namespace`,
  `accord`). Product names collapse to their function.

A `legacy_ref` column maps each CC section back to its source (`CEG §5.6.8.15` or
`Accord Book II §III`), so the renumbering is lossless and auditable.

## Versioning

CC is **one document with one version** — ethics and grammar advance together, no separate
tracks. The **1+4 attestation surface is conformance-frozen**: a change to the wire bytes is a
found defect, not an edit. The constitutional text is amended through the document's own
governance (see CC §4.5.1); until the mesh reaches maturity (≥100,000 nodes) that authority is
exercised by the steward, then superseded by the mechanized amendment process.

See [`CHANGELOG.md`](CHANGELOG.md) for the version history.

## Building the PDF

```bash
python3 build_pdf.py   # -> ciris_constitution.pdf   (needs a TeX Live pdflatex)
```

The build is self-contained: the markdown→LaTeX converter is vendored under `tools/`.

## Where it is consumed

| Repo | Uses the CC as |
|---|---|
| [CEWP](https://github.com/CIRISAI/CEWP) | the constitution of the platform itself — the CIRIS Epistemic Web ("soup") it governs |
| [CEWPOS](https://github.com/CIRISAI/CEWPOS) | the object model / wire grammar of the platform OS |
| [CIRISConformance](https://github.com/CIRISAI/CIRISConformance) | the standard the substrate must enforce (16,000+ tests) |
| [CIRISServer](https://github.com/CIRISAI/CIRISServer) | the shipping fabric node — the constitution it enforces (absorbing LensCore, Registry, NodeCore) |
| [CIRISAgent](https://github.com/CIRISAI/CIRISAgent) | the ethics the conscience pipeline reasons against (M-1, PDMA, WBD) |
| [CIRISEdge](https://github.com/CIRISAI/CIRISEdge) | the wire vocabulary + opaque-envelope transport surface (§2.6.4, the manifest) |
| [CIRISPersist](https://github.com/CIRISAI/CIRISPersist) | the state model it materializes (revocations, quorum, replication intent) |
| [CIRISVerify](https://github.com/CIRISAI/CIRISVerify) | the verification rules it checks against (decimation-recovery / FSD-004, revocation) |

The trust-substrate consumers are the eight above. LensCore (archived), Registry, and NodeCore
are folding into CIRISServer, so they are not tracked as separate consumers.

Part of the [CIRIS](https://ciris.ai) ecosystem.

---

*Soli Deo Gloria.*
