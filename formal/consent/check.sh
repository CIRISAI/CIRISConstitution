#!/bin/bash
# formal/consent: every configuration, every planted break and every witness, with the verdict each must give.
# A closing configuration must close. A planted break must violate the property it names. A witness is the
# negation of a state the text names; TLC must report it violated, which is the state being reached.
# Exit 0 when every line is as expected. A run is a search over the stated bound, not a proof.
#
#   bash formal/consent/check.sh            every run
#   bash formal/consent/check.sh --quick    everything but the two large closing runs (head_counts, head_ends)
#
# TLA_JAR names tla2tools.jar (1.7.4). The whole file peaked at 3.5 GB: on a shared box run it as
#   grace-sched run --owner CIRISConstitution -- bash formal/consent/check.sh
cd "$(dirname "$0")" || exit 2
JAR="${TLA_JAR:-../../tla2tools.jar}"
[ -f "$JAR" ] || JAR="$HOME/.cache/ciris-kernel/tla2tools-1.7.4.jar"
[ -f "$JAR" ] || { echo "no tla2tools.jar (set TLA_JAR)"; exit 2; }
T="${CONSENT_TMP:-$(mktemp -d)}"; mkdir -p "$T"
XMX="${CONSENT_XMX:-6g}"
fail=0

tlc() {   # cfg-path log-name
  java -XX:+UseParallelGC -Xmx"$XMX" -cp "$JAR" tlc2.TLC -workers "${CONSENT_WORKERS:-4}" -metadir "$T/meta-$2" -deadlock -config "$1" Consent.tla > "$T/$2.log" 2>&1
}
states() { grep -o '[0-9]* distinct states found' "$T/$1.log" | tail -1 | grep -o '^[0-9]*'; }
depth()  { grep -o 'depth of the complete state graph search is [0-9]*' "$T/$1.log" | grep -o '[0-9]*$'; }

closes() {   # cfg
  n="${1%.cfg}"; tlc "$1" "$n"
  if grep -q 'Model checking completed. No error has been found' "$T/$n.log"; then
    echo "ok    closes    $1: $(states "$n") distinct states, depth $(depth "$n")"
  else
    echo "FAIL  closes    $1"; grep -m3 -E 'Error|violated' "$T/$n.log"; fail=1
  fi
}
breaks() {   # cfg, the line TLC must print
  n="${1%.cfg}"; tlc "$1" "$n"
  if grep -q "$2" "$T/$n.log"; then
    c="$(states "$n")"; echo "ok    plant     $1: $2${c:+ ($c distinct states when found)}"
  else
    echo "FAIL  plant     $1: expected '$2'"; grep -m3 -E 'Error|violated|No error' "$T/$n.log"; fail=1
  fi
}
breaks_one() {   # base cfg, the one invariant it must also violate
  n="one-${1%.cfg}-$2"
  grep -v -E '^(INVARIANTS|PROPERTIES)' "$1" > "$T/$n.cfg"; echo "INVARIANTS $2" >> "$T/$n.cfg"
  tlc "$T/$n.cfg" "$n"
  if grep -q "Invariant $2 is violated" "$T/$n.log"; then
    echo "ok    plant     $1 with $2 alone: Invariant $2 is violated ($(states "$n") distinct states when found)"
  else
    echo "FAIL  plant     $1 with $2 alone: expected a violation"; grep -m3 -E 'Error|No error' "$T/$n.log"; fail=1
  fi
}
witness() {  # base cfg, Wit_ name
  n="wit-${1%.cfg}-$2"
  grep -v -E '^(INVARIANTS|PROPERTIES)' "$1" > "$T/$n.cfg"; echo "INVARIANTS $2" >> "$T/$n.cfg"
  tlc "$T/$n.cfg" "$n"
  if grep -q "Invariant $2 is violated" "$T/$n.log"; then
    echo "ok    witness   $2 reached under ${1%.cfg} ($(states "$n") distinct states when found)"
  else
    echo "FAIL  witness   $2 is not reached under ${1%.cfg}"; grep -m3 -E 'Error|No error' "$T/$n.log"; fail=1
  fi
}

closes Consent_head_form.cfg
closes Consent_ruled_st.cfg
closes Consent_replication.cfg
if [ "$1" != "--quick" ]; then
  closes Consent_head_counts.cfg
  closes Consent_head_ends.cfg
fi

# the two sentences, each against the other's reading: neither is chosen here
breaks Consent_counts_vs_3121.cfg 'Invariant Inv_ReplacedBindingEndsGrant is violated'
breaks Consent_ends_vs_331.cfg 'Action property Prop_TransferKeepsFold is violated'

# a row that waited on a binding: the ruled reading against the wider bound W would give were it measured at the count
breaks Consent_waited_counted.cfg 'Invariant Inv_CountedWithinW is violated'
breaks Consent_waited_reach.cfg 'Invariant Inv_LateRevocationWithinW_Waited is violated'

# planted breaks (the two _form plants read no variable, so TLC reports them before the search: 'is equal to FALSE')
breaks Consent_instant.cfg 'Invariant Inv_BackdatedGrantRefused is violated'
breaks Consent_instant_stranger.cfg 'Invariant Inv_StrangerNeverGrants is violated'
breaks Consent_instant_form.cfg 'The invariant of Inv_InstantBuysNoStanding is equal to FALSE'
breaks Consent_current_view.cfg 'Action property Prop_TransferMovesNoVerdict is violated'
breaks Consent_current_view_form.cfg 'The invariant of Inv_SameVerdictOnceHeld is equal to FALSE'
breaks Consent_no_boundary.cfg 'Invariant Inv_RevocationIsBoundary is violated'
breaks Consent_literal_signer.cfg 'Invariant Inv_OwnerCanRecant is violated'
breaks Consent_no_W.cfg 'Invariant Inv_BackdateBounded is violated'

breaks Consent_any_scope.cfg 'Invariant Inv_EmptyScopeMatchesNothing is violated'
breaks Consent_forged_expiry.cfg 'Invariant Inv_ExpiryEmittedBySubstrate is violated'
breaks Consent_eager_decay.cfg 'Invariant Inv_DecayForwardOnly is violated'
breaks Consent_decay_back.cfg 'Action property Prop_DecayForwardOnly is violated'
breaks Consent_decay_stalls.cfg 'Temporal properties were violated'
breaks Consent_decay_never.cfg 'Temporal properties were violated'
breaks Consent_blind_send.cfg 'Invariant Inv_ReplicationNeedsDirectedGrant is violated'
breaks Consent_no_wait.cfg 'Invariant Inv_HeldUntilBindingArrives is violated'
breaks Consent_stranger_repl.cfg 'Invariant Inv_ReplicationGrantHasStanding is violated'
breaks Consent_tie_largest.cfg 'Invariant Inv_TieOnSmallestId is violated'
breaks Consent_stranger_ok.cfg 'Invariant Inv_StrangerNeverGrants is violated'
breaks_one Consent_no_boundary.cfg Inv_RevokedOverridesGranted
breaks_one Consent_no_W.cfg Inv_LateRevocationWithinW

# witnesses
for w in Wit_OldHeadAfterTransfer Wit_OldHeadWhileHoldingB2 Wit_CaptureHoldingB2 Wit_NewOwnerGrants Wit_NodeRegrants Wit_NodeGrantsAtB1 \
         Wit_O1RevokesHoldingB2 Wit_BackdatedWithinW Wit_LateRevocation Wit_FreshGrantAfterRevocation Wit_AgentRevokes Wit_O2Revokes \
         Wit_WaitedRowCounted Wit_WaitedGrantCounted Wit_WaitedRevocationReachesPastW Wit_WithdrawnOwnerGrantsHoldingB2 Wit_WithdrawnOwnerStopsNewOwner; do
  witness Consent_head_counts.cfg $w
done
witness Consent_replication.cfg Wit_PeerHolds
for w in Wit_OldHeadAfterTransfer Wit_CaptureHoldingB2 Wit_FoldEndsOnArrival Wit_NodeRegrants Wit_O1RevokesHoldingB2 \
         Wit_WaitedGrantCounted Wit_WithdrawnOwnerStopsNewOwner; do
  witness Consent_head_ends.cfg $w
done
for w in Wit_ExpiredEmitted Wit_DecayComplete Wit_DecayOnExpiry Wit_ScoreAfterRevocation Wit_ScoreOnTiedGrants; do
  witness Consent_ruled_st.cfg $w
done

echo "fail=$fail"
exit $fail
