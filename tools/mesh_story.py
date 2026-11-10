#!/usr/bin/env python3
"""The mesh story, end to end and executable: one scripted life of a mesh, run as a sequence of
(view, standing) -> queue -> chosen item -> row -> next view steps over the derived data of this
repository, and checked at every step against the rule of CC 4.5.13 and formal/event_lifecycle:
the queue is the door run forwards.

Inputs (all generated artefacts of this repo):
  manifests/transitions.json      the transitions of every family (from the family model)
  manifests/governance_policy.json the five numbers per door
  manifests/topology_vocabulary.json the atoms a view carries
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

def enabled(family, state, roles):
    out = []
    for t in transitions(family):
        if t["from"] != state:
            continue
        need = t["roles"]["value"]
        if not need:
            continue  # a gap or a held-shut family: closed to everyone
        if any(r in need for r in roles) or ("registered" in need and roles):
            out.append(t)
    return out

def item(t, obj):
    return {"kind": "choice", "verb": t["verb"], "writes": {"family": obj["family"], "verb": t["verb"], "to": t["to"]},
            "policy": t["policy"]["value"], "confirm": bool(t["widens"]["value"])}

class Story:
    def __init__(self):
        self.steps = []; self.objects = {}; self.rows = []

    def new(self, oid, family, state="none", atoms=None):
        self.objects[oid] = {"id": oid, "family": family, "state": state, "atoms": atoms or {}}
        return self.objects[oid]

    def step(self, who, roles, oid, verb, note):
        obj = self.objects[oid]
        q = [item(t, obj) for t in enabled(obj["family"], obj["state"], roles)]
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
    s.new("bind:bob", "transport:{kind}"); s.step("bob", ["self", "registered"], "bind:bob", "attest", "Bob announces a device: his binding at federation scope")
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
    return s

def check(s):
    errs = []
    for st in s.steps:
        if st["chosen"] and st["chosen"] not in st["queue"]:
            errs.append(f"step {st['n']}: chosen item not in queue")
        if st["refused"] and st["note"].lower().find("refused") < 0 and st["note"].lower().find("tries") < 0:
            errs.append(f"step {st['n']}: refused but the story expected admission: {st['note']}")
        if not st["standing"] and st["queue"]:
            errs.append(f"step {st['n']}: a stranger was served a queue")
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
