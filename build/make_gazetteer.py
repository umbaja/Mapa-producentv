import json, csv, unicodedata, re
SRC="geo/src/GeoJSON/epsg_4326/"
def norm(s):
    if not s: return ""
    s=unicodedata.normalize('NFKD',s)
    s=''.join(c for c in s if not unicodedata.combining(c))
    s=re.sub(r'[^a-zA-Z0-9]+',' ',s).strip().lower()
    return s
cities=json.load(open(SRC+"cities_regions_districts_epsg_4326.geojson"))["features"]
rows=[]
for f in cities:
    if not f["properties"].get("name"): continue
    p=f["properties"]; c=f["geometry"]["coordinates"]
    rows.append(dict(osm_id=p["osm_id"], nazov=p["name"] or "", nazov_norm=norm(p["name"]),
                     okres=p["district"], kraj=p["region"], typ=p["type"],
                     lon=round(c[0],6), lat=round(c[1],6)))
with open("data/csv/gazetteer_obce.csv","w",newline="",encoding="utf-8") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("obce:",len(rows))
print("okresy:",len({r['okres'] for r in rows}),"kraje:",len({r['kraj'] for r in rows}))
print("typy:",{r['typ'] for r in rows})
# ambiguity check
from collections import Counter
c=Counter(r['nazov_norm'] for r in rows)
amb=[k for k,v in c.items() if v>1]
print("nejednoznacne nazvy:",len(amb), amb[:10])
lats=[r['lat'] for r in rows]; lons=[r['lon'] for r in rows]
print("bbox lat %.3f-%.3f lon %.3f-%.3f"%(min(lats),max(lats),min(lons),max(lons)))
