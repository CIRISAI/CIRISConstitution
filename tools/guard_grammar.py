#!/usr/bin/env python3
"""
CC — the guard grammar: what must be held, live or signed for a row to be admitted, as data.

A guard is a conjunction of clauses. Each clause is a query over the rows a node holds, joined to the row at
the door, with a named outcome when it fails. This module parses a guard and holds every terminal to a
vocabulary the repository already has: a registry family or leaf, a row state, a role token, a signer
condition, an identity type, a policy row, a scope, and a refusal token or hard-case kind that stands in the
text. It is used by tools/build_transitions.py, which reads formal/derivation/guard_text.tsv.

    guard   := "none" | clause *( " & " clause )
    clause  := [ "each(" KEYS ") " ] [ "when(" cond *( "," cond ) ") " ] ( atom | "(" guard ")" ) [ " else " outcome ]
    cond    := "verb=" VERB | "leaf=" LEAF *( "|" LEAF ) | "subkind=" SUBKIND | "has=" MEMBER | atom
    atom    := rowatom | keyatom
    rowatom := QUANT " " FAMILYSET "@" STATE "[" join *( "," join ) "]" [ " as " NAME ] [ " at " INSTANT ] [ " " window ]
    join    := SLOT OP SLOT
    keyatom := [ "not " ] ( ROLE "(" KEY "," TARGET [ ",via=" VIA ] ")" | CONDITION "(" KEY ")" | "type(" KEY "," TYPE ")" | "signs(" KEY ")" ) [ " at " INSTANT ]
    window  := ( "within" | "after" ) "(" POLICY ")"        ; also a clause of its own
    outcome := ( "refuse" [ "(" TOKEN ")" ] | "exclude" | "advise" ) [ "+" HARD_CASE_KIND ]

Three tokens name something no other vocabulary does and are counted wherever they are used: the state
`landed` (admitted and its policy met), the operator `commits`, the key atom `signs`. So are a reference to
no named member (`ref:*`) and a refusal with no token (`refuse` bare). parse() returns the tree and the list
of those marks; closure() returns what is outside the vocabularies.

Run: python3 tools/guard_grammar.py --self-test
"""
import re, sys

QUANTS = ("one", "all", "latest", "no")
STATES = ("admitted", "withdrawn", "recanted", "superseded", "landed")
OPS = (">=", "<=", "=", " in ", " commits ")
INSTANTS = ("asserted_at", "receipt", "its_asserted_at")
VERBS = ("attest", "authorize", "replace", "withdraw", "recant")
CONDITIONS = ("adult", "capacitated")
IDENTITY_TYPES = ("user", "node", "agent")
SCOPES = ("self", "family", "affiliations", "community", "federation", "accord", "public")
PLAIN_SLOTS = ("id", "signer", "attested", "subject", "object", "key")


class GuardError(ValueError):
    pass


def split_top(s, sep):
    """Split on `sep` outside (), [] and {}."""
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


def take_call(s, name):
    """`name(...)` at the start of s -> (inside, rest), honouring nesting; None if s does not start with it."""
    if not s.startswith(name + "("):
        return None
    depth = 0
    for i in range(len(name), len(s)):
        if s[i] == "(": depth += 1
        elif s[i] == ")":
            depth -= 1
            if depth == 0:
                return s[len(name) + 1:i], s[i + 1:]
    raise GuardError(f"unclosed ( after {name}")


def parse_slot(s, marks):
    s = s.strip()
    m = re.fullmatch(r"(?:([A-Z])\.)?(.+)", s)
    name, body = m.group(1), m.group(2)
    if body in PLAIN_SLOTS:
        kind, arg = body, None
    elif body == "ref:*":
        kind, arg = "ref", "*"; marks.append("ref:*")
    elif re.fullmatch(r"(ref|val|leaf):[a-z_0-9A-Z]+", body):
        kind, arg = body.split(":", 1)
    elif re.fullmatch(r"[a-z_]+", body):
        kind, arg = "const", body          # a literal value on the right of a join (val:scope=analyze)
    else:
        raise GuardError(f"slot {s!r}")
    return {"slot": kind, "arg": arg, "of": name}


def parse_join(s, marks):
    for op in OPS:
        parts = split_top(s, op)
        if len(parts) == 2:
            if op == " commits ": marks.append("commits")
            return {"left": parse_slot(parts[0], marks), "op": op.strip(), "right": parse_slot(parts[1], marks)}
    raise GuardError(f"join {s!r}")


def parse_atom(s, marks):
    s = s.strip()
    at = None
    m = re.search(r" at (asserted_at|receipt|its_asserted_at)$", s)
    if m:
        at = m.group(1); s = s[:m.start()]
    m = re.fullmatch(r"(within|after)\(([a-z_]+)\)", s)
    if m:
        return {"atom": "window", "dir": m.group(1), "policy": m.group(2)}
    window = None
    m = re.search(r" (within|after)\(([a-z_]+)\)$", s)
    if m:
        window = {"dir": m.group(1), "policy": m.group(2)}; s = s[:m.start()]
    name = None
    m = re.search(r" as ([A-Z])$", s)
    if m:
        name = m.group(1); s = s[:m.start()]
    m = re.fullmatch(r"(one|all|latest|no|set\([a-z:_*]+\)) (.+?)@([a-z]+)\[(.*)\]", s)
    if m:
        quant, fams, state, joins = m.groups()
        if quant.startswith("set(") and "ref:*" in quant: marks.append("ref:*")
        if state not in STATES: raise GuardError(f"state {state!r}")
        if state == "landed": marks.append("landed")
        other = take_call(fams, "other")
        famset = {"other": split_top(other[0], "|")} if other and not other[1] else {"any": True} if fams == "*" else {"of": split_top(fams, "|")}
        return {"atom": "row", "quant": quant, "families": famset, "state": state,
                "joins": [parse_join(j, marks) for j in split_top(joins, ",") if j], "as": name, "at": at, "window": window}
    if name or window:
        raise GuardError(f"`as` or a window on something that is not a row atom: {s!r}")
    neg = s.startswith("not ")
    if neg: s = s[4:]
    m = re.fullmatch(r"([a-z_:]+)\((.*)\)", s)
    if not m:
        raise GuardError(f"atom {s!r}")
    fn, args = m.group(1), [a.strip() for a in split_top(m.group(2), ",")]
    if fn == "signs": marks.append("signs")
    return {"atom": "key", "not": neg, "fn": fn, "args": args, "at": at}


def parse_outcome(s):
    m = re.fullmatch(r"(refuse|exclude|advise)(?:\(([a-z_0-9]+)\))?(?:\+([a-z_0-9]+))?", s.strip())
    if not m or (m.group(2) and m.group(1) != "refuse"):
        raise GuardError(f"outcome {s!r}")
    return {"do": m.group(1), "token": m.group(2), "hard_case": m.group(3)}


def parse_cond(s, marks):
    s = s.strip()
    m = re.fullmatch(r"(verb|leaf|subkind|has)=([a-z_0-9|]+)", s)
    if m:
        return {"cond": m.group(1), "values": m.group(2).split("|")}
    return {"cond": "atom", "atom": parse_atom(s, marks)}


def parse_clause(s, marks):
    s = s.strip()
    c = {"each": None, "when": [], "else": None}
    for _ in range(2):                       # `each` and `when` lead a clause in either order
        t = take_call(s, "each")
        if t and c["each"] is None:
            c["each"] = t[0]; s = t[1].strip()
        t = take_call(s, "when")
        if t and not c["when"]:
            c["when"] = [parse_cond(x, marks) for x in split_top(t[0], ",")]; s = t[1].strip()
    parts = split_top(s, " else ")
    if len(parts) > 2:
        raise GuardError(f"two outcomes on one clause: {s!r}")
    body = parts[0].strip()
    if len(parts) == 2:
        c["else"] = parse_outcome(parts[1])
        if c["else"]["do"] == "refuse" and not c["else"]["token"]: marks.append("refuse")
    if body.startswith("(") and body.endswith(")") and take_call("g" + body, "g")[1] == "":
        c["group"] = parse(body[1:-1], marks)[0]
    else:
        c["atom"] = parse_atom(body, marks)
    return c


def parse(s, marks=None):
    """A guard string -> (list of clauses, marks). Raises GuardError on anything outside the grammar."""
    marks = [] if marks is None else marks
    s = s.strip()
    if s == "none":
        return [], marks
    return [parse_clause(x, marks) for x in split_top(s, " & ")], marks


def family_ok(name, families):
    """A registry family, a leaf of one (placeholder segments filled, trailing ones left off), or a stem ending `:*`."""
    if name in families:
        return True
    if name.endswith(":*"):
        return any(f.startswith(name[:-1]) for f in families)
    for f in families:
        if "{" not in f:
            continue
        segs = f.split(":")
        while len(segs) >= 2:                    # the family, or the family less its trailing placeholders (never the bare stem)
            if re.fullmatch(":".join("[a-z0-9_]+" if x.startswith("{") else re.escape(x) for x in segs), name):
                return True
            if not segs[-1].startswith("{"):
                break
            segs = segs[:-1]
    return False


def closure(clauses, voc, family=None):
    """What a parsed guard names outside the vocabularies `voc` (families, roles, policy_rows, tokens, hard_cases)."""
    bad = []

    def atom(a):
        if a["atom"] == "window":
            if a["policy"] not in voc["policy_rows"]: bad.append(f"policy row {a['policy']}")
        elif a["atom"] == "row":
            fs = a["families"]
            for f in fs.get("of", []) + fs.get("other", []):
                if not family_ok(f, voc["families"]): bad.append(f"family {f}")
            if a["window"] and a["window"]["policy"] not in voc["policy_rows"]: bad.append(f"policy row {a['window']['policy']}")
        else:
            fn, args = a["fn"], a["args"]
            if fn in CONDITIONS or fn == "signs":
                if len(args) != 1: bad.append(f"{fn} takes one key")
            elif fn == "type":
                if len(args) != 2 or args[1] not in IDENTITY_TYPES: bad.append(f"identity type in {fn}({','.join(args)})")
            elif fn in voc["roles"]:
                if len(args) not in (2, 3) or (len(args) == 3 and args[2] not in ("via=none", "via=delegates_to")):
                    bad.append(f"{fn}({','.join(args)})")
            else:
                bad.append(f"role or condition {fn}")

    def walk(cs):
        for c in cs:
            for w in c["when"]:
                if w["cond"] == "verb" and not set(w["values"]) <= set(VERBS): bad.append(f"verb {w['values']}")
                if w["cond"] == "atom": atom(w["atom"])
            if "group" in c: walk(c["group"])
            else: atom(c["atom"])
            o = c["else"]
            if o:
                if o["token"] and o["token"] not in voc["tokens"]: bad.append(f"refusal token {o['token']}")
                if o["hard_case"] and o["hard_case"] not in voc["hard_cases"]: bad.append(f"hard-case kind {o['hard_case']}")
    walk(clauses)
    return bad


def top_conds(clauses, key):
    """The values of a `verb=` or `leaf=` condition that every clause of the guard carries at its top, else None."""
    vals = None
    for c in clauses:
        got = [set(w["values"]) for w in c["when"] if w["cond"] == key]
        if not got:
            return None
        vals = got[0] if vals is None else vals & got[0]
    return sorted(vals) if vals else None


def self_test():
    good = [
        "none",
        "one deferral:response:approved@admitted[id=ref:authorized_by,subject=subject] as R else refuse(x) & wa(R.signer,subject,via=none) at its_asserted_at else refuse(x)",
        "each(subject) when(leaf=widening,not member(key,object)) (one membership:acceptance@admitted[signer=key,object=object] as A & no membership:widening@admitted[ref:*=A.id] else refuse+k)",
        "set(ref:*) ballot:moderator@admitted[object=object] else refuse & winner(signer,object) else refuse & after(moderator_election) else refuse",
        "one other(ratchet:flag:*|detection:*)@admitted[id=ref:evidence_refs] else refuse",
        "when(leaf=recovery) one trust:charter@admitted[object=object,val:recovery_commitments commits signer] else refuse",
        "when(leaf=confirmed) one accord:invoke:constitutional:{halt_id}@admitted[object=object] within(accord_halt) else refuse",
        "one *@admitted[id=ref:*,val:cohort_scope=val:cohort_scope] else refuse",
    ]
    bad = ["one x@held[id=id]", "some x@admitted[id=id]", "member(key) else refuse(a)(b)", "one x@admitted[id~id]", "each(subject one x@admitted[id=id]"]
    for g in good:
        parse(g)
    n = 0
    for g in bad:
        try:
            parse(g)
        except GuardError:
            n += 1
    _, marks = parse(good[2])
    assert n == len(bad), f"{len(bad) - n} malformed guards parsed"
    assert marks.count("ref:*") == 1 and marks.count("refuse") == 1
    assert top_conds(parse("when(verb=withdraw,leaf=decided) no a@admitted[object=object] else refuse")[0], "verb") == ["withdraw"]
    assert family_ok("membership:acceptance", {"membership:{stage}"}) and not family_ok("membership", {"membership:{stage}"})
    print(f"guard grammar: {len(good)} forms parse, {len(bad)} malformed forms refused")


if __name__ == "__main__":
    self_test()
