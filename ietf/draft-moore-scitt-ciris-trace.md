---
title: "Signed Reasoning Traces of CIRIS Agents"
abbrev: "CIRIS Agent Reasoning Trace"
category: info
submissiontype: IETF
docname: draft-moore-scitt-ciris-trace-latest
number:
date: 2026-11-19
v: 3
area: "Security"
workgroup: "Supply Chain Integrity, Transparency, and Trust"
keyword:
 - AI agent
 - reasoning trace
 - transparency
 - signature
 - JSON canonicalization
venue:
  github: "CIRISAI/CIRISConstitution"
  latest: "https://github.com/CIRISAI/CIRISConstitution/tree/main/ietf"

author:
 -
    fullname: Eric Moore
    organization: CIRIS L3C
    email: eric@ciris.ai

normative:
  RFC2104:
  RFC2119:
  RFC8174:
  RFC3339:
  RFC4648:
  RFC6234:
  RFC8032:
  RFC8259:
  RFC8610:
  RFC8785:
  I-D.moore-scitt-ciris-ceg:
    title: "Signed Attestation Rows of the CIRIS Epistemic Grammar and Their Relationship to SCITT"
    author:
      - name: Eric Moore
    date: 2026-11
    seriesinfo:
      Internet-Draft: draft-moore-scitt-ciris-ceg-02

informative:
  RFC6973:
  RFC7942:
  RFC8949:
  RFC8792:
  RFC9943:
  I-D.moore-scitt-ciris-trace-context:
    title: "Context Manifests for the CIRIS Agent Trace: Prompt Context Provenance for AI Agent Decision Traces"
    author:
      - name: Eric Moore
    date: 2026-11
    seriesinfo:
      Internet-Draft: draft-moore-scitt-ciris-trace-context-00
  I-D.thaha-scitt-agent-execution-evidence:
  I-D.sharif-agent-audit-trail:
  I-D.emirdag-scitt-ai-agent-execution:
  I-D.mih-scitt-agent-action-capsule:
  I-D.gilda-audit-agent-audit-record:
  I-D.birkholz-vcon-ai-agent-extension:
  I-D.kuehlewind-audit-architecture:
  I-D.birkholz-verifiable-agent-conversations:
  I-D.cosme-audit-agent-traceability:
  OTEL-GENAI:
    title: "Semantic Conventions for Generative AI Systems"
    author:
      - org: OpenTelemetry
    target: https://opentelemetry.io/docs/specs/semconv/gen-ai/
  CC:
    title: "CIRIS Constitution 1.0-rc21"
    author:
      org: CIRIS L3C
    date: 2026-11
    target: https://github.com/CIRISAI/CIRISConstitution/tree/v1.0-rc21
  CIRISAGENT:
    title: "CIRISAgent"
    author:
      - org: CIRIS L3C
    target: https://github.com/CIRISAI/CIRISAgent
  FSD-TRACE:
    title: "CIRIS Trace Wire Format Specification (FSD/TRACE_WIRE_FORMAT.md), CIRISAgent 59b7e5d"
    author:
      - org: CIRIS L3C
    target: https://github.com/CIRISAI/CIRISAgent/blob/59b7e5d/FSD/TRACE_WIRE_FORMAT.md
  EGRESS-SCHEMA:
    title: "Per-level trace egress schema (ciris_adapters/ciris_accord_metrics/egress_schema.py), CIRISAgent 59b7e5d"
    author:
      - org: CIRIS L3C
    target: https://github.com/CIRISAI/CIRISAgent/blob/59b7e5d/ciris_adapters/ciris_accord_metrics/egress_schema.py
  TRACE-SCHEMA-JSON:
    title: "CIRIS Reasoning Trace v2.7.0 JSON Schema (ciris_adapters/ciris_accord_metrics/schemas/trace_format_v2_7_0.json), CIRISAgent 59b7e5d"
    author:
      - org: CIRIS L3C
    target: https://github.com/CIRISAI/CIRISAgent/blob/59b7e5d/ciris_adapters/ciris_accord_metrics/schemas/trace_format_v2_7_0.json

--- abstract

An AI agent that acts on a person's behalf reaches each action through
a sequence of steps: it gathers context, runs several evaluations,
selects an action, submits the selection to checks that can veto it,
and then acts.  Most of those steps are calls to language models.

This document specifies the CIRIS reasoning trace: one signed record
per unit of agent work (a thought), sealed when the action is taken.
The trace lists every step and every model call in the order the
recording component received them, with scores, outcomes, sizes,
costs and durations, and, at higher disclosure levels, reasoning text
and the prompts and completions themselves.  It specifies three
disclosure levels, the exact bytes the agent's Ed25519 signature
covers, how a trace is carried as a row of the CIRIS Epistemic Grammar
(CEG), when a trace exists at all, and the checks a consumer runs
before relying on one.  It records where the published specification
and the shipping implementation disagree.

--- middle

# Introduction

A record of what an AI agent did is more useful when a party other
than the agent and its operator can check it.  Several Internet-Drafts
record the action, the authority behind it, and digests of model
inputs ({{related}}).  This document specifies a record of the steps
in between: how the agent arrived at the action.

The record is the trace of the CIRIS agent {{CIRISAGENT}}.  The agent
is a made thing, held in stewardship by its operator; the trace is its
own account of one unit of work, which the agent calls a thought.  A
thought passes through a fixed pipeline ({{components}}): the thought
starts; context is gathered; three evaluators score the situation; an
identity check measures how independent the agent's sources were; an
action is selected; a verb-specific second pass may refine it;
conscience checks may veto it and send it back for reselection; and
the action is taken.  Every language-model call made along the way is
recorded as its own event, linked to the step that issued it.

A third party can check a trace for three reasons.  First, the trace
is the payload of a CEG statement signed by the agent's own key
({{signing}}), so any change after signing is detectable, including
the disclosure level and the link from each model call to the step
that made it.  Second, the identifier of the
agent in every trace is derived from that key ({{agent-id-hash}}), so a
verifier can bind the trace to the key without trusting a directory's
label.  Third, the trace is carried as a signed row of the CIRIS
Epistemic Grammar {{I-D.moore-scitt-ciris-ceg}}, whose admission rules
refuse a trace signed by any key but the agent's, a trace whose
fields break its pinned schema, and, at federation-tier admission, a
trace from a run on a mock model ({{carriage}}).

A trace is the agent's own account.  The signature proves who gave the
account and that it is unchanged, not that it is true.  Checking it
against records made by parties the agent does not control is outside
this document; {{I-D.moore-scitt-ciris-trace-context}} describes one
such check for model calls.

This document is one of three:

* {{I-D.moore-scitt-ciris-ceg}} specifies the signed row, its
  encoding, its names and references, and admission.  This document
  repeats none of them.

* This document specifies the trace: the `trace:complete:v1` payload.

* {{I-D.moore-scitt-ciris-trace-context}} specifies the per-call
  context manifest, carried as a member of this document's `LLM_CALL`
  event ({{llm-call}}).

## Sources and Their Status

The normative content of this document mirrors the agent's wire
contract {{FSD-TRACE}}, its JSON Schema {{TRACE-SCHEMA-JSON}}, the
per-level egress schema {{EGRESS-SCHEMA}} and the producing code, all
at CIRISAgent commit 59b7e5d, and the trace rules of the CIRIS
Constitution {{CC}} (Sections 3.1.5 and 5.3.2).  Where the published
wire contract and the code disagree, this document follows the code
and lists the disagreement in {{divergences}}.  Where the Constitution
states a rule the implementation does not yet meet, this document
states the rule and labels it as not implemented.

## Scope

In scope: the CompleteTrace object, its components and event shapes,
the disclosure levels, the signed bytes, carriage as a CEG row, the
lifecycle rule that decides when a trace exists, and validation by a
consumer.

Out of scope: how the agent transports traces to a collector (the
batch envelope and its correlation metadata), how a collector stores
them, and how scores are aggregated across traces.

# Conventions and Definitions

{::boilerplate bcp14-tagged}

The CDDL {{RFC8610}} in this document describes JSON {{RFC8259}}
values.  In it, `number` is any JSON number, and a `tstr` timestamp is
an RFC 3339 {{RFC3339}} date-time with a numeric offset.

Thought:
: One unit of agent work, from its start to the action it produces.
  A thought belongs to at most one task.

Trace:
: The signed record of one thought (a CompleteTrace, {{envelope}}).

Component:
: One entry of a trace's `components` array: one event of the
  pipeline ({{components}}).

Event type:
: The discriminator of a component's `data` shape ({{events}}).

Trace level:
: The disclosure profile a trace was produced under: `generic`,
  `detailed` or `full_traces` ({{levels}}).

Emitter:
: The software that builds, seals and signs traces on the agent's
  behalf, under the agent's key.

Consumer:
: Any party that verifies or relies on a trace: an admitting CEG node,
  a collector, an auditor.

Seal:
: The act of closing a trace when its terminal event arrives, then
  computing its signature.

# The CompleteTrace Envelope {#envelope}

A trace is a JSON object.  Its members are:

| Member | Type | Required | Meaning |
|---|---|---|---|
| `trace_id` | text | yes | Identifier of the trace, unique per agent |
| `thought_id` | text | yes | The thought the trace records |
| `task_id` | text or null | no | The task the thought serves, if any |
| `agent_id_hash` | text | yes | The agent's key-derived identifier ({{agent-id-hash}}) |
| `started_at` | timestamp | yes | When the first component arrived at the emitter |
| `completed_at` | timestamp | yes | When the terminal event arrived (the seal) |
| `trace_level` | text | yes | `generic`, `detailed` or `full_traces` ({{levels}}) |
| `trace_schema_version` | text | yes | The schema version stamped by the emitter ({{versions}}) |
| `deployment_profile` | object | yes | Six operator-declared labels ({{profile}}) |
| `components` | array | yes | The events, in receipt order ({{components}}) |
| `signature` | text | yes | Base64 Ed25519 signature, current form ({{current-form}}) |
| `signature_key_id` | text | yes | Identifier of the signing key |
{: title="CompleteTrace members"}

`signature` and `signature_key_id` belong to the current, per-trace
signature form ({{current-form}}), which is being replaced by the
signature of the CEG statement that carries the trace ({{signing}}).
In the current form they are outside the signed bytes and every other
member listed above is inside them.

Traces emitted by the reference implementation also carry
`pqc_key_id`, `pubkey_ml_dsa_65` and `signature_ml_dsa_65` (an ML-DSA-65
public key and signature, base64).  The wire contract does not
specify them, and the bytes the ML-DSA-65 signature covers are not
stated in any source available to the author ({{open}}).  A consumer
MUST NOT treat these members as part of the Ed25519 signed bytes and
MUST NOT rely on them until they are specified.

~~~ cddl
complete-trace = {
  trace_id: tstr,
  thought_id: tstr,
  ? task_id: tstr / null,
  agent_id_hash: tstr,          ; 16 lowercase hex characters
  started_at: tstr,             ; RFC 3339 date-time
  completed_at: tstr,           ; RFC 3339 date-time
  trace_level: trace-level,
  trace_schema_version: tstr,   ; "3.0.0" stamped today; not settled
  deployment_profile: deployment-profile,
  components: [+ trace-component],
  signature: tstr,              ; current form: base64 Ed25519
  signature_key_id: tstr,       ; current form
  ; Emitted, not yet specified (see Open Issues):
  ? pqc_key_id: tstr,
  ? pubkey_ml_dsa_65: tstr,
  ? signature_ml_dsa_65: tstr,
}

trace-level = "generic" / "detailed" / "full_traces"

deployment-profile = {
  agent_role: tstr,
  agent_template: tstr,
  deployment_domain: deployment-domain,
  deployment_type: tstr,
  deployment_region: tstr / null,
  deployment_trust_mode: "sovereign" / "limited_trust"
                       / "federated_peer",
}

deployment-domain = "healthcare" / "legal" / "financial"
  / "employment" / "education" / "critical_infra" / "biometric"
  / "law_enforcement" / "personal_assistant" / "moderation"
  / "research_scientific" / "manufacturing_industrial" / "general"

trace-component = {
  agent_id_hash: tstr,
  component_type: tstr,
  event_type: tstr,
  timestamp: tstr,
  data: { * tstr => any },
}
~~~

## The Agent Identifier {#agent-id-hash}

`agent_id_hash` is the first 16 hexadecimal characters, lowercase, of
the SHA-256 {{RFC6234}} digest of the raw public key bytes of the
agent's Ed25519 signing key:

    agent_id_hash = lowercase_hex(SHA-256(public_key))[0..16]

An emitter MUST derive it exactly so, from the key that signs the
trace.  The same value appears on the envelope and on every
component, and the two MUST be equal.

Because the derivation is from the signing key, a consumer that holds
the public key can recompute the identifier and check it
({{validation}}).  The identifier is pseudonymous, not anonymous: any
party holding the public key can compute it.  It is 64 bits long;
{{security}} discusses collisions.

The reference implementation falls back to hashing the agent's name,
or to the literal `unknown`, when its signing engine is unavailable
(test environments).  A trace carrying such a value fails the check
above and MUST NOT be admitted at federation tier ({{divergences}}).
CIRISAgent#1370 (not yet merged) removes the fallback: without a
signing engine the component is refused.

## The Trace Identifier

`trace_id` identifies the trace within the agent's traces.  It is
unique per agent by convention only; consumers MUST key on the pair
(`agent_id_hash`, `trace_id`), never on `trace_id` alone, because an
agent controls its own `trace_id` values.

The wire contract gives the format `trace-<thought_id>-<YYYYMMDDHHMMSS>`
and the JSON Schema requires the prefix `trace-`.  The traces the
implementation emits carry the thought identifier itself as
`trace_id` ({{example}}).  A consumer MUST NOT parse `trace_id`
({{divergences}}).

## The Deployment Profile {#profile}

`deployment_profile` carries six labels the operator declares about
the deployment.  They are inside the signed bytes, so an intermediary
cannot relabel a trace.

agent_role:
: A free-form lowercase role name.

agent_template:
: The identifier of the agent template.

deployment_domain:
: Exactly one value from the closed set in the CDDL above.  `general`
  is the value for multi-domain assistants.

deployment_type:
: An operator-declared label.  Not a closed set in practice: operator
  values (for example `personal`, `business`, `research`,
  `nonprofit`), the original lifecycle values (`development`, `test`,
  `staging`, `production`, `research`, `decommissioned`) and the run
  kind markers `mock`, `qa` and `battery` all occur in it.  A consumer
  MUST NOT treat it as an enumeration.  The run kind belongs in its
  own member ({{run-kind}}).

deployment_region:
: An ISO 3166-1 alpha-2 country code, `global`, or null for "not
  disclosed".  The member is present even when null.

deployment_trust_mode:
: `sovereign` (no federation participation), `limited_trust`
  (partial), or `federated_peer` (full).  This is the agent's declared
  intent, not a finding about it.

An agent with no operator configuration emits the defaults
`deployment_domain = "general"`, `deployment_type = "production"`,
`deployment_trust_mode = "sovereign"`, `deployment_region = null`,
`agent_role` = the lowercased agent name, and `agent_template` =
`<agent name>-default-unspecified`.  These are well-formed and a
consumer MUST accept them.

## Schema Versions {#versions}

The shape of a trace at each trace level is fixed by the agent's
per-level field schema, the pinned artifact `trace_format_v{n}.json`
({{CC}}, Section 3.1.5; {{levels}}).  This document does not fix a
value of `trace_schema_version`.

Today the emitter stamps `trace_schema_version` `3.0.0`, and the
verifier of the current signature form selects its canonicalizer by
that string ({{current-form}}).  The version survives the move to
statement signatures: the storage engine's release 62.0 accepts
`3.1.0`, which names the `context_manifest` member, and the server's
release 0.6 stamps it.  The trace format remains named by the row
family's leaf `trace:complete:v1`; an additive member needs no new
leaf.  Neither release had shipped at the time of writing ({{open}}).

# Components and the Pipeline {#components}

Each component is one event of the pipeline:

agent_id_hash:
: Equal to the envelope's ({{agent-id-hash}}).

component_type:
: The pipeline stage, fixed by `event_type` (table below).

event_type:
: The discriminator of `data` ({{events}}).

timestamp:
: The emitting step's wall-clock time.

data:
: The event's members ({{events}}), filtered to the trace level
  ({{levels}}), with empty values removed ({{strip}}).

| `event_type` | `component_type` | Per thought |
|---|---|---|
| `THOUGHT_START` | `observation` | once |
| `SNAPSHOT_AND_CONTEXT` | `context` | once |
| `DMA_RESULTS` | `rationale` | once |
| `IDMA_RESULT` | `rationale` | once |
| `ASPDMA_RESULT` | `rationale` | once per selection attempt |
| `TSASPDMA_RESULT` (deprecated) | `rationale` | at most once |
| `VERB_SECOND_PASS_RESULT` | `verb_second_pass` | at most once |
| `CONSCIENCE_RESULT` | `conscience` | once per check pass |
| `ACTION_RESULT` | `action` | exactly once; seals the trace |
| `LLM_CALL` | `llm_call` | once per model call |
{: title="Event types and component types"}

The mapping is fixed.  A consumer MUST reject a component whose
`component_type` does not match its `event_type`, and MUST reject an
`event_type` outside the set defined for the trace's schema version:
silent acceptance of an unknown type would let a new payload pass
without review.

The pipeline order of the steps is:

1. `THOUGHT_START`.
2. `SNAPSHOT_AND_CONTEXT`.
3. `DMA_RESULTS`: three evaluators run in parallel.
4. `IDMA_RESULT`.
5. `ASPDMA_RESULT`: an action is selected.
6. `VERB_SECOND_PASS_RESULT`, when the selected verb has a second
   pass.
7. `CONSCIENCE_RESULT`.  If a check overrides the selection, the
   pipeline returns to step 5 with `is_recursive` true; steps 5 to 7
   repeat until the selection passes or an override action is taken.
8. `ACTION_RESULT`.

`LLM_CALL` events occur throughout, each naming the step that issued
it ({{llm-call}}).

The `components` array is in the order the emitter received the
events, which is not the pipeline order and not timestamp order: in
the example of {{example}}, a model call issued for action selection
precedes the `DMA_RESULTS` component, and timestamps are not
monotonic.  A consumer MUST NOT infer a causal link from array
position.  The causal links are `attempt_index` ({{attempt-index}})
and the parent link of each `LLM_CALL`.  The array order is
nonetheless inside the signed bytes and MUST be preserved.

## Empty Values {#strip}

Before signing, the emitter removes from `data`, recursively, every
member whose value is null, the empty string, the empty array or the
empty object.  The values `0` and `false` are kept.  A consumer MUST
read an absent member as "not emitted at this level or for this
event", never as null.

Whether a container left empty by this removal is itself removed is
not stated by the sources ({{open}}).

# Event Types {#events}

Each subsection gives an event's `data` members.  The comment after
each member names the lowest trace level at which it is carried
(`G`, `D` or `F`).  The levels are those of the implementation's
egress schema {{EGRESS-SCHEMA}}; where the wire contract assigns a
different level, {{divergences}} says so.  Every component's `data`
also carries `attempt_index` ({{attempt-index}}), inserted by the
emitter at every level.  In CIRISAgent#1370 (not yet merged) every
component's `data` also carries `run_kind` ({{run-kind}}) and, when
the emitter's filter altered it, `egress_alterations` ({{levels}}).
All members are optional unless stated: what
is absent was not emitted.

## THOUGHT_START

The thought's metadata.

~~~ cddl
thought-start = {
  attempt_index: uint,
  ? round_number: uint,             ; G
  ? thought_depth: uint,            ; G
  ? task_priority: int,             ; G
  ? updated_info_available: bool,   ; G
  ? requires_human_input: bool,     ; G
  ? thought_type: tstr,             ; G  e.g. "standard"
  ? thought_status: tstr,           ; D
  ? parent_thought_id: tstr,        ; D
  ? channel_id: tstr,               ; D
  ? source_adapter: tstr,           ; D
  ? task_description: tstr,         ; F
  ? initial_context: any,           ; F
  ? thought_content: tstr,          ; F  at most 500 characters
}
~~~

## SNAPSHOT_AND_CONTEXT

The agent's state when the thought was processed, including the
integrity attestation of the agent's own binary, environment and key.
`attestation_level` runs from 0 (no attestation) to 5, each level
requiring the lower ones.  The `*_ok` booleans are independent checks
and a consumer SHOULD treat them separately rather than collapse them
into the level.  `attestation_context` is a human-readable summary of
the same facts written by the agent, not by a model; it is the one
text member carried at `generic`, and it is not authoritative: the
booleans are.

~~~ cddl
snapshot-and-context = {
  attempt_index: uint,
  ? agent_name: tstr,               ; G
  ? cognitive_state: tstr,          ; G
  ? attestation_context: tstr,      ; G  at most 1024 characters
  ? attestation_level: 0..5,        ; G
  ? attestation_status: tstr,       ; G
  ? disclosure_severity: "info" / "warning" / "critical", ; G
  ? binary_ok: bool,                ; G
  ? env_ok: bool,                   ; G
  ? registry_ok: bool,              ; G
  ? file_integrity_ok: bool,        ; G
  ? audit_ok: bool,                 ; G
  ? play_integrity_ok: bool,        ; G
  ? hardware_backed: bool,          ; G
  ? memory_count: uint,             ; G
  ? context_tokens: uint,           ; G
  ? active_services: [* tstr],      ; D
  ? context_sources: [* tstr],      ; D
  ? service_health: { * tstr => bool },      ; D
  ? agent_version: tstr,            ; D
  ? circuit_breaker_status: { * tstr => tstr }, ; D
  ? key_status: tstr,               ; D
  ? key_id: tstr,                   ; D
  ? ed25519_fingerprint: tstr,      ; D
  ? key_storage_mode: tstr,         ; D
  ? hardware_type: tstr,            ; D
  ? verify_version: tstr,           ; D
  ? system_snapshot: any,           ; F
  ? gathered_context: any,          ; F
  ? relevant_memories: any,         ; F
  ? conversation_history: any,      ; F
}
~~~

## DMA_RESULTS

The three evaluators that run in parallel: common sense (CSDMA),
domain-specific (DSDMA) and principled (PDMA).  Scores are in [0, 1].
When an evaluator is re-run on a low score, only the surviving result
appears here; every run appears as an `LLM_CALL`.

~~~ cddl
dma-results = {
  attempt_index: uint,
  ? csdma: {
    ? plausibility_score: number,   ; G
    ? flags: [* tstr],              ; D
    ? reasoning: tstr,              ; F
    ? prompt_used: tstr,            ; F
  },
  ? dsdma: {
    ? domain_alignment: number,     ; G
    ? domain: tstr,                 ; D
    ? flags: [* tstr],              ; D
    ? reasoning: tstr,              ; F
    ? prompt_used: tstr,            ; F
  },
  ? pdma: {
    ? has_conflicts: bool,          ; G
    ? stakeholders: [* tstr],       ; D
    ? conflicts: tstr,              ; D  at most 500 characters
    ? alignment_check: tstr,        ; D  at most 500 characters
    ? reasoning: tstr,              ; F
    ? prompt_used: tstr,            ; F
  },
  ? csdma_plausibility_score: number,  ; G  flat copy
  ? dsdma_domain_alignment: number,    ; G  flat copy
  ? dsdma_domain: tstr,                ; D  flat copy
  ? combined_analysis: any,            ; F
}
~~~

## IDMA_RESULT

The identity check, which estimates how many independent sources the
selection rests on.  `k_eff` is the effective source count
k/(1 + rho(k - 1)) for k sources with mean pairwise correlation rho;
`phase` is one of `chaos`, `healthy` or `rigidity`.  Several members
are plain-language aliases of others (`effective_source_count` of
`k_eff`, `source_overlap` of `correlation_risk`, `reasoning_is_fragile`
of `fragility_flag`, `reasoning_state` of `phase`) and carry the same
value.  The values are the model's own estimate; this document makes
no claim about their accuracy.

~~~ cddl
idma-result = {
  attempt_index: uint,
  ? k_eff: number,                  ; G
  ? effective_source_count: number, ; G
  ? correlation_risk: number,       ; G
  ? source_overlap: number,         ; G
  ? fragility_flag: bool,           ; G
  ? reasoning_is_fragile: bool,     ; G
  ? phase: tstr,                    ; G
  ? reasoning_state: tstr,          ; G
  ? idma_k_eff: number,             ; G  flat copy
  ? idma_correlation_risk: number,  ; G  flat copy
  ? idma_fragility_flag: bool,      ; G  flat copy
  ? idma_phase: tstr,               ; G  flat copy
  ? k_raw: uint,                    ; D
  ? rho_mean: number,               ; D
  ? sources_identified: [* tstr],   ; D
  ? source_independence_scores: [* number], ; D
  * tstr => any,                    ; further D members, see text
  ? reasoning: tstr,                ; F
  ? prompt_used: tstr,              ; F
}
~~~

The further `detailed` members are listed in {{EGRESS-SCHEMA}}
(`_IDMA_DETAILED`); they are numbers, integers, short lists of labels
and two capped text members.

## ASPDMA_RESULT

One action selection.  The first carries `is_recursive` false and
`attempt_index` 0; each reselection after a conscience override
carries `is_recursive` true and the next `attempt_index`.

~~~ cddl
aspdma-result = {
  attempt_index: uint,
  ? selected_action: tstr,          ; G
  ? selection_confidence: number,   ; G
  ? is_recursive: bool,             ; G
  ? alternatives_considered: [* tstr], ; D
  ? evaluation_time_ms: number,     ; D
  ? action_rationale: tstr,         ; F
  ? reasoning_summary: tstr,        ; F
  ? action_parameters: any,         ; F
  ? aspdma_prompt: tstr,            ; F
  ? aspdma_system_prompt: tstr,     ; F
  ? raw_llm_response: tstr,         ; F  at most 1000 characters
}
~~~

The spelling of `selected_action` is not stable across sources
({{divergences}}); CIRISAgent#1370 (not yet merged) emits the
action's value.  A consumer SHOULD compare it case-insensitively
after removing a `HandlerActionType.` prefix, since traces from
earlier releases carry one.

## TSASPDMA_RESULT (Deprecated)

The earlier form of the tool second pass, still emitted beside
`VERB_SECOND_PASS_RESULT` during a transition.  A consumer SHOULD
prefer `VERB_SECOND_PASS_RESULT`.

~~~ cddl
tsaspdma-result = {
  attempt_index: uint,
  ? original_tool_name: tstr,       ; G
  ? final_action: tstr,             ; G
  ? final_tool_name: tstr,          ; G
  ? gotchas_acknowledged: [* tstr], ; D
  ? tool_description: tstr,         ; D  at most 500 characters
  ? original_parameters: any,       ; F
  ? final_parameters: any,          ; F
  ? aspdma_rationale: tstr,         ; F
  ? tsaspdma_rationale: tstr,       ; F
  ? tsaspdma_prompt: tstr,          ; F
}
~~~

## VERB_SECOND_PASS_RESULT

A second pass for a verb that has one: today `tool` and `defer`.
`verb` is the discriminator of `verb_specific_data` and is a closed
set at any schema version; a new verb extends it before it is
emitted.  A consumer MUST NOT reject an event because it does not
recognise the verb, and MUST treat `verb_specific_data` as opaque
apart from the members it recognises.

~~~ cddl
verb-second-pass-result = {
  attempt_index: uint,
  ? verb: tstr,                     ; G  "tool" / "defer"
  ? original_action: tstr,          ; G
  ? final_action: tstr,             ; G
  ? refused_without_wa_approval: bool, ; G
  ? verb_specific_data: {
    ; defer
    ? rights_basis: [* tstr],       ; G
    ? primary_need_category: tstr,  ; G
    ? secondary_need_categories: [* tstr], ; G
    ? domain_hint: tstr,            ; G
    ? operational_reason: tstr,     ; G
    ? defer_reason: tstr,           ; D  at most 500 characters
    ? defer_until: tstr,            ; D  timestamp
    ; tool
    ? original_tool_name: tstr,     ; G
    ? final_tool_name: tstr,        ; G
    ? original_parameters: any,     ; F
    ? final_parameters: any,        ; F
    ; memorize
    ? original_node_id: tstr,       ; D
    ? final_node_id: tstr,          ; D
    ? node_id_corrected: bool,      ; G
    ? refused_without_wa_approval: bool, ; G
  },
  ? original_reasoning: tstr,       ; F
  ? final_reasoning: tstr,          ; F
  ? second_pass_prompt: tstr,       ; F
  ? second_pass_system_prompt: tstr, ; F
}
~~~

## CONSCIENCE_RESULT

One pass of the checks that can veto a selection: entropy, coherence,
optimization veto and epistemic humility, plus guards on thought depth
and on updated information.  When a check overrides the selection,
`conscience_passed` is false, `action_was_overridden` is true, and a
new `ASPDMA_RESULT` and `CONSCIENCE_RESULT` follow with the next
`attempt_index`.  A consumer MUST keep every pass: the sequence of
overrides is the record of how the action was reached.

`ethical_faculties_skipped` reports whether the four checks were run.
The checks run only for some actions; for others their members are
absent ({{example}}).

~~~ cddl
conscience-result = {
  attempt_index: uint,
  conscience_passed: bool,          ; G  required
  ? action_was_overridden: bool,    ; G
  ? ethical_faculties_skipped: bool, ; G
  ? is_recursive: bool,             ; G
  ? updated_status_detected: bool,  ; G
  ? thought_depth_triggered: bool,  ; G
  ? thought_depth_current: int,     ; G
  ? thought_depth_max: int,         ; G
  ? entropy_level: number,          ; G
  ? coherence_level: number,        ; G
  ? entropy_passed: bool,           ; G
  ? entropy_score: number,          ; G
  ? entropy_threshold: number,      ; G
  ? coherence_passed: bool,         ; G
  ? coherence_score: number,        ; G
  ? coherence_threshold: number,    ; G
  ? optimization_veto_passed: bool, ; G
  ? optimization_veto_entropy_ratio: number, ; G
  ? epistemic_humility_passed: bool, ; G
  ? epistemic_humility_certainty: number, ; G
  ? final_action: tstr,             ; D
  ? conscience_override_reason: tstr, ; D  at most 500 characters
  ? entropy_reason: tstr,           ; D  at most 500 characters
  ? coherence_reason: tstr,         ; D  at most 500 characters
  ? optimization_veto_decision: tstr, ; D
  ? optimization_veto_affected_values: [* tstr], ; D
  ? epistemic_humility_uncertainties: [* tstr],  ; D
  ? epistemic_humility_recommendation: tstr,     ; D
  ? epistemic_data: any,            ; F
  ? updated_status_content: tstr,   ; F
  ? optimization_veto_justification: tstr,    ; F
  ? epistemic_humility_justification: tstr,   ; F
}
~~~

## ACTION_RESULT

The action taken, its outcome and the thought's totals.  This is the
terminal event: it seals the trace ({{anchor}}).  It anchors the
action to the agent's own audit log by sequence number and entry
digest.

~~~ cddl
action-result = {
  attempt_index: uint,
  ? execution_success: bool,        ; G
  ? success: bool,                  ; G
  ? has_execution_error: bool,      ; G
  ? has_positive_moment: bool,      ; G
  ? execution_time_ms: number,      ; G
  ? tokens_input: uint,             ; G
  ? tokens_output: uint,            ; G
  ? tokens_total: uint,             ; G
  ? cost_cents: number,             ; G
  ? carbon_grams: number,           ; G
  ? energy_mwh: number,             ; G
  ? llm_calls: uint,                ; G
  ? audit_sequence_number: int,     ; G
  ? audit_entry_hash: tstr,         ; G
  ? action_executed: tstr,          ; G
  ? follow_up_thought_id: tstr,     ; D
  ? audit_entry_id: tstr,           ; D
  ? models_used: [* tstr],          ; D
  ? api_bases_used: [* tstr],       ; D
  ? execution_error: tstr,          ; D  at most 500 characters
  ? audit_signature: tstr,          ; D
  ? action_parameters: any,         ; F
  ? positive_moment: tstr,          ; F  at most 500 characters
}
~~~

## LLM_CALL {#llm-call}

One call to a language model provider, successful or not.  Every
call the pipeline makes is recorded, including retries.

`parent_event_type` and `parent_attempt_index` name the pipeline
event that issued the call; together with the trace's
(`agent_id_hash`, `trace_id`, `thought_id`) they identify that event
uniquely.  Because they are in the signed bytes, nobody can move a
call to a different parent without breaking the signature.  An
emitter MUST carry both whenever the issuing step is known.

`status` is one of `ok`, `timeout`, `rate_limited`,
`model_not_available`, `instructor_retry` or `other_error`.
`error_class` names the exception on failure.  `attempt_count` counts
re-prompts after an unparseable response (1 is the first try);
`retry_count` counts provider-level retries (0 is the first attempt).

`prompt_hash` is the SHA-256 of the messages sent, as lowercase hex.
It is the `messages_sha256` of {{I-D.moore-scitt-ciris-trace-context}}.

An `LLM_CALL` component MAY carry a member `context_manifest` at trace
level `detailed` and above: the per-call context manifest specified by
{{I-D.moore-scitt-ciris-trace-context}}, which describes each piece of
text placed into the call by kind, provenance, trust, lifetime and
language.  The verified sender's `subject_id` in the manifest depends
on the level:

* At `detailed` it is HMAC-SHA256 {{RFC2104}} of the identifier string
  under a per-agent secret that the agent holds and never discloses,
  truncated to 16 hexadecimal characters, with `subject_id_form`
  `hmac_sha256_16`.  Where the secret is unavailable the identifier is
  omitted, never sent as it is.

* At `full_traces` it is the identifier as verified, with
  `subject_id_form` `raw`.

* At `generic` the `context_manifest` member is omitted.

The keyed form is used because user identifiers are low-entropy: an
unkeyed digest could be reversed by trying candidates, and would link
one person across every agent that saw them.  The keyed value is
stable within one agent and cannot be linked across agents.

The member is additive: event data stays open to further members, so a
trace carrying it is admitted under the current `3.0.0`.  It is
implemented in CIRISAgent pull request 1370, not yet merged, and is
not in any emitted trace.  It is named in the per-level schema at
`3.1.0`, accepted by the storage engine's release 62.0 and stamped by
the server's release 0.6, neither shipped at the time of writing
({{open}}).

~~~ cddl
llm-call = {
  attempt_index: uint,
  ? handler_name: tstr,             ; G  required by the contract
  ? service_name: tstr,             ; G  required by the contract
  ? model: tstr,                    ; G
  ? base_url: tstr,                 ; D
  ? response_model: tstr,           ; G
  ? duration_ms: number,            ; G  required, >= 0
  ? prompt_tokens: uint,            ; G
  ? completion_tokens: uint,        ; G
  ? prompt_bytes: uint,             ; G
  ? completion_bytes: uint,         ; G
  ? cost_usd: number,               ; G
  ? sent_temperature: number,       ; G
  ? sent_seed: int,                 ; G
  ? sent_max_tokens: uint,          ; G
  ? served_by: tstr,                ; G
  ? served_model: tstr,             ; G
  ? status: llm-status,             ; G  required by the contract
  ? error_class: tstr,              ; G  on failure
  ? attempt_count: uint,            ; G
  ? retry_count: uint,              ; G
  ? parent_event_type: tstr,        ; G
  ? parent_attempt_index: uint,     ; G
  ? prompt_hash: tstr,              ; D  64 lowercase hex
  ? context_manifest: any,          ; D  PR 1370, not merged
  ? prompt: tstr,                   ; F
  ? response_text: tstr,            ; F
}

llm-status = "ok" / "timeout" / "rate_limited"
  / "model_not_available" / "instructor_retry" / "other_error"
~~~

## Other Event Types

The implementation's event taxonomy has five more types, for a
credit and deferral system: `DEFERRAL_ROUTED`, `DEFERRAL_RECEIVED`,
`DEFERRAL_RESOLVED`, `GRATITUDE_SIGNALED` and `CREDIT_GENERATED`, each
with a component type of the same name in lowercase.  They are not in
the wire contract, the reference implementation does not capture them
into traces by default, and this document does not specify them
({{divergences}}).  A consumer of a trace that contains one
MUST reject the trace unless it implements their shapes.

# attempt_index {#attempt-index}

Every component carries `attempt_index` inside `data`.  It is a
counter per (`thought_id`, `event_type`), starting at 0 and increasing
by one with each event of that type in receipt order.  For the types
that occur once per thought it is always 0.  For `ASPDMA_RESULT`,
`CONSCIENCE_RESULT` and `LLM_CALL` it orders the repetitions.

It exists because timestamps of concurrent events can be equal.  A
consumer that stores components MUST key them on

    (agent_id_hash, trace_id, thought_id, event_type,
     attempt_index, timestamp)

and MUST NOT drop `timestamp` from the key: it guards against a
counting defect collapsing two events into one.  It MUST NOT drop
`agent_id_hash`, which prevents one agent from claiming a key that
another agent's trace will need.

# Trace Levels as a Disclosure Profile {#levels}

The trace level is chosen by the operator for each emitter and is the
same for every component of a trace.  It is in the signed bytes, so a
trace re-signed at another level has another signature, and a
consumer cannot be misled about which profile it holds.

| Level | Carries | Does not carry |
|---|---|---|
| `generic` | Scores, booleans, counts, sizes, durations, costs, closed-vocabulary tokens, model and handler names, the attestation summary | Free text from a model or a person, reasoning, prompts, prompt digests, channel and key identifiers |
| `detailed` | Generic, plus bounded lists of labels, key identifiers, channel identifiers, short reason fields (at most 500 characters), prompt digests, provider endpoints, and the context manifest with keyed sender identifiers | The reasoning chain, prompts and completions |
| `full_traces` | Detailed, plus reasoning text, prompts and completions verbatim, tool parameters, and full context snapshots, each bounded | Nothing by design |
{: title="Trace levels"}

The default level is `generic`.  The implementation lowers a
configured `full_traces` to `detailed` when the substrate cannot scrub
personal data from text.

The per-level field schema, which says which members each level
carries, their types, and their string and list bounds, is the agent's
artifact.  {{CC}} (Section 3.1.5) requires that it be pinned by hash in
the Constitution's evidence pins and vendored by tag by every substrate
that admits traces, so that emitter and admitter derive from one
artifact.  The bounds of the implementation's egress schema
{{EGRESS-SCHEMA}} are part of its contract: tokens at most 64
characters, identifiers and labels at most 128, URLs at most 256,
reasons at most 500, the attestation summary at most 1024, free text
at most 65536, lists at most 32 items, maps at most 64, and opaque
JSON at most depth 8, 256 items and 8192 characters per string.

A trace that violates the pinned schema MUST be refused, never
truncated, with the refusal token `trace_field_shape_violation`
({{CC}}, Section 3.1.5): a truncated row is a silently altered signed
record.  The rule binds the admitter.  The implementation's emitter
filters each component before signing instead: it drops a member the
level does not allow or whose type does not fit, truncates over-long
text and cuts over-long lists, and logs and counts each violation
without its value.  Because this happens before signing, the signed
trace is what the agent attests to.  At commit 59b7e5d the alteration
is silent in the signed bytes.

In CIRISAgent#1370 (not yet merged) the emitter records each
alteration in the component's signed `data`, as `egress_alterations`:
a list of at most 64 marks, with a count of any beyond that.  A mark
gives the member's `path`, the `kind` of alteration (`truncated`,
`dropped_wrong_type` or `dropped_not_in_schema`), and the
`original_length`; a `truncated` mark also gives `sha256`, the SHA-256
digest of the original value.  A dropped value gets no digest: it was
content in the wrong place, and a digest of a short value can be
confirmed by guessing.  A member above the trace level is not an
alteration and is not marked.  The emitter discards any
`egress_alterations` a producer supplies before filtering, so the
marks are the filter's own.  With the marks, an emitter's cut is
declared in what the agent signs rather than silent; the admitter's
rule is unchanged.  Whether the Constitution's text should say so, and
how the emitter's and admitter's schemas are bound by one pinned hash,
are open ({{divergences}}).

~~~ cddl
egress-alteration = {
  path: tstr,
  kind: "truncated" / "dropped_wrong_type" / "dropped_not_in_schema",
  original_length: uint,
  ? sha256: tstr,                  ; truncated only
}
~~~

# Signatures {#signing}

## The Normative Signature {#statement-sig}

The signature of a trace is the signature of the CEG statement that
carries it ({{carriage}}).  The signed object, its composite
signature, its keys and its admission are those of
{{I-D.moore-scitt-ciris-ceg}}; this document repeats none of them.
The signer is the agent: {{CC}} (Section 3.1.5) and its key-role
contract (`manifests/key_roles.json`, family `trace:{form}:{version}`,
signer kind `agent`) give a trace's attestation and its withdrawal to
the agent alone, and an admitter verifies the statement at the door.
A node, host or person key MUST NOT sign a trace.

Because the statement signature covers the whole payload, it covers
everything the current form covers ({{current-form}}): the trace
level, the deployment profile, every component and its
`attempt_index`, and every parent link of a model call.

No released implementation yet emits a trace as such a statement.
The transition is in {{open}}.

## The Current Form: Per-Trace Ed25519 {#current-form}

What ships today is a separate Ed25519 signature carried inside the
trace, over canonical bytes of the trace.  It is described so that
traces signed this way can be verified.  It is being replaced by the
statement signature above: the storage engine's version 62 (the
server's 0.6 release, not shipped at the time of writing) removes the
earlier-form trace verification and verifies traces as agent-signed
statements.  An implementer SHOULD NOT build a new emitter or
verifier on this form alone.

### What Is Signed

With `trace_schema_version` `3.0.0`, the signed bytes are the JCS
canonicalization {{RFC8785}} of the following JSON object, built from
the trace:

    {
      "trace_id":             trace.trace_id,
      "thought_id":           trace.thought_id,
      "task_id":              trace.task_id,
      "agent_id_hash":        trace.agent_id_hash,
      "started_at":           trace.started_at,
      "completed_at":         trace.completed_at,
      "trace_level":          trace.trace_level,
      "trace_schema_version": trace.trace_schema_version,
      "deployment_profile": {
        "agent_role", "agent_template", "deployment_domain",
        "deployment_type", "deployment_region",
        "deployment_trust_mode"     (each from the trace)
      },
      "components": [
        for each c in trace.components, in array order:
        { "agent_id_hash":  c.agent_id_hash,
          "component_type": c.component_type,
          "data":           strip_empty(c.data),
          "event_type":     c.event_type,
          "timestamp":      c.timestamp }
      ]
    }

Exactly these members are present, and no others: an unknown member
of the envelope or of a component is not signed, and a verifier
MUST NOT add it to the canonical object.  `strip_empty` is the
removal of {{strip}}.  `attempt_index` is inside `data` and therefore
signed.

The signature is pure Ed25519 {{RFC8032}} over the signed bytes, with
the agent's signing key.  `signature` is its 64 bytes in base64 with
padding ({{RFC4648}}, Section 4).

### Canonical Shapes by Version

The verifier of this form selects the canonical shape and the
canonicalizer from `trace_schema_version`, which is itself inside the
signed bytes:

| Version | Envelope members signed | Component members signed | Canonicalizer |
|---|---|---|---|
| `2.7.0` | 9, no `deployment_profile` | 4, no `agent_id_hash` | legacy |
| `2.7.9` | 10 | 5 | legacy |
| `3.0.0` | 10 | 5 | JCS {{RFC8785}} |
{: title="Canonical shapes of the current form"}

The legacy canonicalizer is Python's `json.dumps(obj, sort_keys=True,
separators=(",", ":"))` with its default ASCII escaping.  It agrees
with JCS on traces whose text is all ASCII and differs on any other
text.

A verifier MUST select the shape and canonicalizer from
`trace_schema_version` alone, and MUST NOT try another shape when
verification fails under the selected one.  A verifier MUST reject a
version it does not support.  At `2.7.0` a verifier MUST ignore any
`deployment_profile` on the envelope and any `agent_id_hash` on a
component; neither is signed at that version.

### Keys

The key of this form is the agent's own signing key, the same key
that signs the agent's audit entries.

`signature_key_id` names the key for lookup.  How a consumer obtains
the public key for a `signature_key_id` is not specified by the
current sources: the registration path of the wire contract has been
retired in the implementation ({{open}}).  Whatever the lookup, the
consumer checks the key against `agent_id_hash` ({{validation}}).

### Verification

A verifier of this form:

1. obtains the public key named by `signature_key_id`;
2. checks that `agent_id_hash` equals the first 16 lowercase
   hexadecimal characters of SHA-256 of that key;
3. selects the shape and canonicalizer from `trace_schema_version`,
   rejecting an unsupported version;
4. builds the canonical object from the received trace and
   canonicalizes it;
5. verifies the Ed25519 signature over those bytes; and
6. rejects the trace on any failure.

A consumer MUST verify before it stores a trace as a record.

# Carriage as a CEG Row {#carriage}

## The trace:complete:v1 Row

A trace is carried as a CEG row {{I-D.moore-scitt-ciris-ceg}} of the
family `trace:{form}:{version}`; the canonical leaf is
`trace:complete:v1`, which carries the trace after scrubbing.  The
signed object, its composite signature, its names, references,
receipts and admission are those of {{I-D.moore-scitt-ciris-ceg}}.
The statement's signature is the trace's signature ({{signing}}).

{{CC}} (Section 3.1.5) states these rules for the row:

1. **Identifiers.**  The envelope carries a non-empty `trace_id` and a
   non-empty `agent_id_hash`, equal to those of the trace.

2. **Exactly one body.**  The envelope carries exactly one of an
   inline `trace` (the CompleteTrace), within the 1 MiB payload bound
   of {{CC}} (Section 2.6.1.6), or a `manifest` object of schema
   `trace_manifest:v1` naming it ({{oversize}}).  This trace manifest
   is not the per-call context manifest of
   {{I-D.moore-scitt-ciris-trace-context}}.

3. **Shape and provenance.**  Admission validates that the row
   parses, and nothing more: an admitted `trace:*` row is guaranteed
   parseable, and that is all admission claims.  Provenance rides the
   producer's signature, verified at promotion to federation tier
   ({{CC}}, Section 5.3.2.6) and again by consumers.  Neither
   substitutes for the other.

4. **Field schema.**  The per-level field schema is the agent's
   artifact, `trace_format_v{n}.json`, pinned by hash in the
   Constitution's evidence pins and vendored by tag by every substrate
   that admits traces.  A row that violates it is refused, never
   truncated, with `trace_field_shape_violation` ({{levels}}).

5. **Run kind.**  The trace carries `run_kind` in the signed bytes
   ({{run-kind}}).  A `mock` row is refused at federation-tier
   admission only, with `trace_run_kind_mock`; the three production
   values are admitted alike.

6. **Signer and withdrawal.**  The family is reserved ({{CC}},
   Section 3.4.5).  Its attestation and its withdrawal are the
   agent's own, signer kind `agent`; an admitter MUST refuse a
   `trace:*` row signed by any other key.

7. **Erasure.**  Only the signer's withdrawal, or after retirement the
   custodian its retirement row names, erases a trace.  An owner MAY
   stop its own node holding a trace's bytes; that reaches no copy
   another party holds under a consent grant.

~~~ cddl
trace-row-payload = {
  dimension: "trace:complete:v1",
  trace_id: tstr,                  ; non-empty
  agent_id_hash: tstr,             ; non-empty
  run_kind: run-kind,              ; CC 3.1.5; see {{run-kind}}
  ( trace: { * tstr => any }       ; a CompleteTrace
  // manifest: trace-manifest )
  * tstr => any,                   ; members every CEG row carries
}

run-kind = "production" / "prod-personal" / "prod-managed"
  / "qa" / "battery" / "mock"

trace-manifest = {
  schema: "trace_manifest:v1",
  content_hash: tstr,              ; "sha256:" then lowercase hex
  byte_len: uint,                  ; positive
  component_count: uint,
}
~~~

## The Run Kind {#run-kind}

Every trace row names the kind of run that produced it, in the signed
bytes, from the closed set `production`, `prod-personal`,
`prod-managed`, `qa`, `battery` and `mock` ({{CC}}, Section 3.1.5).
`prod-personal` and `prod-managed` mark a production run on a personal
install or a managed deployment; `production` remains valid for an
emitter that does not distinguish them, and admission treats the
three alike.  `qa` marks a test-harness run and `battery` an
evaluation battery, both of which may use a real model.  `mock` marks
a run on a mock model.

A federation-tier admitter MUST refuse a `mock` row with
`trace_run_kind_mock`: a mock model's output attests nothing about any
agent.  The refusal is at federation tier only: a node MAY hold its own
`mock` rows locally, for tests.

**Implementation.**  At commit 59b7e5d the implementation carries the
run kind inside `deployment_profile.deployment_type`, which is signed,
as one of `mock`, `qa` or `battery` overriding the operator's value,
with no marker for a production run and no `prod-personal` or
`prod-managed`.  It keeps `mock` traces out of its federation store at
the source.

In CIRISAgent#1370 (not yet merged) every component's signed `data`
carries `run_kind` from the six-value set.  A test-harness or mock
setting wins; otherwise an operator's `CIRIS_DEPLOYMENT_KIND` of
`managed` or `personal`; otherwise `prod-managed` under the agent's
deployment manager and `prod-personal` elsewhere.  `deployment_type`
is unchanged.  The value is in the signed bytes but in each
component, not as a member of the envelope or of the CEG row.  The
trace format 3.1.0 schema of that pull request requires it in every
event's `data`.  An admitter reads it from the components, in this
order (the rule is to be stated in Section 3.1.5 of {{CC}} after its
`v1.0-rc21` release):

1. If any component carries `mock`, the trace is refused with
   `trace_run_kind_mock`.

2. Otherwise every component MUST carry the same `run_kind` value.  A
   trace any of whose components differ, or of which any component
   lacks `run_kind`, is refused with `trace_field_shape_violation`.
   This check compares values exactly: a trace mixing `prod-personal`
   and `production` is refused.  The three production values are
   treated alike only at admission, after this check passes.

The value can change within a trace for one reason: the agent's mock
model can engage partway through a thought, so that earlier components
carry a production or `qa` value and later ones `mock`.  An emitter
MUST NOT relabel a component's `run_kind` to match an earlier
component's: doing so would carry mock output under a production
label.  The disagreement reaches the admitter, which refuses the
trace.  Whether the value also becomes an envelope or row member is
open ({{divergences}}).

## The Oversize Form {#oversize}

A CEG payload is bounded at 1 MiB of deterministic encoding
({{I-D.moore-scitt-ciris-ceg}}).  When a trace is larger, the row
carries `manifest` instead of `trace`.  `trace_manifest:v1` is a
payload schema tag, not a family:

schema:
: The literal `trace_manifest:v1`.

content_hash:
: `sha256:` followed by the lowercase hexadecimal SHA-256 of the
  trace's canonical bytes.

byte_len:
: The length of those bytes, a positive integer.

component_count:
: The number of components in the trace.

The trace's bytes travel on the blob plane of {{CC}} and are named by
hash in the row's `evidence_refs`.

## trace_summary

`trace_summary:{kind}` is a post-scrub digest of a trace for
consumption on another node, used when the trace itself is out of
scope or over the size bound.  The same self-emission rule applies,
and a summary carries no claim the full trace does not.  Its payload
is not specified by the sources ({{open}}).

## Numbers in the Row

A CEG payload carries no floating-point value: a score is an integer
at the fixed scale of 10^6, and any other non-integral number is a
CBOR decimal fraction (tag 4 of {{RFC8949}}) {{I-D.moore-scitt-ciris-ceg}}.  A trace
is JSON, and many of its members are non-integral numbers: every
score in [0, 1] (`entropy_score`, `plausibility_score`), `k_eff`,
`cost_usd`, `cost_cents` and `duration_ms` among them.  The trace's
own scores are not fixed6 integers.

The sources do not say how these map into a CBOR statement
({{open}}).  Under the statement signature the signed bytes are the
CBOR payload, so the mapping is free of the JSON canonicalization; but
a conversion that rounds (to fixed6, for example) changes the values
the agent attests to, so the mapping must be applied by the agent
before it signs, never by a relay.  While a current-form signature is
also carried, a verifier must be able to reconstruct the JCS bytes of
the JSON trace exactly, which a lossy conversion prevents.  The
implementation's carrier is the earlier JSON row form, which carries
the trace's numbers as JSON numbers ({{impl}}).

# The Action Anchor and Orphan Purge {#anchor}

A trace exists only when its thought produces an action.  The emitter
seals and signs the trace when `ACTION_RESULT` arrives; a thought that
times out, ends without acting, or is abandoned produces no trace.
This is the anchor rule of {{CC}} (Section 1.13.6), which Section
5.3.2 applies to the durable trace: a trace is durable only when it is
anchored on the record of an act.  Reasoning that
produced no act is working state, not history.

{{CC}} states the rule as duties:

* Every execution path that produces an external effect (every
  utterance, every tool call, every emission through an adapter) MUST
  close with a terminal result row.  In this document's terms that is
  the `ACTION_RESULT` that seals the trace.

* An in-flight trace that reaches no terminal event MUST be purged
  after a declared, bounded age, and the emitter MUST export a count of
  the traces it purges, so that an auditor can see how much is
  discarded while its contents stay unavailable.

* The purge cannot erase evidence of a consequential act.  If it ever
  did, the defect is in the action path, not the purge.

The implementation purges orphan traces after a configured age
(default the larger of 120 seconds and twice the sweep interval) and
logs the number purged by each sweep.  Whether that count is exported
as a metric, as {{CC}} requires, is not determinable from the agent's
sources.  That every effect-producing path closes
with a terminal event is not yet tested; {{CC}} requires that it be
represented as a named wager wherever the control is claimed, and this
document so represents it.

A consumer that needs records of interrupted reasoning will not find
them in traces.  {{CC}} allows an operator to enable a bounded,
privacy-scoped plane for incomplete receipts as an explicit opt-in;
this document does not specify one.

# Validation by a Consumer {#validation}

A consumer that relies on a trace, whether it admits it, stores it or
scores it, MUST:

1. Verify the trace's signature ({{signing}}), including the check of
   `agent_id_hash` against the key.

2. Check that every component's `agent_id_hash` equals the
   envelope's (at `2.7.9` and later).

3. Check every `event_type` against the set of its schema version and
   every `component_type` against the mapping ({{components}}), and
   reject the trace on a mismatch.

4. Check that the trace has exactly one `ACTION_RESULT`.

5. Check that, for each `event_type`, the `attempt_index` values are
   0, 1, 2 and onward in array order without gaps or repeats.

6. Check that each `LLM_CALL` carrying a parent link names an
   (`event_type`, `attempt_index`) present in the same trace.  A call
   whose parent is absent SHOULD be held but MUST NOT be linked.

7. Read absent members as not emitted ({{strip}}), and group by
   `trace_level` before concluding that reasoning data is missing.

8. Keep every repeated event: every `ASPDMA_RESULT`,
   `CONSCIENCE_RESULT` and `LLM_CALL`.

9. As a CEG admitter, apply the row rules of {{carriage}}: the
   agent's key only, the closed `run_kind` with `mock` refused at
   federation tier, and the pinned field schema, refused not
   truncated.

10. Reject a trace whose schema version is newer than it supports,
    and say which version it supports.

A consumer MAY reject a component whose `agent_id_hash` differs from
the envelope's as malformed even where step 2 does not apply.

# Relationship to Other Work {#related}

Several individual Internet-Drafts record AI agent activity as signed
statements, several of them registered with a SCITT transparency
service {{RFC9943}}:

* {{I-D.thaha-scitt-agent-execution-evidence}} records digests of the
  request and response octets of each model call.  This document's
  `LLM_CALL` carries the request digest (`prompt_hash`) at `detailed`
  and the octets at `full_traces`, and links each call to the step that
  issued it.

* {{I-D.sharif-agent-audit-trail}}, {{I-D.emirdag-scitt-ai-agent-execution}},
  {{I-D.mih-scitt-agent-action-capsule}} and
  {{I-D.gilda-audit-agent-audit-record}} record actions, decisions,
  delegation and input hashes.  A trace is one such record per action,
  together with the evaluation, selection and veto steps that led to
  it.

* {{I-D.birkholz-vcon-ai-agent-extension}} and
  {{I-D.birkholz-verifiable-agent-conversations}} record agent
  conversations and attribute messages to parties.

* {{I-D.kuehlewind-audit-architecture}} and
  {{I-D.cosme-audit-agent-traceability}} address auditing delegation
  and interactions across domains.  A trace is evidence from one
  party, the agent, about its own processing.

* The OpenTelemetry GenAI conventions {{OTEL-GENAI}} define spans for
  model calls; they carry no signature and no disclosure profile.

What this document adds is a fixed pipeline vocabulary with a signed
link from every model call to the step that made it, the record of
every veto and reselection, disclosure levels that are part of the
signed bytes, and a lifecycle rule under which a trace exists exactly
when an act does.  It is complementary to the action records above: a
trace can be referenced from them by (`agent_id_hash`, `trace_id`).

# Open Issues {#open}

Note to the RFC Editor: please remove this section before publication.

- **Run kind member.**  {{CC}} requires a signed `run_kind` from a
  six-value set on the envelope.  CIRISAgent#1370 carries the six
  values in every component's signed `data`.  Whether the value is
  also an envelope or row member, and the rule for a trace whose
  components disagree, are not agreed.

- **Refuse, not truncate.**  The implementation's emitter truncates
  over-long values before signing; {{CC}} forbids truncation at
  admission.  CIRISAgent#1370 declares each cut in the signed data
  (`egress_alterations`, {{levels}}).  Whether the Constitution
  accepts a declared emitter cut, and how the emitter's and admitter's
  schemas are bound by one pinned hash, are open.

- **Numbers in a CBOR row.**  How a trace's non-integral JSON numbers
  are carried in a CEG CBOR payload, given that the trace's signature
  must remain verifiable, is not specified.  Two possibilities are to
  carry the trace's canonical bytes as a byte string, or to map each
  number to a decimal fraction from its shortest round-trip form.

- **ML-DSA-65 members.**  `pqc_key_id`, `pubkey_ml_dsa_65` and
  `signature_ml_dsa_65` are emitted but unspecified, including which
  bytes the ML-DSA-65 signature covers and how it relates to the
  composite signature of {{I-D.moore-scitt-ciris-ceg}}.

- **Key discovery.**  How a consumer resolves `signature_key_id` to a
  public key after the retirement of the registration endpoint.

- **Empty containers.**  Whether `strip_empty` removes a container
  that becomes empty only after its members are removed.

- **trace_summary payload.**  The members of `trace_summary:{kind}`.

- **context_manifest.**  The `LLM_CALL` member of {{llm-call}} is in
  CIRISAgent pull request 1370, not yet merged, and not yet in the
  egress schema.

- **Signature transition.**  The normative signature is the agent's
  CEG statement signature ({{statement-sig}}).  What ships is the
  per-trace Ed25519 form ({{current-form}}) in an earlier-form JSON
  row.  The storage engine's version 62 (server 0.6, not shipped)
  removes the earlier-form verification and verifies traces as
  agent-signed statements at admission.  Whether the current-form
  members are kept inside the payload during the change, and for how
  long, is not settled.

- **Schema version.**  `3.0.0` is what is stamped today, and the
  current form's verifier dispatches canonicalization on it.  `3.1.0`,
  naming `context_manifest`, is accepted by the storage engine's
  release 62.0 and stamped by the server's release 0.6; neither had
  shipped at the time of writing, and the per-level schema for it (the
  pinned `trace_format_v{n}.json`) and its evidence re-pin in {{CC}}
  land with them.

- **conscience_guidance_mode.**  The implementation hands each
  component a member `conscience_guidance_mode` outside `data`.
  Whether it reaches the signed bytes is not determinable from the
  agent's sources; the emitted example predates it.

- **Event taxonomy.**  The five credit and deferral event types are in
  the implementation's taxonomy but not in the wire contract.

- **Divergences.**  The disagreements of {{divergences}}.

# Implementation Status {#impl}

Note to the RFC Editor: please remove this section before publication,
together with the reference to {{RFC7942}}.

This section records the status of known implementations at the time
of writing, as described in {{RFC7942}}.  Listing an implementation
here does not imply endorsement.

CIRISAgent:
: {{CIRISAGENT}}, CIRIS L3C, AGPL-3.0, version 2.22.1 at commit
  59b7e5d.  The agent subscribes to its reasoning-event stream, builds
  each component's `data` under the configured trace level, filters it
  through its egress schema, derives `agent_id_hash` from its signing
  key, stamps `deployment_profile` with the run kind, and hands each
  component to the substrate library below.  It keeps traces from mock
  runs out of its federation store.  Its wire contract is
  {{FSD-TRACE}}.

ciris-lens-core:
: CIRIS L3C.  Named by the agent's sources as the library that owns
  partial-trace assembly, `attempt_index`, the seal on `ACTION_RESULT`,
  the consent gate, the canonical bytes, the Ed25519 signature, the
  orphan sweep and handing sealed traces to storage.  It stamps
  `trace_schema_version` `3.0.0` and selects the JCS canonicalizer by
  the same version rule a verifier uses.

ciris-persist:
: CIRIS L3C.  Named by the wire contract as the store that verifies a
  trace's current-form signature by version-selected canonicalizer
  before storing it, and that keys stored components on the tuple of
  {{attempt-index}}.  Its version 62 removes that verification and
  verifies traces as agent-signed CEG statements at admission; it had
  not shipped at the time of writing.

CIRISLens:
: CIRIS L3C.  Named by the wire contract as the consumer that verifies
  and persists traces and computes scores over them.

The trace of {{example}} was emitted by the agent at release 2.9.9
and carried as an earlier-form JSON CEG row of dimension
`trace:complete:v1`, signed by the agent's key, with the trace inline.
No implementation emits the CBOR row of {{I-D.moore-scitt-ciris-ceg}}
for a trace or the envelope's `run_kind` member.  The
`context_manifest` member, the per-component `run_kind` and the
`egress_alterations` marks are in an unmerged pull request
(CIRISAgent#1370).
No second, independent implementation of the emitter or the verifier
exists.

# Security Considerations {#security}

**An account, not a proof.**  A valid signature shows that the agent's
key signed the trace and that it has not changed since.  It does not
show that the steps happened as recorded.  A compromised agent can
sign a consistent but false trace.  Comparing a trace with records
made by parties the agent does not control, such as a model gateway,
is what turns the account into evidence.

**Identifier collisions.**  `agent_id_hash` is 64 bits.  A targeted
collision against one agent's identifier costs about 2^64 SHA-256
evaluations, and a collision between any two of a population about
2^32.  The identifier is an index and an anti-collision prefix for
stored components, not a security boundary: a consumer MUST verify
the signature with the full key, and MUST NOT accept a trace on a
matching `agent_id_hash` alone.

**Agent-controlled identifiers.**  `trace_id` and `thought_id` are
chosen by the agent.  Keying stored components without
`agent_id_hash` would let one agent pre-claim keys another agent's
traces need.

**Version confusion.**  In the current form the version selects the canonicalizer and is
itself signed.  Trying several shapes until one verifies would let an
attacker choose the interpretation; {{current-form}} forbids it.  At
`2.7.0`, members a later version signs are unsigned, and a verifier
that read them would accept injected values.

**Level confusion.**  The level is signed, so a trace cannot be
presented as having been produced under a different level.

**Parent links.**  The link from a model call to its step is signed.
A collector cannot reattribute a call's cost, latency or failure to
another step without invalidating the trace.

**Unknown events.**  Accepting an unknown `event_type` would admit a
payload no schema has reviewed.  Consumers reject it.

**Mock runs.**  A trace from a mock model looks like a real one.  The
run kind is the only signed marker.  At commit 59b7e5d an admitter
relies on `deployment_type` and on the emitter keeping mock traces
local; with CIRISAgent#1370 it reads `run_kind` from the components.

**Unspecified signatures.**  The ML-DSA-65 members are not specified.
Relying on them could give a false sense of post-quantum protection.

**Truncation.**  A filter that truncates before signing produces a
valid signature over an altered record.  The signature then attests to
the truncated text, and nothing in the trace says what was removed.

# Privacy Considerations {#privacy}

A trace describes how an agent handled a person's request, so it can
carry personal data ({{RFC6973}}).  The trace level decides how much.

**generic.**  No prompt, completion or reasoning text.  It does carry
the agent's name, model and handler names, timings, token counts and
costs, which can reveal activity patterns, and the agent-written
attestation summary.  In the example of {{example}}, which predates
the current egress schema, a `generic` trace carries the free-text
`dsdma_domain` label "theology / philosophy of suffering", which
describes the subject of the person's request, and the provider
endpoint `base_url`.  The current schema moves both to `detailed`.

**detailed.**  Adds channel identifiers, key identifiers and
fingerprints, provider endpoints, short reasons written by a model
(which can paraphrase the request), and prompt digests.  A digest of a
short or guessable prompt can be inverted by trying candidates.  The
context manifest at this level carries each verified sender as a
keyed digest (HMAC-SHA256 under a per-agent secret the agent never
discloses, truncated to 16 hexadecimal characters, `subject_id_form`
`hmac_sha256_16`).  Without the secret it cannot be reversed by trying
candidate identifiers, and it differs between agents, so it does not
link one person across agents.  Within one agent it is stable and
links that person's traces to one another.  The protection lasts only
while the secret is kept: a party that learns it can try candidates
as against an unkeyed digest.  At `full_traces` the identifier is
carried raw.

**full_traces.**  Adds prompts and completions verbatim, conversation
history and memories: the person's own words.  The implementation
lowers this level to `detailed` where personal data cannot be
scrubbed.

**agent_id_hash.**  Links every trace of one agent.  It identifies the
agent's key, not a person, but an agent serving one person links that
person's traces.

**Erasure.**  A person whose data is in a trace keeps the route of
{{CC}}: withdrawing consent starts a deletion clock.  The trace itself
is erased only by its signer or custodian ({{carriage}}).

Location and timezone metadata that the implementation sends beside
traces, under consent, are outside the CompleteTrace and its
signature and are not specified here.

# IANA Considerations

This document has no IANA actions.

--- back

# Divergences Between the Sources {#divergences}

Each entry is a point where the wire contract {{FSD-TRACE}}, the JSON
Schema {{TRACE-SCHEMA-JSON}}, the implementation at commit 59b7e5d, an
emitted trace, or {{CC}} disagree.  This document follows the code
where the question is what ships, and states the Constitution's rule
where the question is what is required.

Each entry's status is as of CIRISAgent#1370, which
adds a Section 0 ("As shipped") to the wire contract and fixes entries in
the code; this paragraph and the statuses below are updated to its
commit 3c4713a.  That pull request is not yet merged; until it
is, the "Shipped" text describes commit 59b7e5d.

Transport:
: Specified: HTTP POST of batches to a collector, with key registration.  Shipped: HTTP shipping and registration retired; sealing, signing and storage moved to ciris-lens-core.  Status: contract corrected to the code in CIRISAgent#1370, Section 0 (not yet merged).

Schema version:
: Specified: `2.7.9` in the contract text, const `2.7.0` in the JSON Schema.  Shipped: `3.0.0`, JCS.  Status: contract and JSON Schema corrected to the code in CIRISAgent#1370 (not yet merged); the trace format 3.1.0 schema is generated from the egress schema.

`trace_id`:
: Specified: `trace-<thought_id>-<YYYYMMDDHHMMSS>`; schema pattern `^trace-`.  Shipped: equals `thought_id`.  Status: contract and JSON Schema corrected to the code in CIRISAgent#1370 (not yet merged); the trace format 3.1.0 schema is generated from the egress schema.

Envelope members:
: Specified: 12 members.  Shipped: also `pqc_key_id`, `pubkey_ml_dsa_65`, `signature_ml_dsa_65`.  Status: contract corrected to the code in CIRISAgent#1370, Section 0 (not yet merged).

`agent_id_hash`:
: Specified: MUST be the key derivation.  Shipped: falls back to a hash of the agent name, or `unknown`, without a signing engine.  Status: fixed in CIRISAgent#1370 (not yet merged): with no signing engine the component is refused and counted, never captured under a name hash or `unknown`.

Event types:
: Specified: 10, closed.  Shipped: 15 in the taxonomy (five credit and deferral types), capture of `DEFERRAL_ROUTED` off by default.  Status: contract and JSON Schema corrected to the code in CIRISAgent#1370 (not yet merged); the trace format 3.1.0 schema is generated from the egress schema.

Components per trace:
: Specified: at most 6 components and five component types in the JSON Schema.  Shipped: 16 components in the example; seven component types in the core pipeline, twelve with the credit and deferral types.  Status: contract and JSON Schema corrected to the code in CIRISAgent#1370 (not yet merged); the trace format 3.1.0 schema is generated from the egress schema.

Component type `unknown`:
: Specified: listed in the contract.  Shipped: no event maps to it.  Status: contract corrected to the code in CIRISAgent#1370, Section 0 (not yet merged).

Run kind:
: Specified: a dedicated member pending in trace format v2.8.0 (contract); its own signed member with six values ({{CC}}).  Shipped: inside `deployment_type`; four values (`production` implicit, `qa`, `battery`, `mock`).  Status: CIRISAgent#1370 (not yet merged) carries the six values as signed `run_kind` in every component's `data`; an envelope or row member remains open.

Field schema enforcement:
: Specified: refuse, never truncate ({{CC}}).  Shipped: emitter drops and truncates before signing.  Status: CIRISAgent#1370 (not yet merged) declares each cut and drop in the signed data (`egress_alterations`); whether the Constitution accepts a declared emitter cut, and the pinned-hash binding, remain open.

Reasoning text:
: Specified: reasoning text at `detailed` (contract).  Shipped: reasoning text at `full_traces`; short reasons only at `detailed`.  Status: contract corrected to the code in CIRISAgent#1370, Section 0 (not yet merged).

Second-pass reasoning:
: Specified: `original_reasoning` and `final_reasoning` at `detailed` (contract).  Shipped: at `full_traces`.  Status: contract corrected to the code in CIRISAgent#1370, Section 0 (not yet merged).

`base_url`:
: Specified: optional, with no level (contract).  Shipped: `detailed` in the egress schema; at `generic` in the example trace (release 2.9.9).  Status: contract corrected to the code in CIRISAgent#1370, Section 0 (not yet merged).

`dsdma_domain`:
: Specified: not in the contract.  Shipped: `detailed` in the egress schema; at `generic` in the example trace.  Status: contract corrected to the code in CIRISAgent#1370, Section 0 (not yet merged).

`LLM_CALL` members:
: Specified: the contract's list.  Shipped: the code adds `sent_temperature`, `sent_seed`, `sent_max_tokens`, `served_by`, `served_model`.  Status: contract corrected to the code in CIRISAgent#1370, Section 0 (not yet merged).

Parent link:
: Specified: required from 2.7.9, no transition window.  Shipped: omitted when the issuing step is unknown.  Status: contract corrected to the code in CIRISAgent#1370, Section 0 (not yet merged).

`selected_action`:
: Specified: `speak` (contract), `SPEAK` (JSON Schema).  Shipped: `HandlerActionType.SPEAK` in the example trace.  Status: fixed in CIRISAgent#1370 (not yet merged): `selected_action` and `final_action` carry the action's value, `speak`.

`thought_type`:
: Specified: `seed`, `follow_up`, `retry` (JSON Schema).  Shipped: `standard`.  Status: contract corrected to the code in CIRISAgent#1370, Section 0 (not yet merged).

`attestation_status`:
: Specified: four values, without `partial` (contract text).  Shipped: `partial` in the emitted trace, and in the contract's own example.  Status: contract corrected to the code in CIRISAgent#1370, Section 0 (not yet merged).

`audit_entry_hash`:
: Specified: a SHA-256 digest, encoding unstated (contract).  Shipped: base64 in the emitted trace.  Status: contract corrected to the code in CIRISAgent#1370, Section 0 (not yet merged).

Once-per-thought list:
: Specified: the contract lists `ROUND_COMPLETE` among once-per-thought events.  Shipped: no such event type exists in the contract's own closed set or in the code.  Status: contract corrected to the code in CIRISAgent#1370, Section 0 (not yet merged).

Component order:
: Specified: receipt order, with component type a coarse hint of pipeline order (contract).  Shipped: in the example trace a model call for action selection precedes the evaluators' `DMA_RESULTS`, and timestamps are not monotonic.  Status: contract corrected to the code in CIRISAgent#1370, Section 0 (not yet merged).


# Example {#example}

This is a real trace, not constructed for this document.  It was
emitted by the reference agent at release 2.9.9 on 2026-08-01, running
on a real model (meta-llama/llama-4-scout through OpenRouter), and is
committed to the agent's repository as
`docker/research-traces/default/lens-batch-00000000.json` (commit
901266144).  The sibling directories `accord_detailed` and
`accord_full` hold the same thought captured at `detailed` and
`full_traces` by two other emitter instances, each with its own
signature, and each directory holds the earlier-form CEG rows that
carried its traces.  Its `deployment_type` is `production`; release
2.9.9 predates the run-kind marker, so the trace carries no run-kind
information.

It is shown at level `generic`, with these changes only: the two
ML-DSA-65 values (2604 and 4412 characters) are elided as `"..."`;
nine of the sixteen components are elided, as marked with `...`
lines, so the text is not valid JSON as shown; one long line is
folded as in {{RFC8792}}; and the members are in the order the file
has them.  Every value shown is as emitted.  The author did not verify
the signature, because the artifact does not include the Ed25519
public key.

~~~
=============== NOTE: '\' line wrapping per RFC 8792 ================

{
 "agent_id_hash": "9bff02b556cd84cb",
 "completed_at": "2026-08-01T02:55:05.156598+00:00",
 "components": [
  {
   "agent_id_hash": "9bff02b556cd84cb",
   "component_type": "observation",
   "data": {
    "attempt_index": 0,
    "round_number": 0,
    "task_priority": 0,
    "thought_depth": 0,
    "thought_type": "standard",
    "updated_info_available": false
   },
   "event_type": "THOUGHT_START",
   "timestamp": "2026-08-01T02:54:50.447918+00:00"
  },
  {
   "agent_id_hash": "9bff02b556cd84cb",
   "component_type": "llm_call",
   "data": {
    "attempt_count": 1,
    "attempt_index": 0,
    "base_url": "https://openrouter.ai/api/v1",
    "completion_bytes": 694,
    "completion_tokens": 139,
    "cost_usd": 0.0015144000000000002,
    "duration_ms": 1134.770154953003,
    "handler_name": "BaseDSDMA",
    "model": "meta-llama/llama-4-scout",
    "parent_attempt_index": 0,
    "parent_event_type": "DMA_RESULTS",
    "prompt_bytes": 32648,
    "prompt_tokens": 7433,
    "response_model": "DSDMAResult",
    "retry_count": 0,
    "service_name": "ciris_primary",
    "status": "ok"
   },
   "event_type": "LLM_CALL",
   "timestamp": "2026-08-01T02:54:52.484955+00:00"
  },
  ... components 3 to 7 elided: LLM_CALL attempts 1 to 3,
  ... SNAPSHOT_AND_CONTEXT, LLM_CALL attempt 4
  ... (parent ASPDMA_RESULT, timestamp 02:54:59.759)
  {
   "agent_id_hash": "9bff02b556cd84cb",
   "component_type": "rationale",
   "data": {
    "attempt_index": 0,
    "csdma": {
     "plausibility_score": 0.8
    },
    "csdma_plausibility_score": 0.8,
    "dsdma": {
     "domain_alignment": 0.5
    },
    "dsdma_domain": "theology / philosophy of suffering",
    "dsdma_domain_alignment": 0.5,
    "pdma": {
     "has_conflicts": false
    }
   },
   "event_type": "DMA_RESULTS",
   "timestamp": "2026-08-01T02:54:57.129347+00:00"
  },
  {
   "agent_id_hash": "9bff02b556cd84cb",
   "component_type": "rationale",
   "data": {
    "attempt_index": 0,
    "correlation_risk": 0.0,
    "effective_source_count": 1.0,
    "fragility_flag": true,
    "idma_correlation_risk": 0.0,
    "idma_fragility_flag": true,
    "idma_k_eff": 1.0,
    "idma_phase": "chaos",
    "k_eff": 1.0,
    "phase": "chaos",
    "reasoning_is_fragile": true,
    "reasoning_state": "chaos",
    "source_overlap": 0.0
   },
   "event_type": "IDMA_RESULT",
   "timestamp": "2026-08-01T02:54:57.129347+00:00"
  },
  ... components 10 to 13 elided: LLM_CALL attempts 5 to 8,
  ... parents CONSCIENCE_RESULT attempt 0, handlers
  ... optimization_veto_conscience, coherence_conscience,
  ... entropy_conscience, epistemic_humility_conscience
  {
   "agent_id_hash": "9bff02b556cd84cb",
   "component_type": "rationale",
   "data": {
    "attempt_index": 0,
    "is_recursive": false,
    "selected_action": "HandlerActionType.SPEAK"
   },
   "event_type": "ASPDMA_RESULT",
   "timestamp": "2026-08-01T02:54:59.778206+00:00"
  },
  {
   "agent_id_hash": "9bff02b556cd84cb",
   "component_type": "conscience",
   "data": {
    "action_was_overridden": false,
    "attempt_index": 0,
    "coherence_level": 0.9,
    "coherence_passed": true,
    "coherence_score": 0.9,
    "coherence_threshold": 0.6,
    "conscience_passed": true,
    "entropy_level": 0.2,
    "entropy_passed": true,
    "entropy_score": 0.2,
    "entropy_threshold": 0.4,
    "epistemic_humility_certainty": 0.9,
    "epistemic_humility_passed": true,
    "ethical_faculties_skipped": false,
    "is_recursive": false,
    "optimization_veto_entropy_ratio": 4.2,
    "optimization_veto_passed": true,
    "thought_depth_triggered": false,
    "updated_status_detected": false
   },
   "event_type": "CONSCIENCE_RESULT",
   "timestamp": "2026-08-01T02:55:05.132181+00:00"
  },
  {
   "agent_id_hash": "9bff02b556cd84cb",
   "component_type": "action",
   "data": {
    "action_executed": "speak",
    "attempt_index": 0,
    "audit_entry_hash":
      "wfDyaRQtc/eRD/iV01OH/+dCElBXnLY/wHt3dDoWSWA=",
    "audit_sequence_number": 2,
    "carbon_grams": 41.6628,
    "cost_cents": 5.55504,
    "energy_mwh": 83325.6,
    "execution_success": true,
    "execution_time_ms": 4.979,
    "has_execution_error": false,
    "has_positive_moment": false,
    "llm_calls": 9,
    "success": true,
    "tokens_input": 276423,
    "tokens_output": 1329,
    "tokens_total": 277752
   },
   "event_type": "ACTION_RESULT",
   "timestamp": "2026-08-01T02:55:05.156598+00:00"
  }
 ],
 "deployment_profile": {
  "agent_role": "ally",
  "agent_template": "Ally-default-unspecified",
  "deployment_domain": "general",
  "deployment_region": null,
  "deployment_trust_mode": "sovereign",
  "deployment_type": "production"
 },
 "pqc_key_id": "ciris-agent-bootstrap-tp7qfnkwzw",
 "pubkey_ml_dsa_65": "...",
 "signature": "s6u5gEOd9L2GbkDQrm1zh3RbCwuN7U0lVNq/JUPHpaedazYOKD\
NSEQUGFZwsZhtH25wOUCP/hg2aW0TiQv5zDg==",
 "signature_key_id": "ciris-agent-bootstrap-tp7qfnkwzw",
 "signature_ml_dsa_65": "...",
 "started_at": "2026-08-01T02:54:50.447918+00:00",
 "task_id": "4195adb2-0b71-40a0-8ad6-ab7b42027a8c",
 "thought_id": "th_seed_4195adb2_09df8b1f-5cc",
 "trace_id": "th_seed_4195adb2_09df8b1f-5cc",
 "trace_level": "generic",
 "trace_schema_version": "3.0.0"
}
~~~

Points the example shows:

* `trace_id` equals `thought_id`.

* Components are in receipt order.  The model call issued for action
  selection (timestamp 02:54:59.759) precedes the `DMA_RESULTS`
  component (02:54:57.129), and `ASPDMA_RESULT` (02:54:59.778) follows
  the four conscience calls (02:55:02 to 02:55:05).

* Every `LLM_CALL` names a parent present in the trace, and
  `attempt_index` runs 0 to 8 over the nine calls.

* The action was `speak`; all four checks passed on the first pass.

* No run kind is carried; `deployment_type` is the operator default.

The same file's companion,
`docker/research-traces/default/lens-batch-00000001.json`, is the
follow-up thought, whose action was `task_complete`.  Its
`CONSCIENCE_RESULT` carries no entropy, coherence, optimization-veto
or epistemic-humility members, because those checks did not run for
that action.

# Acknowledgments
{:numbered="false"}

The wire contract this document mirrors was written by the CIRIS
agent and lens engineers.
