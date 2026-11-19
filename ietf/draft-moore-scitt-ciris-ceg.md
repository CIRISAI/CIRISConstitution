---
title: "Signed Attestation Rows of the CIRIS Epistemic Grammar and Their Relationship to SCITT"
abbrev: "CEG Attestation Rows and SCITT"
category: info
submissiontype: IETF
docname: draft-moore-scitt-ciris-ceg-latest
number:
date: 2026-11-16
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
    title: "CIRIS Constitution 1.0-rc20"
    author:
      org: CIRIS L3C
    date: 2026-11-16
    target: https://github.com/CIRISAI/CIRISConstitution/tree/v1.0-rc20
  CC-VECTORS:
    title: "CIRISVerify v23.2.0"
    author:
      org: CIRIS L3C
    date: false
    target: https://github.com/CIRISAI/CIRISVerify/tree/v23.2.0

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
a SCITT Signed Statement.  CEG has no Transparency Service of its
own.  {{scitt}} describes the relationship and what still differs.

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

Refusal token:
: A fixed, case-sensitive ASCII string that names why a row was
  refused, so that two implementations agree on a refusal as well as
  on an acceptance.  The tokens of {{CC}} are either all lowercase or
  all uppercase, and are compared byte for byte.  Some refusals use
  the token `federation_malformed_row` together with a reason from a
  closed set.

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

## The Unprotected Header and External AAD

`external_aad` is the empty byte string, and no party puts a domain
prefix there.  The unprotected header is outside the signature, and
no rule reads it.  A holder may add a receipt there, or present a
disclosure there ({{erasable}}, {{receipts}}).

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

The row type label (-70001) takes exactly one of five values.  A
Substrate MUST refuse any other value, compared byte for byte, with
`attestation_type_unregistered`.  It MUST apply this check to rows it
emits and to rows it receives.

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
Substrate MUST refuse a payload with null for an optional member,
with `federation_malformed_row` and the reason `envelope_member_null`.
No value a family names, at any depth, is a float, a null, an
undefined value, a tag or a simple value.  The one exception is the
redaction marks of {{erasable}}.

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
  deterministic encodings and holds no duplicate.  A verifier refuses
  any other with `federation_set_semantics_unsorted`, naming the
  member.  It never re-sorts the set, because that would change the
  signed bytes.

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
write path, with `ENVELOPE_TOO_LARGE`.

Every write path MUST also enforce a finite ceiling on the octets it
buffers from an untrusted source.  It refuses at that ceiling with
the same token, without completing the decode.  The ceiling is local,
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

## What a Row Names {#refs}

Every row a row names stands in one payload member, `refs`, by
reference.  A reference is the array `[2, digest]`: the edition and
the row id.  `refs` is a map with these members:

| Member | What it names |
|---|---|
| head | The head a count is over ({{counted}}) |
| further_heads | Further tips beside `head` |
| prev | A predecessor |
| answers | The row this row answers |
| target | The row a `supersedes`, `withdraws` or `recants` row names, the act a cut ends or the member a removal removes, and, on a halt's confirmation or resumption, that halt ({{halt}}) |
| trusted_through | On a key revocation, the last rows of the key held good |
| also | A map from a role, `ack` or `cites`, to a set of references |
{: title="Members of refs"}

A holder reads the set of named rows from `refs` alone, without
knowing the family.  The roles of `also` are a closed registry of
two.  `ack` names an acknowledgement.  `cites` names a row the row
cites.

Every array inside `refs` is a set, and a set out of order is
refused.  An empty `refs` is refused: absence is its one encoding.
No row names an object of the earlier form of {{earlier}}.

## The Author {#author}

A family is either authored or counted, as {{CC}} states for each
family.  An authored family's payload carries `author`, the `iss` of
the one who authors the row.  The row id reads it from the payload.
A counted family's author is null.

A statement whose `iss` is not the payload's `author` is accepted
only in a role its family names, such as a delegate or a bound node.
Its `iss` MUST then be the party that role names in the payload.
Where that party is the attested key, as a delegate is, it MUST be
the CWT `sub`.  Any other `iss` is Invalid ({{verify}}).

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
identifier is -70100, a private-use value, until one is assigned.
Only the identifier changes then.  ML-DSA-65 alone is COSE algorithm
-49 {{RFC9964}}; CEG does not use it alone.

## Keys {#keys}

A key is one composite COSE key of key type AKP (kty 7).  Its `pub`
(label -1) is the ML-DSA-65 public key followed by the Ed25519 public
key, 1984 bytes.  Its `kid` is its 32-byte SHA-256 thumbprint
{{RFC9679}}, fixed for the key's life.  A key's displayed identity is
that thumbprint.

A key record is a row of the family `key:record`.  Its payload
carries `key`, `identity_type`, `asserted_at` and, where its end rule
requires, `valid_until`.  A key renews by a `supersedes` of its own
record.  A rotation is a record of another key that names the old
key's record and carries the old key's signature.

`identity_type` is a set of roles.  A set that mixes a person's role
(`user` or `accord_holder`) with a machine's (`node` or `agent`) is
refused.  A record whose set contains a person's role carries no
`valid_until`.  One whose set contains `node` or `agent` carries one,
with stated exceptions.  A record that breaks the rule is refused
`key_record_out_of_window`.

A key is live at an instant when one of its records covers that
instant and its own revocation has not taken effect by then.  Only
the key's own revocation ends its liveness.  The key's owner and the
roster that seats it may also revoke it.  That ends the owner's
binding or the seat, not the key's liveness.

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

## Verification Has Three Answers {#verify}

Verifying a statement gives one of three answers: Valid, Invalid with
a reason, or Waiting on the keys it names as missing.

- A bad signature under a held key is Invalid, and that answer is
  final.  A structural fault is Invalid whatever keys are held.
- A statement whose key record is Waiting is Waiting, naming the
  deepest missing key.  A statement whose key record is Invalid is
  Invalid.
- A key held in part is Waiting on the missing half.  A key never
  verifies on one half.
- Waiting never becomes Valid by default and is never counted.  A
  waiting statement is held inert until the key it names is held.

A verifier proceeds in this order:

1. Decode strictly: tag 18, and the protected header and the payload
   in the deterministic encoding.
2. Check the header: `typ` on the closed list; `alg` -70100; edition
   2; `cty` the constant; a row's type and family labels present, an
   object's absent.
3. Check the payload against the schema: no float or null, the sets,
   the ranges, and `dimension` resolving to the header's family.
4. Check `iat`, `nbf` and `exp` against the payload.
5. Run the family's static checks, the key record's end among them.
6. Read `kid`; resolve the key record, or answer Waiting on it.
7. Verify the composite signature over the bytes received.
8. Check `iss` against `author`, or against the party of a role the
   family names ({{author}}).
9. On Valid, apply the defaults of {{CC}} to absent members, at
   interpretation time only, and then the Consumer's own policy.
10. Store or forward the statement as received.

A failure at steps 1 to 5, 7 or 8 is Invalid.  Step 6 alone answers
Waiting.

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

The genesis bundle seats the holders of a trust root and its serve
nodes.  It is counted: one statement for each holder, over one
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

## Receipts {#receipts}

Receipts over the provenance log and each stream's log are COSE
Receipts {{RFC9942}} over the SHA-256 tree of {{RFC9162}}.  Its
hashing is that of {{RFC6962}}, so roots already published stay
valid.  Each witness issues its own receipt over the same root, with
its instant in the protected header.  A stream's receipts cover
batches, never single chunks.

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
ignored and never makes the statement invalid.  Anyone may run a
Transparency Service, and a receipt adds no authority.

# Admission as a Registration Policy {#admission}

{{RFC9943}} lets each Transparency Service define a Registration
Policy: the checks a Signed Statement must pass before it is
registered.  The CEG admission checks are such a policy.  A Substrate
MUST apply them to every row before storing or relaying it.  It MUST
NOT truncate, repair or re-encode a row in order to admit it.

| Check | Refusal |
|---|---|
| Payload at most 1 MiB | ENVELOPE_TOO_LARGE |
| Deterministic encoding of payload and header | Invalid |
| Header members exactly as {{object}} | Invalid |
| Composite signature verifies | SIGNATURE_VERIFICATION_FAILED |
| Type is one of the five | attestation_type_unregistered |
| No optional member is null | (R) envelope_member_null |
| Sets sorted and unique | federation_set_semantics_unsorted |
| Header instants equal the payload's | Invalid |
| `dimension` resolves to the family | Invalid |
| `iss` is the author or a named role | Invalid |
| Key record within its window | key_record_out_of_window |
| Termed delegation within 365 days | delegation_term_required |
| Withdrawal meets {{withdraw-rule}} | federation_withdraws_not_admitted |
{: title="Admission checks"}

"(R) r" means the token `federation_malformed_row` with reason r.
"Invalid" marks a check that {{CC}} makes a refusal without naming a
token for it.

Admission has a third outcome besides admit and refuse.  A row signed
by a key whose record is not yet held is Waiting ({{verify}}).  It is
held and retried, never counted, until the key is held.

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
that have it among their ancestors still stand.

The kept list stops a named party from withdrawing a third party's
adverse finding about itself, such as a detection, a licensing
decision or a moderation record.  {{CC}} lists the families it
covers.  The named party's route is to contest the row.  A key
revocation is never withdrawn.

Recantation is not covered by these rules.  Only T's signer can
recant T.

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
(CC 4.4.3.8).  A row defaults to the smallest scope that fits its
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

- A community has at least one holder of its moderation duty at all
  times.  A seat is two consents, the placer's and the holder's.  If
  no duty holder is left, the community locks and its members elect
  one (CC 4.5.4).

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
affected.  Any node can leave a root by withdrawing one row; a halt
that has already reached it still binds it (CC 4.2.1).

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
| Transparency Service | No counterpart; see {{deltas}}. |
| Receipt | A COSE Receipt {{RFC9942}} over a provenance or stream log ({{receipts}}). |
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
: CEG has no Transparency Service and no registrar.  A node admits by
  its own checks, and what it serves is decided by trust the reader
  chose.  No party stands in the middle.

Registration Policy.
: {{RFC9943}} has the Transparency Service evaluate its policy and
  requires the policy itself to be registered, so that Auditors can
  reproduce the decision.  The CEG checks read the payload as well as
  the headers.  They are fixed by {{CC}} rather than registered as
  statements.  Any party can reproduce an admission decision from the
  row and the checks, but the checks are not themselves on a log.

Receipts.
: A SCITT Receipt is issued at registration by the service.  A CEG
  receipt is issued by a witness over a log root, and each witness
  issues its own.  Nothing requires a receipt when a row is admitted.
  A holder may add one to a statement's unprotected header.

Witnesses.
: {{CC}} defines witness cosignature of log heads and of trust-root
  lineages.  A lineage that runs with witnessed mode off has a single
  signer.  That signer can show different histories to different
  peers until a peer compares heads.

Statement content.
: SCITT leaves the meaning of a statement to its issuer.  CEG fixes
  the five row types and requires every claim to name a registered
  family, so a Consumer can interpret any admitted row without
  out-of-band agreement.

Waiting.
: A CEG verifier can answer Waiting on a key it does not hold, and
  hold the statement inert ({{verify}}).  A SCITT Registration Policy
  admits or refuses.

# Lifecycle of an Agent Decision {#lifecycle}

This section is informative.

Several individual SCITT drafts record AI agent actions as a sequence
of statements: an authorisation before the act, a record of the act,
and a refusal where the agent declined.  In CEG the same events are
rows.  The reasoning steps before an act are rows in the decision
families of {{CC}}.  The act is recorded by one row whose dimension is
`trace:complete:v1`, ending in a terminal result.  A completed action,
a refusal, and a deferral to a human are the same kind of row with
different terminal results, so a Consumer reads all three the same
way.  Authority to act, and any transfer of it, is a `delegates_to`
row.

# Open Issues {#open}

Note to the RFC Editor: please remove this section before publication.

- The composite algorithm has no assigned COSE identifier, and the
  drafts that define it may still change ({{deltas}}).

- Several encodings are open in {{CC}}, each waiting on its owner.
  They include the payload rule of `ceg-boot-manifest/2`, the family
  of an agent's text manifest statement, and the layout of the short
  displayed form of a key's thumbprint.  {{CC}} lists them in its
  table of open encodings (CC 2.6.1.12).

- {{CC}} names no refusal token for several checks of {{admission}}.

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
admission path exists yet.

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
  header is not.  No rule may read the unprotected header.  Who a row
  is about and who may see it are in the signed bytes, so a relay
  cannot redirect a validly signed row.

Composite signature.
: Both halves sign one representative that names the composite
  label, so neither half verifies alone.  A forger must break both ML-DSA-65 and
  Ed25519.  A verifier MUST NOT accept a statement on one half, and a
  key held in part is Waiting, never Valid.

Identity references.
: `kid` and `iss` carry full 32-byte thumbprints, not short
  fingerprints.  A verifier resolves `kid` to a key record and
  verifies with the full composite key that record holds.

Withdrawal.
: The withdrawal rules let parties other than the signer retract a
  row.  The rules in {{withdraw-rule}} stop a subject from removing
  adverse findings about itself, and stop any single key from undoing
  a quorum's act.

Single-signer logs.
: Where witness cosignature is off, a log head is signed by one key.
  A Substrate can then show different histories to different peers
  until the heads are compared ({{deltas}}).

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
{{CC-VECTORS}}.  {{CC}} pins each file at a tag of CIRISVerify,
v23.1.1 or v23.2.0 (CC 2.6.5).
They cover the row id, the refusals of non-deterministic encodings,
the order of the sets in `refs`, a counted row as several
statements, and the three answers of {{verify}}.

The row statements file holds four valid statements and 42 refusals,
with 17 key records.  The composite signature's vectors are checked
against the examples of {{COMPOSITE-JOSE}}.  Further files cover the
genesis bundles, the recovery commitment, and the accord halt.

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

The canonical-form rules in this document were found and fixed in
review by the implementers of CIRISPersist, CIRISVerify and CIRISEdge.
