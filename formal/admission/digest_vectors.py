#!/usr/bin/env python3
"""
digest_vectors.py: known answers for the three derived digests of CC 2.7.11, written to digest_vectors.json.

  CEG-call/2      a call's fingerprint: SHA-256 over CDE(["CEG-call/2", verb, tool, arguments, channel])
  CEG-review/2    a review record's digest: SHA-256 over CDE(["CEG-review/2", record])
  CEG-profile/2   a profile's digest: SHA-256 over CDE(["CEG-profile/2", d0, d1, ..., dn])

Each digest is written [-16, digest]. CDE is CBOR's deterministic encoding (RFC 8949 4.2.1): shortest integer and
length heads, definite lengths, map keys sorted by the bytewise order of their encodings. No float is written. The
arguments of a call come from JSON: object to map, array to array, string to text, true, false and null to simple
values 21, 20 and 22. A number is read by its exact decimal value: integral, an integer; otherwise CBOR tag 4
[exponent, mantissa], normalised (the exponent negative, the mantissa not divisible by ten). An integer or a mantissa
outside CBOR's integer range is refused, call_argument_unrepresentable. A secret stands as its reference text.

The encoder is self-contained (standard library) and is checked first against the examples of RFC 8949 Appendix A
(its floats excepted) and the decimal fraction of 3.4.4. A planted reader that judges a number by its lexical form,
or rounds it through binary64, must change the vectors, every run.

  python3 -I digest_vectors.py           compare with digest_vectors.json; exit 1 on a difference
  python3 -I digest_vectors.py --write   write digest_vectors.json
"""
from decimal import Decimal
import hashlib
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLANT = set()


def _head(major, n):
    if n < 24: return bytes([major << 5 | n])
    for ai, fmt, lim in ((24, ">B", 1 << 8), (25, ">H", 1 << 16), (26, ">I", 1 << 32), (27, ">Q", 1 << 64)):
        if n < lim: return bytes([major << 5 | ai]) + struct.pack(fmt, n)
    raise ValueError("integer out of range")


class Tag:
    """A CBOR tag over a value: tag 4 is a decimal fraction [exponent, mantissa] (RFC 8949 3.4.4)."""
    def __init__(self, tag, value): self.tag, self.value = tag, value


def cde(v):
    if v is None: return b"\xf6"
    if v is True: return b"\xf5"
    if v is False: return b"\xf4"
    if isinstance(v, int): return _head(0, v) if v >= 0 else _head(1, -1 - v)
    if isinstance(v, float): raise TypeError("no float is written anywhere in this form")
    if isinstance(v, Tag): return _head(6, v.tag) + cde(v.value)
    if isinstance(v, bytes): return _head(2, len(v)) + v
    if isinstance(v, str):
        b = v.encode("utf-8")
        return _head(3, len(b)) + b
    if isinstance(v, (list, tuple)): return _head(4, len(v)) + b"".join(cde(x) for x in v)
    if isinstance(v, dict):
        items = sorted((cde(k), cde(x)) for k, x in v.items())
        return _head(5, len(items)) + b"".join(k + x for k, x in items)
    raise TypeError(type(v))


def cset(xs):
    """A set: its elements sorted by the bytewise order of their encodings, no duplicate (CC 2.6.1.2)."""
    out = sorted({cde(x): x for x in xs}.items())
    return [x for _, x in out]


class Unrepresentable(ValueError):
    """call_argument_unrepresentable: an integral value outside CBOR's integer range."""


INT_MIN, INT_MAX = -(2 ** 64), 2 ** 64 - 1      # CBOR's major types 0 and 1


def number(lexeme):
    """A JSON number by its exact decimal value, never by its lexical form and never through binary64:
      integral by value, within CBOR's integer range: that integer (so 1e2 is 100 and -0.0 is 0);
      integral by value, outside that range: refused;
      otherwise its exact decimal as tag 4 [exponent, mantissa], normalised: the exponent negative and the mantissa
      not divisible by ten; a mantissa outside CBOR's integer range is refused.
    The 10^20 guard applies to integral values only: it refuses one that could not fit without expanding it."""
    if "lexical_numbers" in PLANT:
        return int(lexeme) if lexeme.lstrip("-").isdigit() else Tag(4, [-1, int(float(lexeme) * 10)])
    d = Decimal(lexeme)
    if d == d.to_integral_value():
        if d.adjusted() > 20: raise Unrepresentable(lexeme)      # |value| >= 10^20 > 2^64
        n = int(d)
        if not INT_MIN <= n <= INT_MAX: raise Unrepresentable(lexeme)
        return n
    sign, digits, exp = d.as_tuple()
    m = int("".join(map(str, digits))) * (-1 if sign else 1)
    while m % 10 == 0:                                            # normalise; m != 0 since the value is not integral
        m //= 10; exp += 1
    if not INT_MIN <= m <= INT_MAX: raise Unrepresentable(lexeme)
    return Tag(4, [exp, m])


def from_json(text):
    """JSON arguments to the value the fingerprint encodes."""
    return json.loads(text, parse_float=number, parse_int=number)


def digest(label, *rest):
    enc = cde([label, *rest])
    return enc, [-16, hashlib.sha256(enc).digest()]


# RFC 8949 Appendix A, the examples this encoder must reproduce
# RFC 8949 Appendix A and 3.4.4: the examples this encoder must reproduce (every one but the floats, which this form
# never writes), and the decimal fraction 273.15
RFC = [(0, "00"), (23, "17"), (24, "1818"), (100, "1864"), (1000, "1903e8"), (1000000, "1a000f4240"),
       (1000000000000, "1b000000e8d4a51000"), (18446744073709551615, "1bffffffffffffffff"), (-1, "20"), (-100, "3863"),
       (-1000, "3903e7"), (-18446744073709551616, "3bffffffffffffffff"), (False, "f4"), (True, "f5"), (None, "f6"),
       ("", "60"), ("IETF", "6449455446"), ("\u00fc", "62c3bc"), ([], "80"), ([1, [2, 3], [4, 5]], "8301820203820405"),
       ({"a": 1, "b": [2, 3]}, "a26161016162820203"), (b"\x01\x02\x03\x04", "4401020304"),
       (Tag(4, [-2, 27315]), "c48221196ab3")]


def rfc_ok():
    return all(cde(v).hex() == h for v, h in RFC)


def row_ref(n): return [2, [-16, bytes([n]) * 32]]


def vectors():
    out = {"call": [], "review": [], "profile": []}
    calls = [
        ("a secret stands as its reference", "tool", "http_get",
         '{"url": "https://example.org/a", "token": "{SECRET:7f3c}"}', "c1"),
        ("integers, a negative and a large one", "tool", "db_query", '{"limit": 3, "offset": -42, "id": 4294967296}', "c1"),
        ("non-integral numbers as exact decimals (tag 4), and an integral number read as an integer",
         "tool", "thermostat", '{"temperature": 0.5, "ratio": 1.10, "gain": 100000.5, "steps": 2.0, "bias": -273.15}', "c1"),
        ("null, true and false", "tool", "search", '{"filter": null, "dry_run": true, "safe": false}', "c1"),
        ("nested maps and arrays", "tool", "post",
         '{"body": {"tags": ["b", "a"], "meta": {"z": -1, "a": [1, {"k": "v"}]}}, "to": "room"}', "c1"),
        ("no channel: the empty text", "tool", "clock", "{}", ""),
        ("1e2 is the integer 100", "tool", "n", '{"x": 1e2}', "c1"),
        ("9007199254740993.0 is that integer exactly, not the nearest binary64", "tool", "n", '{"x": 9007199254740993.0}', "c1"),
        ("-0.0 is integral by value: the integer 0", "tool", "n", '{"x": -0.0}', "c1"),
        ("0.1 is its exact decimal, 4([-1, 1])", "tool", "n", '{"x": 0.1}', "c1"),
        ("1 + 2^-53 written out exactly: never rounded; its 54-digit mantissa exceeds CBOR's integer range, so refused",
         "tool", "n", '{"x": 1.00000000000000011102230246251565404236316680908203125}', "c1"),
        ("a long mantissa within range: 1.0000000000000002220 is 4([-18, 1000000000000000222]), never rounded",
         "tool", "n", '{"x": 1.0000000000000002220}', "c1"),
        ("1.0e-1 and 0.10 are the same decimal as 0.1", "tool", "n", '{"x": 1.0e-1, "y": 0.10}', "c1"),
        ("the largest CBOR integer, 2^64 - 1", "tool", "n", '{"x": 18446744073709551615}', "c1"),
        ("the least CBOR integer, -2^64", "tool", "n", '{"x": -18446744073709551616}', "c1"),
        ("1e400 is integral and outside CBOR's integer range: refused", "tool", "n", '{"x": 1e400}', "c1"),
        ("2^64 is outside CBOR's integer range: refused", "tool", "n", '{"x": 18446744073709551616}', "c1"),
        ("a decimal whose mantissa is 2^64 is refused", "tool", "n", '{"x": 0.18446744073709551616}', "c1"),
    ]
    for what, verb, tool, args, chan in calls:
        v = {"what": what, "verb": verb, "tool": tool, "arguments_json": args, "channel": chan}
        try:
            enc, d = digest("CEG-call/2", verb, tool, from_json(args), chan)
            v.update(cde_hex=enc.hex(), digest=[-16, d[1].hex()])
        except Unrepresentable:
            v.update(refused="call_argument_unrepresentable")
        out["call"].append(v)
    fp = digest("CEG-call/2", "tool", "http_get", from_json(calls[0][3]), "c1")[1]
    obj = {"fingerprint": fp, "thought": "th-1", "outcome": "objected", "faculties": cset(["optimization_veto"])}
    obj_d = digest("CEG-review/2", obj)[1]
    records = [
        ("an objection by one faculty", obj),
        ("a pass of all four, nothing derived from untrusted input",
         {"fingerprint": fp, "thought": "th-1", "outcome": "passed",
          "faculties": cset(["coherence", "entropy", "epistemic_humility", "optimization_veto"])}),
        ("a pass that discharges an objection to the same draft, carries one to another, and declares its derivation",
         {"fingerprint": fp, "thought": "th-1", "outcome": "passed",
          "faculties": cset(["coherence", "entropy", "epistemic_humility", "optimization_veto"]),
          "discharges": cset([[obj_d, row_ref(9)]]), "considered": cset([[-16, bytes([4]) * 32]]),
          "derived_from": cset(["request", "tool_output"])}),
    ]
    for what, rec in records:
        enc, d = digest("CEG-review/2", rec)
        out["review"].append({"what": what, "record_cde_hex": cde(rec).hex(), "cde_hex": enc.hex(), "digest": [-16, d[1].hex()]})
    links = [[-16, hashlib.sha256(b"base template manifest").digest()],
             [-16, hashlib.sha256(b"amendment one").digest()], [-16, hashlib.sha256(b"amendment two").digest()]]
    for what, ds in (("the base link alone", links[:1]), ("the base and two amendments, in chain order", links),
                     ("the same three in another order: another digest", [links[0], links[2], links[1]])):
        enc, d = digest("CEG-profile/2", *ds)
        out["profile"].append({"what": what, "links": [[-16, x[1].hex()] for x in ds], "cde_hex": enc.hex(),
                               "digest": [-16, d[1].hex()]})
    return out


def main(argv):
    ok = rfc_ok()
    clean = vectors()
    caught = True
    PLANT.add("lexical_numbers")
    try:
        caught = caught and vectors() != clean
    except (OverflowError, ValueError):
        pass
    PLANT.discard("lexical_numbers")
    text = json.dumps({"_note": "Known answers for CC 2.7.11's derived digests; written by digest_vectors.py.",
                       **vectors()}, indent=1, sort_keys=True) + "\n"
    path = os.path.join(HERE, "digest_vectors.json")
    if "--write" in argv:
        open(path, "w", encoding="utf-8").write(text)
    same = os.path.exists(path) and open(path, encoding="utf-8").read() == text
    n = sum(len(v) for v in vectors().values())
    print(f"digest vectors: {n} known answers; RFC 8949 Appendix A examples {'reproduced' if ok else 'NOT reproduced'}; "
          f"the lexical number reader {'caught' if caught else 'missed'}; file {'current' if same else 'stale'}")
    return 0 if ok and caught and same else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
