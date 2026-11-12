#!/bin/bash
# regenerators + gates under one fail flag; prints fail=N last
cd "$(git rev-parse --show-toplevel)"
S="${HANDOFF_TMP:-/tmp/cc-handoff}"; mkdir -p "$S"
fail=0
run(){ "$@" > "$S/gate.out" 2>&1; rc=$?; if [ $rc -ne 0 ] || grep -q "FAIL" "$S/gate.out"; then fail=1; echo "XX rc=$rc: $*"; tail -12 "$S/gate.out"; else echo "ok: $*"; fi; }
run python3 tools/build_cc_namespace.py
run python3 tools/cc_namespace_match.py --write-vectors
run python3 tools/build_cc_signed_object.py
run python3 tools/build_governance_policy.py
run python3 tools/build_csd4_chain.py
run python3 tools/topology_to_cfg.py --all
run python3 tools/build_promise_status.py
run python3 build_pdf.py --write-toc-volumes
run python3 tools/build_family_model.py
run python3 tools/build_ietf_draft.py
git checkout -- ietf/
run python3 tools/check_claims.py
cp "$S/gate.out" "$S/check_claims.out"
run python3 tools/check_links.py
run python3 tools/check_stale_refs.py
run python3 tools/check_formal_counts.py
run python3 tools/check_formal_tables.py
run python3 tools/check_lifecycle_coverage.py
run python3 tools/check_family_kinds.py --check
run python3 tools/build_family_model.py --check
run python3 tools/guard_grammar.py
run python3 tools/change_grammar.py
run python3 tools/fold_grammar.py
run python3 tools/build_transitions.py --check
run python3 tools/build_reactions.py --check
run python3 tools/family_card.py --check
run python3 -I tools/mesh_story.py --check
run python3 -I tools/check_fold_order.py
run python3 tools/check_transition_roles.py
run python3 tools/check_signer_gate.py
run python3 formal/takedown/takedown_model.py --check
run python3 formal/deletion/deletion_model.py --check
run python3 formal/owner_binding/owner_binding_model.py --check
run python3 formal/key_plane/key_plane_model.py --check
run python3 formal/guardianship/guardianship_model.py --check
run python3 formal/ranked_choice/ranked_choice_model.py --check
run python3 formal/set_item/set_item_model.py --check
run python3 -I formal/kernel_lib/kernel_lib_check.py --check
run python3 -I formal/causal_kernel/check.py --bound 5
run python3 -I formal/causal_kernel/check_cut.py
run python3 -I formal/causal_kernel/check_lock.py
run python3 -I formal/roster_fork/fork_check.py --check
run python3 tools/ui_closure.py --check
run python3 tools/check_termination.py
run python3 tools/kernel_closure.py --check
run python3 tools/kernel_requirements.py --check
run python3 tools/family_need.py --check
run python3 -I formal/transport_tiers/frame_ab.py --check
run python3 tools/check_compliance_wire_forms.py
run python3 tools/check_rule_entries.py
run python3 tools/check_ui_primitives.py
echo "fail=$fail"
exit $fail
