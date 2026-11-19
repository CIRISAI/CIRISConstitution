#!/usr/bin/env python3
"""
Build draft-moore-scitt-agent-context-provenance (the companion to draft-moore-scitt-ciris-ceg).

  ietf/draft-moore-scitt-agent-context-provenance.md   the kramdown-rfc source (edit this)

Separate from tools/build_ietf_draft.py on purpose: that script's --check compares the CEG drafts byte for byte,
and nothing here may change its output.

Steps: stamp the revision into ietf/draft-moore-scitt-agent-context-provenance-NN.md, check that the manifest
CDDL parses (`cddl ... generate`), then kramdown-rfc -> .xml and xml2rfc --v3 -> .txt and .html. Any xml2rfc
warning fails the build.

Run:  python3 tools/build_ietf_agent_context.py [--rev 00]
Tools: kramdown-rfc and cddl (gem install --user-install kramdown-rfc cddl), xml2rfc (pip).
"""
import argparse
import glob
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IETF = os.path.join(ROOT, "ietf")
NAME = "draft-moore-scitt-agent-context-provenance"
SRC = os.path.join(IETF, f"{NAME}.md")


def gem_path() -> str:
    bins = sorted(glob.glob(os.path.expanduser("~/.local/share/gem/ruby/*/bin")))
    return os.pathsep.join(bins + [os.environ.get("PATH", "")])


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, text=True, capture_output=True, **kw)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", default="00")
    rev = ap.parse_args().rev
    env = dict(os.environ, PATH=gem_path(), KRAMDOWN_REFCACHEDIR=os.path.join(IETF, ".refcache"))
    src = open(SRC, encoding="utf-8").read()
    doc = f"{NAME}-{rev}"
    stamped = src.replace(f"docname: {NAME}-latest", f"docname: {doc}")
    if stamped == src:
        sys.exit("docname line not found in the source")
    with open(os.path.join(IETF, f"{doc}.md"), "w", encoding="utf-8") as f:
        f.write(stamped)

    start = src.index("~~~ cddl") + len("~~~ cddl")
    with tempfile.NamedTemporaryFile("w", suffix=".cddl", delete=False) as f:
        f.write(src[start : src.index("~~~", start)])
        cddl_path = f.name
    try:
        run(["cddl", cddl_path, "generate"], env=env)
    finally:
        os.unlink(cddl_path)

    xml = os.path.join(IETF, f"{doc}.xml")
    with open(xml, "w", encoding="utf-8") as out:
        subprocess.run(["kramdown-rfc", f"{doc}.md"], cwd=IETF, env=env, check=True, stdout=out, stderr=subprocess.PIPE)
    result = run(["xml2rfc", "--v3", "--text", "--html", xml], cwd=IETF, env=env)
    warnings = [line for line in (result.stdout + result.stderr).splitlines() if "Warning" in line or "Error" in line]
    if warnings:
        print("\n".join(warnings))
        return 1
    print(f"built ietf/{doc}.xml, .txt, .html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
