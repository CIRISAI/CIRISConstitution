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
      python3 tools/build_ietf_draft.py --check   (step 1 only, on both CDDL files; CI)
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


def tool(name):
    for d in [os.path.expanduser(p) for p in glob.glob(os.path.expanduser("~/.local/share/gem/ruby/*/bin"))] + os.environ.get("PATH", "").split(os.pathsep):
        p = os.path.join(d, name)
        if os.access(p, os.X_OK):
            return p
    sys.exit(f"build_ietf_draft: {name} not found")


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


def main(argv):
    rev = argv[argv.index("--rev") + 1] if "--rev" in argv else "00"
    wrapped = wrap_cddl(open(CDDL_IN, encoding="utf-8").read().replace("\u2014", "-"))
    open(CDDL_OUT, "w", encoding="utf-8").write(wrapped)
    n = check_cddl(CDDL_OUT)
    print(f"CDDL wrapped to {WIDTH} columns; parses; {n} admit vectors validate")
    if "--check" in argv:
        n = check_cddl(CDDL_IN)
        print(f"manifests/signed_object.cddl parses; {n} admit vectors validate")
        return

    name = f"draft-moore-scitt-ciris-ceg-{rev}"
    src = open(SRC, encoding="utf-8").read()
    src = src.replace("docname: draft-moore-scitt-ciris-ceg-latest", f"docname: {name}")
    src = src.replace("{::include ../manifests/signed_object.cddl}", "{::include signed_object.cddl}")
    md = os.path.join(IETF, name + ".md")
    open(md, "w", encoding="utf-8").write(src)
    xml = os.path.join(IETF, name + ".xml")
    try:
        with open(xml, "w") as f:
            r = subprocess.run([tool("kramdown-rfc"), os.path.basename(md)], cwd=IETF, stdout=f, stderr=subprocess.PIPE, text=True)
        if r.returncode:
            sys.exit(r.stderr)
        for fmt in ("--text", "--html"):
            r = subprocess.run([tool("xml2rfc"), "--v3", fmt, os.path.basename(xml)], cwd=IETF, capture_output=True, text=True)
            warn = [l for l in (r.stdout + r.stderr).splitlines() if "Warning" in l or "Error" in l]
            if r.returncode or warn:
                sys.exit("\n".join(warn) or r.stderr)
    finally:
        os.remove(md)
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
