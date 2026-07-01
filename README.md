# The CIRIS Constitution

The canonical source of the **CIRIS Constitution (CC)** — one document that joins the
**ethics** the CIRIS federation serves and the **wire grammar** it speaks, under a single
version line.

**Current version**: CC 0.7 · **Status**: adversarially certified (0 REJECT) · **License**: AGPL-3.0-or-later
**Stewarded by** Eric Moore — perpetual, no expiry (see [`constitution/STEWARDSHIP.md`](constitution/STEWARDSHIP.md))

## What this is

The CIRIS Constitution unifies two documents that already contained each other:

- the **CIRIS Accord** — the ethical / constitutional layer: Meta-Goal **M-1**, the six
  principles, the PDMA, Wisdom-Based Deferral, Stewardship, and the Book IX mathematics of
  coherence; and
- **CEG** (the *CIRIS Epistemic Grammar*) — the wire format the federation speaks: the
  **1+4 attestation surface** (`scores` + `delegates_to` / `supersedes` / `withdraws` /
  `recants`), the namespace, and the admission gate.

They were written apart but reference each other throughout — the Accord's Book IX *defines*
the CEG primitives; CEG's halt layer, `accord:*` prefixes, and pervasive M-1 grounding point
back up. This document joins them. When the joined corpus is measured for importance, **M-1
emerges as the single apex** every mechanism traces back to, while the ~390 operational
concepts stay co-equal beneath it — **peaked in purpose, flat in power**.

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
| [`validation/`](validation/) | The adversarial certification evidence (rubric, per-chapter results) |
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
| [CIRISConformance](https://github.com/CIRISAI/CIRISConformance) | the standard the substrate must enforce (16,000+ tests) |
| [CEWPOS](https://github.com/CIRISAI/CEWPOS) | the object model / wire grammar of the platform OS |
| [CIRISServer](https://github.com/CIRISAI/CIRISServer) · [CIRISAgent](https://github.com/CIRISAI/CIRISAgent) | the shipping fabric node + agent they conform to |

Part of the [CIRIS](https://ciris.ai) ecosystem.

---

*Soli Deo Gloria.*
