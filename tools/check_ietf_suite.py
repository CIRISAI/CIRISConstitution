#!/usr/bin/env python3
"""The CIRIS SCITT drafts land as one suite (ietf/SUITE.tsv).

For every draft source in ietf/ (the working `<name>.md` of each suite row that is in-tree):
  - each sibling it cites (an I-D.moore-scitt-ciris-* reference) names the revision SUITE.tsv releases, or an earlier
    one where the citing draft was published before the sibling's newer revision (a note, not an error);
  - a normative sibling reference follows the suite's `depends` order, and nothing cites up it normatively;
  - every draft that pins the CC pins the same tag;
  - a row marked in-tree has its stamped `<name>-<rev>.txt` in ietf/.
--release also refuses any row still pending: the suite is cut whole.

Run: python3 tools/check_ietf_suite.py [--release]
"""
import csv, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IETF = os.path.join(ROOT, "ietf")


def suite():
    with open(os.path.join(IETF, "SUITE.tsv"), encoding="utf-8") as f:
        return list(csv.DictReader((l for l in f if not l.startswith("#")), delimiter="\t"))


def refs(src):
    """{draft name: (rev, section)} for each I-D.moore-scitt-ciris-* reference in the YAML front matter."""
    head = src.split("\n---", 2)[0] if src.startswith("---") else src.split("--- abstract")[0]
    out, section, cur = {}, None, None
    for line in head.splitlines():
        if re.match(r"^(normative|informative):\s*$", line): section = line.split(":")[0]; continue
        if re.match(r"^\S", line): section = None if not line.startswith(("normative", "informative")) else section
        m = re.match(r"^  (I-D\.moore-scitt-ciris-[a-z-]+):\s*$", line)
        if m and section: cur = m.group(1); continue
        m = re.match(r"^\s+Internet-Draft:\s*(draft-moore-scitt-ciris-[a-z-]+?)-(\d\d)\s*$", line)
        if m and cur and section: out[m.group(1)] = (m.group(2), section); cur = None
    return out


def main():
    rows = suite(); by = {r["name"]: r for r in rows}; errs, notes, tags = [], [], {}
    for r in rows:
        if "--release" in sys.argv and r["status"] != "in-tree":
            errs.append(f"{r['name']}: still {r['status']} on {r['branch']}; the suite is cut whole")
        if r["status"] != "in-tree": continue
        if not os.path.exists(os.path.join(IETF, f"{r['name']}-{r['rev']}.txt")):
            errs.append(f"{r['name']}: in-tree, and ietf/{r['name']}-{r['rev']}.txt is missing")
        p = os.path.join(IETF, f"{r['name']}.md")
        if not os.path.exists(p): errs.append(f"{r['name']}: no working source ietf/{r['name']}.md"); continue
        src = open(p, encoding="utf-8").read()
        for name, (rev, section) in refs(src).items():
            if name == r["name"]: continue
            if name not in by: errs.append(f"{r['name']}: cites {name}, which is not in SUITE.tsv"); continue
            if rev > by[name]["rev"]: errs.append(f"{r['name']}: cites {name}-{rev}; the suite releases -{by[name]['rev']}")
            elif rev < by[name]["rev"]: notes.append(f"{r['name']}-{r['rev']} cites {name}-{rev}, published before -{by[name]['rev']}; its next revision cites the newer one")
            deps = by[r["name"]]["depends"].split()
            if section == "normative" and name not in deps:
                errs.append(f"{r['name']}: cites {name} normatively against the suite's order (depends: {' '.join(deps) or '-'})")
        m = re.search(r"CIRISConstitution/tree/(v1\.0-rc\d+)", src)
        if m: tags[r["name"]] = m.group(1)
    if len(set(tags.values())) > 1: errs.append("the drafts pin different CC tags: " + ", ".join(f"{k} {v}" for k, v in tags.items()))
    for n in notes: print("ietf suite: note: " + n)
    for e in errs: print("ietf suite: error: " + e)
    print(f"ietf suite: {len(rows)} drafts ({sum(r['status'] == 'in-tree' for r in rows)} in tree), CC tag {', '.join(sorted(set(tags.values()))) or 'none'}; {len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
