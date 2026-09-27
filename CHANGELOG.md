# Changelog

All notable changes to the CIRIS Constitution. CC is one document with one version line;
each cut is validated against its sources under the skeptical rubric before it lands.

## 1.0-rc5 — the grammar as data, the trust root human-held, and every ruling anchored where its code lives

**Cut 2026-09-27, released as guidance.** rc5 is released as the text the substrate implements against, not as a record of what the substrate has proven. The register at the cut: 282 rows established, 68 staged, 8 normative, 0 unresolved; every pin at its upstream head (re-pin 5); every gate green. Of the release criterion stated below, clauses (2), (3) and (4) are met. Clause (1) is **carried**: of the four tickets rc5 named, CIRISAgent#1139 is done and CIRISConformance#90 (4 rows), CIRISServer#536 (26 rows) and CIRISPersist#803 (8 rows) are open — they hold the code that proves the rulings this release makes (halt authority, the pluggable trust root, the GenesisBundle route, epoch keying), and code that proves a new ruling cannot precede the ruling's release. Every one of the 68 staged rows names the open ticket it waits on, in the repository that owns the code: CIRISServer#536/#537/#614/#691, CIRISPersist#803/#922/#924–#928/#935, CIRISConformance#90, CIRISVerify#297, CIRISRegistry#139, CIRISAgent#1180, and this repository's #43, #71, #88, #93. Rows flip on the re-pins that follow; a ruling that moves under implementation contact is an rc6 amendment (#118–#121, #123 are already scoped there). Tagged `v1.0-rc5` on the finalize commit; `v1.0-rc4` tagged retroactively on its own.

RC5 opened as the **evidence re-pin release**: rc4 locked the registry so that every row resolves to a pinned artifact or names an open ticket; rc5 lands the evidence those tickets ask for — CIRISConformance#90, CIRISServer#536, CIRISPersist#803, CIRISAgent#1139 — and flips the 38 staged rows that earn it. Rulings filed against rc4 (#96 operational relief, #97 node self-report route, #98 `session:*`) land here as they are decided.

**Re-pin 1 (2026-09-06).** Six manifests at heads (server `41d5df9`, conformance `da0ec8a`, agent `bddb610`, verify `84fef3b`, persist `52f6592` v41.2.0, edge `905a50e` v20.3.0). Conformance flipped the CC 3.2 minor-stewardship vectors from xfail to green — the #87 supersession resolved — and shipped three new green gates: `test_573_co_stewardship` (3.4.7.3 custody cardinality one), `test_581_envelope_size_cap` (2.6.1.3), `test_582_wholeness_witness_merkle` (6.1.1). Four staged rows flip: `CLM-actor-substrate` and `CLM-common-human` (the #95 pair, on the cardinality test), `CLM-adult-incapacity`, `CLM-wholeness-witness`. 274 established / 34 staged / 7 normative, zero unresolved. Verify carries seven `UNASSIGNED` rows awaiting CC decimals — the designation task for this cycle.

**Art. 50(2) posture stated as it is, not as rc3 hoped (#9).** CC 3.4.14's conformance pin named "CIRISAgent 2.9.8" and "CIRISServer 0.6" as the releases discharging the marking path; neither carried it under that number, and after the 2 August 2026 deadline a forward-dated claim in the present tense is the F7 class on the most regulation-facing sentence in the document. Corrected: the R1–R2 path is **structural and ships** — an agent's federation identity is minted with `identity_type` containing `agent` (CIRISAgent v2.10.0-stable), so what it attests is machine-origin by construction and the client renders agent-versus-human from the signed envelope; the disclosure is the attestation read back, not a label. The R3 C2PA media form is normative wherever generated media is published and **dormant, not missing**, since no component publishes AI-generated media yet — it MUST ship with the first release that does. The conformance claim now resolves through the evidence registry, never by assertion. Rows re-staged on the repos that owe the manifest rows.

**The pluggable trust root was ratified in rc3; #40 is discharged as a ruling and its three bets enter the register.** Every ask in #40 was already in-text — the eight-point model at CC 4.4.3.8, reach-is-consent-scoped with the severance window at 4.2.1, root conferral in the enumeration, charter recovery with the independence audit, `infra:observe` deliberately unmarked at 4.1.3 — except the three named bets, now **R11 the growth tax, R12 blessing plurality, R13 first-halt legitimacy** in the Part VIII register. What remained was evidence: persist publishes the trust-root symbols at CC 3.2 under nsproc ids, and server's `mint_portable_root` is unpublished, so the two rows are re-staged on CIRISPersist#803 / CIRISServer#536 and #40 closes.

**The media Source struct gets its vocabulary, and the render tier becomes receiver policy (#104).** CC 3.3.13 said what each multimedia Source struct carries but not what fills `format` and `codec`, and it omitted the one field every byte-verifying system needs. The ruling, from a brief with five underlying surveys: `format` is the IANA media-type essence, `codec` is an RFC 6381 identifier in its own field and required for MP4 audio and video, `size` is required on every blob the wire cites and checked before the digest (CC 5.3.2.5, a general rule the media struct inherits; a live stream in progress is the one descriptor without a total), captions are a separate `text/vtt` blob by hash, and the AI-generation disclosure takes its values from the IPTC Digital Source Type vocabulary so it interoperates with C2PA without adopting C2PA's digest-changing manifest. Not multicodec, no CID layer. The struct carries no `safe` or tier bit, because a new CC 5.3.2.6 rules that a consumer decides whether to render from the verified, sniffed bytes and its own policy, never from a claim in the descriptor: sniffed essence must equal declared `format` or the blob is refused. Renditions are separate blobs, the sender canonicalises before hashing, and the node stores verbatim. The Tier A / B / C renderable set is published under 5.3.2.6 as recommended client policy, not normative, and the SVG open call dissolves under the rendition rule: the bytes are Tier C, a node's PNG of them is Tier A. The `live_stream` row records the HLS / CMAF mapping as its Phase 2 shape. The motivation is the decoder CVE record, which makes the type set a client renders a security boundary this document owns. Node-side pipeline filed as CIRISServer#614.

**Consent scope lives in the envelope, not in a companion row (#103).** CC 3.3.1 described the scope of a `consent:state:granted` as `consent:scope:{kind}` companion attestations, and its own composition pattern showed them. Every live producer emits the scope as the `scope` member of the granted row's envelope, and every fold reads it there; run the CC's documented pattern through the substrate and the scoped fold returns nothing, so a `capacity:*` score about that subject is refused. Fail-closed, but the constitution's common case was inert. The row and the pattern now say the envelope member is the carrier, sub-scoping is in the token (`retain:90d`), and a `consent:scope:{kind}` row is descriptive. The same row said `analyze`-on-emission for `capacity:*` was "deferred and non-normative"; that was true before #46 ratified the CC 3.4.5 consent-before-scoring gate and false since. Deleted. Operator decision of 2026-09-18 from the CIRISEdge transmission-principle audit (CIRISPersist#866, #867).

**`consent:decay:{stage}` is emitted by whoever runs the protocol (CIRISAgent#1180).** The row named the substrate as emitter. The three canonical stages are the CIRISAgent consent module's 90-day protocol, states of the agent's own processing that the substrate cannot observe; the substrate's decay sweep evicts fountain symbols on a clock, which is byte eviction, not a stage, and it emits no decay row. The emitter column now reads the protocol runner, a self-report under CC 3.4.5.1 that confers no right to be believed. The substrate's own leaf in the family, `consent:state:expired` for a lapsed grant, is named in the row.

**CC 3.2 said communities do not encrypt at rest; CC 4.4.3.2.1 says they must.** The family-versus-community comparison table carried a row reading "At-rest encryption: community — No, content federates per status quo." That is the pre-cascade design, and it survived the change that made the community DEK cascade mandatory. The prose in the same section already said the opposite, plainly: "A community is not therefore plaintext-by-default." The table row is corrected to the mandatory cascade, with the `cohort_subkind: infrastructure` carve-out named where a reader meets the rule. The carve-out itself is unchanged. Reported by CIRISPersist#824, which is enforcing that contract at the write door and needed the text to stop contradicting itself.

**Dimensions are case-sensitive, and the Constitution's vocabulary is lowercase (CIRISPersist#815).** Persist's adversarial pass found `Config:Admission:v1` walking past every byte-exact family gate, closed the stem half itself, and asked which of three casing readings holds. CC 3.1.7 gains R3: a dimension is compared byte-exactly everywhere and no consumer case-folds; which rule a segment obeys is a per-segment class carried as data — `literal` (CC stem, lowercase, build-gated), `vocab` (CC-defined vocabulary, `[a-z0-9][a-z0-9_.-]*`, refused with `namespace_dimension_case_malformed` otherwise), `external` (ISO 4217 / BCP 47 / rating-scheme tokens, verbatim), `value` (caller identity, case-preserved), `hex` (CC 2.6.3 lowercase). `tools/build_cc_namespace.py` now classifies every placeholder of every family into `families[].segments[]` and publishes the rule as `_meta.case_rule`; an unclassified placeholder or a non-lowercase stem fails the build. The `slashing:{outcome}` row's `PROVEN_ROGUE` / `NOT_PROVEN` were the one in-text violation and are lowercased to what the substrate already emits.

**Anyone may be a licensing authority; a licence admits like everything else (CIRISPersist#814).** Persist shipped the emitter half of the `license` delegated scope and asked what object says "X holds licence authority for A", what quorum it is over, and who emits it. CC 2.4.1.2.1 now answers: no object and no roster. `authority_id` names a key (or an org resolving through `org_membership`); X holds authority for A iff X's key is A or holds a `license` chain to A; a `licensure:{A}` row admits under the ordinary gate — the reader trusts the emitter's root or has consented to receive from it, as the contextual-integrity medical exemplar already shows — and "by quorum" describes the authority's own governance where it is a collective, never a gate on somebody else's authority. The fold for `(subject, A)` takes only rows whose emitter resolves to A; a stranger's row is testimony, admitted but outside the fold, so an absorbing `revoked` binds nobody. One refusal, `licensure_delegator_not_authority`, on a `license`-scoped issuance whose chain does not resolve to A. CC 3.4.9 clarified: Registry/Verify co-steward the CIRIS-issued licence, the family is not reserved to them. CC 3.3.9: an organisation names itself by `org_id`, not the registration number the reference Registry projects (CIRISRegistry#139).

**Ticket state and pin staleness become checked conditions (#65, #63).** The two remaining halves of the drift-gate family. A `staged:`/`open:` token naming a CLOSED ticket now fails the build — either the work shipped and the row must graduate to its artifact, or the ticket closed unfixed and the row is unanchored; both are the registry asserting something untrue, which is what #65 measured at 134 of 158 rows on rc3. Evidence pins behind their upstream head now warn with the head named. Both need the network and say so when they cannot run — a check that did not run did not pass. First live run: all 15 staging tickets open, every pin at head; dye-tested in both directions. Two vestigial `staged:CIRISPersist#356` tokens on rows already established on real tests were the gate's first catch, and are gone.

**Namespace coverage becomes a checked condition (#102).** Landing `duty:{kind}` surfaced that a family added beside `consent:scope:{kind}` in CC 3.3.1 does not register. The audit corrected the diagnosis twice: the cause is not the table's header shape but that the generator harvests **only** under a `3.1.x` component heading — correct behaviour, since registration needs an owner — and the consent plane is **not** unregistered, because `consent:{kind}` is a registered parameterized family that covers its kinds. Measured across all 159 prefix-table rows: zero misses inside CC 3.1, and **12 genuinely unowned families** in CC 3.3.8 / 3.3.11 / 3.3.12 (`event:*`, the inter-content set, the multimedia set) — documented dimension families with no owning component, which under CC 3.1.7 R2 admit under the ProducerSteward fallback, *an authority nobody chose*. `check_claims.py` gains a **namespace-coverage gate**: every prose family must register, resolve to a registered parent, or sit in a pinned inventory — a new orphan fails the build, and a pin that outlives its gap fails too. Both directions dye-tested. Owner assignment for the 12 is named as the open decision rather than taken unilaterally.

**CC 2.4.1.2.1 — licensure, grant, delegation: the triad named at the grammar (#100, ruled).** All five asks granted, from an audit against fourteen standards. The document already routed two of the three legs through different machinery (CC 3.3.9) but said so as an aside inside an operational-data section; the triad is now normative at CC 2.4, where an implementer meets `delegates_to` — with the four discriminators and the **wire test for each** (dimension prefix / `subject_kind` / structural primitive), since only delegation had a structural identity and a consumer could not ask *is this a licence?* without a prefix table. **The transitivity row is the discriminator of record**: only delegation chains, which is why only `delegates_to` gets a graph walk — a design that walks a licence or a grant transitively has mistaken it for a delegation. Provenance is the `authority_id`, conferred by quorum, never by `delegates_to`; a `key_grant` is non-transferable by default, an onward grant being a *new* grant by a key-holder (enforced cryptographically before policy). **Issuance becomes delegable with precision**: `license` and `grant` join the emission-authority table under the same **enforced admission** as `moderate`/`takedown`/`review` — an issuance whose delegator does not hold the underlying authority is refused, not merely unweighted — and `infra:attest` MAY be attenuated to a dimension family (`infra:attest:licensure:{authority}`) as a **caveat on an existing capability**, adding no member to the closed `infra:*` set. That carries its own trap, ruled: **sub-scope matching is directional** — a parent satisfies a check for its child, a child MUST NOT satisfy a check for its parent, and an unknown caveat fails closed; the naive `starts_with` test hands a deliberately narrowed holder the full capability, the same shape as the CC 3.4.7.3 purity-vs-membership defect. `licensure:{authority_id}` widens to eight statuses with **`suspended` reversible and `revoked` terminal** and concurrent statuses admitted (active-on-probation is two facts, not a blended state). **`duty:{kind}` is registered** (116 families) — the ODRL Duty leg a permission-and-prohibition grammar cannot express and every content licence rests on; a duty *states* the obligation, the existing `commitment_fulfillment` evidences discharge, and breach routes to `hard_case:duty_unmet` — adjudication, never automatic slashing.

**CC 3.4.5.1 — how a self-report reaches a peer, and what a peer owes it (#97, ruled).** Three implementation attempts hit three walls; only one was constitutional. **Scope**: this document never pinned `config:*` to a `cohort_scope` — the CC 3.1.9 row constrains the *subject*, which is a different axis from scope — so the reported dilemma (*compliant and unreadable, or federation-scoped and in breach*) is false, and comes from generalizing one implementation's correct fix for **sensitive** config rows into a family-wide invariant. Sensitive leaves (`admission`, `transport`) stay `self`; a bare operational leaf like `load` MAY take the smallest scope that reaches the peers which route to it. **Trust**: `infra:attest` confers authority to emit and **no right to be believed** — a grant from my owner cannot bind your composer, which would be authority laundering — so an unpinned peer's self-report is *admissible but unweighted*, and weighting is CC 4.4 consumer policy. Anyone may claim anything; absent trust or consent a claim reaches no one but its author, and the route is the consent-gated attestation plane rather than a new namespace. **Renewal**: a renewing self-report MUST carry `supersedes`, so the live set is one row per `(subject, scope, leaf)` and composers count **distinct subjects, never rows** — otherwise renewing correctly halves a node's own signal and continued pressure makes the claim quieter. Named as not-CC: whether a plane carries an event kind is a substrate gap, not a rule.

**CC 3.1.3.1 — `session:*`, the session-claim plane (#98, ruled).** Persist shipped a governed family CC had no row for, and its own `family_rules` gate refused to let the divergence sit silently — a downstream reading the classifier would conclude the family is open while persist refuses emissions on it. Now registered (115 families of record; persist stewards 6) with both enforced rules stated: **emitter self-report** (`attesting_key_id` = `attested_key_id` = the claiming occurrence — a third-party assertion of where you are attending is a rumour, the CC 3.4.5 discipline) and **convergent merge** (earliest `claimed_at`, ties on the lowest occurrence `key_id`; the tie-break is load-bearing because a fan-out arrives at once and clocks are coarse, so without a total order two nodes disagree forever, each correctly applying earliest-wins). Beneath both, the invariant: **an unclaimed exchange is never acted on** — not by quorum, not by lowest id, not by a single-node self, because being the only occurrence means there is one place where nobody is home; attendance is presence in the table, and no weak-claim variant may exist for a careless comparison to promote into a right to act. The **`Cohort` projection ceiling is ratified as a decided row with its reason in-text** — at `Global` the family publishes an attendance map of a person's devices, which is structural invisibility inverted, and would arrive as a refactor rather than a ruling.

**CC 4.2.1.4 — operational relief: the node detects, the root relieves (#96, ruled).** Two implementations read the mesh-config rules and got it wrong in opposite directions in one week, because the rules constrain *authoring* while the question under load is *what may a node do about itself*. Ruled on the filer's own correction: `config:load` is the node's self-report (`infra:attest`, `witness_relation: self`, `expires_at`, about itself only); `mesh_config` is the root's plane over other nodes; neither is authorable on the other's, and the two compose — the self-report is evidence a root may act on, the relief is a bound the node consumes. Stated positively for the first time: a node MAY always do less of its own optional work, a local act that declares and confers nothing. Both records expire for one reason — the TTL attaches to *unilateralness*. `config:load` named as a canonical scope with `shedding`. The CC 3.4.5 self-or-owner rule for `config:*` is now enforced at substrate admission (persist v38.7.0/#778), completing CC 3.4.7's three legs.

**CC 2.6.8 — NodeCode becomes FedCode: tied to the user, nodes optional, directory otherwise.** The section still pinned the v1 node-tied code while verify ships FSD-003's kind-tagged v2/v3 (`user / agent / node / family / community`, mapping 1:1 onto `identity_type` and the rostered `subject_kind`s; v1 decodes as `kind: node`). Rewritten to the model: a `user` code is the owner's identity; owned nodes and transport are optional (v3 embeds up to 16, transport keys only — never a federation key, CIRISServer#335's lesson; only `kind = user` may embed; lightnet facts only per 5.4.6/#91), and a bare code resolves through the directory via `nodes_owned_by(U)`, the by-construction inverse of `owner_of`. The PQC commitment (`sha256` of the ML-DSA-65 pubkey; pulled half verified before the hybrid write; fails closed absent; unsigned — binding, never authentication), the `label-fingerprint` `key_id` (collision-resistant, not collision-free — 50 bits, birthday bound near 2²⁵ keys per label, so registry uniqueness is load-bearing; verifiable), and the usercode → owner onboarding flow (pending `identity_occurrence`, one signed approval tap; the pre-authorized bearer alternative rejected) are pinned. **Designation (#101)**: seven verify `UNASSIGNED` rows minted with decimals — subject binding (2.3.2.1, 3.3.6), scope destination (5.4.6), validity window (2.1), fedcode ×2 (2.6.8), keyring RNG latch (4.2.2).

**The Constitution's own SLA vocabulary was unwritable under its own casing rule (#106), and the value half of R3 is now build-gated.** CC 3.1.5.2 enumerated `fidelity:explainability_sla:{tier}` as `L1_summary` … `L4_attested_chain` while CC 3.1.7 R3 classes `{tier}` as `vocab`, lowercase, refused on the wire as `namespace_dimension_case_malformed` and never folded — so no conformant producer could commit to a tier. The four tiers are lowercased (`l1_summary`, `l2_reasoning_trace`, `l3_full_dma_chain`, `l4_attested_chain`), the same disposition rc5 gave `slashing:{outcome}`. The generator gated only literal stems; it now also checks every in-row `{name}` ∈ … enumeration of a `vocab`-classed placeholder against `vocab_pattern`, so the next uppercase value fails the build instead of the wire. Dye-tested in both directions. Two smaller repairs in the same pass: the #102 coverage gate read the CC 3.3.8 `event:rsvp_count` row as a table header (its description links to `…-relation-prefixes`) and so never audited it — the header test now keys on the first cell, and the family joins the pinned unowned inventory (13, all on the #102 owner decision); and the twelve toc.tsv titles still carrying pre-migration CEG wording are aligned to their prose headings, so the checker reports zero drift.
**The thirteen ownerless content families are NodeCore's (#102, decided).** The #102 audit left one decision open: who stewards the `event:*` (CC 3.3.8), inter-content (CC 3.3.11) and media-type (CC 3.3.12) families, which admitted under the CC 3.1.7 R2 ProducerSteward fallback because no owning component reached them. The prose had already answered: these dimensions are emitted against the `external_content` sub_kinds NodeCore ships (CC 3.3 intro), the Source-struct schemas are NodeCore's (CC 3.3.13), and `chat_message` + `topical_relation:*` is NodeCore's thread composition — the same table in CC 3.3.12 already registers `content_class` / `cw_class` / `content_rating` under NodeCore at CC 3.1.9.2. Registry, the other candidate, is not the owner: its slice is identity / build / license / partner, and none of these is one. Landed the way R1 prescribes rather than by widening the generator's harvest: thirteen one-line catalogue rows under CC 3.1.9 (a content-ingestion block beside the node-configuration family), each pointing at the section that keeps its semantics, so the generator's rule that registration needs an owner is untouched. 129 families of record, NodeCore 48. The coverage gate's pinned-unowned inventory is now **empty** — the gate stays, and would have failed had the pins outlived their gap — and each of the three CC 3.3 sections names its owner where a reader meets the rows. R1's sentence that a CC 3.3-only ungated family "is registered and conformant" said the opposite of what the build enforces since #102 and is corrected: describable there, registered only by its CC 3.1 row. Discharges #102 and the harvest half of #105's ask 1; the `ledger:*` / `settlement:*` rows #105 asks for are an ownership ruling of their own and stay open there.

**A trailing `*` is variadic, and the registry now says so as data (#108, cause B).** The generator emitted a wildcard as one `{segment: "*", class: wildcard}` entry, and the client's binding checker read that as "exactly one more segment" — so `accord:*` could name `accord:invoke` and none of the four invocation kinds CC 4.2.1.2 obliges a consumer to distinguish, and the same for every `dma:*` verdict leaf and `system:*`. CC 3.4.1's own table lists four-segment leaves under `accord:*`, so the Constitution already meant one-or-more. R3 now states it — a trailing `*` matches one *or more* remaining segments, never exactly one — and the manifest carries it twice: `variadic: true` on every wildcard segment and `_meta.case_rule.wildcard_rule` with the rule spelled out, so a vendoring checker keys on the manifest rather than on its own reading of `*`. The other half of #108 — registering the four `accord:` leaves explicitly — waits on a casing decision that is not a nit: `CONSTITUTIONAL` is inside the CC 4.2.1 canonical signed bytes of the kill switch, so lowercasing it is a wire break for accord holders, and classing it `value` to keep the uppercase is the alternative; that is the operator's call and stays open on the issue.

**The device roster is public exactly for the devices announced, per node (#111, recorded).** Operator ruling of 2026-09-25 from CIRISServer#655, recorded at CC 5.4.6 where implementations meet the announce rule: a person is contactable through the nodes they chose to announce, and that set *is* their public roster; an unannounced node stays on the derived plane — reachable by their own nodes and by whoever holds a v3 code they issued — and MUST NOT be listed or enumerated by any directory, serve policy or read route. It is the CC 2.1 `listed` discipline read at the transport plane, where announcing is the opt-in. Composed with the CC 3.4.13 Q5 hard floor, which forbids a minor being contactable or discoverable by unconnected adults and lets no steward or stacked consent lift it: a node whose owner resolves to the `minor` band MUST NOT announce at federation scope. One evidence row, `CLM-device-roster-announced`, normative.

**The dimension grammar becomes data, and one matcher implements it everywhere (#112 — operator decision 2026-09-26).** Checked against persist, edge, server, verify and the client at their heads, four defects shared one cause: the registry manifest carried too little of the grammar for a consumer to match a wire dimension without inventing rules, so six consumers wrote six matchers (four prefix-based, two arity-exact, one that case-folds). Every real emitter appends a `:v1` the Constitution never mentioned while persist's admission door required it; the kill switch's invocation kind sat uppercase inside signed bytes under an R3 that makes CC vocabulary lowercase; six vocabularies answered "where does this key live"; and the word "announce" named three different acts. The manifest now carries the rule: **`_meta.case_rule.version_segment`** (every scored dimension carries exactly one trailing `:v{N}` after its family's segments; matching strips it; absence is `missing_version_segment`; the attestation ladder and the canonical-binding claim are exempt, as data), **`segments[].values`** for every enumerated `vocab` placeholder (closed only where the row says the word, else the canonical subset of an open vocabulary; an unlisted closed value is `namespace_vocab_value_unregistered`), **`leaves` / `leaves_closed`** on reserved wildcard families (any other leaf is `namespace_family_unregistered` — a reservation is not a namespace), the **`refusal_tokens`** table, and **`_meta.registry_sha256`**, the hash of the grammar rather than of the prose, so a wording edit no longer invalidates every downstream pin (the client's sixty CSD cards pin the prose hash today, and this branch alone moved it four times). `tools/cc_namespace_match.py` is the **reference matcher**, `manifests/namespace_match_vectors.json` its published vectors (776 at this cut; the count is the manifest's and moves with every family), and the generator refuses to build unless every family's sample round-trips to itself and to no other family — the dye test caught two defects in the matcher's own first draft. R3 states all of it; CC 1's T3 no longer says the dimension's version lives in `evidence_refs[]`; two citations of a "CC 4.1.3 version-segment gate" that named the rejected-additions table now cite R3; `{unit}` is classed `external` (#105 ask 4).

**The accord leaves are lowercase, closed, and six (#108 asks 2–3, ruled; the wire break rides the domain label).** `invocation_kind` is `constitutional` \| `notify` \| `drill`, byte-exact, under **`ciris.accord_invoke.v2`** — the label's version exists so a signature under the old spelling fails loudly, and rc5 is the last cut at which this is not a MAJOR. Nothing durable pins the old bytes: no database column, no conformance vector, only a transient halt latch, so the one cut-over precondition is that no halt is latched. CC 3.4.1 had labelled the heartbeat with the resumption token: **`accord:lifecycle`** (wire `accord:lifecycle:v1`, frozen and genesis-signed) is the heartbeat, **`accord:lifecycle:active`** the resumption kind, two rows. `accord:human_dignity` is registered **provisionally** under R2(a) because the substrate admits it today; ratify or retire on #112. All six carry CC 3.1.1 rows and `accord:*` is `leaves_closed`, so the ten client card fields that bind invented `accord:` leaves refuse on re-vendor, correctly. CC 4.2.1.2 adds the consumer rule the client's screen breaks today: switch on the four kinds byte-exactly, no case-fold, fail-closed default.

**Hardware custody is one closed vocabulary; hardware class is a property, not a dimension (#107, ruled).** `hardware_custody:{platform}` is the thirteen-token snake_case of `ciris_keyring::HardwareType`, closed and generated; `tpm`, `android` and `software_fallback` are retired, since production emitted none of them and verify emitted the enum's Debug name lowercased instead. `hardware_class` has no `federation_keys` column — it rides inside `attestation_evidence` and two registry routes — so it is a JSON property outside R3, keeps its stored spellings, gains a normative class-to-mechanism mapping table at CC 4.2.2, and an unlisted class carries multiplier 0.0 (nine classes code has minted are unlisted). CC 4.2.2.1 said no attestation mechanism existed while CC 8.3.1 R5 recorded it discharged; 4.2.2.1 now says what R5 says. `identity:canonical_binding:{canonical_hash}` gains the CC 3.1 row a reserved dimension owes under R1.

**"Announced" is the owner-binding at federation scope (#111, refined).** Server pins the transport announce on for every node and delivers privacy through the owner-binding's scope, which the one announce operation promotes from `self` to `federation`; a stranger's directory walk yields exactly the federation-scoped bindings. CC 5.4.6 now says so, CC 2.6.8 says the walk is as visible to the walker, CC 3.2 says a binding is written at `self` and re-signed at `federation`, and the minors clause is enforceable: a minor's node MUST NOT carry a federation-scope owner-binding and admission MUST refuse the promotion — no component enforces it today. Six evidence rows staged on #112, which carries the per-repository program: persist's v50 takes the matcher port, the R3 zip fix and the minors gate; verify the lowercase kinds and `as_platform()`; server the hardware literals and promote check; edge and the client the vector replay and the pin.

**Codex review of #113 — nine findings, nine fixes, all landed.** On the grammar cut: a row ending in `{version}` now recognises an input without the tail and refuses it `missing_version_segment` instead of letting it fall into open vocabulary (`age_assurance:provider:adult`); `external` segments are checked against the syntax of the standard the manifest names for them (`_meta.case_rule.external_standards`, copied onto the segment — `USD` passes, `usd` is malformed, BCP 47 tags are shape-checked); the version pattern admits a dotted suite version (`^v[0-9]+(\.[0-9]+)*$`) because HE-300 documents `v1.0` / `v1.1` / `v1.2`, now carried as the row's `values` so the round-trip sample exercises them; and the coverage gate resolves a prose family **by shape through the reference matcher** rather than by shared stem, which exposed nine consent leaves (`consent:state:{stance}`, `consent:scope:{kind}`, `consent:deletion_sla:{days}` …) that were "covered" by `consent:{kind}` while no matcher could resolve them — all live on the wire as three-segment dimensions, all now CC 3.1.5 rows with the per-leaf emitter reservation. The two hard-case tables at CC 3.4.2 / 3.4.4 are retitled as what they are, `hard_case` **event kinds** with the key id in the payload, not prefix families. On the rest of rc5: the CI job now exports `GH_TOKEN` so the #65 / #63 ticket-state and pin gates run instead of noting that they could not; the PDF finalizer also refreshes a permalink whose bytes differ from the clean release file, so a stable-version bump cannot leave `latest` stale; the README says rc5; CC 2.6.8's 50-bit fingerprint is stated as collision-resistant with the birthday bound near 2²⁵ keys per label, registry uniqueness made load-bearing, and a raise to 80 bits recommended above 2¹⁶ identities per label (FSD-003 owns the change); and CC 3.1.3.1's session-claim staleness is the row's own signed `valid_until`, never a consumer-local horizon, since two horizons would undo the convergence the section exists for. 145 families; the vector count is the manifest's. One drift surfaced for #112: persist emits `consent:share:v1`, a leaf no CC row names.

**Re-pin 3 (2026-09-26): agent @6f00288 — the ticket-state gate's first live catch.** The #113 review's `GH_TOKEN` fix made the #65 gate run in CI for the first time, and it failed the build at once: `CLM-synthesis-disclosure` staged on CIRISAgent#1139, which closed on 2026-09-08 when the agent shipped the CC 3.4.14 rows (`ea2bd14`). The agent manifest is re-vendored at head (73 rows, three new) and the row graduates to `edge_runtime.py#initialize_edge_runtime`, `established`. The other six pins are behind their heads and warn; each is a re-pin of its own.

**Codex, second pass on #113 — ten findings, ten fixes.** Matcher: a dimension no row claims is now checked for being a *malformed form* of a registered family before it is called open vocabulary — a case-mutated stem (`Capacity:composite:v1`), an uppercase or duplicated version tail (`…:V1`, `…:v1:v2`) — folding and stripping only to detect, never to admit, so a mutation can no longer route around a reserved family's emitter rule; a version-like token inside a wildcard tail or a multi-segment value is malformed for the same reason. Three rows whose documented values carry colons (`consent:scope:{kind}` sub-scoped as `retain:90d`, `detection:correlated_action:{axis}` as `rights_asymmetry:{population}`, `provenance:skill_import:{source}` as `registry:{id}`) declare the placeholder **multi-segment** (`multi` on the segment), each sub-segment obeying the class; no other placeholder contains a colon. `{canonical_hash}` pins a 64-character shape and `{days}` / `{tree_size}` pin digits, as `pattern` on the segment. Exempt families publish a with-version vector so a consumer that refuses the tolerated tail fails replay. `session:{kind}` carries its own `occurrence-self-report` reserved rule ahead of the substrate-wide one that had been mis-stamped on it. Gate: the pin-staleness check warns per unreadable pin instead of calling a partial read a pass. Prose: an onward `key_grant` is issued by the asset's owner or steward or a `grant`-scoped delegate, never by whoever holds the DEK — every recipient holds it — and admission refuses a grant issued on possession alone (CC 2.4.1.2.1, CC 4.4.3.4.3); the blob-size rule names where the size lives (the citing descriptor's canonical shape) and states that a bare `evidence_refs[]` string carries none, so the CC 2.6.1.3 cap is the check there and no size field is invented on the frozen envelope (CC 5.3.2.5).

**Codex, third pass on #113 — six findings, six fixes, one re-pin.** The matcher reads a version-shaped last segment as a *value* when nothing matches with it stripped (`config:v1` is `config:{scope}` with the tail omitted, refused `missing_version_segment`, never open vocabulary). **Re-pin 4: verify @cdc6498** — the head manifest assigns 2.6.8 to the two FedCode rows, so `CLM-fedcode-owned-nodes` and `CLM-fedcode-pqc-commitment` graduate to `fedcode.rs`; `CLM-key_id`, which called the v1 NodeCode encoder evidence for a section now describing FedCode v2/v3, is re-scoped to the v1 leg the section retains, and a new `CLM-fedcode-kind-tagged` row stages the v2/v3 encoder on #101 until verify publishes the symbol. **CC 2.1 gains the `scope` member** every live producer already emits and #103 made the carrier of a grant's scope: optional, REQUIRED on `consent:state:granted`, inside the signed bytes, with its wire-table row — the envelope catalogue had never listed it, so a conforming consumer could ignore it and refuse every gated `capacity:*` row. The CC 3.4.5 reservation cell that still had `consent:decay:*` emitted by the substrate now says the protocol runner, matching CC 3.3.1's erratum; `consent:state:expired` is the one substrate-emitted consent leaf. CC 8.3.6's "deferred" entry for per-platform attestation chains says discharged, matching R5, and CC 4.2.2.1 is retitled. The rc5 FedCode changelog entry no longer calls the fingerprint collision-free.

**Codex, fourth pass on #113 — five findings, five fixes.** The stems CC 3.4 reserves as a whole (`accord:`, `detection:`, `capacity:`, `age_assurance:`, `capacity_assurance:`, `transparency_log:cosigned:`) are now manifest data, `_meta.case_rule.reserved_stems`, and the matcher refuses an unclaimed leaf beneath one as `namespace_family_unregistered` instead of calling it open vocabulary — the reservation covers the leaves nobody minted yet. `licensure:` leaves that table and its CC 3.1.1 cell reads `No`: CC 3.4.9 co-stewards the CIRIS-issued licence and says the family is open-emitter, while the generator had kept it `reserved: true`. The session-claim merge keys on three **signed** members — `community_id`, and this family's `session_id` and `claimed_at`, now CC 2.1 rows REQUIRED on `session:*` — exactly the members persist reads, so no consumer substitutes `asserted_at` or a payload field. CC 2.6.1's byte-field rule no longer says a `key_id` is lowercase hex: hashes and raw key material are, a `key_id` is the CC 2.6.8 `<label>-<fingerprint>` identifier carried verbatim, and CC 2.3.2.1's tag argument is restated for a world where key ids are format-distinguishable from bare hashes by construction. The two literal vector counts in this changelog are gone; the count is the manifest's.

**The age ladder's value sets close, and the self-declared rung takes the wire's arity (#113 review, Codex fifth pass).** `age_assurance:{level}:{band}:{version}` and `age_self_declared:…` enumerated the full ladder but not the word *closed*, so the registry published them open and the reference matcher admitted `age_assurance:self:adult:v1` and `age_self_declared:unknown:v1` — values CC 3.4.11 refuses by name. `{level}` is closed to `provider` \| `government`; `{band}` is closed to `minor` \| `adult` \| `under_13` \| `13_15` \| `16_17`, the CC 3.4.13 Q1 finer bands spelled as the substrate's `AgeBandFine` already spells them; `unknown` is a consumer's fail-secure resolution, never a wire token. Checking the emitters surfaced a drift Codex did not name: persist and the conformance suite carry the self-declared rung as **`age_self_declared:band:{band}:v1`**, three segments with a literal `band` marking the rung, while this Part registered the two-segment `age_self_declared:{band}:{version}` that nothing emitted — so every real self-declared row was open vocabulary to the matcher. The row is aligned to the wire and the old prefix is retired through the removal gate. The client's generated `Dim` name for the family changes on its next re-vendor; persist's vendored-family removal gate will name the retirement.

**The trust root is human-held and the installs are members — the registry-fold deconflict (#113, CIRISServer#537, CIRISRegistry#141).** A CSD/3-style pass over the Registry's fold-readiness statement resolved every token in it against the CC, the matcher and the live trackers, and found the CC still specifying the model the fold withdraws. CC 3.2's `ciris-canonical` worked example had `registry_steward_us/eu/apac` as founders and said "the three steward nodes ARE members (founders)"; CC 5.3.4 specified a per-region steward set with a self-attested HSM class and a response signature by "the serving region's steward"; CC 4.4's recommended default pinned `{us-steward, eu-steward, apac-steward, …}`; the CC 3.1.1 `cert_validity` and `agent_files` rows cited the steward triple. All re-cut on the 2026-09-22 ruling (infrastructure does not vote): founders of an `infrastructure` community are human-held keys conferred on the ceremony plane, a `node`-bearing key joins as `member` and MUST NOT be counted or listed as founder (a new normative paragraph in CC 3.2, refusal `hard_case:community_consensus_protocol_violation`); CC 5.3.4 is retitled around `GET /v1/trust-root/bundle` — the GenesisBundle, `/v1/steward-key` a kept alias, authority inside `bundle` and nowhere else, deliberately no `response_signature`, no `hardware_class` on the envelope, a signed roster's bound a liveness signal never an expiry (T4); CC 4.4's default pin is `{community_key_id: ciris-canonical, family: humanity-accord}`; CC 8.3.6's steward-key row is re-closed on the bundle. Two persist-shipped shapes the text had called drift are admitted as the text's own: T2's ceremony plane is a **family roster** co-scrub reaching its `consensus_protocol` (the accord is the shipped family) and CC 3.4.7's charter rule gains the keyless-family form (`delegates_to(member → family_id)`, self-reference by roster, family derived from the verified signers). CC 4.1.1 gains the ceiling sentence (a substrate MAY clamp at 16; the default stays 5). CC 3.1.7 R1 gains the fold rule — a fold changes `owning_repo` (previous owner recorded in the manifest, `COMPONENT_REPO_HISTORY`) and re-points anchors in one cut; a family never becomes unregistered because its repository was archived — and CC 3.1.1's steward line names the fold. The reading recorded for the maintainer: "the admission quorum is the accord's, not the nodes'" is taken as the quorum of the accord-*conferred* steward founders; if the accord holders are meant to vote admission directly, CC 3.2 and the example change together on #537. Seven claims rows stage on CIRISServer#537 and on the five persist issues filed for v50 (CIRISPersist#924 the #112 program, #925 founder eligibility, #926 the missing `ciris-canonical` community row, #927 the family-quorum plane, #928 the depth default).

**Eleven dangling links, and a gate so there is never a twelfth.** The CC was extracted from CIRISRegistry and eleven links still pointed at `../../MISSION.md`, twelve more at `../LANGUAGE_PRIMER.md`, `../../CLAUDE.md`, `../../rust-registry/…`, `README.md` from inside `constitution/` and the retired `FSD/WITNESS_KIND_REGISTRY.md` (absent from CIRISRegistry `main`, now cited by name). All resolve; `tools/check_links.py` fails CI on any relative path that does not exist. `check_claims.py` now warns per CC 3.1 slice whose `owning_repo` has no evidence pin — today Registry (17 families), LensCore (15), NodeCore (48) and the catalogued-only CIRISBench — so "no impl: row can exist" is said rather than silently true; the registry slice's first manifest is CIRISServer's after the fold, not a CIRISRegistry one that would be archived.

**Codex, sixth pass on #113 — ten findings (four carried from the fourth pass), ten fixes.** One wire member for one thing: `delegates_to` carries its scope set as the CC 2.1 `scope` member (persist has read `scope`, string or array, since v8.7.0), and the twelve `delegated_scope[]` mentions in CC 2.4, CC 2.6.1.1.1 and CC 4.4 now name `scope[]`, with the old name recorded once. The matcher treats a **version attempt** in last place — `v` + digit that is not a version (`v1beta`, `v1.`, `V1x`) — as `namespace_dimension_case_malformed` on the family the other segments name, for exact, variadic and multi-segment families alike (a bare `vx` stays a leaf name: a version begins `v` + digit); R3 says so, and the vector set gains one such case per family (924 vectors). `{lang_code}` enforces BCP 47 canonical casing (`en-US`, `zh-Hant-TW`; `EN-us` and `en-us` malformed). `delivery_receipt:{stream_id}` carries its own emitter rule — subscriber-only, CC 3.4.6 — ahead of the edge-wide substrate-self-report fallback the generator had applied to it. On the human-held root: the CC 3.2 membership bullet counts a member in `consensus_protocol` only where the protocol counts its role, never a `node`-bearing key; CC 3.4.7.1's "a co-located node gains a *vote*, never a *verdict*" is now "neither a vote nor a verdict"; CC 5.3.4 calls the bundle tamper-evident, not authentic (T5), and requires an out-of-band anchor — the pinned `bundle_fingerprint` or the holders' key fingerprints — before a cold-start consumer promotes anything, `ciris-canonical` and `humanity-accord` being names, not anchors; the H6 steward-backstop PQC keys resolve through `federation_keys` under their own `identity_type` and never through `bundle.holders`. CC 5.3.2.6's ingest pipeline is ordered size → full-SHA → sniff, as CC 5.3.2.5 requires. Age-assurance closure stays a per-row word (both placeholders of both rows are closed; the manifest carries `open` per segment). The rc5 PDF is rebuilt from this head (`rc5.19`; the build had been failing on a superscript glyph the fourth pass introduced, now mapped).

**Persist's port of the rc5 manifest found two gaps and a ruling waiting for text (#116, #117, #114).** The reverse-quorum-grade check a second implementation gives: CIRISPersist#924 vendored the registry byte-exact and replayed every vector, and filed what did not fit. **#117:** CC 3.4.12 has required the reversible-cause companions `capacity_assurance:reversible_excluded:{domain}` and `reversible_pending:{domain}` since rc3, but no CC 3.1 row registered them, so the matcher refused the very rows the ladder demands; they are CC 3.1.2 rows now (witness-reserved, versioned as the wire carries them), and the rung row closes `{level}` to `provider | panel | government` and `{band}` to `capacitated | incapacitated`, so `capacity_assurance:reversible_excluded:a:b:v1` — which the open `{level}` had admitted as a rung — refuses `namespace_vocab_value_unregistered`. The ladder block shows the `:v1` tail. Persist's `CC_TEXT_LEAVES_WITHOUT_ROWS` exemption fails its own build once it re-vendors, which is the right way round. **#116:** every segment pattern is applied whole-segment (`re.fullmatch`) so a `$` anchor never admits a trailing newline — `config:admission\n:v1` is malformed in the reference exactly as in a byte-exact port — and `_meta.case_rule.match_semantics` says so; a case-malformed form is now attributed to the registered row it mutates when that row resolves cleanly once folded or stripped (`accord:lifecycle:V1` → `accord:lifecycle`, not `accord:*`; `…:reversible_excluded:medical:v1:v2` → the companion, not the rung), so `self_test` compares `(family, refusal)` exactly and the vectors' contract no longer carries a "best-effort attribution" clause. 147 families, 940 vectors. **#114:** the maintainer's 2026-09-27 ruling is CC text: the Source struct gains `sealed_descriptor` (AEAD under the room DEK over `{name, format, codec}` as JCS, associated data the address digest); `size`, `digest`, room, `content_digest` and `placeholder` stay in clear; `format`/`codec` are in clear iff no seal and a struct carrying both is refused; the sniff runs where the bytes decrypt (CC 5.3.2.6 says so too). Persist adopts on CIRISPersist#922; three claims rows stage on #922 / #924.

**Codex, seventh and eighth passes on #113 — eleven findings, eleven fixes, landed after the merge on the rc5 follow-on branch.** Grammar: a case-mutated reserved stem (`Capacity:zz:v1`) is `namespace_dimension_case_malformed`, never a bypass (fold only to detect); open vocabulary owes the trailing version segment (`third_party:signal` → `missing_version_segment`); every component of a multi-segment value is verbatim (`provenance:skill_import:registry:v1:v1` binds `registry:v1`), so the duplicated-tail vectors do not exist for multi families and an unversioned input whose last segment is a mutated tail (`…:V1`) is malformed whatever class absorbed it; `{lang_code}` admits BCP 47's `privateuse` production (`x-acme`) and names the two productions it takes. **`consent:{kind}` is closed in its leaves as its row has always said:** the generator now encodes closure for a parameterized parent whose row says so, the nine catalogued consent leaves are its `leaves`, and `consent:totally_new:v1` refuses `namespace_family_unregistered` — the second of #112's two open consent questions, answered: no producer emits `consent:share` (CIRISEdge carries the string only as a test fixture), so the leaf is not minted. 147 families, 948 vectors. Text: CC 4.4.3.4.3.1's canonicalization no longer hex-encodes `*_key_id` / `subject_key_ids[]` (identifiers, verbatim — CC 2.6.1/2.6.8; hex is for byte fields); `/v1/accord/holders` carries no response signature and says so; the `cert_validity` row and CC 8.3.6 call the bundle tamper-evident and anchored, not self-authenticating (T5). **Session claims (CC 3.1.3.1):** the claimant's clock is bounded at admission — `claimed_at` within the ±5-minute skew of the admitting substrate, lease ≤ the community's `session_max_lease` (default 24 h), refusal `session_claim_out_of_window` — so earliest-wins cannot be won by back-dating. Gate: the ticket-state note "all staging tickets open" is emitted only when every ticket was read; a partial read says so.

**Codex on #122, first pass — four findings, four fixes.** A closed family's stem is a fence like a reserved stem: an unmatched descendant beneath `consent:` (`consent:totally:new:v1`, `consent:state:granted:extra:v1`) is `namespace_family_unregistered`, never open vocabulary, and a case-mutated closed stem is malformed. Open vocabulary carries exactly one version segment: `third_party:signal:v1:v2` is malformed. 951 vectors. The session-claim bounds are **replication-stable**: they read only signed members — `claimed_at` not before the exchange's opening instant (the earliest row carrying the `session_id`), `claimed_at ≤ signed_at ≤ claimed_at + 5 min`, and lease ≤ `session_max_lease_s` — never the receiving substrate's arrival clock, so every peer reaches the same verdict at any arrival time; the residual (back-dating within the exchange's lifetime, bounded by one lease) is stated rather than hidden. `session_max_lease_s` is a `community` record member: optional, whole seconds, JSON integer ≥ 1, 86400 where absent.

**Codex on #122, second pass — three findings, three fixes.** Open vocabulary: a version attempt in last place (`third_party:signal:V1`, `…:v1beta`) is `namespace_dimension_case_malformed` as R3 says, not a missing tail; a duplicated tail is a *version* (or its uppercase) right before the real one, so `third_party:protocol:v1beta:v2` is open vocabulary — `v1beta` is a family segment when a valid version follows it. 953 vectors. Session claims: bound (a) no longer depends on which row arrives first — a claim whose opening row has not yet arrived is **held** outside the fold (`session_claim_pending_opening`), re-evaluated when the opening row arrives, and dropped unread if its own `valid_until` passes first, so every substrate reaches the same final verdict from the same two rows whatever the replication order.

**The PDF build number is monotonic across a finalize (#122 review).** `build_pdf.py` numbered a pre-release build from the highest numbered same-version file in the tree; the finalize on main deletes that file when it collapses the name, so the branch cut from the finalized rc5 restarted at rc5.1 — a newer build with a smaller number than rc5.20. The counter now also reads every numbered name git has ever seen on any ref and the number the finalize commit records (`from <V>.N`, which `pdf-finalize.yml` now writes), so this branch continues at **rc5.21**; and the finalized bare-name file is no longer swept by a branch build — it is a published release name and the next finalize overwrites it.

**Codex on #122, third pass — three findings, three fixes.** Session claims: bound (c) reads `session_max_lease_s` from the community record **in force at `claimed_at`** (the latest record on the `supersedes` chain whose signed `asserted_at` is not after it), never whichever record is current at arrival, so a policy change neither admits nor evicts a claim already made and a claim whose covering record has not replicated is held like (a). `{lang_code}` says what it takes rather than claiming a production it does not: RFC 5646 `langtag` without the `extlang` branch, or `privateuse`; an extlang form (`zh-cmn-Hans-CN`) is written as its §4.5 preferred value (`cmn-Hans-CN`), the one canonical spelling. The partnership envelope's own member mapping (CC 4.4.3.4.3.1) no longer calls `attesting_key_id` / `subject_key_ids[]` hex byte fields — identifiers, verbatim, as the paragraph above it already said.

**Codex on #122, fourth pass — five findings; the session rule is cut back rather than patched again.** Three of the five were the same objection from three angles: a bound that reads a row other than the claim — the opening row, the community record in force, a receiver's clock — is order-dependent unless the claim pins that row, and CC 2.1 gives a claim no member to pin with (there is no `signed_at` member either, which bound (b) had cited). So CC 3.1.3.1 now imposes **one self-contained bound**: `valid_until − claimed_at ≤ 86 400 s`, read from the claim alone, the same verdict on every peer in any order; peers never re-apply an arrival-clock check to a replicated claim; the residual (back-dating within one lease) is stated; the per-community lease and the opening-row anchor are named as persist's to propose under #98 once the envelope carries a pinned id, and `session_max_lease_s` is withdrawn from the community record. `{lang_code}` admits the five grandfathered tags the registry gives no preferred value (`i-default`, `i-enochian`, `i-mingo`, `cel-gaulish`, `zh-min`) literally; every other grandfathered or extlang form is written as its §4.5 preferred value. `pdf-finalize.yml` captures the collapsed build number in the state step, before the rebuild sweeps the numbered files, so the finalize commit actually records it.

**Existing consent rows keep working: `consent:community_trust` is catalogued (#122).** Closing `consent:{kind}` in its leaves was checked against every downstream tree, not only persist. One live wire leaf was uncatalogued: `consent:community_trust:v1`, the node owner's trace-capture grant CIRISAgent has emitted since 2.9.6, lens-core gates every seal on, CIRISServer promotes and persist's admission tests carry. It is now a CC 3.1.5 catalogue row and a CC 3.3.1 leaf (positive-only; emitter the owner-binding chain, self-or-owner; `withdraws` a hard stop under the CC 3.3.9 fold) — catalogued, not minted; the row says so. 148 families, 960 vectors. The four other spellings found are not wire rows and need no CC row: CIRISEdge's `consent:share:v1` is a test fixture standing in for the Consent family gate (edge moves it to a catalogued leaf when it replays the vectors — #112's edge list); CIRISAgent's `consent:partnered:abc123` is a memory-graph node id in an XSS test; CIRISClient's `consent:revocation` and `consent:delegation` are display binds in CSD-090 / CSD-001 that the CSDs themselves already mark as not leaves (the CSD/3 checker refuses them once it reads `leaves_closed` — #112's client list).

**Codex on #122, fifth pass — three findings, three fixes.** `consent:community_trust` gets its own fold rather than a pointer at CC 3.3.9's org keys: rows group by `attested_key_id` (the node), a `withdraws` / `recants` removes a grant forward-only, latest `asserted_at` among the survivors wins, ties on the smallest attestation id; capture resumes only on a fresh grant from the owner-binding chain, and a row from outside that chain is not the node's consent. A version attempt may carry any vocabulary byte after `v` + digit (`v1-beta`, `v1_beta` are malformed, not missing). The PDF build floor lives in the tree: `ciris_constitution.build` records `<VERSION> <N>` on every numbered build, so a depth-1 checkout that sees neither the deleted numbered file nor the finalize commit still continues the count.

**Codex on #122, sixth pass — three findings, three fixes.** `consent:community_trust`: a revocation is a fold **boundary**, not a deletion — every grant asserted at or before the latest revocation is out, whichever row the revocation named, so revoking the newest grant never resurrects an older one; and the owner can always revoke — a node-emitted grant MUST list its owner in `subject_key_ids[]` so the owner's `withdraws` is admitted on the CC 2.4.1.1 third-party path. Session claims: `claimed_at ≤ valid_until` joins the 86 400 s ceiling, so a lease runs forward from its claim.

**Codex on #122, seventh pass — three findings, three fixes.** `consent:community_trust`: the owner a node-emitted grant must list is `owner_of(node)` **at the grant's own `asserted_at`**, resolved over the replicated owner-binding rows and never the receiver's current view, so an ownership transfer neither admits nor un-admits a grant already made; the listed key keeps its revocation seat whatever ownership later becomes, and a new owner re-grants rather than inheriting it. Open vocabulary needs a family segment before its version: `v1` and `v1:v2` are malformed (962 vectors). The session rule's clock exception cites CC 2.6.7, where the ±5-minute rule lives, not CC 2.6.2.

**Re-pin 5 (2026-09-27): server `046e1b3`, persist `a5965d4` (v49.0.0), edge `28c5295`, RATCHET `38933ef`; five rows graduate on verify; every rc5 ruling row moves to the repository that implements it.** Verify's manifest at `cdc6498` already carried the five #101 decimals, so `CLM-subject-binding`, `CLM-subject-binding-keyrecord`, `CLM-scope-destination`, `CLM-key-validity-window` and `CLM-keyring-rng-latch` are established on their symbols (the sixth, the v2/v3 FedCode encoder, waits on CIRISVerify#297). Persist v49 resolves every established row and flips none of #803's. The nine rows that had been staged on this repo's own ruling issues (#100 ×5, #96, #97, #98, #101) now stage where the code is: CIRISPersist#935 (the licensure triad, scope attenuation, `key_grant` issuance, `session:*`, self-report routing, `duty`, and `consent:community_trust`'s fold), CIRISServer#691 (operational relief) and CIRISVerify#297 — a ruling issue here is closed when its text lands, and its row's anchor is the implementing ticket, never the ruling. The #112 program now has an issue in every repository it names: CIRISPersist#924, CIRISServer#691, CIRISVerify#297, CIRISEdge#706, CIRISClient#114. The six rows #112 had staged on itself move the same way — matcher and minors rows to CIRISPersist#924, the accord kinds and hardware vocabulary to CIRISVerify#297, the roster announce to CIRISServer#691 — so #112 can close as the program's index rather than stay open as an anchor.

**The rc5 release criterion, stated (2026-09-27).** rc5 opened promising to flip "the 38 staged rows that earn it"; the cut has since staged 73, because every ruling and every review round stages what it cannot yet prove. The criterion is therefore restated as what the release actually needs: (1) the rows staged on the four tickets rc5 named — CIRISConformance#90, CIRISServer#536, CIRISPersist#803, CIRISAgent#1139 — graduated or the ticket closed with the row re-anchored (Agent#1139 is done); (2) every evidence pin at its upstream head at the cut; (3) the three rc4 rulings landed as text (done) and anchored on implementing tickets (done); (4) every remaining `staged` row anchored on an **open** ticket in the repository that owns the code, which the ticket-state gate enforces. Rows that stay staged under (4) ship in rc5 as what they are — claims the Constitution makes and the substrate has not yet proven — and the register says so per row.


## 1.0-rc4 — the actor/substrate line, ledgers as content, and every row resolving

**Evidence lockdown — every row resolves or names an open ticket.** All eight pins re-vendored at heads (persist v40.0.0, edge v20.0.0, verify v14.1.0, agent v2.9.48, server 0.5.196, RATCHET, coherence-ratchet; conformance already current). The two closed manifest-tracking tickets (CIRISConformance#59, CIRISServer#155) are retired as pointers — 139 rows rewritten from section-level placeholders to the symbols and node ids the pinned manifests actually publish, under a strict rule: a manifest row naming a *different* claim id is that claim's evidence, never this one's. Seven rows graduate on real artifacts (the ledger pair on persist's `src/ledgers/standard.rs`, reverse-quorum on `test_271`/`test_272`, age-assurance, registry-canonical, affiliations, cohabitation); none demote — the sibling manifests back every decimal Server and Conformance do not reach. Thirty-nine rows remain `staged`, all on open tickets: the per-repo evidence asks (CIRISConformance#90, CIRISServer#536, CIRISPersist#803) plus #9, #40, #43, #71, #88, #93. `CLM-noise-N5` moves to 6.1.2, where RC3 put the rule and where conformance publishes the test. Nine toc title drifts repaired. CC 2.1 no longer names an `accountability:mode_shift` dimension — a mode shift is a superseding `delegates_to` on the delegation plane, and accountability is structural (the D23 design), so the family was never one to mint. CC 1.13.4 gains the kinds-of-change map shared with RATCHET: the 27 compliance dimensions are the Record's vocabulary, each *about* one or more of the eleven kinds; Manner and Circumstances are thin on purpose (context, carried by envelope fields), and the deep kinds want instruments, not a 28th dimension.

**CC 3.4.7.3 — the actor/substrate separation (#95, ruled).** CC enforced one direction of the
node/agency split and was silent on its converse: a node-only key may not *receive* agency, but
nothing stopped an actor key from *being* the infrastructure — and the live agent topology fused
both onto one key, so `owner_of()` resolved a person to an actor where a node was asked for. Worse,
the escape was legal: CC 4.4.3.4.3's conformance rule fired only on `node`-**only** recipients, so
adding `agent` to a node's role-set repealed the invariant — **the loophole was spelled as a
simplification**. Ruled in six clauses: `node` is exclusive of `agent`/`user` (A); the gate reads
**set membership**, never purity (B) — both required, since A stops a fused key being minted and B
protects against the ones that already exist; the actor↔node relation is **entailed, never
asserted** (C) — neither party has standing, so the pairing derives from two human-signed edges and
cannot be forged by either side; the common-human predicate `∃h. h=owner_of(node) ∧ h ∈
stewards_of(agent)` (D), existential because node ownership is single-valued while stewardship is
multi-parent, fail-closed on unresolvable; the enforcement seam is the **node's** (E), because
infrastructure holding no agency is exactly what can be trusted to refuse it — an actor gating
itself is the constrained party checking its own constraint; and fused keys are **non-conformant,
not deprecated** (F), forward-only so history stands, and still refused agency meanwhile.
Amended in the same cut (CIRISPersist v38.6.0, ffa6608): `stewards_of` is the **custody** set, never the conferral set — for a key that can accept for itself the delegation half counts only where the envelope declares custody (#87), so an unmarked delegation is a job and MUST NOT satisfy Clause D; and the cardinality is the occurrence half plus **one** custody claim, a second distinct claim being refused at bind time. That withdraws this section's first, too-broad statement that co-stewardship expresses multi-tenant hosting: only two shapes are admissible, and the deferred space is most of multi-tenancy rather than an exotic corner. Also repaired: the
"infrastructure must not have agency" rule was cited **four times** at CC 1.13.5 — the
operational-language gate, which says nothing about agency, and which a substrate implementation
had already inherited into its own doc comments. 3.4.7.3 is now that rule's numbered home and all
four citations repoint to it. `CLM-actor-substrate` / `CLM-common-human` staged.

**CC 1.13.6 — the durable trace anchors on the act, not the deliberation (normative).** An assurance
finding the substrate passed *by behaving as designed*: an aged `THOUGHT_START` with no
`ACTION_RESULT` is purged, and nothing in the compliance surface said that was deliberate. The
defect was documentation, so the repair is a stated position. Traces anchor on the terminal
`ACTION_RESULT` — no action, no trace — because accountability attaches to acts, and because
retained deliberation would be a permanent archive of unexecuted thought carrying the
conversation's humans at their most exposed while carrying no accountability weight (CC 1.9 requires
an agent free to consider and reject). The safety argument is reduced to one attackable invariant:
*absence of an `ACTION_RESULT` asserts no external effect occurred* — so the sweep can only ever
discard deliberation that produced nothing, and any counterexample is a defect in the emission path,
never in the purge. Stated as a **named wager** (#84 discipline) with its falsification condition and
its dye test — a totality test over effect-producing paths, explicitly *not* a retention test on
thoughts — filed at #93, plus a rate-observability requirement on the purge and an honest residual
on interrupted-path forensics. `CLM-trace-anchor` staged.

**CC 3.3.10.1 — in-grammar ledgers: owner-serialized content, cohort-witnessed conservation (#92).**
The ballot machinery extended to value, on a three-track prior-art sweep (theory, channels/mints,
mutual-credit practice). Total order lives in the owner's hash chain, never the grammar (CC 3.2
single-owner ⇒ consensus number 1, Guerraoui PODC 2019 — which also corrects the stance's dated
"no totally-ordered ledger" premise; the real exclusions are named in-text). Nine normative
clauses: identity/unit binding, dense hash-chained entries, delegate serialization, witness-anchored
heads with the cadence stated as the equivocation-exposure window (SUNDR's 2004 "time stamp box";
CT's failed voluntary gossip is why the anchor is an obligation), checkpoints riding §19.7 descent
(the regulator-endorsed summarize-and-delete shape), promotion-with-proof, the deterministic
byte-equal conservation fold (Sardex's zero-sum invariant; PeerReview's transferable evidence),
fork-as-adjudicated-slashing with mandatory restore-then-resync (the eltoo critique answered —
available because the witness set is cooperative), and the non-claims (no atomicity, no
member-vs-member privacy, no cross-cohort conservation — netting + net rail settlement, the
CLS ~96% pattern). 1+4 lockdown holds: rides scores + subject_kind + evidence_refs + supersedes +
cohort_scope. Staged claim rows on #92 / CIRISPersist#754. The attempted-systems record lands
verified: Holochain's 8-year gestation vs NetzBon-on-Taler's two; SSB/Hypercore fork-death
answered by L8's mandatory resync and L3's Keybase-shaped in-chain delegation; Sardex's
load-bearing brokers hooked to the named-moderator invariant; Circles' rail-boundary death
shaping the netting guidance. Closed with the kernel note: each application is the club-bounded
sibling of its famous problem, the novelty budget spent once on the deployed two-plane kernel.
CC 5.4.6 Position additionally adopts the lightnet/darknet name the transport implementation
already carries, closing edge's dangling citation. *Lightnet settles; darknet transacts.*

**CC 5.4.6 — a directed announce inherits the prohibition (#91, ruled).** The first RC4 revision.
The clause binds the emission, not the addressing mode: on Reticulum transport no directed announce
satisfies the purposive sentence — multi-hop path learning *is* outsider observation (path state a
subpoena reaches), and the epoch-bound derivation forces either a roster-wide re-announce wave on
every Add/Remove or a removed member keeping every peer's addressing indefinitely. The flat MUST NOT
was never broadcast-era shorthand — the same section bans the targeted, non-broadcast per-destination
query in the same breath. The trade on offer was a structural, claimable guarantee for a
traffic-analysis-statistical one — a claim base CEG/RET declines to make (CC 1.13.3.1; the goal
stands, the Anonymous Tier is its opt-in). The leak reading's sound insight is kept in-text:
in-group MLS distribution of addressing material was never prohibited. Multi-hop scoped reach is an
amendment-plane design question with its bar stated in-clause.

## 1.0-rc3 — the external-review remediation, the trust-root ratifications, and an honest matrix

RC3 closes the open issue set. Where an issue asked for a ruling, this cut gives one; where an
issue was wrong, the disposition says so. Provenance, review archaeology and superseded text live
in the GitHub issues and on Zenodo — not in this document.

**Part VI — the math corrections (#50, #45, #26, #34, #35, #6).** §6.2 is demoted from
justification to **capacity analysis under chosen constraints**: the collapse geometry cuts honest
and deceptive regions alike, so the asymmetry lives in the choice of constraints, not in a
theorem's gift. The reviewer's contradiction is real and is fixed at the root — J = k_eff·λ_op·σ is
a *throughput index* monotone in diversity, maximised at ρ̄ = 0, and it **MUST NOT** be cited as the
corridor's basis. **No operating corridor is stated at all**: the campaign's own k ≥ 4 positive floor means the
poles-are-zero basis does not hold in the regime CC needs, so §6.2 declines to re-found a corridor,
voids any band appearing in a derived document, and an implementation MUST NOT gate on one. The σ recurrence was a conformance
bug — not step-invariant for interior signals, yet carrying a MUST that implementations agree at
Δt ∈ {1, 25, 400} days, which is unsatisfiable as written; the event-time form is now the rule, and
conformance MUST include a strictly-interior signal, since those three deltas cannot discriminate
the two forms. The §6.1 fountain sentence is corrected (RaptorQ is all-or-nothing at block level;
graceful degradation belongs to the layered codec) and the noise-floor default re-founds on the
layered-codec fidelity metric. #6 is addressed without being closed: the MUST now binds relative to
a pinned adversary model, and the side-informed limb is marked unverifiable-pending-instrument.

**CCA is no longer cited as authority.** CCA v5 withdraws its own validations — k_eff hardware
checks reclassified as identity checks, institutional application re-scored below chance, collapse
asymmetry "assumed, not derived". No "CCA-validated" label attaches to any claim in §6.2; v5 is
cited for the surviving Möbius/ceiling core only.

**Part VIII — the traceability matrix stops flattering itself (#50 item 7).**
`remainder_scales_with_k_eff` is re-graded to *theorem-given-model, remainder only*: it bounds the
remainder order of an assumed decay law with substrate-specific free constants. It does not
establish the decay law, and nothing in the corpus establishes the collapse asymmetry. Kish and the
ceiling are *identity*; J = F is *identity*. §8.6.1 is populated with the borrowed instruments, and
the priority claim is retired positively: **the claim is application, not discovery.**

**Part I — the keeper thesis (#32), scoped to what is evidenced.** A recognition-grade preamble
paragraph, and "what M-1 does not contain": no aggregation rule, no ranking of losses, no
superlative derivable. M-1 does not launder witness into theorem.

**Trust, consent and contextual integrity (#48, #46, #47, #49, #40, #44).** Trust-root operational
semantics ratified: two named conferral planes, un-trust as one deletable acceptance edge with
everything downstream failing closed emergently, and **liveness as a reported signal that MUST NOT
be ANDed into validity** — a root is valid until revoked, superseding an RC2 reading that would
have darkened the mesh at once. Consent-before-scoring for `capacity:*` is **ratified**
(CC 3.4.5): family-scoped, community-addressed (root-addressed consent is consent to an
unenumerable set), enforced at federation-tier admission on a live `consent:scope:analyze` grant,
with the role-gated abuse-response families exempt because an abuser never consents — the rule the
shipped substrate already enforces, so the spec and the mesh agree. The fourteen verify attestation
families are dispositioned per family (none consent-gated: they verify artifacts, not agents). The
**read boundary** remains reserved design space, tracked at CIRISConstitution#49.
`hard_case:deletion_window_breach` is evidence, never a verdict; no affirmative `deletion_proof`
artifact, which a producer could emit while retaining the bytes. The swap test becomes a
mandatory drafting gate, and bootstrap is handled by *building* the declared-asymmetry register
rather than leaving a silent exemption.

**Wire hygiene (#41, #38, #37, #30, #42, #43, #39).** The CC 2.3.2.1 canonical-subject preimage is
pinned byte-level (all five golden vectors verified to reproduce; no digest changes). A 1 MiB
canonical-bytes bound lands at CC 2.6.1.3, enforced at every write path — Part V's fixed 1.4 KB
envelope is a traffic-analysis rule that chunks rather than refuses, so it bounded nothing at
admission. One canonical spelling is frozen for the hybrid construction, chosen on repo evidence
rather than preference, together with the class rule that prevents the next collision. `C_CIRIS`
becomes `min(...)`: the five-factor product scored positive whenever an even number of factors were
negative, inverting the anti-Goodhart rationale it exists to serve. Family counts are now
**generated, not asserted** — `manifests/namespace_registry.json` is the registry of record, and the
generator's hard-coded expectation is removed so the number cannot go stale again.

**Declined or deferred, on the record.** Dead-clauses-keep-their-killers (#49-A4) — declined;
errata live in git, GitHub and Zenodo. The proof-centipede witness format (#36) — deferred to 1.1;
ratifying a paragraph does not make a format real. The `lp()` re-spelling of the canonical subject
(#41 comment) — declined; it crosses the CC 6.1.3 seam and re-spells every ratified digest to buy a
property the colon-ban already gives. The severance window on the halt fire path (#40 comment) —
declined; it hands the halted party an escape at the instant the brake is pulled.

**Deferred to the post-1.0 candidate backlog, on the record (the #36 principle: ratify the format that survived, not the one specified).** #32's asks 2-5 — the six consent-foundation `lean:` claim rows, the `need:survival:*` reserved domain with the one-card mandate, and the totalitarian-case proxy-promotion composition — are deferred with successor issues; only the keeper thesis (ask 1) landed in this cut. #57 (mesh-config authorship) is **reserved, not designed**: CC 4.2.1 now forbids an implementation deriving the authority from silence, and the model ratifies on the issue's sketch. #58 (graded enforcement tiers), #59 (reverse-quorum objection form), #60 (volume standing + `revoked_after`) are deferred with their proposal sketches recorded on the issues — each has no implementation whose survival could be ratified, and #60's own caveat (a naive rate cap is a censorship primitive absent a reserved admission class) is the reason not to ratify it from the armchair. #49-A1 (the `capacity:*` read boundary) is deferred at CC 3.4.5 with the non-conformance rationale stated in-text.

**Not discharged, and marked as such.** #49-A2's anti-forking binding did not survive drafting:
CC 1.15.5 states covenant identity recognition-grade and explicitly declines the binding (no
lineage dimension family exists, moderation records are relative and positional, and nothing
bounds keys per owner — a whole-or-nothing rule would quantify over a unit the subject itself
partitions); the wire-level design is tracked at #49 and the claims row is `staged` against it. #50 item 8 — commissioning
external reviewers with standing to kill sections — is not a document change and remains open; it
is the one item nobody inside this ecosystem can substitute for.

### Machine-generation disclosure becomes mandatory (#9, EU AI Act Art. 50(2))

**CC 3.4.14 `synthesis-disclosure` (new, normative).** Marking AI-generated content is no longer a
planned interoperability profile — it is a MUST, discharging EU AI Act Art. 50(2)/(4) (applicable
2026-08-02) with **zero new wire surface**. The rule rests on what CEG already does: attest a source.
R1 makes `content_class:generated` / `content_class:generated_modified` mandatory on every
Contribution carrying generated or materially-altered content, from any attester; R2 binds the
agent-produced case to an `identity_type` containing `agent`, so machine origin is readable from the
signed envelope rather than from a self-declared flag; R3 requires the marking to survive egress to
non-CEG channels, with an unmarkable channel recorded as a `hard_case:*` exception rather than
silently dropped; R4 carves out assistive operations (a disclosure that fires on every spell-check is
not a signal); R5 puts the duty on the generator, keeps false marking on the existing false-attestation
evidence floor, and leaves verdicts with the WA quorum. `generated_modified` is a canonical addition to
`content_class`'s existing open vocabulary (documentation-only per CC 4.5.1.1), and CC 3.3.12's
`content_class` is clarified as not multimedia-scoped — it reaches text.

**CC 8.4.2 C2PA profile — ADOPT → adopted, emit limb normative.** The profile's `MAY` is promoted to
`MUST` for generated media as the media-egress form of CC 3.4.14 R3; the AI-generation disclosure
named descriptively in the CC 3.3.13 multimedia Source structs is marked mandatory with a fail-secure
default (absent/unknown on an agent-attested Contribution resolves to *disclosed as generated*).

**Compliance-mapping corrections.** The CC 4.5.2 regulatory table filed training-data transparency
under EU AI Act Art. 50; that is Art. 53(1)(d) (GPAI) — the row is split and both are now pointed at
the primitives that actually carry them. The CC 8.3 conformance row for Art. 50 moves from
*Informative* to *Evidence-bearing (staged)* — the normative rule is cut; the emit is unshipped and
tracked at CIRISConstitution#9.

**Conformance pin.** For the text outputs the platform generates — the only synthetic content any
shipped path produces — the Art. 50(2) machine-readable marking is the **shipped attestation
surface itself** (`is_bot` on every agent message + the admission-enforced signed
`identity_type: agent` binding), marking by construction rather than add-on. The **C2PA emit** is
the media-egress interop limb: no shipped path generates synthetic media, so it is pre-staged, not
overdue — its claims rows are `staged` against CIRISConstitution#9 until a generation path exists
for it to mark. Normative coverage holds at 100% (134/134 sections).

## 1.0-rc2 — evidence registry, two new invariants, and the coherence math finalized

Consolidates the post-review work into the release candidate.

**Evidence registry (spec as executable infrastructure).** New `constitution/EVIDENCE.md`
(tag vocabulary), `constitution/claims.tsv` (146 load-bearing claims), and
`tools/check_claims.py` — a CI gate (`.github/workflows/consistency.yml`) that validates
evidence pointers, the dual-ID spine, and normative coverage. Coverage **132/132 sections
(100%)**. Cross-repo `impl`/`test`/`lean`/`bench` pointers resolve by CC decimal against
five **pinned, vendored** sibling manifests (CIRISServer, CIRISConformance,
coherence-ratchet, RATCHET, CIRISAgent): **116 pointers resolved, 118 claims established**.
A generated **Evidence Register** appendix is rendered into the PDF. The checker also caught
and closed real drift — **29 prose sections** were missing from `toc.tsv`/`codebook.json`
(reconciled; spine 400 → 429; drift now a hard error).

**Single-owner invariant (CC 3.2).** Closes a grindable ownership-resolution leak: node
ownership is the single-valued `delegates_to(user→key, purpose: owner_binding)` sub-relation
(distinct from multi-parent act-on-behalf/hierarchy); `owner_of` is purpose-filtered → at
most one; admission-time reject of a second distinct owner; consumers fail-closed on
cardinality ≠ 1 (no `.next()` a sorted set); no permanent ownerless lock. Adversarially
validated (grind CLOSED).

**Detection discriminator (CC 3.4.8).** Pins the wire discriminator as the prefix contract
itself — any `detection:*` row is a primary emission requiring `lenscore_detector`;
cross-attestations ride `truth_grounding:detection:*` — so the persist admission gate is a
blanket reserved-prefix rule with no envelope parsing.

**Coherence mathematics finalized (CC 6.2.1 / 6.2.3.1).** Both upstream-open questions are
now mechanized in Lean. The collapse remainder is **`O(r²·k_eff)`** (not `O(r²·k)`) —
`remainder_scales_with_k_eff` — so the bound is uniform in `k` and the crossover pathology
dissolves. The **σ signal-source Kish discount** (`Signal_eff`, `clique_neutralization`)
lands normatively at 6.2.3.1, closing the colluding-clique σ-pump. Honesty caveats preserved
(substrate-specific constants; the full source-attributed provenance-vector state-shape is a
stated future refinement).

VERSION → 1.0-rc2.

## 1.0-rc1 — 1.0-readiness gap register (G-A…G-G) + finalized front matter

The seven-gap pre-1.0 register, applied with exact fixes, plus the finalized executive summary.

**G-A (BLOCKER) — live-quorum roster-capture (CC 4.2.6).** Closes a defeat of the HUMANITY_ACCORD
kill switch through its own recovery path: an adversary capturing a strict live majority and censoring
the honest minority through the participation window `W` could remove honest holders (the old
steward-cosign trigger only fired at `\|L\| < L_floor = 3`, which stopped scaling as the roster grew).
Four additive fixes: (1) a **scaling removal-gate** — any roster change that *removes* a standing
holder needs the 2-of-3 steward co-sign whenever `2·\|L\| ≤ N_standing`; (2) **fire-authority
persistence** — a holder named for removal keeps floor-of-1 fire through a lame-duck window;
(3) **contest is a duty** — a removed holder MAY contest within `W` **or post-`W` on immutable
append-log evidence**, the steward quorum MUST adjudicate within a bounded SLA (72 h / 7 d) and MUST
restore on a seizure finding; (4) the entrenchment proof corrected to state the capture partition
honestly. Adds the `accord_contest` / `accord_restore` canonical-bytes domains and the log-snapshot
verify-resolution carve-out for off-roster contestants. Adversarially validated:
PARTIALLY-CLOSED → fixes → **CLOSED** (attack no longer achieves permanent disablement; the surviving
bounded steward-restore dependence is named).

**G-B — noise-floor overclaim (CC 6.1.2).** "Information-theoretically unrecoverable" → **not
individually recoverable by the specified procedure `R` above fidelity `ε`**; `(R, ε)` operator-tunable
with a pinned default + conformance vector; the `< 1/N` claim caveated to non-dominated composites.
New acknowledged risk **R9** (composite invertibility) in CC 8.3.1.

**G-C — Order-Maximisation Veto (CC 1.3).** "→ abort action" → **mandatory WBD deferral** (CC 1.9): the
10× ratio triggers human judgment over incommensurable estimates, not an unfalsifiable MUST-abort.

**G-D…G-G (editorial).** Kill severity-dial paragraph (missed fire terminal / false fire recoverable)
at CC 4.2.6 + cross-ref from 4.2.3; "coherence signal" defined in CC 8.1.1 by what it measures (kills
the σ integrand circularity); σ constants `d`/`w` marked initial operating values pending calibration;
the HF/Reticulum relay backbone indexed as a deferred row in CC 8.3.6.

**Doc precision (folded in — closes #8, #10).** Annex C statutory mapping consolidated to adopted
**Regulation (EU) 2024/1689** numbering (post-market monitoring **Art 61 → Art 72**; added Art 10 / 15 /
16 / 50 rows; 2 Aug 2026 applicability). The `DISCRIMINATION` prohibition is described at its true
enforcement point — the **WiseBus capability gate** (`NEVER_ALLOWED`), with the prohibited-capability
set injected into the round-1 DMA reasoning context (CIRISAgent#910) — not "PDMA Step 1"; the Art
10(2)(f)/Art 9 evidence is the bus-rejection log **and** the DMA reasoning trace.

**Front matter.** Executive summary finalized: running-system framing ("this is not a proposal"), the
safety thesis stated as a bet (plurality, never a singleton; correlation not headcount), and Part 8 as
the standing weakness register.

**Ratification note.** G-A amends the **entrenched** CC 4.2 HUMANITY_ACCORD surface; per CC 4.5.1.2 an
entrenched change requires a MAJOR version bump **and** a dedicated accord ratification — pre-maturity,
the founder/accord-holder authority, exercised via an out-of-band ceremony. Tagged **1.0-rc1** pending
that ratification; tagging 1.0 is the steward's ratifying act.

## 0.9.3 — executive summary: mesh-safety thesis + what the assumptions rest on

Reframes the executive summary around the whole-mesh safety thesis: this is the
constitution of a decentralized network (CEWP — the internet without the centralized
middle), safety is a property of the diverse federation rather than any single aligned
model ("a singleton is a condition to be prevented; the parts, together, are what is
safe"; check the behavior, not the weights). Adds an explicit "what the safety
assumptions rest on" section — the Part VI correlation-not-headcount mathematics, its
narrow engineering-tier import from coherence-ratchet, its falsifiable/open status, and
that current empirics strengthen it. No normative change.

## 0.9.2 — executive summary revised: consent-reaching-all-agency-surfaces framing

Revises the executive summary to lead with *why*: consent-based governance must touch
every output surface a frontier system's agency can reach, checkable at the point of
expression. Trims the apex language to a single M-1 mention; adds an explicit statement
of how the science (coherence-ratchet) relates to the law — narrow engineering-tier
import, public retractions upstream, the seam explicit so neither corrupts the other.
No normative change.

## 0.9.1 — executive summary in the front matter

Adds `constitution/EXECUTIVE_SUMMARY.md` — a one-page plain-language statement of
what this document is and why (the README's register, inside the document itself) —
placed before the Foreword in the built PDF. No normative change.

## 0.9 — CEG replication storage-contention axis (§Q, seed-blocker)

Closes the last replication gap before mesh seed: replication was specified by **wire type**
(CC 5.3.2.3), **membership** (`cohort_scope`), and **consent** (`consent:replication`), but had
**no rule for resource / storage contention on an owned node** — no owner budget, no pin, only
reactive eviction after content had already landed. New normative section **CC 6.1.5.2**
(`storage-contention`, §Q) adds the missing 4th axis (the IPFS-pinning model), sourced from
CIRISServer `FSD/MESH_REPLICATION.md §3.3` and twinned with CIRISServer#145:

- **Pin classes / pin-on-consent (B1–B2).** Identity/consent/config always pinned; corpus is
  pinned iff a `consent:replication` grant authorizes its `subject_kind` **and** the owner elects
  to spend budget on it — else it is cache (GC-eligible, descends first). The grant's
  `attestation_prefixes` grammar is extended to name corpus classes (reciprocal note at CC 3.3.7).
- **Owner budget, per `cohort_scope` (B3).** A new signed `StorageBudgetV1` declares per-scope
  `budget_bytes` + `pin_reserve_bytes`; `self`/`family` scopes are suppressed from the wire
  (CC 5.2 structural invisibility); supersedable by monotonic `revision` (anti-rollback).
- **want/have + size cap (B4).** A new signed `CorpusWantV1` makes large corpus wanted-then-pulled,
  never unsolicited-pushed; content-addressed (CID) for free dedup.
- **Arbitration + consent supremacy (B5–B6).** Deterministic descent order (cache → low-rarity →
  oldest revision); budgets are consumption-challengeable (no forged-budget force-evict); a pin
  **never** defeats revocation (N5 still forces descent below the floor regardless of pin).

Both `StorageBudgetV1` and `CorpusWantV1` are CC 6.1 substrate shapes (16-byte domain separators,
hybrid Ed25519+ML-DSA-65, verify-at-ingest, #57 freeze-gate vectors) — **not** CC 2.1 attestations,
so the 1+4 surface is untouched. Given its own skeptical validation: REJECT (9 issues) → fixes →
ACCEPT (results.csv + MANIFEST addendum). Wired into CC 6.1.2 pressure sources and CC 6.1.2.3
`EjectionVerdict`.

## 0.8.1 — coherence-math errata (σ decay + λ symbol split)

Two bounded corrections to the Part VI coherence mathematics, surfaced by a
review of the 0.8 migration and pressure-tested before landing:

- **σ update rule → continuous exponential decay (CC 6.2.3).** The printed
  linear recurrence `σ·(1 − d·Δt)` went negative for `Δt > 20` days (flipping the
  sign of `J = k_eff·λ_op·σ` for a node rejoining after a long partition — the
  decimation-recovery case) and, more deeply, was not a semigroup, so peers
  polling σ at different cadences over the same signal stream desynced. Replaced
  with `σ(t+Δt) = σ(t)·exp(−d·Δt) + Signal·w` (`d = 0.05`/day, continuous rate,
  decay before signal), with normative **step-invariance**, **right-to-return**
  (a rejoining peer never scores below cold-start), source-semantics, and a
  recalibration note. `d` is now a continuous rate (half-life ≈ 13.9 d).
- **λ symbol split (CC 6.2.1 / 6.2.2 / 6.2.4).** The collapse theorem's geometric
  decay rate (`λ_geo ≈ 2r`, deceptive-region radius) and the operational
  strictness knob of J/F (`λ_op`) were one glyph; now split, with a normative
  MUST-NOT-substitute clause. Added a **saturation note**: past the Kish ceiling
  `k_eff ≤ 1/ρ̄` the collapse bound is uninformative, so only lowering `ρ̄`
  (genuine diversity) — never adding correlated constraints — tightens the floor.

σ is a locally-computed metric and enters no signed/byte-exact preimage, so this
is behavioral errata, not a wire change. Deeper items (a noise-floor adversary
model, signal-source correlation discounting, the O(r²·k) error-term form) are
tracked as issues, not bundled here.

## 0.8 — Book IX migrated into Part VI; honesty & pointer-hygiene pass

Migrates the Accord's **Book IX** (1.3-RC2, post-cleanup) into **Part VI** as a new chapter
**CC 6.2 — the coherence mathematics**: the constraint-manifold ratchet and topological-collapse
theorem, the defense / flourishing functions `J = F = k_eff·λ·σ`, the sustainability integral σ,
and the normative **σ-attestation requirement** (CC 6.2.3.1). Only the surviving F-form engineering
tier is carried — the upstream-retracted universal-scale material (grace / joint-backward pass) is
excluded by construction. Repoints the previously-dangling "Book IX §5.2" citation (Annex G) to
CC 6.2.3.1, and extends the dual-ID codebook (392 → 399 concepts). Also carries the **C/F**
nomenclature note where `𝒞_CIRIS` is introduced (CC 3.1.8.1); adds the pointer-hygiene notes
(Piece 10 *karma* precision; the A0–A4 autonomy-tier vs A0..A5 substrate-rung scale
disambiguation); and, per the corpus's own honesty discipline, restates the migration record as
**source-fidelity validation under a skeptical rubric** rather than "adversarial certification"
(the evidence is unchanged; only the framing is corrected).

## 0.7 — wire vocabulary as a hash-pinned artifact

Introduces the two-tier wire-vocabulary governance hook (§2.6.4, no new section) plus the
[`manifests/WIRE_VOCABULARY.md`](manifests/WIRE_VOCABULARY.md) registry artifact: **Tier-1**
CC-ratified load-bearing message types (amended via the ordinary §4.5.1 "Standards Action"
path) and **Tier-2** opaque `kind`-range channels delegated per-repo ("Private Use"), grounded
in the RFC 8126 / Nostr / Matrix / AT-Lexicon prior art. The vocabulary is a hash-pinned
manifest; migrating a type to Tier-2 moves its schema, canonicalization, and convenience API
into the range steward's own repo.

## 0.6.1 — CEWPOS object-model review batch

Ratifies / doc-fixes the CEWPOS object-model review findings (#116–127) and triages the
demand-pull backlog (#118–129): fair-exchange narrowed to trustless atomic swap,
canonicalization totality, the Order-Max-Veto reasoning ruling, record/legal-recognition
clarification, and acronym doc-fixes.

## 0.6 — adult-incapacity stewardship, child-safety rulings, HUMANITY_ACCORD H6/H7

Adds adult-incapacity stewardship (§3.4.12 — capacity-assurance, prior-will-first,
least-restrictive per CRPD Art 12, fail-to-liberty auto-restore); seven child-protection
rulings (§3.4.13); the HUMANITY_ACCORD key-independent steward floor (H6) and
restore-to-known-good entrenchment exception (H7); and the live-quorum decimation-recovery
canonical-bytes pins (#113).

## 0.5.1 — affiliations + infohazard glossary

Defines the affiliations institutional cohort (§4.4.3.2.8 — necessity-vs-interest, legal-hold,
N5-erasure gate, compartments, lawful-access) and the six-phase infohazard glossary entry
(§8.1.1, grounded in the Bostrom typology).

## 0.5 — mesh-safe seed cut

The mesh-safe seed. Reframes binding to **stewardship** throughout (responsible *for*, never
holder *of* — steward, not the retired term); adds verified-rung age-assurance (§3.4.11) and minor-steward binding; absorbs the
§11 wire vocabulary; and defines reverse-quorum moderation (§4.5.13 — propose → 48h fallback →
unilateral moderator/steward action or community live-vote; default-remove for harm reports;
infohazard consent gate).

## 0.4 — accord:lifecycle:active resumption preimage

Ratifies the `accord:lifecycle:active` resumption preimage into HUMANITY_ACCORD (§4.2.1.3).

## 0.3 — accord live-quorum decimation-recovery

Ratifies the live-quorum decimation-recovery procedure into the entrenched HUMANITY_ACCORD
(§4.2.6 — fire-floor-1, fail-to-liberty for adults). Grounds CIRISVerify FSD-004.

## 0.2 — first complete cut

The first complete, clean cut: all ten Accord annexes (A–J) migrated in full, all internal
references resolved, and the three definitional frameworks anchored to international sources
(Risk Magnitude → MIL-STD-882E / DO-178C / EU AI Act; autonomy A0–A4 → SAE J3016 / DoDD
3000.09; sentience heuristic).

## 0.1 – 0.1.5 — consolidation

Initial consolidation of CEG (1.0-RC29, 1+4 surface frozen) and the CIRIS Accord (1.3-RC2)
into one document. Importance-derived spine (PageRank over the unified cross-reference graph),
dual reversible IDs, faithful copy-migration baseline, skeptical per-chapter validation to
0-REJECT certification, Scope & Disclaimers, and the perpetual-stewardship model.
