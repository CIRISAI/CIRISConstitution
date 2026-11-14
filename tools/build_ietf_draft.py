#!/usr/bin/env python3
"""
CC — the Internet-Draft built from the signed-object data.

  ietf/draft-moore-scitt-ciris-ceg.md     the kramdown-rfc source (edit this)
  manifests/signed_object.cddl            the CDDL, generated from constitution/signed_object.tsv

Steps:
  1. wrap the CDDL to the 72-column limit of an Internet-Draft (a trailing comment moves to
     its own line, a long `.regexp` string moves below its rule, a long choice breaks at
     ` / `) into ietf/signed_object.cddl, and check that the wrapped CDDL still parses and
     admits every admit vector of manifests/signed_object_vectors.json (needs the `cddl` gem);
  2. stamp the version into a copy of the source (draft-moore-scitt-ciris-ceg-NN.md);
  3. kramdown-rfc → .xml, xml2rfc --v3 → .txt and .html;
  4. with --idnits, POST the .xml to the IETF author-tools idnits API and save the report.

Run:  python3 tools/build_ietf_draft.py [--rev 00] [--idnits]
      python3 tools/build_ietf_draft.py --check   (CI; writes nothing)
--check parses both CDDL files and validates the admit vectors against each, then compares what the
build would write with the committed files: ietf/signed_object.cddl always, and the .xml and .txt of
the draft when kramdown-rfc and xml2rfc are installed (a line says so when they are not). A
difference exits 1: run the build and commit ietf/. The draft's date is the day of the build
(the source leaves `date:` empty), so the draft compares equal only on the day it was built.
Each run also alters the generated CDDL's persist pin and requires the comparison to catch it.
Tools: kramdown-rfc and cddl (gem install --user-install kramdown-rfc cddl), xml2rfc (pip).
"""
import glob, json, os, re, shutil, subprocess, sys, tempfile, textwrap, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IETF = os.path.join(ROOT, "ietf")
SRC = os.path.join(IETF, "draft-moore-scitt-ciris-ceg.md")
CDDL_IN = os.path.join(ROOT, "manifests", "signed_object.cddl")
CDDL_OUT = os.path.join(IETF, "signed_object.cddl")
VECTORS = os.path.join(ROOT, "manifests", "signed_object_vectors.json")
WIDTH = 69  # artwork is indented three columns in the text rendering


def find_tool(name):
    for d in [os.path.expanduser(p) for p in glob.glob(os.path.expanduser("~/.local/share/gem/ruby/*/bin"))] + os.environ.get("PATH", "").split(os.pathsep):
        p = os.path.join(d, name)
        if os.access(p, os.X_OK):
            return p
    return None


def tool(name):
    return find_tool(name) or sys.exit(f"build_ietf_draft: {name} not found")


def wrap_cddl(text):
    out = []
    for line in text.splitlines():
        if len(line) <= WIDTH:
            out.append(line)
            continue
        indent = re.match(r"\s*", line).group(0)
        body, comment = line, ""
        m = re.match(r"^(.*?\S)\s+;\s?(.*)$", line)
        if m and not line.lstrip().startswith(";"):
            body, comment = m.group(1), m.group(2)
        elif line.lstrip().startswith(";"):
            comment, body = line.lstrip()[1:].strip(), ""
        if comment:
            for c in textwrap.wrap(comment, WIDTH - len(indent) - 2):
                out.append(f"{indent}; {c}")
        if not body:
            continue
        if len(body) <= WIDTH:
            out.append(body)
            continue
        m = re.match(r"^(\s*\S.*?\.regexp)\s+(\".*\")(.*)$", body)
        if m:
            out.append(m.group(1))
            out.append(f"{indent}  {m.group(2)}{m.group(3)}")
            continue
        if " / " in body:
            sep = " = " if " = " in body else ": "
            head, _, rest = body.partition(sep)
            parts = rest.split(" / ")
            cur = f"{head}{sep}{parts[0]}"
            for p in parts[1:]:
                if len(cur) + 3 + len(p) > WIDTH:
                    out.append(cur)
                    cur = f"{indent}  / {p}"
                else:
                    cur += f" / {p}"
            out.append(cur)
            continue
        out.append(body)
    long = [l for l in out if len(l) > WIDTH]
    if long:
        sys.exit("build_ietf_draft: CDDL lines still too long:\n" + "\n".join(long))
    return "\n".join(out) + "\n"


def check_cddl(path):
    cddl = tool("cddl")
    if subprocess.run([cddl, path, "generate"], capture_output=True).returncode:
        sys.exit(f"build_ietf_draft: {path} does not parse")
    vecs = json.load(open(VECTORS, encoding="utf-8"))["vectors"]
    bad = []
    with tempfile.TemporaryDirectory() as d:
        for v in vecs:
            if v["kind"] != "admit":
                continue
            f = os.path.join(d, v["name"] + ".json")
            json.dump(v["row"], open(f, "w"))
            if subprocess.run([cddl, path, "validate", f], capture_output=True).returncode:
                bad.append(v["name"])
    if bad:
        sys.exit(f"build_ietf_draft: admit vectors fail the CDDL: {bad}")
    return sum(1 for v in vecs if v["kind"] == "admit")


def wrapped_cddl(text=None):
    text = open(CDDL_IN, encoding="utf-8").read() if text is None else text
    return wrap_cddl(text.replace("\u2014", "-"))


def build_draft(rev, out, cddl):
    """kramdown-rfc and xml2rfc over the source, in directory `out`, which holds `cddl` as signed_object.cddl."""
    name = f"draft-moore-scitt-ciris-ceg-{rev}"
    src = open(SRC, encoding="utf-8").read()
    src = src.replace("docname: draft-moore-scitt-ciris-ceg-latest", f"docname: {name}")
    src = src.replace("{::include ../manifests/signed_object.cddl}", "{::include signed_object.cddl}")
    if os.path.abspath(out) != IETF:
        open(os.path.join(out, "signed_object.cddl"), "w", encoding="utf-8").write(cddl)
    md = os.path.join(out, name + ".md")
    open(md, "w", encoding="utf-8").write(src)
    xml = os.path.join(out, name + ".xml")
    try:
        with open(xml, "w") as f:
            r = subprocess.run([tool("kramdown-rfc"), os.path.basename(md)], cwd=out, stdout=f, stderr=subprocess.PIPE, text=True)
        if r.returncode:
            sys.exit(r.stderr)
        for fmt in ("--text", "--html"):
            r = subprocess.run([tool("xml2rfc"), "--v3", fmt, os.path.basename(xml)], cwd=out, capture_output=True, text=True)
            warn = [l for l in (r.stdout + r.stderr).splitlines() if "Warning" in l or "Error" in l]
            if r.returncode or warn:
                sys.exit("\n".join(warn) or r.stderr)
    finally:
        os.remove(md)
    return name


def differs(generated, path):
    """The first line at which `generated` and the committed file at `path` part, or None when they are equal."""
    committed = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    if generated == committed:
        return None
    a, b = generated.splitlines(), committed.splitlines()
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return f"line {i + 1}: built {x.strip()[:70]!r}, committed {y.strip()[:70]!r}"
    return f"built {len(a)} lines, committed {len(b)}"


def check(rev):
    stale = []
    wrapped = wrapped_cddl()
    with tempfile.TemporaryDirectory() as d:
        tmp = os.path.join(d, "signed_object.cddl")
        open(tmp, "w", encoding="utf-8").write(wrapped)
        n = check_cddl(tmp)
        print(f"CDDL wrapped to {WIDTH} columns; parses; {n} admit vectors validate")
    n = check_cddl(CDDL_IN)
    print(f"manifests/signed_object.cddl parses; {n} admit vectors validate")
    # the deliberate break: the same source with its persist pin altered must not compare equal
    src = open(CDDL_IN, encoding="utf-8").read()
    pin = re.search(r"Typed from CIRISPersist ([0-9a-f]+)", src)
    if not pin:
        sys.exit("build_ietf_draft: no persist pin in manifests/signed_object.cddl for the deliberate break")
    broken = wrapped_cddl(src.replace(pin.group(0), "Typed from CIRISPersist " + "0" * len(pin.group(1))))
    if differs(broken, CDDL_OUT) is None:
        sys.exit("build_ietf_draft: the deliberate break (an altered persist pin) was not caught")
    print("deliberate break caught: an altered persist pin makes ietf/signed_object.cddl stale")
    w = differs(wrapped, CDDL_OUT)
    if w:
        stale.append(f"ietf/signed_object.cddl is stale ({w})")
    if find_tool("kramdown-rfc") and find_tool("xml2rfc"):
        with tempfile.TemporaryDirectory() as d:
            name = build_draft(rev, d, wrapped)
            for ext in (".xml", ".txt"):
                w = differs(open(os.path.join(d, name + ext), encoding="utf-8").read(), os.path.join(IETF, name + ext))
                if w:
                    stale.append(f"ietf/{name}{ext} is stale ({w})")
        print(f"draft built and compared: ietf/{name}.xml, .txt")
    else:
        print("kramdown-rfc or xml2rfc not installed: the draft's .xml and .txt are not compared here")
    for s in stale:
        print("STALE", s)
    if stale:
        print("run python3 tools/build_ietf_draft.py and commit ietf/")
        sys.exit(1)


def main(argv):
    rev = argv[argv.index("--rev") + 1] if "--rev" in argv else "00"
    if "--check" in argv:
        check(rev)
        return
    wrapped = wrapped_cddl()
    open(CDDL_OUT, "w", encoding="utf-8").write(wrapped)
    n = check_cddl(CDDL_OUT)
    print(f"CDDL wrapped to {WIDTH} columns; parses; {n} admit vectors validate")
    name = build_draft(rev, IETF, wrapped)
    print(f"built ietf/{name}.xml, .txt, .html with no xml2rfc warnings")

    if "--idnits" in argv:
        boundary = "----ccdraft"
        body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}.xml\"\r\n"
                f"Content-Type: application/xml\r\n\r\n").encode() + open(xml, "rb").read() + \
               f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"submitcheck\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request("https://author-tools.ietf.org/api/idnits", data=body,
                                     headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        report = urllib.request.urlopen(req, timeout=120).read().decode()
        open(os.path.join(IETF, name + ".idnits.txt"), "w").write(report)
        print(report[-1500:])


if __name__ == "__main__":
    main(sys.argv[1:])
