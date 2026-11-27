# TEST ARTEFACTS for the SCITT list (draft-moore-scitt-ciris-ceg-04, Appendix B.3): a pure ML-DSA-65 companion of a
# composite-signed CEG statement, under a registration key of its own that the issuer's composite key vouches for.
# Every key here is a TEST KEY from a fixed public seed. Nothing here is a registered wire shape: the vouch's
# dimension and members, the companion's header label and its payload map are PROPOSALS for the group.
#   python3 -I gen_scitt_companion.py <path to CIRISVerify src/ciris-verify-core/tests/vectors/edition2>
import base64, contextlib, hashlib, io, json, os, runpy, sys, tempfile
from dilithium_py.ml_dsa import ML_DSA_65

e2 = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
cwd = os.getcwd()
with tempfile.TemporaryDirectory() as scratch, contextlib.redirect_stdout(io.StringIO()):
    os.chdir(scratch)
    g = runpy.run_path(os.path.join(e2, "gen_row_statements_v5.py"))
    os.chdir(cwd)
Key, statement, enc, Tag = g["Key"], g["statement"], g["enc"], g["Tag"]
sha = lambda b: hashlib.sha256(b).digest()
b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=").decode()

# ---- the original: the pinned B.3 statement (row_statements_v4.json, valid[0], authored_score) ----
with open(os.path.join(e2, "row_statements_v4.json")) as f:
    B3 = json.load(f)["valid"][0]
ORIG = bytes.fromhex(B3["statement_hex"])
assert len(ORIG) == 3864 and B3["statement_id_hex"] == "7d868e399743467fd3f01b0c92ab3e10a442ad1141f68a54261dd558c111bad4"
ORIG_ID = bytes.fromhex(B3["statement_id_hex"])
A = Key(B3["key_seed"])                        # the test issuer: composite, ML-DSA seed [1]*32, Ed25519 seed [101]*32
assert A.iss == B3["iss"]

# ---- 1. the registration key: ML-DSA-65 alone, from its own seed, used for nothing else ----
REG_SEED = hashlib.sha256(b"CIRIS TEST registration key 1 (SCITT companion demo)").digest()
assert REG_SEED != A.ml_seed
reg_pk, reg_sk = ML_DSA_65.key_derive(REG_SEED)
assert len(reg_pk) == 1952 and reg_pk != A.ml_pk
ALG_ML_DSA_65 = -49                            # RFC 9964
REG_COSE_KEY = {1: 7, 3: ALG_ML_DSA_65, -1: reg_pk}       # AKP: kty 7, alg, pub
REG_THUMB = sha(enc(REG_COSE_KEY))             # RFC 9679 over the required members kty, alg, pub
REG_SUB = b64(REG_THUMB)                       # the key-segment form a trust:accepts service edge uses for a key

# ---- 2. the vouch: the issuer's composite statement naming the registration key ----
T = 1763200000000 + 86_400_000                 # one day after the vector epoch (2025-11-16), a fixed instant
UNTIL = 1826358400000                          # 2027-11-16T09:46:40Z: the term spans the demonstration (two years)
assert UNTIL - T == 2 * 31_536_000_000
VOUCH_PAYLOAD = {
    "author": A.iss,
    "dimension": "trust:registers:v1",
    "registration_key": REG_COSE_KEY,
    "registers": "companions",
    "delegation_valid_from": T,
    "delegation_valid_until": UNTIL,
    "asserted_at": T,
}
VOUCH, vouch_prot, vouch_plb = statement(A, REG_SUB, "delegates_to", "trust:.job:.version", VOUCH_PAYLOAD)
VOUCH_ID = sha(enc(["CEG-statement-id/2", vouch_prot, vouch_plb]))
VOUCH_ROW = sha(enc(["CEG-row/2", "delegates_to", "trust:.job:.version", REG_SUB, A.iss, vouch_plb]))

# ---- 3. the companion, two placements ----
LABEL_COMPANION_OF = -70010                    # private use, beside CEG's -70001..-70003: the original's statement id
COMPANION_SUB = "ceg-companion:" + ORIG_ID.hex()
COMPANION_IAT = 1795705436                      # when the companions were minted, seconds (2026-11-26T15:03:56Z); fixed here so the bytes reproduce
assert T // 1000 <= COMPANION_IAT < UNTIL // 1000, "the companion is made inside the vouch's term"
LABEL_COMPANION_OF_SHA256 = -70011             # private use, beside -70010: SHA-256 of the original's full bytes
COMPANION_C_IAT = 1795815890                    # when variant (c) was minted (2026-11-27T21:44:50Z); fixed so the bytes reproduce
assert T // 1000 <= COMPANION_C_IAT < UNTIL // 1000
def companion(extra_prot, payload, iat=COMPANION_IAT):
    prot = {1: ALG_ML_DSA_65, 4: REG_THUMB, 15: {1: A.iss, 2: COMPANION_SUB, 6: iat}}
    prot.update(extra_prot)
    pb = enc(prot)
    tbs = enc(["Signature1", pb, b"", payload])
    sig = ML_DSA_65.sign(reg_sk, tbs, ctx=b"", deterministic=True)
    assert len(sig) == 3309
    assert ML_DSA_65.verify(reg_pk, tbs, sig, ctx=b"")
    assert not ML_DSA_65.verify(A.ml_pk, tbs, sig, ctx=b""), "must not verify under the composite's ML-DSA half"
    return enc(Tag(18, [pb, {}, payload, sig])), pb, tbs, sig
COMP_A, pa, tbs_a, sig_a = companion({LABEL_COMPANION_OF: ORIG_ID}, VOUCH_ID)
PAYLOAD_B = enc({"statement_id": ORIG_ID, "statement_sha256": sha(ORIG), "vouch_statement_id": VOUCH_ID})
COMP_B, pb_, tbs_b, sig_b = companion({3: "application/cbor"}, PAYLOAD_B)
# (c) header placement carrying what (b) carries: the id AND the digest of the original's full bytes
COMP_C, pc_, tbs_c, sig_c = companion({LABEL_COMPANION_OF: ORIG_ID, LABEL_COMPANION_OF_SHA256: sha(ORIG)}, VOUCH_ID,
                                      iat=COMPANION_C_IAT)

out = {
    "_meta": {
        "status": "TEST ARTEFACTS, NOT FOR PRODUCTION. Every key is derived from a public seed in this file. The vouch's "
                  "dimension and members, the header label and the payload map are proposals, registered nowhere.",
        "generator": "gen_scitt_companion.py: dilithium_py (FIPS 204) for ML-DSA-65; CIRISVerify's independent "
                     "gen_row_statements_v5.py for the CBOR encoder and the composite signer.",
        "signing": "ML-DSA-65 pure (no pre-hash), empty context, DETERMINISTIC variant (rnd = 32 zero bytes) so the bytes "
                   "reproduce. A production signer uses the hedged variant; a verifier cannot tell them apart.",
        "cose_sign1": "tag 18 [protected, {}, payload, signature]; signature over the Sig_structure "
                      "[\"Signature1\", protected, h'', payload] (RFC 9052), deterministically encoded.",
    },
    "original": {
        "what": "draft-moore-scitt-ciris-ceg-04 Appendix B.3; CIRISVerify row_statements_v4.json valid[0] authored_score",
        "statement_id_hex": ORIG_ID.hex(), "sha256_hex": sha(ORIG).hex(), "length": len(ORIG),
        "iss": A.iss, "issuer_kid_hex": A.kid.hex(),
        "issuer_seeds": "TEST: ML-DSA-65 seed 01*32, Ed25519 seed 65*32 (hex)",
        "statement_hex": ORIG.hex(),
    },
    "registration_key": {
        "seed_hex": REG_SEED.hex(), "seed_from": "SHA-256(\"CIRIS TEST registration key 1 (SCITT companion demo)\")",
        "alg": ALG_ML_DSA_65, "public_key_hex": reg_pk.hex(),
        "cose_key_hex": enc(REG_COSE_KEY).hex(),
        "thumbprint_hex": REG_THUMB.hex(), "thumbprint_b64url": REG_SUB,
        "thumbprint_of": "SHA-256 over the deterministic encoding of {1: 7, 3: -49, -1: pub} (RFC 9679; AKP required members)",
        "not_the_composite_half": reg_pk != A.ml_pk,
    },
    "vouch": {
        "row_type": "delegates_to", "family": "trust:.job:.version", "dimension": "trust:registers:v1",
        "cwt_iss": A.iss, "cwt_sub": REG_SUB,
        "payload_members": ["author", "dimension", "registration_key", "registers", "delegation_valid_from",
                            "delegation_valid_until", "asserted_at"],
        "statement_id_hex": VOUCH_ID.hex(), "row_id_hex": VOUCH_ROW.hex(), "sha256_hex": sha(VOUCH).hex(),
        "length": len(VOUCH), "payload_hex": vouch_plb.hex(), "statement_hex": VOUCH.hex(),
    },
    "companion_cwt_claims": {"iss": A.iss, "sub": COMPANION_SUB, "iat": COMPANION_IAT},
    "companion_header": {
        "placement": "the original's statement id in the PROTECTED header, label %d; payload = the vouch's statement id" % LABEL_COMPANION_OF,
        "protected_hex": pa.hex(), "payload_hex": VOUCH_ID.hex(), "to_be_signed_hex": tbs_a.hex(),
        "signature_sha256_hex": sha(sig_a).hex(), "sha256_hex": sha(COMP_A).hex(), "length": len(COMP_A),
        "cose_sign1_hex": COMP_A.hex(),
    },
    "companion_payload": {
        "placement": "the original's statement id in the PAYLOAD: {statement_id, statement_sha256, vouch_statement_id}; cty application/cbor",
        "protected_hex": pb_.hex(), "payload_hex": PAYLOAD_B.hex(), "to_be_signed_hex": tbs_b.hex(),
        "signature_sha256_hex": sha(sig_b).hex(), "sha256_hex": sha(COMP_B).hex(), "length": len(COMP_B),
        "cose_sign1_hex": COMP_B.hex(),
    },
    "companion_header_digest": {
        "placement": "the original's statement id (label %d) AND the SHA-256 of its full bytes (label %d) in the "
                     "PROTECTED header; payload = the vouch's statement id" % (LABEL_COMPANION_OF, LABEL_COMPANION_OF_SHA256),
        "iat": COMPANION_C_IAT,
        "protected_hex": pc_.hex(), "payload_hex": VOUCH_ID.hex(), "to_be_signed_hex": tbs_c.hex(),
        "signature_sha256_hex": sha(sig_c).hex(), "sha256_hex": sha(COMP_C).hex(), "length": len(COMP_C),
        "cose_sign1_hex": COMP_C.hex(),
    },
    "checks_made_by_the_generator": {
        "each_companion_verifies_under_registration_key": True,
        "each_companion_fails_under_composite_ml_dsa_half": True,
        "issuer_composite_ml_dsa_half_sha256_hex": sha(A.ml_pk).hex(),
    },
}
with open(os.path.join(here, "scitt_companion_test_v1.json"), "w") as f:
    json.dump(out, f, indent=1, sort_keys=True); f.write("\n")
for n, b in (("original_b3.cose", ORIG), ("vouch.cose", VOUCH), ("companion_header.cose", COMP_A),
             ("companion_payload.cose", COMP_B),
             ("companion_header_digest.cose", COMP_C), ("registration_key.cosekey", enc(REG_COSE_KEY))):
    with open(os.path.join(here, n), "wb") as f: f.write(b)
print("ok", len(VOUCH), len(COMP_A), len(COMP_B), len(COMP_C))
