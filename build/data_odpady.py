# -*- coding: utf-8 -*-
"""Číselník biotransformovateľných odpadov a väzba na typy producentov.

Katalógové čísla sú NÁVRH podľa charakteru materiálu (vyhláška MŽP SR č. 365/2015 Z. z.,
skupiny 02, 03, 19, 20). Pole katalog_overeny = 0 pri všetkých záznamoch — pred publikovaním
musí zaradenie potvrdiť odborne spôsobilá osoba. Rovnaká konvencia ako v tabuľke substrat.
"""

# kod, nazov_sk, nazov_en, katalogove_cislo_navrh, skupina, pravny_status,
# sezonnost, drahy (H=hmyz, F=fermentácia/SSF, E=enzymatická hydrolýza, A=anaeróbna digescia),
# poznamka
ODPADY = [
 # --- nápojársky priemysel ---
 ("pivovarske_mlato","Pivovarské mláto","Brewer's spent grain","02 07 01","napoje","vedlajsi_produkt","celorocne","H,F,E","Najväčší jednotlivý tok v SR; vlhkosť 75-80 %, rýchlo sa kazí"),
 ("pivovarske_kvasnice","Pivovarské kvasnice","Spent brewer's yeast","02 07 05","napoje","vedlajsi_produkt","celorocne","H,F","Vysoký obsah dusíkatých látok a B-vitamínov"),
 ("chmelovy_mlat","Chmeľový mlát","Spent hops","02 07 01","napoje","odpad","celorocne","F,A","Horké látky obmedzujú kŕmne využitie"),
 ("kremelinovy_kal","Kremelinový kal z filtrácie","Kieselguhr filter sludge","02 07 05","napoje","odpad","celorocne","A","Vysoký podiel anorganického nosiča"),
 ("sladovy_klicok","Sladový klíčok","Malt rootlets","02 07 01","napoje","krmna_surovina","celorocne","H,F","Zapísaný v Katalógu kŕmnych surovín (EÚ) 68/2013"),
 ("sladovy_prach","Sladový prach a plevy","Malt dust and husks","02 07 01","napoje","vedlajsi_produkt","celorocne","H,F",""),
 ("hroznove_vylisky","Hroznové výlisky (matolina)","Grape pomace","02 07 04","napoje","vedlajsi_produkt","sezonne_jesen","F,E","Polyfenoly a taníny znižujú stráviteľnosť"),
 ("vinne_kaly","Vínne kaly","Wine lees","02 07 05","napoje","odpad","sezonne_jesen","F,A",""),
 ("hroznove_stopky","Hroznové stopky (strapiny)","Grape stalks","02 07 01","napoje","odpad","sezonne_jesen","E,A","Lignocelulóza, vyžaduje predúpravu"),
 ("vypalky","Liehovarnícke výpalky","Distillery stillage","02 07 02","napoje","vedlajsi_produkt","celorocne","H,F,A","Nízke pH, vysoký obsah vody"),
 ("jablcne_vylisky","Jablčné výlisky","Apple pomace","02 07 04","napoje","vedlajsi_produkt","sezonne_jesen","H,F,E","Vysoký podiel pektínu a NSC"),
 ("bobulove_vylisky","Výlisky z bobuľového ovocia","Berry pomace","02 07 04","napoje","vedlajsi_produkt","sezonne_leto","H,F",""),
 ("citrusove_vylisky","Citrusové výlisky","Citrus peel","02 03 04","potravinarstvo","vedlajsi_produkt","celorocne","F,E","Limonén inhibuje mikrobiálne procesy"),
 # --- mliekarenský priemysel ---
 ("srvatka_sladka","Sladká srvátka","Sweet whey","02 05 01","mliekarstvo","vedlajsi_produkt","celorocne","F,E","Laktóza ako uhlíkový zdroj pre kvasinky"),
 ("srvatka_kysla","Kyslá srvátka","Acid whey","02 05 01","mliekarstvo","odpad","celorocne","F,A","pH pod 5, horšie zhodnotiteľná"),
 ("srvatkovy_permeat","Srvátkový permeát","Whey permeate","02 05 01","mliekarstvo","vedlajsi_produkt","celorocne","F",""),
 ("cmar","Cmar","Buttermilk","02 05 01","mliekarstvo","krmna_surovina","celorocne","H,F",""),
 ("mliekarensky_kal","Kal z mliekarenskej ČOV","Dairy WWTP sludge","02 05 02","mliekarstvo","odpad","celorocne","A","Kontrola kontaminantov nutná"),
 # --- mäso, ryby, ŽVP ---
 ("bachorovy_obsah","Obsah bachora a tráviaceho traktu","Rumen and digestive tract content","02 02 04","maso","odpad","celorocne","H,A","ABP kat. 2 - pre hmyz na krmivá neprípustné"),
 ("krv_bitunok","Krv z bitúnku","Slaughterhouse blood","02 02 03","maso","vedlajsi_produkt","celorocne","F","ABP kat. 3; pre hmyz obmedzené nar. (ES) 1069/2009"),
 ("perie","Perie z hydinových bitúnkov","Poultry feathers","02 02 02","maso","odpad","celorocne","E,F","Keratín - vyžaduje keratinolytické mikroorganizmy"),
 ("kostny_zvysok","Kosti a kostné zvyšky","Bone residues","02 02 02","maso","vedlajsi_produkt","celorocne","E",""),
 ("kozne_odrezky","Kožné odrezky a podkožný tuk","Hide trimmings and fat","02 02 02","maso","odpad","celorocne","E,A",""),
 ("masovy_flotacny_kal","Flotačný kal z mäsospracovania","Meat processing flotation sludge","02 02 04","maso","odpad","celorocne","A",""),
 ("rybie_zvysky","Rybie hlavy, vnútornosti a kosti","Fish processing residues","02 02 03","maso","vedlajsi_produkt","celorocne","E,F","Zdroj rybieho oleja a hydrolyzátu"),
 ("kal_akvakultura","Kal z akvakultúry","Aquaculture sludge","02 01 01","maso","odpad","celorocne","A",""),
 # --- cukrovarníctvo a olejniny ---
 ("repne_rezky","Cukrovarnícke repné rezky","Sugar beet pulp","02 04 99","potravinarstvo","krmna_surovina","sezonne_jesen","H,F,E","Kampaň september-január"),
 ("melasa","Melasa","Molasses","02 04 99","potravinarstvo","krmna_surovina","sezonne_jesen","F","Uhlíkový substrát pre fermentácie"),
 ("saturacne_kaly","Saturačné kaly","Carbonation lime sludge","02 04 02","potravinarstvo","odpad","sezonne_jesen","A","Prevažne CaCO3, nutrične bezcenné"),
 ("repna_zemina","Zemina a chvostíky z prania repy","Beet washing soil","02 04 01","potravinarstvo","odpad","sezonne_jesen","A",""),
 ("repkovy_srot","Repkový extrahovaný šrot","Rapeseed meal","02 03 04","potravinarstvo","krmna_surovina","celorocne","H,F","Glukozinoláty ako antinutričný faktor"),
 ("slnecnicovy_srot","Slnečnicový extrahovaný šrot","Sunflower meal","02 03 04","potravinarstvo","krmna_surovina","celorocne","H,F",""),
 ("olejnaty_kal","Kaly z rafinácie jedlých olejov","Edible oil refining sludge","02 03 05","potravinarstvo","odpad","celorocne","A",""),
 # --- škrob, mlyny, pekárne ---
 ("skrobarenske_zvysky","Škrobárenské zvyšky","Starch industry residues","02 03 01","potravinarstvo","vedlajsi_produkt","celorocne","H,F,E",""),
 ("zemiakove_supky","Zemiakové šupky a orezky","Potato peelings","02 03 04","potravinarstvo","vedlajsi_produkt","celorocne","H,F","Solanín pri zelených hľuzách"),
 ("psenicne_otruby","Pšeničné otruby","Wheat bran","02 03 04","potravinarstvo","krmna_surovina","celorocne","H,F,E","Štandardný nosič pri SSF"),
 ("mlynske_zmetky","Mlynské zmetky a plevy","Mill screenings","02 03 04","potravinarstvo","vedlajsi_produkt","celorocne","H,F",""),
 ("pekarenske_zvysky","Pekárenské zvyšky","Bakery waste","02 06 01","potravinarstvo","vedlajsi_produkt","celorocne","H,F","Vysoká energetická hustota, nízke NL"),
 ("cestovinove_zvysky","Cestovinové a múčne zvyšky","Pasta and flour residues","02 06 01","potravinarstvo","vedlajsi_produkt","celorocne","H,F",""),
 ("cukrovinkarske_zvysky","Zvyšky z výroby cukroviniek","Confectionery residues","02 06 01","potravinarstvo","vedlajsi_produkt","celorocne","H,F","Vysoký podiel jednoduchých cukrov"),
 # --- káva, čaj, zelenina, droždie ---
 ("kavova_sedlina","Kávová sedlina","Spent coffee grounds","02 03 04","potravinarstvo","odpad","celorocne","H,F,E","Kofeín a polyfenoly limitujú dávku"),
 ("kavove_slupky","Kávové šupky (silverskin)","Coffee silverskin","02 03 04","potravinarstvo","vedlajsi_produkt","celorocne","F,E",""),
 ("zeleninove_orezky","Orezky a nepodarky zeleniny","Vegetable trimmings","02 03 04","potravinarstvo","odpad","sezonne_leto","H,F,A",""),
 ("kal_pranie_zeleniny","Kal z prania a lúpania zeleniny","Vegetable washing sludge","02 03 01","potravinarstvo","odpad","sezonne_leto","A",""),
 ("drozdiarske_zvysky","Zvyšky z výroby droždia","Yeast production residues","02 03 04","potravinarstvo","vedlajsi_produkt","celorocne","F",""),
 ("syrarska_srvatka_tuh","Tuhé zvyšky zo syrárskej výroby","Cheese production solids","02 05 01","mliekarstvo","vedlajsi_produkt","celorocne","H,F",""),
 # --- poľnohospodárstvo, rastlinná výroba ---
 ("slama_obilna","Obilná slama","Cereal straw","02 01 03","polnohospodarstvo","vedlajsi_produkt","sezonne_leto","E,A","Lignocelulóza; nutná predúprava"),
 ("kukuricne_korovie","Kukuričné kôrovie a stonky","Maize stover","02 01 03","polnohospodarstvo","vedlajsi_produkt","sezonne_jesen","E,A",""),
 ("repkova_slama","Repková slama","Rapeseed straw","02 01 03","polnohospodarstvo","vedlajsi_produkt","sezonne_leto","E,A",""),
 ("slnecnicove_stonky","Slnečnicové stonky a úbory","Sunflower stalks and heads","02 01 03","polnohospodarstvo","odpad","sezonne_jesen","E,A",""),
 ("travna_hmota_ttp","Trávna hmota z lúk a TTP","Grassland biomass","02 01 03","polnohospodarstvo","vedlajsi_produkt","sezonne_leto","H,F,A","Zdroj listového proteínového koncentrátu"),
 ("vnate_pozberove","Vňate a pozberové zvyšky zeleniny","Vegetable haulm residues","02 01 03","polnohospodarstvo","odpad","sezonne_jesen","H,A",""),
 ("odpad_cistenie_zrna","Odpad z čistenia a sušenia obilia","Grain cleaning waste","02 01 03","polnohospodarstvo","vedlajsi_produkt","sezonne_leto","H,F","Riziko mykotoxínov"),
 # --- poľnohospodárstvo, živočíšna výroba ---
 ("hnoj_hovadzi","Maštaľný hnoj hovädzí","Cattle manure","02 01 06","polnohospodarstvo","odpad","celorocne","A","Pre hmyz na krmivá zakázané - nar. (ES) 1069/2009"),
 ("hnojovica_osipane","Hnojovica ošípaných","Pig slurry","02 01 06","polnohospodarstvo","odpad","celorocne","A","Pre hmyz na krmivá zakázané"),
 ("hydinovy_trus","Hydinový trus a podstielka","Poultry litter","02 01 06","polnohospodarstvo","odpad","celorocne","A","Pre hmyz na krmivá zakázané"),
 ("ovciarsky_hnoj","Ovčí a kozí hnoj","Sheep and goat manure","02 01 06","polnohospodarstvo","odpad","celorocne","A","Pre hmyz na krmivá zakázané"),
 ("kadavery","Uhynuté zvieratá (kadávery)","Fallen stock","02 01 02","polnohospodarstvo","odpad","celorocne","-","ABP kat. 1/2 - vylúčené z potravinového aj krmivového reťazca"),
 # --- komunálny a gastro ---
 ("travna_hmota_kosba","Trávna hmota z kosby verejnej zelene","Municipal grass clippings","20 02 01","komunalny","odpad","sezonne_leto","H,F,A","Kosba miest 6-10x ročne; riziko posypových solí a Pb pri cestách"),
 ("konare_stiepka","Konáre a drevná štiepka z údržby zelene","Municipal woody green waste","20 02 01","komunalny","odpad","sezonne_jar","E,A",""),
 ("listie","Lístie z verejnej zelene","Municipal leaf litter","20 02 01","komunalny","odpad","sezonne_jesen","F,A",""),
 ("bro_zahrady","Biologicky rozložiteľný odpad zo záhrad","Garden biowaste","20 02 01","komunalny","odpad","sezonne_leto","H,F,A",""),
 ("kuchynsky_odpad","Biologicky rozložiteľný kuchynský a reštauračný odpad","Food and catering waste","20 01 08","komunalny","odpad","celorocne","H,A","Obsahuje ŽVP - sterilizácia povinná"),
 ("jedle_oleje_pouzite","Použité jedlé oleje a tuky","Used cooking oil","20 01 25","komunalny","odpad","celorocne","F",""),
 ("odpad_trhoviska","Odpad z trhovísk","Market waste","20 03 02","komunalny","odpad","sezonne_leto","H,A",""),
 ("potraviny_po_dobe","Nepredané potraviny po dátume spotreby","Retail food surplus","20 01 08","komunalny","odpad","celorocne","H,F","Rozdielny status podľa obsahu ŽVP"),
 ("digestat","Digestát z bioplynovej stanice","Digestate","19 06 06","komunalny","odpad","celorocne","F","Vstup pre ďalšie zhodnotenie, nie primárny odpad"),
 ("kompost_nevyhovujuci","Kompost nevyhovujúcej kvality","Off-spec compost","19 05 03","komunalny","odpad","celorocne","-",""),
 ("cov_kal_komunalny","Kal z komunálnej ČOV","Municipal sewage sludge","19 08 05","komunalny","odpad","celorocne","-","Vylúčené z chovu hmyzu na krmivá"),
 ("tuky_odlucovace","Tuky z odlučovačov","Grease trap fats","19 08 09","komunalny","odpad","celorocne","A",""),
 # --- drevo, lesníctvo, papier ---
 ("kora","Odpadová kôra","Bark","03 01 01","drevo","vedlajsi_produkt","celorocne","F,E","Substrát pre vláknité huby"),
 ("piliny","Piliny a hobliny","Sawdust and shavings","03 01 05","drevo","vedlajsi_produkt","celorocne","F,E","Nosič pri SSF a pri pestovaní húb"),
 ("odrezky_dreva","Odrezky a drevný odpad","Wood offcuts","03 01 05","drevo","vedlajsi_produkt","celorocne","E",""),
 ("lesna_stiepka","Lesná štiepka a haluzina","Forest chips and slash","02 01 07","drevo","vedlajsi_produkt","celorocne","E,A",""),
 ("papierensky_kal","Papierenský kal","Paper mill sludge","03 03 11","drevo","odpad","celorocne","F,A",""),
 ("vlaknity_vymet","Výmety z vlákien a plnív","Fibre rejects","03 03 10","drevo","odpad","celorocne","F",""),
]

# typ producenta (keyword v RPO harveste) -> zoznam kodov odpadu
PRODUCENT_ODPAD = {
 "pivovar": ["pivovarske_mlato","pivovarske_kvasnice","chmelovy_mlat","kremelinovy_kal"],
 "sladovna": ["sladovy_klicok","sladovy_prach"],
 "mliekaren": ["srvatka_sladka","srvatka_kysla","srvatkovy_permeat","cmar","mliekarensky_kal"],
 "syraren": ["srvatka_sladka","srvatka_kysla","syrarska_srvatka_tuh","mliekarensky_kal"],
 "bitunok": ["bachorovy_obsah","krv_bitunok","kostny_zvysok","kozne_odrezky","masovy_flotacny_kal"],
 "masovyroba": ["kostny_zvysok","kozne_odrezky","masovy_flotacny_kal"],
 "hydina": ["perie","hydinovy_trus","krv_bitunok","kadavery"],
 "cukrovar": ["repne_rezky","melasa","saturacne_kaly","repna_zemina"],
 "liehovar": ["vypalky","drozdiarske_zvysky"],
 "vinarstvo": ["hroznove_vylisky","vinne_kaly","hroznove_stopky"],
 "pekaren": ["pekarenske_zvysky","cestovinove_zvysky"],
 "cukrovinky": ["cukrovinkarske_zvysky","kavove_slupky"],
 "mlyn": ["psenicne_otruby","mlynske_zmetky","odpad_cistenie_zrna"],
 "olejnin": ["repkovy_srot","slnecnicovy_srot","olejnaty_kal"],
 "praziaren_kavy": ["kavova_sedlina","kavove_slupky"],
 "zeleninarstvo": ["zeleninove_orezky","kal_pranie_zeleniny","vnate_pozberove","zemiakove_supky"],
 "ovocne_sady": ["jablcne_vylisky","bobulove_vylisky","vnate_pozberove"],
 "polnohospodarske_druzstvo": ["slama_obilna","kukuricne_korovie","repkova_slama","travna_hmota_ttp",
                               "hnoj_hovadzi","hnojovica_osipane","odpad_cistenie_zrna","slnecnicove_stonky"],
 "agro": ["slama_obilna","kukuricne_korovie","repkova_slama","odpad_cistenie_zrna","travna_hmota_ttp"],
 "farma": ["hnoj_hovadzi","hnojovica_osipane","ovciarsky_hnoj","travna_hmota_ttp","kadavery"],
 "rybarstvo": ["rybie_zvysky","kal_akvakultura"],
 "technicke_sluzby": ["travna_hmota_kosba","konare_stiepka","listie","bro_zahrady","odpad_trhoviska"],
 "mesto": ["travna_hmota_kosba","konare_stiepka","listie","bro_zahrady","kuchynsky_odpad","odpad_trhoviska"],
 "mestske_lesy": ["lesna_stiepka","kora","odrezky_dreva","konare_stiepka"],
 "kompostaren": ["kompost_nevyhovujuci","bro_zahrady","travna_hmota_kosba"],
 "bioplynova_stanica": ["digestat","kukuricne_korovie","hnojovica_osipane"],
 "odpadove_hospodarstvo": ["kuchynsky_odpad","bro_zahrady","jedle_oleje_pouzite","tuky_odlucovace","potraviny_po_dobe"],
 "pila": ["piliny","kora","odrezky_dreva"],
 "papierne": ["papierensky_kal","vlaknity_vymet","kora"],
 "vodarenska": ["cov_kal_komunalny","tuky_odlucovace"],
 "skrobaren": ["skrobarenske_zvysky","zemiakove_supky"],
}

# sektor podľa kľúčového slova (hrubé zaradenie pre filtre v mape)
SEKTOR = {
 "pivovar":"Potravinárstvo a nápoje","sladovna":"Potravinárstvo a nápoje","mliekaren":"Potravinárstvo a nápoje",
 "syraren":"Potravinárstvo a nápoje","bitunok":"Potravinárstvo a nápoje","masovyroba":"Potravinárstvo a nápoje",
 "cukrovar":"Potravinárstvo a nápoje","liehovar":"Potravinárstvo a nápoje","vinarstvo":"Potravinárstvo a nápoje",
 "pekaren":"Potravinárstvo a nápoje","cukrovinky":"Potravinárstvo a nápoje","mlyn":"Potravinárstvo a nápoje",
 "olejnin":"Potravinárstvo a nápoje","praziaren_kavy":"Potravinárstvo a nápoje",
 "hydina":"Poľnohospodárstvo a chov","zeleninarstvo":"Poľnohospodárstvo a chov","ovocne_sady":"Poľnohospodárstvo a chov",
 "polnohospodarske_druzstvo":"Poľnohospodárstvo a chov","agro":"Poľnohospodárstvo a chov","farma":"Poľnohospodárstvo a chov",
 "rybarstvo":"Drevo, lesníctvo a ostatné",
 "technicke_sluzby":"Komunálny a gastro bioodpad","mesto":"Komunálny a gastro bioodpad",
 "kompostaren":"Komunálny a gastro bioodpad","bioplynova_stanica":"Komunálny a gastro bioodpad",
 "odpadove_hospodarstvo":"Komunálny a gastro bioodpad",
 "mestske_lesy":"Drevo, lesníctvo a ostatné","pila":"Drevo, lesníctvo a ostatné",
 "papierne":"Drevo, lesníctvo a ostatné","vodarenska":"Komunálny a gastro bioodpad",
 "skrobaren":"Potravinárstvo a nápoje",
}

TYP_NAZOV = {
 "pivovar":"Pivovar / minipivovar","sladovna":"Sladovňa","mliekaren":"Mliekáreň","syraren":"Syráreň a bryndziareň",
 "bitunok":"Bitúnok","masovyroba":"Mäsospracovanie","hydina":"Hydinárska prevádzka","cukrovar":"Cukrovar",
 "liehovar":"Liehovar a pálenica","vinarstvo":"Vinárstvo","pekaren":"Pekáreň","cukrovinky":"Výroba cukroviniek",
 "mlyn":"Mlyn","olejnin":"Spracovanie olejnín","praziaren_kavy":"Pražiareň kávy",
 "zeleninarstvo":"Zeleninárstvo","ovocne_sady":"Ovocné sady a spracovanie ovocia",
 "polnohospodarske_druzstvo":"Poľnohospodárske družstvo","agro":"Poľnohospodársky podnik","farma":"Živočíšna farma",
 "rybarstvo":"Rybárstvo a akvakultúra","technicke_sluzby":"Technické služby mesta / obce","mesto":"Mesto - správa zelene",
 "kompostaren":"Kompostáreň","bioplynova_stanica":"Bioplynová stanica","odpadove_hospodarstvo":"Odpadové hospodárstvo",
 "mestske_lesy":"Mestské lesy","pila":"Píla a drevospracovanie",
 "papierne":"Papiereň a celulózka","vodarenska":"Vodárenská spoločnosť (ČOV)",
 "skrobaren":"Škrobáreň",
}

# --- vlna 2: gastro, retail, živočíšne vedľajšie produkty pre technické dráhy ---
ODPADY += [
 ("skolsky_kuchynsky_odpad","Kuchynský odpad zo školských jedální","School canteen food waste","20 01 08","gastro","odpad","celorocne","H,A","Vysoký a predvídateľný objem, pravidelný zvoz, jedno miesto vzniku"),
 ("zvysky_z_taniera","Zvyšky z taniera","Plate waste","20 01 08","gastro","odpad","celorocne","H,A","Zmiešaný materiál vrátane ŽVP; pre krmivá vylúčené, pre technické dráhy použiteľné"),
 ("nemocnicny_kuchynsky_odpad","Kuchynský odpad zo zdravotníckych a sociálnych zariadení","Hospital and care home food waste","20 01 08","gastro","odpad","celorocne","H,A","Celoročná prevádzka bez sezónneho výpadku"),
 ("gastro_kuchynsky_odpad","Kuchynský odpad z reštaurácií a hotelov","Restaurant and hotel food waste","20 01 08","gastro","odpad","celorocne","H,A","Sezónne kolísanie v turistických oblastiach"),
 ("gastro_fritovaci_olej","Použitý fritovací olej z gastroprevádzok","Used frying oil","20 01 25","gastro","odpad","celorocne","F","Priamy vstup do oleochémie a esterifikácie"),
 ("gastro_kavova_sedlina","Kávová sedlina z gastroprevádzok","Spent coffee grounds (catering)","20 01 08","gastro","odpad","celorocne","H,F,E","Oddelene zbierateľná, čistá frakcia"),
 ("retail_ovocie_zelenina","Neupredané ovocie a zelenina z predajní","Retail fruit and vegetable surplus","20 01 08","retail","odpad","celorocne","H,F,A","Bez ŽVP - najlepší retailový tok pre chov hmyzu"),
 ("retail_pecivo","Neupredané pečivo a pekárske výrobky","Retail bakery surplus","02 06 01","retail","vedlajsi_produkt","celorocne","H,F","Bývalé potraviny bez ŽVP; vysoká energetická hustota"),
 ("retail_mliecne","Mliečne výrobky po dátume minimálnej trvanlivosti","Retail dairy surplus","20 01 08","retail","odpad","celorocne","H,F","Mlieko a mliečne výrobky sú pre hmyz prípustné ako ŽVP kat. 3"),
 ("retail_maso_zvysky","Mäsové a údenárske výrobky po dátume spotreby","Retail meat surplus","02 02 03","retail","odpad","celorocne","H,F","ŽVP kat. 3 živočíšneho pôvodu - technická dráha"),
 ("retail_zmesovy","Zmesový potravinový odpad z predajne","Mixed retail food waste","20 01 08","retail","odpad","celorocne","H,A","Netriedený; pre krmivá vylúčený, pre technické dráhy vhodný"),
 ("zvp_kat3","Živočíšne vedľajšie produkty kategórie 3","Category 3 animal by-products","02 02 02","maso","vedlajsi_produkt","celorocne","H,F,E","Vysoký obsah bielkovín a tuku; technologické makronutrienty"),
 ("zvp_kat2","Živočíšne vedľajšie produkty kategórie 2","Category 2 animal by-products","02 02 02","maso","odpad","celorocne","H,A","Tlaková sterilizácia povinná; len technické využitie"),
 ("zvp_kat1","Živočíšne vedľajšie produkty kategórie 1","Category 1 animal by-products","02 01 02","maso","odpad","celorocne","-","Vylúčené zo všetkých dráh okrem spálenia"),
 ("technicky_zivocisny_tuk","Technický živočíšny tuk","Technical animal fat","02 02 03","maso","vedlajsi_produkt","celorocne","F","Vstup do oleochémie; nekonkuruje potravinovému reťazcu"),
 ("masokostna_mucka","Mäsokostná múčka","Meat and bone meal","02 02 02","maso","odpad","celorocne","F","Produkt kafilérie; dráha závisí od kategórie vstupu"),
]

PRODUCENT_ODPAD.update({
 "skola_zakladna": ["skolsky_kuchynsky_odpad","zvysky_z_taniera","gastro_kavova_sedlina","bro_zahrady"],
 "skola_materska": ["skolsky_kuchynsky_odpad","zvysky_z_taniera","bro_zahrady"],
 "skola_stredna": ["skolsky_kuchynsky_odpad","zvysky_z_taniera","gastro_fritovaci_olej","bro_zahrady"],
 "skolska_jedalen": ["skolsky_kuchynsky_odpad","zvysky_z_taniera","gastro_fritovaci_olej"],
 "nemocnica": ["nemocnicny_kuchynsky_odpad","zvysky_z_taniera","gastro_fritovaci_olej"],
 "socialne_zariadenie": ["nemocnicny_kuchynsky_odpad","zvysky_z_taniera","bro_zahrady"],
 "restauracia": ["gastro_kuchynsky_odpad","zvysky_z_taniera","gastro_fritovaci_olej","gastro_kavova_sedlina","tuky_odlucovace"],
 "hotel": ["gastro_kuchynsky_odpad","zvysky_z_taniera","gastro_fritovaci_olej","gastro_kavova_sedlina","bro_zahrady"],
 "retail_druzstvo": ["retail_ovocie_zelenina","retail_pecivo","retail_mliecne","retail_maso_zvysky","retail_zmesovy"],
 "retail_retazec": ["retail_ovocie_zelenina","retail_pecivo","retail_mliecne","retail_maso_zvysky","retail_zmesovy","gastro_fritovaci_olej"],
 "jedalen_zavodna": ["gastro_kuchynsky_odpad","zvysky_z_taniera","gastro_fritovaci_olej","tuky_odlucovace"],
})
PRODUCENT_ODPAD["bitunok"] += ["zvp_kat3","zvp_kat2","zvp_kat1","technicky_zivocisny_tuk"]
PRODUCENT_ODPAD["masovyroba"] += ["zvp_kat3","technicky_zivocisny_tuk","masokostna_mucka"]
PRODUCENT_ODPAD["hydina"] += ["zvp_kat3","zvp_kat2"]

SEKTOR.update({
 "skola_zakladna":"Gastro a stravovacie zariadenia","skola_materska":"Gastro a stravovacie zariadenia",
 "skola_stredna":"Gastro a stravovacie zariadenia","skolska_jedalen":"Gastro a stravovacie zariadenia",
 "nemocnica":"Gastro a stravovacie zariadenia","socialne_zariadenie":"Gastro a stravovacie zariadenia",
 "restauracia":"Gastro a stravovacie zariadenia","hotel":"Gastro a stravovacie zariadenia",
 "retail_druzstvo":"Retail a distribúcia potravín","retail_retazec":"Retail a distribúcia potravín",
 "jedalen_zavodna":"Gastro a stravovacie zariadenia",
})
TYP_NAZOV.update({
 "skola_zakladna":"Základná škola","skola_materska":"Materská škola","skola_stredna":"Stredná škola",
 "skolska_jedalen":"Školská jedáleň","nemocnica":"Nemocnica","socialne_zariadenie":"Zariadenie sociálnych služieb",
 "restauracia":"Reštaurácia","hotel":"Hotel","retail_druzstvo":"Spotrebné družstvo (predajne)",
 "retail_retazec":"Obchodný reťazec","jedalen_zavodna":"Závodná a verejná jedáleň",
})

# ---------------------------------------------------------------------------
# DRÁHY ZHODNOTENIA
# Odpoveď na to, že legislatívne schválené krmivové toky sú len časť možností.
# Materiál vylúčený z krmivového reťazca môže byť plne prípustný pre technické
# makronutrienty - hmyzí tuk do oleochémie, chitín, hydrolyzáty, frass ako hnojivo.
# ---------------------------------------------------------------------------
DRAHY = [
 ("krmivo_hosp","Krmivo pre hospodárske zvieratá","Spracovaná živočíšna bielkovina z hmyzu do krmív pre hydinu a ošípané",
  "nar. (EÚ) 2021/1372, nar. (EÚ) 2017/893"),
 ("krmivo_akva","Krmivo pre akvakultúru","PAP z hmyzu do krmív pre ryby","nar. (EÚ) 2017/893"),
 ("petfood","Krmivo pre spoločenské zvieratá","Hmyzia múčka a tuk do petfoodu","nar. (ES) 1069/2009, nar. (EÚ) 142/2011"),
 ("potravina","Potravina pre ľudí","Celý hmyz a hmyzia múčka ako nová potravina","nar. (EÚ) 2015/2283, únijný zoznam 2017/2470"),
 ("technicky_tuk","Technický tuk a oleochémia","Hmyzí tuk do biopalív, mazív, tenzidov a kozmetiky - mimo potravinového a krmivového reťazca",
  "nar. (ES) 1069/2009 čl. 33 - technické použitie"),
 ("chitin","Chitín a chitozán","Exúvie a kutikula ako surovina pre biopolyméry, obalové fólie a biomedicínu",
  "mimo krmivovej regulácie; REACH podľa aplikácie"),
 ("hydrolyzat","Proteínový hydrolyzát a biostimulátor","Enzymatický hydrolyzát ako biostimulátor rastlín a technická bielkovina",
  "nar. (EÚ) 2019/1009 o hnojivých výrobkoch"),
 ("frass","Frass ako organické hnojivo","Trus a zvyšky substrátu ako hnojivý výrobok","nar. (EÚ) 2021/1925, nar. (EÚ) 2019/1009"),
 ("bioplyn","Anaeróbna digescia","Energetické zhodnotenie tam, kde nutričná dráha nie je prípustná","nar. (ES) 1069/2009 čl. 13"),
]

# regulačná trieda materiálu -> prípustnosť po dráhach
# povolene | podmienene | zakazane | mimo_regulacie
REGULACIA = {
 "rastlinny": dict(krmivo_hosp="povolene", krmivo_akva="povolene", petfood="povolene", potravina="povolene",
   technicky_tuk="povolene", chitin="povolene", hydrolyzat="povolene", frass="povolene", bioplyn="povolene",
   pozn="Materiál rastlinného pôvodu - prípustný substrát pre chov hmyzu vo všetkých dráhach."),
 "mlieko_vajcia": dict(krmivo_hosp="povolene", krmivo_akva="povolene", petfood="povolene", potravina="povolene",
   technicky_tuk="povolene", chitin="povolene", hydrolyzat="povolene", frass="povolene", bioplyn="povolene",
   pozn="Mlieko, mliečne výrobky a vajcia sú výslovne prípustné ŽVP pre chov hmyzu."),
 "byvala_potravina_bez_zvp": dict(krmivo_hosp="povolene", krmivo_akva="povolene", petfood="povolene", potravina="podmienene",
   technicky_tuk="povolene", chitin="povolene", hydrolyzat="povolene", frass="povolene", bioplyn="povolene",
   pozn="Bývalé potraviny bez mäsa a rýb - prípustná kŕmna surovina podľa nar. (EÚ) 68/2013."),
 "byvala_potravina_so_zvp": dict(krmivo_hosp="zakazane", krmivo_akva="zakazane", petfood="podmienene", potravina="zakazane",
   technicky_tuk="povolene", chitin="povolene", hydrolyzat="povolene", frass="podmienene", bioplyn="povolene",
   pozn="Obsahuje mäso alebo ryby. Pre krmivá hospodárskych zvierat vylúčené, pre technické makronutrienty plne použiteľné."),
 "kuchynsky_odpad": dict(krmivo_hosp="zakazane", krmivo_akva="zakazane", petfood="zakazane", potravina="zakazane",
   technicky_tuk="povolene", chitin="povolene", hydrolyzat="povolene", frass="podmienene", bioplyn="povolene",
   pozn="Kuchynský a reštauračný odpad je zakázaným kŕmnym materiálom (nar. (ES) 1069/2009 čl. 11). "
        "Technické dráhy tým dotknuté nie sú - toto je najväčší nevyužitý tok v SR."),
 "zvp_kat3": dict(krmivo_hosp="zakazane", krmivo_akva="zakazane", petfood="podmienene", potravina="zakazane",
   technicky_tuk="povolene", chitin="povolene", hydrolyzat="povolene", frass="podmienene", bioplyn="povolene",
   pozn="ŽVP kat. 3 živočíšneho pôvodu: hmyz kŕmený týmto materiálom nesmie do krmív pre hospodárske zvieratá, "
        "technický tuk, chitín a hydrolyzát sú prípustné."),
 "zvp_kat2": dict(krmivo_hosp="zakazane", krmivo_akva="zakazane", petfood="zakazane", potravina="zakazane",
   technicky_tuk="podmienene", chitin="podmienene", hydrolyzat="podmienene", frass="zakazane", bioplyn="povolene",
   pozn="Tlaková sterilizácia 133 °C/20 min/3 bar povinná. Len technické produkty mimo reťazca."),
 "zvp_kat1": dict(krmivo_hosp="zakazane", krmivo_akva="zakazane", petfood="zakazane", potravina="zakazane",
   technicky_tuk="zakazane", chitin="zakazane", hydrolyzat="zakazane", frass="zakazane", bioplyn="zakazane",
   pozn="Kategória 1 - povinné spálenie alebo spoluspálenie. Zo všetkých dráh vylúčené."),
 "hnoj": dict(krmivo_hosp="zakazane", krmivo_akva="zakazane", petfood="zakazane", potravina="zakazane",
   technicky_tuk="podmienene", chitin="podmienene", hydrolyzat="podmienene", frass="zakazane", bioplyn="povolene",
   pozn="Hnoj a exkrementy sú zakázaným substrátom pre hmyz určený do krmív. Výskum technického využitia prebieha."),
 "kal_cov": dict(krmivo_hosp="zakazane", krmivo_akva="zakazane", petfood="zakazane", potravina="zakazane",
   technicky_tuk="podmienene", chitin="podmienene", hydrolyzat="zakazane", frass="zakazane", bioplyn="povolene",
   pozn="Čistiarenský kal - riziko ťažkých kovov a liečiv. Mimo potravinového aj krmivového reťazca."),
 "lignocelulozny": dict(krmivo_hosp="povolene", krmivo_akva="povolene", petfood="povolene", potravina="podmienene",
   technicky_tuk="povolene", chitin="povolene", hydrolyzat="povolene", frass="povolene", bioplyn="povolene",
   pozn="Rastlinný lignocelulózny materiál - nízka stráviteľnosť, nutná predúprava alebo hubová fermentácia."),
}

# priradenie regulačnej triedy druhom odpadu
TRIEDA = {}
for _o in ODPADY:
    _k, _skup, _kat = _o[0], _o[4], _o[3]
    if _k in ("srvatka_sladka","srvatka_kysla","srvatkovy_permeat","cmar","syrarska_srvatka_tuh","retail_mliecne"):
        TRIEDA[_k] = "mlieko_vajcia"
    elif _k in ("kadavery","zvp_kat1"):
        TRIEDA[_k] = "zvp_kat1"
    elif _k in ("bachorovy_obsah","zvp_kat2","masokostna_mucka"):
        TRIEDA[_k] = "zvp_kat2"
    elif _k in ("krv_bitunok","perie","kostny_zvysok","kozne_odrezky","masovy_flotacny_kal","rybie_zvysky",
                "zvp_kat3","technicky_zivocisny_tuk","retail_maso_zvysky"):
        TRIEDA[_k] = "zvp_kat3"
    elif _k in ("hnoj_hovadzi","hnojovica_osipane","hydinovy_trus","ovciarsky_hnoj"):
        TRIEDA[_k] = "hnoj"
    elif _k in ("cov_kal_komunalny","mliekarensky_kal","kal_akvakultura","papierensky_kal","olejnaty_kal"):
        TRIEDA[_k] = "kal_cov"
    elif _kat.startswith("20 01 08") or _k in ("kuchynsky_odpad","zvysky_z_taniera","retail_zmesovy",
                                               "odpad_trhoviska","potraviny_po_dobe"):
        TRIEDA[_k] = "kuchynsky_odpad"
    elif _k in ("retail_pecivo","pekarenske_zvysky","cestovinove_zvysky","cukrovinkarske_zvysky",
                "retail_ovocie_zelenina","gastro_fritovaci_olej","jedle_oleje_pouzite","tuky_odlucovace"):
        TRIEDA[_k] = "byvala_potravina_bez_zvp"
    elif _k in ("slama_obilna","kukuricne_korovie","repkova_slama","slnecnicove_stonky","hroznove_stopky",
                "kora","piliny","odrezky_dreva","lesna_stiepka","konare_stiepka","vlaknity_vymet","listie"):
        TRIEDA[_k] = "lignocelulozny"
    else:
        TRIEDA[_k] = "rastlinny"
