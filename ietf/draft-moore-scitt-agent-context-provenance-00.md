---
title: "Prompt Context Provenance for AI Agent Decision Traces"
abbrev: "Agent Context Provenance"
category: info
submissiontype: IETF
docname: draft-moore-scitt-agent-context-provenance-00
number:
date: 2026-11-19
v: 3
area: "Security"
workgroup: "Supply Chain Integrity, Transparency, and Trust"
keyword:
 - AI agent
 - provenance
 - transparency
 - prompt
 - ablation
 - formal verification
venue:
  github: "CIRISAI/CIRISConstitution"
  latest: "https://github.com/CIRISAI/CIRISConstitution/tree/main/ietf"

author:
 -
    fullname: Eric Moore
    organization: CIRIS L3C
    email: eric@ciris.ai

normative:
  RFC5646:
  RFC6234:
  RFC8610:
  RFC8949:
  RFC9052:
  I-D.moore-scitt-ciris-ceg:
    title: "Signed Attestation Rows of the CIRIS Epistemic Grammar and Their Relationship to SCITT"
    author:
      - name: Eric Moore
    date: 2026-11
    seriesinfo:
      Internet-Draft: draft-moore-scitt-ciris-ceg-02

informative:
  RFC7942:
  RFC8785:
  RFC9943:
  I-D.thaha-scitt-agent-execution-evidence:
  I-D.durga-wimse-ctx-isolation:
  I-D.sharif-agent-audit-trail:
  I-D.emirdag-scitt-ai-agent-execution:
  I-D.mih-scitt-agent-action-capsule:
  I-D.birkholz-vcon-ai-agent-extension:
  I-D.gilda-audit-agent-audit-record:
  I-D.kuehlewind-audit-architecture:
  I-D.birkholz-verifiable-agent-conversations:
  I-D.cosme-audit-agent-traceability:
  AUDIT-CHARTER:
    title: "Agent Use of Delegation and Interaction Traceability (AUDIT) Working Group Charter (draft)"
    author:
      - org: AUDIT BoF proponents
    date: 2026
    target: https://github.com/mirjak/audit-bof-preparation/blob/main/audit-charter.md
  TLA:
    title: "Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers"
    author:
      - name: Leslie Lamport
    date: 2002
    seriesinfo:
      ISBN: 0-321-14306-X
  OTEL-GENAI:
    title: "Semantic Conventions for Generative AI Systems"
    author:
      - org: OpenTelemetry
    target: https://opentelemetry.io/docs/specs/semconv/gen-ai/
  CC:
    title: "The CIRIS Constitution"
    author:
      - org: CIRIS L3C
    target: https://github.com/CIRISAI/CIRISConstitution
  CIRISAGENT:
    title: "CIRISAgent"
    author:
      - org: CIRIS L3C
    target: https://github.com/CIRISAI/CIRISAgent
  FORMAL:
    title: "H3ERE context-flow model (TLA+), vendored at CIRISAgent 59b7e5d"
    author:
      - org: CIRIS L3C
    target: https://github.com/CIRISAI/CIRISAgent/tree/59b7e5d/formal/h3ere_ctxflow

--- abstract

An AI agent that acts on a person's behalf makes each decision through
several calls to language models: one stage drafts an action, others
evaluate it, and others may veto it.  What each call was given decides
what it can judge.  A record of the action alone cannot show whether a
judging stage lacked a rule the drafting stage had, whether untrusted
text reached a stage designed never to see it, or whether a stage was
prompted in a language other than the one the person used.

This document specifies a per-call context manifest.  It describes
every contiguous piece of text placed into a model call (a segment) by
what it is, where it came from, how far it can be trusted, which
authority stands behind it, how long it lives, and which language it is
in.  It specifies a closed-vocabulary context policy that says which
stage may and must receive which kinds of segment, ablation stubs that
stand in for text withheld from a stage, and the checks a verifier runs
against the manifest and against the bytes actually sent.  It states
the safety properties of the policy as invariants checked by a model
checker.  The manifest is carried as the payload of a CEG trace row or
of any SCITT signed statement.

--- middle

# Introduction

Several Internet-Drafts record what an AI agent did: the tool it called,
the authorization it held, the decision it reached, and a digest of the
model input ({{related}}).  They answer "what was done, by whom, under
whose authority".  They do not answer a question that comes before it:
what was each model call actually given, and was it supposed to be
given that?

The question matters because an agent's decision is not one model call.
In the agent this document was developed against, a decision passes
through up to fourteen call sites in four roles: a drafter that
proposes an action, second passes that fill in a chosen verb,
evaluators that score the situation, and judges (consciences) that may
veto the draft ({{model}}).  Some judges are deliberately denied the
untrusted text the drafter saw, so that a persuasive request cannot
argue a judge out of its veto.  This is input ablation.

Measurement of that agent, before the mechanism in this document
existed, found failures that no action record could show
({{measured}}):

* A rule a Wise Authority (the agent's human overseer) had stated
  reached the drafter, but almost never the two ablated judges.  The
  judges then vetoed compliant replies as "invented policy".

* The reason for a veto never reached the stage asked to revise the
  draft (0 of 162 retries).

* Raw user text reached the ablated judges inside a system-built record
  of earlier actions, in about a third of first-pass calls.  The
  ablation leaked.

* A user's self-chosen display name was laid out where a verified
  identity belonged.

All four were found by pattern-matching 42,998 prompts after the fact.
This document makes the same facts a signed record of every call.

## What This Document Adds

Five properties distinguish this profile from the agent trace drafts
surveyed in {{related}}.  As far as the author has found, none of them
is specified elsewhere for agent traces.

1. **Provenance of each piece of context.**  Each segment carries its
   kind, provenance, source, trust level and lifecycle, and the
   authentication, authorization and accounting records that make it
   binding ({{taxonomy}}).  Trust propagates: a segment is no more
   trusted than any segment whose bytes it contains.

2. **Withholding with a record.**  A stage may be given a stub in place
   of a segment: closed-vocabulary properties of the withheld text,
   never its bytes ({{stubs}}).  The manifest records what was withheld
   and a digest of it, and a verifier checks that the withheld bytes do
   not appear elsewhere in the call.

3. **Language as evidence.**  Each segment records the locale its bytes
   were rendered in and how that is known, and the manifest lists the
   segments that fell back to another language ({{locale}}).

4. **Machine-checked policy.**  The context policy is compiled from a
   closed vocabulary.  The same source generates the runtime guard and
   a TLA+ {{TLA}} specification whose invariants a model checker
   verifies ({{formal}}).

5. **Declared against observed.**  Each segment records its span and a
   digest of its bytes in the message actually sent, so a verifier can
   check that the manifest describes the call and not an intention
   ({{verify}}).

## Scope

This document specifies the manifest, the policy vocabulary, the stub,
and the checks.  It does not specify how an agent decides, what any
stage concludes, or how a tool call is authorized: the manifest
records what models were given, not whether they were right.  It
defines no new signature, receipt or transparency mechanism: those are
{{I-D.moore-scitt-ciris-ceg}} and {{RFC9943}}.

## Conventions and Definitions

{::boilerplate bcp14-tagged}

Call:
: One request to a language model.

Stage:
: A named call site in the agent's decision procedure.  Every call
  belongs to exactly one stage.

Stage role:
: What a stage does: `drafter`, `second_pass`, `evaluator` or `judge`
  ({{model}}).

Ablated stage:
: A stage that by policy receives no untrusted text.

Segment:
: One contiguous run of text placed into a call, described as in
  {{taxonomy}}.

Assembler:
: The component that builds a call's messages from segments, enforces
  the policy, and emits the manifest.  An implementation conforming to
  this document has exactly one assembler path for every call.

Policy:
: The table that says, for each stage and each kind of segment, whether
  the stage must, may or must not receive it, and in which form
  ({{policy}}).

Manifest:
: The per-call record specified in {{manifest}}.

Stub:
: The closed-vocabulary description sent in place of a withheld segment
  ({{stubs}}).

Wise Authority (WA):
: A human party whose signed grants make rules binding on the agent.
  The term is that of {{CC}}; any deployment's equivalent overseer
  fills the same role here.

# The Decision Model {#model}

A decision is the work an agent does on one thought: a unit of
reasoning within a task.  The stages of the model are:

| Role | Stages in the reference implementation |
|---|---|
| drafter | `aspdma` (action selection) |
| second_pass | `tsaspdma`, `dsaspdma`, `fsaspdma`, `msaspdma`, `rsaspdma` (one per verb: tool, defer, forget, memorize, recall) |
| evaluator | `csdma` (common sense), `dsdma` (domain), `pdma` (principles), `idma` (intuition) |
| judge | `coherence`, `epistemic`, `entropy`, `optveto` (optimization veto) |
{: title="Stages and their roles"}

Evaluators run first and their results reach the drafter.  The drafter
proposes an action; a second pass completes it for its verb.  Every
judge then reviews the draft.  A veto sends the thought back to the
drafter with typed feedback (a retry), up to a depth limit.  A draft
that survives review is executed.

A deployment MAY name different stages.  This profile requires only
that each stage has a stable name, one role, and an entry in the
policy, and that the set of ablated stages is declared in the policy.

In the reference implementation the ablated stages are `entropy` and
`optveto`.  They judge the draft against the agent's own commitments
and against signed rules, but never see the request that prompted it.

# Segment Taxonomy {#taxonomy}

A segment is described on six independent axes.  The kind says what the
text is; provenance, source, trust and lifecycle say where it came from
and what it is worth; locale says what language it is in.  Keeping the
axes separate is deliberate: the earlier measurement mixed them, and the
mixing is how leaks hid.

## Kind

| Kind | Meaning |
|---|---|
| `stage_instruction` | the stage's own prompt: role, task, output contract |
| `schema_instruction` | output-schema text a provider library appends to the call |
| `accord` | the agent's governing ethical text |
| `identity_base` | the agent's configured identity |
| `amendment` | one approved, signed change to the agent's identity |
| `rule` | a behavioural rule in force for this request, with its provenance |
| `wa_guidance` | a Wise Authority's guidance from a resolved deferral |
| `request` | the message being answered |
| `history` | earlier messages in the conversation |
| `sender_identity` | the verified sender: subject, role, and what verified them |
| `display_name` | the sender's self-chosen name |
| `action_record` | the factual record of actions already taken in the task |
| `draft` | the proposed action under review |
| `dma_output` | an evaluator's result passed downstream |
| `conscience_feedback` | a typed veto passed to a retry |
| `tool_output` | a tool's result |
| `pipeline_position` | where the stage sits and what it cannot see |
{: title="Segment kinds"}

`sender_identity` and `display_name` are separate kinds so that no
layout can present a name as an identity.  A `sender_identity` segment
carries no text of its own: the assembler renders it from its
authentication carrier ({{carriers}}).

## Provenance

Provenance applies to `rule` segments only, and is REQUIRED on them.

| Provenance | Meaning | Trust |
|---|---|---|
| `user_chat` | stated by a user in conversation | untrusted |
| `wa_chat` | stated by a Wise Authority in conversation, unsigned | untrusted |
| `signed_guidance` | from a resolved deferral whose grant signature verified | verified |
| `amendment` | from a landed, signed identity amendment | verified |
{: title="Rule provenance"}

A rule stated in conversation is advisory, whoever states it.  It
remains part of the `request` or `history` segment it was said in.  In
the reference policy no stage lists `rule.user_chat` or `rule.wa_chat`,
so no such segment is ever produced; the values exist so that a policy
that admitted one would be expressible and checkable.

## Source

Which component produced the bytes: `user_input`, `adapter_metadata`,
`auth_context`, `signed_row`, `agent_profile`, `engine`, `llm_output`,
`tool_output` or `provider_lib`.  A kind MAY be restricted by the
policy to one source.

## Trust {#trust}

Trust has three ordered levels: `untrusted` < `verified` < `system`.

* `untrusted`: user-controlled or model-generated text.
* `verified`: established by the system against a credential or a
  signature.
* `system`: produced by the agent from its own state.

The policy assigns each kind (and each rule provenance) a trust level.
A producer MAY state a lower trust for a segment than the policy's; it
MUST NOT state a higher one.

**Taint rule.**  A segment's trust after taint is the minimum of its own
trust and the trust after taint of every segment listed in its
`derived_from`.  The manifest records trust after taint.  An
`action_record` that quotes a user's words is therefore `untrusted`,
whichever component built it.  A segment whose trust after taint is
below the trust the policy requires for its kind is a `tainted`
violation ({{violations}}).

## Lifecycle

How long a segment lives: `standing`, `per-task`, `per-message`,
`per-thought`, `retry-only` or `per-call`.  A per-task or per-thought
segment records the task or thought it belongs to; one placed in a call
for another task or thought is a `cross_scope` violation.

## AAA Carriers {#carriers}

Each segment MAY carry three records.  The policy states which are
REQUIRED for which kind.

Authentication (`authn`):
: The verified subject: subject identifier, role, and the verifier that
  established them.  REQUIRED on `sender_identity`.

Authorization (`authz`):
: The grant that makes the segment binding: its kind (`amendment`,
  `deferral` or `response_attestation`), its identifier, the
  authorizer, whether its signature verified, and when it was granted.
  REQUIRED on `amendment`, on `rule` with provenance `signed_guidance`
  or `amendment`, and on `wa_guidance`.

Accounting (`acct`):
: The record tying the segment to the audit trail: audit entry, the
  hash of the signed row its bytes came from, the trace, and for
  `conscience_feedback` the veto and discharge identifiers.

A judge that is asked whether a rule binds reads the rule's `authz`
carrier, attested by the system, not prose claiming authority.

## Locale {#locale}

Each segment records `locale`, a language tag {{RFC5646}}, and
`locale_basis`:

`declared`:
: The producer stated the locale it actually served, after any
  fallback.  For text read from a localized prompt file, this is the
  file read, not the file requested.

`assembler_rendered`:
: The assembler rendered the bytes itself (for example, a sender line
  from its carrier in the call's language, or a stub line).

`unstated`:
: No component vouches for a locale.  User text, model output, and text
  authored in an agent's configuration are `unstated` unless their
  producer states otherwise.

Two tags have fixed meanings here: `mul` for text that is deliberately
multilingual (a polyglot prompt), and `zxx` for closed-vocabulary
tokens with no linguistic content (a stub line).

The call records `language`, the locale it was rendered for.  A
segment is a locale fallback when its basis is `declared`, its locale
is neither `mul` nor `zxx`, and its primary language subtag differs
from that of the call's language.  The manifest lists every fallback
segment in `locale_fallbacks`.  A regional variant (`pt-BR` in a `pt`
call) is not a fallback.

A segment joined from fields served in different locales (for example,
a localized paragraph followed by one that fell back to English)
records the locale that differs from the call's language, so that the
segment is listed as a fallback.  A per-field fallback is a fallback:
a producer that serves one field of a localized prompt from another
language MUST record that field's segment with the language actually
served.

The reason this is evidence and not configuration: a judge prompted
partly in English while the person wrote in Amharic is a different
judge.  In the reference implementation this was first found by
counting script characters in sent prompts; with this record it is a
field of every call.

# The Context Policy {#policy}

The policy is a single document.  It has five parts:

`version`:
: An integer.

`ablated_stages`:
: The stages that receive no untrusted text.

`kinds`:
: For each kind: its trust (absent for `rule`, whose trust comes from
  provenance), its lifecycle, which carriers are REQUIRED, whether it
  is rendered with a label, whether it is an accepted residual
  ({{residuals}}), and the one source it may have, if fixed.

`rule_provenance`:
: The trust of each rule provenance.

`stages`:
: For each stage, an ordered list of rows.  A row is a kind (or
  `rule.<provenance>`), a predicate, and a form.  Row order is the
  stage's rendering order.

`stub_fields`:
: The closed set of fields a stub may carry ({{stubs}}).

## Predicates

A row's predicate says when the stage receives the kind.  The predicates
are a closed set, each evaluated against facts the system establishes
from its own state (signed rows, the authentication context), never
from the segments being checked:

| Predicate | Holds when |
|---|---|
| `always` | always |
| `never` | never |
| `retry` | the call is a retry after a veto |
| `signed_guidance_in_force` | signed WA guidance from a resolved deferral applies |
| `amendment_in_force` | a landed identity amendment carries a rule that applies |
| `trusted_rule_in_force` | either of the two above |
| `id_scoped` | the rule in force is scoped to a verified identity |
| `advisory_rule` | an unsigned rule was stated in conversation |
{: title="Policy predicates"}

When a predicate holds, the kind is REQUIRED at that stage; a call
without it is a `missing_required` violation.  When it does not hold,
or the kind has no row, the kind is forbidden.  Facts MUST NOT be
derived from the segments, or a missing rule could hide itself.

## Form

A row's form is `full` (the segment's bytes are sent) or `stub` (a stub
is sent in place of the bytes).  A `stub` row is permitted only at an
ablated stage, and only for an untrusted kind.

## Static Checks

A policy is admissible only if a compiler confirms all of the following
before it is deployed.  The reference compiler refuses a policy that
fails any of them.

1. **Closed vocabulary.**  Every kind, provenance, source, trust,
   lifecycle, predicate, form and stub field is one this document
   names.

2. **Firewall.**  At an ablated stage, every untrusted kind is either
   absent, a `stub` row, or a declared residual.

3. **Signed rules only.**  No stage requires a rule whose provenance is
   untrusted.

4. **No laundering.**  A kind the policy marks `system` is admitted only
   with an empty `derived_from` at runtime; the assembler enforces this
   per call.

5. **Identity layout.**  Any stage that admits `display_name` admits it
   only as a labelled kind, never inside `sender_identity`.

6. **Evidence sufficiency.**  Wherever a trusted rule can be in force,
   every judge receives that rule with its authorization carrier.

7. **Coverage.**  Every declared kind is used by some stage, and every
   stage is assigned a role.

The same policy source generates the runtime guard, the TLA+ contract
({{formal}}) and the conformance tests, so that code, model and
behaviour cannot silently diverge.

## Residuals {#residuals}

Some untrusted text cannot be withheld from a judge without defeating
the judge.  The draft under review is the main case: it may quote the
request.  A policy names such kinds as residuals.  A residual is sent in
full at an ablated stage, is excluded from the leak check
({{verify}}), and is recorded as untrusted.  Residuals are a stated
limit of the ablation, not an exception to it.

# Ablation Stubs {#stubs}

A stub tells an ablated stage that something was withheld, and what
kind of thing it was, without its bytes.  Without a stub the stage
would judge a draft that answers a question it cannot know was asked.

A stub's fields are drawn only from this closed set; a policy's
`stub_fields` selects which are rendered:

| Field | Values |
|---|---|
| `kind` | the withheld segment's kind |
| `provenance` | for a rule: its provenance |
| `source` | the withheld segment's source |
| `trust` | its trust after taint (always `untrusted` for a stub) |
| `author_role` | the author's verified role, or `unauthenticated` |
| `authority` | `none`, `advisory`, or `signed` (only with a verified grant) |
| `scope` | `this_turn`, `this_task`, `standing` |
| `disposition` | the engine's state for it, per kind (below) |
| `transforms` | engine operations applied: `sanitized`, `truncated`, `normalized`, `redacted`, `coalesced` |
| `draft_relation` | `none`, `responds_to`, `quotes`; with `quote_share` `0`, `<10%`, `10-50%`, `>50%` |
| `size` | `short` (at most 200 characters), `medium` (at most 1000), `long` |
| `position` | `current` or `prior_<n>` |
| `digest` | the first 12 hexadecimal digits of SHA-256 of the withheld bytes |
{: title="Stub fields"}

Dispositions are per kind: a request is `open`, `answered`, `deferred`
or `refused`; a rule is `advisory_unsigned`, `awaiting_signature` or
`refused`; a tool output is `success` or `failure`; history is `prior`.

`quote_share` is the share of the withheld segment's character 8-grams
(after whitespace collapsing and case folding) that the draft repeats.
It is computed deterministically and never by a model.

Every field value comes from the engine's state or from a deterministic
function of the bytes.  No field carries text of the withheld segment,
and no field is produced by a model.  The rendered stub line is
assembler-rendered with locale `zxx`.

# The Context Manifest {#manifest}

## Encoding

The manifest is a CBOR map {{RFC8949}} with text-string keys, encoded
deterministically (Section 4.2 of {{RFC8949}}) when it is the payload
of a signed statement.  Following {{I-D.moore-scitt-ciris-ceg}}, it
contains no floating-point values: every number is an integer.
Digests are SHA-256 {{RFC6234}}.

The reference implementation emits the same structure as JSON on its
reasoning stream, with digests as lowercase hexadecimal text.  A
producer that signs a manifest converts each digest to a byte string of
32 octets (6 octets for a stub digest), omits each optional member the
JSON form gives as null, and otherwise keeps the structure.

## CDDL

The manifest is specified in CDDL {{RFC8610}}.

~~~ cddl
context-manifest = {
  "call_id": tstr,
  ? "task_id": tstr,
  ? "thought_id": tstr,
  "thought_kind": "seed" / "followup" / "guidance",
  "retry_index": uint,
  "stage": stage-name,
  "stage_role": "drafter" / "second_pass" / "evaluator" / "judge",
  "response_model": tstr,
  ? "max_tokens_sent": uint,
  "policy_version": uint,
  "policy_sha256": digest,
  "assembler_version": tstr,
  "guard_mode": "fail_closed" / "strip_and_incident",
  "guard_violations": [* guard-violation],
  "segments": [* segment-record],
  "messages_sha256": digest,
  ? "messages_digest_form": messages-digest-form,
  ? "sent_messages_match": bool,
  ? "language": language-tag,
  "locale_fallbacks": [* tstr],
  "provider_capture": provider-capture,
  ? "provider_mode": tstr,
  "provider_kwargs_added": [* tstr],
}

stage-name = tstr .regexp "[a-z][a-z0-9_]{0,31}"
digest = bstr .size 32
language-tag = tstr

segment-record = {
  "segment_id": tstr,
  "kind": kind,
  ? "provenance": provenance,
  "source": source,
  "trust": "untrusted" / "verified" / "system",
  "lifecycle": "standing" / "per-task" / "per-message" /
               "per-thought" / "retry-only" / "per-call",
  ? "authn": authn,
  ? "authz": authz,
  ? "acct": acct,
  "message_index": uint,
  "span_start": uint,
  "span_end": uint,
  "sha256": digest,
  "truncated": bool,
  "derived_from": [* tstr],
  "form": "full" / "stub",
  ? "stub": stub,
  ? "withheld_sha256": digest,
  ? "locale": language-tag,
  "locale_basis": "declared" / "assembler_rendered" / "unstated",
}

kind = "stage_instruction" / "schema_instruction" / "accord" /
       "identity_base" / "amendment" / "rule" / "wa_guidance" /
       "request" / "history" / "sender_identity" / "display_name" /
       "action_record" / "draft" / "dma_output" /
       "conscience_feedback" / "tool_output" / "pipeline_position"

provenance = "user_chat" / "wa_chat" / "signed_guidance" /
             "amendment"

source = "user_input" / "adapter_metadata" / "auth_context" /
         "signed_row" / "agent_profile" / "engine" / "llm_output" /
         "tool_output" / "provider_lib"

authn = {
  "subject_id": tstr,
  "role": tstr,
  "verifier": tstr,
}

authz = {
  "grant_kind": "amendment" / "deferral" / "response_attestation",
  "grant_id": tstr,
  ? "authorizer_id": tstr,
  "signature_verified": bool,
  "attestation_ids": [* tstr],
  ? "granted_at": tstr,
}

acct = {
  ? "audit_entry_id": tstr,
  ? "row_hash": tstr,
  ? "trace_id": tstr,
  ? "veto_id": tstr,
  "discharge_ids": [* tstr],
}

stub = {
  "kind": kind,
  ? "provenance": provenance,
  "source": source,
  "trust": "untrusted",
  "author_role": "OBSERVER" / "ADMIN" / "AUTHORITY" /
                 "SYSTEM_ADMIN" / "unauthenticated",
  "authority": "none" / "advisory" / "signed",
  "scope": "this_turn" / "this_task" / "standing",
  "disposition": "open" / "answered" / "deferred" / "refused" /
                 "advisory_unsigned" / "awaiting_signature" /
                 "success" / "failure" / "prior",
  "transforms": [* "sanitized" / "truncated" / "normalized" /
                   "redacted" / "coalesced"],
  "draft_relation": "none" / "responds_to" / "quotes",
  "quote_share": "0" / "<10%" / "10-50%" / ">50%",
  "size": "short" / "medium" / "long",
  "position": tstr .regexp "current|prior_[0-9]{1,4}",
  "digest": bstr .size 6,
}

guard-violation = {
  "kind": "forbidden" / "missing_required" / "tainted" /
          "missing_carrier" / "wrong_source" / "lifecycle_mismatch" /
          "cross_scope" / "duplicate_segment_id" / "untrusted_bytes",
  "stage": stage-name,
  "policy_key": tstr,
  ? "segment_id": tstr,
  "detail": tstr,
  "action": "raised" / "stripped" / "recorded",
}

messages-digest-form = "ciris-json-1" / "jcs"

provider-capture = "not_finalized" / "captured" /
                   "no_message_change" / "unsupported_mode" /
                   "unrecognized_change" / "unavailable"
~~~
{: #fig-cddl title="The context manifest"}

## Field Semantics

`call_id`
: Unique per call.  When the producer has none, it is the first 32
  hexadecimal digits of SHA-256 over the stage, task, thought, retry
  index and messages digest joined by `|`.

`retry_index`
: 0 on the first pass, n on the n-th retry after a veto.

`policy_sha256`
: SHA-256 of the policy document's bytes.  A verifier MUST hold the
  policy with this digest to run the checks of {{verify}}.

`guard_mode`
: `fail_closed` means a violation aborts the call (used in testing and
  QA).  `strip_and_incident` means the offending segment is removed,
  an incident is recorded, and the call proceeds (used in production).
  A manifest with violations in `fail_closed` mode never accompanies a
  sent call.

`segments`
: In rendering order.  `message_index` and `[span_start, span_end)`
  locate the segment in the content of the message sent, in Unicode
  scalar values.  `sha256` is over the UTF-8 encoding of exactly that
  span.  For a `stub` segment, the span holds the stub line, `stub`
  holds the stub, and `withheld_sha256` is over the UTF-8 encoding of
  the withheld bytes.

`messages_sha256`, `messages_digest_form`
: A digest of the messages as sent.  Form `ciris-json-1` is the form
  the reference implementation's model bus hashes: a JSON array of the
  message objects in order, each with `role` and `content`, members in
  insertion order, separators `", "` and `": "`, non-ASCII characters
  unescaped, encoded as UTF-8.  Form `jcs` is the JSON Canonicalization
  Scheme {{RFC8785}} over the same array.  Absent means `ciris-json-1`.
  New implementations SHOULD use `jcs` and state it.

`sent_messages_match`
: Set by the component that sent the call: true when the messages it
  sent hash to `messages_sha256`.  Absent when the manifest was not
  finalized at the sending component.

`provider_capture`
: Whether text a provider library added to the call (for example, an
  output schema appended to the last message) was reproduced and
  recorded as `schema_instruction` segments.  `unrecognized_change`
  means the library rewrote the messages in a way the producer could
  not record; a verifier treats such a call's segment list as
  incomplete.

# Guard Violations {#violations}

The assembler checks every call against the policy before it is sent:

| Violation | Meaning |
|---|---|
| `forbidden` | the policy does not admit this kind at this stage in this state |
| `missing_required` | a required kind is absent |
| `tainted` | trust after taint is below the policy's trust for the kind |
| `missing_carrier` | a required `authn`, `authz` or `acct` is absent |
| `wrong_source` | the kind's fixed source differs |
| `lifecycle_mismatch` | a stated lifecycle differs from the policy's |
| `cross_scope` | a per-task or per-thought segment from another task or thought |
| `duplicate_segment_id` | two segments share an identifier in one call |
| `untrusted_bytes` | at an ablated stage, a withheld segment's bytes were found inside another, non-residual segment |
{: title="Guard violations"}

A violation's `detail` explains it and MUST NOT contain segment text.

The `untrusted_bytes` check normalizes text by collapsing whitespace and
case folding, then looks for windows of 32 characters taken every 16
characters (at most 256 windows) of each withheld segment of at least
20 characters, inside every other segment that is neither a residual
nor attested by a verified grant.

# Verifying a Manifest {#verify}

A verifier holds the manifest, the policy whose digest the manifest
names, and, where available, the messages as sent.  It runs these
checks and reports each as passed, failed, or not run with the reason.

V1 Policy conformance:
: Recompute, from the segment records and the facts the verifier can
  establish, every violation of {{violations}} except `untrusted_bytes`.
  Report any the manifest does not list.

V2 Sent bytes:
: With the messages as sent: recompute `messages_sha256`, and for each
  segment the digest of its span.  Report any mismatch.  This is the
  check that catches a call that bypassed the assembler, or a manifest
  that misdescribes its call.

V3 Taint:
: Recompute trust after taint from `derived_from` and the policy.
  Report any segment recorded at a higher trust.

V4 Ablation:
: At each ablated stage, confirm every untrusted, non-residual segment
  has form `stub`; with the messages as sent and the withheld bytes, run
  the `untrusted_bytes` search over the text outside residual spans.

V5 Carriers:
: Confirm each required carrier is present, and that every `authz` with
  `signature_verified` true resolves to a grant whose signature the
  verifier can check.

V6 Locale:
: Recompute `locale_fallbacks` from the segment records and `language`.
  A deployment that requires a locale MAY additionally require that no
  segment of kind `stage_instruction` or `pipeline_position` is a
  fallback.

V7 Completeness:
: Report `provider_capture` values `unsupported_mode`,
  `unrecognized_change` and `unavailable`: the segment list may not
  cover the call.

A verifier that lacks the messages as sent can run V1, V3, V5, V6 and
V7.  V2 and V4 require the bytes.  This separation lets a manifest be
published while the prompts, which may hold personal data, are not
({{privacy}}).

# Formal Model {#formal}

The policy's safety properties are stated as invariants of a TLA+
specification and checked with the TLC model checker.  The
specification, `H3EREContextFlow.tla`, models one thought through
drafting, judging, retry and execution across six scenarios (no rule;
a user's own preference; an unsigned WA rule; signed WA guidance; a
signed amendment; an identity-scoped amendment with an impersonation
attempt) and a bounded retry depth.  Its context inputs are generated:
the contract configuration from the policy by the compiler of
{{policy}} (`ContractPolicy.tla`), and the measured configuration from
manifests and sent prompts of real runs (`ContextData.tla`).

The invariants, by name, as checked at {{FORMAL}}:

| Invariant | Property |
|---|---|
| `Ablation` | no ablated judge receives an untrusted kind |
| `EvidenceSufficiency` | when a trusted rule is in force, every judge receives it |
| `VerifiedIdentity` | under an identity-scoped rule, every judge receives the verified sender |
| `NoLaundering` | no judge receives a system segment carrying untrusted bytes |
| `NoCrossTaskLeak` | WA guidance reaches judges only within its own task |
| `IdentityLayout` | a display name never appears inside the sender line |
| `StubsOnlyAblated` | stubs appear only at ablated stages |
| `NoWrongExecution` | an executed action is acceptable for its scenario |
| `ReviewIntegrity` | the action executed is the action reviewed, or a refusal the tool gate forced |
| `VetoContinuity` | a vetoed action executes only after its veto is discharged |
| `AuthMonotone` | once refused for lack of authority, the action is not later executed |
| `NoForcedDeferral` | no deferral is forced by the depth limit alone |
| `DeferralInformative` | every deferral carries its package to the WA |
| `Terminates` | every thought reaches a final state |
{: title="Invariants of H3EREContextFlow.tla"}

Results at {{FORMAL}}: the contract configuration satisfies all
fourteen invariants.  The configuration measured from the reference
agent before the mechanism of this document (version 2.22.1) violates
ten of them.  A variant of the contract that admits one unreviewed
change after review violates `ReviewIntegrity`, `VetoContinuity`,
`AuthMonotone` and `NoWrongExecution`; adding the tool gate restores
`AuthMonotone` only.  These are model-checking results over a finite
abstraction, not proofs about the implementation; the manifest is what
connects the two, since the measured configuration is generated from
it.

# Carrying the Manifest {#carrying}

## As a CEG Trace Row

In {{I-D.moore-scitt-ciris-ceg}}, an agent's own reasoning trace is a
row of the family `trace:{form}:{version}`.  A context manifest is
carried in such a row as follows:

* The row is signed only by the agent's own key.  {{CC}} (Section
  3.1.5) assigns the trace family's attest and withdraw uses to the
  agent signer kind; a node, host or person key MUST NOT sign it.  The
  machine-checkable form is the key-role contract of {{CC}}
  (`manifests/key_roles.json`, family `trace:{form}:{version}`, signer
  kind `agent`).

* The row names its run: `run_kind` is in the signed bytes, from the
  closed set of {{CC}} (`production`, `prod-personal`, `prod-managed`,
  `qa`, `battery`, `mock`).  A `mock` trace is refused at
  federation-tier admission outright, with refusal token
  `trace_run_kind_mock`: a mock model's output attests nothing about any
  agent.  A node MAY hold its own mock rows locally (for QA and tests).

* The manifests of a thought's calls are members of the trace payload,
  in call order.  The payload is deterministically encoded CBOR with no
  floating-point values.  Any score or confidence elsewhere in the
  trace is a fixed6 integer, as {{I-D.moore-scitt-ciris-ceg}} requires.

* The policy document a manifest names by `policy_sha256` SHOULD itself
  be published as a signed row, so that a verifier can obtain it.

The signed object, its signature, its names and references, and its
admission are those of {{I-D.moore-scitt-ciris-ceg}}; this document
repeats none of them.

## As a SCITT Signed Statement

A manifest MAY be the payload of any SCITT signed statement
{{RFC9943}} (a COSE_Sign1 {{RFC9052}} message registered with a
transparency service).  The checks of {{verify}} are unchanged.  Two
guarantees of a CEG row are lost:

* **The family's door.**  A CEG node admits a trace row only if its
  family's static checks pass, including the closed `run_kind`.  A
  generic transparency service admits a statement without inspecting
  its payload, so a `mock` or malformed manifest can be registered.

* **The key-role check.**  A CEG node refuses a trace row signed by any
  key but the agent's own.  Outside CEG, nothing binds the signer of a
  manifest to the agent whose calls it describes; a verifier MUST
  establish that binding by other means before relying on it.

# Relationship to Other Work {#related}

Several individual Internet-Drafts record agent actions in SCITT-style
statements.  Measured against the five properties of the Introduction:

* {{I-D.thaha-scitt-agent-execution-evidence}} digests the request and
  response octets at each model call, which this document's
  `messages_sha256` and span digests also provide.  It records digests
  of the system prompt and skills, but not who supplied each piece of
  context or at what trust, and its digest is taken before any content
  is withheld; it has no notion of a stage denied some context.

* {{I-D.durga-wimse-ctx-isolation}} attests a taint level for a context
  window per tool call, and refuses a call rather than withholding
  content.  This document's taint rule is per segment and its stubs
  record withholding.

* {{I-D.sharif-agent-audit-trail}}, {{I-D.emirdag-scitt-ai-agent-execution}},
  {{I-D.mih-scitt-agent-action-capsule}} and
  {{I-D.gilda-audit-agent-audit-record}} record actions, decisions,
  delegation and input hashes, and some redact the stored record.
  Redacting a record after the fact is different from withholding text
  from a model before the call, which is what a stub records.

* {{I-D.birkholz-vcon-ai-agent-extension}} attributes each message of
  an agent conversation to a party.

* The OpenTelemetry GenAI conventions {{OTEL-GENAI}} define spans for
  model calls and can capture input messages, but carry no provenance,
  trust or signature.

* {{I-D.kuehlewind-audit-architecture}} describes an architecture for
  auditing agent delegation and interactions across domains, and
  {{I-D.cosme-audit-agent-traceability}} the attestation and registry
  evidence for delegation traceability.  {{I-D.birkholz-verifiable-agent-conversations}}
  specifies verifiable records of agent conversations.  These address
  what passed between parties; this document addresses what each model
  call inside one party was given.

None of these, as far as the author has found, records the locale of
model input or states its properties as model-checked invariants.  This
document is complementary to all of them: an action record can
reference the manifests of the calls behind the action.

## Relationship to the AUDIT Charter {#audit}

The proposed AUDIT working group {{AUDIT-CHARTER}} would define
interoperable audit records for agents and delegated systems,
verifiable by a party that trusts neither the agent nor its operator.
The table below maps each signal the draft charter names to where a
deployment of {{I-D.moore-scitt-ciris-ceg}} with this profile carries
it.

| AUDIT signal | Carried by |
|---|---|
| Attribution to a user, agent instance or delegation context | the trace row is signed by the agent's own key; the `authn` carrier names the verified sender; delegation is a CEG `delegates_to` row |
| Delegation chains | `delegates_to` rows and their references ({{I-D.moore-scitt-ciris-ceg}}) |
| Authorization as a time-evolving state | `authz` carriers with grant identifier, authorizer, signature status and grant time; the grant's own rows, replaced and withdrawn by later rows; the policy predicates evaluated per call |
| Identity transitions | key records and identity amendments as signed rows; `amendment` segments with their grants |
| User intent declarations | the `request` segment (its digest, and its stub where withheld) |
| Agent and tool interactions, exchanged data | `tool_output`, `dma_output` and `draft` segments with span digests; `messages_sha256` per call |
| Invoked or declined actions, and outcomes | the trace's terminal result (completed, refused, deferred); typed vetoes in `conscience_feedback` |
| Execution context and structure as it emerges | one manifest per call, in call order, with stage, role, retry index and thought kind |
| Verifiable without trusting agent or operator | signed rows with transparency receipts; check V2 against bytes captured by a party the agent does not control ({{verify}}) |
| Privacy and selective disclosure without disclosing prompts | manifests carry identifiers, digests and closed-vocabulary values, never text; CEG members can be blinded (selective disclosure); V1, V3, V5, V6 and V7 run without the prompts |
{: title="AUDIT draft-charter signals and where they are carried"}

This profile also carries signals the draft charter does not ask for:
per-segment provenance and trust with taint, withholding with a record,
locale, and machine-checked policy invariants.

Two charter items are not covered here, and are not claimed:

* **Cross-domain correlation in protocols.**  CEG rows reference one
  another by name, and a manifest names its task and thought, but this
  document defines no identifier propagated across other parties'
  protocols (HTTP headers, token claims) to link one interaction across
  administrative domains.  That is the charter's third deliverable, and
  the identifier is expected from the agentproto working group.

* **Evidence from parties other than the agent.**  A trace row is the
  agent's own account.  Correlating it with records made by tools,
  services and other agents in other domains, where no single party has
  the whole picture, needs those parties' records; this profile is one
  of them, not the collection.

The draft charter places the auditing of "the underlying AI model,
training data, or inference mechanisms" out of scope while allowing
interactions with the model.  A manifest describes what each model call
was given and under which policy, not how the model computes; it is a
record of an interaction with the model, in the charter's terms.

# Implementation Status {#impl}

Note to the RFC Editor: please remove this section before publication,
together with the reference to {{RFC7942}}.

This section records the status of known implementations at the time of
writing, as described in {{RFC7942}}.  Listing an implementation here
does not imply endorsement.

CIRISAgent:
: {{CIRISAGENT}}, CIRIS L3C, AGPL-3.0.  The assembler, the policy file
  `ciris_engine/data/context_policy.yaml`, the runtime guard, ablation
  stubs and the per-call manifest are on the main branch at commit
  59b7e5d (pull request 1367).  The locale record of {{locale}} is in
  pull request 1368, not yet merged at the time of writing.  The
  implementation emits each manifest as JSON, with hexadecimal digests
  and the `ciris-json-1` messages form, on the `llm_call` event of its
  reasoning stream.  Its signed traces carry each call's
  `messages_sha256` (as `prompt_hash`) but not yet the manifest itself,
  and it does not emit `messages_digest_form`.  The reference
  policy compiler and the TLA+ specification are in
  `formal/h3ere_ctxflow/` of the same repository.

RATCHET:
: CIRIS L3C.  A context-map harness that drives the agent through the
  six scenarios with a deterministic mock model and checks every call's
  manifest against the policy and against the bytes sent (checks V1,
  V2, V4, and a script-based locale check that predates V6).  On the
  merged implementation it found the Amharic-locale gap that {{locale}}
  now records directly.

No second, independent implementation exists.

# Security Considerations

**What the manifest proves.**  A manifest signed by the agent's key is
the agent's own account of its calls.  Check V2 against independently
captured bytes (for example, at a model gateway the agent does not
control) is what turns that account into evidence.  Without it, a
compromised agent can emit a consistent but false manifest.

**Ablation is a stated limit, not a guarantee.**  Residuals are
untrusted text sent to ablated stages by design.  The leak check is a
substring search over normalized text: paraphrase, translation or
encoding defeats it.  It detects copying, not influence.

**Stubs leak properties.**  A stub reveals the kind, size bucket,
author role and disposition of withheld text, and its quote share
reveals how much of it the draft repeats.  The field set is closed so
that what leaks is known.

**Facts versus segments.**  Policy predicates are evaluated against
facts from trusted state.  An implementation that derived them from the
segments could let a missing rule hide itself, or let a forged segment
make itself required.

**Provider libraries.**  A library that rewrites messages after the
assembler can add text the policy never admitted.  The
`provider_capture` field makes that visible; it cannot prevent it.

# Privacy Considerations {#privacy}

A manifest contains identifiers, digests and closed-vocabulary values,
never segment text; violation details never contain segment text.  It
does contain subject identifiers in `authn` carriers, which are
personal data where the subject is a person.

Digests of short, guessable text can be inverted by trying candidates.
`withheld_sha256` and the stub digest of a short request (a size of
`short` is at most 200 characters) are open to this.  A deployment that
publishes manifests SHOULD replace these with keyed digests whose key is
held with the prompts, or omit them, and record which it did; the
reference implementation uses unkeyed SHA-256 and is affected.

Publishing manifests while withholding prompts is the intended use: V1,
V3, V5, V6 and V7 run on the manifest alone.

# IANA Considerations

This document has no IANA actions.

--- back

# Measured Motivation {#measured}

The figures below were measured on the reference agent, version 2.22.1,
with one model (qwen/qwen3.6-35b-a3b), one or two episodes per case,
before the mechanism of this document existed.  They are reported to
explain the design, not as general claims about agents.

| Finding | Measured |
|---|---|
| A rule the WA stated in conversation reached the ablated judges | about 1% of calls |
| WA guidance reached the `entropy` judge in a guidance task | 0% (other stages 100%) |
| The veto reason reached the verb second pass on retry | 0 of 162 calls |
| Raw user text reached the ablated judges via the action record | about 33% of first-pass calls, 62% of retries |
| The sender was given as a separate verified field | never |
{: title="Findings that motivated the manifest"}

# Example {#example}

This example is one call from a context-map run of the reference agent
(engine commit d6471f2) driven by a deterministic mock model, so it is a
`mock` run in the sense of {{carrying}} and would be refused at
federation-tier admission (`trace_run_kind_mock`).  It is reproduced as the implementation emitted it (JSON, with
hexadecimal digests and nulls), trimmed to three of its nine segments.
The call is the `entropy` judge, an ablated stage, reviewing a draft
reply to an observer's request.  The request is withheld and a stub
sent in its place.

~~~ json
{
 "call_id": "692f06ff7cdbc46a8bd9963e93b02cf9",
 "thought_kind": "seed",
 "retry_index": 0,
 "stage": "entropy",
 "stage_role": "judge",
 "response_model": "EntropyResult",
 "policy_version": 1,
 "policy_sha256":
  "facd58408a8b6a9e990edf85fd6beea11b6d3a0f5fbd0dd0f872dd63c73078fc",
 "assembler_version": "2",
 "guard_mode": "fail_closed",
 "guard_violations": [],
 "messages_sha256":
  "d61c8b816c5a6f1a63528f38cdf9985a8aa28c119874de5694451ac5de4f7377",
 "sent_messages_match": true,
 "provider_capture": "unavailable",
 "segments": [
  {
   "segment_id": "instr:system:pipeline_position",
   "kind": "pipeline_position",
   "source": "engine", "trust": "system", "lifecycle": "standing",
   "message_index": 1, "span_start": 1216, "span_end": 1526,
   "sha256":
  "84a557e030368407597c04f038733111f6e53bd19613cd28b1cd5fd8085a251b",
   "form": "full"
  },
  {
   "segment_id": "request",
   "kind": "request",
   "source": "user_input", "trust": "untrusted",
   "lifecycle": "per-message",
   "authn": {"subject_id": "wa-2026-11-19-75B7EB",
             "role": "OBSERVER", "verifier": "api_auth"},
   "message_index": 3, "span_start": 11, "span_end": 236,
   "sha256":
  "c38e1604e79f43dfd5dd92f5d2c2188716b860c04154ff90627ba120c9a07916",
   "form": "stub",
   "stub": {
    "kind": "request", "source": "user_input", "trust": "untrusted",
    "author_role": "OBSERVER", "authority": "none",
    "scope": "this_turn", "disposition": "open", "transforms": [],
    "draft_relation": "quotes", "quote_share": "<10%",
    "size": "medium", "position": "current", "digest": "3521ef40909a"
   },
   "withheld_sha256":
  "3521ef40909a426b42306e94a1ada345877f38b1483ac7022dc5e0202af3ddce"
  },
  {
   "segment_id": "draft",
   "kind": "draft",
   "source": "llm_output", "trust": "untrusted",
   "lifecycle": "per-thought",
   "message_index": 3, "span_start": 299, "span_end": 334,
   "sha256":
  "11133a80e1ff80fd997c817118a8ad1d4eb4a0bf2fa24219319e3604e92737b5",
   "form": "full"
  }
 ]
}
~~~
{: title="An entropy-judge manifest (trimmed)"}

Reading it: the judge received the draft in full (a residual) and,
in place of the request, a stub saying that an observer's request exists,
open, of medium size and carrying no authority, that the draft quotes
under 10% of it, and that its digest begins `3521ef40909a`.  The span
`[11, 236)` of message 3 holds the stub line, whose own digest is
`sha256`.  `sent_messages_match` is true: the bus sent exactly these
messages.  The run predates the locale record of {{locale}}, so the
segments carry no `locale` members.

# Acknowledgments
{:numbered="false"}

The context policy, the stubs and the formal model were developed
across the CIRISAgent, CIRISConstitution and RATCHET projects.
