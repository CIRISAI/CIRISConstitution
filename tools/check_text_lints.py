#!/usr/bin/env python3
"""Six lints on the prose of the Parts, each a measure held at a maximum that only falls.

  counts     a number the prose states that a table or a tool also states (the sections of a Part, the
             registry's families, the role names, the compliance dimensions, the closed leaves of a
             prefix, the shapes of the families, the Lean files) and a constant of
             constitution/constants.tsv stated in prose with another value
  citations  a citation of a section that does not exist; a link whose anchor differs from the number it
             shows, or that points into the wrong Part, or names no anchor; a citation of a section that is
             only a heading; a "below" or "above" that points the wrong way
  terms      one thing under two names or one name for two things, from a closed list: the names a landed
             rule is not called by (tools/check_rule_entries.py OTHER_NAMES), a founder or a steward tier
             in a community, a row refused for what another row says, the halt called an asymmetry, an AI
             agent written as a person, and the recorded term conflicts
  force      an RFC 2119 keyword in an informative paragraph or an example; a requirement in lower case
             in a normative paragraph; a restatement whose keyword differs from its home's
  length     sentences over 40 words in Parts 2 to 8 (Part 1 is not measured), held by Part
  history    history words ("previously", "no longer", "now" as a time word …), a reference to a ruling,
             a review or a refactor, and product, company or repository names

Each lint writes its worklist to formal/derivation/text_lints/<lint>.tsv and is held at the maximum in
tools/text_lints_max.tsv. The check exits 1 when a count rises above its maximum or a plant is missed;
a count below its maximum is reported so the maximum can be lowered. Every lint has a deliberate break
(a planted sentence) run every time, which must raise its count.

Read only prose: tables, fenced blocks, headings and the generated sections (CC 2.6.1.7, CC 8.10) are
skipped, except where a lint says otherwise. A line ending in `<!-- stale-ok -->` is not read by the
history lint (the same exemption tools/check_stale_refs.py gives).

  python3 tools/check_text_lints.py            # all six
  python3 tools/check_text_lints.py counts     # one
"""
import csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parts_text as P

ROOT = P.ROOT
OUT = ROOT / "formal" / "derivation" / "text_lints"
MAXIMA = ROOT / "tools" / "text_lints_max.tsv"
RFC = re.compile(r"\b(MUST NOT|MUST|SHALL NOT|SHALL|SHOULD NOT|SHOULD|REQUIRED|RECOMMENDED|NOT RECOMMENDED|MAY|OPTIONAL)\b")
WORDNUM = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                                      "fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}
NUM = r"(\d{1,3}(?:[,\u00a0\u202f ]\d{3})+(?!\d)|\d+|" + "|".join(sorted(WORDNUM, key=len, reverse=True)) + r")"


def num(s):
    s = s.strip().lower()
    return WORDNUM[s] if s in WORDNUM else int(re.sub(r"[,\u00a0\u202f ]", "", s))


def short(t, n=300):
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= n else t[:n - 1] + "…"


def sentences_of(parts, which=None):
    """(part, section, line, sentence raw, paragraph raw) over the prose."""
    for p in P.paragraphs(parts, which):
        for s in P.sentences(p["text"]):
            yield p["part"], p["section"], p["line"], s, p["text"]


def rows(path):
    with open(path, encoding="utf-8") as f:
        return [r for r in csv.DictReader((l for l in f if not l.startswith("#")), delimiter="\t", quoting=csv.QUOTE_NONE)]


# ---------------------------------------------------------------------------------------------- counts
# A constant of constitution/constants.tsv as the prose states it: the words that must stand in the
# sentence, the unit, and the values the table gives (in that unit). A sentence carrying the words and a
# number in that unit that is not one of the values is a mismatch.
CONSTANT_PROSE = [
    ("shaped_frame_bytes", r"\bshaped\b.*\bframe|\bframe\b.*\bshaped\b", r"bytes", {1400}),
    ("shaped_link_bound", r"\bshaped links?\b", r"shaped links?", {8}),
    ("asked_shaped_link_idle_secs", r"\bidle\b.*\bshaped|\bshaped\b.*\bidle\b", r"minutes|s\b", {10, 600}),
    ("shaped_file_max_bytes", r"\bshaped link\b.*\bfile|\bfile\b.*\bshaped link", r"KiB", {64}),
    ("admission_freshness_window_secs", r"\bfreshness window\b|\bwindow `?W`?\b|\bW = ", r"h\b|hours", {72, 168}),
    ("moderation_fallback_window_secs", r"\bfallback window\b|\bruled_48h\b", r"h\b|hours", {48, 24}),
    ("census_k_floor", r"\bk-anonymity\b|\bk = \d|\bk-floor\b|\bk floor\b", r"sources", {10}),
    ("trust_walk_hop_cap", r"\btrust_depth\b|\btrust walk\b|\bhop cap\b", r"hops?", {5}),
    ("envelope_cap_bytes", r"\benvelope\b.*\bcap\b|\bENVELOPE_TOO_LARGE\b", r"MiB|bytes", {1, 1048576}),
    ("session_claim_max_secs", r"\bsession claim\b|\bsession_claim\b", r"h\b|hours|s\b", {24, 86400}),
    ("custody_report_ttl_secs", r"\bcustody report\b", r"h\b|hours", {72}),
    ("accord_heartbeat_max_secs", r"\bheartbeat\b", r"days", {90}),
    ("membership_proposal_max_secs", r"\bmembership proposal\b|\bproposal's `?asserted_at`?", r"days", {30}),
    ("delegation_term_max_secs", r"\bdelegation\b.*\bterm\b|\bdelegation_valid_from\b", r"days", {365}),
    ("consent_temporary_ttl_secs", r"\btemporary grant\b", r"days", {14}),
    ("epoch_key_retention_secs", r"\bpast-epoch keys?\b|\brotate-forward window\b", r"days", {30}),
    ("withhold_window_dmca512", r"\bDmca512\b", r"days", {10}),
    ("withhold_window_dsa16", r"\bDsaArticle16\b", r"days", {14}),
    ("withhold_window_community_standards", r"\bCommunityStandards\b", r"days", {30}),
    ("rendezvous_mailbox_retention_secs", r"\bmailbox\b.*\bretain|\bretention\b.*\bmailbox", r"hours|h\b|s\b", {2, 7200}),
]


def lint_counts(parts):
    hits = []
    toc = Counter(r["decimal_id"].split(".")[0] for r in rows(ROOT / "constitution" / "toc.tsv"))
    fam = len(json.load(open(ROOT / "manifests" / "family_model.json", encoding="utf-8"))["rows"])
    roles = len(json.load(open(ROOT / "manifests" / "transitions.json", encoding="utf-8"))["_meta"]["role_tokens"])
    dims = len(rows(ROOT / "formal" / "derivation" / "compliance_dimensions.tsv"))
    shapes = Counter(r["shape"] for r in rows(ROOT / "formal" / "derivation" / "family_shapes.tsv"))
    m = re.search(r"for f in ([^;]+);", (ROOT / "formal" / "causal_order" / "build.sh").read_text(encoding="utf-8"))
    lean = len(m.group(1).split()) if m else 0
    # The Part headers: "**N sections**" against the Part's rows of constitution/toc.tsv.
    for part, text in parts.items():
        for i, l in enumerate(text.split("\n"), 1):
            for mm in re.finditer(r"\*\*(\d+) sections\*\*", l):
                if int(mm.group(1)) != toc[part[1:]]:
                    hits.append((part, "", i, short(l, 160), f"states {mm.group(1)} sections; constitution/toc.tsv has {toc[part[1:]]}"))
    # Prose of the Parts and of the formal pages that quote the same tables.
    formal = {}
    for name in ("formal/KERNEL.md", "formal/README.md", "formal/causal_order/README.md", "formal/ADEQUACY.md"):
        if (ROOT / name).exists():
            formal[name] = (ROOT / name).read_text(encoding="utf-8")
    checks = [
        (r"\b(?:the|registry's|of|all) " + NUM + r" (?:row )?families\b", lambda v: v < 100 or v == fam, f"the registry has {fam} families (manifests/family_model.json)"),
        (r"\b" + NUM + r" role (?:names|tokens)\b", lambda v: v == roles, f"manifests/transitions.json has {roles} role tokens"),
        (r"\b(?:all|the|of the) " + NUM + r" dimensions\b", lambda v: v == dims, f"formal/derivation/compliance_dimensions.tsv has {dims} dimensions"),
        (r"\b(?:compiles|built on|Lean,) (?:the )?" + NUM + r" files\b|\bLean, " + NUM + r" files", lambda v: v == lean, f"formal/causal_order/build.sh compiles {lean} files"),
    ]
    def scan(where, part, sec, line, text):
        for pat, ok, why in checks:
            for mm in re.finditer(pat, text):
                g = next(x for x in mm.groups() if x)
                v = num(g)
                if not ok(v):
                    hits.append((part, sec, line, short(text), f"states {g}; {why}"))
        mm = re.search(NUM + r" are claims, " + NUM + r" content, " + NUM + r" doors, " + NUM + r" consents and " + NUM + r" both", text)
        if mm:
            got = [num(x) for x in mm.groups()]
            want = [shapes["claim"], shapes["content"], shapes["door"], shapes["consent"], shapes["consent+door"]]
            if got != want:
                hits.append((part, sec, line, short(text), f"states shapes {got}; formal/derivation/family_shapes.tsv has {want}"))
    for part, sec, line, s, _ in sentences_of(parts):
        scan("part", part, sec, line, P.plain(s))
    for name, text in formal.items():
        for i, l in enumerate(text.split("\n"), 1):
            scan("formal", name, "", i, l)
    # A closed list stated with its size: "The N leaves are a closed vocabulary" or "The N <things>; `{x}` ∈ `a` | `b` …"
    # against the items the section's enumeration (`{x}` ∈ …) lists.
    for part, text in parts.items():
        lines = text.split("\n")
        secs = P.section_of_lines(text)
        enum = {}
        for i, l in enumerate(lines):
            mm = re.search(r"∈ ((?:`[^`]+`\s*(?:\\\||\|)\s*)+`[^`]+`)", l)
            if mm and secs[i]:
                enum[secs[i]] = len(re.findall(r"`[^`]+`", mm.group(1)))
        for i, l in enumerate(lines):
            for mm in re.finditer(r"\b[Tt]he " + NUM + r" (leaves are a closed vocabulary|[a-z-]+ categories; `)", l):
                n = enum.get(secs[i])
                if n is not None and num(mm.group(1)) != n:
                    hits.append((part, secs[i], i + 1, short(l), f"states {mm.group(1)}; the enumeration of CC {secs[i]} lists {n}"))
    # Constants restated with another value.
    names = {r["name"] for r in rows(ROOT / "constitution" / "constants.tsv")}
    for part, sec, line, s, _ in sentences_of(parts):
        t = P.plain(s)
        for name, ctx, unit, values in CONSTANT_PROSE:
            c = re.search(ctx, t)
            if name not in names or not c:
                continue
            # the first value in the unit within 80 characters after the words that name the constant
            mm = re.search(r"(?<![\d.])" + NUM + r"(?:\s|-)(?:" + unit + r")", t[c.start():c.end() + 80])
            if mm and num(mm.group(1)) not in values:
                hits.append((part, sec, line, short(s), f"{name}: states {mm.group(0).strip()}; constitution/constants.tsv gives {sorted(values)}"))
    return hits


# ------------------------------------------------------------------------------------------- citations
def section_index(parts):
    """number -> (part, line index, has a body of its own)."""
    idx = {}
    for part, text in parts.items():
        lines = text.split("\n")
        heads = P.headings(text)
        for k, (i, d, n, _) in enumerate(heads):
            if not n:
                continue
            end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
            body = any(l.strip() and l.strip() != "---" for l in lines[i + 1:end])
            idx[n] = (part, i, body)
    return idx


LINKED = re.compile(r"\[([^\]]*)\]\(([^)\s#]*)(?:#([^)\s]*))?\)")


def lint_citations(parts):
    hits = []
    idx = section_index(parts)
    for part, text in parts.items():
        lines = text.split("\n")
        secs = P.section_of_lines(text)
        fenced = False
        for i, l in enumerate(lines):
            if l.lstrip().startswith("```"):
                fenced = not fenced
                continue
            if fenced or P.generated(secs[i]) or P.HEAD.match(l):
                continue
            sec = secs[i]
            # links whose label shows a section number
            for mm in LINKED.finditer(l):
                label, f, anchor = mm.group(1), mm.group(2), mm.group(3)
                shown = re.fullmatch(r"CC (\d+(?:\.\d+)*)", label.strip())
                if not shown:
                    continue
                n = shown.group(1)
                if f and f in P.FILE_PART and n in idx and idx[n][0] != P.FILE_PART[f]:
                    hits.append((part, sec, i + 1, short(l), f"[CC {n}] links into {f}; CC {n} is in {P.PARTS[idx[n][0]]}"))
                elif anchor is None and (f in P.FILE_PART or not f):
                    hits.append((part, sec, i + 1, short(l), f"no anchor: [CC {n}] links to {f or 'this Part'} with no #{n}"))
                elif anchor is not None and re.fullmatch(r"\d+(?:\.\d+)*", anchor) and anchor != n:
                    hits.append((part, sec, i + 1, short(l), f"[CC {n}] links to #{anchor}"))
                elif anchor == "":
                    hits.append((part, sec, i + 1, short(l), f"[CC {n}] links to an empty anchor"))
            # every cited number
            plain_l = re.sub(r"\]\([^)]*\)", "]", l)
            for mm in re.finditer(r"\bCC (\d+(?:\.\d+)*)", plain_l):
                n = mm.group(1)
                if "." not in n and n in "12345678":
                    continue                                   # a whole Part
                if n not in idx:
                    hits.append((part, sec, i + 1, short(l), f"CC {n} is not a section"))
                elif not idx[n][2]:
                    hits.append((part, sec, i + 1, short(l), f"CC {n} is a heading with no body"))
                else:
                    after = plain_l[mm.end():mm.end() + 14]
                    before = plain_l[max(0, mm.start() - 40):mm.start()]
                    way = (re.match(r"\]?\)?,?\s*(below|above)(?=\s*[.,;:)]|\s*$)", after)
                           or re.search(r"\b(?:see|set out|stated|given|defined|described|listed|rule)\s+(below|above)\s*[(,:]?\s*\[?$", before, re.I))
                    if way and n != sec:
                        tp, tl, _ = idx[n]
                        down = (int(tp[1]), tl) > (int(part[1]), i)
                        if (way.group(1) == "below") != down:
                            hits.append((part, sec, i + 1, short(l), f"CC {n} is cited as {way.group(1)}"))
    return hits


# ----------------------------------------------------------------------------------------------- terms
def other_names():
    import importlib.util
    spec = importlib.util.spec_from_file_location("cre", ROOT / "tools" / "check_rule_entries.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.OTHER_NAMES


# (name, pattern on the sentence, allowed when this matches the paragraph, sections where the other sense stands)
TERMS = [
    ("founder", r"\bfound(?:er|ers|ing)\b",
     r"\binfrastructure\b|\baccord\b|\bciris-canonical\b|\bfounding (?:record|row|bundle|genesis|head)\b|\bgenesis\b"
     r"|\btrust-root\b|\bfounder[- ]quorum\b|\brole: founder\b|\brole == founder\b|\badmission_quorum_basis\b", ("8.6",)),
    ("community steward", r"\bfirst steward\b|\bcommunity(?:'s)? steward\b|\bsteward of (?:a|the|its|this) (?:community|room|lineage|group|mesh)\b|\bsteward tiers?\b",
     None, ()),
    ("refused for another row", r"\b(?:refus|reject)\w*\b[^.]{0,120}\b(?:another|other|earlier|later|prior|conflicting|competing|second|existing) (?:row|record|grant|version|claim)\b"
     r"|\b(?:another|other|earlier|later|prior|conflicting|competing|second|existing) (?:row|record|grant|version|claim)\b[^.]{0,120}\b(?:is|are) (?:refused|rejected)\b",
     r"\bconcludes nothing\b|\bnot counted\b|\bcontested\b", ()),
    ("halt as asymmetry", r"\basymmetr\w*", r"\bnot an asymmetry\b|\bcondition of symmetry\b", ()),
    ("agent as person", r"\b(?:AI )?agents?,? (?:who|whom)\b|\bagents? (?:himself|herself|themselves)\b|\bagent is a person\b|\bagents are persons\b", None, ()),
    ("network-consensus clock (C122)", r"\bnetwork-consensus clock\b", None, ()),
]


def lint_terms(parts):
    hits = []
    for key, names in other_names().items():
        for part, sec, line, s, para in sentences_of(parts):
            t = P.plain(s)
            for o in names:
                if o in t:
                    hits.append((part, sec, line, short(s), f"{key} called \"{o}\""))
    for name, pat, allow, secs in TERMS:
        for part, sec, line, s, para in sentences_of(parts):
            t = P.plain(s)
            if not re.search(pat, t, re.I if name != "founder" else 0):
                continue
            if name == "halt as asymmetry" and not re.search(r"\bhalt", P.plain(para), re.I):
                continue
            if allow and re.search(allow, P.plain(para), re.I):
                continue
            if any(sec == a or sec.startswith(a + ".") for a in secs):
                continue
            hits.append((part, sec, line, short(s), name))
    return hits


# ----------------------------------------------------------------------------------------------- force
INFORMATIVE = re.compile(r"\((?:informative|informational)[^)]*\)|^\**(?:Worked )?[Ee]xample\b|^\**For example\b|^\*?\*?e\.g\.")
NORMATIVE = re.compile(r"\(normative[^)]*\)")
LOWER = re.compile(r"(?<![`*])\b(must not|must|shall not|shall|should not|should|is required to|are required to)\b(?![`*])")


def marked_sections(parts):
    """number -> 'informative' or 'normative' from the heading's own marker."""
    out = {}
    for part, text in parts.items():
        for i, d, n, title in P.headings(text):
            if n and INFORMATIVE.search(title):
                out[n] = "informative"
            elif n and NORMATIVE.search(title):
                out[n] = "normative"
    return out


def lint_force(parts):
    hits = []
    marks = marked_sections(parts)
    for p in P.paragraphs(parts):
        lead = p["text"][:200]
        mode = "informative" if INFORMATIVE.search(lead) else "normative" if NORMATIVE.search(lead) else marks.get(p["section"])
        for s in P.sentences(p["text"]):
            code_free = re.sub(r"`[^`]*`", "", s)
            if (mode == "informative" or re.match(r"\**(?:For example|E\.g\.)", s)) and RFC.search(code_free):
                hits.append((p["part"], p["section"], p["line"], short(s), f"keyword {RFC.search(code_free).group(1)} in an informative paragraph or an example"))
            elif mode == "normative" and LOWER.search(P.plain(code_free)) and not RFC.search(code_free):
                hits.append((p["part"], p["section"], p["line"], short(s), f"requirement \"{LOWER.search(P.plain(code_free)).group(1)}\" with no keyword in a normative paragraph"))
    # A restatement whose keyword differs from the keyword of its home's phrase.
    import check_restatements as R
    entries, inv = R.read("rule_entries.tsv"), R.read("rule_inventory.tsv")
    found = R.measure(parts, entries, inv)[0]
    states = defaultdict(list)
    for e in entries:
        if e["role"] == "states":
            states[(e["rule_key"], e["home"])].append(e["entry_phrase"])
    level = lambda k: {"MUST": 3, "MUST NOT": 3, "SHALL": 3, "SHALL NOT": 3, "REQUIRED": 3, "SHOULD": 2, "SHOULD NOT": 2,
                       "RECOMMENDED": 2, "NOT RECOMMENDED": 2, "MAY": 1, "OPTIONAL": 1}[k]
    for (part, sent, key), (sec, hs, para, src) in sorted(found.items(), key=lambda x: (x[0][0], x[1][0], x[0][1])):
        mine = {level(k) for k in RFC.findall(re.sub(r"`[^`]*`", "", sent))}
        if len(mine) != 1:
            continue
        st = set(R.toks(sent))
        best, score = None, 0.0
        for h in hs:
            for ph in states.get((key, h), ()):
                pt = set(R.toks(ph))
                sc = len(st & pt) / max(len(pt), 1)
                if sc > score:
                    best, score = (h, ph), sc
        if not best or score < 0.5:
            continue
        theirs = {level(k) for k in RFC.findall(re.sub(r"`[^`]*`", "", best[1]))}
        if len(theirs) == 1 and theirs != mine:
            hits.append((part, sec, 0, short(sent), f"{key}: keyword level {mine.pop()} here, {theirs.pop()} at its home CC {best[0]}"))
    return hits


# ---------------------------------------------------------------------------------------------- length
MAX_WORDS = 40


def exempt():
    import importlib.util
    spec = importlib.util.spec_from_file_location("cre", ROOT / "tools" / "check_rule_entries.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.EXEMPT


def lint_length(parts):
    hits, keep = [], exempt()
    for part, sec, line, s, _ in sentences_of(parts, which=[p for p in parts if p != "p1"]):
        t = P.plain(s)
        for k in keep:
            t = t.replace(k, "")
        n = len(t.split())
        if n > MAX_WORDS:
            hits.append((part, sec, line, short(s), f"{n} words"))
    return hits


# --------------------------------------------------------------------------------------------- history
HISTORY = [
    ("history word", r"\b(?:previously|formerly|no longer|(?:was|were|has been|have been) (?:changed|renamed)|used to be|originally|as of (?:this writing|today|now)|until now|from now on)\b"),
    ("now", r"(?<![-@`])\bnow\b(?![-`])"),
    ("ruling, review or refactor", r"\b(?:steward(?:'s)?|owner(?:'s)?|this|that|the owner's) ruling\b|\bwas ruled\b|\bruled (?:by|on|that)\b|\brefactor\w*|\breview pass\w*|\bexternal review\b|\b(?:the|a) reviewers? (?:found|noted|said|raised)\b|\brc\d+\b"),
    ("product or repository", r"\bCIRIS[A-Z][A-Za-z]+\b|\bCIRIS L3C\b|\bAnthropic\b|\bOpenAI\b|\bGitHub\b|\bPR #\d+|(?<![\w&])#\d{3,5}\b"),
]
HISTORY_ALLOW = ("8.6",)          # references and lineage: naming the source is the point


def lint_history(parts):
    hits, keep = [], exempt()
    clean = {}
    for part, text in parts.items():
        clean[part] = "\n".join("" if l.rstrip().endswith("<!-- stale-ok -->") else l for l in text.split("\n"))
    for part, sec, line, s, _ in sentences_of(clean):
        if any(sec == a or sec.startswith(a + ".") for a in HISTORY_ALLOW):
            continue
        t = P.plain(re.sub(r"`[^`]*`", "", s))
        for k in keep:
            t = t.replace(k, "")
        for name, pat in HISTORY:
            mm = re.search(pat, t, 0 if name == "product or repository" else re.I)
            if mm:
                hits.append((part, sec, line, short(s), f"{name}: {mm.group(0)}"))
    return hits


# ---------------------------------------------------------------------------------------------- plants
def plant_into(parts, number, text):
    p = dict(parts)
    part = "p" + number[0]
    lines = p[part].split("\n")
    at = next(i for i, l in enumerate(lines) if re.match(rf"#+ {re.escape(number)} ", l))
    lines[at + 1:at + 1] = ["", text, ""]
    p[part] = "\n".join(lines)
    return p


PLANTS = {
    "counts": ("5.4.3", "A shaped frame carries 1,500 bytes before its seal."),
    "citations": ("3.2", "The rule is stated at [CC 9.9.9](part_3_the_namespace.md#9.9.9)."),
    "terms": ("4.2", "The halt is an asymmetry in the relationship."),
    "force": [("3.2", "**Example (informative).** A node MUST read the planted row."),
              ("6.1.6", "A node SHOULD admit a `withdraws` against a target row `T` when one line of this table holds.")],
    "length": ("3.2", " ".join(["word"] * 44) + "."),
    "history": ("3.2", "This rule was previously stated in another section."),
}
LINTS = {"counts": lint_counts, "citations": lint_citations, "terms": lint_terms, "force": lint_force,
         "length": lint_length, "history": lint_history}


def maxima():
    out = {}
    for l in MAXIMA.read_text(encoding="utf-8").split("\n"):
        if l.strip() and not l.startswith(("#", "lint\t")):
            k, v = l.split("\t")[:2]
            out[k] = int(v)
    return out


def held_counts(name, hits):
    if name == "citations":
        na = sum(1 for h in hits if h[4].startswith("no anchor"))
        return {"citations": len(hits) - na, "citations_no_anchor": na}
    if name == "length":
        c = Counter(h[0] for h in hits)
        return {"length": len(hits), **{f"length:{p}": c.get(p, 0) for p in P.PARTS if p != "p1"}}
    return {name: len(hits)}


def main(argv):
    which = [a for a in argv if a in LINTS] or list(LINTS)
    parts = P.load()
    cap = maxima()
    OUT.mkdir(parents=True, exist_ok=True)
    bad = 0
    for name in which:
        hits = LINTS[name](parts)
        with (OUT / f"{name}.tsv").open("w", encoding="utf-8") as f:
            f.write("part\tsection\tline\ttext\tfinding\n")
            for h in sorted(hits, key=lambda h: (str(h[0]), h[1], h[2])):
                f.write("\t".join(str(x).replace("\t", " ") for x in h) + "\n")
        counts = held_counts(name, hits)
        detail = Counter(h[4].split(":")[0] if name in ("history", "terms") else "" for h in hits)
        extra = "" if name not in ("history", "terms") else " (" + ", ".join(f"{k} {v}" for k, v in sorted(detail.items())) + ")"
        if name == "citations":
            extra = f" ({counts['citations']} defects, {counts['citations_no_anchor']} links with no anchor)"
        if name == "length":
            extra = " (" + ", ".join(f"{k.split(':')[1]} {v}" for k, v in counts.items() if ":" in k) + ")"
        print(f"text lints: {name}: {len(hits)}{extra}")
        for k, v in counts.items():
            m = cap.get(k)
            if m is None:
                print(f"text lints: {k}: no maximum in tools/text_lints_max.tsv"); bad = 1
            elif v > m:
                print(f"text lints: {k}: {v} is above its maximum {m}; see formal/derivation/text_lints/{name}.tsv"); bad = 1
            elif v < m:
                print(f"text lints: {k}: {v} is below its maximum {m}: lower it in tools/text_lints_max.tsv")
        plants = PLANTS[name] if isinstance(PLANTS[name], list) else [PLANTS[name]]
        for sec, text in plants:
            after = LINTS[name](plant_into(parts, sec, text))
            if len(after) <= len(hits):
                print(f"text lints: {name}: the planted break in CC {sec} was not caught"); bad = 1
    return bad


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
