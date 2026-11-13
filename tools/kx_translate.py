"""
KX translators: each of the five rule grammars of the repository (tools/guard_grammar.py, tools/fold_grammar.py,
tools/change_grammar.py, the `count` arms of formal/derivation/count_text.tsv with the policy rows of
tools/build_governance_policy.py, and tools/build_reactions.py) written into the one expression language of
tools/kx.py. Each translator takes the parse tree the grammar's own tool returns and gives KX source text.

    translate(guard_clauses)            guards        -> verdicts(...)
    Tx(parts, family, when).build()     folds         -> tuple(groups, order, combined, verdict, absent, n)
    ch_kx(items)                        changes       -> set of (on, verdict, effects)
    re_kx(clauses)                      reactions     -> set of (kind, name, state) / (land, name, held, late) / (react, effects)
    count_kx(arms)                      count arms    -> the door of the first arm whose selector holds
    policy_call(row)                    policy rows   -> tally2(...) with BASE, A, O, EL to be filled
"""
import re


ROW_ALONE_ROLES = {"subject", "author", "self"}     # read off the row judged (KERNEL 5)


def outcome(o):
    if not o: return "fail"
    return o["do"] + (f"({o['token']})" if o["token"] else "") + (f"+{o['hard_case']}" if o.get("hard_case") else "")


def q(s): return "'" + s + "'"


def digest_source(joins):
    """A join id=ref:X or id=N.ref:X finds its row by a digest: (owner name or None, field)."""
    for j in joins:
        if j["op"] == "=" and j["left"]["slot"] == "id" and j["right"]["slot"] == "ref":
            return j["right"]["of"], j["right"]["arg"]
    return None


def t_slot(slot, rowvar, bound_prefix_ok=True):
    k, a = slot["slot"], slot["arg"]
    base = slot["of"] if slot["of"] else rowvar
    if k == "key": return "key"
    if k == "const": return q(a)
    if k == "ref": return f"{base}.names" if a == "*" else f"{base}.ref.{a}"
    if k == "val": return f"{base}.{a}"
    if k == "leaf": return f"{base}.leaf.{a}"
    return f"{base}.{k}"


def t_join(j):
    L = t_slot(j["left"], "r"); R = t_slot(j["right"], "self")
    lref = j["left"]["slot"] == "ref" and j["left"]["arg"] == "*"
    rref = j["right"]["slot"] == "ref" and j["right"]["arg"] == "*"
    op = j["op"]
    if op == "=":
        if lref and rref: return f"meets({L}, {R})"
        if lref: return f"member({R}, {L})"
        if rref: return f"member({L}, {R})"
        return f"eq({L}, {R})"
    if op == ">=": return f"ge({L}, {R})"
    if op == "<=": return f"le({L}, {R})"
    if op == "in": return f"member({L}, {R})"
    if op == "commits": return f"member({R}, {L})"
    raise ValueError(op)


def t_keyarg(s):
    m = re.fullmatch(r"(?:([A-Z])\.)?(.+)", s)
    who, body = m.group(1), m.group(2)
    base = who or "self"
    if body == "key": return "key"
    if body.startswith("val:"): return f"{base}.{body[4:]}"
    if body.startswith("ref:"): return f"{base}.ref.{body[4:]}"
    if body in ("signer", "subject", "attested", "object"): return f"{base}.{body}"
    return q(body)


def t_source(a):
    if a["quant"].startswith("set("):
        f = a["quant"][4:-1].split(":", 1)[1]; return f"named(self, {q(f)})"
    if a["state"] == "named": return "past(self)"
    src = digest_source(a["joins"])
    if src:
        who, f = src; return f"named({who or 'self'}, {q(f)})"
    return "held"


def t_cands(a, policy):
    preds = ["ne(r.id, self.id)"]
    fs = a["families"]
    if "of" in fs: preds.append(f"isfam(r, {q('|'.join(fs['of']))})")
    if "other" in fs: preds += [f"isfam(r, {q('|'.join(fs['other']))})", "ne(r.signer, self.signer)"]
    src = digest_source(a["joins"]) if not a["quant"].startswith("set(") and a["state"] != "named" else None
    for j in a["joins"]:
        if src and j["op"] == "=" and j["left"]["slot"] == "id" and j["right"]["slot"] == "ref": continue
        preds.append(t_join(j))
    if a["at"] == "asserted_at": preds.append("le(r.asserted_at, self.asserted_at)")
    if a["at"] == "receipt": preds.append("lt(arrival(r), arrival(self))")
    if a["window"]:
        w = f"cell('policy', {q(a['window']['policy'])})"
        inside = f"in(self.asserted_at, r.asserted_at, add(r.asserted_at, {w}))"
        preds.append(inside if a["window"]["dir"] == "within" else f"and(has(r, 'asserted_at'), has(self, 'asserted_at'), not({inside}))")
    return f"sel({t_source(a)}, \\r: and({', '.join(preds)}))"


def t_state(a, var):
    s = a["state"]
    if s == "named": return f"live_in(past(self), {var})"
    if s == "landed": return f"and(live({var}), eq({var}.landed, 1))"
    return f"eq(state({var}), {q(s)})"


def t_atom(a):
    if a["atom"] == "window":
        w = f"cell('policy', {q(a['policy'])})"
        closed = f"and(some(named(self, '*')), every(named(self, '*'), \\x: ge(now, add(arrival(x), {w}))))"
        return closed if a["dir"] == "after" else f"and(some(named(self, '*')), not({closed}))"
    if a["atom"] == "row":
        C = t_cands(a, None)
        M = f"sel({C}, \\m: {t_state(a, 'm')})"
        qn = a["quant"]
        if qn == "one": return f"some({M})"
        if qn == "no": return f"none({M})"
        if qn == "all" or qn.startswith("set("): return f"and(some({C}), eq(size({M}), size({C})))"
        if qn == "latest": return f"let L = greatest({C}, \\r: r.asserted_at) in and(ne(L, 'tie'), some(L), {t_state(a, 'L')})"
    fn, args = a["fn"], a["args"]
    S = "held"
    if a["at"] in ("asserted_at", "its_asserted_at"):
        who = re.match(r"([A-Z])\.", args[0]) if a["at"] == "its_asserted_at" else None
        if a["at"] == "its_asserted_at" and not who:
            raise ValueError("at its_asserted_at with no named row: whose instant is not stated")
        lim = f"{who.group(1)}.asserted_at" if who else "self.asserted_at"
        S = f"sel(held, \\x: or(not(isfam(x, 'seat:*')), le(x.asserted_at, {lim})))"
    if fn == "type": v = f"eq(typeof({t_keyarg(args[0])}), {q(args[1])})"
    elif fn == "signs": v = f"member({t_keyarg(args[0])}, cosigners(self))"
    elif fn in ("adult", "capacitated"):
        k = t_keyarg(args[0]); v = f"stands_in({S}, {k}, {q(fn)}, {k})"
    elif fn in ROW_ALONE_ROLES:
        k = t_keyarg(args[0]); tgt = args[1]
        if tgt.startswith("ref:"):
            v = f"let T = named(self, {q(tgt[4:])}) in and(some(T), eq(fld(the(T), 'subject'), {k}))"
        else:
            v = f"eq(self.{fn if fn != 'self' else 'signer'}, {k})"
    else:
        v = f"stands_in({S}, {t_keyarg(args[0])}, {q(fn)}, {t_keyarg(args[1])})"
    return f"not({v})" if a["not"] else v


def t_outcome(o):
    if not o: return "'fail'"
    return q(outcome(o))


def named_field(a):
    """The member of the judged row by whose digest a row atom finds its rows (`*`: any of them), else None."""
    if a["atom"] != "row": return None
    if a["quant"].startswith("set("): return a["quant"][4:-1].split(":", 1)[1]
    src = digest_source(a["joins"])
    return src[1] if src and src[0] is None else None


def t_waits(f):
    """A row the judged row names in member f is not held: the kept layer's `missing`, read for one member."""
    return "some(missing(self))" if f == "*" else f"and(not(isnone(self.ref.{f})), none(named(self, {q(f)})))"


def t_clause(c):
    if "group" in c:
        inner = t_clauses(c["group"])
        body = inner if not c["else"] else f"let G = {inner} in first(some(G) -> verdicts(G, {t_outcome(c['else'])}), else -> G)"
    else:
        body = f"check({t_atom(c['atom'])}, {t_outcome(c['else'])})"
        f = named_field(c["atom"])
        if f and (c["else"] or {}).get("do") == "void":       # void: the row waits for what it names, and is judged once that is held
            body = f"first({t_waits(f)} -> wait({q(f)}), else -> {body})"
    if c["when"]:
        conds = []
        for w in c["when"]:
            if w["cond"] == "verb": conds.append(f"member(self.verb, {{{', '.join(q(x) for x in w['values'])}}})")
            elif w["cond"] == "leaf": conds.append(f"member(self.leafname, {{{', '.join(q(x) for x in w['values'])}}})")
            elif w["cond"] == "subkind": conds.append(f"member(self.subkind, {{{', '.join(q(x) for x in w['values'])}}})")
            elif w["cond"] == "has": conds.append(f"has(self, {q(w['values'][0])})")
            else: conds.append(t_atom(w["atom"]))
        body = f"first(and({', '.join(conds)}) -> {body}, else -> ok())"
    if c["each"]:
        k = c["each"][4:] if c["each"].startswith("val:") else c["each"]
        body = f"each(elems(self, {q(k)}), \\key: {body})"
    return body


def t_clauses(cs):
    lets = []
    for c in cs:
        if "atom" in c and c["atom"]["atom"] == "row" and c["atom"]["as"]:
            a = c["atom"]
            lets.append((a["as"], f"the(sel({t_cands(a, None)}, \\m: {t_state(a, 'm')}))"))
    body = f"verdicts({', '.join(t_clause(c) for c in cs)})"
    for n, e in reversed(lets):
        body = f"let {n} = {e} in {body}"
    return body


def t_clause_among(c, siblings, outer=None):
    """One clause as its own expression, for its layer: with the rows its siblings bind by `as`, and inside the
    `when` and `each` of the group clause that holds it."""
    body = t_clauses([c])
    for x in reversed(siblings):
        if x is not c and "atom" in x and x["atom"]["atom"] == "row" and x["atom"]["as"]:
            a = x["atom"]
            body = f"let {a['as']} = the(sel({t_cands(a, None)}, \\m: {t_state(a, 'm')})) in {body}"
    if outer:
        for w in outer["when"]:
            if w["cond"] == "atom": body = f"first({t_atom(w['atom'])} -> {body}, else -> ok())"
    return body


def translate(clauses):
    return t_clauses(clauses) if clauses else "verdicts()"


LABELS = ("by", "feeds", "result")


ROW_READ = {"self": "attested", "subject": "subject", "author": "signer"}   # roles read off the row (KERNEL 5), not seats


UNITS = {"person": {"u1": "P", "u2": "P", "n1": "N"}, "owner": {"u1": "u1", "u2": "u1", "n1": "n1"}}


class NeedsOperator(Exception):
    pass


VERB_RANK = {"recants": "recant", "withdraws": "withdraw", "supersedes": "replace"}


TOKA = re.compile(r"\s*(\d+|[A-Za-z_][A-Za-z_0-9.]*|div|[()*+\-/,]|>=|<=|=|>|<)")


def lexa(s):
    out, i = [], 0
    while i < len(s):
        m = TOKA.match(s, i)
        if not m: raise SyntaxError(s[i:])
        out.append(m.group(1)); i = m.end()
    return out


def parse_arith(s):
    toks = lexa(s); pos = [0]
    def peek(): return toks[pos[0]] if pos[0] < len(toks) else None
    def take(): pos[0] += 1; return toks[pos[0] - 1]
    def atom():
        t = take()
        if t == "(":
            e = expr(); take(); return e
        if t == "-": return ("neg", atom())
        if t.isdigit(): return ("num", int(t))
        if peek() == "(":
            take(); args = []
            while peek() != ")":
                args.append(expr())
                if peek() == ",": take()
            take(); return ("fn", t, args)
        return ("name", t)
    def term():
        e = atom()
        while peek() in ("*", "/", "div"):
            op = take(); e = (op, e, atom())
        return e
    def expr():
        e = term()
        while peek() in ("+", "-"):
            op = take(); e = (op, e, term())
        return e
    e = expr()
    if pos[0] != len(toks): raise SyntaxError(s)
    return e


def split_top(s):
    out, d, cur = [], 0, ""
    for ch in s:
        if ch == "(": d += 1
        elif ch == ")": d -= 1
        if ch == "," and d == 0: out.append(cur); cur = ""; continue
        cur += ch
    out.append(cur)
    return out


class Tx:
    def __init__(self, parts, family, when=None):
        self.P, self.family, self.when = parts, family, when
        self.tables = {}
        self.gaps = []

    def fld(self, var, m):
        return f"arrival({var})" if m == "admission_order" else f"{var}.{m}"

    def source(self):
        reads = self.P.get("reads", "own&live")
        bits = reads.split("&"); srcs = bits[0].split("+")
        parts = []
        for s in srcs:
            if s == "own": parts.append(f"sel(held, \\r: and(isfam(r, {q(self.family)}), ne(r.id, self.id)))")
            elif s == "head": parts.append("let H = sel(held, \\r: isfam(r, 'group:roster')) in sel(H, \\r: none(sel(H, \\x: member(r.id, x.names))))")
            else: parts.append(f"sel(held, \\r: isfam(r, {q(s)}))")
        S = parts[0] if len(parts) == 1 else f"union_rows({', '.join(parts)})"
        if len(parts) > 1:
            S = "sel(held, \\r: or(" + ", ".join(self._srcpred(s) for s in srcs) + "))"
        preds = []
        for flt in bits[1:]:
            if flt == "live": preds.append("live(r)")
            elif flt == "direct": preds.append("not(has(r, 'via'))")
            elif flt.startswith("signer:"): preds.append("or(" + ", ".join(f"eq(r.signer, r.{ROW_READ[x]})" if x in ROW_READ else f"stands(r.signer, {q(x)}, r.object)" for x in flt[7:].split("|")) + ")")
            elif flt.startswith("seat:"): preds.append("eq(typeof(r.signer), 'user')")
            elif flt.startswith("at("): preds.append("and(le(r.asserted_at, now), or(not(has(r, 'valid_until')), lt(now, r.valid_until)))")
            elif flt.startswith("has("): preds.append("or(" + ", ".join(f"has(r, {q(m)})" for m in flt[4:-1].split("|")) + ")")
            elif flt.startswith("cap("): preds.append(f"stands(r.signer, {q('cap:' + flt[4:-1])}, r.object)")
            elif flt.startswith("declared("): preds.append(f"has(r, {q(flt[9:-1])})")
            elif flt.startswith("cites("): preds.append(f"some(sel(past(r), \\x: isfam(x, {q(flt[6:-1])})))")
        if self.when: preds.append("member(r.leafname, {" + ", ".join(q(x) for x in self.when["leaves"]) + "})")
        if preds: S = f"sel({S}, \\r: and({', '.join(preds)}))"
        return S

    def _srcpred(self, s):
        if s == "own": return f"and(isfam(r, {q(self.family)}), ne(r.id, self.id))"
        if s == "head": return "and(isfam(r, 'group:roster'), none(sel(held, \\x: and(isfam(x, 'group:roster'), member(r.id, x.names)))))"
        return f"isfam(r, {q(s)})"

    def cut(self, S):
        retracted = "some(sel(held, \\q: and(member(q.verb, {'withdraw', 'recant'}), member(X.id, q.names), eq(q.signer, X.signer))))"
        for c in self.P.get("cut", "named,forward").split(","):
            if c == "named": S = f"sel({S}, \\r: not({retracted.replace('X.', 'r.')}))"
            elif c == "forward": S = f"sel({S}, \\r: none(sel(past(r), \\y: {retracted.replace('X.', 'y.')})))"
            elif c == "terminal": S = f"sel({S}, \\r: none(sel(past(r), \\y: eq(y.terminal, 1))))"
            elif c.startswith("boundary("):
                m = c[9:-1]
                b = f"min(sel(held, \\k: and(isfam(k, 'key:revocation'), eq(k.attested, r.signer), live(k))), \\k: k.revoked_after)"
                S = f"sel({S}, \\r: or(isnone({b}), not(has(r, {q(m)})), lt({self.fld('r', m)}, {b})))"
        return S

    def key(self, var="r"):
        ms = self.P.get("key", "references_attestation_id,attesting_key_id").split(",")
        return "tuple(" + ", ".join(self.fld(var, m) for m in ms) + ")"

    def comps(self, spec, var):
        out = []
        for p in split_top(spec):
            m = re.fullmatch(r"(max|min)\((.+)\)", p)
            if m:
                out.append(f"neg({self.fld(var, m.group(2))})" if m.group(1) == "max" else self.fld(var, m.group(2))); continue
            m = re.fullmatch(r"rank\((.+)\)", p)
            if m:
                names = m.group(1).split(">"); tname = "rank:" + m.group(1)
                tab = {}
                for i, x in enumerate(names): tab["verb:" + VERB_RANK[x] if x in VERB_RANK else "leaf:" + x] = i
                self.tables[tname] = tab
                vs = [f"cell({q(tname)}, {q('verb:' + VERB_RANK[x])})" for x in names if x in VERB_RANK]
                # the rank is the cell for the row's verb when the list names verbs, else for its leaf
                if any(x in VERB_RANK for x in names):
                    out.append(f"imin(first(member({var}.verb, {{{', '.join(q(VERB_RANK[x]) for x in names if x in VERB_RANK)}}}) -> cell({q(tname)}, add_str('verb:', {var}.verb)), else -> {len(names)}), first(member({var}.leafname, {{{', '.join(q(x) for x in names)}}}) -> cell({q(tname)}, add_str('leaf:', {var}.leafname)), else -> {len(names)}))")
                else:
                    out.append(f"first(member({var}.leafname, {{{', '.join(q(x) for x in names)}}}) -> cell({q(tname)}, add_str('leaf:', {var}.leafname)), else -> {len(names)})")
        return out

    def least_id(self, G, spec):
        cs = self.comps(spec, "r")
        return f"let W = least({G}, \\r: tuple({', '.join(cs)})) in first(eq(W, 'tie') -> 'tie', else -> fld(W, 'id'))"

    def pick(self, G):
        spec = self.P.get("pick")
        if spec is None: return "none"
        bits = split_top(spec)
        if bits[0].startswith("pair("):
            F = bits[0][5:-1]
            G = f"sel({G}, \\r: some(sel(held, \\x: and(isfam(x, {q(F)}), member(r.id, x.names), live(x)))))"
            bits = bits[1:]
            if not bits: return f"ids({G})"
            return f"let G2 = {G} in first(none(G2) -> none, else -> {self.least_id('G2', ','.join(bits))})"
        b = bits[0]
        if b in ("union", "set"): return f"ids({G})"
        if b == "agree": return f"one({G}, \\r: r.value)"
        if b.startswith("once"):
            tok = b[5:-1] if "(" in b else ""
            return f"first(gt(count({G}, \\r: r.id), 1) -> contested({q(tok)}), else -> fld(the({G}), 'id'))"
        if b.startswith("chain("):
            tips = f"setof(sel({G}, \\r: none(sel({G}, \\x: and(ne(x.id, r.id), member(r.id, x.names))))), \\r: r.id)"
            if len(bits) > 1 and bits[1] == "tips": return tips
            return f"let T = {tips} in first(eq(size(T), 1) -> one(sel({G}, \\r: member(r.id, T)), \\r: r.id), else -> 'tie')"
        return self.least_id(G, spec)

    def bounds(self, G):
        spec = self.P.get("bound")
        if not spec: return "tuple()"
        out = []
        for b in split_top(spec):
            mono, m = re.fullmatch(r"([a-z_]+)\((.+)\)", b).groups()
            how = {"raise_only": "max", "fixed": "one"}.get(mono, "min")
            out.append(f"{how}({G}, \\r: {self.fld('r', m)})")
        return "tuple(" + ", ".join(out) + ")"

    def over(self):
        spec = self.P.get("over")
        if not spec: return None
        m = re.fullmatch(r"([a-z_]+)(?:@([a-z_]+))?(?:/([a-z]+))?", spec)
        role, inst = m.group(1), m.group(2)
        if inst == "named": S = "past(self)"
        elif inst == "signed":       # the set as it stood at the instant the counted row was signed
            S = "sel(held, \\x: or(not(isfam(x, 'seat:*')), le(x.asserted_at, self.asserted_at)))"
        else: S = "held"
        return f"size(holder_units_in({S}, {q(role)}, self.object, {q(m.group(3) or 'key')}))"

    def arith(self, e, var, env):
        t = e[0]
        if t == "num": return str(e[1])
        if t == "neg": return f"neg({self.arith(e[1], var, env)})"
        if t == "name":
            n = e[1]
            if n in env: return env[n]
            if var: return f"first(has({var}, {q(n)}) -> fld({var}, {q(n)}), else -> cell('const', {q(n)}, 1))"
            return f"cell('const', {q(n)}, 1)"
        if t == "fn":
            fn, args = e[1], e[2]
            if fn == "count":
                return f"count(STAND, \\x: x.{args[0][1]})" if args else "size(STAND)"
            if fn == "rate":
                self.gaps.append("rate: a table of weights per class; a weight that is not an integer is floating point")
                return f"cell('const', add_str('rate:', {self.arith(args[0], var, env)}), 1)"
            if fn not in ("min", "max"): raise NeedsOperator(fn)
            xs = [self.arith(a, var, env) for a in args]
            return f"{'imin' if fn == 'min' else 'imax'}({', '.join(xs)})" if None not in xs else "none"
        a, b = self.arith(e[1], var, env), self.arith(e[2], var, env)
        if t == "/": self.gaps.append("'/' in a cell: read as floor division (div); the cell does not say")
        return f"{ {'+': 'add', '-': 'sub', '*': 'mul', 'div': 'div', '/': 'div'}[t] }({a}, {b})"

    def build(self):
        S = self.cut(self.source())
        K = self.key("r")
        per_group = f"tuple({self.pick('G')}, {self.bounds('G')})"
        groups = f"each(setof(S, \\r: {K}), \\g: let G = sel(S, \\r: eq({K}, g)) in {per_group})"
        spec = self.P.get("pick")
        if spec is None:
            stand = "S"
        else:
            stand = (f"sel(S, \\r: let G = sel(S, \\x: eq({self.key('x')}, {K})) in let V = {self.pick('G')} in "
                     f"or(eq(V, r.id), member(r.id, V)))")
        order = "none"
        if self.P.get("order"):
            cs = self.comps(self.P["order"], "x"); cr = self.comps(self.P["order"], "r")
            order = (f"each(STAND, \\r: count(sel(STAND, \\x: lt_tuple(tuple({', '.join(cs)}), tuple({', '.join(cr)}))), \\x: x.id))")
        env = {}
        ov = self.over()
        if ov: env["n"] = "N"
        comb = "none"
        if "combine" in self.P and not self.P["combine"].startswith("policy("):
            m = re.fullmatch(r"([a-z]+)\((.+)\)", self.P["combine"]); agg, arg = m.groups()
            if agg == "all": comb = f"every(STAND, \\r: eq(r.{arg}, 1))"
            elif agg == "count": comb = f"count(STAND, \\r: r.{arg})"
            elif agg == "max" and "," in arg and "count(" in arg:
                comb = self.arith(parse_arith("max(" + arg + ")"), None, env)
            else:
                ex = parse_arith(arg if "," not in arg else "min(" + arg + ")" if agg == "min" else arg)
                env2 = dict(env)
                if "weight" in self.P: env2["weight"] = self.arith(parse_arith(self.P["weight"]), "r", env)
                v = self.arith(ex, "r", env2)
                if agg == "sum": comb = f"sum(sel(STAND, \\r: not(isnone({v}))), \\r: {v})"
                elif agg in ("min", "max"): comb = f"{agg}(STAND, \\r: {v})"
                elif agg == "median":
                    comb = (f"let VS = sel(STAND, \\r: not(isnone({v}))) in min(sel(VS, \\y: let Y = {v.replace('(r', '(y').replace('r.', 'y.')} in "
                            f"ge(mul(2, size(sel(VS, \\r: le({v}, Y)))), size(VS))), \\y: {v.replace('(r', '(y').replace('r.', 'y.')})")
                    self.gaps.append("median: read as the lower median of the multiset; the text's median of an even count is a mean")
                elif agg == "mean":
                    comb = f"let VS = sel(STAND, \\r: not(isnone({v}))) in first(eq(size(VS), 0) -> none, else -> div(sum(VS, \\r: {v}), size(VS)))"
                    self.gaps.append("mean: read as the floor of the mean (integers only); the text's mean is a fraction")
                else: self.gaps.append(f"combine {agg}")
        if "weight" in self.P and "combine" not in self.P:
            comb = f"each(STAND, \\r: {self.arith(parse_arith(self.P['weight']), 'r', env)})"
        verdict = "none"
        if "test" in self.P:
            m = re.fullmatch(r"(.+?)(>=|<=|=|>|<)(.+?) (?:!([a-z_0-9]+)|\?([a-z_]+):([a-z_]+))", self.P["test"])
            L, op, R, tok, a, b = m.groups()
            env2 = dict(env); env2["count"] = "size(STAND)"
            for nm in ("sum", "score", "voices", "yes"): env2[nm] = "first(isnone(COMB) -> size(STAND), else -> COMB)"
            lv, rv = self.arith(parse_arith(L), None, env2), self.arith(parse_arith(R), None, env2)
            cmp = {">=": "ge", "<=": "le", "=": "eq", ">": "gt", "<": "lt"}[op]
            verdict = f"first({cmp}({lv}, {rv}) -> {q('ok') if tok else q(a)}, else -> {q('refuse(' + tok + ')') if tok else q(b)})"
        absent = f"first(and(none(STAND), true) -> {q(self.P['absent'])}, else -> none)" if "absent" in self.P else "none"
        body = f"tuple(GROUPS, {order}, COMB, {verdict}, {absent}, {'N' if ov else 'none'})"
        body = body.replace("GROUPS", groups)
        expr = f"let S = {S} in let STAND = {stand} in " + (f"let N = {ov} in " if ov else "") + f"let COMB = {comb} in {body}"
        return expr


REL_KX = {"by": "eq(x.signer, T.signer)", "under": "member(T.id, x.names)", "ref": "member(T.id, x.names)",
          "about": "eq(x.subject, T.attested)", "over": "eq(x.object, T.object)"}


def ch_kx(items):
    arms = []
    for it in items:
        conds = [f"or(eq(self.verb, {q(it['on'])}), eq(self.leafname, {q(it['on'])}))"]
        for a in it["when"]:
            k, vs = a["test"], a["values"]
            setlit = "{" + ", ".join(q(v) for v in vs) + "}" if vs else None
            if vs is None: conds.append("eq(self.leafname, 'recovery')" if k == "recovery" else "ge(size(cosigners(self)), 1)" if k == "cosigned" else f"eq(self.{k}, 1)")
            elif k == "grade": conds.append(f"and(some(T), member(fld(T, 'grade'), {setlit}))")
            elif k in ("subkind", "scope", "axis"): conds.append(f"member(self.{k}, {setlit})")
            elif k == "seat": conds.append("or(" + ", ".join(f"stands(self.signer, {q(v)}, self.object)" for v in vs) + ")")
            elif k == "last": conds.append("or(" + ", ".join(f"eq(holders_in(held, {q(v)}, self.object), single(self.signer))" for v in vs) + ")")
        checks, effects, tok, word = [], [], None, "refuse"
        for c in it["clauses"]:
            k = c["clause"]
            if k == "by":
                b = c["by"]
                checks.append({"none": "true", "same_attester": "and(some(T), eq(self.signer, T.signer))",
                               "cosigned": "and(some(T), ge(size(cosigners(self)), 1))",
                               "cosigned_prior": "and(some(T), member(T.signer, cosigners(self)))",
                               "committed_key": "and(some(T), member(self.signer, T.recovery_commitments))",
                               "substrate": "and(some(T), eq(typeof(self.signer), 'node'))"}[b])
            elif k == "link": checks.append(f"and(some(T), eq(self.ref.{c['member']}, T.id))")
            elif k == "field":
                d, m = c["dir"], c["member"]
                if d in ("any", "as_attest"): checks.append("true")
                else:
                    op = {"frozen": "eq", "shrink": "le", "lower": "le"}.get(d, "ge")
                    checks.append(f"{op}(self.{m}, T.{m})")
            elif k == "reach":
                r = c["reach"]
                checks.append("true" if r in ("other_attester", "whole") else
                              "and(some(T), eq(T.signer, self.signer))" if r == "own_prior" else "lt(T.seq, self.seq)")
            elif k == "after": checks.append(f"some(sel(past(self), \\x: isfam(x, {q(c['family'])})))")
            elif k == "refuse": tok, word = c["token"], c.get("do", "refuse")
            elif k == "key": effects.append(f"single(tuple('key', {q(c['key'])}))")
            elif k == "cascade":
                fam = "true" if c["family"] == "*" else f"isfam(x, {q(c['family'])})"
                base = f"sel(held, \\x: and(some(T), ne(x.id, self.id), ne(x.id, T.id), {fam}, {REL_KX[c['rel']]}"
                if c["effect"] == "void_after":
                    effects.append(f"setof({base}, gt(x.asserted_at, T.{c['member']}))), \\x: tuple(x.id, 'void'))")
                else:
                    effects.append(f"setof({base})), \\x: tuple(x.id, {q(c['effect'])}))")
        v = q(word + "(" + tok + ")") if tok else q("refuse")
        verdict = f"first(and({', '.join(checks) or 'true'}) -> 'ok', else -> {v})"
        eff = f"union({', '.join(effects)})" if effects else "{}"
        arms.append(f"first(and({', '.join(conds)}) -> single(tuple({q(it['on'])}, {verdict}, {eff})), else -> {{}})")
    return "let T = the(named(self, 'target')) in union(" + ", ".join(arms) + ")"


CONST_DUR = 3
LAND_ROW_ALONE = ("self", "author")     # a landing by the signer of the row that opened the window: read off the two rows, no seat


def re_kx(clauses, only=None):
    """-> KX source, and the names the cell calls that no table defines."""
    lets, items, unresolved = [], [], []
    def dur(name):
        if name is None: return "none"
        if "." in name and name.split(".")[0] == "self": return f"self.{name.split('.', 1)[1]}"
        return f"cell('dur', {q(name)}, {CONST_DUR})"
    def origin(c):
        o = c.get("from")
        if o is None or o == "first_held": return "arrival(self)"
        if isinstance(o, str): return f"self.{o}"
        alts = []
        for e in o:
            if e["event"] in ("admitted", "withdrawn") and e["of"] not in ("self", "target"):
                st = f"eq(state(x), {q(e['event'])})"
                alts.append(f"and(isfam(x, {q(e['of'])}), {st})")
        return f"min(sel(held, \\x: or({', '.join(alts) or 'false'})), \\x: arrival(x))"
    def event(e):
        k, of = e["event"], e["of"]
        if k == "close": return f"and(not(isnone(C_{of})), ge(now, C_{of}))" if any(c.get("name") == of and c["kind"] == "clock" for c in clauses) else "false"
        if k == "fold": unresolved.append(f"fold({of})"); return None
        rows = "single(self)" if of == "self" else None
        src = ("sel(held, \\x: eq(x.id, self.id))" if of == "self" else "named(self, 'target')" if of == "target" else f"sel(held, \\x: and(isfam(x, {q(of)}), ne(x.id, self.id)))")
        if e.get("by") == "producer": src = f"sel({src}, \\x: eq(x.signer, self.signer))"
        if e.get("by") == "subject": src = f"sel({src}, \\x: eq(x.signer, self.subject))"
        if k in ("admitted", "withdrawn", "recanted", "superseded"): return f"some(sel({src}, \\x: eq(state(x), {q(k)})))"
        return f"some(sel({src}, \\x: eq(x.state, {q(k)})))"
    for ci, c in enumerate(clauses):
        n_items = len(items)
        guard = f"member(self.leafname, {{{', '.join(q(x) for x in c['leaves'])}}})" if c.get("leaves") else "true"
        if c.get("scope"): guard = f"and({guard}, eq(self.scope, {q(c['scope'])}))"
        if c["kind"] == "clock":
            d = f"first(not(isnone({dur(c['dur'])})) -> {dur(c['dur'])}, else -> {dur(c.get('default'))})"
            if c.get("max"): d = f"let D = {d} in first(isnone(D) -> none, else -> imin(D, {dur(c['max'])}))"
            lets.append((f"C_{c['name']}", f"first({guard} -> add({origin(c)}, {d}), else -> none)"))
            items.append(f"first({guard} -> single(tuple('clock', {q(c['name'])}, first(isnone(C_{c['name']}) -> none, ge(now, C_{c['name']}) -> 'closed', else -> 'open'))), else -> {{}})")
        elif c["kind"] == "expiry":
            m = c.get("member"); v = f"self.{m}" if m else "none"
            if c["mode"] == "none": body = "tuple('expiry', 'none')"
            elif c["mode"] == "forbidden": body = f"tuple('expiry', first(not(isnone({v})) -> 'refuse', else -> 'ok'))"
            else:
                o = origin(c) if c.get("from") else "self.asserted_at"
                end = f"first(not(isnone({v})) -> {v}, else -> {'add(O, ' + dur(c['default']) + ')' if c.get('default') else 'none'})"
                arms = []
                if c["mode"] == "required": arms.append(f"isnone({v}) -> 'refuse'")
                if c.get("eq"): arms.append(f"and(not(isnone(E)), not(isnone(O)), ne(E, add(O, {dur(c['eq'])}))) -> 'refuse'")
                if c.get("max"): arms.append(f"and(not(isnone(E)), not(isnone(O)), gt(sub(E, O), {dur(c['max'])})) -> 'refuse'")
                arms += ["isnone(E) -> 'open'", "lt(now, E) -> 'live'", "else -> 'expired'"]
                body = f"let O = {o} in let E = {end} in tuple('expiry', first({', '.join(arms)}))"
            items.append(f"first({guard} -> single({body}), else -> {{}})")
        elif c["kind"] == "land":
            late = q(c.get("late", "unstated"))        # whether an answer first held after the close still counts
            if c["concluder"] == "local": items.append(f"first({guard} -> single(tuple('land', {q(c['name'])}, 'local', {late})), else -> {{}})"); continue
            who = "eq(x.signer, self.signer)" if c["concluder"] in LAND_ROW_ALONE else f"stands(x.signer, {q(c['concluder'])}, self.object)"
            items.append(f"first({guard} -> single(tuple('land', {q(c['name'])}, some(sel(held, \\x: and(isfam(x, {q(c['landing'])}), member(self.id, x.names), live(x), {who}))), {late})), else -> {{}})")
        else:
            on = [event(e) for e in c["on"]]; un = [event(e) for e in c.get("unless", [])]
            if None in on or None in un:
                items.append(f"first({guard} -> single(tuple('react', 'unresolved')), else -> {{}})"); continue
            eff = sorted(("" if x.get("force", "must") == "must" else x["force"] + " ") + f"{x['effect']}:{x.get('family') or x.get('verdict') or x.get('act') or x.get('policy')}" for x in c["effects"])
            efft = "tuple(" + ", ".join(q(x) for x in eff) + ")"
            items.append(f"first({guard} -> single(tuple('react', owed(and(or({', '.join(on)}), not(or({', '.join(un) or 'false'}))), {efft}))), else -> {{}})")
    if only is not None: items = [items[only]]
    body = "union(" + ", ".join(items) + ")"
    for n, e in reversed(lets): body = f"let {n} = {e} in {body}"
    return body, unresolved


# Authoring words whose meaning the grammar does not state, or which this translation does not carry. A cell that
# uses one is reported `reads_dropped` with the word; it does not count as translated. The words are listed here as
# data so the list can only shrink as each gets a meaning of its own. (grammar, regex on the cell text, word, why)
DROPPED = [
    ("guard", r"\bother\(", "other(...)", "which rows are 'other' is not stated (read as another signer)"),
    ("guard", r"\bset\(ref", "set(ref:...)", "the quantifier over the named rows is not stated"),
    ("guard", r"@landed\b", "@landed", "admitted and its policy met: the policy is not read"),
    ("guard", r"\bafter\(", "after(POLICY)", "which instant the window runs from is not stated"),
    ("guard", r"\bwithin\(", "within(POLICY)", "which instant the window runs from is not stated"),
    ("guard", r"via=delegates_to", "via=delegates_to", "the delegation walk is not translated"),
    ("fold", r"@(decision|count|seating|prior|close|act|founding)\b", "@INSTANT", "the grammar does not say which head or instant"),
    ("fold", r"over=[a-z_]+(?:/[a-z]+)?(?:;|$)", "over without an instant", "the cell does not say which head or instant"),
    ("fold", r"\b(narrow_only|drop_only)\(", "BOUND", "the order a narrowing or a drop is judged in is not stated"),
    ("fold", r"cut=[a-z_(),]*\bwhole\b", "cut=whole", "not implemented"),
    ("fold", r"pick=set\b", "pick=set", "not told apart from union"),
    ("fold", r"combine=policy\(", "combine=policy(...)", "the tally of the policy row is not called"),
    ("change", r"/(about|over|under):", "cascade REL", "which rows stand in this relation to the changed row is not stated"),
    ("change", r"link=(ranked|chained):", "link=ranked:/chained:", "the rank or chain the link implies is not read"),
    ("change", r":(shrink|grow_signed|no_weaker|as_attest)\b", "field DIR", "set inclusion, the signed growth, the protocol order or the attest guard is not read"),
    ("change", r"reach=whole", "reach=whole", "every version is reached: not read"),
    ("change", r"by=cosigned\b(?!_)", "by=cosigned", "the count of cosigners is the family's count arm: not called"),
    ("change", r"\b(entrenched|ephemeral|stalled)\b", "ATOM", "a property of the group, not of the row: not read"),
    ("reaction", r" by (receipt|signed|origin_door)\b", "by JUDGE", "who judges the clock is not read"),
    ("reaction", r"\b(purged|matched|sealed|refused)\(", "EVENT", "the state has no row that states it"),
    ("reaction", r"[^;]*\bfold\([^;]*", "fold(NAME)", "no cell defines the fold: the whole clause is dropped"),
]
LABEL_PARTS = {"fold": r"\b(by|result|feeds)=[A-Za-z_.:*{},|()]+"}   # who runs the fold, its shape, its readers: carried, not evaluated


def dropped_words(grammar, text):
    out = []
    for g, rx, word, why in DROPPED:
        if g != grammar: continue
        for m in re.finditer(rx, text):
            w = word
            if "INSTANT" in word or word in ("BOUND", "cascade REL", "field DIR", "ATOM", "by JUDGE", "EVENT"): w = m.group(0).strip()
            out.append((w, why))
    return sorted(set(out))


def dropped_spans(grammar, text):
    return [m.span() for g, rx, _, _ in DROPPED if g == grammar for m in re.finditer(rx, text)]


def label_words(grammar, text):
    rx = LABEL_PARTS.get(grammar)
    return sorted(set(m.group(0) for m in re.finditer(rx, text))) if rx else []


COUNT_KEYS = {"leaf": "self.leafname", "verb": "self.verb", "identity": "typeof(self.attested)", "group": "self.group", "seats": "self.seats"}


def door_kx(d):
    md = re.fullmatch(r"(none|shut)|([a-z_]+)(?:@([a-z_]+))?(?:!(confers|result))?", d)
    if md.group(1): return q(md.group(1))
    return f"tuple('tally', {q(md.group(2))}, {q(md.group(3) or '')}, {q(md.group(4) or '')})"


def count_kx(arms):
    """arms: [{selector, doors}] in order; the first whose selector holds decides."""
    out = []
    for a in arms:
        if a["selector"] == "*": out.append(f"else -> {door_kx(a['doors'])}"); continue
        tests = []
        for t in a["selector"].split(" & "):
            k, vs = t.split("=")
            tests.append(f"member({COUNT_KEYS[k]}, {{{', '.join(q(v) for v in vs.split('|'))}}})")
        out.append(f"and({', '.join(tests)}) -> {door_kx(a['doors'])}")
    if not any(x.startswith("else") for x in out): out.append("else -> 'none'")
    return f"first({', '.join(out)})"


def policy_call(f):
    """A governance policy row whose enact cell is a fraction, as a call of tally2 (kx_prelude.kx); None otherwise."""
    if not (isinstance(f.get("enact"), dict) and "num" in f["enact"]): return None
    e = f["enact"]; c = f.get("cancel") if isinstance(f.get("cancel"), dict) and "num" in f.get("cancel", {}) else {"num": 0, "den": 0}
    fl = f.get("floor") if isinstance(f.get("floor"), dict) and "num" in f.get("floor", {}) else {"num": 0, "den": 0}
    mc = 1 if f.get("corridor") == "self" else 2
    return (f"tally2({e['num']}, {e['den']}, {c['num']}, {c['den']}, {fl['num']}, {fl['den']}, {mc}, {f['window_secs']}, "
            f"{'true' if f['irreversible'] else 'false'}, {'true' if f['reverse_path'] else 'false'}, BASE, A, O, EL)")


def fill_call(call, base, a, o, el):
    return call.replace("BASE, A, O, EL)", f"{base}, {a}, {o}, {el})")


COUNTED_AT = {"named": "past(self)", "signed": "sel(held, \\x: le(x.asserted_at, self.asserted_at))",
              "act": "sel(held, \\x: le(x.asserted_at, fld(the(named(self, 'act')), 'asserted_at')))",
              "founding": "past(the(named(self, 'founding')))"}


COUNT_SET_LESS = {"target": "single(self.target)", "proposer": "single(self.signer)"}
COUNT_SET_SEATS = ("member", "self", "holder", "operator", "wa", "moderate", "review", "founder", "custodian", "owner", "steward")


def count_set_kx(value):
    """Who a policy row counts, by its count_set cell (formal/derivation/policy_text.tsv): the keys seated in each role
    the cell names, over the roster the row extends, less the party the cell leaves out. None where the cell names a
    set no seat gives: `protocol` (the group's declared kind), a role that is no seat token, or `-node`."""
    m = re.fullmatch(r"([a-z_:]+(?:\+[a-z_:]+)*)(?:-([a-z]+))?", value)
    if not m or any(r not in COUNT_SET_SEATS for r in m.group(1).split("+")) or (m.group(2) and m.group(2) not in COUNT_SET_LESS): return None
    sets = [f"holders_in(past(self), {q(r)}, self.object)" for r in m.group(1).split("+")]
    s = sets[0] if len(sets) == 1 else f"union({', '.join(sets)})"
    return f"diff({s}, {COUNT_SET_LESS[m.group(2)]})" if m.group(2) else s


def counted_at_kx(value):
    """The set a policy row counts over, by its counted_at cell (formal/derivation/policy_text.tsv)."""
    return f"size(holders_in({COUNTED_AT[value]}, 'member', self.object))"
