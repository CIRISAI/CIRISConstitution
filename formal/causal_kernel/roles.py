"""
roles.py: every row of role_shapes.tsv run as an instance of seat.py (or read off a row, or as a tally).

For a seat row the instance is built from the row's parameters alone (conferrer, consent, policy, ends), and checked:
  live          the seat stands with the offer and the acceptance
  two walks     without the acceptance it does not stand (unless the row waives it); without the offer it does not
  third party   a withdrawal by a key that signed neither row changes nothing
  each ending   the seat does not stand after it; a counted unseat signed by one voice changes nothing
A `lapse` ending is a window (window.py) and is counted, not run, here.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import seat as ST  # noqa: E402

CK, K, R = ST.CK, ST.K, ST.R
TABLE = os.path.join(HERE, "role_shapes.tsv")


def load():
    lines = [l for l in open(TABLE, encoding="utf-8") if not l.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))


def live(rows, k, s, obj, root=None):
    S = CK.concluded(CK.kept(rows), ST.seat_rule)
    return ST.Seats(S).stands(k, s, obj, root)


def build(t):
    """rows, the scope read, the object, the offer id, the acceptance id (or None), the upstream offer id, the body
    (group object, counted scope, its keys) an unseat is counted over, the root to walk from."""
    conf, s = t["conferrer"], t["scope"]
    body = None
    if conf == "self:holder":
        if s in ("duty", "moderate"):        # a founding record seats the duty holders that sign it (CC 4.5.4)
            g = ST.offer("o", "K", ("K", "f2", "f3"), "duty", "@", "self", cosigners=("f2", "f3"))
            return dict(rows=[g], s=s, obj="o", o="o", a=None, up=None, body=("o", "duty", ("f2", "f3")), root="K")
        return dict(rows=[ST.offer("o", "K", "K", s, "K", "self")], s=s, obj="K", o="o", a=None, up=None, body=None, root="K")
    if conf == "self:object":
        if s == "root":            # the reader confers; the root's own charter is the acceptance, named by the offer
            ch = ST.accept("a", "K", None, scope="root")
            return dict(rows=[ch, ST.offer("o", "READER", "K", "root", "READER", "self", ("a",))], s=s, obj="READER",
                        o="o", a="a", up=None, body=None, root="READER")
        if t["object"].startswith("a row"):
            rec = R("rec", "record", "AUTH", subjects=("SUBJ",))
            return dict(rows=[rec, ST.offer("o", "SUBJ", "K", s, "rec", "self", ("rec",)), ST.accept("a", "K", "o")],
                        s=s, obj="rec", o="o", a="a", up=None, body=None, root="SUBJ")
        rows = [ST.offer("o", "A", "K", s, "A", "self"), ST.accept("a", "K", "o")]
        if "unseat:" in t["ends"]:
            rows.append(ST.offer("g", "f1", ("f1", "f2", "f3"), "member", "@", "self", cosigners=("f2", "f3")))
            body = ("g", "member", ("f1", "f2", "f3"))
        return dict(rows=rows, s=s, obj="A", o="o", a="a", up=None, body=body, root="A")
    if conf == "seat:duty":                 # a lone duty holder confers alone, with the new holder's acceptance (CC 4.5.4)
        g = ST.offer("g", "F", "F", "duty", "@", "self")
        return dict(rows=[g, ST.offer("o", "F", "K", s, "g", "seat", ("g",), under="g"), ST.accept("a", "K", "o")],
                    s=s, obj="g", o="o", a="a", up="g", body=None, root=("group", "g"))   # an equal: rooted in the group
    if conf == "seat:owner":
        obj = "K" if s == "infra:attest" else "A"          # a node attests about itself; a Wise Authority is over the agent
        b, ab = ST.offer("b", obj, "OWN", "owner", obj, "self"), ST.accept("ab", "OWN", "b")
        return dict(rows=[b, ab, ST.offer("o", "OWN", "K", s, obj, "seat", ("ab",), under="b"), ST.accept("a", "K", "o")],
                    s=s, obj=obj, o="o", a="a", up="b", body=None, root=obj)
    if conf == "seat:root":
        ch = ST.accept("ch", "ROOT", None, scope="root")
        t0 = ST.offer("t", "READER", "ROOT", "root", "READER", "self", ("ch",))
        return dict(rows=[ch, t0, ST.offer("o", "ROOT", "K", s, "ROOT", "seat", ("t",), under="t"), ST.accept("a", "K", "o")],
                    s=s, obj="ROOT", o="o", a="a", up="t", body=None, root="READER")
    if conf == "group":
        counted = "duty" if t["policy"] in ST.DUTY_POLICY else s if s in ("member", "holder", "self") else "member"
        g = ST.offer("g", "f1", ("f1", "f2", "f3"), counted, "@", "self", cosigners=("f2", "f3"))
        rows, names, a, kw = [g], ["g"], None, {}
        if t["consent"] == "one":
            kw["consent"] = "one"
        else:
            a = "a"; rows.append(ST.accept("a", "K", None, ("g",), scope=s, obj="g")); names.append("a")
        if K.rule(ST.POLICY, t["policy"])[0] == "ranked":
            for i, f in enumerate(("f1", "f2", "f3")):
                rows.append(R("b%d" % i, "ballot", f, ("g",), ranking=("K", "x") if i < 2 else ("x", "K"))); names.append("b%d" % i)
            kw["options"] = ("K", "x")
        else:
            rows += [ST.cosign("c2", "f2", "o", ("g",)), ST.cosign("c3", "f3", "o", ("g",))]; names += ["c2", "c3"]
        rows.append(ST.offer("o", "f1", "K", s, "g", "group", names, head=("g",), policy=t["policy"], counted=counted,
                             content="o", need=3, **kw))
        return dict(rows=rows, s=s, obj="g", o="o", a=a, up=None, body=("g", counted, ("f1", "f2", "f3")), root=("group", "g"))
    raise ValueError(conf)


def run_seat(t):
    """Returns (problems, checks run, endings left to a window)."""
    w = build(t)
    rows, s, obj, bad, n, windows = w["rows"], w["s"], w["obj"], [], 0, 0
    ok = lambda extra=(), drop=(): live([r for r in rows if r["id"] not in drop] + list(extra), "K", s, obj, w["root"])

    def want(cond, what):
        nonlocal n
        n += 1
        if not cond: bad.append(what)

    want(ok(), "the seat does not stand")
    want(not live(rows, "K", s, obj, "nobody"), "the seat stands from a root that conferred nothing")
    want(not ok(drop=(w["o"],)), "it stands without the offer")
    if w["a"]:
        want(not ok(drop=(w["a"], w["o"])) and not ok(drop=(w["a"],)), "it stands without the acceptance")
    elif t["consent"] == "one":
        want(t["conferrer"] == "group", "the acceptance is waived outside a counted offer")
    want(ok([ST.withdraw("wz", "Z", w["o"])]), "a third party's withdrawal ended it")
    if t["token"] == "serve":           # two seats at once: the node's member seat and a live owner seat over the node
        own = [ST.offer("b", "K", "OWN", "owner", "K", "self"), ST.accept("ab", "OWN", "b")]
        both = lambda extra: (lambda Q: Q.stands("K", "member", obj) and Q.one("owner", "K") == "OWN")(
            ST.Seats(CK.concluded(CK.kept(rows + list(extra)), ST.seat_rule)))
        want(both(own) and not both(own[:1]) and not both(own + [ST.withdraw("wo", "OWN", "b")]), "serve is not the two seats together")
    if t["token"] == "steward" and t["scope"] == "owner":
        want(live(rows, "K", "steward", obj), "the owner seat does not read as steward")
    if t["token"] == "owner" and t["shape"] == "seat":      # single-valued: a second live owner leaves none
        two = [ST.offer("o2", "A", "K2", s, "A", "self"), ST.accept("a2", "K2", "o2")]
        Q = lambda extra: ST.Seats(CK.concluded(CK.kept(rows + list(extra)), ST.seat_rule)).one(s, obj)
        want(Q([]) == "K" and Q(two) is None, "the owner seat is not single-valued")
    for e in [x.strip() for x in t["ends"].split(";") if x.strip() not in ("", "-")]:
        if e == "lapse":
            windows += 1
        elif e == "withdraw:conferrer":
            sg = next(r for r in rows if r["id"] == w["o"])["signer"]
            want(not ok([ST.withdraw("wc", sg, w["o"])]), e)
        elif e == "withdraw:holder":
            want(not ok([ST.withdraw("wh", "K", w["o"])]), e)
            if w["a"]: want(not ok([ST.withdraw("wh", "K", w["a"])]), e + " (against the acceptance)")
        elif e == "upstream":
            up = next(r for r in rows if r["id"] == w["up"])
            want(not ok([ST.withdraw("wu", up["signer"], w["up"])]), e)
        elif e == "unseat:self":
            want(not ok([ST.unseat("x", "K", "K", s, obj, "self", (w["o"],))]), e)
        elif e.startswith("unseat:"):
            pol = e.split(":", 1)[1]
            grp, counted, keys = w["body"]
            head = w["o"] if grp == obj and w["o"] != grp else grp
            base = (w["o"], head) if head != w["o"] else (w["o"],)
            cs = [ST.cosign("xc%d" % i, f, "x", base) for i, f in enumerate(keys[1:])]
            seatscope = next(r for r in rows if r["id"] == w["o"])["scope"]
            mk = lambda names: ST.unseat("x", keys[0], "K", seatscope, obj, "group", names, head=(head,), policy=pol,
                                         counted=counted, over=grp, content="x", need=len(keys))
            want(not ok(cs + [mk(base + tuple(c["id"] for c in cs))]), e)
            want(ok([mk(base)]), e + ": one voice unseated it")
        else:
            bad.append("unknown ending " + e)
    return bad, n, windows


def run_row(t):
    """Read off the row judged: the same function that names the object's own key for a self-rooted seat."""
    rec = R("rec", "record", "AUTH", subjects=("SUBJ",), about="AUTH", owner_key_id="OWNR")
    by = {"rec": rec}
    own = ST.own_keys(by, "rec")
    if t["token"] == "author": return ([] if "AUTH" in own and "Z" not in own else ["author"]), 2, 0
    if t["token"] == "subject": return ([] if "SUBJ" in own and "Z" not in own else ["subject"]), 2, 0
    if t["token"] == "self": return ([] if rec["about"] == rec["signer"] else ["self"]), 1, 0
    if t["token"] == "owner": return ([] if rec["owner_key_id"] == "OWNR" else ["owner"]), 1, 0
    return ["no reading for " + t["token"]], 0, 0


def run_tally(t):
    w, r = ST.RANKED([("f1", ("K", "x")), ("f2", ("K", "x")), ("f3", ("x", "K"))], ["K", "x"])
    w2, _ = ST.RANKED([("f1", ("K", "x")), ("f1", ("x", "K")), ("f3", ("x", "K"))], ["K", "x"])   # f1 says two things
    return ([] if w == "K" and w2 is None else ["ranked tally"]), 2, 1


def run_all():
    tokens = json.load(open(os.path.join(ROOT, "manifests", "transitions.json"), encoding="utf-8"))["_meta"]["role_tokens"]
    table, out, problems = load(), [], []
    if sorted({t["token"] for t in table}) != sorted(tokens):
        problems.append("the table does not cover the role tokens of the transitions manifest")
    for t in table:
        if t["policy"] != "-" and t["policy"] not in ST.POLICY: problems.append("%s: no policy row %s" % (t["token"], t["policy"]))
        for e in t["ends"].split(";"):
            e = e.strip()
            if e.startswith("unseat:") and e != "unseat:self" and e.split(":", 1)[1] not in ST.POLICY:
                problems.append("%s: no policy row for %s" % (t["token"], e))
        if t["shape"] == "seat": bad, n, win = run_seat(t)
        elif t["shape"] == "row": bad, n, win = run_row(t)
        elif t["shape"] == "tally": bad, n, win = run_tally(t)
        else: bad, n, win = [], 0, 0
        if t["shape"] == "none" and t["fits"] != "no": bad.append("no shape and fits is not no")
        if t["shape"] != "none" and t["fits"] == "no": bad.append("a shape and fits is no")
        out.append((t, bad, n, win))
        problems += ["%s (%s): %s" % (t["token"], t["way"], b) for b in bad]
    return table, out, problems, tokens


def summary(table, tokens):
    shapes = sorted({t["shape"] for t in table if t["shape"] != "none"})
    confs = sorted({t["conferrer"].split(":")[0] for t in table if t["shape"] == "seat"})
    best = {}
    order = {"yes": 2, "partly": 1, "no": 0}
    for t in table: best[t["token"]] = max(best.get(t["token"], "no"), t["fits"], key=order.get)
    worst = {}
    for t in table: worst[t["token"]] = min(worst.get(t["token"], "yes"), t["fits"], key=order.get)
    merges = {}
    for t in table:
        if t["shape"] == "seat":
            merges.setdefault((t["conferrer"], t["consent"], t["ends"]), []).append(t["token"] + (" (%s)" % t["way"] if t["way"] else ""))
    first = {}
    for t in table: first.setdefault(t["token"], t["shape"])
    return {"rows": len(table), "tokens": len(tokens), "shapes": shapes, "conferrers": confs,
            "tokens_by_first_shape": {s: sorted(k for k, v in first.items() if v == s) for s in sorted(set(first.values()))},
            "fits_rows": {f: sum(t["fits"] == f for t in table) for f in ("yes", "partly", "no")},
            "tokens_best": {f: sorted(k for k, v in best.items() if v == f) for f in ("yes", "partly", "no")},
            "tokens_every_way_yes": sorted(k for k, v in worst.items() if v == "yes"),
            "same_parameters": {" | ".join(k): v for k, v in merges.items() if len(v) > 1}}


if __name__ == "__main__":
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
    table, out, problems, tokens = run_all()
    for t, bad, n, win in out:
        print("%-28s %-26s %-6s %-13s %-7s checks=%d windows=%d %s" % (t["token"], t["way"][:26], t["shape"], t["conferrer"], t["fits"], n, win, "FAIL " + "; ".join(bad) if bad else ""))
    print(json.dumps(summary(table, tokens), indent=1))
    print("problems:", problems)
    sys.exit(1 if problems else 0)
