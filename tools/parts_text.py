#!/usr/bin/env python3
"""The Parts read as prose: sections, paragraphs, sentences and the sections a sentence cites.

A shared reader for the text lints (tools/check_restatements.py, tools/check_text_lints.py). It is
not a check. A paragraph is a run of non-blank lines, or one list item; a fenced block, a table
row, an HTML comment, a heading and the generated sections (written by a tool from a table) are not
prose and are never read. Every function takes the Parts as a dict {part: text} so a check can read a
planted copy of the text through the same code it reads the real text with.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = {"p1": "part_1_foundation.md", "p2": "part_2_the_grammar.md", "p3": "part_3_the_namespace.md",
         "p4": "part_4_composition_governance.md", "p5": "part_5_transport_substrate.md",
         "p6": "part_6_the_coherence_mathematics.md", "p7": "part_7_lifecycle_stewardship.md",
         "p8": "part_8_appendices.md"}
FILE_PART = {v: k for k, v in PARTS.items()}
# Sections whose body a tool writes from a table: CC 2.6.1.7 (build_cc_signed_object.py) and the
# family cards of CC 8.10 (family_card.py). Their sentences are the table's, not the prose's.
GENERATED = ("2.6.1.7", "8.10")
HEAD = re.compile(r"^(#{1,6}) (.*)$")
DEC = re.compile(r"^(\d+(?:\.\d+)*) ")
# A citation: "CC 4.5.13" in the words, or a link whose anchor is a decimal section.
CITE_TEXT = re.compile(r"\bCC (\d+(?:\.\d+)*)")
CITE_ANCHOR = re.compile(r"\]\((?:part_\d_[a-z_]+\.md)?#(\d+(?:\.\d+)*)\)")
LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


def load():
    return {p: (ROOT / "constitution" / f).read_text(encoding="utf-8") for p, f in PARTS.items()}


def headings(text):
    """(line index, depth, number or None, title) for every heading outside a fenced block."""
    out, fenced = [], False
    for i, l in enumerate(text.split("\n")):
        if l.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        m = HEAD.match(l)
        if m:
            d = DEC.match(m.group(2))
            out.append((i, len(m.group(1)), d.group(1) if d else None, m.group(2)))
    return out


def section_of_lines(text):
    """For each line index, the decimal number of the numbered section it sits in ('' before the first)."""
    lines = text.split("\n")
    sec, cur, heads = [""] * len(lines), "", {h[0]: h for h in headings(text)}
    for i in range(len(lines)):
        h = heads.get(i)
        if h and h[2]:
            cur = h[2]
        sec[i] = cur
    return sec


def generated(sec):
    return any(sec == g or sec.startswith(g + ".") for g in GENERATED)


def paragraphs(parts, which=None):
    """Prose paragraphs: dicts with part, line (1-based), section, text (the raw lines joined by a space)."""
    out = []
    for part, text in parts.items():
        if which and part not in which:
            continue
        lines = text.split("\n")
        secs = section_of_lines(text)
        fenced, comment, buf, start = False, False, [], 0

        def flush():
            if buf:
                out.append({"part": part, "line": start + 1, "section": secs[start], "text": " ".join(buf)})
            buf.clear()
        for i, l in enumerate(lines):
            s = l.strip()
            if s.startswith("```"):
                flush(); fenced = not fenced; continue
            if fenced:
                continue
            if comment:
                if "-->" in s:
                    comment = False
                continue
            if s.startswith("<!--") and "-->" not in s:
                flush(); comment = True; continue
            if (not s or s.startswith("|") or HEAD.match(l) or s in ("---", "***") or generated(secs[i])
                    or (s.startswith("<!--") and s.endswith("-->"))):
                flush(); continue
            if LIST_ITEM.match(l) or (s.startswith(">") and buf and not buf[-1].startswith(">")):
                flush()
            if not buf:
                start = i
            buf.append(s)
        flush()
    return out


def plain(raw):
    """The words of a raw span: link markup to its text, emphasis and code ticks dropped, a trailing comment removed."""
    t = re.sub(r"<!--.*?-->", "", raw)
    t = LINK.sub(r"\1", t)
    t = re.sub(r"^\s*(?:[-*+]|\d+[.)]|>)\s+", "", t)
    return t.replace("**", "").replace("`", "")


SPLIT = re.compile(r"(?<=[.!?])(?:\*\*|\*|[\"”’)])*\s+(?=[A-Z*`\[(_\"“‘\x00])")


def sentences(raw):
    """The sentences of a raw paragraph, each as its raw span (link markup kept, so its citations can be read).
    A bold lead that ends in a full stop is a sentence of its own."""
    t = raw
    # Hide the full stops of decimals, abbreviations and link targets so they never end a sentence.
    keep = {}

    def hide(m):
        k = f"\x00{len(keep)}\x00"
        keep[k] = m.group(0)
        return k
    t = re.sub(r"\]\([^)]*\)", hide, t)
    t = re.sub(r"`[^`]*`", hide, t)
    t = re.sub(r"\b(?:e\.g|i\.e|cf|vs|etc|et al|Art|No|Fig|approx|resp)\.", hide, t)
    out = []
    for s in SPLIT.split(t):
        for k, v in keep.items():
            s = s.replace(k, v)
        if s.strip():
            out.append(s.strip())
    return out


def words(raw):
    return len(plain(raw).split())


def cites(raw):
    """The decimal sections a raw span cites, by "CC x.y" or by a link anchor."""
    return set(CITE_TEXT.findall(raw)) | set(CITE_ANCHOR.findall(raw))


def cites_any(cited, homes):
    """True when a cited section is one of the homes or inside one."""
    return any(c == h or c.startswith(h + ".") for c in cited for h in homes)
