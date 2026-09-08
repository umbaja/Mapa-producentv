/* Kalkulačka energetickej náročnosti, nákladov a uhlíkovej stopy chovu hmyzu.
   Model je totožný s build/model_d32.py — výstup D3.2 projektu APETBIO.
   Bez závislostí. */
(function () {
"use strict";

/* Klimatický normál 1991–2020, stanica Hurbanovo. */
var T_MES = [0.1, 1.8, 6.1, 12.0, 16.6, 20.3, 22.0, 21.4, 16.1, 10.8, 5.9, 1.0];
var DNI   = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

var POLIA = ["larvy","susinaL","vlhkostP","plocha","vyska","uhod","obalF","vymeny",
  "tin","rekup","meta","osvW","osvH","techKw","techH","susKwh","substratPomer",
  "dopravaKm","dopravaEf","cop","ucinnost","cenaEl","cenaPlyn","efEl","efPlyn",
  "fvKwp","fvVynos","fvPodiel","cenaFv","efFv","znzVykon","znzUcinnost","cenaZnz","efZnz"];

function $(s){return document.querySelector(s);}
function v(id){var e=$("#"+id); return e ? parseFloat(e.value) : NaN;}

function citaj(){
  var p = {};
  POLIA.forEach(function(k){ p[k] = v(k); });
  p.susit = $("#susit").checked;
  p.zdroj = $("#zdroj").value;
  p.dTposun = v("dTposun") || 0;
  p.fvAktivna = $("#fvAktivna").checked;
  p.znzAktivne = $("#znzAktivne").checked;
  return p;
}

function bilancia(p){
  var larvyKg = p.larvy * 1000;
  var susinaKg = larvyKg * p.susinaL / 100;
  var produktKg, vodaKg;
  if (p.susit) { produktKg = susinaKg / (1 - p.vlhkostP/100); vodaKg = larvyKg - produktKg; }
  else { produktKg = larvyKg; vodaKg = 0; }

  var obal = p.plocha * p.obalF;
  var prietok = p.plocha * p.vyska * p.vymeny;
  var ucinRek = 1 - p.rekup/100;

  var teploMesiac = [];
  for (var m = 0; m < 12; m++) {
    var dT = p.tin - (T_MES[m] + p.dTposun);
    var qNet = 0;
    if (dT > 0) {
      var qObal = p.uhod * obal * dT;
      var qVetr = 0.34 * prietok * dT * ucinRek;
      var qMeta = p.meta * p.plocha;
      qNet = Math.max(0, qObal + qVetr - qMeta);
    }
    teploMesiac.push(qNet * DNI[m] * 24 / 1000);
  }
  var teplo = teploMesiac.reduce(function(a,b){return a+b;}, 0);

  /* zvyškové teplo zo splyňovacej stanice: nepretržitý výkon, kryje časť mesačnej potreby */
  var teploZnz = 0, teploZvysok = teplo;
  if (p.znzAktivne) {
    teploZnz = 0; teploZvysok = 0;
    for (var m2 = 0; m2 < 12; m2++) {
      var dostupne = p.znzVykon * (p.znzUcinnost/100) * DNI[m2] * 24;
      var kryte = Math.min(teploMesiac[m2], dostupne);
      teploZnz += kryte;
      teploZvysok += teploMesiac[m2] - kryte;
    }
  }

  var kurEl = 0, kurPlyn = 0;
  if (p.zdroj === "tepelne_cerpadlo") kurEl = teploZvysok / p.cop;
  else if (p.zdroj === "plyn") kurPlyn = teploZvysok / p.ucinnost;
  else kurEl = teploZvysok;

  var osv = p.osvW * p.plocha / 1000 * p.osvH * 365;
  var tech = p.techKw * p.techH * 365;
  var sus = vodaKg * p.susKwh;

  var el = kurEl + osv + tech + sus;
  var plyn = kurPlyn;
  var dopravaCo2 = p.larvy * p.substratPomer * p.dopravaKm * p.dopravaEf;

  /* fotovoltaika: kryje elektrickú spotrebu vcelku, nie je viazaná na konkrétnu záťaž */
  var fvVyroba = 0, fvVlastna = 0;
  if (p.fvAktivna) {
    fvVyroba = p.fvKwp * p.fvVynos;
    fvVlastna = Math.min(fvVyroba * (p.fvPodiel/100), el);
  }
  var elSiet = el - fvVlastna;
  var efBlend = el > 0 ? (elSiet*p.efEl + fvVlastna*p.efFv) / el : p.efEl;
  var cenaBlend = el > 0 ? (elSiet*p.cenaEl + fvVlastna*p.cenaFv) / el : p.cenaEl;

  var naklady = el * cenaBlend + plyn * p.cenaPlyn + teploZnz * p.cenaZnz;
  var emisie = el * efBlend + plyn * p.efPlyn + teploZnz * p.efZnz + dopravaCo2;

  return {
    produktKg: produktKg, vodaKg: vodaKg, teplo: teplo,
    energia: el + plyn + teploZnz, el: el, plyn: plyn,
    teploZnz: teploZnz, fvVyroba: fvVyroba, fvVlastna: fvVlastna,
    kwhKg: (el + plyn + teploZnz) / produktKg,
    eurKg: naklady / produktKg,
    co2Kg: emisie / produktKg,
    nakladyRok: naklady, emisieRok: emisie,
    energiaZ: {"kúrenie (nákup)": kurEl + kurPlyn, "zvyškové teplo": teploZnz,
               "sušenie": sus, "technológia": tech, "osvetlenie": osv},
    emisieZ: {"kúrenie (nákup)": kurEl*efBlend + kurPlyn*p.efPlyn, "zvyškové teplo": teploZnz*p.efZnz,
              "sušenie": sus*efBlend, "technológia": tech*efBlend, "osvetlenie": osv*efBlend,
              "doprava": dopravaCo2}
  };
}

/* --- scenáre: každý je zmena oproti aktuálnemu zadaniu --- */
var SCENARE = [
  ["K1","Cenový šok: elektrina 0,35 €/kWh", {cenaEl:0.35}],
  ["K2","Cenový šok: elektrina 0,50 €/kWh", {cenaEl:0.50}],
  ["K3","Chladná zima: teploty o 3 K nižšie", {dTposun:-3}],
  ["O1","Tepelné čerpadlo", {zdroj:"tepelne_cerpadlo"}],
  ["O2","Plynový kotol", {zdroj:"plyn"}],
  ["O3","Rekuperácia tepla 70 %", {rekup:70}],
  ["O4","Zateplenie na U = 0,18", {uhod:0.18}],
  ["O5","Bez sušenia — čerstvé larvy", {susit:false}],
  ["O6","Tepelné čerpadlo + rekuperácia + zateplenie",
        {zdroj:"tepelne_cerpadlo", rekup:70, uhod:0.18}],
  ["D1","Substrát z okruhu 150 km", {dopravaKm:150}],
  ["D2","Substrát z okruhu 10 km", {dopravaKm:10}],
  ["F1","Fotovoltaika 50 kWp", {fvAktivna:true}],
  ["F2","Zvyškové teplo zo splyňovania, 20 kW", {znzAktivne:true}],
  ["F3","FV 50 kWp + zvyškové teplo 20 kW", {fvAktivna:true, znzAktivne:true}]
];

/* referenčné bielkoviny — Oonincx a de Boer 2012, kg CO2e na kg jedlej bielkoviny */
var REFERENCIE = [
  ["Múčiar (táto štúdia, Holandsko)", 14, 14],
  ["Múčiar (Rakúsko, Dreyer a kol. 2021)", 20.4, 20.4],
  ["Mlieko", 24.8, 39.2],
  ["Kuracie mäso", 18.5, 37.4],
  ["Bravčové mäso", 21.1, 54.2],
  ["Hovädzie mäso", 77.3, 175.1]
];

function fmt(x, d){ 
  if (!isFinite(x)) return "—";
  return x.toLocaleString("sk-SK", {minimumFractionDigits:d, maximumFractionDigits:d});
}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){
  return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];});}

function pruh(zlozky, celok){
  var kl = ["seg1","seg2","seg3","seg4","seg5"], h = '<div class="bar">', i = 0;
  Object.keys(zlozky).forEach(function(k){
    var w = 100 * zlozky[k] / celok;
    if (w > 0.05) h += '<i class="' + kl[i % 5] + '" style="width:' + w.toFixed(2) + '%" title="' +
      esc(k) + ' ' + w.toFixed(1) + ' %"></i>';
    i++;
  });
  return h + "</div>";
}
function legenda(zlozky){
  var kl = ["seg1","seg2","seg3","seg4","seg5"], h = '<div class="leg">', i = 0;
  Object.keys(zlozky).forEach(function(k){
    h += '<span><i class="' + kl[i % 5] + '"></i>' + esc(k) + "</span>"; i++;
  });
  return h + "</div>";
}
function tabZloziek(zlozky, celok, jed, des){
  var h = '<table><thead><tr><th>Zložka</th><th class="n">' + jed +
          '</th><th class="n">Podiel</th><th style="width:34%"></th></tr></thead><tbody>';
  var poradie = Object.keys(zlozky).sort(function(a,b){return zlozky[b]-zlozky[a];});
  poradie.forEach(function(k){
    var val = zlozky[k], pct = 100*val/celok;
    h += "<tr><td>" + esc(k) + '</td><td class="n">' + fmt(val, des) +
         '</td><td class="n">' + fmt(pct,1) + ' %</td><td>' +
         '<div class="bar"><i class="seg1" style="width:' + pct.toFixed(1) + '%"></i></div></td></tr>';
  });
  h += '<tr class="hl"><td>Spolu</td><td class="n">' + fmt(celok, des) +
       '</td><td class="n">100,0 %</td><td></td></tr></tbody></table>';
  return h;
}

function prepocitaj(){
  var p = citaj(), z = bilancia(p);

  $("#kpi").innerHTML =
    kpi(fmt(z.kwhKg,2), "kWh / kg produktu", fmt(z.energia,0) + " kWh za rok") +
    kpi(fmt(z.eurKg,2) + " €", "náklady / kg", fmt(z.nakladyRok,0) + " € za rok") +
    kpi(fmt(z.co2Kg,3), "kg CO₂e / kg", fmt(z.emisieRok/1000,1) + " t CO₂e za rok") +
    kpi(fmt(z.produktKg,0), "kg produktu / rok",
        p.susit ? fmt(z.vodaKg,0) + " kg odparenej vody" : "bez sušenia");

  $("#energia").innerHTML = tabZloziek(z.energiaZ, z.energia, "kWh/rok", 0) +
    '<p class="small" style="margin-top:8px">Kúrenie je vo väčšine konfigurácií rozhodujúcou ' +
    'položkou, pretože chov beží pri teplote výrazne nad vonkajšou po celý rok.</p>';
  $("#emisie").innerHTML = tabZloziek(z.emisieZ, z.emisieRok, "kg CO₂e/rok", 0);

  /* scenáre */
  var h = '<table><thead><tr><th>Scenár</th><th class="n">kWh/kg</th><th class="n">€/kg</th>' +
          '<th class="n">kg CO₂e/kg</th><th class="n">Δ emisií</th></tr></thead><tbody>';
  h += '<tr class="hl"><td>Aktuálne zadanie</td><td class="n">' + fmt(z.kwhKg,2) +
       '</td><td class="n">' + fmt(z.eurKg,2) + '</td><td class="n">' + fmt(z.co2Kg,3) +
       '</td><td class="n">—</td></tr>';
  SCENARE.forEach(function(s){
    var q = {}; Object.keys(p).forEach(function(k){ q[k] = p[k]; });
    Object.keys(s[2]).forEach(function(k){ q[k] = s[2][k]; });
    var r = bilancia(q);
    var d = 100 * (r.co2Kg - z.co2Kg) / z.co2Kg;
    h += "<tr><td>" + esc(s[1]) + '</td><td class="n">' + fmt(r.kwhKg,2) +
         '</td><td class="n">' + fmt(r.eurKg,2) + '</td><td class="n">' + fmt(r.co2Kg,3) +
         '</td><td class="n delta ' + (d < -0.5 ? "dn" : (d > 0.5 ? "up" : "")) + '">' +
         (d > 0 ? "+" : "") + fmt(d,1) + " %</td></tr>";
  });
  $("#scenare").innerHTML = h + "</tbody></table>";

  /* porovnanie na kg bielkoviny */
  var podielBielkovin = v("bielkoviny") / 100;
  var co2Bielkovina = z.co2Kg / (podielBielkovin || 1);
  var hh = '<p class="small">Prepočet na kilogram bielkoviny umožňuje porovnanie s inými ' +
    'bielkovinovými zdrojmi. Hodnota pre chov hmyzu je <b>brána – brána</b>: nezahŕňa výrobu ' +
    'substrátu, ktorý je v tomto modeli odpadom bez priradenej záťaže.</p>' +
    '<table><thead><tr><th>Zdroj bielkoviny</th><th class="n">kg CO₂e / kg bielkoviny</th>' +
    '<th style="width:38%"></th></tr></thead><tbody>';
  var maxRef = 175.1;
  hh += '<tr class="hl"><td>Hmyzí produkt — toto zadanie</td><td class="n">' +
        fmt(co2Bielkovina,1) + '</td><td><div class="bar"><i class="seg1" style="width:' +
        (100*co2Bielkovina/maxRef).toFixed(1) + '%"></i></div></td></tr>';
  REFERENCIE.forEach(function(r){
    var stred = (r[1] + r[2]) / 2;
    hh += "<tr><td>" + esc(r[0]) + '</td><td class="n">' +
      (r[1] === r[2] ? fmt(r[1],1) : fmt(r[1],1) + " – " + fmt(r[2],1)) +
      '</td><td><div class="bar"><i class="seg3" style="width:' +
      (100*stred/maxRef).toFixed(1) + '%"></i></div></td></tr>';
  });
  $("#porovnanie").innerHTML = hh + "</tbody></table>";

  /* interpretačná poznámka */
  var pozn = "";
  if (p.zdroj === "plyn")
    pozn = '<div class="note warn"><b>Plyn je lacnejší, ale emisne horší.</b> Emisný faktor ' +
      'slovenskej elektriny je približne 0,095 kg CO₂e/kWh, zemného plynu 0,202 kg CO₂e/kWh. ' +
      'Prechod na plyn preto znižuje náklady a zároveň zvyšuje uhlíkovú stopu — pri vykazovaní ' +
      'podľa CSRD ide o krok opačným smerom.</div>';
  else if (p.zdroj === "tepelne_cerpadlo")
    pozn = '<div class="note ok"><b>Tepelné čerpadlo je pri slovenskom energetickom mixe ' +
      'najsilnejšie opatrenie.</b> Znižuje spotrebu aj emisie v pomere zodpovedajúcom ' +
      'vykurovaciemu faktoru.</div>';
  if (!p.susit)
    pozn += '<div class="note">Sušenie je vypnuté. Výsledok platí pre čerstvé larvy, ktoré majú ' +
      'krátku trvanlivosť a musia sa spracovať alebo skŕmiť bezprostredne.</div>';
  if (p.fvAktivna) {
    var fvPodielSpotreby = z.el > 0 ? 100 * z.fvVlastna / z.el : 0;
    pozn += '<div class="note ok"><b>Fotovoltaika ' + fmt(p.fvKwp,0) + ' kWp</b> vyrobí ' +
      fmt(z.fvVyroba,0) + ' kWh/rok, na mieste sa spotrebuje ' + fmt(z.fvVlastna,0) +
      ' kWh/rok (' + fmt(fvPodielSpotreby,0) + ' % elektrickej spotreby). Zvyšok výroby sa ' +
      'v tomto modeli neoceňuje ani neexportuje.</div>';
  }
  if (p.znzAktivne) {
    var znzPodiel = z.teplo > 0 ? 100 * z.teploZnz / z.teplo : 0;
    pozn += '<div class="note ok"><b>Zvyškové teplo zo splyňovania</b> pokryje ' + fmt(z.teploZnz,0) +
      ' kWh/rok z ' + fmt(z.teplo,0) + ' kWh/rok potreby kúrenia (' + fmt(znzPodiel,0) + ' %). ' +
      'Výkon stanice sa počíta ako rovnomerne dostupný počas mesiaca — v mesiacoch s vysokou ' +
      'potrebou kúrenia (najmä v zime) môže výkon nestačiť a zvyšok pokryje zvolený zdroj tepla.</div>';
  }
  $("#poznamka").innerHTML = pozn;

  window.__vysledok = {p: p, z: z};
}
function kpi(v, k, s){
  return '<div><div class="v">' + v + '</div><div class="k">' + k + '</div>' +
         '<div class="s">' + s + "</div></div>";
}

function exportCSV(){
  var p = window.__vysledok.p, z = window.__vysledok.z;
  var r = [["parameter","hodnota"]];
  Object.keys(p).forEach(function(k){ r.push([k, p[k]]); });
  r.push([]); r.push(["výsledok","hodnota"]);
  r.push(["kWh na kg produktu", z.kwhKg.toFixed(3)]);
  r.push(["EUR na kg produktu", z.eurKg.toFixed(3)]);
  r.push(["kg CO2e na kg produktu", z.co2Kg.toFixed(4)]);
  r.push(["spotreba energie kWh/rok", z.energia.toFixed(0)]);
  r.push(["náklady EUR/rok", z.nakladyRok.toFixed(0)]);
  r.push(["emisie kg CO2e/rok", z.emisieRok.toFixed(0)]);
  r.push([]); r.push(["zložka","kWh/rok"]);
  Object.keys(z.energiaZ).forEach(function(k){ r.push([k, z.energiaZ[k].toFixed(0)]); });
  r.push([]); r.push(["zložka","kg CO2e/rok"]);
  Object.keys(z.emisieZ).forEach(function(k){ r.push([k, z.emisieZ[k].toFixed(0)]); });
  var csv = r.map(function(row){ return row.join(";"); }).join("\n");
  var a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob(["﻿" + csv], {type:"text/csv;charset=utf-8"}));
  a.download = "kpb2_energeticka_bilancia.csv";
  document.body.appendChild(a); a.click(); a.remove();
}

document.addEventListener("input", function(e){
  if (e.target.closest("#vstupy")) prepocitaj();
});
document.addEventListener("change", function(e){
  if (e.target.closest("#vstupy")) prepocitaj();
});
$("#bCSV").addEventListener("click", exportCSV);
$("#bReset").addEventListener("click", function(){
  document.querySelectorAll("#vstupy [data-def]").forEach(function(el){
    if (el.type === "checkbox") el.checked = el.dataset.def === "1";
    else el.value = el.dataset.def;
  });
  prepocitaj();
});
prepocitaj();
})();
