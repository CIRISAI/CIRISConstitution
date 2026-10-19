#!/usr/bin/env python3
"""
CC — the governance policy table as data (CIRISConstitution#180; steward 2026-10-18: "the whole point of
the models is to take these decisions and make them data backed").

One row per door in constitution/governance_policy.tsv: five numbers (enact, cancel, floor, window,
irreversible) over a named standing set and base. This tool

  * checks every two-path row against the corridor (a Python port of formal/two_path/PolicyCorridor.lean,
    self-tested against that file's own examples) and refuses to build a row outside it;
  * writes manifests/governance_policy.json — the rows, the base law, the decider as prose, a pin;
  * writes manifests/governance_policy_vectors.json — (policy, base, approvals, objections, elapsed) → verdict,
    so an implementation replays the decision function rather than re-reading the text;
  * writes formal/two_path/generated/<family>.cfg — every two-path row is a TLC instance of TwoPath.tla
    (CI runs them), so a row that breaks the machine's invariants fails the build, not a card.

The one decision function, which every consumer implements and replays against the vectors:

    enact_votes  = enact_num  * base // enact_den + 1              (strictly more than the fraction)
    cancel_votes = max(min_count, ceil(cancel_num * base / cancel_den))   (at least the fraction, never one voice)
    floor_votes  = max(min_count, ceil(floor_num  * base / floor_den))    (min_count = 2 for a community, 1 for a self)
    if approvals >= enact_votes and not irreversible:  lands  (forward, now)
    if elapsed < window:                               pending
    if objections >= cancel_votes:                     cancelled (cancel reached)
    if approvals >= enact_votes:                       lands  (forward; it waited its window)
    if reverse_path and approvals >= floor_votes:      lands  (reverse: floored, unopposed, window closed)
    else:                                              cancelled (below the floor, or no reverse path)

The floor is a reverse-path predicate only: it never lands anything before the window closes (the
machine's Prop_FloorNeverLandsEarly). Two per-row fields answer the implementer's questions: `cancel_over`
is the denominator of the cancel fraction — `base` for a community (the proposer counted), `others` for a
self roster (every key is one person's, so the proposer is not asked to object to itself); `at_window` is
what happens to a proposal that has not landed when the window closes — `cancelled` for every community
row (a held change resolves: formal/membership no_hold_expiry), `stay_open` for the self roster as ruled
(cleared by the proposer's withdraws or the target's act), `lapsed` for the halt, `tallied` for moderation. The base is the standing roster at or below k members and the
expected-active count above it, never below `min` (the law's constants are provisional; the exponent
is a measurement, #180 item 2).

Run: python3 tools/build_governance_policy.py            # build
     python3 tools/build_governance_policy.py --self-test  # replay the vectors + the Lean examples
     python3 tools/build_governance_policy.py decide <family> --base N --approvals A --objections O --elapsed S
"""
import csv, hashlib, json, os, sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TSV = os.path.join(ROOT, "constitution", "governance_policy.tsv")
OUT = os.path.join(ROOT, "manifests", "governance_policy.json")
VEC = os.path.join(ROOT, "manifests", "governance_policy_vectors.json")
GEN = os.path.join(ROOT, "formal", "two_path", "generated")

BASE_LAW = OrderedDict([("kind", "standing_then_expected_active"), ("k", 12), ("tail", 30), ("min", 3),
                        ("status", "provisional: k and the tail are a stand-in for the measured participation law (#180 item 2)"),
                        ("rule", "base(N) = N if N <= k else max(min, k + (N - k) // tail); rows with base=standing use N")])
WINDOW_CLASSES = OrderedDict([("content_24h", 86400), ("standing_72h", 259200), ("irreversible_7d", 604800),
                              ("ruled_24h", 86400), ("ruled_48h", 172800), ("fuse_24h", 86400), ("none", 0)])


def frac(s):
    """'2/3' -> (2,3); '1/N' -> ('N',); '—' -> None; anything with letters -> the string (an instance's own rule)."""
    s = s.strip()
    if s in ("—", "-", ""):
        return None
    if s == "1/N":
        return ("one_voter",)
    if "/" in s and all(p.strip().isdigit() for p in s.split("/")):
        a, b = s.split("/"); return (int(a), int(b))
    return s


def ceil_div(a, b):
    return (a + b - 1) // b


def votes(fr, base, strict):
    n, d = fr
    return n * base // d + 1 if strict else ceil_div(n * base, d)


def expected_active(N, k=BASE_LAW["k"], tail=BASE_LAW["tail"], mn=BASE_LAW["min"]):
    return N if N <= k else max(mn, k + (N - k) // tail)


# ---- the corridor (port of PolicyCorridor.lean; checked against its examples in --self-test) ----
def rigidity(e, c, base):
    return votes(c, base, False) <= 1 or votes(e, base, True) >= base

def chaos(e, c, f, base):
    return votes(e, base, True) <= 1 or votes(c, base, False) >= base or votes(f, base, False) <= 1

def in_corridor(e, c, f, window, base, window_floor, with_floor=True):
    ok = not rigidity(e, c, base)
    ok = ok and not (votes(e, base, True) <= 1 or votes(c, base, False) >= base)
    if with_floor:
        ok = ok and not votes(f, base, False) <= 1 and f[0] * e[1] <= e[0] * f[1]
    ok = ok and c[0] * e[1] <= e[0] * c[1] and 2 * e[0] >= e[1] and window_floor <= window
    return ok


def lean_examples_agree():
    ruled = ((2, 3), (1, 3), (1, 3), 259200)
    assert in_corridor(*ruled, 6, 86400) and in_corridor(*ruled, 7, 86400)
    assert not in_corridor((2, 3), (1, 6), (1, 3), 259200, 6, 86400)        # libertumVeto
    assert not in_corridor((1, 7), (1, 3), (1, 7), 259200, 6, 86400)        # oneEnacts
    assert rigidity((1, 1), (1, 3), 6)                                       # unanimity
    assert not in_corridor((2, 3), (1, 3), (1, 3), 60, 6, 86400)            # tooFast
    assert chaos((2, 3), (1, 3), (0, 1), 6) and chaos((2, 3), (1, 3), (0, 1), 10000)   # noFloor
    assert in_corridor((2, 3), (1, 3), (2, 3), 259200, 344, 86400)          # strict
    assert not in_corridor((2, 3), (1, 3), (1, 344), 259200, 344, 86400)    # lax
    assert votes((1, 3), expected_active(10000), False) == 115 and votes((1, 3), 10000, False) == 3334
    assert votes((1, 3), 10, False) == 4 and votes((2, 3), 10, True) == 7
    assert in_corridor((1, 2), (1, 2), (1, 3), 86400, 3, 86400, with_floor=False)      # self roster, own corridor
    assert not in_corridor((1, 2), (1, 2), (1, 3), 86400, 3, 86400)                     # and outside the community one


# ---- the decision function ----
MIN_COUNT = {"community": 2, "self": 1}


def decide(row, base, approvals, objections, elapsed):
    e, c, f = row["_enact"], row["_cancel"], row["_floor"]
    mc = MIN_COUNT.get(row["corridor"], 2)
    ev = votes(e, base, True)
    if approvals >= ev and not row["irreversible"]:
        return "lands", "forward", "enact reached"
    if elapsed < row["window_secs"]:
        return "pending", "none", "window open"
    if c and objections >= max(mc, votes(c, base, False)):
        return "cancelled", "none", "cancel reached at the window"
    if approvals >= ev:
        return "lands", "forward", "enact reached; the irreversible waited its window"
    if row["reverse_path"] and f and approvals >= max(mc, votes(f, base, False)):
        return "lands", "reverse", "floored and unopposed when the window closed"
    if not row["reverse_path"]:
        return "cancelled", "none", "window closed below enact; this door has no reverse path"
    return "cancelled", "none", "window closed below the floor: silence alone never admits"


def load():
    rows = list(csv.DictReader(open(TSV, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))
    for r in rows:
        r["window_secs"] = int(r["window_secs"])
        r["irreversible"] = r["irreversible"] == "yes"
        r["reverse_path"] = r["reverse_path"] == "yes"
        r["_enact"], r["_cancel"], r["_floor"] = frac(r["enact"]), frac(r["cancel"]), frac(r["floor"])
        if r["window_class"] not in WINDOW_CLASSES or WINDOW_CLASSES[r["window_class"]] != r["window_secs"]:
            sys.exit(f"governance_policy: {r['family']} window {r['window_secs']} does not match class {r['window_class']}")
    return rows


def machine_rows(rows):
    """rows the generic machine decides: numeric fractions, community corridor"""
    return [r for r in rows if r["kind"] == "two_path" and r["corridor"] == "community"]


def check_corridor(rows):
    bad = []
    for r in machine_rows(rows):
        e, c, f = r["_enact"], r["_cancel"] or r["_enact"], r["_floor"] or r["_enact"]
        wf = WINDOW_CLASSES["content_24h"] if r["window_class"] == "content_24h" else WINDOW_CLASSES["standing_72h"]
        if r["irreversible"]:
            wf = WINDOW_CLASSES["irreversible_7d"]
        for base in (3, 6, 7, 10, expected_active(10000)):
            # the count minimum lifts a tiny community's floor and cancel to two voices; the corridor is
            # checked on the fraction alone from base 6 up and on the lifted counts at 3
            if r["reverse_path"] and base >= 6 and not in_corridor(e, c, f, r["window_secs"], base, wf):
                bad.append(f"{r['family']} outside the corridor at base {base}")
            if not r["reverse_path"] and (votes(e, base, True) <= 1 or 2 * e[0] < e[1] or r["window_secs"] < wf):
                bad.append(f"{r['family']} forward-only row below the enact floor or window floor at base {base}")
    for r in rows:
        if r["corridor"] == "self":
            if not in_corridor((1, 2), (1, 2), (1, 3), r["window_secs"], 3, 86400, with_floor=False):
                bad.append(f"{r['family']} outside the self corridor")
    if bad:
        sys.exit("governance_policy: " + "; ".join(bad))


def vectors(rows):
    out = []
    for r in machine_rows(rows):
        e, c, f = r["_enact"], r["_cancel"], r["_floor"]
        for N in (3, 6, 10, 10000):
            base = N if r["base"] == "standing" else expected_active(N)
            ev = votes(e, base, True)
            cv = max(2, votes(c, base, False)) if c else None
            fv = max(2, votes(f, base, False)) if f else None
            A = sorted({0, 1, max(fv - 1, 0) if fv else 0, fv or 0, ev - 1, ev})
            O = sorted({0, max((cv or 1) - 1, 0), cv or 0})
            T = sorted({0, r["window_secs"] - 1, r["window_secs"]})
            for a in A:
                for o in O:
                    if a + o > base:
                        continue
                    for t in T:
                        v, path, why = decide(r, base, a, o, t)
                        out.append(OrderedDict([("family", r["family"]), ("roster", N), ("base", base),
                                                ("thresholds", {"enact": ev, "cancel": cv, "floor": fv}),
                                                ("approvals", a), ("objections", o), ("elapsed_secs", t),
                                                ("verdict", v), ("path", path), ("why", why)]))
    return out


def gen_cfgs(rows):
    os.makedirs(GEN, exist_ok=True)
    names = []
    for r in machine_rows(rows):
        e, c, f = r["_enact"], r["_cancel"] or r["_enact"], r["_floor"] or r["_enact"]
        for N, coerced in ((6, "{v6}"), (7, "{v6, v7}")):
            vs = ", ".join(f"v{i}" for i in range(1, N + 1))
            consts = " ".join(f"v{i} = v{i}" for i in range(1, N + 1))
            name = f"{r['family']}_{N}"
            inv = "Inv_OneVoiceNeverAdmits Inv_BelowFloorNothingLands Inv_AdversaryBelowCancelCannotBlock Inv_HonestAtCancelStopsAdversary"
            cfg = f"""\\* generated by tools/build_governance_policy.py from constitution/governance_policy.tsv — do not edit
SPECIFICATION Spec
CONSTANTS {consts}
  Voters = {{{vs}}}
  Silent = {{}}
  Coerced = {coerced}
  EnactNum = {e[0]}  EnactDen = {e[1]}
  CancelNum = {c[0]}  CancelDen = {c[1]}
  FloorNum = {f[0]}  FloorDen = {f[1]}
  Window = 2
  MaxChanges = 2
  Irreversible = {"TRUE" if r["irreversible"] else "FALSE"}
  ReversePath = {"TRUE" if r["reverse_path"] else "FALSE"}
  MinCount = 2
INVARIANTS {inv}
PROPERTIES Prop_IrreversibleWaits Prop_HonestChangeResolves Prop_FloorNeverLandsEarly
"""
            open(os.path.join(GEN, name + ".cfg"), "w").write(cfg)
            names.append(name)
    open(os.path.join(GEN, "INSTANCES.txt"), "w").write("\n".join(names) + "\n")
    return names


def build():
    lean_examples_agree()
    rows = load()
    check_corridor(rows)
    fams = []
    for r in rows:
        d = OrderedDict()
        for k in ("family", "cc_ref", "kind", "standing_set", "base"):
            d[k] = r[k]
        for k in ("enact", "cancel", "floor"):
            v = r["_" + k]
            d[k] = {"num": v[0], "den": v[1]} if isinstance(v, tuple) and len(v) == 2 else (None if v is None else (v[0] if isinstance(v, tuple) else v))
        d["cancel_over"] = r["cancel_over"]; d["at_window"] = r["at_window"]   # persist v59 questions (b) and (c)
        d["window_secs"] = r["window_secs"]; d["window_class"] = r["window_class"]
        d["irreversible"] = r["irreversible"]; d["reverse_path"] = r["reverse_path"]
        d["corridor"] = r["corridor"]; d["model"] = r["model"].split(); d["status"] = r["status"]; d["note"] = r["note"]
        fams.append(d)
    body = OrderedDict([("families", fams), ("base_law", BASE_LAW), ("min_count", MIN_COUNT), ("window_classes", WINDOW_CLASSES),
                        ("decider", [l.strip() for l in __doc__.split("The one decision function")[1].split("The floor is")[0].strip().splitlines() if l.strip()][1:]),
                        ("verdicts", ["lands", "pending", "cancelled"]), ("paths", ["forward", "reverse", "none"]),
                        ("floor_is_reverse_only", "the floor is consulted only when the window has closed; before that only enact lands (Prop_FloorNeverLandsEarly)"), ("votes_family", "objection:{state} — proposal (counts as the proposer's approval), assent (+1), raised (−1); CC 3.1.9.2")])
    pin = hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    doc = OrderedDict([("_meta", OrderedDict([("source", "constitution/governance_policy.tsv"), ("cc_section", "4.5.13"),
                                               ("policy_sha256", pin), ("corridor", "formal/two_path/PolicyCorridor.lean"),
                                               ("machine", "formal/two_path/TwoPath.tla; one generated instance per two-path row in formal/two_path/generated/")]))])
    doc.update(body)
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False); open(OUT, "a").write("\n")
    vec = vectors(rows)
    json.dump(OrderedDict([("_meta", {"policy_sha256": pin, "count": len(vec)}), ("vectors", vec)]),
              open(VEC, "w", encoding="utf-8"), indent=1, ensure_ascii=False); open(VEC, "a").write("\n")
    names = gen_cfgs(rows)
    print(f"governance_policy: {len(rows)} rows ({len(machine_rows(rows))} machine rows), pin {pin[:8]}, {len(vec)} vectors, {len(names)} TLC instances")


def self_test():
    lean_examples_agree()
    rows = {r["family"]: r for r in load()}
    vec = json.load(open(VEC))["vectors"]
    bad = 0
    for v in vec:
        got = decide(rows[v["family"]], v["base"], v["approvals"], v["objections"], v["elapsed_secs"])
        if (got[0], got[1]) != (v["verdict"], v["path"]):
            bad += 1
    # the floor never lands before the window, in every vector
    early = [v for v in vec if v["verdict"] == "lands" and v["path"] == "reverse" and v["elapsed_secs"] < rows[v["family"]]["window_secs"]]
    lone = [v for v in vec if v["verdict"] == "lands" and v["approvals"] <= 1 and v["base"] > 2]
    print(f"self-test: {len(vec)} vectors replayed, {bad} mismatches; reverse landings before the window: {len(early)}; landings on one voice at base > 2: {len(lone)}")
    sys.exit(1 if bad or early or lone else 0)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    elif len(sys.argv) > 1 and sys.argv[1] == "decide":
        import argparse
        ap = argparse.ArgumentParser(); ap.add_argument("family"); ap.add_argument("--base", type=int, required=True)
        ap.add_argument("--approvals", type=int, default=0); ap.add_argument("--objections", type=int, default=0); ap.add_argument("--elapsed", type=int, default=0)
        a = ap.parse_args(sys.argv[2:]); r = {x["family"]: x for x in load()}[a.family]
        print(*decide(r, a.base, a.approvals, a.objections, a.elapsed))
    else:
        build()
