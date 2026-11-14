"""
witnesses.py: the seventeen cases of formal/derivation/order/witnesses.tsv as rows for causal_kernel.

Each case gives: the rows (encoded with the resolution the table's `symmetric_outcome` column describes),
a rule for the conclusion layer (it reads a row and its concluded ancestors, nothing else), an answer
built from the kernel's derived functions, the answer the table reasoned, variants, and adversaries.
Nothing here is the result of a run: check.py runs every arrival order and compares.
"""
import causal_kernel as CK

K = CK.K
R = CK.row


def show(hn):
    h, n = hn
    return h if n == 1 else ("empty" if n == 0 else "conflict")


CASES = []


def case(**kw):
    kw.setdefault("variants", [])
    kw.setdefault("adversaries", [])
    kw.setdefault("match", None)
    CASES.append(kw)


# ---- W1 census composite ---------------------------------------------------------------------------------
def w1_rule(r, P, past):
    if r["kind"] == "composite":
        parts = [p for p in K.sel(P, kind="partial") if p["id"] in r["names"]]
        return len(parts) == len(r["names"]) and sum(p["val"] for p in parts) == r["total"]  # sum: not in kernel_lib
    return True


def w1_ans(S):
    return {"census": show(CK.slot(S, K.sel(S.Cs, kind="composite"), value=lambda r: r["total"])),
            "void_alone": sorted(r["id"] for r in K.sel(S.rows, kind="composite") if not S.C[r["id"]])}


pa, pb = R("pa", "partial", "seatA", val=3), R("pb", "partial", "seatB", val=4)
c1 = R("c1", "composite", "seatA", ("pa", "pb"), total=7)
c2 = R("c2", "composite", "seatB", ("pa", "pb"), total=7)
c2x = R("c2x", "composite", "seatB", ("pa", "pb"), total=9)
pb2 = R("pb2", "partial", "seatB", val=5)
c3 = R("c3", "composite", "seatB", ("pa", "pb2"), total=8)
case(id="W1", rule=w1_rule, answer=w1_ans, rows=[pa, pb, c1, c2],
     note="two partials added (the table's rows name none); each composite names both and carries a total; "
          "the rule recomputes the total from the named partials; the slot compares totals",
     expected={"census": 7, "void_alone": []}, needed="nothing beyond the partials being named by digest",
     variants=[("second composite carries another total", [pa, pb, c1, c2x], {"census": 7, "void_alone": ["c2x"]})],
     adversaries=[
         ("duplicate to empty the slot: a serve seat signs a second composite with another total over the same partials",
          [pa, pb, c1], [pa, pb, c1, c2x],
          lambda b, a: "nothing: the second composite is void alone, census stays %s" % a["census"] if a["census"] == b["census"] else "census now %s" % a["census"]),
         ("duplicate one level down: a partial seat signs a second partial and a composite is made over it",
          [pa, pb, c1], [pa, pb, c1, pb2, c3],
          lambda b, a: "the period's census goes from %s to %s: both composites recompute, they differ, the slot is empty" % (b["census"], a["census"])),
     ])


# ---- W2, W3 census shares --------------------------------------------------------------------------------
def share_ans(S):
    hn = CK.slot(S, K.sel(S.Cs, kind="share", slot="period7/tok/0"), value=lambda r: r["body"])
    return {"share": show(hn), "voices": 1 if hn[1] == 1 else 0}


for cid, signer, fam in (("W2", "m1", "census:member:share"), ("W3", "n1", "census:share:room")):
    s1 = R("s1", "share", signer, slot="period7/tok/0", body="tok,0,x", family=fam)
    s2 = R("s2", "share", signer, slot="period7/tok/0", body="tok,0,x", family=fam)
    s2x = R("s2x", "share", signer, slot="period7/tok/0", body="tok,0,y", family=fam)
    s3 = R("s3", "share", "seat", slot="period7/tok/0", body="tok,0,z", family=fam)
    case(id=cid, rule=lambda r, P, past: True, answer=share_ans, rows=[s1, s2],
         note="as the table gives them: two rows with the same values and different signed instants (two "
              "digests, one body); the slot is (period, token, index) and compares bodies; no row names another",
         expected={"share": "tok,0,x", "voices": 1}, needed="nothing",
         variants=[("the two rows carry different bodies", [s1, s2x], {"share": "conflict", "voices": 0})],
         adversaries=[
             ("duplicate to empty the slot: whoever knows the token signs a share with another body",
              [s1], [s1, s3],
              lambda b, a: "that one voice goes from %d to %d; no second voice is gained" % (b["voices"], a["voices"])),
         ])


# ---- membership: W4, W5, W6, W10 -------------------------------------------------------------------------
def mem_rule(r, P, past):
    k = r["kind"]
    if k in ("acceptance", "decline"):
        return bool(K.sel(P, kind="proposal", id=r["ref"], subject=r["signer"]))
    if k == "widening":
        for a in K.sel(P, kind="acceptance", signer=r["subject"]):
            if a["id"] not in r["names"]:
                continue
            if K.sel(P, kind="decline", signer=r["subject"], ref=a["ref"]):
                continue                                   # the widening's signer had seen the decline
            if any(past(a["id"], x["id"]) for x in K.sel(P, kind="removal", removes=r["subject"])):
                continue                                   # the acceptance was spent before a removal it names
            return True
        return False
    if k == "removal":
        return r["signer"].startswith("founder")
    return True


def seat(S, key):
    return show(CK.slot(S, K.sel(S.Cs, kind="widening", subject=key) + K.sel(S.Cs, kind="removal", removes=key),
                        value=lambda r: "in" if r["kind"] == "widening" else "out"))


def reply(S, p):
    on = CK.wins(S, K.sel(S.Cs, target=p), lambda r: 2 if r["kind"] == "widening" else 1)
    return show(CK.slot(S, on, value=lambda r: r["kind"]))


def mem_ans(S):
    return {"reply": reply(S, "p"), "member_K": seat(S, "K")}


p = R("p", "proposal", "founder", subject="K")
a = R("a", "acceptance", "K", ("p",), ref="p", target="p")
d = R("d", "decline", "K", ("p",), ref="p", target="p")
w = R("w", "widening", "founder", ("a",), subject="K", target="p")
w2 = R("w2", "widening", "founder2", ("a",), subject="K", target="p")
dX = R("dX", "decline", "X", ("p",), ref="p", target="p")
case(id="W4", rule=mem_rule, answer=mem_ans, rows=[p, a, d],
     note="both replies name the proposal; a reply is concluded when its signer is the proposal's subject; "
          "the reply slot compares kinds",
     expected={"reply": "conflict", "member_K": "empty"}, needed="nothing",
     adversaries=[
         ("duplicate to empty the slot: someone other than K signs a decline of K's proposal",
          [p, a], [p, a, dX],
          lambda b, a_: "nothing: the row concludes nothing, reply stays %s" % a_["reply"] if a_ == b else "reply now %s" % a_["reply"]),
         ("K signs both replies", [p, a], [p, a, d],
          lambda b, a_: "K closes its own invitation: reply %s -> %s" % (b["reply"], a_["reply"])),
     ])

w_both = R("w", "widening", "founder", ("a", "d"), subject="K", target="p")
d_late = R("d2", "decline", "K", ("p", "w"), ref="p", target="p")
case(id="W5", rule=mem_rule, answer=mem_ans, rows=[p, a, d, w],
     note="W4 plus a widening that names the acceptance and not the decline; on the proposal a widening is "
          "a higher kind than a reply (wins), and the seat slot is read from widenings and removals",
     expected={"reply": "widening", "member_K": "in"}, needed="nothing",
     variants=[("no widening (W4's rule)", [p, a, d], {"reply": "conflict", "member_K": "empty"}),
               ("the widening names the decline as well", [p, a, d, w_both], {"reply": "conflict", "member_K": "empty"})],
     adversaries=[
         ("K declines after the widening, naming it, to un-join", [p, a, w], [p, a, w, d_late],
          lambda b, a_: "nothing: member_K stays %s" % a_["member_K"] if a_["member_K"] == b["member_K"] else "member_K now %s" % a_["member_K"]),
         ("withhold an acknowledgement: the inviter holds K's decline and signs a widening that names only the acceptance",
          [p, a, d, w_both], [p, a, d, w],
          lambda b, a_: "K, who signed both replies, is seated: member_K %s -> %s. The inviter decides by what it leaves unnamed" % (b["member_K"], a_["member_K"])),
     ])

x = R("x", "removal", "founder", ("w",), removes="K")
w3 = R("w3", "widening", "founder2", ("a",), subject="K", target="p")
w5 = R("w5", "widening", "founder2", ("a", "x"), subject="K", target="p")
p2 = R("p2", "proposal", "founder", subject="K")
a2 = R("a2", "acceptance", "K", ("p2",), ref="p2", target="p2")
w4 = R("w4", "widening", "founder", ("a2", "x"), subject="K", target="p2")
w4b = R("w4b", "widening", "founder", ("a2",), subject="K", target="p2")
case(id="W6", rule=mem_rule, answer=mem_ans, rows=[p, a, w, w2],
     note="two widenings name one acceptance; the seat slot compares what they say (K is in), not which row said it",
     expected={"reply": "widening", "member_K": "in"},
     needed="for re-use after a removal: a head link both ways (the removal names the seating it ends; a "
            "re-admission names the removal). The duplicate itself needs nothing",
     variants=[("removed, then a second inviter re-seats on the spent acceptance without naming the removal",
                [p, a, w, x, w3], {"reply": "widening", "member_K": "conflict"}),
               ("removed, then re-seated on the spent acceptance naming the removal",
                [p, a, w, x, w5], {"reply": "widening", "member_K": "out"}),
               ("removed, then re-admitted on a new acceptance, naming the removal",
                [p, a, w, x, p2, a2, w4], {"reply": "widening", "member_K": "in"}),
               ("removed, then re-admitted on a new acceptance, not naming the removal",
                [p, a, w, x, p2, a2, w4b], {"reply": "widening", "member_K": "conflict"})],
     adversaries=[
         ("name an old head: a second inviter re-uses the spent acceptance after K's removal",
          [p, a, w, x], [p, a, w, x, w3],
          lambda b, a_: "K is not seated either way (member_K %s -> %s); the removal now reads as contested, not as landed" % (b["member_K"], a_["member_K"])),
     ])


# ---- W7 roster fork ---------------------------------------------------------------------------------------
BOUNDS = {"add": ("grow_signed", "members"), "drop": ("drop_only", "members"), "protocol": ("any", "protocol")}


def members_of(rows):
    g = [q for q in K.sel(rows, kind="roster") if not q["names"]]
    if not g:
        return frozenset()
    m = set(g[0]["members"])
    for v in K.sel(rows, kind="roster"):
        m |= set(v.get("change", {}).get("add", ()))
    for v in K.sel(rows, kind="roster"):
        m -= set(v.get("change", {}).get("drop", ()))
    return frozenset(m)


def w7_rule(r, P, past):
    if r["kind"] == "roster" and r["names"]:
        mem = members_of(P)                        # counted over the roster of the head it names
        voices = [q for q in K.sel(P, kind="cosign") if q["id"] in r["names"] and q["signer"] in mem] + [r]
        return r["signer"] in mem and K.group(voices, None, "count", "signer") >= r.get("need", 1)
    return True


def w7_ans(S):
    g = [q for q in K.sel(S.Cs, kind="roster") if not q["names"]][0]
    vs = [v for v in K.sel(S.Cs, kind="roster") if v["names"] and CK.counts(S, v)]
    st, cf = CK.merge(S, vs, {"members": frozenset(g["members"]), "protocol": g["protocol"]}, BOUNDS)
    out = {"members": sorted(st["members"]), "protocol": st["protocol"], "conflict": sorted(cf)}
    for pr in K.sel(S.Cs, kind="proposal"):
        mem = members_of([S.by[i] for i in S.anc[pr["id"]] if S.C[i]])
        out["tally"] = CK.tally(S, pr, mem)
        out["tally_if_removal_did_not_reach"] = CK.tally(S, pr, mem, counting=lambda v: True)
    return out


h0 = R("h0", "roster", "f1", members=("f1", "f2", "m3"), protocol="majority")
v1 = R("v1", "roster", "f1", ("h0",), change={"drop": ("m3",), "protocol": "unanimous"}, removes="m3")
v2 = R("v2", "roster", "f2", ("h0",), change={"add": ("m4",), "protocol": "quorum2"})
v1b = R("v1", "roster", "f1", ("h0",), change={"drop": ("m3",)}, removes="m3")
v3 = R("v3", "roster", "m3", ("h0",), change={"drop": ("f1",)}, removes="f1")
cs = R("cs", "cosign", "f2", ("h0",))
v1q = R("v1", "roster", "f1", ("h0", "cs"), change={"drop": ("m3",)}, removes="m3", need=2)
v3q = R("v3", "roster", "m3", ("h0",), change={"drop": ("f1",)}, removes="f1", need=2)
prop = R("prop", "proposal", "f2", ("v2",))
vote3 = R("vote3", "vote", "m3", ("prop",), choice="yes")
case(id="W7", rule=w7_rule, answer=w7_ans, rows=[h0, v1, v2],
     note="two versions name one head: one drops m3 and changes the protocol, the other adds m4 and changes "
          "the protocol differently; a version is concluded when its signer is on the roster of its own past "
          "(one signature is taken as the count); the state is the merge by the declared bounds",
     expected={"members": ["f1", "f2", "m4"], "protocol": "majority", "conflict": ["protocol"]},
     needed="a merge function (not among the kernel's functions, added). The head link exists today",
     adversaries=[
         ("name an old head: the removed member signs, on the head before its removal, a removal of the member who removed it",
          [h0, v1b], [h0, v1b, v3],
          lambda b, a_: "the removal is undone: members %s -> %s. Each removal is outside the other's past, so neither version counts" % (b["members"], a_["members"])),
         ("the same where a version needs two voices of the roster it names, and the removed member signs alone",
          [h0, cs, v1q], [h0, cs, v1q, v3q],
          lambda b, a_: "nothing: members stay %s; the lone version concludes nothing. It takes a quorum of the old roster" % a_["members"] if a_ == b else "members now %s" % a_["members"]),
         ("the removed member votes on a proposal that names only the other child",
          [h0, v1, v2, prop], [h0, v1, v2, prop, vote3],
          lambda b, a_: "nothing under removal by causal past: tally %d (it would be %d if the removal did not reach rows outside its past)" % (a_["tally"], a_["tally_if_removal_did_not_reach"])),
     ])


# ---- W8 retirement: frozen against a withdrawn decision ---------------------------------------------------
def w8_rule(r, P, past):
    if r["signer"] not in ("agent", "custodian"):
        return False
    if r["kind"] == "decider":
        return bool(K.sel(P, id=r["picks"]))
    if r["kind"] == "withdraw":
        return bool(K.sel(P, id=r["target"]))
    return True


def w8_ans_link(S):
    out = {}
    for dec in K.sel(S.Cs, kind="decided"):
        c = [f for f in K.sel(S.Cs, kind="frozen") if dec["id"] in f["names"]] \
            + K.sel(S.Cs, kind="withdraw", target=dec["id"]) + K.sel(S.Cs, kind="decider", fate=dec["id"])
        out[dec["id"]] = show(CK.slot(S, c, value=lambda r: r["kind"])) if c else "decided"
    return out


def w8_ans_object(S):
    c = K.sel(S.Cs, kind={"frozen", "withdraw", "decider"}, object="agentX")
    return {"agentX": show(CK.slot(S, c, value=lambda r: r["kind"]))}


dec = R("dec", "decided", "agent", object="agentX")
frz = R("frz", "frozen", "agent", ("dec",), object="agentX")
frz0 = R("frz", "frozen", "agent", object="agentX")
wd = R("wd", "withdraw", "agent", ("dec",), target="dec", object="agentX")
dz = R("dz", "decider", "custodian", ("frz", "wd"), picks="frz", fate="dec", object="agentX")
dz2 = R("dz2", "decider", "agent", ("frz", "wd"), picks="wd", fate="dec", object="agentX")
frzX = R("frzX", "frozen", "X", ("dec",), object="agentX")
dec1 = R("dec1", "decided", "agent", object="agentX")
wd1 = R("wd1", "withdraw", "agent", ("dec1",), target="dec1", object="agentX")
dec2 = R("dec2", "decided", "agent", ("wd1",), object="agentX")
frz2 = R("frz", "frozen", "agent", ("dec2",), object="agentX")
case(id="W8", rule=w8_rule, answer=w8_ans_link, rows=[dec, frz, wd],
     note="with the head link the table asks for: the frozen row names the decision; the slot is the fate "
          "of that decision and compares kinds (frozen, withdrawn)",
     expected={"dec": "conflict"},
     needed="a deciding row to end the contest. The head link is needed only when an agent has more than "
            "one decision; the table's three rows give the same answer without it",
     variants=[("as the tables are today: the frozen row names only the agent; slot keyed by the agent",
                [dec, frz0, wd], {"agentX": "conflict"}, w8_ans_object),
               ("two decisions, first withdrawn, second frozen, no link: a conflict that is not one",
                [dec1, wd1, dec2, frz0], {"agentX": "conflict"}, w8_ans_object),
               ("the same with the link", [dec1, wd1, dec2, frz2], {"dec1": "withdraw", "dec2": "frozen"}),
               ("a later row by the same line of signers names both and picks", [dec, frz, wd, dz], {"dec": "frozen"})],
     adversaries=[
         ("duplicate to empty the slot: a second deciding row, signed as if the first had not been seen",
          [dec, frz, wd, dz], [dec, frz, wd, dz, dz2],
          lambda b, a_: "the settled retirement is contested again: %s -> %s. Either key of the line can do this at any later time, and nobody else" % (b["dec"], a_["dec"])),
         ("an outsider signs a frozen row for the decision", [dec, wd], [dec, wd, frzX],
          lambda b, a_: "nothing: %s stays %s" % ("dec", a_["dec"]) if a_ == b else "dec now %s" % a_["dec"]),
     ])


# ---- W9 key grant against retirement ----------------------------------------------------------------------
def w9_rule(r, P, past):
    if r["kind"] == "archive_release":
        return r["signer"] == "custodian"
    return True


def w9_ans(S):
    out = {}
    for g in K.sel(S.Cs, kind="key_grant"):
        rel = any(S.C.get(n) and S.by[n]["kind"] == "archive_release" for n in g["names"])
        out[g["id"]] = "confers" if rel or CK.counts(S, g, key=lambda r: r["object"]) else "does not confer"
    return out


kg = R("kg", "key_grant", "owner", object="agentX", subject="r1")
ret = R("ret", "retired", "agent", object="agentX", removes="agentX")
ret_l = R("ret", "retired", "agent", ("kg",), object="agentX", removes="agentX")
kg2 = R("kg2", "key_grant", "owner", object="agentX", subject="r2")
rel = R("rel", "archive_release", "custodian", ("ret",))
kg3 = R("kg3", "key_grant", "owner", ("rel",), object="agentX", subject="r3")
case(id="W9", rule=w9_rule, answer=w9_ans, rows=[kg, ret],
     note="as the tables are today (the retirement names nothing): the retirement is a removal keyed on the "
          "object, and a grant confers when it is in the retirement's past or names a concluded archive release",
     expected={"kg": "does not confer"},
     needed="for the exact reading (earlier grants stand): a head link, the retirement names the grants it seals",
     variants=[("the retirement names the grant it seals", [kg, ret_l], {"kg": "confers"}),
               ("and a grant the retirement did not name", [kg, ret_l, kg2], {"kg": "confers", "kg2": "does not confer"}),
               ("a grant that names an archive release", [kg, ret, rel, kg3], {"kg": "does not confer", "kg3": "confers"})],
     adversaries=[
         ("withhold an acknowledgement: the retirement's signer holds an earlier grant and does not name it",
          [kg, ret_l], [kg, ret],
          lambda b, a_: "the earlier grant goes from '%s' to '%s': with the link, the retirement's signer chooses which earlier grants stand" % (b["kg"], a_["kg"])),
     ])


# ---- W10 charter witnesses against members ----------------------------------------------------------------
def w10_ans(S):
    ch = K.sel(S.Cs, kind="charter")
    if not ch:
        return {"charter_kept": False, "member_K": seat(S, "K")}
    voices = sorted(k for k in ch[0]["witnesses"] if seat(S, k) != "in")
    return {"charter_kept": True, "member_K": seat(S, "K"), "witness_voices": voices,
            "witnessed": len(voices) >= ch[0]["quorum"]}


ch = R("ch", "charter", "root", witnesses=("K", "W2"), quorum=2)
pW = R("pW", "proposal", "founder", subject="W2")
wW = R("wW", "widening", "founder", ("pW",), subject="W2", target="pW")
aW = R("aW", "acceptance", "W2", ("pW",), ref="pW", target="pW")
wW2 = R("wW", "widening", "founder", ("aW",), subject="W2", target="pW")
case(id="W10", rule=mem_rule, answer=w10_ans, rows=[p, a, w, ch],
     note="the charter lists K and W2 as witnesses with a quorum of two (the table lists K alone); the "
          "charter names no row and is kept alone; a witness voice is a listed key the roster does not seat",
     expected={"charter_kept": True, "member_K": "in", "witness_voices": ["W2"], "witnessed": False},
     needed="nothing",
     adversaries=[
         ("the group seats the other witness without that witness's acceptance", [p, a, w, ch], [p, a, w, ch, pW, wW],
          lambda b, a_: "nothing: witness voices stay %s" % a_["witness_voices"] if a_ == b else "witness voices now %s" % a_["witness_voices"]),
         ("the group seats the other witness with its signed acceptance", [p, a, w, ch], [p, a, w, ch, pW, aW, wW2],
          lambda b, a_: "witness voices %s -> %s; it took the witness's own signature" % (b["witness_voices"], a_["witness_voices"])),
     ])


# ---- W11 transport rotation against a serve seat ----------------------------------------------------------
def w11_rule(r, P, past):
    if r["kind"] == "rebind":
        return r["signer"] == "holders" and bool(K.sel(P, id=r["transport"]))
    if r["kind"] == "transport" and r["names"]:
        return bool(K.sel(P, id=r["target"], signer=r["signer"]))
    return True


def w11_ans(S):
    seats = K.sel(S.Cs, kind="confers", to="N")
    head = show(CK.slot(S, K.sel(S.Cs, kind="transport", signer="N")))
    if not seats:
        return {"seated": False, "in_force": head}
    c = K.sel(S.Cs, kind="rebind", node="N") + [s for s in seats if s.get("transport")]
    return {"seated": True, "in_force": show(CK.slot(S, c, value=lambda r: r["transport"])), "own_chain_head": head}


t0 = R("t0", "transport", "N")
rep = R("rep", "transport", "N", ("t0",), target="t0")
seat_row = R("seat", "confers", "root", to="N")
seat_l = R("seat", "confers", "root", ("t0",), to="N", transport="t0")
rb = R("rb", "rebind", "holders", ("seat", "rep"), node="N", transport="rep")
case(id="W11", rule=w11_rule, answer=w11_ans, rows=[t0, rep, seat_row],
     note="as the tables are today (the seating names no transport row): for a seated key the pair in force "
          "is the one a concluded rebind names, and nothing until there is one",
     expected={"seated": True, "in_force": "empty", "own_chain_head": "rep"},
     needed="for the exact reading: a head link, the seating names the transport row in force",
     variants=[("the seating names the transport row in force", [t0, rep, seat_l],
                {"seated": True, "in_force": "t0", "own_chain_head": "rep"}),
               ("then a rebind names the seating and the replacement", [t0, rep, seat_l, rb],
                {"seated": True, "in_force": "rep", "own_chain_head": "rep"}),
               ("not seated: the node's own chain decides", [t0, rep], {"seated": False, "in_force": "rep"})],
     adversaries=[
         ("name an old head: the conferrer's seating names the pair the node had already replaced",
          [t0, rep], [t0, rep, seat_l],
          lambda b, a_: "the pair in force goes from %s back to %s until the holders cosign a rebind; the rows cannot say whether the replacement came before the seating or after" % (b["in_force"], a_["in_force"])),
     ])


# ---- G1 two ways out of admitted --------------------------------------------------------------------------
LAB = {"recant": 3, "withdraw": 2, "replace": 1}
OUT = {"recant": "recanted", "withdraw": "withdrawn", "replace": "superseded"}


def g1_rule(r, P, past):
    if r["kind"] in LAB:
        return bool(K.sel(P, id=r["target"], signer=r["signer"]))
    return True


def g1_ans(S):
    on = CK.wins(S, K.sel(S.Cs, target="r"), lambda r: LAB[r["kind"]])
    if not on:
        return {"r": "admitted"}
    out = {"r": OUT[on[0]["kind"]]}
    if on[0]["kind"] == "replace":
        out["successor"] = show(CK.slot(S, on))
    return out


r0 = R("r", "msg", "K1")
g_wd = R("wd", "withdraw", "K1", ("r",), target="r")
g_sup = R("sup", "replace", "K1", ("r",), target="r")
g_sup2 = R("sup2", "replace", "K1", ("r",), target="r")
g_sup2n = R("sup2", "replace", "K1", ("r", "sup"), target="r")
g_wdX = R("wdX", "withdraw", "K2", ("r",), target="r")
case(id="G1", rule=g1_rule, answer=g1_ans, rows=[r0, g_wd, g_sup],
     note="each composer names its target; a composer is concluded when its signer signed the target; "
          "wins with recant > withdraw > replace",
     expected={"r": "withdrawn"},
     needed="nothing for two kinds. For two of one kind by one signer the table ranks by that signer's "
            "signed instants; this kernel has none, so the second must name the first",
     variants=[("two replacements by one signer, neither names the other", [r0, g_sup, g_sup2],
                {"r": "superseded", "successor": "conflict"}),
               ("the second replacement names the first", [r0, g_sup, g_sup2n], {"r": "superseded", "successor": "sup2"})],
     adversaries=[
         ("another key signs a withdrawal of K1's row", [r0, g_sup], [r0, g_sup, g_wdX],
          lambda b, a_: "nothing: r stays %s" % a_["r"] if a_ == b else "r now %s" % a_["r"]),
         ("duplicate to empty the slot: K1 signs a second replacement that does not name the first",
          [r0, g_sup], [r0, g_sup, g_sup2],
          lambda b, a_: "K1 empties the successor of its own row: %s -> %s" % (b["successor"], a_["successor"])),
     ])


# ---- G2 a row it must find --------------------------------------------------------------------------------
def consent_for(rows, s):
    return K.sel(rows, kind="consent", signer=s["attested"], subject=s["signer"], scope="analyze")


def g2_rule(r, P, past):
    if r["kind"] == "score" and r["names"]:
        return bool(consent_for(P, r))
    return True


def g2_ans(S):
    out = {"kept": sorted(S.by)}
    sc = K.sel(S.rows, kind="score")
    if not sc:
        out["score"] = "not kept: it waits for the row it names"
    elif sc[0]["names"]:
        out["score"] = "stands" if S.C[sc[0]["id"]] else "concludes nothing"
    else:   # no digest link: the join is made in the derived layer, over the set
        live = [c for c in consent_for(S.Cs, sc[0])
                if not [x for x in K.sel(S.Cs, kind="withdraw", signer=c["signer"]) if c["id"] in x["names"]]]
        out["score"] = "stands" if live else "inert"
    return out


consent = R("consent", "consent", "node1", subject="scorer", scope="analyze")
score = R("score", "score", "scorer", ("consent",), attested="node1")
score0 = R("score", "score", "scorer", attested="node1")
wdc = R("wdc", "withdraw", "node1", ("consent",))
case(id="G2", rule=g2_rule, answer=g2_ans, rows=[consent, score],
     note="the score names the consent it relies on by digest, so the door holds it until the consent is kept",
     expected={"kept": ["consent", "score"], "score": "stands"},
     needed="the reference as a digest if the door is to do the waiting; without it the join moves to the derived layer",
     variants=[("as today, the guard joins on fields and no digest is named: the join is derived", [consent, score0],
                {"kept": ["consent", "score"], "score": "stands"}),
               ("digest link, and the consent is withdrawn later: the conclusion is final", [consent, score, wdc],
                {"kept": ["consent", "score", "wdc"], "score": "stands"}),
               ("no link, and the consent is withdrawn later: the derived join lets go", [consent, score0, wdc],
                {"kept": ["consent", "score", "wdc"], "score": "inert"})],
     adversaries=[
         ("withhold the row: the consent is never offered to this node", [consent, score], [score],
          lambda b, a_: "nothing is concluded from the score at that node (%s); no wrong conclusion, and no end to the wait" % a_["score"]),
     ])


# ---- G3 standing under a delegation that is later withdrawn ----------------------------------------------
def g3_rule(r, P, past):
    if r["kind"] == "act" and r["names"]:
        for e in K.sel(P, kind="edge", to=r["signer"]):
            if e["id"] in r["names"] and not [x for x in K.sel(P, kind="withdraw", signer=e["signer"]) if e["id"] in x["names"]]:
                return True
        return False
    return True


def g3_ans(S):
    out = {}
    for a_ in K.sel(S.rows, kind="act"):
        out[a_["id"]] = "concluded=%s counts=%s means_to_reader=%s" % (
            S.C[a_["id"]], CK.counts(S, a_), CK.means(S, a_, "root", 1))
    return out


dele = R("del", "edge", "root", to="mod")
act = R("act", "act", "mod", ("del",))
act0 = R("act", "act", "mod")
xdel = R("xdel", "withdraw", "root", ("del", "act"), removes="mod")
xdel1 = R("xdel", "withdraw", "root", ("del",), removes="mod")
xdel0 = R("xdel", "withdraw", "root", ("del",))
act2 = R("act2", "act", "mod", ("del",))
case(id="G3", rule=g3_rule, answer=g3_ans, rows=[dele, act, xdel],
     note="with the links the table asks for: the act names the grant; the withdrawal names the grant and the "
          "delegate's last act it lets stand, and is read both as a withdrawal of the edge (reach) and as a "
          "removal of the delegate (counts). The reader's own key is the conferrer's",
     expected={"act": "concluded=True counts=True means_to_reader=True"},
     match=lambda ans: "partly: the act stands by `counts` and is void by `means`" if ans == {"act": "concluded=True counts=True means_to_reader=False"} else "no",
     needed="a head link both ways (the act names the grant; the withdrawal names what it lets stand), and a "
            "statement of which of the kernel's two endings governs a delegated seat",
     variants=[("as the tables are today, no links: a withdrawal voids every act under the grant", [dele, act0, xdel0],
                {"act": "concluded=True counts=True means_to_reader=False"}),
               ("the act names the grant, the withdrawal does not name the act", [dele, act, xdel1],
                {"act": "concluded=True counts=False means_to_reader=False"})],
     adversaries=[
         ("withhold an acknowledgement: the conferrer holds the delegate's act and does not name it in the withdrawal",
          [dele, act, xdel], [dele, act, xdel1],
          lambda b, a_: "the act goes from [%s] to [%s]: the conferrer voids any past act it chooses" % (b["act"], a_["act"])),
         ("name an old head: the withdrawn delegate signs a new act that names only the grant", [dele, act, xdel], [dele, act, xdel, act2],
          lambda b, a_: "the new act is concluded but does not count [%s]; nothing gained where `counts` is read" % a_["act2"]),
     ])


# ---- C1 self-roster eviction with a silence window --------------------------------------------------------
def c1_rule(r, P, past):
    ks = K.sel(P, kind="keyset")
    return r["kind"] == "keyset" or (bool(ks) and r["signer"] in ks[0]["members"])


def c1_ans(S):
    out = {}
    for e in K.sel(S.Cs, kind="evict"):
        if [o for o in K.sel(S.Cs, signer=e["removes"]) if e["id"] in o["names"]]:
            out[e["id"]] = "cancelled"
        elif not CK.counts(S, e):
            out[e["id"]] = "void: crossed by an eviction of its signer"
        else:
            out[e["id"]] = "pending: no row closes the window"
    return out


ros = R("ros", "keyset", "K1", members=("K1", "K2"))
ev = R("e", "evict", "K1", ("ros",), removes="K2")
xk = R("x", "note", "K2", ("ros",))
xo = R("x", "note", "K2", ("ros", "e"))
ev2 = R("e2", "evict", "K2", ("ros",), removes="K1")
case(id="C1", rule=c1_rule, answer=c1_ans, rows=[ros, ev, xk],
     note="the proposal names the key set it counts over; the target's row names the key set and not the "
          "proposal (the table says only 'any row signed by K2')",
     expected={"e": "pending: no row closes the window"},
     verdict="NOT EXPRESSIBLE WITHOUT a clock",
     needed="a clock, or a signed row that closes the window: the landing of an unopposed eviction is "
            "silence over time. The head link (proposal names the key set) is needed for the count",
     variants=[("the target's row names the proposal: an objection", [ros, ev, xo], {"e": "cancelled"}),
               ("crossing evictions that name one key set", [ros, ev, ev2],
                {"e": "void: crossed by an eviction of its signer", "e2": "void: crossed by an eviction of its signer"}),
               ("unopposed", [ros, ev], {"e": "pending: no row closes the window"})],
     adversaries=[
         ("a stolen key objects, naming the proposal", [ros, ev], [ros, ev, xo],
          lambda b, a_: "the eviction goes from '%s' to '%s', at any time: a veto with no end" % (b["e"], a_["e"])),
         ("name an old head: the target signs a crossing eviction on the same key set", [ros, ev], [ros, ev, ev2],
          lambda b, a_: "the eviction goes from '%s' to '%s', at any time" % (b["e"], a_["e"])),
     ])


# ---- C2 halt, confirmation, fuse --------------------------------------------------------------------------
def c2_rule(r, P, past):
    ks = K.sel(P, kind="keyset")
    return r["kind"] == "keyset" or (bool(ks) and r["signer"] in ks[0]["members"])


def c2_ans(S):
    h = K.sel(S.Cs, kind="halt")
    if not h:
        return {"halt": "none held"}
    mem = K.sel(S.Cs, kind="keyset")[0]["members"]
    n = CK.tally(S, h[0], mem, kind="confirm")
    return {"halt": "confirmed" if 2 * n > len(mem) else "in force or lapsed by each node's fuse: not a conclusion from rows",
            "confirming_voices": n}


hol = R("hol", "keyset", "h1", members=("h1", "h2", "h3"))
halt = R("h", "halt", "h1", ("hol",))
cf1 = R("cf1", "confirm", "h1", ("h",), choice="yes")
cf2 = R("cf2", "confirm", "h2", ("h",), choice="yes")
case(id="C2", rule=c2_rule, answer=c2_ans, rows=[hol, halt, cf1, cf2],
     note="the halt names the holders' key set; the confirmation is two rows by two of three holders, each "
          "naming the halt (the table has one cosigned row); confirmed is a tally over the named key set",
     expected={"halt": "confirmed", "confirming_voices": 2},
     verdict="ONE RESULT for the confirmation; the unconfirmed halt is NOT EXPRESSIBLE WITHOUT a clock",
     needed="a clock for the fuse of an unconfirmed halt; nothing for the confirmation",
     variants=[("the halt alone", [hol, halt],
                {"halt": "in force or lapsed by each node's fuse: not a conclusion from rows", "confirming_voices": 0}),
               ("one confirming voice of three", [hol, halt, cf1],
                {"halt": "in force or lapsed by each node's fuse: not a conclusion from rows", "confirming_voices": 1})],
     adversaries=[
         ("withhold an acknowledgement: the confirmation is kept from a node", [hol, halt, cf1, cf2], [hol, halt],
          lambda b, a_: "that node reads '%s' until it holds the confirmation, then '%s': a delay, at any length" % (a_["halt"], b["halt"])),
     ])


# ---- T1 delegation cycle ----------------------------------------------------------------------------------
def t1_ans(S):
    return {"kept": sorted(S.by), "concluded": sorted(r["id"] for r in S.Cs),
            "standing": sorted(CK.reach(S, "root", 3) - {"root"})}


d0 = R("d0", "edge", "root", to="A")
d1 = R("d1", "edge", "A", to="B")
d2 = R("d2", "edge", "B", to="A")
case(id="T1", rule=lambda r, P, past: True, answer=t1_ans, rows=[d0, d1, d2],
     note="a root edge to A is added (the table has only the two edges of the cycle); standing is the "
          "bounded walk from the root",
     expected={"kept": ["d0", "d1", "d2"], "concluded": ["d0", "d1", "d2"], "standing": ["A", "B"]},
     needed="nothing",
     variants=[("the cycle with no edge from the root", [d1, d2], {"kept": ["d1", "d2"], "concluded": ["d1", "d2"], "standing": []})],
     adversaries=[
         ("the delegate delegates back to its delegator", [d0, d1], [d0, d1, d2],
          lambda b, a_: "nothing: standing stays %s; no edge is refused and none is cut" % a_["standing"] if a_["standing"] == b["standing"] else "standing now %s" % a_["standing"]),
     ])

ORDER = ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9", "W10", "W11", "T1", "G1", "G2", "G3", "C1", "C2"]
CASES.sort(key=lambda c: ORDER.index(c["id"]))

# Where a run contradicts the table beyond the main outcome (its cost column, or a sub-case). Each line is
# backed by an adversary or variant run above; check.py appends it to `matches_reasoned`.
DIFFERS = {
    "W1": "the table says no two valid composites can differ; with a second partial two composites both recompute and the census is empty",
    "W5": "the table gives the cost as none; the inviter chooses whether K's decline is read, by naming it or not",
    "W7": "the table says a member removed in one child keeps its voice on the other child; under removal by causal past it does not. "
          "Not in the table: where one signature makes a version, the removed member undoes its removal from the old head",
    "W11": "with the head link the conferrer picks the pair in force; the rows do not tell a replacement signed before the seating from one signed after",
    "G1": "for two of one kind by one signer the table ranks by that signer's signed instants; here they are a conflict until one names the other",
}
