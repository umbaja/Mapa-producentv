# Databáza odpadovej biomasy KPB2

Tri verejné nástroje projektu, každý na samostatnej stránke:

| Stránka | Čo obsahuje |
|---|---|
| [`index.html`](index.html) — **Kalkulátor a databáza** | 69 substrátov s nutričnou kompozíciou, kalkulátor substrátových zmesí pre výkrm hmyzu s právnym filtrom podľa nar. (ES) 1069/2009, druhy hmyzu, bioakumulácia ťažkých kovov, zdroje |
| [`mapa.html`](mapa.html) — **Mapa producentov** | 1 043 producentov odpadovej biomasy v SR, 92 druhov odpadu s katalógovými číslami, 9 dráh zhodnotenia, odhad objemu pri 288 prevádzkach |
| [`kalkulacka.html`](kalkulacka.html) — **Energetika a uhlíková stopa** | Bilančný model prevádzky chovu hmyzu — spotreba energie, prevádzkové náklady a emisie na kg produktu, jedenásť scenárov, porovnanie s inými bielkovinami |

Obe stránky sú statické, bez servera, bez knižníc tretích strán a bez externých požiadaviek —
fungujú na GitHub Pages, na akomkoľvek hostingu aj po otvorení zo súboru.

## Nasadenie na GitHub Pages

```bash
git remote add origin git@github.com:<konto>/<repozitar>.git
git push -u origin main
```

Potom **Settings → Pages → Source: Deploy from a branch → main / (root)**. Stránky budú na
`https://<konto>.github.io/<repozitar>/` a `.../mapa.html`. Súbor `.nojekyll` je v repozitári
preto, aby Jekyll nepreskakoval priečinky — bez neho sa časť súborov nenasadí.

## Štruktúra

```
index.html              kalkulátor a databáza
mapa.html               mapa producentov
assets/
  site.css              spoločná horná lišta oboch stránok
  app.css  app.js       kalkulátor a prehliadanie databázy
  lp.js                 dvojfázový simplexový riešič, bez závislostí
  data.js               dataset substrátov (generované z kpb2_dataset.sqlite)
  mapa.css  mapa.js     mapa: SVG projekcia, filtre, export
  mapa_data.js          producenti, druhy odpadu, dráhy, hranice okresov (generované)
  kalk.css  kalk.js      kalkulačka energetickej náročnosti a uhlíkovej stopy
data/
  kpb2_mapa.sqlite      relačná databáza geografickej vrstvy
  producenti.geojson    bodová vrstva pre QGIS
  csv/                  exporty všetkých tabuliek a pohľadov
  csv/kapacita_sablona.csv   šablóna na doplnenie skutočných kapacít prevádzok
build/
  data_odpady.py        číselník 92 druhov odpadu, dráhy zhodnotenia, regulačné triedy
  data_kapacita.py      typové kapacity a koeficienty produkcie s DOI
  build_mapa.py         zostaví databázu od nuly
  export_mapa.py        vygeneruje assets/mapa_data.js
  qc_mapa.py            17 kontrol kvality
  model_d32.py          bilančný model energetiky chovu (výstup D3.2)
  ico_check.py          kontrolná číslica IČO nad surovými výpismi
  rpo_raw/              surové výpisy z RPO vrátane použitého dopytu (provenancia)
```

Prestavba mapovej vrstvy:

```bash
python3 build/make_gazetteer.py   # potrebuje geo/src (viď MAPA-README.md)
python3 build/build_mapa.py
python3 build/qc_mapa.py
python3 build/export_mapa.py
```

## Čo dáta tvrdia a čo netvrdia

- **Producenti** sú reálne zapísané subjekty z Registra právnických osôb ŠÚ SR (CC BY 4.0).
  Každé IČO prešlo kontrolou modulo 11, každý bod leží v okrese, ktorý má zapísaný.
- **Poloha** je ťažisko obce podľa adresy v registri, nie GPS brány prevádzky.
- **Toky odpadu** sú odvodené z typu prevádzky (úroveň dôkazu D), nie z ohlásenia o vzniku odpadu.
- **Katalógové čísla** sú návrh, `katalog_overeny = 0` pri všetkých druhoch.
- **Prípustnosť dráh** je právny výklad riešiteľského tímu, nie rozhodnutie ŠVPS SR.
- **Odhad objemu** stojí na typových kapacitách — jednotlivý bod je rádový, súčet za okres
  je spoľahlivejší. Postup nahradenia skutočnými počtami je v `MAPA-README.md`.

### Dokumentácia výstupov

| Výstup | Dokument |
|---|---|
| D2.1 — mapa producentov | [`docs/APETBIO_D2-1_Mapa_producentov.pdf`](docs/APETBIO_D2-1_Mapa_producentov.pdf) |
| D2.2 — kalkulátor kŕmnych dávok | [`docs/APETBIO_D2-2_Kalkulator_krmnych_davok.pdf`](docs/APETBIO_D2-2_Kalkulator_krmnych_davok.pdf) |
| D3.2 — energetika a uhlíková stopa | [`docs/APETBIO_D3-2_Energetika_uhlikova_stopa.pdf`](docs/APETBIO_D3-2_Energetika_uhlikova_stopa.pdf) |

Zdroje správ sú v `docs/sprava_d21/`, `docs/sprava_d22/` a `docs/sprava_d32/`; každý sa
prestaví vlastným `build.py`.

Podrobná metodika mapovej vrstvy: [`MAPA-README.md`](MAPA-README.md).

## Licencie

Dáta **CC BY 4.0**, kód **MIT**. Pri citovaní uvádzajte zdrojový register:
*Údaje z Registra právnických osôb, podnikateľov a orgánov verejnej moci, © Štatistický úrad SR, CC BY 4.0.*
