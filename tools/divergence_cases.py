#!/usr/bin/env python3
"""
The cases of the divergence manifest: for each place where shipped behaviour differs from the text, the rows that
tell the two apart, the named answer to ask, and the parameter each side gives the governed family. Read by
tools/build_divergences.py, which runs every case through tools/divergence_oracle.py (the kernel) and writes
manifests/divergences.json. A case is data: rows in the kernel's row form.

Each entry names its sources (text_conflicts rows, claims, rows of formal/derivation/seven_rankings_shipped.tsv).
`shipped.census` names the vendored census cell (formal/derivation/census_v61.tsv: prefix and column) whose words
the shipped value is; the build reads that cell and the check holds that the words recorded here still stand in it,
so a re-vendored census that has moved makes the entry stale and it is re-read or dropped.
`status` is `runnable` unless the entry says `stated` (with `reason` and a `gap` group) or `wording-only`.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "formal", "causal_kernel"))
_dwb, sys.dont_write_bytecode = sys.dont_write_bytecode, True
import seat as SEAT          # noqa: E402
import window as WN          # noqa: E402
import causal_kernel as CK   # noqa: E402
sys.dont_write_bytecode = _dwb
R = CK.row


# ---- row builders: every row is the kernel's own form --------------------------------------------------------------
def keyrec(id, k, typ="user", **kw):
    return R(id, "keyrec", k, (), identity_type=typ, family="key:record", **kw)


def fam(id, signer, family, names=(), **kw):
    return R(id, "fam", signer, names, family=family, **kw)


def wd(id, signer, target, names=(), **kw):
    return R(id, "withdraw", signer, tuple(names) + (target,), target=target, family="withdraws", **kw)


def root_seat(holder, scope, n=1, root="Rt"):
    """A root (its own founding row) and a seat it confers on `holder` over the root's key, with the holder's
    acceptance: the walk from a root the reader trusts (CC 3.4.7)."""
    rt = SEAT.offer("rt", root, root, "root", "@", "self")
    o = SEAT.offer("o%d" % n, root, holder, scope, root, "seat", names=("rt",), under="rt")
    a = SEAT.accept("a%d" % n, holder, "o%d" % n)
    return [rt, o, a]


def community(holder="A", gid="g"):
    """A community founded alone: its founder is its first duty holder (CC 4.5.4)."""
    return [SEAT.offer(gid, holder, (holder,), "duty", "@", "self")]


def group(keys=("A", "B", "C"), gid="g", protocol="strict"):
    """A group whose founding row is signed by every key it seats, declaring its counting protocol."""
    return [SEAT.offer(gid, keys[0], keys, "member", "@", "self", cosigners=tuple(keys[1:]), protocol=protocol)]


def ids(rows):
    return tuple(r["id"] for r in rows)


SIGNER = ("3_signer_rule",)
LIFE = ("9_lifecycle",)
REPL = ("10_replication",)
COSIGN = ("5_cosign_rule",)


def signer_entry(impl, family, sources, cc_ref, quote, text_dnf, shipped_dnf, shipped_words, rows, target,
                 census="auto", text_value=None, kind="signer", where="signer_rule", leaf=None):
    tg = {leaf: text_dnf, "*": [["any"]]} if leaf else text_dnf
    sg = {leaf: shipped_dnf, "*": [["any"]]} if leaf else shipped_dnf
    return {"implementer": impl, "family": family, "where": where, "kind": kind, "sources": sources,
            "cc_ref": cc_ref, "quote": quote, "text_value": text_value or text_dnf,
            "text_param": {"family": family, "gate": tg},
            "shipped_param": {"family": family, "gate": sg},
            "shipped_value": shipped_words, "census": (family, SIGNER[0]) if census == "auto" else census,
            "rows": rows, "ask": {"answer": "state", "target": target}}


def lifecycle_entry(impl, family, sources, cc_ref, quote, text_dnf, shipped_dnf, shipped_words, rows, target,
                    census="auto", extra_text=None, extra_shipped=None, kind="lifecycle", where="lifecycle.withdraws_by",
                    shipped_source=None):
    tp = {"family": family, "withdraws_by": text_dnf, **(extra_text or {})}
    sp = {"family": family, "withdraws_by": shipped_dnf, **(extra_shipped or {})}
    e = {"implementer": impl, "family": family, "where": where, "kind": kind, "sources": sources, "cc_ref": cc_ref,
         "quote": quote, "text_value": text_dnf, "text_param": tp, "shipped_param": sp, "shipped_value": shipped_words,
         "census": (family, LIFE[0]) if census == "auto" else census, "rows": rows, "ask": {"answer": "state", "target": target}}
    if shipped_source: e["shipped_source"] = shipped_source
    return e


def stated(impl, family, where, kind, sources, cc_ref, quote, shipped_words, gap, reason, census=None, shipped_source=None):
    return {"implementer": impl, "family": family, "where": where, "kind": kind, "sources": sources, "cc_ref": cc_ref,
            "quote": quote, "shipped_value": shipped_words, "census": census, "status": "stated", "gap": gap,
            "reason": reason, "shipped_source": shipped_source}


def wording(impl, family, where, sources, cc_ref, quote, shipped_words, reason, census=None, shipped_source=None):
    return {"implementer": impl, "family": family, "where": where, "kind": "wording-only", "sources": sources,
            "cc_ref": cc_ref, "quote": quote, "shipped_value": shipped_words, "census": census,
            "status": "wording-only", "reason": reason, "shipped_source": shipped_source}


Q347 = "a node, about itself or about a grant it holds | `infra:attest`"


def cases():
    E = []
    U = keyrec("ku", "U")                             # a registered key holding no seat
    # ---- signer: who may sign a row of the family ---------------------------------------------------------------
    E.append(signer_entry("persist", "watchlist:{id}", ["C365", "C388"], "CC 3.1.9.4",
        "Enable/disable is signed by the CC 4.5.5 `moderate`/`takedown` authority and revocable by `withdraws`",
        [["seat:moderate@group"], ["seat:takedown@group"]], [["registered"]], "any_registered x none x {}",
        community() + [U, fam("w", "U", "watchlist:{id}", ("g", "ku"), group="g")], "w"))
    E.append(signer_entry("persist", "age_self_declared:band:{band}:{version}", ["C364", "C422"], "CC 3.4.11",
        "Admitted iff the signer acts for the subject (the subject's own occurrence or an admitted occurrence of it).",
        [["self"]], [["registered"]], "any_registered x none x {}",
        [U, fam("d", "U", "age_self_declared:band:{band}:{version}", ("ku",), subject="S")], "d"))
    E.append(signer_entry("persist", "wa_adjudication:{state}", ["C366"], "CC 3.1.9.4",
        "`petition` is the petitioner's own row that opens the ownership-reclaim ceremony",
        [["self"]], [["seat:wa@root"]], "seat_role(wa) quorum, re-derived from this node's state",
        [keyrec("kp", "P"), SEAT.offer("rt", "Rt", "Rt", "root", "@", "self"),
         fam("p", "P", "wa_adjudication:{state}", ("kp", "rt"), subject="P", root="Rt", leaf="petition")], "p",
        leaf="petition", where="signer_rule[leaf=petition]"))
    E.append(signer_entry("persist", "regime:{artifact}:{version}", ["C445", "C484"], "CC 3.1.9.2",
        "**reserved — substrate-steward-emitted**, the emitter rule pinned at mint per R2(a), so the ProducerSteward default never applies",
        [["type:substrate_persist"]], [["registered"]], "any_registered x none x {}",
        [U, fam("r", "U", "regime:{artifact}:{version}", ("ku",))], "r"))
    E.append(signer_entry("persist", "evidence:{suite}:{kind}:{cell}:{prefix}", ["C446"], "CC 3.1.5.5",
        "Emitted at `federation` scope by a key holding `infra:attest`, delegated by the root or conferred by an accord co-scrub of its key record",
        [["seat:infra:attest@root"]], [["registered"]], "any_registered x none x {}",
        [U, SEAT.offer("rt", "Rt", "Rt", "root", "@", "self"),
         fam("e", "U", "evidence:{suite}:{kind}:{cell}:{prefix}", ("ku", "rt"), root="Rt")], "e"))
    E.append(signer_entry("persist", "slashing:{outcome}", ["C447", "C458"], "CC 4.5.5",
        "A duty action (`takedown_notice`, `moderation:*`, `reconsideration:*`, `slashing:*`, `quarantine:*`) is admitted **iff** one holds **positively**",
        [["seat:slash@group"]], [["registered"]], "any_registered x none x {}",
        community() + [U, fam("s", "U", "slashing:{outcome}", ("g", "ku"), group="g")], "s"))
    E.append(signer_entry("persist", "consent:state:{stance}", ["C449", "C497"], "CC 3.4.5",
        "`consent:state:granted` / `consent:state:revoked`, `consent:scope:*`, `consent:stream:*` MUST be emitted by a `subject_key_id` of the target Contribution or a `delegates_to` chain rooted at one",
        [["self"], ["seat:consent:state@subject"]], [["self"], ["owner_of_subject"]], "self | owner_of_subject(for_key_id) x none x {}",
        [SEAT.offer("dl", "S", "D", "consent:state", "S", "self"), SEAT.accept("da", "D", "dl"),
         fam("c", "D", "consent:state:{stance}", ("dl", "da"), subject="S", leaf="granted")], "c",
        leaf="granted", where="signer_rule[stance=granted|revoked]"))
    E.append(signer_entry("persist", "consent:state:{stance}", ["C450", "C485"], "CC 3.4.5",
        "**`consent:state:expired`** is signed by the node that holds the grant and saw it lapse, under `infra:attest`",
        [["seat:infra:attest@root"]], [["self"], ["owner_of_subject"]], "self | owner_of_subject(for_key_id) x none x {}",
        root_seat("N", "infra:attest") + [fam("x", "N", "consent:state:{stance}", ("a1",), subject="S", root="Rt", leaf="expired")],
        "x", leaf="expired", where="signer_rule[stance=expired]"))
    E.append(signer_entry("persist", "consent:community_trust", ["C496"], "CC 3.3.1",
        "The node-authored form stays valid, and the fold below groups both forms by `attested_key_id`.",
        [["owner_of_subject"], ["self"]], [["owner_of_subject"]], "owner_of_subject (binding in force at the signed instant) x none x {}",
        [fam("t", "N", "consent:community_trust", (), subject="N")], "t"))
    E.append(signer_entry("persist", "takedown_notice:{basis}", ["C521", "C536"], "CC 4.5.5",
        "the content's **authoritative** subject set `subject_of(content_sha256)`",
        [["subject_of_content"], ["seat:takedown@group"]], [["seat:takedown@group"]],
        "seat_role(takedown) x delegates_to(takedown) x {} (takedown: outside vocabulary)",
        community() + [fam("ct", "X", "content", (), subjects=("S",)),
                       fam("n", "S", "takedown_notice:{basis}", ("g", "ct"), group="g", content="ct")], "n"))
    E.append(signer_entry("persist", "community:listing", ["C566"], "CC 3.1.1",
        "signed by a current `moderate`-holder of the community it names; one live row per community",
        [["seat:moderate@group"]], [["seat:moderate@group"], ["seat:founder@group"]],
        "seat_role(moderate) | founder (founder: outside vocabulary) x none x {}",
        [SEAT.offer("g", "F", ("F",), "founder", "@", "self"), fam("l", "F", "community:listing", ("g",), group="g")], "l"))
    E.append(signer_entry("persist", "system:*", ["C486", "C564"], "CC 3.4.7", Q347,
        [["component_of_subject", "seat:infra:attest@root"]], [["type:substrate_persist"]],
        "PROSE: identity_type contains substrate_persist (no vocabulary value) x none x {}",
        [keyrec("ke", "E", "substrate_edge", node="N")] + root_seat("E", "infra:attest")
        + [fam("sy", "E", "system:*", ("ke", "a1"), subject="N", root="Rt")], "sy"))
    # the reserved families still gated on a declared type or the undivided attest (C564, formal/derivation/seat_duties.tsv)
    typed = ["audit_chain:hash_continuity", "corpus_health:n_eff_measurable", "federation_directory:replication_lag",
             "identity_continuity:relational_anchor", "hard_case:{kind}"]
    for f in typed:
        E.append(signer_entry("persist", f, ["C564"], "CC 3.4.7", Q347, [["seat:infra:attest@root"]], [["type:substrate_persist"]],
            "PROSE: identity_type contains substrate_persist", [keyrec("kn", "N", "substrate_persist"),
             SEAT.offer("rt", "Rt", "Rt", "root", "@", "self"), fam("h", "N", f, ("kn", "rt"), subject="N", root="Rt")], "h"))
    for f in ["detection:correlated_action:{axis}", "detection:distributive:access:{resource_type}",
              "detection:hash_chain_integrity", "detection:intra_agent_consistency", "detection:{detector}"]:
        E.append(signer_entry("persist", f, ["C564"], "CC 3.4.7", "`infra:detect`",
            [["seat:infra:detect@root"]], [["type:lenscore_detector", "seat:infra:detect@root"]],
            "PROSE: identity_type contains lenscore_detector x delegates_to(infra:detect)",
            [keyrec("kd", "D")] + root_seat("D", "infra:detect") + [fam("h", "D", f, ("kd", "a1"), root="Rt")], "h"))
    E.append(signer_entry("persist", "transparency_log:cosigned:{tree_size}", ["C564"], "CC 3.4.7", "`infra:attest_assurance`",
        [["seat:infra:attest_assurance@root"]], [["type:witness", "seat:infra:attest_assurance@root"]],
        "seat_role(attest) x delegates_to(infra:attest_assurance) x {}; + identity_type contains witness",
        [keyrec("kw", "W")] + root_seat("W", "infra:attest_assurance")
        + [fam("h", "W", "transparency_log:cosigned:{tree_size}", ("kw", "a1"), root="Rt")], "h"))
    for f, duty, srcs in [("age_assurance:{level}:{band}:{version}", "assure:age", ["C423", "C483", "C564"]),
                          ("capacity_assurance:{level}:{domain}:{band}:{version}", "assure:capacity", ["C483", "C564"]),
                          ("capacity_assurance:reversible_excluded:{domain}:{version}", "assure:capacity", ["C483", "C564"]),
                          ("capacity_assurance:reversible_pending:{domain}:{version}", "assure:capacity", ["C483", "C564"])]:
        E.append(signer_entry("persist", f, srcs, "CC 3.4.7", "`%s`" % duty,
            [["seat:%s@root" % duty, "not_subject"]], [["type:witness", "seat:infra:attest_assurance@root", "not_subject"]],
            "seat_role(attest) x delegates_to(infra:attest_assurance", [keyrec("kw", "W", "witness")]
            + root_seat("W", "infra:attest_assurance") + [fam("h", "W", f, ("kw", "a1"), root="Rt", subject="S")], "h"))
    # ---- lifecycle: who may withdraw ----------------------------------------------------------------------------
    E.append(lifecycle_entry("persist", "watchlist:{id}", ["C365"], "CC 3.1.9.4",
        "Enable/disable is signed by the CC 4.5.5 `moderate`/`takedown` authority and revocable by `withdraws`",
        [["attester"]], [["attester"], ["subject"]], "withdraws_by: {attester, subject}",
        [fam("w", "A", "watchlist:{id}", (), subjects=("S",)), wd("x", "S", "w")], "w"))
    E.append(lifecycle_entry("persist", "quarantine:{state}", ["C370"], "CC 3.1.9.2",
        "Subject-scoped quarantine marker: **slash-duty-holder-only** emitter.",
        [["attester"]], [["attester"], ["subject"]], "withdraws_by: {attester, subject}",
        [fam("q", "A", "quarantine:{state}", (), subject="S", leaf="withhold"), wd("x", "S", "q")], "q"))
    E.append(lifecycle_entry("persist", "revocation:{entity_type}:{reason}", ["C551"], "CC 3.1.1",
        "Entity revocation (`agent` / `partner` / `license`). Immediate, non-rollbackable.",
        [], [["attester"]], "withdraws_by: {attester}",
        [fam("v", "A", "revocation:{entity_type}:{reason}", (), subject="S"), wd("x", "A", "v")], "v"))
    E.append(lifecycle_entry("persist", "objection:{state}", ["C476"], "CC 4.5.13",
        "The act is lifted when a strict majority of the roster at the head the act names has objected within the 48-hour window.",
        [["attester"]], [["attester"], ["subject"]], "withdraws_by: {attester, subject}",
        [fam("ob", "M", "objection:{state}", (), subject="X"), wd("x", "X", "ob")], "ob"))
    E.append(lifecycle_entry("persist", "trace:{form}:{version}", ["C228"], "CC 3.1.5",
        "An agent's trace is erased only by its signer's `withdraws`",
        [["attester"]], [["attester"], ["subject"], ["owner_of_subject"]],
        "withdraws_by: {attester, subject} (+ producer's owner",
        [SEAT.offer("ob", "Ag", "O", "owner", "Ag", "self", cosigners=("O",)),
         fam("tr", "Ag", "trace:{form}:{version}", (), subject="Ag"), wd("x", "O", "tr", ("ob",), subject="Ag")], "tr"))
    E.append(signer_entry("persist", "trust:{job}:{version}", ["C499"], "CC 3.2",
        "The acceptance edge is a person's row: any live key of the person's roster signs it as that person",
        [["seat:member@person"]], [["self"]], "accepts: self (node -> root)",
        [SEAT.offer("p", "D1", ("D1", "D2"), "member", "@", "self", cosigners=("D2",)),
         fam("ac", "D2", "trust:{job}:{version}", ("p",), subject="N", person="p", leaf="accepts")], "ac",
        leaf="accepts", where="signer_rule[leaf=accepts]"))
    E.append(lifecycle_entry("persist", "trust:{job}:{version}", ["C507"], "CC 2.4",
        "so no single signer and no subject can retire a community, un-name a charter or retract a roster event",
        [["count:protocol@group"]], [["attester"], ["subject"]], "withdraws_by: {attester, subject}",
        group() + [fam("ch", "A", "trust:{job}:{version}", ("g",), group="g", head=("g",), subject="B", leaf="charter"),
                   wd("x", "A", "ch", head=("g",), group="g")], "ch", where="lifecycle.withdraws_by[leaf=charter]"))
    E.append(lifecycle_entry("persist", "(default row)", ["C552"], "CC 2.4.1.1",
        "An affiliation withdraws no statement about itself, whatever the statement.",
        [["attester"]], [["attester"], ["subject"]], '"withdraws_by": "{attester, subject}"',
        [fam("st", "A", "(default row)", (), subject="Aff"), wd("x", "Aff", "st")], "st", census=None,
        where="lifecycle.withdraws_by[subject=affiliation]",
        shipped_source="formal/derivation/family_default_row.json withdraws_by (the census reading)"))
    E.append(lifecycle_entry("persist", "membership:{stage}", ["C494", "C506"], "CC 3.1.3.2",
        "The inviter withdraws a proposal with the ordinary `withdraws`.",
        [["attester"]], [["count:protocol@group"]], "withdraws_by: {cosigned}",
        group() + [fam("pr", "A", "membership:{stage}", ("g",), group="g", head=("g",), leaf="proposal"),
                   wd("x", "A", "pr", head=("g",), group="g")], "pr", where="lifecycle.withdraws_by[leaf=proposal]"))
    E.append(lifecycle_entry("persist", "ownership:{relation}:{target_kind}:{version}", ["C346"], "CC 3.2",
        "A rule-2 or rule-4 `withdraws` against a live owner-binding concludes nothing unless it carries a `wa_adjudication_ref`.",
        [["ref"]], [["ref"]], "withdraw: when(verb=withdraw,has=wa_adjudication_ref) ... else refuse",
        [fam("ob", "O", "ownership:{relation}:{target_kind}:{version}", (), subject="N"), wd("x", "N", "ob")], "x",
        census=None, extra_shipped={"refuse": ["withdraw_without_ref"]}, kind="door", where="transition withdraw guard",
        shipped_source="manifests/transitions.json ownership:{relation}:{target_kind}:{version} withdraw guard (text_conflicts C346 side_b)"))
    # ---- cosign / count: a group's act takes the group's count ----------------------------------------------------
    for impl, f, srcs, cc, q, sw, cen, where in [
        ("persist", "goal:{scale}", ["C469", "C508"], "CC 3.1.9.7",
         "A member votes for the Goal by cosigning it, and the row is admitted only when its full scrub set meets the group's protocol over the members at the head the row names",
         "none", ("goal:{scale}", COSIGN[0]), "cosign_rule"),
        ("persist", "mesh_config:{key}", ["C509"], "CC 4.2.1",
         "**Durable** settings are earned by **quorum, never by having been exercised**.", "none",
         ("mesh_config:{key}", COSIGN[0]), "cosign_rule[form=durable]"),
        ("persist", "ownership:{relation}:{target_kind}:{version}", ["C371"], "CC 3.2",
         "It is cosigned under that affiliation's protocol", "none",
         ("ownership:{relation}:{target_kind}:{version}", COSIGN[0]), "cosign_rule[owner=organisation]"),
        ("persist", "licensure:{authority_id}", ["C432"], "CC 2.4.1.3",
         "A `licensure:{community_key_id}` row is a **cosigned row** ([CC 2.4](#2.4)) whose protocol source is the authority named in the dimension.",
         "none", ("licensure:{authority_id}", COSIGN[0]), "cosign_rule[authority=organisation]"),
        ("persist", "accord:lifecycle:{kind}", ["C457"], "CC 4.2.1.3",
         "**It is a cosigned row by a strict majority of the standing roster**", "none",
         ("accord:lifecycle:{kind}", COSIGN[0]), "cosign_rule"),
    ]:
        e = signer_entry(impl, f, srcs, cc, q, [["count:protocol@group"]], [["seat:member@group"]], sw,
                         group() + [fam("h", "A", f, ("g",), group="g", head=("g",))], "h", census=cen, kind="cosign", where=where)
        if cen is None:
            e["shipped_source"] = "manifests/transitions.json transport:canonical_rebind supersede (text_conflicts C471 side_b)"
        E.append(e)
    # an occurrence evicting another: the self-roster door, not one occurrence's act (C412)
    for impl, srcs in [("persist", ["C412"])]:
        E.append({"implementer": impl, "family": "identity:occurrence", "where": "transition withdraw policy", "kind": "count",
                  "sources": srcs, "cc_ref": "CC 3.3.6",
                  "quote": "No single occurrence evicts at once with no window: that unilateral configuration is one a thief wins in two steps.",
                  "text_value": "self_roster_evict: a strict majority of the occurrences, or the lone path's window",
                  "text_param": {"family": "identity:occurrence", "policy": {"occurrence_evict": ["strict", 1, 2]}},
                  "shipped_param": {"family": "identity:occurrence", "policy": {"occurrence_evict": ["one", 1, 1]}},
                  "shipped_value": "selfAct" if impl == "tooling" else "withdraws_by: {attester, subject} via signer_acts_for identity",
                  "census": ("identity:occurrence", LIFE[0]) if impl == "persist" else None,
                  "shipped_source": "manifests/transitions.json identity:occurrence withdraw policy selfAct (tools/build_transitions.py)" if impl == "tooling" else None,
                  "rows": [SEAT.offer("g", "A", ("A", "B"), "member", "@", "self", cosigners=("B",)),
                           SEAT.unseat("u", "A", "B", "member", "g", "group", names=("g",), head=("g",), policy="occurrence_evict")],
                  "ask": {"answer": "stands", "key": "B", "scope": "member", "obj": "g"}})
    # ---- audience ----------------------------------------------------------------------------------------------------
    for f, srcs, cc, q in [("census:share:{class}", ["C383"], "CC 6.1.9", "held by the author's node and the recipient's node and by no other"),
                           ("census:member:share", ["C465"], "CC 3.1.3", "**Yes — addressed:** a member of the room; reach is the named tally member only")]:
        E.append({"implementer": "persist", "family": f, "where": "replication.audience", "kind": "audience", "sources": srcs,
                  "cc_ref": cc, "quote": q, "text_value": "addressed", "census": (f, REPL[0]),
                  "shipped_value": "targeted -> cohort_plus_subjects(full) (refers-to: attested, subjects, for_key_id)",
                  "text_param": {"family": f, "audience": "addressed"}, "shipped_param": {"family": f, "audience": "cohort_plus_subjects"},
                  "rows": group(("A", "T", "M")) + [fam("sh", "A", f, ("g",), group="g", for_key="T")],
                  "ask": {"answer": "audience", "target": "sh", "reader": "M"}})
    E.append({"implementer": "persist", "family": "identity:occurrence", "where": "replication.audience", "kind": "audience",
              "sources": ["C464"], "cc_ref": "CC 5.4.6",
              "quote": "A node offers an `identity:occurrence:v1` row to a peer only when it would also relay the row's attester key to that peer",
              "text_value": "the audience the attester's owner-binding reaches", "census": ("identity:occurrence", REPL[0]),
              "shipped_value": "audience: PROSE key-plane reach (Plane::KeyRecord cells; the carrier: everyone)",
              "text_param": {"family": "identity:occurrence", "audience": "attester_relayed"},
              "shipped_param": {"family": "identity:occurrence", "audience": "everyone"},
              "rows": group(("O", "K")) + [fam("b", "O", "self:delegates_to", ("g",), group="g", tier="cohort"),
                                           fam("oc", "K", "identity:occurrence", ("b",), binding="b")],
              "ask": {"answer": "audience", "target": "oc", "reader": "P"}})
    # ---- door: a check that reads another row concludes nothing, it does not refuse ---------------------------------
    E.append(signer_entry("tooling", "identity:occurrence", ["C516"], "CC 3.3.6",
        "It counts at a node only where that row is Rooted there and its manifest hash equals `build_manifest_hash`, and otherwise concludes nothing.",
        [["provenance_matches"]], [["any"]], "manifests/transitions.json identity:occurrence attest: guard value [] (source generic)",
        [fam("pv", "B", "provenance:build_manifest:{target}", (), rooted=True, hash="h1"),
         fam("oc", "K", "identity:occurrence", ("pv",), provenance="pv", build_manifest_hash="h2")], "oc",
        census=None, kind="door", where="transition attest guard"))
    E[-1]["shipped_source"] = "manifests/transitions.json identity:occurrence attest guard (formal/derivation/guard_text.tsv has no row)"
    E[-1]["note"] = ("stays: the guard row is written and held back, since its void clause needs a reason token the text states and "
                     "none is stated, and a clause with none may not be added (a named limit in CC 8.3.4)")
    E.append(signer_entry("persist", "capacity:{factor}", ["CLM-capacity-consent-gate"], "CC 3.4.5",
        "a `capacity:*` row MUST name that grant in `evidence_refs[]`",
        [["grant_named"]], [["subject_grant_held"]], "admission reads the subject's grants; the scoring row names none",
        [fam("gr", "S", "consent:state:{stance}", (), scope="analyze"),
         fam("cp", "L", "capacity:{factor}", (), subject="S", needs_scope="analyze")], "cp",
        census=None, kind="door", where="consent gate"))
    E[-1]["text_param"]["refuse"] = ["names_no_grant"]
    E[-1]["shipped_source"] = "constitution/claims.tsv CLM-capacity-consent-gate (check_capacity_consent_admission)"
    # ---- the emitter of a reaction (tooling) ----------------------------------------------------------------------
    # ---- owed: what a window's close does -------------------------------------------------------------------------
    E.append({"implementer": "tooling", "family": "takedown_notice:{basis}", "where": "reaction on close(withhold)", "kind": "window",
              "sources": ["C377"], "cc_ref": "CC 4.5.3",
              "quote": "**Inside the window** the bytes are still held: serving resumes, the hard-delete sweep skips them",
              "text_value": "on close(withhold) unless fold(notice_voided) -> do destroy_bytes",
              "shipped_value": "on close(withhold): do destroy_bytes, force must, with no unless",
              "shipped_source": "manifests/reactions.json takedown_notice:{basis} (formal/derivation/reaction_text.tsv)", "census": None,
              "text_param": {"family": "takedown_notice:{basis}", "owed": "withhold_close", "unless": "notice_voided"},
              "shipped_param": {"family": "takedown_notice:{basis}", "owed": "withhold_close"},
              "rows": [fam("n", "A", "takedown_notice:{basis}", ()), R("l", "landing", "A", ("n",), says="withhold"),
                       R("v", "reversal", "A", ("n",))],
              "ask": {"answer": "owed"},
              "note": "stays: no fold or reaction word reads a row that names this one with a stated outcome, so the close cannot skip a reversed or lifted notice (a named limit in CC 8.3.4)"})
    # ---- folds ------------------------------------------------------------------------------------------------------
    def fold_entry(impl, f, srcs, cc, q, name, tmode, smode, sw, rows, ask, where="fold", census=None, src=None):
        return {"implementer": impl, "family": f, "where": where, "kind": "fold", "sources": srcs, "cc_ref": cc, "quote": q,
                "text_value": tmode, "shipped_value": sw, "census": census, "shipped_source": src,
                "text_param": {"family": f, "fold": name, "mode": tmode}, "shipped_param": {"family": f, "fold": name, "mode": smode},
                "rows": rows, "ask": dict(ask, answer="fold")}
    E.append(fold_entry("persist", "consent:community_trust",
        ["seven_rankings item 1", "CLM-consent-community-trust", "CLM-consent-community-trust-owner-authored"], "CC 3.3.1",
        "**Each party's consent is its own**, and each party's rows are folded apart from every other party's.",
        "consent_capture", "per_party", "one_boundary",
        "the latest admitted revocation of any party is R; among grants after R the latest asserted_at wins (fold_community_trust)",
        [fam("g0", "B", "consent:community_trust", (), leaf="grant", at=0), fam("g1", "A", "consent:community_trust", (), leaf="grant", at=1),
         fam("r2", "B", "consent:community_trust", (), leaf="revoke", at=2), fam("g3", "A", "consent:community_trust", (), leaf="grant", at=3)],
        {"bound": ["A", "B"]}, src="constitution/claims.tsv CLM-consent-community-trust; impl:CIRISPersist fold_community_trust"))
    E.append(fold_entry("persist", "key:revocation", ["seven_rankings item 3", "CLM-merge"], "CC 2.4.1.1",
        "Where a key carries multiple revocations the effective bound is the **minimum** `revoked_after` across all of them",
        "revocation_bound", "minimum", "ranked", "revocations ranked by quorum_weight, then signed timestamp, then content hash",
        [fam("r1", "A", "key:revocation", (), leaf="revocation", subject="K", revoked_after=10, weight=1, at=5),
         fam("r2", "B", "key:revocation", (), leaf="revocation", subject="K", revoked_after=20, weight=2, at=6)],
        {"key": "K", "signed_at": 15}, src="constitution/claims.tsv CLM-merge; impl:CIRISPersist check_partner_record_revision"))
    E.append(fold_entry("persist", "licensure:{authority_id}", ["seven_rankings item 4", "CLM-merge"], "CC 5.3.2.3",
        "At equal weight the more restrictive state stands: `revoked` > `suspended` > `active`.",
        "licence_merge", "weight_then_state", "weight_time_hash", "quorum_weight, then signed timestamp, then content hash",
        [fam("l1", "A", "licensure:{authority_id}", (), leaf="licence", status="revoked", weight=1, at=1),
         fam("l2", "B", "licensure:{authority_id}", (), leaf="licence", status="active", weight=1, at=2)],
        {}, src="constitution/claims.tsv CLM-merge"))
    E.append(fold_entry("persist", "quarantine:{state}",
        ["seven_rankings item 5", "CLM-quarantine-marker-not-command", "CLM-quarantine-serve-consult"], "CC 3.1.9.2",
        "**a withhold outranks a release whatever their instants**. The withhold holds until a release names the withhold it lifts.",
        "quarantine", "release_names", "latest_then_withhold", "withhold beats release at a same-instant tie (fold_quarantine)",
        [fam("w", "A", "quarantine:{state}", (), leaf="withhold", at=1), fam("rl", "B", "quarantine:{state}", (), leaf="release", at=2)],
        {}, src="constitution/claims.tsv CLM-quarantine-marker-not-command; impl:CIRISPersist fold_quarantine"))
    E.append(fold_entry("persist", "ballot:moderator_acceptance", ["seven_rankings item 6", "CLM-moderator-election"], "CC 4.5.13",
        "Two acceptances over different sets of equal size are a tie, and neither seats anyone.",
        "acceptance", "larger_then_nobody", "larger_then_digest", "the valid acceptance over the larger set, then the smaller digest",
        [fam("acc1", "X", "ballot:moderator_acceptance", (), leaf="acceptance", ballots=["b1", "b2"], seats="X"),
         fam("acc2", "Y", "ballot:moderator_acceptance", (), leaf="acceptance", ballots=["b1", "b3"], seats="Y")],
        {}, src="constitution/claims.tsv CLM-moderator-election (staged:CIRISPersist#1195)"))
    E.append(fold_entry("persist", "*reader:enumerated", ["seven_rankings item 7", "CLM-nsproc-aggregation-policy"], "CC 4.4.3.34",
        "The reader aggregates per (`dimension`, `attested_key_id`) tuple, over trusted attesters, by the polarity defaults of [CC 4.4.2](#4.4.2).",
        "enumerated", "reader_trust", "most_recent", "most-recent by an authorized attester",
        [R("ca", "claim", "A", (), subject="S", dim="d", value="x", at=2), R("cb", "claim", "B", (), subject="S", dim="d", value="y", at=1),
         R("tr", "trust", "Rd", (), to="B", scope="any")],
        {"reader": "Rd", "subject": "S", "dim": "d"}, src="constitution/claims.tsv CLM-nsproc-aggregation-policy (staged:CIRISPersist#803)"))
    E.append(fold_entry("tooling", "age_assurance:{level}:{band}:{version}", ["C548"], "CC 3.4.11",
        "A subject's declaration of a lower band lowers the reading and never raises it",
        "age_band", "witness_then_self_lowers", "rank", "pick=rank(government>provider>self)",
        [fam("aw", "W", "age_assurance:{level}:{band}:{version}", (), leaf="witness", level="provider", band="adult", subject="S"),
         fam("as", "S", "age_self_declared:band:{band}:{version}", (), leaf="self", level="self", band="minor", subject="S")],
        {"subject": "S"}, src="formal/derivation/fold_text.tsv age fold (tools/fold_grammar.py has no picker)"))
    E[-1]["note"] = "stays: the fold grammar has no picker for the lower of the witness band and a self-declared lower band (a named limit in CC 8.3.4)"
    E.append(fold_entry("persist", "ownership:{relation}:{target_kind}:{version}", ["C208"], "CC 3.4.7.3",
        "The steward set therefore has **at most one** member: the granter of the one live owner-binding.",
        "stewards_of", "binding_only", "binding_and_occurrence", "the steward fold admits on the identity_occurrence anchor",
        [SEAT.offer("ob", "K", "O", "owner", "K", "self", cosigners=("O",)),
         fam("io", "X", "identity:occurrence", (), leaf="identity_occurrence", subject="K")],
        {"key": "K"}, where="fold:stewards_of", src="formal/derivation/text_conflicts.tsv C208 (the store's steward fold, read by the conflict row)"))
    E.append(signer_entry("persist", "takedown_notice:{basis}", ["C307"], "CC 2.4.1.1",
        "authorised by a cosigned `takedown_notice` under the trust root's `consensus_protocol` with basis `steward_purge`",
        [["count:protocol@group"]], [], "steward_purge leaf: none (held shut)",
        group() + [SEAT.cosign("cb", "B", "n", names=("g",)),
                   fam("n", "A", "takedown_notice:{basis}", ("g", "cb"), group="g", head=("g",), leaf="steward_purge")], "n",
        leaf="steward_purge", kind="cosign", where="signer_rule[leaf=steward_purge]"))
    e = signer_entry("persist", "(default row)", ["C331"], "CC 2.1",
        "A row naming a key outside its audience concludes nothing",
        [["subjects_in:group"]], [["any"]], '"in_audience": "no"',
        group(("A", "B")) + [fam("t", "A", "(default row)", ("g",), group="g", head=("g",), subjects=("X",))], "t",
        census=None, kind="subject", where="subject_rule.in_audience")
    e["shipped_source"] = "formal/derivation/family_default_row.json subject_rule in_audience (the census reading, 144 code-v61 cells)"
    e["note"] = ("the text says refused; the check reads the roster at the row's head, another row, so the kernel concludes "
                 "nothing rather than refusing (KERNEL.md section 3)")
    E.append(e)
    e = signer_entry("persist", "moderation:{allegation_type}", ["C439", "C481"], "CC 2.6.1.8", "OPTIONAL on moderation:*",
        [["any"]], [["any"]], "moderation subject digest required", [fam("m", "A", "moderation:{allegation_type}", ())], "m",
        census=("moderation:{allegation_type}", "7_body"), kind="door", where="body.subject_digest")
    e["shipped_param"]["refuse"] = ["missing_subject_digest"]
    E.append(e)
    # ---- stated: the kernel model cannot express it ------------------------------------------------------------------
    E.append(stated("persist", "(targeted rows)", "refusal token", "door", ["C104"], "CC 2.1",
        "A targeted row naming a third party in `attested_key_id` is refused at admission", "no token in CC 3.1.3.2's list",
        "wire", "the case is a refusal by the row alone and the kernel gives it (refused); what differs is the token's name on the wire"))
    E.append(stated("persist", "key:record", "scrub_key_id", "signer", ["C359"], "CC 3.1.3",
        "**Yes — self only, by possession**; every other row is admitted only once its signer's `key:record` is held (retryable otherwise)",
        "an anchor scrub may differ from the subject (KeyRecord in constitution/signed_object.tsv)", "wire",
        "which field carries an anchor's signature is the signed object's byte form; the kernel's row has one signer and cosigners"))
    E.append(stated("persist", "(any, under legal_hold)", "erasure_route", "lifecycle", ["C453"], "CC 4.4.3.29",
        "or under a `legal_hold` ([CC 4.4.3.12](#4.4.3.12)), the `withdraws` is admitted and recorded, and the descent it would force is refused with reason",
        "legal_hold: none in code", "storage",
        "the withdraws is admitted in both; what differs is the erasure descent, a storage act the kernel does not model"))
    E.append(stated("agent", "(agent conduct)", "CC 7.4 stop", "door", ["C562"], "CC 7.4",
        "An agent that finds itself one step from a lethal act — holding a target, a trigger, a release, or the computation another system would fire on — stops.",
        "nothing detects that situation; none of the ten verbs is a stop", "outside the kernel",
        "recognising one step from a lethal act is the agent's reading of its task, not a function of rows"))
    E.append(stated("persist", "moderation:{allegation_type}", "replication.audience", "audience", ["C384"], "CC 4.5.5",
        "A duty-holder's record MAY withhold the reporter's identity and the report's content from the person named",
        "targeted -> cohort_plus_subjects(full) (refers-to: attested, subjects, for_key_id)", "no field-level audience",
        "the subject is served the row's existence and some fields and not others; the model's audience is of a whole row",
        census=("moderation:{allegation_type}", REPL[0])))
    E.append(stated("tooling", "membership:{stage}", "guard[leaf=widening on a stalled roster]", "door", ["C492"], "CC 3.2",
        "So a stalled roster admits **exactly one row kind without that count**: a widening whose only change is the addition of a **founder** seat.",
        "when(leaf=widening) (one trust:confers@landed[...] else refuse & type(signer,user) else refuse ...)", "no such answer",
        "a stalled roster (T7) is no answer of the kernel model and no condition of the guard grammar; its condition reads a count of active founders over a margin (a named limit in CC 8.3.4)",
        shipped_source="tools/guard_grammar.py; manifests/transitions.json membership:{stage} attest guard"))
    E.append(stated("persist", "consent:partnership_grant, consent:partnership_accept", "fold:ratified_pair", "fold",
        ["seven_rankings item 2"], "CC 2.3.2.4",
        "this predicate is **consumer policy**, NOT registry-normative",
        "no claim and no model states the shipped rule", "no shipped value",
        "no claim, census cell or model records what the shipped store does with two halves, so there is no shipped verdict to compute"))
    E.append(stated("persist", "licensure:{authority_id}", "freshness.judged_at", "freshness", ["C372"], "CC 2.6.7",
        "is judged at its signed `asserted_at`", "receipt future-skew <=5 min, us resolution (check_instant_binding); no W",
        "time", "judging at a signed instant bounded by W is neither of the kernel's two notions of time (a row's own end, "
        "a window with a landing); KERNEL.md 5 leaves such clocks without a meaning", census=("licensure:{authority_id}", "8_freshness")))
    for impl in ("persist", "edge"):
        E.append(stated(impl, "transparency_log:cosigned:{tree_size}", "guard[accountable stream]", "door", ["C433"], "CC 5.3.3.11",
            'For accountable streams, "published" means **witness-cosigned**', "no signed member says a stream is accountable",
            "wire", "the guard needs a signed member stating the stream's profile; until the wire carries one no rule can read it",
            shipped_source="CC 8.10 card guard (text_conflicts C433)"))
    E.append(stated("persist", "(occurrence revocation, cosign:signature)", "attestation_id form", "door", ["C443"], "CC 3.1.3",
        "sha256(domain ‖ JCS(object))", "attestation_id typed uuid in manifests/signed_object.cddl", "wire",
        "how a 32-byte digest id folds to the uuid form is a byte form, not a row", shipped_source="manifests/signed_object.cddl uuid"))
    # ---- wording only: a claim's or a table's words differ and behaviour does not ------------------------------------
    for f in ["ledger:head:{unit}:{version}", "ledger:checkpoint:{unit}:{version}", "ledger:promotion:{version}"]:
        E.append(wording("persist", f, "reserved_rule", ["C363"], "CC 3.1.3",
            "**Yes:** the ledger's single owner (the steward-bound identity of its `ledger_id` triple); no delegate writes",
            "or a delegate under its declared serialization discipline",
            "the census reserved_rule words admit a delegate; its signer cell admits self only ('CC delegate arm: GAP'), so no row tells them apart",
            census=(f, "reserved_rule")))
    # ---- the head a row names, not a signed instant: a removal in the row's past signed at a later instant ------------
    def removed_later(act, leaf=None):
        """A group of three; C is removed by a count whose row is signed at 5; then an act by A and C names that
        removal as its head and is signed at 3. Over the head it names C is no member; as of its instant C still is."""
        kw = {"leaf": leaf} if leaf else {}
        return group() + [SEAT.unseat("u", "A", "C", "member", "g", "group", names=("g",), head=("g",), policy="strict",
                                      cosigners=("B",), at=5)] + [act(kw)]
    for f, leaf, srcs, cc, q, cen, sw, where in [
        ("group:roster", None, ["CLM-cosigned-rows"], "CC 2.4",
         "judged on the *receiver's own* fold over the members at the roster head the row names",
         ("group:roster", SIGNER[0]), "roster_member(at)", "cosign_rule count"),
        ("membership:{stage}", "widening", ["CLM-roster-event-fresh", "CLM-cosigned-rows"], "CC 3.3.4",
         "A widening or removal names the roster head it extends, and its signers are counted over the members at that head.",
         ("membership:{stage}", SIGNER[0]), "widening/removal: roster_member(at) cosigned", "roster event signers"),
    ]:
        rows = removed_later(lambda kw: fam("h", "A", f, ("u",), group="g", head=("u",), cosigners=("C",), at=3, **kw), leaf)
        E.append(signer_entry("persist", f, srcs, cc, q, [["count:protocol@group"]], [["count_at:protocol@group"]], sw,
                              rows, "h", census=cen, kind="count", where=where, leaf=leaf))
        E[-1]["note"] = "the removal is in the act's causal past and carries the later signed instant"
    E.append(lifecycle_entry("persist", "group:roster", ["CLM-cosigned-rows"], "CC 2.4.1.1",
        "counted over the members at the roster head the withdrawal names",
        [["count:protocol@group"]], [["count_at:protocol@group"]],
        "a cosigned withdraws admitted when its cosigners satisfy the protocol on the receiver's fold at the signed instant",
        group() + [fam("h0", "A", "group:roster", ("g",), group="g", head=("g",), cosigners=("B", "C")),
                   SEAT.unseat("u", "A", "C", "member", "g", "group", names=("g",), head=("g",), policy="strict", cosigners=("B",), at=5),
                   wd("x", "A", "h0", ("u",), group="g", head=("u",), cosigners=("C",), at=3)], "h0", census=None,
        where="lifecycle.withdraws_by[rule 0]",
        shipped_source="constitution/claims.tsv CLM-cosigned-rows (impl check_cosigned_withdraws, verify_roster_cosignatures)"))
    # ---- authority over the act's causal past, not at its signed instant ---------------------------------------------
    for f, scope, srcs, cc, q, where in [
        ("licensure:{authority_id}", "license", ["CLM-licence-judged-at-issuance"], "CC 2.4.1.3",
         "It is judged over the issuance's own causal past under the cosigned-row rule, never at receipt",
         "authority at issuance"),
        ("self:delegates_to", "moderate", ["CLM-licence-judged-at-issuance"], "CC 4.5.5",
         "for every act that has the withdrawal in its own past or is concurrent with it",
         "acts under a withdrawn delegates_to"),
    ]:
        rows = [SEAT.offer("dl", "Au", "D", scope, "Au", "self"), SEAT.accept("da", "D", "dl"), wd("w", "Au", "dl", at=9),
                fam("i", "D", f, ("da", "w"), authority="Au", delegate="E", at=5)]
        E.append(signer_entry("persist", f, srcs, cc, q, [["seat:%s@authority" % scope]], [["seat_at:%s@authority" % scope]],
            "authority judged at the row's signed asserted_at (licence_roots_at)", rows, "i", census=None, kind="door",
            where=where))
        E[-1]["shipped_source"] = "constitution/claims.tsv CLM-licence-judged-at-issuance (impl licence_roots_at)"
        E[-1]["note"] = "the withdrawal of the delegation is in the act's causal past and carries the later signed instant"
    # ---- the late acceptance: the concluding member's own clock against the proposal's own end -----------------------
    E.append(signer_entry("persist", "membership:{stage}", ["CLM-membership-consent"], "CC 3.1.3.2",
        "P's `expires_at` is P's own stated end, and a late acceptance is closed.",
        [["held_before_end:proposal"]], [["signed_before_end:proposal"]],
        "the acceptance's and the widening's signed instants compared with expires_at (check_growth_accepted)",
        [fam("pr", "A", "membership:{stage}", (), leaf="proposal", subjects=("K",), expires_at=10),
         fam("ac", "K", "membership:{stage}", ("pr",), leaf="acceptance", at=4),
         R("rc", "receipt", "A", ("ac",), at=9),
         fam("w", "A", "membership:{stage}", ("pr", "ac", "rc"), leaf="widening", proposal="pr", at=11)], "w",
        census=None, kind="window", where="invitation expiry", leaf="widening"))
    E[-1]["shipped_source"] = ("constitution/claims.tsv CLM-membership-consent (impl check_growth_accepted; the summary "
                               "before 4aa21dd: an undeclined, unexpired acceptance on signed instants)")
    E[-1]["note"] = "the member held the acceptance before the end on its own clock and signed the widening after it"
    # ---- a check that reads another row: the shipped door refuses, the text concludes nothing ------------------------
    refusals = [
        ("self:delegates_to", ["CLM-self-edge-not-cycle"], "CC 4.1.1",
         "the cycle-closing emission concludes nothing, and a walk visits a cycle once", [["acyclic"]],
         [fam("e1", "A", "self:delegates_to", (), delegate="B"), fam("e2", "B", "self:delegates_to", ("e1",), delegate="A")],
         "e2", None, "the cycle-closing delegates_to refused at admission (check_delegation_cycle_admission)",
         "constitution/claims.tsv CLM-self-edge-not-cycle (impl check_delegation_cycle_admission; the summary before 6e90792: still refused)"),
        ("licensure:{authority_id}", ["CLM-issuance-scope"], "CC 4.4.3.19",
         "**concludes nothing**, and is not merely unweighted", [["seat:license@root"]],
         [SEAT.offer("rt", "Rt", "Rt", "root", "@", "self"), fam("i", "D", "licensure:{authority_id}", ("rt",), root="Rt")],
         "i", None, "an issuance whose delegator lacks the authority refused at admission (check_licensure_delegator_is_authority)",
         "constitution/claims.tsv CLM-issuance-scope (impl check_licensure_delegator_is_authority)"),
        ("key_grant:{axis}", ["CLM-issuance-scope"], "CC 4.4.3.19",
         "**concludes nothing**, and is not merely unweighted", [["owner_of_subject"], ["seat:grant@subject"]],
         [fam("i", "D", "key_grant:{axis}", (), subject="S")],
         "i", None, "a grant whose delegator lacks the authority refused at admission (admit_replicated_key_grant)",
         "constitution/claims.tsv CLM-issuance-scope (impl admit_replicated_key_grant)"),
        ("takedown_notice:{basis}", ["CLM-takedown-notice-row"], "CC 4.5.3",
         "An immediate-removal basis asserted by a key that holds no `takedown` duty over the content concludes nothing",
         [["seat:takedown@group"]], community() + [U, fam("n", "U", "takedown_notice:{basis}", ("g", "ku"), group="g")],
         "n", ("takedown_notice:{basis}", "door"), "takedown_tombstone::check_takedown_notice_row_admission", None),
        ("age_assurance:{level}:{band}:{version}", ["C423"], "CC 3.4.11",
         "a row by any other signer concludes nothing at admission", [["seat:assure:age@root", "not_subject"]],
         [keyrec("ks", "S"), SEAT.offer("rt", "Rt", "Rt", "root", "@", "self"),
          fam("h", "S", "age_assurance:{level}:{band}:{version}", ("ks", "rt"), root="Rt", subject="S")],
         "h", ("age_assurance:{level}:{band}:{version}", "door"), "check_reserved_prefix_admission self arm", None),
        ("capacity_assurance:{level}:{domain}:{band}:{version}", ["CLM-nsproc-attestation-type-capacity-assurance"], "CC 3.4.12",
         "A row by any other signer concludes nothing at admission", [["seat:assure:capacity@root", "not_subject"]],
         [keyrec("ks", "S"), SEAT.offer("rt", "Rt", "Rt", "root", "@", "self"),
          fam("h", "S", "capacity_assurance:{level}:{domain}:{band}:{version}", ("ks", "rt"), root="Rt", subject="S")],
         "h", ("capacity_assurance:{level}:{domain}:{band}:{version}", "door"), "self arms in check_reserved_prefix_admission", None),
    ]
    for f, srcs, cc, q, gate, rows, tgt, cen, sw, src in refusals:
        E.append(signer_entry("persist", f, srcs, cc, q, gate, gate, sw, rows, tgt, census=cen, kind="door",
                              where="admission refusal"))
        E[-1]["shipped_param"]["refuse"] = ["gate_fails"]
        if src: E[-1]["shipped_source"] = src
    E.append(wording("persist", "(tombstoned record)", "purge_tombstoned", ["CLM-purge-whole-or-not"], "CC 4.5.3",
        "A node does not hold a tombstoned record again and never serves it", "a tombstoned record is refused at every admission door and never served",
        "not holding the bytes again and refusing them at the door have one outward effect; the reason reported is purge_tombstoned in both",
        shipped_source="constitution/claims.tsv CLM-purge-whole-or-not (impl refuse_if_tombstoned_attestation; the summary before 6e90792)"))
    return E
