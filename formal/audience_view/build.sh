#!/usr/bin/env bash
# Compiles AudienceView.lean with `#print axioms` added for every theorem it declares. Exits 1 on a
# compile error, a `sorry`, an axiom beyond the three of core Lean (propext, Quot.sound,
# Classical.choice), or a theorem whose axioms were not reported. Then plants two breaks (a theorem
# proved by `sorry`, a theorem resting on a new axiom) and exits 1 unless each is caught. Run from anywhere.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
out="$(mktemp -d)"
trap 'rm -rf "$out"' EXIT

scan() { # $1 = source file; prints the problems found, exits 1 on any
  local src="$1" log="$out/scan.log" names
  names=$(grep -oE '^theorem [^ ({:]+' "$src" | awk '{print $2}')
  cp "$src" "$out/Probe.lean"
  for n in $names; do echo "#print axioms AudienceView.$n" >> "$out/Probe.lean"; done
  if ! lean -M 6000 -T 200000 "$out/Probe.lean" > "$log" 2>&1; then
    echo "does not compile"; grep -m5 "error" "$log"; return 1
  fi
  if grep -nE '(:=|by)[[:space:]]*sorry' "$src" > /dev/null; then echo "a sorry in the source"; return 1; fi
  if grep "depends on axioms" "$log" | sed 's/propext//g; s/Quot\.sound//g; s/Classical\.choice//g' | grep -q "\[[ ,]*[A-Za-z]"; then
    echo "an axiom beyond the three of core:"; grep "depends on axioms" "$log" | grep -vE "\[(propext|Quot\.sound|Classical\.choice|, )*\]$"; return 1
  fi
  for n in $names; do
    grep -qE "'AudienceView\.$n' (depends on axioms|does not depend on any axioms)" "$log" || { echo "no axiom report for $n"; return 1; }
  done
  echo "$(echo "$names" | wc -w) theorems, every one on core axioms at most"
  return 0
}

rc=0
if ! r=$(scan "$here/AudienceView.lean"); then echo "audience_view: $r"; rc=1; else echo "audience_view: $r"; fi

# planted break 1: a theorem proved by sorry
sed 's/^end AudienceView$/theorem planted_sorry : False := sorry\nend AudienceView/' "$here/AudienceView.lean" > "$out/B1.lean"
if scan "$out/B1.lean" > /dev/null; then echo "planted break not caught: sorry"; rc=1; else echo "planted break caught: sorry"; fi
# planted break 2: a theorem resting on a new axiom
sed 's/^end AudienceView$/axiom planted_axiom : False\ntheorem planted_ax : False := planted_axiom\nend AudienceView/' "$here/AudienceView.lean" > "$out/B2.lean"
if scan "$out/B2.lean" > /dev/null; then echo "planted break not caught: new axiom"; rc=1; else echo "planted break caught: new axiom"; fi

echo "audience_view rc=$rc"
exit $rc
