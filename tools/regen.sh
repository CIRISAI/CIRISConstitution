#!/bin/bash
# Regenerate what a text edit moves (the namespace registry and its match vectors, the family
# model, the transitions, the mesh story), print regen_fail=N, then list every path at which
# manifests/namespace_registry.json differs from the copy saved before the edit in
# $GATES_TMP/registry.before.json (default /tmp/cc-gates). Exits N.
#   cp manifests/namespace_registry.json "${GATES_TMP:-/tmp/cc-gates}/registry.before.json"   # before the edit
#   bash tools/regen.sh                                                                         # after it
cd "$(git rev-parse --show-toplevel)"
S="${GATES_TMP:-/tmp/cc-gates}"; mkdir -p "$S"
f=0
for c in "python3 tools/build_cc_namespace.py" "python3 tools/cc_namespace_match.py --write-vectors" "python3 tools/build_family_model.py" "python3 tools/build_transitions.py" "python3 -I tools/mesh_story.py"; do $c > $S/regen.out 2>&1 || { f=1; echo "XX $c"; tail -5 $S/regen.out; }; done
echo regen_fail=$f
python3 - <<'P'
import json
import os; S=os.environ.get('GATES_TMP','/tmp/cc-gates')+'/'
a=json.load(open(S+'registry.before.json')); b=json.load(open('manifests/namespace_registry.json'))
def walk(x,y,p=''):
    if type(x)!=type(y): print('type',p); return
    if isinstance(x,dict):
        for k in set(x)|set(y):
            if k not in x or k not in y: print('key',p+'/'+k)
            else: walk(x[k],y[k],p+'/'+k)
    elif isinstance(x,list):
        if len(x)!=len(y): print('len',p,len(x),len(y)); return
        for i,(u,v) in enumerate(zip(x,y)): walk(u,v,p+'/'+str(i))
    elif x!=y: print('diff',p)
walk(a,b)
P
exit $f
