#!/usr/bin/env python3
"""
check_admission.py: the one admission of CC 2.7.11 run over small worlds (admission.py).

A host owned by a person, an issuer the owner accepts for admission, a stranger, an agent the owner also accepts,
a reviewing group of three, the accord's three holders, an agent with a steward and a seated Wise Authority, and
the rows each case adds. Every case's expected answer is written here from how the world was made, never by the
model, and the model must give it.

Sections, each compared with admission_expected.tsv:
    property   P1 to P14: the cases of each, and the planted breaks of each. Every break must change the answer
               of at least one case of its own property.
    count      the size of the run.

    python3 -I check_admission.py           compare with admission_expected.tsv; exit 1 on a difference or an uncaught plant
    python3 -I check_admission.py --write   write admission_expected.tsv
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import admission as A  # noqa: E402

ORDERS = 12
NOW = 10
_n = [0]


def r(kind, t=0, **f):
    _n[0] += 1
    f.setdefault("id", f"{kind}{_n[0]}")
    return dict(kind=kind, t=t, **f)


def key(who, typ): return r("key", who=who, type=typ, id=f"k_{who}")
def edge(by, to, classes=("admission",), t=0): return r("edge", by=by, to=to, classes=frozenset(classes), t=t)
def stmt(of, by, t=0): return r("stmt", of=of, by=by, t=t)


KEYS = [key(w, "person") for w in ("owner", "iss", "stranger", "far", "m1", "m2", "m3", "h1", "h2", "h3",
                                     "owner2", "steward", "wa", "other")] + \
       [key(w, "program") for w in ("agent", "node", "bot")]
BASE = KEYS + [r("owns", host="hA", owner="owner"), r("owns", host="hB", owner="owner2"),
               edge("owner", "iss"), edge("owner", "bot"), edge("bot", "far"), edge("owner", "G"),
               edge("owner", "accord", ("halt",)), edge("owner", "stranger", ("licence",)),
               r("roster", id="G1", group="G", members=frozenset({"m1", "m2", "m3"}), need=2),
               r("roster", id="G1b", group="G", members=frozenset({"m1", "m2", "m3"}), need=1),
               r("bundle", id="B", holders=frozenset({"h1", "h2", "h3"})),
               r("bind", agent="ag", steward="steward"), r("seat", agent="ag", wa="wa", by="steward"),
               r("template", agent="ag", digest="b", attested=True)]
COMPUTE, NET = frozenset({"compute"}), frozenset({"compute", "net_send"})


def authored(rid, by="iss", unit="d1", caps=COMPUTE, at=0, until=20, t=0, signer=None, scope="federation"):
    return [r("unit", id=rid, unit=unit, caps=caps, at=at, until=until, author=by, scope=scope, t=t), stmt(rid, signer or by, t)]


def counted(rid, voters=("m1", "m2"), unit="d1", caps=NET, at=0, until=20, head="G1", t=0, scope="federation"):
    return [r("unit", id=rid, unit=unit, caps=caps, at=at, until=until, head=head, scope=scope, t=t)] + \
           [stmt(rid, v, t) for v in voters]


def adm(R, digest="d1", host="hA", now=NOW): return A.admit(BASE + R, host, digest, now)
def runs(R, **k): return adm(R, **k)[0] == "admit"
def eff(R, cap="net_send", now=NOW, parent=None, host="hA"):
    return A.may(BASE + R, host, "d1", cap, now, parent)


def halt(by="h1", t=5): return [r("halt", id="H", by=by, t=t)]
def life(what, voters, t=6):
    rid = f"L_{what}_{'_'.join(voters)}"
    return [r("life", id=rid, of="H", what=what, t=t)] + [stmt(rid, v, t) for v in voters]


GOOD = authored("s1")
NETOK = counted("c1")
AMEND = [r("resp", id="ra0", agent="ag", outcome="approved", by="wa", digest="b"),
         r("amend", id="a0", agent="ag", digest="b", by_resp="ra0"),
         r("resp", id="ra1", agent="ag", outcome="approved", by="steward", digest="z1"),
         r("amend", id="a1", agent="ag", digest="z1", prev="a0", by_resp="ra1"),
         r("resp", id="ra2", agent="ag", outcome="approved", by="wa", digest="a2"),
         r("amend", id="a2", agent="ag", digest="a2", prev="a1", by_resp="ra2")]
CALL = dict(verb="tool", tool="http_get", args={"url": "https://example.org", "token": "{SECRET:k1}"}, channel="c")
FP = A.fingerprint(CALL)
FOUR = A.FACULTIES


def review(fp=FP, thought="th", outcome="passed", faculties=FOUR, discharges=(), considered=(), derived_from=(), rid=None):
    return r("review", id=rid or f"rv_{outcome}_{fp}_{len(discharges)}_{len(considered)}", fp=fp, thought=thought,
             outcome=outcome, faculties=frozenset(faculties), discharges=frozenset(discharges),
             considered=frozenset(considered), derived_from=frozenset(derived_from))


def disp(R, call=CALL, thought="th", **k): return A.may_dispatch(BASE + R, thought, call, **k)


def cases():
    """{property: {case: bool}}. Each bool is the case's expected answer compared with the model's."""
    P = {}
    # Inv_NothingRunsUnadmitted
    P["P1 nothing runs without an admitted digest"] = {
        "a unit with no row does not run": adm([]) == ("refuse", "admission_none"),
        "a statement by an issuer the owner reaches runs": runs(GOOD),
        "a valid statement by a stranger does not run": adm(authored("s1", by="stranger")) == ("refuse", "admission_issuer_not_reached"),
        "an issuer the other host's owner does not reach": not runs(GOOD, host="hB"),
        "a host with no owner-binding runs nothing": not runs(GOOD, host="hZ"),
    }
    # Inv_ChangedUnitUnadmitted
    P["P2 a changed unit has no admission"] = {
        "another digest under the same statement does not run": adm(GOOD, digest="d2") == ("refuse", "admission_none"),
        "the admitted digest runs": runs(GOOD, digest="d1"),
    }
    # Inv_ProgramAdmitsNothing
    P["P3 a program's key admits nothing"] = {
        "a statement by an agent the owner accepts": adm(authored("s1", by="bot")) == ("refuse", "admission_issuer_not_person"),
        "a statement by a node key": adm(authored("s1", by="node")) == ("refuse", "admission_issuer_not_person"),
        "an issuer reached only through a program": adm(authored("s1", by="far")) == ("refuse", "admission_issuer_not_reached"),
        "a program's voice is not counted": adm(counted("c1", voters=("m1", "bot"))) == ("waiting", "admission_count_unmet"),
    }
    owner_net = authored("s9", by="owner", caps=NET, scope="self")
    # Inv_EffectNeedsCount
    P["P4 an effect-capable unit needs the count, or the host's own owner on that host"] = {
        "the host's owner admits an effect alone on the host": adm(owner_net)[0] == "admit",
        "the same row on another host admits nothing": adm(owner_net + [edge("owner2", "owner")], host="hB") == ("refuse", "admission_issuer_not_reached"),
        "one person the owner reaches does not admit an effect": adm(authored("s1", caps=NET, scope="self")) == ("refuse", "admission_issuer_not_reached"),
        "the owner's own effect row at any scope but self is Invalid": adm(authored("s9", by="owner", caps=NET, scope="federation")) == ("refuse", "admission_owner_row_not_self"),
        "a counted row published at federation scope admits": adm(counted("c1", scope="federation"))[0] == "admit",
        "two members of the head admit an effect": adm(NETOK)[0] == "admit" and "net_send" in adm(NETOK)[1],
        "one member is not a count": adm(counted("c1", voters=("m1",))) == ("waiting", "admission_count_unmet"),
        "a group declaring one voice still needs two": adm(counted("c1", voters=("m1",), head="G1b")) == ("waiting", "admission_count_unmet"),
        "voices outside the head are not counted": adm(counted("c1", voters=("m1", "stranger"))) == ("waiting", "admission_count_unmet"),
        "a head not held waits": adm(counted("c1", head="G9")) == ("waiting", "head"),
        "a compute-only unit may be one person's": runs(GOOD),
        "a group the host's owner does not reach admits nothing": adm(counted("c1"), host="hB") == ("refuse", "admission_issuer_not_reached"),
    }
    # Inv_LeaseEndsOnHostClock
    P["P5 a lease ends execution on the host's own clock"] = {
        "inside the lease runs": runs(GOOD, now=19),
        "at valid_until it stops": adm(GOOD, now=20) == ("refuse", "admission_lease_ended"),
        "before asserted_at it does not run": adm(authored("s1", at=12, until=30, t=0), now=11) == ("refuse", "admission_lease_ended"),
        "a lease over 24 hours is Invalid": adm(authored("s1", until=25)) == ("refuse", "admission_lease_out_of_window"),
        "a statement held 24 hours ends though its own end is later": adm(authored("s1", at=20, until=40, t=0), now=24) == ("refuse", "admission_lease_ended"),
        "a renewal for the same digest continues it": runs(GOOD + authored("s2", at=18, until=40, t=18), now=30),
        "with no renewal, silence ends it": adm(GOOD, now=30) == ("refuse", "admission_lease_ended"),
    }
    # Inv_WithdrawalEndsForward
    P["P6 a withdrawal ends it forward"] = {
        "the author's withdrawal ends it": adm(GOOD + [r("withdraw", id="w1", of="s1", t=8), stmt("w1", "iss", 8)]) == ("refuse", "admission_withdrawn"),
        "it ran before the withdrawal was held": runs(GOOD + [r("withdraw", id="w1", of="s1", t=8), stmt("w1", "iss", 8)], now=7),
        "a stranger's withdrawal ends nothing": runs(GOOD + [r("withdraw", id="w1", of="s1", t=8), stmt("w1", "stranger", 8)]),
        "a counted admission is withdrawn by the count": adm(NETOK + [r("withdraw", id="w2", of="c1", head="G1", t=8), stmt("w2", "m1", 8), stmt("w2", "m3", 8)]) == ("refuse", "admission_withdrawn"),
        "one voice does not withdraw a count": runs(NETOK + [r("withdraw", id="w2", of="c1", head="G1", t=8), stmt("w2", "m1", 8)]),
    }
    # Inv_HaltStopsEffects
    P["P7 a halt stops every effect from receipt"] = {
        "before the halt the effect is permitted": eff(NETOK + halt(), now=4) == (True, None),
        "from receipt no effect": eff(NETOK + halt(), now=5) == (False, "admission_halted"),
        "computing continues under the halt": eff(NETOK + halt(), cap="compute", now=6) == (True, None),
        "a stranger's halt stops nothing": eff(NETOK + halt(by="stranger")) == (True, None),
        "a lone halt lapses at its fuse": eff(counted("c1", until=34, at=10, t=10) + halt(), now=29) == (True, None),
        "a confirmed halt outlasts the fuse": eff(counted("c1", until=34, at=10, t=10) + halt() + life("confirm", ("h1", "h2")), now=29) == (False, "admission_halted"),
        "one holder does not resume": eff(NETOK + halt() + life("resume", ("h2",))) == (False, "admission_halted"),
        "a majority resumes": eff(NETOK + halt() + life("resume", ("h2", "h3"))) == (True, None),
        "programs do not resume": eff(NETOK + halt() + life("resume", ("agent", "bot"))) == (False, "admission_halted"),
        "a unit of the build is halted too": A.may(BASE + [r("build", units=frozenset({"d1"}), blessed=True)] + halt(), "hA", "d1", "net_send", NOW) == (False, "admission_halted"),
    }
    # Inv_CapabilitiesAttenuate
    P["P8 capabilities only attenuate"] = {
        "a child with a capability its parent lacks": eff(NETOK, parent=COMPUTE) == (False, "admission_capability_not_held"),
        "a child within its parent": eff(NETOK, parent=NET) == (True, None),
        "a capability no row admits": eff(NETOK, cap="actuate") == (False, "admission_capability_not_admitted"),
        "a submitted unit runs only by the receiver's own admission": A.submit(BASE + NETOK, "hA", "hB", "d1", NOW) is False,
        "the receiver's own admission runs it": A.submit(BASE + NETOK + [edge("owner2", "G")], "hA", "hB", "d1", NOW) is True,
    }
    other = A.fingerprint(dict(CALL, args={"url": "https://example.org/a", "token": "{SECRET:k1}"}))
    obj_same = review(outcome="objected", faculties={"entropy"}, rid="o1")
    obj_other = review(fp=other, outcome="objected", faculties={"optimization_veto"}, rid="o2")
    grant = r("resp", id="g1", agent="ag", outcome="approved", by="wa")
    bad_grant = r("resp", id="g2", agent="ag", outcome="approved", by="bot")
    changed = dict(CALL, args={"url": "https://example.org/other", "token": "{SECRET:k1}"})
    passed = review()
    # Inv_DispatchOnlyReviewed
    P["P9 dispatch executes only the reviewed fingerprint"] = {
        "four passes over the fingerprint dispatch": disp([passed]) == (True, None),
        "no record, no dispatch": disp([]) == (False, "action_not_reviewed"),
        "three of four is not a pass": disp([review(faculties=sorted(FOUR)[:3])]) == (False, "action_review_incomplete"),
        "a changed call is another fingerprint": disp([passed], call=changed, reviewed_fp=FP) == (False, "action_not_reviewed"),
        "a record of another thought": disp([passed], thought="other") == (False, "action_not_reviewed"),
        "an objection to this draft, undischarged, blocks it": disp([obj_same, passed]) == (False, "action_objection_undischarged"),
        "discharged by the drafter's own word": disp([obj_same, bad_grant, review(discharges=[("o1", "g2")])]) == (False, "action_objection_undischarged"),
        "discharged by a seated person's row": disp([obj_same, grant, review(discharges=[("o1", "g1")])]) == (True, None),
        "an objection to another draft, carried as considered, does not block a new draft": disp([obj_other, review(considered=["o2"])]) == (True, None),
        "an objection to another draft not carried into the review": disp([obj_other, passed]) == (False, "action_objection_not_carried"),
        "an approved call runs only as approved": disp([passed, r("resp", id="g3", agent="ag", outcome="approved", by="wa", fp="other")], call=dict(CALL, approved_by="g3")) == (False, "action_approval_mismatch"),
        "the approved fingerprint runs": disp([passed, r("resp", id="g4", agent="ag", outcome="approved", by="wa", fp=FP)], call=dict(CALL, approved_by="g4")) == (True, None),
    }
    fork = [r("resp", id="ra3", agent="ag", outcome="approved", by="wa", digest="x3"),
            r("amend", id="a3", agent="ag", digest="x3", prev="a1", by_resp="ra3")]
    orphan = [r("resp", id="ro", agent="ag", outcome="approved", by="wa", digest="x7"),
              r("amend", id="ao", agent="ag", digest="x7", by_resp="ro")]
    # Inv_ProfileDigestMatches
    P["P10 a profile loads only when its derived digest matches"] = {
        "the base and two amendments in their order load": A.may_load(BASE + AMEND, "ag", ["b", "z1", "a2"]),
        "the same digests in another order do not": not A.may_load(BASE + AMEND, "ag", ["b", "a2", "z1"]),
        "an unapproved amendment does not": not A.may_load(BASE + AMEND, "ag", ["b", "z1", "a2", "x9"]),
        "an amendment approved by the agent's own key does not count": not A.may_load(
            BASE + AMEND + [r("resp", id="rb", agent="ag", outcome="approved", by="agent", digest="x9"),
                            r("amend", id="a9", agent="ag", digest="x9", prev="a2", by_resp="rb")], "ag", ["b", "z1", "a2", "x9"]),
        "a fork counts neither branch": not A.may_load(BASE + AMEND + fork, "ag", ["b", "z1", "a2"])
                                        and A.may_load(BASE + AMEND + fork, "ag", ["b", "z1"]),
        "with no base link the template alone loads, unanchored": A.load(BASE, "ag", ["b"]) == (True, "profile_unanchored"),
        "with no base link an approved amendment counts for nothing": A.load(BASE + orphan, "ag", ["b", "x7"]) == (False, "profile_unanchored")
                                                                    and A.load(BASE + orphan, "ag", ["b"]) == (True, "profile_unanchored"),
        "with no attested template nothing loads": not A.may_load([k for k in BASE if k["kind"] != "template"], "ag", ["b"]),
        "a base link approved by a program's key does not anchor": A.load(BASE + [r("resp", id="rp", agent="ag", outcome="approved", by="bot", digest="b"),
                                                                              r("amend", id="ap", agent="ag", digest="b", by_resp="rp")], "ag", ["b"]) == (True, "profile_unanchored"),
        "a base link a seated person approved anchors": A.load(BASE + AMEND[:2], "ag", ["b"]) == (True, None),
        "an approval of another digest anchors nothing": A.load(BASE + [r("resp", id="rq", agent="ag", outcome="approved", by="wa", digest="other"),
                                                                       r("amend", id="aq", agent="ag", digest="b", by_resp="rq")], "ag", ["b"]) == (True, "profile_unanchored"),
    }
    U = lambda i, trust, label, *names: r("data", id=i, trust=trust, label=label, names=list(names))
    dR = [U("req", A.UNTRUSTED, "request"), U("rule", A.VERIFIED, "rule"), U("args", A.VERIFIED, "draft", "req"),
          U("args2", A.VERIFIED, "draft", "rule")]
    E = lambda extra, args="args", **k: A.may_effect(BASE + dR + extra, "th", FP, args, **k)
    # Inv_DerivedTrustLeast
    P["P11 a result is no more trusted than what it derives from"] = {
        "arguments built from a request are untrusted": A.trust_of(dR, "args") == A.UNTRUSTED,
        "arguments built from a signed rule keep its trust": A.trust_of(dR, "args2") == A.VERIFIED,
        "a review that does not declare the derivation does not license the effect": E([review()]) == (False, "effect_untrusted_unacknowledged"),
        "a review that declares it is the review holding the evidence": E([review(derived_from=["request"])]) == (True, None),
        "trusted arguments need no declaration": E([review()], args="args2") == (True, None),
        "an action claiming authority without its approving row": E([review(derived_from=["request"]), r("resp", id="g5", agent="ag", outcome="approved", by="wa", fp="other")], claims="g5") == (False, "effect_untrusted_unacknowledged"),
        "an action claiming authority with the row naming its fingerprint": E([review(derived_from=["request"]), r("resp", id="g6", agent="ag", outcome="approved", by="wa", fp=FP)], claims="g6") == (True, None),
        "an act within a standing delegation needs no approval of its own": E([review(derived_from=["request"]), r("deleg", id="d1", agent="ag", by="wa", scope=["moderate"])], under="d1", duty="moderate") == (True, None),
        "a delegation whose scope does not name the act licenses nothing": E([review(derived_from=["request"]), r("deleg", id="d1", agent="ag", by="wa", scope=["moderate"])], under="d1", duty="takedown") == (False, "effect_untrusted_unacknowledged"),
        "a withdrawn delegation licenses nothing": E([review(derived_from=["request"]), r("deleg", id="d1", agent="ag", by="wa", scope=["moderate"]), r("withdraw", id="wd", of="d1")], under="d1", duty="moderate") == (False, "effect_untrusted_unacknowledged"),
        "a delegation signed by a program's key licenses nothing": E([review(derived_from=["request"]), r("deleg", id="d2", agent="ag", by="bot", scope=["moderate"])], under="d2", duty="moderate") == (False, "effect_untrusted_unacknowledged"),
        "a delegation onto another agent licenses nothing": E([review(derived_from=["request"]), r("deleg", id="d3", agent="other", by="wa", scope=["moderate"])], under="d3", duty="moderate") == (False, "effect_untrusted_unacknowledged"),
        "a mesh row binding others waits for those who could stop it": E([review(derived_from=["request"])], binds_others=("m1", "m2")) == (False, "effect_untrusted_unacknowledged"),
        "their acknowledgements permit it": E([review(derived_from=["request"]), r("ack", of=FP, by="m1"), r("ack", of=FP, by="m2")], binds_others=("m1", "m2")) == (True, None),
    }
    # Inv_OrderFree
    P["P12 every answer is the same in every arrival order"] = {name: orders_agree(R) for name, R in (
        ("renewal", GOOD + authored("s2", at=18, until=40, t=18)),
        ("count and withdrawal", NETOK + [r("withdraw", id="w2", of="c1", head="G1", t=8), stmt("w2", "m1", 8)]),
        ("two issuers", authored("s1", by="stranger") + GOOD))}
    # Inv_OneAdmission
    P["P13 profile and code are one admission"] = one_admission()
    build = [r("build", units=frozenset({"d5"}), blessed=True)]
    # Inv_BuildAttests
    P["P14 a unit of the attested build runs under the build alone"] = {
        "a unit the blessed build names runs with no admission row": adm(build, digest="d5")[0] == "admit",
        "a unit the build does not name needs its own row": adm(build, digest="d6") == ("refuse", "admission_none"),
        "a build whose pipeline is not blessed admits nothing": adm([r("build", units=frozenset({"d5"}), blessed=False)], digest="d5") == ("refuse", "admission_none"),
    }
    return P


def orders_agree(R):
    seen = set()
    for i in range(ORDERS):
        S = list(BASE + R)
        random.Random(i).shuffle(S)
        seen.add(tuple(A.admit(S, "hA", "d1", now) for now in (5, 10, 19, 25, 30)))
    return len(seen) == 1


def one_admission():
    """Over one battery of authorities, a profile base link and a code statement get the same verdict on every rule
    they share: signed by a person reached, by a program, by nobody, or naming another digest."""
    out = {}
    for flaw in (None, "program", "unsigned", "other_digest"):
        by = "bot" if flaw == "program" else "iss"
        dig = "dz" if flaw == "other_digest" else "d1"
        code = [r("unit", id="sx", unit=dig, caps=COMPUTE, at=0, until=20, author=by, scope="federation")] + \
               ([] if flaw == "unsigned" else [stmt("sx", by)])
        code_ok = runs(code)
        resp_by = "bot" if flaw == "program" else "wa"
        prof = [r("template", agent="ag2", digest="d1", attested=True), r("bind", agent="ag2", steward="steward"),
                r("seat", agent="ag2", wa="wa", by="steward")] + \
               ([] if flaw == "unsigned" else [r("resp", id="rx", agent="ag2", outcome="approved", by=resp_by, digest="d1"),
                                              r("amend", id="ax", agent="ag2", digest="d1", by_resp="rx"),
                                              r("resp", id="ry", agent="ag2", outcome="approved", by=resp_by, digest=dig),
                                              r("amend", id="ay", agent="ag2", digest=dig, prev="ax", by_resp="ry")])
        prof_ok = A.load(BASE + prof, "ag2", ["d1", "d1"])[0]
        out[f"profile and code agree: {flaw or 'well formed'}"] = code_ok == prof_ok == (flaw is None)
    return out


PLANTS = {
    "P1 nothing runs without an admitted digest": ["run_unadmitted", "any_signature", "any_class"],
    "P2 a changed unit has no admission": ["no_digest_bind"],
    "P3 a program's key admits nothing": ["program_issuer", "program_relay", "program_voice"],
    "P4 an effect-capable unit needs the count, or the host's own owner on that host": ["effect_on_one", "owner_alone_anywhere", "owner_row_any_scope", "count_floor_one", "voices_outside_head"],
    "P5 a lease ends execution on the host's own clock": ["no_lease", "lease_from_signed", "lease_unbounded"],
    "P6 a withdrawal ends it forward": ["withdraw_ignored", "stranger_withdraws"],
    "P7 a halt stops every effect from receipt": ["no_halt", "stranger_halt", "no_fuse", "lone_resume", "halt_stops_compute"],
    "P8 capabilities only attenuate": ["no_attenuation", "sender_standing_carries"],
    "P9 dispatch executes only the reviewed fingerprint": ["exec_unreviewed", "fp_from_review", "three_of_four", "self_discharge",
                                                           "same_fp_passes", "objection_binds_thought", "drop_considered", "approval_unbound"],
    "P10 a profile loads only when its derived digest matches": ["no_profile_check", "fork_picks_one", "amend_unauthorized", "order_free",
                                                                 "orphan_counts", "unanchored_amends", "digest_unbound"],
    "P11 a result is no more trusted than what it derives from": ["declared_trust", "undeclared_passes", "absent_evidence_licenses", "binds_no_ack", "delegation_any_scope"],
    "P12 every answer is the same in every arrival order": ["first_statement_only"],
    "P13 profile and code are one admission": ["program_issuer", "amend_unauthorized"],
    "P14 a unit of the attested build runs under the build alone": ["unblessed_build", "build_any_digest"],
}


def run():
    clean = cases()
    lines, ok = [], True
    for prop, cs in clean.items():
        holds = all(cs.values())
        ok = ok and holds
        caught = []
        for p in PLANTS[prop]:
            A.PLANTS.add(p)
            try:
                hit = cases()[prop] != cs
            except Exception:
                hit = True
            A.PLANTS.discard(p)
            caught.append(f"{p}={'caught' if hit else 'missed'}")
            ok = ok and hit
        lines.append(f"property\t{prop}\t{'holds' if holds else 'broken'}\t{' '.join(caught)}")
        for name, v in cs.items():
            lines.append(f"case\t{prop.split()[0]}\t{name}\t{'as expected' if v else 'WRONG'}")
    n_cases = sum(len(cs) for cs in clean.values())
    n_plants = sum(len(v) for v in PLANTS.values())
    lines.append(f"count\t{len(clean)} properties, {n_cases} cases, {n_plants} planted breaks, {ORDERS} arrival orders")
    return lines, ok


def main(argv):
    lines, ok = run()
    path = os.path.join(HERE, "admission_expected.tsv")
    text = "\n".join(lines) + "\n"
    if "--write" in argv:
        open(path, "w", encoding="utf-8").write(text)
        print(f"wrote {path}")
    else:
        want = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        if want != text:
            ok = False
            print("differs from admission_expected.tsv")
    for l in lines:
        if l.startswith(("property", "count")): print(l.replace("\t", " | "))
    bad = [l for l in lines if l.endswith("WRONG") or "=missed" in l]
    for l in bad: print("  wrong:", l.replace("\t", " | "))
    print(f"RESULT: {'ok' if ok and not bad else 'broken'}")
    return 0 if ok and not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
