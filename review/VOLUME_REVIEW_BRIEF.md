# Brief: review one rendered volume of the CIRIS Constitution 1.0-rc11 (SWOT)

You are reviewing ONE PDF volume of the CIRIS Constitution as a reader would receive it. The steward
wants a quick, honest lay of the land: which volumes need the most care before 1.0, and why. Read the
rendered PDF, not the markdown. Read ALL of it: the Read tool takes `pages` ranges of at most 20 pages
per call, so page through the whole volume (the page count is given below). Do not skim the second
half. Do not read other files unless a sentence sends you there (then one lookup at most).

Context you need: the Constitution is one document in eight Parts, printed as nine volumes, each a
different lens for a different reader (its first page says who it binds). It is a release candidate
("released as guidance"). Its house rules: the Parts state rules, not history (no ruling attributions,
dates on rules, rc history, ticket links, code pointers, editorializing); plain English; RFC 2119
keywords carry the normative load; comparative claims about other projects are not allowed; every
claim is meant to be backed by a register row. Banned words: humane, dignified, graceful, farewell,
"last word". The volumes are built from markdown by a LaTeX pipeline, so rendering defects (overfull
tables, literal `**` or `\`, missing glyphs, broken numbering, headings that run off the page, code
blocks clipped, empty sections, duplicated text) are in scope and valuable.

## What to produce (exactly this structure, markdown, no preamble)

```
# <Volume title> (<file name>, <N> pages)

**Care score:** <1–5>  (1 = ship as is, 5 = needs a rewrite pass before 1.0)
**One-line verdict:** <one sentence>

## Strengths
- <bullet, with page refs like (p. 12)>

## Weaknesses
- <bullet with page ref; quote the offending words in "quotes" when short>

## Opportunities
- <what a modest edit would buy; be concrete>

## Threats
- <what would embarrass the document in front of a hostile reviewer, regulator, implementer or
  lawyer; a contradiction between two pages; a claim stated stronger than its evidence; a leftover
  from an earlier design>

## Top defects (ranked, at most 8)
| # | Page | Kind | What | Suggested fix |
|---|---|---|---|---|
(kinds: contradiction / stale / rendering / overclaim / unclear rule / editorializing / banned word /
duplicate / numbering / other)

## Rendering
- <every rendering defect you saw, with page; or "none seen">

## Effort estimate
<one sentence: hours of editing, and whether it is mechanical or needs the steward's rulings>
```

Rules for the review: be specific and sparing. A weakness without a page number is worthless. Do not
praise. Do not propose new mechanisms or new policy; you are reviewing the text as a document. If two
pages contradict each other, that is the most valuable finding you can report — quote both. Flag any
sentence that reads as history, attribution, marketing, or a comparison with another project. Flag
numbers quoted in prose that you cannot see the source of. If the volume is clean, say so and give it
a 1 or 2; do not invent findings to fill the template.

A note on dates: the text cites publications and events from 2026, gathered by web search on the dates it
states. A citation dated after your training data is not thereby fabricated; if you cannot verify it, say
"unverifiable from here", not "invented".
