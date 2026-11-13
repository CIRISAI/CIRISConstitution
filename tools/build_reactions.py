#!/usr/bin/env python3
"""
CC — reactions and clocks as data: when a row expires, what window runs from it, and what a node reads, does or
emits when a row lands, a clock closes or a fold changes.

Reads formal/derivation/reaction_text.tsv and writes manifests/reactions.json, one entry per clause. A reaction
relates two families and half its triggers are a clock, which is no transition, so it has a table of its own.

    cell     := clause *( "; " clause )
    clause   := [ selector " " ] ( expiry | clock | land | react )
    selector := "[" LEAF *( "|" LEAF ) "]" | "@" SCOPE
    expiry   := "expiry " MODE [ " " MEMBER ] [ " eq " dur ] [ " default " dur ] [ " max " dur ] [ " from " origin ] [ " by " JUDGE ]
    clock    := "clock " NAME " = " dur [ " default " dur ] [ " max " dur ] " from " origin [ " by " JUDGE ]
    land     := "land " NAME ( " local" | " by " ROLE " as " famref ) [ " late " ( "closed" | "counts" ) ]
    react    := "on " event *( "|" event ) [ " unless " event *( "|" event ) ] " -> " effect *( ", " effect )
    event    := STATE "(" famref [ "," ACTOR ] ")" | "close(" NAME ")" | "fold(" FOLDNAME ")"
    effect   := [ "should " | "may " ] ( "emit " famref " by " ROLE | "read " VERDICT [ " of " famref ] | "do " ACT | "open " POLICY_ROW )
    dur      := CONSTANT | POLICY_ROW ".window_secs" | HOLDER "." MEMBER
    origin   := "first_held" | SIGNED_MEMBER | event *( "|" event )

A duration is a name and never a number: a row of constitution/constants.tsv, a window of the policy table, or
a member of a signed holder (a charter, a group record, the row itself). `emit` produces a row, which enters by
the door like any other; every other effect is a verdict a node recomputes. The rule that a row a clock or a
fold causes has one emitter (CC 4.5.13) is checked: such an emit not signed `by origin_door` is listed, and the
list may only shrink.

A `land` clause says who concludes a window. NAME is a clock of the same family and leaves, or `expiry` for the
row's own stated end. `by ROLE as FAMREF` names the seat that signs the outcome and the row that carries it.
`local` says each node reads the close on its own clock, the outcome binds that node alone and nothing is signed.
`late closed` says an answer the concluder first holds after its close changes nothing, and `late counts` says
it is still counted. A clause is written only where a sentence of the Parts states it. The clocks with no such
clause are listed, and that list may only shrink.

Run: python3 tools/build_reactions.py            # build
     python3 tools/build_reactions.py --check    # the manifest is current
"""
import csv, glob, hashlib, json, os, re, sys
from collections import Counter, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT = os.path.join(ROOT, "formal", "derivation", "reaction_text.tsv")
OUT = os.path.join(ROOT, "manifests", "reactions.json")
MODES = ("required", "optional", "forbidden", "none")
JUDGES = ("signed", "receipt", "origin_door")
STATES = ("admitted", "withdrawn", "superseded", "recanted", "purged", "refused", "matched", "sealed")
NEW_STATES = ("purged", "matched", "sealed")
SCOPES = ("self", "family", "affiliations", "community", "federation", "accord", "public")
HOLDERS = ("charter", "group", "self", "decay_protocol", "community")
SIGNED_ORIGINS = ("asserted_at", "claimed_at", "effective_at", "cosigned_at", "delegation_valid_from")
EMITTER_OPEN_MAX = 7   # clock- or fold-caused emits not signed by the origin door; the number only falls
LANDING_OPEN_MAX = 4   # clocks whose concluder no clause states; the number only falls
LATE = ("closed", "counts")
NAME = r"[A-Za-z_][A-Za-z_0-9]*"

ACTORS = ("producer", "subject")   # whose act the event is, where the rule turns on it (CC 3.3.1 D1)


class ReactionError(ValueError):
    pass


def parse_events(s, need):
    out = []
    for e in s.split("|"):
        m = re.fullmatch(r"([a-z]+)\((.+)\)", e)
        if not m or m.group(1) not in STATES + ("close", "fold"):
            raise ReactionError(f"event {e!r}")
        kind, arg = m.groups()
        arg, _, actor = arg.partition(",")
        if actor and (kind not in STATES or actor not in ACTORS): raise ReactionError(f"event {e!r}: actor {actor!r}")
        if kind in STATES and arg not in ("self", "target"): need["families"].append(arg)
        if kind in NEW_STATES: need["marks"].append(kind)
        out.append({"event": kind, "of": arg, **({"by": actor} if actor else {})})
    return out


def parse_dur(s, need):
    if not re.fullmatch(NAME + r"(\.[A-Za-z_*]+)?", s):
        raise ReactionError(f"duration {s!r}")
    need["durs"].append(s)
    return s


def parse_origin(s, need):
    if s == "first_held" or s in SIGNED_ORIGINS:
        return s
    return parse_events(s, need)


def parse_clause(raw, need):
    c = OrderedDict()
    m = re.match(r"\[([a-zA-Z_0-9|]+)\] ", raw)
    if m:
        c["leaves"] = m.group(1).split("|"); raw = raw[m.end():]
    m = re.match(r"@([a-z]+) ", raw)
    if m:
        if m.group(1) not in SCOPES: raise ReactionError(f"scope {m.group(1)!r}")
        c["scope"] = m.group(1); raw = raw[m.end():]
    def tail(rest, keys):
        """` key value` pairs in the fixed order of the grammar"""
        got = OrderedDict()
        for k in keys:
            m = re.match(r" " + k + r" (\S+)", rest)
            if m:
                got[k] = m.group(1); rest = rest[m.end():]
        if rest: raise ReactionError(f"left over {rest!r}")
        return got
    if raw.startswith("expiry "):
        m = re.match(r"expiry ([a-z]+)(?: (?!eq |default |max |from |by )(" + NAME + r"))?", raw)
        if not m or m.group(1) not in MODES: raise ReactionError(f"expiry {raw!r}")
        c["kind"] = "expiry"; c["mode"] = m.group(1)
        if m.group(2): c["member"] = m.group(2)
        t = tail(raw[m.end():], ("eq", "default", "max", "from", "by"))
    elif raw.startswith("clock "):
        m = re.match(r"clock (" + NAME + r") = (\S+)", raw)
        if not m: raise ReactionError(f"clock {raw!r}")
        c["kind"] = "clock"; c["name"] = m.group(1); c["dur"] = parse_dur(m.group(2), need)
        t = tail(raw[m.end():], ("default", "max", "from", "by"))
        if "from" not in t: raise ReactionError(f"a clock runs from an origin: {raw!r}")
    elif raw.startswith("land "):
        m = re.fullmatch(r"land (" + NAME + r")(?: (local)| by (\S+) as (\S+))(?: late ([a-z]+))?", raw)
        if not m or (m.group(5) and m.group(5) not in LATE): raise ReactionError(f"landing {raw!r}")
        c["kind"] = "land"; c["name"] = m.group(1)
        if m.group(2):
            c["concluder"] = "local"
        else:
            need["roles"].append(m.group(3)); need["families"].append(m.group(4))
            c["concluder"] = m.group(3); c["landing"] = m.group(4)
        if m.group(5): c["late"] = m.group(5)
        return c
    elif raw.startswith("on "):
        m = re.fullmatch(r"on (\S+)(?: unless (\S+))? -> (.+)", raw)
        if not m: raise ReactionError(f"reaction {raw!r}")
        c["kind"] = "react"; c["on"] = parse_events(m.group(1), need)
        if m.group(2): c["unless"] = parse_events(m.group(2), need)
        effects = []
        for e in m.group(3).split(", "):
            force = "must"
            for w in ("should", "may"):
                if e.startswith(w + " "): force = w; e = e[len(w) + 1:]
            me = re.fullmatch(r"emit (\S+) by (\S+)", e)
            mr = re.fullmatch(r"read (" + NAME + r")(?: of (\S+))?", e)
            md = re.fullmatch(r"do (" + NAME + r")", e)
            mo = re.fullmatch(r"open (" + NAME + r")", e)
            if me:
                need["families"].append(me.group(1)); need["roles"].append(me.group(2))
                effects.append({"effect": "emit", "family": me.group(1), "by": me.group(2), "force": force})
            elif mr:
                if mr.group(2) and mr.group(2) not in ("self", "target"): need["families"].append(mr.group(2))
                effects.append({"effect": "read", "verdict": mr.group(1), "of": mr.group(2), "force": force})
            elif md: effects.append({"effect": "do", "act": md.group(1), "force": force})
            elif mo:
                need["policy_rows"].append(mo.group(1)); effects.append({"effect": "open", "policy": mo.group(1), "force": force})
            else: raise ReactionError(f"effect {e!r}")
        c["effects"] = effects
        return c
    else:
        raise ReactionError(f"clause {raw!r}")
    for k in ("eq", "default", "max"):
        if k in t: c[k] = parse_dur(t[k], need)
    if "from" in t: c["from"] = parse_origin(t["from"], need)
    if "by" in t:
        if t["by"] not in JUDGES: raise ReactionError(f"judge {t['by']!r}")
        c["by"] = t["by"]
    return c


def parse(s):
    need = {"families": [], "roles": [], "policy_rows": [], "durs": [], "marks": []}
    return [parse_clause(x, need) for x in s.strip().split("; ")], need


def vocab():
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    tr = json.load(open(os.path.join(ROOT, "manifests", "transitions.json"), encoding="utf-8"))
    fams = {r["family"] for r in tr["rows"]}
    for f in json.load(open(os.path.join(ROOT, "manifests", "namespace_registry.json"), encoding="utf-8"))["families"]:
        fams.add(f["prefix"]); fams.update(f.get("leaves", []))
    pol = {f["family"] for f in json.load(open(os.path.join(ROOT, "manifests", "governance_policy.json"), encoding="utf-8"))["families"]}
    consts = {l.split("\t")[0] for l in open(os.path.join(ROOT, "constitution", "constants.tsv"), encoding="utf-8").read().split("\n")[1:] if l}
    return {"families": fams, "model": {r["family"] for r in tr["rows"]}, "policy_rows": pol, "constants": consts,
            "roles": set(tr["_meta"]["role_tokens"]) | {"author", "origin_door"}}


def closure(need, voc):
    import guard_grammar as gg
    bad = [f"family {f}" for f in need["families"] if not gg.family_ok(f, voc["families"])]
    bad += [f"role {r}" for r in need["roles"] if r not in voc["roles"]]
    bad += [f"policy row {p}" for p in need["policy_rows"] if p not in voc["policy_rows"]]
    for d in need["durs"]:
        head, _, member = d.partition(".")
        ok = (not member and d in voc["constants"]) or (member == "window_secs" and head in voc["policy_rows"]) or (member and head in HOLDERS)
        if not ok: bad.append(f"duration {d}")
    return bad


def build():
    from build_family_model import section_span
    voc = vocab()
    entries, marks, open_emit = [], {k: 0 for k in NEW_STATES}, []
    lines = [l for l in open(TEXT, encoding="utf-8").read().split("\n") if l and not l.startswith("#")]
    for r in csv.DictReader(lines, delimiter="\t", quoting=csv.QUOTE_NONE):
        where = f"reaction_text.tsv: {r['family']} ({r['cc_ref']})"
        try:
            clauses, need = parse(r["reaction"])
        except ReactionError as e:
            sys.exit(f"{where}: {e}")
        bad = closure(need, voc)
        if r["family"] != "*" and r["family"] not in voc["model"]: bad.append("no such family")
        if bad: sys.exit(f"{where}: outside the vocabularies: " + "; ".join(bad))
        span = section_span(r["cc_ref"])
        if span is None or r["quote"] not in span:
            sys.exit(f"{where}: the quoted words do not stand in {r['cc_ref']}")
        for k in need["marks"]: marks[k] += 1
        for c in clauses:
            if c["kind"] == "react" and any(e["event"] in ("close", "fold") for e in c["on"]):
                for e in c["effects"]:
                    if e["effect"] == "emit" and e["by"] != "origin_door":
                        open_emit.append(f"{r['family']}: emit {e['family']} by {e['by']}")
            body = OrderedDict([("family", r["family"])] + list(c.items()))
            same = next((e for e in entries if OrderedDict((k, v) for k, v in e.items() if k != "cc_ref") == body), None)
            if same:                                   # one clause stated in several sections is one entry
                if r["cc_ref"] not in same["cc_ref"]: same["cc_ref"].append(r["cc_ref"])
            else:
                body["cc_ref"] = [r["cc_ref"]]; entries.append(body)
    open_emit = sorted(set(open_emit))
    if len(open_emit) > EMITTER_OPEN_MAX:
        sys.exit(f"reactions: {len(open_emit)} clock- or fold-caused emits are not signed by the origin door, more than {EMITTER_OPEN_MAX}")
    key = lambda e: (e["family"], "|".join(e.get("leaves", ())), e.get("name", "expiry"))
    show = lambda k: k[0] + (f" [{k[1]}]" if k[1] else "") + " " + k[2]
    windows = [key(e) for e in entries if e["kind"] in ("clock", "expiry")]
    lands = [key(e) for e in entries if e["kind"] == "land"]
    stray = sorted(show(k) for k in set(lands) - set(windows)); twice = sorted(show(k) for k in set(lands) if lands.count(k) > 1)
    if stray or twice:
        sys.exit("reactions: a landing names one clock or expiry of its own family and leaves, once: " + "; ".join(
            [f"no clock for {k}" for k in stray] + [f"two landings for {k}" for k in twice]))
    unlanded = sorted(show(key(e)) for e in entries if e["kind"] == "clock" and key(e) not in lands)
    if len(unlanded) > LANDING_OPEN_MAX:
        sys.exit(f"reactions: {len(unlanded)} clocks have no landing clause, more than {LANDING_OPEN_MAX}: " + "; ".join(unlanded))
    land_by = lambda f: OrderedDict(sorted(Counter(f(e) for e in entries if e["kind"] == "land").items()))
    kinds = {k: sum(1 for e in entries if e["kind"] == k) for k in ("expiry", "clock", "land", "react")}
    emits = sum(1 for e in entries if e["kind"] == "react" for x in e["effects"] if x["effect"] == "emit")
    doc = OrderedDict([("_meta", OrderedDict([
        ("source", "formal/derivation/reaction_text.tsv"), ("cc_section", "4.5.13"),
        ("reading", "an entry is an expiry rule, a named clock, a landing or a reaction of one family; `emit` produces a row that enters by the door, every other effect is a verdict a node recomputes from the rows it holds and the instant"),
        ("durations", "a duration is a name: a row of constitution/constants.tsv, POLICY_ROW.window_secs of the governance policy table, or HOLDER.member of a signed record"),
        ("entries", len(entries)), ("kinds", kinds), ("emits", emits),
        ("new_event_words", marks),
        ("landing", OrderedDict([("rule", "a land entry names who concludes a clock or an expiry of its family: a seat and the row it signs, or `local` where each node reads the close on its own clock and nothing is signed"),
                                 ("late", "`closed`: an answer the concluder first holds after its close changes nothing; `counts`: it is still counted; absent: no sentence states it"),
                                 ("by_concluder", land_by(lambda e: e["concluder"])), ("by_late", land_by(lambda e: e.get("late", "unstated"))),
                                 ("clocks_with_no_landing", unlanded)])),
        ("one_emitter", OrderedDict([("rule", "a row a clock or a fold causes is emitted by the door the causing row first entered (CC 4.5.13)"),
                                     ("not_yet_by_origin_door", open_emit)]))])),
        ("reactions", entries)])
    return json.dumps(doc, indent=1, ensure_ascii=False) + "\n", doc["_meta"]


def self_test():
    good = ["expiry none; clock fuse = charter.halt_fuse_secs from first_held by receipt; on close(fuse) unless admitted(accord:lifecycle:confirmed) -> read lapsed",
            "[granted] expiry optional valid_until default consent_temporary_ttl_secs from asserted_at",
            "@community on sealed(self) -> emit key_grant:epoch by author",
            "on withdrawn(self)|recanted(self) -> do cease_replication, should do deregister_peer",
            "on close(sla) unless withdrawn(target,producer)|purged(target) -> read breached",
            "land fuse local late closed", "[pending] land hold local", "land window by winner as ballot:moderator_acceptance late counts"]
    bad = ["expiry sometimes", "clock x = 86400 from first_held", "clock x = a_secs", "on landed(self) -> read x", "on close(x) -> shout", "@galaxy expiry none",
           "on withdrawn(target,anyone) -> read x", "on close(sla,producer) -> read x",
           "land fuse", "land fuse by holder", "land fuse local as hard_case:x", "land fuse local late sometimes", "land fuse late closed"]
    for g in good: parse(g)
    n = 0
    for g in bad:
        try: parse(g)
        except ReactionError: n += 1
    assert n == len(bad), f"{len(bad) - n} malformed reactions parsed"
    return f"reaction grammar: {len(good)} forms parse, {len(bad)} malformed forms refused"


if __name__ == "__main__":
    msg = self_test()
    if "--self-test" in sys.argv:
        print(msg); sys.exit(0)
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    js, meta = build()
    if "--check" in sys.argv:
        ok = os.path.exists(OUT) and open(OUT, encoding="utf-8").read() == js
        print("reactions: current" if ok else "reactions.json is stale (run tools/build_reactions.py)"); sys.exit(0 if ok else 1)
    open(OUT, "w", encoding="utf-8").write(js)
    print(f"reactions: {meta['entries']} entries {meta['kinds']}, {meta['emits']} emits, {len(meta['one_emitter']['not_yet_by_origin_door'])} clock- or fold-caused emits not by the origin door, "
          f"{len(meta['landing']['clocks_with_no_landing'])} clocks with no landing clause")
