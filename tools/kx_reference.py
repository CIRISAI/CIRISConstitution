"""
KX reference readings: what each grammar's cells mean, evaluated directly over the parse tree each grammar's own
tool returns. Four of the five grammars have a parser and no evaluator in the repository; these readings are the
first executable meaning their cells have, and tools/kx_check.py holds every KX translation to them. Where a
grammar is silent the reading chooses, and the choice is stated beside the code. The policy has an evaluator of
its own (tools/build_governance_policy.py decide()), which the check uses instead.

Also the row generators the check runs both sides on. Nothing here imports tools/kx.py.
"""
import itertools, random, re
from kx_translate import parse_arith, split_top, VERB_RANK, ROW_READ, UNITS, NeedsOperator, ROW_ALONE_ROLES, CONST_DUR


def getf(r, path):
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
        ps = p.split(":"); ok = True
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


def ref_state(S, r):
    def by(v): return any(q.get("verb") == v and r["id"] in q.get("names", ()) and q.get("signer") == r.get("signer") for q in S)
    if by("recant"): return "recanted"
    if by("withdraw"): return "withdrawn"
    if by("replace"): return "superseded"
    return "admitted"


def ref_stands(S, k, role, obj):
    def offers(rl):
        return [o for o in S if fam_match(o["fam"], "seat:offer") and (o.get("val") or {}).get("role") == rl and o.get("object") == obj and ref_state(S, o) == "admitted"]
    def acc(o):
        return any(fam_match(a["fam"], "seat:accept") and a.get("signer") == o.get("attested") and o["id"] in a.get("names", ()) and ref_state(S, a) == "admitted" for a in S)
    C = {obj}
    for _ in range(4):
        n = C | {o["attested"] for o in offers("confer") if o["signer"] in C and acc(o)}
        if n == C: break
        C = n
    return k in {o["attested"] for o in offers(role) if o["signer"] in C and acc(o)}


def ref_past(S, r):
    by = {x["id"]: x for x in S}
    seen, todo = set(), list(r.get("names", ()))
    while todo:
        i = todo.pop()
        if i in seen: continue
        seen.add(i)
        if i in by: todo += list(by[i].get("names", ()))
    return [x for x in S if x["id"] in seen]


KEYS = ["u1", "u2", "n1"]


OBJS = ["o1", "o2"]


def fill(pat, rnd):
    """A concrete family string from a pattern: placeholders get a value, a trailing * a segment."""
    segs = []
    for s in pat.split(":"):
        if s == "*": segs.append(rnd.choice(["a", "b"])); break
        segs.append(rnd.choice(["v", "w"]) if s.startswith("{") else s)
    return ":".join(segs)


def seat_rows(rnd, nid, roles, objs, keys):
    """offer + accept rows that seat some keys in some roles, conferred by the object key."""
    out = []
    for _ in range(rnd.randint(0, 2)):
        role = rnd.choice(roles); obj = rnd.choice(objs); k = rnd.choice(keys)
        oid = f"s{nid[0]}"; nid[0] += 1
        out.append({"id": oid, "fam": "seat:offer", "verb": "attest", "signer": obj if rnd.random() < .8 else rnd.choice(keys),
                    "attested": k, "object": obj, "val": {"role": role}, "names": frozenset(), "asserted_at": rnd.randint(0, 3), "ref": {}})
        if rnd.random() < .8:
            aid = f"s{nid[0]}"; nid[0] += 1
            out.append({"id": aid, "fam": "seat:accept", "verb": "attest", "signer": k, "attested": k, "object": obj, "val": {},
                        "names": frozenset([oid]), "asserted_at": rnd.randint(0, 3), "ref": {"offer": oid}})
    return out


def orders(rows, cap=None):
    import itertools
    perms = itertools.permutations(range(len(rows)))
    for n, p in enumerate(perms):
        if cap and n >= cap: break
        yield [dict(r, t=p[i]) for i, r in enumerate(rows)]


def slot_val(slot, row, bind, selfrow):
    """slot {'slot','arg','of'}: of = a bound name (A) or None (the candidate row on the left, self on the right)."""
    k, a = slot["slot"], slot["arg"]
    if k == "key": return bind.get("key")
    if k == "const": return a
    if row is None: return None
    if k == "ref":
        return frozenset(row.get("names", ())) if a == "*" else (row.get("ref") or {}).get(a)
    if k == "val": return getf(row, [a])
    if k == "leaf": return (row.get("leaf") or {}).get(a)
    return row.get(k)


def keyarg(s, bind, selfrow):
    m = re.fullmatch(r"(?:([A-Z])\.)?(.+)", s)
    who, body = m.group(1), m.group(2)
    row = bind.get(who) if who else selfrow
    if body == "key": return bind.get("key")
    if body.startswith("val:"): return getf(row, [body[4:]]) if row else None
    if body.startswith("ref:"): return (row.get("ref") or {}).get(body[4:]) if row else None
    if body in ("signer", "subject", "attested", "object"): return row.get(body) if row else None
    return body          # a literal target: federation, ...


def digest_source(joins):
    """A join id=ref:X or id=N.ref:X finds its row by a digest: (owner name or None, field)."""
    for j in joins:
        if j["op"] == "=" and j["left"]["slot"] == "id" and j["right"]["slot"] == "ref":
            return j["right"]["of"], j["right"]["arg"]
    return None


class Ref:
    def __init__(self, held, selfrow, now, policy):
        self.held, self.self, self.now, self.policy = held, selfrow, now, policy

    def cands(self, a, bind):
        S = self.held
        src = digest_source(a["joins"])
        if a["quant"].startswith("set("):
            f = a["quant"][4:-1].split(":", 1)[1]
            S = [x for x in S if (x["id"] in self.self.get("names", ()) if f == "*" else x["id"] == (self.self.get("ref") or {}).get(f))]
        elif a["state"] == "named":
            S = ref_past(self.held, self.self)
        elif src:
            who, f = src
            base = bind.get(who) if who else self.self
            S = [] if base is None else [x for x in S if (x["id"] in base.get("names", ()) if f == "*" else x["id"] == (base.get("ref") or {}).get(f))]
        fs = a["families"]
        out = []
        for r in S:
            if r["id"] == self.self["id"]: continue
            if "of" in fs and not fam_match(r["fam"], "|".join(fs["of"])): continue
            if "other" in fs and not (fam_match(r["fam"], "|".join(fs["other"])) and r.get("signer") != self.self.get("signer")): continue
            if not all(self.join(j, r, bind) for j in a["joins"]): continue
            if a["at"] == "asserted_at" and not (r.get("asserted_at") is not None and self.self.get("asserted_at") is not None and r["asserted_at"] <= self.self["asserted_at"]): continue
            if a["at"] == "receipt" and not r["t"] < self.self["t"]: continue
            if a["window"]:
                w = self.policy.get(a["window"]["policy"], 0); s0 = self.self.get("asserted_at"); r0 = r.get("asserted_at")
                if s0 is None or r0 is None: continue
                inside = r0 <= s0 < r0 + w
                if (a["window"]["dir"] == "within") != inside: continue
            out.append(r)
        return out

    def join(self, j, r, bind):
        L = slot_val(j["left"], r if j["left"]["of"] is None else bind.get(j["left"]["of"]), bind, self.self)
        right_row = self.self if j["right"]["of"] is None else bind.get(j["right"]["of"])
        R = slot_val(j["right"], right_row, bind, self.self)
        op = j["op"]
        if L is None or R is None: return False
        if op == "=":
            if isinstance(L, frozenset) and isinstance(R, frozenset): return bool(L & R)   # ref:*=ref:*: a shared named row
            if isinstance(L, frozenset): return R in L        # ref:*=A.id
            if isinstance(R, frozenset): return L in R        # id=ref:*
            return L == R
        if op in (">=", "<="):
            try: return L >= R if op == ">=" else L <= R
            except TypeError: return False
        if op == "in": return isinstance(R, (set, frozenset, list)) and L in R
        if op == "commits": return isinstance(L, (set, frozenset, list)) and R in L
        raise ValueError(op)

    def instate(self, r, state):
        if state == "named":
            return ref_state(ref_past(self.held, self.self), r) == "admitted"
        if state == "landed":
            return ref_state(self.held, r) == "admitted" and getf(r, ["landed"]) == 1
        return ref_state(self.held, r) == state

    def matching(self, a, bind):
        C = self.cands(a, bind)
        return [r for r in C if self.instate(r, a["state"])], C

    def atom(self, a, bind):
        if a["atom"] == "window":
            opened = [x for x in self.held if x["id"] in self.self.get("names", ())]
            if not opened: return False
            w = self.policy.get(a["policy"], 0)
            closed = all(self.now >= x["t"] + w for x in opened)
            return closed if a["dir"] == "after" else not closed
        if a["atom"] == "row":
            M, C = self.matching(a, bind)
            q = a["quant"]
            if q == "one" or q.startswith("set("):
                return bool(M) if q == "one" else (bool(C) and len(M) == len(C))
            if q == "no": return not M
            if q == "all": return bool(C) and len(M) == len(C)
            if q == "latest":
                if not C: return False
                top = max(r["asserted_at"] for r in C)
                tops = [r for r in C if r["asserted_at"] == top]
                if len({r["id"] for r in tops}) > 1: return False
                return tops[0] in M
        fn, args = a["fn"], a["args"]
        held = self.held
        if a["at"] in ("asserted_at", "its_asserted_at"):
            row = self.self
            if a["at"] == "its_asserted_at":
                who = re.match(r"([A-Z])\.", args[0]); row = bind.get(who.group(1)) if who else self.self
            lim = row.get("asserted_at") if row else None
            held = [x for x in held if not x["fam"].startswith("seat:") or (lim is not None and x["asserted_at"] <= lim)]
        if fn == "type": v = typeof(keyarg(args[0], bind, self.self)) == args[1]
        elif fn == "signs": v = keyarg(args[0], bind, self.self) in self.self.get("cosig", frozenset())
        elif fn in ("adult", "capacitated"):
            k = keyarg(args[0], bind, self.self); v = ref_stands(held, k, fn, k)
        elif fn in ROW_ALONE_ROLES:
            k = keyarg(args[0], bind, self.self)
            tgt = args[1]
            if tgt.startswith("ref:"):
                rid = (self.self.get("ref") or {}).get(tgt[4:])
                rows = [x for x in self.held if x["id"] == rid]
                v = bool(rows) and rows[0].get("subject") == k
            else:
                v = self.self.get(fn if fn != "self" else "signer") == k
        else:
            k = keyarg(args[0], bind, self.self); obj = keyarg(args[1], bind, self.self)
            v = ref_stands(held, k, fn, obj)
        return (not v) if a["not"] else v

    def bind_as(self, clauses, bind):
        for c in clauses:
            if "atom" in c and c["atom"]["atom"] == "row" and c["atom"]["as"]:
                M, _ = self.matching(c["atom"], bind)
                ids = {r["id"] for r in M}
                bind[c["atom"]["as"]] = M[0] if len(ids) == 1 else None

    def clauses(self, cs, bind):
        bind = dict(bind)
        self.bind_as(cs, bind)
        out = set()
        for c in cs:
            if c["each"] is None:
                for v in self.clause(c, bind): out.add((None, v))
            else:
                for e in elems(self.self, c["each"]):
                    b = dict(bind, key=e)
                    for v in self.clause(c, b): out.add((e, v))
        return out

    def clause(self, c, bind):
        if not all(self.cond(w, bind) for w in c["when"]): return set()
        o = c["else"]
        verdict = outcome(o)
        if "group" in c:
            inner = self.clauses(c["group"], bind)
            res = {v for _, v in inner}
            if o and inner: res.add(verdict)
            return res
        return set() if self.atom(c["atom"], bind) else {verdict}

    def cond(self, w, bind):
        if w["cond"] == "verb": return self.self.get("verb") in w["values"]
        if w["cond"] == "leaf": return self.self.get("leafname") in w["values"]
        if w["cond"] == "subkind": return getf(self.self, ["subkind"]) in w["values"]
        if w["cond"] == "has": return getf(self.self, [w["values"][0]]) is not None
        return self.atom(w["atom"], bind)


def outcome(o):
    if not o: return "fail"
    return o["do"] + (f"({o['token']})" if o["token"] else "") + (f"+{o['hard_case']}" if o.get("hard_case") else "")


def elems(row, keys):
    k = keys[4:] if keys.startswith("val:") else keys
    x = getf(row, [k])
    if x is None: return []
    return sorted(x) if isinstance(x, (list, set, frozenset, tuple)) else [x]


def walk_atoms(cs):
    for c in cs:
        for w in c["when"]:
            if w["cond"] == "atom": yield w["atom"]
        if "group" in c: yield from walk_atoms(c["group"])
        else: yield c["atom"]


def slotname(sl):
    k, a = sl["slot"], sl["arg"]
    if k in ("val", "leaf"): return (k, a)
    if k in ("signer", "attested", "subject", "object"): return ("top", k)
    if k == "key": return ("key", None)
    return None


def guard_sets(family, clauses, seed, n=30, maxrows=5):
    rnd = random.Random(seed)
    pairs = []
    for a in walk_atoms(clauses):
        if a["atom"] == "row":
            for j in a["joins"]:
                L, R = slotname(j["left"]), slotname(j["right"])
                if L and (R or j["right"]["slot"] == "const"): pairs.append((L, R, j["right"]["arg"] if j["right"]["slot"] == "const" else None))
    fams, vals, refs, roles, leaves, verbs, eachk = set(), set(), set(), set(), set(), set(), set()
    def walkc(cs):
        for c in cs:
            if c["each"]: eachk.add(c["each"][4:] if c["each"].startswith("val:") else c["each"])
            for w in c["when"]:
                if w["cond"] == "leaf": leaves.update(w["values"])
                if w["cond"] == "verb": verbs.update(w["values"])
                if w["cond"] in ("has", "subkind"): vals.add(w["values"][0])
            if "group" in c: walkc(c["group"])
    walkc(clauses)
    for a in walk_atoms(clauses):
        if a["atom"] == "row":
            fs = a["families"]; fams.update(fs.get("of", []) + fs.get("other", []))
            if a["quant"].startswith("set("): refs.add(a["quant"][4:-1].split(":", 1)[1])
            for j in a["joins"]:
                for s in (j["left"], j["right"]):
                    if s["slot"] == "val": vals.add(s["arg"])
                    if s["slot"] == "ref": refs.add(s["arg"])
                    if s["slot"] == "leaf": vals.add("leaf:" + s["arg"])
        elif a["atom"] == "key":
            if a["fn"] not in ("type", "signs"): roles.add(a["fn"])
            for x in a["args"]:
                if x.startswith("ref:") or ".ref:" in x: refs.add(x.split("ref:")[1])
                if x.startswith("val:"): vals.add(x[4:])
    roles = sorted(roles) or ["member"]
    famlist = sorted(fams) or ["x:y"]
    out = []
    for _ in range(n):
        nid = [0]
        rows = []
        proto = mkrow(rnd, "proto", fill(family, rnd), vals, [])
        eachvals = {}
        for k in eachk:
            eachvals[k] = sorted(set(rnd.sample(KEYS, rnd.randint(1, 2))))
        n_other = rnd.randint(1, min(3, maxrows - 1))
        for i in range(n_other):
            pat = rnd.choice(famlist)
            r = mkrow(rnd, f"r{i}", fill(pat, rnd) if pat != "*" else rnd.choice(["x:y", "a:b"]), vals, rows)
            copy_like(rnd, r, proto, eachvals, rows)
            for L, R, const in pairs:
                if rnd.random() < .6:
                    if const is not None: v = const
                    elif R[0] == "key": v = rnd.choice([k for vv in eachvals.values() for k in vv] or KEYS)
                    elif R[0] == "top": v = proto.get(R[1])
                    elif R[0] == "val": v = proto["val"].get(R[1])
                    else: v = proto["leaf"].get(R[1])
                    if isinstance(v, list): v = rnd.choice(v) if v else None
                    if L[1] == "recovery_commitments": v = frozenset([v]) if v is not None else frozenset()
                    if L[0] == "top": r[L[1]] = v
                    elif L[0] == "val": r["val"][L[1]] = v
                    elif L[0] == "leaf": r["leaf"][L[1]] = v
            rows.append(r)
        if rows and rnd.random() < .3 and len(rows) < maxrows - 1:
            tgt = rnd.choice(rows)
            rows.append({"id": f"w{len(rows)}", "fam": tgt["fam"], "verb": rnd.choice(["withdraw", "recant", "replace"]),
                         "signer": tgt["signer"] if rnd.random() < .8 else rnd.choice(KEYS), "attested": None, "object": tgt.get("object"),
                         "names": frozenset([tgt["id"]]), "ref": {"target": tgt["id"]}, "val": {}, "asserted_at": rnd.randint(0, 4)})
        room = maxrows - 1 - len(rows)
        if room > 0 and rnd.random() < .7:
            seats = targeted_seats(rnd, nid, roles, proto, eachvals, rows)[:room]
            rows += seats
        selfrow = proto; selfrow["id"] = "self"
        set_refs(rnd, selfrow, refs, rows)
        if leaves: selfrow["leafname"] = rnd.choice(sorted(leaves) * 3 + ["other"])
        selfrow["verb"] = rnd.choice(sorted(verbs) * 3 + ["attest"]) if verbs else "attest"
        for k, v in eachvals.items():
            if k == "subject": selfrow["subject"] = v
            else: selfrow["val"][k] = v
        selfrow["cosig"] = frozenset(rnd.sample(KEYS, rnd.randint(0, 3)))
        out.append((rows + [selfrow], selfrow["id"]))
    return out


def mkrow(rnd, rid, fam, vals, prior, refs=()):
    r = {"id": rid, "fam": fam, "verb": "attest", "signer": rnd.choice(KEYS), "attested": rnd.choice(KEYS),
         "object": rnd.choice(OBJS), "subject": rnd.choice(KEYS), "asserted_at": rnd.randint(0, 4), "val": {}, "leaf": {}, "ref": {}}
    for v in vals:
        if v.startswith("leaf:"): r["leaf"][v[5:]] = rnd.choice(["d1", "d2"])
        elif v in ("recovery_commitments",): r["val"][v] = frozenset(rnd.sample(KEYS, rnd.randint(0, 2)))
        elif v in ("expires_at", "asserted_at"): r["val"][v] = rnd.randint(0, 5)
        elif v.endswith("key_id") or v.endswith("_key"): r["val"][v] = rnd.choice(KEYS)
        else: r["val"][v] = rnd.choice([0, 1, "analyze", "d1"]) if v in ("scope",) else rnd.choice([0, 1])
    r["val"]["landed"] = rnd.choice([0, 1])
    names = set()
    for f in refs:
        if prior and rnd.random() < .85:
            tgt = rnd.choice(prior)["id"]
            if f != "*": r["ref"][f] = tgt
            names.add(tgt)
        elif f != "*" and rnd.random() < .5:
            r["ref"][f] = "absent"; names.add("absent")
    if prior and not refs and rnd.random() < .3:
        names.add(rnd.choice(prior)["id"])
    r["names"] = frozenset(names)
    return r


def copy_like(rnd, r, proto, eachvals, prior):
    for f in ("signer", "attested", "object", "subject"):
        if rnd.random() < .5: r[f] = proto[f]
    keys = [k for v in eachvals.values() for k in v]
    if keys and rnd.random() < .6: r["signer"] = rnd.choice(keys)
    for k, v in proto["val"].items():
        if rnd.random() < .6: r["val"][k] = v
    for k, v in proto["leaf"].items():
        if rnd.random() < .6: r["leaf"][k] = v
    if rnd.random() < .3: r["val"]["recovery_commitments"] = frozenset([proto["signer"]])
    if prior and rnd.random() < .5:
        t = rnd.choice(prior)["id"]; r["names"] = frozenset([t]); r["ref"]["prev"] = t


def targeted_seats(rnd, nid, roles, proto, eachvals, prior=()):
    out = []
    keys = [proto["signer"], proto["subject"] if isinstance(proto["subject"], str) else KEYS[0]] + [k for v in eachvals.values() for k in v]
    keys += [x["signer"] for x in prior] + [v for v in proto["val"].values() if v in KEYS]
    role = rnd.choice(roles); obj = rnd.choice([proto["object"], proto["attested"], "federation", proto["subject"] if isinstance(proto["subject"], str) else "o1"])
    k = rnd.choice(keys)
    oid = f"s{nid[0]}"; nid[0] += 1
    out.append({"id": oid, "fam": "seat:offer", "verb": "attest", "signer": obj if rnd.random() < .85 else rnd.choice(KEYS),
                "attested": k, "object": obj, "val": {"role": role}, "names": frozenset(), "asserted_at": rnd.randint(0, 4), "ref": {}})
    if rnd.random() < .85:
        aid = f"s{nid[0]}"; nid[0] += 1
        out.append({"id": aid, "fam": "seat:accept", "verb": "attest", "signer": k, "attested": k, "object": obj, "val": {},
                    "names": frozenset([oid]), "asserted_at": rnd.randint(0, 4), "ref": {"offer": oid}})
    return out


def set_refs(rnd, r, refs, prior):
    names = set()
    for f in refs:
        if prior and rnd.random() < .85:
            tgt = rnd.choice(prior)["id"]
            if f != "*": r["ref"][f] = tgt
            names.add(tgt)
        elif f != "*" and rnd.random() < .5:
            r["ref"][f] = "absent"; names.add("absent")
    if prior and not refs and rnd.random() < .4:
        names.add(rnd.choice(prior)["id"])
    r["names"] = frozenset(names)


class RefFold:
    def __init__(self, parts, family, held, p, now, consts, when=None):
        self.P, self.family, self.held, self.p, self.now, self.c, self.when = parts, family, held, p, now, consts, when

    def f(self, r, m):
        if m == "admission_order": return r["t"]
        return getf(r, [m])

    def retracted(self, r):
        return any(q.get("verb") in ("withdraw", "recant") and r["id"] in q.get("names", ()) and q.get("signer") == r.get("signer") for q in self.held)

    def source(self):
        reads = self.P.get("reads", "own&live")
        bits = reads.split("&"); srcs = bits[0].split("+")
        S = []
        for src in srcs:
            if src == "own": S += [r for r in self.held if fam_match(r["fam"], self.family) and r["id"] != "p"]
            elif src == "head": S += [r for r in self.held if fam_match(r["fam"], "group:roster") and not any(r["id"] in q.get("names", ()) and fam_match(q["fam"], "group:roster") for q in self.held)]
            else: S += [r for r in self.held if fam_match(r["fam"], src)]
        S = list({r["id"]: r for r in S}.values())
        if self.when: S = [r for r in S if r.get("leafname") in self.when["leaves"]]
        out = []
        for r in S:
            ok = True
            for flt in bits[1:]:
                if flt == "live": ok = ok and ref_state(self.held, r) == "admitted"
                elif flt == "direct": ok = ok and getf(r, ["via"]) is None
                elif flt.startswith("signer:"):
                    ok = ok and any((r.get("signer") == r.get(ROW_READ[role]) and r.get("signer") is not None) if role in ROW_READ else
                                    ref_stands(self.held, r["signer"], role, r.get("object")) for role in flt[7:].split("|"))
                elif flt.startswith("seat:"):
                    ok = ok and typeof(r.get("signer")) == "user"
                elif flt.startswith("at("):
                    vu = getf(r, ["valid_until"])
                    ok = ok and r["asserted_at"] <= self.now and (vu is None or self.now < vu)
                elif flt.startswith("has("):
                    ok = ok and any(getf(r, [m]) is not None for m in flt[4:-1].split("|"))
                elif flt.startswith("cap("):
                    ok = ok and ref_stands(self.held, r["signer"], "cap:" + flt[4:-1], r.get("object"))
                elif flt.startswith("declared("):
                    ok = ok and getf(r, [flt[9:-1]]) is not None
                elif flt.startswith("cites("):
                    F = flt[6:-1]; ok = ok and any(fam_match(x["fam"], F) for x in ref_past(self.held, r))
            if ok: out.append(r)
        return out

    def cut(self, S):
        cuts = self.P.get("cut", "named,forward").split(",")
        for c in cuts:
            if c == "named": S = [r for r in S if not self.retracted(r)]
            elif c == "forward": S = [r for r in S if not any(self.retracted(x) for x in ref_past(self.held, r))]
            elif c == "terminal": S = [r for r in S if not any(getf(x, ["terminal"]) == 1 for x in ref_past(self.held, r))]
            elif c.startswith("boundary("):
                m = c[9:-1]
                def b(r):
                    vs = [getf(q, ["revoked_after"]) for q in self.held if fam_match(q["fam"], "key:revocation") and q.get("attested") == r.get("signer") and ref_state(self.held, q) == "admitted"]
                    vs = [v for v in vs if v is not None]
                    return min(vs) if vs else None
                S = [r for r in S if b(r) is None or self.f(r, m) is None or self.f(r, m) < b(r)]
        return S

    def keyof(self, r):
        return tuple(self.f(r, m) for m in self.P.get("key", "references_attestation_id,attesting_key_id").split(","))

    def comparators(self, spec):
        out = []
        for p in split_top(spec):
            m = re.fullmatch(r"(max|min)\((.+)\)", p)
            if m: out.append((m.group(1), m.group(2))); continue
            m = re.fullmatch(r"rank\((.+)\)", p)
            if m: out.append(("rank", m.group(1).split(">"))); continue
        return out

    def ckey(self, r, comps):
        k = []
        for how, a in comps:
            if how == "rank":
                nm = next((VERB_RANK[x] for x in a if x in VERB_RANK and r.get("verb") == VERB_RANK[x]), None)
                lab = r.get("leafname")
                idx = next((i for i, x in enumerate(a) if (x in VERB_RANK and r.get("verb") == VERB_RANK[x]) or x == lab), len(a))
                k.append(idx)
            else:
                v = self.f(r, a); k.append(None if v is None else (-v if how == "max" else v))
        return tuple(k)

    def least(self, G, comps):
        ks = [(self.ckey(r, comps), r) for r in G]
        ks = [(k, r) for k, r in ks if None not in k]
        if not ks: return None
        best = min(k for k, _ in ks)
        tied = {r["id"] for k, r in ks if k == best}
        return "tie" if len(tied) > 1 else next(iter(tied))

    def pick(self, G):
        spec = self.P.get("pick")
        if spec is None: return None
        bits = split_top(spec)
        head = bits[0]
        if head.startswith("pair("):
            F = head[5:-1]
            G = [r for r in G if any(fam_match(q["fam"], F) and r["id"] in q.get("names", ()) and ref_state(self.held, q) == "admitted" for q in self.held)]
            bits = bits[1:]
            if not bits: return frozenset(r["id"] for r in G)
            if not G: return None
        if bits[0] in ("union", "set"): return frozenset(r["id"] for r in G)
        if bits[0] == "agree":
            vs = {getf(r, ["value"]) for r in G}; return next(iter(vs)) if len(vs) == 1 else None
        if bits[0].startswith("once"):
            tok = bits[0][5:-1] if "(" in bits[0] else ""
            ids = {r["id"] for r in G}
            return ("contested(" + tok + ")") if len(ids) > 1 else next(iter(ids))
        if bits[0].startswith("chain("):
            tips = frozenset(r["id"] for r in G if not any(r["id"] in q.get("names", ()) for q in G if q is not r))
            if len(bits) > 1 and bits[1] == "tips": return tips
            return next(iter(tips)) if len(tips) == 1 else "tie"
        return self.least(G, self.comparators(",".join(bits)))

    def bounds(self, G):
        spec = self.P.get("bound")
        if not spec: return ()
        out = []
        for b in split_top(spec):
            mono, m = re.fullmatch(r"([a-z_]+)\((.+)\)", b).groups()
            vs = [self.f(r, m) for r in G if self.f(r, m) is not None]
            if mono == "raise_only": out.append(max(vs) if vs else None)
            elif mono == "fixed": out.append(next(iter(set(vs))) if len(set(vs)) == 1 else None)
            else: out.append(min(vs) if vs else None)
        return tuple(out)

    def over(self):
        spec = self.P.get("over")
        if not spec: return None
        m = re.fullmatch(r"([a-z_]+)(?:@([a-z_]+))?(?:/([a-z]+))?", spec)
        role, inst = m.group(1), m.group(2)
        p = self.p
        if inst == "named":
            S = ref_past(self.held, p)
        elif inst == "signed":       # the set as it stood at the instant the counted row was signed
            S = [x for x in self.held if not x["fam"].startswith("seat:") or x["asserted_at"] <= p["asserted_at"]]
        else:
            S = self.held
        obj = p.get("object")
        unit = m.group(3) or "key"
        keys = {o["attested"] for o in S if fam_match(o["fam"], "seat:offer") and (o.get("val") or {}).get("role") == role}
        return len({(k if unit == "key" else UNITS[unit].get(k, k)) for k in keys if ref_stands(S, k, role, obj)})

    def arith(self, e, r, env):
        t = e[0]
        if t == "num": return e[1]
        if t == "neg":
            v = self.arith(e[1], r, env); return None if v is None else -v
        if t == "name":
            n = e[1]
            if n in env: return env[n]
            if r is not None and getf(r, [n]) is not None: return getf(r, [n])
            return self.c.get(n, 1)
        if t == "fn":
            fn, args = e[1], e[2]
            if fn == "count":
                return len({getf(x, [args[0][1]]) for x in env["_standing"]} - {None}) if args else len(env["_standing"])
            vs = [self.arith(a, r, env) for a in args]
            if fn == "rate": return self.c.get("rate:" + str(vs[0]), 1)
            if fn not in ("min", "max"): raise NeedsOperator(fn)
            if None in vs: return None
            return min(vs) if fn == "min" else max(vs)
        a, b = self.arith(e[1], r, env), self.arith(e[2], r, env)
        if a is None or b is None: return None
        if t == "+": return a + b
        if t == "-": return a - b
        if t == "*": return a * b
        if t == "div": return a // b
        if t == "/": return a // b        # integer division: the ruling (no floating point)
        raise ValueError(t)

    def run(self):
        S = self.cut(self.source())
        groups = {}
        for r in S: groups.setdefault(self.keyof(r), []).append(r)
        if self.P.get("order") and self.P.get("pick") is None:
            standing_rows = S
        per = []
        standing_rows = []
        for k in sorted(groups, key=repr):
            G = groups[k]
            pk = self.pick(G)
            per.append((k, (pk, self.bounds(G))))
            if isinstance(pk, frozenset): standing_rows += [r for r in G if r["id"] in pk]
            elif isinstance(pk, str): standing_rows += [r for r in G if r["id"] == pk]
            elif pk is None and self.P.get("pick") is None: standing_rows += G
        order = None
        if self.P.get("order"):
            comps = self.comparators(self.P["order"])
            order = tuple(sorted(((("row", r["id"]), sum(1 for q in standing_rows if None not in self.ckey(q, comps) and None not in self.ckey(r, comps) and self.ckey(q, comps) < self.ckey(r, comps))) for r in standing_rows), key=repr))
        env = {"_standing": standing_rows}
        n = self.over()
        if n is not None: env["n"] = n
        comb = None
        if "weight" in self.P:
            we = parse_arith(self.P["weight"])
        if "combine" in self.P and not self.P["combine"].startswith("policy("):
            m = re.fullmatch(r"([a-z]+)\((.+)\)", self.P["combine"])
            agg, arg = m.groups()
            if agg == "all":
                comb = all(getf(r, [arg]) == 1 for r in standing_rows)
            elif agg == "count":
                comb = len({getf(r, [arg]) for r in standing_rows if getf(r, [arg]) is not None})
            elif agg == "max" and "," in arg and "count(" in arg:
                comb = self.arith(parse_arith("max(" + arg + ")"), None, env)
            else:
                ex = parse_arith(arg if "," not in arg else "min(" + arg + ")" if agg == "min" else arg)
                def val(r):
                    e2 = dict(env)
                    if "weight" in self.P: e2["weight"] = self.arith(we, r, env)
                    return self.arith(ex, r, e2)
                vs = [(r["id"], val(r)) for r in standing_rows]
                vs = [(i, v) for i, v in vs if v is not None]
                if agg == "sum": comb = sum(v for _, v in vs)
                elif agg == "min": comb = min((v for _, v in vs), default=None)
                elif agg == "max": comb = max((v for _, v in vs), default=None)
                elif agg == "median":
                    xs = sorted(v for _, v in vs)
                    comb = xs[(len(xs) - 1) // 2] if xs else None      # the lower median: a function of the multiset
                elif agg == "mean":
                    comb = sum(v for _, v in vs) // len(vs) if vs else None   # floor of the mean: integers only (the ruling)
                else: comb = None
        if "weight" in self.P and "combine" not in self.P:
            comb = tuple(sorted(((("row", r["id"]), self.arith(we, r, env)) for r in standing_rows), key=repr))
        verdict = None
        if "test" in self.P:
            m = re.fullmatch(r"(.+?)(>=|<=|=|>|<)(.+?) (?:!([a-z_0-9]+)|\?([a-z_]+):([a-z_]+))", self.P["test"])
            L, op, R, tok, a, b = m.groups()
            env2 = dict(env)
            for nm in ("sum", "score", "voices", "yes"): env2[nm] = comb if comb is not None else len(standing_rows)
            env2["count"] = len(standing_rows)
            lv, rv = self.arith(parse_arith(L), None, env2), self.arith(parse_arith(R), None, env2)
            holds = lv is not None and rv is not None and {">=": lv >= rv, "<=": lv <= rv, "=": lv == rv, ">": lv > rv, "<": lv < rv}[op]
            verdict = ("ok" if holds else f"refuse({tok})") if tok else (a if holds else b)
        absent = None
        if not standing_rows and "absent" in self.P:
            absent = self.P["absent"]
        return (tuple(sorted(per, key=repr)), order, comb, verdict, absent, n)


def fold_sets(family, parts, seed, n=24, maxrows=5, when=None):
    rnd = random.Random(seed)
    members = set()
    for k in ("key", "bound", "pick", "order", "weight", "combine", "test", "cut"):
        if k in parts: members |= set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", parts[k]))
    members -= {"max", "min", "rank", "count", "sum", "union", "once", "chain", "tips", "pair", "agree", "set", "div", "lower_only",
                "raise_only", "narrow_only", "drop_only", "fixed", "boundary", "named", "forward", "terminal", "whole", "none", "median",
                "all", "rate", "policy", "mean"}
    ranks = re.findall(r"rank\(([^)]+)\)", parts.get("pick", "") + "," + parts.get("order", ""))
    leafnames = sorted({x for r in ranks for x in r.split(">") if x not in VERB_RANK}) or ["x"]
    reads = parts.get("reads", "own&live").split("&")[0].split("+")
    pairf = re.findall(r"pair\(([^)]+)\)", parts.get("pick", ""))
    roles = re.findall(r"(?:signer|seat):([a-z_|]+)", parts.get("reads", ""))
    roles = [x for r in roles for x in r.split("|")]
    ov = re.match(r"([a-z_]+)", parts.get("over", "")) if parts.get("over") else None
    if ov: roles.append(ov.group(1))
    caps = re.findall(r"cap\(([^)]+)\)", parts.get("reads", ""))
    roles += ["cap:" + c for c in caps]
    out = []
    for _ in range(n):
        rows = []
        p = {"id": "p", "fam": "proposal:x", "verb": "attest", "signer": rnd.choice(KEYS), "attested": None, "object": rnd.choice(OBJS),
             "asserted_at": rnd.randint(0, 3), "val": {}, "leaf": {}, "ref": {}, "names": frozenset()}
        nown = rnd.randint(1, 3)
        for i in range(nown):
            src = rnd.choice(reads)
            fam = fill(family, rnd) if src in ("own",) else ("group:roster" if src == "head" else fill(src, rnd))
            r = {"id": f"r{i}", "fam": fam, "verb": rnd.choice(["attest"] * 4 + ["replace", "withdraw", "recant"]), "signer": rnd.choice(KEYS),
                 "attested": rnd.choice(KEYS), "object": p["object"] if rnd.random() < .7 else rnd.choice(OBJS), "asserted_at": rnd.randint(0, 2),
                 "leafname": rnd.choice(when["leaves"]) if when and rnd.random() < .75 else rnd.choice(leafnames), "val": {}, "leaf": {}, "ref": {}, "names": frozenset()}
            for m in members:
                r["val"][m] = rnd.choice(KEYS[:2]) if m.endswith("key_id") or m in ("owner", "person", "quorum_key") else rnd.randint(0, 2)
            r["val"]["value"] = rnd.randint(0, 1); r["val"]["terminal"] = int(rnd.random() < .15); r["val"]["present"] = rnd.randint(0, 1)
            if rnd.random() < .2: r["val"]["valid_until"] = rnd.randint(0, 6)
            if rows and rnd.random() < .5:
                t = rnd.choice(rows); r["names"] = frozenset([t["id"]]); r["val"]["prev_head_digest"] = t["id"]
                if rnd.random() < .5: r["signer"] = t["signer"]
            if i > 0 and rnd.random() < .5:   # share a key with an earlier row so groups have several rows
                t = rows[0]
                for m in parts.get("key", "references_attestation_id,attesting_key_id").split(","):
                    if m in t["val"]: r["val"][m] = t["val"][m]
            rows.append(r)
        if len(rows) < maxrows - 1 and rnd.random() < .5:
            if pairf and rnd.random() < .6:
                t = rnd.choice(rows)
                rows.append({"id": "q", "fam": fill(pairf[0], rnd), "verb": "attest", "signer": rnd.choice(KEYS), "attested": None, "object": t["object"],
                             "asserted_at": 1, "val": {}, "leaf": {}, "ref": {}, "names": frozenset([t["id"]])})
            elif "boundary(" in parts.get("cut", "") and rnd.random() < .6:
                t = rnd.choice(rows)
                rows.append({"id": "k", "fam": "key:revocation", "verb": "attest", "signer": "n1", "attested": t["signer"], "object": None,
                             "asserted_at": 1, "val": {"revoked_after": rnd.randint(0, 2)}, "leaf": {}, "ref": {}, "names": frozenset()})
            else:
                t = rnd.choice(rows)
                rows.append({"id": "w", "fam": t["fam"], "verb": rnd.choice(["withdraw", "recant"]), "signer": t["signer"] if rnd.random() < .8 else rnd.choice(KEYS),
                             "attested": None, "object": t["object"], "asserted_at": 2, "val": {}, "leaf": {}, "ref": {}, "names": frozenset([t["id"]])})
        if roles and len(rows) < maxrows - 1:
            nid = [0]
            for _ in range(1):
                role = rnd.choice(roles); k = rnd.choice([r["signer"] for r in rows] + KEYS)
                obj = rnd.choice([r["object"] for r in rows] + [p["object"]])
                oid = f"s{nid[0]}"; nid[0] += 1
                rows.append({"id": oid, "fam": "seat:offer", "verb": "attest", "signer": obj, "attested": k, "object": obj, "val": {"role": role},
                             "asserted_at": rnd.randint(0, 3), "leaf": {}, "ref": {}, "names": frozenset()})
                if len(rows) < maxrows - 1 and rnd.random() < .85:
                    rows.append({"id": f"s{nid[0]}", "fam": "seat:accept", "verb": "attest", "signer": k, "attested": k, "object": obj, "val": {},
                                 "asserted_at": rnd.randint(0, 3), "leaf": {}, "ref": {}, "names": frozenset([oid])})
        if ov and rnd.random() < .6:
            p["names"] = frozenset(r["id"] for r in rows if r["fam"].startswith("seat:"))
        rows.append(p)
        out.append(rows)
    return out


REL_REF = {
    "by": lambda r, t: r.get("signer") == t.get("signer"),
    "under": lambda r, t: t["id"] in r.get("names", ()),
    "ref": lambda r, t: t["id"] in r.get("names", ()),
    "about": lambda r, t: r.get("subject") is not None and r.get("subject") == t.get("attested"),
    "over": lambda r, t: r.get("object") is not None and r.get("object") == t.get("object"),
}


def ch_ref(items, held, s):
    tgt = [x for x in held if x["id"] == (s.get("ref") or {}).get("target")]
    T = tgt[0] if tgt else None
    out = []
    for it in items:
        if not (s.get("verb") == it["on"] or s.get("leafname") == it["on"]): continue
        ok = True
        for a in it["when"]:
            k, vs = a["test"], a["values"]
            if vs is None: ok = ok and (s.get("leafname") == "recovery" if k == "recovery" else len(s.get("cosig", ())) >= 1 if k == "cosigned" else getf(s, [k]) == 1)
            elif k == "grade": ok = ok and T is not None and getf(T, ["grade"]) in vs
            elif k in ("subkind", "scope", "axis"): ok = ok and getf(s, [k]) in vs
            elif k == "seat": ok = ok and any(ref_stands(held, s["signer"], v, s.get("object")) for v in vs)
            elif k == "last":
                ok = ok and any({o["attested"] for o in held if fam_match(o["fam"], "seat:offer") and (o.get("val") or {}).get("role") == v
                                 and ref_stands(held, o["attested"], v, s.get("object"))} == {s["signer"]} for v in vs)
        if not ok: continue
        checks, effects, tok = [], [], None
        for c in it["clauses"]:
            k = c["clause"]
            if k == "by":
                b = c["by"]
                checks.append(True if b == "none" else T is not None and (
                    s["signer"] == T.get("signer") if b == "same_attester" else
                    len(s.get("cosig", ())) >= 1 if b == "cosigned" else
                    T.get("signer") in s.get("cosig", ()) if b == "cosigned_prior" else
                    s["signer"] in (getf(T, ["recovery_commitments"]) or ()) if b == "committed_key" else
                    typeof(s["signer"]) == "node"))
            elif k == "link": checks.append(T is not None and (s.get("ref") or {}).get(c["member"]) == T["id"])
            elif k == "field":
                d, m = c["dir"], c["member"]
                a, b = getf(s, [m]), getf(T, [m]) if T else None
                if d in ("any", "as_attest"): checks.append(True)
                elif a is None or b is None: checks.append(False)
                elif d == "frozen": checks.append(a == b)
                elif d in ("shrink", "lower"): checks.append(a <= b)
                else: checks.append(a >= b)
            elif k == "reach":
                r = c["reach"]
                checks.append(True if r in ("other_attester", "whole") else T is not None and (
                    T.get("signer") == s["signer"] if r == "own_prior" else (getf(T, ["seq"]) is not None and getf(s, ["seq"]) is not None and getf(T, ["seq"]) < getf(s, ["seq"]))))
            elif k == "after": checks.append(any(fam_match(x["fam"], c["family"]) for x in ref_past(held, s)))
            elif k == "refuse": tok = c["token"]
            elif k == "key": effects.append(("key", c["key"]))
            elif k == "cascade":
                if T is None: continue
                for x in held:
                    if x["id"] in (s["id"], T["id"]): continue
                    if (c["family"] == "*" or fam_match(x["fam"], c["family"])) and REL_REF[c["rel"]](x, T):
                        if c["effect"] == "void_after":
                            if getf(x, ["asserted_at"]) is not None and getf(T, [c["member"]]) is not None and x["asserted_at"] > getf(T, [c["member"]]):
                                effects.append((x["id"], "void"))
                        else: effects.append((x["id"], c["effect"]))
        verdict = "ok" if all(checks) else ("refuse(" + tok + ")" if tok else "refuse")
        out.append((it["on"], verdict, frozenset(effects)))
    return frozenset(out)


def ch_gen(items, rnd, n=20):
    sets = []
    for _ in range(n):
        T = {"id": "t", "fam": "f:x", "verb": "attest", "signer": rnd.choice(KEYS), "attested": rnd.choice(KEYS), "object": rnd.choice(OBJS),
             "subject": rnd.choice(KEYS), "asserted_at": rnd.randint(0, 3), "val": {}, "leaf": {}, "ref": {}, "names": frozenset()}
        rows = [T]
        for it in items:
            for c in it["clauses"]:
                if c["clause"] == "field": T["val"][c["member"]] = rnd.randint(0, 2)
                if c["clause"] == "by" and c["by"] == "committed_key": T["val"]["recovery_commitments"] = frozenset(rnd.sample(KEYS, rnd.randint(0, 2)))
                if c["clause"] == "cascade" and c.get("member"): T["val"][c["member"]] = rnd.randint(0, 3)
                if c["clause"] == "cascade" and len(rows) < 4:
                    fam = fill(c["family"], rnd) if c["family"] != "*" else "g:y"
                    x = {"id": f"c{len(rows)}", "fam": fam, "verb": "attest", "signer": T["signer"] if rnd.random() < .5 else rnd.choice(KEYS),
                         "attested": rnd.choice(KEYS), "object": T["object"] if rnd.random() < .5 else rnd.choice(OBJS), "subject": T["attested"] if rnd.random() < .5 else rnd.choice(KEYS),
                         "asserted_at": rnd.randint(0, 4), "val": {}, "leaf": {}, "ref": {}, "names": frozenset(["t"]) if rnd.random() < .5 else frozenset()}
                    rows.append(x)
                if c["clause"] == "after" and len(rows) < 4 and rnd.random() < .5:
                    rows.append({"id": f"a{len(rows)}", "fam": fill(c["family"], rnd), "verb": "attest", "signer": rnd.choice(KEYS), "attested": None,
                                 "object": None, "asserted_at": 0, "val": {}, "leaf": {}, "ref": {}, "names": frozenset()})
            for a in it["when"]:
                if a["test"] in ("seat", "last") and len(rows) < 4:
                    rows += seat_rows(rnd, [len(rows)], a["values"], OBJS, KEYS)[:4 - len(rows)]
        ons = [it["on"] for it in items]
        s = {"id": "self", "fam": "f:x", "verb": rnd.choice(ons + ["attest"]), "leafname": rnd.choice(ons + ["x"]), "signer": T["signer"] if rnd.random() < .5 else rnd.choice(KEYS),
             "attested": rnd.choice(KEYS), "object": T["object"] if rnd.random() < .6 else rnd.choice(OBJS), "asserted_at": rnd.randint(0, 4),
             "cosig": frozenset(rnd.sample(KEYS, rnd.randint(0, 2))), "val": {}, "leaf": {}, "ref": {}, "names": set()}
        if rnd.random() < .85: s["ref"]["target"] = "t"; s["names"].add("t")
        for r in rows[1:]:
            if r["fam"] not in ("seat:offer", "seat:accept") and r["id"].startswith("a") and rnd.random() < .8: s["names"].add(r["id"])
        s["names"] = frozenset(s["names"])
        for it in items:
            for c in it["clauses"]:
                if c["clause"] == "field": s["val"][c["member"]] = rnd.randint(0, 2)
                if c["clause"] == "link": s["ref"][c["member"]] = "t" if rnd.random() < .7 else "zz"
                if c["clause"] == "reach" and c["reach"] == "below_seq": s["val"]["seq"] = rnd.randint(0, 2); T["val"]["seq"] = rnd.randint(0, 2)
            for a in it["when"]:
                if a["values"] is None:
                    s["val"][a["test"]] = rnd.randint(0, 1)
                    if a["test"] == "recovery" and rnd.random() < .6: s["leafname"] = "recovery"
                elif a["test"] == "grade": T["val"]["grade"] = rnd.choice(a["values"] + ["zz"])
                elif a["test"] in ("subkind", "scope", "axis"): s["val"][a["test"]] = rnd.choice(a["values"] + ["zz"])
        sets.append((rows + [s], "self"))
    return sets


def dur_of(name, s):
    if name is None: return None
    if "." in name:
        holder, m = name.split(".", 1)
        if holder == "self": return getf(s, [m])
        return CONST_DUR
    return CONST_DUR


def origin_ref(c, s, held):
    o = c.get("from")
    if o is None or o == "first_held": return s["t"]
    if isinstance(o, str): return getf(s, [o])
    ts = [x["t"] for x in held for e in o if e["event"] in ("admitted", "withdrawn") and e["of"] not in ("self", "target") and fam_match(x["fam"], e["of"])
          and ref_state(held, x) == e["event"]]
    return min(ts) if ts else None


def event_ref(e, s, held, clocks, now):
    k, of = e["event"], e["of"]
    if k == "close":
        return clocks.get(of) is not None and now >= clocks[of]
    if k == "fold": return None
    rows = [s] if of == "self" else [x for x in held if x["id"] == (s.get("ref") or {}).get("target")] if of == "target" else [x for x in held if fam_match(x["fam"], of) and x["id"] != s["id"]]
    if e.get("by") == "producer": rows = [x for x in rows if x.get("signer") == s.get("signer")]
    if e.get("by") == "subject": rows = [x for x in rows if x.get("signer") == s.get("subject")]
    if k in ("admitted", "withdrawn", "recanted", "superseded"):
        return any(ref_state(held, x) == k for x in rows)
    return any(getf(x, ["state"]) == k for x in rows)


def re_ref(clauses, held, s, now):
    out = []
    clocks = {}
    for c in clauses:
        if c["kind"] == "clock" and not (c.get("leaves") and s.get("leafname") not in c["leaves"]) and not (c.get("scope") and getf(s, ["scope"]) != c["scope"]):
            o = origin_ref(c, s, held); d = dur_of(c["dur"], s)
            if d is None: d = dur_of(c.get("default"), s)
            if d is not None and c.get("max"): d = min(d, dur_of(c["max"], s))
            clocks[c["name"]] = None if (o is None or d is None) else o + d
    for c in clauses:
        if c.get("leaves") and s.get("leafname") not in c["leaves"]: continue
        if c.get("scope") and getf(s, ["scope"]) != c["scope"]: continue
        if c["kind"] == "clock":
            o = origin_ref(c, s, held)
            d = dur_of(c["dur"], s)
            if d is None: d = dur_of(c.get("default"), s)
            if d is not None and c.get("max"): d = min(d, dur_of(c["max"], s))
            clocks[c["name"]] = None if (o is None or d is None) else o + d
            out.append(("clock", c["name"], None if clocks[c["name"]] is None else ("closed" if now >= clocks[c["name"]] else "open")))
        elif c["kind"] == "expiry":
            m = c.get("member"); v = getf(s, [m]) if m else None
            if c["mode"] == "none": out.append(("expiry", "none")); continue
            if c["mode"] == "forbidden": out.append(("expiry", "refuse" if v is not None else "ok")); continue
            if c["mode"] == "required" and v is None: out.append(("expiry", "refuse")); continue
            o = origin_ref(c, s, held) if c.get("from") else getf(s, ["asserted_at"])
            end = v if v is not None else (o + dur_of(c["default"], s) if c.get("default") and o is not None else None)
            if end is not None and c.get("eq") and o is not None and end != o + dur_of(c["eq"], s): out.append(("expiry", "refuse")); continue
            if end is not None and c.get("max") and o is not None and end - o > dur_of(c["max"], s): out.append(("expiry", "refuse")); continue
            out.append(("expiry", "open" if end is None else ("live" if now < end else "expired")))
        elif c["kind"] == "land":
            late = c.get("late", "unstated")
            if c["concluder"] == "local": out.append(("land", c["name"], "local", late)); continue
            ok = any(fam_match(x["fam"], c["landing"]) and s["id"] in x.get("names", ()) and ref_state(held, x) == "admitted"
                     and (x.get("signer") == s.get("signer") if c["concluder"] in ("self", "author") else ref_stands(held, x.get("signer"), c["concluder"], s.get("object"))) for x in held)
            out.append(("land", c["name"], ok, late))
        else:
            on = [event_ref(e, s, held, clocks, now) for e in c["on"]]
            un = [event_ref(e, s, held, clocks, now) for e in c.get("unless", [])]
            if None in on or None in un: out.append(("react", "unresolved")); continue
            fires = any(on) and not any(un)
            out.append(("react", tuple(sorted(("" if x.get("force", "must") == "must" else x["force"] + " ") + f"{x['effect']}:{x.get('family') or x.get('verdict') or x.get('act') or x.get('policy')}" for x in c["effects"])) if fires else ()))
    return tuple(out)



def count_ref(arms, s):
    for a in arms:
        ok = True
        if a["selector"] != "*":
            for t in a["selector"].split(" & "):
                k, vs = t.split("="); vs = vs.split("|")
                v = {"leaf": s.get("leafname"), "verb": s.get("verb"), "identity": typeof(s.get("attested")), "group": getf(s, ["group"]), "seats": getf(s, ["seats"])}[k]
                ok = ok and v in vs
        if ok:
            md = re.fullmatch(r"(none|shut)|([a-z_]+)(?:@([a-z_]+))?(?:!(confers|result))?", a["doors"])
            return md.group(1) if md.group(1) else ("tally", md.group(2), md.group(3) or "", md.group(4) or "")
    return "none"
