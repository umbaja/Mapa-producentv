# KPB2 — pokyny pre prácu na tomto repozitári

Dva verejné výstupy projektu, obe statické stránky bez servera a bez knižníc tretích strán:

- `index.html` — databáza 69 substrátov a kalkulátor substrátových zmesí pre výkrm hmyzu (D2.2)
- `mapa.html` — 1 043 producentov odpadovej biomasy v SR, 92 druhov odpadu, 9 dráh zhodnotenia (D2.1)
- `kalkulacka.html` — energetická náročnosť a uhlíková stopa chovu (D3.2)

Cieľom je merateľný ukazovateľ **KPB2 — funkčná online databáza uverejnená na stránke projektu**.
Nie je to bežná webová aplikácia: obsah sa vykazuje kontrolórovi a musí obstáť pri oponentúre.

## Príkazy

```bash
python3 build/build_mapa.py     # zostaví data/kpb2_mapa.sqlite od nuly
python3 build/qc_mapa.py        # 17 kontrol kvality — MUSÍ prejsť pred commitom
python3 build/export_mapa.py    # vygeneruje assets/mapa_data.js z databázy
python3 build/ico_check.py      # kontrolná číslica IČO nad surovými výpismi
python3 -m http.server 8000     # lokálny náhľad na http://localhost:8000
```

Po akejkoľvek zmene dát treba spustiť `build_mapa.py`, `qc_mapa.py` a `export_mapa.py` v tomto
poradí. Samotná zmena SQLite alebo `mapa_data.js` sa pri ďalšom builde stratí.

## Čo sa needituje ručne

Tieto súbory sú generované a akákoľvek ručná zmena v nich zmizne:

- `assets/mapa_data.js` — generuje `build/export_mapa.py`
- `assets/data.js` — generuje sa z `kpb2_dataset.sqlite` (mimo tohto repozitára)
- `data/kpb2_mapa.sqlite`, `data/csv/*`, `data/producenti.geojson` — generuje `build/build_mapa.py`

Zmeny sa robia v zdrojoch: `build/data_odpady.py` (číselník odpadov, dráhy, regulačné triedy),
`build/data_kapacita.py` (kapacity a koeficienty), `build/rpo_raw/*.txt` (surové výpisy z registra).

## Pravidlá práce s dátami — toto je najdôležitejšia časť

Projekt už raz zachytil, že automatické načítanie zdroja vráti **presvedčivo vyzerajúcu, ale
vymyslenú tabuľku**. Stalo sa to dvakrát: pri extrakcii z dvoch prác (celá dávka zahodená)
a pri výpise píl z RPO, kde sa vrátili skrátené nepravé IČO. Preto platí:

1. **Žiadna hodnota bez zdroja.** Každý údaj má `zdroj_id` alebo pole so zdrojom a DOI.
   Riadok bez zdroja sa do databázy nesmie dostať.
2. **Dvojité načítanie.** Každý zdroj sa načíta najmenej dvakrát s **odlišne formulovanou
   otázkou**. Ak sa načítania nezhodnú, hodnota sa **nezapisuje** — nezapíše sa ani jedna
   z nich a do poznámky zdroja sa uvedie, že sa nezhodli. Príklad, ktorý už v dátach je:
   počet nemocničných postelí za rok 2020 (31 422 vs. 31 659) — použil sa rok 2019, na ktorom
   sa obe načítania zhodujú.
3. **Nevymýšľať chýbajúce hodnoty.** Prázdne miesto je legitímny a cenný výsledok; označuje,
   kam smerovať vlastné analýzy. Pohľad `v_odpad_pokrytie` diery zámerne zobrazuje.
4. **Úroveň dôkazu pri každom odvodenom údaji:** A = vlastná akreditovaná analýza,
   B = recenzovaná publikácia s uvedenou metódou, C = publikácia bez metódy alebo prenesený
   koeficient, D = návrh riešiteľského tímu. Úroveň sa uvádza, nie zamlčuje.
5. **`katalog_overeny = 0` pri všetkých druhoch odpadu.** Katalógové čísla sú návrh podľa
   charakteru materiálu. Prepnúť ich smie až odborne spôsobilá osoba, nie skript ani agent.
6. **Nekopírovať chránené databázy.** Feedipedia a podobné zdroje sú chránené právom sui
   generis (smernica 96/9/ES). Používajú sa len ako porovnávacia referencia s citáciou.
   Namerané hodnoty z publikácií sú fakty a citovať sa smú — s DOI.

### Kontroly, ktoré musia prejsť

`build/qc_mapa.py` spúšťa 17 kontrol. Commit sa nerobí, kým niektorá zlyhá. Najdôležitejšie:

- **Kontrolná číslica IČO (modulo 11)** — vymyslené osemmiestne číslo ňou prejde
  s pravdepodobnosťou asi 1 : 11, takže dávka vymyslených záznamov neprejde nikdy.
- **Bod leží v priradenom okrese** — okres pochádza z gazetteera, hranice z iného súboru,
  takže zhoda nie je automatická.
- **ŽVP kategórie 1 zakázané vo všetkých dráhach.**
- **Kuchynský odpad: krmivo zakázané, technický tuk povolený** — toto je vecné jadro
  vrstvy dráh a kontrola stráži, aby sa nestratilo pri úprave regulačných tried.

Pri pridávaní producentov z RPO: výpis sa ukladá do `build/rpo_raw/` **aj s použitým dopytom**
v hlavičke súboru — to je doklad o pôvode. Pri školách treba dopyt obmedziť parametrom
`legalForm=Rozpočtová organizácia`, inak register vracia prevažne základné organizácie
odborového zväzu so sídlom na adrese školy, nie školy samotné.

## Čo výstupy netvrdia

Pri úprave textov na stránkach tieto výhrady neodstraňovať ani nezmäkčovať:

- Poloha je ťažisko obce podľa adresy v registri, nie GPS brána prevádzky.
- Toky odpadu sú odvodené z typu prevádzky (úroveň D), nie z ohlásenia o vzniku odpadu.
- Prípustnosť dráh je právny výklad riešiteľského tímu, nie rozhodnutie ŠVPS SR.
- Odhad objemu stojí na typových kapacitách — jednotlivý bod je rádový, súčet za okres
  je spoľahlivejší.

## Dvojitá implementácia energetického modelu

Model výstupu D3.2 je napísaný **dvakrát nezávisle** — v Pythone (`build/model_d32.py`) pre
štúdiu a v JavaScripte (`assets/kalk.js`) pre verejnú kalkulačku. Zhoda oboch implementácií je
kontrolou proti chybe v prepise vzorcov. **Pri akejkoľvek zmene modelu treba upraviť obe**
a porovnať základný scenár aj všetkých jedenásť scenárov; musia dať rovnaké čísla
(základ: 14,58 kWh/kg, 2,68 €/kg, 1,473 kg CO₂e/kg).

## Štýl kódu

- **Žiadne závislosti.** Vlastný simplexový riešič (`assets/lp.js`), vlastná SVG projekcia
  mapy (`assets/mapa.js`). Nepridávať Leaflet, D3 ani npm balíky — stránky musia fungovať
  na GitHub Pages aj po otvorení zo súboru a bez internetu.
- Vanilla JS, bez build kroku pre front-end. Python 3 so štandardnou knižnicou pre dáta.
- Slovenčina vrátane diakritiky v UI aj v komentároch; kódy a názvy stĺpcov bez diakritiky.
- Svetlá aj tmavá téma cez CSS premenné na `:root`; farbu nikdy nedefinovať len v media bloku.

## Nasadenie

Push do vetvy `main` → GitHub Pages (Settings → Pages → Deploy from a branch → main / root).
Súbor `.nojekyll` musí zostať v repozitári, inak Jekyll preskočí priečinok `assets/`
a obe stránky sa načítajú bez štýlov a bez dát.

Podrobná metodika mapovej vrstvy vrátane zdrojov a koeficientov je v `MAPA-README.md`.
