#!/usr/bin/env python3
"""
span_of.py — the reference extractor for the `span_sha256` column of an implementer's evidence manifest.

Copied verbatim from CIRISVerify tools/check_evidence.py at commit 588c4ad (release/23.0.0): the
constants ITEM_KINDS and BRACE_BODIED and the functions _code_mask, _item_end, _decls, span_of and
span_sha256, below the marker line. That file carries no licence header of its own; CIRISVerify is
distributed under the GNU Affero General Public License v3, as is this repository. Another repository
copies this file whole and keeps the copied block unchanged, so that every manifest's span_sha256
means the same bytes.

The column's definition (CIRISVerify, as copied): the SHA-256 of each cited item's own source text,
from its declaration keyword to its closing `}` or `;`. Docs and attributes above it are excluded,
and CRLF is read as LF. A qualified `Owner::member` resolves inside the owner's impl/trait block; a
name declared more than once is refused.

  python3 tools/span_of.py --self-test        # the shapes it must get right
  python3 tools/span_of.py FILE.rs SYMBOL     # print the span and its hash
"""
from __future__ import annotations

import hashlib
import re
import sys

# ---- copied from CIRISVerify tools/check_evidence.py @ 588c4ad (unchanged below this line) ----
ITEM_KINDS = "fn|struct|enum|const|static|trait|type|mod|union|macro_rules!"


#: Kinds whose item ends at the closing brace of their body; the rest end at a
#: top-level `;` (a `const`'s block initializer is not its end).
BRACE_BODIED = {"fn", "struct", "enum", "trait", "mod", "union", "impl", "macro_rules!"}


def _code_mask(text: str) -> list[bool]:
    """True where `text[i]` is code: not in a comment, string or char literal."""
    n = len(text)
    code = [True] * n
    i = 0
    while i < n:
        c = text[i]
        if text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            for k in range(i, j):
                code[k] = False
            i = j
        elif text.startswith("/*", i):
            depth, j = 1, i + 2
            while j < n and depth:
                if text.startswith("/*", j):
                    depth, j = depth + 1, j + 2
                elif text.startswith("*/", j):
                    depth, j = depth - 1, j + 2
                else:
                    j += 1
            for k in range(i, j):
                code[k] = False
            i = j
        elif re.match(r'b?r#*"', text[i : i + 64]) and (i == 0 or not (text[i - 1].isalnum() or text[i - 1] == "_")):
            m = re.match(r'b?r(#*)"', text[i:])
            close = '"' + m.group(1)
            j = text.find(close, i + m.end())
            j = n if j < 0 else j + len(close)
            for k in range(i, j):
                code[k] = False
            i = j
        elif c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            j = min(j + 1, n)
            for k in range(i, j):
                code[k] = False
            i = j
        elif c == "'":
            # A char literal ('x', '\n', '\u{..}') rather than a lifetime ('a).
            m = re.match(r"'(\\(u\{[0-9a-fA-F]+\}|x[0-9a-fA-F]{2}|.)|[^\\'])'", text[i : i + 16])
            if m:
                for k in range(i, i + m.end()):
                    code[k] = False
                i += m.end()
            else:
                i += 1
        else:
            i += 1
    return code


def _item_end(text: str, code: list[bool], start: int, kind: str) -> int:
    """Index one past the end of the item whose declaration starts at `start`."""
    depth = 0
    for j in range(start, len(text)):
        if not code[j]:
            continue
        ch = text[j]
        if ch in "({[":
            depth += 1
        elif ch in ")}]":
            depth -= 1
            if depth == 0 and ch == "}" and kind in BRACE_BODIED:
                return j + 1
        elif ch == ";" and depth == 0:
            return j + 1
    raise ValueError("item never closes")


def _decls(text: str, code: list[bool], kind_re: str, name: str, lo: int = 0, hi: int | None = None):
    hi = len(text) if hi is None else hi
    pat = re.compile(rf"\b({kind_re})\s+{re.escape(name)}\b")
    for m in pat.finditer(text, lo, hi):
        # `'static T` is a lifetime, not a `static` item.
        if code[m.start()] and (m.start() == 0 or text[m.start() - 1] != "'"):
            yield m.start(), m.group(1)


def span_of(text: str, symbol: str) -> str:
    """The cited item's source text. Raises ValueError if not exactly one."""
    text = text.replace("\r\n", "\n")
    code = _code_mask(text)
    if "::" in symbol:
        owner, _, member = symbol.rpartition("::")
        owner = owner.split("::")[-1]
        hits = []
        blocks = re.compile(rf"\b(impl\b[^;{{]*?\b{re.escape(owner)}\b[^;{{]*|trait\s+{re.escape(owner)}\b[^;{{]*)\{{")
        for b in blocks.finditer(text):
            if not code[b.start()]:
                continue
            kind = "trait" if b.group(0).lstrip().startswith("trait") else "impl"
            end = _item_end(text, code, b.start(), kind)
            hits += [(s, k) for s, k in _decls(text, code, ITEM_KINDS, member, b.start() + 1, end)]
        if not hits:
            # A type-level constant or alias: fall back to the bare member.
            hits = list(_decls(text, code, ITEM_KINDS, member))
    else:
        hits = list(_decls(text, code, ITEM_KINDS, symbol))
    if len(hits) != 1:
        raise ValueError(f"{len(hits)} declarations of {symbol}; cite it unambiguously (Owner::member)")
    start, kind = hits[0]
    return text[start : _item_end(text, code, start, kind)]


def span_sha256(text: str, symbol: str) -> str:
    return hashlib.sha256(span_of(text, symbol).encode("utf-8")).hexdigest()


# ---- end of the copied block ----


def self_test() -> int:
    """CRLF, attributes and docs, nested braces, Owner::member, a duplicate name."""
    src = (
        "/// doc { not code\r\n"
        "#[inline]\r\n"
        "#[cfg(feature = \"x\")]\r\n"
        "pub fn outer(x: u8) -> u8 {\r\n"
        "    if x > 0 { match x { 1 => { 1 } _ => { let s = \"}\"; 2 } } } else { 0 }\r\n"
        "}\r\n"
        "pub struct Head { n: u8 }\r\n"
        "impl Head {\r\n"
        "    /// cosign doc\r\n"
        "    #[must_use]\r\n"
        "    pub fn cosign(&self) -> u8 { { self.n } }\r\n"
        "}\r\n"
        "pub fn cosign() -> u8 { 9 }\r\n"
        "pub const LIMIT: usize = { 4 };\r\n"
    )
    want = {
        "outer": "fn outer(x: u8) -> u8 {\n    if x > 0 { match x { 1 => { 1 } _ => { let s = \"}\"; 2 } } } else { 0 }\n}",
        "Head": "struct Head { n: u8 }",
        "Head::cosign": "fn cosign(&self) -> u8 { { self.n } }",
        "LIMIT": "const LIMIT: usize = { 4 };",
    }
    bad = 0
    for sym, exp in want.items():
        got = span_of(src, sym)
        ok = got == exp
        bad += not ok
        print(f"  {'ok ' if ok else 'BAD'} span {sym}: {got!r}")
    lf = span_sha256(src.replace("\r\n", "\n"), "outer") == span_sha256(src, "outer")
    print(f"  {'ok ' if lf else 'BAD'} CRLF and LF give the same hash")
    bad += not lf
    doc = span_sha256(src.replace("/// doc { not code", "/// a new doc"), "outer") == span_sha256(src, "outer")
    print(f"  {'ok ' if doc else 'BAD'} a doc-only edit leaves the hash unchanged")
    bad += not doc
    body = span_sha256(src.replace("else { 0 }", "else { 3 }"), "outer") != span_sha256(src, "outer")
    print(f"  {'ok ' if body else 'BAD'} a body edit under the same name changes the hash")
    bad += not body
    try:
        span_of(src, "cosign")
        print("  BAD span cosign: a name declared twice was not refused")
        bad += 1
    except ValueError:
        print("  ok  span cosign: a name declared twice is refused")
    print(f"span_of self-test: {'all passed' if not bad else f'{bad} did not pass'}")
    return 1 if bad else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(self_test())
    if len(sys.argv) == 3:
        _t = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
        print(span_of(_t, sys.argv[2]))
        print(span_sha256(_t, sys.argv[2]))
        sys.exit(0)
    print(__doc__)
    sys.exit(2)
