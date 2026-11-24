#!/usr/bin/env bash
# Run every configuration of formal/self_roster and check each verdict against its expectation: the
# closing configurations close, each twin that fails by design and each planted break reports the
# invariant or property named beside it, and every witness is reached under the configuration named
# beside it (a witness is the negation of a state the text names; TLC must report it violated).
# Usage: TLA2TOOLS=/path/to/tla2tools.jar ./run.sh   (exit 1 on any mismatch)
# Options: ONLY="name name" runs those configurations only; NOWIT=1 skips the witnesses;
# LOGDIR=dir keeps each run's TLC output; TLC_XMX and TLC_WORKERS size the JVM.
set -u
cd "$(dirname "$0")"
J="${TLA2TOOLS:-tla2tools.jar}"
META="$(mktemp -d)"
TLC=(java -Xmx"${TLC_XMX:-4500m}" -XX:+UseParallelGC -cp "$J" tlc2.TLC -workers "${TLC_WORKERS:-4}" -deadlock)
fail=0
# config : expectation ("ok" = closes; "temporal" = the liveness property fails; otherwise the
# invariant or action property TLC must report)
expect=(
  "combined1_add:ok" "combined2_lost:ok" "combined3_stolen:ok" "combined3_lost:ok" "combined4_mixed:ok"
  "unilateral3_lost:ok" "quorum3_stolen:ok" "reverse3_lost:ok"
  "mixed3_nospare:ok" "mixed3_ownerlone:ok" "combined3_2stolen:ok" "combined3_stale:ok"
  "unilateral3_stolen:Inv_ThiefCannotEvictHonest"
  "quorum3_lost:temporal" "reverse3_stolen:temporal" "combined2_stolen:temporal" "combined4_2stolen:temporal"
  "combined1_stolen:Inv_SelfSurvives"
  "combined3_absent:Inv_ThiefCannotEvictHonest"
  "combined3_mixed:Inv_ThiefNeverMajority"
  "plant_no_held_rule:Inv_OwnerRowStopsThief"
  "plant_owner_names_all:Inv_OwnerRowStopsThief"
  "plant_ended_counts:Inv_SpentRowsCountNothing"
  "plant_wd_approval_counts:Inv_WithdrawalRefuses"
  "plant_settle_contested:Prop_NothingChangesUnlessLanded"
)
# witness : the configuration it is reached under   (an action-property witness is marked with "!")
witness=(
  "Wit_Open:mixed3_nospare" "Wit_Contested:mixed3_nospare" "Wit_LoneLanded:combined3_lost"
  "Wit_CountLanded:combined3_stolen" "Wit_RefusedByCount:combined3_stolen"
  "Wit_RefusedByWithdrawal:combined3_stolen"
  "Wit_ApprovalBeatsWithdrawal:combined3_2stolen" "Wit_ApprovalAfterWithdrawal:combined3_2stolen"
  "!Wit_LoneLandingNotFinal:mixed3_nospare"
  "Wit_ConcluderChoosesInstants:combined3_stolen"
  "Wit_AbsentOwnerReadsLost:combined3_absent"
  "Wit_OneKeyCannotEvictSigningThief:mixed3_ownerlone"
  "Wit_AddOneObjection:combined3_mixed"
  "Wit_SpentKeySigns:combined3_stale" "Wit_BadHeldLanded:mixed3_nospare" "Wit_VoidLanding:combined3_stolen"
)
report() { echo "$1  $2  (expected: $3; $(echo "$4" | grep -oE '[0-9]+ distinct states found' | tail -1); depth $(echo "$4" | grep -oE 'search is [0-9]+' | grep -oE '[0-9]+' | tail -1); $(echo "$4" | grep -oE 'Finished in [0-9a-z ]+s' | tail -1))"; }
for e in "${expect[@]}"; do
  c="${e%%:*}"; want="${e#*:}"
  if [ -n "${ONLY:-}" ] && ! echo " $ONLY " | grep -q " $c "; then continue; fi
  out="$("${TLC[@]}" -metadir "$META/$c" -config "SelfRoster_$c.cfg" SelfRoster.tla 2>&1)"
  case "$want" in
    ok) echo "$out" | grep -q 'No error has been found' && r=PASS || r=FAIL ;;
    temporal) echo "$out" | grep -q 'Temporal properties were violated' && r=PASS || r=FAIL ;;
    *) echo "$out" | grep -qE "(Invariant|Action property) $want is violated" && r=PASS || r=FAIL ;;
  esac
  [ -n "${LOGDIR:-}" ] && echo "$out" > "$LOGDIR/sr_$c.log"
  [ $r = FAIL ] && { fail=1; echo "$out" | tail -40; }
  report "$r" "$c" "$want" "$out"
done
if [ -z "${NOWIT:-}" ]; then
  for w in "${witness[@]}"; do
    name="${w%%:*}"; c="${w#*:}"
    if [ -n "${ONLY:-}" ] && ! echo " $ONLY " | grep -q " $c "; then continue; fi
    if [ "${name#!}" != "$name" ]; then
      name="${name#!}"
      grep -vE '^(INVARIANTS|PROPERTIES)' "SelfRoster_$c.cfg" > "$META/wit.cfg"; echo "PROPERTIES $name" >> "$META/wit.cfg"
    else
      grep -vE '^(INVARIANTS|PROPERTIES)' "SelfRoster_$c.cfg" > "$META/wit.cfg"; echo "INVARIANTS $name" >> "$META/wit.cfg"
    fi
    out="$("${TLC[@]}" -metadir "$META/w-$name-$c" -config "$META/wit.cfg" SelfRoster.tla 2>&1)"
    echo "$out" | grep -qE "(Invariant|Action property) $name is violated" && r=PASS || r=FAIL
    [ -n "${LOGDIR:-}" ] && echo "$out" > "$LOGDIR/sr_$name-$c.log"
    [ $r = FAIL ] && { fail=1; echo "$out" | tail -15; }
    report "$r" "witness $name under $c" "reached" "$out"
  done
fi
rm -rf "$META"
[ $fail = 0 ] && echo "self_roster: every configuration gave its expected verdict" || echo "self_roster: MISMATCH"
exit $fail
