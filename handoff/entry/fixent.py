#!/usr/bin/env python3
"""Apply (old,new) pairs to entry phrases that no longer stand in <name>.new.md. usage: fixent.py <name>; pairs on stdin."""
import sys, ast
n=sys.argv[1]; pairs=ast.literal_eval(sys.stdin.read())
new=open(n+'.new.md').read(); L=open(n+'.entries.tsv').read().split('\n')
for i,l in enumerate(L):
    if not i or not l: continue
    f=l.split('\t')
    if f[-1] not in new:
        for a,b in pairs: f[-1]=f[-1].replace(a,b)
        L[i]='\t'.join(f)
open(n+'.entries.tsv','w').write('\n'.join(L))
print(n,'still missing:',[l.split('\t')[-1][:100] for l in L[1:] if l and l.split('\t')[-1] not in new])
