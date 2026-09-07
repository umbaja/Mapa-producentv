# -*- coding: utf-8 -*-
"""Kapacity prevádzok a koeficienty produkcie kuchynského odpadu.

Odhad objemu stojí na piatich samostatne viditeľných faktoroch:

    t/rok = kapacita × podiel_stravníkov × jedál_za_deň × koeficient(g/jedlo) × dní_rok / 10^6

Každý faktor má vlastný zdroj a vlastnú úroveň dôkazu. Nič sa nezlučuje do jedného
"magického" čísla, takže sa dá napadnúť a opraviť ktorýkoľvek z nich zvlášť.
"""

# --- typové kapacity: národný súčet delený počtom zariadení ---------------
# CVTI SR, Vývojové tendencie ukazovateľov MŠ, ZŠ a SŠ, školský rok 2021/22.
# Zdroj načítaný dvakrát s odlišne formulovanou otázkou, obe načítania sa zhodujú.
TYPOVA_KAPACITA = {
 # typ_prevadzky: (hodnota, jednotka, zdroj, poznamka)
 "skola_materska": (56, "dieťa",
   "CVTI SR, Vývojové tendencie 2022: 173 170 detí / 3 102 MŠ (2021/22)",
   "Aritmetický priemer na zariadenie; skutočné MŠ sa pohybujú od 20 do 250 detí."),
 "skola_zakladna": (226, "žiak",
   "CVTI SR, Vývojové tendencie 2022: 468 540 žiakov / 2 070 ZŠ (2021/22)",
   "Aritmetický priemer; malotriedky majú desiatky, sídliskové ZŠ vyše 800 žiakov."),
 "skola_stredna": (299, "žiak",
   "CVTI SR, Vývojové tendencie 2022: (72 776 + 121 470) žiakov / (233 gymnázií + 416 SOŠ) (2021/22)",
   "Aritmetický priemer gymnázií a SOŠ."),
 "skolska_jedalen": (226, "stravník",
   "Odvodené z typovej kapacity ZŠ (CVTI SR 2021/22)",
   "Samostatne zapísaná školská jedáleň spravidla obsluhuje jednu ZŠ."),
 "nemocnica": (349, "lôžko",
   "Eurostat hlth_rs_bds: 31 422 postelí (2019) / 90 nemocníc (MF SR, Revízia výdavkov na nemocnice 2025)",
   "Priemer na nemocnicu; fakultné nemocnice majú vyše 1 000 postelí, malé pod 100."),
}

# socialne_zariadenie zámerne chýba - kapacitu zariadení sociálnych služieb sa
# nepodarilo získať z overiteľného zdroja (NKÚ aj MPSVR SR blokujú automatické
# načítanie). Odhad sa preto pri týchto prevádzkach nepočíta.

# --- koeficienty produkcie -------------------------------------------------
# (typ_prevadzky, druh_odpadu_kod,
#  koef_min, koef_stred, koef_max [g na jedlo alebo na lôžkodeň],
#  jedal_za_den, podiel_stravnikov, dni_rok, zdroj, doi, uroven_dokazu, poznamka)
KOEFICIENTY = [
 ("skola_zakladna","skolsky_kuchynsky_odpad", 45, 55, 80, 1.0, 0.75, 190,
  "Malefors a kol. 2026, Environmental Development 57:101386 (45-47 g/stravník, Švédsko, 693 škôl); "
  "Zhang a kol. 2024, Front. Sustain. Food Syst. 8:1336220 (44,5 g/stravník, obed 55,3 g, Čína)",
  "10.1016/j.envdev.2025.101386; 10.3389/fsufs.2024.1336220", "B",
  "Dva nezávislé zdroje sa zhodujú na 45-55 g na porciu. Horná hranica 80 g pokrýva "
  "kuchynský odpad z prípravy, ktorý švédska metodika započítava len čiastočne. "
  "Podiel stravníkov 0,75 a 190 vyučovacích dní sú predpoklady riešiteľského tímu (úroveň D)."),
 ("skola_materska","skolsky_kuchynsky_odpad", 45, 55, 80, 2.5, 0.95, 210,
  "Rovnaké koeficienty ako pri ZŠ; 2,5 jedla denne (desiata, obed, olovrant s nižšou hmotnosťou)",
  "10.1016/j.envdev.2025.101386", "C",
  "Prenos koeficientu zo školského na predškolské stravovanie je predpoklad, nie meranie."),
 ("skola_stredna","skolsky_kuchynsky_odpad", 45, 55, 80, 1.0, 0.50, 190,
  "Malefors a kol. 2026 (starší žiaci 36 g odpadu z taniera vs. 18 g u mladších)",
  "10.1016/j.envdev.2025.101386", "B",
  "Nižší podiel stravníkov - stredoškoláci sa vo väčšej miere stravujú mimo školy."),
 ("skolska_jedalen","skolsky_kuchynsky_odpad", 45, 55, 80, 1.0, 1.00, 190,
  "Malefors a kol. 2026; Zhang a kol. 2024",
  "10.1016/j.envdev.2025.101386; 10.3389/fsufs.2024.1336220", "B",
  "Kapacita jedálne je priamo počet stravníkov, preto podiel 1,0."),
 ("nemocnica","nemocnicny_kuchynsky_odpad", 240, 320, 390, 1.0, 0.659, 365,
  "Abiad a kol. 2025, Front. Sustain. Food Syst. 9:1516331 (390 g/lôžko/deň, 16 nemocníc, Libanon); "
  "Burgoa Sánchez a de Camargo 2026, Sustainability 18(3):1458 (81 g/jedlo, Holandsko, ~240 g/deň); "
  "obložnosť akútnych lôžok 65,9 % - MF SR, Revízia výdavkov na nemocnice 2025",
  "10.3389/fsufs.2025.1516331; 10.3390/su18031458", "B",
  "Koeficient je na lôžkodeň, preto jedál_za_deň = 1. Obložnosť 65,9 % je nezávisle potvrdená "
  "výpočtom z NCZI (988 691 hospitalizácií × 7,8 dňa / 31 422 postelí / 365 = 67 %)."),
]

# --- sektorové odhady, kde kapacita na prevádzku nedáva zmysel -------------
# Reštaurácie, hotely a retail sú v databáze menovite, ale bez počtu miest ani
# obratu. Namiesto falošnej presnosti na prevádzku sa uvádza národný odhad.
SEKTOROVY_ODHAD = [
 ("Reštaurácie a stravovacie služby", 14.0, "kg/obyvateľa/rok", 5_420_000,
  "Eurostat env_wasfw (2023), priemer EÚ: 14 kg/obyv./rok v sektore reštaurácií a stravovacích služieb",
  "Prepočet na SR je alokácia priemeru EÚ, nie meranie v SR."),
 ("Maloobchod a distribúcia potravín", 10.0, "kg/obyvateľa/rok", 5_420_000,
  "Eurostat env_wasfw (2023), priemer EÚ: 10 kg/obyv./rok v maloobchode a distribúcii",
  "Prepočet na SR je alokácia priemeru EÚ, nie meranie v SR."),
 ("Spracovanie potravín", 24.0, "kg/obyvateľa/rok", 5_420_000,
  "Eurostat env_wasfw (2023), priemer EÚ: 24 kg/obyv./rok v spracovaní a výrobe potravín",
  "Zahŕňa priemyselné toky (mláto, srvátka, výlisky), ktoré vrstva menovite eviduje, ale nekvantifikuje."),
]

# počet zariadení v SR pre národnú extrapoláciu
NARODNE_POCTY = {
 "skola_materska": (3102, "CVTI SR, Vývojové tendencie 2022"),
 "skola_zakladna": (2070, "CVTI SR, Vývojové tendencie 2022"),
 "skola_stredna": (649, "CVTI SR, Vývojové tendencie 2022 (233 gymnázií + 416 SOŠ)"),
 "nemocnica": (90, "MF SR, Revízia výdavkov na nemocnice, marec 2025"),
}
