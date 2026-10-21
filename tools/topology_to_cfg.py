#!/usr/bin/env python3
"""
CC — one CSD/4 catalogue entry, every plane model's constants (CIRISConstitution#131 §1).

Reads a catalogue entry (CIRISServer FSD/TOPOLOGY.md shape; vendored copies under
formal/cewp_node/catalog/) and writes, under formal/cewp_node/generated/<Tn>/:

  trust_root_<root>.cfg      TrustRootVerdict constants for each infrastructure root
                             (Founders / NodeKeys / Witnesses / M / K / AttachWindow / MaxT);
                             a root with no witness directory is witnessed-mode-off, which the
                             model does not cover (residual E): the cfg is still written, marked.
  accord_halt_<root>.cfg     AccordHalt (row mode) and accord_fuse_<root>.cfg AccordHaltFuse:
                             Holders = the seated holders, Nodes = the entry's nodes, Subscribed =
                             the nodes that accept the root.
  self_roster_<person>_{stolen,lost}.cfg
                             SelfRoster for every person: Devices = owned + one spare, Initial =
                             the devices held before any join relation, combined mode, W=2.
  root_reach.cfg             RootReach over the entry's nodes.
  MeshNet_<Tn>.tla + mesh_net.cfg
                             a wrapper instantiating MeshNet with the entry's persons, nodes
                             (canonicals are servers), owner map and up to two blobs.
  closure.json               the entry's promised atoms mapped through
                             manifests/topology_vocabulary.json to a state predicate and the plane
                             model that constrains it (or "no model"), plus what was generated.

The same entry feeds TLC (exhaustive over each plane machine) and the server harness (one trace
on the implementation); the row export the harness writes is what a trace check replays.
Deterministic; CI regenerates and diffs. Needs PyYAML.
Run:  python3 tools/topology_to_cfg.py --all     |  python3 tools/topology_to_cfg.py <entry.yaml>
"""
import json, math, os, re, sys
try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("topology_to_cfg: PyYAML required (pip install pyyaml)")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "formal", "cewp_node", "catalog")
OUT = os.path.join(ROOT, "formal", "cewp_node", "generated")
VOC = json.load(open(os.path.join(ROOT, "manifests", "topology_vocabulary.json"), encoding="utf-8"))
PLANE_MODEL = {"root": "trust_root / accord_halt / accord_roster", "node": "mesh_net.RootReach / guarantees (subscription, latch)",
               "self": "self_roster", "membership": "mesh_net (moderation, cohorts) — ceremony: no model",
               "consent": "no model (withdraws_admission covers erasure only)", "content": "mesh_net",
               "authority": "authority_tree", "agent": "guarantees", "harness": "—"}


def ident(s):
    return re.sub(r"[^A-Za-z0-9_]", "_", str(s))


def tla_set(xs):
    return "{" + ", ".join(xs) + "}"


def consts_line(names):
    return "  ".join(f"{n} = {n}" for n in names)


def gen(entry_path):
    e = yaml.safe_load(open(entry_path, encoding="utf-8"))
    tid = e["catalog_id"]
    topo = e.get("topology", {})
    odir = os.path.join(OUT, tid)
    os.makedirs(odir, exist_ok=True)
    for old in os.listdir(odir):
        os.remove(os.path.join(odir, old))
    written, notes = [], []
    roots = topo.get("roots", [])
    nodes = [n["id"] for n in topo.get("nodes", [])]
    canon = [c["id"] for c in topo.get("canonicals", [])]
    persons = topo.get("persons", [])
    rels = topo.get("relations", [])

    def w(name, text):
        open(os.path.join(odir, name), "w", encoding="utf-8").write(text)
        written.append(name)

    # ---- roots: trust_root + accord_halt ----
    for r in roots:
        rid = ident(r["id"])
        if r.get("kind") == "infrastructure":
            f = r.get("founders", {})
            seated, conf, nb = int(f.get("seated", 0)), int(f.get("conferrable", 0)), int(f.get("node_bearing", 0))
            humans = [f"f{i}" for i in range(1, seated + conf + 1)]
            nkeys = [f"n{i}" for i in range(1, nb + 1)]
            M = int(r.get("quorum", 2))
            wit = r.get("witnesses", {}) or {}
            wn = int(wit.get("n", 0))
            K = wn // 2 + 1 if wn else 0
            ch = r.get("charter", {}) or {}
            aw = ch.get("attach_window_secs"); cad = ch.get("witness_cadence_secs")
            attach = math.ceil(aw / cad) if aw and cad else 2
            witnesses = [f"w{i}" for i in range(1, wn + 1)]
            mark = "" if wn else "\\* witnessed mode OFF (no witness directory declared): TrustRootVerdict needs K >= 1; residual E in review/notes/formal_closure_rc9_2026-10-18.md — cfg written for the record, not run\n"
            if not wn:
                notes.append(f"root {r['id']}: witnessed mode off; trust_root model not applicable until extended (residual E)")
            txt = (f"\\* generated from {os.path.basename(entry_path)} root {r['id']} by tools/topology_to_cfg.py\n{mark}"
                   "SPECIFICATION Spec\nSYMMETRY Symm\nCONSTANTS\n"
                   f"    Founders = {tla_set(humans + nkeys)}\n    NodeKeys = {tla_set(nkeys)}\n"
                   f"    Witnesses = {tla_set(witnesses)}\n    M = {M}\n    K = {K}\n    MaxT = 3\n    AttachWindow = {attach}\n"
                   "INVARIANTS\n    TypeOK\n    Inv_i\n    Inv_vi\n    Inv_viii\n    Inv_T7\n    Inv_RecoverEnabled\nPROPERTIES\n    Prop_ii\n    Prop_iv\n")
            w(f"trust_root_{rid}.cfg", txt)
            holders = [f"h{i}" for i in range(1, seated + 1)]
            subscribed = [ident(n["id"]) for n in topo.get("nodes", []) if n.get("accepts") == r["id"]]
            allnodes = [ident(n) for n in nodes] or ["n1"]
            w(f"accord_halt_{rid}.cfg",
              f"\\* generated from {os.path.basename(entry_path)} root {r['id']}\nSPECIFICATION Spec\n"
              f"CONSTANTS {consts_line(holders + allnodes)}\n  Holders = {tla_set(holders)}  Nodes = {tla_set(allnodes)}  Subscribed = {tla_set(subscribed)}\n  Mode = \"row\"\n"
              "INVARIANTS Inv_SubscribersOnly Inv_ResumeNeedsHonest Inv_RowNoWindow Inv_RowFireEnabled\nPROPERTIES Prop_RowNoServer\n")
            fuse = int((ch.get("halt_fuse_secs") or 86400) / 43200)  # abstract ticks: 86400 s = 2 ticks
            w(f"accord_fuse_{rid}.cfg",
              f"\\* generated from {os.path.basename(entry_path)} root {r['id']}\nSPECIFICATION Spec\n"
              f"CONSTANTS {consts_line(holders)}  Holders = {tla_set(holders)}  Fuse = {max(fuse, 1)}\n"
              "INVARIANTS Inv_LoneBounded Inv_ConfirmNeedsHonest Inv_ResumeNeedsHonest Inv_FireEnabled Inv_MajorityCanConfirm Inv_MajorityCanResume\nPROPERTIES Prop_ConfirmedPersists\n")
        else:
            notes.append(f"root {r['id']}: kind {r.get('kind')} (one holder key): no roster machine applies; standing is by the key alone")
    # ---- persons: self_roster ----
    for p in persons:
        owns = [ident(x) for x in p.get("owns", [])]
        joins = {ident(x) for x in p.get("joins", [])}
        initial = [d for d in owns if d not in joins] or owns[:1]
        if not owns:
            continue
        spare = f"{ident(p['id'])}_spare"
        devices = owns + [spare]
        for adversary, ms, ml in (("stolen", 1, 0), ("lost", min(2, max(1, len(initial) - 1)), 0)):
            if adversary == "lost":
                ms, ml = 0, min(2, max(1, len(initial) - 1))
            w(f"self_roster_{ident(p['id'])}_{adversary}.cfg",
              f"\\* generated from {os.path.basename(entry_path)} person {p['id']}: {len(initial)} initial key(s), {len(owns) - len(initial)} joined by approval, one spare\n"
              "SPECIFICATION Spec\n"
              f"CONSTANTS {consts_line(devices)}\n  Devices = {tla_set(devices)}\n  Initial = {tla_set(initial)}\n"
              f"  Mode = \"combined\"\n  Window = 2\n  StolenAuth = TRUE\n  MaxStolen = {ms}\n  MaxLost = {ml}\n  OwnerPresent = TRUE\n"
              "INVARIANTS TypeOK Inv_ThiefCannotEvictHonest Inv_ThiefNeverMajority Inv_SelfSurvives\nPROPERTIES Prop_LostRecoverable\n")
        if len(initial) == 1:
            notes.append(f"person {p['id']}: one initial key — a theft or a loss of it is the stated one-key bound (CC 3.3.6.3): Inv_SelfSurvives fails in both generated configurations by design")
        if len(initial) == 2:
            notes.append(f"person {p['id']}: two keys — a theft is the stated two-key stalemate (CC 3.3.6.3)")
    # ---- nodes: RootReach ----
    if nodes:
        ns = [ident(n) for n in nodes]
        w("root_reach.cfg", f"\\* generated from {os.path.basename(entry_path)}\nSPECIFICATION Spec\nCONSTANTS {consts_line(ns)}  Nodes = {tla_set(ns)}\n"
                            "INVARIANTS Inv_HaltOnlySubscribers Inv_RestrictNeedsRoot\nPROPERTIES Prop_HaltReach Prop_RestrictOnly Prop_NoBan\n")
    # ---- mesh_net wrapper ----
    if persons and nodes:
        ps = [ident(p["id"]) for p in persons]
        owner_of = {}
        for p in persons:
            for d in p.get("owns", []):
                owner_of[ident(d)] = ident(p["id"])
        allnodes = [ident(n) for n in nodes] + [ident(c) for c in canon]
        for c in canon:
            owner_of.setdefault(ident(c), ps[0])
        nfiles = sum(1 for r in rels if r.get("rel") in ("file", "note", "message"))
        blobs = [f"b{i}" for i in range(1, max(1, min(2, nfiles)) + 1)]
        owner_fn = " ELSE ".join([f"IF n = {n} THEN {o}" for n, o in owner_of.items()] + [ps[0]])
        class_fn = ("IF n \\in " + tla_set([ident(c) for c in canon]) + ' THEN "server" ELSE "personal"') if canon else '"personal"'
        household = any(r.get("rel") in ("household", "family", "member") and "family" in json.dumps(r) for r in rels) or tid == "T4"
        fam = ps if household else ps[:1]
        room = ps[:2] if len(ps) >= 2 else ps
        pub = ps[-1:]
        members_fn = f'IF c = "fam" THEN {tla_set(fam)} ELSE IF c = "room" THEN {tla_set(room)} ELSE IF c = "pub" THEN {tla_set(pub)} ELSE {tla_set(ps)}'
        mods_fn = f'IF c \\in {{"room", "pub"}} THEN {tla_set(pub)} ELSE {{}}'
        mod = f"MeshNet_{tid}"
        w(f"{mod}.tla",
          f"---------------------------- MODULE {mod} ----------------------------\n"
          f"(* generated from {os.path.basename(entry_path)} by tools/topology_to_cfg.py: MeshNet instantiated with the entry's\n   persons, nodes (canonicals are servers), owner map and blobs. *)\n"
          "EXTENDS Naturals, FiniteSets\n"
          f"CONSTANTS {', '.join(ps + allnodes + blobs)}, ClaimScope, ClaimsBind\n"
          "VARIABLES scope, author, held, claimed, allow, withdrawn, members, mods, federating, restricted\n"
          f"M == INSTANCE MeshNet WITH Persons <- {tla_set(ps)}, Nodes <- {tla_set(allnodes)}, Blobs <- {tla_set(blobs)},\n"
          f"       Owner <- [n \\in {tla_set(allnodes)} |-> {owner_fn}],\n"
          f"       Class <- [n \\in {tla_set(allnodes)} |-> {class_fn}],\n"
          f"       InitMembers <- [c \\in {{\"fam\", \"room\", \"pub\", \"commons\"}} |-> {members_fn}],\n"
          f"       InitMods <- [c \\in {{\"fam\", \"room\", \"pub\", \"commons\"}} |-> {mods_fn}]\n"
          "Spec == M!Spec\nInv_KnownHold == M!Inv_KnownHold\nInv_Consent == M!Inv_Consent\nInv_Invisible == M!Inv_Invisible\n"
          "Inv_ClaimNotBinding == M!Inv_ClaimNotBinding\nInv_Moderated == M!Inv_Moderated\nInv_ScanSeam == M!Inv_ScanSeam\nProp_RestrictOnly == M!Prop_RestrictOnly\n"
          "=============================================================================\n")
        w("mesh_net.cfg", f"\\* generated from {os.path.basename(entry_path)}; run against {mod}.tla with ../../mesh_net on the module path\nSPECIFICATION Spec\n"
                          f"CONSTANTS\n  {consts_line(ps + allnodes + blobs)}\n  ClaimScope = \"content\"\n  ClaimsBind = FALSE\n"
                          "INVARIANTS\n  Inv_KnownHold\n  Inv_Consent\n  Inv_Invisible\n  Inv_ClaimNotBinding\n  Inv_Moderated\n  Inv_ScanSeam\nPROPERTIES\n  Prop_RestrictOnly\n")
        if len(allnodes) > 4 or len(ps) > 3:
            notes.append(f"mesh_net: {len(ps)} persons × {len(allnodes)} nodes is above the rc7 instance (3×3); expect a long TLC run or reduce with symmetry")
    # ---- closure report ----
    atoms = {}
    for a in e.get("promises", []):
        v = VOC["atoms"].get(a)
        if not v:
            atoms[a] = {"error": "atom not in manifests/topology_vocabulary.json"}
            continue
        atoms[a] = {"plane": v["plane"], "state_predicate": v["state_predicate"], "cc_ref": v["cc_ref"],
                    "in_state_table": v["in_state_table"], "plane_models": PLANE_MODEL.get(v["plane"], "—")}
    report = {"catalog_id": tid, "title": e.get("title"), "catalogue_version": e.get("catalogue_version"),
              "serves": e.get("serves", []), "derives": e.get("derives", []),
              "entity_counts": {"roots": len(roots), "canonicals": len(canon), "nodes": len(nodes), "persons": len(persons),
                                "devices_max_per_person": max([len(p.get("owns", [])) for p in persons] or [0]),
                                "holders": max([int((r.get("founders") or {}).get("seated", 0)) for r in roots] or [0])},
              "generated": written, "notes": notes, "promised_atoms": atoms,
              "atoms_with_a_plane_model": sum(1 for a in atoms.values() if a.get("plane_models", "—") not in ("—",) and "no model" not in a.get("plane_models", "")),
              "atoms_without": sum(1 for a in atoms.values() if "no model" in a.get("plane_models", "") or a.get("plane_models") == "—")}
    w("closure.json", json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    return report


def main():
    args = sys.argv[1:]
    paths = sorted(p for p in (os.path.join(CATALOG, f) for f in os.listdir(CATALOG)) if re.search(r"/T\d+-.*\.ya?ml$", p)) if "--all" in args or not args else args
    rows = []
    for p in paths:
        r = gen(p)
        rows.append(r)
        print(f"{r['catalog_id']:3} {len(r['generated']):2} files  atoms with a plane model {r['atoms_with_a_plane_model']}/{len(r['promised_atoms'])}  "
              f"nodes {r['entity_counts']['nodes']} persons {r['entity_counts']['persons']} holders {r['entity_counts']['holders']}")
    summ = {"entries": [r["catalog_id"] for r in rows],
            "max": {k: max(r["entity_counts"][k] for r in rows) for k in rows[0]["entity_counts"]} if rows else {},
            "atoms_with_a_plane_model": sum(r["atoms_with_a_plane_model"] for r in rows),
            "atoms_promised": sum(len(r["promised_atoms"]) for r in rows)}
    open(os.path.join(OUT, "SUMMARY.json"), "w", encoding="utf-8").write(json.dumps(summ, indent=1) + "\n")
    print("max over the catalogue:", summ["max"])


if __name__ == "__main__":
    main()
