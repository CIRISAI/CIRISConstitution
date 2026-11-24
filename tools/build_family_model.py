#!/usr/bin/env python3
"""The family model manifest, draft 0: every scores family as one row over the agreed columns.

Sources: the CC table (formal/derivation/family_kind_verb.tsv: kind, side, verbs, maintains_record,
reference) and persist's census at the v61 head (formal/derivation/census_v61.tsv: what the code
enforces today on each axis). Every cell carries its value and its source: cc-table, code-v61,
prose (bespoke code outside the closed vocabulary), or gap (nothing enforces). The vendor gate of a
later version refuses a gap; this draft counts them. A placement the census leaves to the signer and the
text states for no family takes the default of formal/derivation/placement_text.tsv, with the audience of
each scope. What a row confers comes from the family's shape (formal/derivation/family_shapes.tsv) and
formal/derivation/confers_text.tsv; which key slot each placeholder holds from the registry's segment classes;
which rows a derived row must equal from confers_text.tsv; which named answers read the family's rows (`read_by`) from the KX of its rule cells. Writes manifests/family_model.json; --check
only compares.
"""
import csv, glob, hashlib, json, os, re, sys
from collections import Counter, OrderedDict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CC = os.path.join(ROOT, "formal/derivation/family_kind_verb.tsv")
CENSUS = os.path.join(ROOT, "formal/derivation/census_v61.tsv")
CENSUS_NAMES = os.path.join(ROOT, "formal/derivation/census_names.tsv")
SIGNER_TEXT = os.path.join(ROOT, "formal/derivation/signer_rule_text.tsv")
# Cells where a reading found the text states another rule than the store enforced (formal/derivation/text_review.tsv, reading differs).
# For these the table takes the text's rule and keeps the store's reading beside it as `code`.
TEXT_OVER_CODE = {tuple(l.split("\t")[:2]) for l in open(os.path.join(ROOT, "formal/derivation/text_review.tsv"), encoding="utf-8").read().split("\n")
                  if l and not l.startswith("#") and l.split("\t")[2:3] == ["differs"]}
CELL_TEXT = os.path.join(ROOT, "formal/derivation/cell_text.tsv")
PLACEMENT_TEXT = os.path.join(ROOT, "formal/derivation/placement_text.tsv")
SCOPES = ("self", "family", "community", "affiliations", "species", "biosphere", "federation")   # CC 2.1: the closed set of seven
COUNT_TEXT = os.path.join(ROOT, "formal/derivation/count_text.tsv")
POLICY = os.path.join(ROOT, "manifests/governance_policy.json")
SIGNED_OBJECT = os.path.join(ROOT, "constitution/signed_object.tsv")
SIGNED_OBJECT_V2 = os.path.join(ROOT, "constitution/signed_object_v2.tsv")
# The families whose payload CC 2.6.1.4 states, by the schema rule that holds it (manifests/family_payloads_v2.cddl).
# A family whose leaves have different payloads has one rule for each (membership:{stage}): each member then names its rule.
FORWARD_PAYLOAD = OrderedDict([("group-roster", "group:roster"), ("membership-change", "membership:{stage}"),
                               ("membership-reply", "membership:{stage}"),
                               ("occurrence-revocation", "identity:occurrence_revocation"),
                               ("entity-revocation", "revocation:{entity_type}:{reason}"),
                               ("takedown-notice", "takedown_notice:{basis}"), ("custody-ack", "custody:{kind}"),
                               ("key-grant", "key_grant:{axis}"), ("delivery-ack", "delivery_ack:{stream_id}"),
                               ("identity-occurrence", "identity:occurrence"), ("identity-amendment", "identity_amendment"),
                               ("deferral-response", "deferral:response:{outcome}"), ("deferral-request", "deferral:request"),
                               ("canonical-rebind", "transport:canonical_rebind"), ("trust-accepts", "trust:{job}:{version}"),
                               ("act-ack", "act:ack"), ("objection-vote", "objection:{state}"),
                               ("owner-binding", "ownership:{relation}:{target_kind}:{version}"),
                               ("holon-claim", "holon:claim"),
                               ("leaf-vouch", "mls:leaf_vouch")])
FORWARD_PARTIAL = {"deferral:response:{outcome}", "deferral:request", "transport:canonical_rebind", "trust:{job}:{version}"}   # the rule names some members; the cell's others stay
FORWARD_LEAVES = {"membership:{stage}": ("widening", "removal", "acceptance", "decline"),   # the leaves the rules state; the others keep their cell
                  "trust:{job}:{version}": ("accepts",)}
CELL_CITES = os.path.join(ROOT, "formal/derivation/cell_cites.tsv")
FOLD_TEXT = os.path.join(ROOT, "formal/derivation/fold_text.tsv")
FOLD_MARKS_MAX = 50   # uses of words no other vocabulary has; the number only falls
COUNT_SOURCES = ("subject_group", "signer_group", "dimension_authority", "accord", "trust_root", "self", "conferrer")
COUNT_KEYS = ("leaf", "verb", "identity", "group", "seats", "act")
COUNT_ARM_KEYS = COUNT_KEYS   # a count arm reads `act` as the row member self.act (tools/kx_translate.py COUNT_KEYS)
COUNT_OPEN_MAX = 4   # families with a cosign cell that is not none and no typed count; the number only falls
REG = os.path.join(ROOT, "manifests/namespace_registry.json")
OUT = os.path.join(ROOT, "manifests/family_model.json")
DEFAULT = os.path.join(ROOT, "formal/derivation/family_default_row.json")
DEPARTS = os.path.join(ROOT, "manifests/family_departures.tsv")
REASONS = os.path.join(ROOT, "formal/derivation/departure_reasons.json")
REASONS_MD = os.path.join(ROOT, "formal/family_model/DEPARTURES.md")
BASES = ("text", "census", "build")
COLUMNS = OrderedDict([
    ("kind", "Priorities | Rules | Manner | Identity | Confidence | Facts | Circumstances | Process | Model | Structure | Premises"),
    ("side", "thing | account (a function of kind)"),
    ("verbs", "subset of {attest, authorize, replace, withdraw, recant}"),
    ("maintains_record", "bool: the row is itself the evidence that something happened; fixes erasure and projection"),
    ("reference", "none | pre:<kind|any> | carry:<kind> (the row it names; only a carry is a cell of the carries grid)"),
    ("placement", "self_collective | targeted_family | targeted_room | commons | addressed"),
    ("signer_rule", "{self | owner_of_subject | seat_role(duty) | roster_member(at) | minter | steward | any_registered} x via {none | delegates_to(scope, depth, term, caps)} x conditions ⊆ {adult, capacitated, not_subject, not_author}"),
    ("emitter_class", "derived from signer_rule: person (any registered key) | self | owner | seat:<duty> | roster | steward | substrate:<identity_type> | shut; several joined by |; the tier that writes the family's rows, read by nothing at admission"),
    ("subject_rule", "{subject_kind, cardinality, must_be_registered, for_key_id ∈ {none, serve_seat, recipient}, in_audience, attested_party, subject_blind}"),
    ("cosign_rule", "none | group_consensus_protocol | moderator_quorum | accord | deciding_seat_plus_outside"),
    ("polarity", "the registry's polarity class"),
    ("body", "CDDL reference beyond the signed object; an existence_only audience names a two-part shape"),
    ("freshness", "{judged_at ∈ {signed_instant_with_W, receipt}, W}"),
    ("lifecycle", "{withdraws_by ⊆ {attester, subject, cosigned}, retraction_class ∈ {peer, duty_record, authority_act, cosigned}, supersedes ∈ {same_attester, none}, expires, rotation_on_removal}"),
    ("replication", "{tier ∈ {local, cohort, federation}, audience ∈ {cohort, cohort_plus_subjects(full|existence_only), addressee, everyone}, non_recipient ∈ {drop, hold_sealed}, held ∈ {settle_on_key, refuse}}"),
    ("projection", "{table, rebuild ∈ {byte_equal, none}}"),
    ("erasure_route", "dsar | purge | legal_hold | none"),
    ("names_head", "roster | standing | none | by_placement: which head a row of the family names in refs.head (CC 2.4.1.1, CC 2.7.8); null where the placement is unread"),
    ("shape", "claim | content | consent | door | consent+door, the family's kernel shape (formal/derivation/family_shapes.tsv); null where none takes it"),
    ("descends_on_withdrawal", "bytes_and_words | row | nothing: what a holder other than the signer drops when a row of the family is withdrawn (CC 6.1.5 N5)"),
    ("subject_may_withdraw", "true | false | a map by selector | null where open: whether a party a row of the family names, other than its signer, may withdraw it under rules 2 to 4 of CC 2.4.1.1; false on the kept list, for a row never withdrawn and for a counted row"),
    ("accountability_record", "bool: the row is kept as the record of its signer's own acts, so the signer's owner may not withdraw it (CC 3.1.5)"),
    ("may_carry_under", "true | false | a map by selector | null where open: a row of the family may be a deputy's edge and carry refs.also.under, a set of exactly one (CC 4.5.5)"),
    ("standing_act", "offer | end | acceptance | exercise | none | a map by selector | null where open: what a row of the family is with respect to a standing; receipter is admitted only on an offer and lifts only on a counted end (CC 2.4.1.1)"),
    ("room_content", "true | false | a map by selector: a row of the family placed at a room or a family scope is the room's content, read by the tips rule after its author's seat ends; a leaf a map does not name is false (CC 3.1.3.2)"),
    ("names_stands_on", "true | false | a map by selector: a row of the family signed under a root grant names in refs.also.stands_on the one acceptance of that grant it stands on, beside the bundle in refs.head; true for the reserved families whose duty a root confers (CC 2.4.1.1, CC 3.4.7)"),
    ("blind", "members minted as disclosures (CC 2.6.1.10): every free-text and other-authored member of a dsar|purge family, body.note always; [] for none|legal_hold; no fold, verdict or admission reads a listed member"),
    ("governance", "policy_row | none"),
    ("fold", "how the family's rows, read as a set, give a value: statements in the grammar of tools/fold_grammar.py, a part not stated taken from the default (formal/derivation/fold_text.tsv)"),
    ("count", "arms `selector => doors` joined by ` ; `, the first that holds deciding; a door is none | shut | POLICY_ROW[@source][!confers|!result] (formal/derivation/count_text.tsv)"),
    ("authorship", "authored | subject (authored, and the author is the attested key: iss == sub, positive only) | counted | arms `selector => authored|subject|counted` joined by ` ; `, on the count column's selector keys and `act` (group: the row is signed as the act of a roster under its consensus_protocol, by several statements over one payload, CC 2.6.1.9; own: one signer's own row; caller-supplied), the first that holds deciding; a counted row is several statements over one payload and its author is null (CC 2.6.1.3, CC 2.6.1.9; formal/derivation/authorship_text.tsv)"),
    ("second_signers", "[{role, member, when?, cc_ref}]: each role besides the author whose statement over the same payload the row accepts; member is the payload member that names the party, `sub` where the party is the attested key, `owner_of_sub` where it is the owner the owner-binding of the attested key names, or `gap` where the text names none; [] means only the author signs (formal/derivation/authorship_text.tsv)"),
    ("derived", "projection_id | none (the row must equal the named projection's rebuild; formal/derivation/confers_text.tsv)"),
    ("read_by", "the named answers that read the family's rows (state, stands, tally, may, audience, missing, owed, window), from the KX of its rule cells (tools/kx_translate.py over tools/kx_prelude.kx); `by` names each cell. A family with no cell of its own takes the default reading (state, stands) of the default fold and change: rule default, stated once and checked for none of the families it covers"),
    ("confers", "nothing | a permission (binds the signer: one row) | a seat (binds the placer and the holder: two consents) | an ending, with scope, conferrer, consent and ends (formal/derivation/family_shapes.tsv, confers_text.tsv)"),
    ("binds_segment", "placeholder → signer | subject | group | none; a segment of class literal, vocab or external names no key (formal/derivation/confers_text.tsv)"),
    ("evidence", "{claim_ids, refusal tokens}"),
])
CENSUS_MAP = {"placement": "2_placement", "signer_rule": "3_signer_rule", "subject_rule": "4_subject_rule",
              "cosign_rule": "5_cosign_rule", "body": "7_body", "freshness": "8_freshness", "lifecycle": "9_lifecycle",
              "replication": "10_replication", "projection": "11_projection", "erasure_route": "12_erasure_route",
              "governance": "13_governance", "evidence": "14_evidence"}
SUBKEYS = {"replication": ["tier", "audience", "non_recipient", "held"],
           "lifecycle": ["withdraws_by", "retraction_class", "supersedes", "expires", "rotation_on_removal"],
           "projection": ["table", "rebuild"],
           "subject_rule": ["kind", "cardinality", "must_be_registered", "for_key_id", "in_audience", "attested_party", "subject_blind"]}
TAGS = ("GAP", "PROSE", "GENERIC", "DATA")
HELD_SHUT = "none (held shut)"   # the census value of a family the code never stores
def tag_of(t):
    """The census writes a source tag as the first token: GAP:, PROSE:, GENERIC:, DATA:. Returns (tag, rest)."""
    m = re.match(r"^(GAP|PROSE|GENERIC|DATA)\s*:?\s*(.*)$", t.strip(), re.S)
    return (m.group(1), m.group(2).strip()) if m else (None, t.strip())
def head_of(t):
    """The closed value at the front of a cell: up to the first ' (' (a space before the parenthesis, so
    cohort_plus_subjects(full) keeps its qualifier), ';', ' via ', ' @ ' or ' on release'."""
    h = re.split(r"\s+\(|;| on release| via | @ ", t, 1)[0].strip().rstrip(".,")
    return h or None
def split_top(t, sep):
    """Split on sep outside parentheses and braces."""
    out, depth, cur = [], 0, ""
    for ch in t:
        if ch in "({[": depth += 1
        elif ch in ")}]": depth = max(0, depth - 1)
        if ch == sep and depth == 0: out.append(cur); cur = ""
        else: cur += ch
    out.append(cur)
    return [x.strip() for x in out if x.strip()]
def slices(t):
    """s2:/s3: segments (an unmerged slice's value) split out of a sub-value, at the top level only."""
    out, keep = {}, []
    for seg in split_top(t.replace(" ;", ";"), ";"):
        m = re.match(r"^(s[23])\s*:\s*(.+)$", seg)
        if m: out[m.group(1)] = m.group(2).strip()
        else: keep.append(seg)
    return out, "; ".join(keep)
def arms(t):
    """A per-arm value: 'by cohort_scope: a -> x; b -> y' or 'leaf: rule; leaf2: rule2' (split at the top level)."""
    body = re.sub(r"^by cohort_scope:\s*", "", t).replace(" ;", ";")
    segs = split_top(body, ";")
    if "->" in body:
        d = OrderedDict()
        for arm in segs:
            m = re.match(r"\s*([a-z_]+)\s*->\s*(.+)$", arm)
            if m: d[m.group(1)] = m.group(2).strip()
        return d or None
    if len(segs) >= 2 and all(re.match(r"^[a-z_/]+:\s*\S", x) for x in segs):
        d = OrderedDict()
        for x in segs:
            k, v = x.split(":", 1); d[k.strip()] = v.strip()
        return d
    if any(re.match(r"^([a-z_]+) leaf:\s*\S", x) or x.startswith("other leaves ") for x in segs):
        d = OrderedDict()
        for x in segs:
            m = re.match(r"^([a-z_]+) leaf:\s*(.+)$", x)
            if m: d[m.group(1)] = m.group(2).strip()
            elif x.startswith("other leaves "): d["other"] = x[len("other leaves "):].strip()
            else: return None
        return d
    return None
def leaf(t):
    """One sub-value: {value, source, note, closed, alternatives, arms, s2, s3}. The tag decides the source;
    a closed value after a GAP or PROSE tag is kept (the de-facto or target value, not nothing); nothing is
    cut: `value` is the whole reading, `closed` its head, `alternatives` the set when the cell lists several."""
    t = t.strip()
    tag, rest = tag_of(t)
    src = {"GAP": "gap", "PROSE": "prose", "GENERIC": "generic", "DATA": "code-v61", None: "code-v61"}[tag]
    if t.startswith("any of {"):
        m = re.match(r"any of \{([^}]*)\}", t)
        return {"value": [x.strip() for x in m.group(1).split(",")], "source": "gap", "note": t}
    if tag is None and re.search(r"\bGAP\b", rest): src = "mixed"
    if tag is None and re.search(r"\bPROSE\b", rest): src = "mixed" if src == "mixed" else "prose"
    sl, rest2 = slices(rest)
    if tag == "GAP" and rest.startswith("on release"):
        out = {"value": None, "source": "gap", "note": rest}; out.update(sl); return out
    if re.match(r"^federation only\b", rest2): rest2 = "federation (capacity never local)"
    a = arms(rest2)
    alts = [x.strip() for x in rest2.split(" | ")] if " | " in rest2 and not a else None
    closed = head_of(rest2) if rest2 else None
    if src == "gap" and closed and closed.lower() in ("none", "no per-family constraint", "nothing"): closed = None
    out = {"value": a if a else (alts if alts else (rest2 if rest2 else None)), "source": src}
    if closed and out["value"] != closed: out["closed"] = closed
    if a and src == "prose": out["source"] = "code-v61"   # per-leaf closed values are closed
    if rest and rest != out["value"]: out["note"] = rest
    out.update(sl)
    return out
def cell(col, text):
    t = (text or "").strip()
    if not t or t in ("—", "-"): return {"value": None, "source": "gap"}
    keys = SUBKEYS.get(col)
    if keys and (" | " in t or re.match(r"^(%s):" % "|".join(keys), t)):
        sub, order, cur = OrderedDict(), [], None
        for part in [x.strip() for x in t.split(" | ")]:
            m = re.match(r"^([a-z_]+):\s*(.*)$", part, re.S)
            if m and m.group(1) in keys: cur = m.group(1); sub[cur] = m.group(2); order.append(cur)
            elif cur is None: cur = keys[0]; sub[cur] = part; order.append(cur)
            else: sub[cur] = sub[cur] + " | " + part   # an alternative of the field before, not a new field
        parts = OrderedDict((k, leaf(v)) for k, v in sub.items())
        for k, v in parts.items():   # a sub-field's value is its closed head when the reading is one value with a note
            if isinstance(v.get("value"), str) and v.get("closed") and v["closed"] != v["value"]:
                v["note"] = v["value"]; v["value"] = v.pop("closed")
        srcs = {v["source"] for v in parts.values()}
        return {"value": OrderedDict((k, v["value"]) for k, v in parts.items()), "source": srcs.pop() if len(srcs) == 1 else "mixed", "parts": parts}
    if col == "freshness": return freshness(t)
    if col == "signer_rule": return signer(t)
    if col == "evidence": return evidence(t)
    return leaf(t)
def freshness(t):
    tag, rest = tag_of(t)
    out = leaf(t)
    if tag == "GENERIC" or "future-skew" in rest:
        out["value"] = {"judged_at": "receipt", "W": None}
        if tag == "GENERIC": out["source"] = "generic"
    elif re.search(r"\bW\b", rest):
        m = re.search(r"W\s*=\s*(\d+)\s*(h|d|s)\b", rest)
        W = int(m.group(1)) * {"h": 3600, "d": 86400, "s": 1}[m.group(2)] if m else None
        out["value"] = {"judged_at": "signed_instant_with_W", "W": W if W is not None else rest}
    return out
EMITTER_RULES = [  # (regex over the signer text, class); the same vocabulary build_transitions.py maps to role tokens
    (r"none \(held shut\)", "shut"),
    (r"seat_role\(([\w:]+)\)", "seat:{}"),
    (r"identity_type contains (\w+)", "substrate:{}"),
    (r"roster_member|\bcosign|holder quorum|\bquorum\b", "roster"),
    (r"\bsteward\b", "steward"),
    (r"owner_of_subject|owner_of\(|\bminter\b|\bowner\b", "owner"),
    (r"any_registered", "person"),
    (r"\bself\b", "self"),
]
def emitter_class(cell):
    """Who writes the family's rows, as a class the tier table can be read off (CC#203): derived from the
    signer rule's closed text; None with source gap where the rule itself is a gap."""
    v = cell.get("value") if isinstance(cell, dict) else cell
    if isinstance(v, dict): v = v.get("who")
    raw = " | ".join(map(str, v)) if isinstance(v, list) else (str(v) if v is not None else "")
    closed = cell.get("closed") if isinstance(cell, dict) else None
    classes = set()
    for text in (closed, raw):  # the closed head first; the raw cell only where the head names no emitter
        for pat, cls in EMITTER_RULES:
            for m in re.finditer(pat, text or ""):
                classes.add(cls.format(m.group(1)) if "{}" in cls else cls)
        if classes:
            break
    if not classes:
        return {"value": None, "source": "gap", "note": "signer rule names no emitter"}
    return {"value": "|".join(sorted(classes)), "source": "derived"}
def signer(t):
    tag, rest = tag_of(t)
    out = leaf(t)
    m = re.match(r"^([^;]*?)\s+x\s+(.*?)\s+x\s+\{([^}]*)\}(.*)$", rest, re.S)
    if m:
        who = m.group(1).strip()
        out["value"] = {"who": [w.strip() for w in who.split(" | ")] if " | " in who else who,
                        "via": m.group(2).strip(), "conditions": [c.strip() for c in m.group(3).split(",") if c.strip()]}
        q = m.group(4).strip(" ;")
        if q: out["qualifier"] = q
    return out
def evidence(t):
    out = leaf(t)
    d = OrderedDict()
    for m in re.finditer(r"(\d+ nsproc|door claims|door tokens|generic tokens|nsproc)\s*:\s*([^;]+)", t):
        k = m.group(1); vals = [x.strip() for x in re.split(r"[,/]", m.group(2)) if x.strip()]
        n = re.match(r"(\d+) nsproc", k)
        if n: d["nsproc"] = vals; d["n_nsproc"] = int(n.group(1))
        else: d[k.replace(" ", "_")] = vals
    if d: out["value"] = d
    return out
def reference_code(t):
    t = (t or "").strip()
    if not t or t.lower().startswith("none"): return None
    refs = []
    for m in re.finditer(r"\{family:\s*(.+?),\s*standing:\s*(.+?),\s*same_group:\s*([^}]+?)\}(?:\s*@\s*([^;]+))?", t):
        refs.append({"family": m.group(1).strip(), "standing": m.group(2).strip(), "same_group": m.group(3).strip(), "where": (m.group(4) or "").strip()})
    return refs or [{"raw": t}]
def polarity_census(t):
    m = re.search(r"alias\s*->\s*([^)]+)\)", t or "")
    if m: return m.group(1).strip()
    tag, rest = tag_of(t or "")
    return head_of(rest) if rest else None

CARD_HOME, CARD_QUOTE = "CC 8.10", "=card"


class _CardHome(str):
    """The span of the family cards (CC 8.10) as a home: it holds exactly the marker `=card`. A row of a text
    table whose value no prose states any longer names the cards as its home with that marker in place of a
    quote: the card the build prints from the row is the document's statement of the value (CC 8.10)."""
    def __contains__(self, quote):
        return quote == CARD_QUOTE


def section_span(ref):
    """The text of a Constitution section with its subsections, by its number; None when no heading carries it."""
    if ref == CARD_HOME: return _CardHome()
    m = re.fullmatch(r"CC (\d+(?:\.\d+)*)", ref or "")
    if not m: return None
    num = m.group(1)
    for path in sorted(glob.glob(os.path.join(ROOT, "constitution", f"part_{num.split('.')[0]}_*.md"))):
        lines = open(path, encoding="utf-8").read().split("\n")
        start = None
        for i, l in enumerate(lines):
            h = re.match(r"#{1,6} (\d+(?:\.\d+)*)(?= |$)", l)
            if not h: continue
            if start is None:
                if h.group(1) == num: start = i
            elif not h.group(1).startswith(num + "."):
                return "\n".join(lines[start:i])
        if start is not None: return "\n".join(lines[start:])
    return None


def fam_match(fam, pat):
    """A pattern is a family's name, or a stem ending in a colon that takes every family under it."""
    return fam == pat or (pat.endswith(":") and fam.startswith(pat))


def departure_reasons(rows, default):
    """Give every departing cell its reason, or refuse.

    A reason says when a family leaves the default row and why, and names the cells it moves. Three bases:
    text (a section of the Constitution and words that stand in it), census (the family is not built, so
    its cells are unread), build (a fact of the store that no rule turns on). The check runs both ways:
    a departing cell with no reason fails unless it is listed open with its question, and a cell a reason
    names that sits on the default fails too, so a reason cannot outlive what it explained.
    """
    spec = json.load(open(REASONS, encoding="utf-8"), object_pairs_hook=OrderedDict)
    errs, claims, seen = [], OrderedDict(), set()
    census_place = lambda r: (r["placement"].get("code") or r["placement"]).get("value")   # the census reading, under a value the text gives
    unbuilt = {r["family"] for r in rows if census_place(r) is None or str(census_place(r)).startswith("none (held shut")}
    for rs in spec["reasons"]:
        rid = rs.get("id", "?")
        if rid in seen: errs.append(f"{rid}: named twice")
        seen.add(rid)
        for k in ("when", "why", "basis"):
            if not rs.get(k): errs.append(f"{rid}: no {k}")
        if rs.get("basis") not in BASES: errs.append(f"{rid}: basis is one of {', '.join(BASES)}")
        if "enforced" in rs and (rs["enforced"] is not False or rs.get("basis") != "text"):
            errs.append(f"{rid}: enforced is stated only as false, and only where the text gives the rule")
        if ("cell" in rs or "build_note" in rs) and rs.get("enforced") is not False:
            errs.append(f"{rid}: cell and build_note describe a rule the build does not enforce; state enforced false or remove them")
        if "cell" in rs and rs["cell"] != "build":
            errs.append(f"{rid}: cell is stated only as build, where the cell records the build and not the text")
        if rs.get("cell") == "build" and rs.get("value"):
            errs.append(f"{rid}: a reason whose cell records the build fixes no value")
        if rs.get("basis") == "text":
            span = section_span(rs.get("cc_ref"))
            if span is None: errs.append(f"{rid}: {rs.get('cc_ref')} is not a section of the Constitution")
            elif not rs.get("quote") or rs["quote"] not in span: errs.append(f"{rid}: the quoted words do not stand in {rs.get('cc_ref')}")
        moves = rs.get("moves") or OrderedDict()
        if rs.get("premise") == "unbuilt":
            moves = OrderedDict((col, sorted(f for f in unbuilt if col in next(r for r in rows if r["family"] == f)["departs"])) for col in default)
        elif rs.get("premise") == "typed_view":   # every built family whose table rebuilds from its rows
            moves = OrderedDict([("projection", sorted(r["family"] for r in rows if r["family"] not in unbuilt and "projection" in r["departs"]
                                                       and isinstance(r["projection"].get("value"), dict) and r["projection"]["value"].get("rebuild") == "byte_equal"))])
        elif rs.get("premise"):
            errs.append(f"{rid}: unknown premise {rs['premise']}")
        if not any(moves.values()): errs.append(f"{rid}: moves nothing")
        for col, pats in moves.items():
            if col not in default: errs.append(f"{rid}: {col} is not a column of the default row"); continue
            for pat in pats:
                hit = [r for r in rows if fam_match(r["family"], pat)]
                if not hit: errs.append(f"{rid}: {pat} names no family")
                for r in hit:
                    if r["family"] in unbuilt and rs.get("premise") != "unbuilt":
                        errs.append(f"{rid}: {r['family']} is not built; its cells are unread and take no other reason")
                    elif col not in r["departs"]:
                        errs.append(f"{rid}: {r['family']} is said to leave the default in {col} and sits on it")
                    else:
                        claims.setdefault((r["family"], col), []).append(rid)
        for path, want in (rs.get("value") or {}).items():   # the reason fixes the cell's value, not only that it moves
            col, _, sub = path.partition(".")
            for pat in moves.get(col, []):
                for r in rows:
                    if not fam_match(r["family"], pat): continue
                    v = r[col].get("value")
                    got = v.get(sub) if sub and isinstance(v, dict) else v
                    if got != want: errs.append(f"{rid}: {r['family']} {path} is {got!r}, and the reason gives {want!r}")
    opens = OrderedDict()
    for o in spec.get("open", []):
        k = (o.get("family"), o.get("column"))
        if not o.get("question"): errs.append(f"open {k[0]} {k[1]}: no question")
        if k in opens: errs.append(f"open {k[0]} {k[1]}: listed twice")
        opens[k] = o.get("question")
    departing = {(r["family"], col) for r in rows for col in r["departs"]}
    for k in sorted(departing):
        if k in claims and k in opens: errs.append(f"{k[0]} {k[1]}: has a reason and is listed open; remove one")
        if k not in claims and k not in opens: errs.append(f"{k[0]} {k[1]}: leaves the default with no reason; give one or list it open with its question")
    for k in opens:
        if k not in departing: errs.append(f"open {k[0]} {k[1]}: no longer leaves the default; remove the line")
    return spec, claims, opens, errs


def reasons_md(spec, claims, opens, rows, default):
    cells = Counter(rid for v in claims.values() for rid in v)
    fams = {}
    for (f, c), v in claims.items():
        for rid in v: fams.setdefault(rid, OrderedDict()).setdefault(c, []).append(f)
    out = ["# Why and when a family leaves the default row", "",
           "Generated by `tools/build_family_model.py` from `formal/derivation/departure_reasons.json`; do not edit.", "",
           spec["reading"], ""]
    for rs in spec["reasons"]:
        rid = rs["id"]
        out += [f"## {rs['title']}", "", f"**When.** {rs['when']}", "", f"**Why.** {rs['why']}", ""]
        if rs["basis"] == "text":
            out += [f"**Text.** {rs['cc_ref']}: \"{rs['quote']}\"", ""]
            if rs.get("enforced") is False:
                out += ["**Build.** The text states this and the pinned build does not enforce it; the cell records the "
                        + ("build" if rs.get("cell") == "build" else "text") + "." + (" " + rs["build_note"] if rs.get("build_note") else ""), ""]
        else: out += [f"**Basis.** {'The family is not built; the census read nothing.' if rs['basis'] == 'census' else 'A fact of the store; no rule turns on it.'}", ""]
        out += ["| column | families |", "|---|---|"]
        out += [f"| {c} | {', '.join('`' + f + '`' for f in fs)} |" for c, fs in fams.get(rid, {}).items()]
        out += [""]
    if opens:
        out += ["## Open", "", "Cells that leave the default with no reason yet, each with the question that would give it one.", "",
                "| family | column | question |", "|---|---|---|"]
        out += [f"| `{f}` | {c} | {q} |" for (f, c), q in opens.items()]
        out += [""]
    return "\n".join(out)


def placement_text(default_value):
    """Where a row goes when its family states no placement of its own (formal/derivation/placement_text.tsv).

    One `default` row: the placements a family's rows may take, with the sentence that leaves the choice to
    the emitter. `scope` rows: the audience of each `cohort_scope`, each quoting its line of the CC 5.2 table.
    `reach` rows: whom a row reaches because it names them. `moves` rows: when a row in a peer's audience moves to it. `copy` rows: whose audience a row joins because
    another row names it. Returns (table, errors); every quote stands in its section, the scope rows cover the
    seven scopes once each, and their placements are exactly the default's.
    """
    rows = list(csv.DictReader([l for l in open(PLACEMENT_TEXT, encoding="utf-8").read().split("\n") if l and not l.startswith("#")], delimiter="\t", quoting=csv.QUOTE_NONE))
    errs, out = [], OrderedDict([("source", "formal/derivation/placement_text.tsv"), ("default", None), ("scopes", []), ("reach", []), ("moves", []), ("copy", [])])
    seen = Counter()
    for r in rows:
        where = f"placement_text.tsv: {r['rule']} {r['when']}"
        span = section_span(r["cc_ref"])
        if span is None or not r["quote"] or r["quote"] not in span:
            errs.append(f"{where}: the quoted words do not stand in {r['cc_ref']}"); continue
        if r["rule"] == "default":
            if out["default"] is not None: errs.append(f"{where}: the default is stated once")
            out["default"] = OrderedDict([("value", [x.strip() for x in r["placement"].split(" | ")]), ("chosen_by", r["audience"]), ("cc_ref", r["cc_ref"]), ("quote", r["quote"])])
        elif r["rule"] == "scope":
            names = [x.strip() for x in r["when"].split(",")]
            room = r["public_room"] == "yes"
            for x in names:
                if x not in SCOPES or "`" + x + "`" not in r["quote"]: errs.append(f"{where}: {x} is not a scope the quoted line names")
                elif not room: seen[x] += 1
            for k in ("audience", "outside"):
                if r[k] not in r["quote"]: errs.append(f"{where}: the {k} is not in the quoted line")
            out["scopes"].append(OrderedDict([("cohort_scope", names), ("public_room", room), ("placement", r["placement"]), ("audience", r["audience"]),
                                              ("outside", r["outside"]), ("cc_ref", r["cc_ref"])]))
        elif r["rule"] in ("reach", "moves", "copy"):
            if r["audience"] in ("", "-"): errs.append(f"{where}: no statement")
            out[r["rule"]].append(OrderedDict([("when", r["when"]), ("statement", r["audience"]), ("cc_ref", r["cc_ref"]), ("quote", r["quote"])]))
        else:
            errs.append(f"{where}: the rule is one of default, scope, reach, moves, copy")
    if out["default"] is None: errs.append("placement_text.tsv: no default row")
    elif out["default"]["value"] != default_value:
        errs.append("placement_text.tsv: the default's placements are not those of the default row (formal/derivation/family_default_row.json)")
    for x in SCOPES:
        if seen[x] != 1: errs.append(f"placement_text.tsv: the scope {x} has {seen[x]} audience rows; it has one")
    if out["default"] and {s["placement"] for s in out["scopes"]} != set(out["default"]["value"]):
        errs.append("placement_text.tsv: the placements of the scope rows are not exactly the default's")
    return out, errs


SHAPES = os.path.join(ROOT, "formal/derivation/family_shapes.tsv")
NAMES_HEAD_TEXT = {}
for _l in open(os.path.join(ROOT, "formal/derivation/names_head_text.tsv"), encoding="utf-8").read().split("\n"):
    if _l and not _l.startswith("#") and not _l.startswith("family\t"):
        _f, _sel, _v, _w = _l.split("\t")
        if _v not in ("roster", "standing", "none", "by_placement"): raise SystemExit(f"names_head_text.tsv: {_f}: unknown value {_v}")
        NAMES_HEAD_TEXT.setdefault(_f, []).append((_sel, _v, _w))
SHAPE_OF = {l.split("\t")[0]: l.split("\t")[1] for l in open(SHAPES, encoding="utf-8").read().split("\n")
            if l and not l.startswith("#") and not l.startswith("family\t")}
def names_head(row):
    """Which head a row of the family names in refs.head (CC 2.4.1.1, CC 2.7.8), from where it is placed and who signs it.
    roster: placed only at a room's or a family's scope, so it names that roster's version. standing: signed under a seat, a grant
    or a binding and placed outside any roster, so it names the record that seats the signer. none: a person's own row, exercising
    no conferred standing. by_placement: the family is placed at several scopes; at a room or family it names that roster's version,
    and at self, at federation or in the commons, where there is no roster, it names none unless its signer signs as someone's node,
    agent or delegate or under a grant, and then that binding, delegation or bundle."""
    pl = row["placement"].get("value"); sr = row["signer_rule"].get("value")
    places = set(pl) if isinstance(pl, list) else ({head_of(pl)} if isinstance(pl, str) else set())
    places = {head_of(x) if isinstance(x, str) else x for x in places}
    who = sr.get("who") if isinstance(sr, dict) else sr
    who = " ".join(who) if isinstance(who, list) else (who or "")
    seated = any(t in who for t in ("seat_role", "identity_type contains", "holder", "steward", "minter", "owner_of"))
    rooms = {"targeted_room", "targeted_family"}
    if not places or pl is None or (isinstance(pl, str) and pl.startswith("none")):
        v, why = None, "the placement cell is unread or the family is never stored"
    elif places <= rooms: v, why = "roster", "placed only at a room's or a family's scope"
    elif places & rooms: v, why = "by_placement", "placed at a room or a family and elsewhere"
    elif seated or "roster_member" in who: v, why = "standing", "signed under a seat, a grant or a binding, outside any roster"
    else: v, why = "none", "a row of its signer's own, exercising no conferred standing"
    return {"value": v, "source": "derived" if v else "gap", "from": "placement, signer_rule", "note": why, "cc_ref": "CC 2.4.1.1"}


# What a holder other than the signer drops when a row of the family is withdrawn (CC 6.1.5 N5, CC 2.4.1.1): content is N5's object;
# a claim leaves every audience; a consent or a door is structure, kept and read as retracted, since past acts are judged against it.
DESCENDS = {"content": "bytes_and_words", "claim": "row", "consent": "nothing", "door": "nothing", "consent+door": "nothing", "none fits": "nothing"}
# Six read-only columns on withdrawal and standing (CC 2.4.1.1, CC 3.1.5, CC 4.5.5, CC 3.1.3.2, CC 3.4.7): each cell is derived by a stated rule from
# the other columns, and a row of formal/derivation/standing_text.tsv replaces it for one family or one leaf, quoting its sentence.
STANDING_TEXT = os.path.join(ROOT, "formal/derivation/standing_text.tsv")
STANDING_VALUES = OrderedDict([("subject_may_withdraw", ("true", "false")), ("accountability_record", ("true", "false")),
                               ("may_carry_under", ("true", "false")), ("standing_act", ("offer", "end", "acceptance", "exercise", "none")),
                               ("room_content", ("true", "false")), ("names_stands_on", ("true", "false"))])
# The two branches of a names_head cell that reads by_placement, as data: where the row is placed decides which head it names.
# Each branch takes its sentences from the `_meta` rule of standing_text.tsv it names, so a branch with no quoted rule fails the build.
NAMES_HEAD_BRANCHES = (
    OrderedDict([("placed_at", ["targeted_room", "targeted_family"]), ("names", "roster"), ("rule", "names_head.by_placement.room_or_family")]),
    OrderedDict([("placed_at", ["self_collective", "commons"]), ("names", "standing"), ("when", "the signer signs under a standing: the binding, the delegation or the bundle"),
                 ("otherwise", "none"), ("rule", "names_head.by_placement.elsewhere")]),
)
STANDING_RANK = ("derived", "quote", "ruling", "open")   # a cell of several selectors takes the last of these any selector has


def standing_text():
    """The rows of standing_text.tsv, by column, and the rules and notes of its `_meta` rows. A quote stands verbatim in its section;
    a ruling carries its note; an open row carries the sentence the text would need and no value. Returns (rows, meta, errors)."""
    rows, meta, errs = {c: [] for c in STANDING_VALUES}, OrderedDict(), []
    for r in tsv_rows(STANDING_TEXT):
        where = f"standing_text.tsv: {r['column']} {r['family']} {r['selector']}"
        if r["source"] not in ("quote", "ruling", "open"): errs.append(f"{where}: the source is one of quote, ruling, open"); continue
        if not r["words"]: errs.append(f"{where}: no words"); continue
        if r["source"] == "quote" or r["cc_ref"]:
            span = section_span(r["cc_ref"])
            if span is None: errs.append(f"{where}: {r['cc_ref']} is no section"); continue
            if r["source"] == "quote" and r["words"] not in span: errs.append(f"{where}: the quoted words do not stand in {r['cc_ref']}"); continue
        if r["column"] == "_meta":
            if r["source"] != "quote": errs.append(f"{where}: a rule or a note quotes its sentence"); continue
            m = meta.setdefault(r["family"], OrderedDict([("statement", r["value"]), ("cites", [])]))
            if m["statement"] != r["value"]: errs.append(f"{where}: one key, two statements"); continue
            m["cites"].append(OrderedDict([("cc_ref", r["cc_ref"]), ("quote", r["words"])]))
            continue
        if r["column"] not in STANDING_VALUES: errs.append(f"{where}: unknown column"); continue
        if r["source"] == "open":
            if r["value"] != "-": errs.append(f"{where}: an open row states no value"); continue
            v = None
        elif r["value"] not in STANDING_VALUES[r["column"]]: errs.append(f"{where}: unknown value {r['value']}"); continue
        else: v = {"true": True, "false": False}.get(r["value"], r["value"])
        if r["selector"] != "*" and not re.fullmatch(r"(leaf|act)=[a-z_|]+", r["selector"]): errs.append(f"{where}: the selector is * or leaf=NAME or act=NAME"); continue
        rows[r["column"]].append(OrderedDict([("family", r["family"]), ("selector", r["selector"]), ("value", v), ("source", r["source"]),
                                              ("cc_ref", r["cc_ref"]), ("words", r["words"]), ("used", False)]))
    return rows, meta, errs


def standing_cells(row, text):
    """The six cells of one family; room_content and names_stands_on are false unless a row of the table says otherwise. Derived first: subject_may_withdraw is true, and false on each arm the authorship column gives
    as counted (CC 2.4.1.1 rule 0); accountability_record and may_carry_under are false; standing_act is end where the confers cell
    is an ending, acceptance where its role is acceptance, else exercise where names_head is roster, standing or by_placement, none
    where it is none, and open where names_head is unread. Then the family's rows of standing_text.tsv replace the derived value,
    for the family (selector *) or leaf by leaf."""
    fam, out = row["family"], OrderedDict()
    au, nh, cf = row["authorship"], row["names_head"].get("value"), row["confers"].get("value")
    for col in STANDING_VALUES:
        if col == "subject_may_withdraw":
            arms = [a for a in au.get("arms") or [] if a["value"] == "counted"]
            if au.get("value") == "counted": v, why = False, "every row of the family is counted: rules 1 to 4 never reach a counted row"
            elif arms:
                v = OrderedDict([(a["when"], False) for a in arms] + [("*", True)])
                why = "false on the arms the authorship column gives as counted; true for a row one party authors"
            else: v, why = True, "a named party may retire a row about itself; the family is on no kept list"
            c = OrderedDict([("value", v), ("source", "derived"), ("from", "authorship"), ("note", why), ("cc_ref", "CC 2.4.1.1")])
        elif col == "accountability_record":
            c = OrderedDict([("value", False), ("source", "derived"), ("note", "no sentence keeps the family's rows from their signer's owner"), ("cc_ref", "CC 3.1.5")])
        elif col == "may_carry_under":
            c = OrderedDict([("value", False), ("source", "derived"), ("note", "no row of the family is a deputy's edge"), ("cc_ref", "CC 4.5.5")])
        elif col == "room_content":
            c = OrderedDict([("value", False), ("source", "derived"), ("note", "the family is not among those CC 3.1.3.2 names as a room's content"), ("cc_ref", "CC 3.1.3.2")])
        elif col == "names_stands_on":
            c = OrderedDict([("value", False), ("source", "derived"), ("note", "no root confers the family's duty, so no row of it stands on an acceptance of a root grant"), ("cc_ref", "CC 2.4.1.1")])
        else:
            act = lambda h: "none" if h == "none" else "exercise"
            if isinstance(cf, dict) and cf.get("relation") == "ending": v, src, frm, why = "end", "derived", "confers", "the family's rows end a standing"
            elif isinstance(cf, dict) and cf.get("role") == "acceptance": v, src, frm, why = "acceptance", "derived", "confers", "the family's row is the acceptor's own consent"
            elif nh is None: v, src, frm, why = None, "open", "names_head", "the names_head cell is unread, so nothing says whether a row of the family exercises a standing"
            elif isinstance(nh, dict): v, src, frm, why = OrderedDict((k, act(h)) for k, h in nh.items()), "derived", "names_head", "by the head each selector names"
            else: v, src, frm, why = act(nh), "derived", "names_head", ("a row of its signer's own, exercising no conferred standing" if nh == "none" else f"its rows name a head ({nh})")
            c = OrderedDict([("value", v), ("source", src), ("from", frm), ("note", why), ("cc_ref", "CC 2.4.1.1")])
        mine = [t for t in text[col] if fam_match(fam, t["family"])]
        for t in mine: t["used"] = True
        if mine:
            derived = c["value"]
            if len(mine) == 1 and mine[0]["selector"] == "*":
                t = mine[0]
                c = OrderedDict([("value", t["value"]), ("source", t["source"]), ("from", "formal/derivation/standing_text.tsv")] +
                                ([("cc_ref", t["cc_ref"])] if t["cc_ref"] else []) +
                                [("quote" if t["source"] == "quote" else ("note" if t["source"] == "ruling" else "needs"), t["words"]), ("derived", derived)])
            else:
                if any(t["selector"] == "*" for t in mine) or len({t["selector"] for t in mine}) != len(mine):
                    raise SystemExit(f"standing_text.tsv: {col} {fam}: a family takes one * row, or one row a selector")
                c = OrderedDict([("value", OrderedDict((t["selector"], t["value"]) for t in mine)),
                                 ("source", max((t["source"] for t in mine), key=STANDING_RANK.index)), ("per_selector", True),
                                 ("from", "formal/derivation/standing_text.tsv"),
                                 ("sources", OrderedDict((t["selector"], t["source"]) for t in mine)),
                                 ("cc_ref", OrderedDict((t["selector"], t["cc_ref"]) for t in mine if t["cc_ref"])),
                                 ("words", OrderedDict((t["selector"], t["words"]) for t in mine)), ("derived", derived)])
        elif isinstance(c["value"], dict): c["per_selector"] = True
        out[col] = c
    return out


CONFERS_TEXT = os.path.join(ROOT, "formal/derivation/confers_text.tsv")
RELATION = {"signer": "permission", "signer+holder": "seat", "body+holder": "seat"}   # formal/KERNEL.md 5: one voice bound is one row, two are a seat
SEAT_PARAMS = ("role", "scope", "roster", "holders", "conferrer", "consent", "proposal", "ends", "revoker", "single", "closes", "door")
BLOCKED = (("conferrer", "unstated"), ("signer", "unstated"), ("role", "a term on an offer"))   # the shapes table's own `cannot run` for a consent


def tsv_rows(path):
    return list(csv.DictReader([l for l in open(path, encoding="utf-8").read().split("\n") if l and not l.startswith("#")], delimiter="\t", quoting=csv.QUOTE_NONE))


def conferral_columns(fams, reg):
    """The `confers`, `binds_segment` and `derived` cells, from formal/derivation/family_shapes.tsv, the registry's segment classes and
    formal/derivation/confers_text.tsv. A consent family's `confers` is its shape's parameters, each with the source the shapes
    table gives it; a family whose shapes row says confers=nothing takes that sentence; a claim or content family takes the one
    default. Returns ({family: cell}, {family: cell}, {family: cell}, errors)."""
    errs, conf, segs = [], OrderedDict(), OrderedDict()
    shapes = OrderedDict()
    for r in tsv_rows(SHAPES):
        p = [tuple(x.split("=", 1)) for x in r["parameters"].split(" ; ")] if r["parameters"] else []
        s = [tuple(x.split(" <- ", 1)) for x in r["sources"].split(" ; ")] if r["sources"] else []
        if [k for k, _ in p] != [k for k, _ in s]: errs.append(f"family_shapes.tsv: {r['family']}: parameters and sources do not name the same things")
        shapes[r["family"]] = (r, OrderedDict(p), OrderedDict(s))
    if set(shapes) != set(fams): errs.append("family_shapes.tsv: its families are not the model's: " + ", ".join(sorted(set(shapes) ^ set(fams))))
    default, by_seg, by_class, stated, derived, armed = None, {}, {}, OrderedDict(), OrderedDict(), OrderedDict()
    for t in tsv_rows(CONFERS_TEXT):
        where = f"confers_text.tsv: {t['column']} {t['when']}"
        span = section_span(t["cc_ref"])
        if span is None or t["quote"] not in span: errs.append(f"{where}: the quoted words do not stand in {t['cc_ref']}"); continue
        src = OrderedDict([("cc_ref", t["cc_ref"]), ("quote", t["quote"])])
        if t["column"] == "confers" and t["when"].startswith("shape="):
            if default is not None: errs.append(f"{where}: the default is stated once")
            default = (set(t["when"][6:].split("|")), t["value"], src)
        elif t["column"] == "confers" and " => " in t["value"]:
            # an armed cell, in the count column's style: `selector => value ; ...`, the first arm that holds deciding
            if t["when"] not in fams: errs.append(f"{where}: no such family"); continue
            arms_ = []
            for seg in t["value"].split(" ; "):
                sel, _, val = seg.partition(" => ") if " => " in seg else ("*", "", seg)
                if sel != "*" and not re.fullmatch(r"[a-z_]+=[a-z_|]+", sel): errs.append(f"{where}: {sel} is not a selector"); break
                arms_.append(OrderedDict([("when", sel), ("value", val.strip())]))
            else:
                if arms_[-1]["when"] != "*": errs.append(f"{where}: an armed cell ends in a `*` arm")
                armed[t["when"]] = OrderedDict([("value", t["value"]), ("arms", arms_), ("source", "cc-table"), ("cc_ref", t["cc_ref"]),
                                                ("rule", "stated"), ("from", "formal/derivation/confers_text.tsv")])
        elif t["column"] == "confers":
            if t["when"] not in fams: errs.append(f"{where}: no such family"); continue
            k, _, v = t["value"].partition("=") if t["value"] != "nothing" else ("confers", "", "nothing")
            if k != "confers" and k not in SEAT_PARAMS: errs.append(f"{where}: {k} is not a seat parameter"); continue
            stated.setdefault(t["when"], OrderedDict())[k] = (v, f'quote:{t["cc_ref"]} "{t["quote"]}"')
        elif t["column"] == "binds_segment":
            if t["value"] not in ("signer", "subject", "group", "none"): errs.append(f"{where}: {t['value']} is not signer, subject, group or none"); continue
            if t["when"].startswith("class="): by_class[t["when"][6:]] = (t["value"], src)
            else:
                fam, _, ph = t["when"].rpartition(" ")
                if fam not in fams: errs.append(f"{where}: no such family")
                by_seg[(fam, ph)] = (t["value"], src)
        elif t["column"] == "derived":
            if t["when"] not in fams: errs.append(f"{where}: no such family"); continue
            derived[t["when"]] = OrderedDict([("value", t["value"]), ("source", "cc-table"), ("cc_ref", t["cc_ref"]), ("rule", "stated"), ("from", "formal/derivation/confers_text.tsv")])
        else: errs.append(f"{where}: the column is confers, binds_segment or derived")
    if default is None: errs.append("confers_text.tsv: no default for confers")
    for f, cell in armed.items():
        if f in stated: errs.append(f"confers_text.tsv: {f}: an armed cell and a plain one; state it once")
    for f in fams:
        if f not in shapes: continue
        r, P, S = shapes[f]
        here = "formal/derivation/family_shapes.tsv"
        for k, (v, src) in stated.get(f, {}).items():   # a parameter the shapes table does not state, from confers_text.tsv; never a copy
            if k in P: errs.append(f"confers_text.tsv: {f}: family_shapes.tsv already states {k}; remove the row"); continue
            P, S = OrderedDict(P, **{k: v}), OrderedDict(S, **{k: src})
        if f in armed:
            conf[f] = armed[f]; continue
        if "confers" in P:
            if r["shape"] in default[0]: errs.append(f"confers_text.tsv: {f}: a {r['shape']} takes the default; its row is a copy")
            m = re.match(r'^quote:(CC [\d.]+) "(.*)"$', S["confers"])
            if not m: errs.append(f"{f}: confers rests on a sentence, not {S['confers']}"); continue
            conf[f] = OrderedDict([("value", P["confers"]), ("source", "cc-table"), ("cc_ref", m.group(1)), ("rule", "stated"), ("from", "formal/derivation/confers_text.tsv")])
        elif "consent" in r["shape"].split("+") and r["binds"] not in ("", "-"):
            blocked = [f"{k}={v}" for k, v in BLOCKED if P.get(k) == v] + [f"{k} guessed" for k, v in S.items() if v == "guessed" and P.get(k) not in [b for _, b in BLOCKED]]
            if blocked:
                conf[f] = OrderedDict([("value", None), ("source", "gap"), ("from", here), ("note", "the shapes table cannot run this consent (" + "; ".join(blocked) + "): " + r["misfit"])])
                continue
            rel = "|".join(sorted({RELATION.get(b, "?") for b in r["binds"].split("|")}))
            v = OrderedDict([("relation", "ending" if P.get("role") == "ending" else rel), ("binds", r["binds"])])
            v.update((k, P[k]) for k in SEAT_PARAMS if k in P)
            if "binds" in P: v["binds_by_leaf"] = P["binds"]
            if "consent" not in v and r["binds"] == "signer":   # one voice bound: its own row is the consent
                v["consent"] = "same_row"; S = OrderedDict(S, consent=f"cell:{here}#{f}.binds")
            refs = sorted({m.group(1) for x in S.values() for m in [re.match(r'^quote:(CC [\d.]+) ', x)] if m})
            conf[f] = OrderedDict([("value", v), ("source", "cc-table"), ("cc_ref", refs), ("rule", "shape"), ("from", here),
                                   ("sources", OrderedDict((k, S[k]) for k in list(v) if k in S)), ("cells_from", sorted({here} | ({"formal/derivation/confers_text.tsv"} if f in stated else set())))])
        elif r["shape"] in default[0]:
            conf[f] = OrderedDict([("value", default[1]), ("source", "cc-table"), ("cc_ref", default[2]["cc_ref"]), ("rule", "default")])
        else:
            conf[f] = OrderedDict([("value", None), ("source", "gap"), ("from", here),
                                   ("note", f"a {r['shape']} family, and no sentence says what its rows confer")])
    classes = {x["prefix"]: x.get("segments", []) for x in reg.get("families", []) if isinstance(x, dict) and "prefix" in x}
    for f in fams:
        sg = classes.get(f)
        if sg is None: segs[f] = OrderedDict([("value", None), ("source", "gap"), ("note", "not in the registry")]); continue
        val, srcs, open_ = OrderedDict(), OrderedDict(), []
        for s in sg:
            c, ph = s["class"], s["segment"]
            if c in ("literal", "wildcard"):
                if c not in by_class: open_.append(ph)
                continue
            if (f, ph) in by_seg: val[ph], src = by_seg[(f, ph)]
            elif c in by_class: val[ph], src = by_class[c]
            else: open_.append(ph); continue
            srcs[ph] = src["cc_ref"]
        if open_:
            segs[f] = OrderedDict([("value", None), ("source", "gap"), ("parts", val), ("note", "no sentence says which key slot " + ", ".join(open_) + " holds")])
        else:
            segs[f] = OrderedDict([("value", val or "none"), ("source", "cc-table"), ("cc_ref", sorted(set(srcs.values())) or by_class["literal"][1]["cc_ref"]),
                                   ("rule", "stated" if any((f, p) in by_seg for p in val) else "class")])
    der = OrderedDict((f, derived.get(f) or OrderedDict([("value", None), ("source", "gap"), ("note", "no sentence says whether a row of this family equals a recomputation from other rows")])) for f in fams)
    return conf, segs, der, errs


AUTHORSHIP_TEXT = os.path.join(ROOT, "formal/derivation/authorship_text.tsv")
AUTHORSHIP_VALUES = ("authored", "subject", "counted", "gap")   # subject: authored, and the author is the attested key (iss == sub)
AUTHORSHIP_GAP_MAX = 0   # families whose authorship the text gives both ways with no selector to tell them; the number only falls
SECOND_SIGNERS_GAP_MAX = 0   # roles whose payload member the text does not name; the number only falls
SELECTOR_VALUE = r"[a-z_:{}]+(?:\|[a-z_:{}]+)*"
ACT_VALUES = ("group", "own")   # the `act` key: the act of a roster under its consensus_protocol (CC 2.6.1.9), or one signer's own row


def authorship_cells(stmts, rows, members, span=None):
    """The `authorship` and `second_signers` cells (CC 2.6.1.3, CC 2.6.1.9) from formal/derivation/authorship_text.tsv.

    authorship: arms `selector => authored|counted` in the style of the count column, the first that holds deciding; a family
    with no row is authored. A family whose count cell names a policy row, or is open, is listed either way, and a counted arm
    needs a count that is not none. second_signers: each role besides the author whose statement over the same payload the
    row accepts, with the payload member that names the party (`sub` for the attested key, `gap` where the text names none).
    Returns ({family: cell}, {family: cell}, errors)."""
    span = span or section_span
    errs, by = [], OrderedDict()
    fams = {r["family"]: r for r in rows}
    for i, s in enumerate(stmts):
        where = f"authorship_text.tsv row {i + 1}: {s.get('family')} {s.get('column')}"
        if s.get("family") not in fams: errs.append(f"{where}: no such family"); continue
        if s.get("column") not in ("authorship", "second_signers"): errs.append(f"{where}: the column is authorship or second_signers"); continue
        sel = s.get("selector") or ""
        if sel != "*":
            for t in sel.split(" & "):
                mt = re.fullmatch(r"([a-z]+)=(%s)" % SELECTOR_VALUE, t)
                if not mt or mt.group(1) not in COUNT_KEYS: errs.append(f"{where}: {t!r} is not a test on one of {', '.join(COUNT_KEYS)}")
                elif mt.group(1) == "act" and not set(mt.group(2).split("|")) <= set(ACT_VALUES): errs.append(f"{where}: {t!r}: an act is one of {', '.join(ACT_VALUES)}")
        sp = span(s.get("cc_ref"))
        if sp is None or not s.get("quote") or s["quote"] not in sp: errs.append(f"{where}: the quoted words do not stand in {s.get('cc_ref')}"); continue
        if s["column"] == "authorship" and s.get("value") not in AUTHORSHIP_VALUES:
            errs.append(f"{where}: {s.get('value')!r} is not one of {', '.join(AUTHORSHIP_VALUES)}"); continue
        if s["column"] == "second_signers":
            m = re.fullmatch(r"([a-z_]+)=([a-z_]+)", s.get("value") or "")
            if not m: errs.append(f"{where}: {s.get('value')!r} is not role=member"); continue
            if m.group(2) not in ("sub", "owner_of_sub", "gap") and m.group(2) not in members:
                errs.append(f"{where}: {m.group(2)} is not sub, owner_of_sub, gap or a member the text names"); continue
        by.setdefault(s["family"], OrderedDict()).setdefault(s["column"], []).append(s)
    auth, second = OrderedDict(), OrderedDict()
    def has_count(r):
        cnt = r.get("count", {})
        return cnt.get("source") == "gap" or (cnt.get("value") not in (None, "none"))
    def leaf_families(fam, sel):   # a stem (`x:*`) names its leaf families by leaf; their own count cells hold the count
        if not fam.endswith(":*"): return None
        m = re.search(r"(?:^| & )leaf=(%s)" % SELECTOR_VALUE, sel)
        return [fam[:-1] + v for v in m.group(1).split("|")] if m else None
    for fam, r in fams.items():
        cnt = r.get("count", {})
        counts = has_count(r)
        a = by.get(fam, {}).get("authorship", [])
        if not a:
            if counts: errs.append(f"authorship: {fam} has the count {cnt.get('value')!r} and no authorship row; state authored or counted with its sentence")
            auth[fam] = OrderedDict([("value", "authored"), ("source", "generic"), ("note", "no counted arm: one party authors the row (CC 2.6.1.3)")])
        elif any(x["value"] == "gap" for x in a):
            if len(a) != sum(1 for x in a if x["value"] == "gap" and x["selector"] == "*"):
                errs.append(f"authorship: {fam} is gap with other arms; a gap is the family's one arm, selector *")
            auth[fam] = OrderedDict([("value", None), ("source", "gap"), ("cc_ref", list(dict.fromkeys(x["cc_ref"] for x in a))),
                                     ("note", "the text gives both readings and no selector key names the case: " + " / ".join(x["quote"] for x in a))])
        else:
            arms_ = []
            for x in a:
                cur = next((y for y in arms_ if y["when"] == x["selector"]), None)
                if cur is None: arms_.append(OrderedDict([("when", x["selector"]), ("value", x["value"]), ("cc_ref", [x["cc_ref"]])]))
                elif cur["value"] != x["value"]: errs.append(f"authorship: {fam} gives the selector {x['selector']} two values")
                elif x["cc_ref"] not in cur["cc_ref"]: cur["cc_ref"].append(x["cc_ref"])
            if any(y["when"] == "*" for y in arms_[:-1]): errs.append(f"authorship: {fam}: an arm for every row is the last arm")
            for y in arms_:
                if y["value"] != "counted": continue
                lf = leaf_families(fam, y["when"])
                if lf is not None:
                    bad = [x for x in lf if x not in fams or not has_count(fams[x])]
                    if bad: errs.append(f"authorship: {fam}: the leaf families {', '.join(bad)} are not families with a count")
                elif not counts: errs.append(f"authorship: {fam} is counted in an arm and its count is none; a counted row has a count")
            if arms_[-1]["when"] != "*": arms_.append(OrderedDict([("when", "*"), ("value", "authored"), ("cc_ref", ["CC 2.6.1.3"]), ("rule", "default")]))
            val = arms_[0]["value"] if len(arms_) == 1 else " ; ".join((y["when"] + " => " if y["when"] != "*" else "") + y["value"] for y in arms_)
            auth[fam] = OrderedDict([("value", val), ("source", "cc-table"), ("arms", arms_),
                                     ("cc_ref", list(dict.fromkeys(c for y in arms_ for c in y["cc_ref"] if y.get("rule") != "default")))])
        ss = by.get(fam, {}).get("second_signers", [])
        if not ss:
            second[fam] = OrderedDict([("value", []), ("source", "generic"), ("note", "no role is named: the author's statement alone, or on a counted row the voices of its count")]); continue
        ents = []
        for x in ss:
            role, member = x["value"].split("=")
            cur = next((e for e in ents if (e["role"], e["member"], e.get("when", "*")) == (role, member, x["selector"])), None)
            if cur is None:
                e = OrderedDict([("role", role), ("member", member)])
                if x["selector"] != "*": e["when"] = x["selector"]
                e["cc_ref"] = [x["cc_ref"]]; ents.append(e)
            elif x["cc_ref"] not in cur["cc_ref"]: cur["cc_ref"].append(x["cc_ref"])
        gaps = sum(1 for e in ents if e["member"] == "gap")
        second[fam] = OrderedDict([("value", ents), ("source", "cc-table" if not gaps else ("gap" if gaps == len(ents) else "mixed"))])
        if gaps: second[fam]["note"] = "a member reading gap: the text names the role and not the payload member that names its party"
    return auth, second, errs


def authorship_self_test():
    """The breaks the authorship check must catch, run every time: a misquote, an unknown selector key, a counted arm on a
    family whose count is none, a family with a count and no row, a gap beside another arm, a member the text never names, and an
    `act` value outside group and own."""
    rows = [OrderedDict([("family", "a"), ("count", {"value": "none", "source": "generic"})]),
            OrderedDict([("family", "b"), ("count", {"value": "x@self", "source": "cc-table"})])]
    span = lambda ref: "the words stand here" if ref == "CC 1" else None
    ok = dict(family="b", column="authorship", selector="*", value="counted", cc_ref="CC 1", quote="words stand")
    breaks = [("misquote", [dict(ok, quote="not here")]), ("selector key", [dict(ok, selector="kind=x")]), ("act value", [dict(ok, selector="act=club")]),
              ("counted with no count", [dict(ok, family="a")]), ("count with no row", []),
              ("gap beside an arm", [dict(ok, value="gap"), dict(ok, selector="leaf=y", value="counted")]),
              ("unnamed member", [ok, dict(ok, column="second_signers", value="delegate=nobody")])]
    _, _, clean = authorship_cells([ok], rows, set(), span)
    missed = [] if not clean else ["a clean table: " + "; ".join(clean)]
    for name, st in breaks:
        if not authorship_cells(st, rows, set(), span)[2]: missed.append(name)
    return missed


# The named answers of formal/KERNEL.md 5, as tools/kx_prelude.kx writes them: each answer and the prelude functions that are it.
ANSWERS = OrderedDict([("state", ("state", "state_in", "live", "live_in")),
                       ("stands", ("stands", "stands_in", "holders_in", "holder_units_in", "conferrers", "offers", "accepted")),
                       ("tally", ("tally", "tally2", "roster", "voters", "votes", "rule_votes")),
                       ("may", ("may",)), ("audience", ("audience",)), ("missing", ("missing",)), ("owed", ("owed",)), ("window", ("window",))])


def read_by_cells(fams):
    """Which named answers read a family's rows: every rule cell of the family (guard, fold, change, reaction, count) translated
    by tools/kx_translate.py, and the answers its KX calls, through the prelude's own definitions. A guard is the `guard`
    argument of `may`; a count arm that names a policy row is a `tally`; a clock or a landing is a `window`. A family with no
    cell of its own in a grammar reads by that grammar's default. Returns ({family: cell}, errors)."""
    import fold_grammar as fg, guard_grammar as gg, change_grammar as cg, build_reactions as br, kx_translate as T
    errs = []
    pre = open(os.path.join(ROOT, "tools/kx_prelude.kx"), encoding="utf-8").read()
    defs = {m.group(1): set(re.findall(r"\b([a-z_0-9]+)\(", m.group(2))) for m in re.finditer(r"^def (\w+)\([^)]*\)\s*=\s*(.*?)(?=^def |\Z)", pre, re.M | re.S)}
    for a, fs in ANSWERS.items():
        for fn in fs:
            if fn not in defs: errs.append(f"read_by: {fn} (the answer {a}) is not defined in tools/kx_prelude.kx")
    def answers(src, extra=()):
        seen, todo = set(), set(re.findall(r"\b([a-z_0-9]+)\(", src))
        while todo:
            fn = todo.pop()
            if fn not in seen: seen.add(fn); todo |= defs.get(fn, set())
        got = {a for a, fs in ANSWERS.items() if seen & set(fs)} | set(extra)
        if "tuple('tally'," in src: got.add("tally")
        if "tuple('clock'," in src or "tuple('land'," in src: got.add("window")
        return got
    dparts = fg.parse(fg.DEFAULT)[0]["parts"]
    def fold_src(fam, text):
        parsed = fg.parse(text)[0]; parts = dict(parsed["parts"])
        if not [k for k in parts if k not in T.LABELS]: return ""
        for k in ("reads", "key", "pick", "cut"):
            if k not in parts and k in dparts: parts[k] = dparts[k]
        return T.Tx(parts, "x:{y}" if fam.startswith("*") else fam, parsed["when"]).build()
    D = os.path.join(ROOT, "formal/derivation")
    own, every = {f: [] for f in fams}, []
    def put(fam, grammar, where, got):
        e = OrderedDict([("grammar", grammar), ("cell", where), ("answers", [a for a in ANSWERS if a in got])])
        if fam == "*": every.append(e)
        elif fam in own: own[fam].append(e)
    jobs = [("guard", "guard_text.tsv", "guard", lambda f, t: answers(T.translate(gg.parse(t)[0]), ("may",))),
            ("fold", "fold_text.tsv", "fold", lambda f, t: answers(fold_src(f, t))),
            ("change", "change_text.tsv", "change", lambda f, t: answers(T.ch_kx(cg.parse(t)[0]))),
            ("reaction", "reaction_text.tsv", "reaction", lambda f, t: answers(T.re_kx(br.parse(t)[0])[0]))]
    typed, failed = {g: set() for g, _, _, _ in jobs}, {}
    for g, fn, col, tr in jobs:
        for i, r in enumerate(tsv_rows(os.path.join(D, fn))):
            try: got = tr(r["family"], r[col])
            except Exception as e:  # noqa: BLE001 -- a cell its own tool refuses is reported by that tool; here the family stays open
                failed.setdefault(r["family"], []).append(f"{fn} row {i + 1}: {type(e).__name__}"); continue
            put(r["family"], g, f"formal/derivation/{fn}#{r['family']} ({r['cc_ref']})", got)
            typed[g].add(r["family"])
    arms = OrderedDict()
    for r in tsv_rows(os.path.join(D, "count_text.tsv")): arms.setdefault(r["family"], []).append(r)
    for f, a in arms.items(): put(f, "count", f"formal/derivation/count_text.tsv#{f}", answers(T.count_kx(a)))
    m = re.search(r'^CHANGE_DEFAULT = "([^"]+)"', open(os.path.join(ROOT, "tools/build_transitions.py"), encoding="utf-8").read(), re.M)
    dflt = [OrderedDict([("grammar", "fold"), ("cell", "tools/fold_grammar.py DEFAULT"), ("answers", [a for a in ANSWERS if a in answers(fold_src("*", fg.DEFAULT))])])]
    if m: dflt.append(OrderedDict([("grammar", "change"), ("cell", "tools/build_transitions.py CHANGE_DEFAULT"), ("answers", [a for a in ANSWERS if a in answers(T.ch_kx(cg.parse(m.group(1))[0]))])]))
    base = set().union(*[set(e["answers"]) for e in every + dflt])
    out = OrderedDict()
    for f in fams:
        by = list(own[f])
        if f not in typed["fold"]: by.append(dflt[0])
        if f not in typed["change"] and len(dflt) > 1: by.append(dflt[1])
        got = set().union(*[set(e["answers"]) for e in by]) | base
        val = [a for a in ANSWERS if a in got]
        if f in failed:
            out[f] = OrderedDict([("value", None), ("source", "gap"), ("note", "a rule cell does not translate into KX: " + "; ".join(failed[f]))]); continue
        out[f] = OrderedDict([("value", val), ("source", "cc-table"), ("rule", "cells" if own[f] else "default"),
                              ("by", [e for e in by if e["answers"]])])
    return out, OrderedDict([("every_family", every), ("defaults", dflt), ("value", [a for a in ANSWERS if a in base])]), errs


def census_names(census, registered):
    """formal/derivation/census_names.tsv: the census rows whose name the text does not register, each retired (not
    read) or renamed (read as the text's family). Returns (rows, errors); the census itself is never edited."""
    rows, errs = [], []
    for r in csv.DictReader([l for l in open(CENSUS_NAMES, encoding="utf-8").read().split("\n") if l and not l.startswith("#")], delimiter="\t"):
        old, fate, new, why = r["census_prefix"], r["fate"], r["family"], r["reason"]
        if old not in census: errs.append(f"census_names.tsv: {old} is not a row of the census")
        if old in registered: errs.append(f"census_names.tsv: {old} is a registered family; remove the row")
        if fate not in ("retired", "renamed") or (fate == "renamed") != bool(new): errs.append(f"census_names.tsv: {old}: fate {fate!r} with family {new!r}")
        if new and new not in registered: errs.append(f"census_names.tsv: {old}: {new} is not a registered family")
        if new and new in census: errs.append(f"census_names.tsv: {old}: the census already carries {new}")
        if not why: errs.append(f"census_names.tsv: {old}: no reason")
        rows.append(OrderedDict([("census_prefix", old), ("fate", fate)] + ([("family", new)] if new else []) + [("reason", why)]))
    return rows, errs


def read_census(registered):
    """The vendored census keyed by the family each row is read as (census_names.tsv), with the table's rows."""
    census_lines = [l for l in open(CENSUS, encoding="utf-8").read().split("\n") if not l.startswith("#")]
    census = OrderedDict((r["prefix"], r) for r in csv.DictReader(census_lines, delimiter="\t"))
    names, errs = census_names(census, registered)
    for n in names:
        row = census.pop(n["census_prefix"], None)
        if row is not None and n["fate"] == "renamed": census[n["family"]] = row
    return census, names, errs


def main():
    cc = {r["family"]: r for r in csv.DictReader(open(CC, encoding="utf-8"), delimiter="\t")}
    reg = json.load(open(REG, encoding="utf-8"))
    census, census_named, nerrs = read_census({f["prefix"] for f in reg.get("families", []) if isinstance(f, dict) and "prefix" in f})
    if nerrs:
        [print(e) for e in nerrs]; return 1
    pol = {}
    for f in reg.get("families", []):
        if isinstance(f, dict) and "prefix" in f: pol[f["prefix"]] = f.get("polarity")
    signer_text = OrderedDict()   # family -> rows; one row for a whole-family rule, one per stage where the text gives stages
    for r in csv.DictReader([l for l in open(SIGNER_TEXT, encoding="utf-8").read().split("\n") if l and not l.startswith("#")], delimiter="\t"):
        signer_text.setdefault(r["family"], []).append(r)
    # A cell the text states and the census leaves open (formal/derivation/cell_text.tsv): the cell
    # takes the text's value, written in the column's own vocabulary, with the words it rests on.
    cell_text = OrderedDict()
    if os.path.exists(CELL_TEXT):
        for r in csv.DictReader([l for l in open(CELL_TEXT, encoding="utf-8").read().split("\n") if l and not l.startswith("#")], delimiter="\t"):
            cell_text.setdefault(r["family"], []).append(r)
    # Where a row goes when its family states no placement: the default, with the audience of each scope.
    placing, perrs = placement_text(json.load(open(DEFAULT, encoding="utf-8"))["columns"]["placement"])
    if perrs:
        [print(e) for e in perrs]; return 1
    placed_by_default = 0
    count_text = OrderedDict()
    for r in csv.DictReader([l for l in open(COUNT_TEXT, encoding="utf-8").read().split("\n") if l and not l.startswith("#")], delimiter="\t", quoting=csv.QUOTE_NONE):
        count_text.setdefault(r["family"], []).append(r)
    policy_rows = {f["family"] for f in json.load(open(POLICY, encoding="utf-8"))["families"]}
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import fold_grammar as fg, guard_grammar as gg
    fold_text, fold_every, fold_marks = OrderedDict(), [], Counter()
    for r in csv.DictReader([l for l in open(FOLD_TEXT, encoding="utf-8").read().split("\n") if l and not l.startswith("#")], delimiter="\t", quoting=csv.QUOTE_NONE):
        fold_text.setdefault(r["family"], []).append(r)
    reg_fams = set(cc) | set(census)
    for f in reg.get("families", []):
        if isinstance(f, dict) and "prefix" in f:
            reg_fams.add(f["prefix"]); reg_fams.update(f.get("leaves", []))
    part_text = "\n".join(open(p, encoding="utf-8").read() for p in sorted(glob.glob(os.path.join(ROOT, "constitution", "part_*.md"))))
    fold_voc = {"families": reg_fams, "policy_rows": policy_rows, "tokens": set(re.findall(r"`([a-z_0-9:]+)`", part_text)),
                "roles": set(json.load(open(os.path.join(ROOT, "manifests/transitions.json"), encoding="utf-8"))["_meta"]["role_tokens"])}
    fg.parse(fg.DEFAULT)
    def fold_cell(fam, stmts):
        out = []
        for st in stmts:
            where = f"fold_text.tsv: {fam} ({st['cc_ref']})"
            try:
                parsed, mk, names = fg.parse(st["fold"])
            except fg.FoldError as e:
                print(f"{where}: {e}"); return None
            bad = fg.closure(names, fold_voc, gg.family_ok)
            if bad:
                print(f"{where}: outside the vocabularies: " + "; ".join(bad)); return None
            span = section_span(st["cc_ref"])
            if span is None or st["quote"] not in span:
                print(f"{where}: the quoted words do not stand in {st['cc_ref']}"); return None
            cur = next((x for x in out if x["fold"] == st["fold"]), None)
            if cur:
                if st["cc_ref"] not in cur["cc_ref"]: cur["cc_ref"].append(st["cc_ref"])
            else:
                out.append(OrderedDict([("fold", st["fold"]), ("cc_ref", [st["cc_ref"]])]))
                fold_marks.update(mk)
        return out
    conf_cells, seg_cells, derived_text, cerrs = conferral_columns(sorted(set(cc) | set(census)), reg)
    if cerrs:
        [print(e) for e in cerrs]; return 1
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    der_cells, der_meta, derrs = read_by_cells(sorted(set(cc) | set(census)))
    if derrs:
        [print(e) for e in derrs]; return 1
    rows = []
    for fam in sorted(set(cc) | set(census)):
        c, z = cc.get(fam), census.get(fam)
        row = OrderedDict([("family", fam)])
        if c:
            row["kind"] = {"value": c["kind"], "source": "cc-table", "confidence": c["confidence"]}
            row["side"] = {"value": c["side"].lower(), "source": "cc-table"}
            row["verbs"] = {"value": [v.strip() for v in c["verbs"].split(",") if v.strip()], "source": "cc-table"}
            row["maintains_record"] = {"value": c["maintains_record"] == "yes", "source": "cc-table"}
            row["reference"] = {"value": None if c["reference"] == "—" else c["reference"], "source": "cc-table"}
        else:
            for k in ("kind", "side", "verbs", "maintains_record", "reference"): row[k] = {"value": None, "source": "gap", "note": "not in the CC table"}
        for col, zc in CENSUS_MAP.items():
            row[col] = cell(col, z[zc]) if z else {"value": None, "source": "gap", "note": "not in the census"}
        if fam in signer_text:
            sts = signer_text.pop(fam); cur = row["signer_rule"]
            if cur.get("source") != "gap" and cur.get("value") != HELD_SHUT and (fam, "signer_rule") not in TEXT_OVER_CODE:
                print(f"signer_rule_text.tsv: {fam} has a closed census cell ({cur.get('source')}); remove the row, or list the cell in text_review.tsv as differs"); return 1
            parsed = []
            for st in sts:
                txt = signer(st["signer_rule"])
                if not isinstance(txt.get("value"), dict):
                    print(f"signer_rule_text.tsv: {fam} is not `who x via x {{conditions}}`"); return 1
                parsed.append(((st.get("stage") or "").strip(), txt, st))
            stages = [p[0] for p in parsed]
            if (len(parsed) > 1 and "" in stages) or len(set(stages)) != len(stages):
                print(f"signer_rule_text.tsv: {fam} mixes a whole-family rule with stages, or repeats a stage"); return 1
            code = {"value": cur.get("value"), "source": cur.get("source")}
            if stages == [""]:
                _, txt, st = parsed[0]
                row["signer_rule"] = {"value": txt["value"], "source": "cc-table", "cc_ref": st["cc_ref"], "code": code}
                if txt.get("qualifier"): row["signer_rule"]["qualifier"] = txt["qualifier"]
            else:
                def text_of(v): return (" | ".join(v["who"]) if isinstance(v["who"], list) else v["who"]) + " x " + v["via"] + " x {" + ", ".join(v["conditions"]) + "}"
                row["signer_rule"] = {"value": OrderedDict((stg, text_of(txt["value"])) for stg, txt, _ in parsed), "source": "cc-table",
                                      "per_stage": True, "closed": "; ".join(f"{stg}: {text_of(txt['value'])}" for stg, txt, _ in parsed),
                                      "cc_ref": OrderedDict((stg, st["cc_ref"]) for stg, _, st in parsed), "code": code}
                q = OrderedDict((stg, txt["qualifier"]) for stg, txt, _ in parsed if txt.get("qualifier"))
                if q: row["signer_rule"]["qualifier"] = q
        for ct in cell_text.pop(fam, []):
            col = ct["column"]
            if col not in CENSUS_MAP or col == "signer_rule":
                print(f"cell_text.tsv: {fam} names the column {col}, which is not one this table fills"); return 1
            cur = row[col]
            if cur.get("source") not in ("gap", "generic") and (fam, col) not in TEXT_OVER_CODE:
                print(f"cell_text.tsv: {fam} {col} is closed by the census ({cur.get('source')}); a difference from the text is a departure with a reason, not a row here"); return 1
            span = section_span(ct["cc_ref"])
            if span is None or ct["quote"] not in span:
                print(f"cell_text.tsv: {fam} {col}: the quoted words do not stand in {ct['cc_ref']}"); return 1
            new = cell(col, ct["value"])
            new["source"] = "cc-table"; new["cc_ref"] = ct["cc_ref"]
            new["code"] = {"value": cur.get("value"), "source": cur.get("source")}
            row[col] = new
        # A family whose rows the census finds at any scope the signer chooses, and for which the text states no
        # placement of its own, takes the default: the scope each row carries, with the audience CC 5.2 gives it.
        cur = row["placement"]
        if cur.get("source") == "gap" and cur.get("value") == placing["default"]["value"]:
            row["placement"] = {"value": cur["value"], "source": "cc-table", "cc_ref": placing["default"]["cc_ref"], "rule": "default",
                                "code": OrderedDict((k, cur[k]) for k in ("value", "source", "note") if k in cur)}
            placed_by_default += 1
        pv = polarity_census(z["6_polarity"]) if z else None
        row["polarity"] = {"value": pv or pol.get(fam), "source": "code-v61" if pv else ("cc-table" if pol.get(fam) else "gap"), "registry": pol.get(fam)}
        row["emitter_class"] = emitter_class(row["signer_rule"])
        row["derived"], row["read_by"] = derived_text[fam], der_cells[fam]
        row["confers"], row["binds_segment"] = conf_cells[fam], seg_cells[fam]
        row["names_head"] = names_head(row)
        ruled = NAMES_HEAD_TEXT.pop(fam, None)
        if ruled:
            derived = row["names_head"].get("value")
            if len(ruled) == 1 and ruled[0][0] == "*":
                row["names_head"] = {"value": ruled[0][1], "source": "ruled", "from": "formal/derivation/names_head_text.tsv", "note": ruled[0][2], "derived": derived, "cc_ref": "CC 2.4.1.1"}
            else:
                row["names_head"] = {"value": OrderedDict((sel, v) for sel, v, _ in ruled), "source": "ruled", "per_selector": True, "from": "formal/derivation/names_head_text.tsv",
                                     "note": OrderedDict((sel, w) for sel, _, w in ruled), "derived": derived, "cc_ref": "CC 2.4.1.1"}
        shp = SHAPE_OF.get(fam)
        row["shape"] = {"value": None if shp == "none fits" else shp, "source": "kernel-table", "from": "formal/derivation/family_shapes.tsv"}
        if shp == "none fits": row["shape"]["note"] = "no kernel shape takes the family; it is read as structure"
        row["descends_on_withdrawal"] = {"value": DESCENDS[shp], "source": "derived", "from": "shape", "cc_ref": "CC 6.1.5"}
        stmts = fold_text.pop(fam, [])
        if stmts:
            fc = fold_cell(fam, stmts)
            if fc is None: return 1
            row["fold"] = {"value": fc, "source": "cc-table"}
        else:
            row["fold"] = {"value": [], "source": "generic", "note": "no fold is typed for the family; it reads by the default"}
        # How the family's act is counted: typed arms over the policy table, each with the words it rests on.
        arms = count_text.pop(fam, [])
        if arms:
            out_arms = []
            for i, a in enumerate(arms):
                where = f"count_text.tsv: {fam} arm {i + 1}"
                sel = a["selector"]
                if sel != "*":
                    for t in sel.split(" & "):
                        mt = re.fullmatch(r"([a-z]+)=([a-z_]+(?:\|[a-z_]+)*)", t)
                        if not mt or mt.group(1) not in COUNT_ARM_KEYS:
                            print(f"{where}: {t!r} is not a test on one of {', '.join(COUNT_ARM_KEYS)}"); return 1
                elif i != len(arms) - 1:
                    print(f"{where}: an arm for every row is the last arm"); return 1
                md = re.fullmatch(r"(none|shut)|([a-z_]+)(?:@([a-z_]+))?(?:!(confers|result))?", a["doors"])
                if not md or (md.group(2) and (md.group(2) not in policy_rows or (md.group(3) and md.group(3) not in COUNT_SOURCES))):
                    print(f"{where}: {a['doors']!r} is not none, shut or a policy row with a known source"); return 1
                span = section_span(a["cc_ref"])
                if span is None or a["quote"] not in span:
                    print(f"{where}: the quoted words do not stand in {a['cc_ref']}"); return 1
                out_arms.append(OrderedDict([("when", sel), ("doors", a["doors"]), ("cc_ref", a["cc_ref"])]))
            row["count"] = {"value": " ; ".join((x["when"] + " => " if x["when"] != "*" else "") + x["doors"] for x in out_arms),
                            "arms": out_arms, "source": "cc-table"}
        elif row["cosign_rule"].get("value") == "none":
            row["count"] = {"value": "none", "source": "generic", "note": "the cosign cell reads none: one signature carries the row"}
        else:
            row["count"] = {"value": None, "source": "gap", "note": "the cosign cell is not none and no arm is typed", "cosign_rule": row["cosign_rule"].get("value")}
        er = row["erasure_route"].get("value")
        erh = head_of(er) if isinstance(er, str) else (head_of(er[0]) if isinstance(er, list) and er else None)
        if erh in ("dsar", "purge"):
            row["blind"] = {"value": ["body.note"], "source": "derived", "note": "from erasure_route; further free-text and other-authored members are named with the family's ruled row"}
        elif erh in ("none", "legal_hold"):
            row["blind"] = {"value": [], "source": "derived", "note": "from erasure_route: sealed"}
        else:
            row["blind"] = {"value": None, "source": "gap", "note": "erasure_route unread"}
        if z:
            vc = [v.strip() for v in z.get("verbs_admitted", "").split(",") if v.strip()]
            row["verbs_code"] = {"value": vc, "delta_vs_cc": z.get("verbs_delta", ""), "source": "code-v61"}
            row["maintains_record_code"] = {"value": z.get("maintains_record_code", "").startswith("yes"), "source": "code-v61", "note": z.get("maintains_record_code", "")}
            row["reference_code"] = {"value": reference_code(z.get("15_reference_rule")), "source": "code-v61" if reference_code(z.get("15_reference_rule")) else "gap"}
            row["reserved"] = {"value": z.get("reserved", "") == "true", "rule": z.get("reserved_rule", ""), "source": "cc-table"}
            row["code_v61"] = {"door": z.get("door", ""), "witness": z.get("witness", ""), "formal_witness": z.get("formal_witness", ""),
                                "carries_kind_census": z.get("carries_kind", ""), "sources": z.get("sources", "")}
        rows.append(row)
    if signer_text:
        print("signer_rule_text.tsv names families outside the model: " + ", ".join(sorted(signer_text))); return 1
    if cell_text:
        print("cell_text.tsv names families outside the model: " + ", ".join(sorted(cell_text))); return 1
    # The body of a family from the signed-object table (CC 8.11.9): each member whose presence that table states for
    # a wire form of the family, with its type. A presence written in words that name no wire form is left to the
    # table and counted. A cell the census reads as prose is not replaced.
    all_fams = [r["family"] for r in rows]
    def owners(name):
        name = re.sub(r":v\d+$", "", name.strip())
        if name.endswith(":*"):
            return [(f, None) for f in all_fams if f.startswith(name[:-1])]
        if name in by_fam_names: return [(name, None)]
        return [(f, name) for f in all_fams if "{" in f and gg.family_ok(name, {f})]
    by_fam_names = set(all_fams)
    body_members, body_unread = OrderedDict(), []
    for so in csv.DictReader(open(SIGNED_OBJECT, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE):
        if so["object"] != "attestation_row": continue
        for mode, lst in re.findall(r"(REQUIRED|OPTIONAL) on ([^;()]+)", so["presence"]):
            for name in [x.strip() for x in re.split(r",| and ", lst) if x.strip()]:
                own = owners(name) if re.fullmatch(r"[a-z_]+(:[a-z_{}*0-9]+)+", name) else []
                if not own:
                    body_unread.append(f"{so['member']}: {name}"); continue
                for fam, leaf in own:
                    e = OrderedDict([("member", so["member"]), ("type", so["type"]), ("presence", mode.lower())])
                    if leaf: e["leaf"] = leaf
                    if e not in body_members.setdefault(fam, []): body_members[fam].append(e)
    body_text_n = Counter()
    for bt in csv.DictReader([l for l in open(os.path.join(ROOT, "formal/derivation/body_text.tsv"), encoding="utf-8").read().split("\n") if l and not l.startswith("#")], delimiter="\t", quoting=csv.QUOTE_NONE):
        where = f"body_text.tsv: {bt['family']} {bt['member']} ({bt['cc_ref']})"
        if bt["family"] not in by_fam_names or bt["presence"] not in ("required", "optional", "forbidden", "unstated") or bt["in_cddl"] not in ("yes", "no"):
            print(f"{where}: no such family, or a presence or in_cddl value outside its words"); return 1
        span = section_span(bt["cc_ref"])
        if span is None or bt["quote"] not in span:
            print(f"{where}: the quoted words do not stand in {bt['cc_ref']}"); return 1
        lst = body_members.setdefault(bt["family"], [])
        if not any(e["member"] == bt["member"] for e in lst):
            lst.append(OrderedDict([("member", bt["member"]), ("type", bt["type"]), ("presence", bt["presence"]),
                                    ("in_cddl", bt["in_cddl"] == "yes"), ("cc_ref", bt["cc_ref"])]))
            body_text_n[bt["in_cddl"]] += 1
    for r in rows:
        mem = body_members.get(r["family"])
        if mem and r["body"].get("source") == "gap":
            r["body"] = {"value": OrderedDict([("members", mem)]), "source": "cc-table", "cc_ref": "CC 8.11.9",
                         "code": {"value": r["body"].get("value"), "source": "gap"},
                         "note": "the members the signed-object table states for this family's wire forms, and those the text states (each with its section and whether the name is in the CDDL), beyond those every row carries"}
    # The forward payload (CC 2.6.1.4): where the signed-object table of this form states a family's payload rule, that rule
    # is the family's body, member for member, and the earlier form's cell gives way to it (a family whose rule covers
    # some leaves only keeps its cell's members of the others).
    fwd = OrderedDict()
    for so in csv.DictReader(open(SIGNED_OBJECT_V2, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE):
        fam = FORWARD_PAYLOAD.get(so["rule"])
        if fam:
            e = OrderedDict([
                ("member", so["member"].strip('"')), ("type", so["type"]),
                ("presence", "required" if so["required_when"] == "always" else "optional"),
                ("when", so["required_when"]), ("in_cddl", True), ("cc_ref", "CC " + so["cc_ref"].split()[0])])
            if list(FORWARD_PAYLOAD.values()).count(fam) > 1: e["rule"] = so["rule"]
            if len(FORWARD_LEAVES.get(fam, ())) == 1: e["leaf"] = fam.split(":")[0] + ":" + FORWARD_LEAVES[fam][0]   # the one leaf the rule states
            fwd.setdefault(fam, []).append(e)
    if set(fwd) != set(FORWARD_PAYLOAD.values()):
        print("signed_object_v2.tsv states no payload for: " + ", ".join(sorted(set(FORWARD_PAYLOAD.values()) - set(fwd)))); return 1
    for r in rows:
        if r["family"] in fwd:
            leaves = FORWARD_LEAVES.get(r["family"])
            old = r["body"].get("value") if isinstance(r["body"].get("value"), dict) else {}
            named = {e["member"] for e in fwd[r["family"]]}
            keep = [e for e in old.get("members", []) if (leaves and e.get("leaf") and e["leaf"].split(":")[1] not in leaves)
                    or (r["family"] in FORWARD_PARTIAL and e.get("member") not in named)]
            its = [k for k, v in FORWARD_PAYLOAD.items() if v == r["family"]]
            r["body"] = {"value": OrderedDict([("rule", its[0]) if len(its) == 1 else ("rules", its),
                                               ("members", fwd[r["family"]] + keep)]),
                         "source": "cc-table", "cc_ref": "CC 2.6.1.4",
                         "note": "the family's payload in this form, member for member from the members table of CC 2.6.1.4"
                                 + (f"; {'stages' if r['family'].startswith('membership') else 'leaves'} {', '.join(leaves)}; the others keep the members the earlier cell gave" if leaves else "")}
    # The sentences that state a closed cell: the cell gains the sections that say it, its value untouched.
    by_fam = {r["family"]: r for r in rows}
    cited = 0
    for ct in csv.DictReader([l for l in open(CELL_CITES, encoding="utf-8").read().split("\n") if l and not l.startswith("#")], delimiter="\t", quoting=csv.QUOTE_NONE):
        where = f"cell_cites.tsv: {ct['family']} {ct['column']} ({ct['cc_ref']})"
        cellv = by_fam.get(ct["family"], {}).get(ct["column"])
        if not isinstance(cellv, dict) or ct["reading"] not in ("agree", "fills"):
            print(f"{where}: no such cell, or a reading that is not agree or fills"); return 1
        if cellv.get("source") == "gap":
            print(f"{where}: the cell is open; state its value in cell_text.tsv"); return 1
        span = section_span(ct["cc_ref"])
        if span is None or ct["quote"] not in span:
            print(f"{where}: the quoted words do not stand in {ct['cc_ref']}"); return 1
        cites = cellv.setdefault("cites", [])
        entry = next((x for x in cites if x["cc_ref"] == ct["cc_ref"]), None)
        if entry is None:
            cites.append(OrderedDict([("cc_ref", ct["cc_ref"]), ("reading", ct["reading"])])); cited += 1
        elif ct["reading"] == "fills":
            entry["reading"] = "fills"
    reader_defaults = []
    for rd in csv.DictReader([l for l in open(os.path.join(ROOT, "formal/derivation/fold_reader_defaults.tsv"), encoding="utf-8").read().split("\n") if l and not l.startswith("#")], delimiter="\t", quoting=csv.QUOTE_NONE):
        try:
            fg.parse(rd["fold"])
        except fg.FoldError as e:
            print(f"fold_reader_defaults.tsv: {rd['polarity']}: {e}"); return 1
        span = section_span(rd["cc_ref"])
        if span is None or rd["quote"] not in span:
            print(f"fold_reader_defaults.tsv: {rd['polarity']}: the quoted words do not stand in {rd['cc_ref']}"); return 1
        reader_defaults.append(OrderedDict([("polarity", rd["polarity"]), ("fold", rd["fold"]), ("cc_ref", rd["cc_ref"])]))
    if "*" in fold_text:
        fold_every = fold_cell("*", fold_text.pop("*"))
        if fold_every is None: return 1
    if NAMES_HEAD_TEXT:
        print("names_head_text.tsv names families outside the model: " + ", ".join(sorted(NAMES_HEAD_TEXT))); return 1
    if fold_text:
        print("fold_text.tsv names families outside the model: " + ", ".join(sorted(fold_text))); return 1
    if sum(fold_marks.values()) > FOLD_MARKS_MAX:
        print(f"fold: {sum(fold_marks.values())} uses of words no other vocabulary has, more than {FOLD_MARKS_MAX}"); return 1
    if count_text:
        print("count_text.tsv names families outside the model: " + ", ".join(sorted(count_text))); return 1
    count_open = [r["family"] for r in rows if r["count"]["source"] == "gap"]
    if len(count_open) > COUNT_OPEN_MAX:
        print(f"count: {len(count_open)} families have a cosign cell and no typed count, more than {COUNT_OPEN_MAX}: " + ", ".join(count_open)); return 1
    # Who signs a row: authored or counted, and the roles beside the author (CC 2.6.1.3, CC 2.6.1.9).
    missed = authorship_self_test()
    if missed:
        print("authorship: the check let through its deliberate breaks: " + ", ".join(missed)); return 1
    auth, second, aerrs = authorship_cells(tsv_rows(AUTHORSHIP_TEXT), rows, fold_voc["tokens"])
    if aerrs:
        [print(e) for e in aerrs]; return 1
    for r in rows:
        fam, items = r["family"], list(r.items()); k = [x[0] for x in items].index("count") + 1
        r.clear(); r.update(items[:k] + [("authorship", auth[fam]), ("second_signers", second[fam])] + items[k:])
    # Withdrawal and standing: six cells a family, placed after descends_on_withdrawal (formal/derivation/standing_text.tsv).
    st_text, st_meta, serrs = standing_text()
    if serrs:
        [print(e) for e in serrs]; return 1
    for r in rows:
        cells = standing_cells(r, st_text)
        items = list(r.items()); k = [x[0] for x in items].index("descends_on_withdrawal") + 1
        r.clear(); r.update(items[:k] + list(cells.items()) + items[k:])
    unused = [f"{c} {t['family']} {t['selector']}" for c, ts in st_text.items() for t in ts if not t["used"]]
    if unused:
        print("standing_text.tsv names families outside the model: " + ", ".join(unused)); return 1
    nh_branches = []
    for b in NAMES_HEAD_BRANCHES:
        if b["rule"] not in st_meta:
            print(f"standing_text.tsv: no _meta rule {b['rule']} for the by_placement branch at {', '.join(b['placed_at'])}"); return 1
        nh_branches.append(OrderedDict(list(b.items()) + [("cites", st_meta[b["rule"]]["cites"])]))
    st_key = lambda v: "by_selector" if isinstance(v, dict) else ("open" if v is None else str(v).lower())
    st_counts = OrderedDict((c, OrderedDict([("by_value", OrderedDict(sorted(Counter(st_key(r[c]["value"]) for r in rows).items()))),
                                             ("by_source", OrderedDict((s, sum(1 for r in rows if r[c]["source"] == s)) for s in STANDING_RANK))]))
                            for c in STANDING_VALUES)
    auth_gap = [f for f, c in auth.items() if c["source"] == "gap"]
    second_gap = [(f, e["role"]) for f, c in second.items() for e in c["value"] if e["member"] == "gap"]
    if len(auth_gap) > AUTHORSHIP_GAP_MAX:
        print(f"authorship: {len(auth_gap)} families are open, more than {AUTHORSHIP_GAP_MAX}: " + ", ".join(auth_gap)); return 1
    if len(second_gap) > SECOND_SIGNERS_GAP_MAX:
        print(f"second_signers: {len(second_gap)} roles name no payload member, more than {SECOND_SIGNERS_GAP_MAX}: " + ", ".join(f"{f} {x}" for f, x in second_gap)); return 1
    a_kind = Counter("gap" if c["source"] == "gap" else (c["value"] if c["value"] in ("authored", "subject", "counted") else "mixed") for c in auth.values())
    # The default row: the value a family takes in each of these columns unless it states its own.
    # Pinned as data, and held to be the commonest value of its column, so a change of default is a
    # deliberate edit and never a drift. Each row lists the columns in which it departs.
    default = json.load(open(DEFAULT, encoding="utf-8"), object_pairs_hook=OrderedDict)["columns"]
    canon = lambda v: json.dumps(v, sort_keys=True, ensure_ascii=False)
    for col, dv in default.items():
        cnt = Counter(canon(r[col].get("value")) for r in rows)
        top, n = cnt.most_common(1)[0]
        if canon(dv) != top:
            print(f"family_default_row.json: the default for {col} is held by {cnt.get(canon(dv), 0)} families and another value by {n}"); return 1
    departures = []
    for r in rows:
        r["departs"] = [col for col, dv in default.items() if canon(r[col].get("value")) != canon(dv)]
    # Every departure carries its reason: when a family leaves the default and why, or the open question.
    spec, claims, opens, errs = departure_reasons(rows, default)
    if errs:
        print("departure_reasons.json: FAIL"); [print("  " + e) for e in errs]; return 1
    for r in rows:
        r["because"] = OrderedDict((col, claims.get((r["family"], col)) or "open") for col in r["departs"])
        departures += [(r["family"], col, "; ".join(claims.get((r["family"], col)) or ["open"]), canon(r[col].get("value"))) for col in r["departs"]]
    md_out = reasons_md(spec, claims, opens, rows, default) + "\n"
    by_count = Counter(len(r["departs"]) for r in rows)
    dep_out = ("# Every family against the default row (formal/derivation/family_default_row.json): one line per column in which a family departs.\n"
               "# A family with no line here is the default row in all of these columns. Generated by tools/build_family_model.py.\n"
               "# reason: the reasons of formal/derivation/departure_reasons.json that move the cell, or open; formal/family_model/DEPARTURES.md states each.\n"
               "family\tcolumn\treason\tvalue\n" + "".join(f"{f}\t{c}\t{w}\t{v}\n" for f, c, w, v in departures))
    cov = OrderedDict()
    SRC = ("cc-table", "code-v61", "generic", "prose", "mixed", "gap")
    for col in COLUMNS:
        cnt = Counter(r[col]["source"] for r in rows if col in r)
        cov[col] = OrderedDict((k, cnt.get(k, 0)) for k in SRC)
        if col in SUBKEYS:
            subcnt = Counter(v["source"] for r in rows if col in r for v in r[col].get("parts", {}).values())
            cov[col]["sub_cells"] = OrderedDict((k, subcnt.get(k, 0)) for k in SRC)
    reg_sha = hashlib.sha256(open(REG, "rb").read()).hexdigest()
    meta = OrderedDict([
        ("cc_section", "3.1 (the family model manifest, CIRISConstitution#189)"),
        ("version", "0-draft"), ("taxonomy_version", "11+1 v1"),
        ("registry_sha256", reg_sha), ("census", "CIRISPersist release-61.0.0 ea6ab724, #1130 comment 6563875341"),
        ("census_names", OrderedDict([("source", "formal/derivation/census_names.tsv"), ("rows", census_named),
                                      ("reading", "a census row whose name the text does not register: retired is not read and makes no family row; renamed is read as the text's family")])),
        ("columns", COLUMNS), ("families", len(rows)), ("coverage", cov),
        ("cites", OrderedDict([("source", "formal/derivation/cell_cites.tsv"), ("cells_cited", sum(1 for r in rows for c in r.values() if isinstance(c, dict) and c.get("cites"))),
                               ("citations", cited), ("reading", "a cell with `cites` is stated by those sections; `fills` marks a sentence that says more than the cell holds")])),
        ("placement", OrderedDict(list(placing.items()) + [("families_on_the_default", placed_by_default),
                                  ("reading", "a placement cell with rule default is the scope each row carries, chosen by its emitter; the audience of a row is the scopes entry for its cohort_scope; copy states whose audience a row joins because another row names it")])),
        ("body", OrderedDict([("source", "constitution/signed_object.tsv"), ("families_with_members", sum(1 for r in rows if isinstance(r["body"].get("value"), dict) and "members" in r["body"]["value"])),
                              ("presence_in_words", sorted(set(body_unread))),
                              ("members_from_text", OrderedDict([("in_cddl", body_text_n["yes"]), ("named_by_the_text_alone", body_text_n["no"])]))])),
        ("fold", OrderedDict([("default", fg.DEFAULT), ("every_family", fold_every), ("reader_defaults", reader_defaults),
                              ("typed_families", sum(1 for r in rows if r["fold"]["value"])),
                              ("statements", sum(len(r["fold"]["value"]) for r in rows)),
                              ("marks", OrderedDict(sorted(fold_marks.items()))), ("marks_total", sum(fold_marks.values()))])),
        ("conferral", OrderedDict([(col, OrderedDict(sorted(Counter(r[col].get("rule") or r[col]["source"] for r in rows).items()))) for col in ("confers", "binds_segment", "derived", "read_by")] +
                                  [("read_by_default", der_meta),
                                   ("reading", "rule default: the one stated default (confers: a claim or content confers nothing; read_by: the default fold and change, checked for none of the families it covers); shape: the family's consent parameters in formal/derivation/family_shapes.tsv; stated: a sentence for this family; class: every placeholder names no key by its registry class; cells: the family's own rule cells; gap: listed with what is missing")])),
        ("authorship", OrderedDict([("source", "formal/derivation/authorship_text.tsv"),
                                    ("families", OrderedDict((k, a_kind.get(k, 0)) for k in ("authored", "subject", "counted", "mixed", "gap"))),
                                    ("second_signers", OrderedDict([("families_with_roles", sum(1 for c in second.values() if c["value"])), ("families_author_only", sum(1 for c in second.values() if not c["value"])),
                                                                    ("roles", sum(len(c["value"]) for c in second.values())), ("roles_without_member", len(second_gap))])),
                                    ("reading", "authorship gives each family's rows as authored (one party authors; the payload carries author), subject (authored, and the author is the attested key: a statement whose iss is not the sub is refused) or counted (several statements over one payload, author null), arm by arm on the count column's selector keys; gap where the text gives both and no selector names the case. second_signers names each role whose statement over the same payload a row accepts besides the author's, and the payload member that names that party, or sub; a statement in no role is Invalid (CC 2.6.1.3)")])),
        ("standing", OrderedDict([("source", "formal/derivation/standing_text.tsv"), ("columns", list(STANDING_VALUES)),
                                  ("rules", st_meta), ("cells", st_counts), ("names_head_by_placement", nh_branches),
                                  ("reading", "source derived: the cell follows from the other columns by the rule of that name in rules; quote: a row of the table whose words stand verbatim in cc_ref; ruling: a ruled reading the text does not yet state for the family by name; open: no value, and needs states the sentence the text would need. A cell with per_selector gives its value by leaf or by act, `*` taking every other row. Two rules of subject_may_withdraw hold in every family and are no cell: affiliation_subject and legal_weight_act. withdraws is a composer row and no family: rules.`standing_act.withdraws` states how an end is recognised")])),
        ("default_row", OrderedDict([("columns", default), ("families_on_it", by_count.get(0, 0)),
                                     ("families_by_departures", OrderedDict((str(k), by_count[k]) for k in sorted(by_count))),
                                     ("reading", "a family's cell in one of these columns is the default unless the family is listed in departs; manifests/family_departures.tsv carries the departures alone")])),
        ("departure_reasons", OrderedDict([
            ("reasons", [OrderedDict([("id", rs["id"]), ("title", rs["title"]), ("when", rs["when"]), ("why", rs["why"]), ("basis", rs["basis"])] +
                                     ([("cc_ref", rs["cc_ref"]), ("quote", rs["quote"])] if rs["basis"] == "text" else []) +
                                     [("cells", sum(1 for v in claims.values() if rs["id"] in v))]) for rs in spec["reasons"]]),
            ("open", [OrderedDict([("family", f), ("column", c), ("question", q)]) for (f, c), q in opens.items()]),
            ("reading", "every departing cell names in because the reasons that move it, or open; a departure with no reason fails the build, and so does a reason whose cell sits on the default")])),
        ("reading", "every cell carries its source: cc-table (the CC classification), code-v61 (what persist's door enforces for this family), generic (the generic door's value, not the family's), prose (bespoke code outside the closed vocabulary), mixed (a compound cell whose parts differ; see parts), gap (nothing enforces; a value after the tag is the de-facto or target value). A signer rule the text gives where the code enforces none, or holds the family shut, is cc-table, with the census reading kept beside it as code; where the text gives one signer per stage the value is keyed by stage (per_stage). Census-only readings ride beside the CC columns as verbs_code, maintains_record_code, reference_code and reserved. A ruled version replaces every generic, prose, mixed and gap cell with a closed value and refuses what remains."),
    ])
    out = json.dumps(OrderedDict([("_meta", meta), ("rows", rows)]), indent=1, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != out: print("family_model.json is stale (run tools/build_family_model.py)"); return 1
        cur = open(DEPARTS, encoding="utf-8").read() if os.path.exists(DEPARTS) else ""
        if cur != dep_out: print("family_departures.tsv is stale (run tools/build_family_model.py)"); return 1
        cur = open(REASONS_MD, encoding="utf-8").read() if os.path.exists(REASONS_MD) else ""
        if cur != md_out: print("DEPARTURES.md is stale (run tools/build_family_model.py)"); return 1
    else:
        open(OUT, "w", encoding="utf-8").write(out)
        open(DEPARTS, "w", encoding="utf-8").write(dep_out)
        open(REASONS_MD, "w", encoding="utf-8").write(md_out)
    print(f"departure reasons: {len(spec['reasons'])} reasons move {len(claims)} cells; {len(opens)} open")
    print(f"placement: {placed_by_default} families take the default, the scope each row carries; {len(placing['scopes'])} audience rows, {len(placing['reach'])} on reach, {len(placing['moves'])} on what moves, {len(placing['copy'])} on copying")
    print(f"authorship: " + ", ".join(f"{k} {v}" for k, v in meta["authorship"]["families"].items()) + f"; second_signers: {meta['authorship']['second_signers']['families_with_roles']} families name roles, {len(second_gap)} roles with no member")
    for c in STANDING_VALUES:
        print(f"{c}: " + ", ".join(f"{k} {v}" for k, v in st_counts[c]["by_value"].items()) + "; by source: " + ", ".join(f"{k} {v}" for k, v in st_counts[c]["by_source"].items()))
    print(f"default row: {by_count.get(0, 0)} of {len(rows)} families are on it in all {len(default)} columns, {by_count.get(1, 0)} depart in one; {len(departures)} departures in all")
    print("conferral: " + "; ".join(f"{col} " + ", ".join(f"{k} {v}" for k, v in meta["conferral"][col].items()) for col in ("confers", "binds_segment", "derived", "read_by")))
    print(f"family_model: {len(rows)} families; coverage per column (cc-table/code-v61/generic/prose/mixed/gap): " +
          "; ".join(f"{k} {v['cc-table']}/{v['code-v61']}/{v['generic']}/{v['prose']}/{v['mixed']}/{v['gap']}" for k, v in cov.items()))
    return 0
if __name__ == "__main__":
    sys.exit(main())
