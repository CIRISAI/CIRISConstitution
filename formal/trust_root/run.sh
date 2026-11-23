#!/usr/bin/env bash
# Run every configuration of formal/trust_root and check each verdict against its expectation:
# the closing configurations close, each planted fault is caught by the invariant named beside it,
# the rejected reading fails in both its corners, and every reachability witness in
# TrustRootWitness.tla is reached under the configuration named beside it.
# Usage: TLA2TOOLS=/path/to/tla2tools.jar ./run.sh   (exit 1 on any mismatch)
# Options: ONLY="name name" runs those configurations only; NOWIT=1 skips the witnesses and
# NOCFG=1 the configurations;
# LOGDIR=dir keeps each configuration's TLC output; TLC_XMX and TLC_WORKERS size the JVM.
set -u
cd "$(dirname "$0")"
J="${TLA2TOOLS:-tla2tools.jar}"
META="$(mktemp -d)"
TLC=(java -Xmx"${TLC_XMX:-3g}" -XX:+UseParallelGC -cp "$J" tlc2.TLC -workers "${TLC_WORKERS:-auto}" -deadlock)
fail=0
# config : expectation ("ok" = closes; otherwise the invariant or property TLC must report)
expect=(
  "named:ok" "revoked:ok" "anchored:ok" "deep:ok"
  "plant_seat_counts:Inv_i"
  "plant_aging_detaches:Prop_T4"
  "plant_revocation_reaches_behind:Inv_iii"
  "plant_fresh_by_clock:Prop_iv"
  "plant_attach_under_quorum:Prop_iv"
  "plant_halt_folds:Inv_v"
  "plant_end_by_instant:Inv_EndNoInstant"
  "plant_first_seen_wins:Inv_vii"
  "plant_unmade_head_stays:Inv_viii"
  "plant_founder_margin:Inv_T7"
  "plant_own_charter:Prop_PredecessorSet"
  "plant_fork_freezes:Inv_ForkNeverFreezes"
  "plant_freeze_blocks_ends:Inv_FreezeAdoptionOnly"
  "plant_unnamed_receipts_count:Inv_NoServicesNoReceipt"
  "reading_vii_freeze:Inv_vii_Unconditional"
  "reading_vii_uncount:Inv_vii_Unconditional"
)
# witness : the closing configuration it is reached under
witness=(
  "Wit_Rooted:named" "Wit_Stalled:named" "Wit_RecoveredRooted:named" "Wit_Adopted:named"
  "Wit_FellBack:named" "Wit_LineageUnmade:named" "Wit_SignerRevoked:named"
  "Wit_FrozenAttached:named" "Wit_ForkAttempt:named" "Wit_StaleStillRooted:named"
  "Wit_StalledAtEdge:named" "Wit_UnreceiptedStillRooted:revoked" "Wit_Rooted:revoked"
  "Wit_Rooted:anchored" "Wit_Stalled:anchored" "Wit_TipsWait:anchored"
  "Wit_ReceiptsHeldUnnamed:anchored" "Wit_ThirdVersion:anchored"
  "Wit_ThirdVersion:deep" "Wit_RecoveredRooted:deep"
)
cfg_of() { [ "$1" = named ] && echo TrustRootVerdict.cfg || echo "TrustRootVerdict_$1.cfg"; }
for e in "${expect[@]}"; do
  c="${e%%:*}"; want="${e#*:}"
  [ -n "${NOCFG:-}" ] && continue
  if [ -n "${ONLY:-}" ] && ! echo " $ONLY " | grep -q " $c "; then continue; fi
  out="$("${TLC[@]}" -metadir "$META/$c" -config "$(cfg_of "$c")" TrustRootVerdict.tla 2>&1)"
  if [ "$want" = ok ]; then
    echo "$out" | grep -q 'No error has been found' && r=PASS || r=FAIL
  else
    echo "$out" | grep -qE "(Invariant|Action property) $want is violated" && r=PASS || r=FAIL
  fi
  [ -n "${LOGDIR:-}" ] && echo "$out" > "$LOGDIR/$c.log"
  [ $r = FAIL ] && { fail=1; echo "$out" | tail -25; }
  echo "$r  $c  (expected: $want; $(echo "$out" | grep -oE '[0-9]+ distinct states found' | tail -1); depth $(echo "$out" | grep -oE 'search is [0-9]+' | grep -oE '[0-9]+' | tail -1); $(echo "$out" | grep -oE 'Finished in [0-9a-z ]+s' | tail -1))"
done
if [ -z "${NOWIT:-}" ]; then
  for e in "${witness[@]}"; do
    w="${e%%:*}"; c="${e#*:}"
    if [ -n "${ONLY:-}" ] && ! echo " $ONLY " | grep -q " $c "; then continue; fi
    sed -e '/^INVARIANTS/,$d' -e '/^SYMMETRY/d' "$(cfg_of "$c")" > "$META/wit.cfg"
    echo "INVARIANT $w" >> "$META/wit.cfg"
    out="$("${TLC[@]}" -metadir "$META/wit_${w}_$c" -config "$META/wit.cfg" TrustRootWitness.tla 2>&1)"
    echo "$out" | grep -q "Invariant $w is violated" && r=PASS || { r=FAIL; fail=1; echo "$out" | tail -8; }
    echo "$r  witness $w reached under $c"
  done
fi
rm -rf "$META"
exit $fail
