"""
model.py: THE BINDING OF A PRIVATE ROOM AND ITS CARRIAGE BEFORE THE SEAT (CC 3.1.3.2, CC 2.6.1.11, CC 4.5.4).

The rule run here
    seat row     the key record of a room key R, signed under R, carrying a commitment to (room, R, person, nonce).
    binding      three flows between M (who holds R and the binding key of person P) and ONE addressee A (a room key):
                   claim         M -> A   the person, sealed to A's room-key KEM key
                   challenge     A -> M   an encapsulation that only P's binding key opens
                   confirmation  M -> A   a seal to A's room-key KEM key, keyed by the challenge's secret, whose plaintext
                                          is the opening [person, nonce]
                 A accepts iff the opening opens R's commitment and names the person A challenged. Nobody signs any of
                 it. One exchange for each room key.
    carriage     before an admission row is signed, each cosigner, each founder and the duty holder holds the joiner's
                 binding. Every flow rides a sealed envelope addressed to one room key. A count of persons waits at a
                 node that lacks a binding.

Everything is symbolic. A term is a nested tuple, and a party knows what it can derive from what it holds (the
Dolev-Yao closure below). Nothing here is cryptography and nothing here is a proof: a verdict says what follows if
the primitives behave as their symbols do, over the bound printed by the check.

Sections
    1  terms and what a party can derive
    2  the construction, with every planted break as a switch of RULE
    3  authenticity inside                       (property 1)
    4  deniability outside                       (property 2)
    5  the carriage, as a state machine          (properties 3 and 4)
    6  a second voice                            (property 5)
    7  a count of persons waits                  (property 6)
    8  what a relay learns                       (property 7)
"""
import itertools

# =========================================================================================================
# 1. terms, and what a party can derive
# =========================================================================================================
def pk(x): return ("pk", x)                                      # the public half of secret x
def kem(p, ss): return ("kem", p, ss)                            # an encapsulation to public key p of secret ss
def spsk(p, psk, info, pt): return ("spsk", p, psk, info, pt)    # a seal to p, keyed by psk and bound to info
def seal(p, pt): return ("seal", p, pt)                          # a seal to p that anyone can make
def h(*a): return ("h",) + a                                     # a hash
def sig(sk, m): return ("sig", sk, m)                            # a signature under sk over m
def tup(*a): return ("t",) + a                                   # an encoding of several members


def analyse(K, key_private=False):
    """Everything that follows from the terms in K by taking them apart. A sealed term is opened only with the
    secret half of its key, and a keyed seal only with the key as well. Unless key_private, a sealed term shows the
    public key it was made to: no anonymity of the key exchange is assumed."""
    K = set(K)
    todo = list(K)
    while todo:
        t = todo.pop()
        new = ()
        if isinstance(t, tuple):
            c = t[0]
            if c == "t":
                new = t[1:]
            elif c == "sig":
                new = (t[2], pk(t[1]))
            elif c in ("seal", "kem", "spsk"):
                new = () if key_private else (t[1],)
                if isinstance(t[1], tuple) and t[1][0] == "pk" and t[1][1] in K:
                    if c in ("seal", "kem"): new += (t[2],)
                    elif t[2] in K: new += (t[4],)
        fresh = [n for n in new if n not in K]
        if fresh:
            K.update(fresh)
            todo = list(K)                                       # a new secret may open a term seen earlier
    return K


def can_make(K, t):
    """Can a party whose analysed knowledge is K produce exactly the term t?"""
    if t in K: return True
    if isinstance(t, tuple): return all(can_make(K, x) for x in t[1:])
    return False


def subterms(t, acc=None):
    acc = set() if acc is None else acc
    if t not in acc:
        acc.add(t)
        if isinstance(t, tuple):
            for x in t[1:]: subterms(x, acc)
    return acc


# =========================================================================================================
# 2. the construction
# =========================================================================================================
TEXT = {
    "info": ("room", "R", "A", "commit", "pkB"),   # what the confirmation's info binds, after its label
    "keyed": True,                                 # the confirmation is keyed by the challenge's secret
    "challenge_to": "binding",                     # the challenge is made to the person's binding key
    "check_person": True,                          # the opened person is the one challenged
    "check_commit": True,                          # the opening opens the seat row's commitment
    "claim_signed": False,                         # nobody signs the claim
    "commit_in_seat_row": True,                    # the commitment is inside the row R signs
    "seat_signed_by": "roomkey",                   # the seat row is signed under the room key and under nothing else
    "nonce_in_commit": True,                       # the commitment covers fresh random bytes
}


def rule(**change):
    r = dict(TEXT)
    r.update(change)
    return r


def commitment(room, key, person, nonce):
    return h("CEG-seat/2", room, key, person, nonce)


def record(key, room, commit):
    """The key record of a room key: its name, its KEM key, its room and its commitment."""
    return tup("rec", key, pk("rk:" + key), room, commit)


def seat_row(key, room, commit):
    return sig("rs:" + key, record(key, room, commit))


def info_of(r, room, R, A, commit, pkB):
    m = {"room": room, "R": R, "A": A, "commit": commit, "pkB": pkB}
    return tup("CEG-binding/2", *[m[x] for x in r["info"]])


def challenge(r, person, R, ss):
    return kem(pk("bk:" + person) if r["challenge_to"] == "binding" else pk("rk:" + R), ss)


def confirm(r, pkA, ss, info, person, nonce):
    if r["keyed"]: return spsk(pkA, ss, info, tup(person, nonce))
    return seal(pkA, tup(info, tup(person, nonce)))


def prove(r, me, a_kid, pkA, ct):
    """The honest holder of a room key and of its person's binding key answers one challenge. It keeps no state: the
    answer is a function of what it holds for good and of the challenge. me: person, R, room, nonce."""
    want = pk("bk:" + me["person"]) if r["challenge_to"] == "binding" else pk("rk:" + me["R"])
    if not (isinstance(ct, tuple) and ct[0] == "kem" and ct[1] == want): return None
    c = commitment(me["room"], me["R"], me["person"], me["nonce"])
    return confirm(r, pkA, ct[2], info_of(r, me["room"], me["R"], a_kid, c, pk("bk:" + me["person"])), me["person"], me["nonce"])


def accept(r, s, m):
    """The addressee's check of one confirmation against one of its own sessions. s: room, R, A, c (the commitment on
    the seat row it holds for R), person (the one it challenged), ss (its pending secret, None when it holds none).
    Returns the person it now takes R to be, or None."""
    if not isinstance(m, tuple): return None
    want = info_of(r, s["room"], s["R"], s["A"], s["c"], pk("bk:" + s["person"]))
    if r["keyed"]:
        if m[0] != "spsk" or m[1] != pk("rk:" + s["A"]) or s["ss"] is None or m[2] != s["ss"] or m[3] != want: return None
        pt = m[4]
    else:
        if m[0] != "seal" or m[1] != pk("rk:" + s["A"]) or not isinstance(m[2], tuple) or len(m[2]) != 3 or m[2][1] != want: return None
        pt = m[2][2]
    if not (isinstance(pt, tuple) and pt[0] == "t" and len(pt) == 3): return None
    person, nonce = pt[1], pt[2]
    if r["check_person"] and person != s["person"]: return None
    if r["check_commit"] and commitment(s["room"], s["R"], person, nonce) != s["c"]: return None
    return person


# =========================================================================================================
# 3. authenticity inside
# =========================================================================================================
# P is the honest person. It holds room key RP in room g and RP2 in room g2. A is the honest addressee, room key RA.
# The coalition is everyone else and the network, and it also holds every secret of P except the binding key and the
# roster key that publishes it: P's room keys, P's nonces, P's content key.
ROOM, ROOM2 = "g", "g2"
P_KEYS = {"RP": (ROOM, "n:RP"), "RP2": (ROOM2, "n:RP2")}
PERSONS3 = ("P", "C", "A")
NONCES = ("n:RP", "n:RP2", "n:adv")
PUBLIC = {"P", "C", "A", "Z", ROOM, ROOM2, "RP", "RP2", "RA", "RC", "RX", "RY", "RZ", "CEG-binding/2", "CEG-seat/2",
          pk("bk:P"), pk("bk:C"), pk("bk:A"), pk("rk:RA"), pk("rk:RC"), pk("rk:RP"), pk("rk:RP2")}
COALITION = {"rs:RX", "rk:RX", "rs:RY", "rk:RY", "rs:RZ", "rk:RZ", "rs:RC", "rk:RC", "bk:C", "ik:C", "n:adv", "ss:adv",
             "rs:RP", "rk:RP", "n:RP", "rs:RP2", "rk:RP2", "n:RP2", "ck:P"}


def sessions(r, restated=False):
    """The sessions the honest addressee A runs. Each is (label, session). A challenges the binding key it reads on
    a live occurrence of the person claimed."""
    def s(label, R, person, commit_person, nonce, i):
        d = {"room": ROOM, "R": R, "A": "RA", "person": person, "c": commitment(ROOM, R, commit_person, nonce), "ss": "ss:A:%d" % i}
        return label, d
    return [
        s("a coalition key committed to P with P's own nonce, claimed as P", "RX", "P", "P", "n:RP", 0),
        s("a coalition key committed to P with a coalition nonce, claimed as P", "RY", "P", "P", "n:adv", 1),
        s("P's own room key, claimed as P", "RP", "P", "P", "n:RP", 2),
        s("a coalition key committed to P, claimed as the coalition's C", "RZ", "C", "P", "n:adv", 3),
        s("P's own room key, claimed as the coalition's C", "RP", "C", "P", "n:RP", 4),
        # the coalition holds the signing secret of P's room key of the other room, and states a seat row for it here
        s("P's room key of another room, restated in this room by the coalition, claimed as P", "RP2", "P", "P", "n:RP2", 5),
    ] + ([
        # the coalition holds the signing secret of P's room key, and states a second seat row for it, committed to C
        s("P's own room key on a seat row the coalition restated to its own C, claimed as C", "RP", "C", "C", "n:adv", 6),
    ] if restated else [])


def authenticity(r, roster_key_leaked=False, restated=False):
    """Every confirmation the coalition can put before A, in every session A runs, with honest P answering every
    challenge the coalition can form, to every addressee record the coalition can state. Returns
    {goal: example}, and the number of honest acceptances (the premise is reached).
        forged     A takes a key that P never proved to be P's
        misaddressed  A takes P's own key as P's on an answer P made for another addressee
        crossroom  A takes a key P holds in another room as P's in this room, on an answer P made in that other room
        stolen     A takes P's own key to be a coalition person's
    With restated, A also runs a session on a seat row the coalition signed for P's room key (it holds that key's
    signing secret) and committed to its own person.
    """
    known = set(PUBLIC) | set(COALITION)
    if roster_key_leaked:
        known |= {"ik:P", "bk:adv"}                              # the coalition publishes an occurrence of P with its own binding key
    sess = sessions(r, restated)
    cts = {}
    for label, s in sess:
        target = s["person"]
        ct = kem(pk("bk:adv"), s["ss"]) if (roster_key_leaked and target == "P") else challenge(r, target, s["R"], s["ss"])
        cts[label] = ct
    known |= set(cts.values())
    # honest P as an oracle: every room key it holds, every addressee name and KEM key the coalition can state, every
    # challenge it would open (A's own, and one of the coalition's making)
    own = [kem(pk("bk:P"), "ss:adv"), kem(pk("rk:RP"), "ss:adv"), kem(pk("rk:RP2"), "ss:adv")]
    calls = {}
    for key, (room, nonce) in P_KEYS.items():
        me = {"person": "P", "R": key, "room": room, "nonce": nonce}
        for a_kid in ("RA", "RC"):
            for pka in (pk("rk:RA"), pk("rk:RC")):
                for ct in list(cts.values()) + own:
                    out = prove(r, me, a_kid, pka, ct)
                    if out is not None: calls.setdefault(out, set()).add((key, a_kid))
    K = analyse(known | set(calls))
    goals, honest, tried = {}, 0, 0
    for label, s in sess:
        cands = set(calls) | {t for t in K if isinstance(t, tuple) and t[0] in ("spsk", "seal")}
        if (not r["keyed"]) or s["ss"] in K:                      # then the coalition can make any confirmation it likes
            want = info_of(r, s["room"], s["R"], s["A"], s["c"], pk("bk:" + s["person"]))
            for person in PERSONS3:
                for nonce in NONCES:
                    cands.add(confirm(r, pk("rk:RA"), s["ss"], want, person, nonce))
        for m in cands:
            tried += 1
            if not can_make(K, m): continue
            got = accept(r, s, m)
            if got is None: continue
            src = calls.get(m)
            in_room = s["R"] in P_KEYS and P_KEYS[s["R"]][0] == s["room"]
            if src == {(s["R"], s["A"])} and got == "P" and in_room:   # P made it for this key, this addressee and this room
                honest += 1
                continue
            if got == "P" and s["R"] not in P_KEYS: goal = "forged"
            elif got == "P" and not in_room: goal = "crossroom"
            elif got == "P": goal = "misaddressed"
            elif s["R"] in P_KEYS: goal = "stolen"
            else: continue                                        # the coalition binds its own key to its own person
            other = sorted(x for x in (src or ()) if x != (s["R"], s["A"]))
            how = ("an answer P made for %s to %s" % other[0] if other else
                   "an answer P made for the same room key in its other room" if src else "made by the coalition")
            goals.setdefault(goal, (label, how))
    return goals, honest, tried


INFO_MEMBERS = TEXT["info"]


def info_ablation():
    """Every subset of the info's members left out: which goals the coalition then reaches."""
    out = {}
    for k in range(len(INFO_MEMBERS) + 1):
        for drop in itertools.combinations(INFO_MEMBERS, k):
            goals, _, _ = authenticity(rule(info=tuple(x for x in INFO_MEMBERS if x not in drop)))
            out[frozenset(drop)] = frozenset(goals)
    return out


# =========================================================================================================
# 4. deniability outside
# =========================================================================================================
A_SECRETS = {"rs:RA", "rk:RA", "bk:A", "ik:A", "ck:A"}
EVERY_SECRET = {"rs:RA", "rk:RA", "bk:A", "ik:A", "ck:A", "bk:P", "ik:P", "ck:P", "rs:RP", "rk:RP", "n:RP",
                "rs:RS", "rk:RS", "n:Z", "bk:Z", "ik:Z", "bk:T", "ik:T"}
P_SECRETS = {"bk:P", "ik:P", "ck:P"}                             # what makes P the person P: the keys of its identity


def transcript(r, key, nonce, ss):
    """What the addressee A ends up holding after one exchange for room key `key` committed to P: every term of
    it, whoever made it. Returns (view, shown): shown is what A would hand a third party to show who R named."""
    c = commitment(ROOM, key, "P", nonce)
    row = seat_row(key, ROOM, c) if r["commit_in_seat_row"] else seat_row(key, ROOM, "none")
    if r["seat_signed_by"] == "identity": row = tup(row, sig("ik:P", row[2]))      # the person's identity key signs it as well
    claim_body = tup("claim", "P", pk("bk:P"), row) if r["commit_in_seat_row"] else tup("claim", "P", pk("bk:P"), row, c)
    if r["claim_signed"]: claim_body = tup(claim_body, sig("ik:P", tup("claim", key, ROOM)))
    claim = seal(pk("rk:RA"), claim_body)
    ct = challenge(r, "P", key, ss)
    chal = seal(pk("rk:" + key), tup("chal", ct, "RA"))
    conf = confirm(r, pk("rk:RA"), ss, info_of(r, ROOM, key, "RA", c, pk("bk:P")), "P", nonce)
    view = [row, claim, claim_body, ct, ss, chal, conf, tup("P", nonce)]
    shown = tup(row, c, tup("P", nonce))
    return view, shown


FRESH = {"RP": "R*", "rs:RP": "rs:R*", "rk:RP": "rk:R*", "n:RP": "n*", "RS": "R*", "rs:RS": "rs:R*", "rk:RS": "rk:R*",
         "n:Z": "n*", "ss:A:real": "ss*", "ss:A:sim": "ss*"}


def canon(t):
    """A term up to the names of what is made fresh for one exchange: the room key, the nonce, the challenge secret."""
    if isinstance(t, tuple): return (t[0],) + tuple(canon(x) for x in t[1:])
    return FRESH.get(t, t)


def deniability(r):
    """Four answers.
        from_a_and_r   every term A holds follows from A's own secrets and from what a holder of R's secret says (the
                       seat row and the opening)
        without_p      the same view, up to fresh names, is made by A and a party Z that is not P, and every term of it
                       follows from the secrets of everyone except P
        r_named_p      what A shows a third party (the seat row and the opening) cannot be made without R's secret, and
                       it opens to P: A can show that R's holder named P
        convinces      a third party handed everything A holds and every secret of A is convinced that P took part: some
                       term of it cannot be made without a key of P's identity
    """
    pub = set(PUBLIC) | {pk("bk:P"), pk("rk:RP"), pk("rk:RS"), "RS", "none", "claim", "chal", "rec"}
    view, shown = transcript(r, "RP", "n:RP", "ss:A:real")
    row = view[0]
    base_a = analyse(pub | A_SECRETS | {"ss:A:real", row, "n:RP"})
    from_a_and_r = all(can_make(base_a, t) for t in view)
    sim, _ = transcript(r, "RS", "n:Z", "ss:A:sim")
    non_p = analyse(pub | (EVERY_SECRET - P_SECRETS) | {"ss:A:sim"})
    without_p = [canon(t) for t in sim] == [canon(t) for t in view] and all(can_make(non_p, t) for t in sim)
    not_r = analyse(pub | (EVERY_SECRET - {"rs:RP"}) | {"ss:A:real"})        # everyone but R's holder, and they hold the row
    opens_to_p = shown[2] in subterms(shown) and commitment(ROOM, "RP", shown[3][1], shown[3][2]) == shown[2]
    signed_part = [t for t in subterms(shown[1]) if isinstance(t, tuple) and t[0] == "sig" and t[1] == "rs:RP"]
    names_p_under_r = any(shown[2] in subterms(s) for s in signed_part)
    r_named_p = opens_to_p and names_p_under_r and not can_make(not_r, shown[1])
    # the seat row is not handed over as a given: everyone but P holds R's secret and the nonce, and must make it
    convinces = any(not can_make(analyse(pub | (EVERY_SECRET - P_SECRETS) | {"ss:A:real"}), t) for t in view)
    return {"from_a_and_r": from_a_and_r, "without_p": without_p, "r_named_p": r_named_p, "convinces": convinces}


def live_judge():
    """The stated limit, as a run: a third party T forms the challenge and A relays. A does not hold the challenge's
    secret, so the confirmation is one that only P's binding key and T could have keyed. T is then convinced."""
    r = TEXT
    c = commitment(ROOM, "RP", "P", "n:RP")
    conf = prove(r, {"person": "P", "R": "RP", "room": ROOM, "nonce": "n:RP"}, "RA", pk("rk:RA"), challenge(r, "P", "RP", "ss:T"))
    others = analyse(set(PUBLIC) | (EVERY_SECRET - P_SECRETS) | {"n:RP", seat_row("RP", ROOM, c)})   # everyone but P, and not T's secret
    a_alone = analyse(set(PUBLIC) | A_SECRETS | {"n:RP"})
    return conf is not None and not can_make(others, conf) and not can_make(a_alone, conf)


# =========================================================================================================
# 5. the carriage
# =========================================================================================================
# An exchange is one ordered pair (prover, addressee). Its messages are the claim, and for each challenge the
# addressee has issued, that challenge and its confirmation. The network holds every message sent and delivers any of
# them to anyone, any number of times, or never. A wipe empties it. An addressee may lose its pending secret.
CARRIAGE_PLANTS = ("sign_on_claim", "hearsay", "final_without_ack", "confirm_not_keyed", "claim_once", "challenge_once", "refuse_after_bad",
                   "sign_on_one", "final_without_cosign", "accept_without_pending", "pending_not_resent")
ENVIRONMENT = ("lose the pending secret", "the network loses everything in flight")      # steps no party chooses


def config(name, L=None, W=None):
    """The bounds run. parties sign a row once they hold what `needs` lists; `final` is the admission. L and W, where
    given, replace the bound on lost pending secrets and on wipes of the network."""
    cfg = _config(name)
    if L is not None: cfg["L"] = L
    if W is not None: cfg["W"] = W
    return cfg


def _config(name):
    if name == "widening":       # joiner J; the inviter I and a second cosigner C; the duty holder D
        return {"name": name, "ex": (("J", "I"), ("J", "C"), ("J", "D")), "inviter": "I",
                "sign": (("cosign:I", (0,)), ("cosign:C", (1,)), ("ack:D", (2,))), "ack": ("ack:D",), "L": 2, "W": 2}
    if name == "founding2":      # two founders, each holds the other's binding before signing the founding record
        return {"name": name, "ex": (("F1", "F2"), ("F2", "F1")), "inviter": None,
                "sign": (("found:F1", (1,)), ("found:F2", (0,))), "ack": (), "L": 2, "W": 2}
    if name == "founding3":      # three founders, six exchanges, one lost secret and no wipe
        ex = tuple((a, b) for a in ("F1", "F2", "F3") for b in ("F1", "F2", "F3") if a != b)
        return {"name": name, "ex": ex, "inviter": None,
                "sign": tuple(("found:" + f, tuple(i for i, e in enumerate(ex) if e[1] == f)) for f in ("F1", "F2", "F3")),
                "ack": (), "L": 1, "W": 0}
    raise ValueError(name)


def exchange_terms(r, cfg):
    """The terms of every message of the configuration, and who can open each."""
    msgs = {}
    for e, (p, a) in enumerate(cfg["ex"]):
        R, A, person, nonce = "R" + p, "R" + a, "person:" + p, "n:" + p
        c = commitment(ROOM, R, person, nonce)
        me = {"person": person, "R": R, "room": ROOM, "nonce": nonce}
        msgs[(e, "claim", 0)] = seal(pk("rk:" + A), tup("claim", person, pk("bk:" + person), seat_row(R, ROOM, c)))
        for i in range(cfg["L"] + 1):
            ss = "ss:%d:%d" % (e, i)
            ct = challenge(r, person, R, ss)
            msgs[(e, "chal", i)] = seal(pk("rk:" + R), tup("chal", ct, A))
            msgs[(e, "conf", i)] = prove(r, me, A, pk("rk:" + A), ct)
    return msgs


def session_of(cfg, e, i):
    p, a = cfg["ex"][e]
    R, person = "R" + p, "person:" + p
    return {"room": ROOM, "R": R, "A": "R" + a, "person": person, "c": commitment(ROOM, R, person, "n:" + p),
            "ss": None if i is None else "ss:%d:%d" % (e, i)}


def delivery_table(r, cfg):
    """Every message against every party and every pending secret that party could hold: does the party open it, and
    does it then hold a binding. Read with the rule r, and with the text's rule for the ghost `verified`."""
    msgs = exchange_terms(r, cfg)
    parties = sorted({x for e in cfg["ex"] for x in e})
    opens, acc, vref, wrong = {}, {}, {}, 0
    for key, m in msgs.items():
        for q in parties:
            opens[(key, q)] = m[0] == "seal" and m[2] in analyse({m, "rk:R" + q, "bk:person:" + q})
    for (e, kind, i), m in msgs.items():
        if kind != "conf": continue
        for e2 in range(len(cfg["ex"])):
            for j in [None] + list(range(cfg["L"] + 1)):
                got = accept(r, session_of(cfg, e2, j), m) is not None
                acc[(e, i, e2, j)] = got
                vref[(e, i, e2, j)] = e == e2 and j is not None and i == j      # the addressee's own live challenge was answered
                wrong += got and (e2 != e or j != i)
    return {"msgs": msgs, "opens": opens, "accept": acc, "verified": vref, "wrong": wrong, "parties": parties}


# the state: (exchanges, rows, inv, losses, wipes); one exchange: (claim, ever, chal, conf, issued, pending, held, verified, lost, dead)
def initial(cfg):
    return (tuple((0, 0, 0, 0, 0, -1, 0, 0, 0, 0) for _ in cfg["ex"]), frozenset(), (0, 0), 0, 0)


def steps(cfg, tab, plant, s):
    """Every step from s, as (label, next state)."""
    exs, rows, (inv_sent, has_inv), losses, wipes = s
    out = []
    done = "final" in rows
    def put(label, e=None, x=None, rows_=None, inv=None, losses_=None, wipes_=None, exs_=None):
        ne = exs_ if exs_ is not None else (exs if e is None else exs[:e] + (x,) + exs[e + 1:])
        out.append((label, (ne, rows if rows_ is None else rows_, (inv_sent, has_inv) if inv is None else inv,
                            losses if losses_ is None else losses_, wipes if wipes_ is None else wipes_)))
    if cfg["inviter"] and not done:
        put("send invitation", inv=(1, has_inv))
        if inv_sent: put("deliver invitation", inv=(inv_sent, 1))
    for e, (claim, ever, chal, conf, issued, pending, held, verified, lost, dead) in enumerate(exs):
        p, a = cfg["ex"][e]
        joined = has_inv or not cfg["inviter"]
        # the prover sends its claim: again and again until the admission is held, since the admission is a row it can read
        if joined and not done and not (plant == "claim_once" and ever):
            put("send claim", e, (1, 1, chal, conf, issued, pending, held, verified, lost, dead))
        if claim and not held and not dead:
            cap = 1 if plant == "challenge_once" else 1 + lost
            if pending < 0 and issued < cap:
                put("issue challenge", e, (claim, ever, chal | (1 << issued), conf, issued + 1, issued, held, verified, lost, dead))
            elif pending >= 0 and plant != "pending_not_resent":
                put("send the pending challenge again", e, (claim, ever, chal | (1 << pending), conf, issued, pending, held, verified, lost, dead))
        for i in range(cfg["L"] + 1):
            if chal >> i & 1 and joined:
                put("answer challenge", e, (claim, ever, chal, conf | (1 << i), issued, pending, held, verified, lost, dead))
            if conf >> i & 1 and not held and not dead:
                j = pending if pending >= 0 else None
                if tab["accept"][(e, i, e, j)]:
                    put("accept confirmation", e, (claim, ever, chal, conf, issued, -1, 1, int(tab["verified"][(e, i, e, j)]), lost, dead))
                elif plant == "accept_without_pending" and j is None:
                    put("accept a confirmation while holding no pending secret", e, (claim, ever, chal, conf, issued, -1, 1, 0, lost, dead))
                else:
                    put("drop a confirmation it cannot open", e, (claim, ever, chal, conf, issued, pending, held, verified, lost,
                                                                  1 if plant == "refuse_after_bad" else dead))
            if conf >> i & 1 and held:
                put("a confirmation repeated to a holder changes nothing", e, exs[e])
        if pending >= 0 and losses < cfg["L"]:
            put("lose the pending secret", e, (claim, ever, chal, conf, issued, -1, held, verified, lost + 1, dead), losses_=losses + 1)
        if plant == "hearsay" and not held:
            if any(x[6] and cfg["ex"][k][0] == p for k, x in enumerate(exs) if k != e):
                put("take another member's word", e, (claim, ever, chal, conf, issued, pending, 1, 0, lost, dead))
    if wipes < cfg["W"] and (inv_sent or any(x[0] or x[2] or x[3] for x in exs)):
        put("the network loses everything in flight", exs_=tuple((0, x[1], 0, 0) + x[4:] for x in exs), inv=(0, has_inv), wipes_=wipes + 1)
    for row, needs in cfg["sign"]:
        if row in rows: continue
        ok = all(exs[k][6] for k in needs)
        if plant == "sign_on_claim": ok = all(exs[k][4] > 0 or exs[k][6] for k in needs)
        if plant == "sign_on_one": ok = any(exs[k][6] for k in needs)
        if ok: put("sign " + row, rows_=rows | {row})
    if not done:
        need = [row for row, _ in cfg["sign"] if not (plant == "final_without_ack" and row in cfg["ack"])]
        if plant == "final_without_cosign": need = [row for row in need if row in cfg["ack"] or row == "cosign:" + str(cfg["inviter"])]
        if all(x in rows for x in need) and (has_inv or not cfg["inviter"]):
            put("the admission is signed", rows_=rows | {"final"})
    return out


def safe(cfg, s):
    """Property 3 at one state: every signature stands on a binding its signer checked itself, and the admission
    stands on every one of them."""
    exs, rows = s[0], s[1]
    for row, needs in cfg["sign"]:
        if row in rows and not all(exs[k][7] for k in needs): return False
    if "final" in rows and not all(row in rows and all(exs[k][7] for k in needs) for row, needs in cfg["sign"]): return False
    return True


def explore(cfg, r=TEXT, plant=None, stop_at_unsafe=False):
    """Every reachable state. Returns the count, the first unsafe state's path, the labels seen, the states from which
    the admission can never be signed, and facts about what was reached. With stop_at_unsafe the run ends at the first
    unsafe state, and then says nothing of property 4."""
    if plant == "confirm_not_keyed": r = rule(keyed=False)
    tab = delivery_table(r, cfg)
    s0 = initial(cfg)
    seen, order, edges, own, labels, same = {s0: None}, [s0], {}, {}, set(), {s0: s0}
    bad = None
    i = 0
    while i < len(order):
        s = order[i]; i += 1
        if bad is None and not safe(cfg, s):
            bad = s
            if stop_at_unsafe: break
        out, mine = [], []
        for label, t in steps(cfg, tab, plant, s):
            labels.add(label)
            if t not in seen:
                seen[t] = (s, label)
                same[t] = t
                order.append(t)
            out.append(same[t])                                   # one object for each state, whoever reaches it
            if label not in ENVIRONMENT: mine.append(same[t])
        edges[s] = out
        own[s] = mine
    # property 4: from every state, the admission can still be signed
    def cannot_finish(graph):
        back = {}
        for s, ts in graph.items():
            for t in ts: back.setdefault(t, []).append(s)
        good = {s for s in seen if "final" in s[1]}
        todo = list(good)
        while todo:
            t = todo.pop()
            for s in back.get(t, ()):
                if s not in good:
                    good.add(s); todo.append(s)
        return [s for s in order if s not in good]
    stuck = cannot_finish(edges)
    # the same with no help from a loss or a wipe: a path to the admission that needs the network to lose something
    # is not one the parties can take
    stuck_own = None if (bad is not None and stop_at_unsafe) else len(cannot_finish(own))
    def path(s):
        out = []
        while seen[s] is not None:
            s, label = seen[s]
            out.append(label)
        return list(reversed(out))
    n_sign = len(cfg["sign"])
    facts = {
        "admitted": any("final" in s[1] for s in seen),
        "admitted after a lost secret": any("final" in s[1] and s[3] > 0 for s in seen),
        "admitted after the network lost everything": any("final" in s[1] and s[4] > 0 for s in seen),
        "all but one signed and the admission waits": any("final" not in s[1] and len(s[1]) == n_sign - 1 for s in seen),
        "a stale confirmation is dropped": "drop a confirmation it cannot open" in labels,
        "a repeated confirmation changes nothing": "a confirmation repeated to a holder changes nothing" in labels,
        "a pending challenge is sent again": "send the pending challenge again" in labels,
    }
    if cfg["ack"]:
        others = frozenset(row for row, _ in cfg["sign"] if row not in cfg["ack"])
        ack_ex = [k for row, needs in cfg["sign"] if row in cfg["ack"] for k in needs]
        facts["every cosigner has signed, the duty holder holds no binding, and the admission waits"] = any(
            s[1] == others and not any(s[0][k][6] for k in ack_ex) for s in seen)
    return {"states": len(seen), "unsafe": None if bad is None else path(bad), "stuck": len(stuck),
            "stuck_path": path(stuck[0]) if stuck else None, "stuck_own": stuck_own, "facts": facts, "wrong_accepts": tab["wrong"]}


def misdelivery(cfg, r=TEXT):
    """Every message handed to every party: who can open it. Returns (pairs, opened by a party it was not made for)."""
    tab = delivery_table(r, cfg)
    intended = {}
    for (e, kind, i) in tab["msgs"]:
        p, a = cfg["ex"][e]
        intended[(e, kind, i)] = p if kind == "chal" else a
    n = bad = 0
    for (key, q), can in tab["opens"].items():
        if key[1] == "conf": continue
        n += 1
        bad += can != (q == intended[key])
    for (e, i, e2, j), got in tab["accept"].items():
        n += 1
        bad += got != (e == e2 and i == j)
    return n, bad


# =========================================================================================================
# 6. a second voice
# =========================================================================================================
# P has a first admission (room key R1) and asks for a second (R2). Each signer of the second is described by three
# facts: does it check, has the first admission reached it as a seat (sees), does it hold R1's binding (holds).
READINGS = ("as written", "as written, strict", "held")


def presentable():
    """What P can make a checking member hold for R2. P and an accomplice Z act together; Q is an honest person who is
    not in the room. For every person the seat row commits to and every person claimed: the person the member's own
    check ends with, or None."""
    out = {}
    K = analyse(set(PUBLIC) | {"bk:P", "ik:P", "bk:Z", "ik:Z", "rs:R2", "rk:R2", "n:2", "Q", "R2"})
    for committed in ("P", "Q", "Z"):
        for claimed in ("P", "Q", "Z"):
            s = {"room": ROOM, "R": "R2", "A": "RA", "person": claimed, "c": commitment(ROOM, "R2", committed, "n:2"), "ss": "ss:A:9"}
            K2 = analyse(K | {challenge(TEXT, claimed, "R2", "ss:A:9")})
            got = None
            if "ss:A:9" in K2:
                want = info_of(TEXT, ROOM, "R2", "RA", s["c"], pk("bk:" + claimed))
                for person in ("P", "Q", "Z"):
                    got = got or accept(TEXT, s, confirm(TEXT, pk("rk:RA"), "ss:A:9", want, person, "n:2"))
            out[(committed, claimed)] = got
    return out


def decide(reading, checks, sees, holds, plant=None):
    """One signer's answer to the second admission: sign, refuse or wait."""
    if not checks: return "sign"
    if plant == "ignore_seated": return "sign"
    if reading == "as written":                  # refuses what it can tell: R1 is seated where it reads, and it holds R1's binding
        return "refuse" if (sees and holds) else "sign"
    if reading == "as written, strict":          # it cannot say 'not already seated' while it lacks a seated key's binding
        if sees and not holds: return "wait"
        return "refuse" if sees else "sign"
    if reading == "held":                        # refuses a person it holds another binding of, seated or not
        if holds: return "refuse"
        return "wait" if sees else "sign"
    raise ValueError(reading)


def decide_from_bindings(checks, sees, holds, pres=None, joiner="P", first="P"):
    """The cosigner's duty as CC 3.1.3.2 writes it, read from what the signer holds and not from a table: it ends its
    own exchange for the second room key with a person (presentable), and refuses when that person is one it holds a
    binding of on a room key it reads as seated."""
    if not checks: return "sign"
    named = (pres or presentable())[(joiner, joiner)]
    seated_persons = {first} if (sees and holds) else set()
    return "refuse" if named in seated_persons else "sign"


def second_voice(reading, duty_holder, max_signers=4, plant=None):
    """Every second admission of up to max_signers signers, each with its three facts, and a duty holder (who
    acknowledged the first, so holds R1's binding) where the room seats one. Returns the cases, the cases seated, and
    the seated cases sorted by why a checking signer signed."""
    seated = n = with_checking_d = 0
    classes = {"none checked": 0, "a checker without the first binding": 0, "a checker the first seat had not reached": 0}
    for k in range(2, max_signers + 1):
        for signers in itertools.product(itertools.product((0, 1), repeat=3), repeat=k):
            for d in (itertools.product((0, 1), repeat=2) if duty_holder else [None]):
                n += 1
                everyone = list(signers) + ([(d[0], d[1], 1)] if d is not None else [])
                if any(decide(reading, c, s, hd, plant) != "sign" for c, s, hd in everyone): continue
                seated += 1
                with_checking_d += d is not None and d[0] == 1
                checkers = [(s, hd) for c, s, hd in everyone if c]
                if not checkers: classes["none checked"] += 1
                elif any(s and not hd for s, hd in checkers): classes["a checker without the first binding"] += 1
                else: classes["a checker the first seat had not reached"] += 1
    return {"cases": n, "seated": seated, "classes": classes, "seated with a checking duty holder": with_checking_d}


def second_voice_sequential(reading, duty_holder, max_signers=4, plant=None):
    """The case the text describes: the first seat has reached every signer and every signer holds its binding.
    Returns (cases, seated, seated with a checker among the signers)."""
    n = seated = with_checker = 0
    for k in range(2, max_signers + 1):
        for checks in itertools.product((0, 1), repeat=k):
            for d in ((0, 1) if duty_holder else [None]):
                n += 1
                everyone = [(c, 1, 1) for c in checks] + ([(d, 1, 1)] if d is not None else [])
                if any(decide(reading, c, s, hd, plant) != "sign" for c, s, hd in everyone): continue
                seated += 1
                with_checker += any(c for c, _, _ in everyone)
    return n, seated, with_checker


# =========================================================================================================
# 7. a count of persons waits
# =========================================================================================================
COUNT_KEYS = ("k1", "k2", "kP", "kQ", "kS")                      # kS is one more key that the colluders P and Q share
TRUTH = {"k1": "H1", "k2": "H2", "kP": "P", "kQ": "Q", "kS": "P"}
HOLDERS = {"k1": ("H1",), "k2": ("H2",), "kP": ("P",), "kQ": ("Q",), "kS": ("P", "Q")}     # whose binding keys answer for the key


def acceptable(r, key, commits, two_rows="any"):
    """The persons a node can come to hold for `key`, by its own check, given the commitments on the seat rows it
    holds for the key. The holders of the key answer any challenge made to one of them, with any opening."""
    if len(set(commits)) > 1 and two_rows == "void": return frozenset()
    out = set()
    for c in set(commits):
        for claimed in HOLDERS[key]:
            s = {"room": ROOM, "R": key, "A": "RA", "person": claimed, "c": c, "ss": "ss:n"}
            want = info_of(r, ROOM, key, "RA", c, pk("bk:" + claimed))
            for person in HOLDERS[key]:
                got = accept(r, s, confirm(r, pk("rk:RA"), "ss:n", want, person, "n:" + key))
                if got: out.add(got)
    return frozenset(out)


def person_count(votes, held, count_bound_only=False, keys=COUNT_KEYS, voters_only=False):
    """A count of persons at one node. votes: key -> yes, no or None. held: key -> the person its binding names."""
    missing = frozenset(k for k in keys if k not in held)
    if voters_only and not any(votes.get(k) for k in missing): missing = frozenset()
    if missing and not count_bound_only: return ("waits", missing)
    said = {}
    for k, v in votes.items():
        if v and k in held: said.setdefault(held[k], set()).add(v)
    return ("counted", sum(1 for v in said.values() if v == {"yes"}), sum(1 for v in said.values() if v == {"no"}),
            len(set(held.values())))


def count_world(r=TEXT, equivocate=False, two_rows="any", count_bound_only=False, voters_only=False):
    """Two nodes hold the same rows. Each holds, for each seated key, no binding or one its own check accepts. Every
    pair of holdings and every way the keys vote. Returns the tallies of what the pair concludes."""
    commits = {k: [commitment(ROOM, k, TRUTH[k], "n:" + k)] for k in COUNT_KEYS}
    if equivocate: commits["kS"].append(commitment(ROOM, "kS", "Q", "n:kS"))       # a second seat row of kS, committed to Q
    options = {k: [None] + sorted(acceptable(r, k, commits[k], two_rows)) for k in COUNT_KEYS}
    holdings = [dict((k, p) for k, p in zip(COUNT_KEYS, combo) if p) for combo in itertools.product(*(options[k] for k in COUNT_KEYS))]
    out = {"pairs": 0, "both counted": 0, "fork": 0, "differ and neither waits": 0, "one waits": 0, "both wait": 0,
           "missing not as stated": 0, "holdings": len(holdings), "first fork": None}
    for votes_ in itertools.product(("yes", "no", None), repeat=len(COUNT_KEYS)):
        votes = dict(zip(COUNT_KEYS, votes_))
        ans = [person_count(votes, hd, count_bound_only, voters_only=voters_only) for hd in holdings]
        for i, a in enumerate(ans):
            if a[0] == "waits" and a[1] != frozenset(COUNT_KEYS) - set(holdings[i]): out["missing not as stated"] += 1
        for i, a in enumerate(ans):
            for j, b in enumerate(ans):
                out["pairs"] += 1
                wa, wb = a[0] == "waits", b[0] == "waits"
                if not wa and not wb:
                    out["both counted"] += 1
                    if a != b:
                        out["fork"] += 1
                        out["first fork"] = out["first fork"] or (votes, holdings[i], a, holdings[j], b)
                    if holdings[i] != holdings[j]: out["differ and neither waits"] += 1
                elif wa and wb: out["both wait"] += 1
                else: out["one waits"] += 1
    out["a full holding exists"] = any(len(hd) == len(COUNT_KEYS) for hd in holdings)
    out["full holdings"] = sum(len(hd) == len(COUNT_KEYS) for hd in holdings)
    out["persons for a key, at most"] = max(len(v) - 1 for v in options.values())
    return out


# =========================================================================================================
# 8. what a relay learns
# =========================================================================================================
DIRECTORY = {pk("ck:P"): "P", pk("bk:P"): "P", pk("ck:I"): "I", pk("bk:I"): "I"}     # public: an identity's keys name the person
RELAY_PLANTS = ("claim_in_clear", "challenge_bare", "info_in_header", "address_by_record", "wrap_to_identity_key")


def envelopes(plant=None):
    """Every envelope of one honest widening: the invitation, the return and the other claims, the challenges, the
    confirmations. Returns [(name, term)]."""
    c = commitment(ROOM, "RJ", "P", "n:J")
    row = seat_row("RJ", ROOM, c)
    recs = {a: record("R" + a, ROOM, commitment(ROOM, "R" + a, "person:" + a, "n:" + a)) for a in ("I", "C", "D")}
    out = [("the invitation", seal(pk("ck:P"), tup("inv", ROOM, recs["I"], recs["C"], recs["D"])))]
    me = {"person": "P", "R": "RJ", "room": ROOM, "nonce": "n:J"}
    for a in ("I", "C", "D"):
        body = tup("claim", "P", pk("bk:P"), row)
        claim = body if plant == "claim_in_clear" else seal(pk("rk:R" + a), body)
        if plant == "address_by_record": claim = tup(recs[a], claim)
        if plant == "wrap_to_identity_key" and a == "I": claim = seal(pk("ck:I"), body)   # as today's wraps, to a content key
        ct = challenge(TEXT, "P", "RJ", "ss:" + a)
        chal = tup(ct, "R" + a) if plant == "challenge_bare" else seal(pk("rk:RJ"), tup("chal", ct, "R" + a))
        conf = prove(TEXT, me, "R" + a, pk("rk:R" + a), ct)
        if plant == "info_in_header": conf = tup(conf[3], conf)
        out += [("the claim to " + a + (", the return" if a == "I" else ""), claim), ("the challenge from " + a, chal), ("the confirmation to " + a, conf)]
    return out


def relay(plant=None, key_private=False):
    """What a relay that holds no row of the room and no secret derives from each envelope, and from all of them
    together. Returns {envelope: (persons, room?)} and the same for the whole."""
    def learned(terms):
        K = analyse(set(terms), key_private)
        persons = frozenset(DIRECTORY[t] for t in K if t in DIRECTORY) | frozenset(x for x in ("P",) if x in K)
        room = ROOM in K or any(isinstance(t, tuple) and t[0] == "t" and t[1:2] == ("rec",) for t in K)
        secret = any(x in K for x in ("n:J", "ss:I", "ss:C", "ss:D"))
        return persons, room, secret
    env = envelopes(plant)
    each = {name: learned([t]) for name, t in env}
    return each, learned([t for _, t in env])


def row_holder(r=TEXT):
    """A holder of the room's rows that holds no binding and no secret (a custodian, or a relay handed the rows). It
    knows every public person. Returns the persons it can tie to the joiner's room key: those whose commitment it
    can compute and then find on the seat row."""
    def c_of(person):
        return commitment(ROOM, "RJ", person, "n:J") if r["nonce_in_commit"] else h("CEG-seat/2", ROOM, "RJ", person)
    c = c_of("P")
    K = analyse(set(PUBLIC) | {"RJ", pk("rk:RJ"), "rec", seat_row("RJ", ROOM, c)}) - {c}
    return {person for person in ("P", "C", "A", "Z") if c_of(person) == c and can_make(K, c_of(person))}
