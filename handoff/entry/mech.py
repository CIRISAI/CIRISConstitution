#!/usr/bin/env python3
"""Mechanical check of one entry patch. usage: mech.py <name> <part file rel> <mode: whole|one> <rule_key>"""
import re, sys, subprocess, tempfile, shutil, os, collections
S = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(S, "..", ".."))
name, part, mode, key = sys.argv[1:5]
patch = f"{S}/{name}.patch"
old_full = subprocess.run(["git", "-C", ROOT, "show", f"{os.environ.get('BASE', 'b9e21f8')}:{part}"], capture_output=True, text=True, check=True).stdout
tmp = tempfile.mkdtemp()
os.makedirs(os.path.dirname(f"{tmp}/{part}"), exist_ok=True)
open(f"{tmp}/{part}", "w").write(old_full)
r = subprocess.run(["patch", "-p1", "-s", "-d", tmp, "-i", patch], capture_output=True, text=True)
if r.returncode: print("PATCH FAILS", r.stdout, r.stderr); sys.exit(1)
new_full = open(f"{tmp}/{part}").read()
# files touched
files = re.findall(r"^diff --git a/(\S+)", open(patch).read(), re.M)
print("files touched:", files)
old_sec = open(f"{S}/{name}.old.md").read().rstrip("\n")
if old_sec not in old_full: print("WARN old.md is not a verbatim slice of the Part at b9e21f8")
ol, nl = old_full.split("\n"), new_full.split("\n")
# common prefix/suffix
i = 0
while i < min(len(ol), len(nl)) and ol[i] == nl[i]: i += 1
j = 0
while j < min(len(ol), len(nl)) - i and ol[-1 - j] == nl[-1 - j]: j += 1
print(f"changed span old lines {i+1}..{len(ol)-j}, new lines {i+1}..{len(nl)-j}")
start = old_full.find(old_sec); sl = old_full[:start].count("\n") + 1; el = sl + old_sec.count("\n")
print(f"home section old lines {sl}..{el}", "OK inside" if i + 1 >= sl and len(ol) - j <= el else "FAIL: edit outside home")
new_sec = "\n".join(nl[sl - 1: len(nl) - (len(ol) - el)])
open(f"{S}/{name}.new.md", "w").write(new_sec + "\n")
ow, nw = len(old_sec.split()), len(new_sec.split())
print(f"words {ow} -> {nw}")
KW = ["MUST NOT", "MUST", "SHALL NOT", "SHALL", "REQUIRED", "SHOULD NOT", "SHOULD", "MAY", "NOT REQUIRED"]
def kw(t):
    c = collections.Counter(); t2 = t
    for k in ["MUST NOT", "SHALL NOT", "SHOULD NOT", "NOT REQUIRED"]:
        c[k] = len(re.findall(rf"\b{k}\b", t2)); t2 = re.sub(rf"\b{k}\b", "", t2)
    for k in ["MUST", "SHALL", "REQUIRED", "SHOULD", "MAY"]:
        c[k] = len(re.findall(rf"\b{k}\b", t2))
    return c
ko, kn = kw(old_sec), kw(new_sec)
print("keywords:", {k: (ko[k], kn[k]) for k in ko if ko[k] or kn[k]}, "DIFF" if ko != kn else "same")
def toks(t): return collections.Counter(re.findall(r"`[^`\n]+`", t))
to, tn = toks(old_sec), toks(new_sec)
print("backtick tokens lost:", sorted(k for k in to if k not in tn))
print("backtick tokens new:", sorted(k for k in tn if k not in to))
def nums(t): return set(re.findall(r"(?<![\w.`#])\d+(?:[.,]\d+)*(?:\s?(?:%|hours?|days?|years?|months?|minutes?|seconds?|h|s|ms)\b)?", re.sub(r"CC \d+(\.\d+)*", "", t)))
print("numbers lost:", sorted(nums(old_sec) - nums(new_sec)))
print("numbers new:", sorted(nums(new_sec) - nums(old_sec)))
def cites(t): return set(re.findall(r"CC \d+(?:\.\d+)*", t))
print("citations lost:", sorted(cites(old_sec) - cites(new_sec)))
print("citations new:", sorted(cites(new_sec) - cites(old_sec)))
def heads(t): return [l for l in t.split("\n") if re.match(r"#+ ", l)]
print("headings same:", heads(old_sec) == heads(new_sec), "" if heads(old_sec) == heads(new_sec) else (heads(old_sec), heads(new_sec)))
def leads(t): return set(re.findall(r"^\*\*([^*]+)\*\*", t, re.M)) | set(re.findall(r"^[-\d.]+ \*\*([^*]+)\*\*", t, re.M))
print("bold leads lost:", sorted(leads(old_sec) - leads(new_sec)))
def blocks(t): return re.findall(r"```.*?```", t, re.S)
print("code blocks same:", blocks(old_sec) == blocks(new_sec))
if "part_3" in part:
    ot = [l for l in old_sec.split("\n") if l.startswith("|") or "Canonical leaves:" in l or "Polarity:" in l]
    nt = [l for l in new_sec.split("\n") if l.startswith("|") or "Canonical leaves:" in l or "Polarity:" in l]
    print("generator-read lines kept:", all(l in nt for l in ot), "| lost:", [l[:80] for l in ot if l not in nt][:10], "| new table rows:", len([l for l in nt if l not in ot]))
for w in ["humane", "dignified", "graceful", "farewell", "last word", "optimal", "trade-off", "prioritise", "balanced", "previously", "used to", "as of", "asymmetr",
          "broadened admission", "retraction carve-out", "third-party path", "trust list", "trusted set", "pin set", "trust store", "target-membership",
          "recipient predicate", "one audience rule", "existence-invisible", "owner binding", "steward binding", "ownership edge", "responsible steward"]:
    a, b = old_sec.lower().count(w), new_sec.lower().count(w)
    if b > a: print(f"WORD '{w}' {a}->{b}")
pins = [l.split("\t") for l in open(f"{S}/../sweep/pinned.tsv").read().split("\n") if l.strip()]
for p in pins:
    for f in p:
        if len(f) > 15 and f in old_sec and f not in new_sec: print("PINNED LOST:", f[:100])
# entries
wl = [l.split("\t") for l in open(f"{S}/{name}.worklist.tsv").read().split("\n") if l.strip()]
wh = wl[0]; wl = [dict(zip(wh, r)) for r in wl[1:]]
en = [l.split("\t") for l in open(f"{S}/{name}.entries.tsv").read().split("\n") if l.strip()]
eh = en[0]; print("entries header:", eh)
bad = [r for r in en[1:] if len(r) != len(eh)]
if bad: print("FAIL rows with wrong field count:", len(bad))
en = [dict(zip(eh, r)) for r in en[1:] if len(r) == len(eh)]
have = {(e["file"], e["line"], e["gist"]) for e in en}
need = [w for w in wl if mode == "whole" or w["rule_key"] == key]
miss = [w for w in need if (w["file"], w["line"], w["gist"]) not in have]
print(f"worklist {len(wl)}, needed {len(need)}, entries {len(en)} (extras {sum(1 for e in en if e['line']=='x')}), missing {len(miss)}")
for w in miss: print("  MISSING", w["line"], w["rule_key"], w["gist"][:90])
np = [e for e in en if e["entry_phrase"] not in new_sec]
print("phrases not in new section:", len(np))
for e in np: print("  NOT IN", e["line"], e["entry_phrase"][:90])
short = [e for e in en if len(e["entry_phrase"].split()) < 4]
print("phrases under 4 words:", len(short))
# sentences
nb = []
if os.path.exists(f"{S}/{name}.neighbours.txt"): nb = [l.strip() for l in open(f"{S}/{name}.neighbours.txt") if l.strip()]
print("neighbours:", nb)
longest = 0; over = []; lens = []
for para in new_sec.split("\n")[1:]:
    if not para.strip() or para.startswith(("|", "- ", "#", "```")) or (nb and para.startswith(tuple(nb))): continue
    plain = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", para)
    for s in re.split(r"(?<=[.])\s+(?=[A-Z*`])", plain):
        n = len(s.split()); lens.append(n)
        if n > 40: over.append((n, s[:80]))
print(f"sentences {len(lens)}, mean {sum(lens)/max(1,len(lens)):.1f}, max {max(lens) if lens else 0}, over 40: {len(over)}")
for o in over: print("  OVER", o)
shutil.rmtree(tmp)
