# `formal/roster_listing` — a member's public listing is a per-membership opt-in

CC 2.1 defines `listed`: a per-membership opt-in flag, value `public`, default absent. The roster is producer- and self-queryable and never globally enumerable; opting into roster visibility is a one-way disclosure the member chooses, admitted only on a community membership signed by its own subject. CC 5.4.6 and the mesh-net invariant I3 say nothing about a bounded cohort is observable outside it unless a member discloses it. This file states the rule a non-member's roster view must obey and shows the two readings that break it.

**The model** (`RosterListing.lean`, core Lean). A key's standing in a room is a span count (how many times admitted), whether the current span is live, and the span in which the key last signed a listing. Three acts: a join opens a new span, a leave ends it, a listing lands only when signed by the member about their own live membership. Three views a non-member might be served: the constitution's (listed within the current live span), and two twins (absent means listed; the span filter dropped).

| Theorem | What it says | CC |
|---|---|---|
| `cc_view_discloses_only_the_listed` | the constitution's view serves nothing the member has not disclosed in this span, in every world | 2.1, 5.4.6 |
| `listing_needs_the_members_signature`, `listing_needs_a_live_membership` | a listing by anyone but the member, or about a membership that is not live, is refused | 2.1 ("signed by its own subject") |
| `leave_ends_the_listing` | removal or resignation ends the disclosure | 2.1 (per-membership) |
| `readmission_is_unlisted`, `step_keeps_tidy` | a re-admitted member is unlisted until they list again; the hypothesis it needs is an invariant of every reachable world | 2.1 (per-membership) |
| `twin_absent_listed_fails` | the reading "absent means listed" serves a member who never disclosed | the default inverted |
| `twin_no_span_fails` | the reading without the span filter serves a stale listing after re-admission | the span rule dropped |
| the worked room | key 7 joins (private), lists (served), leaves (private), rejoins (private); a stranger's listing of 7 is refused | the rule as a run |

**What it does not model.** The ceremony that opens and closes a span (`formal/membership`); who may read the roster inside the cohort (the audience rule, CC 4.4.3.4); the group's own discovery row `community:listing:v1`, which names no roster.

**Running.** `lean RosterListing.lean`; the CI job `reciprocity` compiles it beside the cascade, the trust set and the affiliation model.
