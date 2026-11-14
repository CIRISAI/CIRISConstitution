#!/bin/bash
# Compatibility copy: the regenerator is tools/regen.sh. Kept until handoff/ is deleted at the cut.
export GATES_TMP="${GATES_TMP:-${HANDOFF_TMP:-/tmp/cc-handoff}}"
exec bash "$(git rev-parse --show-toplevel)/tools/regen.sh" "$@"
