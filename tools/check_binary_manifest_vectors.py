#!/usr/bin/env python3
"""The build manifest blob's vendored files are the ones pinned, and the text's tree rule gives their roots.

manifests/binary_manifest_v1.cddl and manifests/binary_manifest_v1_vectors.json are the verification library's
(CC 3.1.2.1, CC 2.6.1.12): this repo vendors them and writes none of their content. Two things are checked here.

1. Each vendored file has the SHA-256 recorded in PINS, with the commit it was taken at. A change to a file
   without a change to its pin fails, so the files move only by a deliberate re-pin.
2. The Merkle tree of CC 3.1.2.1, written here from the text's words and from nothing of the vendored
   generator, gives the root of every `merkle_tree` case: a leaf is SHA-256 over 0x00 and the leaf's bytes, a
   parent is SHA-256 over 0x01, the left child and the right child, and a leaf count that is no power of two
   is padded by repeating the last leaf. A single leaf is its own root. The same rule serves a locale manifest
   and a function table, so one set of known answers is pinned for both.

--self-test plants a tree that pads by RFC 6962's split instead and requires at least one case to refuse it.

stdlib only. Exit 0 when every check holds.
"""
import hashlib, json, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SOURCE = "CIRISAI/CIRISVerify, branch feat/fsd008-blob, commit 231b9e4, src/ciris-verify-core/tests/vectors/edition2/build_manifest/"
PINS = {
    "manifests/binary_manifest_v1.cddl": "07bbe78801ea75a8c245e0e4194bf49ea859f0c711fac59c0af4b7e5b4b09806",
    "manifests/binary_manifest_v1_vectors.json": "468cce628e4f35232bd3b367f68f6e92adf30b6937525f2240e5bf7314446f58",
}
MAX_BYTES = 1048576                                      # build_manifest_max_bytes (constitution/constants.tsv)


def text_root(leaves):
    """CC 3.1.2.1: prefixes 0x00 and 0x01; pad by repeating the last leaf to the next power of two."""
    level = [hashlib.sha256(b"\x00" + leaf).digest() for leaf in leaves]
    size = 1
    while size < len(level):
        size *= 2
    level += [level[-1]] * (size - len(level))
    while len(level) > 1:
        level = [hashlib.sha256(b"\x01" + level[i] + level[i + 1]).digest() for i in range(0, len(level), 2)]
    return level[0]


def split_root(leaves):
    """The planted rule: RFC 6962's split of an odd count, which CC 3.1.2.1 says this tree is not."""
    hs = [hashlib.sha256(b"\x00" + leaf).digest() for leaf in leaves]

    def mth(h):
        if len(h) == 1:
            return h[0]
        k = 1
        while k * 2 < len(h):
            k *= 2
        return hashlib.sha256(b"\x01" + mth(h[:k]) + mth(h[k:])).digest()
    return mth(hs)


def main():
    bad = []
    for rel, want in PINS.items():
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            bad.append(f"{rel}: missing")
            continue
        got = hashlib.sha256(open(p, "rb").read()).hexdigest()
        if got != want:
            bad.append(f"{rel}: sha256 {got}, pinned {want}")
    vec = json.load(open(os.path.join(ROOT, "manifests", "binary_manifest_v1_vectors.json"), encoding="utf-8"))
    if vec.get("max_blob_len") != MAX_BYTES:
        bad.append(f"max_blob_len is {vec.get('max_blob_len')}, and build_manifest_max_bytes is {MAX_BYTES}")
    consts = open(os.path.join(ROOT, "constitution", "constants.tsv"), encoding="utf-8").read()
    if "build_manifest_max_bytes\t1,048,576 bytes" not in consts:
        bad.append("constitution/constants.tsv does not state build_manifest_max_bytes as 1,048,576 bytes")
    cases = vec["merkle_tree"]
    ok = 0
    for c in cases:
        leaves = [bytes.fromhex(x) for x in c["leaves_hex"]]
        if len(leaves) != c["leaf_count"]:
            bad.append(f"merkle case {c['id']}: {len(leaves)} leaves, leaf_count {c['leaf_count']}")
        if text_root(leaves).hex() == c["root_hex"]:
            ok += 1
        else:
            bad.append(f"merkle case {c['id']}: the text's rule gives another root")
    counts = sorted(c["leaf_count"] for c in cases)
    if "--self-test" in sys.argv:
        caught = sum(split_root([bytes.fromhex(x) for x in c["leaves_hex"]]).hex() != c["root_hex"] for c in cases)
        if not caught:
            bad.append("deliberate break not caught: a tree that splits an odd count passed every case")
        print(f"binary manifest vectors: the planted split rule is refused by {caught} of {len(cases)} cases")
    print(f"binary manifest vectors: {len(PINS)} files at their pins ({SOURCE}); the text's tree rule gives "
          f"{ok} of {len(cases)} roots, leaf counts {counts}; {len(vec.get('valid', []))} valid blobs and "
          f"{len(vec.get('refusals', []))} refusals vendored; {len(bad)} error(s)")
    for b in bad:
        print("binary manifest vectors: error: " + b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
