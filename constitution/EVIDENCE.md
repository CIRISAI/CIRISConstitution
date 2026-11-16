# Evidence registry — the tag vocabulary

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
`impl`/`test`/`lean`/`bench` pointer whose manifest does not yet reach the section is reported as a
**warning** (unresolved, pending manifest). A pointer that names an artifact the pinned manifest does
**not publish** is an **error** — a dead pointer is not a pending one, and the distinction is the whole
value of naming symbols rather than sections.

## Status

- `established` — at least one resolvable `impl`/`test`/`lean`/`bench` artifact backs the claim.
- `normative` — the claim is **settled by this document and has no external artifact to resolve**: a
  definition, a governance rule, or a threat-model classification whose whole content is the text.
  Pairs with `normative-only:—`. This is not a weaker `established` — it is a different kind of claim,
  and conflating the two is what let self-contained rules read as externally evidenced.
- `staged` — the claim is normative now; its artifact is named but not yet resolvable (a `staged:` or
  cross-repo pointer pending its manifest).
- `open` — an acknowledged gap (mirrors a CC 8.3.1 R-bet / a tracked issue).

## Adding a claim

Every new **normative** claim (a `MUST` / `MUST NOT` / `SHALL`, or a load-bearing definition) should
land with a `claims.tsv` row — the same discipline by which every new section ships with a dual-ID.
Give it a stable `claim_id` (`CLM-<area>-<slug>`), the section `decimal_id` (or `corpus` for a
whole-document claim), a one-line summary, its evidence tokens, and a status. Run `check_claims.py`
before committing.

## Superseded vectors (normative reading rule)

A **known-failing (`xfail`) conformance vector is not automatically a gap.** Where a ratified change moves the standard under an existing vector, or where a control migrates from the conformance tier into the substrate, the vector fails *because it encodes the superseded rule* — and the honest disposition is **superseded**, carrying the amendment that moved it and the substrate symbol that now witnesses the behavior. Two rules keep this from becoming an excuse: a vector may be called superseded only when a **named substrate witness publishes the equivalent control** (an unpublished symbol is a gap, not a supersession — a claim MUST NOT be repointed at a symbol no manifest carries), and a green sibling row at the same decimal **never** clears a failing vector on its own. Live instance: the CC 3.2 steward-binding family and the CC 3.4.x age plane, moved by the [CC 3.2](part_3_the_namespace.md) conferral-is-not-stewardship ruling (CIRISConstitution#87) — supersession tracked at CIRISPersist#729 / CIRISConformance#89.

## Span hashes (`span_sha256`)

An implementer's manifest may carry a trailing `span_sha256` column. Its definition, as CIRISVerify
states it: "the ``span_sha256`` column is the SHA-256 of the item's own text, from its declaration
keyword to its closing ``}`` or ``;`` (doc comments and attributes above it excluded; CRLF read as LF)."
A qualified `Owner::member` resolves inside the owner's impl or trait block, and a name declared more
than once is refused. The reference extractor is [`../tools/span_of.py`](../tools/span_of.py), copied
unchanged from CIRISVerify; another repository copies it whole so every manifest's hash means the same bytes.

Every implementer manifest should carry the column. The implementer's own gate then fails when a cited
item's body changes under an unchanged name, and the claim it backs is re-read in the same commit.

`check_claims.py` reads the column by name. When a pin moves, each row carrying a hash is compared with
the same row (claim id and symbol) in the manifest vendored at the earlier pin, found in this
repository's git history. Each claim whose span changed is listed as
`re-read CLM-x: its code changed at <repo> <old>→<new>`. The listing is a note; `--span-changes-block`
makes it an error. A manifest without the column is skipped.

The constitution's own Lean citations are pinned by statement, not proof:
[`../formal/derivation/lean_statements.tsv`](../formal/derivation/lean_statements.tsv) records the hash
of each cited theorem's text from `theorem` to the `:=` that starts its proof, comments removed and
whitespace normalised. [`../tools/lean_statement_hash.py`](../tools/lean_statement_hash.py) fails when a
statement changes without the table; re-proving a theorem leaves its hash alone.
