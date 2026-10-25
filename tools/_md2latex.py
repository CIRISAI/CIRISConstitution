#!/usr/bin/env python3
"""Assemble an exhaustively-complete CEG 1.0-RC29 PDF from the markdown spec.
No pandoc available -> a focused markdown->LaTeX converter for this spec's
subset (headings, pipe tables, code fences, lists, inline bold/italic/code/links,
blockquotes), pdflatex + newunicodechar for the 42 special glyphs.

Front matter: title + a hand-written PQC-streaming model section (clean LaTeX
with the matplotlib figures + a TikZ stack diagram). Then the full spec.
"""
import re, glob, sys
from pathlib import Path

D = Path(__file__).parent
SPEC = D.parent

# ---- spec file order: README (overview) then 00..17 ----
FILES = ["README.md"] + sorted(f.name for f in SPEC.glob("[0-9][0-9]_*.md"))

# ---------------------------------------------------------------- escaping
SPECIAL = {'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#',
           '_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
def esc(s):
    return ''.join(SPECIAL.get(c, c) for c in s)

# ASCII fallbacks for unicode INSIDE code blocks (verbatim can't use newunicodechar)
CODE_ASCII = {'§':'S','—':'--','→':'->','←':'<-','≤':'<=','≥':'>=','∈':'in','‖':'||',
   '²':'^2','³':'^3','⁴':'^4','⁵':'^5','⁶':'^6','⁰':'^0','¹':'^1','⁷':'^7','⁸':'^8','⁹':'^9','✅':'[x]','↔':'<->','·':'*','×':'x','–':'-',
   '∧':'/\\','≠':'!=','│':'|','…':'...','≡':'==','±':'+-','─':'-','𝒞':'C','−':'-',
   '⊇':'>=','∩':'^','┐':'+','┘':'+','✓':'[ok]','á':'a','⚠':'(!)','️':'','∃':'exists',
   'ρ':'rho','⌈':'|','⌉':'|','∪':'U','≫':'>>','≈':'~=','🔴':'(R)','┌':'+','┴':'+',
   '┬':'+','├':'+','┤':'+','┼':'+','╔':'+','╗':'+','╚':'+','╝':'+','║':'|','═':'=',
   # the formula blocks (Part VI n_eff / k_eff, Part III capacity predicates): spelled out,
   # since verbatim cannot draw them; a middle dot in code is a multiplication
   'Σ':'sum','∀':'forall','⇒':'=>','⟹':'=>','≔':':=','∉':'not in','⊆':'subset of','∅':'{}'}
def code_ascii(s):
    return ''.join(CODE_ASCII.get(c, c if ord(c)<128 else '?') for c in s)

CHUNK = 10  # a code run with no separator breaks every CHUNK characters ...
RUN = 24    # ... but only when the run is longer than RUN (a bare hex digest)
SEP = re.compile(r'(?<=[_:/.\-])')  # a code token may break after one of these


def code_runs(t):
    """The pieces of a code token between its break points: split after _ : / . - ; a piece
    longer than RUN (no separator in sight) is cut every CHUNK characters."""
    out = []
    for p in SEP.split(t):
        out += [p[k:k+CHUNK] for k in range(0, len(p), CHUNK)] if len(p) > RUN else [p]
    return [p for p in out if p]


def inline(s):
    """Inline markdown -> LaTeX. Operates on already-escaped-safe segments."""
    # links [text](url) -> text (drop url to avoid overflow; refs are self-describing)
    s = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', s)
    # inline code `x` -> \texttt{escaped}
    def breakable(t):
        # a long token with no spaces (a key id, a dotted path) may break after its separators,
        # so a table cell never clips it and a pasted identifier keeps its pieces whole; only a
        # run with no separator (a hex digest) falls back to fixed chunks
        if len(t) <= 12 or ' ' in t:
            return esc(t)
        return r'\allowbreak{}'.join(esc(p) for p in code_runs(t))
    # code spans are stashed first so that bold / italic markers may wrap them
    # (**`token`** is common); the stash marker survives esc() untouched
    codes = []
    def stash(m):
        codes.append(r'\texttt{' + breakable(m.group(1)) + '}')
        return '\x01%d\x01' % (len(codes) - 1)
    t = esc(re.sub(r'`([^`]*)`', stash, s))
    # bold first, so its content may hold *italic* or a stashed code span; the closer is the
    # first ** not followed by a third star, so **a *b*** closes after the italic and
    # ***x*** is bold italic
    t = re.sub(r'\*\*(?!\s)(.+?)(?<!\s)\*\*(?!\*)', r'\\textbf{\1}', t)
    # a star opens emphasis only when it touches the next character and closes it only when
    # it touches the previous one (the flanking rule), and never after a colon, so a bare
    # glob such as capacity:* or capacity:*; and a multiplication a * b are literal stars
    t = re.sub(r'(?<![*:])\*(?![\s*])([^*]+?)(?<![\s*])\*(?!\*)', r'\\textit{\1}', t)
    t = t.replace('**', '')   # an unmatched ** (a bold run spanning lines) prints nothing
    return re.sub('\x01(\\d+)\x01', lambda m: codes[int(m.group(1))], t)

def split_row(line):
    """A table row's cells. An escaped pipe (\\|) is a literal bar inside a cell, not a
    column break: the registry tables write closed vocabularies as `a \\| b \\| c`."""
    return [c.strip().replace('\x02', '|') for c in line.strip().replace('\\|', '\x02').strip('|').split('|')]

NAV = re.compile(r'^\[.←.*\]\(.*\)\s*\|.*\|.*\)\s*$|^\[←|Next:.*→')
def is_nav(line):
    return bool(re.search(r'\]\(\d\d_.*\.md\)', line)) and '|' in line

# ---------------------------------------------------------------- tables
PT = {r'\small': 10, r'\footnotesize': 9, r'\scriptsize': 8}   # point size of each table size
WIDE = 7           # a table with this many columns is set in landscape
TALL = 0.9         # a row taller than this share of the page cannot sit in a longtable (a row never breaks)
TYPICAL = 0.25     # a table whose middle row is taller than this share of the page reads better as row blocks


def cell_tex(c):
    """A table cell: a long bare token (beside:signature, a dotted path) gets break points at its
    separators so the column never clips it; code spans break the same way inside inline()."""
    def tok(t):
        if len(t) > 12 and ' ' not in t and not t.startswith('`'):
            return re.sub(r'([:_./\-])', lambda m: m.group(1) + '​', t)
        return t
    return inline(' '.join(tok(t) for t in c.split(' ')))


def table(header, rows):
    """A pipe table as LaTeX lines. Three shapes: a longtable whose column widths follow the
    content; the same in landscape when the table is WIDE; and, when a row would stand taller
    than TALL of the page or the typical row taller than TYPICAL of it (the guarantee table,
    whose cells run to hundreds of characters), a run of row blocks -- one short paragraph per row, the first cell in bold as its label, then
    "Header: cell" pairs -- so nothing can run off a page."""
    import math
    ncol = len(header)
    wide = ncol >= WIDE
    sz = r'\small' if wide else (r'\scriptsize' if ncol >= 4 else r'\footnotesize')
    # character widths in cm at this size: typewriter 0.525 em, text about 0.47 em on average
    em = PT[sz] * 0.0352
    mono, text = 0.525 * em, 0.47 * em
    # a column can never be narrower than its longest unbreakable run: a code span breaks at
    # its separators (code_runs), a plain token longer than 12 characters at : _ . / -
    # (cell_tex), a shorter one not at all
    def longest_run(c):
        best = 0
        for t in c.split(' '):
            if t.startswith('`'):
                best = max(best, max((len(x) for x in code_runs(t.strip('`'))), default=0) * mono + 0.25)
            elif len(t) > 12:
                best = max(best, max((len(x) for x in re.split(r'[:_./\-]', t)), default=0) * text + 0.2)
            else:
                best = max(best, len(t) * text + 0.2)
        return best
    lens = [max([len(header[k])] + [len(r[k]) for r in rows]) for k in range(ncol)]
    floors = [max([longest_run(header[k])] + [longest_run(r[k]) for r in rows]) for k in range(ncol)]
    # each column also costs two \tabcolsep (0.6 cm) plus a rule; keep the sum of the
    # p-widths inside the text width after that overhead (24.9 cm across a landscape page)
    avail = max(8.0, (24.1 if wide else 15.4) - 0.5 * ncol)
    floors = [min(f, avail / ncol * 1.5) for f in floors]
    rest = max(0.0, avail - sum(floors))
    # each column's share of the rest is the square root of its longest-cell length (damped
    # so one long note does not starve the others)
    shares = [math.sqrt(max(l, 4)) for l in lens]
    total = sum(shares) or 1.0
    ws = [round(f + rest * sh / total, 2) for f, sh in zip(floors, shares)]
    scale = avail / sum(ws)
    ws = [round(w * scale, 2) for w in ws]
    # row heights: the lines of each row's narrowest-fitting cell times the line height
    line = PT[sz] * 1.2 * 1.25 * 0.0352
    heights = sorted(max(math.ceil(len(c) * text / w) for c, w in zip(r, ws)) * line for r in rows) or [0]
    page = 16.2 if wide else 24.9
    if heights[-1] > TALL * page or heights[len(heights) // 2] > TYPICAL * page:
        out = [r'{\footnotesize']
        for r in rows:
            out.append(r'\par\medskip\noindent{\normalsize\textbf{%s}}\par' % cell_tex(r[0]))
            for h, c in zip(header[1:], r[1:]):
                if c.strip():
                    out.append(r'\textit{%s:} %s\par' % (inline(h), cell_tex(c)))
        out.append(r'\medskip}')
        return out
    colspec = '|' + '|'.join(f'p{{{w}cm}}' for w in ws) + '|'
    out = [r'\begin{landscape}'] if wide else []
    out.append(r'{%s' % sz)
    out.append(r'\begin{longtable}{%s}\hline' % colspec)
    out.append(' & '.join(r'\textbf{%s}' % inline(c) for c in header) + r' \\ \hline\endhead')
    for r in rows:
        out.append(' & '.join(cell_tex(c) for c in r) + r' \\ \hline')
    out.append(r'\end{longtable}}')
    if wide:
        out.append(r'\end{landscape}')
    return out


HEAD = {1:r'\section*{%s}',2:r'\subsection*{%s}',3:r'\subsubsection*{%s}',
        4:r'\paragraph{%s}\mbox{}\\',5:r'\subparagraph{%s}\mbox{}\\',6:r'\subparagraph{%s}\mbox{}\\'}

def item_follows(lines, j):
    """True when a numbered item comes after line j with only bullets, blank lines and indented
    lines between: the bullets at j are then a step's sub-points, not a list of their own."""
    while j < len(lines):
        ln = lines[j]
        if re.match(r'^\s*\d+\.\s+', ln):
            return True
        if not (ln.strip() == '' or re.match(r'^\s*[-*]\s+', ln) or re.match(r'^\s+\S', ln)):
            return False
        j += 1
    return False


def convert(md):
    out, i, lines = [], 0, md.split('\n')
    n = len(lines)
    while i < n:
        line = lines[i]
        # code fence
        if line.lstrip().startswith('```'):
            i += 1; buf = []
            while i < n and not lines[i].lstrip().startswith('```'):
                buf.append(code_ascii(lines[i])); i += 1
            i += 1
            # a one-line fence is a formula set off from the prose; the frame rule beside a
            # single line reads as a stray bar, so it is indented instead
            out.append(r'\begin{lstlisting}' + ('[frame=none,xleftmargin=16pt]' if len(buf) == 1 else ''))
            out.extend(buf)
            out.append(r'\end{lstlisting}')
            continue
        # nav line -> drop
        if is_nav(line):
            i += 1; continue
        # heading
        m = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m:
            lvl = len(m.group(1)); txt = inline(m.group(2))
            out.append(HEAD[lvl] % txt); out.append(''); i += 1; continue
        # table: header row '|...|' followed by separator '|---|'
        if line.strip().startswith('|') and i+1 < n and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i+1]):
            header = split_row(line)
            ncol = len(header); i += 2; rows = []
            while i < n and lines[i].strip().startswith('|'):
                cells = split_row(lines[i])
                cells = (cells + ['']*ncol)[:ncol]
                rows.append(cells); i += 1
            tl = table(header, rows)
            # a short lead-in just before the table (a heading, a bold label line) must not stand
            # alone at the foot of a page with the table on the next: it asks for room first, and
            # before a landscape table (which opens a new page) it moves onto that page
            k = len(out)
            while k > 0 and out[k-1] == '':
                k -= 1
            lead = None
            if k > 0 and len(out[k-1]) < 160 and out[k-1].startswith(('\\section', '\\subsection', '\\subsubsection', '\\paragraph', '\\subparagraph', '\\textbf{')):
                lead = out[k-1]; del out[k-1:]
                k = len(out)
                while k > 0 and out[k-1] == '':
                    k -= 1
            if tl[0] == r'\begin{landscape}':
                # consecutive wide tables (the signed-object table is several) share one
                # landscape run instead of each opening a half-empty page
                if k > 0 and out[k-1] == r'\end{landscape}':
                    del out[k-1:]; del tl[0]
                if lead:
                    at = 1 if tl[0] == r'\begin{landscape}' else 0
                    tl[at:at] = [r'\Needspace*{10\baselineskip}', lead, '']
            elif lead:
                tl[0:0] = [r'\Needspace*{10\baselineskip}', lead, '']
            out.extend(tl); out.append(''); continue
        # blockquote
        if line.startswith('>'):
            buf = []
            while i < n and lines[i].startswith('>'):
                buf.append(inline(lines[i].lstrip('>').strip())); i += 1
            out.append(r'\begin{quote}\itshape ' + ' '.join(buf) + r'\end{quote}'); out.append('')
            continue
        # hrule
        if re.match(r'^\s*---+\s*$', line) or re.match(r'^\s*===+\s*$', line):
            i += 1; continue
        # unordered list
        if re.match(r'^\s*[-*]\s+', line):
            out.append(r'\begin{itemize}\setlength\itemsep{0pt}')
            while i < n and re.match(r'^\s*[-*]\s+', lines[i]):
                out.append(r'\item ' + inline(re.sub(r'^\s*[-*]\s+','',lines[i]))); i += 1
                # a blank line between items does not end the list (the master writes lists both ways)
                if i + 1 < n and lines[i].strip() == '' and re.match(r'^\s*[-*]\s+', lines[i+1]):
                    i += 1
            out.append(r'\end{itemize}'); out.append(''); continue
        # ordered list
        if re.match(r'^\s*\d+\.\s+', line):
            out.append(r'\begin{enumerate}\setlength\itemsep{0pt}')
            expect = None
            while i < n and (m := re.match(r'^\s*(\d+)\.\s+', lines[i])):
                num = int(m.group(1))
                if num != expect:            # the number the markdown gives is the one printed
                    out.append(r'\setcounter{enumi}{%d}' % (num - 1))
                expect = num + 1
                out.append(r'\item ' + inline(lines[i][m.end():])); i += 1
                # what sits between this item and the next belongs to this item: bullets (the
                # master writes a step's sub-points as bullets under it, indented or not) and
                # indented continuation lines; blank lines between do not end the list
                while True:
                    j = i
                    while j < n and lines[j].strip() == '':
                        j += 1
                    if j >= n or re.match(r'^\s*\d+\.\s+', lines[j]):
                        i = j if j < n else i; break
                    bullet = re.match(r'^\s*[-*]\s+', lines[j])
                    indented = re.match(r'^\s+\S', lines[j]) and not lines[j].lstrip().startswith(('```', '|', '#'))
                    if not (bullet or indented) or not (indented or item_follows(lines, j)):
                        break
                    if bullet:
                        out.append(r'\begin{itemize}\setlength\itemsep{0pt}')
                        while j < n and (re.match(r'^\s*[-*]\s+', lines[j]) or
                                         (lines[j].strip() == '' and j + 1 < n and re.match(r'^\s*[-*]\s+', lines[j+1]))):
                            if lines[j].strip():
                                out.append(r'\item ' + inline(re.sub(r'^\s*[-*]\s+', '', lines[j])))
                            j += 1
                        out.append(r'\end{itemize}')
                    else:
                        out.append(''); out.append(inline(lines[j].strip())); j += 1
                    i = j
            out.append(r'\end{enumerate}'); out.append(''); continue
        # blank
        if not line.strip():
            out.append(''); i += 1; continue
        # paragraph
        out.append(inline(line)); out.append(''); i += 1
    return '\n'.join(out)

# ---------------------------------------------------------------- preamble
NUC = {
 '§':r'\S','—':'---','→':r'$\rightarrow$','←':r'$\leftarrow$','≤':r'$\leq$','≥':r'$\geq$',
 '∈':r'$\in$','‖':r'$\|$','²':r'\textsuperscript{2}','³':r'\textsuperscript{3}',
 '⁴':r'\textsuperscript{4}','⁵':r'\textsuperscript{5}','⁶':r'\textsuperscript{6}','⁰':r'\textsuperscript{0}','¹':r'\textsuperscript{1}','⁷':r'\textsuperscript{7}','⁸':r'\textsuperscript{8}','⁹':r'\textsuperscript{9}','✅':r'[\checkmark]','↔':r'$\leftrightarrow$',
 '·':r'\textperiodcentered{}','×':r'$\times$','–':'--','∧':r'$\wedge$','≠':r'$\neq$',
 '│':'|','…':r'\ldots{}','≡':r'$\equiv$','±':r'$\pm$','─':'-','𝒞':r'$\mathcal{C}$',
 '−':'-','⊇':r'$\supseteq$','⊆':r'$\subseteq$','≔':r'$:=$','∩':r'$\cap$','┐':'+','┘':'+','✓':r'\checkmark{}','á':r"\'a",
 '⚠':r'[!]','️':'','∃':r'$\exists$','ρ':r'$\rho$','⌈':r'$\lceil$','⌉':r'$\rceil$',
 '∪':r'$\cup$','≫':r'$\gg$','≈':r'$\approx$','🔴':r'[\textbullet]','⇒':r'$\Rightarrow$',
 '⟹':r'$\Longrightarrow$','∞':r'$\infty$','µ':r'$\mu$','ε':r'$\varepsilon$',
 'Θ':r'$\Theta$','Σ':r'$\Sigma$','Δ':r'$\Delta$','λ':r'$\lambda$','σ':r'$\sigma$','κ':r'$\kappa$',
 '₀':r'\textsubscript{0}','₁':r'\textsubscript{1}','₂':r'\textsubscript{2}','₃':r'\textsubscript{3}',
 '∉':r'$\notin$','∅':r'$\emptyset$','⅔':r'$\frac{2}{3}$','ℝ':r'$\mathbb{R}$','↑':r'$\uparrow$','↓':r'$\downarrow$',
 '⌊':r'$\lfloor$','⌋':r'$\rfloor$','⟨':r'$\langle$','⟩':r'$\rangle$','⟶':r'$\longrightarrow$','\u200b':r'\allowbreak{}',
}
nuc_lines = '\n'.join(r'\newunicodechar{%s}{%s}' % (k, v) for k, v in NUC.items())

PREAMBLE = r'''\documentclass[10pt]{article}
\usepackage[a4paper,margin=2cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{newunicodechar}
\usepackage{amssymb,amsmath}
\usepackage{longtable}
\usepackage{array}
\usepackage{pdflscape}
\usepackage{needspace}
\usepackage{graphicx}
\usepackage{listings}
\usepackage{xcolor}
\usepackage[hidelinks]{hyperref}
\usepackage{tikz}
\usetikzlibrary{positioning,arrows.meta,fit,backgrounds}
\usepackage{titlesec}
\titleformat{\section}{\Large\bfseries\color{black!80}}{}{0pt}{}
\lstset{basicstyle=\ttfamily\scriptsize,breaklines=true,columns=fullflexible,
        frame=single,framerule=0.2pt,rulecolor=\color{black!25},
        backgroundcolor=\color{black!3},xleftmargin=4pt,aboveskip=4pt,belowskip=4pt}
\setlength{\parindent}{0pt}\setlength{\parskip}{4pt}
\renewcommand{\arraystretch}{1.15}
''' + nuc_lines + r'''
\title{\textbf{CEG --- The CIRIS Epistemic Grammar}\\[4pt]\large Version 1.0-RC29 (Release Candidate --- wire surface frozen) --- Exhaustively Complete Reference\\[2pt]\normalsize with the PQC Streaming Bandwidth/Lag Model}
\author{CIRIS Federation --- generated from \texttt{FSD/CEG/}}
\date{2026-06-15}
\begin{document}
\maketitle
\begin{abstract}\noindent
This document is the complete CEG 1.0-RC29 wire-format specification (the 1+4
minimal-and-adequate attestation grammar), assembled from the 18-section source
plus the version-history overview. It opens with a quantitative model of
PQC-native streaming video --- bandwidth and lag --- under CEG \S10.5, isolating
the scale ``long tail'' (the per-epoch O(N) key cascade and the transport-bound
realtime lag), then presents the normative spec in full.
\end{abstract}
\tableofcontents
\clearpage
'''

# ---------------------------------------------------------------- model section (hand-written, clean)
MODEL = r'''
\section*{0. PQC Streaming Video --- Bandwidth/Lag Model (``the toy'')}
\addcontentsline{toc}{section}{0. PQC Streaming Bandwidth/Lag Model}

An analytical, parametric model of CEG \S10.5 streaming under the mandatory PQC
envelope (\S10.5.3 \texttt{wrap\_algorithm:v2} = X25519+ML-KEM-768; \S10.5.2
AES-256-GCM chunk seal; hybrid Ed25519+ML-DSA-65 signatures). Every constant is
sourced from the spec or the relevant FIPS standard. \textbf{The single free
parameter is Reticulum transport RTT/throughput} --- CEG defers transport to RET,
so this is the one empirical input that turns the parametric model into concrete
numbers.

\subsection*{0.1 The CEG/RET vs TCP/IP stack}
\begin{center}
\begin{tikzpicture}[node distance=2pt,
  layer/.style={draw,rounded corners,minimum width=5.4cm,minimum height=0.72cm,align=center,font=\footnotesize},
  ceg/.style={layer,fill=blue!8}, ip/.style={layer,fill=black!5}]
\node[ip] (app2) {Application (HTTP/SMTP/RTP\ldots)};
\node[ip,below=of app2] (tls) {TLS / PKI (X.509 CA)};
\node[ip,below=of tls] (tcp) {TCP / UDP};
\node[ip,below=of tcp] (ip) {IP / DNS / BGP};
\node[ip,below=of ip] (link2) {Link (Ethernet/Wi-Fi/\ldots)};
\node[font=\small\bfseries,above=6pt of app2] {TCP/IP stack};
\node[ceg,right=2.4cm of app2] (ceg) {CEG --- 1+4 attestation grammar\\(\S3 + \S5 namespace)};
\node[ceg,below=of ceg] (deliv) {Delivery axis \S10.5\\(stream/epoch DEK, STH, receipts)};
\node[ceg,below=of deliv] (res) {Resolution \S8.13.1.1\\(community $\rightarrow$ member $\rightarrow$ dest)};
\node[ceg,below=of res] (ret) {Reticulum (RET)\\dest-hash, announce, Links};
\node[ceg,below=of ret] (link3) {Link (LoRa/TCP/serial/\ldots)};
\node[font=\small\bfseries,above=6pt of ceg] {CEG/RET stack};
\draw[-Latex] (ceg)--(deliv); \draw[-Latex] (deliv)--(res); \draw[-Latex] (res)--(ret); \draw[-Latex] (ret)--(link3);
\end{tikzpicture}
\end{center}

\noindent Trust is intrinsic (signed quorum), not bolted on: \textbf{PKI/CA $\rightarrow$ hybrid
signatures + founder-quorum}; \textbf{DNS $\rightarrow$ \texttt{resolve\_community}};
\textbf{A-record $\rightarrow$ signed \texttt{transport\_destination}}; \textbf{IP routing
$\rightarrow$ RET announce/path-request}.

\subsection*{0.2 Per-message PQC sizes (derived)}
\begin{center}\footnotesize
\begin{tabular}{|l|r|l|}\hline
\textbf{Object} & \textbf{Bytes} & \textbf{Composition}\\\hline
Hybrid epoch-DEK grant (v2) & 4{,}669 & X25519 32 + ML-KEM-768 ct 1088 + wrapped DEK 48 + hybrid sig 3373 + env 128\\\hline
Per-stream STH & 3{,}485 & root 32 + sizes 16 + log\_id 64 + hybrid sig 3373\\\hline
AES-GCM tag / 1 MiB chunk & 16 & 0.0015\% content overhead\\\hline
ML-DSA-65 sig / Ed25519 sig & 3{,}309 / 64 & FIPS 204 / RFC 8032\\\hline
ML-KEM-768 ciphertext & 1{,}088 & FIPS 203\\\hline
\end{tabular}
\end{center}

\subsection*{0.3 Findings}
\begin{enumerate}\setlength\itemsep{2pt}
\item \textbf{PQC is not the bandwidth bottleneck --- content fan-out is.} The
AES-256-GCM content overhead is 0.0015\% at a 1 MiB chunk. At scale the dominant
cost is unicast content replication (e.g.\ $\sim$2 Tbps for 1M viewers at 2 Mbps),
which is the CDN / broadcast-relay-tree problem (1.x), independent of crypto.
\item \textbf{The PQC ``long tail'' is the per-rekey key cascade under churn ---
and \emph{removal coalescing}, not delivery topology, is what makes it
affordable.} Each \emph{gated-roster} member-removal forces an epoch rotation
(\S10.5.3 forward-secrecy). \textbf{Churn honesty (1.0-RC1 correction, \#71 C1):}
earlier drafts modeled churn$=$3{,}600/hr at N$=$1M (0.36\%/hr) --- $\sim$2 orders
below realistic broadcast-audience churn ($\sim$30\%/hr). At 30\%/hr with naive
per-removal rotation the flat-unicast cascade is $\sim$\textbf{3.1 Tbps ---
exceeding the $\sim$2 Tbps content fan-out itself}; the ``cascade $<$2\% of
content'' headline does NOT survive realistic churn unmitigated. The normative
mitigations (\S10.5.3): \textbf{(i) removal coalescing} --- all removals within
one STH window (T$=$2 s) batch into ONE rotation, capping the epoch rate at 1/T
\emph{regardless of churn} ($\leq$1{,}800 epochs/hr $\rightarrow$ $\sim$18.7 Gbps
flat-unicast at N$=$1M, $\sim$0.9\% of content fan-out; removed-viewer exposure
$\leq$ 2 s --- the grain the equivocation window already accepts); \textbf{(ii)
the public-broadcast exemption} --- an ungated \texttt{listed:public} roster has
no confidentiality claim against departed viewers, so removal forces no rotation
at all. With coalescing the three delivery regimes (hybrid grant 4.56 KiB;
TreeKEM commit $\sim$1.2 KiB/node, depth$=$20) keep their shape: \textbf{(a)
flat, unicast --- O(N) --- $\sim$18.7 Gbps} (the 1.0 shape); \textbf{(b) tree,
multicast --- O(log N) --- $\sim$0.1 Mbps} --- the 1.x lever, \emph{cheap only if
efficient multicast exists}; \textbf{(c) tree, unicast --- O(N log N) --- WORSE
than flat.} The tree's advantage remains multicast aggregation; whether efficient
multicast exists over the mesh is the open transport question of \S0.4.
\emph{(Two published self-corrections now stand in this item: the
$\log^2$/15 Mbps asymptotic error, and the 3{,}600/hr churn understatement ---
both caught in review, both kept on record per the \S1.4 honesty discipline.)}
Fig.~\ref{fig:cascade}.
\item \textbf{Lag is transport-bound, not crypto-bound.} Per-chunk AES seal/open
is $\sim$$\mu$s; the ML-KEM-768 DEK decap is $\sim$30 $\mu$s \emph{once per epoch}.
Glass-to-glass lag is dominated by chunk/segment duration, STH cadence (T=2s for
accountable broadcast), and \textbf{Reticulum Link RTT}. Fig.~\ref{fig:lag}.
\item \textbf{Join cost is dominated by RNS path-setup, not the handshake.} The
hybrid KEX (ML-KEM encap+decap) + signature verify are sub-millisecond; RNS path
establishment is the variable. Fig.~\ref{fig:join}.
\end{enumerate}

\subsection*{0.4 Do we have enough detail? (yes, parametrically)}
\textbf{Sufficient and pinned:} all crypto sizes (FIPS 203/204, RFC 8032), the
AES-GCM chunk overhead, cadence constants (K=64, T=2s, MAX\_CHUNKS/epoch=$2^{24}$,
1 MiB chunk), and cascade complexity (flat O(N), tree O(log N) with multicast, O(N log N) without).
\textbf{Parametric (RC1-7 unratified):} K, T, MAX\_CHUNKS --- the model is a
function of them. \textbf{The one missing empirical input:} Reticulum transport
characteristics (Link RTT, throughput, MTU, path-setup time) per interface ---
CEG defers transport to RET, so the lag term is a free parameter. Over IP-backed
RNS, assume $\sim$internet RTT + small RNS overhead (realtime video feasible);
over LoRa, seconds (realtime infeasible; store-and-forward only). \textbf{To go
parametric $\rightarrow$ concrete, measure RNS Link RTT/throughput on the target
interfaces.} The O($\log$N) tree (1.x) and SFU relay (1.x) are modelled with
standard complexity, not yet spec-detailed.

\subsection*{0.5 Comparison to other PQC streaming proposals}
The modern E2E-media stack the industry is converging on is \textbf{MLS (group key,
TreeKEM) + SFrame (per-frame AEAD) + hybrid-PQC KEM + PQC-TLS transport}; the
crypto trio everyone lands on is \textbf{ML-KEM-768 + ML-DSA-65 + AES-256-GCM}
(Zoom's shipped PQC E2EE; the Frontiers 2025 authenticated-PQC-session paper;
NIST FIPS 203/204). \textbf{CEG \S10.5 is structurally the same stack} --- we
independently arrived at the converged design, which is the strongest validation
of the crypto choices.

\begin{center}\scriptsize
\begin{tabular}{|p{2.6cm}|p{2.4cm}|p{2.4cm}|p{2.4cm}|p{3.2cm}|}\hline
 & \textbf{Zoom PQC E2EE} & \textbf{MLS+SFrame (IETF)} & \textbf{WebRTC DTLS-SRTP} & \textbf{CEG \S10.5} \\\hline
KEM & ML-KEM-768 & hybrid ML-KEM (agile) & (PQ-DTLS exploratory) & \textbf{hybrid X25519+ML-KEM-768} \\\hline
Per-frame AEAD & AES-GCM & AES-GCM / CTR+HMAC & SRTP & AES-256-GCM (STREAM nonce) \\\hline
Group rekey & key tree & \textbf{TreeKEM O(log N)} & n/a (SFU sees plaintext) & flat O(N) 1.0 $\rightarrow$ MLS-tree (RFC 9420) 1.x, multicast-dependent \\\hline
Transparency log & none & none & none & \textbf{per-stream STH (RFC 6962) + receipts} \\\hline
Identity / trust & Zoom accounts & app-supplied & X.509 / fingerprints & federation keys + founder-quorum, DNS-free \\\hline
Topology & central SFU & delivery-service & SFU/P2P & RET mesh, no central server \\\hline
Maturity & \textbf{shipped at scale} & \textbf{standardized} & \textbf{battle-tested} & pre-1.0 \\\hline
\end{tabular}
\end{center}

\noindent\textbf{Where CEG is unique:} it composes media with the federation's
transparency log + identity + governance + payments under \emph{one} grammar
(the same 1+4 set), DNS-free over RET, no central server or CA --- the per-stream
STH (anti-equivocation: a producer can't show different chunk-K to different
viewers), delivery receipts, and settlement linkage have no equivalent in
Zoom/MLS/SFrame. \textbf{Where CEG is behind (honest):} MLS \emph{ships} TreeKEM
today (our O(log N) tree is 1.x); Zoom \emph{ships} PQC E2EE at scale; WebRTC's
transport is battle-tested where RNS realtime media is unproven (our open
RTT question). \textbf{Crib list} (\S0.7): adopt MLS TreeKEM (RFC 9420) verbatim
for the 1.x tree rather than reinvent; consider SFrame framing to ride
standardization; revisit the forward-only (no-PCS) choice against MLS's PCS.

\subsection*{0.6 Concrete numbers from a transport profile}
Feeding representative transport assumptions into the model (\texttt{concretize.py};
replace with \texttt{rns\_transport\_bench.py} measurements):
\begin{center}\footnotesize
\begin{tabular}{|p{4.6cm}|r|r|r|l|}\hline
\textbf{transport (RTT)} & \textbf{realtime call} & \textbf{broadcast} & \textbf{join} & \textbf{verdict}\\\hline
IP-backed RNS, same region (35 ms) & 115 ms & 2.4 s & 71 ms & interactive-grade\\\hline
IP-backed RNS, cross-region (140 ms) & 220 ms & 2.5 s & 282 ms & OK ($<$400 ms)\\\hline
LoRa SF7 (1.2 s) & 1280 ms & 3.6 s & $\sim$10 s & store-and-forward only\\\hline
\end{tabular}
\end{center}
\noindent Over IP-backed RNS, PQC realtime video is interactive-grade; the crypto
contributes sub-millisecond. (Illustrative pending real RNS measurement.)

\subsection*{0.7 Per-operation benchmark + crib findings}
Measured here (pyca/cryptography); PQC rows from published liboqs (AVX2);
cross-check target = ciris-crypto \texttt{benches/federation\_crypto.rs}.
\begin{center}\footnotesize
\begin{tabular}{|p{5.2cm}|r|r|l|}\hline
\textbf{operation} & \textbf{$\mu$s/op} & \textbf{wire B} & \textbf{source}\\\hline
X25519 ECDH & 23.2 & 32 & measured\\\hline
Ed25519 sign / verify & 20 / 69 & 64 & measured\\\hline
AES-256-GCM seal/open (1 MiB) & 144 / 141 & +16/chunk & measured (58 GB/s)\\\hline
ML-KEM-768 encaps / decaps & $\sim$30 / $\sim$25 & ct 1088 & liboqs\\\hline
ML-DSA-65 sign / verify & $\sim$330 / $\sim$110 & sig 3309 & liboqs\\\hline
\end{tabular}
\end{center}
\noindent\textbf{The headline that answers ``isn't PQC slow E2E?'':} PQC
\emph{compute} is comparable to classical (ML-KEM encaps $\sim$30 $\mu$s $\approx$
X25519 23 $\mu$s); the cost is \emph{size} ($\sim$30--50$\times$). And CEG puts the
asymmetric PQC on the per-\emph{epoch} cold path while every \emph{frame} rides
AES-256-GCM ($\sim$58 GB/s, PQC-safe). ``PQC is slow E2E'' conflates size with
compute; the KEM-then-symmetric placement (same as TLS-bulk, MLS+SFrame) defeats
it. \textbf{Cribbed gotchas:} (1) \emph{multi-sender nonce reuse} --- in group
video N senders share an epoch but each emits its own \texttt{stream\_id}, so the
STREAM nonce prefix HKDF(epoch\_dek; stream\_id, epoch) is per-sender-unique
(SFrame solves the same hazard with per-sender keys; our per-sender stream\_id is
equivalent --- now explicit). (2) \emph{TreeKEM unmerged-leaves / double-join} ---
adopt RFC 9420 handling wholesale in the 1.x tree. (3) \emph{PCS} --- MLS offers
post-compromise security via key-updates; CEG chose forward-only (Option A);
flagged for reconsideration.

\begin{figure}[h]\centering
\includegraphics[width=0.78\textwidth]{fig_cascade.pdf}
\caption{Per-rekey PQC key cascade vs N under three delivery models. The tree wins ONLY with efficient multicast (b); without it (c) it is worse than flat. Delivery, not complexity, is decisive.}\label{fig:cascade}
\end{figure}
\begin{figure}[h]\centering
\includegraphics[width=0.70\textwidth]{fig_overhead.pdf}
\caption{PQC key+STH overhead as a share of egress --- content dominates; the key tail bites only at low bitrate $\times$ high churn $\times$ huge N.}\label{fig:overhead}
\end{figure}
\begin{figure}[h]\centering
\includegraphics[width=0.78\textwidth]{fig_lag.pdf}
\caption{Glass-to-glass lag vs Reticulum Link RTT (the free parameter). PQC adds $\sim\mu$s; transport sets the regime.}\label{fig:lag}
\end{figure}
\begin{figure}[h]\centering
\includegraphics[width=0.70\textwidth]{fig_join.pdf}
\caption{Stream/call join one-time cost --- RNS path setup dominates; crypto is sub-millisecond.}\label{fig:join}
\end{figure}
\clearpage
'''

# ---------------------------------------------------------------- assemble
if __name__ == "__main__":
    body = [PREAMBLE, MODEL]
    for fn in FILES:
        md = (SPEC/fn).read_text(encoding='utf-8')
        body.append(convert(md))
        body.append(r'\clearpage')
    body.append(r'\end{document}')
    (D/'ceg-1.0-rc29.tex').write_text('\n'.join(body), encoding='utf-8')
    print('wrote ceg-1.0-rc29.tex (%d files)' % len(FILES))
