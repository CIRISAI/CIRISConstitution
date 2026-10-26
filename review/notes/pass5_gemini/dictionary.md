# The Dictionary (ciris_constitution-1.0-rc11-dictionary.pdf, 110 pages)

**Care score:** 3
**One-line verdict:** Architecturally rigorous and machine-pinned, but needs a targeted cleanup pass before 1.0 to resolve a polarity contradiction on `age_assurance`, strip migration-history prose and repo/file paths, and fix broken section numbering and a LaTeX escape defect.

## Strengths
- **Machine-verified single source of truth:** The namespace family count and segment rules are generated directly from the text into `manifests/namespace_registry.json` and tested via `manifests/namespace_match_vectors.json` (pp. 1, 2, 27–30), preventing spec-vs-implementation drift.
- **Exhaustive byte-level determinism:** Cryptographic preimages, string encodings, and multi-stage hash constructions are pinned with zero ambiguity—including JCS array-sort preconditions (p. 9), wire-string vs. PascalCase variant tables (pp. 45–48), and the 4-step Reticulum destination hash (pp. 60–61).
- **Clear authority and non-claim boundaries:** The volume explicitly disambiguates overloaded terms like the six senses of "witness" (pp. 93–94) and the two `A{n}` scales (p. 40), while stating cryptographic and operational limits honestly (e.g., KEM rotation does not recover historical confidentiality, p. 58; 1+4 buys accountability, not atomic swaps, pp. 55, 71).

## Weaknesses
- **Internal polarity contradiction:** `age_assurance:{level}:{band}:{version}` is registered with Polarity `signed` in CC 3.1.2 (p. 7), but restated with Polarity `enumerated` in CC 3.3.12 (p. 73).
- **Missing Section 3.2 without explanation:** The volume jumps directly from Section `3.1.10` to Section `3.3` (p. 40), while referencing `CC 3.2` dozens of times (pp. 3, 4, 6, 8, 10, 16, etc.). Even if 3.2 is printed in another volume, p. 1 ("What it leaves out") does not mention that 3.2 is omitted from Part 3 here.
- **Stale transition and migration history in normative rules:** Rules state transition mechanics and pre-door history rather than timeless law, e.g., "Until a substrate’s door carries this family, the same claim travels as a contribution: row... once the family ships, the contribution: prefix no longer carries it" (p. 36); "Wait for amendment: The three kinds below remain registered and in force. Retiring them onto the affiliation’s rows... is a wire change made by amendment (CC 4.5.1), and until that amendment lands both stand" (p. 66); "the two symbol-count keys are retired with fountain storage... whose consumer arrives with the durability tier" (p. 35); and "see CC 5.3.1 for the interim using a registry_witnesses table" (p. 93).
- **Code pointers and repository/file names in rules:** Violations of house rules against code pointers include `manifests/namespace_registry.json` (pp. 1, 2, 27), `trace_format_v{n}.json` (p. 25), `formal/membership` (p. 17), `formal/consent` (p. 43), `formal/self_roster` (p. 63), `Edge MessageType::ContentFetch` (p. 34), `EnvelopeKind::IdentityOccurrence` (p. 57), `CIRISAI/RATCHET` (p. 32), and "Steward: CIRISRegistry, folding into CIRISServer... owning_repo follows the fold" (p. 2).
- **Comparative claims / named external projects:** The text names and compares external projects and protocols, e.g., "(AT Protocol app.bsky.embed.video captions[]: accept: ["text/vtt"], maxSize: 20000)" (p. 75) and "(they hurt honest participants restoring from stale backups — the eltoo argument against Lightning-class penalties)" (p. 71).
- **Colloquial editorializing:** In the middle of formal adult-incapacity rules, the text remarks "(every documented capture, Britney’s included, began as a "temporary" order)" (p. 100).
- **Unanchored numbers in prose:** Page 26 asserts "The 22 leaves are a closed vocabulary" for `prohibited:{category}` without citing a register row or derivation; page 42 references "the agent’s 90-day decay" and "temporary (14d auto-expire, default)" without source anchoring.
- **Inconsistent table schemas:** Some CC 3.1 tables include a `Reserved?` column (pp. 2–5, 7–8, 10–14, 22–24, 32–33), while others omit it (pp. 5–7, 25–26, 31–32, 34–40) and bury reservation status in prose (e.g., `transparency_log:cosigned:{tree_size}` on p. 6; `quarantine:{state}`, `mesh_config:{key}`, and `regime:{artifact}:{version}` on pp. 34–35).

## Opportunities
- **Standardize the `Reserved?` column across all CC 3.1 tables:** Adding the missing 4th column to the tables in 3.1.2 (pp. 5–7), 3.1.5.1–3.1.5.4 (pp. 25–26), 3.1.8 (pp. 31–32), and 3.1.9.1–3.1.10 (pp. 34–40) will make reservation status visually scannable and uniform for the parser.
- **Convert prose-only prefix lists into tables:** Sections 3.1.3 (p. 9), 3.1.4 (p. 20), 3.1.5.1 (p. 25), 3.1.5.3 (p. 26), 3.1.6 (p. 26), 3.1.8.2 (p. 31), and 3.1.8.3 (p. 31) list canonical leaves inline in prose rather than in the standard prefix tables. Tabulating them will unify the volume's dictionary layout.
- **Note the omission of Section 3.2 on Page 1:** Adding six words to "What it leaves out" on p. 1 (explaining which volume holds Section 3.2) will stop readers from thinking pages 40–41 suffered a build failure.

## Threats
- **Strict admission rejection due to the `age_assurance` polarity mismatch (pp. 7, 28, 73):** Under CC 3.1.7 R4 (p. 28), declared polarity is a strict substrate admission gate (`score_outside_declared_polarity`). Having `age_assurance` listed as `signed` on p. 7 and `enumerated` on p. 73 creates a conformance trap for implementers and automated table extractors.
- **Unfinished architectural migrations exposed to auditors (pp. 11, 35, 36, 66, 93):** A hostile reviewer or regulator reading that `organization`, `org_membership`, and `partner_record` are slated to be retired by a future amendment (p. 66), or that `deferral:request:v1` rides `contribution:` "Until a substrate's door carries this family" (p. 36), will conclude that 1.0 is shipping mid-migration with deprecated wire shapes already baked in.
- **Informative economics essay inside a normative specification (pp. 71–72):** The "Design notes (informative)" in CC 3.3.10.1 reads like an opinionated whitepaper ("a salaried broker layer with a network-wide matching view and capacity-based credit lines is load-bearing in a mutual-credit circuit, and a circuit dies at the rail boundary when exit is easier than circulation"). A lawyer or financial regulator will scrutinize this as an implicit design for an unlicensed credit/brokerage facility.

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
| 1 | p. 7 vs. p. 73 | contradiction | `age_assurance:{level}:{band}:{version}` has Polarity `signed` in CC 3.1.2 (p. 7) but `enumerated` in CC 3.3.12 (p. 73). | Align both tables to the same polarity class (matching `manifests/namespace_registry.json`). |
| 2 | pp. 35, 36, 66, 93 | stale | Transition/migration state written into rules: "Until a substrate's door carries this family..." (p. 36), "The three kinds retire into the affiliation at the cut above... until that amendment lands both stand" (p. 66), "interim using a registry_witnesses table" (p. 93). | State only the 1.0 normative rule; remove transitional "until shipped" and "retired with fountain storage" history. |
| 3 | p. 85 | rendering | Literal LaTeX/markdown backslash escape printed in prose: `dimension\’s declared polarity` in item `(iii)`. | Remove the stray backslash before the apostrophe in the source markdown. |
| 4 | p. 40 | numbering | Section numbering jumps from `3.1.10` to `3.3` with no Section `3.2` and no note on p. 1 explaining where `3.2` lives. | Note on p. 1 ("What it leaves out") which volume carries CC 3.2, or insert a 2-line stub at 3.2 pointing to that volume. |
| 5 | pp. 2, 17, 25, 34, 43, 57, 63 | other | Code/repo/file pointers in normative text: `formal/membership` (p. 17), `trace_format_v{n}.json` (p. 25), `Edge MessageType::ContentFetch` (p. 34), `formal/consent` (p. 43), `EnvelopeKind::IdentityOccurrence` (p. 57), `formal/self_roster` (p. 63). | Replace file paths and Rust enum paths with plain-English constitutional concepts. |
| 6 | p. 71, 75 | other | Comparative claims / external project callouts: "the eltoo argument against Lightning-class penalties" (p. 71) and "AT Protocol app.bsky.embed.video captions[]" (p. 75). | Delete the comparative parentheticals; keep only the CIRIS rule (e.g., "a separate `text/vtt` blob with a 20,000-byte cap"). |
| 7 | p. 100 | editorializing | Colloquial aside in normative text: `(every documented capture, Britney’s included, began as a "temporary" order)`. | Delete the parenthetical; the preceding sentence ("This is the anti-'temporary-becomes-permanent' lock") is sufficient. |
| 8 | pp. 56, 74, 75 | rendering | Severe word-breaking/hyphenation across lines in narrow table cells (`SignedIdentityOccurr` / `enceRevocation` p. 11; `X25519MlKem768Aes256GcmHkdfSha` / `256` p. 47; `compositeW` / `ithTrainedAlgorithmicMedia` p. 75) and code comments wrapping mid-clause (pp. 56, 76). | Widen the first column or allow `\raggedright` wrapping in LaTeX tables; shorten inline code comments to <80 chars. |

## Rendering
- **p. 3:** In the `ownership:` row, the not-equal glyph renders with an overlapping slash artifact (`cardinality ̸= 1`).
- **p. 11:** `SignedIdentityOccurrenceRevocation` is broken mid-word across lines without a hyphen (`SignedIdentityOccurr` / `enceRevocation`).
- **p. 21:** `capacity:relay_delivery` table row has uneven spacing (`a    relay’s   delivered-versus-claimed    A/V`).
- **pp. 22–24:** In the `consent:*` and `retirement:*` tables, the `Reserved?` column inconsistently drops the `Yes —` prefix starting at `retirement:{state}` (p. 24: `self-emitted...`, `the agent...`, `the operator...`, `WA-emitted...`, `the steward...`).
- **p. 47:** Variant name `X25519MlKem768Aes256GcmHkdfSha256` breaks mid-token across lines (`...Sha` / `256`).
- **pp. 55–56, 66–67, 76, 98:** Code blocks wrap long lines awkwardly onto unindented continuation lines (e.g., `cohorts: [...], // OPTIONAL...` wrapping to `allow list (below)` on p. 63; `width, height, duration_ms` wrapping `allocation` on p. 76; `OR ( binding_tier == T1_provisional` wrapping `order:` on p. 98).
- **p. 75:** Token `compositeWithTrainedAlgorithmicMedia` breaks mid-word across lines as `compositeW` / `ithTrainedAlgorithmicMedia`.
- **p. 85:** Literal backslash rendered in text: `dimension\’s declared polarity`.
- **p. 91:** Hyphenation split across slash in `person/n-` / `ode axis`.

## Effort estimate
About 6–8 hours of mostly mechanical editing (fixing the `age_assurance` polarity mismatch, stripping repo/code pointers and comparative parentheticals, fixing the `\'` escape and table column consistency), plus 1–2 hours of steward rulings on whether to excise or freeze the "until shipped / until that amendment lands" transitional clauses (pp. 36, 66) for 1.0.

<!-- model google/gemini-4-argon; 110 pages; prompt_tokens 97292; completion_tokens 3338; 51s -->
