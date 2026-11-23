#!/usr/bin/env python3
"""
Build a companion Internet-Draft of draft-moore-scitt-ciris-ceg:

  ietf/draft-moore-scitt-ciris-trace.md           the CIRIS agent trace (CompleteTrace)
  ietf/draft-moore-scitt-ciris-trace-context.md   its LLM_CALL context manifest

(each the kramdown-rfc source; edit these).

Separate from tools/build_ietf_draft.py on purpose: that script's --check compares the CEG drafts byte for byte,
and nothing here may change its output.

Steps: stamp the revision into ietf/<name>-NN.md, check that every ``~~~ cddl`` block parses
(`cddl ... generate`), then kramdown-rfc -> .xml and xml2rfc --v3 -> .txt and .html. Any xml2rfc warning fails
the build.

Run:  python3 tools/build_ietf_companion.py <name> [--rev 00]
      python3 tools/build_ietf_companion.py <name> --check [--rev 00]   (CI; writes nothing)
--check builds from the committed stamped copy ietf/<name>-NN.md (the source as revision NN froze it; the working
source may already carry text toward NN+1) in a temporary directory and compares the .xml and .txt byte for byte with
the committed ones. A difference exits 1.
      e.g. python3 tools/build_ietf_companion.py draft-moore-scitt-ciris-trace-context
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


def gem_path() -> str:
    bins = sorted(glob.glob(os.path.expanduser("~/.local/share/gem/ruby/*/bin")))
    return os.pathsep.join(bins + [os.environ.get("PATH", "")])


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, text=True, capture_output=True, **kw)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="draft name without revision, e.g. draft-moore-scitt-ciris-trace-context")
    ap.add_argument("--rev", default="00")
    ap.add_argument("--check", action="store_true", help="rebuild the stamped copy and compare; write nothing")
    args = ap.parse_args()
    NAME, rev = args.name, args.rev
    SRC = os.path.join(IETF, f"{NAME}.md")
    if args.check:
        return check(NAME, rev)
    env = dict(os.environ, PATH=gem_path(), KRAMDOWN_REFCACHEDIR=os.path.join(IETF, ".refcache"))
    src = open(SRC, encoding="utf-8").read()
    doc = f"{NAME}-{rev}"
    stamped = src.replace(f"docname: {NAME}-latest", f"docname: {doc}")
    if stamped == src:
        sys.exit("docname line not found in the source")
    with open(os.path.join(IETF, f"{doc}.md"), "w", encoding="utf-8") as f:
        f.write(stamped)

    pos = 0
    while (pos := src.find("~~~ cddl", pos)) != -1:
        start = pos + len("~~~ cddl")
        end = src.index("~~~", start)
        with tempfile.NamedTemporaryFile("w", suffix=".cddl", delete=False) as f:
            f.write(src[start:end])
            cddl_path = f.name
        try:
            run(["cddl", cddl_path, "generate"], env=env)
        finally:
            os.unlink(cddl_path)
        pos = end + 3

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


def check(name: str, rev: str) -> int:
    """Rebuild ietf/<name>-<rev>.md in a temporary directory and compare its .xml and .txt with the committed."""
    import shutil

    doc = f"{name}-{rev}"
    stamped = os.path.join(IETF, f"{doc}.md")
    if not os.path.exists(stamped):
        print(f"no stamped copy {stamped}")
        return 1
    env = dict(os.environ, PATH=gem_path(), KRAMDOWN_REFCACHEDIR=os.path.join(IETF, ".refcache"))
    missing = [tool for tool in ("kramdown-rfc", "xml2rfc") if shutil.which(tool, path=env["PATH"]) is None]
    if missing:
        # As build_ietf_draft.py --check: without the renderers the byte comparison cannot run; say so, pass.
        print(f"{doc}: {' and '.join(missing)} not installed: .xml/.txt comparison skipped")
        return 0
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(stamped, tmp)
        with open(os.path.join(tmp, f"{doc}.xml"), "w", encoding="utf-8") as out:
            subprocess.run(["kramdown-rfc", f"{doc}.md"], cwd=tmp, env=env, check=True, stdout=out, stderr=subprocess.PIPE)
        run(["xml2rfc", "--v3", "--text", os.path.join(tmp, f"{doc}.xml")], cwd=tmp, env=env)
        bad, moved = [], []
        for ext in ("xml", "txt"):
            built = open(os.path.join(tmp, f"{doc}.{ext}"), encoding="utf-8").read()
            kept = open(os.path.join(IETF, f"{doc}.{ext}"), encoding="utf-8").read()
            if built == kept:
                continue
            if _without_foreign_refs(built, ext) == _without_foreign_refs(kept, ext):
                moved.append(ext)
            else:
                bad.append(ext)
    if bad:
        print(f"{doc}: {', '.join(bad)} differ from a rebuild of the stamped copy: run the build and commit ietf/")
        return 1
    if moved:
        # The stamped copy is the draft as submitted. A reference to another author's Internet-Draft is resolved
        # from the datatracker at build time, so it moves when that draft is revised; that is no change of ours.
        print(f"{doc}: {', '.join(moved)} differ from a rebuild only in references to other authors' drafts, "
              f"which have been revised since the stamped copy was built; every other byte is identical")
        return 0
    print(f"{doc}: .xml and .txt rebuild byte-identically from the stamped copy")
    return 0


def _without_foreign_refs(text: str, ext: str) -> str:
    """The text with each reference to an Internet-Draft of another author removed: its <reference> element in the
    XML, its entry of the reference list in the text form. A reference to a draft of this suite (I-D.moore-…) stays,
    and so does every RFC, since those do not move."""
    import re

    if ext == "xml":
        return re.sub(r'<reference anchor="I-D\.(?!moore-)[^"]*".*?</reference>\s*', "", text, flags=re.S)
    return re.sub(r"(?m)^ +\[I-D\.(?!moore-)[^\]]*\]\n(?:^ +\S.*\n)+", "", text)


if __name__ == "__main__":
    sys.exit(main())
