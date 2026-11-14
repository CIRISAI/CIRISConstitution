#!/usr/bin/env python3
"""The mesh story, end to end and executable: one scripted life of a mesh, run as a sequence of
(view, standing) -> queue -> chosen item -> row -> next view steps over the derived data of this
repository, and checked at every step against the rule of CC 4.5.13 and formal/event_lifecycle:
the queue is the door run forwards.

Inputs (all generated artefacts of this repo):
  manifests/transitions.json      the transitions of every family (from the family model)
  manifests/governance_policy.json the five numbers per door
  manifests/topology_vocabulary.json the atoms a view carries
A family whose signer the text gives per stage or leaf (manifests/transitions.json, `stages`) is
served by the stage the object's view names in its `stage` atom.
Output:
  manifests/mesh_story_trace.json  the trace a renderer (CEWPOS's scene) replays: per step the
                                    view (object, state, atoms), the actor's standing, the queue
                                    served, the item chosen, the row written, the next view.

  python3 tools/mesh_story.py           # writes the trace and prints the story
  python3 tools/mesh_story.py --check   # exit 1 if the committed trace is stale or a step breaks the rule
"""
import json, sys, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TR = json.loads((ROOT / "manifests" / "transitions.json").read_text())
GP = json.loads((ROOT / "manifests" / "governance_policy.json").read_text())
OUT = ROOT / "manifests" / "mesh_story_trace.json"

FAM = {r["family"]: r for r in TR["rows"]}

def transitions(family):
    return FAM[family]["transitions"] if family in FAM else []

def stage_of(cell, atoms):
    """A cell that carries `stages` answers a view that knows its stage from the stage; else from its value."""
    stages = cell.get("stages") or {}
    return stages.get((atoms or {}).get("stage"), cell["value"])

def enabled(family, state, roles, atoms=None):
    out = []
    for t in transitions(family):
        if t["from"] != state:
            continue
        need = stage_of(t["roles"], atoms)
        if not need:
            continue  # a gap, a held-shut family or a stage closed to everyone
        if "not_subject" in t["roles"].get("conditions", []) and "subject" in roles:
            continue  # the signer rule's condition: never the row's own subject
        if any(r in need for r in roles) or ("registered" in need and roles):
            out.append(t)
    return out

def item(t, obj):
    return {"kind": "choice", "verb": t["verb"], "writes": {"family": obj["family"], "verb": t["verb"], "to": t["to"]},
            "policy": stage_of(t["policy"], obj["atoms"]), "confirm": bool(t["confirm"]["value"])}

class Story:
    def __init__(self):
        self.steps = []; self.objects = {}; self.rows = []

    def new(self, oid, family, state="none", atoms=None):
        self.objects[oid] = {"id": oid, "family": family, "state": state, "atoms": atoms or {}}
        return self.objects[oid]

    def step(self, who, roles, oid, verb, note):
        obj = self.objects[oid]
        q = [item(t, obj) for t in enabled(obj["family"], obj["state"], roles, obj["atoms"])]
        chosen = next((i for i in q if i["verb"] == verb), None)
        refused = chosen is None
        row = None
        if not refused:
            row = {"id": f"row{len(self.rows)+1}", "family": obj["family"], "verb": verb, "signer": who, "object": oid}
            self.rows.append(row)
            obj["state"] = chosen["writes"]["to"]
            obj["atoms"][f"last_{verb}_by"] = who
        self.steps.append({"n": len(self.steps)+1, "note": note, "actor": who, "standing": roles,
                           "view": {"object": oid, "family": obj["family"], "state_before": self.steps[-1]["view"]["state_after"] if self.steps and self.steps[-1]["view"]["object"] == oid else None,
                                    "state_after": obj["state"], "atoms": dict(obj["atoms"])},
                           "queue": [i["verb"] for i in q], "chosen": verb if not refused else None,
                           "refused": refused, "row": row})
        return not refused

def run():
    s = Story()
    # 1. genesis: a founder authorizes the trust root's charter; the other two cosign under the accord's quorum
    s.new("root", "trust:{job}:{version}")
    s.step("alice", ["self", "holder", "founder"], "root", "authorize", "Three people sit down: a founder authorizes the trust root's charter; the other two cosign under the accord's quorum")
    # 2. a person makes a key and announces a device
    s.new("key:bob", "key:record"); s.step("bob", ["self"], "key:bob", "attest", "Bob makes a key: the key record is his own")
    s.new("bind:bob", "identity:occurrence"); s.step("bob", ["self", "registered"], "bind:bob", "attest", "Bob announces a device: his binding at federation scope")
    # 3. a stranger reaches bob: a contact request he accepts
    s.new("contact:carol-bob", "consent:{kind}"); s.step("carol", ["self", "registered"], "contact:carol-bob", "attest", "Carol asks to be a contact; her request is her own row")
    # 4. a room is founded and grows by proposal and acceptance
    s.new("room:1", "group:roster"); s.step("bob", ["founder", "member"], "room:1", "attest", "Bob founds a room: the roster's first version")
    s.new("invite:dave", "membership:{stage}"); s.step("bob", ["member", "founder"], "invite:dave", "attest", "Bob proposes Dave; the second voice is Dave's own acceptance")
    # 5. a post, a stranger's attempt, a recant, a moderator's withhold, the room's objection
    s.new("post:1", "chat:*"); s.step("dave", ["member", "registered"], "post:1", "attest", "Dave posts in the room")
    s.step("erin", [], "post:1", "withdraw", "A stranger tries to withdraw Dave's post: no standing, no item, refused")
    s.new("post:2", "chat:*"); s.step("dave", ["member", "registered"], "post:2", "attest", "Dave posts again")
    s.new("flag:post2", "moderation:{allegation_type}"); s.step("frank", ["moderate", "member"], "flag:post2", "attest", "Frank, the room's moderator, withholds the second post: one signature, the window decides")
    s.new("obj:flag", "objection:{state}"); s.step("carol", ["member", "registered"], "obj:flag", "attest", "Carol objects to the withhold: a vote row under the two-path policy")
    s.step("dave", ["author", "member"], "post:1", "recant", "Dave recants his first post: one step, no window")
    # 6. an agent's own row, signed by the agent
    s.new("trace:1", "trace:{form}:{version}"); s.step("agent:bob", ["self"], "trace:1", "attest", "Bob's agent signs its own trace")
    # 7. the author withdraws a consent: forward only
    s.step("carol", ["author"], "contact:carol-bob", "withdraw", "Carol withdraws her contact consent: her own forward-only act")
    more(s)
    return s

def more(s):
    """The families whose signer the text names: each one admitted from the standing the text gives,
    and refused from a standing it does not."""
    def one(oid, family, who, roles, note, verb="attest", stage=None):
        if oid not in s.objects: s.new(oid, family, atoms={"stage": stage} if stage else None)
        return s.step(who, roles, oid, verb, note)
    # 8. what a device's edge says of itself is the edge's to say
    one("own:edge-bob", "ownership:{relation}:{target_kind}:{version}", "erin", [], "A stranger tries to bind Bob's device as its owner: no standing, refused", verb="authorize")
    one("own:edge-bob", "ownership:{relation}:{target_kind}:{version}", "bob", ["owner"], "Bob binds his device as its owner, the device's own key signing too: the binding confers the duty to report", verb="authorize")
    one("link:bob", "transport:{kind}", "bob", ["self", "registered"], "Bob tries to sign a transport report for his own device: refused, the report is the edge's own")
    one("link:bob", "transport:{kind}", "edge:bob", ["infra:attest"], "The edge on Bob's device reports its own link, under the duty its owner conferred")
    one("deliver:bob", "delivery:{class}", "edge:bob", ["infra:attest"], "The edge reports what it delivered")
    one("reach:bob", "peer_reachability:{network}", "edge:bob", ["infra:attest"], "The edge reports which peers it can reach")
    one("boundary:bob", "key_boundary:{scope}", "edge:bob", ["infra:attest"], "The edge reports where its keys stop")
    one("label:bob", "device:label", "dave", ["member", "registered"], "Dave tries to name Bob's phone: refused, a device's name is its owner's")
    one("label:bob", "device:label", "bob", ["owner"], "Bob names his phone: the owner's row, and it stays in his own circle")
    # 9. a person's own rows: a file, a folder, a route, an observation, a receipt
    one("file:1", "file:{version}", "dave", ["self"], "Dave saves a file: its author's row")
    one("folder:1", "collection:{kind}", "dave", ["self"], "Dave makes a folder: its creator's row")
    one("receipt:1", "delivery_receipt:{stream_id}", "erin", [], "A stranger tries to acknowledge a chunk of the room's stream: refused, a receipt is a member's")
    one("receipt:1", "delivery_receipt:{stream_id}", "dave", ["member"], "Dave acknowledges a chunk of the room's stream: a current member's receipt")
    one("grant:key", "key_grant:{axis}", "erin", [], "A stranger tries to wrap the room's key to herself: refused, a wrap is the sealer's")
    one("grant:key", "key_grant:{axis}", "bob", ["member", "owner"], "Bob wraps the room's key to Dave: the sealer's row")
    one("route:1", "rendezvous:route", "rendezvous:carol", ["self"], "A fresh rendezvous key publishes its own route: attester and subject are the one key")
    one("probe:1", "observation:reachability", "monitor", ["self"], "A monitoring node records what it saw from where it stands")
    one("probe:2", "observation:access_assumption", "monitor", ["self"], "The monitoring node records what its probe assumes about access")
    one("build:1", "provenance:build_manifest:{target}", "pipeline", ["registered"], "A build pipeline signs the manifest of what it built; the reader judges its standing")
    one("build:2", "provenance:build_manifest:{target}:locale:{lang_code}", "pipeline", ["registered"], "The pipeline signs the manifest of one language's build")
    # 10. a deferral, and the seat that answers it
    one("defer:1", "deferral:request", "agent:bob", ["self"], "Bob's agent defers a question it should not decide alone")
    one("seat:grace", "trust:{job}:{version}", "bob", ["self", "steward"], "Bob, the agent's steward, seats Grace over the agent's deferrals: his own delegation, bearing the answering as its scope", verb="authorize")
    one("answer:1", "deferral:response:{outcome}", "agent:bob", ["self"], "The agent tries to answer its own deferral: refused, no seat is the agent's to hold over itself")
    one("answer:1", "deferral:response:{outcome}", "dave", ["member", "registered"], "Dave, whom nobody seated, tries to answer: refused as unseated")
    one("answer:1", "deferral:response:{outcome}", "grace", ["wa"], "Grace answers from the seat Bob conferred")
    one("defer:2", "deferral:request", "agent:bob", ["self"], "The agent defers again")
    one("answer:2", "deferral:response:{outcome}", "bob", ["steward"], "Bob answers this one himself: the conferrer keeps the duty he delegates")
    # 11. consent between a person and an agent
    one("partner:grant", "consent:partnership_grant", "dave", ["member", "registered"], "Dave tries to grant Carol's partnership for her: refused, the grant is her own")
    one("partner:grant", "consent:partnership_grant", "carol", ["self"], "Carol offers Bob's agent a partnership: her own grant")
    one("partner:accept", "consent:partnership_accept", "carol", ["registered"], "Carol tries to accept for the agent: refused, the acceptance is the other side's")
    one("partner:accept", "consent:partnership_accept", "agent:bob", ["self"], "The agent accepts: the producer's own row")
    one("scope:carol", "consent:scope:{kind}", "carol", ["self"], "Carol says what the partnership may be used for")
    one("stream:carol", "consent:stream:{kind}", "carol", ["self"], "Carol grants a bundle of her streams")
    one("sla:agent", "consent:deletion_sla:{days}", "agent:bob", ["self"], "The agent commits to how fast it deletes")
    one("partner:grant", "consent:partnership_grant", "carol", ["author"], "Carol withdraws the partnership: forward only", verb="withdraw")
    one("decay:agent", "consent:decay:{stage}", "agent:bob", ["self"], "The agent reports the decay of what it held, stage by stage")
    one("deleted:agent", "consent:deletion_complete", "carol", ["subject", "registered"], "Carol tries to sign that the deletion is done: refused, that report is the producer's")
    one("deleted:agent", "consent:deletion_complete", "agent:bob", ["self"], "The agent reports the deletion complete")
    one("trust:node", "consent:{kind}", "dave", ["self", "registered"], "Dave tries to grant the capture of Bob's node's traces: refused, that grant is the node owner's", stage="community_trust")
    one("trust:node", "consent:{kind}", "bob", ["owner"], "Bob grants it for the node he owns", stage="community_trust")
    one("summary:1", "trace_summary:{kind}", "agent:bob", ["self"], "The agent signs a summary of its own trace")
    # 12. a count nobody can read alone
    one("census:return", "census:share:{class}", "node:bob", ["self"], "Bob's node returns its share of the census to a serve seat")
    one("census:sum", "census:partial:{class}", "bob", ["self", "registered"], "Bob tries to publish a seat's sum: refused, a sum is a serve seat's")
    one("census:sum", "census:partial:{class}", "seat:1", ["serve"], "A serve seat publishes the sum of the shares it accepted")
    one("census:total", "census:composite:{class}", "seat:1", ["serve"], "The seat publishes the count the two sums make")
    one("cell:dave", "census:member:share", "dave", ["member"], "Dave sends his community cell to a tally member, as every member does every period")
    one("room:sum", "census:member:partial", "dave", ["member"], "Dave tries to publish a tally member's sum: refused, he was not drawn")
    one("room:sum", "census:member:partial", "carol", ["member", "tally"], "Carol, drawn as a tally member, publishes her sum into the room")
    one("room:active", "census:expected_active", "carol", ["member", "tally"], "Carol publishes how many members the room expects to be active")
    one("poll:1", "ballot:tally:{poll_id}", "carol", ["member", "tally"], "Carol publishes a poll's tally")
    # 13. the room elects its moderator
    one("vote:dave", "ballot:moderator", "erin", [], "A stranger tries to cast a ballot for moderator: refused, a ballot is a live member's")
    one("vote:dave", "ballot:moderator", "dave", ["member"], "Dave ranks his choices for moderator")
    one("vote:carol", "ballot:moderator", "carol", ["member"], "Carol casts her ballot")
    one("vote:carol", "ballot:moderator", "carol", ["author"], "Carol withdraws her ballot: her own act, counted as withdrawn", verb="withdraw")
    one("seat:moderator", "ballot:moderator_acceptance", "dave", ["member"], "Dave tries to accept the seat: refused, the count did not yield him")
    one("seat:moderator", "ballot:moderator_acceptance", "frank", ["member", "winner"], "Frank, whom the count yields, accepts and binds the ballots he was seated on")
    one("listing:1", "community:listing", "dave", ["member"], "Dave tries to list the room: refused, a listing is signed by a holder of the room's moderate duty")
    one("listing:1", "community:listing", "frank", ["member", "moderate"], "Frank, who holds the moderate duty, lists the room")
    # 14. a row that needs more than one signature
    one("act:1", "cosign:{state}", "erin", [], "A stranger tries to open a cosigned act in the room: refused", stage="pending")
    one("act:1", "cosign:{state}", "bob", ["member"], "Bob opens a cosigned act: his pending row, served to the room's active members", stage="pending")
    one("act:1:dave", "cosign:{state}", "dave", ["member"], "Dave adds his signature", stage="signature")
    one("act:1:dave", "cosign:{state}", "dave", ["author"], "Dave tries to take his signature back: refused, a signature given stays given", verb="withdraw", stage="signature")
    one("act:2", "cosign:{state}", "bob", ["member"], "Bob opens another", stage="pending")
    one("act:2", "cosign:{state}", "bob", ["author"], "Bob withdraws the pending act while it is still short", verb="withdraw", stage="pending")
    # 15. a node becomes a witness of the lineage
    one("witness:ask", "lineage_witness:{stage}", "carol", ["owner"], "Carol tries to propose her own node as a witness: refused, a proposal is a founder's", stage="proposal")
    one("witness:ask", "lineage_witness:{stage}", "alice", ["founder"], "Alice, a founder, proposes Carol's node as a witness of the lineage", stage="proposal")
    one("witness:answer", "lineage_witness:{stage}", "alice", ["founder"], "Alice tries to accept for the node: refused, the answer is the owner's and never a founder's", stage="acceptance")
    one("witness:answer", "lineage_witness:{stage}", "carol", ["owner"], "Carol, the node's owner, accepts", stage="acceptance")
    # 16. a key is revoked by itself
    one("revoke:dave", "key:revocation", "frank", ["moderate", "member"], "Frank tries to revoke Dave's key: refused, the key is not his", stage="self")
    one("revoke:dave", "key:revocation", "dave", ["self"], "Dave retires an old key under that key's own signature: recognised because the revoker is the key")
    # 17. an agent is retired, and its record handed over
    one("retire:decided", "retirement:{state}", "bob", ["steward"], "Bob tries to sign the agent's retirement row: refused, up to retired the row is the agent's own", stage="until_retired")
    one("retire:decided", "retirement:{state}", "agent:bob", ["self"], "The agent signs its own retirement row", stage="until_retired")
    one("preserve:ask", "preserve_request", "agent:bob", ["self"], "The agent signs the request to preserve its record, naming the operator and the period", stage="until_retired")
    one("preserve:answer", "preserve_response", "agent:bob", ["self"], "The agent tries to answer its own request: refused, the answer is the operator's")
    one("preserve:answer", "preserve_response", "heidi", ["operator"], "Heidi, the operator the request names, accepts")
    one("custody:1", "retirement:{state}", "agent:bob", ["self"], "After retired, the agent's key tries a custody row: refused, those are the listed custodian's", stage="after_retired")
    one("custody:1", "retirement:{state}", "ivan", ["custodian"], "Ivan, the custodian the retired row lists, signs the custody row", stage="after_retired")
    one("preserve:revised", "preserve_request", "ivan", ["custodian"], "Ivan revises the request: after retired, revisions are the custodian's", stage="after_retired")
    one("custody:2", "retirement:{state}", "ivan", ["custodian"], "Ivan tries to name his own successor: refused, a replacement is the operator's and the Wise Authority's", stage="custodian_replace")
    one("custody:2", "retirement:{state}", "heidi", ["operator"], "Heidi and Grace name a successor in one cosigned row", stage="custodian_replace")
    one("seal:open", "archive_release:{basis}", "heidi", ["operator"], "Heidi tries to open the seal: refused, only a Wise Authority's row opens it")
    one("seal:open", "archive_release:{basis}", "grace", ["wa"], "Grace opens the seal for one person's request")
    one("order:1", "lawful_order:release", "grace", ["wa"], "Grace tries to record a lawful order to release: refused, that record is the steward's")
    one("order:1", "lawful_order:release", "bob", ["steward"], "Bob records the order under his own name")
    # 18. what the text does not yet say stays shut
    one("duty:1", "duty:{kind}", "bob", ["self", "registered"], "Bob tries to state a duty: refused, the family names no signer, so the transition is shut to everyone")
    # 19. revoking an occurrence: a person's by the count of the person's own roster, a node's by its key or its owner
    one("unbind:1", "identity:occurrence_revocation", "bob", ["self", "owner"], "Bob tries to carry alone a framed revocation of his old phone: refused, a person's occurrence is revoked by a strict majority of the person's own roster", stage="user_self")
    one("unbind:1", "identity:occurrence_revocation", "bob", ["member"], "Bob's own roster carries the revocation of his old phone: a strict majority of his live keys", stage="user_self")
    one("unbind:2", "identity:occurrence_revocation", "bob", ["owner"], "Bob revokes the occurrence of his node: its owner", stage="node_or_agent")
    # 20. the accord holders re-bind a seated serve node's transport destination
    one("rebind:1", "transport:canonical_rebind", "bob", ["owner", "registered"], "Bob tries to re-bind his serve node's transport destination: refused, a re-bind is the accord holders' act")
    one("rebind:1", "transport:canonical_rebind", "alice", ["holder"], "The accord holders re-bind the serve node's transport destination, cosigned at the charter's threshold")
    one("rebind:1", "transport:canonical_rebind", "alice", ["holder"], "A later re-bind by the holders supersedes the first: again their cosigned act, never one holder's", verb="supersede")

def check(s):
    errs = []
    for st in s.steps:
        if st["chosen"] and st["chosen"] not in st["queue"]:
            errs.append(f"step {st['n']}: chosen item not in queue")
        if st["refused"] and st["note"].lower().find("refused") < 0 and st["note"].lower().find("tries") < 0:
            errs.append(f"step {st['n']}: refused but the story expected admission: {st['note']}")
        if not st["standing"] and st["queue"]:
            errs.append(f"step {st['n']}: a stranger was served a queue")
    # every family whose signer or cell the text states is admitted at least once in the story
    told = set()
    for name in ("signer_rule_text.tsv", "transition_text.tsv"):
        for l in (ROOT / "formal" / "derivation" / name).read_text().split("\n"):
            if l and not l.startswith("#") and not l.startswith("family\t") and l.split("\t")[2:3] != ["undo"]:
                told.add(l.split("\t")[0])   # an undo row states a way back, not a signer
    for fam in sorted(told - {r["family"] for r in s.rows}):
        errs.append(f"{fam}: the text names its signer and no step of the story signs it")
    return errs

def main():
    s = run(); errs = check(s)
    out = {"_meta": {"rule": TR["_meta"]["rule"], "transitions_sha256": hashlib.sha256((ROOT/"manifests"/"transitions.json").read_bytes()).hexdigest(),
                     "policy_sha256": GP["_meta"]["policy_sha256"], "steps": len(s.steps), "rows": len(s.rows), "errors": errs},
           "steps": s.steps}
    js = json.dumps(out, indent=1, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        ok = not errs and OUT.exists() and OUT.read_text() == js
        print("mesh story: current and every step keeps the rule" if ok else f"mesh story: stale or broken ({errs})")
        sys.exit(0 if ok else 1)
    OUT.write_text(js)
    for st in s.steps:
        print(f"{st['n']:2d} {'REFUSED' if st['refused'] else 'ok     '} {st['actor']:10s} {st['view']['family'][:24]:24s} queue={st['queue']}  {st['note']}")
    if errs: print("ERRORS:", errs); sys.exit(1)
    print(f"mesh story: {len(s.steps)} steps, {len(s.rows)} rows, no step breaks the rule")

if __name__ == "__main__":
    main()
