#!/usr/bin/env python3
"""
CC — flat files an implementer pins, built from the repository's own tables so they never go stale.

  manifests/family_placement.tsv          one line per family of manifests/family_model.json: where its rows are placed,
                                          what that follows, its verbs, whether it is counted, its fold, the section
  manifests/refusal_tokens_delta_rc22.tsv the refusal tokens added, renamed, retired or moved against the tag v1.0-rc22
  manifests/claims_delta_rc22.tsv         the claim ids added, renamed or withdrawn against v1.0-rc22
  manifests/retired_rc22.tsv              families, verbs, vocabulary words, envelope members and policy rows present at
                                          v1.0-rc22 and absent now
  manifests/shape_delta_rc22.tsv          every member of constitution/signed_object_v2.tsv added, changed or removed
                                          since v1.0-rc22

The baseline is read with `git show v1.0-rc22:<path>`. A rename is read only where a retired and an added entry share
the same section and the same words with the name taken out; every other pair is an addition and a retirement.

Run: python3 tools/build_adopter_files.py            # write
     python3 tools/build_adopter_files.py --check    # compare with what the tree holds; exit 1 when stale
stdlib only.
"""
import csv, io, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = "v1.0-rc22"
MAN = os.path.join(ROOT, "manifests")


def now(path):
    return open(os.path.join(ROOT, path), encoding="utf-8").read()


def then(path):
    r = subprocess.run(["git", "-C", ROOT, "show", f"{TAG}:{path}"], capture_output=True)
    if r.returncode:
        sys.exit(f"build_adopter_files: cannot read {path} at {TAG}: {r.stderr.decode().strip()}")
    return r.stdout.decode("utf-8")


def tsv(text):
    return list(csv.DictReader(io.StringIO("".join(l for l in text.splitlines(True) if not l.startswith("#"))),
                               delimiter="\t", quoting=csv.QUOTE_NONE))


def cell(v):
    if v is None: return ""
    if isinstance(v, list): return "|".join(cell(x) for x in v)
    if isinstance(v, dict): return json.dumps(v, ensure_ascii=False, sort_keys=True)
    return str(v).replace("\t", " ").replace("\n", " ")


def write(lines):
    return "\n".join("\t".join(cell(c) for c in l) for l in lines) + "\n"


# ---- 1. where each family is placed -------------------------------------------------------------------------------
def family_placement():
    rows = json.loads(now("manifests/family_model.json"))["rows"]
    out = [("family", "placement", "follows", "verbs", "counted", "fold", "cc_ref")]
    for r in rows:
        pl = r["placement"]
        count = r.get("count", {}).get("value")
        counted = "no" if count in (None, "none") else "yes"
        folds = [f["fold"] for f in (r.get("fold", {}).get("value") or [])] if isinstance(r.get("fold", {}).get("value"), list) else r.get("fold", {}).get("value")
        out.append((r["family"], pl.get("value"), pl.get("follows", ""), r["verbs"]["value"], counted, folds or "", pl.get("cc_ref", "")))
    return write(out)


# ---- 2. refusal tokens ----------------------------------------------------------------------------------------------
def strip_name(sentence, name):
    return re.sub(r"\s+", " ", sentence.replace(name, "")).strip()


def pair_renames(old, new, key_sec, key_text):
    """Retired and added names that share a section and the same words with the name taken out."""
    gone = {k: v for k, v in old.items() if k not in new}
    came = {k: v for k, v in new.items() if k not in old}
    ren = {}
    for o, ov in sorted(gone.items()):
        for n, nv in sorted(came.items()):
            if n in ren.values(): continue
            if key_sec(ov) == key_sec(nv) and strip_name(key_text(ov), o) == strip_name(key_text(nv), n):
                ren[o] = n; break
    return ren


def refusal_delta():
    old = tsv(then("manifests/refusal_tokens.tsv")); new = tsv(now("manifests/refusal_tokens.tsv"))
    op = {r["token"]: (i + 1, r) for i, r in enumerate(old)}; np_ = {r["token"]: (i + 1, r) for i, r in enumerate(new)}
    ren = pair_renames({k: v[1] for k, v in op.items()}, {k: v[1] for k, v in np_.items()},
                       lambda r: r["section"], lambda r: r["sentence"])
    out = [("change", "token", "class", "old_position", "new_position", "cc_ref")]
    for t, (i, r) in sorted(np_.items(), key=lambda x: x[1][0]):
        if t in op:
            if op[t][0] != i: out.append(("position_moved", t, r["kind"], op[t][0], i, r["section"]))
        elif t in ren.values():
            o = next(k for k, v in ren.items() if v == t)
            out.append(("renamed", f"{o} -> {t}", r["kind"], op[o][0], i, r["section"]))
        else:
            out.append(("added", t, r["kind"], "", i, r["section"]))
    for t, (i, r) in sorted(op.items(), key=lambda x: x[1][0]):
        if t not in np_ and t not in ren:
            out.append(("retired", t, r["kind"], i, "", r["section"]))
    return write(out)


# ---- 3. claims ------------------------------------------------------------------------------------------------------
def claims_delta():
    old = {r["claim_id"]: r for r in tsv(then("constitution/claims.tsv"))}
    new = {r["claim_id"]: r for r in tsv(now("constitution/claims.tsv"))}
    ren = {}
    for o, ov in sorted(old.items()):
        if o in new: continue
        for n, nv in sorted(new.items()):
            if n not in old and n not in ren.values() and nv["summary"] == ov["summary"]:
                ren[o] = n; break
    out = [("change", "claim_id", "decimal_id", "status")]
    for n, r in new.items():
        if n in old: continue
        if n in ren.values():
            out.append(("renamed", f"{next(k for k, v in ren.items() if v == n)} -> {n}", r["decimal_id"], r["status"]))
        else:
            out.append(("added", n, r["decimal_id"], r["status"]))
    for o, r in old.items():
        if o not in new and o not in ren:
            out.append(("withdrawn", o, r["decimal_id"], r["status"]))
    return write(out)


# ---- 4. retired names -----------------------------------------------------------------------------------------------
ENVELOPE = ("statement", "protected", "cwt", "unprotected", "payload", "refs", "row_id", "statement_id", "key")


def names(get):
    fm = json.loads(get("manifests/family_model.json"))["rows"]
    tr = json.loads(get("manifests/transitions.json"))["_meta"]
    so = tsv(get("constitution/signed_object_v2.tsv"))
    S = {
        "family": {r["family"]: "manifests/family_model.json" for r in fm},
        "verb": {f"{r['family']}#{v}": "manifests/family_model.json verbs" for r in fm for v in (r["verbs"]["value"] or [])},
        "role_token": {t: "manifests/transitions.json role_tokens" for t in tr["role_tokens"]},
        "protocol_kind": {r["kind"]: "constitution/consensus_protocols.tsv" for r in tsv(get("constitution/consensus_protocols.tsv"))},
        "refusal_token": {r["token"]: "manifests/refusal_tokens.tsv (%s)" % r["section"] for r in tsv(get("manifests/refusal_tokens.tsv"))},
        "envelope_member": {f"{r['object']}.{r['member']}": "constitution/signed_object_v2.tsv (%s)" % r["cc_ref"]
                            for r in so if r["object"] in ENVELOPE and r["rule"] != "-"},
        "policy_row": {r["family"]: "constitution/governance_policy.tsv (%s)" % r["cc_ref"] for r in tsv(get("constitution/governance_policy.tsv"))},
    }
    return S


def retired():
    old, new = names(then), names(now)
    out = [("kind", "name", "where_it_was")]
    for kind in old:
        for n in sorted(set(old[kind]) - set(new[kind])):
            out.append((kind, n, old[kind][n]))
    return write(out)


# ---- 5. shapes ------------------------------------------------------------------------------------------------------
def shape_delta():
    key = lambda r: (r["object"], r["rule"], r["member"] if r["rule"] != "-" else r["logical_name"])
    old = {key(r): r for r in tsv(then("constitution/signed_object_v2.tsv"))}
    new = {key(r): r for r in tsv(now("constitution/signed_object_v2.tsv"))}
    out = [("family_or_object", "member", "type", "required", "cc_ref", "change")]
    for k, r in new.items():
        if k not in old:
            ch = "added"
        else:
            diff = [c for c in ("placement", "type", "required_when", "logical_name") if old[k][c] != r[c]]
            if not diff: continue
            ch = "changed:" + ",".join(diff)
        out.append((f"{r['object']} ({r['rule']})", k[2], r["type"], r["required_when"], r["cc_ref"], ch))
    for k, r in old.items():
        if k not in new:
            out.append((f"{r['object']} ({r['rule']})", k[2], r["type"], r["required_when"], r["cc_ref"], "removed"))
    return write(out)


FILES = [("family_placement.tsv", family_placement), ("refusal_tokens_delta_rc22.tsv", refusal_delta),
         ("claims_delta_rc22.tsv", claims_delta), ("retired_rc22.tsv", retired), ("shape_delta_rc22.tsv", shape_delta)]


def main():
    check = "--check" in sys.argv
    stale = []
    for name, fn in FILES:
        text, path = fn(), os.path.join(MAN, name)
        have = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if have != text:
            if check: stale.append(name)
            else: open(path, "w", encoding="utf-8").write(text)
        print(f"adopter files: {name}: {text.count(chr(10)) - 1} lines")
    if stale:
        sys.exit("adopter files: stale (run tools/build_adopter_files.py): " + ", ".join(stale))


if __name__ == "__main__":
    main()
