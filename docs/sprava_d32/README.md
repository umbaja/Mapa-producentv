# Zdroj štúdie k výstupu D3.2

Štúdia `docs/APETBIO_D3-2_Energetika_uhlikova_stopa.pdf` sa zostavuje z častí v tomto priečinku.

```bash
python3 build/model_d32.py          # prepočíta scenáre, vypíše tabuľku a zapíše build/d32_scenare.json
python3 docs/sprava_d32/build.py    # zostaví PDF
```

Čísla v texte štúdie sú prevzaté z výstupu `build/model_d32.py`. Pri zmene vstupných parametrov
modelu treba spustiť skript a hodnoty v kapitolách 4 a 5 aktualizovať — sú v `c3.html` uvedené
ručne, aby text zostal čitateľný.

Model je implementovaný dvakrát: v Pythone (`build/model_d32.py`) a v JavaScripte
(`assets/kalk.js`) pre verejnú kalkulačku. **Obe implementácie musia dávať zhodné výsledky** —
je to kontrola proti chybe v prepise vzorcov. Pri zmene modelu upravte obe a porovnajte
základný scenár aj všetkých jedenásť scenárov.
