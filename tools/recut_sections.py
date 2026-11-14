#!/usr/bin/env python3
"""
recut_sections.py: the decimal re-cut of the Parts, run from a map, in one pass.

The map is formal/derivation/section_map.tsv: one row per numbered section, old number to new number,
with the section's semantic slug (the stable id) and title. The tool rewrites every reference to a
section number across the repository from that map, and refuses to run on a tree the map does not fit.

  --make-map [--part1]   derive the map from the Parts as they stand (depth at most four, by promoting a
                         deeper section to a sibling under its depth-3 ancestor, in document order; gaps
                         closed). A title proposed in an existing map row is kept. Part 1 is held as it
                         stands unless --part1 is given.
  --inventory OUT        write every reference to a section number by file and kind (tab-separated)
  --check                dry run: print what would change, exit 1 if anything would (the quote repairs,
                         which read the rewritten Parts, are made and listed by --apply)
  --apply                rewrite; a second run is a no-op (the headings say which side of the map the tree
                         is on; a tree half on each side is refused)
  --regen                run the generators, in order, after --apply
  --verify               after --apply and --regen: links resolve, sections counted, quotes found, and
                         every number that exists only on the old side is reported wherever it appears

What it rewrites: the numbered headings of constitution/part_*.md (number, level, a title the map
renames); every token equal to a renumbered section in every text file in scope (CC references and
their lists and ranges, link anchors and link texts, table cells, JSON keys and values, quoted code
literals, bare numbers in prose of three levels or more). A two-level number is rewritten only in a CC
reference, an anchor or a data cell. After the rewrite, a row of a quoted-text table (cc_ref and quote
columns) whose quote now lies outside the cited section's span, because a subsection was promoted out of
it, is re-cited to the section that holds the quote.

What it never touches: constitution/vendor/ (pinned implementers' manifests), handoff/, CHANGELOG.md
(release history cites each release's own numbers), REFACTOR_NOTES.md, the map itself, the generated
files and the generated blocks of the Parts (CC 2.6.1.7's body, the policy table of CC 4.5.13, the cards
of CC 8.10, the DATA section of FamilyModel.lean): those are rebuilt by --regen from the rewritten sources.
"""
import argparse
import csv
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = os.path.join(ROOT, "formal", "derivation", "section_map.tsv")
# The reviewed rewrites: a prose reference to a section whose subsections are promoted out, read by hand and
# kept (the head is meant), pointed at one promoted section, or widened to the range of the group; texts are in
# the NEW numbering and are applied after the mechanical rewrite. Also wildcards and shorthand ranges.
REWRITES = os.path.join(ROOT, "formal", "derivation", "section_map_rewrites.tsv")
REWRITE_KINDS = ("keep", "child", "range", "literal", "wildcard", "cite")
COLS = ["old_number", "old_anchor", "old_slug", "new_number", "new_anchor", "new_slug", "title", "moved", "note"]
HEAD = re.compile(r"^(#{1,7}) (\d+(?:\.\d+)+) `([^`]+)`(?: — (.*))?$")
MAX_DEPTH = 4

EXCLUDE_PREFIX = ("constitution/vendor/", "handoff/", "volumes/", ".git/")
EXCLUDE_FILE = {"CHANGELOG.md", "REFACTOR_NOTES.md", "formal/derivation/section_map.tsv",
                "formal/derivation/section_map_rewrites.tsv", "tools/recut_sections.py"}
TEXT_EXT = (".md", ".tsv", ".json", ".py", ".lean", ".tla", ".cfg", ".kx", ".txt", ".yaml", ".yml", ".cddl",
            ".sh", ".xml", ".csv", ".toml", ".rs", ".als", ".smt2", ".dfy")

# Generated files: rebuilt by GENERATORS, never rewritten by hand or by this tool.
GENERATED = {
    "manifests/namespace_registry.json": "tools/build_cc_namespace.py",
    "manifests/namespace_match_vectors.json": "tools/cc_namespace_match.py --write-vectors",
    "manifests/signed_object.json": "tools/build_cc_signed_object.py",
    "manifests/signed_object.cddl": "tools/build_cc_signed_object.py",
    "manifests/governance_policy.json": "tools/build_governance_policy.py",
    "manifests/governance_policy_vectors.json": "tools/build_governance_policy.py",
    "formal/two_path/generated/": "tools/build_governance_policy.py",
    "manifests/csd4_chain.json": "tools/build_csd4_chain.py",
    "formal/cewp_node/generated/": "tools/topology_to_cfg.py --all",
    "manifests/family_model.json": "tools/build_family_model.py",
    "manifests/family_departures.tsv": "tools/build_family_model.py",
    "formal/family_model/DEPARTURES.md": "tools/build_family_model.py",
    "ietf/draft-moore-scitt-ciris-ceg-00.txt": "tools/build_ietf_draft.py",
    "ietf/draft-moore-scitt-ciris-ceg-00.xml": "tools/build_ietf_draft.py",
    "ietf/draft-moore-scitt-ciris-ceg-00.html": "tools/build_ietf_draft.py",
    "ietf/draft-moore-scitt-ciris-ceg-00.md": "tools/build_ietf_draft.py",
    "ietf/signed_object.cddl": "tools/build_ietf_draft.py",
    "manifests/transitions.json": "tools/build_transitions.py",
    "manifests/transitions.tsv": "tools/build_transitions.py",
    "manifests/reactions.json": "tools/build_reactions.py",
    "manifests/mesh_story_trace.json": "tools/mesh_story.py",
    "formal/derivation/family_need.tsv": "tools/family_need.py --write",
    "manifests/divergences.json": "tools/build_divergences.py",
    "manifests/divergences.tsv": "tools/build_divergences.py",
    "manifests/divergences/": "tools/build_divergences.py",
    "formal/derivation/text_lints/": "tools/check_text_lints.py",          # worklists, written on every run
    "formal/derivation/restatements_uncited.tsv": "tools/check_restatements.py",
}
# In order: each reads what the ones before it wrote (the order of tools/gates.sh and tools/regen.sh).
GENERATORS = [
    "python3 tools/build_cc_namespace.py",
    "python3 tools/cc_namespace_match.py --write-vectors",
    "python3 tools/build_cc_signed_object.py",
    "python3 tools/build_governance_policy.py",
    "python3 tools/build_csd4_chain.py",
    "python3 tools/topology_to_cfg.py --all",
    "python3 tools/build_promise_status.py",
    "python3 build_pdf.py --write-toc-volumes",
    "python3 tools/build_family_model.py",
    "python3 tools/build_ietf_draft.py",
    "python3 tools/build_transitions.py",
    "python3 tools/build_reactions.py",
    "python3 -I tools/mesh_story.py",
    "python3 tools/family_card.py --write",
    "python3 tools/family_need.py --write",
    "python3 tools/check_family_kinds.py",
    "python3 tools/build_divergences.py",
    "python3 tools/check_restatements.py",
    "python3 tools/check_text_lints.py",
]
# The checks --verify runs after the generators (exit codes reported, not interpreted).
CHECKS = [
    "python3 tools/fix_entries.py",
    "python3 tools/check_links.py --quiet",
    "python3 tools/check_stale_refs.py --counts",
    "python3 tools/check_claims.py",
    "python3 tools/check_formal_tables.py",
    "python3 tools/check_formal_counts.py",
    "python3 tools/check_lifecycle_coverage.py",
    "python3 tools/build_family_model.py --check",
    "python3 tools/build_transitions.py --check",
    "python3 tools/build_reactions.py --check",
    "python3 tools/family_card.py --check",
    "python3 -I tools/mesh_story.py --check",
    "python3 tools/family_need.py --check",
    "python3 tools/check_family_kinds.py --check",
    "python3 tools/check_rule_entries.py",
    "python3 tools/check_transition_roles.py",
    "python3 tools/check_signer_gate.py",
    "python3 tools/check_ui_primitives.py",
    "python3 tools/check_compliance_wire_forms.py",
    "python3 -I formal/causal_kernel/check_shapes.py",
    "python3 tools/guard_grammar.py",
    "python3 tools/change_grammar.py",
    "python3 tools/fold_grammar.py",
    "python3 -I tools/check_fold_order.py",
    "python3 tools/build_divergences.py --check",
    "python3 tools/check_divergences.py",
    "python3 formal/takedown/takedown_model.py --check",
    "python3 formal/deletion/deletion_model.py --check",
    "python3 formal/owner_binding/owner_binding_model.py --check",
    "python3 formal/key_plane/key_plane_model.py --check",
    "python3 formal/guardianship/guardianship_model.py --check",
    "python3 formal/ranked_choice/ranked_choice_model.py --check",
    "python3 formal/set_item/set_item_model.py --check",
    "python3 -I formal/kernel_lib/kernel_lib_check.py --check",
    "python3 -I formal/roster_fork/fork_check.py --check",
    "python3 tools/ui_closure.py --check",
    "python3 tools/check_termination.py",
    "python3 tools/kernel_closure.py --check",
    "python3 tools/kernel_requirements.py --check",
    "python3 -I formal/transport_tiers/frame_ab.py --check",
    "python3 tools/check_restatements.py",
    "python3 tools/check_text_lints.py",
    "python3 -I formal/screen/check_screen.py",
    "python3 -B tools/kx_check.py --check --workers 2",
]
# formal/causal_kernel/check_door.py, check_rosters.py and check_purge.py read tables that cite sections; each is
# run once, alone, by hand (RUNBOOK), as is formal/causal_order/build.sh (Lean), not from this list.

# A section-number token: not inside a word or a longer number; ".x" after it is a subtree wildcard.
TOKEN = re.compile(r"(?<![\w.])(\d+(?:\.\d+)+)(?![\w]|\.\w)")
ESCAPED = re.compile(r"(?<![\w.\\])(\d+(?:\\\.\d+)+)(?![\w]|\\\.\w)")   # 8\.8\.10 inside a regex in code
WILDCARD = re.compile(r"(?<![\w.])(\d+(?:\.\d+)+)\.(?:x|\*|X)\b")


def rel(p):
    return os.path.relpath(p, ROOT)


def part_files():
    return sorted(glob.glob(os.path.join(ROOT, "constitution", "part_*.md")))


def parse_parts():
    """Numbered headings in document order: dicts with file, line (0-based), level, num, slug, title."""
    out = []
    for f in part_files():
        fence = False
        for i, line in enumerate(open(f, encoding="utf-8").read().split("\n")):
            if line.lstrip().startswith("```"):
                fence = not fence
                continue
            if fence:
                continue
            m = HEAD.match(line)
            if m:
                out.append(dict(file=rel(f), line=i, level=len(m.group(1)), num=m.group(2), slug=m.group(3),
                                title=m.group(4) or ""))
    return out


# ---------------------------------------------------------------- the map

def make_map(secs, hold, old_rows):
    keep = {r["old_slug"]: r for r in old_rows}
    newnum, counter, rows = {}, {}, []
    for s in secs:
        parts = s["num"].split(".")
        part = parts[0]
        if part in hold:
            new = s["num"]
        else:
            d = len(parts)
            if d <= MAX_DEPTH:
                parent_new = newnum.get(".".join(parts[:-1]), ".".join(parts[:-1]))
            else:
                parent_new = newnum.get(".".join(parts[:MAX_DEPTH - 1]), ".".join(parts[:MAX_DEPTH - 1]))
            counter[parent_new] = counter.get(parent_new, 0) + 1
            new = f"{parent_new}.{counter[parent_new]}"
        newnum[s["num"]] = new
        old_parent = s["num"].rsplit(".", 1)[0]
        moved = new.rsplit(".", 1)[0] != newnum.get(old_parent, old_parent)
        prev = keep.get(s["slug"], {})
        title = prev.get("title") or s["title"]
        note = []
        if title != s["title"]:
            note.append("renamed: was \"" + s["title"] + "\"")
        if moved:
            note.append(f"promoted out of {old_parent}")
        if part in hold and part == "1":
            note.append("Part 1 held (the owner's)")
        rows.append(dict(old_number=s["num"], old_anchor="#" + s["num"], old_slug=s["slug"], new_number=new,
                         new_anchor="#" + new, new_slug=prev.get("new_slug") or s["slug"], title=title,
                         moved="yes" if moved else "no", note="; ".join(note)))
    return rows


def read_map():
    with open(MAP, encoding="utf-8") as fh:
        lines = [l for l in fh.read().split("\n") if l and not l.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t", quoting=csv.QUOTE_NONE))


def write_map(rows):
    head = ("# The decimal re-cut: one row per numbered section of the Parts, old number to new number. "
            "Built by tools/recut_sections.py --make-map; applied by --apply. The slug is the stable id across editions.\n")
    with open(MAP, "w", encoding="utf-8") as fh:
        fh.write(head + "\t".join(COLS) + "\n")
        for r in rows:
            fh.write("\t".join(r[c] for c in COLS) + "\n")


def tree_state(secs, rows):
    """'pending' (headings on the old side), 'applied' (on the new side), or raise with the mismatch."""
    by_slug = {s["slug"]: s for s in secs}
    old_side = new_side = 0
    bad = []
    for r in rows:
        s = by_slug.get(r["old_slug"]) or by_slug.get(r["new_slug"])
        if s is None:
            bad.append(f"no heading for {r['old_number']} `{r['old_slug']}`")
            continue
        o, n = s["num"] == r["old_number"], s["num"] == r["new_number"]
        old_side += o
        new_side += n
        if not (o or n):
            bad.append(f"`{s['slug']}` is {s['num']}, the map says {r['old_number']} -> {r['new_number']}")
    known = {r["old_slug"] for r in rows} | {r["new_slug"] for r in rows}
    bad += [f"heading {s['num']} `{s['slug']}` has no map row" for s in secs if s["slug"] not in known]
    if bad:
        raise SystemExit("recut: the map does not fit the Parts (run --make-map):\n  " + "\n  ".join(bad[:30]))
    moving = sum(1 for r in rows if r["old_number"] != r["new_number"])
    if moving == 0 or old_side == len(rows):
        return "pending"
    if new_side == len(rows):
        return "applied"
    raise SystemExit(f"recut: the tree is half re-cut ({old_side} headings old, {new_side} new); refusing")


# ---------------------------------------------------------------- scope

def in_scope():
    try:
        files = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).split("\n")
    except Exception:
        files = [rel(os.path.join(d, f)) for d, _, fs in os.walk(ROOT) for f in fs]
    out = []
    for f in files:
        if not f or not f.endswith(TEXT_EXT) or f.startswith(EXCLUDE_PREFIX) or f in EXCLUDE_FILE:
            continue
        if any(f == g or (g.endswith("/") and f.startswith(g)) for g in GENERATED):
            continue
        if os.path.isfile(os.path.join(ROOT, f)):
            out.append(f)
    return out


def generated_lines(path, lines):
    """Line indexes of a Part (or the Lean family model) that a generator writes."""
    skip = set()
    if path == "formal/family_model/FamilyModel.lean":
        inside = False
        for i, l in enumerate(lines):
            if "DATA BEGIN" in l:
                inside = True
            if inside:
                skip.add(i)
            if "DATA END" in l:
                inside = False
        return skip
    if not path.startswith("constitution/part_"):
        return skip
    for i, l in enumerate(lines):
        m = HEAD.match(l)
        if m and m.group(3) == "signed-object":                 # CC 2.6.1.7: heading kept, body generated
            j = i + 1
            while j < len(lines) and not re.match(r"^#{2,6}\s+\d", lines[j]):
                skip.add(j)
                j += 1
        if m and m.group(3) == "family-cards":                  # CC 8.10: the whole section to the end
            skip.update(range(i + 1, len(lines)))
        if "The rows are these, generated into this section from the table:" in l:   # CC 4.5.13 table
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                skip.add(j)
                j += 1
    return skip


# ---------------------------------------------------------------- rewriting

def classify(text, start, end):
    before = text[max(0, start - 4):start]
    if before.endswith("#"):
        return "anchor"
    if re.search(r"CC[\s ]$", before) or re.search(r"§\s?$", before):
        return "cc"
    if before.endswith("[") and text[end:end + 2] == "](":
        return "link-text"
    return "bare"


def is_data(path):
    return path.endswith((".tsv", ".json", ".csv", ".yaml", ".yml"))


def is_code(path):
    return path.endswith((".py", ".lean", ".tla", ".cfg", ".kx", ".sh", ".rs"))


def kind_of(path, cls):
    if cls == "anchor":
        return "anchor link"
    if cls in ("cc", "link-text"):
        return "CC reference" if not is_data(path) else "data cell (CC form)"
    if is_data(path):
        return "data cell"
    if is_code(path):
        return "code string"
    return "bare reference"


def rewrite_line(path, line, change, report, lineno):
    def sub(m):
        tok = m.group(1)
        new = change.get(tok)
        if new is None:
            return tok
        cls = classify(line, m.start(1), m.end(1))
        if tok.count(".") < 2 and cls == "bare" and not is_data(path):
            report.append((path, lineno, tok, None, "two-level bare number left (ambiguous)"))
            return tok
        report.append((path, lineno, tok, new, kind_of(path, cls)))
        return new
    for w in WILDCARD.finditer(line):
        if w.group(1) in change:
            report.append((path, lineno, w.group(1) + ".x", None, "subtree wildcard left (its children moved)"))
    line = TOKEN.sub(sub, line)
    if is_code(path):
        def esc(m):
            tok = m.group(1).replace("\\.", ".")
            new = change.get(tok)
            if new is None:
                return m.group(1)
            report.append((path, lineno, tok, new, "code string (regex-escaped)"))
            return new.replace(".", "\\.")
        line = ESCAPED.sub(esc, line)
    return line


def heading_line(line, row):
    m = HEAD.match(line)
    new = row["new_number"]
    title = row["title"]
    out = "#" * (new.count(".") + 1) + " " + new + " `" + m.group(3) + "`"
    if m.group(4) is not None:
        out += " — " + title
    return out


def apply_all(rows, write):
    secs = parse_parts()
    state = tree_state(secs, rows)
    change = {r["old_number"]: r["new_number"] for r in rows if r["old_number"] != r["new_number"]}
    if state == "applied":
        return state, [], {}, 0
    for r in rows:
        if r["new_slug"] != r["old_slug"]:
            raise SystemExit(f"recut: a slug rename ({r['old_slug']} -> {r['new_slug']}) is not supported; "
                             "the slug is the id that survives the re-cut")
    by_file_line = {(s["file"], s["line"]): s for s in secs}
    by_slug = {r["old_slug"]: r for r in rows}
    spans_before = section_spans()
    report, edits, nfiles = [], {}, 0
    table, bad = {}, []
    for r in read_rewrites():
        table.setdefault(r["file"], []).append(r)
    for path in in_scope():
        full = os.path.join(ROOT, path)
        try:
            text = open(full, encoding="utf-8").read()
        except UnicodeDecodeError:
            continue
        lines = text.split("\n")
        skip = generated_lines(path, lines)
        out = []
        for i, line in enumerate(lines):
            if i in skip:
                out.append(line)
                continue
            s = by_file_line.get((path, i))
            if s is not None:
                r = by_slug[s["slug"]]
                new = heading_line(line, r)
                if new != line:
                    report.append((path, i + 1, s["num"], r["new_number"], "heading"))
                out.append(new)
                continue
            out.append(rewrite_line(path, line, change, report, i + 1))
        new_text = "\n".join(out)
        if path in table:
            new_text = apply_rewrites(path, new_text, table[path], report, bad)
        if path == "constitution/toc.tsv":
            new_text = retitle_toc(new_text, rows, report)
        if new_text != text:
            nfiles += 1
            edits[path] = new_text
    repoint_inventory(edits, report, bad)
    # a wildcard a reviewed row rewrote is no longer left
    report[:] = [x for x in report if not (x[4].startswith("subtree wildcard") and x[2] not in edits.get(x[0], x[2]))]
    missing = sorted(set(table) - set(in_scope()))
    bad += [f"{p}: a reviewed rewrite names a file out of scope or absent" for p in missing]
    unreviewed = group_references(rows, edits, table)
    for p, ln, n in unreviewed:
        report.append((p, ln, n, None, "unreviewed reference to a section whose subsections were promoted out"))
    if bad:
        raise SystemExit("recut: the reviewed rewrites do not fit the tree (read them again against the Parts):\n  "
                         + "\n  ".join(bad[:40]))
    if write:
        for path, t in edits.items():
            open(os.path.join(ROOT, path), "w", encoding="utf-8").write(t)
        fix_quotes(rows, spans_before, report, write)
    return state, report, edits, nfiles


def read_rewrites():
    if not os.path.exists(REWRITES):
        return []
    with open(REWRITES, encoding="utf-8") as fh:
        lines = [l for l in fh.read().split("\n") if l and not l.startswith("#")]
    out = list(csv.DictReader(lines, delimiter="\t", quoting=csv.QUOTE_NONE))
    for r in out:
        if r["kind"] not in REWRITE_KINDS:
            raise SystemExit(f"recut: rewrite kind {r['kind']!r} is not one of {REWRITE_KINDS}")
        if (r["kind"] == "keep") != (r["old_text"] == r["new_text"]):
            raise SystemExit(f"recut: a 'keep' row changes its text, or another row does not: {r['old_text'][:60]}")
    return out


REPOINT = []        # (part file, line, section, head, promoted section) of each 'child' rewrite


def repoint_inventory(edits, report, bad):
    """An inventory row of the section a 'child' rewrite stands in, pointing at the head, points at the promoted
    section the sentence now cites (formal/derivation/rule_inventory.tsv `points_to`)."""
    path = "formal/derivation/rule_inventory.tsv"
    text = edits.get(path) or open(os.path.join(ROOT, path), encoding="utf-8").read()
    lines = text.split("\n")
    head = lines[0].split("\t")
    fi, si, pi = head.index("file"), head.index("section"), head.index("points_to")
    words = lambda t: set(re.findall(r"[a-z]{4,}", t.lower()))
    gi = head.index("gist")
    for part, line, sec, old, new, said in REPOINT:
        pn = "p" + os.path.basename(part).split("_")[1]
        hits = [k for k, l in enumerate(lines[1:], 1) for c in [l.split("\t")]
                if len(c) > pi and c[fi] == pn and c[si] == sec and old in c[pi].split(",")]
        # several rows of the section point at the head: the one whose gist says what the rewritten line says
        score = sorted(((len(words(lines[k].split("\t")[gi]) & words(said)), k) for k in hits), reverse=True)
        if len(score) > 1 and score[0][0] == score[1][0]:
            bad.append(f"{path}: rows {[k + 1 for _, k in score]} of {pn} {sec} point at {old}; the rewrite at "
                       f"{part}:{line} names one and no gist says it best")
        for _, k in score[:1]:
            c = lines[k].split("\t")
            c[pi] = ",".join(new if x == old else x for x in c[pi].split(","))
            lines[k] = "\t".join(c)
            report.append((path, k + 1, old, new, "inventory points_to follows a reviewed rewrite"))
    new_text = "\n".join(lines)
    if new_text != text:
        edits[path] = new_text


def apply_rewrites(path, text, rows, report, bad):
    """Every row's old_text must stand `count` times in the mechanically rewritten text; then each is replaced."""
    for r in rows:
        n = text.count(r["old_text"])
        if n != int(r["count"]) and r["kind"] == "keep":
            # a kept reference edited since the review: nothing to rewrite; a new reference shows as unreviewed
            report.append((path, 0, r["old_text"][:60], None, "keep row no longer in the text (read it)"))
        elif n != int(r["count"]):
            bad.append(f"{path}: {r['kind']} row found {n} time(s), expected {r['count']}: {r['old_text'][:90]!r}")
    for r in rows:
        if r["kind"] == "keep" or text.count(r["old_text"]) != int(r["count"]):
            continue
        line = text[:text.index(r["old_text"])].count("\n") + 1
        if r["kind"] == "child" and path.startswith("constitution/part_"):
            o = re.search(r"\d+(?:\.\d+)+", r["old_text"][len(os.path.commonprefix([r["old_text"], r["new_text"]])) - 12:])
            n = re.search(r"\d+(?:\.\d+)+", r["new_text"][len(os.path.commonprefix([r["old_text"], r["new_text"]])) - 12:])
            sec = next((m.group(2) for l in reversed(text.split("\n")[:line]) for m in [HEAD.match(l)] if m), None)
            REPOINT.append((path, line, sec, o.group(0), n.group(0), text.split("\n")[line - 1]))
        text = text.replace(r["old_text"], r["new_text"])
        report.append((path, line, r["old_text"][:40], r["new_text"][:40], "reviewed rewrite (" + r["kind"] + ")"))
    return text


def group_heads(rows):
    """New numbers of the sections a promoted subsection left (the parents, at any depth above it)."""
    old2new = {r["old_number"]: r["new_number"] for r in rows}
    heads = set()
    for r in rows:
        if r["moved"] != "yes":
            continue
        parts = r["old_number"].split(".")
        new_parent = r["new_number"].rsplit(".", 1)[0]
        for k in range(len(parts) - 1, 0, -1):
            anc = ".".join(parts[:k])
            if old2new.get(anc, anc) == new_parent:
                break
            heads.add(old2new.get(anc, anc))
    return heads


def group_references(rows, edits, table):
    """(file, line, number): a reference in the prose of a Part, after the rewrite, to a section whose
    subsections were promoted out, that no reviewed row covers. Tables, headings, fences and generated
    lines are not prose and are not listed."""
    heads = group_heads(rows)
    left = []
    for f in part_files():
        path = rel(f)
        text = edits.get(path) or open(f, encoding="utf-8").read()
        lines = text.split("\n")
        skip = generated_lines(path, lines)
        covered = [r["new_text"] for r in table.get(path, [])]
        fence = False
        for i, l in enumerate(lines):
            if l.lstrip().startswith("```"):
                fence = not fence
                continue
            if fence or i in skip or l.startswith("|") or HEAD.match(l):
                continue
            have = {}
            for m in TOKEN.finditer(l):
                if m.group(1) in heads:
                    have[m.group(1)] = have.get(m.group(1), 0) + 1
            for n, k in have.items():
                # every token of the head on the line must stand inside a reviewed row's text
                got = sum(l.count(c) * sum(1 for t in TOKEN.finditer(c) if t.group(1) == n) for c in covered if c in l)
                for _ in range(k - min(k, got)):
                    left.append((path, i + 1, n))
    return left


def retitle_toc(text, rows, report):
    titles = {r["old_slug"]: r["title"] for r in rows if "renamed" in r["note"]}
    lines = text.split("\n")
    head = lines[0].split("\t")
    if "semantic_id" not in head or "title" not in head:
        return text
    si, ti = head.index("semantic_id"), head.index("title")
    for k, l in enumerate(lines[1:], 1):
        c = l.split("\t")
        if len(c) > ti and c[si] in titles and c[ti] != titles[c[si]]:
            c[ti] = titles[c[si]]
            lines[k] = "\t".join(c)
            report.append(("constitution/toc.tsv", k + 1, c[si], titles[c[si]], "toc title"))
    return "\n".join(lines)


# ---------------------------------------------------------------- spans and quotes

def section_spans():
    """number -> the text of the section with its subsections (the reading of tools/build_family_model.py)."""
    spans = {}
    for f in part_files():
        lines = open(f, encoding="utf-8").read().split("\n")
        heads = []
        fence = False
        for i, l in enumerate(lines):
            if l.lstrip().startswith("```"):
                fence = not fence
            m = None if fence else re.match(r"#{1,6} (\d+(?:\.\d+)*)(?= |$)", l)
            if m:
                heads.append((i, m.group(1)))
        for k, (i, num) in enumerate(heads):
            end = len(lines)
            for j, other in heads[k + 1:]:
                if not other.startswith(num + "."):
                    end = j
                    break
            spans[num] = "\n".join(lines[i:end])
    return spans


def own_spans():
    """number -> the text of the section up to its first numbered subheading."""
    spans = {}
    for f in part_files():
        lines = open(f, encoding="utf-8").read().split("\n")
        heads = [(i, m.group(1)) for i, l in enumerate(lines) for m in [re.match(r"#{1,6} (\d+(?:\.\d+)*)(?= |$)", l)] if m]
        for k, (i, num) in enumerate(heads):
            end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
            spans[num] = "\n".join(lines[i:end])
    return spans


def quote_tables():
    """(path, ref column, quote column, style): every table whose quote must stand in the section it cites.
    style 'cc' cites as "CC x.y" (a cell may name several); 'bare' cites one bare number."""
    out = []
    for path in in_scope():
        if not path.endswith(".tsv"):
            continue
        lines = open(os.path.join(ROOT, path), encoding="utf-8").read().split("\n")
        body = [l for l in lines if l and not l.startswith("#")]
        if not body:
            continue
        head = body[0].split("\t")
        if "cc_ref" in head and "quote" in head:
            out.append((path, head.index("cc_ref"), head.index("quote"), "cc"))
        elif "home" in head and "entry_phrase" in head:
            out.append((path, head.index("home"), head.index("entry_phrase"), "bare"))
    return out


def refs_of(cell, style="cc"):
    if style == "bare":
        return [cell.strip()] if re.fullmatch(r"\d+(?:\.\d+)*", cell.strip()) else []
    return re.findall(r"CC (\d+(?:\.\d+)*)", cell)


def rewrite_cores():
    """(old, new) for each changing reviewed rewrite of a Part: the differing middle, widened to whitespace, so a
    quoted-text table that quotes the rewritten sentence can follow it."""
    out = []
    for r in read_rewrites():
        if r["kind"] == "keep" or not r["file"].startswith("constitution/part_"):
            continue
        o, n = r["old_text"], r["new_text"]
        a = 0
        while a < min(len(o), len(n)) and o[a] == n[a]:
            a += 1
        b = 0
        while b < min(len(o), len(n)) - a and o[-1 - b] == n[-1 - b]:
            b += 1
        while a > 0 and not o[a - 1].isspace():
            a -= 1
        while b > 0 and not o[len(o) - b].isspace():
            b -= 1
        out.append((o[a:len(o) - b], n[a:len(n) - b]))
    return out


def fix_quotes(rows, spans_before, report, write):
    """After the rewrite, a quote that no longer stands in the section it cites is repaired in one of two ways.
    Cut inside a section number (the quote ends "[CC 4.4.3.4.3" of "[CC 4.4.3.4.3.1]"): the cut number is
    dropped, so the quote stays a verbatim substring. Cited at a section whose subsection was promoted out of
    it ('cc' tables only; a 'bare' home is the inventory's key and is not moved): re-cited where it now lies."""
    old_of = {r["new_number"]: r["old_number"] for r in rows}
    after, own = section_spans(), own_spans()
    cores = rewrite_cores()
    for path, ci, qi, style in quote_tables():
        full = os.path.join(ROOT, path)
        lines = open(full, encoding="utf-8").read().split("\n")
        changed = False
        for k, l in enumerate(lines):
            if not l or l.startswith("#"):
                continue
            c = l.split("\t")
            if len(c) <= max(ci, qi) or not c[qi]:
                continue
            refs = refs_of(c[ci], style)
            if not refs or any(c[qi] in after.get(n, "") for n in refs):
                continue
            olds = [old_of.get(n, n) for n in refs]
            # each reviewed rewrite on its own (one core text can have several targets): the first that lands it
            followed = next((q for q in (c[qi].replace(o, n, 1) for o, n in cores if o in c[qi])
                             if any(q in after.get(x, "") for x in refs)), c[qi])
            if followed != c[qi]:
                report.append((path, k + 1, ",".join(refs), ",".join(refs), "quote follows a reviewed rewrite"))
                c[qi] = followed
                lines[k] = "\t".join(c)
                changed = True
                continue
            cut = re.sub(r"\d+(?:\.\d+)+$", "", c[qi])
            if cut != c[qi] and len(cut) >= 20 and any(cut in after.get(n, "") for n in refs):
                report.append((path, k + 1, c[qi][len(cut):], "(dropped)", "quote cut inside a section number"))
                c[qi] = cut
                lines[k] = "\t".join(c)
                changed = True
                continue
            if style != "cc" or not any(spans_before.get(o, "") for o in olds):
                report.append((path, k + 1, ",".join(refs), None, "quote outside its cited span, left"))
                continue
            homes = [n for n, txt in own.items() if c[qi] in txt and any(old_of.get(n, n).startswith(o + ".") for o in olds)]
            if len(homes) == 1:
                n = next(n for n, o in zip(refs, olds) if old_of.get(homes[0], homes[0]).startswith(o + "."))
                c[ci] = c[ci].replace("CC " + n, "CC " + homes[0], 1)
                report.append((path, k + 1, n, homes[0], "quote re-cited"))
                lines[k] = "\t".join(c)
                changed = True
            else:
                report.append((path, k + 1, ",".join(refs), None, "quote outside its cited span, left"))
        if changed and write:
            open(full, "w", encoding="utf-8").write("\n".join(lines))


# ---------------------------------------------------------------- inventory

def inventory(out_path):
    secs = parse_parts()
    nums = {s["num"] for s in secs}
    counts = {}

    def add(path, kind, n=1):
        counts[(path, kind)] = counts.get((path, kind), 0) + n
    files = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).split("\n")
    for path in files:
        if not path.endswith(TEXT_EXT) or path in ("tools/recut_sections.py", "formal/derivation/section_map.tsv"):
            continue
        try:
            text = open(os.path.join(ROOT, path), encoding="utf-8").read()
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        area = ("vendor (read-only) " if path.startswith("constitution/vendor/") else
                "handoff (deleted before the cut) " if path.startswith("handoff/") else
                "history (not rewritten) " if path in ("CHANGELOG.md", "REFACTOR_NOTES.md") else
                "generated " if any(path == g or (g.endswith("/") and path.startswith(g)) for g in GENERATED) else "")
        lines = text.split("\n")
        skip = generated_lines(path, lines)
        for i, line in enumerate(lines):
            if path.startswith("constitution/part_") and HEAD.match(line):
                add(path, area + "heading")
                continue
            for m in TOKEN.finditer(line):
                tok = m.group(1)
                if tok not in nums:
                    continue
                cls = classify(line, m.start(1), m.end(1))
                if cls == "bare" and tok.count(".") < 2 and not is_data(path):
                    continue
                k = kind_of(path, cls)
                if cls == "bare" and tok.count(".") < 2:
                    k += " (two-level: may be another number)"
                add(path, area + ("generated block: " if i in skip else "") + k)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("file\tkind\tcount\n")
        for (p, k), n in sorted(counts.items()):
            fh.write(f"{p}\t{k}\t{n}\n")
    tot = {}
    for (p, k), n in counts.items():
        tot[k] = tot.get(k, 0) + n
    for k, n in sorted(tot.items(), key=lambda x: -x[1]):
        print(f"{n:7d}  {k}")


# ---------------------------------------------------------------- verify

LINK_ANCHOR = re.compile(r"\]\(([^)\s#]*)#(\d+(?:\.\d+)*)\)")


def anchor_errors(path, text, nums_by_file):
    """(count, errors): every link anchor into a Part names a section of that Part."""
    n, errs = 0, []
    base = os.path.dirname(path)
    for i, line in enumerate(text.split("\n"), 1):
        for m in LINK_ANCHOR.finditer(line):
            tgt = os.path.normpath(os.path.join(base, m.group(1))) if m.group(1) else path
            if tgt in nums_by_file:
                n += 1
                if m.group(2) not in nums_by_file[tgt]:
                    errs.append(f"{path}:{i}: anchor #{m.group(2)} is not a section of {tgt}")
    return n, errs


def drift(before, after, change):
    """Old numbers that appear in `after` more often than `before`, mapped, gives: left on the old side."""
    want, have = {}, {}
    for m in TOKEN.finditer(before):
        k = change.get(m.group(1), m.group(1))
        want[k] = want.get(k, 0) + 1
    for m in TOKEN.finditer(after):
        have[m.group(1)] = have.get(m.group(1), 0) + 1
    return {o: have[o] - want.get(o, 0) for o in change if have.get(o, 0) > want.get(o, 0)}


def quote_found(quote, refs, spans):
    return any(quote in spans.get(n, "") for n in refs)


def head_text(path):
    r = subprocess.run(["git", "show", "HEAD:" + path], cwd=ROOT, capture_output=True)
    if r.returncode:
        return None
    try:
        return r.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None


def head_is_before(rows):
    """True when git HEAD's Parts carry the old numbers (the re-cut is applied but not committed)."""
    moving = {r["old_slug"]: r["old_number"] for r in rows if r["old_number"] != r["new_number"]}
    for f in part_files():
        t = head_text(rel(f)) or ""
        for line in t.split("\n"):
            m = HEAD.match(line)
            if m and m.group(3) in moving:
                return m.group(2) == moving[m.group(3)]
    return False


def selftest():
    """Plants a break for each check and fails unless every one is caught (run on every --verify)."""
    miss = []
    change = {"4.4.3.2.4.1": "4.4.3.8", "4.4.3.8": "4.4.3.34", "8.8.10": "8.8.8", "2.6.1.7": "2.6.1.8"}
    rep = []
    got = rewrite_line("x.md", "CC 4.4.3.8 and 4.4.3.2.4.1, [CC 4.4.3.8](part_4_x.md#4.4.3.8) v4.4.3.8 0.5.246 4.4.3.8.x",
                       change, rep, 1)
    if got != "CC 4.4.3.34 and 4.4.3.8, [CC 4.4.3.34](part_4_x.md#4.4.3.34) v4.4.3.8 0.5.246 4.4.3.8.x":
        miss.append("rewrite: " + got)
    if not any("wildcard" in r[4] for r in rep):
        miss.append("a subtree wildcard went unreported")
    if rewrite_line("x.py", 'r"8\\.8\\.10|HE"', change, [], 1) != 'r"8\\.8\\.8|HE"':
        miss.append("a regex-escaped number was not rewritten")
    if drift("CC 2.6.1.7", "CC 2.6.1.7", change) != {"2.6.1.7": 1}:
        miss.append("a number left on the old side was not seen")
    if drift("CC 2.6.1.7", "CC 2.6.1.8", change):
        miss.append("a clean rewrite was reported as drift")
    if not anchor_errors("constitution/part_4_x.md", "[a](#9.9.9)", {"constitution/part_4_x.md": {"4.1"}})[1]:
        miss.append("a dangling anchor was not caught")
    if quote_found("abc", ["4.1"], {"4.1": "xyz", "4.2": "abc"}):
        miss.append("a quote outside its span was found")
    for m in miss:
        print("  self-test missed: " + m)
    print(f"recut verify: self-test {6 - len(miss) if len(miss) <= 6 else 0} of 6 planted breaks caught")
    return miss


def verify(rows):
    errs = ["self-test: " + m for m in selftest()]
    secs = parse_parts()
    if len(secs) != len(rows):
        errs.append(f"section count {len(secs)} differs from the map's {len(rows)}")
    want = {r["new_slug"]: r["new_number"] for r in rows}
    for s in secs:
        if want.get(s["slug"]) != s["num"]:
            errs.append(f"`{s['slug']}` is {s['num']}, the map says {want.get(s['slug'])}")
        if s["level"] != s["num"].count(".") + 1:
            errs.append(f"{s['num']} sits at heading level {s['level']}")
    depth = max(s["num"].count(".") + 1 for s in secs)
    print(f"recut verify: {len(secs)} sections, deepest {depth} levels")
    # every link anchor in scope resolves to a heading of the Part it names
    nums_by_file = {}
    for s in secs:
        nums_by_file.setdefault(s["file"], set()).add(s["num"])
    n_links = 0
    for path in in_scope():
        if path.endswith(".md"):
            n, e = anchor_errors(path, open(os.path.join(ROOT, path), encoding="utf-8").read(), nums_by_file)
            n_links += n
            errs += e
    print(f"recut verify: {n_links} section anchors checked")
    # numbers that exist only on the old side: any appearance is stale
    gone = {r["old_number"] for r in rows} - {r["new_number"] for r in rows}
    stale = {}
    files = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).split("\n")
    for path in files:
        if not path.endswith(TEXT_EXT) or path in ("formal/derivation/section_map.tsv", "tools/recut_sections.py",
                                                    "formal/derivation/section_map_rewrites.tsv"):
            continue
        try:
            text = open(os.path.join(ROOT, path), encoding="utf-8").read()
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        for m in TOKEN.finditer(text):
            if m.group(1) in gone:
                area = ("vendor" if path.startswith("constitution/vendor/") else "handoff" if path.startswith("handoff/")
                        else "history" if path in ("CHANGELOG.md", "REFACTOR_NOTES.md") else "in scope")
                stale.setdefault(area, {}).setdefault(path, 0)
                stale[area][path] += 1
    for area, fs in sorted(stale.items()):
        print(f"recut verify: old-only numbers still in {area}: {sum(fs.values())} in {len(fs)} file(s)")
        if area == "in scope":
            for p, n in sorted(fs.items()):
                errs.append(f"{p}: {n} old-only section number(s) left")
    # quoted-text tables still find their quotes in the section they cite
    after = section_spans()
    nq = 0
    for path, ci, qi, style in quote_tables():
        for k, l in enumerate(open(os.path.join(ROOT, path), encoding="utf-8").read().split("\n"), 1):
            c = l.split("\t")
            if l.startswith("#") or len(c) <= max(ci, qi) or not c[qi] or c[ci] in ("cc_ref", "home"):
                continue
            refs = refs_of(c[ci], style)
            if not refs:
                continue
            nq += 1
            if not quote_found(c[qi], refs, after):
                errs.append(f"{path}:{k}: quote not found in {c[ci]}")
    print(f"recut verify: {nq} quotes checked")
    # against git HEAD taken before --apply: every renumbered number in a file, generated or not, moved
    if head_is_before(rows):
        change = {r["old_number"]: r["new_number"] for r in rows if r["old_number"] != r["new_number"]}
        tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).split("\n")
        gen = [f for f in tracked if any(f == g or (g.endswith("/") and f.startswith(g)) for g in GENERATED)]
        nd = ng = nf = 0
        # what the reviewed rewrites add, exactly, per file; and the numbers they point at, which the quoted-text
        # tables and the inventory follow (counted, not exact: the follow-ups are found at --apply)
        exact, targets = {}, set()
        for r in read_rewrites():
            if r["kind"] == "keep":
                continue
            o = [m.group(1) for m in TOKEN.finditer(r["old_text"])]
            for m in TOKEN.finditer(r["new_text"]):
                t = m.group(1)
                if t in o:
                    o.remove(t)
                    continue
                targets.add(t)
                exact.setdefault(r["file"], {}).setdefault(t, 0)
                exact[r["file"]][t] += int(r["count"])
        for path in sorted(set(in_scope()) | set(gen)):
            before = head_text(path)
            if before is None:
                continue
            d = drift(before, open(os.path.join(ROOT, path), encoding="utf-8").read(), change)
            for o, n in sorted(d.items()):
                n -= exact.get(path, {}).get(o, 0)
                if n <= 0:
                    continue
                if path not in gen and o in targets and not path.startswith("constitution/part_"):
                    nf += n
                    print(f"  {path}: {o} +{n}, a number a reviewed rewrite points at (followed by a quote or the inventory)")
                    continue
                if path in gen:
                    # a generator may index by section (refusal tokens by the section that names them): a
                    # promoted subsection is now its own index entry. Listed for a reader, not an error.
                    ng += n
                    print(f"  generated {path}: {o} +{n} against the re-cut of HEAD (read it)")
                else:
                    nd += n
                    errs.append(f"{path}: {o} appears {n} more time(s) than the re-cut of HEAD gives (left on the old side)")
        print(f"recut verify: {nd} reference(s) left on the old side against HEAD; {ng} moved by generators; "
              f"{nf} follow a reviewed rewrite")
    else:
        print("recut verify: HEAD is not the tree before the re-cut; the comparison against it is skipped")
    for e in errs:
        print("  " + e)
    return errs


def run(cmds):
    codes = []
    for c in cmds:
        p = subprocess.run(c, shell=True, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        codes.append((c, p.returncode))
        tail = p.stdout.strip().split("\n")[-1:] if p.stdout.strip() else [""]
        print(f"  exit {p.returncode}  {c}  | {tail[0][:140]}")
    return codes


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--make-map", action="store_true")
    ap.add_argument("--part1", action="store_true", help="with --make-map: re-cut Part 1 too (the owner's)")
    ap.add_argument("--inventory", metavar="OUT")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--regen", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--checks", action="store_true", help="with --verify: also run the repository's checks")
    ap.add_argument("--list", action="store_true", help="with --check: print every rewrite, not a summary")
    a = ap.parse_args()
    if a.make_map:
        old = read_map() if os.path.exists(MAP) else []
        rows = make_map(parse_parts(), set() if a.part1 else {"1"}, old)
        write_map(rows)
        moving = [r for r in rows if r["old_number"] != r["new_number"]]
        print(f"recut map: {len(rows)} sections, {len(moving)} renumbered, "
              f"{sum(r['moved'] == 'yes' for r in rows)} promoted, "
              f"{sum('renamed' in r['note'] for r in rows)} retitled; deepest "
              f"{max(r['old_number'].count('.') for r in rows) + 1} -> {max(r['new_number'].count('.') for r in rows) + 1}")
    if a.inventory:
        inventory(a.inventory)
    if a.check or a.apply:
        rows = read_map()
        state, report, edits, nfiles = apply_all(rows, write=a.apply)
        if state == "applied":
            print("recut: the tree is already on the new side of the map; nothing to do")
        else:
            by = {}
            for p, ln, old, new, kind in report:
                by[kind] = by.get(kind, 0) + 1
                if a.list or new is None:
                    print(f"  {p}:{ln}: {old} -> {new if new else '(left)'}  [{kind}]")
            for k, n in sorted(by.items(), key=lambda x: -x[1]):
                print(f"{n:7d}  {k}")
            print(f"recut: {len(report)} rewrite(s) in {nfiles} file(s)" + (" applied" if a.apply else " would be made"))
            if a.check and report:
                sys.exit(1)
    if a.regen:
        codes = run(GENERATORS)
        if any(c for _, c in codes):
            sys.exit(1)
    if a.verify:
        rows = read_map()
        errs = verify(rows)
        if a.checks:
            run(CHECKS)
        sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
