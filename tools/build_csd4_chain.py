#!/usr/bin/env python3
"""
CC — the CSD/4 chain as data: the end-to-end join from the
formal models to the catalogue, stated so a downstream repo can key its tests, QA and mutation scopes
to it from disk.

  formal model (TLA+/Lean/Python suites)  ──model_ref──►  formal/STATE_TABLE.tsv (variable=state)
      │ INVARIANTS.tsv (symbol over variables, claim_id)          │ atoms column
      ▼                                                           ▼
  constitution/claims.tsv (claim_id → evidence pointers) ◄─ manifests/topology_vocabulary.json (atom, cc_ref)
      │ impl:<Repo>/path#symbol resolved against                   │ promised by
      ▼ constitution/vendor/evidence/<Repo>.cc_impl.tsv            ▼
  the repo's witness / mutation scope                      formal/cewp_node/catalog/T*.yaml (entries)

Writes manifests/csd4_chain.json: per atom, its state-table rows (with the model transition that enters
them), the invariants over those variables (with their claim ids), the claims those invariants realise
plus the claims filed under the same CC section (marked by_section), each claim's evidence pointers
parsed by repo, and the catalogue entries that promise the atom; the sha256 of every input so the join
is pinned; and the refusal tokens the constitution names, by section (a text index: a backticked
snake_case identifier named within a refusal sentence or set in bold code; persist joins its emitted
tokens by exact name). What the chain does NOT carry, because CC does not own it: the per-step refusal
map of a trace (CIRISServer's harness traces.json), and the CSD cards' "stops at rel[k]" relation list
(CEWPOS / CIRISClient packaging/csd4); both are named in _meta.not_here with their owner.

Run: python3 tools/build_csd4_chain.py        (CI diffs manifests/csd4_chain.json)
"""
import csv, glob, hashlib, json, os, re, sys
from collections import OrderedDict, defaultdict
try:
    import yaml
except ImportError:
    sys.exit("build_csd4_chain: PyYAML required")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
ST, IV, VOC, CL, PINS = P("formal", "STATE_TABLE.tsv"), P("formal", "INVARIANTS.tsv"), P("manifests", "topology_vocabulary.json"), P("constitution", "claims.tsv"), P("constitution", "evidence_pins.tsv")
CAT = P("formal", "cewp_node", "catalog")
OUT = P("manifests", "csd4_chain.json")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def rows(path):
    return list(csv.DictReader(open(path, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))


def parse_evidence(ev):
    out = []
    for tok in ev.split():
        m = re.match(r"^(impl|test|bench|lean):(?:@)?([A-Za-z0-9_.-]+)[/:#](.*)$", tok)
        if tok.startswith(("staged:", "open:")):
            k, t = tok.split(":", 1); out.append(OrderedDict([("kind", k), ("ticket", t)]))
        elif tok.startswith("normative-only"):
            out.append(OrderedDict([("kind", "normative-only")]))
        elif tok.startswith("test:@"):
            path, _, syms = tok[6:].partition("#")
            out.append(OrderedDict([("kind", "test"), ("repo", "CIRISConstitution"), ("path", path), ("symbols", syms.split(",") if syms else [])]))
        elif tok.startswith("lean:"):
            _, repo, obj = tok.split(":", 2) if tok.count(":") >= 2 else ("lean", tok[5:], "")
            out.append(OrderedDict([("kind", "lean"), ("repo", repo), ("object", obj)]))
        elif re.match(r"^(impl|test|bench):[A-Za-z0-9_-]+[/#]", tok):
            k, rest = tok.split(":", 1)
            repo, sep, tail = re.split(r"([/#])", rest, 1) if re.search(r"[/#]", rest) else (rest, "", "")
            path, _, syms = tail.partition("#") if sep == "/" else ("", "", tail)
            out.append(OrderedDict([("kind", k), ("repo", repo), ("path", path), ("symbols", syms.split(",") if syms else [])]))
        else:
            out.append(OrderedDict([("kind", "other"), ("raw", tok)]))
    return out


def refusal_tokens():
    """tokens the text names, by section: a backticked snake_case identifier within 140 chars after a
    'refus' word, or set in bold code; envelope member names are excluded"""
    members = set()
    for r in rows(P("constitution", "signed_object.tsv")):
        members.add(r["member"])
    idx = defaultdict(lambda: OrderedDict())
    for f in sorted(glob.glob(P("constitution", "part_*.md"))):
        sec = "—"
        for line in open(f, encoding="utf-8"):
            m = re.match(r"^#{2,4}\s+(\d+(?:\.\d+)*)\s", line)
            if m:
                sec = m.group(1); continue
            for m in re.finditer(r"\*\*`([a-z][a-z0-9_]{5,})`\*\*", line):
                t = m.group(1)
                if t not in members: idx[t].setdefault(sec, "bold")
            for m in re.finditer(r"refus\w*", line):
                win = line[m.end(): m.end() + 140]
                for t in re.findall(r"`([a-z][a-z0-9_]{5,})`", win):
                    if t not in members and ":" not in t: idx[t].setdefault(sec, "after_refusal")
    return OrderedDict((t, OrderedDict(sorted(s.items()))) for t, s in sorted(idx.items()) if "_" in t)


def main():
    st, iv, cl = rows(ST), rows(IV), rows(CL)
    voc = json.load(open(VOC, encoding="utf-8"), object_pairs_hook=OrderedDict)
    pins = {r["repo"]: r["commit"] for r in rows(PINS)}
    catpin = dict(l.rstrip("\n").split("\t", 1) for l in open(P(CAT, "PIN.tsv")) if "\t" in l)
    entries = {}
    for f in sorted(glob.glob(P(CAT, "T*.yaml"))):
        e = yaml.safe_load(open(f, encoding="utf-8"))
        entries[e["catalog_id"]] = {"title": e.get("title", ""), "promises": list(e.get("promises", [])), "catalogue_version": e.get("catalogue_version")}
    promised_by = defaultdict(list)
    for cid, e in entries.items():
        for a in e["promises"]: promised_by[a].append(cid)
    by_var = defaultdict(list)
    for r in iv:
        for v in r["variables"].split():
            by_var[v].append(r)
    claims_by_id = {r["claim_id"]: r for r in cl}
    claims_by_sec = defaultdict(list)
    for r in cl: claims_by_sec[r["decimal_id"]].append(r)
    state_rows_by_atom = defaultdict(list)
    for r in st:
        for a in r["atoms"].split():
            if a != "—": state_rows_by_atom[a].append(r)

    def claim_obj(r, how):
        return OrderedDict([("claim_id", r["claim_id"]), ("cc_ref", r["decimal_id"]), ("status", r["status"]), ("join", how), ("evidence", parse_evidence(r["evidence"]))])

    atoms = OrderedDict()
    for a, meta in voc["atoms"].items():
        srows = state_rows_by_atom.get(a, [])
        vars_ = sorted({r["variable"] for r in srows})
        invs = []
        seen = set()
        for v in vars_:
            for r in by_var.get(v, []):
                if r["inv_id"] in seen: continue
                seen.add(r["inv_id"])
                invs.append(OrderedDict([("inv_id", r["inv_id"]), ("model", r["model"]), ("source", r["source"]), ("symbol", r["symbol"]), ("kind", r["kind"]), ("claim_id", r["claim_id"]), ("verdict", r["verdict"])]))
        claims = []
        cseen = set()
        for i in invs:
            cid = i["claim_id"].replace(" (proposed)", "")
            if cid in claims_by_id and cid not in cseen:
                cseen.add(cid); claims.append(claim_obj(claims_by_id[cid], "by_invariant"))
        secs = {meta.get("cc_ref", "")} | {r["cc_ref"].split()[0] for r in srows if r["cc_ref"]}
        for s in sorted(secs):
            for r in claims_by_sec.get(s, []):
                if r["claim_id"] not in cseen:
                    cseen.add(r["claim_id"]); claims.append(claim_obj(r, "by_section"))
        atoms[a] = OrderedDict([
            ("plane", meta.get("plane")), ("state_predicate", meta.get("state_predicate")), ("cc_ref", meta.get("cc_ref")), ("added_in", meta.get("added_in", 1)),
            ("states", [OrderedDict([("variable", r["variable"]), ("state", r["state"]), ("plane", r["plane"]), ("cc_ref", r["cc_ref"]), ("enters_by", r["enters_by"]), ("signer", r["signer"]), ("model_ref", r["model_ref"]), ("status", r["status"])]) for r in srows]),
            ("invariants", invs), ("claims", claims), ("promised_by", promised_by.get(a, []))])
    body = OrderedDict([
        ("chain", [
            OrderedDict([("link", 1), ("from", "formal models"), ("to", "formal/STATE_TABLE.tsv"), ("by", "model_ref (the transition or variable that enters the state) and formal/INVARIANTS.tsv (symbol over variables)")]),
            OrderedDict([("link", 2), ("from", "formal/STATE_TABLE.tsv"), ("to", "manifests/topology_vocabulary.json"), ("by", "the atoms column; an atom's state_predicate is variable=state")]),
            OrderedDict([("link", 3), ("from", "formal/INVARIANTS.tsv"), ("to", "constitution/claims.tsv"), ("by", "claim_id (exact), plus claims under the same CC section (by_section)")]),
            OrderedDict([("link", 4), ("from", "constitution/claims.tsv"), ("to", "constitution/vendor/evidence/<Repo>.cc_impl.tsv"), ("by", "impl:<Repo>/path#symbol resolved against the pinned manifest (constitution/evidence_pins.tsv)")]),
            OrderedDict([("link", 5), ("from", "manifests/topology_vocabulary.json"), ("to", "formal/cewp_node/catalog/T*.yaml"), ("by", "promises[]; the server's harness traces (traces.json) carry the per-step atoms and refusals")])]),
        ("atoms", atoms),
        ("entries", entries),
        ("refusal_tokens", refusal_tokens()),
    ])
    meta = OrderedDict([
        ("source", "tools/build_csd4_chain.py"),
        ("pins", OrderedDict([("state_table_sha256", sha(ST)), ("invariants_sha256", sha(IV)), ("vocabulary_sha256", sha(VOC)), ("vocabulary_catalogue_version", voc["_meta"].get("catalogue_version")), ("claims_sha256", sha(CL)), ("catalogue", catpin), ("evidence_pins", pins)])),
        ("counts", OrderedDict([("atoms", len(atoms)), ("states", len(st)), ("invariants", len(iv)), ("claims", len(cl)), ("entries", len(entries)), ("refusal_tokens", len(body["refusal_tokens"]))])),
        ("not_here", OrderedDict([
            ("trace_step_refusals", "the per-step refused map of each T0–T19 trace is CIRISServer's harness output (packaging/csd4/traces.json vendored in CIRISClient); CC indexes the tokens it names by section under refusal_tokens"),
            ("card_relations", "the CSD cards' 'stops at rel[k]:…' relation list and its owner-by-repo map are CEWPOS / CIRISClient packaging/csd4 data, not CC's"),
            ("tag", "these files ride the v1.0-rc9 tag; a repo that vendors tagged CC only vendors them at the tag, or pins the rc9 commit as a test fixture as persist does for governance_policy.json")])),
    ])
    doc = OrderedDict([("_meta", meta)]); doc.update(body)
    doc["_meta"]["chain_sha256"] = hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False); open(OUT, "a").write("\n")
    c = meta["counts"]
    unjoined = [a for a, v in atoms.items() if not v["claims"]]
    print(f"csd4_chain: {c['atoms']} atoms, {c['states']} states, {c['invariants']} invariants, {c['claims']} claims, {c['entries']} entries, {c['refusal_tokens']} refusal tokens; atoms with no claim join: {len(unjoined)}" + (f" {unjoined[:6]}" if unjoined else ""))


if __name__ == "__main__":
    main()
