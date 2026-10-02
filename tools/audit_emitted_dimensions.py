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

Usage:  python3 tools/audit_emitted_dimensions.py <checkout> [<checkout> …]
Exit status 1 if any OPEN or REFUSED dimension is found (suitable for CI), 0 otherwise.

Limits, stated: it sees only literals that carry the version tail. A dimension built
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
                for mm in LIT.finditer(txt):
                    raw = mm.group(1)
                    if raw in a.allow or len(raw) > 120:
                        continue
                    d = sample(raw)
                    if not SHAPE.fullmatch(d):
                        continue
                    fam, _, refusal = ccm.match_family(reg, d)
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
