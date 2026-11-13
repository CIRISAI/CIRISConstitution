#!/usr/bin/env python3
"""
CC: the divergence manifest holds as a list of test expectations (manifests/divergences.json, built by
tools/build_divergences.py).

  coverage   every text_conflicts row with still_there = yes and an implementer carrier is a source of an entry
  quote      every entry's quote stands verbatim in the section it cites
  differ     every runnable entry, re-run from the manifest's own rows (the form an implementer reads), gives the
             recorded expect_kernel under the text's parameter and the recorded expect_shipped under the shipped one,
             and the two differ
  orders     the kernel's verdict is one in every arrival order the build ran
  vectors    every vector of manifests/divergences/<implementer>.json, re-run, gives its expect_kernel
  returns    an entry disputed by an open return (formal/derivation/divergence_returns.tsv) has a text_conflicts row
             whose carrier names this repository and whose witness is the entry id; a return whose outcome is
             theirs stands names the section or model file that changed, and the entry, while it stands, asserts their
             verdict
  sources    every runnable entry whose shipped value is not a census cell records the file it was read from and a
             hash of the family's part of it; `build_divergences.py --check` names the entry when that hash moves
  stated     the count of `stated` entries may only fall (MAX_STATED); the total is reported and not held

Plants, run every time, each must be caught: an entry whose shipped parameter is the text's (equal verdicts); a
standing conflict row with an implementer carrier and no entry; a quote that is not in its section; a recorded
expect_kernel the kernel does not give; a disputed entry with no conflict row; a return that theirs stands
whose entry still asserts the old verdict; one whose `changed` names nothing; a shipped source whose hash moved.

Run: python3 tools/check_divergences.py
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
_dwb, sys.dont_write_bytecode = sys.dont_write_bytecode, True
import divergence_oracle as O     # noqa: E402
import build_divergences as B     # noqa: E402
from build_family_model import section_span  # noqa: E402
sys.dont_write_bytecode = _dwb

MAX_STATED = 16     # shrink-only: an entry leaves `stated` when the kernel model can run it (13, plus three new differences on a signed instant)


def coverage(doc, standing):
    mapped = {s for r in doc["entries"] for s in r["sources"]}
    return ["%s: standing with carrier %r and no entry" % (c["id"], c["carrier"]) for c in standing if c["id"] not in mapped]


def quotes(doc):
    return ["%s: quote not verbatim in %s" % (r["id"], r["text"]["cc_ref"]) for r in doc["entries"]
            if r["text"]["quote"] not in (section_span(r["text"]["cc_ref"]) or "")]


def differ(doc):
    errs = []
    for r in doc["entries"]:
        if "case" not in r: continue
        rows, ask = r["case"]["rows"], r["case"]["ask"]
        k = O.run_set(rows, r["text"]["param"], ask)
        s = O.run_set(rows, r["shipped"]["param"], ask)
        if k != r["expect_kernel"]: errs.append("%s: kernel gives %r, recorded %r" % (r["id"], k, r["expect_kernel"]))
        if s != r["expect_shipped"]: errs.append("%s: shipped gives %r, recorded %r" % (r["id"], s, r["expect_shipped"]))
        if k == s: errs.append("%s: the two verdicts are equal (%r): not a behavioural divergence" % (r["id"], k))
        for c in r.get("controls", ()):
            ck, cs = O.run_set(c["rows"], r["text"]["param"], c["ask"]), O.run_set(c["rows"], r["shipped"]["param"], c["ask"])
            if ck != cs or ck != c["expect_kernel"]: errs.append("%s: control %r gives %r and %r" % (r["id"], c["note"], ck, cs))
    return errs


def orders(doc):
    errs = []
    for r in doc["entries"]:
        if "case" in r and r["orders"]["kernel"] != [r["expect_kernel"]]:
            errs.append("%s: kernel verdicts over arrival orders %s" % (r["id"], r["orders"]["kernel"]))
    return errs


def returns_check(doc, conflicts, returns):
    """An open return needs its conflict row; a return whose outcome is theirs stands names what changed, and the
    entry, while it stands, gives their verdict."""
    errs = []
    by = {r["id"]: r for r in doc["entries"]}
    for r in doc["entries"]:
        if r["status"] != "disputed": continue
        if not any("this repository" in c["carrier"] and c.get("witness", "").strip() == r["id"] for c in conflicts):
            errs.append("%s: disputed and no text_conflicts row with carrier this repository and witness the entry id" % r["id"])
    for ret in returns:
        if ret["outcome"] != "theirs stands": continue
        ch = (ret.get("changed") or "").strip()
        ok = bool(section_span(ch)) if ch.startswith("CC ") else bool(ch) and os.path.exists(os.path.join(B.ROOT, ch))
        if not ok: errs.append("return %s: theirs stands and `changed` (%r) names no section and no file" % (ret["id"], ch))
        e = by.get(ret["id"])
        if e is not None and e.get("expect_kernel") != ret["their_verdict"]:
            errs.append("return %s: theirs stands and the entry still asserts %r, not %r" % (ret["id"], e.get("expect_kernel"), ret["their_verdict"]))
    return errs


def vectors():
    errs, n = [], 0
    d = B.OUT_DIR
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if not f.endswith(".json"): continue
        v = json.load(open(os.path.join(d, f), encoding="utf-8"))
        for x in v["vectors"]:
            n += 1
            got = O.run_set(x["case"]["rows"], x["kernel_parameter"], x["case"]["ask"])
            if got != x["expect_kernel"]: errs.append("%s %s: gives %r" % (f, x["id"], got))
    return errs, n


def main():
    doc = json.load(open(B.OUT_JSON, encoding="utf-8"))
    standing = B.standing_rows()
    conflicts = B.tsv(B.CONFLICTS)
    returns, rerrs = B.read_returns()
    errs = rerrs + coverage(doc, standing) + quotes(doc) + differ(doc) + orders(doc) + returns_check(doc, conflicts, returns)
    verrs, nvec = vectors()
    errs += verrs
    nofile = [r["id"] for r in doc["entries"] if r["status"] in ("runnable", "disputed") and not r["shipped"].get("census_cell")
              and not r["shipped"].get("file_sha256")]
    errs += ["%s: runnable, not a census cell, and no hashed shipped source" % i for i in nofile]
    stated = sum(1 for r in doc["entries"] if r["status"] == "stated")
    if stated > MAX_STATED: errs.append("stated entries %d above the held maximum %d" % (stated, MAX_STATED))

    # plants: each must be caught
    caught = []
    run = [r for r in doc["entries"] if r["status"] == "runnable"]
    p = copy.deepcopy(doc); x = next(r for r in p["entries"] if r["status"] == "runnable")
    x["shipped"]["param"] = copy.deepcopy(x["text"]["param"]); x["expect_shipped"] = x["expect_kernel"]
    caught.append(("equal verdicts", any("are equal" in e for e in differ(p))))
    fake = dict(standing[0], id="C999", carrier="CIRISPersist")
    caught.append(("conflict row with no entry", bool(coverage(doc, standing + [fake]))))
    p = copy.deepcopy(doc); p["entries"][0]["text"]["quote"] += " (planted)"
    caught.append(("quote not in its section", bool(quotes(p))))
    p = copy.deepcopy(doc); x = next(r for r in p["entries"] if r["status"] == "runnable"); x["expect_kernel"] = "planted"
    caught.append(("wrong expect_kernel", any("recorded 'planted'" in e for e in differ(p))))
    p = copy.deepcopy(doc); x = next(r for r in p["entries"] if "case" in r); x["status"] = "disputed"
    caught.append(("open return with no conflict row", any("disputed and no" in e for e in returns_check(p, conflicts, returns))))
    x = next(r for r in doc["entries"] if "case" in r)
    ret = {"id": x["id"], "outcome": "theirs stands", "changed": x["text"]["cc_ref"], "their_verdict": x["expect_shipped"]}
    caught.append(("theirs stands, entry not moved", any("still asserts" in e for e in returns_check(doc, conflicts, [ret]))))
    ret = dict(ret, changed="formal/no_such_model.py", their_verdict=x["expect_kernel"])
    caught.append(("theirs stands, nothing changed", any("names no section" in e for e in returns_check(doc, conflicts, [ret]))))
    p = copy.deepcopy(doc); x = next(r for r in p["entries"] if r["shipped"].get("file_sha256"))
    x["shipped"]["file_sha256"] = "0" * 64
    caught.append(("a shipped source whose hash moved", bool(B.moved_sources(p, doc))))
    for name, ok in caught:
        if not ok: errs.append("plant not caught: " + name)

    for e in errs: print("divergences check: error: " + e)
    m = doc["_meta"]
    print("divergences check: %d entries (total, not held): %d runnable, %d disputed, %d stated (max %d), %d wording only; "
          "%d returns; %d vectors re-run; %d of %d standing conflict rows with an implementer carrier mapped; plants caught %d of %d"
          % (len(doc["entries"]), len(run), sum(r["status"] == "disputed" for r in doc["entries"]), stated, MAX_STATED, sum(r["status"] == "wording-only" for r in doc["entries"]),
             len(returns), nvec, len(standing) - len(coverage(doc, standing)), len(standing), sum(ok for _, ok in caught), len(caught)))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
