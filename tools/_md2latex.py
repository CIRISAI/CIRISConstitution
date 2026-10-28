#!/usr/bin/env python3
"""Markdown-to-LaTeX conversion for the PDF build (imported by build_pdf.py).
No pandoc available -> a focused markdown->LaTeX converter for this spec's
subset (headings, pipe tables, code fences, lists, inline bold/italic/code/links,
blockquotes), pdflatex + newunicodechar for the special glyphs in NUC.
"""
import re, sys
from pathlib import Path

D = Path(__file__).parent


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
    # an escaped pipe outside a table is a literal bar too (the Parts write `a \| b` in prose)
    s = s.replace('\\|', '|')
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

def block_start(ln):
    """True when a line opens a block of its own (heading, fence, table row, quote, list item,
    rule, nav), so a paragraph or list item being gathered stops before it."""
    t = ln.lstrip()
    return (t.startswith(('#', '```', '|', '>')) or re.match(r'^[-*]\s+', t) is not None
            or re.match(r'^\d+\.\s+', t) is not None or re.match(r'^(-{3,}|={3,})\s*$', t) is not None
            or is_nav(ln))


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


def bullet_indent(ln):
    """Column at which a bullet line's marker sits (tabs count four), or None for a non-bullet."""
    m = re.match(r'^(\s*)[-*]\s+', ln)
    return len(m.group(1).expandtabs(4)) if m else None


def bullet_item(lines, i, n):
    """One bullet's text: its line plus the indented continuation lines that open no block."""
    item = [re.sub(r'^\s*[-*]\s+', '', lines[i])]; i += 1
    while i < n and re.match(r'^\s+\S', lines[i]) and not re.match(r'^\s*[-*]\s+', lines[i]) and not block_start(lines[i].strip()):
        item.append(lines[i].strip()); i += 1
    return inline(' '.join(item)), i


def skip_gap(lines, i, n):
    """A blank line between items does not end the list (the master writes lists both ways)."""
    if i + 1 < n and lines[i].strip() == '' and re.match(r'^\s*[-*]\s+', lines[i+1]):
        return i + 1
    return i


def convert(md):
    md = re.sub(r"[ \t]*<!--.*?-->", "", md, flags=re.S)   # editorial comments never print
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
                depth = bullet_indent(lines[i])
                text, i = bullet_item(lines, i, n)
                out.append(r'\item ' + text)
                # bullets indented under this one (two or more spaces, or a tab) are its sub-points
                # and nest one level; deeper indents stay at that level
                if i < n and (d := bullet_indent(lines[i])) is not None and d > depth and d >= 2:
                    out.append(r'\begin{itemize}\setlength\itemsep{0pt}')
                    while i < n and (d := bullet_indent(lines[i])) is not None and d > depth:
                        text, i = bullet_item(lines, i, n)
                        out.append(r'\item ' + text)
                        i = skip_gap(lines, i, n)
                    out.append(r'\end{itemize}')
                i = skip_gap(lines, i, n)
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
        # paragraph: consecutive non-blank lines that start no block are one paragraph (the
        # covers and the stewardship note are hard-wrapped in the source)
        buf = [line]; i += 1
        while i < n and lines[i].strip() and not block_start(lines[i]):
            buf.append(lines[i].strip()); i += 1
        out.append(inline(' '.join(buf))); out.append('')
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


if __name__ == "__main__":
    import sys
    sys.stdout.write(convert(sys.stdin.read()))
