#!/usr/bin/env python3
"""
CC — the stale-reference gate for the Parts.

The Parts state rules, not history. This checker lists every line of constitution/part_*.md,
constitution/covers/*.md, constitution/STEWARDSHIP.md and constitution/EXECUTIVE_SUMMARY.md that
still carries one of the patterns the 1.0 sweep removes:

  old-numbering   section numbers of the documents CC was folded from ("S8.1.12.4", "CEG §11",
                  "§3.4 D26"), and "Book N" / "the Covenant" as a reference
  pointers        files and code a reader cannot follow from the page (MISSION.md, FSD-003,
                  foo.py, bar.rs#sym, LANGUAGE_PRIMER.md); the published data files an implementer
                  interoperates against (.tsv/.json vectors, .tla/.lean models) are allowed
  history         release and ticket history ("rc9", "RC1-1b", "v1.4 T-3", "Phase C", "Option A",
                  "(LIVE)", "deprecated", "already-rejected", "next generation of authors")
  labels          working labels that no volume defines ("AV-17", "F-AV-ROLLBACK", "OQ-4",
                  "NodeCore P8", "Piece 10", "§Q", "R1/Q1", "V058", "D08")
  comparisons     named projects and products the house rule keeps out of the Parts
  dated-facts     calendar dates and CVE numbers attached to rules

Lines inside fenced code blocks are skipped for comparisons and dated facts (vectors and examples
carry dates) and reported for the rest. A line ending in `<!-- stale-ok -->` is exempt; use it only
for a reference that is itself the rule (a wire constant's single source).

Run:  python3 tools/check_stale_refs.py            # report, exit 1 if anything is found
      python3 tools/check_stale_refs.py --counts   # counts by file and class only
"""
import glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = sorted(glob.glob(os.path.join(ROOT, "constitution", "part_*.md"))) + \
        sorted(glob.glob(os.path.join(ROOT, "constitution", "covers", "*.md"))) + \
        [os.path.join(ROOT, "constitution", "STEWARDSHIP.md"), os.path.join(ROOT, "constitution", "EXECUTIVE_SUMMARY.md")]

PROJECTS = r"Nostr|Matrix|Element|Synapse|Mastodon|Bluesky|Ozone|IPFS|Scuttlebutt|\bSSB\b|Keybase|Sigstore|\bTUF\b|Holochain|Lightning Network|Sardex|\bWIR\b|Circles UBI|Hypercore|SUNDR|Tahoe-LAFS|WhatsApp|Threema|Briar|SimpleX|Delta Chat|Discord|Facebook|subreddit|bitsavers|Casper FFG|KERI|JS8Call|macaroons|ZCAP|SPKI|ActivityPub|Twitter|Roku|Nest thermostat|nest_thermostat|roku_living_room|Stripe|Spamhaus|The DAO|NeuralHash|Chromium|Android 1\d|EigenTrust|MAX program|HoloFuel|Signal-style|Signal ships|like Signal|Tor leaves|Linux and its"

CLASSES = {
    "old-numbering": [
        (r"\bS\d+(?:\.\d+)+\b", None),
        (r"CEG §\s?\d", None),
        (r"(?<![A-Za-z])§\s?\d+(?:\.\d+)+", r"GDPR|Art\.|MH §|§§|Annex|CFR|U\.S\.C|HB \d"),
        (r"\bBooks? [IVX]+\b", None),
        (r"\bthe Covenant\b|CIRIS Covenant|Covenant Self-Renewal", None),
        (r"\bSection (?:I|II|III|IV|V)\b", None),
    ],
    "pointers": [
        (r"MISSION\.md|LANGUAGE_PRIMER\.md|FEDERATION_ANNOUNCEMENT\.md|TRUST_CONTRACT\.md|PRIOR_ART\.md|LIGHTNET_DARKNET\.md|CLAUDE\.md|README\b", r"master index\]\(\.\./README\.md\)"),
        (r"\bFSD-\d{3}\b|\bFSD/", None),
        (r"\b[a-z_]+\.py\b|\b[a-z_]+\.rs#|\b[a-z_]+\.rs\b|::[a-z_]+\(", None),
        (r"ciris-crypto|scope_privacy::|AlmJoinPlanner|serde\(skip\)|PeerResolver|registry_signing_keys|cirisnode_contributions|Rust handlers|OpenAPI export", None),
    ],
    "history": [
        (r"\brc\d+\b|\bRC\d+-\d|\bRC\d+\b|1\.0-RC\d+", r"1\.0-rc1[01]\b"),
        (r"\bv1\.4 T-3|\bPhase [A-E]\b|\bOption [AB]\b|\(LIVE\)|already-rejected|next generation of authors|downstream-demand-driven|recommended for v1\b|deferred to 1\.1", None),
        (r"\bdeprecated\b|\bDEPRECATED\b|\blegacy\b|\bLegacy\b", r"Legacy label, closed|legacy_ref|legacy unprefixed|Legacy & Knowledge|6-legacy|agent's legacy|its legacy"),
        (r"\bAs shipped\b|as of rc|at rc\d|at re-pin|re-pin \d|steward ruling|steward direction|operator ruling|ruled \d{4}|ruling on #|ruling 20\d\d", None),
        (r"not yet (?:built|shipped|published|installed|wired)|is an rc\d+ item|will print here", None),
    ],
    "labels": [
        (r"\bAV-\d+\b|\bF-AV-[A-Z]+|\bOQ-\d\b|NodeCore P\d+\b|\bPiece \d+\b|§Q\b|\bR1/Q1\b|\bV0\d\d\b|\bD0\d\b|\bCONFIRM-\d\b|\bF-3 detector|\bCEM\b|\bHE-300\b", r"8\.8\.10|HE-300 benchmark"),
        (r"\(normative: [A-Z]\d|\bV\d lock\b|\bE\d–E\d lock|\bCatch-up bound \(P\d\)|\bCloses G\d\b|\bcloses R\d\b|\b\d+ stories\b|\(1 reviewer\)|\bS4 default\b", None),
        (r"Accord Addendum 1|\bAddendum 1\b|ACCORD_UPDATE|ACCORD §|Accord §[IVX]|Section VI Ch\d|ACCORD §VII", None),
        (r"\(part_\d [a-z]|_ID env var|LensCore knob|\[configurable; default", None),
    ],
    "comparisons": [
        (PROJECTS, None),
        (r"\bLeviculum\b|\bERC-8004\b|arXiv:\d|\bMegolm\b|\bSideband\b|Vasserman et al|Guerraoui et al|\beltoo\b|Lightning-class|Ubuntu-aligned|AT Protocol|app\.bsky|Britney|Texas HB|Paxton 20\d\d|DigiNotar|Delaware/BFT|webpsan|\bSignal’s\b|\bSignal's\b|Tor v3|I2P b33", r"8\.6\.1"),
        (r"Per [A-Z][a-z]+ [A-Z][a-z]+['’]s\b|Bostrom \(2011\)", r"8\.6|Other informational citations"),
        (r"ciris\.ai/(?:cewp|constitutional-mesh|safety|philosophy)|the cewp (?:claim|privacy promise)|cewp scaling model|need so dire|CEG['’]s moat|differentiated story|Cheapest win|the honest line|most product-complete|thirteenth path|named as a bet|named bet|Considered and not adopted|This boundary is provisional|This answers the open question|open transport question|kept alias|share a household|street address|transparent translation rate", r"8\.6\.1|Fact Sheet"),
        (r"\b(?:PGP|X\.509|W3C VC)\b.{0,80}(?:treat|types|prior)", None),
        (r"all \d+ surveyed|surveyed systems|surveyed networks|categorically stronger|the only model|first to ship|No prior (?:system|identity)|against the field", None),
    ],
    "working-notes": [
        (r"is, honestly,|honestly, near|Adversarial reviewers|canonical working draft|nobody has implemented|trio Phase|\bFirst deployment\b", None),
        (r"in 1\.0 scope|(?:NOT |not )?required for 1\.0\b|CHECK-arm", None),
        (r"\bplain rules? \d+[a-z]?\b|\(G\d{1,2}\)|\(Scope; plain", None),
        (r"ethically optimal|prioritisation heuristic|must be balanced|locally optimised|principle conflicts or trade-offs", None),
    ],
    "raw-paths": [
        (r"\bformal/[a-z_]+(?:/[A-Za-z_]+\.(?:tla|lean|py|md))?|\btools/[a-z_]+\.py|\bconstitution/[a-z_]+\.tsv|\blean:[a-z-]+:", r"Where the rest lives|What it promises|^\| (?:\d+|all of them) |evidence_refs|governance_policy\.tsv|claims\.tsv|evidence_pins\.tsv"),
        (r"Portal / Verify|\bciris-registry-core\b|ciris_keyring::|\bPolicyCorridor\.lean\b", None),
    ],
    "dated-facts": [
        (r"\b20\d\d-\d\d-\d\d\b|\bCVE-\d{4}-\d+", r"produced_at|asserted_at|valid_until|effective_at|revoked_after|applicable from|\d{4}-\d{2}-\d{2}T"),
        (r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December) 20\d\d\b", r"8\.6\.1|Fact Sheet"),
    ],
}
CODE_SKIP = {"comparisons", "dated-facts"}


def scan():
    hits = []
    for f in FILES:
        rel = os.path.relpath(f, ROOT)
        fenced = False
        for n, line in enumerate(open(f, encoding="utf-8"), 1):
            if line.lstrip().startswith("```"):
                fenced = not fenced
                continue
            if line.rstrip().endswith("<!-- stale-ok -->"):
                continue
            for cls, pats in CLASSES.items():
                if fenced and cls in CODE_SKIP:
                    continue
                for pat, allow in pats:
                    for m in re.finditer(pat, line):
                        if allow and re.search(allow, line):
                            continue
                        hits.append((rel, n, cls, m.group(0), line.strip()))
                        break
    return hits


def main(argv):
    hits = scan()
    if "--counts" in argv:
        from collections import Counter
        byfile = Counter((h[0].split("/")[-1], h[2]) for h in hits)
        files = sorted({k[0] for k in byfile})
        classes = list(CLASSES)
        print("file".ljust(30) + "".join(c.rjust(14) for c in classes) + "  total")
        for fl in files:
            row = [byfile.get((fl, c), 0) for c in classes]
            print(fl.ljust(30) + "".join(str(x).rjust(14) for x in row) + str(sum(row)).rjust(7))
        print("total".ljust(30) + "".join(str(sum(byfile.get((fl, c), 0) for fl in files)).rjust(14) for c in classes) + str(len(hits)).rjust(7))
    else:
        for rel, n, cls, tok, line in hits:
            print(f"{rel}:{n}: [{cls}] {tok!r}  …{line[:140]}")
        print(f"check_stale_refs: {len(hits)} line(s) carry a stale reference, pointer, history, label, comparison or dated fact")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
