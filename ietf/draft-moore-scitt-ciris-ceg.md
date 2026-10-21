---
title: "Signed Attestation Rows of the CIRIS Epistemic Grammar and Their Relationship to SCITT"
abbrev: "CEG Attestation Rows and SCITT"
category: info
submissiontype: IETF
docname: draft-moore-scitt-ciris-ceg-latest
number:
date:
v: 3
area: "Security"
workgroup: "Supply Chain Integrity, Transparency, and Trust"
keyword:
 - attestation
 - transparency
 - canonical JSON
 - hybrid signature
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
  RFC8259:
  RFC8785:
  RFC8032:
  RFC4648:
  RFC3339:
  RFC9562:
  RFC8610:
  RFC9943:
  FIPS204:
    title: "Module-Lattice-Based Digital Signature Standard"
    author:
      org: National Institute of Standards and Technology
    date: 2024-08
    seriesinfo:
      FIPS: "204"
      DOI: 10.6028/NIST.FIPS.204

informative:
  RFC6962:
  RFC7942:
  RFC9052:
  RFC3552:
  RFC6973:
  RFC9794:
  RFC9942:
  RFC9955:
  RFC9964:
  I-D.ietf-lamps-pq-composite-sigs:
  I-D.ietf-jose-pq-composite-sigs:
  CC:
    title: "CIRIS Constitution 1.0-rc9"
    author:
      org: CIRIS L3C
    date: 2026-10-21
    target: https://github.com/CIRISAI/CIRISConstitution/tree/v1.0-rc9
  CC-VECTORS:
    title: "CIRIS Constitution signed object test vectors"
    author:
      org: CIRIS L3C
    date: 2026-10-21
    target: https://github.com/CIRISAI/CIRISConstitution/blob/v1.0-rc9/manifests/signed_object_vectors.json

--- abstract

The CIRIS Epistemic Grammar (CEG) records claims between parties as
signed rows.  Each row is one JSON object, canonicalised with the JSON
Canonicalization Scheme (JCS) and signed twice: once with Ed25519 and
once with ML-DSA-65, where the ML-DSA-65 signature covers the canonical
bytes followed by the Ed25519 signature.  Every row has one of five
types: a claim, a delegation, a replacement, a withdrawal, or a
recantation.  A node admits a row only after a fixed set of checks,
and it refuses a failing row with a named reason.

This document specifies the signed object, the signing input, the
signature construction, and the admission checks, so that a second
implementation can produce and verify the same bytes.  It then
describes how these rows relate to the roles of the SCITT
architecture (RFC 9943), and where they differ from a SCITT
Transparency Service.  It defines no new SCITT mechanism and requests
no IANA action.

--- middle

# Introduction

CEG is the row format of the CIRIS system, in which people, devices,
communities and AI agents make claims about each other and act on
them.  It is defined normatively in the CIRIS Constitution {{CC}}.
This document restates the parts of that definition that another
implementation needs in order to interoperate at the byte level.

Three goals shape the format:

- Any party holding a row can recompute its signing bytes exactly.
  Signatures are over a canonical form, and every point where JSON or
  JCS would let one encoding produce two byte strings is fixed.  Two
  encodings of one meaning can still exist (an explicit default, or a
  one-element `scope` written as a string); they are different rows
  with different bytes, and both verify ({{canon}}).

- Rows exchanged between nodes have to resist forgery by an attacker
  with a quantum computer.  Every such row carries an ML-DSA-65
  signature {{FIPS204}} beside the Ed25519 signature {{RFC8032}}, and
  both MUST verify.

- The set of row types is closed, so that every row is subject to the
  same admission rules.  New kinds of claim are new values of
  `dimension`, never new types.

SCITT {{RFC9943}} defines an architecture for registering signed
statements with a Transparency Service and returning receipts that
prove registration.  CEG rows play a similar role in their own
system, but the two were designed separately and differ in encoding
and in how proofs are delivered.  {{scitt}} describes the
relationship.  A COSE encoding of CEG rows is out of scope; {{scitt}}
says what one would need to cover.

## Scope

In scope:

- the signed object of an attestation row and its member set
  ({{object}});
- the five row types ({{types}});
- the canonical signing input ({{canon}});
- the hybrid signature and cosignatures ({{sig}});
- the admission checks, written as a SCITT Registration Policy
  ({{admission}}).

Informative only:

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

Row:
: One signed attestation.  On the wire it is a JSON object
  {{RFC8259}} that carries the signed object and members beside it.

Signed object:
: The JSON object named `attestation_envelope` inside a row.  Its JCS
  image is the signing input.  Nothing else in the row is signed.

Attester:
: The key that signs a row's signed object.  It plays the SCITT
  Issuer role.

Subject:
: A party a row is about.  `attested_key_id` names the primary
  subject; `subject_key_ids` lists any others, including parties that
  have no key.

Producer, Consumer, Substrate:
: A Producer emits rows.  A Consumer verifies and reads rows.  A
  Substrate stores and relays rows and applies the admission checks.
  One node is usually all three.

Refusal token:
: A fixed, case-sensitive ASCII string that names why a row was
  refused, so that two implementations agree on a refusal as well as
  on an acceptance.  The tokens of {{CC}} are either all lowercase or
  all uppercase, and are compared byte for byte.

Local tier, federation tier:
: A row at the local tier stays on the node that wrote it and is not
  replicated.  A row at the federation tier may leave the node.
  Promotion from the local tier to the federation tier adds the
  ML-DSA-65 signature and does not change the signing input, so a
  promoted row is byte-identical to one written at the federation
  tier.

key_id:
: A key identifier of the form `<label>-<fingerprint>`, where the
  fingerprint is the first ten characters of the lowercase base32
  {{RFC4648}} encoding of the SHA-256 digest of the raw 32-byte
  Ed25519 public key.  The label is chosen by the key holder.

# The Signed Object {#object}

## Members of a Row

A row is a JSON object with the following members.  Each is listed with
its placement: `signed` members are inside the signing input;
`beside` members travel with the row and are bound to it by a check,
but are not signed.

| Member | Placement | Content |
|---|---|---|
| attestation_envelope | signed | The signed object. |
| attestation_id | beside, mirrored | UUID {{RFC9562}} of the row. |
| attesting_key_id | beside, mirrored | key_id of the attester. |
| attested_key_id | beside, mirrored | key_id the row is primarily about. |
| attestation_type | beside, mirrored | One of the five types. |
| subject_key_ids | beside, mirrored | Set of subject identifiers. |
| cohort_scope | beside, mirrored | Audience: one of seven scopes. |
| weight | beside, mirrored | Optional number. |
| asserted_at | beside | Column copy of the signed instant. |
| expires_at | beside | Optional column copy. |
| original_content_hash | beside | Lowercase hex SHA-256 of the signing input. |
| scrub_key_id | beside | key_id that produced the row's signature. |
| scrub_signature_classical | beside | Ed25519 signature, base64. |
| scrub_signature_pqc | beside | ML-DSA-65 signature, base64. |
| scrub_timestamp | beside | When the signature was applied. |
| additional_scrubs | beside | Cosignatures ({{cosign}}). |
{: title="Members of a row"}

The seven members marked "mirrored" are repeated inside the signed
object under the member `row` ({{mirror}}).  `asserted_at` and
`expires_at` beside the row are read out of the signed object: a
Substrate MUST refuse a row whose `asserted_at` column differs from
the signed member, with `typed_diverges_from_envelope`, and `expires_at`
is present beside the row exactly when it is present in the signed
object.  `scrub_timestamp` uses the instant form of {{time}}.  A
Substrate MAY add members of its own beside the row; they are not part
of this specification.

## The Mirror {#mirror}

The signed object MUST contain a member `row` whose value is an object
with exactly these members: `attestation_id`, `attesting_key_id`,
`attestation_type`, `attested_key_id`, `subject_key_ids`,
`cohort_scope`, and optionally `weight`.  The set is closed.  A
Substrate MUST refuse a row:

- whose signed object has no `row` member, with
  `envelope_member_missing`;

- whose `row` object has any member not in this list;

- where any column beside the row differs from its mirror, with
  `typed_diverges_from_envelope`.

The mirror exists because the columns beside a row are what a
Substrate indexes and a Consumer filters on.  If those columns were not signed, a
relay could change who a row is about or who may see it while the
signature still verified.

`subject_key_ids` is always present in the mirror; an empty array means
the row has no subject beyond `attested_key_id`.  `cohort_scope` takes
one of the values `self`, `family`, `community`, `affiliations`,
`species`, `biosphere`, `federation`.

## Members of the Signed Object

Besides `row`, every signed object carries:

asserted_at:
: REQUIRED.  The instant the attester makes the claim, in the form of
  {{time}}.

dimension:
: REQUIRED.  A string naming the claim family, for example
  `expertise:cardiology:en:v1`.  Its grammar and registry are defined
  in {{CC}} and are not needed to verify a signature.

expires_at:
: OPTIONAL.  The instant after which the claim no longer stands.

Each row type adds members ({{types}}).  Claim families add members of
their own.  {{cddl}} gives the full member list with types.  A
Consumer MUST preserve members it does not recognise when it relays a
row, because removing one would change the signing input.

# The Five Row Types {#types}

The `attestation_type` member takes exactly one of five values.  A
Substrate MUST refuse any other value, compared byte for byte, with
`attestation_type_unregistered`.  It MUST apply this check to rows it
emits and to rows it receives.

scores:
: A claim about the attested key on the named dimension.  It carries
  `score` and `confidence`, both numbers.  Every positive or negative
  claim about a party is a `scores` row.

delegates_to:
: The attester authorises the attested key to sign on its behalf
  within `scope`, a set of strings, from `delegation_valid_from` until
  `delegation_valid_until`.  For the scopes that {{CC}} lists as
  requiring a term, among them licensing, moderation and takedown,
  `delegation_valid_until` is REQUIRED and MUST be no more than 365
  days after `delegation_valid_from`; a Substrate refuses a row that
  breaks this with `delegation_term_required`.

supersedes:
: The attester replaces one of its own earlier rows, named by
  `references_attestation_id`.  It MAY list the changed members in
  `differs_in`.

withdraws:
: The attester retracts an earlier row, named by
  `references_attestation_id`, without saying the row was false.
  {{withdraw-rule}} says who may withdraw a row.

recants:
: The attester says one of its own earlier rows was false when it was
  made.  Only the original attester can recant a row.

A withdrawal and a recantation are different statements.  A withdrawal
says "I no longer assert this"; a recantation says "this was wrong".
Consumers can weigh them differently, and the subject of a row has
authority over the first but not the second ({{withdraw-rule}}).

A new kind of record is expressed as a new `dimension` on one of the
five types, never as a sixth type.

# The Signing Input {#canon}

The signing input of a row is the JCS {{RFC8785}} image of its signed
object, as UTF-8 bytes.  No other member of the row contributes to it.

JCS fixes member order, whitespace, string escaping and number
formatting, but leaves several choices open that would let two
Producers encode the same claim differently.  The rules in this section
close them.

## Absent, Never Null, Never Materialised

An optional member is unset by being absent.  A Producer MUST NOT emit
an optional member with the JSON value `null`.  A Substrate MUST
refuse a row whose signed object contains an optional member set to
`null`, with `federation_malformed_row` and the reason
`envelope_member_null`.

A default is applied when a row is read, never when it is encoded.  A
Producer that writes a member at its default value and a Producer that
omits it produce different signing bytes; both rows verify, and both
mean the same thing.  A Substrate that stores or relays a row MUST NOT add a defaulted
member or remove one, because either change alters the signing input.

## Arrays

Each array member is declared as either a set or a sequence.  The
declarations are in {{cddl}}.

- A set MUST be sorted in ascending order of the JCS serialisation of
  each element, compared as sequences of UTF-16 code units (the
  comparison JCS uses for member names), and its elements MUST be
  unique.  A Substrate MUST refuse a row with an
  unsorted or duplicated set, with `federation_set_semantics_unsorted`
  naming the member.  It MUST NOT sort the set itself, because that
  would change the signing input.

- A sequence keeps the order its author gave it.

`subject_key_ids`, `scope` and `differs_in` are sets.  `evidence_refs`
is a sequence.  An array without a declaration is a set.

The `scope` member MAY be a single string or an array.  A single string
denotes the one-element set; a Substrate MUST NOT rewrite one form
into the other.

## Strings That Carry Bytes

JSON has no byte type.  Hashes, digests and raw key material inside the
signing input are lowercase hexadecimal, with no prefix and no
separators.  Members declared as base64 use the standard alphabet of
{{Section 4 of RFC4648}} with padding and no line breaks.

An element of `subject_key_ids` is either a key_id, copied byte for
byte from the key's record, or a tagged canonical identifier of the form
`canonical:<hashalg>:<hex>` for a party that has no key.  The tag is
part of the signed string.  A Substrate MUST refuse an element whose
tag is not in lowercase, and MUST NOT repair it.

## Instants {#time}

Every instant inside the signing input is written as
`YYYY-MM-DDTHH:MM:SS.sssZ`: UTC, the literal uppercase `Z`, and exactly
three fractional digits.  This is a profile of {{RFC3339}}.  A Producer
MUST emit this form.  A Substrate MUST refuse any other form inside the
signing input with `envelope_member_invalid`, even though a signature
over those bytes would still verify.

## Numbers

JCS serialises numbers as IEEE 754 binary64 values.  A Producer MUST
convert every number to its finite binary64 value before computing the
signing input, and MUST fail, rather than emit a row, for a number that
has none (for example `1e1000`).  A parser that keeps numbers at
arbitrary precision would otherwise emit bytes that another
implementation cannot reproduce.

## Size

The signing input MUST NOT exceed 1 MiB (1,048,576 bytes).  A Substrate
MUST refuse a larger row on every path by which rows reach it, with
`ENVELOPE_TOO_LARGE`.  Because the limit is on canonical bytes, it can
only be decided after parsing; each intake path therefore also needs a
local limit on how many bytes it will read before it stops.  That local
limit MUST NOT be less than 1 MiB and is not part of the interoperable
contract.  A Substrate that receives a non-canonical serialisation
larger than its local limit MAY refuse it even if its canonical form
would fit; the interoperable serialisation is the canonical one.
Larger content travels outside the row and is named in
`evidence_refs` by its hash.

## The Content Hash

`original_content_hash` is the lowercase hex SHA-256 digest of the
signing input.  A Substrate MUST recompute it when it receives a row
and MUST refuse a row whose value differs.

# Signatures {#sig}

## The Hybrid Signature

The attester's signature has two parts, made with the attester's key
pair:

1. `scrub_signature_classical` is the Ed25519 signature {{RFC8032}}
   over the signing input.

2. `scrub_signature_pqc` is the ML-DSA-65 signature {{FIPS204}} over
   the signing input followed by the 64 raw bytes of the Ed25519
   signature, computed with ML-DSA.Sign and an empty context string.
   HashML-DSA is not used.

Both values are encoded in base64.  `scrub_key_id` MUST equal
`attesting_key_id`.  A Consumer verifies each part against the public
keys it holds for that key_id.  At the federation tier both parts MUST
verify; a row with only the Ed25519 part is not admitted there.  There
is no configuration that turns the ML-DSA-65 check off.

In the terms of {{RFC9955}} this is a nested hybrid: the second
signature covers the message and the first signature
({{Section 3.3 of RFC9955}}; terminology from {{RFC9794}}).  Because
the ML-DSA-65 input contains the Ed25519 signature, an ML-DSA-65
signature taken from one row cannot be paired with a different Ed25519
signature.  The construction is not the composite signature of
{{I-D.ietf-lamps-pq-composite-sigs}} and
{{I-D.ietf-jose-pq-composite-sigs}}, in which both components sign
the same prefixed message representative and neither covers the
other.  Deployed rows use the nested form, and this document describes
what they carry.

A Producer MAY use either the hedged or the deterministic variant of
ML-DSA.Sign.  A Consumer MUST accept any valid signature and MUST NOT
expect the ML-DSA-65 part to be byte-identical across signers.  The
reference implementation uses the deterministic variant, so the
vectors in {{vectors}} reproduce bit for bit from their seeds.

## Cosignatures {#cosign}

A row MAY carry further signatures over the same signing input in
`additional_scrubs`, an array of objects with these members:

scrub_key_id:
: REQUIRED.  The cosigner's key_id.

scrub_signature_classical:
: REQUIRED.  Ed25519 over the signing input.

scrub_signature_pqc:
: REQUIRED at the federation tier.  ML-DSA-65 over the signing input
  followed by this entry's Ed25519 signature.

cosigned_at:
: OPTIONAL.  When the cosignature was applied.

Cosignatures are beside the signed object, not inside it, because a
signature cannot be part of the bytes it signs.  Adding a cosignature
therefore changes neither the signing input nor the attester's
signature.  An entry carries no role: a Consumer decides what role a
cosigner holds from its own record of the relevant group or roster,
at the row's `asserted_at`.

A claim family can require a quorum.  It does so by naming where the
rule comes from (for example the group the row is about), and a
Substrate admits the row only when the attester and the cosigners that
verify and hold a seat in that group meet the group's rule.  A
cosignature that does not verify, or whose key holds no seat, is not
counted; it is not an error.

## Keys

A Consumer resolves a key_id to an Ed25519 public key and an ML-DSA-65
public key through its own key directory, which is populated by key
records that are themselves signed ({{cddl}}).  {{CC}} defines how keys
are registered and revoked.  Verification also requires that:

- the fingerprint in the key_id MUST match the SHA-256 digest of the
  Ed25519 public key the directory returns, so a directory entry cannot
  be substituted for another key with the same label; and

- a revoked key MAY carry an instant `revoked_after`, so that rows the
  key signed before that instant still stand and rows signed after it
  do not.

# Admission as a Registration Policy {#admission}

{{RFC9943}} lets each Transparency Service define a Registration
Policy: the checks a Signed Statement must pass before it is
registered.  The CEG admission checks are such a policy.  A Substrate
MUST apply them, in any order, to every row before storing or relaying
it, and MUST refuse a failing row with the token given.  It MUST NOT
truncate, repair or re-encode a row in order to admit it.

| Check | Refusal token |
|---|---|
| The signing input is at most 1 MiB | ENVELOPE_TOO_LARGE |
| `original_content_hash` matches the signing input | none defined |
| Both signature parts verify at the federation tier | SIGNATURE_VERIFICATION_FAILED |
| `attestation_type` is one of the five | attestation_type_unregistered |
| The mirror is present | envelope_member_missing |
| The mirror has no other member | none defined |
| Every mirrored column equals its mirror | typed_diverges_from_envelope |
| No optional member is `null` | federation_malformed_row (envelope_member_null) |
| Sets are sorted and unique | federation_set_semantics_unsorted |
| Instants have the canonical form | envelope_member_invalid |
| Subject identifiers are well formed | none defined |
| A termed delegation has a term of at most 365 days | delegation_term_required |
| A withdrawal meets {{withdraw-rule}} | none defined |
| The `dimension` resolves in the namespace | see {{CC}} |
{: title="Admission checks"}

"None defined" means that {{CC}} requires the refusal but does not yet
name a token for it ({{open}}).  A Substrate refuses such a row with a
token of its own choosing until one is defined.

## Who May Withdraw a Row {#withdraw-rule}

A `withdraws` row against a target row T is admitted when its attester
meets any one of these rules:

1. It is T's attester.

2. It appears in T's `subject_key_ids`.

3. It holds an unexpired `delegates_to` chain whose scope includes
   `consent_revocation`, from a canonical identifier that appears in
   T's `subject_key_ids`.  This is how an agent holding data on behalf
   of a party with no key can act on that party's request.

4. It holds an unexpired `delegates_to` from a key that meets rule 1,
   2 or 3.

Two further rules take precedence:

- If T carries cosignatures, rules 1 to 4 do not apply.  T is withdrawn
  only by a `withdraws` that is itself cosigned under T's quorum rule.

- A subject cannot use rules 2 to 4 to withdraw a third party's
  adverse claim about itself, such as a detection or a licensing
  decision.  {{CC}} lists the families this covers.  The subject's
  route is to dispute the claim with a row of its own.

Recantation is not covered by these rules.  Only T's attester can
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
directory state it already holds (a per-group HKDF), so the address is
never announced and there is no emission from which an outsider could
learn that the group exists (CC 5.2, CC 5.4.6).  A node never announces
that it holds content scoped to a family or community outside that
group.  Members relay for members.

## Consent-Bounded Flow

The rows apply the idea of contextual integrity: information flows
appropriately when the flow matches the norms of the context it came
from.  Each row signs its own context.  `attesting_key_id` says who
sent it, `attested_key_id` and `subject_key_ids` say whom it is about,
and `cohort_scope` says who may see it.  All of these are in the
mirror ({{mirror}}), so a relay cannot change them without breaking
the signature.

A Consumer accepts a row only if it trusts the attester's root or has
consented to receive from the attester, and a row reaches no one else
(CC 4.4.3.8).  A row defaults to the smallest scope that fits its
purpose; `federation` scope, the public commons, is an explicit choice
(CC 1.13.3.4).  Consent is itself a row, and a subject can withdraw a
row about itself ({{withdraw-rule}}).  Content in a private scope is
never scanned.  Known abuse images are checked for only when content
is moved to `federation` scope or posted to a public room (CC
1.13.3.4).

## Accountable Key Relationships

Some parties cannot accept obligations for themselves.  The rows give
each of them a named human:

- A key whose identity type includes `agent` or `node` MUST have a
  steward: a human identity with a live `delegates_to` row binding the
  key.  Without one, the key cannot be admitted to any family,
  community or organisation.  It MAY trust and serve infrastructure
  communities without a steward (CC 3.2).

- A minor has a guardian bound by a signed row (CC 3.4.13).

- A community has a named moderator at all times.  If the moderator
  lapses, the most trusted member is promoted in the same step (CC
  4.5.4).

## A Bounded Human Halt

A trust root names a small set of human holders.  Any one holder can
pause the agents that accepted that root with a single signed row.  A
pause by one holder lapses after 24 hours unless a majority of the
holders confirms it, and a majority ends it.  A pause stops agents from
acting; it does not touch stored data, messages or network service.  A root can tell a node to share less,
never more.  A node that never accepted the root is not affected, and
any node can leave a root by withdrawing one row (CC 4.2.1, CC 4.2.6).

## What Is Not Claimed

Where {{CC}} speaks of anonymity, it means anonymity toward outsiders:
a group's existence, and what its members do in it, are hidden from
non-members.  Beyond that:

- The identity plane is not anonymous.
- No multi-hop anonymity is provided today, and the deployed design
  does not resist a global passive observer of traffic.  An opt-in
  anonymous tier using onion routing is planned for deployments that
  need that protection (CC 1.13.3.1).  It is not yet specified in
  {{CC}} or shipped, and this document does not describe it.
- Members of a group can read, and keep, what the group shares.
  Ballots within a group are accountable to its members, not secret
  from them.
- Nothing is detected inside private groups.  The design declines
  client-side scanning.

# Relationship to SCITT {#scitt}

This section is informative.

## Roles

| SCITT role ({{RFC9943}}) | CEG counterpart |
|---|---|
| Issuer | The attester. |
| Signed Statement | A row: its signed object and the hybrid signature. |
| Registration Policy | The admission checks of {{admission}}. |
| Transparency Service | A Substrate with its RFC 6962 logs {{RFC6962}}. |
| Receipt | No direct counterpart; see {{deltas}}. |
| Relying Party | A Consumer. |
{: title="SCITT roles and their CEG counterparts"}

## Differences {#deltas}

Encoding.
: {{RFC9943}} requires Signed Statements to be COSE_Sign1 {{RFC9052}}
  messages with an Issuer and a subject in the protected header.  CEG
  rows are JSON with a JCS signing input, so a CEG row is not a SCITT
  Signed Statement.  A profile that carried CEG rows
  through a SCITT service would wrap the signing input, or its hash, in
  a COSE_Sign1.  ML-DSA-65 now has a COSE algorithm identifier
  {{RFC9964}}, but the nested pair of {{sig}} has none, so such a
  profile would either carry two COSE signatures or change the
  construction.  No such profile is defined.

Registration Policy.
: {{RFC9943}} has the Transparency Service evaluate its policy over the
  COSE headers and requires the policy itself to be registered, so that
  Auditors can reproduce the decision.  The CEG checks read the whole
  signed object, and they are fixed by {{CC}} rather than registered as
  statements.  Any party can reproduce an admission decision from the
  row and the checks, but the checks are not themselves on the log.

Receipts.
: A SCITT Receipt is a proof of inclusion, issued at registration and
  signed by the service, that the holder can present without the log.
  A CEG Substrate keeps RFC 6962 logs and returns inclusion and
  consistency proofs on request, against the current or a named tree
  size, but it does not issue a receipt when a row is admitted and
  does not store one with the row.  The logs exist so that a node
  cannot show different histories to different peers, and so that any
  holder of the rows can recompute them.  Issuing a COSE Receipt
  {{RFC9942}} at admission, against a
  witness-cosigned tree head, would close this gap.  It is not
  specified.

Witnesses.
: At the time of writing, the tree heads of deployed Substrates are
  signed by a single key.  {{CC}} defines witness cosignature of tree
  heads and of trust-root lineages, but deployed roots have it turned
  off.  A single
  signer can therefore equivocate between two forks until a peer
  compares heads.

Statement content.
: SCITT leaves the meaning of a statement to its issuer.  CEG fixes the
  five row types and requires every claim to name a registered
  dimension, so a Consumer can interpret any admitted row without
  out-of-band agreement.

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

- {{CC}} requires a refusal, but names no token, for a content hash
  mismatch, an extra member in the mirror, a malformed subject
  identifier, and a withdrawal that meets no rule.

- CIRISPersist does not yet refuse an unsorted or duplicated
  `subject_key_ids` set at admission ({{implementation-status}}).

- No COSE encoding of a row is defined ({{deltas}}).

- No second implementation exists ({{implementation-status}}).

# Implementation Status {#implementation-status}

Note to the RFC Editor: please remove this section before publication,
together with the reference to {{RFC7942}}.

This section records the status of known implementations at the time
of writing, as described in {{RFC7942}}.  Listing an implementation
here does not imply endorsement.

CIRISPersist:
: The storage and admission engine (Rust), CIRIS L3C, AGPL-3.0.
  Release v59.1.0 implements the signed object, the mirror checks, the
  hybrid signature and `additional_scrubs`.  It does not yet refuse an
  unsorted or duplicated `subject_key_ids` set at admission.
  <https://github.com/CIRISAI/CIRISPersist>

CIRISVerify:
: Verification library (Rust), CIRIS L3C, AGPL-3.0.  Provides the JCS
  implementation, the hybrid signer and verifier, and the RFC 6962
  proofs.  The test vectors in {{vectors}} were produced with it.
  <https://github.com/CIRISAI/CIRISVerify>

Reference vectors:
: {{CC-VECTORS}}: thirteen vectors, recomputed in continuous
  integration by an independent Python implementation of JCS and
  Ed25519 verification.

No second, independent implementation of the full signing and
admission path exists yet.

# Security Considerations

This section follows the guidance of {{RFC3552}}.

Canonical form.
: Every rule in {{canon}} closes a case in which a Producer and a
  Consumer that both follow JCS compute different bytes.  The
  mismatch shows up only as a failed signature, with nothing to say
  which rule was broken.
  Implementations should test against the vectors in {{vectors}}, and
  in particular against arrays, base64 variants and instants.

What the signature covers.
: Only the signed object is signed.  The mirror rule exists because the
  columns beside a row decide who a row is about and who may read it;
  an implementation that indexes those columns without checking them
  against the mirror lets a relay redirect a validly signed row.

Hybrid signature.
: A forger must produce both an Ed25519 signature over the signing
  input and an ML-DSA-65 signature over the signing input and that
  Ed25519 signature, but only against a verifier that checks both.
  {{RFC9955}} notes that a verifier of a nested hybrid can be led to
  check only one part.  A verifier that accepts Ed25519 alone gives no
  protection against an attacker able to forge Ed25519, and an attacker
  can always remove the ML-DSA-65 part of a row.  For this reason the
  federation tier refuses a row without both parts and has no setting
  that relaxes the check.  Rows below the federation tier MAY lack the
  ML-DSA-65 part and have only classical strength.

Short fingerprints.
: The key_id fingerprint is 50 bits.  It is an identifier for lookup,
  not a commitment to a key.  A verifier must use the full public key
  from its directory, and must check that the key's digest matches the
  fingerprint, as {{sig}} requires.

Withdrawal.
: The withdrawal rules let parties other than the attester retract a
  row.  The precedence rules in {{withdraw-rule}} stop a subject from
  removing adverse findings about itself, and stop any single key from
  undoing a quorum's act.

Single-signer logs.
: Until witness cosignature is on, a Substrate's log head is signed by
  one key, and a Substrate can show different histories to different
  peers until the heads are compared ({{deltas}}).

Size.
: The 1 MiB limit applies after parsing.  An implementation that reads
  an unbounded input in order to find out whether it fits is open to
  memory exhaustion; each intake path needs its own read limit.

# Privacy Considerations

This section follows the guidance of {{RFC6973}}.

Labels in key identifiers.
: The label of a key_id is chosen by its holder and is sent in clear
  wherever the key_id appears.  A label such as a person's device name
  reveals that name to every node that sees a row.  For this reason a
  key revocation names the revoked key by the digest of its public key,
  not by its key_id.

Subjects without keys.
: A canonical identifier is a hash of a platform, entity kind and
  identifier.  Where the identifier space is small, the hash can be
  reversed by enumeration.

Audience.
: `cohort_scope` limits which nodes may receive a row.  It is signed,
  through the mirror, so a relay cannot widen it.  It does not
  encrypt the row; a node inside the audience can read and keep it.

Withdrawal is not erasure.
: A `withdraws` row stops a claim from standing.  It does not remove
  the original row from nodes that already hold it.  {{CC}} defines a
  separate removal procedure.

# IANA Considerations

This document has no IANA actions.

--- back

# CDDL {#cddl}

The following CDDL {{RFC8610}} describes the row, the signed object,
the mirror, a cosignature entry, and a key record.  It uses the JSON
interpretation of CDDL.  It is generated from the same table as the
normative text of {{CC}}.

~~~ cddl
{::include ../manifests/signed_object.cddl}
~~~

# Test Vectors {#vectors}

{{CC-VECTORS}} holds two test identities and thirteen vectors: five
rows that MUST be admitted, two size cases, and six rows that MUST be
refused, each with its refusal token.  For each admitted row it gives
the signed object, the JCS bytes in hex, the content hash, and both
signatures.

The smallest vector is reproduced here.  The attester's Ed25519 seed is

~~~
3e072ddf64847215af6d77de9efa0d95af5e2829abba3ff252cad647c8151593
~~~

and its public key is

~~~
69e98359bc7c5c783ee95150f2e9343e4f04775853bae63790bdc4aa3501c18e
~~~

which gives the key_id `alice-ctffz2edis`.  The signed object is

~~~ json
{
  "row": {
    "attestation_id": "5684f46c-749c-282f-bb10-0d74759dcde7",
    "attesting_key_id": "alice-ctffz2edis",
    "attestation_type": "scores",
    "attested_key_id": "bob-fx44qqfrla",
    "subject_key_ids": [],
    "cohort_scope": "federation"
  },
  "asserted_at": "2026-10-18T12:00:00.000Z",
  "dimension": "expertise:cardiology:en:v1",
  "score": 0.8,
  "confidence": 0.9
}
~~~

Its signing input is 326 bytes:

~~~
{"asserted_at":"2026-10-18T12:00:00.000Z","confidence":0.9,
"dimension":"expertise:cardiology:en:v1","row":{"attestation_id":
"5684f46c-749c-282f-bb10-0d74759dcde7","attestation_type":"scores",
"attested_key_id":"bob-fx44qqfrla","attesting_key_id":
"alice-ctffz2edis","cohort_scope":"federation","subject_key_ids":[]},
"score":0.8}
~~~

(line breaks added for display; the signing input has none).  The
content hash is

~~~
f61e3b8bc13fbe4e09897fcf366c84264b69d16dc59d4f6c606cc86a7803fbed
~~~

and the Ed25519 signature, in base64, is

~~~
ahk5YzITuIqtXaBl7fIChZ9x1sMkeuypdtuG/6O4Hm1iubzc/OJ0C/rG6QyJjPZt
8aF5MVJmuuJU6WYopsm+Bg==
~~~

(line break added for display).  The ML-DSA-65 key and one valid
signature are in {{CC-VECTORS}}.

# Acknowledgments
{:numbered="false"}

The canonical-form rules in this document were found and fixed in
review by the implementers of CIRISPersist, CIRISVerify and CIRISEdge.
