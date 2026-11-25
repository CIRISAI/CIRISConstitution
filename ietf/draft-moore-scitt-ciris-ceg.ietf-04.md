---
title: "Signed Attestation Rows of the CIRIS Epistemic Grammar and Their Relationship to SCITT"
abbrev: "CEG Attestation Rows and SCITT"
category: info
submissiontype: IETF
docname: draft-moore-scitt-ciris-ceg-latest
number:
date: 2026-11-25
v: 3
area: "Security"
workgroup: "Supply Chain Integrity, Transparency, and Trust"
keyword:
 - attestation
 - transparency
 - CBOR
 - COSE
 - composite signature
 - ML-DSA
venue:
  github: "CIRISAI/CIRISConstitution"
  latest: "https://github.com/CIRISAI/CIRISConstitution/tree/main/ietf"

author:
 -
    fullname: Eric Moore
    organization: CIRIS L3C
    email: eric@ciris.ai

normative:
  RFC2119:
  RFC8174:
  RFC8949:
  RFC9052:
  RFC8610:
  RFC9165:
  RFC9596:
  RFC9597:
  RFC9679:
  RFC4648:
  RFC8032:
  RFC9943:
  FIPS204:
    title: "Module-Lattice-Based Digital Signature Standard"
    author:
      org: National Institute of Standards and Technology
    date: 2024-08
    seriesinfo:
      FIPS: "204"
      DOI: 10.6028/NIST.FIPS.204
  CDE: I-D.draft-ietf-cbor-cde-13
  COMPOSITE-JOSE: I-D.draft-ietf-jose-pq-composite-sigs-06
  COMPOSITE-LAMPS: I-D.draft-ietf-lamps-pq-composite-sigs-19

informative:
  RFC6962:
  RFC9162:
  RFC7942:
  RFC3552:
  RFC6973:
  RFC8785:
  RFC9942:
  RFC9964:
  SD-CWT: I-D.draft-ietf-spice-sd-cwt-09
  CC:
    title: "CIRIS Constitution 1.0-rc22"
    author:
      org: CIRIS L3C
    date: 2026-11
    target: https://github.com/CIRISAI/CIRISConstitution/tree/v1.0-rc22
    annotation: "The tag v1.0-rc22 is commit f4671933f2b22b33d2db868d4654036162104123."
  I-D.moore-scitt-ciris-trace:
    title: "The CIRIS Agent Reasoning Trace"
    author:
      ins: E. Moore
      name: Eric Moore
    date: 2026-11
    seriesinfo:
      Internet-Draft: draft-moore-scitt-ciris-trace-00
  I-D.moore-scitt-ciris-trace-context:
    title: "Context Manifests for the CIRIS Agent Trace: Prompt Context Provenance for AI Agent Decision Traces"
    author:
      ins: E. Moore
      name: Eric Moore
    date: 2026-11
    seriesinfo:
      Internet-Draft: draft-moore-scitt-ciris-trace-context-00
  CC-VECTORS:
    title: "CIRISVerify v23.4.1"
    author:
      org: CIRIS L3C
    date: false
    target: https://github.com/CIRISAI/CIRISVerify/tree/v23.4.1
    annotation: "The tag v23.4.1 is commit 732c44847cc8d0e3bd2779fd186b504478584623."
  I-D.aylward-aiga:
    title: "Artificial Intelligence Governance Architecture (AIGA)"
    author:
      ins: E. Aylward
    date: false
    seriesinfo:
      Internet-Draft: draft-aylward-aiga-00
  I-D.sparysh-pala-audit:
    title: "PALA-1: A Tamper-Evident Audit Record Format for Constrained and Disconnected Deployments"
    author:
      ins: A. Sparysh
    date: false
    seriesinfo:
      Internet-Draft: draft-sparysh-pala-audit-02

--- abstract

The CIRIS Epistemic Grammar (CEG) records claims between parties as
signed rows.  Each row is one or more COSE_Sign1 messages over a
payload in deterministically encoded CBOR.  Each message carries one
composite ML-DSA-65 and Ed25519 signature.  Every row has one of five
types: a claim, a delegation, a replacement, a withdrawal, or a
recantation.  A node admits a row only after a fixed set of checks,
and it refuses a failing row with a named reason.

This document specifies the signed statement, its encoding, the names
by which rows refer to each other, the signature, and the admission
checks, so that a second implementation can produce and verify the
same bytes.  It then describes how these statements relate to the
roles of the SCITT architecture (RFC 9943), and where they differ.
It defines no new SCITT mechanism and requests no IANA action.

--- middle

# Introduction

CEG is the row format of the CIRIS system, in which people, devices,
communities and AI agents make claims about each other and act on
them.  It is defined normatively in the CIRIS Constitution {{CC}}.
This document restates the parts of that definition that another
implementation needs in order to interoperate at the byte level.

Three goals shape the format:

- Any party holding a row can recompute its bytes and its name
  exactly.  The payload and the protected header are in the
  deterministic encoding of CBOR, and a verifier refuses any other
  encoding of the same value ({{canon}}).

- Rows exchanged between nodes have to resist forgery by an attacker
  with a quantum computer.  Every statement carries one composite
  signature, ML-DSA-65 {{FIPS204}} with Ed25519 {{RFC8032}}, and
  neither half verifies alone ({{sig}}).

- The set of row types is closed, so that every row is subject to the
  same admission rules.  New kinds of claim are new families and
  dimensions, never new types.

SCITT {{RFC9943}} defines an architecture for registering signed
statements with a Transparency Service and returning receipts that
prove registration.  Each CEG statement is a COSE_Sign1 with an
issuer and a subject in its protected header, so it has the shape of
a SCITT Signed Statement.  CEG fixes no Transparency Service, and its
admission checks need none.  A trust root's genesis bundle may name
the services its heads are registered with, and a room may name them
for its accountable streams ({{heads}}).  A host that runs code a row
admits first requires a SCITT receipt from a Transparency Service it
trusts ({{receipts}}).  {{scitt}} describes the relationship and what
still differs.

## Scope

In scope:

- the signed statement of a row and its headers ({{object}});
- the five row types ({{types}});
- the deterministic encoding and the rules that close it
  ({{canon}});
- the row id, the statement id and the object id ({{names}});
- the composite signature, keys and counted rows ({{sig}});
- the admission checks, written as a SCITT Registration Policy
  ({{admission}}).

Informative only:

- the other signed objects and receipts ({{objects}});
- the safety properties the rows carry ({{safety}});
- the relationship to SCITT roles ({{scitt}});
- the lifecycle of an agent's decision record ({{lifecycle}}).

Out of scope: the transport between nodes, the storage schema, the
meaning of individual claim families (the "dimension" namespace), and
the governance rules that decide who may hold which role.  {{CC}}
defines each of these.

## Requirements Language

{::boilerplate bcp14-tagged}

## Terminology

This document uses the terms Issuer, Signed Statement, Transparency
Service, Registration Policy, Receipt, Transparent Statement, and
Relying Party as defined in {{RFC9943}}.  It also uses:

Statement:
: One COSE_Sign1 {{RFC9052}} under CBOR tag 18, made by one signer.

Row:
: One signed attestation.  A row is one statement, or several
  statements over one payload where the row is counted
  ({{counted}}).

Payload:
: The CBOR map a row's statements sign.  It is carried as the
  COSE_Sign1 payload, as a byte string in the deterministic encoding.

Signer:
: The key that makes a statement.  Its stable identity is the CWT
  `iss` claim.  It plays the SCITT Issuer role.

Subject:
: What a row is about.  The CWT `sub` claim names it.  The payload
  member `subject_key_ids` lists any further subjects, including
  parties that have no key.

Identity reference:
: The one spelling of a key's identity: the COSE Key Thumbprint URI
  of {{RFC9679}} for the key ({{idref}}).

Family id:
: The name of a row's claim family, carried in the protected header
  ({{family}}).

Producer, Consumer, Substrate:
: A Producer emits rows.  A Consumer verifies and reads rows.  A
  Substrate stores and relays rows and applies the admission checks.
  One node is usually all three.

Reason, refusal token:
: A fixed, case-sensitive ASCII string, so that two implementations
  agree on a refusal as well as on an acceptance.  A reason is what a
  verifier gives for answering Invalid.  A refusal token is what a
  Substrate gives for refusing a row.  Every reason and token in this
  document is lower case, and is compared byte for byte.  A reason
  may carry a detail after a colon, as in `malformed:refs`.
  {{admission}} lists them all, and says where one fault has both a
  reason and a token.

# The Signed Statement {#object}

## COSE_Sign1 and the Protected Header

A statement is a COSE_Sign1 {{RFC9052}} under CBOR tag 18.  Its
payload is never detached.  The protected header of a row's statement
carries exactly seven members, and the signature covers all of them.

| Label | Member | Value |
|---|---|---|
| 1 | alg | -70100, the composite algorithm of {{sig}} |
| 3 | cty | "application/vnd.ciris.row+cbor", with no parameters |
| 4 | kid | The 32-byte thumbprint of the signing key ({{keys}}) |
| 15 | CWT claims | iss, sub, iat, and nbf and exp where the row has them, and the edition claim |
| 16 | typ | "ceg-row/2" |
| -70001 | row type | One of the five row types, as a text string |
| -70002 | family | The row's family id, as a text string |
{: title="The protected header of a row"}

The CWT claims are carried as {{RFC9597}} defines.  The edition
claim has the label -70003 and the value 2.  `iat`, `nbf` and `exp`
are derived from payload members ({{time}}).

A verifier MUST refuse a row whose `cty` carries parameters, or whose
protected header lacks the type label or the family label.  It MUST
refuse a protected header with any other member, so that one
statement has one statement id ({{names}}).  A signed object that is
not a row carries neither label, and one that does is refused
({{objects}}).

`sub` names what the row is about: the attested key, or the object
the row refers to.  A statement's kind is its `typ` {{RFC9596}}.

## The Family Id {#family}

The family label carries a family id, never a leaf.  A family id is
the family's registry prefix in {{CC}}, with each `{name}` segment
written as a full stop followed by the name, and each `*` written as
a lone full stop.  Examples are `key:record` and
`provenance:build_manifest:.target`.

A literal segment never begins with a full stop, so no two prefixes
share a family id.  A row that scores a dimension carries it whole, leaf and
version, in the payload member `dimension`.  A verifier MUST refuse a
`dimension` that does not resolve to the family id the header
carries.

A `withdraws` or a `recants` row carries the family id of its target
and no `dimension`, and its `sub` is its target's.  One that states a
`dimension` is Invalid, `malformed:dimension`.  A `supersedes` row is
a row of its own family and carries its own `dimension` (CC 2.6.1.1).

## Identity References {#idref}

`iss` is the signer's stable identity reference: the COSE Key
Thumbprint URI of {{Section 5.7 of RFC9679}} for the signer's genesis
key.  It is `urn:ietf:params:oauth:ckt:sha-256:` followed by the
unpadded base64url {{RFC4648}} of the 32-byte thumbprint.  That is
43 characters, the last with zero trailing bits.

Because `iss` names the genesis key, the issuer stays the same when
the signing key rotates; `kid` names the key that signs.  `author`, a
key named by `sub` or by an element of `subject_key_ids`, and every
role party use this one spelling.  A verifier MUST refuse any other.

`iss` is a claim.  The signature shows which key signed, and `kid`
names that key.  That the key is a key of the identity `iss` names is
a separate check of verification ({{key-of-iss}}).  A statement that fails
it is Invalid, whatever its signature.

In a private room a person signs with a room key made for that room.
On a row a room key signs, `iss` is the voice: the identity reference
of the voice's first room key.  It is never the person's (CC
2.6.1.11).

## The Unprotected Header and External AAD

`external_aad` is the empty byte string, and no party puts a domain
prefix there.  The unprotected header is outside the signature, and
no admission check reads it.  A holder may add a receipt there, or
present a disclosure there ({{erasable}}, {{receipts}}).  A host reads
a receipt there before it runs code a row admits; the receipt grants
nothing, and a malformed one is ignored ({{receipts}}).

There is no copy of the headers inside the payload and no signature
beside the statement.  The protected header and the payload are the
row.  A further voice is a further statement ({{counted}}).

## The Payload {#payload}

The payload is a CBOR map whose members the row's family names.
Every row carries `asserted_at`.  Other members that {{CC}} fixes for
every family include:

author:
: The `iss` of the one who authors the row.  It is present when the
  family is authored and absent when the family is counted
  ({{author}}).

refs:
: Every row this row names ({{refs}}).

dimension:
: The full scored dimension, leaf and version.  It resolves to the
  header's family id.

evidence_refs:
: The blobs the row cites, by content hash, as a sequence.

score, confidence, weight:
: Integers at a fixed scale ({{numbers}}).

valid_from, valid_until, expires_at:
: Instants ({{time}}).

salt:
: Sixteen random bytes.  A row whose content is low-entropy, such as
  a ballot or a census cell, carries one, so that its row id confirms
  no guess.

body:
: A map whose member `note` holds at most 2048 bytes of free text.
  No free text stands outside `body.note`.

reason:
: A code from a closed registry.

`subject_key_ids`, `cohort_scope`, `scope` and the claim's other
members are payload members of the same names.  {{cddl}} gives the
full schema.  A Consumer MUST preserve members it does not recognise
when it relays a row ({{relays}}).

# The Five Row Types {#types}

The row type label (-70001) takes exactly one of five values,
compared byte for byte.  A statement that carries any other value
does not meet the header's schema.  A verifier answers Invalid at
step 2 of {{verify}}, with the reason `malformed:row-type`.  A
Substrate MUST refuse such a row, both where it emits the row and
where it receives it, and it reports the refusal with the token
`attestation_type_unregistered` (CC 2.4).  The reason and the token
name one fault ({{admission}}).

scores:
: A claim about the subject on the named dimension.  Every positive
  or negative claim about a party is a `scores` row.

delegates_to:
: The signer authorises the subject to sign on its behalf within
  `scope`, a set of strings.  For the scopes that {{CC}} lists as
  requiring a term, among them licensing, moderation and takedown,
  the delegation's end is REQUIRED.  It MUST be no more than 365 days
  after its start.  A Substrate refuses a row that breaks this with
  `delegation_term_required`.

supersedes:
: The signer replaces one of its own earlier rows, named by row id in
  `refs`.

withdraws:
: The signer retracts an earlier row, named by row id in `refs`,
  without saying the row was false.  {{withdraw-rule}} says who may
  withdraw a row.

recants:
: The signer says one of its own earlier rows was false when it was
  made.  Only the original signer can recant a row.

A withdrawal and a recantation are different statements.  A
withdrawal says "I no longer assert this"; a recantation says "this
was wrong".  The subject of a row has authority over the first but
not the second ({{withdraw-rule}}).

None of the three removes its target: the target stays held and
verifiable, and each names it in `refs.target` ({{refs}}).  A
verifier reports a row's state as one of four: admitted, superseded,
withdrawn or recanted (CC 2.7.5).  The state is derived, not final,
since a later row on the same target, concurrent with the first, can
change it.  Consumers may weigh a withdrawn and a recanted row
differently; they MUST NOT report either as admitted.

A new kind of record is expressed as a new family or dimension on one
of the five types, never as a sixth type.

# Encoding {#canon}

## Deterministic Encoding

The payload is encoded in CBOR's deterministic encoding, as the
Common Deterministic Encoding {{CDE}} fixes it over {{RFC8949}}.  A
verifier MUST refuse a payload whose bytes differ from the
deterministic re-encoding of the value they decode to.  That covers a
non-shortest integer, an indefinite length, an unsorted map key and a
duplicate key.

The protected header is in the deterministic encoding too.  A second
encoding of one value would otherwise be a second row.  A verifier
verifies the bytes it received, never a re-encoding of members it
decoded.

## The Omit Rule {#relays}

The bytes are the members the Producer signs.  An optional member the
Producer omits MUST NOT be written into the payload by any party.  An
optional member the Producer emits, even at its default value, MUST
be kept by every party.  Defaults documented in {{CC}} are applied
when a row is read, never when it is encoded.

An optional member is unset by being absent, never by null.  A
payload with null for an optional member is Invalid, `malformed:` and
the member ({{reason-names}}).  A Substrate MUST refuse it, with the
token `federation_malformed_row` and the reason
`envelope_member_null`.
No value a family names, at any depth, is a float, a null, an
undefined value, a tag or a simple value.  The exceptions are the
redaction marks of {{erasable}} and the decimal fraction of
{{numbers}}.

A Substrate, relay or Consumer that stores or forwards a statement
MUST forward the octets it received.  It never strips an emitted
default and never writes in an omitted one.  Unknown members are kept
the same way.

## Sets, Sequences and Tuples

An array whose positions the schema names is a tuple, and its order
is its definition.  An array of one element type is a set or a
sequence, as its definition states.  Where no definition says, it is
a set.

- A set is sorted by the bytewise order of its elements'
  deterministic encodings and holds no duplicate.  A verifier answers
  Invalid for any other, `set_order:` and the member, and a Substrate
  refuses it with the token `federation_set_semantics_unsorted`,
  naming the member ({{tokens}}).  Neither ever re-sorts the set,
  because that would change the signed bytes.

- A sequence keeps its authored order.  The sequences are
  `evidence_refs`, the redacted-key arrays of {{erasable}}, and the
  others {{CC}} lists.

Every array inside `refs` is a set ({{refs}}).

## Bytes and Text

A byte member is a CBOR byte string.  Hexadecimal and base64 do not
stand in the payload for bytes.

`subject_key_ids` is the one member with two forms.  An element
naming a registered key carries that key's identity reference
({{idref}}).  An element naming a party with no key is the tagged
text `canonical:<hashalg>:<hex>`.  The tag is part of the signed
string, and the hex is lowercase.

## Numbers {#numbers}

No member of the payload is a float.  A score, a confidence and a
weight are integers at the fixed scale of 10^6: the value times 10^6.
A score lies in [-10^6, 10^6], a confidence in [0, 10^6] and a weight
in [0, 10^6], unless the family states a wider range.

A number in a free-form body that is not an integer is a decimal
fraction: CBOR tag 4 {{RFC8949}} over `[exponent, mantissa]`, with a
negative exponent and a mantissa in CBOR's integer range that is not
divisible by 10.  An integral number is a plain integer.  A number
outside CBOR's integer range, alone or as a mantissa, is refused
`body_number_unrepresentable`.  A decimal fraction that is not
normalised is a second encoding of one value, and is refused as any
other is, `not_deterministic:payload` (CC 2.6.1.2).

A fold sums in signed 64-bit integers, and its arithmetic is checked:
a fold that would overflow is refused, and never wraps.  A derived
value is computed in integers and checked by exact equality.  It is
rounded half away from zero unless its own rule states otherwise.

## Instants {#time}

`asserted_at`, `valid_from`, `valid_until`, `expires_at` and every
other instant in a payload are unsigned integers of POSIX
milliseconds, never floats.  The header's `iat`, `nbf` and `exp` are
the standard CWT claims in seconds.  Each is the floor of its payload
member divided by 1000.  A verifier MUST refuse a statement whose
header claim disagrees with its payload member.

Where an instant stands in signed text rather than in a payload,
{{CC}} fixes a separate text form.  No statement of this document
carries one.

## Size

A payload's deterministic encoding MUST NOT exceed 1 MiB (1,048,576
bytes).  The bound is on the bytes the signature covers.  A Producer
MUST NOT emit a larger payload.  A Substrate MUST refuse one at every
write path, with `envelope_too_large` ({{tokens}}).

Every write path MUST also enforce a finite ceiling on the octets it
buffers from an untrusted source.  It refuses at that ceiling in the
same way, without completing the decode.  The ceiling is local,
MUST NOT be below 1 MiB, and SHOULD be published.

Larger content travels outside the row and is named in
`evidence_refs` by its hash.

## Erasable Members {#erasable}

A family may mint some members blind, using the selective disclosure
of {{SD-CWT}}.  A blinded member is absent from its map.  Its
disclosure is the salted claim `[salt, value, key]`, with a salt of
sixteen random bytes.  Its digest stands in that map's
`redacted_claim_keys` array, keyed by the simple value 59, in mint
order.

A blinded array element is tag 60 over its disclosure's digest, and
its disclosure is `[salt, value]`.  A digest is SHA-256 over the
disclosure's bytes.  A disclosure travels beside its statement, in
the unprotected header's `sd_claims` (label 17), only to one who may
see it.

Erasure drops a disclosure and alters no signed byte.  Which members
are blind is fixed by the family in {{CC}}.  No fold, verdict or
admission reads a member that can be blinded.

# Names {#names}

## The Row Id

A row is named by one digest, its row id.  It is SHA-256 over the
deterministic encoding of this array:

~~~
["CEG-row/2", type, family, sub, author, payload]
~~~

`type` and `family` are the text strings of labels -70001 and -70002.
`sub` is the CWT subject.  `author` is the payload's `author`, or
null.  `payload` enters as the byte string signed, never as the
decoded map.  A digest is written as the array `[-16, digest]`, where
-16 names SHA-256.

Signatures, `kid`, `alg`, receipts and disclosures are outside the
row id.  So every voice of a counted row has the same row id.  The
row id does not change when a voice, a receipt or a disclosure is
added.  The row id commits to `iat`, `nbf` and `exp`, because they
are derived from payload members.  It does not read `cty`.

## The Statement Id

A statement's own id is SHA-256 over the deterministic encoding of
`["CEG-statement-id/2", protected, payload]`, written the same way.
`protected` and `payload` are the byte strings of the statement.  It
names one voice; the row id names the row.

This is the CEG statement id, a name of this profile: {{RFC9943}}
defines no statement identifier.  It covers the protected header and
the payload.  It leaves out the signature and the unprotected header,
so a receipt or a disclosure added later does not change it.  The
`external_aad` of a CEG statement is the empty byte string
({{object}}), so a CEG statement id and a reference to the COSE
`Sig_structure` of the same statement select the same statements,
though the two encoded inputs differ.

A match on a statement id, a row id or an object id says that two
parties name the same bytes.  It says nothing of who signed them.
That a statement's key is a key of its `iss`, and that its signature
verifies, are steps of verification ({{verify}}).

## What a Row Names {#refs}

Every row a row names stands in one payload member, `refs`, by
reference.  A reference is the array `[2, digest]`: the edition and
the row id.  `refs` is a map with these members:

| Member | What it names |
|---|---|
| head | The head the row is at: the head a count is over ({{counted}}), the head an act is exercised at, or the head an end acts from ({{standing-end}}) |
| further_heads | Further tips beside `head` |
| prev | The predecessor in a signer's own series; on a content row, a content row its author signed in the same room |
| further_prev | Further content rows of the same author in the same room, beside `prev` |
| answers | The row this row answers: the proposal voted on or accepted, the window opened, the row replied to |
| target | The row a `supersedes`, `withdraws` or `recants` row names; on a rotation record, the old key's record ({{rotation}}); the act a cut ends or the member a removal removes; and, on a halt's confirmation or resumption, that halt ({{halt}}) |
| trusted_through | On a key revocation, the last rows of the key held good; on a row that ends a member's seat and on a `keeps` row, the member's newest content rows held good.  At most 64 |
| also | A map from a role to a set of references.  The roles are `ack`, `cites`, `under`, `stands_on` and `voice` |
{: title="Members of refs"}

A holder reads the set of named rows from `refs` alone, without
knowing the family.  `target` is not confined to the three row types
that replace or retract: a rotation record is a key record that names
its predecessor there.

The roles of `also` are a closed registry of five (CC 2.6.1.3):

- `ack` names a row acknowledged, as a receipt of acts does
  ({{standing-end}}).
- `cites` names a row the row cites.
- `under` names the one edge a deputy's edge hangs from.  It is a set
  of exactly one.
- `stands_on` names the one acceptance that a row signed under a root
  grant stands on.  It is a set of exactly one ({{standing-end}}).
- `voice` names the head of the key roster of the voice a room key
  signs for.  It is a set of exactly one ({{idref}}).

A role is a key of the `also` map and is not a member of `refs`.  Any
other role is Invalid, `unexpected:also`.

A row waits for the rows it names, with two exceptions that are named
for the fold alone: `prev` and `further_prev` on a content row, and
`trusted_through` on a row that ends a seat or a `keeps` row (CC
2.7.3).

Every array inside `refs` is a set, and a set out of order is
refused.  An empty `refs` is refused: absence is its one encoding.
An empty set inside `refs`, and an empty `also`, are refused in the
same way.
No row names an object of the earlier form of {{earlier}}.

## The Author {#author}

A family is either authored or counted, as {{CC}} states for each
family.  An authored family's payload carries `author`, the `iss` of
the one who authors the row.  The row id reads it from the payload.
A counted family's author is null.

Where a family is authored by its subject, the row is authored by
the attested key: `author` MUST be the CWT `sub`, and a statement
whose `iss` is another key is Invalid.

A statement whose `iss` is not the payload's `author` is accepted
only in a role its family names, such as a delegate or a bound node.
Its `iss` MUST then be the party that role names in the payload.
Where that party is the attested key, as a delegate is, it MUST be
the CWT `sub`.  On an authored row that its family counts, a voice of
that count is accepted too.  Any other `iss` is Invalid,
`iss_not_in_role` ({{verify}}, CC 2.6.1.3).

# Signatures and Keys {#sig}

## The Composite Signature

A statement's signature is the composite ML-DSA-65 with Ed25519 of
{{COMPOSITE-JOSE}}, over {{COMPOSITE-LAMPS}}, at the revisions cited.
It is computed over the Sig_structure of {{Section 4.4 of RFC9052}},
with an empty `external_aad`.  That Sig_structure is the message M.

Both halves sign one message representative:

~~~
M' = "CompositeAlgorithmSignatures2025"
     || "COMPSIG-MLDSA65-Ed25519-SHA512"
     || 0x00 || SHA-512(M)
~~~

The zero byte is the empty application context.  ML-DSA-65 signs M'
with the label bytes as its FIPS 204 context string, never the empty
one.  Ed25519 signs M' as it is.  The representative binds both
halves, so neither half verifies alone.

The encoding is the ML-DSA-65 signature (3309 bytes) followed by the
Ed25519 signature (64 bytes), 3373 bytes in all.  The algorithm
identifier is -70100, a private-use value.  A key's thumbprint covers
the identifier, so `kid` and `iss` carry it, and a new identifier
would rename every identity.  A lineage therefore keeps -70100 for
its keys.  A move to an assigned identifier is a planned migration,
by a later genesis bundle that seats the renamed keys (CC 2.6.1.7).
ML-DSA-65 alone is COSE algorithm -49 {{RFC9964}}; CEG does not use
it alone.

## Keys {#keys}

A key is one composite COSE key of key type AKP (kty 7).  Its `pub`
(label -1) is the ML-DSA-65 public key followed by the Ed25519 public
key, 1984 bytes.  Its `kid` is its 32-byte SHA-256 thumbprint
{{RFC9679}}, fixed for the key's life.  The thumbprint is over the
deterministic encoding of the key with exactly its three members,
`{1: 7, 3: -70100, -1: pub}`.  A key's displayed identity is that
thumbprint.

### Key Records {#key-records}

A key record is a row of the family `key:record`.  Its `sub` is the
identity reference of the key it records.  Its payload carries `key`,
`identity_type`, `asserted_at` and, where its end rule requires,
`valid_until`.

`identity_type` is a set of roles.  A set that mixes a person's role
(`user` or `accord_holder`) with a machine's (`node` or `agent`) is
refused, `key_record_mixed_roles`.  A record whose set contains a
person's role carries no `valid_until`.  One whose set contains
`node` or `agent` carries one, unless it is a room key of a private
room.  A pseudonym's record MAY carry one, and a role outside both
groups takes no end rule of its own.  Where `valid_until` is present
it is later than `asserted_at`, and no more than
`key_record_max_secs` after it, a constant of {{CC}}.  A record whose
`valid_until` is not later than its `asserted_at` is Invalid at step
4 of {{verify}}, `valid_until_not_after_asserted_at`.  One that
otherwise breaks the rule is refused `key_record_out_of_window` (CC
2.4.1.1).  The check of a key record's payload alone has no step 4,
and answers `key_record_out_of_window` for either fault.

Each key's own holder signs its record.  A record makes its key live
only where a statement over it by that key itself is held.  A record
that only other keys have signed makes the key live nowhere, and no
third party ends a key or revives one (CC 2.4.1.1).

A record covers an instant that is at or after its `asserted_at`
and, where it states `valid_until`, before it.  The end is not
covered: a record whose `valid_until` is T does not cover T.

A key is live at an instant when one of its records covers that
instant and its own revocation has not taken effect by then.  Only
the key's own revocation ends its liveness.  The key's owner and the
roster that seats it may also revoke it.  That ends the owner's
binding or the seat, not the key's liveness.  A revocation signed by
any other key concludes nothing, `key_revocation_no_standing`.

A key renews by signing a further record that `supersedes` its own
earlier record.  Renewals that do not name each other all count, and
the key lives to the greatest end they state.

### Rotation {#rotation}

`iss` names the signer's genesis key and stays the same when the
signing key changes.  A rotation is what links the next key to that
`iss`.  A rotation record has one shape (CC 3.1.3).  It is the key
record of the new key, and:

1. Its payload names the old key's record in `refs.target`, by row
   id ({{refs}}).
2. Its `iss` is the `iss` of the old key's record, in every statement
   over it.
3. It carries two statements over the one payload.  One is the new
   key's own, which shows possession of the new key.  The other is
   the old key's.
4. The record it names is a valid record of the old key under that
   `iss`, and it covers the rotation record's `asserted_at`.  That is
   the instant of the old key's statement, which is thereby made
   inside the old key's record.

A record of any other shape links no key to an `iss`.  One that names
no predecessor never does.  One that lacks either statement does not
until that statement is held ({{key-of-iss}}).

A rotation hands on what the old key may hand on, and never extends
the old key.  A renewal on the way, a `supersedes` by a key of its
own record, leaves the chain where it was.  A link stands where its
predecessor's statement stands: made inside the predecessor's record,
and before the `revoked_after` of a revocation by that key itself.
So a link made while its predecessor was live stands after that key
has ended, and no other voice's revocation cuts a chain.

Two rotations of one key, neither naming the other, are contested.
They hand on nothing until a rotation names both.  A statement that a
contested successor signs under the old `iss` is Invalid,
`kid_not_of_iss`.  A rotation is such a rival only where it meets
item 4: one that names a record of the old key that does not cover
its own instant blocks nothing (CC 2.4.1.1).

### The Key of an Issuer {#key-of-iss}

A statement's key MUST be a key of its `iss`.  A signature that
verifies shows only that the holder of `kid`'s key signed.  It does
not show that the key belongs to the identity `iss` claims, and
without this check a statement signed by one party could name
another as its issuer.  The key that `kid` resolves to is a key of
`iss` in one of four ways:

1. `kid` is the thumbprint inside `iss`.  The key is the genesis
   key, or a room key signing as itself.
2. The verifier holds a key record of that key whose own `iss` is the
   statement's `iss`, and that record reaches the genesis key's
   record through rotation records, each of the shape of
   {{rotation}}.
3. The genesis bundle in force seats that key for that `iss`, as a
   recovery or a rotation by bundle does ({{objects}}).  The seat
   ends at the first later bundle in force that does not seat the
   key.
4. A live occurrence of `iss` binds that key: an `identity:occurrence`
   row of `iss` that the verifier holds, whose `occurrence_key_id` is
   the key.  The row is admitted, not evicted, and covers the
   statement's instant.  It carries the bound key's own statement
   over the same payload, as proof of possession.

A `node` or `agent` key is never a key of an identity whose genesis
record is a person's.

Where none of the four holds, the answer is Waiting or Invalid, and
what the verifier holds decides which.

Waiting.
: The answer is Waiting where a row that one of the ways needs is
  known to the verifier and not held.  Waiting names that row.  It is
  one of these: the record that a held rotation record names; a
  statement that a held rotation record lacks, the new key's own or
  the old key's; a statement that a held occurrence lacks, the bound
  key's own or one of `iss`; an occurrence that covers the
  statement's instant, where the one held has ended; a row that the
  admission of an occurrence needs; and the bundle in force, where
  the verifier knows of it and does not hold it.  A
  row gains statements without changing its row id, so a record that
  lacks a statement waits for it and is not refused (CC 3.1.3, CC
  2.6.1.9).

Invalid.
: Otherwise the statement is Invalid, `kid_not_of_iss`.  Nothing that
  the verifier could name is missing: each held record of the key is
  of another identity, or the record names no predecessor, or the
  chain does not reach the genesis key, or the rotation is contested,
  or the occurrence that binds the key is of another identity or
  evicted.  Where a link fails only by its predecessor's own
  `revoked_after`, the reason carries the detail
  `rotation_after_revocation`.

Bare keys.
: A verifier that holds bare keys and no rows can show only the first
  way.  It holds no row that names another, so it can name nothing as
  missing.  For a statement whose `kid` is not the thumbprint inside
  `iss`, its answer is Invalid, `kid_not_of_iss`.

`kid_not_of_iss` is an answer over the rows held.  {{CC}} states that
a contested rotation is `kid_not_of_iss` until a rotation names both,
so a later row can change it.  A bad signature is different: that
answer is final ({{verify}}).

The statements of a genesis bundle and of the accord's rows bind
their key to the holder by the bundle in force instead (CC 2.6.1.11,
CC 4.2.1.1).

## Counted Rows {#counted}

A counted row is several statements over one payload, one for each
voice, found by the row id.  The head the row is counted over stands
in `refs.head`, inside what every voice signs.  Further tips stand in
`refs.further_heads`, a set.  A fold counts the statements by person,
as it counts votes.

Each statement is a SCITT Signed Statement with one signer.  Adding a
voice changes neither the payload nor the row id.  A delegation of a
scoped kind seats only with a second statement over the same payload,
signed by the delegate, the row's `sub`.

Two statements over different payloads are two rows, whatever else
they share.

## Verification Has Three Answers {#verify}

Verifying a statement gives one of three answers: Valid, Invalid with
a reason, or Waiting on what it names as missing.  What is missing is
a key at step 6 below, and a row or a statement of a row at step 8.

- A bad signature under a held key is Invalid, and that answer is
  final.  A structural fault is Invalid whatever keys are held.
- A statement whose key record is Waiting is Waiting, naming the
  deepest missing key.  A statement whose key record is Invalid is
  Invalid, `key_not_valid`.
- A key is one composite key.  A statement whose signer's key record
  is not held is Waiting on it, and a key never verifies on one half.
- Waiting never becomes Valid by default and is never counted.  A
  waiting statement is held inert until what it names is held.

A verifier proceeds in this order:

1. Decode strictly: tag 18, and the protected header and the payload
   in the deterministic encoding.
2. Check the header: `typ` on the closed list; `alg` -70100; edition
   2; `cty` the constant; a row's type and family labels present, the
   type one of the five and the family registered; an object's
   absent.
3. Check the payload against the schema: no float or null, the sets,
   the ranges, `passed` and `total`, `dimension` resolving to the
   header's family, and the family's own payload rule.
4. Check `iat`, `nbf` and `exp` against the payload, and that a
   `valid_until` is later than `asserted_at`.
5. Run the family's static checks, the key record's end among them.
6. Read `kid` and resolve the key record: a record of that key that
   the key itself signed and that covers the statement's
   `asserted_at`.  Answer Waiting where the key is not held, where
   its own statement over a held record is not held, or where no held
   record covers the instant.
7. Verify the composite signature over the bytes received.
8. Check that `kid`'s key is a key of `iss` ({{key-of-iss}}).  Answer
   Waiting on a chain link, a statement, the bundle in force or an
   occurrence that is not held; otherwise Invalid, `kid_not_of_iss`.
9. Check `iss` against `author`, or against the party of a role the
   family names ({{author}}).
10. On Valid, apply the defaults of {{CC}} to absent members, at
    interpretation time only, and then the Consumer's own policy.
11. Store or forward the statement as received.

A failure at steps 1 to 5 or 7 to 9 is Invalid.  Steps 6 and 8 alone
answer Waiting.  The reason is that of the first step that fails.

Step 6 is where a key's liveness at the statement's instant is read.
A statement whose `asserted_at` no held record of its key covers is
not Invalid.  It waits for a record that covers the instant, as a
statement signed by a key not yet held waits for the key (CC
2.4.1.1).  A renewal signed later can supply that record.  A verifier
that holds bare keys reads no record, so it reads no instant at this
step.

A Waiting answer says what is missing.  The vectors of {{vectors}}
write it as `waiting:`, the kind of thing missing and, in the row
statement files, what identifies it.

| Step | What is missing | Answer |
|---|---|---|
| 6 | The key `kid` names, or the deepest key a chain of records needs | `waiting:kid:<kid>` |
| 6 | The key's own statement over a held record of it | `waiting:voice:<kid>` |
| 6 | A record of the key that covers the statement's instant | `waiting:covering_record:<kid>:<instant>` |
| 8 | The record a held rotation record names | `waiting:record:<row id>` |
| 8 | A statement that a held rotation record or occurrence lacks | `waiting:voice:<kid>` |
| 8 | An occurrence of `iss` that covers the statement's instant | `waiting:covering_record:<kid>:<instant>` |
| 8 | The bundle in force | `waiting:bundle` |
{: #tab-waiting title="Waiting answers"}

`<kid>` is the thumbprint of the key that is missing, of the key
whose statement is missing, or of the key that lacks a covering
record.  `<row id>` is the row id of the record named.  Each is 64
lowercase hexadecimal digits.  `<instant>` is the statement's
`asserted_at`, in decimal.  `voice` is the vectors' word for one
signer's statement over a row.  The later key-of-issuer file of
{{vectors}} writes each answer by its kind alone: `waiting:kid`,
`waiting:voice`, `waiting:record`, `waiting:bundle`, and
`waiting:covering` for a covering record.

One further Waiting answer lies outside the eleven steps.  It arises
when a row is read under its family.  A `withdraws` or a `recants`
row takes the family of its target ({{family}}).  Where that family's
authorship turns on the target's dimension and the target is not
held, the reading waits on the target, as a row waits for the rows it
names ({{refs}}).  The vectors write it `waiting:row:<row id>`.

# Other Signed Objects and Receipts {#objects}

This section is informative.  {{CC}} is normative for each object.

## Objects That Are Not Rows

Every other signed object is a COSE_Sign1 whose `typ` names its kind,
from one closed list: `ceg-genesis-bundle/2`,
`ceg-revocation-snapshot/2` and `ceg-boot-manifest/2`.  A verifier
MUST refuse any other `typ`.  The protected header carries exactly
`alg`, `kid`, the CWT claims and `typ`, with no `cty`.  Its CWT
claims are `iss`, the edition claim, and `iat` where the object
states an instant.

Such an object is named by its object id: SHA-256 over the
deterministic encoding of `["CEG-object/2", typ, author, payload]`.
`author` is the payload's `author`, or null where it has none.  Like
a row id, it is the same for every voice of a counted object.

## The Genesis Bundle

A trust root is the lineage of a genesis bundle, named by the
bundle's `family_key_id`, and that is the only kind of root (CC 3.2).
A key that signs a charter about itself is no root.

The bundle's payload is a closed map.  `holders` is the root's roster
and `serve_nodes` its seats, each a set of identity references.
`charter` carries the root's parameters, which no row carries: the
recovery commitment of each holder, the scope, `attach_window_secs`,
`halt_fuse_secs` and, where the root names Transparency Services,
`transparency_services`, `receipt_quorum` and `receipt_cadence_secs`
({{heads}}).  Every row the bundle seats stands in `refs.also` under
`cites`, by row id: the key record of each holder, seat and named
service, and the transport binding of each seat.  `holders`,
`serve_nodes` and `transparency_services` are disjoint.  A seat
stands by the bundle that names it, and the end of the seat's key
record does not unseat it (CC 2.6.1.11).

The bundle is counted: one statement for each holder, over one
payload.  Each statement carries `iat`, equal to the payload's
`asserted_at` divided by 1000 and rounded down.

The first bundle counts when every holder it lists has a valid
statement over it.  A later bundle names its predecessor as
`refs.prev`.  It counts when a strict majority of the predecessor's
holders have valid statements over it.  Each holder it adds signs it
too.

A roster change is such a later bundle, with no proposal, window or
separate vote.  A holder's recovery is also a later bundle, with one
statement under the holder's recovery key.  That statement counts
only where the predecessor's recovery commitment for the holder
matches.  Two later bundles that count on one predecessor are a fork,
and a reader reports it.

A reader's anchor is what it was built or configured to trust: the
object id of one first bundle, or the set of its holders'
thumbprints.  Under a thumbprint anchor, a first bundle verifies only
where its holders equal the anchored set and every one of them signed
it.  Two first bundles that both do so are a fork of the genesis, and
the reader roots on neither.  A reader with no root runs no agent and
serves no directory or seat of that root until its owner re-anchors
it by an object id (CC 2.6.1.11).

Each holder's key carries an attestation chain for its classical
half.  Where the chain's leaf names its device, the holders a bundle
seats name distinct devices; a bundle that seats two holders on one
device is refused `holder_device_shared`.  Two holders' chains may
share an intermediate or an attestation key, and the leaf's device
decides (CC 4.2.3).

A malformed bundle is Invalid, `genesis_bundle_malformed`, with a
detail.  Two of the details concern the transparency members.  A
charter that carries only some of the three is
`transparency_members_partial`.  A `receipt_quorum` that is not
floor(n/2) + 1 of the n services named is `receipt_quorum_mismatch`
(CC 2.6.1.11).

## The Node Code {#nodecode}

A key's displayed identity is its thumbprint ({{keys}}).  The code a
person hands over is `CIRIS-V4-` followed by the unpadded base32
{{RFC4648}} of a payload and its CRC.  The payload is a version byte
of 4, a kind, and the 32-byte thumbprint of the identity's key.  A
`user` code may also name up to four of its owner's nodes, and a
`node` code names one node.  For each node the code gives the node's
transport identity and an ordered list of up to eight hints for
reaching it.

A hint is a type, a length and a body.  The eight assigned types are
1 `tcp`, 2 `udp`, 3 `auto`, 4 `rnode`, 5 `http`, 6 `i2p`, 7 `kiss`
and 8 `ble`.  A decoder carries a hint of any other type as unknown,
and a dialler skips it.  A hint of a known type whose body is
malformed is refused.  A hint is unsigned and is only a place to
dial.  A minter writes hints from the node's configured, stable
reachability, and never an observed address mapping.

A code is unsigned and confers no authority.  First contact is a
route request made before the link is sealed, anchored on the node
thumbprint the code carries: the dialler keeps the key record it
receives only where that record's thumbprint equals the code's.  A
decoder of this form refuses the codes of the earlier forms by their
prefix (CC 2.6.8).

The same hints stand in a signed row as `dial_hints` on a node's
transport binding: a sequence of one to eight, each a type and a
body, byte for byte those of the code.  The binding of a serve seat
in a genesis bundle carries at least one `tcp` hint, and a bundle
whose seat lacks one is refused with the detail
`seat_dial_hints_missing` (CC 2.6.1.11).

## Receipts {#receipts}

A receipt is a COSE Receipt {{RFC9942}} over the SHA-256 tree of
{{RFC9162}}.  Its hashing is that of {{RFC6962}}.  A Transparency
Service keeps its own append-only log, registers a Signed Statement
in it as one leaf, and issues a Receipt for that leaf under its own
key.  The Receipt states the service's identity, the subject of the
registered statement and the service's own instant of issue.  No
service signs over another party's root.  A stream's receipts cover
batches, never single chunks (CC 2.6.1.11, CC 5.3.1).

A holder may add a receipt to a statement's unprotected header.  The
receipt is outside the signature and outside the row id.

A host does not run code a row admits until it holds a receipt for
a statement of that row from a Transparency Service the host
trusts.  The receipt is the SCITT receipt itself: a COSE Receipt
{{RFC9942}} in the unprotected header's `receipts` parameter (label
394), as {{RFC9943}} carries it.  The service registers the
statement's deterministic COSE_Sign1 encoding with an empty
unprotected header, its leaf hash SHA-256(0x00 || leaf) as
{{RFC9162}} hashes a leaf.  The host's own acceptance edge carries
the service's key, a COSE_Key with its algorithm or an identity
reference, and a receipt under another algorithm does not verify.
The unprotected header is unsigned, so a malformed receipt is
ignored and never makes the statement invalid.  A missing or
unverifiable receipt is not held: the code waits, with the answer
`admission_receipt_missing`.

A host trusts a Transparency Service by its owner's own acceptance
edge of the class `transparency`: one hop, read at the host's `self`
scope, whatever the edge's tier.  The edge carries the service's key as `service_key`, either a
COSE_Key with its algorithm or an identity reference whose key is that
identity's key record.  Anyone may run a Transparency Service under
their own key, and no list of services ships with anything.  A
receipt adds no authority: it witnesses that the statement was
registered, which closes a release seen only by those it was sent to
(CC 2.7.11, CC 4.4.3.34).

## Registered Heads {#heads}

A signer of a head could show one history to one party and another
to a second.  Registration with Transparency Services exposes that:
each service keeps its own log, and two heads at one position that
are both registered leave two Receipts under one service's key.

Lineage heads.
: A root's charter may name `transparency_services`, a set of at
  least two identity references, each to a composite key.
  `receipt_quorum` is exactly floor(n/2) + 1 of the n services named.
  `receipt_cadence_secs` is how often a named service issues a
  Receipt again for an unchanged head.  The three members are present
  together or not at all.  A lineage's head is the bundle in force,
  and a holder's statement over the bundle is the Signed Statement a
  service registers.  A service registers one head for each lineage
  and position, and refuses a second.

: A head is receipted when Receipts for it are held from
  `receipt_quorum` distinct independent services.  The services are
  those the charter of the head's predecessor names, and for a first
  bundle its own charter.  A service is independent of a lineage when
  it is none of the lineage's holders or seats and none of them owns
  it.  Two heads of one lineage at one position that each hold a
  receipt quorum are equivocation: at least one service registered
  both, and its two Receipts name it.

: A Consumer attaches to a root only on a receipted head whose newest
  counted Receipt was issued within the charter's
  `attach_window_secs` before the acceptance edge's own signed
  instant.  A root already attached stays valid until revoked,
  whatever the age of its Receipts.

: A charter that carries none of the three members names no services.
  Its head is current when the holders have counted it and it
  descends from a head the reader holds out of band.  A holder
  majority that shows two heads to two nodes is then not detectable
  on the wire until a row crosses between them.  Naming a service
  confers no standing on it and places no duty on anyone (CC 3.2, CC
  5.3.1).

Stream heads.
: A stream is its own log, and its chunks are the leaves.  A stream's
  head is a signed row of the family `stream:head`, authored by the
  stream's producer.  It carries the stream's epoch, its tree size
  and its root.  A stream's id is `av-` or `file-` followed by 64
  lowercase hexadecimal digits.  An inline blob's one-leaf log is
  named by 64 hexadecimal digits alone, and an inline file publishes
  no head.

: A head that carries `room` is accountable, and one without it is
  best-effort.  A room may name `transparency_services` and
  `receipt_quorum` in its record, for its accountable streams only,
  with the quorum again floor(n/2) + 1.  An accountable head counts
  as published when `receipt_quorum` distinct services of the room
  have registered it.  A service the producer or the producer's owner
  runs does not count.  A service registers one head for each stream
  and tree size, and each later head is offered with a consistency
  proof {{RFC9162}} from the head it last registered.  A room keeps
  no attach window, cadence or quorum for its roster (CC 5.3.3.8).

A node's own audit log of its rows is no Transparency Service: it
issues no Receipt and takes none.

# Admission as a Registration Policy {#admission}

{{RFC9943}} lets each Transparency Service define a Registration
Policy: the checks a Signed Statement must pass before it is
registered.  The CEG admission checks are such a policy.  A Substrate
MUST apply them to every row before storing or relaying it.  It MUST
NOT truncate, repair or re-encode a row in order to admit it.

The checks run in the order of {{verify}}.  Each has one reason.  A
verifier reports `invalid:` followed by the reason, and the vectors
of {{vectors}} carry the same strings.

| Step | Check | Reason |
|---|---|---|
| 1 | The statement is a COSE_Sign1 under tag 18 | `not_cose_sign1` |
| 1 | Statement, protected header and payload are deterministically encoded; no float; a decimal fraction normalised ({{numbers}}) | `not_deterministic:<part>` |
| 2 | The protected header holds exactly the members of {{object}}, or of {{objects}} for an object that is not a row | `unexpected:protected` |
| 2 | The unprotected header holds only integer labels | `unexpected:unprotected` |
| 2 | Each header member has its type and value | `malformed:<member>` |
| 2 | The family id is registered | `unregistered_family` |
| 3 | Each payload member has its type and range, and a required one is present; no null and no tag but those of {{canon}} | `malformed:<member>` |
| 3 | A closed map holds only its members | `unexpected:<map>` |
| 3 | Each set in `refs` is sorted and without duplicates | `set_order:<member>` |
| 3 | A number is within CBOR's integer range ({{numbers}}) | `body_number_unrepresentable` |
| 3 | Each disclosure is well formed | `malformed:sd-disclosure` |
| 3 | Each disclosure opens one digest the payload carries, once | `disclosure_unmatched` |
| 3 | No redaction digest appears twice | `duplicate_digest` |
| 3 | `dimension` is claimed by a registered family | `dimension_unregistered` |
| 3 | `dimension` resolves to the header's family | `dimension_family` |
| 3 | `dimension` passes the namespace rules of {{CC}} | `dimension_refused:<token>` |
| 3 | The payload meets its family's own rule | `edition2_payload_invalid` |
| 4 | `iat`, `nbf` and `exp` equal the payload's instants, each present exactly where its payload member is | `time:<claim>` |
| 4 | `valid_until` is later than `asserted_at` | `valid_until_not_after_asserted_at` |
| 5 | A key record's `identity_type` is a sorted set of text strings | `key_record_bad_identity_type` |
| 5 | A key record's roles do not mix a person's with a machine's | `key_record_mixed_roles` |
| 5 | A key record meets its end rule ({{key-records}}) | `key_record_out_of_window` |
| 5 | A key record's `attestation_evidence` is a map, and its `pq_custody`, where present, one of the three values | `key_record_bad_pq_custody` |
| 5 | A key record of a class whose mechanism has a chain carries `chain` | `key_record_bad_attestation_evidence` |
| 6 | The held key has the thumbprint `kid` | `kid_mismatch` |
| 6 | The signer's key record is not itself Invalid | `key_not_valid` |
| 7 | The composite signature verifies | `bad_signature` |
| 8 | `kid`'s key is a key of `iss` ({{key-of-iss}}) | `kid_not_of_iss` |
| 9 | Whether the family is authored or counted can be read | `authorship_undetermined` |
| 9 | `author` is present on an authored family and absent on a counted one | `author_column` |
| 9 | `iss` is the author or fills a role the family names | `iss_not_in_role` |
| 9 | A family that scores a dimension carries one | `dimension_missing` |
| 9 | A row supplied as the target of a `withdraws` or a `recants` is the row `refs.target` names | `target_mismatch` |
{: #tab-verify title="Verification checks and their reasons"}

Steps 6 and 8 also answer Waiting, as {{tab-waiting}} lists.

## How a Reason Is Written {#reason-names}

A name in angle brackets stands for the part, member, map or claim at
fault.

`<part>` is `statement`, `protected` or `payload`: the encoded item
that is not in the deterministic encoding.  A float and a decimal
fraction that is not normalised are second encodings of the payload,
`not_deterministic:payload`.

`<claim>` is `iat`, `nbf` or `exp`.

`<map>` is the closed map that holds a key it does not admit:
`protected`, `unprotected`, `refs` or `also`.  A protected header
that lacks a member it requires is `unexpected:protected` as well,
since the header holds exactly its members.

`<member>` follows one rule.  It is the innermost member of the row
that the schema of {{cddl}} names and whose value holds the fault.
The row is the protected header and the payload ({{object}}).

- A member of the payload, of `refs` or of `body` is named by its
  text key, as in `malformed:score`, `malformed:head` and
  `set_order:further_heads`.
- A member of the protected header or of the CWT claims has an
  integer label, and is named `alg`, `cty`, `kid`, `typ`, `row-type`
  (label -70001), `family-id` (label -70002), `iss`, `sub`, `iat`,
  `nbf`, `exp` or `edition` (label -70003).
- A fault in an element of an array is reported under the member that
  holds the array.
- A role of `also` is a key of a registry and not a member
  ({{refs}}).  A fault in a role's set is reported as `also`.
- A required member that is absent from the payload is reported under
  its own name, as in `malformed:asserted_at`.

Where no member that the schema names holds the fault, the name is
that of the rule of {{cddl}} that the value fails.  There are two
such places.  A family's own member is typed by the schema as
`ceg-value` and is not named by it, so a fault in its value, at any
depth, is `malformed:ceg-value`.  A disclosure travels beside the row
and is no member of it, so a fault in one is
`malformed:sd-disclosure`.  The key of a family's own member never
stands in a reason, and the reasons stay a closed set.

A statement with more than one fault is Invalid at the first step
that fails.  This document fixes no order among the faults of one
step.

The token after `dimension_refused:` is the namespace token of
{{CC}}.

Three prefixes say at which level an answer was given.  A statement
read alone answers `valid`, `invalid:` and a reason, or `waiting:`
and what is missing.  A statement read under its family answers the
checks of step 9 as `family_invalid:` and the reason, and where a
role admits its signer it answers `valid:role:` and the role's name.
The check of a key record's payload alone answers `ok` or the bare
reason.  The files of {{vectors}} write them so, and the later
key-of-issuer file writes `family:` for `family_invalid:`.  Several
statements read as one row, where their payloads differ, answer
`several_rows` ({{counted}}).

## Refusal Tokens {#tokens}

A Substrate refuses a row with a token.  {{CC}} names the tokens of
{{tab-admit}} for the checks a Substrate makes at every write path.

| Check | Token |
|---|---|
| Payload at most 1 MiB ({{canon}}) | `envelope_too_large` |
| Type is one of the five ({{types}}) | `attestation_type_unregistered` |
| No optional member is null ({{relays}}) | `federation_malformed_row`, with the reason `envelope_member_null` |
| Each set is sorted and without duplicates ({{canon}}) | `federation_set_semantics_unsorted`, naming the member |
| Termed delegation within 365 days ({{types}}) | `delegation_term_required` |
| Withdrawal meets {{withdraw-rule}} | `federation_withdraws_not_admitted` |
{: #tab-admit title="Admission checks and their tokens"}

The first check needs no verification: a Substrate refuses at its
ceiling without completing the decode.  The last two are made on a
statement that verified.

The other three are faults that verification also finds, so a
statement that has one never verifies.  A verifier and a Substrate
then name one fault in two vocabularies, and neither name is a second
check:

| Fault | Reason, from a verifier | Token, from a Substrate |
|---|---|---|
| A row type outside the five | `malformed:row-type`, at step 2 | `attestation_type_unregistered` |
| A null member | `malformed:<member>`, at step 3 | `federation_malformed_row`, `envelope_member_null` |
| A set out of order, or with a duplicate | `set_order:<member>`, at step 3 | `federation_set_semantics_unsorted` |
{: #tab-both title="Faults that have a reason and a token"}

A Substrate that emits a row checks its type before any statement
exists, which is why {{CC}} states that check at admission and
applies it to emission and to replication alike (CC 2.4).

{{tab-verify}}, {{tab-waiting}} and {{tab-admit}} are the complete
list for a row statement read alone or under its family.  What a
fold concludes from several rows has its own names, such as those of
{{standing-end}}, and {{CC}} lists them.  The reasons of
{{tab-verify}} are those the verifier's vectors carry at the commit
{{vectors}} pins, with three that no row statement vector carries:
`kid_mismatch`, and `edition2_payload_invalid` and
`key_record_bad_attestation_evidence`, which {{CC}} names.

{{CC}} names in its own text `kid_not_of_iss`,
`key_record_out_of_window`, `valid_until_not_after_asserted_at`,
`body_number_unrepresentable`, `edition2_payload_invalid`,
`key_record_bad_pq_custody`, `key_record_bad_attestation_evidence`
and the tokens of {{tab-admit}}.  It states the remaining checks
without a name, and it does not state the rule for `<member>` above.
The HTTP error codes of {{CC}}'s write path are transport status and
are not reasons of this document.  A refusal for size is
`envelope_too_large` on every write path, and over HTTP it is carried
as status 413 with the error code `ENVELOPE_TOO_LARGE` (CC 2.6.1.6,
CC 5.3.6.1).

Admission has a third outcome besides admit and refuse.  A row whose
verification answers Waiting ({{verify}}) is held and retried, never
counted, until what it waits on is held.

The namespace rules that decide whether a dimension is registered,
and their tokens, are defined in {{CC}} and are outside the scope of
this document.

## Who May Withdraw a Row {#withdraw-rule}

A `withdraws` row against a target row T is admitted when its signer
meets one of these rules:

Rule 0:
: If T is a counted row, rules 1 to 4 do not reach it.  T is
  withdrawn only by a `withdraws` counted under T's own rule.  A
  quorum's act is undone only by a quorum.

Rule 1:
: The signer signed T.

Rule 2:
: The signer is named in T's `subject_key_ids`, and T's family is not
  on the kept list below.

Rule 3:
: The signer is a proxy for a party T names by canonical hash.  It
  holds a live `delegates_to` chain to that hash whose scope includes
  `consent_revocation`.  T's family is not on the kept list.

Rule 4:
: The signer holds a live `delegates_to` from a party of rules 1 to
  3, and the kept list binds it as it binds them.

Where T names several parties, an admitted withdrawal from one
retires T for all of them.  A withdrawal reaches forward only: acts
under T that the withdrawal has among its ancestors still stand
({{standing-end}}).

The kept list stops a named party from withdrawing a third party's
adverse finding about itself, such as a detection, a licensing
decision or a moderation record.  {{CC}} lists the families it
covers.  The named party's route is to contest the row.

A key revocation is never withdrawn.  An entity revocation, an
occurrence revocation, a key grant, a cosignature already sent and a
receipt of acts ({{standing-end}}) are never withdrawn either (CC
2.4.1.1).

Recantation is not covered by these rules.  Only T's signer can
recant T.

## The End of a Standing {#standing-end}

A standing is what a row confers on a key: a seat, a grant, an
owner's binding.  A withdrawal or a cut can end it while its holder
is still signing.  No instant decides which of the holder's acts
count.  The rows name heads, and a node reads those (CC 2.4.1.1).

An act names its head.
: A row signed in exercise of a standing names the head it is at, in
  `refs.head`.  The head is the newest its signer holds of the record
  that seats the standing: the roster version for a seat in a room or
  a family, and the bundle in force for a grant from a root.  A row
  signed under a root grant names that bundle, and names under the
  `also` role `stands_on` the acceptance of the grant that it stands
  on.  One that names the bundle alone, or names a binding, stands on
  no acceptance and counts for nobody.  Where one row between two
  keys is the whole record, as an owner's binding is, that row is the
  head.  A row that exercises a standing and
  names no head concludes nothing, `act_names_no_head`.  An
  acceptance or a decline names none, since it names the row it
  answers.  A halt names none, since it fires at each node on receipt
  ({{halt}}).

An end names the head it acts from.
: A row that ends a standing carries `refs.head` beside its target.
  That head is the newest its signer holds.  An end with a newer head
  in its own past concludes nothing, `end_names_old_head`.

Counted, and in force.
: An act with the end in its past does not count under the ended
  standing.  An act at the end's head, at an older head or at a
  concurrent one counts at its own head, and from the end's head on
  it is not in force.  The end never undoes that count.

Receipts.
: Such an act stays in force after the end where a clean receipt of
  it is held that does not have the end in its past.  A receipt is a
  row of the family `act:ack`.  It names each act it acknowledges
  under the `also` role `ack`, at most 256 of them, and it names no
  head.  It has those acts in its past, and it is clean when that
  past holds no cut of them by its own key.  The receipt is the
  conferrer's, another holder's of the body the act was done for, or
  that of a receipter the offer names in `receipter`.  It is never the act's own signer's and never a
  node's.  A receipt changes what is in force, never what counted.

Lifting.
: A counted row that ends a standing may state `lifts`.  Then only
  the count's own receipts keep an act in force.  An end by the one
  whose standing it is lifts nothing, and `lifts` on such an end is
  refused, `lifts_on_own_end`.

Another standing.
: An act that another live standing of its signer authorises at its
  head stands on that standing.

A device that has not seen the end may sign an act at an older head.
That act counts there and is never in force after the end.  No reader
can tell it from an honest earlier act, and no rule tries.

A key's revocation is read differently, by signed instant: a
statement by a revoked key stands where its `asserted_at` precedes
the revocation's `revoked_after`, and a revocation without that
member revokes all (CC 2.4.1.1).

# The Safety Model the Rows Carry {#safety}

This section is informative.  {{CC}} is normative for every rule it
summarises, and the section numbers given are those of {{CC}}.

CEG serves a network with no central operator.  No party can enforce a
safety rule for the others, so each rule has to be carried by the rows
themselves and checked by each node on its own.  This section says
which member or check carries each property, and what is not claimed.

## Two Planes

The network has a public plane and a private plane.  The CIRIS
documents call them the lightnet and the darknet.

The identity plane (lightnet) is public.  Key records, announced
transport destinations and trust roots are visible to every node, and
the plane makes no anonymity claim.  A node attributes every inbound
message to a key before any handler sees it.  A device that has not
yet been bound to an owner can still open a connection, but only under
its own self-signed key, so it is unowned but never anonymous (CC 3.2).

The group plane (darknet) is derived from the identity plane.  Each
member of a family or community computes the group's address from
directory state it already holds, so the address is never announced.
An outsider cannot map an address to a group or fetch its content (CC
5.2, CC 5.4.6).  An observer of link traffic can still see which node
opens links to some derived address, and the timing and size of that
traffic.  Members relay for members.

## Consent-Bounded Flow

The rows apply the idea of contextual integrity: information flows
appropriately when the flow matches the norms of the context it came
from.  Each row signs its own context.  `iss` and `author` say who
sent it, `sub` and `subject_key_ids` say whom it is about, and
`cohort_scope` says who may see it.  All of these are in the protected
header or the payload, so a relay cannot change them without breaking
the signature.

A Consumer accepts a row only if it trusts the signer's root or has
consented to receive from the signer, and a row reaches no one else
(CC 4.4.3.34).  A row defaults to the smallest scope that fits its
purpose; `federation` scope, the public commons, is an explicit choice
(CC 1.13.3.4).  Consent is itself a row, and a subject can withdraw a
row about itself ({{withdraw-rule}}).  Content in a private scope is
never scanned.  Known abuse images are checked for only when content
is moved to `federation` scope or posted to a public room (CC
1.13.3.4).

## Delegation

Only delegation composes.  A Consumer walks the `delegates_to` graph
with a depth cap and a cap on aggregate weight (CC 2.4.1.3, CC 4.1.1).
The walk visits each key once, so a cycle adds no reach.  A row that
closes a cycle is not refused or discounted for it.

## Accountable Key Relationships

Some parties cannot accept obligations for themselves.  The rows give
each of them a named human:

- An `agent` key MUST be bound to a human steward before it is
  admitted to any community.  A `node` key MUST be so bound before it
  is admitted to any community other than an infrastructure community
  (CC 3.2).

- A minor has one or more guardians, each bound by a signed row of
  their own (CC 3.2, CC 3.4.13).

- A community names the holders of its moderation duty in its
  founding record.  A seat is two consents, the placer's and the
  holder's, and it goes only to a member.  If no duty holder is left,
  the community locks to read-only and its members elect one (CC
  4.5.4).

## A Bounded Human Halt {#halt}

A trust root names a set of human holders.  Any one holder can pause
the AI agents of the nodes that accepted that root.  The halt is one
row with one statement, the holder's own, and it fires on receipt
with no window.  A holder may sign one in advance and keep it sealed
(CC 4.2.1.1).

A halt by one holder lapses a fixed time after each node received it:
`halt_fuse_secs` in the charter, 24 hours when absent.  It stands
longer only if a strict majority of the standing roster confirms it.  A strict majority may resume a halt at any time.  The
confirmation and the resumption are counted rows ({{counted}}): one
statement from each holder, over one payload (CC 4.2.1.3).

There is no rate bound on a holder's lone halts.  A missed halt is
the one failure that cannot be recovered from, so the one-holder stop
is never rationed.  A rogue holder is answered by the fuse, by a
strict majority's resumption, and by removal through a later genesis
bundle.  Roster changes and recoveries are later bundles, counted
over the standing roster ({{objects}}, CC 4.2.6).

A halt pauses the effectful acts of AI agents and does nothing else.
It does not stop a node, and it does not touch stored data, messages
or network service.  An agent checks the latch before every
effectful act.  A halted agent may still raise a deferral to a human.

The halt is the condition of symmetry between people and the AI
agents they make.  Consent that cannot be withdrawn was never
consent, and withdrawal needs a halt outside the system halted (CC
1.13.2).  A root can tell a node to
share less, never more.  A node that never accepted the root is not
affected.  Acceptance of a root is a person's row, and a node reads
its owner's.  An owner leaves a root by withdrawing that one row, for
every node and agent the owner holds (CC 3.2); a halt that has
already reached a node still binds it (CC 4.2.1).

## What Is Not Claimed

Where {{CC}} speaks of anonymity, it means anonymity toward outsiders:
a group's existence, and what its members do in it, are hidden from
non-members.  Beyond that:

- The identity plane is not anonymous.
- The base design does not resist a global passive observer of
  traffic.  {{CC}} specifies an opt-in Anonymous Tier, using layered
  onion routing, for deployments that need that protection (CC
  1.13.3.1, CC 5.4.6).  This document does not describe it.
- Members of a group can read, and keep, what the group shares.
  Ballots within a group are signed rows, accountable to its members.
  A community may instead hold a secret poll through the census (CC
  6.1.9).
- Nothing is detected inside private groups.  The design declines
  client-side scanning.

{{CC}} also states limits that hold against an attacker (CC 2.7.9).
Among them:

- A relay can choose the order of delivery, and withhold a row until
  it is delivered.
- A relay can withhold the row that would answer a window until one
  node's clock has closed it.  That node's answer then differs for
  good from a node that held the row in time.  The halt's fuse is one
  such window; a fresh halt is the remedy.
- Whoever holds an ended key's private half can revive it.  Only the
  key's own revocation makes its end final.
- Keys that met a past count can fork on a past head.  Whoever
  controls a new reader's first view can make a wrong head stick.

On aggregation, correlated sources are discounted, and fully
correlated sources count as one.  Sources that stay independent on
every measured act and coordinate only on one decisive act show no
correlation until that act.  No measure over the past can see them (CC
6.1.2.3).

# Relationship to SCITT {#scitt}

This section is informative.

## Roles

| SCITT role ({{RFC9943}}) | CEG counterpart |
|---|---|
| Issuer | The signer, named by `iss`. |
| Signed Statement | A statement: one COSE_Sign1 by one signer. |
| Registration Policy | The admission checks of {{admission}}. |
| Transparency Service | A service a root's charter or a room's record names for its heads, or one a host trusts by its owner's acceptance edge; CEG fixes none ({{receipts}}, {{heads}}, {{deltas}}). |
| Receipt | A COSE Receipt {{RFC9942}} from a service's own log: for a registered head, or the receipt a host requires before it runs admitted code ({{receipts}}, {{heads}}). |
| Transparent Statement | A statement with a receipt in its unprotected header. |
| Relying Party | A Consumer. |
{: title="SCITT roles and their CEG counterparts"}

A CEG statement is a COSE_Sign1 with `iss` and `sub` in the CWT
Claims header of {{RFC9597}}, as {{RFC9943}} requires.  It can be
presented to a SCITT Transparency Service as it stands.  A counted
row is several Signed Statements over one payload.  A Transparency
Service would register each one separately; CEG relates them by the
row id ({{names}}).

## Differences {#deltas}

Algorithm.
: The composite signature uses the private-use COSE algorithm
  identifier -70100.  A Transparency Service or Relying Party must
  support that construction to verify a statement.  Its parent drafts
  {{COMPOSITE-JOSE}} and {{COMPOSITE-LAMPS}} are not yet published as
  RFCs.  The header labels -70001, -70002 and -70003 are also from
  the private-use range.

Registered values.
: The content type `application/vnd.ciris.row+cbor` and the `typ`
  values `ceg-row/2` and the three object kinds are used without
  registration.  This document requests no IANA action for them.

Transparency Service.
: CEG fixes no Transparency Service and no registrar.  A node admits
  a row by its own checks, and what it serves is decided by trust the
  reader chose.  Registration is asked for in three places.  A root's
  charter may name the services its lineage heads are registered
  with, a room's record may name them for its accountable streams
  ({{heads}}), and a host runs code a row admits only once it holds a
  receipt from a service its owner trusts ({{receipts}}).  Each
  service is SCITT's own and keeps its own log.  Its receipt shows
  registration and confers no standing.

Registration Policy.
: {{RFC9943}} has the Transparency Service evaluate its policy and
  requires the policy itself to be registered, so that Auditors can
  reproduce the decision.  The CEG checks read the payload as well as
  the headers.  They are fixed by {{CC}} rather than registered as
  statements.  Any party can reproduce an admission decision from the
  row and the checks, but the checks are not themselves on a log.

Receipts.
: A SCITT Receipt is issued at registration by the service, and a
  CEG receipt is the same: each service issues its own, from its own
  log.  Nothing requires a receipt when a row is admitted.  Attaching
  to a root that names services requires a receipt quorum for its
  head, an accountable stream head is published by one, and running
  the code a row admits requires a receipt from a service the host
  trusts ({{heads}}, {{receipts}}).  A holder may add a receipt to a
  statement's unprotected header.

Quorums of services.
: {{RFC9943}} leaves to a Relying Party how many Receipts it asks
  for.  {{CC}} fixes a count: a head is receipted at a
  strict majority of the services named for it, and only services
  independent of the lineage count ({{heads}}).  A lineage whose
  charter names no services has no such check.  Its holders can show
  different heads to different peers until a row crosses between
  them.

Statement content.
: SCITT leaves the meaning of a statement to its issuer.  CEG fixes
  the five row types and requires every claim to name a registered
  family, so a Consumer can interpret any admitted row without
  out-of-band agreement.

Waiting.
: A CEG verifier can answer Waiting on a key or a row it does not
  hold, and hold the statement inert ({{verify}}).  A SCITT
  Registration Policy admits or refuses.

Statement identifier.
: {{RFC9943}} defines no identifier for a Signed Statement.  The CEG
  statement id is a name of this profile ({{names}}).  It covers the
  protected header and the payload, as the COSE `Sig_structure` does
  with an empty `external_aad`, and is a different digest from one
  over the `Sig_structure` or over the whole COSE_Sign1.

## Registering a Head {#loghead}

Revision -03 of this document proposed that the signer of a log's
head register each head with a Transparency Service as a Signed
Statement.  {{CC}} states that rule, and {{heads}} describes it.  A
stream's head is a `stream:head` row, a lineage's head is the bundle
in force, and each is a Signed Statement a service registers as it
stands.  The services are named in signed bytes: by a root's charter
for its lineage, and by a room's record for its accountable streams.

Two registered heads at one position are proof of equivocation,
signed by the equivocating keys and held by a third party.  A head
that is registered with no service is single-signer, and its readers
compare heads themselves.

This is the method of Section 8 of {{I-D.sparysh-pala-audit}}, where
a chain head is carried to a Transparency Service as a signed
statement that also carries the derived root.

# Lifecycle of an Agent Decision {#lifecycle}

This section is informative.

Other individual drafts record AI agent actions as a sequence of
logged events: an authorisation before the act, a record of the act,
and a refusal where the agent declined.  The Artificial Intelligence
Governance Architecture {{I-D.aylward-aiga}} logs agent activity in
Merkle trees and is the closest in aim.  PALA-1
{{I-D.sparysh-pala-audit}} defines a tamper-evident audit record for
inference runtimes and carries its chain head to a Transparency
Service.  In CEG the same events are rows.  The reasoning steps before an act are rows in the decision
families of {{CC}}.  The act is recorded by one row whose dimension is
`trace:complete:v1`, ending in a terminal result.  That trace, its
components, levels and signing are specified in
{{I-D.moore-scitt-ciris-trace}}, and the context manifest of each
model call within it in {{I-D.moore-scitt-ciris-trace-context}}; this
document specifies only the row that carries it.  A completed action,
a refusal, and a deferral to a human are the same kind of row with
different terminal results, so a Consumer reads all three the same
way.  Authority to act, and any transfer of it, is a `delegates_to`
row.

# Open Issues {#open}

Note to the RFC Editor: please remove this section before publication.

- The composite algorithm has no assigned COSE identifier, and the
  drafts that define it may still change ({{deltas}}).

- Several encodings are open in {{CC}}, each waiting on its owner.
  They include the payload rule of `ceg-boot-manifest/2` and the
  family of an agent's text manifest statement.  {{CC}} lists them in
  its table of open encodings (CC 2.6.1.12).

- {{CC}} names only some of the reasons of {{admission}} in its own
  text ({{tokens}} says which), and it does not state the rule by
  which a reason names a member ({{reason-names}}).  It is to adopt
  both as written here.

- {{CC}} lists two vector files at versions that predate its own
  text, and this document pins their successors ({{vectors}}).

- {{CC}} states its verification order with Waiting at steps 6 and 8
  alone.  A `withdraws` or a `recants` row read under its family can
  also wait on its target ({{verify}}), and {{CC}} gives that reading
  no step.

- {{CC}} does not state the row type of a rotation record, the
  answer of a verifier that holds bare keys, the `iss` of the bound
  key's statement over an occurrence, or the answer for a statement
  dated at or after its key's own revocation.  For the first three
  this document gives what the pinned vectors carry ({{key-of-iss}},
  {{vectors}}).  For the fourth it gives only the rule of {{CC}}
  ({{standing-end}}), and no vector carries a reason.

- No row statement vector carries the detail
  `rotation_after_revocation`, a role of `also` other than `ack` and
  `cites`, or a pair of statements that differ only in the
  unprotected header.  Such a pair
  is proposed for the next row statements file;
  {{kat-statement-id}} states what it shows.

- Known-answer vectors of the revocation snapshot and the boot
  manifest are not yet published.

- No second implementation exists ({{implementation-status}}).

# Implementation Status {#implementation-status}

Note to the RFC Editor: please remove this section before publication,
together with the reference to {{RFC7942}}.

This section records the status of known implementations at the time
of writing, as described in {{RFC7942}}.  Listing an implementation
here does not imply endorsement.

CIRISVerify:
: Verification library (Rust), CIRIS L3C, AGPL-3.0.  It publishes the
  known-answer vectors of the form this document describes
  ({{vectors}}).  <https://github.com/CIRISAI/CIRISVerify>

CIRISPersist:
: The storage and admission engine (Rust), CIRIS L3C, AGPL-3.0.  Its
  release v59.1.0 implemented the earlier form ({{earlier}}).  This
  document makes no claim about its support for the form described
  here.  <https://github.com/CIRISAI/CIRISPersist>

No second, independent implementation of the full signing and
admission path exists yet.  A reader working from the text of
revision -03 alone has run the known-answer cases of a statement, a
key record's payload, a value and an object, and this revision
answers what that run found ({{vectors}}).

# Security Considerations

This section follows the guidance of {{RFC3552}}.

Deterministic encoding.
: A verifier that re-encodes a decoded payload before checking the
  signature can accept bytes the signer never signed, or reject bytes
  it did.  A verifier MUST check the bytes received and refuse any
  encoding that is not deterministic.  Implementations should test
  against the refusals of non-deterministic encodings in {{vectors}}.

What the signature covers.
: The protected header and the payload are signed; the unprotected
  header is not.  No admission check reads the unprotected header;
  the host's receipt check reads it and grants nothing.  Who a row
  is about and who may see it are in the signed bytes, so a relay
  cannot redirect a validly signed row.

Composite signature.
: Both halves sign one representative that names the composite
  label, so neither half verifies alone.  A forger must break both ML-DSA-65 and
  Ed25519.  A verifier MUST NOT accept a statement on one half.  A key
  is one composite key, and a statement whose signer's key record is
  not held is Waiting, never Valid.

Identity references.
: `kid` and `iss` carry full 32-byte thumbprints, not short
  fingerprints.  A verifier resolves `kid` to a key record and
  verifies with the full composite key that record holds.

The issuer is a claim.
: `iss` is signed by whoever signs the statement, so a signature that
  verifies does not show that the signer is the identity `iss`
  names.  A verifier MUST check that `kid`'s key is a key of `iss`
  ({{key-of-iss}}) before it treats the statement as that issuer's.
  A Relying Party that reads `iss` from a statement it has not
  verified through step 8 of {{verify}} reads an unchecked claim.

A name is not a signature.
: A row id, a statement id and an object id are digests of bytes.
  Two parties that hold the same id hold the same bytes, and nothing
  more follows.  An id is computed without any key, so anyone can
  compute the id of a statement nobody signed.  A statement id leaves
  out the signature and the unprotected header, so a statement with a
  corrupted signature has the id of the valid one.  An id is evidence
  of a statement only together with a verification of that statement
  ({{names}}, {{verify}}).

Rotation.
: A rotation record links a new key to an identity only with the old
  key's statement and the new key's own.  A verifier MUST NOT accept
  a new key on the new key's word, or on the old key's alone.  Two
  successors of one key hand on nothing, so a thief of an old key who
  rotates it cannot displace the holder's own rotation: both are
  refused until one rotation names both.  The thief can block the
  hand-on in that way.  {{CC}} leaves the pair to the key's owner,
  who binds one successor (CC 2.4.1.1, {{rotation}}).

Withdrawal.
: The withdrawal rules let parties other than the signer retract a
  row.  The rules in {{withdraw-rule}} stop a subject from removing
  adverse findings about itself, and stop any single key from undoing
  a quorum's act.

Unregistered heads.
: A head that is registered with no Transparency Service stands on
  its signers alone.  They can show different histories to different
  peers until the heads are compared.  A root whose charter names no
  services, and a best-effort stream, are in this case ({{heads}}).

Clock-dependent readings.
: A window closed on one node's clock, such as the halt's fuse, is
  read differently by nodes that held a row at different instants.
  {{CC}} states which readings depend on a node's clock and gives
  them no meaning beyond that node's own (CC 2.7.9).

Size.
: The 1 MiB limit applies to the deterministic encoding.  An
  implementation that reads an unbounded input in order to find out
  whether it fits is open to memory exhaustion.  Each write path
  needs its own read limit.

# Privacy Considerations

This section follows the guidance of {{RFC6973}}.

Stable identities.
: `iss` names a signer's genesis key and does not change when the
  signing key rotates.  Every row a signer makes can therefore be
  linked to every other.  Statements carry thumbprints, not
  human-chosen labels.

Subjects without keys.
: A canonical identifier is a hash of a platform, entity kind and
  identifier.  Where the identifier space is small, the hash can be
  reversed by enumeration.

Low-entropy rows.
: A row whose content is guessable, such as a ballot, carries a
  random salt in its payload.  Without it, the row id would confirm a
  guess.

Audience.
: `cohort_scope` limits which nodes may receive a row.  It is signed,
  so a relay cannot widen it.  It does not encrypt the row; a node
  inside the audience can read and keep it.

Withdrawal is not erasure.
: A `withdraws` row stops a claim from standing.  It does not remove
  the original row from nodes that already hold it.  Members minted
  blind ({{erasable}}) can be erased by dropping their disclosures,
  which alters no signed byte.  {{CC}} defines a separate removal
  procedure for the rest.

# IANA Considerations

This document has no IANA actions.

--- back

# CDDL {#cddl}

The following CDDL {{RFC8610}} describes the statement, the protected
header, the payload, the names of {{names}}, the composite key, the
key record, the other signed objects and the accord's rows.  It is
the schema of {{CC}}, wrapped to fit this document.  Where a string
was too long for one line, it is split with the `.cat` control
operator of {{RFC9165}}.

~~~ cddl
{::include signed_object.cddl}
~~~

# Test Vectors {#vectors}

The known-answer vectors of this form are the verifier's
{{CC-VECTORS}}.  {{CC}} 1.0-rc22 is the tag `v1.0-rc22`, commit
f4671933f2b22b33d2db868d4654036162104123.  It vendors the models and
proofs of its causal kernel (CC 2.7), the proof of the key-of-issuer
check of {{key-of-iss}} among them, from the repository CIRISKernel
at the tag `kernel-v0.3.0`, commit 5e5a40906eea.

Every vector file of this document is pinned at one tag of
CIRISVerify, v23.4.1, which is commit
732c44847cc8d0e3bd2779fd186b504478584623, and by the SHA-256 digest
of the file at that commit.

The files for a row statement and its keys:

~~~
edition2/row_statements_v4.json
  ec83f2d8dc4080c62bc5482d7eaa99f778d374c8f126df884ee416cf67cb0b93
edition2/key_of_iss_v3.json
  371eebcb647e802d522bf44fd979d7faa338d87c42a6af0377e5ab4aaab3a8f9
edition2/key_of_iss_v1.json
  bd584d9b31b7271dc86c05a29eec75044b5fe74aae8dd586701a227f09001333
edition2/composer_v1.json
  a795e8a8cb0200d87d913882ce90dfcf9ce349232602f085036922bc9f0b6d08
mldsa65_ed25519_draft_kats.json
  7dc03ce5e7da7d54c2e1616593bce53ff4a09b0cb52b787a0a6061a22eb102f3
~~~

The files for the trust root of {{objects}}, the halt of {{halt}},
the node code of {{nodecode}}, and the receipts and stream heads of
{{heads}}:

~~~
edition2/genesis/genesis_bundles_v6.json
  82778bc136e33af7c3c6eaf9fde763b74096868a5186f931f69c3e969bb97be9
edition2/genesis/genesis_holder_device_v2.json
  0c9a4514cdbaf19633116295bfeb1d49689dcee13e8dee0bb85c3dd99da9463d
edition2/genesis/genesis_commitments_v2.json
  b4220cc7bd61653f795b819c88d0ebf6499e1ab1df8f136798407c4fecd9ab82
edition2/genesis/genesis_reseat_v4.json
  f95e69d1dc79530266f953344c53d62274b885e3610d22a9033ac98f36e44f90
recovery_commitment/recovery_commitment_v1.json
  cf552e323d06776c42c3da25ad8b2a01874e622402fcbbee0be77c41d0a521a2
accord_halt/accord_halt_v2.json
  a70536271ee3d19af4390c4c603e17a4cba54fa18449d6296d3696f6756e9581
fedcode/fedcode_e2_v1.json
  f00bae960c2a498171b7eb3ff461cb09624c72832af001bdfd7590511db3b386
edition2/receipts/receipts_v1.json
  d7e8cb35191c2094fa1cac744d8b28a0aa650e8d786e78be7689cbd8dbe474e8
edition2/receipts/stream_heads_v1.json
  a8e88d02039c3631244ad191b482b59a601d0ac2e8470098d42883c077df3da2
stream_key_binding_v2_composite_v3.json
  4f2c4dd780fc19b428a693ed01022893cc721bc1f5f82bc17878ad0c4984740f
~~~

The two files whose names begin `mldsa65` and `stream_key_binding`
are under `src/ciris-crypto/tests/vectors/composite/`.  The others
are under `src/ciris-verify-core/tests/vectors/`.  The composite
signature's vectors are checked against the examples of
{{COMPOSITE-JOSE}}.

A key of the vectors is made from a seed n: its ML-DSA-65 seed is 32
bytes of the value n, and its Ed25519 seed is 32 bytes of the value
n + 100.  Both signatures are deterministic, so a second
implementation that signs the same input reproduces a valid
statement byte for byte.

## What the Files Hold

The row statements file holds five valid statements and 50 refusals,
each with its answer.  It holds 17 key record payloads read alone, 6
statements read through a directory of key records, 6 statements of
objects that are not rows, 11 values read as references, and 46
statements read under a family.  A value read as a reference answers
`row` for the array `[-16, digest]` over a 32-byte digest, `key` for
an identity reference, and `neither` for anything else.

The later key-of-issuer file, `key_of_iss_v3.json`, holds 32 cases of
steps 4, 6, 8 and 9: the end rule, a record's cover of an instant, a
rotation with and without each statement, a seat in the bundle in
force, an occurrence that binds a key, and a row its subject authors.
In it the bound key's statement over an occurrence carries that key's
own identity reference as `iss`.  One that carries the identity's is not read as
proof of possession, and the answer is Waiting on the key's
statement.  A key that the bundle in force seats is read from the
seat, with no key record of its own.  An eviction of an occurrence
evicts nothing for a statement dated before the instant the eviction
takes effect, and nothing at all where a key that is not of the
identity signed it or where its signer's key is not held.

The earlier, `key_of_iss_v1.json`, holds 24 cases, and is the file
with the cases of a verifier that holds bare keys, of a contested
rotation, of a rival that names a record which does not cover it, and
of a chain of two rotations.  In both files a key record, a rotation
record among them, is a `scores` row of the family `key:record` with
no `author`.  The earlier file was written before {{CC}} stated that
a row waits for a statement it lacks, and two kinds of its answers
are read by that rule today:

- where a key record or a rotation record lacks a statement, the file
  answers `invalid:kid_not_of_iss`, and the answer of this document
  is Waiting on that statement ({{key-of-iss}}), as in its cases
  `rotation_without_predecessor_statement` and
  `rotation_without_own_statement`;
- in two cases where the record that a rotation names is not held,
  `rotation_genesis_not_held` and `rotation_two_hops_middle_missing`,
  the file answers `waiting:kid:` and the key of that record, and the
  answer of this document is `waiting:record:` and that record's row
  id.

Every other answer of the file stands.  The cases of
`key_of_iss_v3.json` whose names begin `rotation_` give the later
answers.

The composer file holds 15 cases of rows read under a family: a
`withdraws` or a `recants` under the family of its target, and a
`supersedes` under its own ({{family}}).

One case of the row statements file has two faults.
`names_earlier_form` carries a faulty reference in `refs.target` and
faulty references under `refs.also`, and its reason names `also`,
which comes first in the encoding of `refs`.

{{CC}} lists the row statements file at its third version and the
key-of-issuer file at its first alone, both at the tag v23.3.0 (CC
2.6.5).  Revision -03 of this document pinned those.  The third
version of the row statements file predates the rule that each key
signs its own record, and the end rule of step 4.  The fourth differs from it in three places: its
directory cases are read by a key's own statement over its record
({{key-records}}), a key record whose `valid_until` equals its
`asserted_at` is refused, and the cases of a decimal fraction are
added ({{numbers}}).  The other 125 cases are the same bytes with the
same answers.

## A Row Id Known Answer

The first valid statement of the row statements file,
`authored_score`, is a `scores` row of the family
`evidence:.suite:.kind:.cell:.prefix`, with `sub` `subject-1` and its
signer as `author`.  Its payload is these 236 bytes:

~~~
a66573636f72651a000b71b066617574686f72784d75726e3a696574663a70617261
6d733a6f617574683a636b743a7368612d3235363a31764356747a696834592d324c
366b6b65414e686963754a51674f5562557878705332624a37515264474d6964696d
656e73696f6e782665766964656e63653a7361666574795f626174746572793a6361
70747572653a613a623a76316a636f6e666964656e63651a000dbba06b6173736572
7465645f61741b0000019a86e8e07b6d65766964656e63655f7265667381822f5820
0909090909090909090909090909090909090909090909090909090909090909
~~~

The row id input of {{names}} is the six-element array
`["CEG-row/2", "scores", family, "subject-1", author, payload]`, with
the payload entered as a byte string.  Its deterministic encoding is
382 bytes: the prefix below, then the byte-string head `58ec`, then
the payload above.

~~~
86694345472d726f772f326673636f726573782365766964656e63653a2e73756974
653a2e6b696e643a2e63656c6c3a2e707265666978697375626a6563742d31784d75
726e3a696574663a706172616d733a6f617574683a636b743a7368612d3235363a31
764356747a696834592d324c366b6b65414e686963754a51674f5562557878705332
624a37515264474d
~~~

The row id is the SHA-256 of those 382 bytes:

~~~
4d7193e4b48b2313b7f03a9a79fbf8749202c988d94f8909e2fdc652ae74e1f5
~~~

## A Statement Id Known Answer {#kat-statement-id}

The protected header of the same statement is these 245 bytes:

~~~
a7013a000111d303781e6170706c69636174696f6e2f766e642e63697269732e726f
772b63626f72045820d6f095b738a1e18fb62fa92478036189cb894203946d4c71a5
2d9b27b41174630fa401784d75726e3a696574663a706172616d733a6f617574683a
636b743a7368612d3235363a31764356747a696834592d324c366b6b65414e686963
754a51674f5562557878705332624a37515264474d02697375626a6563742d31061a
69184c003a000111720210696365672d726f772f323a000111706673636f7265733a
00011171782365766964656e63653a2e73756974653a2e6b696e643a2e63656c6c3a
2e707265666978
~~~

The statement id input of {{names}} is the three-element array
`["CEG-statement-id/2", protected, payload]`.  Its deterministic
encoding is 505 bytes: the 20 bytes
`83724345472d73746174656d656e742d69642f32`, then the byte-string head
`58f5` and the protected header above, then the byte-string head
`58ec` and the payload of the row id known answer.  The statement id
is the SHA-256 of those 505 bytes:

~~~
7d868e399743467fd3f01b0c92ab3e10a442ad1141f68a54261dd558c111bad4
~~~

The unprotected header is no part of that input.  The statement as
the file holds it is 3864 bytes, and its unprotected header is the
empty map, the one byte `a0` at offset 249.  Replace that byte with
the seven bytes `a119018a814100`, the map `{394: [h'00']}`: one entry
under the `receipts` label, holding a byte string that is no receipt.
The result is a statement of 3870 bytes.  Its SHA-256 digest is
f1792406ebff5cf5cd628390c660ffb7994b581aadc8278329c7ce29e92d6bbd.  Its
protected header, payload and signature are unchanged.  It therefore
has the same row id and the same statement id, and it verifies with
the same answer, Valid, with the same `kid` and `iss`: no check of
{{verify}} reads the entry, and a malformed receipt is ignored
({{receipts}}).

The vector files hold no such pair of their own.  {{open}} records
that one is proposed.

{{CC}} also builds schema samples, which are not known-answer
vectors.  The build of this document checks that the CDDL of
{{cddl}} admits each valid sample and refuses each broken one.

# The Earlier Form {#earlier}

An earlier, retired form of the signed object was a JSON object,
canonicalised with JCS {{RFC8785}} and signed by a nested pair of an
Ed25519 and an ML-DSA-65 signature.  Revision -00 of this document
described it.  {{CC}} keeps it as an annex (CC 8.11).  No node of the
current edition reads it, and no row of the current form names an
object of it.

# Changes since draft-moore-scitt-ciris-ceg-03
{:numbered="false"}

Note to the RFC Editor: please remove this section before publication.

This revision brings the text to {{CC}} 1.0-rc22 and answers two
readings of -03.  One was a run of the known-answer cases from the
text of -03 alone, which found five places where the text did not
give the vectors' answers.

Those five:

- A rotation is stated in full.  A rotation record names the old
  key's record in `refs.target`, carries the new key's own statement
  and the old key's, keeps the old record's `iss`, and is made inside
  the old key's record.  A contested rotation hands on nothing
  ({{rotation}}).  The table of `refs` says that `target` names the
  old record ({{refs}}).
- Invalid and Waiting have one answer each.  A row that is known and
  not held, or a statement that a held row lacks, is Waiting.
  Everything else is Invalid, `kid_not_of_iss`, and that includes a
  verifier that holds bare keys ({{key-of-iss}}).  Waiting is said to
  name a key at step 6 and a row at step 8, in every section
  ({{verify}}).
- A key's liveness at the statement's instant is read at step 6.  A
  record covers an instant up to and not including its end, each key
  signs its own record, and a statement that no held record covers
  waits ({{key-records}}, {{verify}}).  The Waiting answers are a
  table ({{tab-waiting}}).
- A row type outside the five is Invalid at step 2,
  `malformed:row-type`.  `attestation_type_unregistered` is the token
  a Substrate reports for the same fault.  Reasons and tokens are
  told apart, and the three faults that have both are a table
  ({{types}}, {{tokens}}).
- The list of reasons gains `key_record_bad_identity_type`,
  `key_record_bad_pq_custody`, `key_record_bad_attestation_evidence`,
  `authorship_undetermined`, `target_mismatch` and
  `malformed:sd-disclosure`, with the Waiting answers.  One rule says
  which member a reason names, and the prefixes of the three levels
  of reading are stated ({{reason-names}}).

The other reading:

- The statement id is named the CEG statement id, a name of this
  profile, in the text and in the CDDL of {{cddl}}.  What it covers
  is set beside the COSE `Sig_structure` ({{names}}, {{deltas}}).
- A match on an id shows nothing of who signed, and `iss` is a claim
  until the key-of-issuer check has passed ({{idref}}, {{names}},
  Security Considerations).

From {{CC}} 1.0-rc22:

- A trust root is the lineage of a genesis bundle, and the bundle's
  `charter` carries its parameters ({{objects}}).
- Transparency follows SCITT throughout.  A service keeps its own
  log and issues its own Receipt; a root's charter and a room's
  record name the services heads are registered with, at a receipt
  quorum.  The log-head proposal of -03 is replaced by the rule
  ({{heads}}, {{scitt}}).
- The end of a standing is described: an act names its head, an end
  names the head it acts from, what counts and what stays in force,
  and receipts ({{standing-end}}).
- `refs` gains `further_prev` and the `also` roles `under`,
  `stands_on` and `voice`, and `head`, `answers` and
  `trusted_through` are stated in full ({{refs}}).
- On a row a room key signs, `iss` is the voice ({{idref}}).
- A `withdraws` or a `recants` row carries the family of its target
  and no `dimension` ({{family}}).
- The node code `CIRIS-V4-` and its eight hint types are described
  ({{nodecode}}).
- The composite algorithm identifier stays -70100 for a lineage's
  keys ({{sig}}).
- The verification steps name the family's payload rule and its
  reason, `edition2_payload_invalid`, and a decimal fraction that is
  not normalised is a second encoding ({{verify}}, {{numbers}}).
- A node's owner, not the node, accepts and leaves a root, and a
  community names its duty holders ({{safety}}).
- A receipt of acts is never withdrawn ({{withdraw-rule}}).

Pins and known answers:

- {{CC}} is pinned at 1.0-rc22 and every vector file at one tag of
  the verifier.  The row statements file is its fourth version and
  the key-of-issuer file its third, with the first kept for the cases
  only it holds ({{vectors}}).
- A statement id known answer is given in full, with a statement that
  differs from it only in the unprotected header
  ({{kat-statement-id}}).
- The CDDL of {{cddl}} is the schema of {{CC}} 1.0-rc22.

# Changes since draft-moore-scitt-ciris-ceg-02
{:numbered="false"}

Note to the RFC Editor: please remove this section before publication.

Revision -02 brought the text to the wire of {{CC}} 1.0-rc21.  This
revision answers the reviews of -01.

- A statement's key must be a key of its `iss`, by one of four ways,
  with the reason `kid_not_of_iss` and a Waiting answer where a row
  is missing ({{keys}}, {{verify}}).  Songbo Bu found that -01 did
  not bind the two.
- Every check has a reason or token, in one lower-case style, and
  the two tables of {{admission}} are the complete list.
- {{CC}} and each vector file are pinned by commit, each vector file
  also by SHA-256, and one row id known answer is given in full
  ({{vectors}}).
- A profile that registers a log head with a Transparency Service is
  proposed for review ({{loghead}}).
- The related drafts are named ({{lifecycle}}).

# Changes since draft-moore-scitt-ciris-ceg-01
{:numbered="false"}

Note to the RFC Editor: please remove this section before publication.

- {{CC}} is cited at 1.0-rc21.
- A host runs code a row admits only once it holds a SCITT receipt
  from a Transparency Service it trusts.  The receipt, its leaf, the
  trust edge and its `service_key`, and the waiting answer are
  described ({{receipts}}).  The SCITT roles and differences follow
  ({{scitt}}).
- The unprotected header is read by the host's receipt check and by
  no admission check.
- A decimal fraction in a free-form body is CBOR tag 4 ({{numbers}}).
- A fork of two first bundles under a thumbprint anchor roots on
  neither, and the holders a bundle seats name distinct devices.
- `refs.target` names every row it can target, and the state a
  verifier reports for a superseded, withdrawn or recanted row is
  stated ({{types}}, {{refs}}).
- The CDDL appendix follows the current schema of {{CC}}.

# Changes since draft-moore-scitt-ciris-ceg-00
{:numbered="false"}

Note to the RFC Editor: please remove this section before publication.

- The signed object is now the CBOR and COSE form of {{CC}} 1.0-rc20:
  a COSE_Sign1 over a deterministically encoded payload, with one
  composite ML-DSA-65 and Ed25519 signature.
- The JSON, JCS and nested-signature sections are replaced by
  {{canon}}, {{names}} and {{sig}}.  The earlier form is reduced to
  {{earlier}}.
- The section on a future CBOR and COSE edition is removed.
- The CDDL appendix is the schema of the CBOR form.
- The SCITT roles and differences are rewritten: a statement is now a
  COSE_Sign1 with issuer and subject claims.
- The admission checks, the withdrawal rules, the halt, the key's end
  and the conceded limits follow {{CC}} 1.0-rc20.
- Other signed objects, receipts and erasable members are described.

# Acknowledgments
{:numbered="false"}

Songbo Bu found that revision -01 did not bind a statement's signing
key to the identity in `iss`, supplied the test cases that confirmed
it, and re-ran them against the fix.  The rule of {{keys}} is the
result.

Andrii Sparysh reviewed revision -01 as an implementer would.  The
complete list of reasons, the pinned digests, the row id known
answer, the statement of what `refs.target` names and of a verifier's
reported state, and the log-head proposal of {{loghead}} all follow
from that review.  He then ran the known-answer cases from the text
of revision -03 alone, with his answers fixed before he saw the
expected ones.  The rotation rule of {{rotation}}, the one answer for
Invalid and for Waiting, the step at which a key's liveness is read,
the two names of a row type outside the five, and the rule for naming
a member in a reason are the result.

A reader of revision -03 pointed out that the statement id was named
as if {{RFC9943}} defined it, that the text did not say how it stands
to the COSE `Sig_structure`, and that a match on an id could be taken
for evidence of the signer.  The text of {{names}} and the two
security considerations on the issuer and on names are the result.

The canonical-form rules in this document were found and fixed in
review by the implementers of CIRISPersist, CIRISVerify and CIRISEdge.
