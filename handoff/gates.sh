#!/bin/bash
# Compatibility copy: the gate is tools/gates.sh. Kept until handoff/ is deleted at the cut.
export GATES_TMP="${GATES_TMP:-${HANDOFF_TMP:-/tmp/cc-handoff}}"
exec bash "$(git rev-parse --show-toplevel)/tools/gates.sh" "$@"
