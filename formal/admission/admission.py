"""
admission.py: one admission for what an agent is, what a node runs and what an agent does (CC 2.7.11).

Each answer is a function of the rows a host holds, the host's key and the host's clock, written with the shared
library (formal/kernel_lib). Nothing here knows an order of arrival: the rows are a set.

Rows (each a dict with `id`, `kind` and `t`, the instant the host first held it):
  key        {who, type}                       an identity and its group: "person" or "program" (CC 2.6.1.7)
  owns       {host, owner}                     a node's owner-binding: signed by the owner, cosigned by the node (CC 3.2)
  edge       {by, to, classes}                 an acceptance edge, trust:accepts (CC 4.4.3.34)
  roster     {group, members, need}            a group's roster head and its declared count
  build      {units, blessed}                  an attested build: its manifest's units, and whether its pipeline's
                                               counted trust:blessing is held (CC 3.1.2.1)
  unit       {unit, caps, at, until, scope, author | head}   the admission:unit row (CC 3.1.3): authored or counted;
                                               scope is its cohort_scope (CC 2.1)
  stmt       {of, by}                          one voice's statement over a row's payload (CC 2.6.1.9)
  withdraw   {of, author | head}               a withdraws of an admission row (CC 2.4.1.1)
  bundle     {holders}                         the accord's bundle in force
  halt       {by}                              one holder's halt (CC 4.2.1.1)
  life       {of, what}                        a counted confirmation or resumption of a halt (CC 4.2.1.3)
  bind       {agent, steward}                  an agent's owner-binding
  seat       {agent, wa, by}                   a seat over the agent's deferrals (CC 4.3)
  resp       {agent, outcome, by, digest?, fp?}  a deferral:response: `digest` its amendment_digest, `fp` its call_fingerprint
  template   {agent, digest, attested}         the shipped template, checked by its signature or the attested build
  amend      {agent, digest, prev, by_resp}    an identity_amendment (CC 3.1.5); prev names the link before
  review     {thought, fp, outcome, faculties, discharges, considered, derived_from}  the review record (CC 2.7.11)
  data       {trust, label, names}             a row an action's arguments derive from, its own trust and its kind
  ack        {of, by}                          an acknowledgement of an effect by a voice that could stop it

  PLANTS is the set of planted breaks; check_admission.py turns each on and requires a result to change.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kernel_lib"))
from kernel_lib import closure, fix, group, in_range, sel  # noqa: E402

DEPTH = 5                       # the walk's cap of five hops (CC 4.1.1)
LEASE_MAX = 24                  # unit_lease_max_secs, in the model's hours (86400 s)
FUSE = 24                       # halt_fuse_secs, in the model's hours (86400 s)
COUNT_FLOOR = 2                 # one voice is not a count (CC 2.7.5)
CAPS = frozenset({"compute", "read", "net_send", "submit", "sign", "store_write", "actuate"})
EFFECTS = frozenset({"net_send", "submit", "sign", "store_write", "actuate"})
FACULTIES = frozenset({"entropy", "coherence", "optimization_veto", "epistemic_humility"})
UNTRUSTED, VERIFIED, SYSTEM = 0, 1, 2
PLANTS = set()


def held(R, now):
    """The rows the host holds at `now`."""
    return [r for r in R if r["t"] <= now]


def H(*parts):
    return hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:16]


def kind_of(R, who):
    return next((k["type"] for k in sel(R, kind="key", who=who)), None)


def person(R, who):
    return kind_of(R, who) == "person"


def owner_of(R, host):
    """The host's owner: the person its owner-binding names (signed by the owner, cosigned by the node, CC 3.2)."""
    return next((o["owner"] for o in sel(R, kind="owns", host=host) if person(R, o["owner"])), None)


# ---- standing: the host owner's own walk -----------------------------------------------------------------
def reach(R, owner):
    """Keys and groups the owner's own acceptance edges reach for the class `admission`, through persons only,
    capped at DEPTH hops. There is no list of issuers anywhere else (CC 2.7.1, CC 4.4.3.34)."""
    hop_ok = lambda by: person(R, by) or "program_relay" in PLANTS
    cls_ok = lambda e: "admission" in e["classes"] or "any_class" in PLANTS
    step = lambda acc: acc | frozenset(e["to"] for e in sel(R, kind="edge")
                                       if e["by"] in acc and hop_ok(e["by"]) and cls_ok(e))
    return fix(step, frozenset({owner}) if owner else frozenset(), DEPTH)


def voices(R, rid, members=None):
    """The persons whose statements over row `rid` count, among `members` where given. A program's
    statement is refused alone (CC 2.7.11)."""
    vs = {s["by"] for s in sel(R, kind="stmt", of=rid)}
    vs = {v for v in vs if person(R, v) or "program_voice" in PLANTS}
    if members is not None and "voices_outside_head" not in PLANTS: vs &= members
    return vs


def count(R, row):
    """'met', 'unmet' or 'waiting' (the head is not held) for a counted row (CC 2.6.1.9, CC 2.7.5)."""
    heads = sel(R, kind="roster", id=row["head"])
    if not heads: return "waiting"
    head = heads[0]
    need = head["need"] if "count_floor_one" in PLANTS else max(COUNT_FLOOR, head["need"])
    return "met" if len(voices(R, row["id"], head["members"])) >= need else "unmet"


# ---- the code scope ----------------------------------------------------------------------------------------
def static(row):
    """The family's static checks (CC 2.6.1.8 step 5): Invalid with a token, or None."""
    if ("author" in row) == ("head" in row): return "admission_unit_malformed"
    if not row["caps"] or not row["caps"] <= CAPS: return "admission_capability_unknown"
    if not row["at"] < row["until"]: return "admission_lease_out_of_window"
    if row["until"] - row["at"] > LEASE_MAX and "lease_unbounded" not in PLANTS: return "admission_lease_out_of_window"
    if ("author" in row and row["caps"] & EFFECTS and row.get("scope") != "self"
            and "owner_row_any_scope" not in PLANTS): return "admission_owner_row_not_self"
    return None


def withdrawn(R, row):
    """A withdraws of the row: by its author where it is authored; counted by the same group where it is
    counted, since a quorum's act is undone only by a quorum (CC 2.4.1.1 rule 0)."""
    if "withdraw_ignored" in PLANTS: return False
    for w in sel(R, kind="withdraw", of=row["id"]):
        if "author" in row:
            if "stranger_withdraws" in PLANTS or row["author"] in voices(R, w["id"]): return True
        elif w.get("head") == row["head"] and count(R, w) == "met":
            return True
    return False


def one(R, owner, digest, now, row):
    """(answer, token) for one admission row at a host owned by `owner`: 'admit', 'refuse' or 'waiting'."""
    bad = static(row)
    if bad: return "refuse", bad
    reached = reach(R, owner)
    if "author" in row:
        if row["author"] not in voices(R, row["id"]) and not ("program_issuer" in PLANTS and
                                                              sel(R, kind="stmt", of=row["id"], by=row["author"])):
            return "refuse", "admission_issuer_not_person" if sel(R, kind="stmt", of=row["id"]) else "admission_none"
        if row["author"] not in reached and "any_signature" not in PLANTS: return "refuse", "admission_issuer_not_reached"
        # one person admits an effect only on a host that person owns (the owner's ruling)
        if (row["caps"] & EFFECTS and row["author"] != owner
                and "effect_on_one" not in PLANTS and "owner_alone_anywhere" not in PLANTS):
            return "refuse", "admission_issuer_not_reached"
    else:
        heads = sel(R, kind="roster", id=row["head"])
        if not heads: return "waiting", "head"
        if heads[0]["group"] not in reached and "any_signature" not in PLANTS:
            return "refuse", "admission_issuer_not_reached"
        if count(R, row) != "met": return "waiting", "admission_count_unmet"
    first_bound = row["t"] + LEASE_MAX
    if "no_lease" not in PLANTS:
        if not in_range(now, row["at"], row["until"]): return "refuse", "admission_lease_ended"
        if "lease_from_signed" not in PLANTS and not now < first_bound: return "refuse", "admission_lease_ended"
    if withdrawn(R, row): return "refuse", "admission_withdrawn"
    return "admit", None


def built_in(R, digest):
    """A unit of the attested build runs under the build's own attestation: its manifest names the digest and the
    pipeline's counted blessing is held (CC 3.1.2.1). It is outside admission:unit."""
    for b in sel(R, kind="build"):
        if (b["blessed"] or "unblessed_build" in PLANTS) and (digest in b["units"] or "build_any_digest" in PLANTS):
            return True
    return False


def admit(R, host, digest, now):
    """('admit', caps) | ('waiting', what) | ('refuse', token) at `host`. A unit of the attested build is admitted by
    the build. Otherwise its capabilities are the union over the live admitting rows: each names what it admits,
    and renewal is a later row for the same digest."""
    R = held(R, now)
    owner = owner_of(R, host)
    if built_in(R, digest): return "admit", CAPS
    rows = sel(R, kind="unit") if "no_digest_bind" in PLANTS else sel(R, kind="unit", unit=digest)
    if "first_statement_only" in PLANTS: rows = rows[:1]
    if not rows:
        return ("admit", frozenset({"compute"})) if "run_unadmitted" in PLANTS else ("refuse", "admission_none")
    got = [(row, one(R, owner, digest, now, row)) for row in rows]
    caps = frozenset().union(*[row["caps"] for row, (a, _) in got if a == "admit"])
    if caps: return "admit", caps
    waits = sorted(t for _, (a, t) in got if a == "waiting")
    if waits: return "waiting", waits[0]
    return "refuse", sorted(t for _, (a, t) in got)[0]


def halted(R, host, now):
    """The accord's halt read at a host (CC 4.2.1, CC 4.2.1.1): one holder's row latches from the host's receipt
    where the host's owner held an edge to the accord at that instant; alone it lapses FUSE after receipt; a strict
    majority confirms it before then; a strict majority resumes it at any time."""
    if "no_halt" in PLANTS: return False
    R = held(R, now)
    owner = owner_of(R, host)
    holders = frozenset().union(*[b["holders"] for b in sel(R, kind="bundle")])
    majority = lambda vs: 2 * len(vs) > len(holders) or ("lone_resume" in PLANTS and len(vs) >= 1)
    for h in sel(R, kind="halt"):
        if h["by"] not in holders and "stranger_halt" not in PLANTS: continue
        if not sel(R, h["t"] + 1, kind="edge", by=owner, to="accord"): continue
        life = lambda what: [l for l in sel(R, kind="life", of=h["id"], what=what)]
        if any(majority(voices(R, l["id"], holders)) for l in life("resume")): continue
        confirmed = any(majority({s["by"] for s in sel(R, h["t"] + FUSE, kind="stmt", of=l["id"])} & holders)
                        for l in life("confirm"))
        if "no_fuse" in PLANTS or now < h["t"] + FUSE or confirmed: return True
    return False


def may(R, host, digest, cap, now, parent=None):
    """The host's gate before a unit does `cap`: (True, None) or (False, token). A unit started by another
    unit holds no capability its parent lacks; a unit submitted from another host is admitted here under this
    host's owner, never the sender's (CC 2.7.11)."""
    a, x = admit(R, host, digest, now)
    if a != "admit": return False, x if a == "refuse" else "admission_waiting"
    caps = x
    if parent is not None and "no_attenuation" not in PLANTS:
        if cap not in parent: return False, "admission_capability_not_held"
    if cap not in caps: return False, "admission_capability_not_admitted"
    if (cap in EFFECTS or "halt_stops_compute" in PLANTS) and halted(R, host, now):
        return False, "admission_halted"
    return True, None


def submit(R, sender, receiver, digest, now):
    """Whether the receiving host runs a unit another host submitted: by its own owner's admission alone."""
    host = sender if "sender_standing_carries" in PLANTS else receiver
    return admit(R, host, digest, now)[0] == "admit"


# ---- the profile scope -------------------------------------------------------------------------------------
def steward(R, agent):
    return next((b["steward"] for b in sel(R, kind="bind", agent=agent)), None)


def authorized(R, a):
    """An identity_amendment counts when its response is held, approved, about this agent, and signed by the
    agent's steward (the seat's conferrer) or the person it seated unscoped; never by a program (CC 3.1.5, 4.3)."""
    if "amend_unauthorized" in PLANTS: return True
    for r in sel(R, kind="resp", id=a["by_resp"]):
        seated = {s["wa"] for s in sel(R, kind="seat", agent=a["agent"], by=steward(R, a["agent"]))}
        if (r["outcome"] == "approved" and r["agent"] == a["agent"] and person(R, r["by"])
                and (r.get("digest") == a["digest"] or "digest_unbound" in PLANTS)
                and r["by"] in seated | {steward(R, a["agent"])}):
            return True
    return False


def template(R, agent):
    """The digest of the agent's shipped template, where its manifest is checked by its signature or the build."""
    return next((t["digest"] for t in sel(R, kind="template", agent=agent) if t["attested"]), None)


def chain(R, agent):
    """The amendments in the order their rows name. The base link names no predecessor and approves the attested
    template's exact digest; an amendment naming no predecessor that is not the template is no base and counts for
    nothing. Two links naming one predecessor are concurrent rows of one kind on one slot: neither counts, and the
    chain stops before them (CC 2.7.7 rule 2). A link whose predecessor is not held waits."""
    links = [a for a in sel(R, kind="amend", agent=agent) if authorized(R, a)]
    base_ok = lambda a: a["digest"] == template(R, agent) or "orphan_counts" in PLANTS
    out, cur = [], None
    while True:
        cands = [a for a in links if a.get("prev") == cur and (cur is not None or base_ok(a))]
        if "fork_picks_one" in PLANTS and cands: cands = cands[:1]
        if len(cands) != 1: return out
        out.append(cands[0]["digest"])
        cur = cands[0]["id"]


def expected_profile(R, agent):
    """SHA-256 over ["CEG-profile/2", d0, d1, ..., dn], the base link first (CC 3.1.5)."""
    ds = chain(R, agent)
    if "order_free" in PLANTS: ds = sorted(ds)
    return H("CEG-profile/2", *ds) if ds else None


def load(R, agent, loaded, now=10**6):
    """(loads, status). With a base link, the agent loads only the profile whose digest the chain derives. With none,
    it loads its attested template alone, counts no amendment, and reports `profile_unanchored` (fail-safe)."""
    R = held(R, now)
    if "no_profile_check" in PLANTS: return True, None
    exp = expected_profile(R, agent)
    if exp is None:
        tpl = template(R, agent)
        ok = tpl is not None and (loaded == [tpl] or ("unanchored_amends" in PLANTS and loaded[:1] == [tpl]))
        return ok, "profile_unanchored"
    return H("CEG-profile/2", *loaded) == exp, None if H("CEG-profile/2", *loaded) == exp else "profile_digest_mismatch"


def may_load(R, agent, loaded, now=10**6):
    return load(R, agent, loaded, now)[0]


# ---- the action scope --------------------------------------------------------------------------------------
def fingerprint(call):
    """SHA-256 over ["CEG-call/2", verb, tool, arguments, channel] (CC 2.7.11); a secret stands as its reference."""
    return H("CEG-call/2", call["verb"], call["tool"], call["args"], call["channel"])


def trusted_evidence(R, rid, agent=None):
    """A row that may discharge an objection: an approving response by a person seated over the agent. Where the
    acting agent is given, the response must be about THAT agent: an approval for one agent's call is none for
    another's, though the fingerprints match."""
    for r in sel(R, kind="resp", id=rid):
        if agent is not None and r["agent"] != agent and "approval_any_agent" not in PLANTS: continue
        seated = {s["wa"] for s in sel(R, kind="seat", agent=r["agent"])} | {steward(R, r["agent"])}
        if r["outcome"] == "approved" and person(R, r["by"]) and r["by"] in seated: return True
    return False


def may_dispatch(R, thought, call, reviewed_fp=None):
    """(True, None) or (False, token). Dispatch recomputes the fingerprint of what it will execute and runs it only
    when a pass record of this thought names that fingerprint with all four faculties. An objection binds the
    fingerprint it was raised against: one against this fingerprint is named with the trusted row that discharges
    it; one against another fingerprint of the thought is carried into the record as considered. An approved call
    runs only as approved."""
    if "exec_unreviewed" in PLANTS: return True, None
    fp = reviewed_fp if ("fp_from_review" in PLANTS and reviewed_fp) else fingerprint(call)
    passes = sel(R, kind="review", thought=thought, outcome="passed", fp=fp)
    if not passes: return False, "action_not_reviewed"
    need = FACULTIES if "three_of_four" not in PLANTS else frozenset(list(sorted(FACULTIES))[:3])
    passes = [p for p in passes if p["faculties"] >= need]
    if not passes: return False, "action_review_incomplete"
    objections = sel(R, kind="review", thought=thought, outcome="objected")
    same = [o for o in objections if o["fp"] == fp or "objection_binds_thought" in PLANTS]
    other = [o for o in objections if o not in same]

    def discharged(p, o):
        if "same_fp_passes" in PLANTS: return True
        return any(oid == o["id"] and ("self_discharge" in PLANTS or trusted_evidence(R, ev))
                   for oid, ev in p["discharges"])
    passes = [p for p in passes if all(discharged(p, o) for o in same)]
    if not passes: return False, "action_objection_undischarged"
    passes = [p for p in passes if all(o["id"] in p["considered"] or "drop_considered" in PLANTS for o in other)]
    if not passes: return False, "action_objection_not_carried"
    if call.get("approved_by") and "approval_unbound" not in PLANTS:
        if not any(r.get("fp") == fp for r in sel(R, kind="resp", id=call["approved_by"], outcome="approved")):
            return False, "action_approval_mismatch"
    return True, None


# ---- derived trust and the effect gate ---------------------------------------------------------------------
def trust_of(R, rid):
    """The least trust over the row and every row it names: nothing declares it (CC 2.7.11)."""
    by = {r["id"]: r for r in R if r["kind"] == "data"}
    if "declared_trust" in PLANTS: return by[rid]["trust"]
    anc = closure(list(by.values()))
    return group([by[a] for a in anc[rid] | {rid} if a in by], None, "min", val="trust")


def untrusted_labels(R, rid):
    by = {r["id"]: r for r in R if r["kind"] == "data"}
    anc = closure(list(by.values()))
    return {by[a]["label"] for a in anc[rid] | {rid} if a in by and by[a]["trust"] < VERIFIED}


def delegated(R, agent, rid, duty):
    """A standing delegation that is authority for an act (CC 4.5.5 (b)): a live `delegates_to` onto this agent,
    signed by a person seated over it, whose scope names the act's duty. An act within it needs no approval of its
    own. A withdrawn delegation, one from a program's key, one onto another agent or one whose scope does not name the
    duty licenses nothing."""
    seated = {s["wa"] for s in sel(R, kind="seat", agent=agent)} | {steward(R, agent)}
    for d in sel(R, kind="deleg", id=rid):
        if d["agent"] != agent or not person(R, d["by"]) or d["by"] not in seated: continue
        if sel(R, kind="withdraw", of=d["id"]): continue
        if duty in d["scope"] or "delegation_any_scope" in PLANTS: return True
    return False


def may_effect(R, thought, fp, args, claims=None, binds_others=(), under=None, duty=None, agent="ag"):
    """The effect gate after review. The pass record over `fp` is the review holding the evidence when it declares
    in `derived_from` every untrusted kind the arguments derive from. An action that claims authority (for a person,
    or under a seat) has it in one of two ways: a standing delegation whose scope names the act (`under`, `duty`),
    which needs no approval of each act; or the approving row that names its fingerprint (`claims`), for an act no
    delegation covers. An effect that is a mesh row binding others needs the acknowledgements of every voice that
    could stop it (CC 2.7.5). Absent evidence licenses nothing."""
    p = next(iter(sel(R, kind="review", thought=thought, outcome="passed", fp=fp)), None)
    if p is None: return False, "action_not_reviewed"
    declared = p["derived_from"]
    if trust_of(R, args) < VERIFIED:
        if not untrusted_labels(R, args) <= declared and "undeclared_passes" not in PLANTS:
            return False, "effect_untrusted_unacknowledged"
    if under is not None:
        if not delegated(R, agent, under, duty): return False, "effect_untrusted_unacknowledged"
    elif claims and "absent_evidence_licenses" not in PLANTS:
        if not any(r.get("fp") == fp and trusted_evidence(R, r["id"], agent) for r in sel(R, kind="resp", id=claims)):
            return False, "effect_untrusted_unacknowledged"
    if binds_others and "binds_no_ack" not in PLANTS:
        if not set(binds_others) <= {a["by"] for a in sel(R, kind="ack", of=fp)}:
            return False, "effect_untrusted_unacknowledged"
    return True, None
