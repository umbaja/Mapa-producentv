# -*- coding: utf-8 -*-
"""Bilančný model energetickej a finančnej náročnosti chovu hmyzu (výstup D3.2).

Model je zámerne postavený zdola nahor z fyzikálnych parametrov prevádzky, nie
z jedného agregovaného koeficientu. Každý vstup má vlastnú jednotku, zdroj a úroveň
dôkazu, takže sa dá napadnúť a opraviť samostatne. Výsledky sú validované proti
publikovaným LCA štúdiám chovu hmyzu.

Hranica systému: brána - brána (gate to gate). Zahŕňa temperovanie chovného priestoru,
vetranie, osvetlenie, chod technológie, sušenie produktu a dopravu substrátu.
Nezahŕňa výstavbu budovy, výrobu zariadení ani distribúciu hotového produktu.
"""
import json, math

# ---------------------------------------------------------------------------
# 1. VSTUPNÉ PARAMETRE
# ---------------------------------------------------------------------------

# Klimatický normál 1991-2020, stanica Hurbanovo (ročný priemer 11,1 °C).
# Reprezentuje juh Slovenska, kde je sústredená väčšina potravinárskych prevádzok.
TEPLOTY_MESACNE = [0.1, 1.8, 6.1, 12.0, 16.6, 20.3, 22.0, 21.4, 16.1, 10.8, 5.9, 1.0]
DNI_MESIACE = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

ZAKLAD = dict(
    # --- produkcia ---
    larvy_cerstve_t_rok = 100.0,   # t čerstvých lariev za rok
    susina_lariev_pct   = 28.0,    # % sušiny v čerstvých larvách
    vlhkost_produktu_pct= 7.0,     # % vlhkosti v sušenom produkte
    susit               = True,    # sušiť produkt, alebo predávať čerstvé larvy

    # --- chovný priestor ---
    plocha_m2           = 600.0,   # podlahová plocha chovnej haly
    vyska_m             = 4.0,     # svetlá výška
    u_hodnota           = 0.35,    # W/(m²·K) - priemerná pre obal budovy
    obalova_plocha_faktor = 2.6,   # obalová plocha ako násobok podlahovej plochy
    vymeny_vzduchu_h    = 2.0,     # výmeny vzduchu za hodinu
    teplota_vnutorna    = 28.0,    # °C - cieľová teplota chovu
    rekuperacia_pct     = 0.0,     # % spätného získavania tepla z vetrania

    # --- metabolické teplo lariev ---
    metabolicke_teplo_w_m2 = 0.0,  # W/m² - zámerne 0; viď poznámku v dokumentácii

    # --- elektrická záťaž mimo kúrenia ---
    osvetlenie_w_m2     = 4.0,     # W/m² inštalovaný príkon
    osvetlenie_h_den    = 12.0,    # hodín denne
    technologia_kw      = 6.0,     # priemerný príkon technológie (dopravníky, triedenie)
    technologia_h_den   = 8.0,

    # --- sušenie ---
    sus_kwh_na_kg_vody  = 1.30,    # kWh na kg odparenej vody (pásová sušiareň)

    # --- doprava substrátu ---
    substrat_t_na_t_lariev = 6.0,  # t substrátu na 1 t čerstvých lariev
    doprava_km          = 40.0,    # priemerná prepravná vzdialenosť (jedným smerom)
    doprava_kg_co2_tkm  = 0.11,    # kg CO2e na tonokilometer, nákladné vozidlo

    # --- zdroj tepla ---
    zdroj_tepla         = 'elektrina',  # elektrina | tepelne_cerpadlo | plyn
    cop_tepelne_cerpadlo= 3.2,
    ucinnost_kotla      = 0.92,

    # --- ceny a emisné faktory ---
    cena_elektrina      = 0.1837,  # €/kWh - priemer EÚ, nedomácnosti, 2. polrok 2025
    cena_plyn           = 0.0605,  # €/kWh - priemer EÚ, nedomácnosti, 2. polrok 2025
    ef_elektrina        = 0.095,   # kg CO2e/kWh - SR, priemer z dvoch nezávislých zdrojov
    ef_plyn             = 0.202,   # kg CO2e/kWh - zemný plyn, štandardný emisný faktor
)

# ---------------------------------------------------------------------------
# 2. VÝPOČET
# ---------------------------------------------------------------------------

def bilancia(p):
    """Vráti energetickú, nákladovú a emisnú bilanciu za rok a na kg produktu."""
    o = dict(p)

    # --- množstvo produktu ---
    larvy_kg = o['larvy_cerstve_t_rok'] * 1000.0
    susina_kg = larvy_kg * o['susina_lariev_pct'] / 100.0
    if o['susit']:
        produkt_kg = susina_kg / (1.0 - o['vlhkost_produktu_pct'] / 100.0)
        voda_odparena_kg = larvy_kg - produkt_kg
    else:
        produkt_kg = larvy_kg
        voda_odparena_kg = 0.0

    # --- tepelná strata obalom a vetraním, po mesiacoch ---
    obal_m2 = o['plocha_m2'] * o['obalova_plocha_faktor']
    objem_m3 = o['plocha_m2'] * o['vyska_m']
    prietok_m3_h = objem_m3 * o['vymeny_vzduchu_h']
    ucin_rek = 1.0 - o['rekuperacia_pct'] / 100.0

    teplo_kwh = 0.0
    for t_out, dni in zip(TEPLOTY_MESACNE, DNI_MESIACE):
        dT = o['teplota_vnutorna'] - t_out
        if dT <= 0:
            continue
        q_obal = o['u_hodnota'] * obal_m2 * dT                      # W
        q_vetr = 0.34 * prietok_m3_h * dT * ucin_rek                # W
        q_meta = o['metabolicke_teplo_w_m2'] * o['plocha_m2']       # W (zisk)
        q_net = max(0.0, q_obal + q_vetr - q_meta)
        teplo_kwh += q_net * dni * 24.0 / 1000.0

    # --- prevod tepla na spotrebu podľa zdroja ---
    if o['zdroj_tepla'] == 'tepelne_cerpadlo':
        kur_el, kur_plyn = teplo_kwh / o['cop_tepelne_cerpadlo'], 0.0
    elif o['zdroj_tepla'] == 'plyn':
        kur_el, kur_plyn = 0.0, teplo_kwh / o['ucinnost_kotla']
    else:
        kur_el, kur_plyn = teplo_kwh, 0.0

    # --- ostatná elektrina ---
    osvetlenie_kwh = o['osvetlenie_w_m2'] * o['plocha_m2'] / 1000.0 * o['osvetlenie_h_den'] * 365.0
    technologia_kwh = o['technologia_kw'] * o['technologia_h_den'] * 365.0
    susenie_kwh = voda_odparena_kg * o['sus_kwh_na_kg_vody']

    el_kwh = kur_el + osvetlenie_kwh + technologia_kwh + susenie_kwh
    plyn_kwh = kur_plyn

    # --- doprava substrátu ---
    substrat_t = o['larvy_cerstve_t_rok'] * o['substrat_t_na_t_lariev']
    doprava_tkm = substrat_t * o['doprava_km']
    doprava_co2 = doprava_tkm * o['doprava_kg_co2_tkm']

    # --- náklady a emisie ---
    naklady = el_kwh * o['cena_elektrina'] + plyn_kwh * o['cena_plyn']
    emisie = el_kwh * o['ef_elektrina'] + plyn_kwh * o['ef_plyn'] + doprava_co2

    zlozky = {
        'kúrenie':    kur_el * o['ef_elektrina'] + kur_plyn * o['ef_plyn'],
        'sušenie':    susenie_kwh * o['ef_elektrina'],
        'osvetlenie': osvetlenie_kwh * o['ef_elektrina'],
        'technológia':technologia_kwh * o['ef_elektrina'],
        'doprava':    doprava_co2,
    }
    energia_zlozky = {
        'kúrenie': kur_el + kur_plyn, 'sušenie': susenie_kwh,
        'osvetlenie': osvetlenie_kwh, 'technológia': technologia_kwh,
    }

    return dict(
        produkt_kg=produkt_kg, voda_odparena_kg=voda_odparena_kg,
        teplo_kwh=teplo_kwh, el_kwh=el_kwh, plyn_kwh=plyn_kwh,
        energia_kwh=el_kwh + plyn_kwh,
        kwh_na_kg=(el_kwh + plyn_kwh) / produkt_kg,
        eur_na_kg=naklady / produkt_kg,
        co2_na_kg=emisie / produkt_kg,
        naklady_rok=naklady, emisie_rok=emisie,
        energia_zlozky=energia_zlozky, emisie_zlozky=zlozky,
    )

# ---------------------------------------------------------------------------
# 3. SCENÁRE
# ---------------------------------------------------------------------------

SCENARE = [
    ("Z",  "Základný scenár", {}),
    ("K1", "Cenový šok: elektrina 0,35 €/kWh", dict(cena_elektrina=0.35)),
    ("K2", "Cenový šok: elektrina 0,50 €/kWh", dict(cena_elektrina=0.50)),
    ("K3", "Chladná zima: vonkajšie teploty o 3 K nižšie", dict(_dT=-3.0)),
    ("O1", "Tepelné čerpadlo namiesto elektrického kúrenia", dict(zdroj_tepla='tepelne_cerpadlo')),
    ("O2", "Plynový kotol namiesto elektrického kúrenia", dict(zdroj_tepla='plyn')),
    ("O3", "Rekuperácia tepla z vetrania 70 %", dict(rekuperacia_pct=70.0)),
    ("O4", "Zateplenie obalu na U = 0,18 W/(m²·K)", dict(u_hodnota=0.18)),
    ("O5", "Bez sušenia — predaj čerstvých lariev", dict(susit=False)),
    ("O6", "Kombinácia O1 + O3 + O4", dict(zdroj_tepla='tepelne_cerpadlo', rekuperacia_pct=70.0, u_hodnota=0.18)),
    ("D1", "Substrát z okruhu 150 km namiesto 40 km", dict(doprava_km=150.0)),
    ("D2", "Substrát z okruhu 10 km", dict(doprava_km=10.0)),
]

def spusti_scenar(zmeny):
    global TEPLOTY_MESACNE
    p = dict(ZAKLAD)
    dT = zmeny.pop('_dT', None) if isinstance(zmeny, dict) else None
    zaloha = TEPLOTY_MESACNE
    if dT is not None:
        TEPLOTY_MESACNE = [t + dT for t in TEPLOTY_MESACNE]
    p.update({k: v for k, v in zmeny.items() if not k.startswith('_')})
    v = bilancia(p)
    TEPLOTY_MESACNE = zaloha
    return v

if __name__ == '__main__':
    print(f"{'kód':<4}{'scenár':<52}{'kWh/kg':>9}{'€/kg':>9}{'kg CO2e/kg':>12}")
    print("-" * 86)
    vysledky = {}
    for kod, nazov, zmeny in SCENARE:
        v = spusti_scenar(dict(zmeny))
        vysledky[kod] = dict(nazov=nazov, **{k: v[k] for k in ('kwh_na_kg','eur_na_kg','co2_na_kg','energia_kwh','naklady_rok','emisie_rok','produkt_kg')})
        print(f"{kod:<4}{nazov:<52}{v['kwh_na_kg']:>9.2f}{v['eur_na_kg']:>9.2f}{v['co2_na_kg']:>12.3f}")
    z = spusti_scenar({})
    print("\nZákladný scenár — rozklad spotreby energie (kWh/rok):")
    for k, val in sorted(z['energia_zlozky'].items(), key=lambda x: -x[1]):
        print(f"  {k:<14}{val:>12,.0f}   {100*val/z['energia_kwh']:>5.1f} %".replace(",", " "))
    print(f"  {'SPOLU':<14}{z['energia_kwh']:>12,.0f}".replace(",", " "))
    print("\nZákladný scenár — rozklad emisií (kg CO2e/rok):")
    for k, val in sorted(z['emisie_zlozky'].items(), key=lambda x: -x[1]):
        print(f"  {k:<14}{val:>12,.0f}   {100*val/z['emisie_rok']:>5.1f} %".replace(",", " "))
    print(f"  {'SPOLU':<14}{z['emisie_rok']:>12,.0f}".replace(",", " "))
    print(f"\nProdukt: {z['produkt_kg']:,.0f} kg sušeného produktu za rok".replace(",", " "))
    print(f"Odparená voda: {z['voda_odparena_kg']:,.0f} kg/rok".replace(",", " "))
    json.dump(vysledky, open('build/d32_scenare.json','w'), ensure_ascii=False, indent=1)
