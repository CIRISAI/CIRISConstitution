#!/bin/bash
# The genesis's interleavings under TLC: one configuration that closes, and one twin per planted break that must
# fail on its own invariant. Needs Java and tla2tools.jar (v1.7.4, as the continuous build pins it).
#   bash formal/ceremony/run_tlc.sh /path/to/tla2tools.jar [metadir]
# Prints one line per run and ok=N bad=M last; exits M.
cd "$(dirname "$0")"
JAR="${1:?tla2tools.jar}"; META="${2:-${RUNNER_TEMP:-/tmp}/cutover-tlc}"
ok=0; bad=0
tlc(){ java -Xmx2g -cp "$JAR" tlc2.TLC -workers 2 -metadir "$META/$1" -deadlock -config "$1.cfg" Cutover.tla > "$META.$1.log" 2>&1; }
mkdir -p "$META"
for c in Cutover; do
  tlc $c; if grep -q "No error has been found" "$META.$c.log"; then ok=$((ok+1)); echo "closes: $c $(grep -o '[0-9]* distinct states found, 0 states left' "$META.$c.log")"; else bad=$((bad+1)); echo "XX does not close: $c"; tail -20 "$META.$c.log"; fi
done
while read -r c inv; do
  tlc $c; if grep -q "Invariant $inv is violated" "$META.$c.log"; then ok=$((ok+1)); echo "twin fails as it must: $c ($inv)"; else bad=$((bad+1)); echo "XX twin not caught: $c ($inv)"; tail -20 "$META.$c.log"; fi
done <<'T'
Cutover_acceptearlier Inv_P1
Cutover_arrival Inv_P9
Cutover_carries Inv_P2
Cutover_earliervotes Inv_P7
Cutover_ungated Inv_HaltAvailable
Cutover_norecords Inv_HaltPathOpen
Cutover_earlierhalt Inv_NoEarlierLatch
T
rm -rf "$META" "$META".*.log
echo "ok=$ok bad=$bad"
exit $bad
