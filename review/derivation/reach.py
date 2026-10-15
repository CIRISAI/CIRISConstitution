import json,re,glob,collections,os,sys
CC='/home/emoore/CIRISConstitution'
reg=json.load(open(f'{CC}/manifests/namespace_registry.json'))['families']
def stem(p):
    segs=[]
    for s in p.split(':'):
        if s=='*' or s.startswith('{'): break
        segs.append(s)
    return ':'.join(segs)
stems={f['prefix']:stem(f['prefix']) for f in reg}
pat={p:re.compile(r'(?<![A-Za-z0-9_])'+re.escape(s)+r'(?![A-Za-z0-9_])') for p,s in stems.items()}
# sections
parts=sorted(glob.glob(f'{CC}/constitution/part_*.md'))
H=re.compile(r'^(#{2,6})\s+(\d+(?:\.\d+)*)\b')
sections={}  # decimal -> text (incl. subsections)
for pf in parts:
    lines=open(pf,encoding='utf-8').read().split('\n')
    heads=[(i,len(m.group(1)),m.group(2)) for i,l in enumerate(lines) if (m:=H.match(l))]
    for k,(i,lvl,dec) in enumerate(heads):
        j=len(lines)
        for i2,l2,d2 in heads[k+1:]:
            if l2<=lvl: j=i2; break
        sections.setdefault(dec,'')
        sections[dec]+='\n'.join(lines[i:j])+'\n'
# promise -> G rows (P00 0b) ; G -> cites
p00=open(f'{CC}/review/pieces/00_guarantees.md',encoding='utf-8').read()
pm={}
for m in re.finditer(r'^\| (\d)\. [^|]+\| ([^|]+)\|',p00,re.M):
    pm[int(m.group(1))]=re.findall(r'G\d+',m.group(2))
gc={}
for m in re.finditer(r'^\| (G\d+) \| [^|]+\| [^|]+\| ([^|]+)\|',p00,re.M):
    if m.group(1) not in gc: gc[m.group(1)]=re.findall(r'\d+(?:\.\d+)+|\b[1-9]\.\d+\b',m.group(2))
reach=collections.defaultdict(set); missing=set()
for p,gs in pm.items():
    for g in gs:
        for dec in gc.get(g,[]):
            if dec not in sections: missing.add(dec); continue
            t=sections[dec]
            for pfx,rx in pat.items():
                if rx.search(t): reach[pfx].add(p)
print("promise->G:",{p:len(g) for p,g in pm.items()})
print("cites not found as headings:",sorted(missing))
# CSD reach
csd=collections.defaultdict(set)
for f in glob.glob('/home/emoore/CIRISClient/FSD/CSD/CSD-*.md')+glob.glob('/home/emoore/CIRISRegistry/FSD/CSD/CSD-*.md'):
    t=open(f,encoding='utf-8').read(); cid=os.path.basename(f)[:7]
    for pfx,rx in pat.items():
        if rx.search(t): csd[pfx].add(cid)
allp=[f['prefix'] for f in reg]
byrule=[p for p in allp if reach[p]]; bycsd=[p for p in allp if csd[p]]
neither=[p for p in allp if not reach[p] and not csd[p]]
csd_only=[p for p in allp if csd[p] and not reach[p]]
rule_only=[p for p in allp if reach[p] and not csd[p]]
print(f"families {len(allp)}: reached by promises {len(byrule)}, by CSDs {len(bycsd)}, by both {len([p for p in allp if reach[p] and csd[p]])}, by neither {len(neither)}, CSD-only {len(csd_only)}, promise-only {len(rule_only)}")
comp={f['prefix']:f['owning_component'] for f in reg}
def grp(lst):
    c=collections.Counter(comp[p] for p in lst); return dict(c)
print("neither by component:",grp(neither)); print("csd-only by component:",grp(csd_only)); print("promise-only by component:",grp(rule_only))
print("\n== per promise family count:",{p:len([x for x in allp if p in reach[x]]) for p in range(1,10)})
json.dump({'reach':{p:sorted(v) for p,v in reach.items()},'csd':{p:sorted(v) for p,v in csd.items()},'neither':neither,'csd_only':csd_only,'rule_only':rule_only,'comp':comp},open(sys.argv[1],'w'),indent=1)
print("\n== NEITHER:"); [print(' ',comp[p].ljust(18),p) for p in neither]
print("\n== CSD-ONLY (surface, no promise):"); [print(' ',comp[p].ljust(18),p.ljust(50),','.join(sorted(csd[p]))[:60]) for p in csd_only]
print("\n== PROMISE-ONLY (rule, no screen):"); [print(' ',comp[p].ljust(18),p.ljust(50),sorted(reach[p])) for p in rule_only]
