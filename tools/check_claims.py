#!/usr/bin/env python3
"""
check_claims.py — validate constitution/claims.tsv (the CC evidence registry).

For each load-bearing claim: verify its section address exists in toc.tsv, its
evidence tags are well-formed, in-repo (@) pointers resolve, and cross-repo
pointers are well-formed (their resolution is deferred to the pinned sibling
spec-map manifests — see EVIDENCE.md and the downstream evidence issues).

Exit nonzero on STRUCTURAL errors (bad row, unknown section, unknown tag,
duplicate id, dead in-repo pointer). A cross-repo pointer that cannot yet be
resolved is a WARNING (pending sibling manifest), not a failure.

Usage:  python3 tools/check_claims.py
"""
import csv, os, sys, re, glob
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOC = os.path.join(ROOT, "constitution")

TAGS = {"impl", "test", "lean", "bench", "staged", "open", "normative-only"}
RESOLVABLE_TAGS = {"impl", "test", "lean", "bench"}   # count toward "evidenced"
STATUSES = {"established", "staged", "open"}
# The 1.14.x parable was migrated into FOREWORD.md; it is intentionally in toc but
# has no numbered prose heading. Exempt it from the toc↔prose drift report.
DRIFT_EXEMPT_PREFIX = ("1.14",)

_HEADING = re.compile(r'^#{2,6}\s+(\d+(?:\.\d+)+)\s+`')
_NORM = re.compile(r'\b(?:MUST NOT|MUST|SHALL NOT|SHALL|REQUIRED)\b')


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


def load_toc_decimals():
    decs = set()
    with open(os.path.join(DOC, "toc.tsv"), encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            decs.add(row["decimal_id"])
    return decs


def load_prose_decimals():
    decs = set()
    for fn in glob.glob(os.path.join(DOC, "part_*.md")):
        for ln in open(fn, encoding="utf-8"):
            m = _HEADING.match(ln)
            if m:
                decs.add(m.group(1))
    return decs


def load_backed_decimals():
    """repo -> set of CC decimals its pinned, vendored spec-map manifest BACKS.
    Manifests are vendored under constitution/vendor/evidence/ at the commits pinned
    in constitution/evidence_pins.tsv, so resolution is reproducible and CI-local.
    Cross-repo pointers join on the CC decimal (claim_ids differ between repos)."""
    backed = {}
    pins = os.path.join(DOC, "evidence_pins.tsv")
    if not os.path.exists(pins):
        return backed
    for row in csv.DictReader(open(pins, encoding="utf-8"), delimiter="\t"):
        repo, vend = row["repo"], os.path.join(DOC, row["vendored"])
        if not os.path.exists(vend):
            continue
        decs = set()
        lines = [l for l in open(vend, encoding="utf-8") if not l.lstrip().startswith("#")]
        for r in csv.DictReader(lines, delimiter="\t"):
            dec = (r.get("decimal_id") or r.get("cc_decimal_id") or "").strip()
            if not dec:
                continue
            if repo == "CIRISServer":
                if r.get("repo", "").strip() not in ("—", "") and r.get("crate@version", "").strip().lower() != "open":
                    decs.add(dec)
            elif repo == "CIRISConformance":
                if r.get("status", "").strip().lower() == "green":
                    decs.add(dec)
            elif repo == "coherence-ratchet":
                if r.get("status", "").strip().lower() == "mechanized":
                    decs.add(dec)
            elif repo == "RATCHET":
                if r.get("status", "").strip().lower() in ("mechanized", "empirical"):
                    decs.add(dec)
        backed[repo] = decs
    return backed


def report_toc_drift(toc, prose, errors, warnings):
    # A prose section absent from the spine is a hard error: every numbered section
    # MUST carry a dual-ID (toc.tsv + codebook.json). Reconciled in CIRISConstitution#20.
    missing = sorted(d for d in prose if d not in toc)
    # A toc decimal with no prose heading is a warning (e.g. the 1.14.x parable → FOREWORD).
    extra = sorted(d for d in toc if d not in prose
                   and not d.startswith(DRIFT_EXEMPT_PREFIX) and "." in d)
    if missing:
        errors.append(f"toc drift: {len(missing)} prose section(s) missing from toc.tsv/codebook "
                      f"(every numbered section MUST have a dual-ID): {', '.join(missing)}")
    if extra:
        warnings.append(f"toc drift: {len(extra)} toc decimal(s) with no prose heading: {', '.join(extra)}")


def main():
    errors, warnings = [], []
    toc = load_toc_decimals()
    prose = load_prose_decimals()
    decs = toc | prose                                                # a claim may address any real section
    report_toc_drift(toc, prose, errors, warnings)
    path = os.path.join(DOC, "claims.tsv")
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        expected = ["claim_id", "decimal_id", "summary", "evidence", "status"]
        if r.fieldnames != expected:
            print(f"FATAL: claims.tsv header {r.fieldnames} != {expected}")
            sys.exit(2)
        rows = list(enumerate(r, 2))

    ids = set()
    claim_decimals = set()
    status_ct, tag_ct = Counter(), Counter()
    resolvable_evidenced = inrepo_checked = 0
    backed = load_backed_decimals()                         # repo -> backed CC decimals (pinned manifests)
    xrepo_resolved = xrepo_pending = 0
    resolved_by_repo = Counter()

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

        has_resolvable = False
        for tok in ev.split():
            if ":" not in tok:
                errors.append(f"L{ln} [{cid}]: malformed evidence token '{tok}'")
                continue
            tag, ptr = tok.split(":", 1)
            if tag not in TAGS:
                errors.append(f"L{ln} [{cid}]: unknown tag '{tag}'")
                continue
            tag_ct[tag] += 1
            if tag == "normative-only":
                continue
            if ptr.startswith("@"):                       # in-repo
                inrepo_checked += 1
                if not os.path.exists(os.path.join(ROOT, ptr[1:])):
                    errors.append(f"L{ln} [{cid}]: dead in-repo pointer '{ptr}'")
                elif tag in RESOLVABLE_TAGS:
                    has_resolvable = True
            elif tag in RESOLVABLE_TAGS:                  # cross-repo: resolve by decimal vs pinned manifest
                repo = re.split(r"[#/:]", ptr, 1)[0]
                if repo in backed and dec in backed[repo]:
                    xrepo_resolved += 1
                    resolved_by_repo[repo] += 1
                    has_resolvable = True                 # backed by a pinned sibling manifest → counts as evidence
                elif repo in backed:
                    xrepo_pending += 1
                    warnings.append(f"L{ln} [{cid}]: {tag} pointer '{ptr}' — {repo} manifest (pinned) does not yet back CC {dec}")
                else:
                    xrepo_pending += 1
                    warnings.append(f"L{ln} [{cid}]: cross-repo {tag} pointer '{ptr}' unresolved (no pinned {repo} manifest yet)")

        if has_resolvable:
            resolvable_evidenced += 1
        if dec != "corpus":
            claim_decimals.add(dec)

    # --- coverage: every normative-bearing section should carry >= 1 claim ---
    norm = load_normative_sections()
    covered = {d for d in norm if d in claim_decimals}
    uncovered = sorted((norm[d], d) for d in norm if d not in covered)
    cov_pct = 100.0 * len(covered) / len(norm) if norm else 100.0

    print("=== CC evidence registry (claims.tsv) ===")
    print(f"claims: {len(rows)}")
    print("status: " + ", ".join(f"{k}={v}" for k, v in sorted(status_ct.items())))
    print("tags:   " + ", ".join(f"{k}={v}" for k, v in sorted(tag_ct.items())))
    print(f"in-repo pointers checked: {inrepo_checked}")
    print(f"claims with resolvable evidence (in-repo @ or pinned-manifest-backed): {resolvable_evidenced}/{len(rows)}")
    print(f"\n=== cross-repo resolution (against pinned manifests) ===")
    if backed:
        print("pinned manifests: " + ", ".join(f"{k}({len(v)} decimals)" for k, v in sorted(backed.items())))
        print(f"pointers RESOLVED: {xrepo_resolved} — " + ", ".join(f"{k}={v}" for k, v in sorted(resolved_by_repo.items())))
        unpinned = sorted({re.split(r'[#/:]', p, 1)[0] for r in rows for tok in r[1]['evidence'].split()
                           if ':' in tok and (p := tok.split(':', 1)[1])
                           and tok.split(':', 1)[0] in RESOLVABLE_TAGS
                           and re.split(r'[#/:]', p, 1)[0] not in backed})
        print(f"pointers PENDING:  {xrepo_pending} (unpinned repos: {', '.join(unpinned) or 'none'} — plus decimals a pinned manifest does not yet back)")
    else:
        print("(no evidence_pins.tsv — all cross-repo pointers pending)")
    print(f"\n=== normative coverage (P2) ===")
    print(f"normative-bearing sections: {len(norm)} | covered by >=1 claim: {len(covered)} ({cov_pct:.0f}%)")
    if uncovered:
        print("top uncovered normative-density sections:")
        for c, d in sorted(uncovered, reverse=True)[:12]:
            print(f"  {d:12} {c:3} MUST/SHALL")

    if warnings:
        print(f"\n{len(warnings)} warning(s) [cross-repo pending — see the downstream evidence issues]:")
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
