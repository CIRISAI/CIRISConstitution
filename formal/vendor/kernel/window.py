"""
window.py: a window as rows.

    open      row p opens the window. It names the head it is counted over, and (for an eviction) its target.
    answer    a row naming p that says something the window's table counts: approve, object, confirm, answered, act,
              against (a vote against the act proposed: the same row as `act` with the other polarity).
    receipt   a key with the concluder's seat signs that it holds p, stating its own instant.
              "Inside the window" is what the landing has in its past and the receipt has not, so a receipt
              with a row of the target in its past would put that row before the window. A row that has one, beyond
              what the opener itself has in its past, is no receipt, and a landing naming it concludes nothing.
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

The five windows are data (WINDOWS): the policy row of manifests/governance_policy.json, the clauses that close
the window at once, the clauses read at the close, and the default.

A clause is (value said, threshold, base, outcome). The bases:
    all               the window's counted scope at the opener's head
    others            the same, less the opener's signer: out of the voices and out of the size counted over (the
                      members' check: "a strict majority of the members seated at the head the act names, the
                      act's author apart"). Where the opener is a removal of an AI agent's key (an unseat marked
                      `agent`), the key it removes is apart too: an agent "acts under its own key and has no
                      vote", so in the lift of its own removal it is no voice and is not counted over, whether
                      the count is read with no landing, by a landing, or by the recount
    opener            the opener's signer alone
    any other word    that scope at the opener's head
The thresholds: "strict", "one", ("atleast", n, d, min), ("more", n, d, min), and
    ("voted", n, d, min, against)   more than n/d of the keys of the base that VOTED, and at least min voices: a key
                      voted if it said the clause's value or `against`. A silent key is not counted over.

A duty holder's single-signature answer (a value an at-once clause reads as "one" over a named scope, said by a
holder of that scope) is what that key said: a vote the same key also cast is moot, and does not make its answer
two things said.

An opener is a row of kind `open`, or a counted act that names a window (`window` on an unseat: a moderator's lone
removal of an agent's key, seat.py). Such an act is concluded by the seat's rule and the opener's together.
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
    # formal/self_roster, CC 3.3.6.4: a strict majority of the roster lands it at once (the proposer approves);
    # a strict majority of the others refuses it; alone it lands at the close, and only if the target was silent
    # The proposer may withdraw its own open proposal: refused at once, unless a strict majority has already approved
    # (a count once met is final, so the approval is read first).
    "self_roster_evict": {"policy": "self_roster_evict", "counted": "self", "concluder": "self", "opener_says": "approve",
                          "at_once": (("approve", "strict", "all", "landed"), ("withdraw", "one", "opener", "refused"),
                                      ("object", "strict", "others", "refused")),
                          "silent": "refused", "at_close": (), "default": "landed"},
    # the same policy for adding a key: the eviction's table without the target's silence
    "self_roster_add": {"policy": "self_roster_add", "counted": "self", "concluder": "self", "opener_says": "approve",
                        "at_once": (("approve", "strict", "all", "landed"), ("withdraw", "one", "opener", "refused"),
                                    ("object", "strict", "others", "refused")),
                        "silent": None, "at_close": (), "default": "landed"},
    # CC 4.5.13: a moderator answers within 48 h; on their absence the members act: "a strict majority of the members
    # who voted, never fewer than two voices" (data/governance_policy.tsv, moderation_action). `act` is a vote for,
    # `against` a vote against, a silent member is not counted over. A moderator's answer is no vote
    "moderation_fallback": {"policy": "moderation_action", "counted": "member", "concluder": "member", "opener_says": None,
                            "at_once": (("answered", "one", "moderate", "answered"),),
                            "silent": None, "at_close": (("act", ("voted", 1, 2, 2, "against"), "all", "fallback"),), "default": "lapsed"},
    # CC 4.2.1.1: one holder fires at once; the halt lapses at the fuse unless a strict majority confirms
    "halt_fuse": {"policy": "accord_halt", "counted": "holder", "concluder": "holder", "opener_says": "confirm",
                  "at_once": (("confirm", "strict", "all", "confirmed"),),
                  "silent": None, "at_close": (), "default": "lapsed"},
    # CC 4.5.13, the members' check: a duty holder's act takes effect at once and is itself the opener. "The act is
    # lifted when a strict majority of the members seated at the head the act names, the act's author apart, has
    # objected within the 48-hour window. ... The floor is two voices. The author's own objection is no voice, and the
    # author is not among the members the majority is taken of. Where the author is one of two members no lift is
    # possible." Short of that at the close it stands. So the base is `others`
    "moderation_overturn": {"policy": "moderation_overturn", "counted": "member", "concluder": "member", "opener": "moderate",
                            "opener_says": None, "at_once": (("object", ("more", 1, 2, 2), "others", "lifted"),),
                            "silent": None, "at_close": (), "default": "stands"},
}
SECS = None
MUT = set()            # planted breaks, switched on by a check
BASES = ("all", "others", "opener")


def is_opener(r):
    """A row that opens a window: an `open` row, or a counted act that names a window."""
    return r["kind"] == "open" or (r["kind"] == "unseat" and r.get("window") in WINDOWS)


def secs(name):
    """The window's length, from the policy table."""
    global SECS
    if SECS is None:
        import json
        fam = json.load(open(os.path.join(ROOT, "data", "governance_policy.json"), encoding="utf-8"))["families"]
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
    tv = {p.get("target")} if spec.get("target_votes") else set()   # the joiner's own yes is a voice of the floor (CC 3.1.3.2)
    withdrawn = any(a["signer"] == p["signer"] and a["says"] == "withdraw" for a in answers)
    heard = [a for a in answers if a["signer"] in base("all") | base.raw("moderate") | tv
             and not (a["signer"] == p["signer"] and a["says"] == "withdraw")]
    # a duty holder's single-signature answer is what that key said: its vote is moot
    duty = {value: over for value, how, over, _ in spec["at_once"] if how == "one" and over not in BASES}
    acted = {a["signer"] for a in heard if a["says"] in duty and a["signer"] in base.raw(duty[a["says"]])}
    if "vote_beside_answer" in MUT: acted = set()
    said = K.group([a for a in heard if a["signer"] not in acted or a["says"] in duty], "signer", "one", "says")
    if spec["opener_says"]: said.setdefault(p["signer"], spec["opener_says"])       # a voice that says two things says nothing
    def count_met(value, how, over, floor=False):
        if over == "opener": return withdrawn if value == "withdraw" else said.get(p["signer"]) == value
        # a count (a fraction, a floor) leaves the agents out; a clause one holder's act resolves reads them
        keys = voice = base.raw(over) if how == "one" else base(over)
        # MUTATION overturn_whole_roster: the opener's signer is no voice and is still counted over
        if over == "others" and "overturn_whole_roster" in MUT: keys = base("all")
        yes = K.group([{"k": s} for s, v in said.items() if v == value and (s in voice or (floor and s in tv and value == "approve"))], None, "count", "k")
        if isinstance(how, tuple):               # a threshold read off the policy table
            kind, num, den, least = how[:4]      # ("atleast", n, d, min): >= max(min, ceil(n*N/d)); ("more", n, d, min): > n/d and >= min
            if kind == "voted":                  # ("voted", n, d, min, against): > n/d of those of the base who voted, and >= min
                no = K.group([{"k": s} for s, v in said.items() if v == how[4] and s in voice], None, "count", "k")
                return yes * den > num * (yes + no) and yes >= least
            if kind == "atleast": return yes >= max(least, -(-num * len(keys) // den))
            return yes * den > num * len(keys) and yes >= least
        return yes >= 1 if how == "one" else 2 * yes > len(keys)
    for value, how, over, out in spec["at_once"]:
        if count_met(value, how, over): return out
    if not elapsed: return "open"
    if spec["silent"] and K.sel(inside, signer=p.get("target")): return spec["silent"]
    for value, how, over, out in spec["at_close"]:
        if count_met(value, how, over, floor=True): return out
    return spec["default"]


def _base(rows, past, p):
    spec = WINDOWS[p["window"]]
    cache = {}
    def base(name):
        if name not in cache:
            scope = spec["counted"] if name in ("all", "others") else name
            # a count of the room is by person: an agent's key is no voice and is not counted over (seat.counted_keys); the
            # key a lone removal removes is an agent's, so it is apart from the lift of its own removal
            # in no count means out of the base for every scope a clause reads, `moderate` included (the ruling of
            # 2026-11-25; MUTATION scope_keeps_agents: a named scope keeps its agents)
            m = ST.members_at(rows, past, p["obj"], p["head"], scope) if name not in ("all", "others") and "scope_keeps_agents" in MUT \
                else ST.counted_keys(rows, past, p["obj"], p["head"], scope)[0]
            cache[name] = m - {p["signer"]} if name == "others" else m
        return cache[name]

    def raw(name):
        """The keys a clause one holder's act resolves (`one`) reads over a named scope: its holders, agents
        included (an agent acts under its seat by the acts one signature resolves; the ruling of 2026-11-25)."""
        if name in ("all", "others", "opener") or "one_leaves_agents" in MUT: return base(name)
        if ("raw", name) not in cache:
            cache[("raw", name)] = ST.members_at(rows, past, p["obj"], p["head"], name)
        return cache[("raw", name)]
    base.raw = raw
    return base


def elapsed(landing_, rec, p):
    """The concluder's own two instants span the window. With either instant missing it has not elapsed."""
    a, b = landing_.get("at"), rec.get("at")
    return a is not None and b is not None and a - b >= secs(p["window"])


def voices_of(answers, p, past):
    """The answers that are voices: an approval that has the proposer's withdrawal in its past approves nothing."""
    wd = [a["id"] for a in answers if a["signer"] == p["signer"] and a["says"] == "withdraw"]
    return [a for a in answers if not (a["says"] == "approve" and any(past(w, a["id"]) for w in wd))]


def rule(r, P, past):
    """The conclusion rule: window rows here, every other row by seat.seat_rule."""
    k = r["kind"]
    if k not in ("open", "answer", "receipt", "landing") and not is_opener(r):
        return ST.seat_rule(r, P, past)
    by = {q["id"]: q for q in P}
    if is_opener(r):
        w = WINDOWS[r["window"]]                               # the opener's signer holds the opener's scope, by default the counted one
        if k != "open" and not ST.seat_rule(r, P, past): return False     # an act that opens its own window: validly made, by the seat
        return r["signer"] in ST.members_at(P, past, r["obj"], r["head"], w.get("opener", w["counted"]))
    p = by.get(r["of"])
    if p is None or not is_opener(p): return False
    if k == "answer": return True                              # whether its voice counts is read against the roster at p's head
    spec, base = WINDOWS[p["window"]], _base(P, past, p)
    if r["signer"] not in ST.members_at(P, past, p["obj"], p["head"], spec["concluder"]): return False
    if k == "receipt":
        # a receipt puts no row of the target before the window: none in its past that the opener's past does not hold
        t = p.get("target")
        return t is None or not any(q["signer"] == t and q["id"] != p["id"] and not past(q["id"], p["id"]) for q in P)
    rec = by.get(r["receipt"])
    if rec is None or rec["kind"] != "receipt" or rec["signer"] != r["signer"] or rec["of"] != p["id"]: return False
    answers = voices_of(K.sel(P, kind="answer", of=p["id"]), p, past)
    inside = [q for q in P if q["id"] != rec["id"] and not past(q["id"], rec["id"])]
    return r["says"] == table_outcome(spec, p, answers, inside, base, elapsed(r, rec, p))


# ---- derived: the outcome of a window under each rule ----------------------------------------------------
def outcome(S, pid, how, by_arrival=False, checkpoint=False):
    """how: void | contest | recount. Returns the outcome, "open" (no landing counts yet) or "contested"."""
    p = S.by.get(pid)
    if p is None or not S.C.get(pid): return "none"
    spec = WINDOWS[p["window"]]
    Ls = K.sel(S.Cs, kind="landing", of=pid)
    if not Ls and "landing_only" in MUT: return "open"
    if Ls and how == "void":
        C = CUT.Cut(S)                                          # the landing is a cut on p's slot; only landings speak on it
        st = {L["id"]: C.status(L) for L in Ls}
        said = [{"v": L["says"]} for L in K.frontier(S.anc, [L for L in Ls if st[L["id"]] == "counts"])]
        if "contested" in st.values() or not said: return "contested"
        return K.group(said, None, "one", "v") or "contested"
    past = lambda a, b: a in S.anc[b]
    base = _base(S.Cs, past, p)
    pos = {r["id"]: i for i, r in enumerate(S.rows)}
    late = lambda r: False
    if how == "recount" or not Ls:
        C = CUT.Cut(S)
        # the rows that ended a seat over the object, with the keys each ended
        gone = [(frozenset(u["to"]), u) for u in K.sel(S.Cs, kind="unseat") if u["obj"] == p["obj"] and C.counts(u)]
        for w in K.sel(S.Cs, kind="withdraw"):
            o = S.by.get(w["target"])
            if o is not None and o["kind"] == "offer" and o["obj"] == p["obj"]:
                gone.append((frozenset({w["signer"]}) if w["signer"] in o["to"] else frozenset(o["to"]), w))
        cps = CP.checkpoints(S, C, p["obj"], group=True) if checkpoint else []   # off by default: see the module's head
        late = lambda r: any(r["signer"] in ks and r["id"] not in S.anc[x["id"]] for ks, x in gone) or CP.stale_answer(S, cps, p, r)
    if not Ls:
        # no landing has concluded: a count that is met needs no clock and no concluder, so the table's at-once
        # outcome over the answers held is the outcome; short of it the window is open
        held = voices_of([a for a in K.sel(S.Cs, kind="answer", of=pid) if not late(a)], p, past)
        return table_outcome(spec, p, held, [], base, False)
    said = []
    for L in K.frontier(S.anc, Ls):                             # a landing that a later landing names is answered by it
        # MUTATION by_arrival: "concurrent" read as "arrived after the landing", by list position
        conc = [r for r in S.Cs if (pos[r["id"]] > pos[L["id"]] and L["id"] not in S.anc[r["id"]]) if by_arrival] if by_arrival else \
               [r for r in S.Cs if S.concurrent(r["id"], L["id"])]
        conc = [r for r in conc if not late(r)]
        ans = [r for r in K.sel(conc, kind="answer", of=pid) if r["signer"] in base("all") | base.raw("moderate") | ({p.get("target")} if spec.get("target_votes") else set())]
        tgt = K.sel(conc, signer=p.get("target")) if spec["silent"] else []
        if how == "contest":
            said.append({"v": "contested" if ans or tgt else L["says"]})
        else:
            rec = S.by[L["receipt"]]
            mine = [q for q in S.Cs if q["id"] in S.anc[L["id"]]]
            inside = [q for q in mine if q["id"] != rec["id"] and q["id"] not in S.anc[rec["id"]]] + tgt
            again = table_outcome(spec, p, voices_of(K.sel(mine, kind="answer", of=pid) + ans, p, past), inside, base, elapsed(L, rec, p))
            said.append({"v": L["says"] if again == L["says"] else "contested"})
    if how == "recount" and any(x["v"] != "contested" for x in said):
        said = [x for x in said if x["v"] != "contested"]       # a landing that does not stand is no voice against one that does
    return K.group(said, None, "one", "v") or "contested"


RULES = ("void", "contest", "recount")


def outcomes(S, pid, **kw):
    return {h: outcome(S, pid, h, **kw) for h in RULES}


# ---- the five windows, and the adversary in each --------------------------------------------------------
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
        ("the count with no landing: the owner's two devices approve the eviction of the stolen one and nobody lands",
         [g, q_p, answer("a2", "d2", "p", "approve")], "a count that is met needs no clock and no concluder", "landed"),
        ("the others refuse with no landing: the thief proposes and the owner's two devices object",
         [g, thief_p, answer("o1", "d1", "p", "object"), answer("o2", "d2", "p", "object")], "thief cannot evict alone", "refused"),
        ("one approval short of the count, no landing: nothing has changed",
         [g, thief_p], "(a proposal alone is open)", "open"),
        ("the proposer withdraws its open proposal",
         [g, own_p, answer("wd", "d1", "p", "withdraw")], "the proposer may withdraw its own open proposal", "refused"),
        ("a withdrawal beside a majority's approval, neither naming the other",
         [g, q_p, answer("a2", "d2", "p", "approve"), answer("wd", "d1", "p", "withdraw")], "a count once met is final", "landed"),
        ("an approval that names the withdrawal",
         [g, q_p, answer("wd", "d1", "p", "withdraw"), answer("a2", "d2", "p", "approve", ("wd",))],
         "nobody approves a withdrawn proposal", "refused"),
        ("a withdrawal in the lone landing's past: the landing states 'landed' over it",
         [g, own_p, receipt("r", "d1", "p", 0), answer("wd", "d1", "p", "withdraw"), landing("L", "d1", "p", "r", "landed", W, ("wd",))],
         "a withdrawn proposal does not land", "not landed"),
        ("a withdrawal concurrent with the lone landing",
         [g, own_p, receipt("r", "d1", "p", 0), landing("L", "d1", "p", "r", "landed", W), answer("wd", "d1", "p", "withdraw")],
         "a withdrawn proposal does not land", "not landed"),
        ("a withdrawal that names the lone landing: it came after",
         [g, own_p, receipt("r", "d1", "p", 0), landing("L", "d1", "p", "r", "landed", W), answer("wd", "d1", "p", "withdraw", ("L",))],
         "a landed eviction is not withdrawn", "landed"),
        ("another key signs a withdrawal of the proposal",
         [g, own_p, answer("wd", "d3", "p", "withdraw")], "only the proposer withdraws", "open"),
    ]
    return "self roster, lone eviction (24 h, target silent)", cases


def add_world():
    g = ST.offer("g", "d1", ("d1", "d2", "d3"), "self", "@", "self", cosigners=("d2", "d3"))
    W = secs("self_roster_add")
    p = opener("p", "d1", "self_roster_add", "g", ("g",), target="d4")               # the owner adds a new device
    thief_p = opener("p", "d3", "self_roster_add", "g", ("g",), target="t9")         # the thief adds a key of its own
    cases = [
        ("the count with no landing: two of three approve the new key",
         [g, p, answer("a2", "d2", "p", "approve")], "a count that is met needs no clock and no concluder", "landed"),
        ("a proposal alone: the key of an addition is not seated while the window is open",
         [g, p], "nothing a proposal would change has changed while it is open", "open"),
        ("the lone path: nobody answers in 24 h and the proposer lands",
         [g, p, receipt("r", "d1", "p", 0), landing("L", "d1", "p", "r", "landed", W)], "one key adds another after the window", "landed"),
        ("false landing, early: the thief lands its own key before its window has run",
         [g, thief_p, receipt("r", "d3", "p", 0), landing("L", "d3", "p", "r", "landed", W - 1)], "thief cannot add alone at once", "not landed"),
        ("the others refuse: the thief proposes its own key and the owner's two devices object, no landing",
         [g, thief_p, answer("o1", "d1", "p", "object"), answer("o2", "d2", "p", "object")], "thief cannot add alone", "refused"),
        ("false landing: the thief lands its key at the close, leaving the two objections unnamed",
         [g, thief_p, receipt("r", "d3", "p", 0), answer("o1", "d1", "p", "object"), answer("o2", "d2", "p", "object"),
          landing("L", "d3", "p", "r", "landed", W)], "thief cannot add alone", "not landed"),
        ("one objection of two others is not a refusal: the thief lands at the close over it",
         [g, thief_p, receipt("r", "d3", "p", 0), answer("o1", "d1", "p", "object"), landing("L", "d3", "p", "r", "landed", W, ("o1",))],
         "(the stated residual: one device of the owner's objecting does not stop a lone addition)", None),
        ("the key being added signs rows in the window: an addition has no target's silence",
         [g, p, receipt("r", "d1", "p", 0), R("n4", "note", "d4", ("g",)), landing("L", "d1", "p", "r", "landed", W)],
         "the added key's own rows do not refuse it", "landed"),
        ("the proposer withdraws the addition",
         [g, p, answer("wd", "d1", "p", "withdraw")], "the proposer may withdraw its own open proposal", "refused"),
    ]
    return "self roster, lone addition (24 h)", cases


def admitted(k, by=("m1", "m3"), founders=("m1", "m2", "m3")):
    """A room of three founding duty holders, and key k admitted to its roster by two of them (k cosigning: its own
    yes). A duty seat stands only on a member (seat.py, `member`), so a world that confers one on k admits k first and
    counts the conferral over the admission."""
    g = ST.offer("g", founders[0], founders, "duty", "@", "self", cosigners=founders[1:])     # three duty holders (CC 4.5.4)
    am = ST.offer("am", by[0], k, "member", "g", "group", ("g",), head=("g",), policy="community_invite", cosigners=tuple(by[1:]) + (k,))
    return g, am


def moderation_world():
    g, am = admitted("MOD")                                                    # MOD is a member, then a moderator
    md = ST.offer("md", "m1", "MOD", "moderate", "g", "group", ("am",), head=("am",), policy="duty_confer", counted="duty",
                  cosigners=("m3", "MOD"))                                     # two of the three confer, MOD accepting
    W = secs("moderation_fallback")
    p = opener("p", "m2", "moderation_fallback", "g", ("md",))
    # four members at the head (m1, m2, m3 and MOD); the count at the close is over the members who voted
    acts = [answer("x1", "m1", "p", "act"), answer("x2", "m2", "p", "act"), answer("x3", "m3", "p", "act")]
    xs = ("x1", "x2", "x3")
    A = answer("A", "MOD", "p", "answered")
    base = [g, am, md, p, receipt("r", "m2", "p", 0)] + acts
    L = landing("L", "m2", "p", "r", "fallback", W, xs)
    cases = [
        ("false landing: a member lands the members' moderation; the moderator had answered and the landing leaves the answer unnamed",
         base + [A, L], "present moderator is not overridden", "not fallback"),
        ("false landing, stated falsely: the same landing naming the moderator's answer",
         base + [A, landing("L", "m2", "p", "r", "fallback", W, xs + ("A",))], "present moderator is not overridden", "not fallback"),
        ("false landing, no count: one member lands the fallback alone",
         [g, am, md, p, receipt("r", "m2", "p", 0), landing("L", "m2", "p", "r", "fallback", W)], "the fallback needs the members' majority", "not fallback"),
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
        ("a moderator's seat conferred on a key that is not a member: its answer is no moderator's answer, and the members' majority lands",
         [g, dict(md, names=("g",), head=("g",)), dict(p), receipt("r", "m2", "p", 0), acts[0], acts[1], A,
          landing("L", "m2", "p", "r", "fallback", W, ("x1", "x2"))],
         "a duty seat stands only on a member", "fallback"),
        ("false landing, short of the count: one member acts and another votes against, and one of them lands the fallback",
         [g, am, md, p, receipt("r", "m2", "p", 0), acts[0], answer("n2", "m2", "p", "against"),
          landing("L", "m2", "p", "r", "fallback", W, ("x1", "n2"))],
         "the fallback needs the members' majority", "not fallback"),
    ]
    # a room of four founders and MOD, admitted and then made moderator: the count is over the members who voted,
    # for (`act`) or against (`against`), floor two voices; a silent member (MOD among them) is not counted over
    g4, am4 = admitted("MOD", by=("m1", "m3", "m4"), founders=("m1", "m2", "m3", "m4"))
    md4 = ST.offer("md", "m1", "MOD", "moderate", "g", "group", ("am",), head=("am",), policy="duty_confer", counted="duty",
                   cosigners=("m3", "m4", "MOD"))
    b4 = [g4, am4, md4, p, receipt("r", "m2", "p", 0)]
    acts = acts[:1] + acts[2:]                                                 # x1 and x3: m2 lands, and votes against below
    n2, n4 = answer("n2", "m2", "p", "against"), answer("n4", "m4", "p", "against")
    fb = lambda *names: landing("L", "m2", "p", "r", "fallback", W, names)
    cases += [
        ("five members, two vote for and three are silent: the landing names the two votes",
         b4 + acts + [fb("x1", "x3")], "a silent member is not counted over", "fallback"),
        ("five members, one votes for and nobody against",
         b4 + acts[:1] + [fb("x1")], "never fewer than two voices", "not fallback"),
        ("five members, two vote for and two against: the landing names all four",
         b4 + acts + [n2, n4, fb("x1", "x3", "n2", "n4")], "a strict majority of those who voted", "not fallback"),
        ("five members, two vote for and one against",
         b4 + acts + [n2, fb("x1", "x3", "n2")], "a strict majority of those who voted", "fallback"),
        ("withheld votes: two vote for and the landing names them; two votes against were kept from the lander",
         b4 + acts + [n2, n4, fb("x1", "x3")], "a strict majority of those who voted", "not fallback"),
        ("a member votes both for and against, beside one vote for",
         b4 + acts + [answer("n1", "m1", "p", "against"), fb("x1", "x3", "n1")], "a voice that says two things says nothing", "not fallback"),
        ("two keys off the roster vote against two members' votes for",
         b4 + acts + [answer("z1", "z", "p", "against"), answer("z2", "y", "p", "against"), fb("x1", "x3", "z1", "z2")],
         "only a member's vote is counted", "fallback"),
        ("a key conferred `moderate` while it is no member votes for, beside one member's vote",
         [g4, dict(md4, names=("g",), head=("g",)), p, receipt("r", "m2", "p", 0)] + acts[:1] + [answer("xM", "MOD", "p", "act"), fb("x1", "xM")],
         "a duty seat stands only on a member, and a non-member's vote is no vote", "not fallback"),
        ("a moderator who is also a member answers and votes for, beside one vote for: no landing",
         b4 + acts + [answer("A1", "m1", "p", "answered")], "its act answers and its vote is moot", "answered"),
        ("the same, and a member lands the fallback over it, naming all three",
         b4 + acts + [answer("A1", "m1", "p", "answered"), fb("x1", "x3", "A1")], "its act answers and its vote is moot", "not fallback"),
        ("after the fallback has landed, the moderator answers, naming the landing",
         b4 + acts + [n2, fb("x1", "x3", "n2"), answer("A", "MOD", "p", "answered", ("L",))],
         "a moderator's act after the fallback has landed does not reopen the window", "fallback"),
    ]
    return "moderation fallback (48 h, absent moderator, a majority of the members who voted)", cases


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


def overturn_world():
    g, am = admitted("MOD")                                                    # MOD is a member, then a moderator
    md = ST.offer("md", "m1", "MOD", "moderate", "g", "group", ("am",), head=("am",), policy="duty_confer", counted="duty",
                  cosigners=("m3", "MOD"))
    W = secs("moderation_overturn")
    p = opener("p", "MOD", "moderation_overturn", "g", ("md",))         # the duty holder's act opens its own window
    # four members at the head (m1, m2, m3 and MOD, the duty holder); the act's author apart, three are counted over and
    # two objections lift (rule of CC 4.5.13: a strict majority of the members less the author, floor two)
    o1, o2, o3 = answer("o1", "m1", "p", "object"), answer("o2", "m2", "p", "object"), answer("o3", "m3", "p", "object")
    base = [g, am, md, p]
    r1, r3 = receipt("r", "m1", "p", 0), receipt("r", "m3", "p", 0)
    stands = landing("L", "m3", "p", "r", "stands", W, ("o1",))
    g1 = ST.offer("g", "m1", ("m1",), "duty", "@", "self")
    p1 = opener("p", "m1", "moderation_overturn", "g", ("g",))          # the lone duty holder (its founding seat moderates) is the one member
    cases = [
        ("false landing, no count: one member objects and lands the lift alone",
         base + [o1, r1, landing("L", "m1", "p", "r", "lifted", 0, ("o1",))], "the lift needs the members' majority", "not lifted"),
        ("the room lifts: two of the three members other than the duty holder object and one of them lands at once",
         base + [o1, o2, r1, landing("L", "m1", "p", "r", "lifted", 0, ("o1", "o2"))], "the room may lift a duty holder's act", "lifted"),
        ("the room lifts: all three members other than the duty holder object and one of them lands at once",
         base + [o1, o2, o3, r1, landing("L", "m1", "p", "r", "lifted", 0, ("o1", "o2", "o3"))], "the room may lift a duty holder's act", "lifted"),
        ("stands at the close: one objection in 48 h and another member lands",
         base + [o1, r3, stands], "short of the count the act stands", "stands"),
        ("false landing: a member lands 'stands' leaving a second objection unnamed",
         base + [o1, o2, r3, stands], "a majority's objections are not overridden by a landing", "not stands"),
        ("withheld objection: an honest member lands 'stands'; a relay had kept the second objection from it",
         base + [o1, o2, r3, stands], "a majority's objections are not overridden by a landing", "not stands"),
        ("a second landing naming both: a member lands 'lifted', naming the first landing and the second objection",
         base + [o1, o2, r3, stands, receipt("r2", "m1", "p", 0), landing("L2", "m1", "p", "r2", "lifted", 0, ("L", "o2"))],
         "a row naming both decides", "lifted"),
        ("the duty holder objects to its own act, with one member: the landing names both",
         base + [o1, answer("oM", "MOD", "p", "object"), r1, landing("L", "m1", "p", "r", "lifted", 0, ("o1", "oM"))],
         "the author's objection is no voice", "not lifted"),
        ("the duty holder objects to its own act, with two members: the landing names the three",
         base + [o1, o2, answer("oM", "MOD", "p", "object"), r1, landing("L", "m1", "p", "r", "lifted", 0, ("o1", "o2", "oM"))],
         "the author is not among the members the majority is taken of", "lifted"),
        ("a key with no seat at the head objects, with one member",
         base + [o1, answer("oz", "z", "p", "object"), r1, landing("L", "m1", "p", "r", "lifted", 0, ("o1", "oz"))],
         "only a member seated at the head the act names counts", "not lifted"),
        ("the floor: in a room of one, the one member (its lone duty holder) objects to its own act and lands",
         [g1, p1, dict(o1), r1, landing("L", "m1", "p", "r", "lifted", 0, ("o1",))], "never fewer than two voices", "not lifted"),
        ("a member who holds no duty opens the check on an act of its own, and the three other members object and land the lift",
         [g, am, opener("p", "MOD", "moderation_overturn", "g", ("am",)), o1, o2, o3, r1, landing("L", "m1", "p", "r", "lifted", 0, ("o1", "o2", "o3"))],
         "only a duty holder's act opens the members' check", "not lifted"),
        ("objection signed just after, naming the landing: a member objects late and honestly",
         base + [o1, r3, stands, answer("o2", "m2", "p", "object", ("L",))], "(what an honest late objection is worth)", None),
        ("objection signed just after, leaving the landing unnamed",
         base + [o1, r3, stands, o2], "(a late objection against a landing that stands)", None),
    ]
    # the moderator is itself on the roster (a duty holder is a member and holds every duty): its own objection is no
    # voice and it is not among the members the majority is taken of
    pm = opener("p", "m1", "moderation_overturn", "g", ("g",))
    o3, o4 = answer("o3", "m3", "p", "object"), answer("o4", "m4", "p", "object")
    r2 = receipt("r", "m2", "p", 0)
    lift = lambda *names: landing("L", "m2", "p", "r", "lifted", 0, names)
    g4 = ST.offer("g", "m1", ("m1", "m2", "m3", "m4"), "duty", "@", "self", cosigners=("m2", "m3", "m4"))
    g2 = ST.offer("g", "m1", ("m1", "m2"), "duty", "@", "self", cosigners=("m2",))
    cases += [
        ("room of three, the moderator a member: both others object, two of two",
         [g, pm, o2, o3, r2, lift("o2", "o3")], "the room may lift a duty holder's act", "lifted"),
        ("room of three, the moderator a member: one other objects alone",
         [g, pm, o2, r2, lift("o2")], "never fewer than two voices", "not lifted"),
        ("room of three, the moderator a member: one other and the moderator object",
         [g, pm, o1, o2, r2, lift("o1", "o2")], "the author's objection is no voice", "not lifted"),
        ("room of four, the moderator a member: two of the three others object",
         [g4, pm, o2, o3, r2, lift("o2", "o3")], "the author is not among the members the majority is taken of", "lifted"),
        ("room of four, the moderator a member: one of the three others objects",
         [g4, pm, o2, r2, lift("o2")], "the lift needs the members' majority", "not lifted"),
        ("room of four, the moderator a member: one other and the moderator object",
         [g4, pm, o1, o2, r2, lift("o1", "o2")], "the author's objection is no voice", "not lifted"),
        ("room of two, the moderator and one member: both object",
         [g2, pm, o1, o2, r2, lift("o1", "o2")], "where the author is one of two members no lift is possible", "not lifted"),
        ("room of two, the moderator and one member: the member objects, no landing",
         [g2, pm, o2], "where the author is one of two members no lift is possible", "open"),
    ]
    return "moderation overturn (48 h, the members' check on a duty holder's act)", cases


WORLDS = (self_world, add_world, moderation_world, halt_world, overturn_world)


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
