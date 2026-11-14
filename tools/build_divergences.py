#!/usr/bin/env python3
"""
CC: the divergence manifest. For each implementer, the places where its shipped behaviour differs from the text, each
as a test expectation: a case (rows in the kernel's row form), an ask (one named answer), the verdict the shipped
behaviour gives and the verdict the kernel gives under the text. `expect_kernel` is what the implementer's test
asserts once it moves.

Sources, read mechanically:
  1. family-model cells sourced from the shipped census (code-v61) that a sentence contradicts: a `cites` reading of
     disagree (counted), or a standing text_conflicts row naming the family (each must be covered by an entry);
  2. every text_conflicts row with still_there = yes whose carrier is an implementer (the store, the transport, the
     agent, the server, the client, verify, the claims register, or a tool or a text-side table of this repository);
  3. formal/derivation/seven_rankings_shipped.tsv (shipped claims that rank) and formal/derivation/models_vs_text.tsv
     (this repository's own models against the text: counted, not entered);
  4. every claim those rows name, resolved against constitution/claims.tsv and attached to its entry.
The cases themselves are tools/divergence_cases.py. Every runnable case is run by tools/divergence_oracle.py over
formal/causal_kernel: once with the text's parameter, once with the shipped one, by the set and in every arrival order
to a cap. An entry whose two verdicts agree is refused by this build: the case is wrong or the entry is wording only.

Writes manifests/divergences.json, manifests/divergences.tsv and manifests/divergences/<implementer>.{md,json}.
  python3 tools/build_divergences.py            write
  python3 tools/build_divergences.py --check    exit 1 if a written file is stale
"""
import csv
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
_dwb, sys.dont_write_bytecode = sys.dont_write_bytecode, True
import divergence_oracle as O    # noqa: E402
import divergence_cases as DC    # noqa: E402
from build_family_model import section_span  # noqa: E402
sys.dont_write_bytecode = _dwb

P = lambda *a: os.path.join(ROOT, *a)
CONFLICTS = P("formal", "derivation", "text_conflicts.tsv")
CENSUS = P("formal", "derivation", "census_v61.tsv")
CLAIMS = P("constitution", "claims.tsv")
MODEL = P("manifests", "family_model.json")
SEVEN = P("formal", "derivation", "seven_rankings_shipped.tsv")
MODELS_VS_TEXT = P("formal", "derivation", "models_vs_text.tsv")
RETURNS = P("formal", "derivation", "divergence_returns.tsv")
RETURN_COLS = ["id", "implementer", "date", "disputes", "counter_rows", "counter_ask", "their_verdict", "reason", "outcome", "changed"]
DISPUTES = ("case", "expect_kernel", "sentence")
OUTCOMES = ("open", "ours stands", "theirs stands")
OUT_JSON, OUT_TSV, OUT_DIR = P("manifests", "divergences.json"), P("manifests", "divergences.tsv"), P("manifests", "divergences")
RETURN_HOWTO = ("To return an entry whose verdict you hold wrong, add a row to `formal/derivation/divergence_returns.tsv` with "
                "the entry's `id`, your implementer name, the date, what it `disputes` (case, expect_kernel or sentence), "
                "your counter-case as JSON rows in `counter_rows` with `counter_ask`, `their_verdict`, a one-line `reason` "
                "and `outcome` open. The entry then reads `disputed`, the kernel's verdict on your counter-case is recorded "
                "beside yours, and the text or the model is corrected or the entry stands.")
CONTRACT = "each entry is one test: build `case`, ask `ask`, assert `expect_kernel`"
IMPLEMENTERS = ("persist", "edge", "agent", "server", "client", "verify", "tooling")
KINDS = ("signer", "subject", "cosign", "audience", "lifecycle", "fold", "count", "window", "door", "freshness",
         "wording-only")


def tsv(path):
    return list(csv.DictReader((l for l in open(path, encoding="utf-8") if not l.startswith("#")), delimiter="\t"))


def carrier_implementers(carrier):
    """Who a conflict row's carrier names, as implementers. A model or a manifest of this repository is not one."""
    out = set()
    c = carrier or ""
    if re.search(r"\bpersist\b|CIRISPersist", c): out.add("persist")
    if "CIRISAgent" in c: out.add("agent")
    if "CIRISEdge" in c: out.add("edge")
    if re.search(r"tools/|this repository|^this\b|formal/derivation/", c): out.add("tooling")
    if "constitution/claims.tsv" in c: out.add("claims")
    return out


def standing_rows():
    rows = tsv(CONFLICTS)
    return [r for r in rows if r["still_there"] == "yes" and carrier_implementers(r["carrier"])]


def claim_index():
    out = {}
    for r in tsv(CLAIMS):
        ev = r.get("evidence", "")
        m = re.search(r"(?:impl|staged):CIRIS(\w+?)(?:/|#|$)", ev)
        impl = {"Persist": "persist", "Edge": "edge", "Agent": "agent", "Server": "server", "Verify": "verify"}.get(
            m.group(1) if m else "", "persist" if "Persist" in ev else None)
        out[r["claim_id"]] = {"implementer": impl, "evidence": ev, "status": r.get("status", "")}
    return out


def census_cell(prefix, column):
    for r in tsv(CENSUS):
        if r["prefix"] == prefix: return r.get(column)
    return None


def source_one():
    """Source 1: code-v61 cells with a disagreeing cite; families a standing conflict row names in family_model.json."""
    m = json.load(open(MODEL, encoding="utf-8"))
    disagree = [(r["family"], col) for r in m["rows"] for col, v in r.items()
                if isinstance(v, dict) and v.get("source") == "code-v61"
                and any(c.get("reading") == "disagree" for c in v.get("cites") or [])]
    fams = sorted({r["family"] for r in m["rows"]}, key=len, reverse=True)
    named = {}
    for c in standing_rows():
        blob = c["side_a"] + " " + c["side_b"] + " " + c["resolution"]
        if "family_model" not in blob and "code-v61" not in blob: continue
        for f in fams:
            if f in blob: named.setdefault(c["id"], []).append(f)
    return disagree, named


def read_returns():
    """The returns implementers send (formal/derivation/divergence_returns.tsv), each checked for its form."""
    errs, out = [], []
    if not os.path.exists(RETURNS): return out, ["formal/derivation/divergence_returns.tsv is missing"]
    with open(RETURNS, encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("#")]
    if not lines or lines[0].rstrip("\n").split("\t") != RETURN_COLS:
        return out, ["divergence_returns.tsv: the header is not " + " ".join(RETURN_COLS)]
    for r in csv.DictReader(lines, delimiter="\t"):
        tag = "return %s (%s)" % (r["id"], r["date"])
        if r["disputes"] not in DISPUTES: errs.append("%s: disputes %r" % (tag, r["disputes"]))
        if r["outcome"] not in OUTCOMES: errs.append("%s: outcome %r" % (tag, r["outcome"]))
        for col in ("counter_rows", "counter_ask"):
            try: r[col] = json.loads(r[col]) if r[col].strip() else None
            except ValueError: errs.append("%s: %s is not JSON" % (tag, col)); r[col] = None
        out.append(r)
    return out, errs


def attach_returns(out, returns, errs):
    """An open return makes its entry `disputed` and carries the counter-case; a runnable counter-case is run on the
    kernel under the text's parameter, and its verdict is recorded beside the implementer's."""
    by = {r["id"]: r for r in out}
    for ret in returns:
        e = by.get(ret["id"])
        if e is None:
            if ret["outcome"] == "open": errs.append("return %s: open, and no entry has that id" % ret["id"])
            continue
        rec = {k: ret[k] for k in RETURN_COLS if k != "id"}
        if ret["counter_rows"] and "param" in e["text"]:
            try:
                rec["kernel_on_counter"] = O.run_set(ret["counter_rows"], e["text"]["param"], ret["counter_ask"] or e["case"]["ask"])
            except Exception as x:  # a counter-case the oracle cannot read is recorded as such, never dropped
                rec["kernel_on_counter"] = "not runnable here: %s" % type(x).__name__
        e.setdefault("returns", []).append(rec)
        if ret["outcome"] == "open": e["status"] = "disputed"


def source_digest(path, keys=(), family=None):
    """The sha256 of what the shipped value was read from: in a shared register (the claims, the conflicts) the rows
    the entry names; in another table the lines naming the family; in a manifest the items of the family; else the
    whole file. So an unrelated change elsewhere in the file does not move it, and a change to the family's own part
    does."""
    full = os.path.join(ROOT, path)
    text = open(full, encoding="utf-8").read()
    if keys:
        part = [l for l in text.split("\n") if any(l.startswith(k + "\t") for k in keys)]
    elif path.endswith(".tsv") and family:
        part = [l for l in text.split("\n") if family in l]
    elif path.endswith(".json") and family:
        d = json.loads(text)
        part = [json.dumps(x, sort_keys=True) for v in (d.values() if isinstance(d, dict) else [d]) if isinstance(v, list)
                for x in v if isinstance(x, dict) and family in (x.get("family"), x.get("prefix"))]
        part = part or [text]
    else:
        part = [text]
    return hashlib.sha256("\n".join(part).encode("utf-8")).hexdigest()


def shipped_file(e):
    f = e.get("shipped_file")
    if not f and e.get("shipped_source"):
        f = e["shipped_source"].split()[0]
    return f if f and os.path.isfile(os.path.join(ROOT, f)) else None


def entry_id(e):
    return "%s/%s/%s" % (e["implementer"], e["family"], e["where"])


def run_entry(e):
    if e.get("status") in ("stated", "wording-only"): return
    res = O.run_all(e["rows"], e["text_param"], e["shipped_param"], e["ask"])
    e.update(res)
    e["status"] = "runnable"


def build():
    claims = claim_index()
    errs = []
    entries = DC.cases()
    for e in entries:
        if e["implementer"] == "claims":
            c = next((s for s in e["sources"] if s.startswith("CLM-")), None)
            e["implementer"] = (claims.get(c) or {}).get("implementer") or "persist"
        run_entry(e)
    out, seen = [], {}
    for e in entries:
        i = entry_id(e)
        if i in seen:
            seen[i]["sources"] = sorted(set(seen[i]["sources"]) | set(e["sources"]))
            continue
        span = section_span(e["cc_ref"]) or ""
        if e["quote"] not in span: errs.append("%s: the quote does not stand in %s" % (i, e["cc_ref"]))
        cell = None
        if e.get("census"):
            cell = census_cell(*e["census"])
            if cell is None or e["shipped_value"] not in cell:
                errs.append("%s: the shipped words are not in the census cell %s %s: re-read the entry" % (i, *e["census"]))
        cl = sorted({c for s in e["sources"] for c in re.findall(r"CLM-[\w-]+", s)})
        for c in cl:
            if c not in claims: errs.append("%s: claim %s is not in constitution/claims.tsv" % (i, c))
        if e["kind"] not in KINDS: errs.append("%s: kind %s" % (i, e["kind"]))
        if e["implementer"] not in IMPLEMENTERS: errs.append("%s: implementer %s" % (i, e["implementer"]))
        rec = {
            "id": i, "implementer": e["implementer"], "family": e["family"], "where": e["where"], "kind": e["kind"],
            "status": e["status"], "sources": sorted(set(e["sources"])), "claims": cl,
            "text": {"value": e.get("text_value"), "cc_ref": e["cc_ref"], "quote": e["quote"]},
            "shipped": {"value": e["shipped_value"],
                        "source": e.get("shipped_source") or ("formal/derivation/census_v61.tsv %s %s" % tuple(e["census"]) if e.get("census") else None),
                        "census_cell": cell},
        }
        if not e.get("census") and e["status"] == "runnable":
            f = shipped_file(e)
            if f is None:
                errs.append("%s: the shipped value names no file it was read from (shipped_file)" % i)
            else:
                keys = [x for x in e["sources"] if re.fullmatch(r"C\d+|CLM-[\w-]+", x)] if f in (
                    "constitution/claims.tsv", "formal/derivation/text_conflicts.tsv") else []
                keys = [x for x in keys if x.startswith("CLM-")] if f == "constitution/claims.tsv" else keys
                rec["shipped"]["file"] = f
                rec["shipped"]["file_sha256"] = source_digest(f, keys, e["family"])
                if keys: rec["shipped"]["file_rows"] = keys
        if e["status"] == "runnable":
            if e["expect_kernel"] == e["expect_shipped"]:
                errs.append("%s: the two verdicts agree (%s): the case does not tell them apart" % (i, e["expect_kernel"]))
            if len(e["kernel_verdicts_over_orders"]) != 1 or e["kernel_verdicts_over_orders"][0] != e["expect_kernel"]:
                errs.append("%s: the kernel's verdict depends on arrival order %s" % (i, e["kernel_verdicts_over_orders"]))
            rec["text"]["param"] = e["text_param"]
            rec["shipped"]["param"] = e["shipped_param"]
            rec["case"] = {"rows": [O.plain(r) for r in e["rows"]], "ask": e["ask"]}
            rec["expect_shipped"] = e["expect_shipped"]
            rec["expect_kernel"] = e["expect_kernel"]
            rec["orders"] = {"run": e["orders_run"], "of": e["orders_total"],
                             "kernel": e["kernel_verdicts_over_orders"],
                             "shipped_judged_on_arrival": e["shipped_on_arrival_verdicts"]}
            rec["order_dependent_shipped"] = len(e["shipped_on_arrival_verdicts"]) > 1
            if rec["order_dependent_shipped"]:
                rec["also_assert"] = "the same verdict in every arrival order"
            if e.get("note"): rec["note"] = e["note"]
            for k in ("replayed_by", "vectors_to_add"):
                if e.get(k): rec[k] = e[k]
            if e["ask"]["answer"] == "door": rec["door_model_at_build"] = O.door_model(e["rows"], e["ask"])
            if e.get("controls"):
                rec["controls"] = []
                for c in e["controls"]:
                    k, sv = O.run_set(c["rows"], e["text_param"], c["ask"]), O.run_set(c["rows"], e["shipped_param"], c["ask"])
                    if k != sv: errs.append("%s: a control must give one verdict both ways, gives %r and %r" % (i, k, sv))
                    rec["controls"].append({"note": c["note"], "rows": [O.plain(r) for r in c["rows"]], "ask": c["ask"],
                                            "expect_kernel": k, "expect_shipped": sv})
        else:
            rec["reason"] = e["reason"]
            if e["status"] == "stated": rec["gap"] = e["gap"]
        seen[i] = rec
        out.append(rec)
    if len({r["id"] for r in out}) != len(out): errs.append("duplicate ids")
    returns, rerrs = read_returns()
    errs += rerrs
    attach_returns(out, returns, errs)
    # a conflict row whose witness is an entry's id (a disputed entry's row) is a source of that entry
    byid = {r["id"]: r for r in out}
    for c in tsv(CONFLICTS):
        w = c.get("witness", "").strip()
        if w in byid and c["id"] not in byid[w]["sources"]:
            byid[w]["sources"] = sorted(byid[w]["sources"] + [c["id"]])
    # coverage of the standing conflict rows with an implementer carrier
    mapped = {s for r in out for s in r["sources"]}
    standing = standing_rows()
    unmapped = [c["id"] for c in standing if c["id"] not in mapped]
    for c in unmapped: errs.append("%s: a standing conflict row with an implementer carrier has no entry" % c)
    disagree, named = source_one()
    fams_of = {}
    for r in out:
        for s in r["sources"]: fams_of.setdefault(s, set()).add(r["family"])
    # a conflict row naming model families whose entries name none of them (an entry on a family the row does not name)
    off_family = sorted(c for c, fs in named.items() if c in fams_of and not (set(fs) & fams_of[c]))
    seven = tsv(SEVEN)
    models = tsv(MODELS_VS_TEXT)
    counts = lambda key: {k: sum(1 for r in out if r[key] == k) for k in sorted({r[key] for r in out})}
    meta = {
        "contract": CONTRACT,
        "generator": "tools/build_divergences.py (cases: tools/divergence_cases.py; oracle: tools/divergence_oracle.py over formal/causal_kernel)",
        "row_form": O.__doc__.split("Parameter (JSON)")[0].split("Row form (JSON):")[1].strip(),
        "verdicts": {"state": "admitted | concludes nothing | withdrawn | recanted | refused | waits",
                     "stands": "stands | does not stand", "audience": "served | not served",
                     "fold": "the value the fold gives", "owed": "the effects owed, or nothing"},
        "orders": "every arrival order of the case up to %d (a fixed sample above); `kernel` must hold one verdict, and "
                  "`shipped_judged_on_arrival` is the shipped parameter judged once at admission against every row held" % O.ORDER_CAP,
        "total": len(out), "by_status": counts("status"), "by_implementer": counts("implementer"), "by_kind": counts("kind"),
        "order_dependent_shipped": sum(1 for r in out if r.get("order_dependent_shipped")),
        "conflict_rows_with_implementer_carrier": len(standing), "conflict_rows_mapped": len(standing) - len(unmapped),
        "source_1_cells_with_disagree_cite": len(disagree),
        "source_1_conflict_rows_naming_model_families": len(named),
        "source_1_rows_whose_entries_name_another_family": off_family,
        "source_3_rows_read": {"seven_rankings_shipped.tsv": len(seven), "models_vs_text.tsv (this repository's models; not entered)": len(models)},
    }
    return {"_meta": meta, "entries": out}, errs


def tsv_text(doc):
    cols = ["id", "implementer", "kind", "status", "family", "where", "cc_ref", "expect_kernel", "expect_shipped", "sources"]
    lines = ["\t".join(cols)]
    for r in doc["entries"]:
        lines.append("\t".join([r["id"], r["implementer"], r["kind"], r["status"], r["family"], r["where"], r["text"]["cc_ref"],
                                r.get("expect_kernel") or "-", r.get("expect_shipped") or "-", " ".join(r["sources"])]))
    return "# Generated by tools/build_divergences.py from manifests/divergences.json. Do not edit.\n" + "\n".join(lines) + "\n"


def one_line(case):
    rows = case["rows"]
    show = lambda r: "%s:%s by %s%s" % (r["id"], r.get("family") if r["kind"] == "fam" else r["kind"], r["signer"],
                                        " names " + ",".join(r["names"]) if r["names"] else "")
    ask = case["ask"]
    tgt = ask.get("target") or ask.get("key") or ""
    return "; ".join(show(r) for r in rows) + " | ask " + ask["answer"] + (" " + tgt if tgt else "")


def views(doc):
    out = {}
    for impl in sorted({r["implementer"] for r in doc["entries"]}):
        es = [r for r in doc["entries"] if r["implementer"] == impl]
        run = [r for r in es if "case" in r]
        md = ["# Divergences: %s" % impl, "",
              "Generated by `tools/build_divergences.py` from `manifests/divergences.json`. Do not edit.", "",
              "How to consume: %s. The case is rows in the kernel's row form (see `_meta.row_form` of the manifest); "
              "`expect_shipped` is what the shipped code gives today. Where `also_assert` is set, the verdict must also be "
              "the same in every arrival order." % CONTRACT, "", RETURN_HOWTO, "",
              "%d entries: %d runnable, %d disputed, %d stated, %d wording only." % (
                  len(es), sum(r["status"] == "runnable" for r in es), sum(r["status"] == "disputed" for r in es),
                  sum(r["status"] == "stated" for r in es), sum(r["status"] == "wording-only" for r in es)), "",
              "| id | family | where | the sentence | the case | assert |", "|---|---|---|---|---|---|"]
        esc = lambda s: str(s).replace("|", "\\|").replace("\n", " ")
        for r in es:
            sent = "%s: %s" % (r["text"]["cc_ref"], r["text"]["quote"])
            case = one_line(r["case"]) if "case" in r else "(%s) %s" % (r["status"], r.get("reason", ""))
            assert_ = (r.get("expect_kernel") or "-") + (" (disputed)" if r["status"] == "disputed" else "")
            md.append("| %s | %s | %s | %s | %s | %s |" % tuple(esc(x) for x in (
                r["id"], r["family"], r["where"], sent, case, assert_)))
        vec = {"_meta": {"contract": CONTRACT, "implementer": impl, "source": "manifests/divergences.json",
                         "row_form": doc["_meta"]["row_form"], "verdicts": doc["_meta"]["verdicts"], "count": len(run)},
               "returns": RETURN_HOWTO, "vectors": [{"id": r["id"], "family": r["family"], "where": r["where"], "kind": r["kind"],
                            "case": r["case"], "expect_kernel": r["expect_kernel"], "expect_shipped": r["expect_shipped"],
                            "kernel_parameter": r["text"]["param"], **({"also_assert": r["also_assert"]} if r.get("also_assert") else {}),
                            **({"disputed": True, "returns": r["returns"]} if r["status"] == "disputed" else {})}
                           for r in run],
               "not_runnable": [{"id": r["id"], "status": r["status"], "reason": r.get("reason"), "cc_ref": r["text"]["cc_ref"],
                                 "quote": r["text"]["quote"]} for r in es if "case" not in r]}
        out[os.path.join(OUT_DIR, impl + ".md")] = "\n".join(md) + "\n"
        out[os.path.join(OUT_DIR, impl + ".json")] = json.dumps(vec, indent=1, ensure_ascii=False) + "\n"
    return out


def files(doc):
    out = {OUT_JSON: json.dumps(doc, indent=1, ensure_ascii=False) + "\n", OUT_TSV: tsv_text(doc)}
    out.update(views(doc))
    return out


def moved_sources(old_doc, new_doc):
    """The entries whose shipped source has moved since the manifest was written: (id, file, old hash, new hash)."""
    old = {r["id"]: r for r in old_doc["entries"]}
    out = []
    for r in new_doc["entries"]:
        o = old.get(r["id"], {}).get("shipped", {})
        if o.get("file_sha256") and o["file_sha256"] != r["shipped"].get("file_sha256"):
            out.append((r["id"], o.get("file"), o["file_sha256"], r["shipped"].get("file_sha256") or "none"))
    return out


def main():
    check = "--check" in sys.argv[1:]
    doc, errs = build()
    for e in errs: print("divergences: error: " + e)
    if errs: return 1
    want = files(doc)
    if check:
        moved = moved_sources(json.load(open(OUT_JSON, encoding="utf-8")), doc) if os.path.exists(OUT_JSON) else []
        for i, f, a, b in moved:
            print("divergences: entry %s: its shipped source %s moved (sha256 %s -> %s): re-read the entry" % (i, f, a[:12], b[:12]))
        stale = [p for p, t in want.items() if not os.path.exists(p) or open(p, encoding="utf-8").read() != t]
        have = {os.path.join(OUT_DIR, f) for f in os.listdir(OUT_DIR)} if os.path.isdir(OUT_DIR) else set()
        stale += sorted(have - set(want))
        for p in stale: print("divergences: stale: " + os.path.relpath(p, ROOT))
        if stale or moved: return 1
    else:
        os.makedirs(OUT_DIR, exist_ok=True)
        for p, t in want.items():
            open(p, "w", encoding="utf-8").write(t)
    m = doc["_meta"]
    print("divergences: %d entries %s; by implementer %s; by kind %s; shipped order-dependent %d; conflict rows %d mapped of %d"
          % (m["total"], m["by_status"], m["by_implementer"], m["by_kind"], m["order_dependent_shipped"],
             m["conflict_rows_mapped"], m["conflict_rows_with_implementer_carrier"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
