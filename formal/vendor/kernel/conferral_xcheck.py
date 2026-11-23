#!/usr/bin/env python3
"""
conferral_xcheck.py: dump every reachable state of models/tla/ConferralEnd.tla under a cross-check configuration
(DUMPANS = TRUE: the state carries the spec's own "weakR" answer for every held act, in `ans`) and compare each
with models/causal_kernel/conferral_end.py over the same rows: the reference must give the same
<<counted, in_force>> for every act at every distinct state.

    python3 -I tools/conferral_xcheck.py --jar PATH [CFG ...]   default: the two configurations tools/tla_check.sh runs

The spec's rows are translated into the reference's: H0 is a head every row has in its past, H1 extends H0, an act
names its head, and an act's `prev` and the end's `ack` are dropped (the recommended wire carries neither).
"""
import os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(ROOT, "models", "tla")
sys.path.insert(0, os.path.join(ROOT, "models", "causal_kernel"))
sys.dont_write_bytecode = True
import conferral_end as CE  # noqa: E402

DEFAULT = ["ConferralEnd_xcheck_all.cfg", "ConferralEnd_xcheck_none.cfg"]
TOK = re.compile(r'\s*(<<|>>|\|->|"[^"]*"|TRUE|FALSE|-?\d+|[A-Za-z_][A-Za-z0-9_]*|[\[\]{}(),:@])')


def parse(text):
    toks = TOK.findall(text)
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def take(t=None):
        x = toks[pos[0]]
        assert t is None or x == t, (t, x, toks[pos[0] - 5:pos[0] + 5])
        pos[0] += 1
        return x

    def items(close, one):
        out = []
        if peek() == close:
            take(close); return out
        while True:
            out.append(one())
            if peek() == ",":
                take(","); continue
            take(close); return out

    def value():
        t = take()
        if t == "<<":
            return tuple(items(">>", value))
        if t == "{":
            return frozenset(items("}", value))
        if t == "[":
            def field():
                k = take(); take("|->"); return (k.strip('"'), value())
            return dict(items("]", field))
        if t == "TRUE":
            return True
        if t == "FALSE":
            return False
        if t.startswith('"'):
            return t[1:-1]
        if re.fullmatch(r"-?\d+", t):
            return int(t)
        raise ValueError(t)
    v = value()
    return v


def states(cfg, jar):
    with tempfile.TemporaryDirectory() as d:
        dump = os.path.join(d, "states")
        subprocess.run(["java", "-XX:+UseParallelGC", "-cp", jar, "tlc2.TLC", "-workers", "auto", "-metadir",
                        os.path.join(d, "meta"), "-dump", dump, "-config", cfg, "ConferralEnd.tla"], cwd=SPEC,
                       check=True, stdout=subprocess.DEVNULL)
        with open(dump + ".dump", encoding="utf-8") as fh:
            block = []
            for line in fh:
                if line.startswith("State "):
                    if block:
                        yield block
                    block = []
                else:
                    block.append(line)
            if block:
                yield block


def variables(block):
    out, cur = {}, None
    for line in block:
        m = re.match(r"/\\ (\w+) = (.*)", line)
        if m:
            cur = m.group(1); out[cur] = m.group(2)
        elif cur and line.strip():
            out[cur] += " " + line.strip()
    return {k: parse(v) for k, v in out.items()}


def consts(cfg):
    text = open(os.path.join(SPEC, cfg), encoding="utf-8").read()
    who = re.search(r'WHO = "(\w+)"', text).group(1)
    tie = re.search(r"WithTie = (\w+)", text).group(1) == "TRUE"
    assert 'RSCOPE = "any"' in text and "LINEACTS = FALSE" in text and "DUMPANS = TRUE" in text, cfg
    return who, tie


def rows_of(st):
    f, held = st["f"], st["h1"]
    rows = [CE.head("H0")]
    for i in sorted(held):
        r = f[i]
        k = r["k"]
        nm = set(r["nm"])
        if i == "H1":
            rows.append(CE.head("H1", "H0")); continue
        if k == "act":
            nm.discard(r["prev"])
            hd = None if r["hd"] == "none" else r["hd"]
            row = CE.act(i, hd, nm, signer=r["s"])
            if i == "c1":
                row["via"] = next(n for n in r["nm"] if n.startswith("b"))
            rows.append(row)
        elif k == "end":
            rows.append(CE.end(r["hd"], signer=r["s"], names=nm - set(r["ack"]), lifts=r["lifts"]))
        elif k == "receipt":
            rows.append(CE.receipt(i, r["of"], r["s"], nm))
        elif k == "removal":
            rows.append(CE.removal(i, r["tgt"], sorted(nm)))
        elif k == "accept":
            rows.append({"id": i, "kind": "accept", "signer": r["s"], "names": sorted(nm)})
        elif k == "unseat":
            rows.append({"id": "rx", "kind": "receipter_end", "signer": r["s"], "names": sorted(nm)})
        else:
            raise ValueError(k)
    # the spec names the receipter's end "Rx"
    for row in rows:
        row["names"] = ["rx" if n == "Rx" else n for n in row["names"]]
    return rows


def main():
    jar = sys.argv[sys.argv.index("--jar") + 1]
    cfgs = [a for a in sys.argv[1:] if a.endswith(".cfg")] or DEFAULT
    bad = total = acts = 0
    for cfg in cfgs:
        who, tie = consts(cfg)
        seen = set()
        for block in states(cfg, jar):
            st = variables(block)
            if not st["done"] or not st["h1"]:
                continue
            key = (repr(sorted(st["h1"])), repr(sorted((k, repr(v)) for k, v in st["f"].items() if k in st["h1"])),
                   st["ak"])
            if key in seen:
                continue
            seen.add(key)
            got = CE.answers(rows_of(st), reader_acks=["H1"] if st["ak"] else [], other_standing=tie, who=who)
            want = st["ans"] if isinstance(st["ans"], dict) else {}
            total += 1
            for x, (c, fo) in want.items():
                acts += 1
                g = got.get(x)
                if g is None or (g["counted"], g["in_force"]) != (c, fo):
                    bad += 1
                    if bad <= 10:
                        print("DISAGREE %s: %s spec %s reference %s rows %s ak %s" % (cfg, x, (c, fo), g,
                              rows_of(st), st["ak"]))
            if set(got) != set(want):
                bad += 1
                if bad <= 10:
                    print("DISAGREE %s: acts spec %s reference %s" % (cfg, sorted(want), sorted(got)))
    print("conferral_xcheck: %d configurations, %d distinct held states, %d act answers, %d disagreements"
          % (len(cfgs), total, acts, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
