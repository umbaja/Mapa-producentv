import sys,re,glob
def ico_ok(ico):
    if not re.fullmatch(r'\d{8}',ico): return False
    w=[8,7,6,5,4,3,2]
    s=sum(int(ico[i])*w[i] for i in range(7))
    r=s%11
    c=(11-r)%10 if r!=0 else 0
    # standard SK/CZ algorithm
    if r==0: c=1
    elif r==1: c=0
    else: c=11-r
    return c==int(ico[7])
if __name__=="__main__":
    tot=bad=0
    for f in glob.glob("build/rpo_raw/*.txt"):
        for ln in open(f,encoding="utf-8"):
            ln=ln.strip()
            if not ln or ln.startswith("#") or ln.startswith("COUNT"): continue
            ico=ln.split("|")[0].strip()
            tot+=1
            if not ico_ok(ico):
                bad+=1; print("BAD",f,ln[:70])
    print(f"IČO kontrolná číslica: {tot-bad}/{tot} OK")
