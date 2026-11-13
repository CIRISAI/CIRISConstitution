"""
door.py: ONE parametrised door on the kernel.

A door is: WHO MAY OPEN (one voice with a seat in a scope), WHO MAY ANSWER (a counted set read at the head the
opener names, extra seats, the target), WITH WHAT KINDS of answer, HOW LONG (no window, or a window closed on the
concluder's own two instants), and WHAT HOLDS AT THE CLOSE: a table of clauses over the answers, read at once or at
the close, with a default. The outcome is that table over the answers.

The kernel's rules are not changed. The rows, the receipt, the landing and the recount are window.py's own (this
file sits beside it in formal/causal_kernel). The door specs are added to window.py's WINDOWS under "door:<name>";
window.py's table_outcome, _base and secs are wrapped so that a door spec is read here and every other spec by
window.py itself, and a door whose clauses window.py can state (a threshold of its own shapes, target_votes, the
moderate seat) is handed to window.py's own table. window.outcome() then runs unchanged. The conclusion rule is
window.rule with one generalisation: who concludes is a scope, the target itself ("target"), or the ranked winner
("winner"). check_door.py shows first that window.py's three windows, judged by this rule, give
window_adversary.tsv line for line.

Every door is built from the cells of manifests/governance_policy.json or manifests/reactions.json; each spec carries
`cells` (the parameter -> the cell it came from) and `unstated` (the parameters the tables do not give, with the
reading taken here).

Who concludes a window, with which row, and whether a late answer counts are read from the `land` entries of
manifests/reactions.json wherever one names the door's clock (LANDS, stated()). `local` there says each node reads
its own close and nothing is signed: the door runs it with the key that stands for the reading node, the spec's
`reader`. A door with no such entry keeps the reading written here, and says so in `unstated`.

What the opening row is while its window is open is read from the `while` entries of manifests/reactions.json:
`in_force` (it binds each node from that node's own first holding, as a halt does) or `pending` (it binds nobody
until the window lands or its fallback carries, as a moderation proposal). state() answers it.

Whether the target's own yes is a voice of the floor is the policy row's `target_voice` cell. A count under a
declared protocol is read from the `consensus_protocol` the group's founding row declares, never from the door.
A parameter the text states and no rule table has a column for is a row of formal/derivation/door_text.tsv, read
here with its quote (check_door.py checks each quote stands in its section).
"""
import csv
import re
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import window as WN  # noqa: E402
import seat as ST    # noqa: E402

CK, K, R = ST.CK, ST.K, ST.R
PTAB = json.load(open(os.path.join(ROOT, "manifests", "governance_policy.json"), encoding="utf-8"))
POLICY = {f["family"]: f for f in PTAB["families"]}
PROTOCOLS = {k["kind"]: k for k in PTAB["protocols"]["kinds"]}
NEVER = 10 ** 15
MIN_COUNT = PTAB["min_count"]                    # community 2, self 1; role/halt/cosign corridors read the community's
RX = json.load(open(os.path.join(ROOT, "manifests", "reactions.json"), encoding="utf-8"))["reactions"]
BASE_LAW = PTAB["base_law"]                      # base(N) = N for N <= k: the sizes run (3 and 4) are all below k
DOOR_TEXT_PATH = os.path.join(ROOT, "formal", "derivation", "door_text.tsv")
DOOR_TEXT = list(csv.DictReader((l for l in open(DOOR_TEXT_PATH, encoding="utf-8") if not l.startswith("#")), delimiter="\t", quoting=csv.QUOTE_NONE))
SEAT = {"identity:substrate_persist": "substrate"}      # a role token of the manifest -> the seat name the worlds use

# the door -> the clock or expiry of reactions.json it runs: (family, leaf or None, name)
LANDS = {
    "accord_halt": ("accord:invoke:constitutional:{halt_id}", None, "fuse"),
    "self_roster_add": ("identity:occurrence", None, "window"),
    "moderation_action": ("moderation:{allegation_type}", None, "window"),
    "harm_report": ("moderation:{allegation_type}", "harm_report", "window"),
    "moderator_election": ("ballot:moderator", None, "window"),
    "deletion_sla": ("consent:deletion_sla:{days}", None, "sla"),
    "accord_roster_change": ("group:roster", None, "W"),
    "takedown_withhold": ("takedown_notice:{basis}", "Dmca512", "withhold"),
    "retirement_objection": ("retirement:{state}", "decided", "objection"),
    "decay_stage": ("consent:decay:{stage}", None, "anonymise"),
    "invitation": ("membership:{stage}", "proposal", "expiry"),
    "deferral": ("deferral:request", None, "expiry"),
}
HOLD = ("cosign:{state}", "pending", "hold")            # the close of a cosigned row's hold


def land_entry(family, leaf, name):
    """The `land` entry of manifests/reactions.json for one clock or expiry, or None where no sentence states it."""
    for e in RX:
        if e["kind"] == "land" and e["family"] == family and e["name"] == name and e.get("leaves", [None]) == [leaf]:
            return e
    return None


def while_entry(family, leaf, name):
    """The `while` entry of manifests/reactions.json for one clock or expiry, or None where no sentence states it."""
    for e in RX:
        if e["kind"] == "while" and e["family"] == family and e["name"] == name and e.get("leaves", [None]) == [leaf]:
            return e
    return None


def land_text(e):
    return "reactions `land %s %s%s` (%s)" % (e["name"], "local" if e["concluder"] == "local" else "by %s as %s" % (e["concluder"], e["landing"]),
                                              " late " + e["late"] if e.get("late") else "", ", ".join(e["cc_ref"]))


def stated(spec, door, reader, author=None):
    """The concluder, the landing row and the late answer of a door, from the manifest where it states them.
    `reader`: the seat that stands for the node reading its own close, where the manifest says `local`.
    `author`: the seat of the opening row's signer, where the manifest says `author` and that signer concludes."""
    w = while_entry(*LANDS[door])
    if w is not None:
        spec = dict(spec, open=w["open"], cells=dict(spec["cells"], open="reactions `while %s %s` (%s)" % (w["name"], w["open"], ", ".join(w["cc_ref"]))))
    e = land_entry(*LANDS[door])
    if e is None:
        return dict(spec, concluder=reader if spec.get("concluder") is None else spec["concluder"])
    spec = dict(spec, cells=dict(spec["cells"], landing=land_text(e)), landing_from="reactions",
                unstated=[u for u in spec["unstated"] if not u.startswith(("concluder", "landing row", "late"))])
    if e["concluder"] == "local":
        spec["concluder"] = reader; spec["landing_row"] = "none: each node reads its own close (run as the key in '%s')" % reader
    else:
        spec["concluder"] = SEAT.get(e["concluder"], e["concluder"]); spec["landing_row"] = e["landing"]
        if e["concluder"] == "author" and author: spec["concluder"] = author
    if e.get("late"): spec["late"] = e["late"]
    return spec


def hold_close(spec):
    """A cosigned row under a hold: the row itself lands it; who closes the hold is the manifest's `land hold`."""
    e = land_entry(*HOLD)
    if e is None or e["concluder"] != "local": return spec
    return dict(spec, cells=dict(spec["cells"], close=land_text(e)),
                unstated=[u for u in spec["unstated"] if not u.startswith(("concluder at the close", "no clock entry"))])

ORIG_WINDOWS = dict(WN.WINDOWS)
WN_TABLE, WN_BASE, WN_SECS = WN.table_outcome, WN._base, WN.secs

# ---- mutation switches (check_door.py turns one on at a time) ------------------------------------------------
MUT = set()


# ---- the threshold of one clause ------------------------------------------------------------------------------
def met(rule, yes, n):
    k = rule[0]
    if k == "strict":  _, num, den, mn = rule; return yes * den > num * n and yes >= mn
    if k == "atleast": _, num, den, mn = rule; return n > 0 and yes * den >= num * n and yes >= mn
    if k == "abs":     return yes >= rule[1]
    raise ValueError(rule)


# a protocol kind's rule (consensus_protocols.tsv) as a threshold; the door's own floor raises the least count
PROTO_RULE = {"all": ("atleast", 1, 1, 1), "strict_majority": ("strict", 1, 2, 1), "voices:{m}": ("abs", 2),
              "all_and_majority": ("all_and_majority",)}
MISREAD = {"unanimous": "quorum:{m}/{n}", "majority": "unanimous", "quorum:{m}/{n}": "unanimous"}   # MUTATION protocol_misread


def state(S, pid):
    """What the opening row is at this node. While no landing stands, `in_force` or `pending` as the door's `while`
    cell states (`open` where none does); once one stands, the outcome; `none` where the opener is not concluded."""
    o = outcome(S, pid)
    if o != "open": return o
    w = WN.WINDOWS[S.by[pid]["window"]].get("open")
    if w and "force_flipped" in MUT: w = {"in_force": "pending", "pending": "in_force"}[w]   # MUTATION: the cell read the other way
    return w or "open"


def text_rows(name):
    """The rows of door_text.tsv for a door: those naming its policy row, before any [instance], @ or - suffix."""
    base = re.split(r"[\[@+\-]", name)[0]
    return [t for t in DOOR_TEXT if t["door"] == base]


# what a door_text.tsv parameter settles: the `unstated` items it removes, and those it moves to `stated_not_run`
TEXT_SETTLES = {"concluder": (("concluder", "landing row"), ()), "opener_counts": (("the opener's proposal counts",), ()),
                "silent": (("outcome when the target signed",), ()), "opener": ((), ("who opens",)),
                "options": (("options:",), ()), "decline": ((), ("a declining winner",)), "answers": (("answers:", "a duty clock"), ()),
                "tally": (("concluder: the period's tally member",), ()), "escalate": (("going up at the end",), ("the conferrer's own answer",)),
                "signer": ((), ())}


def apply_text(name, spec):
    for t in text_rows(name):
        drop, move = TEXT_SETTLES[t["parameter"]]
        spec = dict(spec, cells=dict(spec["cells"], **{t["parameter"]: "door_text `%s` (%s)" % (t["value"], t["cc_ref"])}))
        spec["stated_not_run"] = spec.get("stated_not_run", []) + [u for u in spec["unstated"] if u.startswith(move)] if move else spec.get("stated_not_run", [])
        spec["unstated"] = [u for u in spec["unstated"] if not u.startswith(drop + move)]
        if t["parameter"] == "concluder" and t["value"] == "local" and not spec.get("landing_row"):
            spec["landing_row"] = "none: each node reads its own close (run as the key in '%s')" % spec["concluder"]
    return spec


def enact_rule(cell):
    """An enact cell as build_governance_policy reads it: strictly more than the fraction (votes(e, base, True))."""
    k = cell["kind"]
    if k == "fraction":
        if cell["num"] >= cell["den"] and "strict_2_2" not in MUT:
            return ("atleast", 1, 1, 1)              # build_governance_policy.votes: the whole set, never more than there are
        return ("strict", cell["num"], cell["den"], 1)
    if k == "strict_majority": return ("strict", 1, 2, 1)
    if k == "one_of_n": return ("abs", 1)
    raise ValueError(cell)


def at_least_rule(cell, mc):
    k = cell["kind"]
    if k == "fraction": return ("atleast", cell["num"], cell["den"], mc)
    if k == "strict_majority_of_others": return ("strict", 1, 2, 1)
    if k == "strict_majority": return ("strict", 1, 2, 1)
    if k == "one_of_n": return ("abs", 1)
    if k == "voices": return ("abs", cell["count"])
    if k == "voted_majority": return ("strict", 1, 2, cell["count"])     # over those who voted (the clause's `over`)
    raise ValueError(cell)


# ---- the table ------------------------------------------------------------------------------------------------
def to_window(spec):
    """The door in window.py's own shape, or None where a clause needs more than window.py states."""
    if spec.get("late") != "counts" or set(spec["extra"]) - {"moderate"} or "dedupe_off" in MUT: return None
    ats = {"once": [], "close": []}
    for when, value, rule, over, out in spec["clauses"]:
        if over not in ("all", "others", "extra"): return None
        over = "moderate" if over == "extra" else over
        if "one_voice" in MUT: how = "one"
        elif rule == ("abs", 1): how = "one"
        elif rule[0] == "abs": how = ("atleast", 0, 1, rule[1])
        elif rule[0] == "strict" and rule[3] <= 1: how = "strict" if rule[1:3] == (1, 2) else ("more", rule[1], rule[2], 0)
        elif rule[0] == "atleast": how = ("atleast",) + tuple(rule[1:])
        else: return None
        ats[when].append((value, how, over, out))
    return {"policy": spec["policy"], "counted": spec["counted"], "concluder": spec["concluder"], "opener_says": spec["opener_says"],
            "at_once": tuple(ats["once"]), "at_close": tuple(ats["close"]), "silent": spec["silent"] if "no_silent" not in MUT else None,
            "default": spec["default"], "target_votes": spec.get("target_votes", False)}



def table_outcome(spec, p, answers, inside, base, elapsed):
    if not spec.get("door"): return WN_TABLE(spec, p, answers, inside, base, elapsed)
    w = to_window(spec)
    if w is not None:
        return WN_TABLE(w, p, answers, inside, base, elapsed)
    return door_table(spec, p, answers, inside, base, elapsed)


def door_table(spec, p, answers, inside, base, elapsed):
    """window.table_outcome generalised: clauses (when, value, rule, over, outcome); a ranked clause; `late`."""
    said = K.group([a for a in answers if a["signer"] in base("all") | base("moderate")], "signer", "one", "says")
    if "dedupe_off" in MUT:                                         # MUTATION: a person's two ballots both count
        said = {}
        for a in answers:
            if a["signer"] in base("all"): said[a["signer"] + "#" + a["id"]] = a["says"]
    if spec["opener_says"]: said.setdefault(p["signer"], spec["opener_says"])
    def count(value, over, close=False):
        keys = base(over)
        if over == "voted": keys = frozenset(s for s in said if s in base("all"))
        n = len(keys)                                                # the base stays the roster
        if close and value == "approve" and spec.get("target_votes") and p.get("target"):
            keys = keys | {p["target"]}                             # the target's own yes is a voice of the floor (target_voice)
        yes = len({s.split("#")[0] for s, v in said.items() if v == value and s.split("#")[0] in keys})
        return yes, n
    def clause(c):
        when, value, rule, over, out = c
        if rule[0] == "ranked":
            keys = base(over)
            ballots = [(s.split("#")[0] if "dedupe_off" not in MUT else s, v) for s, v in said.items()
                       if isinstance(v, tuple) and s.split("#")[0] in keys]
            if "dedupe_off" in MUT:
                if len(ballots) < rule[1]: return None
                from collections import Counter
                tops = Counter(b[1][0] for b in ballots)                  # the mutation also skips the fold: first choices
                best = max(sorted(tops), key=lambda o: tops[o])
                return out + best if 2 * tops[best] > len(ballots) else None
            # an election declares no order (CC 4.5.13): a tie for weakest seats nobody and the count runs again; the floor
            # in a small room is the smaller of two voices and the roster's size, so a room of one elects itself
            w, _ = WN.ST.RANKED(ballots, list(spec["options"]), floor=rule[1] if "election_floor_two" in MUT else min(rule[1], len(keys)), declared="tie_by_position" in MUT) if ballots else (None, 0)
            return out + w if w else None
        if rule[0] == "protocol":                                 # the rule of the protocol the group declares (its founding row)
            kind = base("declared")
            if kind is None: return None
            if "protocol_misread" in MUT: kind = MISREAD.get(kind, kind)
            pr = PROTOCOLS[kind]
            r2 = PROTO_RULE[pr[rule[1]]]
            r2 = r2 if r2[0] in ("all_and_majority", "abs") else r2[:3] + (max(r2[3], rule[2]),)
            over2 = "nontarget" if pr["removal_set" if rule[1] == "removal_rule" else "count_set"] == "member-target" else over
            return clause((when, value, r2, over2, out))
        if rule[0] == "all_and_majority":                         # every other member, and that a strict majority of the roster
            yes, n = count(value, "nontarget")
            if "one_voice" in MUT: return out if yes >= 1 else None
            return out if n and yes == n and 2 * yes > len(base("all")) else None
        yes, n = count(value, over, when == "close")
        if "one_voice" in MUT: return out if yes >= 1 else None
        if when == "once" and value == "approve" and spec.get("target_votes") and p.get("target") and rule[0] in ("strict", "atleast"):
            # the target's own yes is a voice toward the floor of two, never part of the enact fraction (decide(), CC 4.5.13)
            tv = 1 if said.get(p["target"]) == "approve" else 0
            return out if met(rule[:3] + (0,), yes, n) and yes + tv >= rule[3] else None
        return out if met(rule, yes, n) else None
    for c in spec["clauses"]:
        if c[0] != "once": continue
        if elapsed and spec.get("late") == "closed": break
        got = clause(c)
        if got: return got
    if not elapsed: return "open"
    if spec.get("silent") and "no_silent" not in MUT and K.sel(inside, signer=p["target"]): return spec["silent"]
    for c in spec["clauses"]:
        if c[0] != "close": continue
        got = clause(c)
        if got: return got
    return spec["default"]


def _base(rows, past, p):
    spec = WN.WINDOWS[p["window"]]
    if not spec.get("door"): return WN_BASE(rows, past, p)
    cache = {}
    live = None
    def at(scope):
        nonlocal live
        if "live_roster" in MUT:                                    # MUTATION: counted over whoever is seated now
            if live is None:
                S = CK.State(rows, {q["id"]: True for q in rows})
                live = ST.Seats(S)
            return live.holders(scope, p["obj"])
        return ST.members_at(rows, past, p["obj"], p["head"], scope)
    def base(name):
        if name not in cache:
            if name in ("all", "others", "voted"):
                m = at(spec["counted"])
                if "any_opener" in MUT: m = m | {p["signer"]}               # MUTATION: the opener counted whatever its seat
                cache[name] = m - {p["signer"]} if name == "others" else m
            elif name == "moderate":                                # what window.outcome reads as the extra voices
                m = frozenset()
                for s in spec["extra"]: m |= at(s)
                if spec.get("target_votes") and p.get("target"): m |= {p["target"]}
                cache[name] = m
            elif name == "extra":
                cache[name] = base("moderate")
            elif name == "nontarget":
                cache[name] = base("all") - {p.get("target")}
            elif name == "all+target":
                cache[name] = base("all") | ({p["target"]} if p.get("target") else frozenset())
            elif name == "target":
                cache[name] = frozenset({p["target"]}) if p.get("target") else frozenset()
            elif name == "declared":                                # the consensus_protocol the group's founding row declares
                cache[name] = next((r.get("protocol") for r in rows if r["id"] == p["obj"]), None)
            else:
                cache[name] = at(name)
        return cache[name]
    return base


def secs(name):
    spec = WN.WINDOWS.get(name)
    if spec is None or not spec.get("door"): return WN_SECS(name)
    return NEVER if spec["secs"] is None else spec["secs"]


def key(name):
    """The name a door's opener row carries in its `window` field."""
    return "door:" + name




def rule(r, P, past):
    """window.rule, with the opener's scope and the concluder read from the door."""
    k = r["kind"]
    if k not in ("open", "answer", "receipt", "landing"):
        return ST.seat_rule(r, P, past)
    by = {q["id"]: q for q in P}
    if k == "open":
        spec = WN.WINDOWS[r["window"]]
        if not spec.get("door"): return WN.rule(r, P, past)
        if "any_opener" in MUT: return True                                      # MUTATION: any key opens
        return r["signer"] in ST.members_at(P, past, r["obj"], r["head"], spec["opener"])
    p = by.get(r["of"])
    if p is None or p["kind"] != "open": return False
    if k == "answer": return True
    spec, base = WN.WINDOWS[p["window"]], _base(P, past, p)
    if not spec.get("door"): return WN.rule(r, P, past)
    c = spec["concluder"]
    if "concluder_holder" in MUT and c == "target": c = spec["counted"]       # MUTATION: the halt landed by a holder
    if "concluder_target" in MUT and p.get("target"): c = "target"            # MUTATION: the target closes its own window
    if c == "target":
        if r["signer"] != p.get("target"): return False
    elif c == "winner":
        if r["signer"] not in base("all"): return False
        if k == "landing" and r["says"] not in ("open",) and r["says"] != "winner:" + r["signer"]: return False
    elif r["signer"] not in ST.members_at(P, past, p["obj"], p["head"], c):
        return False
    if k == "receipt": return True
    rec = by.get(r["receipt"])
    if rec is None or rec["kind"] != "receipt" or rec["signer"] != r["signer"] or rec["of"] != p["id"]: return False
    answers = K.sel(P, kind="answer", of=p["id"])
    inside = [q for q in P if q["id"] != rec["id"] and not past(q["id"], rec["id"])]
    return r["says"] == table_outcome(spec, p, answers, inside, base, r["at"] - rec["at"] >= secs(p["window"]))


def outcome(S, pid, how="recount", **kw):
    if "void" in MUT: how = "void"
    return WN.outcome(S, pid, how, **kw)


# ---- the doors, from the tables' own cells -----------------------------------------------------------------------
def two_path(fam):
    f = POLICY[fam]
    mc = MIN_COUNT.get(f["corridor"], 2)
    e = enact_rule(f["enact_rule"])
    if e[0] in ("strict", "atleast") and "enact_floor_off" not in MUT:   # MUTATION: the enact met by fewer voices than the floor
        e = e[:3] + (max(e[3], mc),)        # no single vote admits (CC 4.5.13): the enact, too, needs the floor's voices
    over_c = "others" if f["cancel_over"] == "others" else "all"
    cl = []
    if not f["irreversible"] or "ignore_irreversible" in MUT: cl.append(("once", "approve", e, "all", "landed"))
    if f["cancel_rule"]["kind"] != "none": cl.append(("close", "object", at_least_rule(f["cancel_rule"], mc), over_c, "cancelled"))
    cl.append(("close", "approve", e, "all", "landed"))
    if f["reverse_path"] and f["floor_rule"]["kind"] != "none" and "no_floor" not in MUT:
        cl.append(("close", "approve", at_least_rule(f["floor_rule"], mc), "all", "landed"))
    if "no_floor" in MUT and f["reverse_path"]:
        cl.append(("close", "approve", ("abs", 1), "all", "landed"))   # MUTATION: silence lands on the proposer alone
    default = {"cancelled": "cancelled", "stay_open": "open"}[f["at_window"]]
    silent = default if f["counted"]["target_silent"]["value"] == "yes" else None
    tv = f["counted"].get("target_voice", {}).get("value") == "yes" and "target_voice_ignored" not in MUT   # MUTATION: the cell not read
    spec = dict(policy=fam, kind="two_path", opener=f["counted"]["count_set"]["value"], counted=f["counted"]["count_set"]["value"],
                extra=(), target_votes=tv, opener_says="approve", kinds=("approve", "object"), clauses=tuple(cl),
                silent=silent, default=default, secs=f["window_secs"], concluder=f["counted"]["count_set"]["value"],
                late="counts", outcomes=("landed", "cancelled", "open"),
                cells={"opener": "counted.count_set (a member proposes)", "answers": "counted.count_set, voices objection + approve",
                       "enact": "enact_rule %s" % json.dumps(f["enact_rule"]), "cancel": "cancel_rule %s over %s" % (json.dumps(f["cancel_rule"]), f["cancel_over"]),
                       "floor": "floor_rule %s, min_count %d" % (json.dumps(f["floor_rule"]), mc), "window": "window_secs %d" % f["window_secs"],
                       "default": "at_window %s" % f["at_window"], "irreversible": str(f["irreversible"]), "reverse_path": str(f["reverse_path"]),
                       "target_silent": f["counted"]["target_silent"]["value"], "counted_at": f["counted"]["counted_at"]["value"],
                       "base": "%s; base_law: N for N <= k = %d (the sizes run, 3 and 4)" % (f["base"], BASE_LAW["k"])}
                | ({"target_voice": "counted.target_voice yes (%s)" % f["counted"]["target_voice"]["cc_ref"]} if tv else {}),
                unstated=["concluder: any member of the counted set (no cell names who lands)",
                          "landing row: none named",
                          "the opener's proposal counts as its own approval"]
                + ([] if BASE_LAW["k"] >= 4 else ["base '%s': expected_active(N), equal to N at the sizes run" % f["base"]])
                + (["outcome when the target signed inside the window: not stated; read as at_window (%s)" % f["at_window"]] if silent else [])
                + (["counted_at 'unstated': read at the head the proposal names (ruling)"] if f["counted"]["counted_at"]["value"] == "unstated" else []))
    return spec


def door_specs():
    D = {}
    for fam in ("default_content", "default_standing", "default_irreversible", "community_invite", "self_roster_add", "self_roster_evict"):
        D[fam] = two_path(fam)
    D["self_roster_add"] = stated(D["self_roster_add"], "self_roster_add", "self")
    # community_remove: cosigned under the room's declared protocol (enact cell `protocol`; the protocols' removal_rule)
    f = POLICY["community_remove"]
    assert f["enact"] == "protocol"
    for kind in ("unanimous", "majority", "quorum:{m}/{n}"):
        # the room declares its protocol in its founding row; the door reads that row, never the instance's name
        D["community_remove[%s]" % kind.split(":")[0]] = hold_close(dict(policy="community_remove", kind="cosigned", opener="member", counted="member",
            extra=(), target_votes=False, opener_says="assent", kinds=("assent",), clauses=(("once", "assent", ("protocol", "removal_rule", 2), "all", "removed"),),
            silent=None, default="cancelled", secs=f["window_secs"], concluder="member", late="counts", outcomes=("removed", "cancelled", "open"),
            declared=kind,
            cells={"enact": "protocol: the founding row's consensus_protocol -> protocols.kinds[KIND].removal_rule over its removal_set, never fewer than two voices (CC 3.3.4, CC 4.5.13)",
                   "declared": "the world's founding row declares %s%s" % (kind, " with m = 2" if "quorum" in kind else ""),
                   "window": "window_secs %d (hold)" % f["window_secs"], "default": "at_window cancelled", "counted_at": "signed (the head the row names)"},
            unstated=["concluder at the close: a node's own drop (cosign:{state} hold is local)"]))
    D["community_invite-invitee"] = dict(D["community_invite"], target_votes=False,
        contrast="not the table's reading: the invitee's own yes is not a voice (the row's target_voice cell read as no)")
    f = POLICY["moderation_action"]
    fl = {"kind": "voices", "count": 2} if "floor_two_voices" in MUT else f["floor_rule"]     # MUTATION: the old cell, two voices of the roster
    D["moderation_action"] = stated(dict(policy="moderation_action", kind="mirror", opener="member", counted="member", extra=("moderate",),
        target_votes=False, opener_says=None, kinds=("answered", "act", "keep"),
        clauses=(("once", "answered", ("abs", 1), "extra", "answered"),
                 ("close", "act", at_least_rule(fl, 2), "voted" if fl["kind"] == "voted_majority" else "all", "fallback")),
        silent=None, default="lapsed", secs=f["window_secs"], concluder="member", late="counts", outcomes=("answered", "fallback", "lapsed", "open"),
        cells={"enact": "role_at moderate 1 (a holder of the moderate duty)",
               "floor": "floor_rule voted_majority 2: more than half of the members who voted, at least two voices",
               "window": "window_secs 172800", "default": "at_window tallied -> lapsed"},
        unstated=["who opens: a member raising the action", "what the members' answers are: 'act' and 'keep' (voices cell 'unstated')",
                  "concluder: a member"]), "moderation_action", "member")
    f = POLICY["moderation_overturn"]
    D["moderation_overturn"] = dict(policy="moderation_overturn", kind="mirror", opener="moderate", counted="member", extra=(), target_votes=False,
        opener_says=None, kinds=("object",), clauses=(("once", "object", ("strict", 1, 2, 2), "all", "lifted"),),
        silent=None, default="stands", secs=f["window_secs"], concluder="member", late="counts", outcomes=("lifted", "stands", "open"),
        cells={"opener": "the moderator's act (standing_set: roster at the instant of the act)", "enact": "strict majority, floor 2 voices",
               "counted_at": "act: the head the act names", "window": "window_secs 172800", "default": "at_window lapsed (the lift lapses; the act stands)"},
        unstated=["concluder: a member (none named; reactions.json has no clock entry for the lift)"])
    f = POLICY["moderator_recall"]
    D["moderator_recall"] = hold_close(dict(policy="moderator_recall", kind="cosigned", opener="member", counted="member", extra=(), target_votes=False,
        opener_says="assent", kinds=("assent",), clauses=(("once", "assent", ("strict", 2, 3, 2), "all", "recalled"),),
        silent=None, default="cancelled", secs=f["window_secs"], concluder="member", late="counts", outcomes=("recalled", "cancelled", "open"),
        cells={"enact": "2/3 strict, floor 2 voices", "window": "window_secs 259200 (hold)", "default": "at_window cancelled"},
        unstated=["whether the recalled moderator counts in the base (here: not a member key)", "no clock entry in reactions.json"]))
    f = POLICY["accord_halt"]
    halt = dict(policy="accord_halt", kind="mirror", opener="holder", counted="holder", extra=(), target_votes=False,
        opener_says="confirm", kinds=("confirm",), clauses=(("once", "confirm", ("strict", 1, 2, 1), "all", "confirmed"),),
        silent=None, default="lapsed", secs=f["window_secs"], late="counts", outcomes=("confirmed", "lapsed", "open"), concluder=None,
        cells={"enact": "one_of_n fires (the open row is the act)", "confirm": "cancel_rule strict_majority over base", "window": "window_secs 86400 = clock fuse",
               "default": "at_window lapsed", "clock": "reactions: fuse from first_held by receipt"},
        unstated=["concluder: no cell names who lands the lapse", "late answer: no cell says whether a late confirmation counts"])
    # the manifest's reading (each halted node for itself, a late confirmation closed), and the two readings it rules out
    told = stated(halt, "accord_halt", "target")
    D["accord_halt@node+late_closed"] = told
    if told.get("landing_from"):
        D["accord_halt@node"] = dict(told, late="counts", landing_from=None, contrast="not the table's reading: a late confirmation is counted")
        D["accord_halt@holder"] = dict(told, concluder="holder", late="counts", landing_from=None, landing_row="a holder's own row (none exists)",
                                       contrast="not the table's reading: a holder concludes and a late confirmation is counted")
    else:
        D["accord_halt@node"] = dict(told, unstated=told["unstated"] + ["concluder read as the halted node itself; the fuse is per node"])
        D["accord_halt@holder"] = dict(told, concluder="holder", unstated=told["unstated"] + ["concluder read as a holder (window.py)"])
        D["accord_halt@node+late_closed"] = dict(D["accord_halt@node"], late="closed", unstated=D["accord_halt@node"]["unstated"] + ["late answer read as closed"])
    for fam in ("custodian_replace", "affiliation_member_action"):
        f = POLICY[fam]
        D[fam] = dict(policy=fam, kind="cosigned", opener="pair", counted="pair", extra=(), target_votes=False, opener_says="assent",
            kinds=("assent",), clauses=(("once", "assent", enact_rule(f["enact_rule"]), "all", "landed"),), silent=None, default="open",
            secs=None, concluder="pair", late="counts", outcomes=("landed", "open"),
            cells={"enact": "fraction 2/2: a cell of n/n needs the whole set (build_governance_policy.votes)", "standing_set": f["standing_set"],
                   "window": "window_secs 0, at_window '—': no window"},
            unstated=[])
    f = POLICY["moderator_election"]
    D["moderator_election"] = stated(dict(policy="moderator_election", kind="ranked", opener="member", counted="member", extra=(), target_votes=False,
        opener_says=None, kinds=("ballot",), clauses=(("close", "ballot", ("ranked", 2), "all", "winner:"),), options=("m1", "m2", "m3"),
        silent=None, default="open", secs=f["window_secs"], concluder="winner", late="counts", outcomes=("winner:m1", "winner:m2", "winner:m3", "open"),
        cells={"enact": "ranked_irv choices 3", "floor": "2 voices", "window": "window_secs 86400", "default": "at_window stay_open",
               "counted_at": "named"},
        unstated=["who opens: the lock is no row (named by election id); here a member's open row stands for it",
                  "options: the roster in worthiness order (given)", "a declining winner passing to the next: not run"]), "moderator_election", "member")
    assert POLICY["cosigned_act"]["enact"] == "protocol"
    D["cosigned_act"] = hold_close(dict(policy="cosigned_act", kind="cosigned", opener="member", counted="member", extra=(), target_votes=False,
        opener_says="assent", kinds=("assent",), clauses=(("once", "assent", ("protocol", "rule", 1), "all", "landed"),), silent=None,
        default="cancelled", secs=POLICY["cosigned_act"]["window_secs"], concluder="member", late="counts", outcomes=("landed", "cancelled", "open"),
        declared="majority",
        cells={"enact": "protocol: the founding row's consensus_protocol -> protocols.kinds[KIND].rule (the group's declared rule)",
               "declared": "the world's founding row declares majority", "window": "hold 259200, a group may set longer", "default": "at_window cancelled"},
        unstated=[]))
    D["accord_majority"] = dict(policy="accord_majority", kind="cosigned", opener="holder", counted="holder", extra=(), target_votes=False,
        opener_says="assent", kinds=("assent",), clauses=(("once", "assent", ("strict", 1, 2, 1), "all", "landed"),), silent=None,
        default="open", secs=None, concluder="holder", late="counts", outcomes=("landed", "open"),
        cells={"enact": "strict_majority of the standing holders", "window": "none"}, unstated=[])
    # ---- clocks of reactions.json that are doors -------------------------------------------------------------
    D["deletion_sla"] = stated(dict(policy="consent:deletion_sla:{days}", kind="clock", opener="subject", counted="producer", extra=(), target_votes=False,
        opener_says=None, kinds=("deleted",), clauses=(("once", "deleted", ("abs", 1), "all", "deleted"),), silent=None, default="breached",
        secs=30 * 86400, concluder="substrate", late="counts", outcomes=("deleted", "breached", "open"),
        cells={"clock": "sla, dur self.days (the opener row's own member)", "answers": "unless withdrawn/superseded/purged by producer",
               "close": "emit hard_case:deletion_window_breach by identity:substrate_persist"},
        unstated=[]), "deletion_sla", "substrate")
    D["accord_roster_change"] = stated(dict(policy="group:roster (accord)", kind="clock", opener="holder", counted="holder", extra=(), target_votes=False,
        opener_says="yes", kinds=("yes",), clauses=(("close", "yes", ("strict", 1, 2, 1), "all", "landed"),), silent=None, default="lapsed",
        secs=259200, concluder="holder", late="counts", outcomes=("landed", "lapsed", "open"),
        cells={"clock": "W admission_freshness_window_secs max accord_roster_window_max_secs, from first_held by receipt",
               "close": "lapsed unless fold policy_met", "count": "CC 4.2.6: yes against the standing roster"},
        unstated=["concluder: a holder", "W is also the proposal's own window_until (cells.tsv:171)"]), "accord_roster_change", "holder")
    D["harm_report"] = stated(dict(policy="moderation:{allegation_type}[harm_report]", kind="clock", opener="member", counted="member", extra=("moderate",),
        target_votes=False, opener_says=None, kinds=("keep",),
        clauses=(("once", "keep", ("abs", 1), "extra", "kept"), ("close", "keep", ("strict", 1, 2, 2), "voted", "kept")),
        silent=None, default="removed", secs=172800, concluder="member", late="counts", outcomes=("kept", "removed", "open"),
        cells={"clock": "window moderation_fallback_window_secs from first_held by receipt", "close": "withdrawn(target) unless fold keep_decided"},
        unstated=["keep_decided: a moderator's keep at once, or a strict majority of those who voted, floor two (CC 4.5.13 text)"]), "harm_report", "member")
    D["takedown_withhold"] = stated(dict(policy="takedown_notice:{basis}", kind="clock", opener="takedown", counted="member", extra=("review",),
        target_votes=False, opener_says=None, kinds=("reversed", "lift"),
        clauses=(("once", "reversed", ("abs", 1), "extra", "reversed"), ("once", "lift", ("strict", 1, 2, 2), "all", "lifted")),
        silent=None, default="destroy", secs=10 * 86400, concluder="target", late="counts", outcomes=("reversed", "lifted", "destroy", "open"),
        cells={"clock": "withhold dur withhold_window_<basis> from admitted(self) by receipt", "close": "do destroy_bytes"},
        unstated=["concluder: the holding device (custody:ack signer), per node", "answers: reconsideration reversed; members' lift"]), "takedown_withhold", "target")
    D["retirement_objection"] = stated(dict(policy="retirement:{state}[decided]", kind="clock", opener="decider", counted="decider", extra=(),
        target_votes=True, opener_says=None, kinds=("withdrawn", "object"),
        clauses=(("once", "withdrawn", ("abs", 1), "all", "cancelled"), ("close", "object", ("abs", 1), "target", "objected")),
        silent=None, default="proceed", secs=259200, concluder="target", late="counts", outcomes=("cancelled", "objected", "proceed", "open"),
        cells={"clock": "objection dur default_standing.window_secs from first_held by receipt",
               "objection": "the agent signs its own; a `decided` row that does not name one its signer held concludes nothing (CC 7.5.5): the recount"},
        unstated=["the family of the agent's objection row is not named in the text",
                  "an objection first held after the close: no sentence says whether it counts; run as counted",
                  "the decider is run as the signer of the opening `decided` row (the cell's `author`); the register has the agent key sign that row and name the decider in `decided_by`",
                  "concluder: the agent (it signs the ladder)"]), "retirement_objection", "target", author="decider")
    D["decay_stage"] = stated(dict(policy="consent:decay:{stage}", kind="clock", opener="subject", counted="subject", extra=(), target_votes=False,
        opener_says=None, kinds=(), clauses=(), silent=None, default="due", secs=30 * 86400, concluder="author", late="counts",
        outcomes=("due", "open"), cells={"clock": "anonymise / complete, from admitted revocation"},
        unstated=["a duty clock: no answers", "landing row: the runner's own stage row"]), "decay_stage", "author")
    D["invitation"] = stated(dict(policy="membership:{stage}[proposal] expiry", kind="extra", opener="member", counted="member", extra=(),
        target_votes=True, opener_says=None, kinds=("accept",), clauses=(("once", "accept", ("abs", 1), "target", "admitted"),),
        silent=None, default="closed", secs=7 * 86400, concluder="member", late="closed", outcomes=("admitted", "closed", "open"),
        cells={"expiry": "expires_at, max membership_proposal_max_secs, from asserted_at by signed (CC 3.1.3.2 (3))"},
        unstated=["late=closed: an acceptance not in the landing's past by its close does not admit"]), "invitation", "member")
    # ---- a poll (CC 4.5.13): the rule its opening row states, or the default of the policy row `poll` ---------------
    f = POLICY["poll"]
    own = "the window's length: the poll's own close, stated by its opening row; run at 86 400 s"
    for name, rule, over, cell, extra in (
            ("poll", at_least_rule(f["floor_rule"], MIN_COUNT.get(f["corridor"], 2)), "voted",
             "floor_rule voted_majority 2: more than half of those who voted, at least two voices (the poll states no rule)", []),
            ("poll[stated]", ("strict", 2, 3, 2), "all", "the rule the poll's opening row states (CC 4.5.13)",
             ["the poll's own rule: run here as more than two thirds of the roster, floor two"])):
        if "stated_ignored" in MUT:                                  # MUTATION: the opening row's own rule is not read
            rule, over = at_least_rule(f["floor_rule"], 2), "voted"
        D[name] = dict(policy="poll", kind="tally", opener="member", counted="member", extra=(), target_votes=False, opener_says=None,
            kinds=("for", "against"), clauses=(("close", "for", rule, over, "carried"),), silent=None, default="not_carried", secs=86400,
            concluder="member", late="counts", outcomes=("carried", "not_carried", "open"),
            landing_row="ballot:tally:{poll_id} (the tally member's row; CC 3.1.3)",
            cells={"count": cell, "counted": "counted.count_set member, voice person, counted_at named", "default": "at_window tallied",
                   "window": "window_secs 0: the poll's own close"},
            unstated=extra + [own, "who opens: no family is named for the row that opens a poll; a member's open row stands for it",
                              "concluder: the period's tally member signs the result; run as a member, since a tally member is drawn from a group secret that is not a row",
                              "a ballot after the closing period: a secret poll counts only its closing period (CC 6.1.9); the door recounts a concurrent ballot"])
    # ---- a Wise Authority adjudication (CC 4.3): one row cosigned under the body's own declared protocol ------------
    f = POLICY["wa_adjudication"]
    assert f["enact"] == "protocol"
    D["wa_adjudication"] = hold_close(dict(policy="wa_adjudication", kind="cosigned", opener="wa", counted="wa", extra=(), target_votes=False,
        opener_says="assent", kinds=("assent",),
        clauses=(("once", "assent", ("protocol", "rule", 1), "voted" if "live_subset" in MUT else "all", "landed"),),   # MUTATION: the live subset
        silent=None, default="cancelled", secs=f["window_secs"], concluder="wa", late="counts", outcomes=("landed", "cancelled", "open"),
        declared="majority",
        cells={"enact": "protocol: the founding row's consensus_protocol -> protocols.kinds[KIND].rule (the body's declared rule)",
               "declared": "the world's founding row declares majority",
               "counted": "counted.count_set wa, voice person, counted_at named: the full seated roster the finding names",
               "window": "window_secs %d (hold)" % f["window_secs"], "default": "at_window cancelled"},
        unstated=["concluder at the close: a node's own drop (cosign:{state} hold is local)"]))
    # ---- a deferral (CC 4.3): the request states its own end; no default answers it; at the end it goes up ----------
    D["deferral"] = stated(dict(policy="deferral:request", kind="extra", opener="deferring", counted="resolve_deferral", extra=(), target_votes=False,
        opener_says=None, kinds=("approved", "rejected"),
        clauses=(("once", "approved", ("abs", 1), "all", "approved"), ("once", "rejected", ("abs", 1), "all", "rejected")),
        silent=None, default="rejected" if "default_answers" in MUT else "escalated",                              # MUTATION: silence answers
        secs=7 * 86400, concluder="deferring", late="counts", outcomes=("approved", "rejected", "escalated", "open"),
        landing_row="none: each node reads the request's own end; going up is an effect and no row",
        cells={"expiry": "expiry required valid_until (the request's own end)",
               "close": "CC 4.3: with no answer held at the end the request goes up to whoever conferred the seat; the agent stays deferred",
               "answers": "deferral:response:{outcome}, approved | rejected, by the seat the request is addressed to"},
        unstated=["concluder: each node reads the request's own end; run as the deferring party's node",
                  "an answer of the seat first held after the end: no sentence says whether it still answers; run as counted",
                  "the conferrer's own answer once the request has gone up: the same door one seat up; not run",
                  "going up at the end is a sentence of CC 4.3 and no clause of the reactions table"]), "deferral", "deferring")
    # ---- the one row that opens a seal (CC 3.1.5, CC 3.4.7): one signature of a stated seat, no window ------------------
    D["archive_release"] = dict(policy="archive_release:{basis}", kind="seat_act", opener="resolve_deferral", counted="resolve_deferral", extra=(),
        target_votes=False, opener_says="assent", kinds=("assent",), clauses=(("once", "assent", ("abs", 1), "all", "released"),), silent=None,
        default="open", secs=None, concluder="resolve_deferral", late="counts", outcomes=("released", "open"),
        landing_row="the release row itself",
        cells={"opener": "the conferrer of the retired agent's seat or the person holding its unscoped seat (resolve_deferral, unscoped)",
               "window": "none: one row"},
        unstated=[])
    for name in list(D):
        D[name] = apply_text(name, D[name])
    return D


def install(D):
    WN.WINDOWS = dict(ORIG_WINDOWS)
    for name, spec in D.items():
        spec["door"] = True
        WN.WINDOWS[key(name)] = spec


DOORS = door_specs()
install(DOORS)
WN.table_outcome = table_outcome
WN._base = _base
WN.secs = secs


def rebuild():
    """Re-read the specs after a mutation switch changed how cells are read."""
    global DOORS
    DOORS = door_specs()
    install(DOORS)
