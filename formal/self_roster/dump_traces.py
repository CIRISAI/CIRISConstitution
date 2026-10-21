#!/usr/bin/env python3
"""Dump SelfRoster behaviours as JSON for implementers to replay against their roster door
(CIRISPersist#1099). Run from formal/self_roster:  python3 dump_traces.py <tla2tools.jar>

Six traces, written to traces/<config>.json:
  refuse  unilateral3_stolen   — the thief's lone eviction lands at once; a conforming door REFUSES it
  bound   combined1_stolen     — one key, stolen: Inv_SelfSurvives fails; the stated one-key bound
  bound   combined2_stolen     — two keys, one stolen: the stalemate; the stated two-key bound (a
                                 behaviour that never reaches Recovered; printed as a lasso)
  land    combined3_stolen / combined3_lost / combined4_mixed — the shortest behaviour reaching
                                 Recovered under the ruled policy; every Execute in it must land

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
TOK = re.compile(r'\s*(\|->|:>|@@|[{}\[\]\(\),]|"[^"]*"|-?\d+|[A-Za-z_][A-Za-z0-9_]*)')
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
    if prev is None: return "init"
    if cur["holder"] != prev["holder"] and cur["member"] == prev["member"]:
        d = next(k for k in cur["holder"] if cur["holder"][k] != prev["holder"][k])
        return f"{'Steal' if cur['holder'][d]=='thief' else 'Lose'}({d})"
    if cur["member"] != prev["member"]:
        gone = set(prev["member"]) - set(cur["member"]); new = set(cur["member"]) - set(prev["member"])
        return f"Execute(evict {sorted(gone)[0]})" if gone else f"Execute(add {sorted(new)[0]})"
    pk = {(p["kind"], p["by"], p["target"]) for p in prev["pending"]}
    ck = {(p["kind"], p["by"], p["target"]) for p in cur["pending"]}
    if ck - pk:
        k, by, tg = sorted(ck - pk)[0]; return f"Propose({k}, by={by}, target={tg})"
    if cur["acted"] == [] and prev["acted"] != [] or any(c["age"] > p["age"] for c in cur["pending"] for p in prev["pending"] if (c["kind"],c["by"],c["target"])==(p["kind"],p["by"],p["target"])):
        return "Tick"
    if set(cur["acted"]) - set(prev["acted"]):
        return f"React({sorted(set(cur['acted']) - set(prev['acted']))[0]})"
    return cur["tlc_action"]

def run(config, kind, prop):
    with tempfile.TemporaryDirectory() as td:
        shutil.copy(os.path.join(HERE, "SelfRoster.tla"), td)
        cfg = open(os.path.join(HERE, f"SelfRoster_{config}.cfg")).read()
        if kind == "land":   # swap the liveness property for the witness invariant
            cfg = re.sub(r"PROPERTIES.*\n?", "", cfg)
            cfg = re.sub(r"INVARIANTS.*", "INVARIANTS TypeOK Inv_NotRecovered", cfg)
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
            "reading": {"refuse": "the last Execute in this trace is the one a conforming door refuses",
                        "bound": "a stated bound: no policy on the wire resolves this behaviour",
                        "land": "every Execute in this trace lands under the ruled two-path policy; the final state is Recovered"}[kind],
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
