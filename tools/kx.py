r"""
KX: one expression language for every rule cell of the five grammars (tools/kx_translate.py writes them into it;
tools/kx_check.py holds each translation to its original). The interpreter is a set of calls on
formal/kernel_lib/kernel_lib.py; the layer of a cell and its type errors are computed, not declared.

FIELD TYPES   formal/derivation/kx_field_types.tsv gives every member a cell reads a type: signed_instant,
digest, key, set or value. A cell that orders rows by a signed_instant or a digest, or compares the
signed_instants of two different rows, carries a type error (ORDER_BY_SIGNED_INSTANT, ORDER_BY_DIGEST,
CROSS_SIGNER_INSTANT); a member with no row in the table is UNTYPED.

GRAMMAR (ABNF; SP and whitespace between tokens elided)

    program = *( def )
    def     = "def" name "(" [ name *( "," name ) ] ")" "=" expr
    expr    = "let" name "=" expr "in" expr
            / "first" "(" arm *( "," arm ) ")"          ; the first arm whose test holds; "else" is the last
            / "\" name ":" expr                         ; a row lambda, only as an argument of sel/every/each/val/least
            / name "(" [ expr *( "," expr ) ] ")"       ; an operator or a def
            / path / INT / STR / "{" [ STR *( "," STR ) ] "}"
    arm     = ( expr / "else" ) "->" expr
    path    = name *( "." name )                        ; r.signer  r.val.x  r.ref.x  r.leaf.x

TYPES   Rows (a set of rows) | Row | Key | Val (int, string, set of strings) | Instant | Verdict | Bool.
        Instants carry a provenance: signed(row var) | arrival | now.

SOURCES (the only expressions that yield rows; the layer of a cell is the greatest source it reaches)
    self              Row     the row judged                              kept
    past(r)           Rows    the rows r names, through others (+ r)      concluded   K.past over K.closure
    named(r, 'f')     Rows    the row r names in field f                  concluded   sel(past(r), id = r.ref.f)
    held              Rows    every row the node holds                    derived
    now               Instant                                             derived + NOW
    arrival(r)        Instant the instant the node first held r           ARRIVAL: not a function of the set

OPERATORS (each a call on formal/kernel_lib/kernel_lib.py, or integer/boolean glue)
    sel(S, \r: p)                       K.sel (field = constant patterns) then the residual predicate
    least(S, \r: v) greatest(S, \r: v)  K.group(by=None, 'least'|'greatest', val): Tie -> 'tie'
    group(S, \r: k, how, \r: v)         K.group(by=k, how in least greatest min max one count sum, val=v); a map
    count(S, \r: v) sum(S, \r: v, \r: per) one(S, \r: v) min(S,\r:v) max(S,\r:v)   K.group(None, ...)
    in(x, lo, hi)                       K.in_range
    cell('table', k)                    K.rule
    walk(\x: step, init, bound)          K.fix
    conc(a, b)  front(S)                K.concurrent  K.frontier
    glue: and or not eq ne lt le gt ge add sub mul div(floor) cdiv imax imin member has isfam some none every
          size ids each(S|list, \x: e) setof tuple typeof check(cond, verdict) ok
    verdicts: refuse wait void contested exclude withhold advise   (each with an optional token)
"""
import csv, importlib.util, inspect, os, re, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
CODE_ROOT = os.path.dirname(HERE)
K = None
FIELD_TYPES = {}
EXT = {}          # which kernel_lib additions are present: sel(where=), group(val=callable), the()


def find(root, rel):
    """A file of the repository: next to this tool first (a port carries its own tables), else under root."""
    p = os.path.join(CODE_ROOT, rel)
    return p if os.path.exists(p) else os.path.join(root, rel)


def use_root(root, kernel=None):
    """Load kernel_lib (or the file `kernel`) and the field-type table of the repository at `root`."""
    global K
    spec = importlib.util.spec_from_file_location("kernel_lib", kernel or find(root, "formal/kernel_lib/kernel_lib.py"))
    K = importlib.util.module_from_spec(spec); spec.loader.exec_module(K)
    EXT["where"] = "where" in inspect.signature(K.sel).parameters
    EXT["callable_val"] = getattr(K, "COMPUTED_VALUES", False)
    EXT["the"] = hasattr(K, "the")
    FIELD_TYPES.clear()
    path = find(root, "formal/derivation/kx_field_types.tsv")
    if not os.path.exists(path): return K
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader((l for l in f if not l.startswith("#")), delimiter="\t"):
            FIELD_TYPES[row["member"]] = row["type"]
    return K

# ------------------------------------------------------------------ lexer / parser
TOK = re.compile(r"\s*(?:(->)|(\\)|([A-Za-z_][A-Za-z_0-9]*)|(-?\d+)|('[^']*')|(.))")


def lex(s):
    out, i = [], 0
    while i < len(s):
        m = TOK.match(s, i)
        if not m or m.end() == i:
            if s[i:].strip() == "": break
            raise SyntaxError(s[i:i + 20])
        i = m.end()
        a, b, n, d, q, c = m.groups()
        if a: out.append(("op", "->"))
        elif b: out.append(("op", "\\"))
        elif n: out.append(("name", n))
        elif d: out.append(("int", int(d)))
        elif q: out.append(("str", q[1:-1]))
        elif c and c.strip(): out.append(("op", c))
    return out


class P:
    def __init__(self, s): self.t = lex(s); self.i = 0
    def peek(self, k=0): return self.t[self.i + k] if self.i + k < len(self.t) else ("eof", None)
    def take(self, v=None):
        x = self.peek()
        if v is not None and x[1] != v: raise SyntaxError(f"want {v} got {x} at {self.i}: {self.t[max(0,self.i-6):self.i+4]}")
        self.i += 1; return x

    def program(self):
        defs = {}
        while self.peek()[0] != "eof":
            self.take("def"); name = self.take()[1]; self.take("(")
            params = []
            while self.peek()[1] != ")":
                params.append(self.take()[1])
                if self.peek()[1] == ",": self.take(",")
            self.take(")"); self.take("="); defs[name] = (params, self.expr())
        return defs

    def expr(self):
        k, v = self.peek()
        if v == "let" and k == "name":
            self.take(); n = self.take()[1]; self.take("="); e = self.expr(); self.take("in")
            return ("let", n, e, self.expr())
        if v == "first" and k == "name" and self.peek(1)[1] == "(":
            self.take(); self.take("("); arms = []
            while True:
                if self.peek()[1] == "else": self.take(); c = ("else",)
                else: c = self.expr()
                self.take("->"); arms.append((c, self.expr()))
                if self.peek()[1] == ",": self.take(","); continue
                self.take(")"); return ("first", arms)
        if v == "\\":
            self.take(); n = self.take()[1]; self.take(":"); return ("lam", n, self.expr())
        if k == "int": self.take(); return ("lit", v)
        if k == "str": self.take(); return ("lit", v)
        if v == "{":
            self.take(); xs = []
            while self.peek()[1] != "}":
                xs.append(self.take()[1])
                if self.peek()[1] == ",": self.take(",")
            self.take("}"); return ("lit", frozenset(xs))
        if k == "name":
            self.take()
            if self.peek()[1] == "(":
                self.take("("); args = []
                while self.peek()[1] != ")":
                    args.append(self.expr())
                    if self.peek()[1] == ",": self.take(",")
                self.take(")"); return ("call", v, args)
            path = [v]
            while self.peek()[1] == "." and self.peek(1)[0] == "name":
                self.take("."); path.append(self.take()[1])
            return ("path", path)
        raise SyntaxError(f"unexpected {self.peek()} at {self.i}")


def parse(s):
    p = P(s); e = p.expr()
    if p.peek()[0] != "eof": raise SyntaxError(f"trailing {p.t[p.i:p.i+5]}")
    return e


def parse_program(s):
    """Definitions; a line whose first non-blank character is # is a comment."""
    return P("\n".join(l for l in s.splitlines() if not l.lstrip().startswith("#"))).program()


OPS = {"sel", "least", "greatest", "group", "count", "sum", "one", "min", "max", "in", "cell", "walk", "conc", "front",
       "past", "named", "held", "now", "arrival", "and", "or", "not", "eq", "ne", "lt", "le", "gt", "ge", "add", "sub",
       "mul", "div", "cdiv", "imax", "imin", "member", "has", "isfam", "some", "none", "every", "size", "ids", "each",
       "setof", "tuple", "typeof", "check", "ok", "refuse", "wait", "void", "contested", "exclude", "withhold", "advise",
       "union", "neg", "mapv", "cosigners", "elems", "single", "the", "verdicts", "diff", "heldnames", "fld", "meets", "add_str", "lt_tuple", "isnone"}
VERDICTS = ("refuse", "wait", "void", "contested", "exclude", "withhold", "advise")

# ------------------------------------------------------------------ static analysis: layer and exposures
LAYER = {"kept": 0, "concluded": 1, "derived": 2}
STRUCTURAL = {"self", "held", "now", "none", "true", "false"}


def ftype(path):
    """The type of the member a path reads: a member of `ref` is a digest by construction."""
    if len(path) >= 3 and path[-2] == "ref": return "digest"
    return FIELD_TYPES.get(path[-1])


class Info:
    __slots__ = ("layer", "flags")
    def __init__(self, layer=0, flags=()): self.layer, self.flags = layer, set(flags)
    def join(self, o): self.layer = max(self.layer, o.layer); self.flags |= o.flags; return self


def analyse(e, defs, env=None, depth=0):
    """-> Info. env maps a variable to the Info of what it ranges over (rows) or is bound to."""
    env = env or {}
    t = e[0]
    if t == "lit": return Info()
    if t == "path":
        h = e[1][0]
        untyped = len(e[1]) >= 2 and ftype(e[1]) is None
        i = _path_info(h, env)
        if untyped: i.flags.add("UNTYPED:" + e[1][-1])
        return i
    if t == "__never__":
        if h == "self": i = Info(0)
        elif h == "held": i = Info(2)
        elif h == "now": i = Info(2, {"NOW"})
        elif h in env: i = Info(env[h].layer, env[h].flags)
        else: i = Info()
        return i
    if t == "let":
        a = analyse(e[2], defs, env, depth)
        return analyse(e[3], defs, {**env, e[1]: a}, depth)
    if t == "first":
        i = Info()
        for c, v in e[1]:
            if c != ("else",): i.join(analyse(c, defs, env, depth))
            i.join(analyse(v, defs, env, depth))
        return i
    if t == "lam":
        return analyse(e[2], defs, env, depth)
    name, args = e[1], e[2]
    if name in ("past", "named"):
        i = Info(1); [i.join(analyse(a, defs, env, depth)) for a in args]; i.layer = max(i.layer, 1); return i
    if name == "heldnames":
        i = Info(0); [i.join(analyse(a, defs, env, depth)) for a in args]; return i
    if name == "arrival":
        i = Info(0, {"ARRIVAL"}); [i.join(analyse(a, defs, env, depth)) for a in args]; return i
    if name in ("sel", "least", "greatest", "group", "count", "sum", "one", "min", "max", "every", "each", "mapv", "setof"):
        src = analyse(args[0], defs, env, depth) if args else Info()
        i = Info(src.layer, src.flags)
        for a in args[1:]:
            if a[0] == "lam": i.join(analyse(a[2], defs, {**env, a[1]: src}, depth))
            else: i.join(analyse(a, defs, env, depth))
        if name in ("least", "greatest") or (name == "group" and len(args) > 2 and args[2] in (("lit", "least"), ("lit", "greatest"))):
            vl = args[-1] if name != "group" else args[3]
            for p in paths_of(vl):
                if ftype(p) == "signed_instant": i.flags.add("ORDER_BY_SIGNED_INSTANT")
                elif ftype(p) in ("digest", "key"): i.flags.add("ORDER_BY_DIGEST")     # a key id is the digest of a key
        return i
    if name in ("lt", "le", "gt", "ge", "in", "eq", "ne") and depth < 50:
        i = Info()
        for a in args: i.join(analyse(a, defs, env, depth))
        owners = set()
        for a in args: owners |= signed_owners(a)
        if len(owners) >= 2: i.flags.add("CROSS_SIGNER_INSTANT")
        return i
    if name in ("div",) and len(args) == 2 and args[1][0] == "lit" and args[1][1] not in (1,):
        pass
    if name in ("mean", "median", "rate", "fdiv"):
        i = Info(0, {"FLOAT"}); [i.join(analyse(a, defs, env, depth)) for a in args]; return i
    i = Info()
    for a in args: i.join(analyse(a, defs, env, depth))
    if name in ("fld", "has") and len(args) == 2 and args[1][0] == "lit" and FIELD_TYPES.get(args[1][1]) is None:
        i.flags.add("UNTYPED:" + args[1][1])
    if name in defs and depth < 6:
        params, body = defs[name]
        sub = {p: analyse(a, defs, env, depth) for p, a in zip(params, args)}
        i.join(analyse(body, defs, sub, depth + 1))
    elif name not in OPS and name not in defs:
        i.flags.add("UNKNOWN_OP:" + name)
    return i


def _path_info(h, env):
    if h == "self": return Info(0)
    if h == "held": return Info(2)
    if h == "now": return Info(2, {"NOW"})
    if h in env: return Info(env[h].layer, env[h].flags)
    return Info()


def signed_owners(e):
    """Row variables whose signed instants an expression reads."""
    out = set()
    def w(x):
        if not isinstance(x, tuple) or not x: return
        if x[0] == "path":
            if len(x[1]) >= 2 and ftype(x[1]) == "signed_instant" and x[1][0] not in ("now",): out.add(x[1][0])
            return
        if x[0] == "call" and x[1] == "arrival": return
        for y in x[1:]:
            if isinstance(y, tuple): w(y)
            elif isinstance(y, list): [w(z) for z in y]
    w(e); return out


def paths_of(e):
    out = []
    def w(x):
        if isinstance(x, tuple):
            if x and x[0] == "path" and len(x[1]) >= 2: out.append(x[1])
            for y in x[1:]:
                if isinstance(y, (tuple, list)): w(y) if isinstance(y, tuple) else [w(z) for z in y]
    w(e); return out


def fields_of(e):
    out = []
    def w(x):
        if isinstance(x, tuple):
            if x and x[0] == "path" and len(x[1]) >= 2: out.append(x[1][-1])
            for y in x[1:]:
                if isinstance(y, (tuple, list)): w(y) if isinstance(y, tuple) else [w(z) for z in y]
    w(e); return out


def layer_name(i):
    return {0: "kept", 1: "concluded", 2: "derived"}[i.layer]


# ------------------------------------------------------------------ interpreter
class Tie_(Exception): pass


def getf(r, path):
    """r.f -> top-level, else val; r.val.f / r.ref.f / r.leaf.f explicit."""
    if r is None: return None
    x = r
    for i, p in enumerate(path):
        if isinstance(x, dict):
            if p in x: x = x[p]
            elif i == 0 and isinstance(x.get("val"), dict) and p in x["val"]: x = x["val"][p]
            else: return None
        else: return None
    return x


def fam_match(fam, pats):
    if fam is None: return False
    fs = fam.split(":")
    for p in pats.split("|"):
        if p == "*": return True
        ps = p.split(":")
        ok = True
        for i, s in enumerate(ps):
            if s == "*": break
            if i >= len(fs): ok = False; break
            if s.startswith("{") or s == fs[i]: continue
            ok = False; break
        else:
            ok = ok and len(fs) == len(ps)
        if ok: return True
    return False


def typeof(k):
    if not isinstance(k, str) or not k: return None
    return {"n": "node", "u": "user", "g": "agent"}.get(k[0], "user")


class Ev:
    def __init__(self, defs, held, self_row, now=100, tables=None):
        self.defs, self.held, self.self_row, self.now = defs, held, self_row, now
        self.tables = tables or {}
        self.anc = K.closure(held + ([self_row] if self_row and self_row not in held else []))
        self.byid = {r["id"]: r for r in held}
        if self_row: self.byid.setdefault(self_row["id"], self_row)
        self.memo = {}

    def run(self, e, env=None):
        return self.ev(e, env or {})

    def ev(self, e, env):
        t = e[0]
        if t == "lit": return e[1]
        if t == "path":
            h, rest = e[1][0], e[1][1:]
            if h == "self": base = self.self_row
            elif h == "held": return self.held
            elif h == "now": return self.now
            elif h in env: base = env[h]
            elif h == "none": return None
            elif h == "true": return True
            elif h == "false": return False
            else: return h if not rest else None   # a bare word is a constant
            return getf(base, rest) if rest else base
        if t == "let":
            return self.ev(e[3], {**env, e[1]: self.ev(e[2], env)})
        if t == "first":
            for c, v in e[1]:
                if c == ("else",) or self.ev(c, env): return self.ev(v, env)
            return None
        if t == "lam": return (e, env)
        return self.call(e[1], e[2], env)

    def lam(self, f, x):
        (_, n, body), env = f
        return self.ev(body, {**env, n: x})

    def call(self, name, args, env):
        ev = lambda a: self.ev(a, env)
        if name in self.defs:
            params, body = self.defs[name]
            vals = [ev(a) for a in args]
            key = (name, tuple(_hashable(v) for v in vals))
            if key in self.memo: return self.memo[key]
            self.memo[key] = None                      # a recursive call reads none (bounded walk handles depth)
            out = self.ev(body, dict(zip(params, vals)))
            self.memo[key] = out; return out
        if name == "and":
            for a in args:
                if not ev(a): return False
            return True
        if name == "or":
            for a in args:
                if ev(a): return True
            return False
        if name == "check":
            return "ok" if ev(args[0]) else ev(args[1])
        v = [ev(a) for a in args]
        if name == "not": return not v[0]
        if name in ("eq", "ne"):
            r = v[0] == v[1] and v[0] is not None if name == "eq" else not (v[0] == v[1] and v[0] is not None)
            return r
        if name in ("lt", "le", "gt", "ge"):
            a, b = v
            if a is None or b is None: return False
            return {"lt": a < b, "le": a <= b, "gt": a > b, "ge": a >= b}[name]
        if name in ("add", "sub", "mul", "div", "cdiv"):
            a, b = v
            if a is None or b is None: return None
            if name == "add": return a + b
            if name == "sub": return a - b
            if name == "mul": return a * b
            if name == "div": return a // b
            return (a + b - 1) // b
        if name == "neg": return None if v[0] is None else -v[0]
        if name == "imax": vs = [x for x in v if x is not None]; return max(vs) if vs else None
        if name == "imin": vs = [x for x in v if x is not None]; return min(vs) if vs else None
        if name == "member":
            x, s = v
            return isinstance(s, (set, frozenset, list, tuple)) and x is not None and x in s
        if name == "has": return getf(v[0], [v[1]]) is not None
        if name == "isfam": return v[0] is not None and fam_match(v[0].get("fam"), v[1])
        if name == "typeof": return typeof(v[0])
        if name == "some": return bool(v[0])
        if name == "none": return not v[0]
        if name == "size": return len(v[0]) if v[0] is not None else 0
        if name == "ids": return frozenset(r["id"] for r in v[0])
        if name == "setof": return frozenset(x for x in (self.lam(v[1], r) for r in v[0]) if x is not None)
        if name == "union": return frozenset().union(*[x or frozenset() for x in v])
        if name == "tuple": return tuple(v)
        if name == "meets": return bool(frozenset(v[0] or ()) & frozenset(v[1] or ()))
        if name == "fld": return getf(v[0], [v[1]]) if isinstance(v[0], dict) else None
        if name == "single": return frozenset() if v[0] is None else frozenset([v[0]])
        if name == "diff": return frozenset(v[0] or ()) - frozenset(v[1] or ())
        if name == "heldnames": return frozenset(i for i in (v[0] or {}).get("names", ()) if i in self.byid and i != v[0]["id"])
        if name == "the":
            if EXT.get("the"): return K.the(v[0])
            g = K.group([r for r in v[0]], None, "one", "id")
            return self.byid.get(g) if g is not None else None
        if name == "verdicts":
            out = set()
            for x in v:
                _flat(x, None, out)
            return frozenset(out)
        if name == "ok": return "ok"
        if name in VERDICTS: return name + ("(" + v[0] + ")" if v else "")
        if name == "cell":
            return K.rule(self.tables.get(v[0], {}), v[1], v[2] if len(v) > 2 else None)
        if name == "isnone": return v[0] is None
        if name == "add_str": return None if v[0] is None or v[1] is None else str(v[0]) + str(v[1])
        if name == "lt_tuple":
            a, b = v
            if a is None or b is None or None in a or None in b: return False
            return a < b
        if name == "past":
            r = v[0]
            if r is None: return []
            return [x for x in K.past(self.held, self.anc, r["id"], inclusive=False) if x["id"] != r["id"]]
        if name == "named":
            r, f = v
            if r is None: return []
            rid = (r.get("ref") or {}).get(f)
            if f == "*": return [x for x in self.held if x["id"] in r.get("names", ())]
            return [x for x in self.held if x["id"] == rid]
        if name == "arrival": return None if v[0] is None else v[0]["t"]
        if name == "cosigners": return v[0].get("cosig", frozenset()) if v[0] else frozenset()
        if name == "elems":
            x = getf(v[0], [v[1]]) if v[0] else None
            if x is None: return []
            return sorted(x) if isinstance(x, (set, frozenset, list, tuple)) else [x]
        if name == "sel":
            S, f = v
            pat, rest = _split_pattern(f)
            if EXT.get("where"): return K.sel(S, where=lambda r: self.lam(f, r), **pat)
            base = K.sel(S, **pat) if pat else list(S)
            return [r for r in base if self.lam(f, r)] if rest else base
        if name in ("least", "greatest", "count", "sum", "one", "min", "max"):
            S, f = v[0], v[1]
            if EXT.get("callable_val"):
                vf = lambda r: self.lam(f, r)
                if name == "sum":
                    per = v[2] if len(v) > 2 else None
                    return K.group(S, None, "sum", vf, per=(lambda r: self.lam(per, r)) if per else "id")
                ok = lambda x: x is not None and not (isinstance(x, tuple) and None in x)
                rows = [r for r in S if ok(vf(r))]
                try:
                    return K.group(rows, None, name, vf)
                except K.Tie:
                    return "tie"
            rows = [dict(r, _v=self.lam(f, r)) for r in S]
            if name == "sum":
                per = v[2] if len(v) > 2 else None
                for r, x in zip(rows, S): r["_p"] = self.lam(per, x) if per else x["id"]
                return K.group(rows, None, "sum", "_v", per="_p")
            rows = [r for r in rows if r["_v"] is not None and not (isinstance(r["_v"], tuple) and None in r["_v"])] if name in ("min", "max", "least", "greatest", "one", "count") else rows
            try:
                g = K.group(rows, None, name, "_v")
            except K.Tie:
                return "tie"
            if name in ("least", "greatest") and isinstance(g, dict):
                return self.byid.get(g["id"], {k: x for k, x in g.items() if k != "_v"})
            return g
        if name == "group":
            S, kf, how, vf = v
            rows = [dict(r, _k=self.lam(kf, r), _v=self.lam(vf, r)) for r in S]
            out = {}
            for k in {r["_k"] for r in rows}:
                sub = [r for r in rows if r["_k"] == k]
                try:
                    g = K.group(sub, None, how, "_v")
                except K.Tie:
                    g = "tie"
                if isinstance(g, dict): g = g["id"]
                out[k] = g
            return out
        if name == "mapv":
            return {k: self.lam(v[1], x) for k, x in v[0].items()}
        if name == "every":
            return all(self.lam(v[1], r) for r in v[0])
        if name == "each":
            return tuple(sorted(((_hashable(x), _hashable(self.lam(v[1], x))) for x in v[0]), key=repr))
        if name == "in": return K.in_range(*v)
        if name == "walk":
            f, init, bound = v
            return K.fix(lambda s: self.lam(f, s), init, bound)
        if name == "conc": return K.concurrent(self.anc, v[0]["id"], v[1]["id"])
        if name == "front": return K.frontier(self.anc, v[0])
        raise NameError(name)


def _flat(x, elem, out):
    if x is None or x == "ok": return
    if isinstance(x, str): out.add((elem, x)); return
    if isinstance(x, frozenset):
        for e, y in x: out.add((elem if e is None else e, y))
        return
    if isinstance(x, tuple):           # from each: ((elem, value), ...)
        for e, y in x: _flat(y, e, out)
        return
    raise TypeError(x)


def _split_pattern(f):
    """A lambda whose body is and(eq(r.F, 'const'), ...) gives K.sel a pattern for those conjuncts."""
    (_, n, body), env = f
    conj = body[2] if body[0] == "call" and body[1] == "and" else [body]
    pat, rest = {}, False
    for c in conj:
        if c[0] == "call" and c[1] == "eq" and c[2][0][0] == "path" and c[2][0][1][0] == n and len(c[2][0][1]) == 2 \
                and c[2][1][0] == "lit" and c[2][0][1][1] in ("verb", "signer", "object", "attested", "fam"):
            pat[c[2][0][1][1]] = c[2][1][1]
        else:
            rest = True
    if pat: rest = True  # residual check keeps None-semantics identical; the pattern narrows first
    return pat, rest


def _hashable(x):
    if isinstance(x, dict):
        if "id" in x and "fam" in x: return ("row", x["id"])
        return tuple(sorted((repr(k), _hashable(v)) for k, v in x.items()))
    if isinstance(x, list): return tuple(sorted((_hashable(y) for y in x), key=repr))
    if isinstance(x, set): return frozenset(x)
    return x
