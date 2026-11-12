#!/usr/bin/env python3
"""
CC — the change grammar: what a row that replaces, withdraws or removes may do, as data.

A change is a list of items. Each item governs one verb or one leaf of a family, under an optional condition,
and states who may sign the changing row, how it names the row it changes, which members may move and in what
direction, which rows it displaces, what it does to rows that depended on the old one, and what follows for
keys. Used by tools/build_transitions.py, which reads formal/derivation/change_text.tsv.

    change := item *( " ; " item )
    item   := on [ "[" atom *( "&" atom ) "]" ] ": " clause *( ", " clause )
    clause := "by=" BY | "link=" ( "ranked:" | "chained:" ) MEMBER | "field=" MEMBER ":" DIR | "reach=" REACH
            | "after=" FAMILY | "cascade=" FAMILY "/" REL ":" EFFECT | "key=" KEY | "refuse=" TOKEN

Tokens that name something no other vocabulary does are returned as marks and counted where they are used.

Run: python3 tools/change_grammar.py
"""
import re

VERBS = ("attest", "authorize", "replace", "withdraw", "recant")
BY = ("same_attester", "none", "cosigned", "cosigned_prior", "committed_key", "substrate")
DIRS = ("any", "frozen", "shrink", "grow_signed", "lower", "no_weaker", "as_attest")
REACH = ("own_prior", "other_attester", "below_seq", "whole")
RELS = ("by", "under", "about", "ref", "over")
EFFECTS = ("stand", "lapsed", "withdrawn", "stop", "discharged", "forfeited")
KEYS = ("rekey_walk", "next_seal", "at_seat", "stop_wrap", "rotate_epoch", "none")
BARE_ATOMS = ("entrenched", "stalled", "ephemeral", "cosigned", "recovery")
KEYED_ATOMS = ("grade", "subkind", "scope", "seat", "last", "axis")
SCOPES = ("self", "family", "affiliations", "community", "federation", "accord", "public")
MARKED = ("recovery", "cosigned_prior", "committed_key", "forfeited", "no_weaker")


class ChangeError(ValueError):
    pass


def parse(s):
    """A change string -> (items, marks). Raises ChangeError on anything outside the grammar."""
    items, marks = [], []
    for raw in s.strip().split(" ; "):
        m = re.fullmatch(r"([a-z_]+)(?:\[([^\]]+)\])?: (.+)", raw)
        if not m:
            raise ChangeError(f"item {raw!r}")
        on, cond, body = m.groups()
        atoms = []
        for a in (cond.split("&") if cond else []):
            k, _, v = a.partition(":")
            if (not v and k not in BARE_ATOMS) or (v and (k not in KEYED_ATOMS or not re.fullmatch(r"[a-z_|]+", v))):
                raise ChangeError(f"condition {a!r}")
            if k == "scope" and not set(v.split("|")) <= set(SCOPES):
                raise ChangeError(f"scope {v!r}")
            if k in MARKED: marks.append(k)
            atoms.append({"test": k, "values": v.split("|") if v else None})
        clauses = []
        for c in body.split(", "):
            k, eq, v = c.partition("=")
            if not eq:
                raise ChangeError(f"clause {c!r}")
            d = {"clause": k}
            if k == "by" and v in BY: d["by"] = v
            elif k == "link" and re.fullmatch(r"(ranked|chained):[a-z_]+", v): d["how"], d["member"] = v.split(":")
            elif k == "field" and re.fullmatch(r"[A-Za-z_]+:[a-z_]+", v) and v.split(":")[1] in DIRS: d["member"], d["dir"] = v.split(":")
            elif k == "reach" and v in REACH: d["reach"] = v
            elif k == "after": d["family"] = v
            elif k == "cascade":
                mc = re.fullmatch(r"(.+)/([a-z]+):([a-z_]+)(?::([a-z_]+))?", v)
                if not mc or mc.group(2) not in RELS or not (mc.group(3) in EFFECTS and not mc.group(4) or mc.group(3) == "void_after" and mc.group(4)):
                    raise ChangeError(f"cascade {v!r}")
                d.update(family=mc.group(1), rel=mc.group(2), effect=mc.group(3), member=mc.group(4))
            elif k == "key" and v in KEYS: d["key"] = v
            elif k == "refuse" and re.fullmatch(r"[a-z_0-9]+", v): d["token"] = v
            else:
                raise ChangeError(f"clause {c!r}")
            for x in (d.get("by"), d.get("dir"), d.get("effect")):
                if x in MARKED: marks.append(x)
            clauses.append(d)
        items.append({"on": on, "when": atoms, "clauses": clauses})
    return items, marks


def closure(items, voc, family_ok):
    """What a parsed change names outside the vocabularies `voc` (families, roles, tokens)."""
    bad = []
    for it in items:
        for a in it["when"]:
            if a["test"] in ("seat", "last") and not set(a["values"]) <= voc["roles"] | {"seat"}:
                bad.append(f"role {a['values']}")
        for c in it["clauses"]:
            fam = c.get("family")
            if fam and fam != "*" and not family_ok(fam, voc["families"]): bad.append(f"family {fam}")
            if c.get("token") and c["token"] not in voc["tokens"]: bad.append(f"refusal token {c['token']}")
    return bad


def self_test():
    good = ["replace: by=same_attester, link=ranked:references_attestation_id, reach=own_prior ; withdraw: cascade=*/ref:stand",
            "widening[stalled&recovery]: field=members:grow_signed, field=M:frozen",
            "attest: cascade=*/by:void_after:revoked_after",
            "removal[scope:community|affiliations]: key=rotate_epoch",
            "replace[seat:serve]: after=transport:canonical_rebind, refuse=serve_transit_pair_rotation_before_rebind"]
    bad = ["replace by=none", "replace: by=anyone", "replace[scope:galaxy]: by=none", "replace: field=members:sideways", "withdraw: cascade=*/near:stand", "replace: key=melt"]
    for g in good: parse(g)
    n = 0
    for g in bad:
        try: parse(g)
        except ChangeError: n += 1
    assert n == len(bad), f"{len(bad) - n} malformed changes parsed"
    assert parse(good[1])[1] == ["recovery"]
    print(f"change grammar: {len(good)} forms parse, {len(bad)} malformed forms refused")


if __name__ == "__main__":
    self_test()
