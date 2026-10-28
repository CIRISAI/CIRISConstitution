# `formal/trust_set` — the reader's pinned trust set

"Who I trust" is one of the reader's options: it adds licensors, licensors of licensors, or a class of licensor (medical, legal, financial), and removes them, the shipped root included. CC 4.4.3.8 states the pinned trust set as a graph with pluggable roots, the reader hanging acceptance edges off its own base, "added and removed freely", the shipped root the default entry and never *the* root. This file states that model in core Lean and proves what the clause claims.

**The model** (`TrustSet.lean`). A finite world: acceptance edges (each the signed row of the key it leaves: `src` trusts `dst` as a licensor, for the listed classes or for every class the target's charter declares, with a `depth` of further hops allowed past it), charters (the classes an authority declares, CC 2.4.1.2.1), and licences (authority, holder, class). The reader is key `0`. The walk `reaches` starts at the reader's own edges, follows an edge only if it admits the class, and continues past an authority only within that edge's `depth` and the global cap of five hops (CC 4.1.1). The reader **honours** a licence iff its walk reaches the issuing authority for the licence's class and that authority's charter declares the class.

**What is proved.**

| Theorem | What it says | CC |
|---|---|---|
| `no_trust_without_my_edge`, `empty_set_honours_nothing` | nothing is honoured without an edge that leaves the reader; a reader with no edge honours nothing, whatever the rest of the graph says | 4.4.3.8 (1), (3) |
| `licence_confers_no_trust` | the licences in the world move no reach: holding a licence from an authority makes nobody a licensor the reader trusts | 2.4.1.2.1; `authority_tree` I4 |
| `reaches_mono`, `removal_only_removes` | more edges, more reach, never less; removing an edge (the shipped root's included) removes only what reached through it | 4.4.3.8 (3), (4) |
| `class_edge_admits_listed`, `class_edge_refuses_unlisted`, `undeclared_class_never_honoured` | an edge that lists classes admits exactly those; the authority's charter is the second gate | 2.4.1.2.1 (scope per licence class) |
| `reaches_mono_budget`, `verdict_is_the_capped_walk` | more budget never reaches less; an edge's depth lowers the walk past it and the cap is the outer bound | 4.1.1 |
| `reaches_same_edges` | the verdict reads the edges as a set: order never matters | 4.4.3.4.3 (determinism) |
| the worked world | as shipped, the root alone, a hospital board's licence is not honoured; the reader adds the board for medical, and it is; the board's legal licence is not; a stranger's never is; the reader removes the CIRIS root and the board's medical licence stands; a licensor-of-licensor is honoured at depth 1 and cut at depth 0 | the clause as a run |

**What it does not model.** The rows themselves (an acceptance edge is `delegates_to(reader → authority)` bearing `trust:accepts:v1`, CC 3.2 T3; the class filter and depth are the reader's own members on that row, which the grammar must name — see the CHANGELOG at rc13); revocation timing (an edge removed is removed; CC 2.4.1.1's reach-back is the grammar's); the standing verdict of the root itself (`formal/trust_root`); delegation chains and their attenuation (`formal/authority_tree`).

**Running.** `lean TrustSet.lean` (core Lean 4.14, no Mathlib, no `sorry`, no axioms beyond core); the CI job `reciprocity` compiles it beside the cascade.
