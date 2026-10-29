# The Evidence Register

**What this is.** Every load-bearing claim of the constitution, one row each, with its section, its status, the artefact that establishes it and the commit it was checked at: implementation symbols, conformance tests, mechanised proofs and benchmarks, or a named ticket where the claim is staged, or an acknowledged gap. With it, Part 8 except the case studies (8.7, which print in *The Charter*): the glossary, the translation discipline, the concerns ledger, the interoperability profiles, the sources, the annexes and the stub registry.

**Whom it binds.** The stewards of this document, who may not call a claim established without a resolvable pointer, and the repositories that publish the manifests the pointers resolve against. It is what an auditor, a regulator or a sceptical engineer reads first.

**What it promises.** That the status column, not the tense, says whether a row ships: an established row names a resolving artifact, a staged row names the ticket; the annexes of 8.8 state operational targets and say so. A row is *established* only when the pinned manifest of the owning repository publishes the named symbol in a backed state; a row is *staged* when a ticket names the work; a row is *normative* when it is a rule with no code. The checker that enforces this runs on every commit, and the counts at each cut are printed in the change log.

**What it leaves out.** The rules themselves, which are in the other volumes. This volume says whether a rule has evidence, not what the rule is.

**Where the rest lives.** The machine form is `constitution/claims.tsv` with `constitution/evidence_pins.tsv` and the vendored manifests under `constitution/vendor/evidence/`. The change log records each amendment by release.
