#!/usr/bin/env bash
# Compiles the stack in order into a temporary directory. Exits 1 on any compile error, any use of
# sorry, or an axiom beyond the three of core Lean (propext, Quot.sound, Classical.choice). Run from anywhere.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
out="$(mktemp -d)"
trap 'rm -rf "$out"' EXIT
rc=0
for f in Order Causal Seat Window Recount Harden Harden2 Harden3 SeatG Terms Reader Merge Consent Carry RosterHead TwoMechanisms KeyEnd Duty Settled; do
  if ! LEAN_PATH="$out" lean -M 6000 -T 200000 --root="$here" -o "$out/$f.olean" "$here/$f.lean" > "$out/$f.log" 2>&1; then
    echo "does not compile: $f"; grep -m5 "error" "$out/$f.log"; rc=1
  fi
  if grep "depends on axioms" "$out/$f.log" | sed 's/propext//g; s/Quot\.sound//g; s/Classical\.choice//g' | grep -q "\[[ ,]*[A-Za-z]"; then
    echo "sorry or an axiom beyond the three of core: $f"; rc=1
  fi
done
n=$(cat "$out"/*.log | grep -c "depend")
echo "causal_order: 19 files, $n theorems reported, rc=$rc"
exit $rc
