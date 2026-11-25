#!/usr/bin/env python3
"""Dump SelfRoster behaviours as JSON for implementers to replay against their roster door
Run from formal/self_roster:  python3 dump_traces.py <tla2tools.jar>

Six traces, written to traces/<config>.json:
  refuse  unilateral3_stolen   — the thief's eviction is read as landed on its word; a conforming reader does not
  bound   combined1_stolen     — one key, stolen: Inv_SelfSurvives fails; the stated one-key bound
  bound   combined2_stolen     — two keys, one stolen: the stalemate; the stated two-key bound (a
                                 behaviour that never reaches Recovered; printed as a lasso)
  land    combined3_stolen / combined3_lost / combined4_mixed — the shortest behaviour reaching
                                 Recovered under the combined policy; every Settle in it reads `landed`

Each state carries the model variables and a derived `step` naming the transition that produced it.
stdlib only; TLC output parsed, never edited by hand."""
import json, os, re, subprocess, sys, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
JAR = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "tla2tools.jar")
OUT = os.path.join(HERE, "traces")
CASES = [("unilateral3_stolen", "refuse", "Inv_ThiefCannotEvictHonest"),
         ("combined1_stolen", "bound", "Inv_SelfSurvives"),
         ("combined2_stolen", "bound", "Prop_LostRecoverable"),
         ("combined3_stolen", "land", "Inv_NotRecovered"),
         ("combined3_lost", "land", "Inv_NotRecovered"),
         ("combined4_mixed", "land", "Inv_NotRecovered")]

# ---- a small parser for the TLA+ values TLC prints ----
TOK = re.compile(r'\s*(\|->|:>|@@|<<|>>|[{}\[\]\(\),]|"[^"]*"|-?\d+|[A-Za-z_][A-Za-z0-9_]*)')
def tokens(s):
    pos, out = 0, []
    while pos < len(s):
        m = TOK.match(s, pos)
        if not m:
            if s[pos:].strip() == "": break
            raise ValueError(f"bad token at {s[pos:pos+20]!r}")
        out.append(m.group(1)); pos = m.end()
    return out
def parse(toks):
    def peek(): return toks[0] if toks else None
    def take(): return toks.pop(0)
    def value():
        t = take()
        if t == "{":
            items = []
            while peek() != "}":
                items.append(value())
                if peek() == ",": take()
            take(); return {"set": items}
        if t == "[":
            rec = {}
            while peek() != "]":
                k = take(); assert take() == "|->"; rec[k] = value()
                if peek() == ",": take()
            take(); return rec
        if t == "<<":   # a tuple; TLC prints a function with an empty domain as << >>
            items = []
            while peek() != ">>":
                items.append(value())
                if peek() == ",": take()
            take(); return items if items else {}
        if t == "(":
            fn = {}
            while True:
                k = take(); assert take() == ":>"; fn[k] = value()
                if peek() == "@@": take(); continue
                break
            assert take() == ")"; return fn
        if t.startswith('"'): return t[1:-1]
        if re.fullmatch(r"-?\d+", t): return int(t)
        if t == "TRUE": return True
        if t == "FALSE": return False
        return t   # model value
    return value()
def plain(v):
    if isinstance(v, dict) and set(v) == {"set"}:
        return sorted((plain(x) for x in v["set"]), key=lambda x: json.dumps(x, sort_keys=True))
    if isinstance(v, dict): return {k: plain(x) for k, x in v.items()}
    return v

def parse_states(text):
    states = []
    for m in re.finditer(r"State (\d+): <([^>\n]*)>\n(.*?)(?=\nState \d+: <|\n\n|\Z)", text, re.S):
        body = m.group(3)
        vars_ = {}
        for part in re.split(r"\n/\\ ", "\n" + body.strip()):
            part = part.strip()
            if not part: continue
            name, _, val = part.partition(" = ")
            vars_[name.strip()] = plain(parse(tokens(val)))
        states.append({"n": int(m.group(1)), "tlc_action": m.group(2).split(" line")[0], **vars_})
    return states

def step_name(prev, cur):
    """The transition, named from what changed between the two states."""
    if prev is None: return "init"
    key = lambda p: (p["kind"], p["by"], p["target"])
    pk = {key(p): p for p in prev["props"]}; ck = {key(p): p for p in cur["props"]}
    if cur["holder"] != prev["holder"] and cur["member"] == prev["member"] and not pk:
        d = next(k for k in cur["holder"] if cur["holder"][k] != prev["holder"][k])
        return f"{'Steal' if cur['holder'][d] == 'thief' else 'Lose'}({d})"
    if set(ck) - set(pk):
        k, by, tg = sorted(set(ck) - set(pk))[0]; return f"Propose({k}, by={by}, target={tg})"
    if cur["member"] != prev["member"]:
        out = set(prev["member"]) - set(cur["member"]); new = set(cur["member"]) - set(prev["member"])
        k, by, tg = next(q for q in pk if q[2] in (out | new))
        return f"Settle({k} {tg} by {by}: landed)"
    if set(pk) - set(ck):
        k, by, tg = sorted(set(pk) - set(ck))[0]; return f"Settle({k} {tg} by {by}: refused)"
    note = None
    for q in sorted(ck):
        a, b = pk[q], ck[q]
        if a == b: continue
        k, by, tg = q
        if a["ans"] != b["ans"]:
            d = next(x for x in b["ans"] if b["ans"][x] != a["ans"][x])
            return f"Answer({d}: {b['ans'][d]} on {k} {tg} by {by})"
        if a["wd"] != b["wd"]: return f"Withdraw({k} {tg} by {by})"
        if a["held"] != b["held"]: return f"Hold({k} {tg} by {by}: {b['held']})"
        if a["land"] != b["land"]: return f"Land({k} {tg} by {by}: {b['land']})"
        note = f"Note({tg})"
    return note or cur["tlc_action"]

def run(config, kind, prop):
    with tempfile.TemporaryDirectory() as td:
        shutil.copy(os.path.join(HERE, "SelfRoster.tla"), td)
        cfg = open(os.path.join(HERE, f"SelfRoster_{config}.cfg")).read()
        if kind == "land":   # swap the liveness property for the witness invariant
            cfg = re.sub(r"PROPERTIES.*\n?", "", cfg)
            cfg = re.sub(r"INVARIANTS.*", "INVARIANTS TypeOK Inv_NotRecovered", cfg)
        elif prop.startswith("Inv_"):   # report the named invariant, whatever else the configuration lists
            cfg = re.sub(r"PROPERTIES.*\n?", "", cfg)
            cfg = re.sub(r"INVARIANTS.*", "INVARIANTS TypeOK " + prop, cfg)
        open(os.path.join(td, "run.cfg"), "w").write(cfg)
        out = subprocess.run(["java", "-Xmx3g", "-cp", JAR, "tlc2.TLC", "-workers", "1", "-metadir",
                              os.path.join(td, "m"), "-deadlock", "-config", "run.cfg", "SelfRoster.tla"],
                             cwd=td, capture_output=True, text=True).stdout
    violated = re.search(r"Error: (Invariant \w+ is violated|Temporal properties were violated)", out)
    states = parse_states(out)
    lasso = re.search(r"Back to state (\d+)", out)
    stutter = "Stuttering" in out
    prev = None
    for s in states:
        s["step"] = step_name(prev, s); prev = s
    return {"config": config, "kind": kind, "checked": prop,
            "tlc": violated.group(1) if violated else "no violation (unexpected)",
            "reading": {"refuse": "the last Settle in this trace is the one a conforming reader never makes",
                        "bound": "a stated bound: no policy on the wire resolves this behaviour",
                        "land": "every Settle in this trace reads landed under the rule of CC 3.3.6.4 (a met count, or a lone landing that stands); the final state is Recovered"}[kind],
            "lasso_back_to_state": int(lasso.group(1)) if lasso else ("stutter" if stutter else None),
            "states": states}

def main():
    os.makedirs(OUT, exist_ok=True)
    for config, kind, prop in CASES:
        tr = run(config, kind, prop)
        with open(os.path.join(OUT, f"{config}.json"), "w") as f:
            json.dump(tr, f, indent=1); f.write("\n")
        print(f"{config:22} {kind:7} {tr['tlc']:45} {len(tr['states'])} states")

if __name__ == "__main__":
    main()
