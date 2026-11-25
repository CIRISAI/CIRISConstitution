#!/usr/bin/env python3
"""build_refusal_tokens.py: the refusal, hold and hard-case names of the Parts, as one table.

manifests/refusal_tokens.tsv has one row per name the text refuses, holds or reports under: the name as
the text spells it, its kind, the section that states what it means, the line, and the sentence. It is
built from a review kept as data, formal/derivation/refusal_tokens_review.tsv, which gives every
candidate name a kind or the word not_a_token and a few words of why. The tool does not decide what a
name is; the review does. The tool finds each reviewed name's defining sentence and keeps the review
complete in both directions.

The kinds: refusal (the row or object is refused, Invalid or malformed under the name), hold (it waits
or is held), hard_case (a hard_case:{kind} record the substrate raises), http_code (an upper-case error
code of the HTTP surface, CC 5.3.6.1), report (a name a node reports that refuses nothing), and two the
text needed: concludes_nothing (the row is kept and has no effect: "concludes nothing", "not counted",
"contested") and detail (a finer name carried with another name: "with the detail", "with reason").

A candidate is a name in code ticks (snake_case with at least one underscore, lower or upper case), or a
hard_case:{kind} spelling anywhere (a fenced block included), that
  - stands in a sentence carrying one of the refusal words (WORDS: refused, rejected, Invalid, malformed,
    held, Waiting, waits, hard case, error, fault, fails, nothing, reported, reason, token, contested,
    not counted, dropped, denied, violation, detail), or next to such a sentence in its paragraph or
    its table row; or
  - closes a clause by itself (", `name`." or "(`name`)" or "else `name`"), or stands in a parenthesis
    that holds only names, or in a list item under a paragraph that ends in a colon on such a sentence; or
  - stands first in a cell of a table column whose header says Refusal, Fault, Error, Code, Reason, Token
    or Hard-case, or first in the first column of a table one of whose headers does; or
  - is a hard_case:{kind} spelling; or
  - is itself built from a refusal word (SHAPE: ..._mismatch, ..._violation, invalid_..., ..._too_large,
    ..._not_..., ..._unregistered, ...).
Sections CC 8.10 (the generated family cards) and CC 8.11 (the earlier form) are not read.

The defining sentence of a token is chosen by rank: a table row whose refusal column holds the name (the
whole row is the sentence), then a sentence with a refusal word that closes a clause on the name, then
any sentence with a refusal word, then a sentence next to one, then any sentence that carries it; ties
go to the earliest in the order of the Parts. A review row may pin the section (column `section`) where
the rank picks a mention over the definition, and one token with two meanings has two rows, each pinned;
a pin that no longer holds the name is an error.

  python3 tools/build_refusal_tokens.py              # write the manifest (refuses while the review has an error)
  python3 tools/build_refusal_tokens.py --check      # stale manifest, a reviewed name gone, an unreviewed candidate
  python3 tools/build_refusal_tokens.py --self-test  # the plants: unreviewed names caught, a deleted name caught
  python3 tools/build_refusal_tokens.py --candidates [--new] [--all]   # the candidates with their sentences
Exit 1 on any failure. Standard library only; the output is sorted by token.
"""
import os, re, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parts_text as P

ROOT = str(P.ROOT)
REVIEW = os.path.join(ROOT, "formal", "derivation", "refusal_tokens_review.tsv")
MANIFEST = os.path.join(ROOT, "manifests", "refusal_tokens.tsv")
KINDS = ("refusal", "hold", "hard_case", "http_code", "report", "concludes_nothing", "detail")
NOT = "not_a_token"
SKIP = ("8.10", "8.11")                      # generated family cards; the earlier form, kept on purpose
SPAN = re.compile(r"`([^`\n]+)`")
LOWER = re.compile(r"(?<![A-Za-z0-9_])[a-z][a-z0-9]*(?:_[a-z0-9]+)+(?![A-Za-z0-9_])")
UPPER = re.compile(r"(?<![A-Za-z0-9_])[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+(?![A-Za-z0-9_])")
HARD = re.compile(r"(?<![A-Za-z0-9_])hard_case:([a-z][a-z0-9_]*)")
# The refusal words. Read on the sentence with its code spans taken out, so a name never triggers itself here.
WORDS = re.compile(r"\b(?:refus(?:e|es|ed|al|als|ing)|reject(?:s|ed|ion|ing)?|invalid|malformed|held|waiting|waits?|"
                   r"hard[- ]cases?|errors?|faults?|fail(?:s|ed|ure|ures)?|nothing|reported|reasons?|tokens?|"
                   r"contested|not counted|does not count|dropped|denied|violations?|details?)\b", re.I)
HEADER = re.compile(r"refusal|fault|error|code|reason|token|hard-case", re.I)
# A name that closes a clause by itself (", `name`." or "(`name`)") is how the text gives a refusal its name.
CLOSES_L = re.compile(r"(?:,\s*|\(\s*|\bas\s+|\bis\s+|\bunder\s+|\belse\s+)\**`$")
CLOSES_R = re.compile(r"^`\**\s*(?:[.;:)]|$)")
# A parenthesis that holds nothing but names: "(`a`, `b` and `c`)".
NAMES_ONLY = re.compile(r"\((?:\s*\**`[^`\n]+`\**\s*(?:,|;|/|\band\b|\bor\b)?)+\s*\)")
# A name built from a refusal word is a candidate wherever it stands.
SHAPE = re.compile(r"(?:^|_)(?:mismatch|violation|invalid|malformed|refused|rejected|unregistered|unreceipted|"
                   r"equivocation|too_large|too_long|too_many|error|failed|missing|unknown|unsupported|"
                   r"not|no|below|exceeds|exceeded|expired|stale|partial|lags|conflict|"
                   r"un(?:available|resolved|met|authori[sz]ed|seated|signed|verified|trusted|bound|placed|anchored|"
                   r"sorted|named|announced|licensed|representable|reviewed|discharged|acknowledged|attested|settled))"
                   r"(?:_|$)", re.I)


def skipped(sec):
    return any(sec == s or sec.startswith(s + ".") for s in SKIP)


def names_in(line, fenced):
    """(name, start) for every name the line spells: in code ticks, or a hard_case spelling anywhere."""
    out = []
    spans = [(0, len(line))] if fenced else [(m.start(1), m.end(1)) for m in SPAN.finditer(line)]
    for a, b in spans:
        seg = line[a:b]
        taken = []
        for m in HARD.finditer(seg):
            out.append(("hard_case:" + m.group(1), a + m.start()))
            taken.append((m.start(), m.end()))
        if fenced:
            continue
        for rx in (LOWER, UPPER):
            for m in rx.finditer(seg):
                if any(s <= m.start() < e for s, e in taken) or m.group(0) == "hard_case":
                    continue
                out.append((m.group(0), a + m.start()))
    return out


def cells_of(row):
    """The cells of a table row with their offsets in the line."""
    out, ticked, start = [], False, None
    for i, ch in enumerate(row):
        if ch == "`":
            ticked = not ticked
        if ch == "|" and not ticked and (i == 0 or row[i - 1] != "\\"):
            if start is not None:
                out.append((start, row[start:i]))
            start = i + 1
    return out


def pieces(text, base):
    """The sentences of a span, each with its offset in the line."""
    out, at = [], 0
    for s in P.sentences(text):
        k = text.find(s, at)
        if k < 0:
            k = at
        out.append((base + k, s))
        at = k + len(s)
    return out


def occurrences(parts):
    """Every spelling of a name in the Parts: dicts with token, part, line, section, sentence, how it
    stands (column: in a refusal column of a table; worded: with a refusal word in its sentence; near:
    next to such a sentence, or in a naming position; plain) and whether it closes a clause."""
    out = []
    for part in sorted(parts):
        text = parts[part]
        lines = text.split("\n")
        secs = P.section_of_lines(text)
        fenced, header, lead = False, None, False
        for i, l in enumerate(lines):
            st = l.strip()
            if st.startswith("```"):
                fenced, header = not fenced, None
                continue
            if skipped(secs[i]):
                continue
            if fenced:
                for name, _ in names_in(l, True):
                    out.append(dict(token=name, part=part, line=i + 1, section=secs[i], sentence=st, how="plain"))
                continue
            if st.startswith("|"):
                cells = cells_of(l)
                if header is None:
                    header = [bool(HEADER.search(c)) for _, c in cells]
                    continue
                if all(re.fullmatch(r"\s*:?-+:?\s*", c) for _, c in cells):
                    continue
                sents, col_of = [], []
                for ci, (off, c) in enumerate(cells):
                    for o, s in pieces(c, off):
                        sents.append((o, s))
                        col_of.append(ci)
            else:
                header = None
                if not st:
                    continue
                if P.HEAD.match(l):
                    lead = False
                    continue
                sents, col_of = pieces(l, 0), None
                item = bool(P.LIST_ITEM.match(l))
            listed = [(m.start(), m.end()) for m in NAMES_ONLY.finditer(l)]
            hot = [bool(WORDS.search(SPAN.sub(" ", P.LINK.sub(r"\1", s)))) for _, s in sents]
            if col_of is None and not item:        # a paragraph that ends in a colon leads the list under it
                lead = st.rstrip("*").endswith(":") and bool(hot) and hot[-1]
            under = col_of is None and item and lead
            for name, at in names_in(l, False):
                k = max((j for j, (o, _) in enumerate(sents) if o <= at), default=0) if sents else None
                if k is None:
                    continue
                how, closes = "plain", bool(CLOSES_L.search(l[:at]) and CLOSES_R.match(l[at + len(name):]))
                if under or closes or any(a <= at < b for a, b in listed):
                    how = "near"
                if hot[k]:
                    how = "worded"
                elif (k > 0 and hot[k - 1]) or (k + 1 < len(hot) and hot[k + 1]):
                    how = "near"
                if col_of is not None and header and any(header):
                    ci = col_of[k]
                    first = sents[k][1].lstrip().lstrip("*").startswith("`" + name.split(":")[0])
                    if (ci < len(header) and header[ci] and first) or (ci == 0 and first):
                        how = "column"
                said = " | ".join(c.strip() for _, c in cells) if how == "column" else sents[k][1]   # a table row states it whole
                out.append(dict(token=name, part=part, line=i + 1, section=secs[i],
                                sentence=re.sub(r"\s+", " ", said.replace("\t", " ")).strip(), how=how,
                                closes=closes))
    return out


def candidates(occ):
    """token -> its occurrences, for every name that looks like a refusal name somewhere."""
    by = defaultdict(list)
    for o in occ:
        by[o["token"]].append(o)
    return {t: v for t, v in by.items()
            if t.startswith("hard_case:") or SHAPE.search(t) or any(o["how"] != "plain" for o in v)}


def read_review(path=REVIEW):
    rows, errs = {}, []
    lines = [l.rstrip("\n") for l in open(path, encoding="utf-8") if l.strip() and not l.startswith("#")]
    if lines[0].split("\t") != ["token", "kind", "section", "why"]:
        return {}, ["review: the header is not token, kind, section, why"]
    for l in lines[1:]:
        c = l.split("\t")
        if len(c) != 4:
            errs.append(f"review: {c[0]}: {len(c)} columns"); continue
        tok, kind, sec, why = c
        if (tok, sec) in rows or (not sec and any(t == tok for t, _ in rows)) or (sec and (tok, "") in rows):
            errs.append(f"review: {tok}: listed twice (a second meaning names its own section on both rows)")
        if kind not in KINDS and kind != NOT:
            errs.append(f"review: {tok}: unknown kind {kind}")
        if kind == NOT and sec:
            errs.append(f"review: {tok}: not_a_token takes no section")
        if not why:
            errs.append(f"review: {tok}: no reason given")
        rows[(tok, sec)] = (kind, why)
    return rows, errs


def define(tok, sec, occs):
    """The defining occurrence of a token: by rank, earliest first; within the pinned section when one is given."""
    pool = [o for o in occs if not sec or o["section"] == sec]
    if not pool:
        return None
    order = {"column": 0, "worded": 2, "near": 3, "plain": 4}
    return min(pool, key=lambda o: (order[o["how"]] - (o["how"] == "worded" and o.get("closes", False)), o["part"], o["line"]))


def build(parts, review):
    """(manifest rows, errors). A row is (token, kind, section, part_line, sentence)."""
    occ = occurrences(parts)
    by = defaultdict(list)
    for o in occ:
        by[o["token"]].append(o)
    rows, errs = [], []
    for (tok, sec), (kind, _why) in sorted(review.items()):
        if kind == NOT:
            if tok not in by:
                errs.append(f"{tok}: reviewed as not_a_token and the Parts no longer carry it (drop the review row)")
            continue
        d = define(tok, sec, by.get(tok, []))
        if d is None:
            where = f" in CC {sec}" if sec else ""
            errs.append(f"{tok}: reviewed as {kind} and no longer stands in the Parts{where}")
            continue
        rows.append((tok, kind, d["section"], f"{d['part']}:{d['line']}", d["sentence"]))
    reviewed = {t for t, _ in review}
    for tok, v in sorted(candidates(occ).items()):
        if tok not in reviewed:
            o = define(tok, "", v)
            errs.append(f"{tok}: looks like a refusal name and is not in the review "
                        f"({o['part']}:{o['line']}, CC {o['section']}): {o['sentence'][:160]}")
    return sorted(rows), errs


def render(rows):
    return "token\tkind\tsection\tpart_line\tsentence\n" + "".join("\t".join(r) + "\n" for r in rows)


def self_test(review):
    """The plants. Returns the list of those not caught."""
    parts = P.load()
    base = build(parts, review)[1]
    missed = []
    # (c) a made-up name, said to be refused, in a copy of Part 3.
    p = dict(parts)
    lines = p["p3"].split("\n")
    at = next(i for i, l in enumerate(lines) if re.match(r"#+ 3\.2 ", l))
    lines[at + 1:at + 1] = ["", "A row whose head is planted is refused as `planted_head_never_reviewed`.", ""]
    p["p3"] = "\n".join(lines)
    got = [e for e in build(p, review)[1] if e not in base]
    if not any(e.startswith("planted_head_never_reviewed: looks like a refusal name") for e in got):
        missed.append("an unreviewed refusal name planted in Part 3 was not caught")
    # (c) again, by the hard_case spelling alone, in a sentence with no refusal word.
    p = dict(parts)
    p["p5"] = p["p5"] + "\n\nThe substrate emits `hard_case:planted_kind_never_reviewed` at that instant.\n"
    got = [e for e in build(p, review)[1] if e not in base]
    if not any(e.startswith("hard_case:planted_kind_never_reviewed: looks like") for e in got):
        missed.append("an unreviewed hard_case kind planted in Part 5 was not caught")
    # (b) a reviewed token deleted from every Part.
    tok = next(t for (t, _), (k, _w) in sorted(review.items()) if k == "refusal" and "_" in t)
    p = {k: v.replace(tok, "x") for k, v in parts.items()}
    got = [e for e in build(p, review)[1] if e not in base]
    if not any(e.startswith(f"{tok}: reviewed as refusal and no longer stands") for e in got):
        missed.append(f"the reviewed token {tok}, deleted from the Parts, was not caught")
    # A plant inside a section that is not read must not be reported.
    p = dict(parts)
    lines = p["p8"].split("\n")
    at = next(i for i, l in enumerate(lines) if re.match(r"#+ 8\.11\.1 ", l))
    lines[at + 1:at + 1] = ["", "A row is refused as `planted_in_the_earlier_form`.", ""]
    p["p8"] = "\n".join(lines)
    if any("planted_in_the_earlier_form" in e for e in build(p, review)[1]):
        missed.append("a name planted in CC 8.11 (not read) was reported")
    return missed


def main(argv):
    parts = P.load()
    if "--candidates" in argv:
        occ = occurrences(parts)
        seen = {t for t, _ in read_review()[0]} if os.path.exists(REVIEW) else set()
        for tok, v in sorted(candidates(occ).items()):
            if "--new" in argv and tok in seen:
                continue
            for o in sorted(v, key=lambda o: ({"column": 0, "worded": 1, "near": 2, "plain": 3}[o["how"]], o["part"], o["line"]))[:3 if "--all" not in argv else None]:
                print(f"{tok}\t{o['how']}\t{o['section']}\t{o['part']}:{o['line']}\t{o['sentence'][:500]}")
        return 0
    review, errs = read_review()
    if "--self-test" in argv:
        missed = self_test(review)
        for m in missed:
            print("refusal tokens: plant not caught: " + m)
        print(f"refusal tokens: self-test, {4 - len(missed)} of 4 plants behave")
        return 1 if missed else 0
    rows, more = build(parts, review)
    errs += more
    text = render(rows)
    if "--check" in argv:
        have = open(MANIFEST, encoding="utf-8").read() if os.path.exists(MANIFEST) else ""
        if have != text:
            errs.append("manifests/refusal_tokens.tsv is stale: run tools/build_refusal_tokens.py")
    elif not errs:
        with open(MANIFEST, "w", encoding="utf-8") as f:
            f.write(text)
    for e in errs:
        print("refusal tokens: error: " + e)
    n = {k: sum(1 for r in rows if r[1] == k) for k in KINDS}
    nots = sum(1 for v in review.values() if v[0] == NOT)
    print(f"refusal tokens: {len(rows)} rows; " + ", ".join(f"{k} {v}" for k, v in n.items())
          + f"; {len(review)} reviewed, {nots} not a token; {len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
