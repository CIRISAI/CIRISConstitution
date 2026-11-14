#!/usr/bin/env python3
"""The four mapped works against the namespace registry: nothing a work was mapped to drops out (CC 8, Annex C).

The operational cross-walk maps four works (Magnifica Humanitas, the EU HLEG Ethics Guidelines for
Trustworthy AI, IEEE Ethically Aligned Design, the ASEAN Guide on AI Governance and Ethics) to wire
dimensions, unit by unit, and groups them under 27 stable dimension ids. This tool holds the
registry to that mapping in two tables under formal/derivation/:

  compliance_dimensions.tsv   one row per dimension id: its prefix, the attestations each work gives
                              it, the registry families under its stem and the sections that carry them
  compliance_wire_forms.tsv   one row per distinct wire form a work was mapped to: the work, how
                              many mapped lines carry it, the family it resolves to, and the answer
                              (resolves, open, or the registry's refusal token)

A wire form is resolved by the reference matcher (tools/cc_namespace_match.py) as written and, where
that owes only a version, with `:v1` appended, since the mapping was written without version segments.
`resolves` is a registered family with no refusal; `open` is vocabulary no row claims and none refuses.

The check recomputes both tables from manifests/namespace_registry.json and fails when

  1. a dimension id has no registered family under its stem and no structural anchor that exists;
  2. a family's section, or a structural anchor, is not a heading of Part 3;
  3. a wire form that resolved in the committed table no longer resolves (a loss);
  4. any other answer differs from the committed table (regenerate with --write and review the diff).

  python3 tools/check_compliance_wire_forms.py                    # check
  python3 tools/check_compliance_wire_forms.py --write            # rewrite the answers from the registry
  python3 tools/check_compliance_wire_forms.py --extract <dir>    # rebuild both tables from a checkout of the mapping
"""
import csv, glob, json, os, re, sys
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cc_namespace_match as m  # noqa: E402

ROOT = os.path.join(HERE, "..")
DIMS = os.path.join(ROOT, "formal", "derivation", "compliance_dimensions.tsv")
FORMS = os.path.join(ROOT, "formal", "derivation", "compliance_wire_forms.tsv")
PART3 = os.path.join(ROOT, "constitution", "part_3_the_namespace.md")
WORKS = OrderedDict([("v1.4", "MH"), ("EU_HLEG", "EU"), ("IEEE_EAD", "IEEE"), ("ASEAN", "ASEAN")])
# A dimension whose evidence is a structure and not a family of its own stem names the family that carries it.
STRUCTURAL = {"D23": "audit_chain:hash_continuity"}
DIM_HDR = ["id", "prefix", "tier", "MH", "EU", "IEEE", "ASEAN", "families", "sections"]
FORM_HDR = ["work", "wire_form", "lines", "family", "answer"]


def resolve(rules, form):
    fam, _, ref = m.match_family(rules, form)
    if ref is not None or fam is None:
        fam2, _, ref2 = m.match_family(rules, form + ":v1")
        if ref2 is None or fam is None:
            fam, ref = fam2, ref2
    if fam is not None and ref is None:
        return fam, "resolves"
    if fam is None and ref is None:
        return "", "open"
    return fam or "", ref


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path, hdr, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(hdr)
        for r in rows:
            w.writerow([r[h] for h in hdr])


def fill_dims(manifest, dims):
    for d in dims:
        stem = d["prefix"].split(":")[0]
        fams = [f for f in manifest["families"] if f["prefix"].split(":")[0] == stem]
        if not fams and d["id"] in STRUCTURAL:
            fams = [f for f in manifest["families"] if f["prefix"] == STRUCTURAL[d["id"]]]
        d["families"] = " ".join(f["prefix"] for f in fams)
        d["sections"] = " ".join(sorted({f.get("cc_section", "") for f in fams}))
    return dims


def fill_forms(rules, forms):
    for r in forms:
        r["family"], r["answer"] = resolve(rules, r["wire_form"])
    return forms


def extract(src):
    seed = open(os.path.join(src, "SEED_DIMENSIONS.yaml"), encoding="utf-8").read()
    dims = []
    for block in re.split(r"\n  - id: (?=D\d\d\n)", seed)[1:]:
        did = block[:3]
        prefix = re.search(r"\n\s+prefix: (\S+)", block).group(1)
        tier = re.search(r"\n\s+tier: (\S+)", block).group(1)
        att = re.search(r"attestations:\s*\{([^}]*)\}", block) or re.search(r"attestations:\n((?:\s+\w+: \d+\n)+)", block)
        counts = dict(re.findall(r"(MH|EU|IEEE|ASEAN): (\d+)", att.group(1)))
        dims.append(dict({"id": did, "prefix": prefix, "tier": tier}, **{w: counts.get(w, "0") for w in WORKS.values()}))
    lines = Counter()
    for path in sorted(glob.glob(os.path.join(src, "CONTRIBUTION_OBJECTS_*.md"))):
        work = next(v for k, v in WORKS.items() if k in os.path.basename(path))
        for line in open(path, encoding="utf-8"):
            mm = re.match(r'\s*dimension:\s*"?([^"#\n]+?)"?\s*(#.*)?$', line)
            if mm:
                lines[(work, mm.group(1).strip())] += 1
    order = list(WORKS.values())
    forms = [{"work": w, "wire_form": f, "lines": str(n)}
             for (w, f), n in sorted(lines.items(), key=lambda kv: (order.index(kv[0][0]), kv[0][1]))]
    return dims, forms


def main(argv):
    manifest = m.load_manifest()
    rules = m.Rules(manifest)
    if "--extract" in argv:
        dims, forms = extract(argv[argv.index("--extract") + 1])
        write_tsv(DIMS, DIM_HDR, fill_dims(manifest, dims))
        write_tsv(FORMS, FORM_HDR, fill_forms(rules, forms))
        print(f"compliance wire forms: wrote {len(dims)} dimensions and {len(forms)} wire forms")
        return 0
    old_dims, old_forms = read_tsv(DIMS), read_tsv(FORMS)
    new_dims = fill_dims(manifest, [dict(d) for d in old_dims])
    new_forms = fill_forms(rules, [dict(r) for r in old_forms])
    if "--write" in argv:
        write_tsv(DIMS, DIM_HDR, new_dims)
        write_tsv(FORMS, FORM_HDR, new_forms)
    headings = set(re.findall(r"^#{2,6} (\d+(?:\.\d+)+)\b", open(PART3, encoding="utf-8").read(), re.M))
    errs = []
    for d in new_dims:
        if not d["families"]:
            errs.append(f"{d['id']} {d['prefix']}: no registered family under its stem and no structural anchor")
        for s in d["sections"].split():
            if s not in headings:
                errs.append(f"{d['id']} {d['prefix']}: section {s} is not a heading of Part 3")
    for o, n in zip(old_dims, new_dims):
        if (o["families"], o["sections"]) != (n["families"], n["sections"]) and "--write" not in argv:
            errs.append(f"{n['id']}: families or sections differ from the committed table: {o['families']} -> {n['families']}")
    lost = changed = 0
    for o, n in zip(old_forms, new_forms):
        if (o["family"], o["answer"]) == (n["family"], n["answer"]):
            continue
        if o["answer"] == "resolves" and n["answer"] != "resolves":
            lost += 1
            errs.append(f"lost: {n['work']} {n['wire_form']} resolved to {o['family']} and now answers {n['answer']}")
        elif "--write" not in argv:
            changed += 1
            errs.append(f"changed: {n['work']} {n['wire_form']}: {o['family']} {o['answer']} -> {n['family']} {n['answer']}")
    if errs:
        print("compliance wire forms: FAIL")
        [print("  " + e) for e in errs]
        return 1
    tot = Counter()
    for r in new_forms:
        kind = r["answer"] if r["answer"] in ("resolves", "open") else "refused"
        tot[(r["work"], kind)] += int(r["lines"])
    n_lines = sum(tot.values())
    print(f"compliance wire forms: {len(new_dims)} dimensions, each with a registered family or a structural anchor; "
          f"{len(new_forms)} wire forms on {n_lines} mapped lines; none lost")
    for w in WORKS.values():
        print(f"  {w:6s} resolves {tot[(w, 'resolves')]:4d}  open {tot[(w, 'open')]:4d}  refused {tot[(w, 'refused')]:4d}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
