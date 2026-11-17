#!/usr/bin/env python3
"""
CC — the Internet-Draft built from the signed-object data.

  ietf/draft-moore-scitt-ciris-ceg.md     the kramdown-rfc source (edit this)
  manifests/signed_object_v2.cddl         the CDDL of the signed object (CC 2.6.1), hand-written

Steps:
  1. wrap the CDDL to the 72-column limit of an Internet-Draft into ietf/signed_object.cddl: a
     trailing comment moves to its own line above its rule, a long rule breaks between tokens
     (never inside a string) with a deeper indent, and a string too long for one line becomes a
     `.cat` of shorter strings (RFC 9165). Then check that the wrapped CDDL still parses, admits
     every schema sample of tools/build_cc_signed_object_v2.py and refuses every broken one (the
     generator's own samples, read by importing it; needs the `cddl` gem);
  2. stamp the version into a copy of the source (draft-moore-scitt-ciris-ceg-NN.md);
  3. kramdown-rfc → .xml, xml2rfc --v3 → .txt and .html;
  4. with --idnits, POST the .xml to the IETF author-tools idnits API and save the report.

The tree holds one revision, REV below: the build writes it, --check compares it, and a new
revision replaces the outputs of the one before (git history keeps them).

Run:  python3 tools/build_ietf_draft.py [--rev 01] [--idnits]
      python3 tools/build_ietf_draft.py --check   (CI; writes nothing)
--check parses both CDDL files and runs the samples against each, then compares what the build
would write with the committed files: ietf/signed_object.cddl always, and the .xml and .txt of the
draft when kramdown-rfc and xml2rfc are installed (a line says so when they are not). A
difference exits 1: run the build and commit ietf/. The draft's date is the source's `date:`
line, so a build on any day compares equal; set it when the draft is revised.
Each run also alters the composite algorithm identifier in a copy of the CDDL and requires the
comparison to catch it.
Tools: kramdown-rfc and cddl (gem install --user-install kramdown-rfc cddl), xml2rfc (pip).
"""
import glob, os, re, shutil, subprocess, sys, tempfile, textwrap, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IETF = os.path.join(ROOT, "ietf")
SRC = os.path.join(IETF, "draft-moore-scitt-ciris-ceg.md")
CDDL_IN = os.path.join(ROOT, "manifests", "signed_object_v2.cddl")
CDDL_OUT = os.path.join(IETF, "signed_object.cddl")
REV = "01"  # the one revision the tree holds
BREAK = ("composite-alg = -70100", "composite-alg = -70199")  # the deliberate break
WIDTH = 69  # artwork is indented three columns in the text rendering


def find_tool(name):
    for d in [os.path.expanduser(p) for p in glob.glob(os.path.expanduser("~/.local/share/gem/ruby/*/bin"))] + os.environ.get("PATH", "").split(os.pathsep):
        p = os.path.join(d, name)
        if os.access(p, os.X_OK):
            return p
    return None


def tool(name):
    return find_tool(name) or sys.exit(f"build_ietf_draft: {name} not found")


def split_comment(line):
    """(body, comment): the comment starts at the first `;` outside a string."""
    q = False
    for i, ch in enumerate(line):
        if ch == '"':
            q = not q
        elif ch == ";" and not q:
            return line[:i].rstrip(), line[i + 1:].strip()
    return line.rstrip(), None


def tokens(body):
    """The body split at spaces outside strings."""
    out, cur, q = [], "", False
    for ch in body:
        if ch == '"':
            q = not q
        if ch == " " and not q:
            if cur:
                out.append(cur)
            cur = ""
        else:
            cur += ch
    return out + ([cur] if cur else [])


def cat_string(tok, room):
    """A quoted string too long for `room` columns, as `("a"` `.cat "b")` pieces of at most `room`."""
    m = re.match(r'^"([^"\\]*)"([,)\]]*)$', tok)
    if not m:
        sys.exit(f"build_ietf_draft: cannot break the CDDL token {tok}")
    inner, tail = m.group(1), m.group(2)
    n = room - len('.cat "")') - len(tail)
    parts = [inner[i:i + n] for i in range(0, len(inner), n)]
    return [f'("{parts[0]}"'] + [f'.cat "{p}"' for p in parts[1:-1]] + [f'.cat "{parts[-1]}"){tail}']


def wrap_body(body, base):
    """A rule body longer than WIDTH, broken between tokens; a continuation is indented under `base`."""
    indent = re.match(r"\s*", body).group(0)
    cont = base + "  "
    out, cur = [], indent
    for t in tokens(body):
        pieces = [t]
        if len(cont) + len(t) > WIDTH and t.startswith('"'):
            pieces = cat_string(t, WIDTH - len(cont))
        for p in pieces:
            if cur.strip() and len(cur) + 1 + len(p) > WIDTH:
                out.append(cur)
                cur = cont + p
            else:
                cur = cur + (" " if cur.strip() else "") + p
    return out + [cur]


def wrap_cddl(text):
    """The CDDL at WIDTH columns. A run of comment lines with a long line is reflowed as one
    paragraph; a trailing comment, with the aligned comment lines that continue it, moves above
    its rule; a long rule breaks between tokens; a choice line that continues a rule is indented
    two columns under the rule it continues."""
    src = text.splitlines()
    out, base, i = [], "", 0
    is_comment = lambda l: l.lstrip().startswith(";")
    while i < len(src):
        line = src[i]
        indent = re.match(r"\s*", line).group(0)
        if is_comment(line):
            j = i
            while j < len(src) and is_comment(src[j]) and re.match(r"\s*", src[j]).group(0) == indent:
                j += 1
            block = src[i:j]
            if any(len(l) > WIDTH for l in block):
                para = " ".join(l.strip()[1:].strip() for l in block)
                out += [f"{indent}; {c}" for c in textwrap.wrap(para, WIDTH - len(indent) - 2, break_on_hyphens=False)]
            else:
                out += block
            i = j
            continue
        body, comment = split_comment(line)
        if body.lstrip().startswith("/ "):
            body = base + "  " + body.lstrip()
        else:
            base = indent
        j = i + 1
        if comment is not None:
            while j < len(src) and is_comment(src[j]) and len(re.match(r"\s*", src[j]).group(0)) > len(indent) + 4:
                comment += " " + src[j].strip()[1:].strip()
                j += 1
        if j == i + 1 and len(line) <= WIDTH and body == line[:len(body)]:
            out.append(line)
        else:
            cindent = re.match(r"\s*", body).group(0)
            if comment:
                out += [f"{cindent}; {c}" for c in textwrap.wrap(comment, WIDTH - len(cindent) - 2, break_on_hyphens=False)]
            out += [body] if len(body) <= WIDTH else wrap_body(body, base)
        i = j
    long = [l for l in out if len(l) > WIDTH]
    if long:
        sys.exit("build_ietf_draft: CDDL lines still too long:\n" + "\n".join(long))
    return "\n".join(out) + "\n"


def check_cddl(path):
    """Parse the CDDL at `path` and run the generator's samples against it: (lines, problems)."""
    if not find_tool("cddl"):
        sys.exit("build_ietf_draft: cddl not found")
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import build_cc_signed_object_v2 as v2
    lines, bad = v2.cddl_checks(open(path, encoding="utf-8").read())
    if bad:
        sys.exit(f"build_ietf_draft: {os.path.relpath(path, ROOT)}: " + "; ".join(bad))
    return [l for l in lines if "parses" not in l]


def wrapped_cddl(text=None):
    text = open(CDDL_IN, encoding="utf-8").read() if text is None else text
    return wrap_cddl(text.replace("\u2014", "-").replace("\u00a7", "Section "))


def build_draft(rev, out, cddl):
    """kramdown-rfc and xml2rfc over the source, in directory `out`, which holds `cddl` as signed_object.cddl."""
    name = f"draft-moore-scitt-ciris-ceg-{rev}"
    src = open(SRC, encoding="utf-8").read()
    src = src.replace("docname: draft-moore-scitt-ciris-ceg-latest", f"docname: {name}")
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
        lines = check_cddl(tmp)
        print(f"CDDL wrapped to {WIDTH} columns; parses; " + "; ".join(lines))
    check_cddl(CDDL_IN)
    print("manifests/signed_object_v2.cddl parses; the same samples validate and the same breaks are refused")
    # the deliberate break: the same source with its algorithm identifier altered must not compare equal
    src = open(CDDL_IN, encoding="utf-8").read()
    if src.count(BREAK[0]) != 1:
        sys.exit(f"build_ietf_draft: {BREAK[0]!r} is not in manifests/signed_object_v2.cddl once, for the deliberate break")
    if differs(wrapped_cddl(src.replace(*BREAK)), CDDL_OUT) is None:
        sys.exit("build_ietf_draft: the deliberate break (an altered algorithm identifier) was not caught")
    print("deliberate break caught: an altered algorithm identifier makes ietf/signed_object.cddl stale")
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
    rev = argv[argv.index("--rev") + 1] if "--rev" in argv else REV
    if "--check" in argv:
        check(rev)
        return
    wrapped = wrapped_cddl()
    open(CDDL_OUT, "w", encoding="utf-8").write(wrapped)
    lines = check_cddl(CDDL_OUT)
    print(f"CDDL wrapped to {WIDTH} columns; parses; " + "; ".join(lines))
    name = build_draft(rev, IETF, wrapped)
    print(f"built ietf/{name}.xml, .txt, .html with no xml2rfc warnings")

    if "--idnits" in argv:
        boundary = "----ccdraft"
        body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}.xml\"\r\n"
                f"Content-Type: application/xml\r\n\r\n").encode() + open(os.path.join(IETF, name + ".xml"), "rb").read() + \
               f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"submitcheck\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request("https://author-tools.ietf.org/api/idnits", data=body,
                                     headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        report = urllib.request.urlopen(req, timeout=120).read().decode()
        open(os.path.join(IETF, name + ".idnits.txt"), "w").write(report)
        print(report[-1500:])


if __name__ == "__main__":
    main(sys.argv[1:])
