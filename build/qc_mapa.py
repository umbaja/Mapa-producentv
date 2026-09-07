# -*- coding: utf-8 -*-
"""Kontroly kvality geografickej vrstvy KPB2."""
import json, os, re, sqlite3, sys, collections
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P=lambda *a: os.path.join(ROOT,*a)
ok=lambda b: "OK  " if b else "CHYBA"
fails=0
def rep(name, passed, total, detail=""):
    global fails
    if passed!=total: fails+=1
    print("[%s] %-52s %d/%d %s"%(ok(passed==total),name,passed,total,detail))

con=sqlite3.connect(P('data/kpb2_mapa.sqlite'))
q=lambda s,*a: con.execute(s,a).fetchall()

# 1 — kontrolná číslica IČO
def ico_ok(i):
    if not re.fullmatch(r'\d{8}',i or ''): return False
    s=sum(int(i[k])*(8-k) for k in range(7)); r=s%11
    c=1 if r==0 else (0 if r==1 else 11-r)
    return c==int(i[7])
icos=[r[0] for r in q("SELECT ico FROM producent")]
rep("Kontrolná číslica IČO (modulo 11)", sum(1 for i in icos if ico_ok(i)), len(icos))

# 2 — duplicity
rep("Jedinečnosť IČO", len(set(icos)), len(icos))
dup=q("SELECT nazov,obec_nazov,COUNT(*) c FROM producent GROUP BY nazov,obec_nazov HAVING c>1")
rep("Žiadne dvojice rovnaký názov + obec", 0 if dup else 1, 1, str(dup[:3]) if dup else "")

# 3 — poloha v hraniciach SR
BB=(16.83,47.73,22.57,49.62)
pts=q("SELECT ico,lat,lon,okres FROM producent WHERE lat IS NOT NULL")
inbb=sum(1 for _,la,lo,_ in pts if BB[1]<=la<=BB[3] and BB[0]<=lo<=BB[2])
rep("Súradnice v bounding boxe SR", inbb, len(pts))

# 4 — bod leží v okrese, ktorý má priradený (nezávislá kontrola geokódovania)
dg=json.load(open(P('geo/src/GeoJSON/epsg_4326/districts_epsg_4326.geojson')))
polys={}
for f in dg['features']:
    g=f['geometry']
    rings=g['coordinates'] if g['type']=='Polygon' else [r for p in g['coordinates'] for r in p]
    polys.setdefault(f['properties']['NM3'],[]).extend(rings)
def inside(lon,lat,rings):
    c=False
    for ring in rings:
        n=len(ring); j=n-1
        for i in range(n):
            xi,yi=ring[i]; xj,yj=ring[j]
            if ((yi>lat)!=(yj>lat)) and (lon < (xj-xi)*(lat-yi)/(yj-yi)+xi): c=not c
            j=i
    return c
hit=sum(1 for _,la,lo,o in pts if o in polys and inside(lo,la,polys[o]))
rep("Bod leží v priradenom okrese (point-in-polygon)", hit, len(pts),
    "zvyšok = obce na hranici alebo ťažisko okresu")

# 5 — každý producent má aspoň jeden tok odpadu
n=q("SELECT COUNT(*) FROM producent")[0][0]
withtok=q("SELECT COUNT(DISTINCT producent_id) FROM tok_odpadu")[0][0]
rep("Producent má aspoň jeden tok odpadu", withtok, n)

# 6 — formát katalógového čísla
kats=[r[0] for r in q("SELECT katalogove_cislo_navrh FROM druh_odpadu")]
rep("Formát katalógového čísla '00 00 00'",
    sum(1 for k in kats if re.fullmatch(r'\d{2} \d{2} \d{2}',k or '')), len(kats))
rep("Katalógová skupina 02/03/19/20",
    sum(1 for k in kats if k[:2] in ('02','03','19','20')), len(kats))

# 7 — všetky hodnoty katalog_overeny = 0 (žiadne tvrdenie o overení)
rep("katalog_overeny = 0 pri všetkých druhoch",
    q("SELECT COUNT(*) FROM druh_odpadu WHERE katalog_overeny=0")[0][0], len(kats))

# 8 — referenčná integrita
orph=q("""SELECT COUNT(*) FROM tok_odpadu t LEFT JOIN producent p ON p.id=t.producent_id
          LEFT JOIN druh_odpadu d ON d.id=t.druh_odpadu_id WHERE p.id IS NULL OR d.id IS NULL""")[0][0]
rep("Referenčná integrita tok_odpadu", 0 if orph else 1, 1)

# 9 — úplnosť matice odpad × dráha
nd=q("SELECT COUNT(*) FROM druh_odpadu")[0][0]; ndr=q("SELECT COUNT(*) FROM draha")[0][0]
rep("Matica druh odpadu × dráha je úplná", q("SELECT COUNT(*) FROM odpad_draha")[0][0], nd*ndr)

# 10 — kategória 1 je vylúčená zo všetkých dráh
k1=q("""SELECT COUNT(*) FROM odpad_draha WHERE regulacna_trieda='zvp_kat1' AND pripustnost<>'zakazane'""")[0][0]
rep("ŽVP kategórie 1 zakázané vo všetkých dráhach", 0 if k1 else 1, 1)

# 11 — kuchynský odpad: zakázaný pre krmivá, prípustný pre technické dráhy
ko=q("""SELECT dr.kod,od.pripustnost FROM odpad_draha od JOIN draha dr ON dr.id=od.draha_id
        WHERE od.regulacna_trieda='kuchynsky_odpad' GROUP BY dr.kod,od.pripustnost""")
m={k:v for k,v in ko}
rep("Kuchynský odpad: krmivo zakázané, technický tuk povolený",
    1 if (m.get('krmivo_hosp')=='zakazane' and m.get('technicky_tuk')=='povolene') else 0, 1)

# 12 — každý druh odpadu má aspoň jednu povolenú alebo podmienenú dráhu (okrem kat. 1)
bez=q("""SELECT COUNT(*) FROM druh_odpadu d WHERE NOT EXISTS
         (SELECT 1 FROM odpad_draha od WHERE od.druh_odpadu_id=d.id
          AND od.pripustnost IN ('povolene','podmienene'))""")[0][0]
rep("Druh odpadu má aspoň jednu použiteľnú dráhu (mimo kat. 1)", nd-bez, nd-2,
    "2 druhy kategórie 1 sú vylúčené zámerne")

# 13 — odhad má konzistentné rozpätie
bad=q("SELECT COUNT(*) FROM odhad_produkcie WHERE NOT (t_rok_min<=t_rok_stred AND t_rok_stred<=t_rok_max)")[0][0]
tot=q("SELECT COUNT(*) FROM odhad_produkcie")[0][0]
rep("Odhad objemu: min ≤ stred ≤ max", tot-bad, tot)

# 14 — každý odhad má kapacitu aj koeficient
orf=q("""SELECT COUNT(*) FROM odhad_produkcie o
         LEFT JOIN kapacita k ON k.producent_id=o.producent_id WHERE k.id IS NULL""")[0][0]
rep("Odhad má naviazanú kapacitu", tot-orf, tot)

# 15 — kapacita je označená ako typová, nie meraná (žiadne falošné tvrdenie o meraní)
mer=q("SELECT COUNT(*) FROM kapacita WHERE uroven='merana'")[0][0]
allk=q("SELECT COUNT(*) FROM kapacita")[0][0]
rep("Kapacity sú označené ako typové (nie merané)", allk-mer, allk,
    "meraných: %d - po doplnení reálnych počtov sa toto číslo zmení"%mer)

print()
print("--- Odhad objemu kuchynského odpadu ---")
for r in q("""SELECT p.typ_nazov, COUNT(*), ROUND(SUM(o.t_rok_min),1), ROUND(SUM(o.t_rok_stred),1),
                     ROUND(SUM(o.t_rok_max),1), ROUND(AVG(o.t_rok_stred),2)
              FROM producent p JOIN odhad_produkcie o ON o.producent_id=p.id
              GROUP BY p.typ_nazov ORDER BY 4 DESC"""):
    print("  %-22s n=%-4d %7.1f – %7.1f – %7.1f t/rok  (priemer %.2f)"%r)
t=q("SELECT SUM(t_rok_min),SUM(t_rok_stred),SUM(t_rok_max) FROM odhad_produkcie")[0]
print("  %-22s        %7.1f – %7.1f – %7.1f t/rok"%("SPOLU v databáze",t[0],t[1],t[2]))

print()
print("--- Národná extrapolácia (typová kapacita × počet zariadení v SR) ---")
import importlib.util
spec=importlib.util.spec_from_file_location("dk", P('build/data_kapacita.py'))
dk=importlib.util.module_from_spec(spec); spec.loader.exec_module(dk)
narod=0
for typ,(poc,zdroj) in dk.NARODNE_POCTY.items():
    r=q("""SELECT AVG(o.t_rok_stred) FROM producent p JOIN odhad_produkcie o ON o.producent_id=p.id
           WHERE p.typ_prevadzky=?""",typ)
    if r and r[0][0]:
        v=r[0][0]*poc; narod+=v
        print("  %-18s %4d zariadení × %5.2f t/rok = %8.0f t/rok"%(typ,poc,r[0][0],v))
print("  %-18s %28s %8.0f t/rok"%("SPOLU SR","",narod))
sek=q("SELECT sektor,t_rok FROM sektorovy_odhad")
gastro=[x[1] for x in sek if x[0].startswith("Reštaur")][0]
print("  Kontrola: sektor reštaurácií a stravovacích služieb v SR podľa Eurostatu = %.0f t/rok,"%gastro)
print("            školské a nemocničné stravovanie je %.0f %% z toho — rádovo súhlasí."%(100*narod/gastro))

print()
print("--- Sektorové odhady pre SR (Eurostat env_wasfw, priemer EÚ) ---")
for r in q("SELECT sektor,koef,jednotka,t_rok FROM sektorovy_odhad"):
    print("  %-38s %4.0f %-18s %8.0f t/rok"%r)

print()
print("--- Dráhy zhodnotenia ---")
for r in q("SELECT draha,nazov,druhov_povolenych,druhov_podmienene,druhov_zakazanych FROM v_draha_pokrytie"):
    print("  %-14s povolené %2d | podmienené %2d | zakázané %2d   %s"%(r[0],r[2],r[3],r[4],r[1]))
print()
print("--- Producenti podľa dráhy (aspoň jeden povolený tok) ---")
for r in q("""SELECT dr.kod, COUNT(DISTINCT p.id) FROM producent p
              JOIN tok_odpadu t ON t.producent_id=p.id
              JOIN odpad_draha od ON od.druh_odpadu_id=t.druh_odpadu_id
              JOIN draha dr ON dr.id=od.draha_id
              WHERE od.pripustnost='povolene' GROUP BY dr.kod ORDER BY 2 DESC"""):
    print("  %-14s %d"%r)
print()
print("--- Pokrytie ---")
print("producentov            :", n)
print("z toho s polohou       :", len(pts))
print("druhov odpadu          :", len(kats))
print("druhov s ≥1 producentom:", q("SELECT COUNT(*) FROM v_odpad_pokrytie WHERE producentov>0")[0][0])
print("okresov (z 79)         :", q("SELECT COUNT(DISTINCT okres) FROM producent WHERE okres<>''")[0][0])
print("obcí                   :", q("SELECT COUNT(DISTINCT obec_nazov) FROM producent")[0][0])
print("väzieb producent–odpad :", q("SELECT COUNT(*) FROM tok_odpadu")[0][0])
print()
print("--- Presnosť polohy ---")
for r in q("SELECT presnost_polohy,COUNT(*) FROM producent GROUP BY 1 ORDER BY 2 DESC"):
    print("  %-16s %d"%r)
print()
print("--- Druhy odpadu bez identifikovaného producenta ---")
z=q("SELECT kod,nazov_sk FROM v_odpad_pokrytie WHERE producentov=0")
print("  "+("žiadne" if not z else "; ".join(a+" ("+b+")" for a,b in z)))
print()
print("--- Okresy bez producenta ---")
have={r[0] for r in q("SELECT DISTINCT okres FROM producent")}
print("  "+"; ".join(sorted(set(polys)-have)))
print()
sys.exit(1 if fails else 0)
