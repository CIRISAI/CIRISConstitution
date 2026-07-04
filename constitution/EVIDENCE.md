# Evidence registry — the tag vocabulary (CC 1.0-rc2)

The Constitution should not carry all of its own evidentiary weight. This file defines how each
load-bearing claim names **which artifact establishes it**, so a reviewer — and CI — can follow the
claim to the code, test, proof, or benchmark that backs it. It operationalizes the four-artifact view:

1. **Constitution** — normative principles + governance (this repo).
2. **Protocol specification** — wire semantics (this repo's Parts II–VI + `manifests/`).
3. **Reference implementation** — behavior (CIRISServer / CIRISAgent + pinned substrate crates).
4. **Formal model** — mechanized proofs + computational validation (coherence-ratchet / RATCHET).

The registry is [`claims.tsv`](claims.tsv); it is checked by [`../tools/check_claims.py`](../tools/check_claims.py).

## Tag vocabulary

Each claim's `evidence` column is a space-separated list of `tag:pointer` tokens.

| Tag | Establishes the claim by | Pointer form |
|---|---|---|
| `impl` | reference implementation | `REPO/path#symbol` |
| `test` | test suite / conformance vector | `REPO#test_id` |
| `lean` | mechanized proof | `coherence-ratchet:Module.theorem` |
| `bench` | evaluation report / experiment | `REPO#experiment` |
| `staged` | spec ahead of impl, named ticket | `REPO#issue` |
| `open` | acknowledged gap, tracked | `REPO#issue` |
| `normative-only` | self-contained rule/definition, no external artifact | `—` |

**Pointer resolution.** A pointer beginning `@` is **in-repo** (a path relative to the repo root) and
is resolved directly by the checker; a dead in-repo pointer fails the build. All other pointers are
**cross-repo** and resolve against the pinned sibling **spec-map manifests** each downstream repo
publishes (`evidence/cc_tests.tsv`, `evidence/cc_impl.tsv`, `evidence/cc_formal.tsv` — tracked in
CIRISConformance#59, CIRISServer#155, CIRISAgent#911, RATCHET#8). Until those land, a cross-repo
`impl`/`test`/`lean`/`bench` pointer is reported as a **warning** (unresolved, pending manifest), not a
failure — so the registry is useful immediately and tightens as the manifests arrive.

## Status

- `established` — at least one resolvable `impl`/`test`/`lean`/`bench` artifact backs the claim.
- `staged` — the claim is normative now; its artifact is named but not yet resolvable (a `staged:` or
  cross-repo pointer pending its manifest).
- `open` — an acknowledged gap (mirrors a CC 8.3.1 R-bet / a tracked issue).

## Adding a claim

Every new **normative** claim (a `MUST` / `MUST NOT` / `SHALL`, or a load-bearing definition) should
land with a `claims.tsv` row — the same discipline by which every new section ships with a dual-ID.
Give it a stable `claim_id` (`CLM-<area>-<slug>`), the section `decimal_id` (or `corpus` for a
whole-document claim), a one-line summary, its evidence tokens, and a status. Run `check_claims.py`
before committing.
