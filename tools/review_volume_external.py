#!/usr/bin/env python3
"""
CC — an outside-model review of one rendered volume.

Sends a volume's text (pdftotext -layout) with the review brief to a model served by OpenRouter and
writes the model's report. The brief is the same one the in-house reviewers use, so passes by
different model families are comparable. The key is read from ~/.openrouter_key and never printed.

Run:  python3 tools/review_volume_external.py <volume> [--model x-ai/grok-4.7] [--out DIR] [--max-tokens N]
      python3 tools/review_volume_external.py all --model x-ai/grok-4.7 --out review/notes/pass3_grok
volume ∈ charter constitution wire dictionary policies maths register threats digest, or all.
Needs: pdftotext (poppler), a built volumes/ciris_constitution-<VERSION>-<volume>.pdf, the brief at
review/VOLUME_REVIEW_BRIEF.md.
"""
import json, os, re, subprocess, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = open(os.path.join(ROOT, "VERSION")).read().strip()
VOLUMES = ["charter", "constitution", "wire", "dictionary", "policies", "maths", "register", "threats", "digest"]
TITLES = {"charter": "The Charter", "constitution": "The Constitution", "wire": "The Wire", "dictionary": "The Dictionary",
          "policies": "The Reader's Policies", "maths": "The Mathematics", "register": "The Evidence Register",
          "threats": "The Threat Model", "digest": "The Digest"}
BRIEF = os.path.join(ROOT, "review", "VOLUME_REVIEW_BRIEF.md")


def volume_text(vol):
    pdf = os.path.join(ROOT, "volumes", f"ciris_constitution-{VERSION}-{vol}.pdf")
    if not os.path.exists(pdf):
        sys.exit(f"review_volume_external: {pdf} not built (python3 build_pdf.py --volume {vol})")
    pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
    out = []
    for p in range(1, pages + 1):
        t = subprocess.run(["pdftotext", "-layout", "-f", str(p), "-l", str(p), pdf, "-"], capture_output=True, text=True).stdout
        out.append(f"\n\n===== page {p} =====\n{t}")
    return pages, "".join(out)


def review(vol, model, out_dir, max_tokens=12000):
    pages, text = volume_text(vol)
    brief = open(BRIEF, encoding="utf-8").read()
    prompt = (f"{brief}\n\n---\n\nYour volume: \"{TITLES[vol]}\" (ciris_constitution-{VERSION}-{vol}.pdf, {pages} pages). "
              f"The full text follows, one block per page, with page markers for your page references. "
              f"Produce only the structured report the brief specifies.\n\n{text}")
    key = open(os.path.expanduser("~/.openrouter_key")).read().strip()
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.2, "max_tokens": max_tokens}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                          "HTTP-Referer": "https://github.com/CIRISAI/CIRISConstitution", "X-Title": "CC volume review"})
    t0 = time.time()
    resp = json.load(urllib.request.urlopen(req, timeout=1800))
    content = resp["choices"][0]["message"]["content"]
    usage = resp.get("usage", {})
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{vol}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.rstrip() + f"\n\n<!-- model {model}; {pages} pages; prompt_tokens {usage.get('prompt_tokens')}; completion_tokens {usage.get('completion_tokens')}; {time.time()-t0:.0f}s -->\n")
    m = re.search(r"\*\*Care score:\*\*\s*(\d)", content)
    print(f"{vol}: care {m.group(1) if m else '?'}; {usage.get('prompt_tokens')} in / {usage.get('completion_tokens')} out; {time.time()-t0:.0f}s -> {os.path.relpath(path, ROOT)}")


def main(argv):
    model = argv[argv.index("--model") + 1] if "--model" in argv else "x-ai/grok-4.7"
    out_dir = argv[argv.index("--out") + 1] if "--out" in argv else os.path.join(ROOT, "review", "notes", "pass3_external")
    max_tokens = int(argv[argv.index("--max-tokens") + 1]) if "--max-tokens" in argv else 12000
    vols = VOLUMES if argv[0] == "all" else [argv[0]]
    for v in vols:
        review(v, model, out_dir, max_tokens)


if __name__ == "__main__":
    main(sys.argv[1:])
