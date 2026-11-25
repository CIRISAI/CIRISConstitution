# The genesis of the humanity accord, version 1

This folder is the public record of the ceremony that minted the trust root on 2026-11-21. Nothing here is a
secret. Every signed file is exactly as its signer produced it.

| | |
|---|---|
| Lineage | `humanity-accord` |
| Bundle object id | `cb9ada31fbce34103a8b01acecc67bbb8cb0e96c1210bb83e40c5f34d8e6deb5` |
| Version | 1, with no predecessor |
| Signed instant | 1795302284535 (milliseconds since the Unix epoch) |
| Holders | three, each on its own hardware token (device serials 38165850, 38165563, 38165401) |
| Seat | `canonical-1` |
| Charter | a halt fuse of 86,400 seconds, one recovery commitment for each holder, and six scopes; witnessing is off |

## What is in `package/`

| File | What it is |
|---|---|
| `holder-record-0.cose` to `holder-record-2.cose` | each holder's signed key record, with its custody attestation chain |
| `seat-record-0.cose`, `seat-binding-0.cose` | the seat's signed key record and its transport binding |
| `voice-0.cose` to `voice-2.cose` | the genesis bundle: one signed statement from each holder over one payload |
| `terms.json`, `ceremony.json`, `key_material.json` | the agreed terms, the ceremony's parameters and each holder's recovery commitment |
| `canonical-1.transport.json` | the seat's public transport keys |
| `trace.json` | every statement of the ceremony decoded, in order, with its signed bytes |
| `WITHHELD.txt` | what is not published |
| `SHA256SUMS` | the SHA-256 of every file above |

## What is withheld

Each holder signed a halt in advance and keeps it. The signature of each of those three halts is withheld, and so
are its full signed bytes. Each halt's decoded header, its decoded payload and the SHA-256 of its signed bytes are
published in `trace.json`. Nothing else is withheld.

## Checking it yourself

    cd package && sha256sum -c SHA256SUMS
    python3 -I ../../../formal/ceremony/check_trace.py trace.json

The second command decodes the signed bytes with its own reader, recomputes each row id and the bundle's object id,
and checks the nineteen invariants of [`manifests/ceremony.json`](../../manifests/ceremony.json). It does not verify
the composite signatures or the hardware attestation chains; the verifier does
([CIRISVerify](https://github.com/CIRISAI/CIRISVerify)).

## When it existed

Two public timestamp authorities signed the SHA-256 of `SHA256SUMS`,
`8569a30a7519347154133a28a0fe4bfcd523ac4e389ac8b1bdbf0ffbefc6b41f`, under RFC 3161. Only that hash was sent to them.

| Authority | Time (UTC) | Serial | Token |
|---|---|---|---|
| DigiCert | 2026-11-21 23:23:53 | `724F35A59734FDBB9674F3F4A9F8D793` | `timestamps/SHA256SUMS.digicert.tsr` |
| FreeTSA | 2026-11-21 23:23:57 | `0A5A9D3D` | `timestamps/SHA256SUMS.freetsa.tsr` |

    openssl ts -verify -digest 8569a30a7519347154133a28a0fe4bfcd523ac4e389ac8b1bdbf0ffbefc6b41f \
      -in timestamps/SHA256SUMS.digicert.tsr -CApath /etc/ssl/certs

The FreeTSA token verifies against the root that authority publishes. A timestamp shows that these bytes existed by
that time. It does not show that the authority checked any signature in the package.

The statements are not registered at a public transparency service. Such a service checks a statement's signature
before it registers it, and none yet reads the composite signature these statements carry.
