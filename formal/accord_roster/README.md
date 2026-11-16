# Accord roster rule (CC 4.2.6)

`AccordRoster.lean` is a counting model of one HUMANITY_ACCORD roster decision, written
to decide the roster rule CC 4.2.6 adopts with no backstop outside the roster. Holders are
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

## The roster as a lineage of bundles (`AccordBundle.tla`, CC 2.6.1.11, CC 4.2.6)

The counting above fixes the rule; `AccordBundle.tla` checks its form. A roster change is a later genesis bundle,
counted at a strict majority of the predecessor's holders, with each holder it adds and each holder whose recovery
commitment it changes. A recovery is a later bundle signed by the recovering holder's recovery key alone, the key the
commitment in force commits to. It changes that holder's signing key and next commitment and nothing else. The world:
three holders, one who may be added, one who may recover twice and one who may re-commit; an adversary that may steal
the recovering holder's signing key, and any recovery key once a recovery has spent it. Any party may present any
bundle; the reader's rule is what is checked. `AccordBundle.cfg` closes at 19,024 distinct states (`MaxVer` 4).

| Invariant | What holds | Twin that fails it |
|---|---|---|
| `Inv_ChangeCounted` | no change without the count | `AccordBundle_nocount.cfg`: a change counted on any one holder |
| `Inv_RecoveryOwnSeat` | a recovery is the recovery key's one statement and changes only its own seat | `AccordBundle_otherseat.cfg`: a recovery that changes a second seat |
| `Inv_SpentNeverReturns` | a spent commitment is never in force again and no recovery uses one, across any sequence of bundles | `AccordBundle_spentreturns.cfg`: the next commitment need only differ from the one spent |
| `Inv_RecKeyNeverSeat` | a recovery key never becomes a seat's key | `AccordBundle_reckeyseat.cfg`: a recovery key named as the new signing key |
| `Inv_SignKeyCannotRecover` | a holder's stolen signing key does not recover the seat | `AccordBundle_anykey.cfg`: a recovery accepted under any key |
| `Inv_SpentKeyGainsNothing` | a stolen spent recovery key gains nothing | `AccordBundle_spentkey.cfg`: a recovery accepted under any commitment ever named |

Four witnesses, each required to fail, show the paths are reached: a holder recovers twice, a holder is added, a
re-commitment lands, and the adversary holds a spent recovery key. The Lean theorems above are unchanged: the bundle's
count is the standing rule they decide.

    bash formal/accord_roster/run_tlc.sh /path/to/tla2tools.jar     # one closes, six twins and four witnesses fail
