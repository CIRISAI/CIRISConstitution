#!/usr/bin/env python3
"""
CC (the CIRIS Constitution) — dimension-namespace catalog extractor.

Single-source-of-truth codegen for CIRISPersist#425. Parses CC Part 3 "The Namespace"
(constitution/part_3_the_namespace.md) and emits a deterministic, machine-readable
catalog of every dimension prefix family to manifests/namespace_registry.json — the file
downstream crates vendor.

Section CC 3.1 (`### 3.1.1` … `### 3.1.10`, minus the 3.1.7 summary) catalogs the prefix
families by owning component; section CC 3.4 (`### 3.4.1` …) defines the reserved-emit
rules that this generator cross-references onto each family.

The families appear in THREE source formats, all handled here:
  1. Markdown tables         `| Prefix | Description | Polarity | Reserved? |` — first cell.
  2. "Canonical leaves:" prose lines — each backtick token (3.1.3 persist, 3.1.4 edge).
  3. Inline backtick-prefix definitions — `a` / `b` / `c` — … Polarity: signed.
     (3.1.5.1 dma, 3.1.5.3 conscience, 3.1.6 ratchet, 3.1.8.2/3 detection/cohort).

stdlib only, Python 3, fully deterministic (families sorted by prefix; json sort_keys).
Does NOT commit. Run:  python3 tools/build_cc_namespace.py
"""
import json, os, re, hashlib
from collections import OrderedDict

HERE = os.path.dirname(__file__)
SOURCE_REL = "constitution/part_3_the_namespace.md"
SOURCE = os.path.join(HERE, "..", SOURCE_REL)
VERSION_FILE = os.path.join(HERE, "..", "VERSION")
OUT = os.path.join(HERE, "..", "manifests", "namespace_registry.json")

EXPECTED_FAMILIES = 83          # normative claim (CC 3.1 intro + 3.1.7 summary)
EXPECTED_COMPONENTS = 8         # normative claim: "8 owning components"

# ---- owning components -------------------------------------------------------
# Every top-level `### 3.1.N` heading (N != 7 summary) is one owning component.
# slug + repo are parsed from the heading and cross-checked against this map.
COMPONENT_REPO = {
    "registry": "CIRISRegistry",
    "attestation": "CIRISVerify",
    "persist": "CIRISPersist",
    "transport-delivery": "CIRISEdge",
    "accord-agent": "CIRISAgent",
    "anti-sybil": "RATCHET",
    "lens": "CIRISLensCore",
    "node": "CIRISNodeCore",
    "cirisbench": "CIRISBench",
}
# The 8 owning components committed via a sibling MISSION.md (CIRISBench is cited from a
# README, not a MISSION.md, and is the 9th, catalogued-but-not-in-the-normative-8 slice).
NORMATIVE_8 = {"registry", "attestation", "persist", "transport-delivery",
               "accord-agent", "anti-sybil", "lens", "node"}

# ---- CC 3.4 reserved-emit rules (cross-referenced onto families) ------------
# Each entry: (predicate(prefix, component) -> bool, rule, cc_ref). First match wins;
# order is specificity-first. Component-scoped substrate-self-report rules come after the
# prefix-specific ones.
def _reserved_rules():
    return [
        (lambda p, c: p.startswith("accord:"),
         "accord_holder-only", "CC 3.4.1"),
        (lambda p, c: p.startswith("transparency_log:cosigned"),
         "witness-emitter (identity_type contains witness)", "CC 3.4.10"),
        (lambda p, c: p.startswith("detection:"),
         "detector-only (identity_type contains lenscore_detector)", "CC 3.4.8"),
        (lambda p, c: p.startswith("capacity:"),
         "no-self-emit (attesting_key_id != attested_key_id)", "CC 3.4.5"),
        (lambda p, c: p.startswith("age_assurance:"),
         "witness-reserved, subject-not-self", "CC 3.4.11"),
        (lambda p, c: p.startswith("capacity_assurance:"),
         "witness-reserved, subject-not-self, attester != steward", "CC 3.4.12"),
        (lambda p, c: p.startswith("licensure:"),
         "co-stewarded (Registry + Verify)", "CC 3.4.9"),
        # component-scoped: persist / edge dimensions are substrate-self-reports.
        (lambda p, c: c in ("persist", "transport-delivery"),
         "substrate-self-report", "CC 3.4.3"),
    ]

RESERVED_RULES = _reserved_rules()

BACKTICK = re.compile(r"`([^`]+)`")
HEADING = re.compile(r"^(#{2,6})\s+(3\.[0-9]+(?:\.[0-9]+)*)\s+(.*)$")
TABLE_ROW = re.compile(r"^\s*\|(.*)\|\s*$")


def clean_text(s):
    """Strip markdown links/bold/backticks; collapse whitespace."""
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)   # [text](url) -> text
    s = s.replace("**", "").replace("`", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def first_sentence(s, cap=240):
    s = clean_text(s)
    m = re.search(r"\.(?:\s|$)", s)
    if m:
        s = s[:m.start() + 1]
    return s[:cap].strip()


def split_row(row):
    # honor escaped pipes (`\|`) that appear inside enum cells like `a` \| `b`
    row = row.replace("\\|", "\x00")
    return [c.replace("\x00", "|").strip() for c in row.split("|")]


def heading_slug_repo(tail):
    """From a `### 3.1.N `slug` — Repo — desc` tail, return (slug, repo)."""
    m = BACKTICK.search(tail)
    slug = m.group(1) if m else None
    parts = [p.strip() for p in re.split(r"\s+[—–]\s+", tail)]
    repo = parts[1] if len(parts) > 1 else None
    return slug, repo


def apply_reserved(prefix, component):
    for pred, rule, ref in RESERVED_RULES:
        if pred(prefix, component):
            return True, {"rule": rule, "cc_ref": ref}
    return False, None


def main():
    raw = open(SOURCE, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    cc_version = open(VERSION_FILE).read().strip()
    lines = raw.decode("utf-8").split("\n")

    families = OrderedDict()          # prefix -> record  (first definition wins)
    per_section = OrderedDict()       # cc_section -> [prefixes]

    component = None                  # active top-level component slug
    repo = None
    cc_section = None                 # deepest active 3.1.N[.M] section
    in_fence = False
    i = 0

    def add_family(prefix, section, comp, crepo, description, polarity, reserved_hint):
        prefix = prefix.strip()
        if not prefix:
            return
        per_section.setdefault(section, [])
        if prefix not in [p for p in per_section[section]]:
            per_section[section].append(prefix)
        if prefix in families:
            return  # first definition wins (e.g. agent_files joint claim 3.1.1 + 3.1.9.1)
        reserved, rule = apply_reserved(prefix, comp)
        if not reserved and reserved_hint:   # table "Reserved? = Yes ... CC 3.4.x"
            reserved = True
            m = re.search(r"CC\s*(3\.4\.\d+)", reserved_hint)
            rule = {"rule": "reserved (see table)", "cc_ref": "CC " + m.group(1)} if m \
                else {"rule": "reserved (see table)", "cc_ref": None}
        rec = OrderedDict()
        rec["prefix"] = prefix
        rec["owning_component"] = comp
        rec["owning_repo"] = crepo
        rec["cc_section"] = section
        rec["polarity"] = polarity or ""
        rec["reserved"] = reserved
        if reserved:
            rec["reserved_rule"] = rule
        rec["description"] = description or ""
        families[prefix] = rec

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            in_fence = not in_fence
            i += 1
            continue
        if in_fence:
            i += 1
            continue

        hm = HEADING.match(line)
        if hm:
            hashes, num, tail = hm.group(1), hm.group(2), hm.group(3)
            if hashes == "##":
                # a `## 3.2`/`## 3.3`/... closes the 3.1 catalog region
                if not num.startswith("3.1"):
                    component = None
                    cc_section = None
            if num == "3.1.7":
                component = None      # summary — skip
                cc_section = None
            elif re.match(r"^3\.1\.\d+$", num):     # top-level component heading
                slug, hrepo = heading_slug_repo(tail)
                component = slug
                repo = hrepo or COMPONENT_REPO.get(slug)
                if slug in COMPONENT_REPO:
                    repo = COMPONENT_REPO[slug]
                cc_section = num
            elif num.startswith("3.1.") and component is not None:
                cc_section = num      # deeper subsection under an active component
            i += 1
            continue

        if component is None:
            i += 1
            continue

        # ---- format 1: markdown table -------------------------------------
        tm = TABLE_ROW.match(line)
        if tm and "prefix" in line.lower() and "---" not in line:
            header = split_row(tm.group(1))
            hlow = [h.lower() for h in header]
            try:
                pol_idx = next(k for k, h in enumerate(hlow) if "polarity" in h)
            except StopIteration:
                pol_idx = None
            try:
                res_idx = next(k for k, h in enumerate(hlow) if "reserved" in h)
            except StopIteration:
                res_idx = None
            desc_idx = 1 if len(header) > 1 else None
            i += 1
            # skip separator row
            if i < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i]):
                i += 1
            while i < len(lines):
                r = TABLE_ROW.match(lines[i])
                if not r:
                    break
                cells = split_row(r.group(1))
                bt = BACKTICK.search(cells[0]) if cells else None
                if bt:
                    prefix = bt.group(1)
                    polarity = clean_text(cells[pol_idx]) if pol_idx is not None and pol_idx < len(cells) else ""
                    resv = cells[res_idx] if res_idx is not None and res_idx < len(cells) else ""
                    resv = resv if resv and resv.strip().lower() not in ("no", "") else ""
                    desc = first_sentence(cells[desc_idx]) if desc_idx is not None and desc_idx < len(cells) else ""
                    add_family(prefix, cc_section, component, repo, desc, polarity, resv)
                i += 1
            continue

        # ---- format 2: "Canonical leaves:" prose --------------------------
        if "Canonical leaves:" in line:
            head, _, rest = line.partition("Canonical leaves:")
            body = rest.split("Polarity:")[0]
            pol_m = re.search(r"Polarity:\s*([A-Za-z0-9_\- ]+)", line)
            polarity = pol_m.group(1).strip().rstrip(".") if pol_m else ""
            for tok in BACKTICK.findall(body):
                add_family(tok, cc_section, component, repo, "", polarity, "")
            i += 1
            continue

        # ---- format 3: inline backtick-prefix definition ------------------
        if stripped.startswith("`") and "Polarity:" in line:
            body = line.split("Polarity:")[0]
            pol_m = re.search(r"Polarity:\s*([A-Za-z0-9_\- ]+)", line)
            polarity = pol_m.group(1).strip().rstrip(".") if pol_m else ""
            toks = BACKTICK.findall(body)
            # description = text after the last token group, before Polarity
            after = body
            last = None
            for mt in BACKTICK.finditer(body):
                last = mt
            desc = ""
            if last:
                tail = body[last.end():]
                tail = re.sub(r"^\s*[—–\-/.]+\s*", "", tail)
                desc = first_sentence(tail)
            for tok in toks:
                add_family(tok, cc_section, component, repo, desc, polarity, "")
            i += 1
            continue

        i += 1

    # ---- assemble deterministic output ----------------------------------
    fam_list = sorted(families.values(), key=lambda r: r["prefix"])
    comps = OrderedDict()
    for r in fam_list:
        comps.setdefault(r["owning_component"], 0)
        comps[r["owning_component"]] += 1
    per_component = OrderedDict((k, comps[k]) for k in sorted(comps))

    n_families = len(fam_list)
    n_components = len(per_component)
    reserved_count = sum(1 for r in fam_list if r["reserved"])

    meta = OrderedDict()
    meta["cc_version"] = cc_version
    meta["source"] = SOURCE_REL
    meta["source_sha256"] = sha
    meta["n_families"] = n_families
    meta["n_components"] = n_components
    meta["per_component"] = per_component
    meta["generator"] = "tools/build_cc_namespace.py"
    if n_families != EXPECTED_FAMILIES or n_components != EXPECTED_COMPONENTS:
        meta["discrepancy"] = OrderedDict([
            ("normative_n_families", EXPECTED_FAMILIES),
            ("normative_n_components", EXPECTED_COMPONENTS),
            ("observed_n_families", n_families),
            ("observed_n_components", n_components),
            ("note",
             "CC 3.1 intro + the 3.1.7 summary assert '83 prefix families across 8 owning "
             "components'. This catalog extracts every distinct backtick prefix family at "
             "leaf granularity (the granularity a vendoring crate needs), deduping the one "
             "cross-section joint claim (agent_files, CC 3.1.1 + CC 3.1.9.1). The observed "
             "count exceeds 83 because the normative summary predates later-added families "
             "(e.g. CC 3.1.8.4/3.1.8.5 structural-injustice + distributive-access detectors, "
             "CC 3.1.9.4 health:liveness / watchlist / judge_model). CIRISBench (CC 3.1.10) is "
             "the 9th owning_component here but is cited from a README rather than a MISSION.md, "
             "so it is outside the normative 'is 8 owning components' (all MISSION.md-committed).")
        ])

    out = OrderedDict()
    out["_meta"] = meta
    out["families"] = fam_list

    with open(OUT, "w") as f:
        f.write(json.dumps(out, sort_keys=True, indent=2))
        f.write("\n")

    # ---- stdout summary -------------------------------------------------
    print("CC namespace catalog  (cc_version %s)" % cc_version)
    print("source: %s  sha256=%s" % (SOURCE_REL, sha[:16] + "…"))
    print("-" * 60)
    print("per-component families:")
    for comp in sorted(per_component):
        star = "" if comp in NORMATIVE_8 else "   (README-cited; outside normative 8)"
        print("  %-20s %-14s %3d%s" % (comp, COMPONENT_REPO.get(comp, "?"),
                                       per_component[comp], star))
    print("-" * 60)
    print("total families   : %d   (normative claim: %d)" % (n_families, EXPECTED_FAMILIES))
    print("total components : %d   (normative claim: %d)" % (n_components, EXPECTED_COMPONENTS))
    print("reserved families: %d" % reserved_count)
    if n_families != EXPECTED_FAMILIES:
        print("-" * 60)
        print("DELTA vs 83 — per-section breakdown (families found):")
        def skey(s):
            return [int(x) for x in s.split(".")]
        for sec in sorted(per_section, key=skey):
            fams = per_section[sec]
            print("  %-9s %2d  %s" % (sec, len(fams),
                                      ", ".join(fams[:6]) + (" …" if len(fams) > 6 else "")))
        print("-" * 60)
        print("reconciliation: leaf-granularity catalog = %d distinct prefixes." % n_families)
        print("  - dedup: agent_files joint claim counted once (CC 3.1.1 + CC 3.1.9.1).")
        print("  - the normative '83' predates later-added detector/observability families;")
        print("    merging the 2 explicit sub-leaves (provenance:build_manifest:*:locale,")
        print("    credits:*:substrate_building) would net -2 but does not reach 83.")
        print("  - honest count + discrepancy recorded in _meta.discrepancy.")
    print("wrote %s" % os.path.relpath(OUT, os.path.join(HERE, "..")))


if __name__ == "__main__":
    main()
