#!/usr/bin/env python3
"""The volume map: which sections print in which volume.

    tools/volume_map.py --check        # exit 1 if any prefix in constitution/volumes.tsv matches no section

A row of constitution/volumes.tsv names decimal-id prefixes to include and exclude, the
extra files printed with them, the formal/ models that witness them and the volumes they
feed. build_pdf.py reads this module to cut the nine volumes from the one edition.
"""
import csv, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONST = os.path.join(ROOT, "constitution")
PART_FILES = {"I": "part_1_foundation.md", "II": "part_2_the_grammar.md", "III": "part_3_the_namespace.md",
              "IV": "part_4_composition_governance.md", "V": "part_5_transport_substrate.md",
              "VI": "part_6_the_coherence_mathematics.md", "VII": "part_7_lifecycle_stewardship.md",
              "APP": "part_8_appendices.md"}
HDR = re.compile(r"^(#{2,6})\s+(\d+(?:\.\d+)*)\s+`([^`]+)`\s+—")


def under(dec, prefix):
    return dec == prefix or dec.startswith(prefix + ".")


def load_pieces():
    with open(os.path.join(ROOT, "constitution", "volumes.tsv"), newline="") as f:
        return {r["piece_id"]: r for r in csv.DictReader(f, delimiter="\t")}


def split_list(s):
    return [] if s.strip() in ("", "-") else s.split()


def headers(path):
    out = []
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    for i, ln in enumerate(lines):
        m = HDR.match(ln)
        if m:
            out.append((i, m.group(2), m.group(3), ln))
    return lines, out


LEAD = re.compile(r"\*\*([^*]+?)\s+\((normative|informative|entrenched)\s+—\s+([^)]*?)\)\s*([.:])\*\*")


def render_line(ln):
    r"""Reader rendering of one master line: the master keeps the machine-parsed forms; the volume does not.

    - a section heading `## 4.2 \`accord\` — Accord — the layer` renders as `## 4.2 Accord: the layer`
      (slug dropped; the first dash inside the title becomes a colon);
    - a bold lead `**Rule (normative — CC 4.2).**` renders as `**Rule.** *(normative; CC 4.2)*`
      so the rule is read before its citation.
    """
    m = HDR.match(ln)
    if m:
        hashes, dec, slug = m.group(1), m.group(2), m.group(3)
        title = ln[m.end():].strip()
        title = title.replace(" — ", ": ", 1)
        return f"{hashes} {dec} {title}"
    def lead(mm):
        label, kind, cite, punct = mm.group(1), mm.group(2), mm.group(3), mm.group(4)
        return f"**{label}{punct}** *({kind}; {cite})*"
    return LEAD.sub(lead, ln)


def slice_sections(include, exclude):
    """Return [(decimal, title_line, text)] for every included top prefix, excluded sub-prefixes cut out."""
    parts = {}
    for key, fn in PART_FILES.items():
        parts[key] = headers(os.path.join(CONST, fn))
    found = {p: False for p in include}
    # A whole-part prefix ("1", "7") has no header of its own: expand it to its top-level children.
    all_decs = {dec for (_, hs) in parts.values() for (_, dec, _, _) in hs}
    targets = []
    for p in include:
        if p in all_decs:
            targets.append((p, p))
        else:
            kids = sorted({d for d in all_decs if under(d, p) and d.count(".") == p.count(".") + 1},
                          key=lambda d: [int(x) for x in d.split(".")])
            if kids:
                found[p] = True
            targets += [(k, p) for k in kids]
    chunks = []
    for key, (lines, hs) in parts.items():
        for idx, (ln_no, dec, slug, hdr) in enumerate(hs):
            for p, src in targets:
                if dec != p:
                    continue
                found[src] = True
                end = len(lines)
                for (ln2, dec2, _, _) in hs[idx + 1:]:
                    if not under(dec2, p):
                        end = ln2
                        break
                keep = []
                i = ln_no
                while i < end:
                    m = HDR.match(lines[i])
                    if m and any(under(m.group(2), x) for x in exclude):
                        xdec = m.group(2)
                        j = i + 1
                        while j < end and not (HDR.match(lines[j]) and not under(HDR.match(lines[j]).group(2), xdec)):
                            j += 1
                        keep.append(f"*[{xdec} reviewed in another piece — omitted here]*")
                        i = j
                        continue
                    keep.append(render_line(lines[i]))
                    i += 1
                chunks.append((dec, hdr, "\n".join(keep)))
    missing = [p for p, ok in found.items() if not ok and re.match(r"^\d", p)]
    chunks.sort(key=lambda c: [int(x) for x in c[0].split(".")])
    return chunks, missing


def main(argv):
    pieces = load_pieces()
    bad = 0
    for pid, p in pieces.items():
        _, missing = slice_sections(split_list(p["include"]), split_list(p["exclude"]))
        if missing:
            print(f"{pid}: no header for {missing}")
            bad += 1
        for f in split_list(p["files"]):
            if not os.path.exists(os.path.join(ROOT, f)):
                print(f"{pid}: missing file {f}")
                bad += 1
    print(f"{len(pieces)} rows, {bad} with unmatched prefixes or missing files")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
