#!/usr/bin/env python3
"""
lean_statement_hash.py — pin each Lean theorem this repository cites by its STATEMENT, not its proof.

The statement of `theorem n ...` is its source text from the `theorem`/`lemma` keyword to the `:=`
that starts the proof (or the `where`, or the first `|` of an equation-style proof), taken at
bracket depth zero. Comments are removed and every run of whitespace becomes one space before the
SHA-256 is taken, so re-proving a theorem, re-wrapping it or re-commenting it leaves the hash alone;
weakening or strengthening a hypothesis or the conclusion, or renaming the theorem, changes it.

What counts as cited (in-repo Lean only; the coherence-ratchet and RATCHET manifests cite Lean
that is not in this tree and are pinned by their own repositories):
  constitution/claims.tsv  every `lean:@path#a,b,c` pointer
  formal/INVARIANTS.tsv    every row whose source is a .lean file (its symbol column)
  formal/KERNEL.md         every backticked name that is a theorem declared in a Lean file under formal/

The table formal/derivation/lean_statements.tsv (theorem, file, statement_sha256) records the hash
of each. The check exits 1 when a cited theorem is missing from the table, cannot be found, is
declared more than once in its file, or has a statement whose hash differs from the table's. After
re-reading the claim a changed statement backs, record it with --update in the same commit.

  python3 tools/lean_statement_hash.py                      # check (runs the self-test first)
  python3 tools/lean_statement_hash.py --update             # rewrite the table
  python3 tools/lean_statement_hash.py --self-test          # the self-test alone
  python3 tools/lean_statement_hash.py FILE.lean NAME       # print one statement and its hash
"""
import csv, hashlib, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE = os.path.join(ROOT, "formal", "derivation", "lean_statements.tsv")
KERNEL = os.path.join(ROOT, "formal", "KERNEL.md")
HEADER = ["theorem", "file", "statement_sha256"]

_DECL = re.compile(r"\b(theorem|lemma)\s+([^\s(\[{:]+)")
_OPEN = "([{⟨⦃"
_CLOSE = ")]}⟩⦄"


def strip_comments(text):
    """Remove `--` line comments and nested `/- -/` block comments (doc comments included); keep strings."""
    text = text.replace("\r\n", "\n")
    out, i, n = [], 0, len(text)
    while i < n:
        if text.startswith("--", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
        elif text.startswith("/-", i):
            depth, j = 1, i + 2
            while j < n and depth:
                if text.startswith("/-", j):
                    depth, j = depth + 1, j + 2
                elif text.startswith("-/", j):
                    depth, j = depth - 1, j + 2
                else:
                    j += 1
            out.append(" ")
            i = j
        elif text[i] == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1])
            i = j + 1
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def _namespaces(text):
    """[(offset, dotted namespace in force from that offset)] from `namespace X` / `end X` lines."""
    marks, stack = [(0, "")], []
    for m in re.finditer(r"(?m)^\s*(namespace|section|end)\b[ \t]*([^\s]*)", text):
        kw, name = m.group(1), m.group(2)
        if kw == "namespace":
            stack.append(("ns", name))
        elif kw == "section":
            stack.append(("sec", name))
        elif stack:
            stack.pop()
        marks.append((m.start(), ".".join(n for k, n in stack if k == "ns")))
    return marks


def _ns_at(marks, pos):
    cur = ""
    for off, ns in marks:
        if off > pos:
            break
        cur = ns
    return cur


def _statement_end(text, start):
    depth, j, n = 0, start, len(text)
    while j < n:
        c = text[j]
        if c in _OPEN:
            depth += 1
        elif c in _CLOSE:
            depth -= 1
        elif depth == 0:
            if text.startswith(":=", j):
                return j
            if re.match(r"\swhere\b", text[j - 1:j + 6]) and text.startswith("where", j):
                return j
            if c == "|" and text[j - 1] in " \n" and text[j + 1:j + 2] in (" ", "\n"):
                return j
        j += 1
    raise ValueError("statement never reaches := , where or |")


def statement_of(text, name):
    """The normalised statement of theorem `name` (bare or namespace-qualified). ValueError unless exactly one."""
    clean = strip_comments(text)
    marks = _namespaces(clean)
    hits = []
    for m in _DECL.finditer(clean):
        decl = m.group(2)
        full = ".".join(x for x in (_ns_at(marks, m.start()), decl) if x)
        if name in (decl, full) or full.endswith("." + name):
            hits.append(m.start())
    if len(hits) != 1:
        raise ValueError(f"{len(hits)} declarations of theorem {name}")
    start = hits[0]
    return " ".join(clean[start:_statement_end(clean, start)].split())


def statement_sha256(text, name):
    return hashlib.sha256(statement_of(text, name).encode("utf-8")).hexdigest()


# --- what this repository cites ----------------------------------------------

def _kernel_theorems():
    """bare theorem name -> [file] over every Lean file under formal/ (build trees excluded)."""
    out = {}
    for dirpath, dirs, files in os.walk(os.path.join(ROOT, "formal")):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for fn in sorted(f for f in files if f.endswith(".lean")):
            rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
            txt = strip_comments(open(os.path.join(ROOT, rel), encoding="utf-8").read())
            for m in _DECL.finditer(txt):
                out.setdefault(m.group(2).split(".")[-1], []).append(rel)
    return out


def cited():
    """{(theorem, file)} for every in-repo Lean theorem the sources name, and a list of problems."""
    got, problems = set(), []
    claims = os.path.join(ROOT, "constitution", "claims.tsv")
    for row in csv.DictReader(open(claims, encoding="utf-8"), delimiter="\t"):
        for tok in re.findall(r"lean:@([^\s;]+\.lean)#([^\s;]+)", row.get("evidence") or ""):
            for name in tok[1].split(","):
                if name.strip():
                    got.add((name.strip(), tok[0]))
    inv = os.path.join(ROOT, "formal", "INVARIANTS.tsv")
    for row in csv.DictReader(open(inv, encoding="utf-8"), delimiter="\t"):
        if row["source"].endswith(".lean"):
            got.add((row["symbol"], row["source"]))
    thms = _kernel_theorems()
    kernel = open(KERNEL, encoding="utf-8").read()
    # A paragraph names its file as (`File.lean`); an ambiguous bare name is resolved by that file.
    for para in re.split(r"\n\s*\n", kernel):
        files = re.findall(r"`(?:[\w/]+/)?(\w+\.lean)`", para)
        for name in re.findall(r"`([A-Za-z_][A-Za-z0-9_']*)`", para):
            where = thms.get(name)
            if not where:
                continue
            if len(set(where)) == 1:
                got.add((name, where[0]))
                continue
            named = [w for w in where if os.path.basename(w) in files]
            if len(set(named)) == 1:
                got.add((name, named[0]))
            else:
                problems.append(f"KERNEL.md cites `{name}`, declared in {', '.join(sorted(set(where)))}, "
                                f"and its paragraph names no single one of those files")
    return got, problems


def load_table():
    if not os.path.exists(TABLE):
        return {}
    lines = [l for l in open(TABLE, encoding="utf-8") if not l.startswith("#")]
    return {(r["theorem"], r["file"]): r["statement_sha256"] for r in csv.DictReader(lines, delimiter="\t")}


def compute(pairs):
    hashes, problems, cache = {}, [], {}
    for name, rel in sorted(pairs):
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            problems.append(f"{rel}: file not found (cited theorem {name})")
            continue
        txt = cache.setdefault(p, open(p, encoding="utf-8").read())
        try:
            hashes[(name, rel)] = statement_sha256(txt, name)
        except ValueError as e:
            problems.append(f"{rel}#{name}: {e}")
    return hashes, problems


# --- self-test (runs before every check) -------------------------------------

_SRC = """namespace T
/-- doc -/
@[simp] theorem keep (a b : Nat) (h : a ≤ b) : a ≤ b + 1 := by
  omega
-- a comment
theorem other {x : Nat} : x = x := rfl
theorem eqn : Nat → Nat → Prop
  | _, _ => True
end T
theorem keep (n : Nat) : n = n := rfl
"""


def self_test():
    bad = 0
    def case(label, ok):
        nonlocal bad
        bad += not ok
        print(f"  {'ok ' if ok else 'BAD'} self-test: {label}")
    base = statement_sha256(_SRC, "T.keep")
    reproved = _SRC.replace(":= by\n  omega", ":= by\n  -- re-proved\n  exact Nat.le_succ_of_le h")
    case("re-proof leaves the hash unchanged", statement_sha256(reproved, "T.keep") == base)
    rewrapped = _SRC.replace("(h : a ≤ b) : a ≤ b + 1", "(h : a ≤ b)\n    /- note -/ :  a ≤ b + 1")
    case("re-wrapping and a comment leave the hash unchanged", statement_sha256(rewrapped, "T.keep") == base)
    weakened = _SRC.replace("(h : a ≤ b) : a ≤ b + 1", "(h : a < b) : a ≤ b + 1")
    case("a changed hypothesis is caught", statement_sha256(weakened, "T.keep") != base)
    concl = _SRC.replace("a ≤ b + 1 := by", "a ≤ b + 2 := by")
    case("a changed conclusion is caught", statement_sha256(concl, "T.keep") != base)
    renamed = _SRC.replace("theorem keep (a b", "theorem keep' (a b")
    try:
        statement_of(renamed, "T.keep")
        case("a renamed theorem is caught", False)
    except ValueError:
        case("a renamed theorem is caught", True)
    try:
        statement_of(_SRC, "keep")
        case("a bare name declared twice is refused", False)
    except ValueError:
        case("a bare name declared twice is refused", True)
    case("equation-style statement ends at |", statement_of(_SRC, "eqn") == "theorem eqn : Nat → Nat → Prop")
    case("statement ends at := with binders braced", statement_of(_SRC, "other") == "theorem other {x : Nat} : x = x")
    return bad


def main(argv):
    if len(argv) == 3 and argv[1].endswith(".lean"):
        txt = open(argv[1], encoding="utf-8").read()
        print(statement_of(txt, argv[2]))
        print(statement_sha256(txt, argv[2]))
        return 0
    if argv[1:] == ["--self-test"]:
        return 1 if self_test() else 0
    bad = self_test()
    pairs, problems = cited()
    hashes, p2 = compute(pairs)
    problems += p2
    if "--update" in argv:
        if problems:
            for p in problems:
                print("  ERR " + p)
            return 1
        with open(TABLE, "w", encoding="utf-8") as f:
            f.write("# The statement hash of every in-repo Lean theorem the constitution cites "
                    "(tools/lean_statement_hash.py --update writes it).\n")
            f.write("\t".join(HEADER) + "\n")
            for (name, rel), h in sorted(hashes.items(), key=lambda x: (x[0][1], x[0][0])):
                f.write(f"{name}\t{rel}\t{h}\n")
        print(f"lean statements: {len(hashes)} recorded")
        return 1 if bad else 0
    table = load_table()
    # The deliberate break, on real data: alter the first cited statement's hypothesis in memory.
    if hashes:
        name, rel = sorted(hashes)[0]
        st = statement_of(open(os.path.join(ROOT, rel), encoding="utf-8").read(), name)
        mutated = st.replace(name, name + " (hx : False)", 1)
        caught = hashlib.sha256(mutated.encode("utf-8")).hexdigest() != hashes[(name, rel)]
        print(f"  {'ok ' if caught else 'BAD'} deliberate break: an added hypothesis on {name} changes its hash")
        bad += not caught
    for key, h in sorted(hashes.items()):
        if key not in table:
            problems.append(f"{key[1]}#{key[0]}: cited but not in lean_statements.tsv — run --update")
        elif table[key] != h:
            problems.append(f"{key[1]}#{key[0]}: the statement changed under its name — re-read the claim it "
                            f"backs; if it still holds, record it with --update")
    stale = sorted(set(table) - set(hashes))
    print(f"lean statements: {len(hashes)} cited theorems pinned, {len(problems)} problem(s), "
          f"{len(stale)} table row(s) no longer cited")
    for k in stale:
        print(f"  NOTE no longer cited: {k[1]}#{k[0]}")
    for p in problems:
        print("  ERR " + p)
    return 1 if (bad or problems) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
