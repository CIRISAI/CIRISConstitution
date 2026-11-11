#!/usr/bin/env python3
"""Every statement a rule's home section carried is still carried by its entry.

A rule lands in the rulebook register one at a time: its home section is rewritten as one entry.
formal/derivation/rule_entries.tsv lists, for each rule landed so far, every inventory statement
whose home is that section, and the phrase of the entry that carries it. This check reads the
home section out of its Part and fails when

  1. an inventory statement keyed to a landed rule and its home section has no row here;
  2. a row's phrase is not in the home section as it now reads;
  3. a sentence of the entry runs past 40 words (tables, lists and the paragraphs of
     neighbouring rules, which land with their own rules, are not counted; where a rule's home
     is one headed block of a larger section, the entry is that block);
  4. a Part calls a landed rule by a name its entry does not use, so a second wording of the
     rule cannot grow beside the entry.

  python3 tools/check_rule_entries.py
"""
import csv, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = {"p1": "part_1_foundation.md", "p2": "part_2_the_grammar.md", "p3": "part_3_the_namespace.md",
         "p4": "part_4_composition_governance.md", "p5": "part_5_transport_substrate.md",
         "p6": "part_6_the_coherence_mathematics.md", "p7": "part_7_lifecycle_stewardship.md"}
HOME_PART = {"2": "p2", "3": "p3", "4": "p4", "5": "p5", "6": "p6", "7": "p7", "1": "p1"}
# Paragraphs inside a home section that belong to a rule not yet landed, by their bold lead.
NEIGHBOURS = {"2.4.1.1": ("**`revoked_after`", "**A key revocation names its subject", "**A purge is a tombstone",
                          "**What the signer keeps"),
              "4.4.3.8": ("**Cold-start bootstrap", "**Capability gate", "**Two conferral planes",
                          "**Charter recovery lives", "**Genesis is tamper-evident"),
              "5.2": ("> **Scope (normative)", "**Substrate enforcement", "**Two layers, not one", "**Composition with the at-rest",
                      "**Recipient encryption-key resolution", "**Exclusion MUST NOT be silent", "**Locality dividend",
                      "**Boundary cases"),
              "3.2": ("**Adding a device",)}
# A rule whose home is one headed block of a larger section: the entry is that block alone.
WITHIN = {("owner_binding", "3.2"): "Who owns a key"}
MAX_WORDS = 40
# Names a landed rule is not called by: the entry's own words are the rule's only name.
OTHER_NAMES = {"withdraw": ("broadened `withdraws` admission", "broadened admission", "withdraws-isn't-retroactive",
                            "retraction carve-out", "2.4.1.1 carve-out", "third-party path"),
               "trust_fold": ("trust list", "trusted set", "pin set", "trust store"),
               "audience": ("target-membership", "recipient predicate", "one audience rule", "existence-invisible"),
               "owner_binding": ("owner binding", "steward binding", "ownership edge", "responsible steward")}


def section(part, number):
    lines = (ROOT / "constitution" / PARTS[part]).read_text().split("\n")
    start = next(i for i, l in enumerate(lines) if re.match(rf"#+ {re.escape(number)} ", l))
    depth = len(lines[start]) - len(lines[start].lstrip("#"))
    end = next((i for i in range(start + 1, len(lines)) if re.match(r"#+ ", lines[i])
                and len(lines[i]) - len(lines[i].lstrip("#")) <= depth), len(lines))
    return lines[start:end]


def block(sec, title):
    """The lines of one unnumbered heading inside a section, up to the next heading at its depth or above."""
    start = next(i for i, l in enumerate(sec) if re.match(rf"#+ {re.escape(title)}", l))
    depth = len(sec[start]) - len(sec[start].lstrip("#"))
    end = next((i for i in range(start + 1, len(sec)) if re.match(r"#+ ", sec[i])
                and len(sec[i]) - len(sec[i].lstrip("#")) <= depth), len(sec))
    return sec[start:end]


def main():
    entries = list(csv.DictReader((ROOT / "formal/derivation/rule_entries.tsv").open(), delimiter="\t"))
    inv = list(csv.DictReader((ROOT / "formal/derivation/rule_inventory.tsv").open(), delimiter="\t"))
    errs = []
    landed = sorted({(e["rule_key"], e["home"]) for e in entries})
    for key, home in landed:
        sec = section(HOME_PART[home[0]], home)
        if (key, home) in WITHIN:
            sec = block(sec, WITHIN[(key, home)])
        text = "\n".join(sec)
        mine = [e for e in entries if (e["rule_key"], e["home"]) == (key, home)]
        have = {(e["file"], e["line"], e["gist"]) for e in mine}
        for r in inv:
            if r["rule_key"] == key and r["section"] == home and (r["file"], r["line"], r["gist"]) not in have:
                errs.append(f"{key} {home}: no entry row for {r['file']}:{r['line']} {r['gist'][:70]}")
        for e in mine:
            if e["entry_phrase"] not in text:
                errs.append(f"{key} {home}: the entry no longer carries {e['file']}:{e['line']}: {e['entry_phrase'][:70]}")
        longest = 0
        for para in sec[1:]:
            if not para.strip() or para.startswith(("|", "- ")) or para.startswith(NEIGHBOURS.get(home, ())):
                continue
            plain = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", para)
            for s in re.split(r"(?<=[.])\s+(?=[A-Z*`])", plain):
                n = len(s.split())
                longest = max(longest, n)
                if n > MAX_WORDS:
                    errs.append(f"{key} {home}: a sentence of {n} words: {s[:70]}")
        for part, name in PARTS.items():
            for i, line in enumerate((ROOT / "constitution" / name).read_text().split("\n"), 1):
                for other in OTHER_NAMES.get(key, ()):
                    if other in line:
                        errs.append(f"{key} {home}: {part}:{i} calls the rule \"{other}\"; cite the entry instead")
        print(f"rule entries: {key} at CC {home}: {len(mine)} statements carried, longest sentence {longest} words")
    if errs:
        print("rule entries: FAIL"); [print("  " + e) for e in errs]
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
