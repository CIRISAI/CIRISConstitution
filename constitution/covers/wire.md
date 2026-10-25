# The Wire

**What this is.** The specification an implementer builds a second, independent producer and consumer from: the envelope and its members (2.1), the closed set of five row types (2.4), the signed object and its byte vectors (2.6.1.7), canonicalisation and its determinism rules (2.6), identifiers and time (2.6.2 to 2.6.8), and the transport, custody, key and privacy rules of Part 5 with the adversary model of 1.13.3.

**Whom it binds.** Any CEG-Conforming Producer, Consumer or Substrate. Conformance is judged against this volume, *The Dictionary* (the reservations and admission rules of 3.4 and 3.5) and *The Reader's Policies* (the composition policies of 4.4).

**What it promises.** One envelope, one signing input, one signature construction; a closed row-type slot; byte identity across implementations as a target with a published vector set as its proof; a refusal with a named reason, never a silent truncation; fixed-size frames on a shaped link, and a 1 MiB cap on the signed object.

**What it leaves out.** The meaning of any dimension, which is the dictionary's; the reasons a rule exists, which are the charter's; and whether a given MUST has shipped, which is the register's. Where this volume states a rule as normative, it means the bytes; where it explains, it says so.

**Where the rest lives.** The generated artefacts this volume is the source of: `manifests/signed_object.cddl`, `manifests/signed_object_vectors.json`, and `manifests/namespace_registry.json` with its match vectors. An implementer should read those beside the text, because the text is checked against them in CI and they are what a second implementation is measured by.
