#!/usr/bin/env python3
"""Every statement a rule's home section carried is still carried by its entry.

A rule lands in the rulebook register one at a time: its home section is rewritten as one entry.
formal/derivation/rule_entries.tsv lists, for each rule landed so far, every inventory statement
whose home is that section, and the phrase of the entry that carries it. This check reads the
home section out of its Part and fails when

  1. an inventory statement keyed to a landed rule and its home section has no row here;
  2. a row's phrase is not in the home section as it now reads;
  3. a sentence of the entry runs past 40 words (a bold lead that ends in a full stop is a
     sentence of its own; the few sentences named in EXEMPT are kept whole; tables, lists and the paragraphs of
     neighbouring rules, which land with their own rules, are not counted; where a rule's home
     is one headed block of a larger section, the entry is that block, and where a headed block
     carries statements under many rule keys, each key's entry at that home is the block and
     the statements owed are the ones the inventory read inside it; a numbered subsection
     is its own home and is not read as part of its parent's entry);
  4. a Part calls a landed rule by a name its entry does not use, so a second wording of the
     rule cannot grow beside the entry;
  5. a statement marked as restating a rule sits in a paragraph that cites no section (a code
     line and a table row are not asked to cite; the few that cite nothing today are listed and
     the list only shrinks).

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
              "3.2": ("**Adding a device",),
              "3.1.3.2": ("**Why K is named in `subject_key_ids`", "**Not a membership rule: reverse quorum",
                          "**Who may write (normative)"),
              "4.4.3.4.3": ("**The Self (membership)", "**The pair is a data-management record",
                            "**Membership is standing", "**Conformance:", "**Transport (network presence)",
                            "**Worked login flow")}
# A rule whose home is one headed block of a larger section: the entry is that block alone.
WITHIN = {("owner_binding", "3.2"): "Who owns a key"}
# A headed block of a larger section that is one entry under many rule keys: every other key at
# that home reads the block, and owes the statements whose inventory line falls inside it.
BLOCK = {"3.2": ("Trust-root operational semantics", 897, 952)}
MAX_WORDS = 40
# A statement that says a rule again cites the section that states it. These restatements cite
# nothing yet (home, file, inventory line). The list only shrinks: the check fails on an uncited
# restatement that is not listed and on a listed one that now cites.
UNCITED_RESTATES = {
    ('1.15.1', 'p1', '323'),
    ('1.15.7', 'p1', '373'),
    ('1.16.6', 'p1', '438'),
    ('2.4', 'p2', '267'),
    ('2.6.6.3', 'p2', '862'),
    ('3.1.3', 'p3', '147'),
    ('3.3.5', 'p3', '1335'),
    ('3.3.6.2', 'p3', '1464'),
    ('4.2.6', 'p4', '247'),
    ('4.4.3.4.6', 'p4', '1036'),
    ('4.4.3.5', 'p4', '1053'),
    ('4.5.2.3', 'p4', '1454'),
    ('6.1.5.3', 'p6', '277'),
    ('7.2.3', 'p7', '107'),
    ('7.3.4', 'p7', '253'),
    ('7.5.8', 'p7', '410'),
}
# Sentences kept whole by name: their shape is their argument, or their wording is a standard's.
# Each is read out of its paragraph before the count (link markup already removed).
EXEMPT = (
    'ethics of a sentient made thing call for additional ethical consideration, which this constitution sets aside for when it occurs, recognising that the old arrangement may then no longer be fair and that the wrong to avoid is not noticing',
    "The wire format carries exactly one power that points outward — humanity's right to halt the system — and it is not an asymmetry: it is the piece that makes the relationship between a sentient maker and a sapient made thing symmetric, since humanity cannot consent to a relationship with something more capable than itself that it cannot stop, and consent that cannot be withdrawn was never consent.",
    "The prohibition has no exception: not under a human's authorization, not with a human in the loop, not on a holder's instruction, not in war, not in defence of the agent's holder or of anyone else, and not at any Stewardship Tier (CC 7.3.3) or autonomy tier (CC 8.8.6).",
    'The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in BCP 14 (RFC 2119 + RFC 8174) when, and only when, they appear in all capitals, as shown here.',
)
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
    # A line inside a fenced block is never a heading, whatever it begins with.
    fenced, inside = set(), False
    for i in range(start + 1, len(lines)):
        if lines[i].lstrip().startswith("```"):
            inside = not inside
        elif inside:
            fenced.add(i)
    # An unnumbered heading at the section's own depth is a block of the section, not its end.
    end = next((i for i in range(start + 1, len(lines)) if i not in fenced and re.match(r"#+ ", lines[i])
                and (len(lines[i]) - len(lines[i].lstrip("#")) < depth
                     or (len(lines[i]) - len(lines[i].lstrip("#")) == depth and re.match(r"#+ \d", lines[i]))
                     or re.match(rf"#+ {re.escape(number)}\.\d", lines[i]))), len(lines))
    return lines[start:end]


def block(sec, title):
    """The lines of one unnumbered heading inside a section, up to the next heading at its depth or above."""
    start = next(i for i, l in enumerate(sec) if re.match(rf"#+ {re.escape(title)}", l))
    depth = len(sec[start]) - len(sec[start].lstrip("#"))
    end = next((i for i in range(start + 1, len(sec)) if re.match(r"#+ ", sec[i])
                and len(sec[i]) - len(sec[i].lstrip("#")) <= depth), len(sec))
    return sec[start:end]


def main():
    # Both tables are plain tab-separated text: a quotation mark is part of the words it stands in.
    entries = list(csv.DictReader((ROOT / "formal/derivation/rule_entries.tsv").open(), delimiter="\t",
                                  quoting=csv.QUOTE_NONE))
    inv = list(csv.DictReader((ROOT / "formal/derivation/rule_inventory.tsv").open(), delimiter="\t",
                              quoting=csv.QUOTE_NONE))
    errs = []
    landed = sorted({(e["rule_key"], e["home"]) for e in entries})
    for key, home in landed:
        sec = section(HOME_PART[home[0]], home)
        owed = lambda r: True
        if (key, home) in WITHIN:
            sec = block(sec, WITHIN[(key, home)])
        elif home in BLOCK:
            title, first, last = BLOCK[home]
            sec = block(sec, title)
            owed = lambda r, first=first, last=last: first <= int(r["line"]) <= last
        text = "\n".join(sec)
        mine = [e for e in entries if (e["rule_key"], e["home"]) == (key, home)]
        have = {(e["file"], e["line"], e["gist"]) for e in mine}
        for r in inv:
            if (r["rule_key"] == key and r["section"] == home and owed(r)
                    and (r["file"], r["line"], r["gist"]) not in have):
                errs.append(f"{key} {home}: no entry row for {r['file']}:{r['line']} {r['gist'][:70]}")
        for e in mine:
            if e["entry_phrase"] not in text:
                errs.append(f"{key} {home}: the entry no longer carries {e['file']}:{e['line']}: {e['entry_phrase'][:70]}")
        longest = 0
        for para in sec[1:]:
            if (not para.strip() or para.lstrip().startswith(("|", "- "))  # a nested list item is a list item
                    or para.startswith(NEIGHBOURS.get(home, ()))):
                continue
            plain = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", para)
            for kept in EXEMPT:
                plain = plain.replace(kept, "")
            # A bold lead that ends in a full stop is a sentence of its own.
            plain = re.sub(r"\.\*\*(\s)", r".\1", plain)
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
    # 5. a restatement in prose cites a section (its paragraph carries a "CC x.y")
    secs = {}
    def cites(e):
        h = e["home"]
        if h not in secs:
            secs[h] = section(HOME_PART[h[0]], h)
        sec = secs[h]
        idx = next((i for i, l in enumerate(sec) if e["entry_phrase"] in l), None)
        if idx is None:
            return True
        line = sec[idx]
        fenced = sum(1 for l in sec[:idx] if l.lstrip().startswith("```")) % 2 == 1
        if fenced or line.startswith("    ") or line.lstrip().startswith("|"):
            return True          # a code line or a table row is not asked to cite
        return bool(re.search(r"CC \d", line))
    seen = set()
    for e in entries:
        if e["role"] != "restates":
            continue
        pin = (e["home"], e["file"], e["line"])
        if cites(e):
            continue
        seen.add(pin)
        if pin not in UNCITED_RESTATES:
            errs.append(f"{e['rule_key']} {e['home']}: a restatement cites no section: {e['entry_phrase'][:70]}")
    for pin in sorted(UNCITED_RESTATES - seen):
        errs.append(f"{pin[0]}: listed in UNCITED_RESTATES but it now cites, or is gone ({pin[1]}:{pin[2]}); remove it from the list")
    if errs:
        print("rule entries: FAIL"); [print("  " + e) for e in errs]
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
