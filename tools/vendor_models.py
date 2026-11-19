#!/usr/bin/env python3
"""The models vendored from the implementing repositories are the bytes their manifest records.

formal/vendor/VENDOR.tsv lists every vendored file: where it sits here, the repository, ref, and commit it was
taken from, its path there, the sha256 of the upstream bytes, and the sha256 of the bytes here. The two hashes
differ only where this repository edited the copy (a section number re-cut, say); the `note` column says why.

  --check     (CI) every listed file exists and hashes to local_sha256; no file under a vendored directory is
              unlisted; a row whose two hashes differ carries a note
  --upstream  (needs local clones at ~/<repo>) each upstream path at the recorded commit still hashes to
              upstream_sha256, and reports where the ref's head has moved since the recorded commit
  --write     re-hash the local files into the manifest (after a re-vendor), keeping the other columns

formal/vendor/PINS.tsv names trees that are cited by commit and not copied (a simulation too large to vendor): the
repository, ref, commit, path and git tree id. --check holds each row's form; --upstream checks the tree id at the
commit and names the pins whose ref has moved on.

Run: python3 tools/vendor_models.py --check
"""
import csv, hashlib, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TSV = os.path.join(ROOT, "formal/vendor/VENDOR.tsv")
PINS = os.path.join(ROOT, "formal/vendor/PINS.tsv")
PIN_COLS = ["repo", "ref", "commit", "path", "tree", "what"]
COLS = ["local_path", "repo", "ref", "commit", "upstream_path", "upstream_sha256", "local_sha256", "note"]
# directories whose every file is vendored (besides the manifest and the README that explain them)
DIRS = ["formal/vendor/edge", "formal/vendor/server", "formal/vendor/client", "formal/vendor/agent", "formal/onion_layers",
        "formal/cewp_node/catalog"]
OWN = {"formal/vendor/edge/README.md", "formal/onion_layers/PIN.tsv", "formal/onion_layers/README.md",
       "formal/onion_layers/RESULTS.md", "formal/cewp_node/catalog/PIN.tsv"}


def sha(b): return hashlib.sha256(b).hexdigest()


def rows():
    with open(TSV, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write(rs):
    with open(TSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in sorted(rs, key=lambda r: r["local_path"]): w.writerow(r)


def check(rs):
    errs, listed = [], set()
    for r in rs:
        p = os.path.join(ROOT, r["local_path"]); listed.add(r["local_path"])
        if not os.path.isfile(p): errs.append(f"{r['local_path']}: listed and missing"); continue
        h = sha(open(p, "rb").read())
        if h != r["local_sha256"]: errs.append(f"{r['local_path']}: hashes {h[:12]}, manifest records {r['local_sha256'][:12]} (re-vendor, or record the edit and run --write)")
        if r["local_sha256"] != r["upstream_sha256"] and not r["note"].strip():
            errs.append(f"{r['local_path']}: differs from upstream {r['repo']}@{r['commit'][:7]} with no note saying why")
    for d in DIRS:
        for base, _, files in os.walk(os.path.join(ROOT, d)):
            for fn in files:
                rel = os.path.relpath(os.path.join(base, fn), ROOT)
                if "__pycache__" in rel or rel in OWN: continue
                if rel not in listed: errs.append(f"{rel}: under a vendored directory and not in VENDOR.tsv")
    return errs


def upstream(rs):
    errs, moved = [], {}
    for r in rs:
        repo = os.path.expanduser("~/" + r["repo"])
        if not os.path.isdir(os.path.join(repo, ".git")): errs.append(f"{r['repo']}: no clone at {repo}"); continue
        b = subprocess.run(["git", "-C", repo, "show", f"{r['commit']}:{r['upstream_path']}"], capture_output=True)
        if b.returncode: errs.append(f"{r['local_path']}: {r['upstream_path']} not at {r['repo']}@{r['commit'][:7]}"); continue
        if sha(b.stdout) != r["upstream_sha256"]: errs.append(f"{r['local_path']}: upstream bytes at {r['commit'][:7]} do not hash to the manifest")
        head = subprocess.run(["git", "-C", repo, "show", f"origin/{r['ref']}:{r['upstream_path']}"], capture_output=True)
        if head.returncode == 0 and sha(head.stdout) != r["upstream_sha256"]:
            moved.setdefault(f"{r['repo']} {r['ref']}", []).append(r["upstream_path"])
    for k, v in moved.items(): print(f"vendor: upstream moved since the recorded commit on {k}: {', '.join(v)}")
    return errs


def pins():
    with open(PINS, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def check_pins(ps):
    errs = []
    for p in ps:
        if list(p) != PIN_COLS: return [f"PINS.tsv: columns {list(p)}, expected {PIN_COLS}"]
        for k in ("commit", "tree"):
            if len(p[k]) != 40 or any(c not in "0123456789abcdef" for c in p[k]): errs.append(f"PINS.tsv {p['repo']}:{p['path']}: {k} is not a full git id")
        if not p["what"].strip(): errs.append(f"PINS.tsv {p['repo']}:{p['path']}: says nothing of what it pins")
    return errs


def upstream_pins(ps):
    errs = []
    for p in ps:
        repo = os.path.expanduser("~/" + p["repo"])
        if not os.path.isdir(os.path.join(repo, ".git")): errs.append(f"{p['repo']}: no clone at {repo}"); continue
        g = lambda ref: subprocess.run(["git", "-C", repo, "rev-parse", f"{ref}:{p['path']}"], capture_output=True, text=True).stdout.strip()
        if g(p["commit"]) != p["tree"]: errs.append(f"pin {p['repo']}:{p['path']}: tree at {p['commit'][:7]} is not {p['tree'][:12]}")
        h = g(f"origin/{p['ref']}")
        if h and h != p["tree"]: print(f"vendor: pin moved on {p['repo']} {p['ref']}: {p['path']}")
    return errs


def main():
    rs = rows()
    ps = pins()
    if "--write" in sys.argv:
        for r in rs: r["local_sha256"] = sha(open(os.path.join(ROOT, r["local_path"]), "rb").read())
        write(rs); print(f"vendor: {len(rs)} files re-hashed"); return 0
    errs = check(rs) + check_pins(ps) + (upstream(rs) + upstream_pins(ps) if "--upstream" in sys.argv else [])
    edited = sum(r["local_sha256"] != r["upstream_sha256"] for r in rs)
    for e in errs: print("vendor: error: " + e)
    print(f"vendor: {len(rs)} files from {len({r['repo'] for r in rs})} repositories; {edited} edited here, each with its note; {len(ps)} trees pinned by commit; {len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
