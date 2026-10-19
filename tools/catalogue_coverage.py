#!/usr/bin/env python3
"""
CC — does the CSD/4 catalogue exercise the states the formal definition reaches?

The forward gate (closure.json) asks: does every atom a catalogue entry promises have a plane
model behind it. This is the reverse gate, the one the steward set before the catalogue may be
pushed (2026-10-18): of the states formal/STATE_TABLE.tsv names and a model constrains, which
does NO catalogue entry exercise? A state is exercised when some vocabulary atom that implies it
(the table's `atoms` column) is promised by some entry in formal/cewp_node/catalog/.

Prints coverage by plane, the modelled-but-unexercised states, and the entries that would close
them (the proposal list, maintained by hand below so it stays a proposal). Exit 0 always; CI
records, it does not fail, because exhaustiveness is the steward's call.
Run: python3 tools/catalogue_coverage.py [--json]
"""
import csv, glob, json, os, sys, collections
try:
    import yaml
except ImportError:
    sys.exit("catalogue_coverage: PyYAML required")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = os.path.join(ROOT, "formal", "STATE_TABLE.tsv")
VOC = os.path.join(ROOT, "manifests", "topology_vocabulary.json")
CAT = os.path.join(ROOT, "formal", "cewp_node", "catalog")

# Entries that would close the unexercised modelled states, as a proposal to the catalogue's
# owner (CIRISServer) and the steward. Each names the plane states it reaches.
PROPOSED = [
    ("T10", "A stolen device: the owner evicts it by the quorum path", ["key.holder=owner", "key.holder=thief", "key.membership=proposed_evict", "key.membership=evicted", "self.roster_size=three_or_more"]),
    ("T11", "Two lost devices: recovery by the lone path over the window", ["key.holder=lost", "key.membership=evicted", "self.roster_size=one"]),
    ("T12", "A root stalls (a founder resigns below the margin) and recovers by a conferred human", ["root.standing=Stalled", "root.liveness=stalled", "root.liveness=live", "seat.identity_type=human"]),
    ("T13", "A witnessed lineage: a stale head refuses attach, a fresh head admits; a node-bearing seat never counts", ["root.head=stale", "seat.identity_type=node_bearing"]),
    ("T14", "Consent end to end: grant, capture, revoke as a boundary, expiry, decay to complete; replication grant and its withdrawal", ["consent.state=granted", "consent.state=revoked", "consent.state=expired", "consent.decay=identity_severed", "consent.decay=patterns_anonymized", "consent.decay=complete", "consent.community_trust=granted", "consent.community_trust=bounded", "consent.replication=none"]),
    ("T15", "A community's ceremony: decline, removal, resignation; a moderator lapses, merit-promotes, and a room fails secure", ["member.stage=proposed", "member.stage=accepted_awaiting_group", "member.stage=declined", "member.stage=removed", "member.stage=resigned", "group.moderator=lapsed", "group.moderator=merit_promoted", "group.moderator=fail_secure", "group.federating=no"]),
    ("T16", "An agent retired under the Standard: decided, objection window, frozen, secrets destroyed, handed over, notified, custodian minted, retired; a subject withdrawal inside the record", ["agent.bond=unbound", "agent.bond=lapsed", "agent.retirement=decided", "agent.retirement=frozen", "agent.retirement=secrets_destroyed", "agent.retirement=handed_over", "agent.retirement=notified", "agent.retirement=custodian_minted", "agent.retirement=retired", "agent.halt_gate=acting"]),
    ("T17", "A takedown and a steward purge: tombstone by digest, the dwell, a withheld blob; family and community scope content", ["row.standing=admitted", "row.standing=tombstoned", "blob.custody=purged", "row.scope=family", "row.scope=community"]),
    ("T18", "Delegation ends: a withdrawal cascades, a term expires, a grant held and rotated; a guardian bond made and absent", ["delegation.link=withdrawn", "delegation.link=expired", "grant.state=held", "guardian.bond=none"]),
    ("T19", "A holder under coercion and censorship: the standing rule holds; an announced node", ["root.holder_disposition=honest", "root.holder_disposition=coerced", "root.holder_disposition=censored", "root.holder_disposition=lost", "node.announce=announced", "key.revocation=revoked_after", "key.revocation=revoked_all", "key.revocation=none"]),
]


def main():
    st = list(csv.DictReader(open(ST, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))
    voc = json.load(open(VOC, encoding="utf-8"))["atoms"]
    promised = {}
    for f in sorted(glob.glob(os.path.join(CAT, "T*.yaml"))):
        e = yaml.safe_load(open(f, encoding="utf-8"))
        for a in e.get("promises", []):
            promised.setdefault(a, []).append(e["catalog_id"])
    by_plane = collections.OrderedDict()
    unexercised = []
    for r in st:
        atoms = [a for a in r["atoms"].split() if a != "—"]
        ex = any(a in promised for a in atoms)
        by_plane.setdefault(r["plane"], [0, 0, 0])
        by_plane[r["plane"]][1] += 1
        if ex:
            by_plane[r["plane"]][0] += 1
        elif r["status"] in ("modelled", "modelled-partial"):
            by_plane[r["plane"]][2] += 1
            unexercised.append(f"{r['variable']}={r['state']}")
    tot = len(st); ex = sum(v[0] for v in by_plane.values())
    covered_by_proposal = set(s for _, _, ss in PROPOSED for s in ss)
    still = [s for s in unexercised if s not in covered_by_proposal]
    out = {"states": tot, "exercised": ex, "modelled_unexercised": len(unexercised),
           "by_plane": {p: {"exercised": v[0], "states": v[1], "modelled_unexercised": v[2]} for p, v in by_plane.items()},
           "unexercised_modelled_states": unexercised,
           "proposed_entries": [{"id": i, "title": t, "closes": ss} for i, t, ss in PROPOSED],
           "still_unclosed_after_proposal": still,
           "vocabulary_atoms_promised_by_no_entry": sorted(a for a in voc if a not in promised)}
    if "--json" in sys.argv:
        print(json.dumps(out, indent=1, ensure_ascii=False)); return
    print(f"catalogue coverage: {ex}/{tot} states exercised by T0–T9; {len(unexercised)} modelled states unexercised")
    for p, v in by_plane.items():
        print(f"  {p:11} {v[0]:2}/{v[1]:2} exercised, {v[2]:2} modelled-but-unexercised")
    print(f"proposed entries T10–T19 would close {len(covered_by_proposal & set(unexercised))} of {len(unexercised)}; still open: {still}")
    print("atoms promised by no entry:", out["vocabulary_atoms_promised_by_no_entry"])


if __name__ == "__main__":
    main()
