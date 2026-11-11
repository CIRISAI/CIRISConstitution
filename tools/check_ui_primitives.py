#!/usr/bin/env python3
"""manifests/ui_primitives.json (CSD/5) agrees with the manifests it is built on.

The screen standard names a context, verbs, read outcomes, states, laws and primitives. Each
of those is either closed inside the file or is another manifest's vocabulary. This check fails when

  1. the circles of `context` are not the scopes of manifests/view.cddl and the circles of
     manifests/choice_item.cddl;
  2. `write_verbs` is not the set of verbs manifests/transitions.json carries;
  3. the `confirm` cell of manifests/transitions.json is not one value for each family and verb,
     so that a card's copy could not be checked by lookup (L6);
  4. a tag prefix has two owners, among primitives and the shell (L1);
  5. a state names a read outcome the file does not list, or a primitive a law it does not state;
  6. `@states` is a slot of a primitive that is bound to no read;
  7. a law cites a CC section, a manifest, a member of one, or a theorem of
     formal/event_lifecycle that is not there.

  python3 tools/check_ui_primitives.py
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "manifests"


def enum_after(text, member):
    """The quoted alternatives of the first `member: "a" / "b" ...` in a CDDL file."""
    m = re.search(rf"\b{member}:\s*((?:\"[a-z_]+\"\s*/\s*)*\"[a-z_]+\")", text)
    return re.findall(r"\"([a-z_]+)\"", m.group(1)) if m else []


def main():
    ui = json.loads((M / "ui_primitives.json").read_text())
    errs = []

    view, item = (M / "view.cddl").read_text(), (M / "choice_item.cddl").read_text()
    circles = ui["context"]["circle"]
    for name, got in (("view.cddl scope", enum_after(view, "scope")), ("choice_item.cddl circle", enum_after(item, "circle"))):
        if got != circles:
            errs.append(f"context.circle {circles} is not {name} {got}")

    rows = json.loads((M / "transitions.json").read_text())["rows"]
    verbs, cell = set(), {}
    for r in rows:
        for t in r["transitions"]:
            verbs.add(t["verb"])
            cell.setdefault((r["family"], t["verb"]), set()).add(t["confirm"]["value"])
    if sorted(verbs) != sorted(ui["write_verbs"]):
        errs.append(f"write_verbs {sorted(ui['write_verbs'])} is not the transitions' verbs {sorted(verbs)}")
    for pair, vals in sorted(cell.items()):
        if len(vals) != 1:
            errs.append(f"confirm is not one value for {pair[0]} {pair[1]}")

    owner = {p: "the shell" for p in ui["shell_prefixes"]}
    for name, prim in ui["primitives"].items():
        for p in prim["prefixes"]:
            if not re.fullmatch(r"[a-z]+", p):
                errs.append(f"{name}: prefix {p!r} is not one lower-case word")
            if p in owner:
                errs.append(f"prefix {p!r} is owned by {owner[p]} and by {name}")
            owner[p] = name
        for law in prim.get("laws", ()):
            if law not in ui["laws"]:
                errs.append(f"{name}: law {law} is not stated")
        if "@states" in prim.get("slots", ()) and prim.get("binds") != "read":
            errs.append(f"{name}: carries the states and is bound to no read")
    for name, prim in ui["primitives"].items():
        for p in prim.get("legacy_prefixes", ()):
            if p in owner and owner[p] != name:
                errs.append(f"{name}: legacy prefix {p!r} is owned by {owner[p]}")
    for name, st in ui["states"].items():
        if st["outcome"] not in ui["read_outcomes"]:
            errs.append(f"state {name}: outcome {st['outcome']!r} is not a read outcome")

    headings = set()
    for part in (ROOT / "constitution").glob("part_*.md"):
        headings |= set(re.findall(r"^#+ (\d+(?:\.\d+)+) ", part.read_text(), re.M))
    lean = (ROOT / "formal/event_lifecycle/EventLifecycle.lean").read_text()
    theorems = set(re.findall(r"^theorem (\w+)", lean, re.M))
    cited = 0
    for law, text in ui["laws"].items():
        for sec in re.findall(r"CC (\d+(?:\.\d+)+)", text):
            cited += 1
            if sec not in headings:
                errs.append(f"{law}: cites CC {sec}, which no Part heads")
        for path in re.findall(r"manifests/[a-z_0-9]+\.[a-z]+", text):
            cited += 1
            if not (ROOT / path).exists():
                errs.append(f"{law}: cites {path}, which is not there")
        for path, member in re.findall(r"(manifests/[a-z_0-9]+\.cddl): an answer's `(\w+)`", text):
            if member not in (ROOT / path).read_text():
                errs.append(f"{law}: cites `{member}` of {path}, which is not there")
        for group in re.findall(r"formal/event_lifecycle:? ([a-z_, ]+)\.?\)", text):
            for th in re.findall(r"[a-z]+(?:_[a-z]+)+", group):
                cited += 1
                if th not in theorems:
                    errs.append(f"{law}: cites {th}, which formal/event_lifecycle does not prove")
    for key, text in ui["_meta"]["builds_on"].items():
        for path in re.findall(r"(?:manifests|formal)/[a-z_0-9]+(?:\.[a-z]+)?", text):
            if not (ROOT / path).exists():
                errs.append(f"builds_on.{key}: {path} is not there")

    print(f"ui primitives: CSD/5 draft {ui['_meta']['draft']}: {len(ui['primitives'])} primitives, "
          f"{len(owner)} prefixes each with one owner, {len(ui['states'])} states, {len(ui['laws'])} laws, "
          f"{cited} citations resolve, confirm is one value on each of {len(cell)} family-verb pairs")
    if errs:
        print("ui primitives: FAIL"); [print("  " + e) for e in errs]
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
