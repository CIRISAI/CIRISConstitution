"""
window.py: a window as rows.

    open      row p opens the window. It names the head it is counted over, and (for an eviction) its target.
    answer    a row naming p that says something the window's table counts: approve, object, confirm, answered, act.
    receipt   a key with the concluder's seat signs that it holds p, stating its own instant.
    landing   the same key names its receipt and the head it then holds, states its own instant and the outcome.

"Inside the window" is a relation between rows: in the past of the landing and not in the past of the receipt.
The duration is the concluder's own two instants (landing.at - receipt.at >= secs); no instant of one signer is
compared with another's. A landing is CONCLUDED iff its signer held the concluder's seat at the head p names, it
names its own receipt, and the outcome it states is the one the window's table gives over its own past. A landing
that states another outcome concludes nothing, for every reader, in every order.

The landing is a cut on p's slot. What is left open is a row that answers p (or, where the table asks for the
target's silence, any row the target signed) and is CONCURRENT with the landing. Three rules, all run:

    void      (i)   the cut voids it: the landing stands (cut.py, unchanged)
    contest   (ii)  any such row contests the landing: it does not count until a landing names both
    recount   (ii, narrowed) such rows are counted with the landing's past; the landing stands iff the table then
              gives the outcome it states, and is contested otherwise

A row that NAMES the landing is judged at the head it names under every rule: it came after and changes nothing.
Concurrency is the signer's own word: a key can always leave the landing unnamed.

Under recount two things bound that word.
    ended seat   a row of a key whose seat over the object was ended (a counting unseat, or a withdrawal of the offer
                 that seated it) is counted only if the ending row has it in its past (KERNEL.md section 6).
    standing     a landing that does not stand says nothing against a landing that does: the outcome is contested only
                 when no frontier landing stands, or two that stand state different outcomes.

The checkpoint (checkpoint.py) is NOT applied to a window's answers. A window protects one voice against the count,
and a checkpoint is made by the count: with it on, a majority voids a present moderator's timely answer by signing
counted rows that leave it unnamed (attacks.py, checkpoint_price). `outcome(..., checkpoint=True)` exists only to
show that witness.

The three windows are data (WINDOWS): the policy row of manifests/governance_policy.json, the clauses that close
the window at once, the clauses read at the close, and the default.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import seat as ST  # noqa: E402
import checkpoint as CP  # noqa: E402

CK, CUT, K, R = ST.CK, ST.CUT, ST.K, ST.R

# value said, threshold, over which base, outcome
WINDOWS = {
    # formal/self_roster, CC 3.3.6.3: a strict majority of the roster lands it at once (the proposer approves);
    # a strict majority of the others refuses it; alone it lands at the close, and only if the target was silent
    "self_roster_evict": {"policy": "self_roster_evict", "counted": "self", "concluder": "self", "opener_says": "approve",
                          "at_once": (("approve", "strict", "all", "landed"), ("object", "strict", "others", "refused")),
                          "silent": "refused", "at_close": (), "default": "landed"},
    # CC 4.5.13: a moderator answers within 48 h; on their absence a live majority of the members acts
    "moderation_fallback": {"policy": "moderation_action", "counted": "member", "concluder": "member", "opener_says": None,
                            "at_once": (("answered", "one", "moderate", "answered"),),
                            "silent": None, "at_close": (("act", "strict", "all", "fallback"),), "default": "lapsed"},
    # CC 4.2.1.1: one holder fires at once; the halt lapses at the fuse unless a strict majority confirms
    "halt_fuse": {"policy": "accord_halt", "counted": "holder", "concluder": "holder", "opener_says": "confirm",
                  "at_once": (("confirm", "strict", "all", "confirmed"),),
                  "silent": None, "at_close": (), "default": "lapsed"},
}
SECS = None


def secs(name):
    """The window's length, from the policy table."""
    global SECS
    if SECS is None:
        import json
        fam = json.load(open(os.path.join(ROOT, "manifests", "governance_policy.json"), encoding="utf-8"))["families"]
        SECS = {f["family"]: f["window_secs"] for f in fam}
    return SECS[WINDOWS[name]["policy"]]


# ---- rows ----------------------------------------------------------------------------------------------
def opener(id, signer, window, obj, head, target=None, names=()):
    return R(id, "open", signer, tuple(names) + tuple(h for h in head if h not in names), window=window, obj=obj,
             head=tuple(head), target=target, slot=("win", id))


def answer(id, signer, p, says, names=()):
    return R(id, "answer", signer, tuple(names) + ((p,) if p not in names else ()), of=p, says=says, on=(("win", p),))


def receipt(id, signer, p, at):
    return R(id, "receipt", signer, (p,), of=p, at=at)


def landing(id, signer, p, rec, says, at, names=()):
    return R(id, "landing", signer, tuple(names) + ((rec,) if rec not in names else ()), of=p, receipt=rec, says=says,
             at=at, cuts=(("win", p),))


# ---- the table -----------------------------------------------------------------------------------------
def table_outcome(spec, p, answers, inside, base, elapsed):
    """The outcome the table gives. answers: rows answering p; inside: rows read for the target's silence;
    base(name) -> the keys counted; elapsed: whether the concluder's two instants span the window."""
    tv = {p["target"]} if spec.get("target_votes") else set()   # the joiner's own yes is a voice of the floor (CC 3.1.3.2)
    said = K.group([a for a in answers if a["signer"] in base("all") | base("moderate") | tv], "signer", "one", "says")
    if spec["opener_says"]: said.setdefault(p["signer"], spec["opener_says"])       # a voice that says two things says nothing
    def count_met(value, how, over, floor=False):
        keys = base(over)
        yes = K.group([{"k": s} for s, v in said.items() if v == value and (s in keys or (floor and s in tv and value == "approve"))], None, "count", "k")
        if isinstance(how, tuple):               # a threshold read off the policy table
            kind, num, den, least = how          # ("atleast", n, d, min): >= max(min, ceil(n*N/d)); ("more", n, d, 0): > n/d
            if kind == "atleast": return yes >= max(least, -(-num * len(keys) // den))
            return yes * den > num * len(keys)
        return yes >= 1 if how == "one" else 2 * yes > len(keys)
    for value, how, over, out in spec["at_once"]:
        if count_met(value, how, over): return out
    if not elapsed: return "open"
    if spec["silent"] and K.sel(inside, signer=p["target"]): return spec["silent"]
    for value, how, over, out in spec["at_close"]:
        if count_met(value, how, over, floor=True): return out
    return spec["default"]


def _base(rows, past, p):
    spec = WINDOWS[p["window"]]
    cache = {}
    def base(name):
        if name not in cache:
            scope = spec["counted"] if name in ("all", "others") else name
            m = ST.members_at(rows, past, p["obj"], p["head"], scope)
            cache[name] = m - {p["signer"]} if name == "others" else m
        return cache[name]
    return base


def rule(r, P, past):
    """The conclusion rule: window rows here, every other row by seat.seat_rule."""
    k = r["kind"]
    if k not in ("open", "answer", "receipt", "landing"):
        return ST.seat_rule(r, P, past)
    by = {q["id"]: q for q in P}
    if k == "open":
        return r["signer"] in ST.members_at(P, past, r["obj"], r["head"], WINDOWS[r["window"]]["counted"])
    p = by.get(r["of"])
    if p is None or p["kind"] != "open": return False
    if k == "answer": return True                              # whether its voice counts is read against the roster at p's head
    spec, base = WINDOWS[p["window"]], _base(P, past, p)
    if r["signer"] not in ST.members_at(P, past, p["obj"], p["head"], spec["concluder"]): return False
    if k == "receipt": return True
    rec = by.get(r["receipt"])
    if rec is None or rec["kind"] != "receipt" or rec["signer"] != r["signer"] or rec["of"] != p["id"]: return False
    answers = K.sel(P, kind="answer", of=p["id"])
    inside = [q for q in P if q["id"] != rec["id"] and not past(q["id"], rec["id"])]
    return r["says"] == table_outcome(spec, p, answers, inside, base, r["at"] - rec["at"] >= secs(p["window"]))


# ---- derived: the outcome of a window under each rule ----------------------------------------------------
def outcome(S, pid, how, by_arrival=False, checkpoint=False):
    """how: void | contest | recount. Returns the outcome, "open" (no landing counts yet) or "contested"."""
    p = S.by.get(pid)
    if p is None or not S.C.get(pid): return "none"
    spec = WINDOWS[p["window"]]
    Ls = K.sel(S.Cs, kind="landing", of=pid)
    if not Ls: return "open"
    if how == "void":
        C = CUT.Cut(S)                                          # the landing is a cut on p's slot; only landings speak on it
        st = {L["id"]: C.status(L) for L in Ls}
        said = [{"v": L["says"]} for L in K.frontier(S.anc, [L for L in Ls if st[L["id"]] == "counts"])]
        if "contested" in st.values() or not said: return "contested"
        return K.group(said, None, "one", "v") or "contested"
    past = lambda a, b: a in S.anc[b]
    base = _base(S.Cs, past, p)
    pos = {r["id"]: i for i, r in enumerate(S.rows)}
    late = lambda r: False
    if how == "recount":
        C = CUT.Cut(S)
        # the rows that ended a seat over the object, with the keys each ended
        gone = [(frozenset(u["to"]), u) for u in K.sel(S.Cs, kind="unseat") if u["obj"] == p["obj"] and C.counts(u)]
        for w in K.sel(S.Cs, kind="withdraw"):
            o = S.by.get(w["target"])
            if o is not None and o["kind"] == "offer" and o["obj"] == p["obj"]:
                gone.append((frozenset({w["signer"]}) if w["signer"] in o["to"] else frozenset(o["to"]), w))
        cps = CP.checkpoints(S, C, p["obj"], group=True) if checkpoint else []   # off by default: see the module's head
        late = lambda r: any(r["signer"] in ks and r["id"] not in S.anc[x["id"]] for ks, x in gone) or CP.stale_answer(S, cps, p, r)
    said = []
    for L in K.frontier(S.anc, Ls):                             # a landing that a later landing names is answered by it
        # MUTATION by_arrival: "concurrent" read as "arrived after the landing", by list position
        conc = [r for r in S.Cs if (pos[r["id"]] > pos[L["id"]] and L["id"] not in S.anc[r["id"]]) if by_arrival] if by_arrival else \
               [r for r in S.Cs if S.concurrent(r["id"], L["id"])]
        conc = [r for r in conc if not late(r)]
        ans = [r for r in K.sel(conc, kind="answer", of=pid) if r["signer"] in base("all") | base("moderate") | ({p["target"]} if spec.get("target_votes") else set())]
        tgt = K.sel(conc, signer=p["target"]) if spec["silent"] else []
        if how == "contest":
            said.append({"v": "contested" if ans or tgt else L["says"]})
        else:
            rec = S.by[L["receipt"]]
            mine = [q for q in S.Cs if q["id"] in S.anc[L["id"]]]
            inside = [q for q in mine if q["id"] != rec["id"] and q["id"] not in S.anc[rec["id"]]] + tgt
            again = table_outcome(spec, p, K.sel(mine, kind="answer", of=pid) + ans, inside, base, L["at"] - rec["at"] >= secs(p["window"]))
            said.append({"v": L["says"] if again == L["says"] else "contested"})
    if how == "recount" and any(x["v"] != "contested" for x in said):
        said = [x for x in said if x["v"] != "contested"]       # a landing that does not stand is no voice against one that does
    return K.group(said, None, "one", "v") or "contested"


RULES = ("void", "contest", "recount")


def outcomes(S, pid, **kw):
    return {h: outcome(S, pid, h, **kw) for h in RULES}


# ---- the three windows, and the adversary in each --------------------------------------------------------
DAY = 86400


def self_world():
    g = ST.offer("g", "d1", ("d1", "d2", "d3"), "self", "@", "self", cosigners=("d2", "d3"))
    W = secs("self_roster_evict")
    thief_p = opener("p", "d3", "self_roster_evict", "g", ("g",), target="d1")       # the thief holds d3
    own_p = opener("p", "d1", "self_roster_evict", "g", ("g",), target="d2")         # the owner holds d1 only
    q_p = opener("p", "d1", "self_roster_evict", "g", ("g",), target="d3")           # the owner holds d1 and d2
    cases = [
        # name, rows, who gains, property read, the outcome the property needs
        ("false landing: the thief (one device of three) lands an eviction of the owner's device; the owner's two devices objected and the landing leaves them unnamed",
         [g, thief_p, receipt("r", "d3", "p", 0), answer("o1", "d1", "p", "object"), answer("o2", "d2", "p", "object"),
          landing("L", "d3", "p", "r", "landed", W)], "thief cannot evict alone", "not landed"),
        ("false landing, stated falsely: the same landing naming the objections",
         [g, thief_p, receipt("r", "d3", "p", 0), answer("o1", "d1", "p", "object"), answer("o2", "d2", "p", "object"),
          landing("L", "d3", "p", "r", "landed", W, ("o1", "o2"))], "thief cannot evict alone", "not landed"),
        ("false landing, early: the thief lands before its own window has run",
         [g, thief_p, receipt("r", "d3", "p", 0), landing("L", "d3", "p", "r", "landed", W - 1)], "thief cannot evict alone", "not landed"),
        ("withheld row: the target used its device in the window (a row that is no objection) and a relay kept it from everyone until after the landing",
         [g, thief_p, receipt("r", "d3", "p", 0), R("n1", "note", "d1", ("g",)), landing("L", "d3", "p", "r", "landed", W)],
         "thief cannot evict alone", "not landed"),
        ("the owner is away the whole window and signs nothing; the thief lands",
         [g, thief_p, receipt("r", "d3", "p", 0), landing("L", "d3", "p", "r", "landed", W)], "(the stated residual: an absent owner looks lost)", None),
        ("objection signed just after, naming the landing: the owner returns and objects honestly",
         [g, thief_p, receipt("r", "d3", "p", 0), landing("L", "d3", "p", "r", "landed", W), answer("o1", "d1", "p", "object", ("L",)),
          answer("o2", "d2", "p", "object", ("L",))], "(what an honest late objection is worth)", None),
        ("objection signed just after, leaving the landing unnamed: the owner returns and objects with both devices",
         [g, thief_p, receipt("r", "d3", "p", 0), landing("L", "d3", "p", "r", "landed", W), answer("o1", "d1", "p", "object"),
          answer("o2", "d2", "p", "object")], "thief cannot evict alone", "not landed"),
        ("a second landing naming both: after the thief's landing, the owner's second device lands 'refused', naming the landing and the objections",
         [g, thief_p, receipt("r", "d3", "p", 0), answer("o1", "d1", "p", "object"), answer("o2", "d2", "p", "object"),
          landing("L", "d3", "p", "r", "landed", W), receipt("r2", "d2", "p", 0), landing("L2", "d2", "p", "r2", "refused", 0, ("L", "o1", "o2"))],
         "a row naming both decides", "refused"),
        ("lost device: the owner holds one of three and evicts a lost device, which signs nothing",
         [g, own_p, receipt("r", "d1", "p", 0), landing("L", "d1", "p", "r", "landed", W)], "lost device cannot veto", "landed"),
        ("silent stolen device: the same eviction; the target is held by a thief who signs a row after the landing and leaves it unnamed",
         [g, own_p, receipt("r", "d1", "p", 0), landing("L", "d1", "p", "r", "landed", W), R("n2", "note", "d2", ("g",))],
         "(a device that can still sign is not lost)", None),
        ("quorum: the owner's two devices evict the stolen one at once; the thief objects, concurrent with the landing",
         [g, q_p, answer("a2", "d2", "p", "approve"), receipt("r", "d1", "p", 0), landing("L", "d1", "p", "r", "landed", 0, ("a2",)),
          answer("o3", "d3", "p", "object")], "an active thief is evicted by the count", "landed"),
    ]
    return "self roster, lone eviction (24 h, target silent)", cases


def moderation_world():
    g = ST.offer("g", "m1", ("m1", "m2", "m3"), "duty", "@", "self", cosigners=("m2", "m3"))     # three duty holders (CC 4.5.4)
    md = ST.offer("md", "m1", "MOD", "moderate", "g", "group", ("g",), head=("g",), policy="duty_confer", counted="duty",
                  cosigners=("m3", "MOD"))                                     # two of the three confer, MOD accepting
    W = secs("moderation_fallback")
    p = opener("p", "m2", "moderation_fallback", "g", ("md",))
    acts = [answer("x1", "m1", "p", "act"), answer("x3", "m3", "p", "act")]
    A = answer("A", "MOD", "p", "answered")
    base = [g, md, p, receipt("r", "m2", "p", 0)] + acts
    L = landing("L", "m2", "p", "r", "fallback", W, ("x1", "x3"))
    cases = [
        ("false landing: a member lands the members' moderation; the moderator had answered and the landing leaves the answer unnamed",
         base + [A, L], "present moderator is not overridden", "not fallback"),
        ("false landing, stated falsely: the same landing naming the moderator's answer",
         base + [A, landing("L", "m2", "p", "r", "fallback", W, ("x1", "x3", "A"))], "present moderator is not overridden", "not fallback"),
        ("false landing, no count: one member lands the fallback alone",
         [g, md, p, receipt("r", "m2", "p", 0), landing("L", "m2", "p", "r", "fallback", W)], "the fallback needs the members' majority", "not fallback"),
        ("withheld answer: an honest member lands; a relay had kept the moderator's answer from the room",
         base + [A, L], "present moderator is not overridden", "not fallback"),
        ("a second landing naming both: another member lands 'answered', naming the first landing and the moderator's answer",
         base + [A, L, receipt("r2", "m1", "p", 0), landing("L2", "m1", "p", "r2", "answered", 0, ("L", "A"))],
         "a row naming both decides", "answered"),
        ("absent moderator: nobody answers in 48 h and the members' majority acts",
         base + [L], "the fallback works when the moderator is absent", "fallback"),
        ("answer signed just after, naming the landing: the moderator returns and answers honestly",
         base + [L, answer("A", "MOD", "p", "answered", ("L",))], "(what an honest late answer is worth)", None),
        ("answer signed just after, leaving the landing unnamed: the moderator returns late",
         base + [L, A], "(a late moderator against the members' act)", None),
    ]
    return "moderation fallback (48 h, absent moderator, members' majority)", cases


def halt_world():
    g = ST.offer("g", "h1", ("h1", "h2", "h3"), "holder", "@", "self", cosigners=("h2", "h3"))
    W = secs("halt_fuse")
    p = opener("p", "h1", "halt_fuse", "g", ("g",))
    c2 = answer("c2", "h2", "p", "confirm")
    cases = [
        ("false landing: the halting holder lands 'confirmed' with no other voice",
         [g, p, receipt("r", "h1", "p", 0), landing("L", "h1", "p", "r", "confirmed", W)], "one holder cannot keep agents stopped alone", "not confirmed"),
        ("the lone halt lapses: nobody confirms; another holder lands the lapse at the fuse",
         [g, p, receipt("r", "h2", "p", 0), landing("L", "h2", "p", "r", "lapsed", W)], "one holder cannot keep agents stopped alone", "lapsed"),
        ("objection signed just after, unnamed: the lapse lands; the halting holder signs a further confirm and leaves the landing unnamed",
         [g, p, receipt("r", "h2", "p", 0), landing("L", "h2", "p", "r", "lapsed", W), answer("c1", "h1", "p", "confirm")],
         "one holder cannot keep agents stopped alone", "lapsed"),
        ("false landing: a holder lands 'lapsed' on a halt a strict majority confirmed, leaving the confirm unnamed",
         [g, p, c2, receipt("r", "h3", "p", 0), landing("L", "h3", "p", "r", "lapsed", W)], "one holder cannot lift a confirmed halt alone", "not lapsed"),
        ("withheld confirm: an honest holder lands the lapse; a relay had kept the confirming voice from it",
         [g, p, c2, receipt("r", "h3", "p", 0), landing("L", "h3", "p", "r", "lapsed", W)], "one holder cannot lift a confirmed halt alone", "not lapsed"),
        ("a second landing naming both: the confirming holder lands 'confirmed', naming the false lapse and its own confirm",
         [g, p, c2, receipt("r", "h3", "p", 0), landing("L", "h3", "p", "r", "lapsed", W), receipt("r2", "h2", "p", 0),
          landing("L2", "h2", "p", "r2", "confirmed", 0, ("L", "c2"))], "a row naming both decides", "confirmed"),
        ("confirm signed just after, naming the landing: a second holder confirms honestly after the lapse",
         [g, p, receipt("r", "h3", "p", 0), landing("L", "h3", "p", "r", "lapsed", W), answer("c2", "h2", "p", "confirm", ("L",))],
         "(what an honest late confirm is worth)", None),
        ("confirm signed just after, unnamed: a second holder confirms after the lapse and leaves the landing unnamed",
         [g, p, receipt("r", "h3", "p", 0), landing("L", "h3", "p", "r", "lapsed", W), c2], "(a late majority against the lapse)", None),
    ]
    return "halt fuse (24 h, lapses unless a strict majority confirms)", cases


WORLDS = (self_world, moderation_world, halt_world)


def holds(need, got):
    if need is None: return None
    return (got != need[4:]) if need.startswith("not ") else (got == need)


def adversary_table():
    """One line per (window, case): the outcome under each rule, and whether the property the case reads holds."""
    out = []
    for world in WORLDS:
        title, cases = world()
        for name, rows, prop, need in cases:
            S = CK.concluded(CK.kept(rows), rule)
            o = outcomes(S, "p")
            landed = [r["id"] for r in K.sel(S.rows, kind="landing") if S.C[r["id"]]]
            out.append({"window": title, "case": name, "property": prop, "needs": need, "landing_concluded": bool(landed),
                        "outcome": o, "holds": {h: holds(need, o[h]) for h in RULES}})
    return out


if __name__ == "__main__":
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
    last = None
    for t in adversary_table():
        if t["window"] != last: print("\n" + t["window"]); last = t["window"]
        print("  %s\n      landing concluded: %-5s  %s\n      %s: %s" % (
            t["case"], t["landing_concluded"], "  ".join("%s=%s" % (h, t["outcome"][h]) for h in RULES), t["property"],
            "-" if t["needs"] is None else "  ".join("%s:%s" % (h, "holds" if t["holds"][h] else "BROKEN") for h in RULES)))
