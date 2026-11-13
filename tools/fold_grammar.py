#!/usr/bin/env python3
"""
CC — the fold grammar: how a family's rows, read as a set, give a value. As data.

A fold names the rows that enter, the members they are grouped on, which rows of a group stand, how a member
may move across versions, what a retraction removes, the set a count is taken over, how values combine, the
test the result must pass, what a reader gets when no row stands, the shape of the result, who runs the fold
and which folds read it. Used by tools/build_family_model.py, which reads formal/derivation/fold_text.tsv.

    fold := [ "@" SEGMENT "=" LEAF *( "|" LEAF ) ": " ] part *( "; " part )
    part := "reads=" source *( "+" source ) *( "&" filter )      ; source: own | head | FAMILY | "key=" MEMBER *( "," MEMBER )
          | "pick=" picker *( "," picker ) | "order=" compare *( "," compare ) | "bound=" MONO "(" MEMBER ")" *( "," ... )
          | "cut=" cut *( "," cut ) | "over=" SET [ "@" INSTANT ] [ "/" UNIT ] | "weight=" expr
          | "combine=" AGG "(" expr ")" | "combine=policy(" POLICY_ROW ")"
          | "test=" expr CMP expr ( " !" TOKEN | " ?" STATE ":" STATE ) | "absent=" ABSENT | "result=" SHAPE
          | "by=" RUNNER | "feeds=" target *( "," target )

The closed words of each part are held here. An expression is held to its alphabet and its function names
only: this module does not evaluate it. Words that name something no other vocabulary does are returned as
marks and counted where they are used.

Run: python3 tools/fold_grammar.py
"""
import re

PARTS = ("reads", "key", "pick", "order", "bound", "cut", "over", "weight", "combine", "test", "absent", "result", "by", "feeds")
SOURCES = ("own", "head")
FILTERS_BARE = ("live", "direct")
FILTERS_CALL = ("at", "has", "cap", "declared", "cites", "last")
INSTANTS = ("now", "asserted_at", "decision", "prior", "act", "count", "seating", "signed", "founding")
PICK_BARE = ("union", "once", "first_seen", "tips", "agree", "set")
MONO = ("lower_only", "raise_only", "narrow_only", "drop_only", "fixed")
CUTS = ("named", "whole", "terminal", "forward", "none")
SETS = ("standing", "active", "live", "others", "present", "founders", "deciding_seats", "seated", "listed")
UNITS = ("person", "key", "owner")
AGGS = ("min", "max", "sum", "count", "mean", "median", "all", "rate")
ABSENT = ("none", "unspecified", "restricted", "protective", "full", "undefined", "refuse")
SHAPES = ("scalar", "set", "one", "bool", "list")
RUNNERS = ("door", "node", "reader", "advisory", "none")
MARK_WORDS = {"authority", "proxy", "trusted", "founders", "deciding_seats", "seated", "present", "listed",
              "prior", "act", "count", "seating", "agree", "pair", "chain", "once", "boundary", "whole", "terminal", "forward"}
MEMBER = r"[A-Za-z_][A-Za-z_0-9.]*"
EXPR = r"[A-Za-z_0-9.,()*+\-/ ]+"


class FoldError(ValueError):
    pass


def split_top(s, sep):
    out, depth, cur, i = [], 0, "", 0
    while i < len(s):
        c = s[i]
        if c in "([{": depth += 1
        elif c in ")]}": depth -= 1
        if depth == 0 and s.startswith(sep, i):
            out.append(cur); cur = ""; i += len(sep); continue
        cur += c; i += 1
    out.append(cur)
    return out


def parse(s):
    """A fold string -> ({when, parts}, marks, names). names lists what closure() must find in a vocabulary."""
    marks, names = [], {"families": [], "policy_rows": [], "tokens": [], "roles": []}
    def mark(w):
        if w in MARK_WORDS: marks.append(w)
    s = s.strip()
    when = None
    m = re.match(r"@([a-z_]+)=([a-z_0-9|]+): ", s)
    if m:
        when = {"segment": m.group(1), "leaves": m.group(2).split("|")}; s = s[m.end():]
    parts = {}
    for raw in split_top(s, "; "):
        k, eq, v = raw.partition("=")
        if not eq or k not in PARTS or k in parts:
            raise FoldError(f"part {raw!r}")
        if k == "reads":
            bits = split_top(v, "&")
            for src in bits[0].split("+"):
                if src not in SOURCES:           # another family's rows enter the fold
                    if not re.fullmatch(r"[a-z_]+(:[a-z_{}]+)+", src): raise FoldError(f"reads source {src!r}")
                    names["families"].append(src)
            for f in bits[1:]:
                mc = re.fullmatch(r"([a-z_]+)\((.+)\)", f)
                if f in FILTERS_BARE: pass
                elif f.startswith("signer:") or f.startswith("seat:"):
                    for role in f.split(":", 1)[1].split("|"):
                        mark(role)
                        if f.startswith("signer:") and role not in MARK_WORDS: names["roles"].append(role)
                elif mc and mc.group(1) in FILTERS_CALL:
                    if mc.group(1) == "cites": names["families"].append(mc.group(2))
                    if mc.group(1) == "at" and not set(mc.group(2).split("|")) <= set(INSTANTS): raise FoldError(f"instant {f!r}")
                else: raise FoldError(f"reads filter {f!r}")
        elif k == "key":
            if not all(re.fullmatch(MEMBER, x) for x in v.split(",")): raise FoldError(f"key {v!r}")
        elif k in ("pick", "order"):
            for p in split_top(v, ","):
                mc = re.fullmatch(r"([a-z_]+)\((.+)\)", p)
                if p in PICK_BARE and k == "pick": mark(p)
                elif mc and mc.group(1) in ("max", "min"): pass
                elif mc and mc.group(1) == "rank" and re.fullmatch(r"[a-z_0-9>]+", mc.group(2)): pass
                elif mc and k == "pick" and mc.group(1) == "once": mark("once"); names["tokens"].append(mc.group(2))
                elif mc and k == "pick" and mc.group(1) == "chain": mark("chain")
                elif mc and k == "pick" and mc.group(1) == "pair": mark("pair"); names["families"].append(mc.group(2))
                else: raise FoldError(f"{k} {p!r}")
        elif k == "bound":
            for b in split_top(v, ","):
                mc = re.fullmatch(r"([a-z_]+)\((" + MEMBER + r")\)", b)
                if not mc or mc.group(1) not in MONO: raise FoldError(f"bound {b!r}")
        elif k == "cut":
            for c in split_top(v, ","):
                mc = re.fullmatch(r"boundary\((" + MEMBER + r")\)", c)
                if mc: mark("boundary")
                elif c in CUTS: mark(c)
                else: raise FoldError(f"cut {c!r}")
        elif k == "over":
            mc = re.fullmatch(r"([a-z_]+)(?:@([a-z_]+))?(?:/([a-z]+))?", v)
            if not mc or mc.group(1) not in SETS or (mc.group(2) and mc.group(2) not in INSTANTS) or (mc.group(3) and mc.group(3) not in UNITS):
                raise FoldError(f"over {v!r}")
            mark(mc.group(1)); mark(mc.group(2) or "")
        elif k == "weight":
            if not re.fullmatch(EXPR, v): raise FoldError(f"weight {v!r}")
        elif k == "combine":
            mc = re.fullmatch(r"([a-z]+)\((.+)\)", v)
            if mc and mc.group(1) == "policy": names["policy_rows"].append(mc.group(2))
            elif not (mc and mc.group(1) in AGGS and re.fullmatch(EXPR, mc.group(2))): raise FoldError(f"combine {v!r}")
        elif k == "test":
            mc = re.fullmatch(r"(" + EXPR + r")(>=|<=|=|>|<)(" + EXPR + r") (?:!([a-z_0-9]+)|\?([a-z_]+):([a-z_]+))", v)
            if not mc: raise FoldError(f"test {v!r}")
            if mc.group(4): names["tokens"].append(mc.group(4))
        elif k == "absent":
            mc = re.fullmatch(r"from\((.+)\)", v)
            if mc: names["families"].append(mc.group(1))
            elif v not in ABSENT: raise FoldError(f"absent {v!r}")
        elif k == "result":
            if v not in SHAPES and not re.fullmatch(r"(vector|state)\([A-Za-z_|0-9]+\)", v): raise FoldError(f"result {v!r}")
        elif k == "by":
            if v not in RUNNERS: raise FoldError(f"by {v!r}")
        elif k == "feeds":
            for t in v.split(","):
                if t != "replication.audience": names["families"].append(t)
        parts[k] = v
    return {"when": when, "parts": parts}, marks, names


def closure(names, voc, family_ok):
    bad = [f"family {f}" for f in names["families"] if not family_ok(f, voc["families"])]
    bad += [f"policy row {p}" for p in names["policy_rows"] if p not in voc["policy_rows"]]
    bad += [f"refusal token {t}" for t in names["tokens"] if t not in voc["tokens"]]
    bad += [f"role {r}" for r in names["roles"] if r not in voc["roles"]]
    return bad


DEFAULT = ("reads=own&live; key=references_attestation_id,attesting_key_id; "
           "pick=rank(recants>withdraws>supersedes),max(asserted_at),min(attestation_id); "
           "bound=narrow_only(cohort_scope); cut=named,forward; over=standing/person; absent=none; result=scalar; by=node")


def self_test():
    good = [DEFAULT, "@job=charter: reads=head; pick=chain(prev_head_digest)", "combine=policy(moderator_election)",
            "@group=accord: over=standing@decision/person; test=2*yes>n !roster_change_below_majority",
            "combine=max(count(owner),(prev*9+9) div 10,floor)", "absent=restricted; by=reader", "feeds=group:roster"]
    bad = ["reads=theirs", "pick=newest", "over=everyone", "by=someone", "bound=sideways(x)", "key=a; key=b", "test=a>b"]
    for g in good: parse(g)
    n = 0
    for g in bad:
        try: parse(g)
        except FoldError: n += 1
    assert n == len(bad), f"{len(bad) - n} malformed folds parsed"
    print(f"fold grammar: {len(good)} forms parse, {len(bad)} malformed forms refused")


if __name__ == "__main__":
    self_test()
