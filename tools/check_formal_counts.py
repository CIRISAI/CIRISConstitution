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
prose cannot disagree. README.md's figures are held the same way:

  established, normative, staged rows   constitution/claims.tsv (status column)
  models and properties                 formal/INVARIANTS.tsv
  the edition of "This tree"            VERSION
  divergence entries, by status and by implementer   manifests/divergences.json

and formal/derivation/README.md's headline numbers against formal/derivation/rule_inventory.tsv
(statements by Part, scope and role) and rule_cut_candidates.tsv (blocks).

Every run also alters the first figure of each sentence matched and requires the comparison to
report it (the deliberate breaks). Each pattern must match at least once in its file: a reworded
sentence fails loudly instead of escaping the check. Exit 1 on any failure.
Run:  python3 tools/check_formal_counts.py
"""
import csv, glob, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORDS = {10: "ten", 20: "twenty", 30: "thirty"}
SMALL = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
         "seventeen eighteen nineteen").split()


def num(g):
    """A stated figure as an integer: digits (with thousands commas) or a number word below twenty."""
    if g.replace(",", "").isdigit():
        return int(g.replace(",", ""))
    return SMALL.index(g.lower()) if g.lower() in SMALL else g


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
    status = {}
    for r in rows("constitution/claims.tsv"):
        status[r["status"]] = status.get(r["status"], 0) + 1
    version = open(os.path.join(ROOT, "VERSION"), encoding="utf-8").read().strip()
    dmeta = json.load(open(os.path.join(ROOT, "manifests/divergences.json"), encoding="utf-8"))["_meta"]
    dst, dimp = dmeta["by_status"], dmeta["by_implementer"]
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
        ("README.md", r"(\d+) established rows, (\d+) normative, (\d+) staged",
         (status.get("established", 0), status.get("normative", 0), status.get("staged", 0))),
        ("README.md", r"(\w+) machine-checked models carrying (\d+) properties", (c["models"], c["properties"])),
        ("README.md", r"\*\*This tree:\*\* ([0-9][^ ,]*)", (version,)),
        ("README.md", r"differs from this text: (\d+) entries, of which (\d+) runnable, (\d+) stated and (\d+) wording only",
         (dmeta["total"], dst.get("runnable", 0), dst.get("stated", 0), dst.get("wording-only", 0))),
        ("README.md", r"\[persist\]\([^)]*\) (\d+), \[tooling\]\([^)]*\) (\d+), "
                      r"\[agent\]\([^)]*\) (\d+), \[edge\]\([^)]*\) (\d+)\.",
         tuple(dimp.get(k, 0) for k in ("persist", "tooling", "agent", "edge"))),
    ]
    if sum(dimp.values()) != dmeta["total"] or set(dimp) - {"persist", "tooling", "agent", "edge"}:
        errs.append(f"README.md names the implementers persist, tooling, agent and edge; manifests/divergences.json has {dimp}")
    if sum(dst.values()) != dmeta["total"] or set(dst) - {"runnable", "stated", "wording-only"}:
        errs.append(f"README.md names the statuses runnable, stated and wording only; manifests/divergences.json has {dst}")
    def compare(f, text, pat, want):
        out = []
        found = list(re.finditer(pat, text))
        if not found:
            out.append(f"{f}: no sentence matches /{pat}/ (reworded? update tools/check_formal_counts.py with it)")
        for m in found:
            got = tuple(num(g) for g in m.groups())
            exp = tuple(want)
            if got != exp:
                out.append(f"{f}: '{m.group(0)}' states {got}, the sources give {exp}")
        return out

    caught = missed = 0
    for f, pat, want in checks:
        text = open(os.path.join(ROOT, f), encoding="utf-8").read()
        errs += compare(f, text, pat, want)
        m = re.search(pat, text)
        if m:   # the deliberate break: the first figure of the sentence altered must be reported
            g = m.group(1)
            alt = str(num(g) + 1) if isinstance(num(g), int) else g + "x"
            broken = text[:m.start(1)] + alt + text[m.end(1):]
            if compare(f, broken, pat, want):
                caught += 1
            else:
                missed += 1
                errs.append(f"{f}: the deliberate break of /{pat}/ (first figure {g!r} altered) was not reported")

    # formal/derivation/README.md: the headline numbers of the rule inventory, as name -> count
    def tally(rows_, col, rename=lambda v: v):
        out = {}
        for r in rows_:
            out[rename(r[col])] = out.get(rename(r[col]), 0) + 1
        return out

    def stated(block):
        return {n.strip(): int(v.replace(",", "")) for n, v in re.findall(r"([A-Za-z]+(?: \d)?)\s+([\d,]+)", block)}

    def tsv_rows(p):
        with open(os.path.join(ROOT, p), newline="", encoding="utf-8") as f:
            return list(csv.DictReader((l for l in f if not l.startswith("#")), delimiter="\t", quoting=csv.QUOTE_NONE))

    inv = tsv_rows("formal/derivation/rule_inventory.tsv")
    cut = tsv_rows("formal/derivation/rule_cut_candidates.tsv")
    head_want = (len(inv), tally(inv, "file", lambda v: "Part " + v[1:]), tally(inv, "scope"), tally(inv, "role"), len(cut))
    head_pat = r"Headline numbers: ([\d,]+) statements \(([^)]*)\); by scope ([^;]*); by role ([^.]*)\. ([\d,]+) cut-candidate"

    def headline(text):
        m = re.search(head_pat, text)
        if not m:
            return [f"formal/derivation/README.md: no sentence matches /{head_pat}/"]
        got = (int(m.group(1).replace(",", "")), stated(m.group(2)), stated(m.group(3)), stated(m.group(4)), int(m.group(5)))
        return [] if got == head_want else [f"formal/derivation/README.md: headline numbers state {got}, the inventory gives {head_want}"]

    der = open(os.path.join(ROOT, "formal/derivation/README.md"), encoding="utf-8").read()
    errs += headline(der)
    hm = re.search(head_pat, der)
    if hm and headline(der[:hm.start(1)] + "1" + der[hm.start(1):]):
        caught += 1
    else:
        missed += 1
        errs.append("formal/derivation/README.md: the deliberate break of the headline numbers was not reported")

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
          f"{c['exercised']}/{c['states']} states exercised; README.md register {status.get('established', 0)}/"
          f"{status.get('normative', 0)}/{status.get('staged', 0)}, divergences {dmeta['total']}; "
          f"deliberate breaks caught {caught} of {caught + missed}")
    for e in errs:
        print("ERR", e)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
