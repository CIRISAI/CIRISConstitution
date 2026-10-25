#!/usr/bin/env python3
"""Build the CIRIS Constitution PDF from the canonical constitution/ markdown.

Front matter is deliberately minimal: title, the Accord foreword (which sets the
tone), the Scope & Disclaimers, and an explicit chapter-level table of contents
built from constitution/toc.tsv -- then Parts I-VIII, then the Stewardship note.

Output: ciris_constitution-<VERSION>[.<build>].pdf (repo root; pre-release builds auto-iterate).
Deps: a TeX Live install providing pdflatex (newunicodechar, listings, titlesec,
hyperref, booktabs). Run:  python3 build_pdf.py
"""
import re, csv, sys, shutil, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOC = HERE / "constitution"
sys.path.insert(0, str(HERE / "tools"))
import _md2latex as B   # convert(), inline(), esc(), code_ascii(), NUC (stdlib-only, safe import)

B.NUC.update({"é": r"\'e", "↑": r"$\uparrow$", "↓": r"$\downarrow$",
              # RC3 additions: reject-vector control pictures (CC 2.3.2.1), R-policy
              # constraint subscripts (CC 6.1.5.1), citation diacritics (§8.6.1),
              # event-time sum + combining macron (Part VI)
              "␊": r"\textlangle LF\textrangle{}", "␣": r"\textvisiblespace{}",
              "₁": r"\textsubscript{1}", "₃": r"\textsubscript{3}",
              "Σ": r"$\Sigma$", "à": r"\`a", "ö": r"\"o",
              "̄": r"\textsuperscript{--}",
              "¶": r"\P{}", "Δ": r"$\Delta$", "σ": r"$\sigma$",
              "⌊": r"$\lfloor$", "⌋": r"$\rfloor$", "⌈": r"$\lceil$", "⌉": r"$\rceil$", "₀": r"\textsubscript{0}", "₂": r"\textsubscript{2}", "⅔": r"$2/3$",
              "⟨": r"$\langle$", "⟩": r"$\rangle$",
              "├": "+", "└": "+", "⟶": r"$\longrightarrow$",
              # effective-count glyphs (Part VI 6.1.2.1.2)
              "λ": r"$\lambda$", "κ": r"$\kappa$", "ℝ": r"$\mathbb{R}$",
              "∉": r"$\notin$", "∅": r"$\emptyset$",
              "": r"$\bar{\rho}$"})   # placeholder for ρ̄ (ρ + combining macron); see prefilter()
B.CODE_ASCII.update({"├": "+", "└": "+", "⟶": "-->"})
nuc_lines = "\n".join(r"\newunicodechar{%s}{%s}" % (k, v) for k, v in B.NUC.items())

VERSION = (HERE / "VERSION").read_text(encoding="utf-8").strip()
PARTS = sorted(DOC.glob("part_*.md"), key=lambda p: int(re.match(r"part_(\d+)_", p.name).group(1)))
PART_TITLE = {1: "Foundation", 2: "The Grammar", 3: "The Namespace", 4: "Composition & Governance",
              5: "Transport & Substrate", 6: "The Substrate", 7: "Lifecycle & Stewardship",
              8: "Appendices"}

def prefilter(md):
    md = re.sub(r"</?(sub|sup)>", "", md)
    md = re.sub(r"<br\s*/?>", "  ", md)
    md = (md.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'"))
    md = md.replace("ρ̄", "")   # ρ̄ (ρ + combining macron) -> single mapped placeholder
    return md

def evidence_appendix_md():
    """Generated Evidence Register (from constitution/claims.tsv) — the reviewer's
    'make the evidence as reviewable as the architecture', rendered into the PDF."""
    from collections import Counter
    rows = list(csv.DictReader(open(DOC / "claims.tsv"), delimiter="\t"))
    st = Counter(r["status"] for r in rows)
    def dk(d): return [999] if d == "corpus" else [int(x) for x in d.split(".")]
    rows.sort(key=lambda r: dk(r["decimal_id"]))
    out = ["# Evidence Register\n",
           "Generated from `constitution/claims.tsv`. Every load-bearing claim names the artifact that "
           "establishes it — **impl** (reference implementation), **test** (conformance vector), "
           "**lean** (mechanized proof), **bench** (evaluation) — or is **staged** against a named "
           "implementation, or an acknowledged **open** gap. The tag vocabulary and the four-artifact "
           "convention are defined in `constitution/EVIDENCE.md`; consistency (evidence pointers, the "
           "dual-ID spine, and normative coverage) is machine-checked by `tools/check_claims.py` as a CI gate.\n",
           f"**{len(rows)} claims** — established {st['established']} · staged {st['staged']} · open {st['open']}. "
           "Cross-repo pointers resolve against the pinned sibling spec-map manifests.\n",
           "| CC | Claim | Evidence | Status |",
           "|---|---|---|---|"]
    for r in rows:
        summ = r["summary"].replace("|", "/")
        if len(summ) > 66: summ = summ[:64].rstrip() + "…"
        ev = r["evidence"].replace("|", "/")
        out.append(f"| {r['decimal_id']} | {summ} | {ev} | {r['status']} |")
    return "\n".join(out)


def contents_md():
    """Explicit chapter-level TOC (decimal + semantic + title), grouped by Part."""
    rows = list(csv.DictReader(open(DOC / "toc.tsv"), delimiter="\t"))
    rows.sort(key=lambda r: [int(x) for x in r["decimal_id"].split(".")])
    out, cur = ["# Contents\n"], None
    for r in rows:
        dec = r["decimal_id"]; part = int(dec.split(".")[0])
        if dec == "1.14" or dec.startswith("1.14."):  # the parable is now the Foreword
            continue
        if part != cur:
            cur = part; out.append(f"\n## Part {part} — {PART_TITLE[part]}\n")
        if dec.count(".") == 1:                      # chapter level only
            out.append(f"- **{dec}** `{r['semantic_id']}` — {r['title'].strip()}")
    return "\n".join(out)

def preamble(title="The CIRIS Constitution", subtitle=None):
    return r"""\documentclass[11pt]{article}
\usepackage[a4paper,margin=2.4cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{newunicodechar}
\usepackage{amssymb,amsmath}
\usepackage{longtable,array,booktabs}
\usepackage{listings}
\usepackage{xcolor}
\definecolor{accent}{HTML}{2a4d69}
\usepackage[hidelinks]{hyperref}
\usepackage{titlesec}
\titleformat{\section}{\LARGE\bfseries\color{accent}}{}{0pt}{}[\vspace{2pt}\hrule]
\titleformat{\subsection}{\large\bfseries\color{accent!85}}{}{0pt}{}
\titleformat{\subsubsection}{\normalsize\bfseries}{}{0pt}{}
\titlespacing*{\section}{0pt}{16pt}{8pt}
\lstset{basicstyle=\ttfamily\scriptsize,breaklines=true,columns=fullflexible,
        keepspaces=true,frame=leftline,framerule=1pt,rulecolor=\color{accent!40},
        backgroundcolor=\color{accent!4},xleftmargin=8pt,aboveskip=6pt,belowskip=6pt}
\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}
\linespread{1.05}
\renewcommand{\arraystretch}{1.25}
""" + nuc_lines + r"""
\title{\vspace{-1cm}\Huge\bfseries\color{accent}""" + title + r"""\\[10pt]
\normalsize\mdseries """ + (subtitle or "Version " + VERSION) + r"""\\[6pt]\itshape Stewarded by Eric Moore}
\author{}\date{}
\begin{document}
\maketitle\thispagestyle{empty}
"""

def build_full():
    body = [preamble()]
    body.append(B.convert(prefilter((DOC / "EXECUTIVE_SUMMARY.md").read_text(encoding="utf-8"))))  # exec summary before the opening
    body.append(r"\clearpage")
    body.append(B.convert(prefilter((DOC / "FOREWORD.md").read_text(encoding="utf-8"))))   # foreword sets the tone
    body.append(r"\clearpage")
    body.append(B.convert(prefilter((DOC / "SCOPE_AND_DISCLAIMERS.md").read_text(encoding="utf-8"))))  # scope + disclaimers
    body.append(r"\clearpage")
    body.append(B.convert(contents_md()))                                                  # explicit contents
    body.append(r"\clearpage")
    for p in PARTS:
        body.append(B.convert(prefilter(p.read_text(encoding="utf-8"))))
        body.append(r"\clearpage")
    body.append(B.convert(prefilter(evidence_appendix_md())))                               # generated evidence register
    body.append(r"\clearpage")
    body.append(B.convert(prefilter((DOC / "STEWARDSHIP.md").read_text(encoding="utf-8"))))
    body.append(r"\end{document}")
    stem = f"ciris-constitution-{VERSION}"
    tex = HERE / f"{stem}.tex"
    tex.write_text("\n".join(body), encoding="utf-8")
    print(f"wrote {tex.name} (foreword + scope + contents + {len(PARTS)} parts)")
    return stem, tex


def _branch():
    import os
    if os.environ.get("PDF_BRANCH"):            # override for CI / testing
        return os.environ["PDF_BRANCH"]
    try:
        return subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=HERE,
                              capture_output=True, text=True).stdout.strip()
    except Exception:
        return ""

def versioned_pdf_name():
    """ciris_constitution-<VERSION>.pdf for releases AND for any build on main;
    pre-release builds off other branches carry an auto-iterating build number:
    -<VERSION>.<n>.pdf, with n read from whatever same-version build is sitting
    in the repo root (every rebuild iterates the value that is there; a version
    bump resets to 1). On merge to main the next build collapses the name to the
    bare version, and it stays there.

    Only SAME-VERSION files are ever swept. Earlier releases
    (ciris_constitution-1.0-rc3.pdf, -rc4.pdf, ...) persist in the tree so
    published links keep resolving, and CIRISConstitution-latest.pdf — the
    permalink, written by the finalize workflow on main — is never touched here.
    The fixed-name ciris_constitution.pdf is refreshed after the move, below.
    Returns (new_name, [stale same-version files])."""
    import glob as _glob
    clean = f"ciris_constitution-{VERSION}.pdf"
    numbered = re.compile(rf"ciris_constitution-{re.escape(VERSION)}\.(\d+)\.pdf$")
    same_version = [p for p in _glob.glob(str(HERE / "ciris_constitution-*.pdf"))
                    if Path(p).name == clean or numbered.search(p)]
    is_prerelease = re.search(r"rc\d", VERSION.lower()) is not None
    if not is_prerelease or _branch() == "main":
        return clean, [p for p in same_version if Path(p).name != clean]
    nums = [int(m.group(1)) for p in same_version if (m := numbered.search(p))]
    # The counter is monotonic across a finalize (#122 review): when main collapses
    # rc5.20 to the bare name it deletes the numbered file, and a branch cut from that
    # main would otherwise restart at .1 — a newer build with a smaller number. So the
    # tree is only the floor: every numbered same-version name git has ever seen, and
    # the number a finalize commit records ("from <V>.N"), raise it. A shallow clone
    # may see less history; the finalize message is there so it still sees the last one.
    nums += _history_build_numbers(numbered)
    nums += _floor_from_tree()
    n = max(nums, default=0) + 1
    name = f"ciris_constitution-{VERSION}.{n}.pdf"
    # Sweep only OTHER numbered builds. The finalized bare-name file, when main has
    # written one, stays beside the branch build: it is a published release name and
    # the next finalize overwrites it from the numbered build (cmp-based).
    return name, [p for p in same_version if Path(p).name not in (name, clean)]


COUNTER = HERE / "ciris_constitution.build"   # "<VERSION> <N>" — the floor, tracked in the tree


def _floor_from_tree():
    """The last build number recorded for this VERSION in the tracked counter file —
    the floor a depth-1 checkout can see when neither the deleted numbered file nor
    the finalize commit is in its history (#122 review)."""
    try:
        v, n = COUNTER.read_text(encoding="utf-8").split()
        return [int(n)] if v == VERSION else []
    except Exception:
        return []


def _record_floor(pdf_name):
    m = re.search(r"\.(\d+)\.pdf$", pdf_name)
    if m:
        COUNTER.write_text(f"{VERSION} {m.group(1)}\n", encoding="utf-8")


def _history_build_numbers(numbered):
    """Build numbers git remembers for this VERSION: numbered filenames ever added or
    deleted on any ref, plus the number a finalize commit message records."""
    out = []
    try:
        names = subprocess.run(
            ["git", "log", "--all", "--diff-filter=AD", "--name-only", "--format=",
             "--", f"ciris_constitution-{VERSION}.*.pdf"],
            cwd=HERE, capture_output=True, text=True, timeout=60).stdout.split()
        out += [int(m.group(1)) for p in names if (m := numbered.search(p))]
        msgs = subprocess.run(
            ["git", "log", "--all", "--format=%s", f"--grep=finalize {VERSION}"],
            cwd=HERE, capture_output=True, text=True, timeout=60).stdout
        out += [int(x) for x in re.findall(rf"from {re.escape(VERSION)}\.(\d+)", msgs)]
    except Exception:
        pass
    return out

def render_full(stem, tex):
    if not shutil.which("pdflatex"):
        print("pdflatex not found -- wrote .tex only; install TeX Live to render the PDF"); return
    for _ in range(2):  # two passes to resolve hyperref/toc references
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex.name],
                       cwd=HERE, check=True, stdout=subprocess.DEVNULL)
    pdf_name, stale = versioned_pdf_name()
    shutil.move(str(HERE / f"{stem}.pdf"), str(HERE / pdf_name))
    for p in stale:                       # one tracked PDF per version (same version only)
        Path(p).unlink(missing_ok=True)
    # Fixed-name permalink. This was the built PDF's name until d53f83a
    # introduced versioned names and deleted it here, which 404'd every
    # external link that predated the change. It is now always a byte copy
    # of the build just written, so raw/<branch>/ciris_constitution.pdf
    # resolves on any branch. Never swept: the stale-file glob requires a
    # "-" after the stem, so it cannot match this name.
    shutil.copyfile(str(HERE / pdf_name), str(HERE / "ciris_constitution.pdf"))
    _record_floor(pdf_name)               # a numbered build raises the tracked floor; a finalize leaves it
    for ext in (".aux", ".log", ".out", ".tex"):
        (HERE / f"{stem}{ext}").unlink(missing_ok=True)
    print(f"wrote {pdf_name}")


# ---------------------------------------------------------------- volumes (#123)
# One edition, several volumes: the same sections, the same decimal spine, cut by the
# `volume` column of review/pieces.tsv (a piece may feed two volumes). A volume opens
# with its plain-language cover (constitution/covers/<volume>.md). Volume PDFs are
# written under volumes/ and are not tracked; the full edition stays the file of record.
VOLUMES = ["charter", "constitution", "wire", "dictionary", "policies", "maths", "register", "threats", "digest"]
VOLUME_TITLE = {"charter": "The Charter", "constitution": "The Constitution", "wire": "The Wire",
                "dictionary": "The Dictionary", "policies": "The Reader's Policies", "maths": "The Mathematics",
                "register": "The Evidence Register", "threats": "The Threat Model", "digest": "The Digests"}
REVIEW = HERE / "review"
OMIT = re.compile(r"\*\[(\d+(?:\.\d+)*) reviewed in another piece — omitted here\]\*")


def _pieces():
    import build_review_piece as R
    return R, R.load_pieces()


def volume_pieces(vol):
    R, pieces = _pieces()
    return R, [p for p in pieces.values() if vol in R.split_list(p["volume"])]


def section_volumes():
    """decimal -> sorted list of volumes that print it (from pieces.tsv include/exclude)."""
    R, pieces = _pieces()
    rows = list(csv.DictReader(open(DOC / "toc.tsv", encoding="utf-8"), delimiter="\t"))
    out = {}
    for r in rows:
        dec = r["decimal_id"]; vols = set()
        for p in pieces.values():
            inc, exc = R.split_list(p["include"]), R.split_list(p["exclude"])
            if any(R.under(dec, x) for x in inc) and not any(R.under(dec, x) for x in exc):
                vols.update(R.split_list(p["volume"]))
        out[dec] = sorted(vols)
    return out


def write_toc_volumes():
    """Add/refresh the `volume` column of constitution/toc.tsv from the pieces map (generated; CI diffs it)."""
    path = DOC / "toc.tsv"
    lines = path.read_text(encoding="utf-8").split("\n")
    hdr = lines[0].split("\t")
    sv = section_volumes()
    if "volume" not in hdr:
        hdr.append("volume")
    vi = hdr.index("volume")
    out = ["\t".join(hdr)]
    for ln in lines[1:]:
        if not ln.strip():
            out.append(ln); continue
        cells = ln.split("\t")
        cells = (cells + [""] * (len(hdr) - len(cells)))[:len(hdr)]
        cells[vi] = " ".join(sv.get(cells[0], [])) or "-"
        out.append("\t".join(cells))
    new = "\n".join(out)
    changed = new != path.read_text(encoding="utf-8")
    path.write_text(new, encoding="utf-8")
    n = sum(1 for v in sv.values() if v)
    print(f"toc.tsv volume column: {n}/{len(sv)} sections placed; {'updated' if changed else 'unchanged'}")


def volume_md(vol):
    """The markdown of one volume: cover, then its sections in decimal order, grouped by Part."""
    cover = (DOC / "covers" / f"{vol}.md").read_text(encoding="utf-8")
    parts_md = [cover]
    if vol == "digest":
        for f in (DOC / "EXECUTIVE_SUMMARY.md", REVIEW / "pieces" / "00_guarantees_plain.md",
                  REVIEW / "pieces" / "00_operator_digest.md", REVIEW / "pieces" / "00_guarantees.md"):
            parts_md.append(f.read_text(encoding="utf-8"))
        return parts_md
    R, pieces = volume_pieces(vol)
    chunks = {}
    for p in pieces:
        cs, _missing = R.slice_sections(R.split_list(p["include"]), R.split_list(p["exclude"]))
        for dec, hdr, text in cs:
            chunks.setdefault(dec, text)
    # splice a child printed in this volume back into the parent's omission marker
    for dec in list(chunks):
        def splice(m):
            child = m.group(1)
            if child in chunks and child != dec:
                txt = chunks.pop(child)
                return txt
            return f"*[{m.group(1)} printed in another volume]*"
        chunks[dec] = OMIT.sub(splice, chunks[dec])
    for dec in list(chunks):
        chunks[dec] = OMIT.sub(lambda m: f"*[{m.group(1)} printed in another volume]*", chunks[dec])
    order = sorted(chunks, key=lambda d: [int(x) for x in d.split(".")])
    cur, group = None, []
    for dec in order:
        part = int(dec.split(".")[0])
        if part != cur:
            if group:
                parts_md.append("\n\n".join(group))
            cur, group = part, [f"# Part {part} — {PART_TITLE[part]}\n"]
        group.append(chunks[dec])
    if group:
        parts_md.append("\n\n".join(group))
    if vol == "charter":
        parts_md.insert(1, (DOC / "FOREWORD.md").read_text(encoding="utf-8"))
        parts_md.append((DOC / "STEWARDSHIP.md").read_text(encoding="utf-8"))
    if vol == "register":
        parts_md.append(evidence_appendix_md())
    return parts_md


def build_volume(vol):
    body = [preamble(f"The CIRIS Constitution: {VOLUME_TITLE[vol]}", f"A volume of edition {VERSION}")]
    for md in volume_md(vol):
        body.append(B.convert(prefilter(md)))
        body.append(r"\clearpage")
    body.append(r"\end{document}")
    vdir = HERE / "volumes"; vdir.mkdir(exist_ok=True)
    stem = f"ciris_constitution-{VERSION}-{vol}"
    tex = vdir / f"{stem}.tex"
    tex.write_text("\n".join(body), encoding="utf-8")
    if not shutil.which("pdflatex"):
        print(f"wrote {tex.name} (.tex only; no pdflatex)"); return None
    for _ in range(2):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex.name],
                       cwd=vdir, check=True, stdout=subprocess.DEVNULL)
    pages = None
    if shutil.which("pdfinfo"):
        info = subprocess.run(["pdfinfo", f"{stem}.pdf"], cwd=vdir, capture_output=True, text=True).stdout
        m = re.search(r"Pages:\s+(\d+)", info); pages = int(m.group(1)) if m else None
    for ext in (".aux", ".log", ".out", ".tex"):
        (vdir / f"{stem}{ext}").unlink(missing_ok=True)
    print(f"wrote volumes/{stem}.pdf" + (f" ({pages} pages)" if pages else ""))
    return pages


def build_volumes(which):
    vols = VOLUMES if which == "all" else [which]
    counts = {}
    for v in vols:
        if v not in VOLUMES:
            raise SystemExit(f"unknown volume {v!r}; one of {', '.join(VOLUMES)} or all")
        counts[v] = build_volume(v)
    if which == "all":
        sv = section_volumes()
        lines = [f"# Volumes of edition {VERSION}", "",
                 "One edition, one decimal spine, several volumes (CIRISConstitution#123). Built by "
                 "`python3 build_pdf.py --volume all`; the PDFs are not tracked, the full edition is the file of record. "
                 "Each volume opens with its plain-language cover from `constitution/covers/`.", "",
                 "| Volume | Sections | Pages |", "|---|---|---|"]
        for v in VOLUMES:
            n = sum(1 for vols in sv.values() if v in vols)
            lines.append(f"| {VOLUME_TITLE[v]} (`{v}`) | {n if v != 'digest' else 'digests + executive summary'} | {counts[v] or '—'} |")
        (HERE / "volumes" / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv):
    if "--write-toc-volumes" in argv:
        write_toc_volumes(); return
    if "--volume" in argv:
        build_volumes(argv[argv.index("--volume") + 1]); return
    stem, tex = build_full()
    render_full(stem, tex)


if __name__ == "__main__":
    main(sys.argv[1:])
