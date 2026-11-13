#!/usr/bin/env python3
"""Every sentence that says a landed rule again cites the rule's home.

A rule's home is the section whose entry states it (formal/derivation/rule_entries.tsv, rows of role
`states`). A sentence elsewhere in the Parts that says the rule again is a restatement. It passes when
the sentence or its paragraph cites the home ("CC 4.2.6", or a link to #4.2.6, or a section inside the
home); otherwise it is an uncited restatement. A sentence inside the home is the rule, not a
restatement, and is never counted.

The restatements are found two ways:
  1. the inventory (formal/derivation/rule_inventory.tsv): every row of role `restates` or `applies`
     whose rule has a home. The row is re-anchored to a sentence of its section by the entry's verbatim
     phrase where the rulebook carries one, else by the words of its gist; its home is the sections its
     `points_to` names, else every home of its rule;
  2. a sentence matcher: a sentence outside a home that carries most of the distinctive words of one of
     the home's stated phrases (the weights and the floor are set on the inventory's own restatements;
     run --tune to see the measure).

The uncited restatements are written to formal/derivation/restatements_uncited.tsv. Their count is
held at the maximum in tools/restatements_max.tsv, which only falls: the check exits 1 when the count
rises above it (and says to lower the maximum when the count has fallen below it).

Plants, run every time: a sentence that copies a landed rule's phrase into another section with no
citation must be counted; the same sentence citing the home must not be; the same sentence inside the
home must not be.

  python3 tools/check_restatements.py            # count, write the worklist, hold the maximum
  python3 tools/check_restatements.py --tune     # the matcher's measure on the inventory
  python3 tools/check_restatements.py --homeless # the rule keys with no home, by statement count
"""
import csv, math, re, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parts_text as P

ROOT = P.ROOT
DER = ROOT / "formal" / "derivation"
WORKLIST = DER / "restatements_uncited.tsv"
MAXIMA = ROOT / "tools" / "restatements_max.tsv"
STOP = set("""a an and are as at be been but by can for from has have if in into is it its may must
never no nor not of on one or other own row rows same shall should so than that the their them then
there these they this those to two under unless was were what when where whether which while who whom
whose will with within without any each every only also more most such does done more less""".split())
# The matcher's floor: the share of a phrase's distinctive weight a sentence must carry, and the least
# number of distinctive words it must share. Set by --tune on the inventory (see the module text).
FLOOR, MIN_SHARED, MIN_PHRASE_WORDS = 0.6, 5, 6
# The share of a gist's words a sentence of its section must carry to stand for an inventory row.
GIST_FLOOR = 0.5


def read(name):
    return list(csv.DictReader((DER / name).open(encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))


def toks(raw):
    t = P.plain(raw).lower()
    return [w for w in re.findall(r"[a-z0-9_:.\-]+", t) if len(w) > 2 and w.strip(".:-") not in STOP and not w[0].isdigit()]


def homes_of(entries):
    """rule_key -> the sections where its entry states it."""
    h = defaultdict(set)
    for e in entries:
        if e["role"] == "states":
            h[e["rule_key"]].add(e["home"])
    return h


def index(parts):
    """Every prose sentence: (part, line, section, sentence, paragraph, its words, the paragraph's words)."""
    out = []
    for p in P.paragraphs(parts):
        pn = norm(p["text"])
        for s in P.sentences(p["text"]):
            out.append((p["part"], p["line"], p["section"], s, p["text"], norm(s), pn))
    return out


def norm(t):
    return re.sub(r"\s+", " ", P.plain(t)).strip()


def anchor(row, phrase, sents_by_sec, sents_by_part, other_lines):
    """The sentence an inventory row stands for: by the entry's verbatim phrase, else by the gist's words.
    Returns a sentence, TABLE when the phrase sits in a table row or a code line (not asked to cite), or None."""
    pool = sents_by_sec.get((row["file"], row["section"]), [])
    if phrase:
        ph = norm(phrase)
        head = " ".join(ph.split()[:8])
        for group in (pool, sents_by_part.get(row["file"], [])):
            for s in group:
                if ph in s[6] and (head in s[5] or ph in s[5]):   # the phrase is in this paragraph: its sentence
                    return s
            for s in group:
                if ph in s[6]:
                    return s
        if any(ph in l for l in other_lines.get((row["file"], row["section"]), ())):
            return TABLE
    g = set(toks(row["gist"]))
    if not g:
        return None
    best, score = None, 0.0
    for s in pool:
        sc = len(g & set(toks(s[3]))) / len(g)
        if sc > score:
            best, score = s, sc
    if score >= GIST_FLOOR:
        return best
    if any(len(g & set(toks(l))) / len(g) >= GIST_FLOOR for l in other_lines.get((row["file"], row["section"]), ())):
        return TABLE
    return None


TABLE = ("table",)


def table_lines(parts):
    """(part, section) -> the table rows and code lines of the section: not prose, not asked to cite."""
    out = defaultdict(list)
    for part, text in parts.items():
        secs = P.section_of_lines(text)
        fenced = False
        for i, l in enumerate(text.split("\n")):
            st = l.strip()
            if st.startswith("```"):
                fenced = not fenced
                continue
            if fenced or st.startswith("|"):
                out[(part, secs[i])].append(norm(l))
    return out


class Matcher:
    """A sentence carries a home's phrase when it holds FLOOR of the phrase's distinctive weight."""

    def __init__(self, entries, sents):
        df = Counter()
        for s in sents:
            df.update(set(toks(s[3])))
        self.n = max(len(sents), 1)
        self.idf = lambda w: math.log((self.n + 1) / (df.get(w, 0) + 1))
        self.phrases = []
        seen = set()
        for e in entries:
            if e["role"] != "states":
                continue
            ws = set(toks(e["entry_phrase"]))
            if len(ws) < MIN_PHRASE_WORDS or (e["rule_key"], e["home"], frozenset(ws)) in seen:
                continue
            seen.add((e["rule_key"], e["home"], frozenset(ws)))
            self.phrases.append((e["rule_key"], e["home"], ws, sum(self.idf(w) for w in ws), e["entry_phrase"]))
        self.post = defaultdict(list)
        for i, ph in enumerate(self.phrases):
            for w in ph[2]:
                self.post[w].append(i)

    def best(self, sentence):
        """[(score, shared, rule_key, home)] for each phrase the sentence carries past the floor."""
        st = set(toks(sentence))
        acc, cnt = defaultdict(float), Counter()
        for w in st:
            for i in self.post.get(w, ()):
                acc[i] += self.idf(w)
                cnt[i] += 1
        out = []
        for i, a in acc.items():
            k, h, ws, tot, _ = self.phrases[i]
            if cnt[i] >= MIN_SHARED and a / tot >= FLOOR:
                out.append((a / tot, cnt[i], k, h))
        return out


def measure(parts, entries, inv):
    """The restatements of the landed rules: (found, uncited rows, unanchored inventory rows)."""
    homes = homes_of(entries)
    sents = index(parts)
    by_sec, by_part = defaultdict(list), defaultdict(list)
    for s in sents:
        by_sec[(s[0], s[2])].append(s)
        by_part[s[0]].append(s)
    phrase = {(e["file"], e["line"], e["gist"]): e["entry_phrase"] for e in entries}
    found = {}          # (part, sentence, rule_key) -> (section, homes, paragraph, source)
    unanchored, tabled = [], []
    other = table_lines(parts)
    for r in inv:
        if r["role"] not in ("restates", "applies") or r["rule_key"] not in homes:
            continue
        pts = [x.strip() for x in r["points_to"].split(",") if x.strip()]
        hs = set(pts) or homes[r["rule_key"]]
        if r["section"] in hs:
            continue                      # said inside its own home: the rule, not a restatement
        s = anchor(r, phrase.get((r["file"], r["line"], r["gist"])), by_sec, by_part, other)
        if s is None:
            unanchored.append(r)
            continue
        if s is TABLE:
            tabled.append(r)
            continue
        if s[2] in hs:
            continue
        key = (s[0], s[3], r["rule_key"])
        prev = found.get(key)
        found[key] = (s[2], (prev[1] | hs) if prev else hs, s[4], "inventory")
    m = Matcher(entries, sents)
    for s in sents:
        for score, shared, k, h in m.best(s[3]):
            if s[2] in homes[k] or s[2] == h:
                continue                  # inside a home of the same rule
            key = (s[0], s[3], k)
            if key in found:
                continue
            found[key] = (s[2], {h}, s[4], "matcher")
    uncited = []
    for (part, sent, k), (sec, hs, para, src) in sorted(found.items(), key=lambda x: (x[0][0], x[1][0], x[0][1])):
        if P.cites_any(P.cites(sent) | P.cites(para), hs):
            continue
        uncited.append((part, sec, sent, k, ",".join(sorted(hs)), src))
    return found, uncited, unanchored, tabled, homes


def plants(entries, inv):
    """The three deliberate breaks; returns the list of those the check did not catch."""
    parts = P.load()
    base = measure(parts, entries, inv)[1]
    # A landed phrase from a home in Part 2, planted as a paragraph of CC 5.1 (another Part, no citation).
    e = next(e for e in entries if e["role"] == "states" and "|" not in e["entry_phrase"] and "`" not in e["entry_phrase"]
             and len(set(toks(e["entry_phrase"]))) >= 10 and e["home"][0] in "234")
    sent = e["entry_phrase"][0].upper() + e["entry_phrase"][1:].rstrip(".") + "."
    missed = []

    def planted(sec_number, text):
        p = dict(parts)
        part = "p" + sec_number[0]
        lines = p[part].split("\n")
        at = next(i for i, l in enumerate(lines) if re.match(rf"#+ {re.escape(sec_number)} ", l))
        lines[at + 1:at + 1] = ["", text, ""]
        p[part] = "\n".join(lines)
        return measure(p, entries, inv)[1]
    homes = homes_of(entries)[e["rule_key"]]
    away = next(n for n in ("6.1.6", "6.1.8", "5.4.4", "6.1.7", "5.3.5") if n not in homes)
    got = planted(away, sent)
    if len(got) != len(base) + 1 or not any(u[2] == sent for u in got):
        missed.append("an uncited copy of a landed rule in another section was not counted")
    cited = sent[:-1] + f" ([CC {e['home']}]({P.PARTS['p' + e['home'][0]]}#{e['home']}))."
    if len(planted(away, cited)) != len(base):
        missed.append("the same copy citing its home was counted")
    if len(planted(e["home"], sent)) != len(base):
        missed.append("the same sentence inside its own home was counted")
    return missed


def held():
    for l in MAXIMA.read_text(encoding="utf-8").split("\n"):
        if l.startswith("uncited_restatements\t"):
            return int(l.split("\t")[1])
    raise SystemExit("restatements: no uncited_restatements row in tools/restatements_max.tsv")


def tune(entries, inv):
    """Recall on the inventory's anchored restatements, and the hits on sentences the inventory reads as
    stating a different rule (a stand-in for false matches)."""
    parts = P.load()
    sents = index(parts)
    m = Matcher(entries, sents)
    homes = homes_of(entries)
    by_sec, by_part = defaultdict(list), defaultdict(list)
    for s in sents:
        by_sec[(s[0], s[2])].append(s)
        by_part[s[0]].append(s)
    phrase = {(e["file"], e["line"], e["gist"]): e["entry_phrase"] for e in entries}
    pos = neg = tp = fp = 0
    other = table_lines(parts)
    for r in inv:
        if r["rule_key"] not in homes:
            continue
        s = anchor(r, phrase.get((r["file"], r["line"], r["gist"])), by_sec, by_part, other)
        if s is None or s is TABLE:
            continue
        hits = [h for h in m.best(s[3]) if s[2] != h[3]]
        if r["role"] in ("restates", "applies"):
            pts = set(x.strip() for x in r["points_to"].split(",") if x.strip()) or homes[r["rule_key"]]
            pos += 1
            tp += any(h[2] == r["rule_key"] and h[3] in pts for h in hits)
        elif r["role"] == "states":
            neg += 1
            fp += any(h[2] != r["rule_key"] for h in hits)
    print(f"matcher floor {FLOOR}, at least {MIN_SHARED} shared words: finds {tp} of {pos} inventory restatements "
          f"at their home; matches {fp} of {neg} statements of one rule to another rule's home (read by hand: mostly true "
          f"restatements across keys, which is why the matcher's hits are counted)")


def main(argv):
    entries, inv = read("rule_entries.tsv"), read("rule_inventory.tsv")
    if "--tune" in argv:
        tune(entries, inv)
        return 0
    found, uncited, unanchored, tabled, homes = measure(P.load(), entries, inv)
    allkeys = Counter(r["rule_key"] for r in inv)
    homeless = {k: c for k, c in allkeys.items() if k not in homes}
    if "--homeless" in argv:
        for k, c in sorted(homeless.items(), key=lambda x: -x[1]):
            print(f"{k}\t{c}")
        return 0
    with WORKLIST.open("w", encoding="utf-8") as f:
        f.write("part\tsection\tsentence\trule_key\thome\tfound_by\n")
        for u in uncited:
            f.write("\t".join(x.replace("\t", " ") for x in u) + "\n")
    src = Counter(v[3] for v in found.values())
    by_part = Counter(u[0] for u in uncited)
    print(f"restatements: {len(homes)} rules with a home ({sum(len(v) for v in homes.values())} home sections); "
          f"{len(found)} restatements found ({src['inventory']} from the inventory, {src['matcher']} by the matcher), "
          f"{len(found) - len(uncited)} cite their home, {len(uncited)} do not "
          f"({', '.join(f'{p} {n}' for p, n in sorted(by_part.items()))})")
    print(f"restatements: {len(tabled)} inventory restatements sit in a table row or a code line (not asked to cite); "
          f"{len(unanchored)} are no longer found in their section; "
          f"{len(homeless)} rule keys have no home ({sum(homeless.values())} statements)")
    errs = plants(entries, inv)
    for e in errs:
        print(f"restatements: plant not caught: {e}")
    cap = held()
    if len(uncited) > cap:
        errs.append("over")
        print(f"restatements: {len(uncited)} uncited restatements, above the maximum {cap}: cite the home "
              f"(see {WORKLIST.relative_to(ROOT)})")
    elif len(uncited) < cap:
        print(f"restatements: {len(uncited)} uncited, below the maximum {cap}: lower it in tools/restatements_max.tsv")
    else:
        print(f"restatements: plants caught; {len(uncited)} uncited, at the maximum")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
