# Rule-statement inventory: brief

## Why
The CIRIS Constitution (`<main checkout>/constitution/part_*.md`) is being refactored. Today the same
rule is stated in many sections, mixed into narrative. The refactor moves every rule statement into one rulebook:

1. **kernel**: general rules that hold for every signed row, stated once;
2. **family model**: per-family rules held as data cells (184 row families x columns; a default row plus departures);
3. **mechanism**: wire bytes, endpoints, transport, media;
4. **stewardship / foundation**: who keeps the text and the principles it rests on.

No rule may be lost in the move, so we need an inventory of every rule statement, tagged so that the same rule stated
in different sections lands on the same key. You are one of twelve readers; each has one line range. Other readers
cover the other ranges, so stay inside yours, and use the closed vocabulary below exactly so the rows join.

## What you do
Read your range linearly, every line, tables included (lines are long; read ~80 to 120 lines at a time with
`sed -n 'A,Bp' FILE`). Write one TSV row per rule statement to your output file. Then write the cut-candidates file.
Then return the short report described at the end.

You are read-only on the repository: change nothing under `<main checkout>`, run no git command that
writes, send no messages, start no subagents, use no network. Write only your two output files.
Do not judge whether a rule is right. Do not skip a rule because it looks like a repeat: repeats are what we are counting.

## What is a rule statement
A sentence or clause that constrains what a conforming node, signer, reader, steward or implementation does or may do.
- Sentences with MUST, MUST NOT, SHALL, SHOULD, MAY, REQUIRED.
- Indicative sentences with rule force: "a roster is never enumerable outside its cohort", "the row is refused",
  "only the attester withdraws", "X is admitted only when Y", "expires after 72 h".
- A registry-table cell that states who signs, whom it names, how it is withdrawn, where it travels, and so on.

Not a rule statement: rationale ("because…"), worked examples, history, a bare definition that constrains nothing,
a bare pointer ("see CC 3.2"). A sentence that says a rule again while pointing elsewhere IS a row (`role` = restates).

Granularity: one row per distinct rule. A paragraph with five rules is five rows. A registry row whose rule cell
states signer, subject and withdrawal is three rows. If one sentence states the same rule for a list of families,
one row with the families listed.

## Output: `<name>.tsv`
Tab-separated, one header line, no tabs or newlines inside a field. Columns:

| # | column | value |
|---|---|---|
| 1 | file | `p1` … `p7` |
| 2 | line | line number in the file where the statement starts |
| 3 | section | the decimal of the nearest numbered heading at or above the line (headings look like ``### 3.4.5 `slug` — Title``); no "CC" prefix |
| 4 | scope | `kernel` (holds for every row or for rows in general) · `family` (about one family or a few named families) · `mechanism` (bytes, encodings, endpoints, transport, media) · `stewardship` · `foundation` |
| 5 | rule_key | one key from the vocabulary below |
| 6 | column | one family-model column from the list below, or `none` |
| 7 | families | comma-separated family stems the statement names (the word before the first `:` in a dimension name, e.g. `consent`, `hard_case`, `identity`); `*` if it speaks of all rows; empty if none |
| 8 | force | `MUST` · `MUST_NOT` · `SHOULD` · `MAY` · `is` (indicative with rule force) |
| 9 | role | `states` (reads as the rule's own full statement) · `restates` (says again, in summary or by pointer, a rule whose home is elsewhere) · `applies` (applies a general rule to one family or case) · `exception` (says this case departs from a general rule) |
| 10 | points_to | decimals of other sections the statement cites, comma-separated, no "CC" |
| 11 | gist | at most 30 words, self-contained, plain words: who may or must do what, to which rows, when. Write it so two statements of the same rule get nearly the same gist. |
| 12 | note | empty, or: a contradiction with another statement in your range (give its line), an ambiguity, or "table" if the statement is a table cell |

## rule_key vocabulary (closed; use `other:<short-slug>` only when none fits)
- `row_shape`: what a row or envelope is; required fields
- `signature`: what is signed; hybrid signature; when a signature is valid
- `admission_order`: order of checks at the door; refuse or hold; rules that depend on arrival order
- `registration`: a key must be registered or known; identity types
- `reserved_prefix`: a family admitted only from particular signers; reservation enforcement
- `signer`: who may sign a row of a family
- `subject`: whom a row may name; what the named party must have agreed to
- `placement`: the scope a row may sit at (self, family, room, community, federation, commons)
- `cosign`: rows needing more than one signature; thresholds; pending acts
- `policy_row`: the governance policy numbers, voting windows, reverse quorum
- `freshness`: the instant a row is judged at; freshness windows; clocks and skew
- `withdraw`: who may withdraw, recant or retract a row, what that does, and what may not be withdrawn
- `supersede`: replacement, latest-wins, tie-breaks, fields that only move one way
- `expiry`: expires_at, decay, time-to-live
- `standing`: the folded standing or roles of a key (member, moderator, owner, and so on)
- `roster_fold`: membership of selves, families, groups and rooms; join, leave, remove; who sees a roster
- `owner_binding`: ownership of nodes, agents, devices; resolving an owner
- `delegation`: `delegates_to`; attenuation; seats held by delegation
- `consent_fold`: consent grants and states; what consent permits or forbids
- `trust_fold`: whom a reader trusts; scores; aggregation; reference policies
- `audience`: who may be served or may hold a row; local and federation tiers; what is never enumerable; replication
- `announce`: announced and unannounced identities; listing; who serves a route
- `key_plane`: content keys, key grants, wraps, epochs, rotation on removal
- `erasure`: purge, tombstone, erasure requests, what is never purged
- `legal_hold`: preserve requests, lawful orders, archives
- `halt`: the accord halt, emergency shutdown, an agent's stop path
- `accord`: accord holders, hardware class, the accord's quorum
- `moderation`: moderation records, takedown, hard cases, review, watchlists
- `licensure`: licensure, capacity, detection, assurance ladders
- `minor_floor`: age; protections of minors
- `agent_identity`: an agent's identity record and its amendment, Wise Authority seat, deferral, retirement
- `amendment`: changing the Constitution or the registry
- `steward`: the trust root, steward duties, the genesis bundle
- `census`: mesh census, secret poll
- `settlement`: credits, ledgers, bonds, slashing
- `content_ingestion`: content families, content class and rating, provenance of content
- `trace`: reasoning traces, audit chain
- `wire`: canonical encoding, record ids, byte layouts
- `endpoint`: HTTP endpoint shapes
- `transport`: links, shaping, frames, onion routing, relays, forwarders
- `media`: calls, streams, chunks
- `transparency_log`: signed tree heads, witness cosigning
- `conformance`: conformance levels; what an implementation must do in general
- `principle`: a foundational principle stated with rule force

## column vocabulary
Existing model columns: `placement` (scope a row may sit at) · `signer_rule` (who may sign) · `subject_rule` (whom it
may name, constraints on the named party) · `cosign_rule` (further signatures required) · `body` (required or
forbidden body content) · `freshness` (instant judged at, window) · `lifecycle` (withdraw, supersede, expire, rotate)
· `replication` (tier, audience, who is served it) · `projection` (the derived table or read model) ·
`erasure_route` (how it is removed) · `governance` (the policy row binding it) · `evidence` (the claim or test that shows it).
Proposed columns for rules no existing column holds: `tie_break` · `monotone_field` · `evidence_screen` (a row counts
only if some evidence holds) · `signer_named_by_ref` (the signer is fixed by another row) · `formula` (a composition
or scoring formula) · `window` (a duration).
Use `none` for a rule that is not a per-family property.

## Output: `<name>.cuts.tsv`
Blocks in your range that are not rules and that a reader could lose without losing a rule, or that say a second time
what the range already says. Columns: `file`, `line_start`, `line_end`, `kind` (`rationale` · `example` · `history` ·
`restated_block` · `duplicate_table` · `informative`), `bytes` (rough), `note` (at most 20 words). Only blocks of 3 lines
or 1,000 bytes and up.

## Your return message (at most 250 words, plain text)
Row count; the ten rules most often repeated in your range (rule_key, gist, sections); every contradiction you saw
(lines); the three largest cut candidates. No preamble.
