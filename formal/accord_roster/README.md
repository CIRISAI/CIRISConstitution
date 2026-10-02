# Accord roster rule (CC 4.2.6)

`AccordRoster.lean` is a counting model of one HUMANITY_ACCORD roster decision, written
to decide what replaced the regional-steward backstop (CIRISConstitution#139). Holders are
honest and reachable (`h`), honest and censored (`s`), lost (`d`), or coerced, including a
seated insider (`c`). Signatures are assumed unforgeable. Firing (floor 1 over the live
set) is not modelled as gated, because no roster rule gates it.

Results (all proved, no `sorry`):

- `live_one_coerced_seizes`: under a majority of the live set, one coerced holder plus
  censorship of every honest holder removes an honest holder, at any roster size.
- `present_quarter_seizes`, `present_needs_only_quarter`: under a majority of a present
  majority, about a quarter of the roster suffices.
- `standing_seize_iff`, `standing_min_coercion`, `standing_censorship_irrelevant`: under a
  majority of the standing roster, seizure needs floor(N/2)+1 coerced and censorship buys
  nothing. This is the rule CC 4.2.6 adopts.
- `standing_frozen_after_decimation`, `standing_survivors_keep_fire`: its cost is that a
  roster with half or more of its holders lost cannot heal, while survivors keep the kill.
- `first_strike_no_coercion`, `majority_capture_unstoppable`: no rule matters against a
  first strike without coercion, and none survives a coerced majority (the remedy there is
  the node's un-trust lever, CC 3.2 T3).
- `recovery_keys_help_heal`, `recovery_keys_never_help_seizure`: pre-committed recovery
  keys held by the same holders help healing and never help an adversary.

Check: `lean AccordRoster.lean` (Lean 4.14, core only).
