#!/usr/bin/env python3
"""
CC — a family's card: everything the data holds about one family, printed as one block.

Reads manifests/family_model.json, manifests/transitions.json and manifests/reactions.json and prints, for the
family named, its kind, who signs each transition, how its act is counted, what must be held for a row to be
admitted, what a changing row may do, how its rows fold, what follows in time, and its body members, each with
the sections that state it. It writes nothing. It is the shape a per-family table in a Part would take if the
data, and not the paragraph, were the Part's statement of these values.

Run: python3 tools/family_card.py --write                     # write the cards into CC 8.10 (Part 8)
     python3 tools/family_card.py --check                     # CC 8.10 is current
     python3 tools/family_card.py 'membership:{stage}'        # one family
     python3 tools/family_card.py --coverage                  # how many families have each block typed
"""
import json, os, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(ROOT, "manifests", p), encoding="utf-8"))


def refs(x):
    r = x.get("cc_ref") if isinstance(x, dict) else None
    if not r: return ""
    return " (" + ", ".join(r if isinstance(r, list) else ([r] if isinstance(r, str) else sorted(set(r.values())))) + ")"


def card(fam, fm, tr, rx):
    r = fm[fam]; out = [f"**`{fam}`** — {r['kind']['value']}, {r['side']['value']}" + ("; keeps the Record" if r["maintains_record"]["value"] else "")]
    out.append("")
    out.append("| Transition | Who signs | Policy | Widens | Confirm | Way back |")
    out.append("|---|---|---|---|---|---|")
    for t in tr[fam]:
        roles = ", ".join(t["roles"]["value"]) or "open cell"
        if t["roles"].get("stages"): roles += " (" + "; ".join(f"{k}: {', '.join(v)}" for k, v in t["roles"]["stages"].items()) + ")"
        pol = t["policy"]["value"]; ptxt = pol["policy"] + (" " + ", ".join(f"`{x}`" for x in pol["rows"]) if pol["rows"] else "")
        w = str(t["widens"]["value"]).lower() + (f" ({t['widens']['when']})" if t["widens"].get("when") else "")
        c = str(t["confirm"]["value"]).lower() + (f" ({t['confirm']['when']})" if t["confirm"].get("when") else "")
        u = (f"{t['undo'].get('via')}" if t["undo"]["value"] else "none")
        out.append(f"| {t['verb']} | {roles.replace('|', chr(92) + '|')} | {ptxt} | {w} | {c} | {u} |")
    cnt = r["count"]
    out += ["", f"Count: `{cnt['value']}`" + (" (" + ", ".join(sorted({a['cc_ref'] for a in cnt['arms']})) + ")" if cnt.get("arms") else "")]
    for label, key, field in (("Guard", "guard", "guard"), ("Change", "change", "item")):
        lines = []
        for t in tr[fam]:
            for g in t[key]["value"]:
                lines.append(f"- {t['verb']}: `{g[field]}` ({', '.join(g['cc_ref'])})")
        if lines: out += ["", f"{label}:"] + sorted(set(lines))
    if r["fold"]["value"]:
        out += ["", "Fold:"] + [f"- `{f['fold']}` ({', '.join(f['cc_ref'])})" for f in r["fold"]["value"]]
    mine = [e for e in rx if e["family"] == fam]
    if mine:
        out += ["", "In time:"]
        for e in mine:
            sel = ("[" + "|".join(e["leaves"]) + "] " if e.get("leaves") else "") + (f"@{e['scope']} " if e.get("scope") else "")
            if e["kind"] == "expiry": body = f"expiry {e['mode']}" + (f" `{e['member']}`" if e.get("member") else "") + "".join(f" {k} `{e[k]}`" for k in ("eq", "default", "max") if e.get(k))
            elif e["kind"] == "clock": body = f"clock `{e['name']}` = `{e['dur']}`"
            else:
                ev = lambda xs: " or ".join(f"{x['event']}({x['of']}" + (f", by the {x['by']}" if x.get('by') else "") + ")" for x in xs)
                eff = ", ".join((f"emit `{x['family']}` by {x['by']}" if x["effect"] == "emit" else f"read {x['verdict']}" if x["effect"] == "read" else f"do {x.get('act')}" if x["effect"] == "do" else f"open {x['policy']}") for x in e["effects"])
                body = f"on {ev(e['on'])}" + (f" unless {ev(e['unless'])}" if e.get("unless") else "") + f": {eff}"
            out.append(f"- {sel}{body} ({', '.join(e['cc_ref'])})")
    b = r["body"].get("value")
    if isinstance(b, dict) and b.get("members"):
        out += ["", "Body: " + ", ".join(dict.fromkeys(f"`{m['member']}`" + ("" if m.get("in_cddl", True) else " (text only)") for m in b["members"]))]
    return "\n".join(out)


def main():
    fm = {r["family"]: r for r in J("family_model.json")["rows"]}
    tr = {r["family"]: r["transitions"] for r in J("transitions.json")["rows"]}
    rx = J("reactions.json")["reactions"]
    if "--coverage" in sys.argv:
        c = Counter()
        for f, r in fm.items():
            c["count typed"] += r["count"]["source"] == "cc-table"
            c["guard typed"] += any(t["guard"]["value"] for t in tr[f])
            c["change typed"] += any(t["change"]["value"] for t in tr[f])
            c["fold typed"] += bool(r["fold"]["value"])
            c["in time typed"] += any(e["family"] == f for e in rx)
            c["body typed"] += isinstance(r["body"].get("value"), dict) and bool(r["body"]["value"].get("members"))
            c["any block typed"] += (r["count"]["source"] == "cc-table" or any(t["guard"]["value"] or t["change"]["value"] for t in tr[f]) or bool(r["fold"]["value"])
                                     or any(e["family"] == f for e in rx) or (isinstance(r["body"].get("value"), dict) and bool(r["body"]["value"].get("members"))))
        print(f"family cards: {len(fm)} families; " + "; ".join(f"{k} {v}" for k, v in c.items()))
        return
    if "--write" in sys.argv or "--check" in sys.argv:
        typed = [f for f in sorted(fm) if fm[f]["count"]["source"] == "cc-table" or any(t["guard"]["value"] or t["change"]["value"] for t in tr[f])
                 or fm[f]["fold"]["value"] or any(e["family"] == f for e in rx)
                 or (isinstance(fm[f]["body"].get("value"), dict) and fm[f]["body"]["value"].get("members"))]
        head = "## 8.10 `family-cards` — The family cards (generated from the data)"
        intro = ("The build writes this section from the family model, the transitions table and the reactions manifest. "
                 "A card states, for one family, who signs each transition and under which policy, whether a row widens and is confirmed, "
                 "how the act is counted, what must be held for a row to be admitted, what a changing row may do, how the rows fold to a value, "
                 "what follows in time, and the members of the body. Each line names the sections that state it. "
                 "The expressions are in the grammars of the tools that build the manifests, and [CC 4.5.13](part_4_composition_governance.md#4.5.13) says what each kind of line means.\n\n"
                 "**Standing (normative).** Where a card states a value, the card is this document's statement of that value. "
                 "A description of the family in [Part 3](part_3_the_namespace.md) gives the family's purpose and reasons, and a card and a description never differ on a value: the build takes each value from words quoted from the text and fails when those words change.\n\n"
                 f"A family with no card states none of these beyond the default row. Cards: {len(typed)} of {len(fm)} families.")
        body = "\n\n".join(card(f, fm, tr, rx) for f in typed)
        path = os.path.join(ROOT, "constitution", "part_8_appendices.md")
        text = open(path, encoding="utf-8").read().rstrip("\n")
        at = text.find("\n" + head)
        base = text[:at].rstrip("\n") if at >= 0 else text
        new = base + "\n\n" + head + "\n\n" + intro + "\n\n" + body + "\n"
        if "--check" in sys.argv:
            ok = open(path, encoding="utf-8").read() == new
            print("family cards: current" if ok else "CC 8.10 is stale (run tools/family_card.py --write)"); sys.exit(0 if ok else 1)
        open(path, "w", encoding="utf-8").write(new)
        print(f"family cards: {len(typed)} cards written to CC 8.10, {len(body.split())} words")
        return
    fam = sys.argv[1]
    if fam not in fm: sys.exit(f"no family {fam!r}")
    print(card(fam, fm, tr, rx))


if __name__ == "__main__":
    main()
