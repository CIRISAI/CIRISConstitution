#!/usr/bin/env python3
"""
check_claims.py — validate constitution/claims.tsv (the CC evidence registry).

For each load-bearing claim: verify its section address exists in toc.tsv, its
evidence tags are well-formed, in-repo (@) pointers resolve, and cross-repo
pointers resolve against the pinned, vendored sibling spec-map manifests.

Cross-repo resolution has two grades, and the difference is reported, never hidden:

  SYMBOL  — the pointer names an artifact (`Module.theorem`, `path#symbol`, a test
            id) and the pinned manifest publishes that name, at this CC decimal,
            in a backed state. This is the only grade that verifies the artifact
            the claim actually cites.
  DECIMAL — the pointer names only the sibling repo's manifest tracking issue
            (e.g. `impl:CIRISServer#155`). Nothing about a specific artifact is
            checked; all that is verified is that the pinned manifest backs
            *something* at this CC decimal. Weak by construction — reported
            separately so a reader is never told more than was checked.

Exit nonzero on STRUCTURAL errors: bad row, unknown section, unknown tag,
duplicate id, dead in-repo pointer, a cross-repo pointer naming an artifact the
pinned manifest does not publish (or publishes in a non-backed state), a
`status: established` row that no resolvable pointer supports, or a toc/prose
semantic-id mismatch. A pointer whose manifest simply does not yet reach this
decimal is a WARNING (pending), not a failure.

Usage:  python3 tools/check_claims.py [--xfail-blocks]
"""
import csv, os, sys, re, glob
from collections import Counter, defaultdict, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOC = os.path.join(ROOT, "constitution")

TAGS = {"impl", "test", "lean", "bench", "staged", "open", "normative-only"}
RESOLVABLE_TAGS = {"impl", "test", "lean", "bench"}   # count toward "evidenced"
TICKET_TAGS = {"staged", "open"}                      # named ticket, NOT evidence
STATUSES = {"established", "normative", "staged", "open"}
# The 1.14.x parable was migrated into FOREWORD.md; it is intentionally in toc but
# has no numbered prose heading. Exempt it from the toc↔prose drift report.
DRIFT_EXEMPT_PREFIX = ("1.14",)

_HEADING = re.compile(r'^#{2,6}\s+(\d+(?:\.\d+)+)\s+`')
_HEADING_FULL = re.compile(r'^#{2,6}\s+(\d+(?:\.\d+)+)\s+`([^`]*)`\s*(.*)$')
_NORM = re.compile(r'\b(?:MUST NOT|MUST|SHALL NOT|SHALL|REQUIRED)\b')

# --- per-manifest reading rules ----------------------------------------------
# `backed`     : row states that count as "this artifact exists and passes".
# `known_bad`  : row states that are published-but-failing (xfail etc.) — these are
#                surfaced explicitly; a green sibling row at the same decimal must
#                not launder them.
# `symbol_cols`: the columns in which this manifest publishes artifact NAMES. A
#                manifest with no symbol column cannot be symbol-matched, and the
#                checker says so rather than silently falling back to the decimal.
# `issue`      : the manifest's own tracking issue. `REPO#<issue>` in claims.tsv is
#                a reference to the manifest itself, not to an artifact.
MANIFESTS = {
    "CIRISEdge": dict(
        status_col="crate@version",
        backed=lambda r: (r.get("repo", "").strip() not in ("—", "")
                          and r.get("crate@version", "").strip().lower() != "open"),
        known_bad=lambda r: False,
        symbol_cols=["path#symbol"], symbol_kind="path#symbol", issue="442"),
    "CIRISPersist": dict(
        status_col="crate@version",
        backed=lambda r: (r.get("repo", "").strip() not in ("—", "")
                          and r.get("crate@version", "").strip().lower() != "open"),
        known_bad=lambda r: False,
        symbol_cols=["path#symbol"], symbol_kind="path#symbol", issue="519"),
    "CIRISVerify": dict(
        status_col="crate@version",
        backed=lambda r: (r.get("repo", "").strip() not in ("—", "")
                          and r.get("crate@version", "").strip().lower() != "open"),
        known_bad=lambda r: False,
        symbol_cols=["path#symbol"], symbol_kind="path#symbol", issue="233"),
    "CIRISServer": dict(
        status_col="crate@version",
        backed=lambda r: (r.get("repo", "").strip() not in ("—", "")
                          and r.get("crate@version", "").strip().lower() != "open"),
        known_bad=lambda r: False,
        symbol_cols=["path#symbol"], symbol_kind="path#symbol", issue="155"),
    "CIRISConformance": dict(
        status_col="status",
        backed=lambda r: r.get("status", "").strip().lower() == "green",
        known_bad=lambda r: r.get("status", "").strip().lower() in ("xfail", "fail", "red"),
        symbol_cols=["conformance_test_id(s)", "freeze_gate_vector(s)"],
        symbol_kind="conformance test id", issue="59"),
    "coherence-ratchet": dict(
        status_col="status",
        backed=lambda r: r.get("status", "").strip().lower() == "mechanized",
        known_bad=lambda r: False,
        symbol_cols=["module_theorem"], symbol_kind="Module.theorem", issue=None),
    "RATCHET": dict(
        status_col="status",
        backed=lambda r: r.get("status", "").strip().lower() in ("mechanized", "empirical"),
        known_bad=lambda r: False,
        symbol_cols=["lean", "bench"], symbol_kind="Module.theorem / experiment path",
        issue="8"),
    "CIRISAgent": dict(
        status_col="status",
        backed=lambda r: r.get("status", "").strip().lower() == "impl",
        known_bad=lambda r: False,
        symbol_cols=["path#symbol"], symbol_kind="path#symbol", issue="911"),
}


def load_normative_sections():
    """decimal_id -> count of normative statements (MUST/SHALL/REQUIRED) in that section."""
    sec = {}
    for fn in glob.glob(os.path.join(DOC, "part_*.md")):
        cur = None
        for ln in open(fn, encoding="utf-8"):
            m = _HEADING.match(ln)
            if m:
                cur = m.group(1)
                sec.setdefault(cur, 0)
            elif cur:
                sec[cur] += len(_NORM.findall(ln))
    return {d: c for d, c in sec.items() if c > 0}


def load_toc():
    """decimal_id -> {semantic_id, title} (spine order preserved)."""
    rows = OrderedDict()
    with open(os.path.join(DOC, "toc.tsv"), encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            rows[row["decimal_id"]] = row
    return rows


def load_prose():
    """decimal_id -> (semantic_id, title) parsed from the numbered prose headings."""
    out = {}
    for fn in glob.glob(os.path.join(DOC, "part_*.md")):
        for ln in open(fn, encoding="utf-8"):
            m = _HEADING_FULL.match(ln)
            if m:
                title = re.sub(r'^\s*[—–-]\s*', '', m.group(3).strip())
                out[m.group(1)] = (m.group(2).strip(), title)
    return out


# --- manifests ---------------------------------------------------------------

def load_manifests():
    """repo -> {backed: set(decimals), sym_backed/sym_all: {symbol -> set(decimals)},
               known_bad: [(dec, claim, symbols, status)], spec: MANIFESTS entry}."""
    out = OrderedDict()
    pins = os.path.join(DOC, "evidence_pins.tsv")
    if not os.path.exists(pins):
        return out
    for row in csv.DictReader(open(pins, encoding="utf-8"), delimiter="\t"):
        repo, vend = row["repo"], os.path.join(DOC, row["vendored"])
        spec = MANIFESTS.get(repo)
        if spec is None or not os.path.exists(vend):
            continue
        backed, sym_backed, sym_all, bad = set(), defaultdict(set), defaultdict(set), []
        sym_state = {}
        lines = [l for l in open(vend, encoding="utf-8") if not l.lstrip().startswith("#")]
        for r in csv.DictReader(lines, delimiter="\t"):
            dec = (r.get("decimal_id") or r.get("cc_decimal_id") or "").strip()
            if not dec or dec == "—":            # non-section row (e.g. h3ere StepPoint)
                continue
            is_backed = spec["backed"](r)
            if is_backed:
                backed.add(dec)
            syms = []
            for col in spec["symbol_cols"]:
                cell = (r.get(col) or "").strip()
                if not cell or cell in ("—", "-"):
                    continue
                for tok in cell.split(","):
                    tok = tok.strip()
                    if tok and tok not in ("—", "-"):
                        syms.append(tok)
            for s in syms:
                sym_all[s].add(dec)
                sym_state[(s, dec)] = (r.get(spec["status_col"]) or "?").strip()
                if is_backed:
                    sym_backed[s].add(dec)
            if spec["known_bad"](r):
                bad.append((dec, (r.get("cc_claim_id") or r.get("claim_id") or "?").strip(),
                            syms, (r.get(spec["status_col"]) or "?").strip()))
        out[repo] = dict(backed=backed, sym_backed=sym_backed, sym_all=sym_all,
                         sym_state=sym_state, known_bad=bad, spec=spec,
                         publishes_symbols=bool(sym_all))
    return out


def parse_pointer(ptr):
    """('repo', kind, fragment). kind: 'issue' | 'symbol' | 'bare'."""
    repo = re.split(r"[#/:]", ptr, 1)[0]
    rest = ptr[len(repo):]
    if not rest:
        return repo, "bare", ""
    sep, frag = rest[0], rest[1:]
    if sep == "#":
        return repo, ("issue" if frag.isdigit() else "symbol"), frag
    return repo, "symbol", frag


def match_symbol(sym, table):
    """decimals at which `sym` is published in `table` ({symbol -> {decimals}})."""
    hits = set()
    for pub, decs in table.items():
        if _sym_eq(sym, pub):
            hits |= decs
    return hits


def _sym_eq(sym, pub):
    """Does claim-pointer `sym` name published artifact `pub`?

    Exact match; a `Module` pointer matching `Module.theorem` (module-level cite);
    a published `repo:Module.theorem` matching a bare `Module.theorem`; a
    `path#symbol` pointer matching the same `path#symbol`; a path-only pointer
    matching that path. Deliberately NOT a bare substring test — matching
    `_validate_capability` against `OtherClass._validate_capability` in a
    different file is exactly the laundering this checker exists to stop.
    """
    if sym == pub:
        return True
    pub_nore = pub.split(":", 1)[1] if ":" in pub and "#" not in pub else pub
    if sym == pub_nore:
        return True
    for p in (pub, pub_nore):
        if p.startswith(sym + "."):              # module-level lean cite
            return True
        if "#" not in sym and p.split("#", 1)[0] == sym:   # path-only impl cite
            return True
        if "::" in p and (sym in p.split("::")):  # exact test-name component
            return True
        if p.split("::", 1)[0].endswith("/" + sym + ".py") or \
           p.split("::", 1)[0].endswith(sym + ".py"):      # test-file cite
            return True
    return False


# --- toc / prose drift -------------------------------------------------------

def _norm_title(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)      # [text](url) -> text
    s = s.replace("**", "").replace("`", "").replace("*", "")
    s = s.replace("—", "-").replace("–", "-").replace("’", "'")
    s = re.sub(r"\s+", " ", s).strip().strip("-").strip()
    return s.lower()


def _strip_annotation(s):
    """Drop one trailing parenthetical (`(CEG 0.7 addition; per X#12)`)."""
    return re.sub(r"\s*\([^()]*\)\s*$", "", s).strip()


def report_toc_drift(toc, prose, errors, warnings, notes):
    missing = sorted(d for d in prose if d not in toc)
    extra = sorted(d for d in toc if d not in prose
                   and not d.startswith(DRIFT_EXEMPT_PREFIX) and "." in d)
    if missing:
        errors.append(f"toc drift: {len(missing)} prose section(s) missing from toc.tsv/codebook "
                      f"(every numbered section MUST have a dual-ID): {', '.join(missing)}")
    if extra:
        warnings.append(f"toc drift: {len(extra)} toc decimal(s) with no prose heading: {', '.join(extra)}")

    # --- title / semantic-id drift (the checker used to compare decimals only) ---
    semid, title_hard, title_annot = [], [], []
    for dec, row in toc.items():
        if dec not in prose:
            continue
        p_sid, p_title = prose[dec]
        t_sid, t_title = (row.get("semantic_id") or "").strip(), (row.get("title") or "").strip()
        if t_sid != p_sid:
            semid.append((dec, t_sid, p_sid))
        a, b = _norm_title(t_title), _norm_title(p_title)
        if a == b:
            continue
        a2, b2 = _strip_annotation(a), _strip_annotation(b)
        if a2 == b2 or a2.startswith(b2) or b2.startswith(a2):
            title_annot.append(dec)                       # toc carries provenance the prose dropped
        else:
            title_hard.append((dec, t_title, p_title))
    for dec, t, p in semid:
        errors.append(f"dual-ID drift at CC {dec}: toc.tsv semantic_id '{t}' != prose heading id '{p}'")
    for dec, t, p in title_hard:
        warnings.append(f"title drift at CC {dec}: toc.tsv={t!r} | prose={p!r}")
    if title_annot:
        notes.append(f"{len(title_annot)} section(s) where toc.tsv keeps a provenance annotation the "
                     f"prose heading dropped (title otherwise identical): {', '.join(title_annot)}")
    return len(semid), len(title_hard), len(title_annot)


# --- main --------------------------------------------------------------------

def main():
    xfail_blocks = "--xfail-blocks" in sys.argv
    errors, warnings, notes = [], [], []
    toc = load_toc()
    prose = load_prose()
    decs = set(toc) | set(prose)
    n_semid, n_title, n_annot = report_toc_drift(toc, prose, errors, warnings, notes)

    path = os.path.join(DOC, "claims.tsv")
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        expected = ["claim_id", "decimal_id", "summary", "evidence", "status"]
        if r.fieldnames != expected:
            print(f"FATAL: claims.tsv header {r.fieldnames} != {expected}")
            sys.exit(2)
        rows = list(enumerate(r, 2))

    man = load_manifests()
    ids = set()
    claim_decimals = defaultdict(list)          # decimal -> [(cid, grade)]
    status_ct, tag_ct = Counter(), Counter()
    grade_ct = Counter()                        # symbol / decimal / none, per claim
    inrepo_checked = 0
    xrepo_symbol = xrepo_decimal = xrepo_pending = 0
    resolved_by_repo = Counter()
    ticket_only_rows = []
    cited_repos = set()

    for ln, row in rows:
        cid = (row["claim_id"] or "").strip()
        dec = (row["decimal_id"] or "").strip()
        st = (row["status"] or "").strip()
        ev = (row["evidence"] or "").strip()
        if not cid:
            errors.append(f"L{ln}: empty claim_id")
            continue
        if cid in ids:
            errors.append(f"L{ln}: duplicate claim_id {cid}")
        ids.add(cid)
        if dec != "corpus" and dec not in decs:
            errors.append(f"L{ln} [{cid}]: decimal_id {dec} is not a document section (toc.tsv ∪ prose headings)")
        if st not in STATUSES:
            errors.append(f"L{ln} [{cid}]: bad status '{st}'")
        status_ct[st] += 1

        grade = None                            # 'symbol' > 'decimal' > None
        n_tickets = 0
        cites_artifact = False                  # row names >=1 impl/test/lean/bench pointer
        only_normative = bool(ev) and all(t.split(":", 1)[0] == "normative-only"
                                          for t in ev.split() if ":" in t)
        for tok in ev.split():
            if ":" not in tok:
                errors.append(f"L{ln} [{cid}]: malformed evidence token '{tok}'")
                continue
            tag, ptr = tok.split(":", 1)
            if tag not in TAGS:
                errors.append(f"L{ln} [{cid}]: unknown tag '{tag}'")
                continue
            tag_ct[tag] += 1
            if tag in RESOLVABLE_TAGS:
                cites_artifact = True

            # ---- normative-only ------------------------------------------------
            if tag == "normative-only":
                if ptr not in ("—", "-", ""):
                    warnings.append(f"L{ln} [{cid}]: normative-only pointer should be '—', got '{ptr}'")
                continue

            # ---- staged: / open: — a named TICKET, never an artifact -----------
            if tag in TICKET_TAGS:
                n_tickets += 1
                if ptr.startswith("@"):
                    errors.append(f"L{ln} [{cid}]: {tag} pointer '{ptr}' is in-repo — a {tag} token "
                                  f"must name a tracked ticket (REPO#issue), not a file")
                    continue
                t_repo, t_kind, t_frag = parse_pointer(ptr)
                cited_repos.add(t_repo)
                if not re.match(r"^[A-Za-z][A-Za-z0-9_.-]*$", t_repo) or t_kind != "issue":
                    errors.append(f"L{ln} [{cid}]: malformed {tag} pointer '{ptr}' "
                                  f"(expected REPO#issue, e.g. {tag}:CIRISServer#155)")
                continue

            # ---- in-repo -------------------------------------------------------
            if ptr.startswith("@"):
                inrepo_checked += 1
                if not os.path.exists(os.path.join(ROOT, ptr[1:])):
                    errors.append(f"L{ln} [{cid}]: dead in-repo pointer '{ptr}'")
                else:
                    grade = "symbol"
                continue

            # ---- cross-repo ----------------------------------------------------
            repo, kind, frag = parse_pointer(ptr)
            cited_repos.add(repo)
            m = man.get(repo)
            if m is None:
                xrepo_pending += 1
                warnings.append(f"L{ln} [{cid}]: cross-repo {tag} pointer '{ptr}' unresolved "
                                f"(no pinned {repo} manifest)")
                continue
            spec = m["spec"]

            if kind == "issue" and frag == (spec["issue"] or ""):
                # pointer names the manifest itself, not an artifact → decimal-only
                if dec in m["backed"]:
                    xrepo_decimal += 1
                    resolved_by_repo[repo] += 1
                    grade = grade or "decimal"
                else:
                    xrepo_pending += 1
                    warnings.append(f"L{ln} [{cid}]: {tag} pointer '{ptr}' — {repo} manifest (pinned) "
                                    f"does not back CC {dec}")
                continue
            if kind == "issue":
                xrepo_pending += 1
                warnings.append(f"L{ln} [{cid}]: {tag} pointer '{ptr}' names issue #{frag}, which is "
                                f"neither an artifact nor the {repo} manifest tracking issue "
                                f"(#{spec['issue']}) — a ticket is not evidence; use staged:/open:")
                continue

            # symbol-bearing pointer
            if not m["publishes_symbols"]:
                xrepo_pending += 1
                warnings.append(f"L{ln} [{cid}]: {tag} pointer '{ptr}' cannot be symbol-checked — the "
                                f"pinned {repo} manifest publishes no artifact names")
                continue
            hit_backed = match_symbol(frag, m["sym_backed"])
            hit_all = match_symbol(frag, m["sym_all"])
            if dec in hit_backed:
                xrepo_symbol += 1
                resolved_by_repo[repo] += 1
                grade = "symbol"
                if frag not in m["sym_backed"]:
                    notes.append(f"L{ln} [{cid}]: {tag} pointer '{ptr}' names a module/file, not a single "
                                 f"artifact — matched by prefix against the pinned {repo} manifest")
            elif dec in hit_all:
                st_here = sorted({v for (s, d), v in m["sym_state"].items()
                                  if d == dec and _sym_eq(frag, s)})
                errors.append(f"L{ln} [{cid}]: {tag} pointer '{ptr}' — the pinned {repo} manifest "
                              f"publishes this artifact at CC {dec} but NOT in a backed state "
                              f"({spec['status_col']}={'/'.join(st_here) or '?'}); it does not "
                              f"establish the claim")
            elif hit_all:
                where = ", ".join(sorted(hit_all))
                xrepo_pending += 1
                warnings.append(f"L{ln} [{cid}]: {tag} pointer '{ptr}' is published by the pinned {repo} "
                                f"manifest at CC {where}, not at CC {dec} — claim/manifest decimals disagree")
            else:
                elsewhere = [rp for rp, mm in man.items()
                             if rp != repo and match_symbol(frag, mm["sym_all"])]
                hint = f" (it IS published by the pinned {'/'.join(elsewhere)} manifest)" if elsewhere else ""
                errors.append(f"L{ln} [{cid}]: {tag} pointer '{ptr}' names an artifact the pinned {repo} "
                              f"manifest does not publish{hint} — dead cross-repo pointer "
                              f"({repo} publishes {spec['symbol_kind']})")

        grade_ct[grade or "none"] += 1
        if grade is None:
            ticket_only_rows.append((ln, cid, dec, st, "normative-only" if only_normative
                                     else ("cites-artifact-unresolved" if cites_artifact else "ticket-only")))
        # --- EVIDENCE.md: `established` = "at least one resolvable artifact backs it"
        if st == "established" and grade is None:
            if only_normative:
                errors.append(f"L{ln} [{cid}]: status 'established' with evidence 'normative-only' — "
                              f"EVIDENCE.md defines normative-only as 'no external artifact' and "
                              f"established as 'at least one resolvable artifact'. A rule settled by the "
                              f"document itself takes status 'normative'")
            else:
                errors.append(f"L{ln} [{cid}]: status 'established' but NO resolvable impl/test/lean/bench "
                              f"artifact backs it (evidence: {ev or '—'}) — EVIDENCE.md:38 defines "
                              f"established as at least one resolvable artifact; use 'staged' or 'open'")
        # `normative` is reserved for rules the document settles by itself. A row claiming it while
        # citing an external artifact is the same conflation in the other direction.
        if st == "normative" and not only_normative:
            errors.append(f"L{ln} [{cid}]: status 'normative' is for self-contained rules and pairs with "
                          f"'normative-only:—', but this row cites '{ev or '—'}' — if an artifact backs "
                          f"it, use 'established'/'staged'/'open'")
        if dec != "corpus":
            claim_decimals[dec].append((cid, grade))

    # --- coverage -------------------------------------------------------------
    norm = load_normative_sections()
    evidenced = {d for d in norm if any(g for _, g in claim_decimals.get(d, []))}
    token_only = {d for d in norm if d in claim_decimals and d not in evidenced}
    uncovered = sorted((norm[d], d) for d in norm if d not in claim_decimals)
    n = len(norm) or 1

    # --- xfail ----------------------------------------------------------------
    xfails = [(repo, dec, claim, syms, stt)
              for repo, m in man.items() for dec, claim, syms, stt in m["known_bad"]]

    print("=== CC evidence registry (claims.tsv) ===")
    print(f"claims: {len(rows)}")
    print("status: " + ", ".join(f"{k}={v}" for k, v in sorted(status_ct.items())))
    print("tags:   " + ", ".join(f"{k}={v}" for k, v in sorted(tag_ct.items())))
    print(f"in-repo pointers checked: {inrepo_checked}")
    print(f"claims with resolvable evidence: {grade_ct['symbol'] + grade_ct['decimal']}/{len(rows)}"
          f"  (artifact-verified {grade_ct['symbol']}, decimal-only {grade_ct['decimal']})")
    kind_ct = Counter(k for _, _, _, _, k in ticket_only_rows)
    print(f"claims with NO resolvable evidence: {grade_ct['none']}"
          f"  (ticket-only staged:/open: {kind_ct['ticket-only']},"
          f" normative-only {kind_ct['normative-only']},"
          f" names an artifact that did not resolve {kind_ct['cites-artifact-unresolved']})")

    print(f"\n=== cross-repo resolution (against pinned manifests) ===")
    if man:
        print("pinned manifests: " + ", ".join(f"{k}({len(v['backed'])} decimals)" for k, v in sorted(man.items())))
        print(f"pointers RESOLVED: {xrepo_symbol + xrepo_decimal} — "
              + ", ".join(f"{k}={v}" for k, v in sorted(resolved_by_repo.items())))
        print(f"  by ARTIFACT NAME (symbol/test id verified in the manifest): {xrepo_symbol}")
        print(f"  by CC DECIMAL only (pointer names the manifest issue, no artifact): {xrepo_decimal}")
        unpinned = sorted(rp for rp in cited_repos if rp not in man)
        print(f"pointers PENDING:  {xrepo_pending}")
        print(f"repos cited with no pinned manifest: {', '.join(unpinned) or 'none'}"
              + (" (staged:/open: tickets only — nothing to resolve against)" if unpinned else ""))
    else:
        print("(no evidence_pins.tsv — all cross-repo pointers pending)")

    print(f"\n=== known-failing vectors in pinned manifests (xfail) ===")
    if xfails:
        print(f"{len(xfails)} known-failing vector(s) across "
              f"{len(set(d for _, d, _, _, _ in xfails))} CC decimal(s) — a green sibling row at the same "
              f"decimal does NOT clear these:")
        for repo, dec, claim, syms, stt in sorted(xfails, key=lambda x: [int(p) for p in x[1].split(".")]):
            here = claim_decimals.get(dec, [])
            who = ", ".join(f"{c} ({'evidenced' if g else 'unevidenced'})" for c, g in here) or "no claims row"
            print(f"  [{stt}] {repo} CC {dec:10} {claim}")
            print(f"         vector: {syms[0] if syms else '—'}")
            print(f"         CC claims at this decimal: {who}")
        print("  RECOMMENDATION: these are disclosed-failing conformance vectors, not unknown risk;"
              "\n  they should BLOCK for any decimal whose claims row is `established` (an established"
              "\n  claim asserts a passing artifact) and WARN otherwise. Run with --xfail-blocks to"
              "\n  enforce; not enforced by default because clearing them is the sibling repo's work.")
        if xfail_blocks:
            for repo, dec, claim, syms, stt in xfails:
                for c, _g in claim_decimals.get(dec, []):
                    errors.append(f"xfail: {repo} vector {claim} at CC {dec} is {stt}; claim {c} rests on it")
    else:
        print("none")

    print(f"\n=== normative coverage (P2) ===")
    print(f"normative-bearing sections: {len(norm)}")
    print(f"  covered by >=1 claim with RESOLVABLE evidence: {len(evidenced)} ({100.0*len(evidenced)/n:.0f}%)")
    print(f"  covered ONLY by unvalidated staged:/open:/normative-only rows: {len(token_only)} "
          f"({100.0*len(token_only)/n:.0f}%)")
    print(f"  no claims row at all: {len(uncovered)} ({100.0*len(uncovered)/n:.0f}%)")
    print(f"  [legacy figure — 'has a claims row', regardless of evidence: "
          f"{len(evidenced) + len(token_only)}/{len(norm)} "
          f"({100.0*(len(evidenced)+len(token_only))/n:.0f}%)]")
    if token_only:
        print(f"all {len(token_only)} normative section(s) carrying NO checkable evidence "
              f"(by MUST/SHALL density):")
        for c, d in sorted(((norm[d], d) for d in token_only), reverse=True):
            who = ", ".join(c for c, _ in claim_decimals[d])
            print(f"  {d:12} {c:3} MUST/SHALL   {who}")
    if uncovered:
        print("top uncovered normative-density sections:")
        for c, d in sorted(uncovered, reverse=True)[:12]:
            print(f"  {d:12} {c:3} MUST/SHALL")

    if notes:
        print(f"\n{len(notes)} note(s):")
        for x in notes:
            print("  NOTE " + x)
    if warnings:
        print(f"\n{len(warnings)} warning(s) [pending manifests / drift — non-blocking]:")
        for w in warnings:
            print("  WARN " + w)
    if errors:
        print(f"\n{len(errors)} ERROR(s):")
        for e in errors:
            print("  ERR  " + e)
        sys.exit(1)
    print("\nOK — registry structurally valid.")
    sys.exit(0)


if __name__ == "__main__":
    main()
