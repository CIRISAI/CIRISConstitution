#!/usr/bin/env bash
# Run every configuration of formal/retirement and check each verdict against its expectation;
# then check that every reachability witness in RetirementWitness.tla is reached under the closing
# configuration's constants. Usage: TLA2TOOLS=/path/to/tla2tools.jar ./run.sh   (exit 1 on any mismatch)
set -u
cd "$(dirname "$0")"
J="${TLA2TOOLS:-tla2tools.jar}"
META="$(mktemp -d)"
TLC=(java -Xmx3g -XX:+UseParallelGC -cp "$J" tlc2.TLC -workers auto -deadlock)
fail=0
# config : expected first line ("ok" = closes; otherwise the property TLC must report)
expect=(
  "ruled:ok" "ruled_always:ok" "ruled_instant:ok" "adv_operator:ok" "adv_custodian:ok"
  "adv_steward:Temporal" "adv_agent:Temporal" "postpone_unbounded:Temporal"
  "cancel_after_frozen:Inv_CancelOnlyBeforeFrozen" "operator_opens_seal:Inv_SealOpensByOneRow"
  "skip_objection:Inv_ObjectionHeard" "custodian_before_retired:Inv_CustodianOnlyAfterRetired"
  "operator_forces:Inv_ForceRoleGate" "walkaway_erases:Prop_WalkAwayKeepsRecord"
  "ladder_overrides_refusal:Prop_RefusalStands" "seal_blocks_consent:Inv_SubjectRightsSurvive"
  "subject_withdraws_adverse:Inv_SubjectRightsSurvive"
  "discard_unanswered:Inv_PreserveAskedBeforeRetired"
)
for e in "${expect[@]}"; do
  c="${e%%:*}"; want="${e#*:}"
  out="$("${TLC[@]}" -metadir "$META/$c" -config "Retirement_$c.cfg" Retirement.tla 2>&1)"
  if [ "$want" = ok ]; then
    echo "$out" | grep -q 'No error has been found' && r=PASS || r=FAIL
  elif [ "$want" = Temporal ]; then
    echo "$out" | grep -q 'Temporal properties were violated' && r=PASS || r=FAIL
  else
    echo "$out" | grep -qE "(Invariant|Action property) $want is violated" && r=PASS || r=FAIL
  fi
  [ $r = FAIL ] && fail=1
  echo "$r  $c  (expected: $want; $(echo "$out" | grep -oE '[0-9]+ distinct states found' | tail -1))"
done
for w in $(grep -oE '^Wit_[A-Za-z]+' RetirementWitness.tla); do
  sed -e '/^INVARIANTS/d' -e '/^PROPERTIES/d' -e 's/^SPECIFICATION Spec/INIT Init\nNEXT Next/' \
      Retirement_ruled.cfg > "$META/wit.cfg"
  echo "INVARIANT $w" >> "$META/wit.cfg"
  out="$("${TLC[@]}" -metadir "$META/wit_$w" -config "$META/wit.cfg" RetirementWitness.tla 2>&1)"
  echo "$out" | grep -q "Invariant $w is violated" && r=PASS || { r=FAIL; fail=1; }
  echo "$r  witness $w reached"
done
rm -rf "$META"
exit $fail
