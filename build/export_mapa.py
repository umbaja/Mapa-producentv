# -*- coding: utf-8 -*-
"""Vygeneruje assets/mapa_data.js z databázy + zjednodušené hranice okresov."""
import json, os, sqlite3, sys, math
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P=lambda *a: os.path.join(ROOT,*a)

def simplify(ring, tol):
    """Douglas-Peucker."""
    if len(ring) < 3: return ring
    def d(p, a, b):
        (x,y),(x1,y1),(x2,y2)=p,a,b
        dx,dy=x2-x1,y2-y1
        if dx==0 and dy==0: return math.hypot(x-x1,y-y1)
        t=max(0,min(1,((x-x1)*dx+(y-y1)*dy)/(dx*dx+dy*dy)))
        return math.hypot(x-(x1+t*dx), y-(y1+t*dy))
    stack=[(0,len(ring)-1)]; keep={0,len(ring)-1}
    while stack:
        i,j=stack.pop()
        if j<=i+1: continue
        md,mi=0,i
        for k in range(i+1,j):
            dd=d(ring[k],ring[i],ring[j])
            if dd>md: md,mi=dd,k
        if md>tol:
            keep.add(mi); stack.append((i,mi)); stack.append((mi,j))
    return [ring[i] for i in sorted(keep)]

con=sqlite3.connect(P('data/kpb2_mapa.sqlite')); con.row_factory=sqlite3.Row
odpady=[dict(r) for r in con.execute("""SELECT id,kod,nazov_sk,nazov_en,katalogove_cislo_navrh,skupina,
            pravny_status,sezonnost,drahy,poznamka FROM druh_odpadu ORDER BY skupina,nazov_sk""")]
drahy=[dict(r) for r in con.execute("SELECT id,kod,nazov,popis,pravny_ramec FROM draha ORDER BY id")]
SKR={'povolene':'p','podmienene':'c','zakazane':'z','mimo_regulacie':'m'}
perm={}
for r in con.execute("""SELECT od.druh_odpadu_id,dr.kod,od.pripustnost,od.regulacna_trieda,od.poznamka
                        FROM odpad_draha od JOIN draha dr ON dr.id=od.draha_id"""):
    perm.setdefault(r[0],{})[r[1]]=SKR[r[2]]
    perm[r[0]]['_t']=r[3]; perm[r[0]]['_p']=r[4]
for o in odpady:
    o['dr']=perm.get(o['id'],{})
kap={}
for r in con.execute("SELECT producent_id,hodnota,jednotka,uroven FROM kapacita"):
    kap[r[0]]=[r[1],r[2],r[3]]
odh={}
for r in con.execute("""SELECT producent_id,ROUND(SUM(t_rok_min),2),ROUND(SUM(t_rok_stred),2),
                               ROUND(SUM(t_rok_max),2) FROM odhad_produkcie GROUP BY producent_id"""):
    odh[r[0]]=[r[1],r[2],r[3]]
koef=[dict(r) for r in con.execute("""SELECT k.typ_prevadzky,d.kod AS odpad_kod,k.koef_min,k.koef_stred,
        k.koef_max,k.koef_jednotka,k.jedal_za_den,k.podiel_stravnikov,k.dni_rok,k.zdroj,k.doi,
        k.uroven_dokazu,k.poznamka FROM koeficient_produkcie k
        JOIN druh_odpadu d ON d.id=k.druh_odpadu_id""")]
sekt=[dict(r) for r in con.execute("SELECT sektor,koef,jednotka,populacia,t_rok,zdroj,poznamka FROM sektorovy_odhad")]
prod=[]
tok={}
for r in con.execute("SELECT producent_id,druh_odpadu_id FROM tok_odpadu"):
    tok.setdefault(r[0],[]).append(r[1])
for r in con.execute("""SELECT id,ico,nazov,ulica,psc,obec_nazov,okres,kraj,lat,lon,presnost_polohy,
                        typ_prevadzky,typ_nazov,sektor FROM producent ORDER BY nazov"""):
    d=dict(r)
    if d['lat'] is None: continue
    prod.append([d['ico'],d['nazov'],d['ulica'] or '',d['psc'] or '',d['obec_nazov'],d['okres'],d['kraj'],
                 round(d['lat'],5),round(d['lon'],5),d['presnost_polohy'],d['typ_prevadzky'],
                 d['typ_nazov'],d['sektor'],sorted(tok.get(d['id'],[])),
                 kap.get(d['id']), odh.get(d['id'])])
zdroje=[dict(r) for r in con.execute("SELECT * FROM zdroj_geo")]

dg=json.load(open(P('geo/src/GeoJSON/epsg_4326/districts_epsg_4326.geojson')))
okresy=[]
TOL=0.004
for f in dg['features']:
    g=f['geometry']; polys = g['coordinates'] if g['type']=='Polygon' else [r for p in g['coordinates'] for r in p]
    rings=[]
    for ring in polys:
        s=simplify([(round(x,4),round(y,4)) for x,y in ring],TOL)
        if len(s)>=4: rings.append([[x,y] for x,y in s])
    if rings: okresy.append({"n":f['properties']['NM3'],"r":rings})

out=P('assets/mapa_data.js')
os.makedirs(P('assets'),exist_ok=True)
with open(out,'w',encoding='utf-8') as fh:
    fh.write("// GENEROVANÉ build/export_mapa.py — neupravovať ručne\n")
    fh.write("window.MAPA={\n")
    fh.write(" odpady:"+json.dumps(odpady,ensure_ascii=False)+",\n")
    fh.write(" drahy:"+json.dumps(drahy,ensure_ascii=False)+",\n")
    fh.write(" koeficienty:"+json.dumps(koef,ensure_ascii=False)+",\n")
    fh.write(" sektorove:"+json.dumps(sekt,ensure_ascii=False)+",\n")
    fh.write(" producenti:"+json.dumps(prod,ensure_ascii=False)+",\n")
    fh.write(" okresy:"+json.dumps(okresy,ensure_ascii=False)+",\n")
    fh.write(" zdroje:"+json.dumps(zdroje,ensure_ascii=False)+",\n")
    fh.write(" polia:['ico','nazov','ulica','psc','obec','okres','kraj','lat','lon','presnost','typ','typ_nazov','sektor','odpady','kapacita','odhad']\n};\n")
print("producentov:",len(prod),"| druhov odpadu:",len(odpady),"| okresov:",len(okresy),
      "| velkost:",round(os.path.getsize(out)/1024),"kB")
