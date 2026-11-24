#!/usr/bin/env bash
# Run every configuration of TwoPathRows.tla and check each verdict against its expectation: the four
# scenarios close, each planted reading is caught by the invariant named beside it, and every witness
# is reached under the scenario named beside it (a witness is the negation of a state the text names;
# TLC must report it violated).
# Usage: TLA2TOOLS=/path/to/tla2tools.jar ./run_rows.sh   (exit 1 on any mismatch)
# LOGDIR=dir keeps each run's TLC output; TLC_XMX and TLC_WORKERS size the JVM.
set -u
cd "$(dirname "$0")"
J="${TLA2TOOLS:-tla2tools.jar}"
META="$(mktemp -d)"
TLC=(java -Xmx"${TLC_XMX:-1500m}" -XX:+UseParallelGC -cp "$J" tlc2.TLC -workers "${TLC_WORKERS:-4}" -deadlock)
fail=0
# config : expectation ("ok" = closes; otherwise the invariant TLC must report)
expect=(
  "evict:ok" "count:ok" "held:ok" "add:ok" "reopen:ok"
  "plant_node_clock:Inv_C1Unreachable"
  "plant_no_cascade:Inv_SameRowsSameOutcome"
  "plant_no_held_rule:Inv_TargetRowStopsLoneEviction"
  "plant_landing_unchecked:Inv_KnownHeld"
  "plant_landing_needed:Inv_MetCountDecides"
  "plant_withdrawal_first:Inv_MetCountDecides"
  "plant_wd_approval_counts:Inv_WithdrawalRefuses"
)
# witness : the closing configuration it is reached under
witness=(
  "Wit_Open:evict" "Wit_Contested:evict" "Wit_Landed:evict" "Wit_Refused:evict" "Wit_Waiting:evict"
  "Wit_LoneLandingNotFinal:evict" "Wit_DifferWhileRowsDiffer:evict"
  "Wit_Landed:add" "Wit_Refused:add" "Wit_AddOneObjection:add"
  "Wit_Contested:held" "Wit_Open:count" "Wit_NamedRowReopens:reopen"
)
report() { echo "$1  $2  (expected: $3; $(echo "$4" | grep -oE '[0-9]+ distinct states found' | tail -1); depth $(echo "$4" | grep -oE 'search is [0-9]+' | grep -oE '[0-9]+' | tail -1))"; }
for e in "${expect[@]}"; do
  c="${e%%:*}"; want="${e#*:}"
  out="$("${TLC[@]}" -metadir "$META/$c" -config "TwoPathRows_$c.cfg" TwoPathRows.tla 2>&1)"
  if [ "$want" = ok ]; then
    echo "$out" | grep -q 'No error has been found' && r=PASS || r=FAIL
  else
    echo "$out" | grep -qE "Invariant $want is violated" && r=PASS || r=FAIL
  fi
  [ -n "${LOGDIR:-}" ] && echo "$out" > "$LOGDIR/rows_$c.log"
  [ $r = FAIL ] && { fail=1; echo "$out" | tail -25; }
  report "$r" "$c" "$want" "$out"
done
for w in "${witness[@]}"; do
  name="${w%%:*}"; c="${w#*:}"
  sed -E "s/^INVARIANTS.*/INVARIANTS $name/" "TwoPathRows_$c.cfg" > "$META/wit.cfg"
  out="$("${TLC[@]}" -metadir "$META/w-$name-$c" -config "$META/wit.cfg" TwoPathRows.tla 2>&1)"
  echo "$out" | grep -qE "Invariant $name is violated" && r=PASS || r=FAIL
  [ -n "${LOGDIR:-}" ] && echo "$out" > "$LOGDIR/rows_$name-$c.log"
  [ $r = FAIL ] && { fail=1; echo "$out" | tail -15; }
  report "$r" "witness $name under $c" "reached" "$out"
done
rm -rf "$META"
[ $fail = 0 ] && echo "TwoPathRows: every configuration gave its expected verdict" || echo "TwoPathRows: MISMATCH"
exit $fail
