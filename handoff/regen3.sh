#!/bin/bash
# Part 3 regeneration + registry diff against the saved copy; prints regen_fail
cd "$(git rev-parse --show-toplevel)"
S="${HANDOFF_TMP:-/tmp/cc-handoff}"; mkdir -p "$S"
f=0
for c in "python3 tools/build_cc_namespace.py" "python3 tools/cc_namespace_match.py --write-vectors" "python3 tools/build_family_model.py" "python3 tools/build_transitions.py" "python3 -I tools/mesh_story.py"; do $c > $S/regen.out 2>&1 || { f=1; echo "XX $c"; tail -5 $S/regen.out; }; done
echo regen_fail=$f
python3 - <<'P'
import json
import os; S=os.environ.get('HANDOFF_TMP','/tmp/cc-handoff')+'/'
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
