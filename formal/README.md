# `formal/` — the models, and the cascade they sit in

*The claim this directory tests is stated in [`ADEQUACY.md`](ADEQUACY.md): the constitution's adequacy to provide decentralized services globally as designed and committed, and an ethical model under which agents participate ethically, decomposed into sub-claims each with its witness and status.*

CIRIS binds power to the rules it imposes, and directs that power toward the protection of the vulnerable.

Its Recursive Golden Rule makes ethical constraints reciprocal: no agent, steward, developer, or institution stands outside the obligations governing the system.

Its Meta-Goal M-1 rejects order and efficiency purchased at the expense of human dignity, justice, or autonomy.

When ethical principles conflict, the decision process gives the interests of the most vulnerable party decisive weight, as specified by its governing rules.

The result is not a guarantee that an AI can never cause harm. It is a framework designed to make power accountable, constrain coercion, and orient decisions toward those least able to protect themselves.

*(the steward, 2026-10-18; the whole statement is [`review/pieces/00_kept_promises.md`](../review/pieces/00_kept_promises.md))*

## The cascade, simply

Each line below is a step the one above forces. Nothing in a lower step may say more than the step above it allows, and every step names where it lives.

1. **Ethics.** Meta-Goal M-1 ([CC 1.1](../constitution/part_1_foundation.md)), the principled decision algorithm and its order of principles with the most vulnerable party as the tie-break ([CC 1.3](../constitution/part_1_foundation.md)), the Recursive Golden Rule that binds every principal including the steward and CIRIS L3C ([CC 1.13.2](../constitution/part_1_foundation.md)), the fail-secure posture that keeps the halt in human hands ([CC 1.5](../constitution/part_1_foundation.md)), and deferral to a named human when the agent is unsure ([CC 1.9](../constitution/part_1_foundation.md)).
2. **Promises.** Eleven promises written once for human and AI participants alike, each paired with the power that could break it and the check on that power: [`review/pieces/00_guarantees.md`](../review/pieces/00_guarantees.md) (the G rows), the plain rules for a user and the digest for an operator beside it. Every promise line carries a marker stamped from data: works today, being built with its ticket, a rule with no code yet, or modelled.
3. **Rules.** The decimal sections of Parts 2 to 8: what a row is, who may sign it, what a substrate refuses and with which token. A promise that no rule carries is incomplete; a rule that no promise needs is suspect.
4. **Invariants.** Each rule that can be stated as something that never happens, or always eventually happens, is written as a property: 98 of them today, in [`INVARIANTS.tsv`](INVARIANTS.tsv), each with its CC decimal, its claim id and its verdict, and each restated over one shared vocabulary.
5. **The state table.** That vocabulary: [`STATE_TABLE.tsv`](STATE_TABLE.tsv) names the states a mesh node and the things around it can be in (155 states over 51 variables in 9 planes), where the text defines each, which row enters it, who signs, and which model realises it. A state the text defines and no model constrains is listed as such, because the gap is the point.
6. **Plane models.** One checked model per plane: the standing verdict, the accord halt and its roster arithmetic, the keys under one self, the mesh of blobs and cohorts and roots, delegation and licences and grants, the participant guarantees, erasure. Each has a ruled configuration that closes and must-fail twins, each twin named after the wrong reading it encodes, so a reader sees what the rule prevents and not only that it holds. Where the steward's word was needed to decide a reading, the model was run first and the counterexample shown.
7. **The spine.** [`cewp_node/CewpNode.tla`](cewp_node/CewpNode.tla) composes the planes over the state table and checks only what no plane sees alone: the halt is not a trust leg, an evicted key's authority ends, replication follows consent, a local row never leaves, leaving is one act. Its breaker twin reproduces the one cross-plane defect the rc8 cut named, and fails as it must.
8. **The catalogue.** The CSD/4 topology catalogue (ten entries, vendored under [`cewp_node/catalog/`](cewp_node/catalog/)) describes the meshes the harness stands up on real nodes. [`tools/topology_to_cfg.py`](../tools/topology_to_cfg.py) turns one entry into every plane model's constants and a report of which promised states a model constrains; the same entry drives the harness, whose row export is what a trace check replays. The vocabulary of states the catalogue speaks is the constitution's ([`manifests/topology_vocabulary.json`](../manifests/topology_vocabulary.json)), so a state nobody has written down cannot be claimed.
9. **The register.** [`constitution/claims.tsv`](../constitution/claims.tsv): every load-bearing claim, established only when a pinned manifest of the owning repository publishes the named symbol, staged on a ticket until then, normative when it is a rule with no code. The markers of step 2 are stamped from it. The checker runs on every commit.

Read downward to see how a principle becomes a thing a machine refuses. Read upward to see which principle a refusal serves.

## What a model proves, and what it does not

A model-checker run says the machine as written has no bad reachable corner within the bound. A harness run says one implementation followed one path of that machine correctly. The register says which claims rest on which. None of them says the rule is wise: the record preserves evidence, the observation is bounded by the instrument, the interpretation gives it meaning, and a named party answers for the interpretation. The models here are the record and the observation. The meaning, and the responsibility for it, stay with the people who wrote the rules and run the nodes.

Every model states its residuals in its README: what it does not cover, the bounds it found, the readings it rejected. A verdict without its residuals is not a verdict.

## The models

| Directory | What it protects | Who it protects | CC | Ruled verdict |
|---|---|---|---|---|
| [`trust_root`](trust_root/) | the standing verdict a node reaches about a root: Rooted, Stalled, NotRooted | the node owner who must not be rooted by a stale or forged head, and never un-rooted by a clock | 3.2 T7, T8 | closes, 22,152,480 states |
| [`accord_halt`](accord_halt/) | one holder's row halts, a lone halt lapses at the fuse, a majority confirms or resumes | everyone an agent could harm in the time a committee would take | 4.2.1.1, 4.2.6 | closes; proposal-mode twins fail |
| [`accord_roster`](accord_roster/) (Lean) | the standing rule needs a strict majority to seize, for any roster size | the holders against coercion, censorship and loss | 4.2.6 | proved for any N |
| [`self_roster`](self_roster/) | the keys under one person: a thief cannot evict the others, lost keys are recoverable | the person whose device was stolen or lost | 3.3.6.3 | closes at 3 and 4 keys; one- and two-key bounds stated |
| [`mesh_net`](mesh_net/) | who may hold a blob, that a private cohort is invisible, that a root only restricts, that no hand bans a community | the member of a family or room whose content must not leak, the community that must not be banned | 5.2, 5.4.6, 4.2.1, 4.5.4 | closes, 2,013,648 states; shipped twins fail |
| [`authority_tree`](authority_tree/) | delegation attenuates, caps, cascades and expires; a licence and a grant never chain | the person a delegate acts for | 4.4.3.4.3, 4.1.1, 2.4.1.2.1 | 595,456 states, 0 violations |
| [`guarantees`](guarantees/) (Lean + TLA+) | the promises reach every participant alike; the halt is the one asymmetry; a refusal stands; retirement follows the Standard | the participant with least standing | 1.13.2, 7.5.5 | closes; three dye twins fail |
| [`withdraws_admission`](withdraws_admission/) | erasure at the subject's request, by the controller, never laundering an adverse row | the person named in a row, and the people the adverse row protects | 2.4.1.1, 4.5.3 | closes, 3,600 states; three twins fail |
| [`cewp_node`](cewp_node/) | the planes composed; the catalogue turned into constants | the node as a whole | 3.2, 3.3.6.3, 3.3.7, 5.3.2.4, 4.2.1 | closes, 419,328 states; breaker twin fails |

| [`reciprocity`](reciprocity/) (Lean) | the opening statement itself: which of its steps are theorems and which are premises the text must carry | the reader who takes "reciprocal" and "most vulnerable" at face value | 1.13.2, 1.3, 1.5, 7.5.5 | eight findings, compiles clean |

| [`retirement`](retirement/) | the seven-state Retirement Standard: forward only, cancel only before frozen, the seal opened by one row, custody only by the named custodian, a walk-away that keeps the record, a refusal that stands | the people an agent served, whose record and rights survive its end; the subject named inside the record | 7.5.5, 7.5, 1.9, 4.5.3 | closes, 594,048 states; 13 twins fail |

| [`consent`](consent/) | the consent fold: a revocation is a boundary, the owner can always recant, backdating is bounded by the window, decay runs forward, replication needs a directed grant | the person whose trace is captured or whose content is replicated | 3.3.1, 3.3.7, 2.6.7 | closes (4,210,336 and 467,692 states); three twins fail |

Being built (2026-10-18): the membership ceremony, the last plane the state table lists with no model.

## Running

TLC: `java -cp tla2tools.jar tlc2.TLC -deadlock -config <cfg> <module>.tla` in the model's directory; Lean: `lake build` in the model's directory; the delegation model: `python3 authority_tree.py`. Every configuration runs in CI (`.github/workflows/formal.yml`), the ruled ones to closure and each twin to its named failure. `tools/check_formal_tables.py` keeps the two tables honest against the sources, the toc and the register.
