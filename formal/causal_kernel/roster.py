"""
roster.py: ONE ROSTER, PARAMETRISED, on the causal kernel, rules unchanged.

A roster is a lineage of versions over one object. Every version is a counted act (an `offer` or `unseat` with
conf=group) that names the head(s) it extends and is counted over the members those heads seat (seat.members_at:
several heads, the members common to all; KERNEL.md section 7, tips wait). A row of a removed key counts only if
the removal has it in its past (cut.py). A founding row seats the keys that signed it (conf=self, the root). That is
the kernel's mechanism, unchanged. What this file adds is the PARAMETERS, and the derived effect of a lone path:

    obj        the object the roster is over (a self, a voice, a room, the accord, an infrastructure community)
    scope      the seat it gives (self / key / member / holder / founder)
    counted    the seat a count is taken over (infra: founders; every other instance: the seat itself)
    unit       what a member is: "key" (a key signs for itself), or "voice"/"person" (a member is itself a roster of
               keys: a room row carries signer = the member, dev = the key that signed, vhead = the head of that
               member's own roster it relies on; the count reads `signer`, so it counts members, never keys)
    add/remove the count, as a row of the policy table (kind, num, den), or the group's declared protocol
    floor      the least number of distinct voices on a counted act (the table's min_count); on an admission the
               joiner's own acceptance is a voice
    consent    "own": a seat needs the seated key's own acceptance; "one": no acceptance (a node has no agency)
    lone       an optional lone path for add and/or evict: a window (window.py) whose table is derived from the policy
               row; its landing is followed by an effect row (`via` = the landing) that is a counted act like any
               other, and the effect stands only if the landing stands under window.py's RECOUNT
    margin     T7: a count admits only while at least need+margin keys hold the counted seat (0 = no margin)
    recovery   the accord: a version signed by a holder's committed recovery key alone, changing only that seat
    body       infra: a conferring body that may sign one founder-adding widening while the roster is stalled
    witnessed  T6: a witnessed lineage refuses a rival head that is not witnessed (a reader-side parameter)

Instances are built from manifests/governance_policy.json by `instances()`.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "roster_fork"))
sys.dont_write_bytecode = True
import seat as ST      # noqa: E402
import window as WN    # noqa: E402
import cut as CUT      # noqa: E402
import fork as FK      # noqa: E402

CK, K, R = ST.CK, ST.K, ST.R
POL = json.load(open(os.path.join(HERE, "..", "..", "manifests", "governance_policy.json"), encoding="utf-8"))
TABLE = {f["family"]: f for f in POL["families"]}
MIN_COUNT = POL["min_count"]


# ---- the count, read off a table row -------------------------------------------------------------------
def count_kind(rule, declared=None):
    """A policy-table rule -> a seat.py met() kind (the same reading seat.policy_table makes)."""
    k = rule.get("kind")
    if k == "fraction":
        return ("strict", 1, 2) if (rule["num"], rule["den"]) == (1, 2) else ("atleast", rule["num"], rule["den"])
    if k in ("strict_majority",): return ("strict", 1, 2)
    if k == "one_of_n": return ("one", 1, 1)
    if k == "protocol": return declared
    return ("not_a_count", 0, 0)


PROTOCOLS = {"majority": ("strict", 1, 2), "two_thirds": ("atleast", 2, 3), "one": ("one", 1, 1),
             "quorum": ("declared", 0, 0)}


def register(name, kind):
    """Add a policy name to the kernel's policy dict (data, not a rule)."""
    ST.POLICY[name] = kind
    return name


def window_from_table(name, family, counted, evict, declared_enact=None):
    """A window spec (window.py's own shape) derived from one policy-table row.
         at once:  approvals meeting enact over the counted set -> landed
         cancel:   objections meeting cancel over `cancel_over` -> refused (at once when the row counts it over the others,
                   as formal/self_roster does; at the close otherwise, as the table's decider does)
         silent:   target_silent=yes and an eviction -> a row of the target inside the window refuses it
         floor:    one_of_n -> the opener's own approval lands it at the close (default landed);
                   a fraction -> approvals meeting the floor (min_count) land it at the close (default refused)"""
    row = TABLE[family]
    mc = MIN_COUNT["self" if row["corridor"] == "self" else "community"]
    how = lambda r: {"strict": "strict", "one": "one"}.get(count_kind(r)[0], ("atleast",) + count_kind(r)[1:] + (mc,)) \
        if count_kind(r)[0] != "atleast" else ("atleast", r["num"], r["den"], 0)
    # CC 3.1.3.2: "The count that enacts it is the protocol's": a declared protocol overrides the row's enact fraction
    enact = declared_enact if declared_enact is not None else how(row["enact_rule"])
    at_once, at_close = [("approve", enact, "all", "landed")], []
    c = row["cancel_rule"]
    if c["kind"] == "strict_majority_of_others": at_once.append(("object", "strict", "others", "refused"))
    elif c["kind"] == "fraction": at_close.append(("object", ("atleast", c["num"], c["den"], mc), "all", "refused"))
    f = row["floor_rule"]
    default = "refused"
    if f["kind"] == "one_of_n": default = "landed"
    elif f["kind"] == "fraction" and row["reverse_path"]: at_close.append(("approve", ("atleast", f["num"], f["den"], mc), "all", "landed"))
    silent = "refused" if evict and row["counted"]["target_silent"]["value"] == "yes" else None
    WN.WINDOWS[name] = {"policy": family, "counted": counted, "concluder": counted, "opener_says": "approve",
                        "at_once": tuple(at_once), "silent": silent, "at_close": tuple(at_close), "default": default}
    return name


# ---- the parameters -------------------------------------------------------------------------------------
class Spec:
    def __init__(self, name, obj, scope, add, remove, counted=None, unit="key", floor=1, consent="own", lone=None,
                 margin=0, need=None, recovery=False, body=None, witnessed=False, protocol_name=None, tables=(), note=""):
        self.name, self.obj, self.scope, self.add, self.remove = name, obj, scope, add, remove
        self.counted = counted or scope
        self.unit, self.floor, self.consent, self.lone = unit, floor, consent, dict(lone or {})
        self.margin, self.need, self.recovery, self.body, self.witnessed = margin, need, recovery, body, witnessed
        self.protocol_name, self.tables, self.note = protocol_name, tables, note

    def params(self):
        kind = lambda p: ST.POLICY.get(p)
        lone = {k: (WN.WINDOWS[v]["at_once"], WN.WINDOWS[v]["at_close"], WN.WINDOWS[v]["silent"], WN.WINDOWS[v]["default"],
                    TABLE[WN.WINDOWS[v]["policy"]]["window_secs"]) for k, v in self.lone.items()}
        return {"member": self.unit, "seat": self.scope, "counted over": self.counted, "add": kind(self.add),
                "remove": kind(self.remove), "need (quorum M)": self.need, "floor (voices)": self.floor,
                "joiner consents": self.consent, "lone path": lone or None, "margin": self.margin,
                "own recovery version": self.recovery, "conferring body": self.body, "witnessed lineage": self.witnessed}


SPECS = {}          # obj -> Spec: the rule is one function; a row finds its parameters through the object it is on


def instances(protocol="majority", private=False):
    """The five instances, from the table's own rows. `protocol` is a community's declared consensus_protocol."""
    S = {}
    # 1. a person's keys: self_roster_add / self_roster_evict (CC 3.3.6.3)
    a = register("R:self_add", count_kind(TABLE["self_roster_add"]["enact_rule"]))
    e = register("R:self_evict", count_kind(TABLE["self_roster_evict"]["enact_rule"]))
    S["self"] = Spec("self", "S", "self", a, e, floor=MIN_COUNT["self"], unit="key",
                     lone={"add": window_from_table("L:self_add", "self_roster_add", "self", False),
                           "evict": window_from_table("L:self_evict", "self_roster_evict", "self", True)},
                     tables=("self_roster_add", "self_roster_evict"))
    # 2. a voice's room keys: no row of its own; CC 3.1.3.2 "as a key of a self roster is" -> the self rows
    S["voice"] = Spec("voice", "vA", "key", a, e, floor=MIN_COUNT["self"], unit="key",
                      lone={"add": window_from_table("L:voice_add", "self_roster_add", "key", False),
                            "evict": window_from_table("L:voice_evict", "self_roster_evict", "key", True)},
                      tables=("(none: self_roster_add, self_roster_evict by CC 3.1.3.2)",))
    # 3. a community, public or private: community_invite / community_remove; the count is the declared protocol
    decl = PROTOCOLS[protocol.split(":")[0]]
    need = int(protocol.split(":")[1]) if protocol.startswith("quorum") else None
    ci = register("R:community_add:" + protocol, decl)
    cr = register("R:community_remove:" + protocol, decl)
    enact = {"strict": "strict", "one": "one"}.get(decl[0], ("atleast",) + decl[1:] + (0,))
    S["community"] = Spec("private room" if private else "community", "g", "member", ci, cr, floor=MIN_COUNT["community"],
                          unit="voice" if private else "person", need=need, protocol_name=protocol,
                          lone={"add": window_from_table("L:community_add:" + protocol, "community_invite", "member", False, enact)},
                          tables=("community_invite", "community_remove", "cosigned_act"))
    # 4. the accord's holders: accord_majority for every roster change; accord_halt is the fire (a window, not a version)
    am = register("R:accord", count_kind(TABLE["accord_majority"]["enact_rule"]))
    S["accord"] = Spec("accord", "A", "holder", am, am, unit="person", floor=1, recovery=True,
                       tables=("accord_majority", "accord_halt"))
    # 5. an infrastructure community: the founders' quorum:M/N (cosigned_act, protocol), nodes seated without consent
    iq = register("R:infra", ("declared", 0, 0))
    S["infra"] = Spec("infra", "I", "member", iq, iq, counted="founder", unit="person", floor=MIN_COUNT["community"], need=2,
                      margin=1, body="BODY", witnessed=True, protocol_name="quorum:2/3", tables=("cosigned_act",))
    for s in S.values(): SPECS[s.obj] = s
    return S


# ---- rows ---------------------------------------------------------------------------------------------------
def found(spec, keys, scope=None, **kw):
    keys = tuple(keys)
    return ST.offer(spec.obj, keys[0], keys, scope or spec.scope, "@", "self", cosigners=keys[1:], **kw)


def add(spec, id, head, k, signers, names=(), scope=None, **kw):
    """A counted version adding k over `head` (a tuple of heads). The joiner's consent is a standing acceptance
    the version names (the widening names the acceptance), or k cosigning (a self roster's new key signs)."""
    head = tuple(head) if not isinstance(head, str) else (head,)
    signers = tuple(signers)
    return ST.offer(id, signers[0], k, scope or spec.scope, spec.obj, "group", head + tuple(names), head=head,
                    policy=spec.add, counted=spec.counted, cosigners=signers[1:], need=spec.need, **kw)


def accept(spec, id, k, names=(), scope=None):
    return ST.accept(id, k, None, tuple(names) or (spec.obj,), scope=scope or spec.scope, obj=spec.obj)


def remove(spec, id, head, k, signers, names=(), scope=None, **kw):
    """A counted version removing k. Returns a list: under a declared quorum the cosignatures are cosign rows the
    removal names (cut.py reads `need` as distinct live voices among those rows), otherwise one row."""
    head = tuple(head) if not isinstance(head, str) else (head,)
    signers = tuple(signers)
    if spec.need is None:
        return [ST.unseat(id, signers[0], k, scope or spec.scope, spec.obj, "group", head + tuple(names), head=head,
                          policy=spec.remove, counted=spec.counted, cosigners=signers[1:], **kw)]
    cos = [ST.cosign("%s~%s" % (id, s), s, id, head) for s in signers[1:]]
    return cos + [ST.unseat(id, signers[0], k, scope or spec.scope, spec.obj, "group", head + tuple(c["id"] for c in cos) + tuple(names),
                            head=head, policy=spec.remove, counted=spec.counted, need=spec.need, content=id, **kw)]


def lone_open(spec, id, signer, act, head, target, names=()):
    p = WN.opener(id, signer, spec.lone[act], spec.obj, tuple(head), target=target, names=names)
    p["act"] = act
    return p


def effect(spec, id, signer, landing, p, names=()):
    """The version a standing lone landing makes: a counted act (conf=group) whose authority is the landing."""
    mk = ST.unseat if p["act"] == "evict" else ST.offer
    names = (landing,) + tuple(n for n in names if n != landing)
    r = mk(id, signer, p["target"], spec.scope, spec.obj, "group", names, head=tuple(p["head"]), counted=spec.counted)
    r["via"], r["of"] = landing, p["id"]
    return r


def recovery(spec, id, rkey, holder, new, head, names=()):
    """A holder's own recovery version: one row under the committed recovery key, replacing the holder's seat."""
    head = tuple(head)
    u = ST.unseat(id + "-", rkey, holder, spec.scope, spec.obj, "group", head + tuple(names), head=head, counted=spec.counted)
    o = ST.offer(id, rkey, new, spec.scope, spec.obj, "group", head + (id + "-",) + tuple(names), head=head,
                 counted=spec.counted, cosigners=(new,))
    for r in (u, o): r["recovery_of"] = holder
    return [u, o]


def body_widening(spec, id, body, k, head, names=()):
    """T7: the one row a stalled infrastructure roster admits without the founders' count."""
    head = tuple(head)
    r = ST.offer(id, body, k, "founder", spec.obj, "group", head + tuple(names), head=head, counted=spec.counted,
                 cosigners=(k,))
    r["by_body"] = True
    return r


def speak(spec, id, signer, head, names=(), **kw):
    head = tuple(head)
    return R(id, "speak", signer, head + tuple(n for n in names if n not in head), obj=spec.obj, head=head,
             on=(("seat", signer, spec.scope, spec.obj),), **kw)


def by_dev(row, dev, vhead):
    """A row of a nested member: signer is the member (a voice, a person); dev the key that signed; vhead the head of the
    member's own roster it relies on (roomkey.by_dev)."""
    return dict(row, dev=dev, vhead=tuple(vhead), names=tuple(row["names"]) + tuple(h for h in vhead if h not in row["names"]))


# ---- the conclusion rule: the kernel's, and the parameters ------------------------------------------------
MUT = set()       # named mutations, switched on by the check
PARAMS = set()    # stated parameters a check may switch on to see whether they restore a property


def _recovery_commit(P, obj):
    g = next((q for q in P if q["id"] == obj), None)
    return (g or {}).get("recovery", {})


def rule(r, P, past):
    if "dev" in r and r["dev"] not in ST.members_at(P, past, r["signer"], r["vhead"], "key"):
        return False                                                   # a nested member speaks only through a live key
    spec = SPECS.get(r.get("obj"))
    by = {q["id"]: q for q in P}
    if r["kind"] == "open" and spec is not None and "persons_only" in PARAMS:
        g = by.get(r["obj"])                                           # CC 3.3.6.3: "The door is a person's"
        if g is not None and g.get("identity_type", "user") != "user": return False
    if r.get("via"):                                                   # the effect of a lone landing
        L, p = by.get(r["via"]), by.get(r.get("of"))
        if L is None or p is None or L["kind"] != "landing" or L["of"] != p["id"] or L["says"] != "landed": return False
        if p.get("act") != ("evict" if r["kind"] == "unseat" else "add") or p["obj"] != r["obj"]: return False
        if "lone_any_target" not in MUT and tuple(r["to"]) != (p["target"],): return False
        return L["signer"] == r["signer"]
    if r.get("recovery_of") is not None and r["kind"] in ("offer", "unseat"):
        if "no_recovery" in MUT: return False
        commit = _recovery_commit(P, r["obj"])
        if commit.get(r["recovery_of"]) != r["signer"]: return False
        if r["kind"] == "unseat":
            return "recovery_any_seat" in MUT or tuple(r["to"]) == (r["recovery_of"],)
        prior = [q for q in P if q["kind"] == "unseat" and q.get("recovery_of") == r["recovery_of"] and q["id"] in r["names"]]
        return bool(prior) and len(r["to"]) == 1
    if r.get("by_body"):
        if spec is None or r["signer"] != spec.body or r["kind"] != "offer" or r["scope"] != "founder": return False
        if r["to"][0] not in ST.signers(r): return False              # the conferred key signs it
        live = ST.members_at(P, past, r["obj"], r["head"], spec.counted)
        return "body_any_time" in MUT or len(live) <= spec.need       # only while stalled
    if r["kind"] == "speak":                                           # a row of the object's own: speech, a vote, a note
        sp = SPECS.get(r["obj"])
        return r["signer"] in ST.members_at(P, past, r["obj"], r["head"], sp.scope if sp else "member")
    # ---- mutations of the check (each must be caught); none is on unless MUT names it
    if r["kind"] == "withdraw" and "decline_ignored" in MUT: return False
    if ("enact_over_others" in MUT and spec is not None and r["kind"] == "offer" and r.get("conf") == "group"
            and r["id"] != r["obj"] and not r.get("via") and not r.get("by_body") and r.get("recovery_of") is None):
        others = ST.members_at(P, past, r["obj"], r.get("head", ()), spec.counted) - {r["signer"]}
        return 2 * len((ST.voices(r, P) - {r["signer"]}) & others) > len(others)
    if spec is not None and r["kind"] in ("offer", "unseat") and r.get("conf") == "group" and r["id"] != r["obj"]:
        if "self_admit" in MUT and r["kind"] == "offer" and r["signer"] in r["to"]: return True
        if "live_set" in MUT and spec.name == "accord":                # a majority of those who took part, not of the standing roster
            mem = ST.members_at(P, past, r["obj"], r.get("head", ()), spec.counted)
            v = ST.voices(r, P) & mem
            live = v | {q["signer"] for q in P if q["kind"] == "participate" and q.get("of") == r.get("proposal")}
            return 2 * len(v) > len(live & mem)
    ok = WN.rule(r, P, past)
    if ok and "spent" in PARAMS and r["kind"] == "offer" and r.get("conf") == "group" and r["id"] != r.get("obj"):
        # CC 3.1.3.2 admission (5): an acceptance is spent by the widening that seats it
        for a in K.sel(P, kind="accept"):
            if a["id"] not in r["names"] or a["signer"] not in r["to"]: continue
            used = [q for q in P if q["kind"] == "offer" and a["id"] in q["names"] and a["signer"] in q["to"]]
            # spent = the key left after being seated on it (a merge that restates a tip's seat re-seats nobody)
            left = [w for w in P if (w["kind"] == "withdraw" and w["signer"] == a["signer"] and w["target"] in {q["id"] for q in used} | {a["id"]})
                    or (w["kind"] == "unseat" and a["signer"] in w["to"])]
            if any(past(q["id"], w["id"]) for q in used for w in left): return False
    if not ok or spec is None or r["kind"] not in ("offer", "unseat") or r.get("conf") != "group": return ok
    if r["id"] == r["obj"]: return ok
    mem = ST.members_at(P, past, r.get("over", r["obj"]), r.get("head", ()), r.get("counted", spec.counted)) \
        - ST.left_in_past(P, r.get("over", r["obj"]), r.get("counted", spec.counted))      # a key that left in the version's past
    v = ST.voices(r, P) & mem
    if r["kind"] == "offer":
        acc = [a for a in K.sel(P, kind="accept") if a["id"] in r["names"] and a["signer"] in r["to"]]
        if acc or set(r["to"]) & ST.signers(r): v = v | set(r["to"])  # the joiner's own yes is a voice of the floor
    if "no_floor" not in MUT and len(v) < spec.floor: return False
    if spec.margin and "no_margin" not in MUT and len(mem) < (spec.need or 0) + spec.margin: return False
    return ok


# ---- derived: the roster ----------------------------------------------------------------------------------
def settle(S0):
    """Stage two of the derived layer: an effect row stands only if its landing stands under RECOUNT."""
    C = dict(S0.C)
    # the window is recounted without the effects of lone landings: an eviction's own effect must not silence its target
    # effects are settled in order of ancestry; while one is judged, it and every effect not yet settled are left out
    eff = sorted([r for r in S0.rows if r.get("via")], key=lambda r: len(S0.anc[r["id"]]))
    pending = {r["id"] for r in eff}
    for r in eff:
        if C.get(r["id"]):
            bare = CK.State(S0.rows, {i: c and i not in pending and not (S0.by[i].get("via") and S0.by[i]["of"] == r["of"])
                                      for i, c in C.items()})
            how = "void" if "lone_void" in MUT else "recount"
            if WN.outcome(bare, r["of"], how) != "landed": C[r["id"]] = False
        pending.discard(r["id"])
    for r in S0.rows:                                    # a row built on an effect that does not stand concludes nothing
        if C.get(r["id"]) and any(not C.get(a, True) and S0.by[a].get("via") for a in S0.anc[r["id"]]):
            C[r["id"]] = False
    return CK.State(S0.rows, C)


def state(rows):
    return settle(CK.concluded(CK.kept(rows), rule))


def arrived(order):
    return settle(CK.arrive(order, rule))


def roster(S, spec, scope=None):
    return ST.Seats(S).holders(scope or spec.scope, spec.obj)


def snapshot(S, spec, windows=()):
    return (frozenset(S.C.items()), roster(S, spec), frozenset(CUT.Cut(S).all().items()),
            tuple(WN.outcome(S, p, "recount") for p in windows))


def linear_extensions(rows, cap=5000):
    """Every distinct order in which a node can come to hold `rows` (an arrival order is held as the rows' names
    allow; two arrival orders that make rows held in the same sequence give the same state)."""
    ids = [r["id"] for r in rows]
    by = {r["id"]: r for r in rows}
    out, seq = [], []
    def go(held):
        if len(out) >= cap: return
        if len(seq) == len(ids):
            out.append([by[i] for i in seq]); return
        for i in ids:
            if i not in held and all(n in held or n not in by for n in by[i]["names"]):
                seq.append(i); held.add(i); go(held); held.discard(i); seq.pop()
    go(set())
    return out


# ---- the fork run of KERNEL section 7, under each instance's count --------------------------------------
def fork_protocol(spec):
    k = ST.POLICY[spec.add]
    if k[0] == "strict": return "majority"
    if k[0] == "atleast" and k[1:] == (2, 3): return "two_thirds"
    if k[0] == "declared": return "quorum%d" % spec.need
    if k[0] == "one": return "founder_only"
    raise ValueError(k)
