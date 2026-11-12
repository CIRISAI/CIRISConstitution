# Fourth reading, share 9: summary

Branch `rc19`, head `05cbcc8`. Output: `out_r4_9.tsv` beside this file (32 findings).

## The three numbers

- New major findings, text against text: **2**
- New major findings, text against data: **2**
- Statements opened in the text: **422** of 425. Read by gist only: **3**.

## Per rule key

| Rule key | Statements | Findings | Major new | Major known | Minor new | Minor known |
|---|---|---|---|---|---|---|
| `trust_fold` | 137 | 9 | 2 | 0 | 6 | 1 |
| `principle` | 121 | 7 | 0 | 0 | 7 | 0 |
| `signature` | 75 | 4 | 0 | 1 | 3 | 0 |
| `minor_floor` | 52 | 7 | 2 | 3 | 2 | 0 |
| `announce` | 37 | 4 | 0 | 1 | 2 | 1 |
| `other:session-claim` | 2 | 1 | 0 | 0 | 1 | 0 |
| `other:dsar-export` | 1 | 0 | 0 | 0 | 0 | 0 |
| **Total** | **425** | **32** | **4** | **5** | **21** | **2** |

## Major new findings in full

### 1. Who may be seated as a child's guardian (text against text; `minor_floor`; CC 3.2 against CC 3.4.13 Q3)

- CC 3.2, user-target admission rule: the steward's adult band is "the I1 band (`age_self_declared` / `age_assurance:*`", and the rule asks only that the steward signed.
- CC 3.4.13 Q3: "The guardian MUST be ≥ `age_assurance:provider:adult` as a floor, and the guardianship relationship to that specific child MUST be verified."

An admission gate built from CC 3.2 alone seats a self-declared adult as guardian with no check of the relationship. Under the fail-secure rule every unassured identity reads as a minor, so the same gate lets a self-declared adult stranger bind any unassured person as a ward. CC 3.4.11 and CC 3.4.13 (a `self` row graduates nobody; "a verified stranger is not a guardian") support Q3. The CC 3.2 pseudo-code needs the provider-rung floor and the relationship check, or a pointer to Q3 as a further condition of admission.

### 2. The age gate of Policy J reads the level and never the band (text against text; `minor_floor`; CC 4.4.3.10 against CC 3.4.11)

- CC 4.4.3.10: `return consumer_level >= required_level`, over the ordering `self < provider… < government…`.
- CC 3.4.11: adult-class content is visible only to a viewer whose band is `adult`, and "The band opens this gate only at a verified level, `provider` or `government`".

Policy J's gate passes a provider-attested `minor` band (the level is high enough), and passes a `self` rung wherever a rating's required level is `self`. CC 3.4.11 and CC 3.4.13 Q3 gate on band `adult` at a verified level and block everything else. The home section and the ruling of 2026-11-11 support the stricter gate. Two smaller faults sit in the same paragraph and are reported as minor: the qualified shapes `provider:{verifier_key}:adult` (the fault of C343, in a third place) and SHOULD where CC 3.4.11 says MUST.

### 3. Who signs the acceptance edge (text against data; `trust_fold`; CC 3.2 T3 against `manifests/family_model.json`)

- CC 3.2: "The acceptance edge is a person's row: any live key of the person's roster signs it as that person". CC 3.1.1 and CC 4.4.3.8 say the same.
- `family_model.json`, `trust:{job}:{version}`, `signer_rule` (source `code-v61`): "accepts: self (node -> root)".

Under the text one edge accepts a root for every node and agent a person owns, and one deletion un-trusts it on all of them; a node's own edge is read only while its owner has signed none. Under the data each node signs and holds its own edge. The text is consistent with itself; the cell is the shipped store's shape.

### 4. The attach window closes an admitted edge (text against data; `trust_fold`; CC 3.2 T4a and T8 against `manifests/reactions.json`)

- CC 3.2: "a lapsed window never detaches a running node"; the gate "runs on the edge's first admission only"; invariant (ii): an expired `attach_window_secs` never moves `Rooted` or `Stalled` to `NotRooted`.
- `reactions.json`, `trust:{job}:{version}` leaf `accepts`: a clock `attach` of `charter.attach_window_secs` from `cosigned_at`, and on its close "read verdict closed, force must".

Executed as data the reaction closes the acceptance edge when the window lapses, which is the failure T4 exists to forbid. `formal/derivation/reaction_text.tsv` cites for this entry the very sentence that forbids it. If "closed" is meant as "no new edge may attach on that head", the verdict belongs to the attach attempt, a refusal at the door, and not to the family's admitted rows.

## Major known findings (still present)

- **C316** (`minor_floor`): an unassured person "uses their own and their family's scopes freely" (CC 3.4.13) against "No minor `user` identity operates without a live adult steward" (CC 3.2, and Q4). Still present.
- **C002** (`minor_floor`, held for Eric): "at most one live guardian" (CC 3.2) against M-of-N co-guardianship (CC 3.4.13 Q7). Added observation: `is_steward_bound` requires exactly one live owner-binding, which a second guardian's edge would break.
- **C317** (`minor_floor`): a minor's node never carries a federation-scope owner-binding (CC 5.4.6) against "Announcing starts on" (CC 4.5.13). Still present.
- **C287** (`signature`, held): the build manifest signed "by the per-primitive steward" (CC 3.1.2) against the pipeline that built it (CC 3.1.2.1).
- **C132** (`announce`, held): un-announcing as a supersede at `self` (CC 5.4.6) against the federation row being a second row, never a replacement (CC 3.2).

## Minor findings, in brief

- `trust_fold`: the halt latch listed among V's inputs though V never reads it (CC 3.2 T8); `cw_class` MUST NOT against the SHOULD of its home (CC 4.4.3.10, 4.4.1); "L3 or above" where the pattern takes L3 or L4 only (CC 4.4.3.11); an agent "pins" signers though the trust set is its owner's (CC 3.1.2.1); data: a `moderate` leaf filed as a `trust:{job}`; data: the `verbs` cell lacks `recant`. Known C426, reported for overlap.
- `principle`: "advances broader ecosystem flourishing" as a condition of every act (CC 7.1.4) against constraints only (CC 1.1); "severe or irreversible" against "severe, irreversible" (CC 7.2.2, 1.6); `accord-principle:*` named as a prefix that is not registered (CC 1.1, 3.1.5.2); duties that "lift with" stewardship against no release from stewardship (CC 1.13.2); duties owed to the agent or to the people it acts on (CC 1.13.2); "a CIRIS agent's hold over a made thing" (CC 7.3.4); "developmental AI" given as a dependent sentient being (CC 7.3.2).
- `signature`: the classical half REQUIRED with no tier in the signed-object table against an unsigned local row (CC 2.6.1.7, 5.3.2.4.3); `contribution_envelope` against `attestation_envelope` (CC 5.3.2.4.2, 2.6.1.7); in the planned CC 2.6.1.8, "verifies as itself for ever" against an unlogged earlier-form row not accepted after the cutover.
- `announce`: known C142 (one verb, two things; still present); "reachability is never an attestation" against the registered `observation:reachability`, `peer_reachability:{network}` and `health:liveness` families; a `public` room is community scope with no DEK, and CC 5.4.6 forbids every community-scope destination to announce and resolves it from a group key it does not have.
- `other:session-claim`: data placement admits `commons` where CC 3.1.3.1 sets the ceiling at `Cohort` (cell flagged `gap`).

## What was compared with data

`manifests/family_model.json` (trust, age_assurance, age_self_declared, session, custody, identity:occurrence, observation:reachability, peer_reachability, transport), `manifests/reactions.json` (trust, session), `manifests/transitions.json` (trust), `manifests/signed_object.cddl` (signature members), `constitution/constants.tsv` (72 h, session lease), `constitution/governance_policy.tsv` (no row touches these keys). The CC 8.10 cards were checked for the two age families only. Data faults already in the table and still present were not repeated: C422 and C423 (signer cells of the two age families).

## Not finished, or read by gist only

- By gist only (3 statements): CC 2.1 "attach_window_secs is never a validity leg for a root already attached" and CC 2.1 "a charter declaring no attach_window_secs…" (both read in their CC 3.2 T4a form, not in the CC 2.1 row); CC 3.2 "the substrate records an adjudication finding; it never makes one" (`principle`; the sentence was not found by its gist).
- Not done: a card-by-card comparison with CC 8.10 for the trust family; the `withdraws_by {attester, subject}` cell of `trust:{job}` against "the reader … adds and removes it freely" (a root withdrawing a reader's acceptance edge) was noticed and left unreported, as the generic rule of CC 2.4.1.1 covers it.
- No key was left unread.
