#!/usr/bin/env python3
"""
CC — the counts the formal prose quotes, kept equal to the tables they count.

The figures a reader (or a deck) takes from formal/README.md, formal/ADEQUACY.md and
formal/cewp_node/README.md are computed here from their sources and compared with every
place the prose states them:

  states, variables, planes      formal/STATE_TABLE.tsv
  properties, models             formal/INVARIANTS.tsv
  variables with / without an invariant, and the A11 list of those without
  atoms, catalogue version       manifests/topology_vocabulary.json
  catalogue entries, commit      formal/cewp_node/catalog/ (T*.yaml, PIN.tsv)
  states exercised               tools/catalogue_coverage.py (its first line)

and with the counts block of manifests/csd4_chain.json, so the chain, the tables and the
prose cannot disagree. Each pattern must match at least once in its file: a reworded
sentence fails loudly instead of escaping the check. Exit 1 on any failure.
Run:  python3 tools/check_formal_counts.py
"""
import csv, glob, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORDS = {10: "ten", 20: "twenty", 30: "thirty"}


def rows(p):
    with open(os.path.join(ROOT, p), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def counts():
    st, iv = rows("formal/STATE_TABLE.tsv"), rows("formal/INVARIANTS.tsv")
    variables = {r["variable"] for r in st}
    named = set()
    for r in iv:
        named |= set(r["variables"].split())
    voc = json.load(open(os.path.join(ROOT, "manifests/topology_vocabulary.json"), encoding="utf-8"))
    pin = dict(r[:2] for r in csv.reader(open(os.path.join(ROOT, "formal/cewp_node/catalog/PIN.tsv")), delimiter="\t") if r)
    entries = sorted(glob.glob(os.path.join(ROOT, "formal/cewp_node/catalog/T*.yaml")))
    cov = subprocess.run([sys.executable, os.path.join(ROOT, "tools/catalogue_coverage.py")],
                         capture_output=True, text=True, cwd=ROOT).stdout
    m = re.search(r"(\d+)/(\d+) states exercised", cov)
    return {
        "states": len(st), "variables": len(variables), "planes": len({r["plane"] for r in st}),
        "properties": len(iv), "models": len({r["model"] for r in iv}),
        "with_inv": len(variables & named), "without": sorted(variables - named),
        "atoms": len(voc["atoms"]), "catalogue_version": voc["_meta"]["catalogue_version"],
        "entries": len(entries), "commit": pin["commit"][:8],
        "exercised": int(m.group(1)) if m else None,
    }


def main():
    c = counts()
    errs = []
    chain = json.load(open(os.path.join(ROOT, "manifests/csd4_chain.json"), encoding="utf-8"))["_meta"]["counts"]
    for k, mine in (("states", c["states"]), ("invariants", c["properties"]), ("atoms", c["atoms"]), ("entries", c["entries"])):
        if chain.get(k) != mine:
            errs.append(f"manifests/csd4_chain.json counts.{k} = {chain.get(k)}, the tables give {mine} (regenerate the chain)")

    last = c["entries"] - 1
    # (file, pattern, expected groups); every pattern must match at least once
    checks = [
        ("formal/README.md", r"written as a property: (\d+) of them today, across (\d+) models", (c["properties"], c["models"])),
        ("formal/README.md", r"\((\d+) states over (\d+) variables in (\d+) planes\)", (c["states"], c["variables"], c["planes"])),
        ("formal/README.md", r"\((\w+) entries, `T0`–`T(\d+)`", (WORDS.get(c["entries"], str(c["entries"])), last)),
        ("formal/cewp_node/README.md", r"the (\w+) entries `T0`–`T(\d+)`", (WORDS.get(c["entries"], str(c["entries"])), last)),
        ("formal/cewp_node/README.md", r"\((\d+) states, (\d+) variables, (\d+) planes\) and the (\d+) properties",
         (c["states"], c["variables"], c["planes"], c["properties"])),
        ("formal/cewp_node/README.md", r"the (\d+) atoms \(catalogue version (\d+)\)", (c["atoms"], c["catalogue_version"])),
        ("formal/ADEQUACY.md", r"`STATE_TABLE\.tsv` \((\d+) states, (\d+) variables\) \+ `INVARIANTS\.tsv` \((\d+) properties\)",
         (c["states"], c["variables"], c["properties"])),
        ("formal/ADEQUACY.md", r"(\d+) of (\d+) variables carry an invariant; the (\d+) without are",
         (c["with_inv"], c["variables"], len(c["without"]))),
        ("formal/ADEQUACY.md", r"`cewp_node/catalog` \(version (\d+), T0–T(\d+), CIRISServer ([0-9a-f]{8})\)",
         (c["catalogue_version"], last, c["commit"])),
        ("formal/ADEQUACY.md", r"T0–T(\d+) exercise (\d+) of (\d+) states", (last, c["exercised"], c["states"])),
        ("formal/ADEQUACY.md", r"the (\d+) unexercised are", ((c["states"] - c["exercised"]) if c["exercised"] is not None else None,)),
    ]
    for f, pat, want in checks:
        text = open(os.path.join(ROOT, f), encoding="utf-8").read()
        found = list(re.finditer(pat, text))
        if not found:
            errs.append(f"{f}: no sentence matches /{pat}/ (reworded? update tools/check_formal_counts.py with it)")
        for m in found:
            got = tuple(g if not g.isdigit() else int(g) for g in m.groups())
            exp = tuple(want)
            if got != exp:
                errs.append(f"{f}: '{m.group(0)}' states {got}, the sources give {exp}")

    # the A11 list of variables without an invariant names exactly those variables
    adq = open(os.path.join(ROOT, "formal/ADEQUACY.md"), encoding="utf-8").read()
    m = re.search(r"the \d+ without are ([^|]+)\|", adq)
    if m:
        listed = sorted(re.findall(r"`([^`]+)`", m.group(1)))
        if listed != c["without"]:
            errs.append(f"formal/ADEQUACY.md A11: lists {listed}, the tables give {c['without']}")

    print(f"formal counts: {c['states']} states, {c['variables']} variables, {c['planes']} planes; "
          f"{c['properties']} properties in {c['models']} models; {c['with_inv']}/{c['variables']} variables with an invariant; "
          f"{c['atoms']} atoms (catalogue v{c['catalogue_version']}, {c['entries']} entries at {c['commit']}); "
          f"{c['exercised']}/{c['states']} states exercised")
    for e in errs:
        print("ERR", e)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
