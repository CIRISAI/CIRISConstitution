#!/usr/bin/env python3
"""Audit a checkout for dimensions it emits that have no registered family.

CC 3.1.7: every claim the federation makes has a registered family. This walks the
non-test source of one or more repository checkouts, extracts every string literal
shaped like a versioned dimension (`stem:seg…:vN`, format placeholders allowed),
replays each through the reference matcher (tools/cc_namespace_match.py) against
manifests/namespace_registry.json, and reports the ones that do NOT resolve to a
registered family:

  OPEN     — resolves as open vocabulary: no row claims it
  REFUSED  — the matcher refuses it (wrong arity, retired family, bad case, …)

It also audits ROW TYPES (CC 2.4): the row-type slot is closed at the five primitives and
the registered carriers. A literal that is a registered carrier token is counted as
registered, not as an unregistered dimension; and every string constant whose name
contains ATTESTATION_TYPE, and every literal assigned to an `attestation_type` field,
is checked against the closed list:

  ROW TYPE — a type constant (or type prefix) the closed list does not admit

Usage:  python3 tools/audit_emitted_dimensions.py <checkout> [<checkout> …]
Exit status 1 if any OPEN or REFUSED dimension is found (suitable for CI), 0 otherwise.

Limits, stated: a row type held in a constant whose name does not say so, or built at
run time, is invisible here; the admission allowlist (CC 2.4) is the gate, this is the
early warning. For dimensions it sees only literals that carry the version tail. A dimension built
from prefix helpers or constants at run time is invisible to it, as is one emitted
with no tail at all; a component should ALSO replay its emitters' real output through
the matcher (as edge, persist and verify do). Negative controls in a repo's own
matcher tests will be reported — list them in --allow.
"""
import argparse, collections, importlib.util, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ccm", os.path.join(HERE, "cc_namespace_match.py"))
ccm = importlib.util.module_from_spec(spec); spec.loader.exec_module(ccm)

EXT = (".rs", ".py", ".kt", ".ts", ".tsx")
SKIP_DIR = ("/target/", "/node_modules/", "/.git/", "/build/", "/dist/", "/vendor/", "/docs/", "/FSD/",
            "/testing/", "/tests/", "/test/", "/benches/", "/fixtures/", "/reference/", "/site-packages/",
            "/harness/", "/localization/", "/i18n/")
LIT = re.compile(r'''["'`]([a-z][a-z0-9_]*(?::[A-Za-z0-9_{}.$<>()\-\[\]?* ]+?)*:v[0-9]+)["'`]''')
TYPE_CONST = re.compile(r'''\b([A-Z0-9_]*ATTESTATION_TYPE[A-Z0-9_]*)\b[^=;\n]*=\s*"([^"\n]*)"''')
TYPE_FIELD = re.compile(r'''\battestation_type\s*[:=]\s*"([^"\n]*)"''')      # a literal placed straight in the slot
TYPE_VALUE = re.compile(r"[a-z][a-z0-9_]*(:[A-Za-z0-9_.{}$<>\-]+)*")           # a value shaped like a type at all
SHAPE = re.compile(r"[a-z][a-z0-9_]*(:[A-Za-z0-9_.\-]+)+")


def sample(d):
    return re.sub(r"\$\{[^}]*\}|\{[^}]*\}|<[^>]*>|\$[A-Za-z_]+", "x", d)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("checkouts", nargs="+")
    ap.add_argument("--registry", default=os.path.join(HERE, "..", "manifests", "namespace_registry.json"))
    ap.add_argument("--allow", action="append", default=[], help="a literal to ignore (repeatable)")
    a = ap.parse_args()
    reg = json.load(open(a.registry))
    bad = 0
    for root in a.checkouts:
        found = collections.defaultdict(set)
        ok = 0
        for dp, dn, fn in os.walk(root):
            if any(k in dp + "/" for k in SKIP_DIR):
                dn[:] = []
                continue
            for f in fn:
                if not f.endswith(EXT) or any(k in f for k in ("_test.", "test_", "Test.kt", ".test.")):
                    continue
                p = os.path.join(dp, f)
                try:
                    txt = open(p, encoding="utf-8", errors="ignore").read()
                except OSError:
                    continue
                if f.endswith(".rs"):
                    i = txt.find("#[cfg(test)]")
                    if i > 0:
                        txt = txt[:i]
                slot = [(mm.group(1), mm.group(2)) for mm in TYPE_CONST.finditer(txt)]
                slot += [("attestation_type", mm.group(1)) for mm in TYPE_FIELD.finditer(txt)]
                for name, val in slot:
                    if val in a.allow or val == "attestation_type" or not TYPE_VALUE.fullmatch(val.rstrip(":")):
                        continue                # a field NAME constant, or prose
                    rt = reg["_meta"]["row_types"]
                    if val.endswith(":"):       # a type PREFIX: admitted iff some carrier token begins with it
                        good = any(c["sample"].startswith(val) for c in rt["carriers"])
                    else:
                        good = ccm.match_row_type(reg, sample(val))[0] is not None
                    if good:
                        ok += 1
                    else:
                        found[("%s = %s" % (name, val), "ROW TYPE")].add(os.path.relpath(p, root))
                for mm in LIT.finditer(txt):
                    raw = mm.group(1)
                    if raw in a.allow or len(raw) > 120:
                        continue
                    d = sample(raw)
                    if not SHAPE.fullmatch(d):
                        continue
                    fam, _, refusal = ccm.match_family(reg, d)
                    if ccm.match_row_type(reg, d)[0] == "carrier":
                        fam = d                     # a carrier row type (CC 2.4), not a dimension
                    if fam:
                        ok += 1
                    else:
                        found[(raw, "REFUSED " + refusal if refusal else "OPEN")].add(os.path.relpath(p, root))
        print(f"{root}: {ok} registered, {len(found)} not")
        for (raw, why), files in sorted(found.items()):
            fs = sorted(files)
            print(f"  [{why}] {raw}   <- {fs[0]}" + (f" +{len(fs) - 1}" if len(fs) > 1 else ""))
        bad += len(found)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
