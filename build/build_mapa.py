# -*- coding: utf-8 -*-
"""Zostaví geografickú vrstvu databázy KPB2: producenti biotransformovateľných odpadov v SR.

Vstupy:  build/rpo_raw/*.txt        - surové výpisy z RPO (ŠÚ SR, CC-BY 4.0)
         data/csv/gazetteer_obce.csv - bodový gazetteer obcí (OSM/ZBGIS, drakh/slovakia-gps-data)
         build/data_odpady.py        - číselník druhov odpadu a väzba typ producenta -> odpad
Výstupy: data/kpb2_mapa.sqlite, data/csv/*.csv, data/producenti.geojson, data/okresy.geojson
"""
import csv, json, os, re, sqlite3, sys, unicodedata, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_odpady import ODPADY, PRODUCENT_ODPAD, SEKTOR, TYP_NAZOV, DRAHY, REGULACIA, TRIEDA
from data_kapacita import TYPOVA_KAPACITA, KOEFICIENTY, SEKTOROVY_ODHAD, NARODNE_POCTY

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)

def norm(s):
    if not s: return ""
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()

def ico_ok(ico):
    if not re.fullmatch(r'\d{8}', ico or ''): return False
    s = sum(int(ico[i]) * (8 - i) for i in range(7))
    r = s % 11
    c = 1 if r == 0 else (0 if r == 1 else 11 - r)
    return c == int(ico[7])

# ---------- 1. gazetteer ----------
gaz = list(csv.DictReader(open(P('data/csv/gazetteer_obce.csv'), encoding='utf-8')))
by_name = {}
RANK = {'city': 0, 'town': 1, 'village': 2, 'suburb': 3, 'hamlet': 4, 'locality': 5}
for g in sorted(gaz, key=lambda x: RANK.get(x['typ'], 9)):
    by_name.setdefault(g['nazov_norm'], g)

# centroidy okresov ako záchranná sieť
_dg = json.load(open(P('geo/src/GeoJSON/epsg_4326/districts_epsg_4326.geojson')))
def _centroid(geom):
    pts = []
    cs = geom['coordinates']
    rings = cs if geom['type'] == 'Polygon' else [r for poly in cs for r in poly]
    for ring in (rings if geom['type'] == 'Polygon' else rings):
        for x, y in ring: pts.append((x, y))
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
OKRES_CENTROID = {f['properties']['NM3']: _centroid(f['geometry']) for f in _dg['features']}

def geocode(municipality):
    """Vráti (gaz_row, presnost). presnost: obec | mestska_cast | obec_zaklad"""
    if not municipality or municipality == 'NA': return None, None
    g = by_name.get(norm(municipality))
    if g: return g, 'obec'
    m = municipality
    part = None
    if ' - ' in m:
        base, rest = m.split(' - ', 1)
        rest = re.sub(r'^mestsk[aá] čas[tť]\s*', '', rest, flags=re.I)
        part = rest.strip()
        m = base.strip()
    if part:
        g = by_name.get(norm(part))
        if g: return g, 'mestska_cast'
    g = by_name.get(norm(m))
    if g: return g, ('obec_zaklad' if part else 'obec')
    return None, None

# ---------- 2. producenti z RPO ----------
producenti = {}
zdrojove_dopyty = []
vynechane = []
for f in sorted(glob.glob(P('build/rpo_raw/*.txt'))):
    kw = sektor = dopyt = None
    for ln in open(f, encoding='utf-8'):
        ln = ln.rstrip('\n')
        if ln.startswith('#'):
            mm = re.search(r'keyword=(\S+)', ln)
            if mm: kw = mm.group(1)
            mm = re.search(r'query=(\S+)', ln)
            if mm: dopyt = mm.group(1)
            continue
        if not ln.strip() or ln.startswith('COUNT'): continue
        p = [x.strip() for x in ln.split('|')]
        if len(p) == 4:
            ico, nazov, obec, obec_kod = p; ulica = psc = 'NA'
        elif len(p) >= 6:
            ico, nazov, ulica, psc, obec, obec_kod = p[:6]
        else:
            continue
        if re.search(r'v\s*(likvid[aá]cii|konkurze)', nazov, re.I):
            vynechane.append((ico, nazov)); continue
        if not ico_ok(ico):
            print('  ! neplatné IČO, preskočené:', ico, nazov[:40]); continue
        if ico in producenti:
            if kw not in producenti[ico]['typy']: producenti[ico]['typy'].append(kw)
            continue
        producenti[ico] = dict(ico=ico, nazov=nazov, ulica=('' if ulica == 'NA' else ulica),
                               psc=('' if psc == 'NA' else psc.replace(' ', '')),
                               obec=('' if obec == 'NA' else obec),
                               obec_kod=('' if obec_kod == 'NA' else obec_kod),
                               typy=[kw], subor=os.path.basename(f))
    zdrojove_dopyty.append((os.path.basename(f), kw, dopyt))

# ---------- 3. geokódovanie ----------
prefix_okres = {}
for pr in producenti.values():
    g, acc = geocode(pr['obec'])
    pr['_g'], pr['_acc'] = g, acc
    if g and pr['obec_kod'][:6]:
        prefix_okres.setdefault(pr['obec_kod'][:6], {}).setdefault(g['okres'], 0)
        prefix_okres[pr['obec_kod'][:6]][g['okres']] += 1
PREF = {k: max(v.items(), key=lambda x: x[1])[0] for k, v in prefix_okres.items()}

rows = []
for pr in sorted(producenti.values(), key=lambda x: x['ico']):
    g, acc = pr['_g'], pr['_acc']
    okres = g['okres'] if g else PREF.get(pr['obec_kod'][:6], '')
    kraj = g['kraj'] if g else ''
    lat = g['lat'] if g else ''
    lon = g['lon'] if g else ''
    if not g and okres in OKRES_CENTROID:
        lon, lat = OKRES_CENTROID[okres]
        lon, lat = round(lon, 6), round(lat, 6)
        acc = 'okres'
        for gg in gaz:
            if gg['okres'] == okres: kraj = gg['kraj']; break
    rows.append(dict(
        ico=pr['ico'], nazov=pr['nazov'], ulica=pr['ulica'], psc=pr['psc'], obec=pr['obec'],
        obec_kod=pr['obec_kod'], okres=okres, kraj=kraj,
        lat=lat, lon=lon,
        presnost_polohy=(acc or 'nezistena'),
        typ_prevadzky=pr['typy'][0], typ_nazov=TYP_NAZOV.get(pr['typy'][0], pr['typy'][0]),
        sektor=SEKTOR.get(pr['typy'][0], ''), zdroj='RPO'))

print('producentov:', len(rows), '| s polohou:', sum(1 for r in rows if r['lat']),
      '| vynechaných (likvidácia/konkurz):', len(vynechane))

# ---------- 4. SQLite ----------
os.makedirs(P('data/csv'), exist_ok=True)
db = P('data/kpb2_mapa.sqlite')
if os.path.exists(db): os.remove(db)
con = sqlite3.connect(db); cur = con.cursor()
cur.executescript("""
PRAGMA foreign_keys=ON;
CREATE TABLE zdroj_geo (
  id INTEGER PRIMARY KEY, nazov TEXT NOT NULL, url TEXT, licencia TEXT,
  datum_ziskania TEXT, overenie TEXT);
CREATE TABLE druh_odpadu (
  id INTEGER PRIMARY KEY, kod TEXT UNIQUE NOT NULL, nazov_sk TEXT NOT NULL, nazov_en TEXT,
  katalogove_cislo_navrh TEXT, katalog_overeny INTEGER NOT NULL DEFAULT 0,
  skupina TEXT, pravny_status TEXT CHECK (pravny_status IN
    ('odpad','vedlajsi_produkt','krmna_surovina','potravinova_surovina')),
  sezonnost TEXT, drahy TEXT, poznamka TEXT);
CREATE TABLE obec (
  id INTEGER PRIMARY KEY, nazov TEXT NOT NULL, okres TEXT, kraj TEXT,
  lat REAL, lon REAL, typ TEXT, UNIQUE (nazov, okres));
CREATE TABLE producent (
  id INTEGER PRIMARY KEY, ico TEXT UNIQUE NOT NULL, nazov TEXT NOT NULL,
  ulica TEXT, psc TEXT, obec_id INTEGER REFERENCES obec(id),
  obec_nazov TEXT, obec_kod TEXT, okres TEXT, kraj TEXT, lat REAL, lon REAL,
  presnost_polohy TEXT NOT NULL CHECK (presnost_polohy IN
    ('obec','mestska_cast','obec_zaklad','okres','nezistena')),
  typ_prevadzky TEXT NOT NULL, typ_nazov TEXT, sektor TEXT,
  zdroj_id INTEGER NOT NULL REFERENCES zdroj_geo(id));
CREATE TABLE tok_odpadu (
  id INTEGER PRIMARY KEY, producent_id INTEGER NOT NULL REFERENCES producent(id),
  druh_odpadu_id INTEGER NOT NULL REFERENCES druh_odpadu(id),
  uroven_dokazu TEXT NOT NULL, poznamka TEXT,
  UNIQUE (producent_id, druh_odpadu_id));
CREATE TABLE kapacita (
  id INTEGER PRIMARY KEY,
  producent_id INTEGER NOT NULL UNIQUE REFERENCES producent(id),
  hodnota REAL NOT NULL, jednotka TEXT NOT NULL,
  uroven TEXT NOT NULL CHECK (uroven IN ('merana','typova','neznama')),
  zdroj TEXT, poznamka TEXT);
CREATE TABLE koeficient_produkcie (
  id INTEGER PRIMARY KEY, typ_prevadzky TEXT NOT NULL,
  druh_odpadu_id INTEGER NOT NULL REFERENCES druh_odpadu(id),
  koef_min REAL NOT NULL, koef_stred REAL NOT NULL, koef_max REAL NOT NULL,
  koef_jednotka TEXT NOT NULL, jedal_za_den REAL NOT NULL,
  podiel_stravnikov REAL NOT NULL, dni_rok INTEGER NOT NULL,
  zdroj TEXT NOT NULL, doi TEXT, uroven_dokazu TEXT NOT NULL, poznamka TEXT,
  UNIQUE (typ_prevadzky, druh_odpadu_id));
CREATE TABLE odhad_produkcie (
  id INTEGER PRIMARY KEY,
  producent_id INTEGER NOT NULL REFERENCES producent(id),
  druh_odpadu_id INTEGER NOT NULL REFERENCES druh_odpadu(id),
  t_rok_min REAL NOT NULL, t_rok_stred REAL NOT NULL, t_rok_max REAL NOT NULL,
  metoda TEXT NOT NULL, uroven_dokazu TEXT NOT NULL,
  UNIQUE (producent_id, druh_odpadu_id));
CREATE INDEX idx_odhad_prod ON odhad_produkcie(producent_id);
CREATE TABLE sektorovy_odhad (
  id INTEGER PRIMARY KEY, sektor TEXT NOT NULL, koef REAL NOT NULL, jednotka TEXT NOT NULL,
  populacia INTEGER NOT NULL, t_rok REAL NOT NULL, zdroj TEXT NOT NULL, poznamka TEXT);
CREATE TABLE draha (
  id INTEGER PRIMARY KEY, kod TEXT UNIQUE NOT NULL, nazov TEXT NOT NULL,
  popis TEXT, pravny_ramec TEXT);
CREATE TABLE odpad_draha (
  id INTEGER PRIMARY KEY,
  druh_odpadu_id INTEGER NOT NULL REFERENCES druh_odpadu(id),
  draha_id INTEGER NOT NULL REFERENCES draha(id),
  pripustnost TEXT NOT NULL CHECK (pripustnost IN
    ('povolene','podmienene','zakazane','mimo_regulacie')),
  regulacna_trieda TEXT NOT NULL, poznamka TEXT, uroven_dokazu TEXT NOT NULL,
  UNIQUE (druh_odpadu_id, draha_id));
CREATE INDEX idx_od_odpad ON odpad_draha(druh_odpadu_id);
CREATE INDEX idx_od_draha ON odpad_draha(draha_id);
CREATE INDEX idx_tok_prod ON tok_odpadu(producent_id);
CREATE INDEX idx_tok_odpad ON tok_odpadu(druh_odpadu_id);
CREATE INDEX idx_prod_okres ON producent(okres);
CREATE VIEW v_producent_odpad AS
  SELECT p.ico, p.nazov, p.obec_nazov AS obec, p.okres, p.kraj, p.lat, p.lon, p.sektor,
         p.typ_nazov, d.kod AS odpad_kod, d.nazov_sk AS odpad, d.katalogove_cislo_navrh,
         d.pravny_status, d.sezonnost, t.uroven_dokazu
  FROM producent p JOIN tok_odpadu t ON t.producent_id=p.id
  JOIN druh_odpadu d ON d.id=t.druh_odpadu_id;
CREATE VIEW v_okres_sumar AS
  SELECT okres, kraj, COUNT(*) AS producentov,
         COUNT(DISTINCT typ_prevadzky) AS typov_prevadzok
  FROM producent WHERE okres<>'' GROUP BY okres, kraj;
CREATE VIEW v_producent_objem AS
  SELECT p.ico, p.nazov, p.obec_nazov AS obec, p.okres, p.kraj, p.sektor, p.typ_nazov,
         k.hodnota AS kapacita, k.jednotka AS kapacita_jednotka, k.uroven AS kapacita_uroven,
         d.nazov_sk AS odpad, d.katalogove_cislo_navrh,
         o.t_rok_min, o.t_rok_stred, o.t_rok_max
  FROM producent p JOIN odhad_produkcie o ON o.producent_id=p.id
  JOIN druh_odpadu d ON d.id=o.druh_odpadu_id
  LEFT JOIN kapacita k ON k.producent_id=p.id;
CREATE VIEW v_okres_objem AS
  SELECT p.okres, p.kraj, COUNT(DISTINCT p.id) AS prevadzok,
         ROUND(SUM(o.t_rok_min),1) AS t_rok_min,
         ROUND(SUM(o.t_rok_stred),1) AS t_rok_stred,
         ROUND(SUM(o.t_rok_max),1) AS t_rok_max
  FROM producent p JOIN odhad_produkcie o ON o.producent_id=p.id
  WHERE p.okres<>'' GROUP BY p.okres, p.kraj;
CREATE VIEW v_draha_pokrytie AS
  SELECT dr.kod AS draha, dr.nazov,
    SUM(CASE WHEN od.pripustnost='povolene' THEN 1 ELSE 0 END) AS druhov_povolenych,
    SUM(CASE WHEN od.pripustnost='podmienene' THEN 1 ELSE 0 END) AS druhov_podmienene,
    SUM(CASE WHEN od.pripustnost='zakazane' THEN 1 ELSE 0 END) AS druhov_zakazanych
  FROM draha dr JOIN odpad_draha od ON od.draha_id=dr.id GROUP BY dr.id;
CREATE VIEW v_producent_draha AS
  SELECT p.ico, p.nazov, p.okres, p.sektor, dr.kod AS draha, od.pripustnost,
         COUNT(DISTINCT d.id) AS druhov
  FROM producent p JOIN tok_odpadu t ON t.producent_id=p.id
  JOIN druh_odpadu d ON d.id=t.druh_odpadu_id
  JOIN odpad_draha od ON od.druh_odpadu_id=d.id
  JOIN draha dr ON dr.id=od.draha_id
  GROUP BY p.id, dr.id, od.pripustnost;
CREATE VIEW v_odpad_pokrytie AS
  SELECT d.kod, d.nazov_sk, d.katalogove_cislo_navrh,
         (SELECT COUNT(*) FROM tok_odpadu t WHERE t.druh_odpadu_id=d.id) AS producentov
  FROM druh_odpadu d ORDER BY producentov DESC;
""")
cur.executemany("INSERT INTO zdroj_geo (id,nazov,url,licencia,datum_ziskania,overenie) VALUES (?,?,?,?,?,?)", [
 (1,'Register právnických osôb, podnikateľov a orgánov verejnej moci (ŠÚ SR)',
  'https://api.statistics.sk/rpo/v1/search','CC BY 4.0','2026-08-22',
  'Dopyty fullName na verejné API RPO. Každé IČO overené kontrolnou číslicou (modulo 11); '
  'vzorka záznamov znovu overená priamym dopytom identifier=. Prvý pokus o extrakciu zoznamu píl '
  'vrátil skrátené, nepravé IČO - celá dávka bola zahodená a načítaná znovu.'),
 (2,'Gazetteer obcí a hranice okresov a krajov (drakh/slovakia-gps-data; ZBGIS SMD + OSM)',
  'https://github.com/drakh/slovakia-gps-data','open data','2026-08-22',
  'GeoJSON EPSG:4326; 3226 sídelných bodov, 79 okresov, 8 krajov. Kontrola bounding boxu SR.'),
 (3,'Vyhláška MŽP SR č. 365/2015 Z. z. - Katalóg odpadov',
  'https://www.slov-lex.sk/ezbierky/pravne-predpisy/SK/ZZ/2015/365/','právny predpis','2026-08-22',
  'Katalógové čísla priradené podľa charakteru materiálu. NEOVERENÉ odborne spôsobilou osobou - '
  'katalog_overeny = 0 pri všetkých záznamoch.')])
cur.executemany("""INSERT INTO druh_odpadu
  (kod,nazov_sk,nazov_en,katalogove_cislo_navrh,katalog_overeny,skupina,pravny_status,sezonnost,drahy,poznamka)
  VALUES (?,?,?,?,0,?,?,?,?,?)""",
  [(o[0],o[1],o[2],o[3],o[4],o[5],o[6],o[7],o[8]) for o in ODPADY])

obec_id = {}
for r in rows:
    if not r['lat']: continue
    k = (r['obec'], r['okres'])
    if k not in obec_id:
        g,_ = geocode(r['obec'])
        if g is None: g = {'typ':'okres_centroid'}
        cur.execute("INSERT OR IGNORE INTO obec (nazov,okres,kraj,lat,lon,typ) VALUES (?,?,?,?,?,?)",
                    (r['obec'], r['okres'], r['kraj'], float(r['lat']), float(r['lon']),
                     g['typ'] if g else ''))
        cur.execute("SELECT id FROM obec WHERE nazov=? AND okres=?", (r['obec'], r['okres']))
        obec_id[k] = cur.fetchone()[0]

for r in rows:
    cur.execute("""INSERT INTO producent
      (ico,nazov,ulica,psc,obec_id,obec_nazov,obec_kod,okres,kraj,lat,lon,presnost_polohy,
       typ_prevadzky,typ_nazov,sektor,zdroj_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)""",
      (r['ico'],r['nazov'],r['ulica'],r['psc'],obec_id.get((r['obec'],r['okres'])),
       r['obec'],r['obec_kod'],r['okres'],r['kraj'],
       float(r['lat']) if r['lat'] else None, float(r['lon']) if r['lon'] else None,
       r['presnost_polohy'],r['typ_prevadzky'],r['typ_nazov'],r['sektor']))

cur.executemany("INSERT INTO draha (kod,nazov,popis,pravny_ramec) VALUES (?,?,?,?)", DRAHY)
cur.execute("SELECT id,kod FROM draha"); drmap = {k: i for i, k in cur.fetchall()}
cur.execute("SELECT id,kod FROM druh_odpadu"); dmap = {k: i for i, k in cur.fetchall()}
for kod, did in dmap.items():
    tr = TRIEDA[kod]; reg = REGULACIA[tr]
    for dkod, drid in drmap.items():
        cur.execute("""INSERT INTO odpad_draha
          (druh_odpadu_id,draha_id,pripustnost,regulacna_trieda,poznamka,uroven_dokazu)
          VALUES (?,?,?,?,?,?)""", (did, drid, reg[dkod], tr, reg['pozn'], 'D'))
cur.execute("SELECT id,typ_prevadzky FROM producent")
for pid, typ in cur.fetchall():
    for kod in PRODUCENT_ODPAD.get(typ, []):
        cur.execute("""INSERT OR IGNORE INTO tok_odpadu
          (producent_id,druh_odpadu_id,uroven_dokazu,poznamka) VALUES (?,?,?,?)""",
          (pid, dmap[kod], 'D',
           'Odvodené z typu prevádzky, nie z ohlásenia o vzniku odpadu. Overiť podľa evidencie prevádzkovateľa.'))

# ---------- 4b. kapacity a odhady objemu ----------
cur.executemany("""INSERT INTO sektorovy_odhad (sektor,koef,jednotka,populacia,t_rok,zdroj,poznamka)
  VALUES (?,?,?,?,?,?,?)""",
  [(a,b,c,d,round(b*d/1000.0,0),e,f) for (a,b,c,d,e,f) in SEKTOROVY_ODHAD])

# reálne kapacity, ak ich niekto doplnil: build/kapacita_merana.csv  (ico;hodnota;jednotka;zdroj)
MERANE = {}
_mp = P('build/kapacita_merana.csv')
if os.path.exists(_mp):
    for r in csv.DictReader(open(_mp, encoding='utf-8-sig'), delimiter=';'):
        if (r.get('hodnota') or '').strip():
            MERANE[r['ico'].strip()] = (float(r['hodnota'].replace(',', '.')),
                                        (r.get('jednotka') or '').strip(),
                                        (r.get('zdroj') or 'doplnené ručne').strip())
    print('meraných kapacít načítaných:', len(MERANE))

cur.execute("SELECT id,ico,typ_prevadzky FROM producent")
prod_typ = [(a, c) for a, b, c in cur.fetchall()]
cur.execute("SELECT id,ico,typ_prevadzky FROM producent")
for pid, ico, typ in cur.fetchall():
    if ico in MERANE:
        hod, jed, zdr = MERANE[ico]
        if not jed and typ in TYPOVA_KAPACITA: jed = TYPOVA_KAPACITA[typ][1]
        cur.execute("""INSERT INTO kapacita (producent_id,hodnota,jednotka,uroven,zdroj,poznamka)
          VALUES (?,?,?,'merana',?,?)""", (pid, hod, jed or 'jednotka neuvedená', zdr,
          'Skutočná kapacita prevádzky, nie národný priemer.'))
    elif typ in TYPOVA_KAPACITA:
        hod, jed, zdr, pozn = TYPOVA_KAPACITA[typ]
        cur.execute("""INSERT INTO kapacita (producent_id,hodnota,jednotka,uroven,zdroj,poznamka)
          VALUES (?,?,?,?,?,?)""", (pid, hod, jed, 'typova', zdr, pozn))

for (typ, okod, mn, st, mx, jd, ps, dni, zdroj, doi, ur, pozn) in KOEFICIENTY:
    cur.execute("""INSERT INTO koeficient_produkcie
      (typ_prevadzky,druh_odpadu_id,koef_min,koef_stred,koef_max,koef_jednotka,
       jedal_za_den,podiel_stravnikov,dni_rok,zdroj,doi,uroven_dokazu,poznamka)
      VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
      (typ, dmap[okod], mn, st, mx, 'g na jedlo alebo lôžkodeň', jd, ps, dni, zdroj, doi, ur, pozn))

cur.execute("""SELECT p.id,p.typ_prevadzky,k.hodnota FROM producent p
               JOIN kapacita k ON k.producent_id=p.id WHERE k.uroven<>'neznama'""")
for pid, typ, kap in cur.fetchall():
    cur.execute("""SELECT druh_odpadu_id,koef_min,koef_stred,koef_max,jedal_za_den,
                          podiel_stravnikov,dni_rok,uroven_dokazu
                   FROM koeficient_produkcie WHERE typ_prevadzky=?""", (typ,))
    for (did, mn, st, mx, jd, ps, dni, ur) in cur.fetchall():
        f = kap * ps * jd * dni / 1e6
        cur.execute("""INSERT INTO odhad_produkcie
          (producent_id,druh_odpadu_id,t_rok_min,t_rok_stred,t_rok_max,metoda,uroven_dokazu)
          VALUES (?,?,?,?,?,?,?)""",
          (pid, did, round(mn*f,3), round(st*f,3), round(mx*f,3),
           'kapacita × podiel stravníkov × jedál za deň × koeficient × dní v roku',
           ur if True else ur))
con.commit()

# ---------- 5. exporty ----------
for t in ['druh_odpadu','producent','obec','zdroj_geo','tok_odpadu','draha','odpad_draha',
          'kapacita','koeficient_produkcie','odhad_produkcie','sektorovy_odhad',
          'v_producent_odpad','v_okres_sumar','v_odpad_pokrytie','v_draha_pokrytie',
          'v_producent_objem','v_okres_objem']:
    cur.execute(f"SELECT * FROM {t}")
    cols = [d[0] for d in cur.description]
    with open(P('data/csv', t + '.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(cols); w.writerows(cur.fetchall())

# šablóna na doplnenie reálnych kapacít
with open(P('data/csv/kapacita_sablona.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, delimiter=';')
    w.writerow(['ico','nazov','obec','okres','typ_prevadzky','jednotka','hodnota','zdroj'])
    for r in con.execute("""SELECT p.ico,p.nazov,p.obec_nazov,p.okres,p.typ_prevadzky,k.jednotka
                            FROM producent p JOIN kapacita k ON k.producent_id=p.id
                            WHERE k.uroven='typova' ORDER BY p.typ_prevadzky,p.nazov"""):
        w.writerow(list(r) + ['', ''])

cur.execute("""SELECT p.id,p.ico,p.nazov,p.obec_nazov,p.okres,p.kraj,p.lat,p.lon,p.typ_prevadzky,
                      p.typ_nazov,p.sektor,p.presnost_polohy FROM producent p WHERE p.lat IS NOT NULL""")
feats = []
for (pid,ico,nazov,obec,okres,kraj,lat,lon,typ,typn,sekt,acc) in cur.fetchall():
    cur2 = con.execute("""SELECT d.kod,d.nazov_sk,d.katalogove_cislo_navrh FROM tok_odpadu t
                          JOIN druh_odpadu d ON d.id=t.druh_odpadu_id WHERE t.producent_id=?""", (pid,))
    od = cur2.fetchall()
    feats.append({"type":"Feature","geometry":{"type":"Point","coordinates":[lon,lat]},
      "properties":{"ico":ico,"nazov":nazov,"obec":obec,"okres":okres,"kraj":kraj,
        "typ":typ,"typ_nazov":typn,"sektor":sekt,"presnost":acc,
        "t_rok":round((con.execute("SELECT COALESCE(SUM(t_rok_stred),0) FROM odhad_produkcie WHERE producent_id=?",(pid,)).fetchone()[0]),2),
        "odpady":[{"kod":a,"nazov":b,"kat":c} for a,b,c in od]}})
json.dump({"type":"FeatureCollection","features":feats}, open(P('data/producenti.geojson'),'w',encoding='utf-8'),
          ensure_ascii=False)
print('geojson bodov:', len(feats))
con.close()
