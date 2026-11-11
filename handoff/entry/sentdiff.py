import re,sys,difflib
name=sys.argv[1]
def sents(f):
    t=open(f).read()
    t=re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    out=[]
    for para in t.split("\n"):
        para=para.strip()
        if not para: continue
        for s in re.split(r"(?<=[.:;])\s+", para):
            s=s.strip()
            if s: out.append(s)
    return out
def norm(s): return re.sub(r"[^a-z0-9]+"," ",s.lower()).strip()
old=sents(name+".old.md"); new=sents(name+".new.md")
oldn=" ".join(norm(s) for s in old)
newn=" ".join(norm(s) for s in new)
print("== NEW sentences whose normalized text is not a substring of OLD ==")
for s in new:
    n=norm(s)
    if n and n not in oldn:
        # find closest old
        best=max(old,key=lambda o: difflib.SequenceMatcher(None,norm(o),n).ratio())
        print("N:",s); print("  ~O:",best[:400]); print()
