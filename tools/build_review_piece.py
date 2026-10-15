#!/usr/bin/env python3
"""Assemble one reviewable piece of the CC into a self-contained packet.

    tools/build_review_piece.py P04            # writes review/packets/P04.md
    tools/build_review_piece.py --all          # every row of review/pieces.tsv
    tools/build_review_piece.py --check        # exit 1 if any piece prefix matches no section

A piece is a row of review/pieces.tsv: decimal-id prefixes to include and exclude,
extra files, the formal/ models that witness it, and the reviewer profile with standing
to kill. The packet carries the sections' text, the claims-register slice with status
counts, the open tickets the staged rows name, and the formal witnesses, so a reviewer
can judge the piece without the monolith.
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
TICKET = re.compile(r"\b(?:staged|open):([A-Za-z0-9_.-]+#\d+)")


def under(dec, prefix):
    return dec == prefix or dec.startswith(prefix + ".")


def load_pieces():
    with open(os.path.join(ROOT, "review", "pieces.tsv"), newline="") as f:
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
    r"""Reader rendering of one master line (#123: the master keeps the machine-parsed forms; the volume does not).

    - a section heading `## 4.2 \`accord\` — Accord — the layer` renders as `## 4.2 Accord: the layer`
      (slug dropped; the first dash inside the title becomes a colon);
    - a bold lead `**Rule (normative — steward ruling …).**` renders as `**Rule.** *(normative; steward ruling …)*`
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


def claims_slice(include, exclude):
    rows = []
    with open(os.path.join(CONST, "claims.tsv"), newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            d = r["decimal_id"]
            if include and not any(under(d, p) for p in include):
                continue
            if any(under(d, x) for x in exclude):
                continue
            rows.append(r)
    return rows


def formal_summary(dirs):
    out = []
    for d in dirs:
        p = os.path.join(ROOT, "formal", d)
        if not os.path.isdir(p):
            out.append(f"- `formal/{d}` — **missing**")
            continue
        names = set()
        for fn in os.listdir(p):
            fp = os.path.join(p, fn)
            if fn.endswith(".cfg"):
                with open(fp, encoding="utf-8") as fh:
                    cfg_lines = fh.read().split("\n")
                for ln in cfg_lines:
                    ln = ln.strip()
                    if ln and not ln.startswith(("\\*", "CONSTANT", "SPECIFICATION", "INIT", "NEXT", "CHECK_DEADLOCK", "SYMMETRY")) and not ln.startswith(("INVARIANT", "PROPERTY", "INVARIANTS", "PROPERTIES")) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", ln):
                        names.add(ln)
            if fn.endswith(".lean"):
                with open(fp, encoding="utf-8") as fh:
                    lean_src = fh.read()
                for m in re.finditer(r"^theorem\s+([A-Za-z_][A-Za-z0-9_']*)", lean_src, re.M):
                    names.add(m.group(1))
        out.append(f"- `formal/{d}` — {len(names)} checked names: " + ", ".join(f"`{n}`" for n in sorted(names)))
    return out


def render_pins(fp):
    out = ["*The pins: which commit of which repo each `impl:` / `test:` / `bench:` artefact was resolved against at the last re-pin.*", "",
           "| repo | commit | manifest | backed when |", "|---|---|---|---|"]
    with open(fp, newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            out.append(f"| {r['repo']} | `{r['commit']}` | `{r['manifest_path']}` | {r['backed_when']} |")
    return out


def render_register(fp):
    """The register as a volume (#123 volume 7): one row per claim, grouped by Part, with the status counts first."""
    rows = []
    with open(fp, newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    st = Counter(r["status"] for r in rows)
    kinds = Counter(r["evidence"].split(":", 1)[0] for r in rows)
    out = ["*Cover. This is what an auditor reads: every normative claim the constitution makes, the section it lives in, "
           "whether it is established (an artefact in a pinned commit backs it), staged (an open ticket will), normative "
           "(ruled, no artefact yet) or open; and the artefact itself. A status the artefact does not support is a defect "
           "of this volume, not of the text.*", "",
           f"{len(rows)} claims: " + ", ".join(f"**{k}** {v}" for k, v in sorted(st.items())) + ".",
           "Evidence kinds: " + ", ".join(f"`{k}` {v}" for k, v in sorted(kinds.items())) + ".", ""]
    def key(r):
        return [int(x) if x.isdigit() else 0 for x in r["decimal_id"].split(".")]
    part = None
    for r in sorted(rows, key=key):
        top = r["decimal_id"].split(".")[0]
        if top != part:
            part = top
            out += ["", f"### Part {part}", "", "| claim_id | CC | status | summary | evidence |", "|---|---|---|---|---|"]
        summ = r["summary"].replace("|", "\\|")
        summ = summ if len(summ) <= 160 else summ[:157] + "…"
        out.append(f"| `{r['claim_id']}` | {r['decimal_id']} | {r['status']} | {summ} | `{r['evidence'][:110]}` |")
    return out


def claims_coverage(pieces):
    """Every register row must map to exactly one prefix piece (a document piece with include '-' owns none)."""
    bad = []
    with open(os.path.join(CONST, "claims.tsv"), newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            d = r["decimal_id"]
            owners = [pid for pid, p in pieces.items()
                      if any(under(d, i) for i in split_list(p["include"])) and not any(under(d, x) for x in split_list(p["exclude"]))]
            if len(owners) != 1:
                bad.append((r["claim_id"], d, owners))
    return bad


def build(piece, pieces):
    inc, exc = split_list(piece["include"]), split_list(piece["exclude"])
    files, formal = split_list(piece["files"]), split_list(piece["formal"])
    chunks, missing = slice_sections(inc, exc) if inc else ([], [])
    rows = claims_slice(inc, exc) if inc else []
    status = Counter(r["status"] for r in rows)
    tickets = Counter()
    for r in rows:
        for t in TICKET.findall(r["evidence"]):
            tickets[t] += 1
    dep = sorted({p2["piece_id"] for p2 in pieces.values() if p2["piece_id"] != piece["piece_id"]
                  for x in exc if any(under(x, i2) or under(i2, x) for i2 in split_list(p2["include"]))})
    L = [f"# {piece['piece_id']} — {piece['title']}", "",
         f"*Review packet, generated by `tools/build_review_piece.py` from `review/pieces.tsv`. Do not edit; edit the sources.*", "",
         f"*Volume (#123): {piece.get('volume', '-')}*", "",
         "## Reviewer and standing", "", piece["reviewer_profile"], "",
         "## Scope", "",
         f"- Sections included: {', '.join('CC ' + p for p in inc) if inc else 'none (document piece)'}",
         f"- Sections excluded (reviewed elsewhere): {', '.join('CC ' + x for x in exc) if exc else 'none'}" + (f" → {', '.join(dep)}" if dep else ""),
         f"- Extra files: {', '.join('`' + f + '`' for f in files) if files else 'none'}", ""]
    if missing:
        L += [f"**WARNING: no section header found for prefix(es): {', '.join(missing)}**", ""]
    L += ["## Claims-register slice", "",
          f"{len(rows)} rows: " + ", ".join(f"{k} {v}" for k, v in sorted(status.items())) if rows else "No register rows map to this piece by decimal id.", ""]
    if tickets:
        L += ["Open tickets the staged rows name:", ""] + [f"- {t} ({n} row{'s' if n > 1 else ''})" for t, n in tickets.most_common()] + [""]
    if rows:
        L += ["| claim_id | CC | status | evidence |", "|---|---|---|---|"]
        for r in sorted(rows, key=lambda r: [int(x) if x.isdigit() else 0 for x in r["decimal_id"].split(".")]):
            L.append(f"| `{r['claim_id']}` | {r['decimal_id']} | {r['status']} | {r['evidence'][:90]} |")
        L.append("")
    L += ["## Formal witnesses", ""] + (formal_summary(formal) or ["none"]) + [""]
    for f in files:
        fp = os.path.join(ROOT, f)
        L += [f"## File: `{f}`", ""]
        if f.endswith("claims.tsv"):
            L += render_register(fp) + [""]
        elif f.endswith("evidence_pins.tsv"):
            L += render_pins(fp) + [""]
        elif f.endswith(".json"):
            L += [f"*(binary-ish manifest, {os.path.getsize(fp)} bytes; not inlined)*", ""]
        elif os.path.exists(fp):
            with open(fp, encoding="utf-8") as fh:
                L += [fh.read(), ""]
        else:
            L += ["**missing**", ""]
    for dec, hdr, text in chunks:
        L += [f"## Section CC {dec}", "", text, ""]
    return "\n".join(L), missing


def main(argv):
    pieces = load_pieces()
    if "--check" in argv:
        bad = 0
        for pid, p in pieces.items():
            _, missing = build(p, pieces)
            if missing:
                print(f"{pid}: no header for {missing}")
                bad += 1
        cov = claims_coverage(pieces)
        for cid, d, owners in cov[:20]:
            print(f"claim {cid} at {d}: owned by {owners or 'nobody'}")
        print(f"{len(pieces)} pieces, {bad} with unmatched prefixes, {len(cov)} claims not owned by exactly one piece")
        return 1 if (bad or cov) else 0
    ids = list(pieces) if "--all" in argv else [a for a in argv[1:] if a in pieces]
    if not ids:
        print(__doc__)
        return 2
    os.makedirs(os.path.join(ROOT, "review", "packets"), exist_ok=True)
    for pid in ids:
        text, missing = build(pieces[pid], pieces)
        out = os.path.join(ROOT, "review", "packets", f"{pid}.md")
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"{pid}: {len(text.split())} words -> review/packets/{pid}.md" + (f"  MISSING {missing}" if missing else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
