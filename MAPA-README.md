# Mapa producentov biotransformovateľných odpadov v SR

Geografická vrstva databázy KPB2. Odpovedá na otázku **kde na Slovensku vzniká odpadová
biomasa**, ktorú databáza nutričnej kompozície popisuje **čo do zloženia**.

| Merateľná podmienka | Požadované | Dosiahnuté |
|---|---|---|
| Druhy odpadu | ≥ 50 | **92** |
| Identifikovaní producenti | ≥ 200 | **1 043** |
| Pokrytie územia | — | 78 zo 79 okresov, 478 obcí |
| Väzby producent → druh odpadu | — | 4 209 |
| Dráhy zhodnotenia | — | 9, s prípustnosťou pri každom druhu odpadu (828 kombinácií) |
| Odhad objemu | — | 288 prevádzok, 1 425 t/rok (rozpätie 1 099 – 1 839) |

## Kľúčové rozlíšenie: krmivo nie je jediná dráha

Vrstva zámerne neobmedzuje databázu na legislatívne schválené krmivové toky. Materiál, ktorý
je z krmivového reťazca vylúčený, býva **plne použiteľný pre technologické makronutrienty** —
hmyzí tuk do oleochémie a biopalív, chitín a chitozán z exúvií, proteínový hydrolyzát ako
biostimulátor, frass ako hnojivo podľa nar. (EÚ) 2021/1925.

Rozdiel je v dátach viditeľný okamžite:

| Dráha | Druhov odpadu povolených | Podmienene | Zakázaných | Producentov s povoleným tokom |
|---|---|---|---|---|
| Krmivo pre hospodárske zvieratá | 59 | 0 | 33 | 934 |
| Krmivo pre akvakultúru | 59 | 0 | 33 | 934 |
| Krmivo pre spoločenské zvieratá | 59 | 9 | 24 | 934 |
| Potravina pre ľudí | 40 | 19 | 33 | 698 |
| **Technický tuk a oleochémia** | **78** | 12 | 2 | **1 022** |
| **Chitín a chitozán** | **78** | 12 | 2 | **1 022** |
| **Proteínový hydrolyzát** | **78** | 7 | 7 | **1 022** |
| Frass ako organické hnojivo | 59 | 19 | 14 | 934 |
| Anaeróbna digescia | 90 | 0 | 2 | 1 022 |

Najvýraznejší je kuchynský a reštauračný odpad. Podľa čl. 11 nar. (ES) č. 1069/2009 je
zakázaným kŕmnym materiálom, takže hmyz na ňom odchovaný nesmie do krmív pre hospodárske
zvieratá. Technické dráhy tým dotknuté nie sú — a práve tento tok je v SR najväčší
a najmenej využitý: **v databáze ho produkuje 400 stravovacích a retailových prevádzok.**

Rovnako živočíšne vedľajšie produkty kategórie 3 z mäsospracovania: pre krmivá hospodárskych
zvierat vylúčené, pre technický tuk, chitín a hydrolyzát prípustné. Kategória 1 je vylúčená
zo všetkých dráh — to vrstva tvrdí tiež a kontrola to overuje.

---

## Čo je v balíku

```
mapa.html                     stránka mapy pre web projektu
mapa_standalone.html          tá istá mapa v jednom súbore (dá sa otvoriť priamo, funguje offline)
assets/mapa.css               vzhľad, svetlá aj tmavá téma
assets/mapa.js                mapa, filtre, export — bez knižníc, bez závislostí
assets/mapa_data.js           dáta pre web (generované, needitovať ručne)
data/kpb2_mapa.sqlite         relačná databáza geografickej vrstvy
data/csv/*.csv                exporty všetkých tabuliek a pohľadov
data/producenti.geojson       bodová vrstva pre QGIS a iné GIS nástroje
data/csv/gazetteer_obce.csv   3 226 sídelných bodov SR s okresom a krajom
build/data_odpady.py          číselník 76 druhov odpadu + väzba typ prevádzky → odpad
build/build_mapa.py           zostaví databázu od nuly
build/export_mapa.py          vygeneruje assets/mapa_data.js
build/qc_mapa.py              10 kontrol kvality
build/ico_check.py            kontrola kontrolnej číslice IČO nad surovými výpismi
build/rpo_raw/*.txt           surové výpisy z RPO vrátane použitého dopytu (provenancia)
build/make_gazetteer.py       zostaví gazetteer z hraníc a sídelných bodov
build/make_standalone.py      zlepí mapu do jedného súboru
```

Prestavba celej vrstvy:

```bash
python3 build/make_gazetteer.py
python3 build/build_mapa.py
python3 build/qc_mapa.py
python3 build/export_mapa.py
python3 build/make_standalone.py
```

## Zaradenie do webu projektu

Súbory `assets/mapa.*` skopírujte vedľa existujúcich `assets/`, `data/kpb2_mapa.sqlite`
a `data/csv/` vedľa existujúcich dát a do hlavnej navigácie `index.html` pridajte položku
**Mapa** smerujúcu na `mapa.html`. Mapa nepotrebuje server, dlaždice ani knižnicu tretej
strany — hranice okresov sú vykreslené z vlastných dát v SVG, takže stránka funguje aj po
otvorení zo súboru a aj bez internetu.

---

## Odhad objemu kuchynského odpadu

Objem sa nepočíta jedným koeficientom, ale **piatimi samostatne viditeľnými faktormi**:

```
t/rok = kapacita × podiel stravníkov × jedál za deň × koeficient (g) × dní v roku / 10⁶
```

Každý faktor má vlastný zdroj a vlastnú úroveň dôkazu, takže sa dá napadnúť a opraviť
ktorýkoľvek z nich zvlášť. Nič sa nezlučuje do jedného neauditovateľného čísla.

| Typ prevádzky | Typová kapacita | Podiel | Jedál/deň | Koeficient | Dní | Odhad na prevádzku |
|---|---|---|---|---|---|---|
| Materská škola | 56 detí | 95 % | 2,5 | 45–55–80 g | 210 | 1,54 t/rok |
| Základná škola | 226 žiakov | 75 % | 1 | 45–55–80 g | 190 | 1,77 t/rok |
| Stredná škola | 299 žiakov | 50 % | 1 | 45–55–80 g | 190 | 1,56 t/rok |
| Školská jedáleň | 226 stravníkov | 100 % | 1 | 45–55–80 g | 190 | 2,36 t/rok |
| Nemocnica | 349 lôžok | 65,9 % obložnosť | 1 | 240–320–390 g/lôžkodeň | 365 | 26,9 t/rok |

**Odkiaľ sú koeficienty**

| Zdroj | Hodnota | DOI |
|---|---|---|
| Malefors a kol. 2026, *Environmental Development* 57:101386 — 693 švédskych škôl | 45–47 g na stravníka (podávanie + tanier); odpad z taniera 18 g u mladších, 36 g u starších žiakov | [10.1016/j.envdev.2025.101386](https://doi.org/10.1016/j.envdev.2025.101386) |
| Zhang a kol. 2024, *Front. Sustain. Food Syst.* 8:1336220 — čínske stredné školy | 44,5 g na stravníka a jedlo; obed 55,3 g | [10.3389/fsufs.2024.1336220](https://doi.org/10.3389/fsufs.2024.1336220) |
| Abiad a kol. 2025, *Front. Sustain. Food Syst.* 9:1516331 — 16 nemocníc, 1 094 jedál | 390 g na lôžko a deň; 142,3 kg na lôžko a rok | [10.3389/fsufs.2025.1516331](https://doi.org/10.3389/fsufs.2025.1516331) |
| Burgoa Sánchez a de Camargo 2026, *Sustainability* 18(3):1458 — prehľad | 81 g na jedlo (Holandsko) ≈ 240 g na pacienta a deň | [10.3390/su18031458](https://doi.org/10.3390/su18031458) |

Dva nezávislé zdroje sa pri školskom stravovaní zhodujú na **45–55 g na porciu** — to je
strednú hodnotu. Horná hranica 80 g pokrýva kuchynský odpad z prípravy, ktorý švédska
metodika započítava len čiastočne. Pri nemocniciach dva zdroje ohraničujú **240–390 g na
lôžkodeň**.

**Odkiaľ sú kapacity**

Typové kapacity sú národný súčet delený počtom zariadení:

- CVTI SR, *Vývojové tendencie ukazovateľov MŠ, ZŠ a SŠ* (šk. rok 2021/22): 173 170 detí
  v 3 102 MŠ, 468 540 žiakov v 2 070 ZŠ, 194 246 žiakov v 649 stredných školách.
  **Zdroj načítaný dvakrát s odlišne formulovanou otázkou, obe načítania sa zhodujú.**
- Eurostat `hlth_rs_bds`: 31 422 postelí (2019). MF SR, *Revízia výdavkov na nemocnice*
  (marec 2025): 90 nemocníc, obložnosť akútnych lôžok 65,9 %.
  Obložnosť je nezávisle potvrdená výpočtom z NCZI: 988 691 hospitalizácií × 7,8 dňa
  / 31 422 postelí / 365 = 67 %.

Pri postelích sa dve načítania Eurostatu **nezhodli** v hodnote za rok 2020 (31 422 vs.
31 659). Podľa protokolu projektu sa nezhodná hodnota nezapisuje — použitý je rok 2019,
na ktorom sa obe načítania zhodujú.

**Národná extrapolácia a jej kontrola**

Typová kapacita × počet zariadení v SR dáva:

| | Zariadení v SR | t/rok |
|---|---|---|
| Materské školy | 3 102 | 4 765 |
| Základné školy | 2 070 | 3 666 |
| Stredné školy | 649 | 1 014 |
| Nemocnice | 90 | 2 418 |
| **Spolu** | | **≈ 11 900 t/rok** |

Kontrola proti nezávislému zdroju: Eurostat `env_wasfw` (2023) uvádza pre sektor reštaurácií
a stravovacích služieb priemer EÚ 14 kg na obyvateľa a rok, čo pre SR znamená ≈ 75 900 t/rok.
Školské a nemocničné stravovanie tvorí **16 %** z toho. Rádovo to sedí — inštitucionálne
stravovanie je podmnožinou celého sektora, nie jeho väčšinou.

**Kde sa objem zámerne nepočíta**

- **Reštaurácie, hotely, retail** — sú v databáze menovite, ale bez počtu miest a obratu.
  Namiesto falošnej presnosti na prevádzku je uvedený sektorový odhad pre SR
  (reštaurácie 75 900 t/rok, maloobchod 54 200 t/rok, spracovanie potravín 130 080 t/rok;
  Eurostat `env_wasfw` 2023, priemer EÚ × 5,42 mil. obyvateľov).
- **Zariadenia sociálnych služieb** — kapacitu sa nepodarilo získať z overiteľného zdroja
  (NKÚ aj MPSVR SR blokujú automatické načítanie). Prevádzky sú v databáze, objem nie.
- **Priemyselné toky** (mláto, srvátka, výlisky) — potrebovali by výrobné objemy jednotlivých
  závodov. Toto je najväčšia zostávajúca diera.

**Ako typovú kapacitu nahradiť skutočnou**

Toto je najdôležitejšie miesto celej vrstvy. Typová kapacita znamená, že **každá nemocnica
má v databáze 349 postelí a každá ZŠ 226 žiakov** — teda že jednotlivý bod je rádový odhad,
nie údaj o konkrétnej prevádzke. Súčet za okres je spoľahlivejší než jednotlivá hodnota.

Oprava je pripravená a stojí jeden súbor:

1. Otvorte `data/csv/kapacita_sablona.csv` (288 riadkov, stĺpce `ico;nazov;obec;okres;
   typ_prevadzky;jednotka;hodnota;zdroj`).
2. Vyplňte stĺpec `hodnota` skutočnými počtami. Zoznamy škôl s počtami žiakov publikuje
   CVTI SR v Exceli: [zoznamy škôl a školských zariadení](https://www.cvtisr.sk/cvti-sr-vedecka-kniznica/informacie-o-skolstve/registre/zoznamy-skol-a-skolskych-zariadeni.html?page_id=9332)
   (`ms_z.xls`, `zs_z.xls`, `GYM_Z.XLS`, `SOS_Z.XLS` — obsahujú adresu aj celkové počty žiakov).
3. Uložte ako `build/kapacita_merana.csv` a spustite `python3 build/build_mapa.py`.

Skript kapacitu prevezme, prepne `uroven` z `typova` na `merana` a prepočíta všetky odhady.
Kontrola kvality č. 17 vtedy zmení počet meraných kapacít z nuly na skutočný počet — takže
je z databázy okamžite vidieť, koľko odhadov už stojí na reálnych číslach.

## Dátový model

```
draha ──< odpad_draha >── druh_odpadu ──< tok_odpadu >── producent ──> obec
                                │                            │
                                │                            ├──> kapacita
                                └──< odhad_produkcie >───────┤
                                                             └──> zdroj_geo
koeficient_produkcie (typ prevádzky × druh odpadu)
```

Prípustnosť sa neukladá pri každom druhu ručne, ale odvodzuje sa z **regulačnej triedy**
materiálu (rastlinný, mlieko a vajcia, bývalá potravina bez ŽVP / so ŽVP, kuchynský odpad,
ŽVP kat. 1/2/3, hnoj, čistiarenský kal, lignocelulózny). Trieda je jedno pole, matica je
generovaná — takže zmena právneho výkladu sa zapíše na jednom mieste a prestaví sa celá
databáza.

| Tabuľka | Záznamov | Obsah |
|---|---|---|
| `producent` | 1 022 | IČO, názov, adresa, obec, okres, kraj, súradnice, presnosť polohy, typ prevádzky, sektor |
| `druh_odpadu` | 92 | kód, názov SK/EN, návrh katalógového čísla, právny status, sezónnosť, vhodné technologické dráhy |
| `tok_odpadu` | 4 127 | ktorý producent produkuje ktorý druh odpadu, s úrovňou dôkazu |
| `draha` | 9 | dráhy zhodnotenia s právnym rámcom |
| `odpad_draha` | 828 | prípustnosť každého druhu odpadu v každej dráhe + regulačná trieda |
| `kapacita` | 288 | kapacita prevádzky s jednotkou, úrovňou (meraná/typová) a zdrojom |
| `koeficient_produkcie` | 5 | merná produkcia odpadu s rozpätím, DOI a úrovňou dôkazu |
| `odhad_produkcie` | 288 | t/rok dolný, stredný a horný odhad na prevádzku a druh odpadu |
| `sektorovy_odhad` | 3 | národné odhady pre sektory, kde kapacita na prevádzku nedáva zmysel |
| `obec` | 478 | sídelné body s okresom, krajom a súradnicami |
| `zdroj_geo` | 3 | RPO, gazetteer, katalóg odpadov — vrátane licencie a spôsobu overenia |

Pohľady: `v_producent_odpad` (denormalizovaný výpis), `v_okres_sumar` (počty po okresoch),
`v_odpad_pokrytie` (koľko producentov pripadá na druh odpadu — ukazuje diery).

### Príklady dotazov

```sql
-- Kde vzniká pivovarské mláto
SELECT nazov, obec, okres FROM v_producent_odpad
WHERE odpad_kod = 'pivovarske_mlato' ORDER BY okres;

-- Ktoré okresy sú najbohatšie na producentov
SELECT * FROM v_okres_sumar ORDER BY producentov DESC LIMIT 10;

-- Substráty prípustné pre chov hmyzu v okrese Nitra
SELECT DISTINCT odpad, katalogove_cislo_navrh FROM v_producent_odpad
WHERE okres = 'Nitra' AND pravny_status <> 'odpad';

-- Kde sú diery
SELECT * FROM v_odpad_pokrytie WHERE producentov = 0;

-- Toky, ktoré sú pre krmivá zakázané, ale pre technický tuk prípustné
SELECT d.nazov_sk, d.katalogove_cislo_navrh, k.pripustnost AS krmivo, t.pripustnost AS technicky
FROM druh_odpadu d
JOIN odpad_draha k ON k.druh_odpadu_id=d.id AND k.draha_id=(SELECT id FROM draha WHERE kod='krmivo_hosp')
JOIN odpad_draha t ON t.druh_odpadu_id=d.id AND t.draha_id=(SELECT id FROM draha WHERE kod='technicky_tuk')
WHERE k.pripustnost='zakazane' AND t.pripustnost='povolene';

-- Kde je najviac producentov kuchynského odpadu
SELECT okres, COUNT(DISTINCT ico) FROM v_producent_odpad
WHERE katalogove_cislo_navrh='20 01 08' GROUP BY okres ORDER BY 2 DESC LIMIT 10;

-- Okresy podľa odhadovaného objemu
SELECT * FROM v_okres_objem ORDER BY t_rok_stred DESC LIMIT 15;

-- Najväčšie jednotlivé zdroje
SELECT nazov, obec, okres, kapacita, kapacita_jednotka, kapacita_uroven, t_rok_stred
FROM v_producent_objem ORDER BY t_rok_stred DESC LIMIT 20;

-- Koľko odhadov už stojí na skutočnej, nie typovej kapacite
SELECT uroven, COUNT(*) FROM kapacita GROUP BY uroven;
```

---

## Odkiaľ sú dáta

| Zdroj | Čo dodal | Licencia |
|-------|----------|----------|
| **Register právnických osôb, podnikateľov a orgánov verejnej moci** (ŠÚ SR), `api.statistics.sk/rpo/v1` | 486 reálnych subjektov: IČO, názov, adresa, obec s kódom | **CC BY 4.0** |
| **drakh/slovakia-gps-data** (ZBGIS SMD + OSM) | hranice 79 okresov a 8 krajov, 3 226 sídelných bodov | otvorené dáta |
| **Vyhláška MŽP SR č. 365/2015 Z. z.** — Katalóg odpadov | číselník katalógových čísel | právny predpis |

Nekopírovala sa žiadna chránená databáza. Feedipedia ani iné komerčné registre neboli
použité — rovnaký režim ako pri nutričnej časti databázy.

## Ako sa dáta overovali

Postup nadväzuje na protokol, ktorý už v projekte platí: **automatické načítanie vie vrátiť
presvedčivo vyzerajúcu, ale vymyslenú tabuľku.** Pri tomto zbere sa to stalo raz a je to
zdokumentované — prvý pokus o výpis píl vrátil skrátené, nepravé IČO. Celá dávka bola
zahodená a načítaná znovu s explicitnou požiadavkou na osemmiestne IČO.

Odhalila to **kontrolná číslica IČO (modulo 11)**. Je to najsilnejší dôkaz pravosti, aký je
tu k dispozícii: vymyslené osemmiestne číslo prejde kontrolou s pravdepodobnosťou približne
1 : 11, takže dávka desiatok vymyslených záznamov ňou neprejde nikdy. **486 zo 486 IČO
kontrolu prechádza.**

Druhá nezávislá kontrola je geometrická: bod priradený producentovi musí ležať vnútri
polygónu okresu, ktorý má v databáze zapísaný. Okres a súradnice pochádzajú z gazetteera,
hranice z iného súboru — zhoda preto nie je automatická. **485 z 485 bodov leží v správnom
okrese.**

Tretia kontrola je spätné overenie vzorky: šesť náhodne vybraných záznamov bolo znovu
načítaných priamym dopytom `identifier=` do RPO. Zhoda názvu aj obce **6 zo 6**:

| IČO | Názov v databáze | Odpoveď RPO |
|---|---|---|
| 43863035 | SAJ pekáreň, s. r. o. | zhoda |
| 00691135 | Mesto Košice | zhoda |
| 30998034 | Poľnohospodárske družstvo Okánikovo | zhoda |
| 44559313 | Pekáreň Hôrka, s.r.o. | zhoda |
| 47655950 | Agrofarma CM s.r.o. | zhoda |
| 46883631 | Mlyn Kolárovo, a. s. | zhoda |

Skript `build/qc_mapa.py` spúšťa **sedemnásť kontrol**; všetky prechádzajú. Štyri z nich sa týkajú
právnej vrstvy: úplnosť matice 92 × 9, vylúčenie kategórie 1 zo všetkých dráh, konzistencia
tvrdenia „kuchynský odpad — krmivo zakázané, technický tuk povolený" a existencia aspoň jednej
použiteľnej dráhy pri každom druhu okrem kategórie 1. Tri sa týkajú vrstvy objemu: konzistencia
rozpätia min ≤ stred ≤ max, naviazanie každého odhadu na kapacitu, a explicitné vykázanie toho,
koľko kapacít je meraných a koľko typových.

---

## Čo vrstva netvrdí

Toto je časť, ktorú treba prečítať pred použitím vo výstupe projektu.

- **Poloha je ťažisko obce podľa adresy v registri, nie GPS súradnica brány prevádzky.**
  Pri firmách so sídlom v Bratislave a výrobou inde je bod na mape na sídle, nie na závode.
  Pole `presnost_polohy` to hovorí pri každom zázname: `obec` (460), `mestska_cast` (14),
  `obec_zaklad` (5), `okres` (6 — obec nebola v gazetteeri, použité ťažisko okresu),
  `nezistena` (1).
- **Toky odpadu sú odvodené z typu prevádzky, nie z ohlásenia o vzniku odpadu.** Úroveň
  dôkazu D. Že pivovar produkuje mláto, je vecná istota; *koľko* ho produkuje, táto vrstva
  netvrdí vôbec. Množstevné údaje treba doplniť z ohlásení podľa § 14 zákona č. 79/2015 Z. z.,
  z RISO alebo priamo od prevádzkovateľov.
- **Katalógové čísla sú návrh**, `katalog_overeny = 0` pri všetkých 76 druhoch. Rovnaká
  konvencia ako v tabuľke `substrat`. Pred publikovaním musí zaradenie potvrdiť odborne
  spôsobilá osoba.
- **Zoznam nie je úplný register.** Vznikol dopytmi na kľúčové slová v názve subjektu, takže
  prevádzku, ktorá odbor nemá v názve (napr. mliekáreň s názvom podľa zakladateľa), nenájde.
  Je to reprodukovateľná vzorka, nie súpis. Doplnenie je lacné — pridá sa dopyt.
- **Prípustnosť dráh je právny výklad riešiteľského tímu, nie rozhodnutie orgánu.** Úroveň
  dôkazu D pri všetkých 828 kombináciách. Pred prevádzkovým použitím si vyžiadajte stanovisko
  ŠVPS SR — najmä pri kuchynskom odpade a ŽVP, kde je hranica medzi krmivovou a technickou
  dráhou určujúca pre celý biznis model.
- **Odhad objemu nie je meranie.** Je to súčin piatich faktorov, z ktorých dva — podiel
  stravníkov a počet prevádzkových dní — sú predpoklady riešiteľského tímu (úroveň D).
  Koeficienty sú z recenzovanej literatúry (úroveň B), ale zo Švédska, Číny, Libanonu
  a Holandska, nie zo Slovenska. Prvé vlastné váženie v jednej školskej jedálni a jednej
  nemocnici by hodnotu vrstvy zdvihlo viac než akékoľvek ďalšie dopĺňanie producentov.
- **Typová kapacita znamená, že jednotlivý bod je rádový.** Každá nemocnica má v databáze
  349 postelí. Súčet za okres je preto oveľa spoľahlivejší než hodnota pri jednej prevádzke.
  Postup nahradenia skutočnými počtami je popísaný vyššie.

## Kde sú diery

- **Množstvá chýbajú úplne.** Vrstva ukazuje *kde*, nie *koľko*. Toto je najväčšia diera
  a zároveň najhodnotnejší ďalší krok.
- **1 okres nemá producenta**: Košice III. Nie je to preto, že tam nič nevzniká, ale preto,
  že tam žiadny subjekt nemá odborové kľúčové slovo v názve.
- **1 druh odpadu bez producenta**: citrusové výlisky — na Slovensku sa citrusy priemyselne
  nespracúvajú, takže je to skutočná neprítomnosť, nie chyba zberu.
- **Školy a jedálne sú vzorka, nie register.** Slovensko má okolo 2 000 základných
  a 2 800 materských škôl; v databáze ich je toľko, koľko vrátil jeden dopyt na RPO. Rovnaké
  obmedzenie platí pre reštaurácie a hotely. Ak je cieľom úplný zoznam stravovacích prevádzok,
  vhodnejším zdrojom je register ŠVPS SR alebo CVTI SR (register škôl); postup je rovnaký,
  len sa vymení dopyt.
- **Pri školách bolo nutné filtrovať odborové organizácie.** Dopyt `fullName=Základná škola`
  vracia prevažne základné organizácie odborového zväzu so sídlom na adrese školy — nie školy
  samotné. Rieši to parameter `legalForm=Rozpočtová organizácia`; bez neho by databáza obsahovala
  stovky subjektov, ktoré nevarí ani nekosí.
- **Mestá sú v zozname len čiastočne.** RPO nevracia samosprávy na hromadný dopyt, takže
  sú vyhľadané po jednom (Bratislava, Košice, Prešov, Nitra, Žilina, Banská Bystrica,
  Trenčín, Trnava, Martin). Údržbu zelene v ďalších mestách zastupuje 23 technických služieb
  a 21 mestských lesov. Doplnenie zvyšných miest je opakovanie jedného dopytu.

## Ďalší krok, ak sa má vrstva použiť pri vykazovaní

1. Doplniť **množstvá** aspoň pri desiatich najväčších tokoch — z ohlásení o vzniku odpadu.
2. Nechať **overiť katalógové čísla** odborne spôsobilou osobou a prepnúť `katalog_overeny`.
3. Prepojiť `druh_odpadu.kod` na `substrat.id` v nutričnej databáze, aby mapa vedela ukázať
   aj zloženie, nielen polohu. Väzba je pripravená, stačí ju vyplniť.
4. Archivovať verziu na **Zenodo** spolu s nutričnou databázou — jeden DOI pre celý dataset.

## Licencie

Dáta **CC BY 4.0** (odvodené z RPO, ktoré je CC BY 4.0 — uvedenie zdroja je povinné),
kód **MIT**. Pri citovaní uvádzajte zdrojový register: *Údaje z Registra právnických osôb,
podnikateľov a orgánov verejnej moci, © Štatistický úrad SR, CC BY 4.0.*
