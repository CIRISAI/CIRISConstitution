#!/usr/bin/env python3
"""
clean_history(text) — strip version-history, RC/version annotations, issue refs, and
provenance from CEG/Accord prose so the CIRIS Constitution reads as clean, positive,
present-tense 1.0 statements. Removes ONLY editorial/historical scaffolding — never
normative content (rules, schemas, tables, numbers, field names untouched).

Robust strategy: drop a WHOLE parenthetical when (and only when) it contains a version
tag / issue ref / provenance link — never partial token-surgery (which mangles prose).
"""
import re

_PAREN = re.compile(r"\((?:[^()]|\([^()]*\))*\)")        # one level of nesting (markdown links)
_CRUFT = re.compile(r"CEG\s+\d+\.\d+|\d\.\d+-RC\d+|1\.0-RC\d+|CIRIS[A-Za-z]+#\d+|\bper\s+\[|\bresolves?\s+\[")

def clean_history(t: str) -> str:
    # 1. drop whole parentheticals that carry version/issue/provenance cruft (leave clean ones)
    def _p(m):
        return "" if _CRUFT.search(m.group(0)) else m.group(0)
    t = _PAREN.sub(_p, t)
    t = _PAREN.sub(_p, t)                                # 2nd pass: nested notes revealed after 1st
    # 2. RESOLVED-at blockquote notes (whole line)
    t = re.sub(r"^>\s*\*\*RESOLVED[^\n]*\n", "", t, flags=re.M)
    # 3. safe bold version labels/lead-ins: **CEG 0.6**: / **CEG 0.6 addition.** / **... 1.0-RC25 ...**
    t = re.sub(r"\*\*CEG\s+\d+\.\d+(?:\s+(?:addition|retcon|change))?\.?\*\*\s*[:—-]?\s*", "", t)
    t = re.sub(r"\*\*[^*\n]*\b1\.0-RC\d+\b[^*\n]*\*\*\s*[:—-]?\s*", "", t)
    # bare inline version stamps in non-structural positions: "CEG 0.6 addition" / ", 1.0-RC1," etc.
    t = re.sub(r"\b(?:CEG\s+)?\d+\.\d+\s+(?:addition|retcon)\b\.?", "", t)
    t = re.sub(r"[(,;]?\s*\b(?:CEG\s+)?1\.0-RC\d+\b", "", t)
    # 4. standalone issue refs left outside parens
    t = re.sub(r"\s*CIRIS[A-Za-z]+#\d+(?:\s*\+\s*#\d+)*", "", t)
    # 5. leftover empty markdown links []()
    t = re.sub(r"\[\]\([^)]*\)", "", t)
    # 6. tidy whitespace + orphaned punctuation
    t = re.sub(r"\s+([,.;:)])", r"\1", t)
    t = re.sub(r"\(\s*\)", "", t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    t = re.sub(r" +\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t

if __name__ == "__main__":
    import sys
    sys.stdout.write(clean_history(sys.stdin.read()))
