SCITT companion demo: TEST ARTEFACTS ONLY
==========================================
Made 2026-11-26 (vouch re-minted the same day with a term through 2027-11-16) from CIRISVerify v23.7.0's vector tooling. Every key is derived from a public seed
(scitt_companion_test_v1.json states each). Nothing here is a registered
wire shape; three things are proposals and are marked PROPOSAL below.

Files (sha256)
  ec5d05875122c5043d18db3225737c0e977f30d80d3d9f4c13c1768aa7c60dab  original_b3.cose          3864 bytes
  8c12109f2b62bd900f53c42565278f23ba5e318ee03f39f4e27a65caa85bd805  vouch.cose                5854 bytes
  2efa15685e987f5e2ae453a24c706c7ffab5b1a85bab965b743895fb45fde1ab  companion_header.cose     3598 bytes
  ac09afb3bb2013402e68f5818f0ef5a105fed0e67a03d8f9389debe558977b7e  companion_payload.cose    3697 bytes
  82532da1d773d07462954bf95b9a82fbddfb850fda045b76c791bca41ad2007c  registration_key.cosekey  1962 bytes
  ddfdba4aab6823a160a1fb264bdd91cdecd407c39fa49e6ba0dc113ad3412d8d  scitt_companion_test_v1.json (all of the above in hex, with ids)
To reproduce: check out CIRISVerify at tag v23.7.0 (commit aae516327d1527fdc5ed4e735d6409493db5986f) and run
  python3 -I gen_scitt_companion.py <checkout>/src/ciris-verify-core/tests/vectors/edition2
with the Python packages dilithium-py and cryptography installed. The generator reads two files of that tag,
gen_row_statements_v5.py and row_statements_v4.json, and nothing outside it. It writes the six files beside itself.
  gen_scitt_companion.py   the generator (Python: dilithium_py for ML-DSA-65; CIRISVerify's gen_row_statements_v5.py
                           for the CBOR encoder and the composite signer)

1. The original
   draft-moore-scitt-ciris-ceg-04 Appendix B.3 = CIRISVerify row_statements_v4.json valid[0] "authored_score".
   Statement id 7d868e399743467fd3f01b0c92ab3e10a442ad1141f68a54261dd558c111bad4. Unchanged, byte for byte.
   Issuer (test): composite ML-DSA-65-Ed25519, seeds 01*32 and 65*32 (hex);
   iss urn:ietf:params:oauth:ckt:sha-256:1vCVtzih4Y-2L6kkeANhicuJQgOUbUxxpS2bJ7QRdGM.

2. The registration key
   ML-DSA-65 alone, seed = SHA-256("CIRIS TEST registration key 1 (SCITT companion demo)"), used for nothing else.
   It is NOT the composite's ML-DSA component key (different seed, different public key; checked).
   COSE_Key {1: 7 (AKP), 3: -49 (ML-DSA-65, RFC 9964), -1: public key (1952 bytes)}.
   Thumbprint (RFC 9679, SHA-256 over the deterministic encoding of exactly those three members):
     hex 82532da1d773d07462954bf95b9a82fbddfb850fda045b76c791bca41ad2007c
     base64url glMtoddz0HRilUv5W5qC-937hQ_aBFt2x5G8pBrSAHw

3. The vouch (PROPOSAL: no existing family's rule says this)
   An ordinary CEG statement by the B.3 issuer, composite-signed, statement id
   55097b48235097b94cb77fd4ba08162115bb41764a2c2b651b382ab02b80769f.
     row type   delegates_to
     family     trust:.job:.version        (registered; its {job} segment is a vocabulary)
     dimension  trust:registers:v1         PROPOSAL: "registers" is not a job the text defines
     CWT iss    the issuer;  CWT sub = the registration key's thumbprint, base64url (the form a trust:accepts
                Transparency Service edge already uses to name a non-composite key)
     payload    author (the issuer), dimension, registration_key (the COSE_Key above),
                registers: "companions"    PROPOSAL: the one thing the key may do
                delegation_valid_from 2025-11-16T09:46:40Z (the fixed test instant, also asserted_at) and
                delegation_valid_until 2027-11-16T09:46:40Z, so the term spans the demonstration
   Why this shape and not another existing one:
     - a key:record cannot carry it: a key record's `key` is a composite key and is signed by the key itself;
     - trust:accepts with service_key is the issuer's edge to a Transparency Service's key, a different statement;
     - a scoped delegation needs a scope word, and the scope vocabulary has none for this.
   What CIRISVerify 23.7.0 does with it: the statement reader reads it Valid, also under the vendored family model
   (trust:{job}:{version} is authored; the delegation term is well formed). It gives the row NO meaning: no reader
   in verify treats `registration_key` or `registers` as authority for anything. That meaning would be new text.

4. The companions: COSE_Sign1, tag 18, [protected, {}, payload, signature]
   Signature: ML-DSA-65 pure, empty context, over the RFC 9052 Sig_structure ["Signature1", protected, h'', payload].
   Signed with the DETERMINISTIC variant so the bytes reproduce; a production signer would use the hedged one and a
   verifier cannot tell the difference.
   Protected header of both: {1: -49, 4: kid = the registration key's thumbprint (32 bytes),
                              15: {1: iss = the original's iss, 2: sub = "ceg-companion:" + the original's statement id in hex,
                                   6: iat = 1795705436, the second the companions were minted}}
   (a) companion_header.cose   the original's statement id in the PROTECTED HEADER under label -70010
                               (PROPOSAL: private use, next to CEG's -70001..-70003); payload = the vouch's
                               statement id (32 bytes).
   (b) companion_payload.cose  header also carries 3: "application/cbor"; payload = the deterministic encoding of
                               {"statement_id": the original's, "statement_sha256": SHA-256 of the 3864 bytes,
                                "vouch_statement_id": the vouch's}  (PROPOSAL)
   Checked twice, by two implementations (dilithium_py in the generator; RustCrypto ml-dsa 0.1.1 through
   CIRISVerify's MlDsa65Verifier): each companion VERIFIES under the registration key and DOES NOT VERIFY under the
   composite's ML-DSA-65 component key.

5. What a relying party checks, in order
   1. The Receipt over the companion (the Transparency Service's own rules; not made here: there is no Receipt yet).
   2. The companion: alg -49; kid; the pure ML-DSA-65 signature under the registration key.
   3. The vouch: a CEG statement, by the checks of Section 6.4 (deterministic encoding, headers, the composite
      signature under the issuer's key, both halves, never one alone; the issuer's key record).
   4. That the vouch names that registration key: SHA-256 thumbprint of the vouch's `registration_key` equals the
      companion's kid (and the vouch's CWT sub); that the vouch's issuer is the companion's CWT iss; that the
      companion's `iat` (in milliseconds) and the Receipt's own time both fall inside the vouch's term
      [delegation_valid_from, delegation_valid_until); that `registers` is "companions". The `iat` is the
      registration key holder's own statement of when; the Receipt's time is the log's.
   5. That the companion names the original: label -70010 (variant a) or payload.statement_id (variant b) equals the
      original's statement id, recomputed from the original's protected header and payload.
   6. The original itself, by its own composite checks. Its iss equals the companion's iss.

6. What the chain does NOT show
   - The log attests the COMPANION's bytes and their order. In variant (a) it does not attest the original's bytes:
     the statement id covers the original's protected header and payload but not its signature or unprotected
     header, so two statements with one id and different signatures are the same to it. Variant (b) also carries
     the SHA-256 of the full original, which pins those bytes too.
   - It does not show the issuer made the companion: anyone holding the registration key can make one. The issuer's
     composite key vouches for the key, not for each companion. A stolen registration key registers false
     companions until the vouch ends or is withdrawn; it cannot forge an original.
   - The companion is not post-quantum-and-classical: it is ML-DSA-65 alone. The original keeps the composite.
   - No reader in CIRISVerify gives the vouch any force today.
   - Whether the vouch has been withdrawn is not visible from these files.
