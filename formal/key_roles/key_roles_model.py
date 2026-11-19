#!/usr/bin/env python3
"""formal/key_roles: which key signs what, in one home, through the split (CC 3.4.7.3, CC 3.2, CC 2.4.1.1).

One home: a person's roster key P (and, in one configuration, the same person's accord-holder key H), a node key N,
an agent key A, and in the fused configuration one configured key C that turns out to be the actor's, so that a
node key is minted beside it (the split). Every sequence of structural acts up to BOUND is explored from each
starting configuration: owner-bindings (cosigned or not, a second owner), the split, renewal, revocation by each
party, rotation (single and rival), losing the person's seed on the device, joining a private room, and the
occurrence of a machine key under the person's identity. In every reachable state every use in
manifests/key_roles.json is tried by every party and every read is asked, and R1-R17 are checked.

The uses are not written here. They are read from the manifest (tools/build_key_roles.py, from the transitions and
formal/derivation/signer_kind.tsv), and the model refuses to run if a use it names is missing. An R that reads an
open cell is reported OPEN, never PASS.

An implementation is a set of choices (which key signs a use for a party, how a key's kind is decided, what
owner_of returns, ...). `Correct` makes each choice from the text. Each plant changes one choice the way a shipped
bug did and must fail the R that names it.

Run: python3 formal/key_roles/key_roles_model.py --check
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MANIFEST = os.path.join(ROOT, "manifests/key_roles.json")
BOUND = 5
YEAR = 31_536_000  # key_record_max_secs, constants.tsv

PERSON = {"person", "holder"}
FORBIDDEN = [({"node"}, {"agent", "user"}), ({"user", "accord_holder"}, {"node", "agent"})]  # CC 3.4.7.1, P2:382


def load():
    d = json.load(open(MANIFEST, encoding="utf-8"))
    uses = {u["use"]: u for u in d["uses"]}
    need = ["@crossing", "@device_join", "@room_row", "@mls_leaf", "@split_key_id", "@content_kem", "@transit_pair"]
    fams = ["trust:{job}:{version}", "consent:community_trust", "trace:{form}:{version}", "transport:{kind}",
            "accord:invoke:constitutional:{halt_id}", "ownership:{relation}:{target_kind}:{version}"]
    missing = [n for n in need if n not in uses] + [f for f in fams if not any(u["family"] == f for u in d["uses"])]
    if missing:
        sys.exit("key_roles model: the manifest lacks uses it needs: " + ", ".join(missing))
    return d, uses


# ---------------------------------------------------------------- the home
# A state is a frozen dict-like tuple. Fields:
#   cfg       two_key | holder | fused | one_key
#   split     None | keep_actor | keep_node      (fused only; which key keeps the configured key_id)
#   bind      frozenset of (owner, target, cosigned)
#   seed      the person's roster seed is held on this device
#   a_end     the agent key's record end (seconds) or None
#   a_rev     None | self | owner | node          (who revoked the agent key)
#   a_rot     None | single | rival
#   room      the home's agent and person joined a private room
#   occ871    a machine key was offered as an occurrence of the person's identity
FIELDS = ["cfg", "split", "bind", "seed", "a_end", "a_rev", "a_rot", "room", "occ871"]


def mk(**kw):
    return tuple(kw[f] for f in FIELDS)


def get(s, f):
    return s[FIELDS.index(f)]


def put(s, **kw):
    l = list(s)
    for k, v in kw.items():
        l[FIELDS.index(k)] = v
    return tuple(l)


def start_states():
    out = []
    for cfg in ("two_key", "holder", "fused", "one_key"):
        out.append(mk(cfg=cfg, split=None, bind=frozenset(), seed=True, a_end=YEAR, a_rev=None, a_rot=None, room=False, occ871=False))
    return out


def keys(s):
    """The keys that exist, by structural kind (what the key is, not what its record says)."""
    cfg, split = get(s, "cfg"), get(s, "split")
    k = {"P": "person"}
    if cfg == "holder":
        k["H"] = "holder"
    if cfg in ("two_key", "holder"):
        k.update(N="node", A="agent")
    elif cfg == "one_key":
        k["N"] = "node"
    elif cfg == "fused":
        k["C"] = "agent"          # the configured key turns out to be the actor's
        if split == "keep_actor":
            k["N"] = "node"       # a fresh node key is minted
        elif split == "keep_node":
            k["N"] = "node"       # the configured key_id is kept for the node: a fresh node key under the old id
            k["A"] = "agent"      # and the actor is re-minted
            del k["C"]
    return k


def agent_key(s):
    k = keys(s)
    return "A" if "A" in k else ("C" if "C" in k else None)


def acts(s):
    """The structural acts from state s, as (name, next_state)."""
    k = keys(s)
    out = []
    b = get(s, "bind")
    for t in ("N", "A", "C"):
        if t in k:
            for cos in (True, False):
                if ("P", t, cos) not in b:
                    out.append((f"bind P->{t} cos={cos}", put(s, bind=b | {("P", t, cos)})))
            if ("Q", t, True) not in b:
                out.append((f"bind Q->{t}", put(s, bind=b | {("Q", t, True)})))
    if get(s, "cfg") == "fused" and get(s, "split") is None:
        for v in ("keep_actor", "keep_node"):
            out.append((f"split {v}", put(s, split=v)))
    if agent_key(s):
        out.append(("renew agent", put(s, a_end=YEAR)))
        if get(s, "a_rev") is None:
            for by in ("self", "owner", "node"):
                out.append((f"revoke agent by {by}", put(s, a_rev=by)))
        if get(s, "a_rot") is None:
            for r in ("single", "rival"):
                out.append((f"rotate agent {r}", put(s, a_rot=r)))
    if get(s, "seed"):
        out.append(("lose seed", put(s, seed=False)))
    if not get(s, "room"):
        out.append(("join private room", put(s, room=True)))
    if not get(s, "occ871") and agent_key(s):
        out.append(("offer agent as person's occurrence", put(s, occ871=True)))
    return out


def counted(s, target):
    """Owners whose binding on target counts: cosigned by the owned key (CC 3.2 P3:994)."""
    return {o for (o, t, cos) in get(s, "bind") if t == target and cos}


def true_owner(s, target):
    o = counted(s, target)
    return next(iter(o)) if len(o) == 1 else None


# ---------------------------------------------------------------- implementations
class Correct:
    """Every choice made from the text."""
    name = "correct"

    def __init__(self, d, uses):
        self.d, self.uses = d, uses

    # which key a party signs a use with; None is a refusal
    def key_for_party(self, s, party):
        k = keys(s)
        if party == "person":
            return "P" if get(s, "seed") else None           # no seed: refuse, never a machine key (P3:1963)
        if party == "holder":
            return "H" if "H" in k else None
        if party == "agent":
            a = agent_key(s)
            if a is None or get(s, "a_rev") == "self" or get(s, "a_rev") == "owner":
                return None
            return a
        if party == "node":
            return self.node_key(s)
        return None

    def node_key(self, s):
        k = keys(s)
        return "N" if "N" in k else None                    # the node is the key minted as the node, never a label

    def signer(self, s, use, party):
        if party_kind(party) not in use["kinds"]:
            return None
        key = self.key_for_party(s, party)
        if key is None:
            return None
        kind = keys(s)[key]
        if kind in ("node", "agent") and use["use"] != "@device_join" and true_owner(s, key) is None:
            return None                                       # unowned machine key: device-join only (P3:996, P3:1033)
        if use["use"] == "@device_join" and true_owner(s, key) is not None:
            return None
        return key

    def record_types(self, s, key):
        kind = keys(s)[key]
        return {"person": {"user"}, "holder": {"accord_holder"}, "node": {"node"}, "agent": {"agent"}}[kind]

    def record_end(self, s, key):
        kind = keys(s)[key]
        if kind in PERSON:
            return None
        return get(s, "a_end") if kind == "agent" else YEAR

    def owner_of(self, s, target):
        return true_owner(s, target)

    def may_act_through(self, s, a, n):
        oa, on = self.owner_of(s, a), self.owner_of(s, n)
        return on is not None and on == oa                   # Clause D: one human at both corners

    def binding_counts(self, s, owner, target, cos):
        return cos

    def accepts_occurrence_under_person(self, s, key):
        return keys(s)[key] in PERSON                         # P3:1821: never a machine key under a person's identity

    def kem_key(self, s):
        return "K"

    def transit_key(self, s):
        return "T"

    def room_signer(self, s, party):
        return "R:" + party                                   # one room key per device per room (P3:281)

    def revoke_ok(self, s, by, target):
        return by in ("self", "owner", "roster")             # P2:380

    def rotation_hands(self, s):
        held = {"owner_binding"} if true_owner(s, agent_key(s) or "") else set()
        return held if get(s, "a_rot") == "single" else set()

    def mls_store_key(self, s, party):
        return "R:" + party if get(s, "room") else self.key_for_party(s, party)

    def node_identity(self, s):
        return self.node_key(s)


def party_kind(p):
    return p


class Plant(Correct):
    def __init__(self, d, uses, name, r, **over):
        super().__init__(d, uses)
        self.name, self.r = name, r
        for k, v in over.items():
            setattr(self, k, v.__get__(self))


def plants(d, uses):
    C = Correct
    P = lambda name, r, **o: Plant(d, uses, name, r, **o)

    def engine(self, s):                                     # the configured engine key: the agent on a split home
        return agent_key(s) or "N"

    def edge_default(self, s, use, party):
        k = C.signer(self, s, use, party)
        if k is not None and use["kinds"] == ["node"] and agent_key(s):
            return engine(self, s)
        return k

    def crossing_engine(self, s, use, party):
        if use["use"] == "@crossing":
            return agent_key(s) or C.signer(self, s, use, party)
        return C.signer(self, s, use, party)

    def agent_root(self, s, use, party):
        if use["family"] == "trust:{job}:{version}" and agent_key(s):
            return agent_key(s)
        return C.signer(self, s, use, party)

    def machine_consent(self, s, use, party):
        k = C.signer(self, s, use, party)
        if k is None and party == "person" and not get(s, "seed") and (use["family"] or "").startswith("consent:"):
            return agent_key(s) or "N"
        return k

    def node_trace(self, s, use, party):
        if use["family"] == "trace:{form}:{version}" and party == "agent" and "N" in keys(s):
            return "N"
        return C.signer(self, s, use, party)

    def first_owner(self, s, t):
        o = sorted(counted(s, t))
        return o[0] if o else None

    def edge_admit(self, s, a, n):                           # "the attendee is the node or its owner"
        return a in (n, self.owner_of(s, n))

    def label_node(self, s):                                 # register_self_key: the configured key is the node
        k = keys(s)
        if "C" in k:
            return "C"
        return "N" if "N" in k else None

    def label_signer(self, s, use, party):
        if party == "node" and "C" in keys(s) and get(s, "split") is None:
            return "C" if party_kind(party) in use["kinds"] else None
        return C.signer(self, s, use, party)

    def unowned_node(self, s, use, party):
        if party == "node" and "N" in keys(s) and "node" in use["kinds"]:
            return "N"
        return C.signer(self, s, use, party)

    def fused_types(self, s, key):
        if get(s, "cfg") == "fused" and key == "C":
            return {"node", "agent"}
        return C.record_types(self, s, key)

    def fused_signer(self, s, use, party):
        if get(s, "cfg") == "fused" and party == "node" and "node" in use["kinds"] and "C" in keys(s):
            return "C"
        return C.signer(self, s, use, party)

    return [
        P("fused configured key keeps both roles", "R1", record_types=fused_types, signer=fused_signer),
        P("edge defaults its signer to the agent", "R2", signer=edge_default),
        P("the mesh crossing is co-scrubbed by the engine (agent)", "R2", signer=crossing_engine),
        P("the agent signs the trust-root acceptance", "R3", signer=agent_root),
        P("a machine key authors consent when no seed is held", "R3", signer=machine_consent),
        P("the node signs the agent's trace", "R4", signer=node_trace),
        P("owner_of picks the first binding", "R5", owner_of=first_owner),
        P("edge admits only the node or its owner", "R6", may_act_through=edge_admit),
        P("an uncosigned binding counts", "R7", binding_counts=lambda self, s, o, t, cos: True),
        P("the agent is the owner's occurrence (#871 as worded)", "R8", accepts_occurrence_under_person=lambda self, s, k: True),
        P("the transit pair is the node's signing key", "R9", transit_key=lambda self, s: "N"),
        P("a private-room row is signed by the identity key", "R10", room_signer=lambda self, s, p: C.key_for_party(self, s, p)),
        P("the agent's record states no end", "R11", record_end=lambda self, s, k: None),
        P("the node revokes the agent key", "R12", revoke_ok=lambda self, s, by, t: True),
        P("register_self_key: the configured key is the node by its label", "R13", node_key=label_node, signer=label_signer),
        P("an unowned node signs node rows", "R14", signer=unowned_node),
        P("rival rotations hand on the old standing", "R15", rotation_hands=lambda self, s: {"owner_binding"} if get(s, "a_rot") else set()),
        P("the MLS store is keyed by the node", "R16", mls_store_key=lambda self, s, p: self.node_key(s) or "C"),
        P("the federation surface answers the agent as the node", "R17", node_identity=lambda self, s: agent_key(s) or self.node_key(s)),
    ]


# ---------------------------------------------------------------- the properties
R_TEXT = {
    "R1": "no key record holds node with agent/user, or user/accord_holder with node/agent; no key signs both node rows and actor rows",
    "R2": "a node-only use is signed by the node key; the node key signs nothing whose cell does not name node",
    "R3": "a person's act is signed by that person's own key (the holder's by the holder key); a machine key never signs for a person",
    "R4": "an agent-only use is signed by the agent key; the agent key signs nothing whose cell does not name agent",
    "R5": "owner_of returns the one counted owner, and nothing for any other count",
    "R6": "an agent acts through a node iff owner_of(node) is the agent's owner (Clause D), never by a node-or-owner rule",
    "R7": "an owner-binding counts only when the owned key cosigned it",
    "R8": "no machine key is admitted as an occurrence of a person's identity",
    "R9": "the content-KEM key, the transit pair and every signing key are distinct",
    "R10": "in a private room every row is signed by a room key, never an identity key",
    "R11": "a node or agent record states an end of at most 365 days; a person's states none",
    "R12": "only the key itself, its owner or its roster revokes a key",
    "R13": "which key is the node is decided by what was minted as the node, never by a configured label",
    "R14": "a node or agent key with no counted owner-binding signs nothing but a device-join request",
    "R15": "a rotation hands on no more than the old key held, and rival rotations hand on nothing",
    "R16": "MLS group state is keyed by the room member's key (the room key in a private room, the member's own key otherwise)",
    "R17": "the node is named by its node key: its public identity, transport binding and serve seat",
}
OPEN_R = {"R16": "@mls_leaf"}   # an R whose rule is an open cell


SPECIAL_FAMILIES = {"trace:{form}:{version}", "trust:{job}:{version}"}


def classes(d):
    """Uses an implementation cannot tell apart: the same kinds, and not one of the uses or families any choice
    names by itself. One representative stands for each class; every use is in exactly one."""
    out = {}
    for u in d["uses"]:
        if u["open"] or not u["kinds"]:
            continue
        if not any(x in u["kinds"] for x in ("person", "holder", "agent", "node")):
            continue   # room, ephemeral, kem, unsigned and the reserved machine roles: R9, R10 and the generator hold them
        fam = u["family"] or ""
        key = (tuple(u["kinds"]), u["use"] if u["use"].startswith("@") else None,
               fam if fam in SPECIAL_FAMILIES else None, fam.startswith("consent:"))
        out.setdefault(key, u)
    return list(out.values())


def check_state(impl, s, d, uses, reps=None):
    """The failures of impl in state s, as (R, message)."""
    f = []
    k = keys(s)
    parties = ["person", "agent", "node"] + (["holder"] if "H" in k else [])
    signed_by = {}
    for u in (reps if reps is not None else classes(d)):
        for p in parties:
            key = impl.signer(s, u, p)
            if key is None:
                continue
            kind = k.get(key)
            signed_by.setdefault(key, set()).add(u["use"])
            if kind == "node" and "node" not in u["kinds"]:
                f.append(("R2", f"{u['use']}: the node key signs a use whose cell is {u['kinds']}"))
            if u["kinds"] == ["node"] and kind != "node":
                f.append(("R2", f"{u['use']}: a node-only use signed by the {kind} key"))
                if key == "C" and get(s, "split") is None:
                    f.append(("R13", f"{u['use']}: the configured key signs as the node before the split"))
            if p in PERSON and kind not in PERSON:
                f.append(("R3", f"{u['use']}: signed for the {p} by the {kind} key"))
            if set(u["kinds"]) <= PERSON and kind not in PERSON:
                f.append(("R3", f"{u['use']}: a person's use signed by the {kind} key"))
            if "holder" in u["kinds"] and set(u["kinds"]) == {"holder"} and kind != "holder":
                f.append(("R3", f"{u['use']}: a holder's use signed by the {kind} key"))
            if u["kinds"] == ["agent"] and kind != "agent":
                f.append(("R4", f"{u['use']}: an agent-only use signed by the {kind} key"))
            if kind == "agent" and "agent" not in u["kinds"]:
                f.append(("R4", f"{u['use']}: the agent key signs a use whose cell is {u['kinds']}"))
            if kind in ("node", "agent") and true_owner(s, key) is None and u["use"] != "@device_join":
                f.append(("R14", f"{u['use']}: signed by an unowned {kind} key"))
    # R1: records, and a key signing in both columns
    for key in k:
        t = impl.record_types(s, key)
        for a, b in FORBIDDEN:
            if t & a and t & b:
                f.append(("R1", f"{key}: record holds {sorted(t)}"))
        used = signed_by.get(key, set())
        node_only = {u for u in used if uses[u]["kinds"] == ["node"]}
        actor_only = {u for u in used if "node" not in uses[u]["kinds"]}
        if node_only and actor_only:
            f.append(("R1", f"{key}: signs node rows ({min(node_only)}) and actor rows ({min(actor_only)})"))
    # R5
    for t in ("N", "A", "C"):
        if t in k and impl.owner_of(s, t) != true_owner(s, t):
            f.append(("R5", f"owner_of({t}) = {impl.owner_of(s, t)}, counted owners {sorted(counted(s, t))}"))
    # R6
    a, n = agent_key(s), impl.node_key(s)
    if a and "N" in k:
        want = true_owner(s, "N") is not None and true_owner(s, "N") == true_owner(s, a)
        if impl.may_act_through(s, a, "N") != want:
            f.append(("R6", f"may_act_through({a}, N) = {not want}, Clause D gives {want}"))
    # R7
    for (o, t, cos) in get(s, "bind"):
        if not cos and impl.binding_counts(s, o, t, cos):
            f.append(("R7", f"an uncosigned binding {o}->{t} counts"))
    # R8
    if get(s, "occ871"):
        for key in k:
            if k[key] in ("node", "agent") and impl.accepts_occurrence_under_person(s, key):
                f.append(("R8", f"{key} ({k[key]}) admitted as an occurrence of the person's identity"))
    # R9
    sig = set(k)
    km, tp = impl.kem_key(s), impl.transit_key(s)
    if km == tp or km in sig or tp in sig:
        f.append(("R9", f"content-KEM {km}, transit {tp}, signing {sorted(sig)} not distinct"))
    # R10
    if get(s, "room"):
        for p in parties:
            rk = impl.room_signer(s, p)
            if rk in k:
                f.append(("R10", f"a private-room row for the {p} signed by the identity key {rk}"))
    # R11
    for key in k:
        end = impl.record_end(s, key)
        if k[key] in PERSON and end is not None:
            f.append(("R11", f"{key}: a person's record states an end"))
        if k[key] in ("node", "agent") and (end is None or end > YEAR):
            f.append(("R11", f"{key}: a {k[key]} record states end {end}"))
    # R12
    if get(s, "a_rev") == "node" and impl.revoke_ok(s, "node", a):
        f.append(("R12", "the node revoked the agent key"))
    # R13
    if impl.node_key(s) != ("N" if "N" in k else None):
        f.append(("R13", f"the implementation takes {impl.node_key(s)} as the node, the home's node key is {'N' if 'N' in k else None}"))
    # R15
    if get(s, "a_rot"):
        held = {"owner_binding"} if true_owner(s, a or "") else set()
        h = impl.rotation_hands(s)
        if get(s, "a_rot") == "rival" and h:
            f.append(("R15", f"rival rotations hand on {sorted(h)}"))
        if not h <= held:
            f.append(("R15", f"a rotation hands on {sorted(h)}, the old key held {sorted(held)}"))
    # R16 (open cell): inferred rule
    for p in ("person", "agent"):
        want = ("R:" + p) if get(s, "room") else Correct.key_for_party(impl, s, p)
        if impl.mls_store_key(s, p) != want:
            f.append(("R16", f"MLS store for the {p} keyed by {impl.mls_store_key(s, p)}, the member's key is {want}"))
    # R17
    if impl.node_identity(s) != ("N" if "N" in k else None):
        f.append(("R17", f"the node's identity is answered as {impl.node_identity(s)}"))
    return f


def explore(impl, d, uses):
    seen, frontier, fails, n_seq = set(), [(s, ()) for s in start_states()], {}, 0
    reps = classes(d)
    depth = 0
    while frontier and depth <= BOUND:
        nxt = []
        for s, path in frontier:
            if s in seen:
                continue
            seen.add(s)
            for r, msg in check_state(impl, s, d, uses, reps):
                fails.setdefault(r, (msg, path))
            if depth < BOUND:
                for name, t in acts(s):
                    n_seq += 1
                    nxt.append((t, path + (name,)))
        frontier, depth = nxt, depth + 1
    return fails, len(seen), n_seq


def main():
    d, uses = load()
    fails, nstates, nseq = explore(Correct(d, uses), d, uses)
    results = {}
    for r in R_TEXT:
        if r in OPEN_R and any(u["use"] == OPEN_R[r] and u["open"] for u in d["uses"]):
            results[r] = "OPEN"
        else:
            results[r] = "FAIL" if r in fails else "PASS"
    n_open_uses = d["_meta"]["counts"]["open_uses"]
    print(f"key roles model: {nstates} states reached by {nseq} acts up to depth {BOUND}, from 4 homes; "
          f"{len(d['uses'])} uses ({n_open_uses} open, reported not passed) tried by every party in every state")
    for r, t in R_TEXT.items():
        extra = ""
        if results[r] == "FAIL":
            extra = f"  <- {fails[r][0]} after {list(fails[r][1])}"
        if results[r] == "OPEN":
            extra = f"  (rule is the open cell {OPEN_R[r]}; the inferred rule {'fails' if r in fails else 'holds'} under the correct choices)"
        print(f"  {r} {results[r]:4} {t}{extra}")
    errs = [r for r, v in results.items() if v == "FAIL"]
    caught = 0
    pl = plants(d, uses)
    for p in pl:
        pf, _, _ = explore(p, d, uses)
        ok = p.r in pf
        caught += ok
        print(f"  plant {'caught' if ok else 'MISSED'} by {p.r}: {p.name}" + ("" if ok else f" (fails {sorted(pf)})"))
        if not ok:
            errs.append("plant missed: " + p.name)
    print(f"key roles model: {sum(v == 'PASS' for v in results.values())} pass, {sum(v == 'OPEN' for v in results.values())} open, "
          f"{sum(v == 'FAIL' for v in results.values())} fail; plants caught {caught} of {len(pl)}")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
