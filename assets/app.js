/* Aplikačná logika: prehliadanie databázy + optimalizácia substrátovej zmesi. */
(function () {
'use strict';
var D = window.DATA, LPs = window.LP.solveLP;
var $ = function (s) { return document.querySelector(s); };
var el = function (t, c, h) { var e = document.createElement(t); if (c) e.className = c;
  if (h !== undefined) e.innerHTML = h; return e; };
var esc = function (s) { return String(s === null || s === undefined ? '' : s)
  .replace(/[&<>"]/g, function (m) { return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'})[m]; }); };
var num = function (v, d) { return v === null || v === undefined || isNaN(v) ? '—' : Number(v).toFixed(d === undefined ? 1 : d); };

var SRC = {}; D.zdroj.forEach(function (z) { SRC[z.id] = z; });
/* parametre zobrazované v prehľade: kód -> [popis, delitel, desatinne] */
var SHOW = [
  ['CP', 'NL'], ['EE', 'Tuk'], ['NSC', 'Sacharidy'], ['NDF', 'NDF'],
  ['ADF', 'ADF'], ['ADL', 'Lignín'], ['ASH', 'Popol'], ['ME', 'ME']
];
/* hodnota prepočítaná na % sušiny; null = zdroj ju neuvádza alebo sa nedá prepočítať */
function pct(s, kod) { var h = s.hodnoty[kod]; return h && h.pct !== null ? h.pct : null; }

/* ---------------------------------------------------------------- záložky */
document.querySelectorAll('nav button').forEach(function (b) {
  b.addEventListener('click', function () {
    document.querySelectorAll('nav button').forEach(function (x) { x.setAttribute('aria-selected', 'false'); });
    b.setAttribute('aria-selected', 'true');
    ['db', 'calc', 'druhy', 'baf', 'src', 'about'].forEach(function (t) {
      $('#tab-' + t).classList.toggle('hidden', t !== b.dataset.tab);
    });
    window.scrollTo(0, 0);
  });
});

/* ---------------------------------------------------------- 1. DATABÁZA */
var filterCat = null;
var kategorie = [];
D.substrat.forEach(function (s) { if (kategorie.indexOf(s.kategoria) < 0) kategorie.push(s.kategoria); });

function labelKat(k) { return k.replace(/_/g, ' '); }

(function chips() {
  var box = $('#catChips');
  var all = el('button', 'chip', 'všetky'); all.setAttribute('aria-pressed', 'true');
  all.onclick = function () { filterCat = null; syncChips(); renderDb(); };
  box.appendChild(all);
  kategorie.forEach(function (k) {
    var c = el('button', 'chip', esc(labelKat(k)));
    c.setAttribute('aria-pressed', 'false');
    c.onclick = function () { filterCat = k; syncChips(); renderDb(); };
    c.dataset.k = k; box.appendChild(c);
  });
  function syncChips() {
    box.querySelectorAll('.chip').forEach(function (c) {
      c.setAttribute('aria-pressed', String((c.dataset.k || null) === filterCat));
    });
  }
  box._sync = syncChips;
})();

function filtered() {
  var q = ($('#search').value || '').toLowerCase().trim();
  return D.substrat.filter(function (s) {
    if (filterCat && s.kategoria !== filterCat) return false;
    if (q && (s.nazov_sk + ' ' + (s.nazov_en || '')).toLowerCase().indexOf(q) < 0) return false;
    return true;
  });
}

function renderDb() {
  var t = $('#dbTable');
  t.querySelector('thead').innerHTML = '<tr><th>Substrát</th>' +
    SHOW.map(function (p) { return '<th class="num">' + p[1] + '</th>'; }).join('') +
    '<th>Kategória</th></tr>';
  var tb = t.querySelector('tbody'); tb.innerHTML = '';
  var list = filtered();
  list.forEach(function (s) {
    var tr = el('tr');
    tr.appendChild(el('td', 'name', esc(s.nazov_sk) +
      '<br><span style="color:var(--ink-3);font-size:11.5px">' + esc(s.nazov_en || '') + '</span>'));
    SHOW.forEach(function (p) {
      var v = pct(s, p[0]);
      tr.appendChild(el('td', 'num', v === null ? '—' : num(v, 1)));
    });
    tr.appendChild(el('td', '', '<span style="color:var(--ink-2);font-size:12px">' + esc(labelKat(s.kategoria)) + '</span>'));
    tr.onclick = function () {
      tb.querySelectorAll('tr').forEach(function (r) { r.classList.remove('sel'); });
      tr.classList.add('sel'); showDetail(s);
    };
    tb.appendChild(tr);
  });
  $('#dbCount').textContent = 'Zobrazených ' + list.length + ' z ' + D.substrat.length +
    ' substrátov. Hodnoty v % sušiny, ME v MJ/kg sušiny.';
}

function showDetail(s) {
  var d = $('#detail'); d.classList.remove('hidden');
  var rows = Object.keys(s.hodnoty).map(function (k) {
    var h = s.hodnoty[k], z = SRC[h.z];
    var p = D.parameter.filter(function (x) { return x.kod === k; })[0] || {};
    var raw = h.rozpatie ? num(h.lo, 1) + ' – ' + num(h.hi, 1) : num(h.v, 1);
    return '<tr><td>' + esc(p.nazov_sk || k) + (h.rozpatie ? ' <span style="color:var(--ink-3);font-size:11px">rozpätie</span>' : '') + '</td>' +
      '<td class="num">' + raw + '</td><td>' + esc(h.j) + '</td>' +
      '<td class="num">' + (h.pct === null ? '—' : num(h.pct, 1)) + '</td>' +
      '<td>' + esc((h.b || '').replace(/_/g, ' ')) + '</td>' +
      '<td><span class="ev ' + esc(h.d) + '">' + esc(h.d) + '</span></td>' +
      '<td>' + esc(h.t || '') + '</td>' +
      '<td>' + (z.doi ? '<a href="https://doi.org/' + esc(z.doi) + '" target="_blank" rel="noopener">' + esc(z.kod) + '</a>' : esc(z.kod)) + '</td></tr>';
  }).join('');
  d.innerHTML = '<h2>' + esc(s.nazov_sk) + '</h2>' +
    '<p class="hint">' + esc(s.nazov_en || '') + ' · ' + esc(labelKat(s.kategoria)) + '</p>' +
    '<div class="kpi">' +
      kpi('Návrh kat. čísla odpadu', s.katalogove_cislo_navrh || '—') +
      kpi('Overené', s.katalog_overeny ? 'áno' : 'nie') +
      kpi('Prípustný pre hmyz', s.abp_pripustny_hmyz ? 'áno' : 'nie') +
    '</div>' +
    (s.katalog_overeny ? '' : '<div class="note warn">Katalógové číslo odpadu je <strong>návrh</strong> ' +
      'podľa kategórie substrátu, nie overené zaradenie. Pred publikovaním ho musí potvrdiť odborne spôsobilá osoba.</div>') +
    '<div class="note">' + esc(s.abp_dovod || '') + '</div>' +
    '<div class="tablewrap"><table><thead><tr><th>Parameter</th><th class="num">Pôvodná hodnota</th>' +
    '<th>Jednotka</th><th class="num">% sušiny</th><th>Báza</th><th>Dôkaz</th><th>Tabuľka</th>' +
    '<th>Zdroj</th></tr></thead><tbody>' + rows + '</tbody></table></div>' +
    (Object.keys(s.vsetky || {}).length ? '<div class="note">Pri tomto substráte máme hodnoty ' +
      'z viacerých nezávislých zdrojov: ' + Object.keys(s.vsetky).join(', ') +
      '. V tabuľke je zobrazený zdroj s vyššou úrovňou dôkazu.</div>' : '');
  d.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
function mixDoplnok(rows, x) {
  return rows.map(function (rw, i) { return { n: rw.s.nazov_sk, v: x[i], vl: rw.s.vlastna }; })
    .filter(function (m) { return m.v > 1e-6 && !m.vl; })
    .sort(function (a, b) { return b.v - a.v; })
    .map(function (m) { return m.n + ' ' + (m.v * 100).toFixed(1) + ' %'; })
    .join(', ');
}
function kpi(k, v) { return '<div><div class="k">' + esc(k) + '</div><div class="v">' + esc(v) + '</div></div>'; }

$('#search').addEventListener('input', renderDb);
if ($('#expDb')) $('#expDb').onclick = function () {
  var head = ['substrat_sk', 'substrat_en', 'kategoria'].concat(SHOW.map(function (p) { return p[0]; })).concat(['zdroj', 'doi']);
  var lines = [head.join(',')];
  filtered().forEach(function (s) {
    var z = null;
    var r = [s.nazov_sk, s.nazov_en || '', s.kategoria];
    SHOW.forEach(function (p) {
      var h = s.hodnoty[p[0]];
      if (h && !z) z = SRC[h.z];
      r.push(h && h.pct !== null ? h.pct.toFixed(2) : '');
    });
    r.push(z ? z.kod : '', z ? (z.doi || '') : '');
    lines.push(r.map(function (v) { return '"' + String(v).replace(/"/g, '""') + '"'; }).join(','));
  });
  download('substraty.csv', lines.join('\n'));
};
function download(name, text) {
  var a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type: 'text/csv;charset=utf-8' }));
  a.download = name; document.body.appendChild(a); a.click(); a.remove();
}

/* ------------------------------------------------------- 2. KALKULÁTOR */
function druhMaData(d) {
  return D.poziadavka.some(function (r) { return r.druh_id === d.id; }) ||
         D.bioakumulacia.some(function (b) { return b.druh_id === d.id; });
}
D.druh_hmyzu.forEach(function (d) {
  var ok = druhMaData(d);
  var znak = d.status_potravina ? ' · potravina + krmivo' : d.status_krmivo ? ' · krmivo' : ' · bez povolenia';
  var o = el('option', null, esc(d.nazov_vedecky) + znak + (ok ? '' : ' — bez dát'));
  o.value = d.id; if (!ok) o.disabled = true;
  $('#species').appendChild(o);
});
D.draha.forEach(function (p) {
  var o = el('option', null, esc(p.nazov_sk)); o.value = p.kod; $('#pathway').appendChild(o);
});
$('#pathway').value = 'krmivo';

D.bioakumulacia.filter(function (b) { return b.parameter_kod === 'Cd' && b.stadium === 'larva'; })
  .forEach(function (b) {
    var o = el('option', null, b.baf.toFixed(2) + ' — expozícia ' + esc(b.uroven_expozicie) +
      ' (Diener 2015)'); o.value = b.baf; $('#bafCd').appendChild(o);
  });
$('#bafCd').value = Math.max.apply(null, D.bioakumulacia
  .filter(function (b) { return b.parameter_kod === 'Cd' && b.stadium === 'larva'; })
  .map(function (b) { return b.baf; }));

function reqFor(kod, parameter) {
  var druhId = +$('#species').value;
  var vlastne = D.poziadavka.filter(function (r) {
    return r.draha === kod && r.parameter_kod === parameter && r.druh_id === druhId; })[0];
  return vlastne || null;
}
function syncPathway() {
  var kod = $('#pathway').value;
  var p = D.draha.filter(function (x) { return x.kod === kod; })[0];
  var req = reqFor(kod, 'PC');
  var reqCP = reqFor(kod, 'CP'), reqEE = reqFor(kod, 'EE');
  $('#pcMin').value = req ? req.min_hodnota : '';
  $('#pcMax').value = req ? req.max_hodnota : '';
  // Polia sa vzdy prepisu podla zvoleneho druhu a drahy. Bez toho by po prepnuti
  // druhu zostala v poli hodnota predchadzajuceho druhu a vypocet by bol nespravny.
  $('#cpMin').value = reqCP ? reqCP.min_hodnota : '';
  $('#cpMax').value = reqCP ? reqCP.max_hodnota : '';
  var z = req ? SRC[req.zdroj_id] : null;
  var cls = req && req.uroven_dokazu === 'D' ? 'note bad' : 'note';
  $('#pathNote').innerHTML =
    '<div class="' + cls + '"><strong>' + esc(p.nazov_sk) + '</strong> — režim výstupu: ' +
    esc(p.rezim_vystupu) + ' · ' + (p.vyzaduje_abp_substrat
      ? 'platia obmedzenia kŕmenia hmyzu podľa (ES) 1069/2009'
      : 'obmedzenia kŕmenia sa neuvoľňujú automaticky — pozri poznámku') +
    '<br>' + esc(p.poznamka) +
    (req ? '<br><br>Okno C:CP ' + req.min_hodnota + '–' + req.max_hodnota +
      ' · úroveň dôkazu <span class="ev ' + req.uroven_dokazu + '">' + req.uroven_dokazu + '</span> · ' +
      esc(req.poznamka) + (z && z.doi ? ' (' + esc(z.kod) + ')' : '') : '') +
    (reqCP ? '<br>Dusíkaté látky ' + reqCP.min_hodnota + '–' + reqCP.max_hodnota + ' % · ' +
      esc(reqCP.poznamka || '') : '') +
    (reqEE ? '<br>Tuk ' + reqEE.min_hodnota + '–' + reqEE.max_hodnota + ' % · ' +
      esc(reqEE.poznamka || '') : '') +
    (!req && !reqCP ? '<br><br><strong>Pre tento druh a dráhu nemáme v datasete požiadavky.</strong> ' +
      'Obmedzenia si zadajte ručne nižšie.' : '') +
    '</div>';
}
$('#species').addEventListener('change', syncPathway);
$('#pathway').addEventListener('change', syncPathway);
$('#ignoreAbp').addEventListener('change', renderStock);

/* ---- vlastné suroviny: žijú len v pamäti prehliadača, do databázy sa nezapisujú ---- */
var CUSTOM = [];

function urobVlastnu(z) {
  /* Vytvorí objekt s rovnakým tvarom ako substrát z databázy, aby s ním
     zvyšok kalkulátora vedel pracovať bez zmien. */
  var delitel = z.baza === 'ph' && z.dm ? z.dm / 100 : 1;
  var hodnoty = {};
  ['CP', 'NSC', 'EE', 'NDF', 'ADL'].forEach(function (k) {
    if (z[k] === null || z[k] === undefined || z[k] === '') return;
    var v = parseFloat(z[k]); if (isNaN(v)) return;
    var vDM = v / delitel;
    hodnoty[k] = { v: v, pct: vDM, j: z.baza === 'ph' ? '% PH' : '% DM',
                   b: z.baza === 'ph' ? 'povodna_hmota' : 'susina', z: null,
                   t: null, d: 'A', ako: 'zadané používateľom' };
  });
  if (z.dm) hodnoty.DM = { v: z.dm, pct: null, j: '% PH', b: 'povodna_hmota',
                           z: null, t: null, d: 'A', ako: 'zadané používateľom' };
  return { id: 'C' + (CUSTOM.length + 1), kod: 'VLASTNA' + (CUSTOM.length + 1),
           nazov_sk: z.nazov, nazov_en: '', kategoria: 'vlastna_surovina',
           abp_pripustny_hmyz: null, hodnoty: hodnoty, vsetky: {}, vlastna: true };
}

/* tabuľka dostupných surovín */
var STOCK = D.substrat.map(function (s) {
  return { s: s, use: true, max: 100, price: '', cd: '', secondary: true };
});

function prestavStock() {
  var stav = {};
  STOCK.forEach(function (r) { stav[r.s.kod] = r; });
  STOCK = D.substrat.map(function (s) {
    return stav[s.kod] || { s: s, use: true, max: 100, price: '', cd: '', secondary: true };
  }).concat(CUSTOM.map(function (s) {
    return stav[s.kod] || { s: s, use: true, max: 100, price: '',
                            cd: s._cd || '', secondary: false };
  }));
  renderStock();
  $('#customNote').innerHTML = CUSTOM.length
    ? '<div class="note ok">Pridané vlastné suroviny: <strong>' +
      CUSTOM.map(function (c) { return esc(c.nazov_sk); }).join(', ') + '</strong>. ' +
      'Nájdete ich dole v zozname surovín. Ak chcete zistiť, koľko vašej suroviny sa dá ' +
      'využiť a čím ju dobalancovať, prepnite cieľ optimalizácie na ' +
      '<strong>„Dobalancovať vlastnú surovinu"</strong>.</div>'
    : '';
}

$('#addCustom').onclick = function () {
  var nazov = ($('#cName').value || '').trim();
  if (!nazov) { alert('Zadajte názov suroviny.'); return; }
  var z = { nazov: nazov, dm: parseFloat($('#cDM').value) || null, baza: $('#cBasis').value,
            CP: $('#cCP').value, NSC: $('#cNSC').value, EE: $('#cEE').value,
            NDF: $('#cNDF').value, ADL: $('#cADL').value };
  if (z.baza === 'ph' && !z.dm) {
    alert('Ak sú hodnoty v pôvodnej hmote, musíte zadať sušinu — bez nej sa nedajú ' +
          'porovnať s databázou.'); return;
  }
  if (!z.CP && !z.NSC) {
    alert('Zadajte aspoň dusíkaté látky a stráviteľné sacharidy — bez nich sa pomer ' +
          'C : CP nedá vypočítať.'); return;
  }
  var novy = urobVlastnu(z);
  novy._cd = $('#cCd').value;
  CUSTOM.push(novy);
  ['#cName', '#cDM', '#cCP', '#cNSC', '#cEE', '#cNDF', '#cADL', '#cCd'].forEach(function (id) {
    $(id).value = '';
  });
  prestavStock();
};

$('#clearCustom').onclick = function () { CUSTOM = []; prestavStock(); };

function renderStock() {
  var t = $('#stockTable');
  t.querySelector('thead').innerHTML =
    '<tr><th>Použiť</th><th>Substrát</th><th class="num">NL %</th><th class="num">Sach. %</th>' +
    '<th class="num">NDF %</th><th class="num">ME</th><th class="num">Max %</th>' +
    '<th class="num">Cena €/t</th><th class="num">Cd mg/kg</th><th>Druhotná</th></tr>';
  var tb = t.querySelector('tbody'); tb.innerHTML = '';
  STOCK.forEach(function (r, i) {
    var tr = el('tr');
    var g = function (k) { var v = pct(r.s, k); return v === null ? '—' : num(v, 1); };
    tr.innerHTML =
      '<td><input type="checkbox" data-i="' + i + '" data-k="use"' + (r.use ? ' checked' : '') + '></td>' +
      '<td class="name">' + esc(r.s.nazov_sk) +
        (r.s.vlastna ? ' <span class="badge" style="margin-left:4px">vlastná</span>' : '') +
        (r.s.abp_pripustny_hmyz === 0 ? ' <span class="ev D" title="zakázaný substrát">✕</span>' : '') +
      '</td>' +
      '<td class="num">' + g('CP') + '</td>' +
      '<td class="num">' + g('NSC') + '</td>' +
      '<td class="num">' + g('NDF') + '</td>' +
      '<td class="num">' + g('ME') + '</td>' +
      '<td class="num"><input type="number" style="width:72px" data-i="' + i + '" data-k="max" value="' + r.max + '" min="0" max="100"></td>' +
      '<td class="num"><input type="number" style="width:78px" data-i="' + i + '" data-k="price" value="' + r.price + '" min="0"></td>' +
      '<td class="num"><input type="number" style="width:78px" data-i="' + i + '" data-k="cd" value="' + r.cd + '" min="0" step="0.01"></td>' +
      '<td><input type="checkbox" data-i="' + i + '" data-k="secondary"' + (r.secondary ? ' checked' : '') + '></td>';
    tb.appendChild(tr);
  });
  var zakazanych = STOCK.filter(function (r) { return r.s.abp_pripustny_hmyz === 0; }).length;
  $('#abpNote').innerHTML = zakazanych
    ? '<div class="note">V zozname je ' + zakazanych + ' substrátov označených ✕ — pre chov ' +
      'hmyzu na krmivá a potraviny sú právne neprípustné. Do výpočtu sa nedostanú, kým ' +
      'nezaškrtnete políčko vyššie.</div>' : '';
  tb.querySelectorAll('input').forEach(function (inp) {
    inp.addEventListener('change', function () {
      var r = STOCK[+inp.dataset.i], k = inp.dataset.k;
      r[k] = inp.type === 'checkbox' ? inp.checked : inp.value;
    });
  });
}
$('#selAll').onclick = function () { STOCK.forEach(function (r) { r.use = true; }); renderStock(); };
$('#selNone').onclick = function () { STOCK.forEach(function (r) { r.use = false; }); renderStock(); };

/* --- zostavenie a riešenie úlohy --- */
function val(id) { var v = $(id).value; return v === '' ? null : parseFloat(v); }
var posledneVyradene = [];

function buildModel(skip) {
  skip = skip || {};
  var rows = STOCK.filter(function (r) { return r.use; });

  /* PRÁVNY FILTER — aplikuje sa PRED riešením, nie ako obmedzenie.
     Bez neho optimalizátor navrhne zmes, ktorú nemožno legálne skrmovať. */
  var draha = D.draha.filter(function (x) { return x.kod === $('#pathway').value; })[0];
  var vyradene = [];
  if (draha && draha.vyzaduje_abp_substrat && !$('#ignoreAbp').checked) {
    rows = rows.filter(function (r) {
      if (r.s.abp_pripustny_hmyz === 0) { vyradene.push(r.s.nazov_sk); return false; }
      return true;
    });
  }
  posledneVyradene = vyradene;
  if (!rows.length) return null;
  var g = function (r, k) { var v = pct(r.s, k); return v === null ? 0 : v; };

  var obj = $('#objective').value, c;
  if (obj === 'custom') c = rows.map(function (r) { return r.s.vlastna ? 1 : 0; });
  else if (obj === 'waste') c = rows.map(function (r) { return r.secondary ? 1 : 0; });
  else if (obj === 'energy') c = rows.map(function (r) { return g(r, 'ME'); });
  else c = rows.map(function (r) { return -(parseFloat(r.price) || 0); });

  var cons = [{ a: rows.map(function () { return 1; }), op: '=', rhs: 1, name: 'bilancia' }];

  var pcMin = val('#pcMin'), pcMax = val('#pcMax');
  if (!skip.pc && pcMin !== null) cons.push({ a: rows.map(function (r) { return g(r, 'NSC') - pcMin * g(r, 'CP'); }), op: '>=', rhs: 0, name: 'pomer C:CP – dolná hranica' });
  if (!skip.pc && pcMax !== null) cons.push({ a: rows.map(function (r) { return g(r, 'NSC') - pcMax * g(r, 'CP'); }), op: '<=', rhs: 0, name: 'pomer C:CP – horná hranica' });

  var cpMin = val('#cpMin'), cpMax = val('#cpMax');
  if (!skip.cp && cpMin !== null) cons.push({ a: rows.map(function (r) { return g(r, 'CP'); }), op: '>=', rhs: cpMin, name: 'dusíkaté látky – minimum' });
  if (!skip.cp && cpMax !== null) cons.push({ a: rows.map(function (r) { return g(r, 'CP'); }), op: '<=', rhs: cpMax, name: 'dusíkaté látky – maximum' });

  var ndfMax = val('#ndfMax'), adlMax = val('#adlMax');
  if (!skip.fib && ndfMax !== null) cons.push({ a: rows.map(function (r) { return g(r, 'NDF'); }), op: '<=', rhs: ndfMax, name: 'NDF – maximum' });
  if (!skip.fib && adlMax !== null) cons.push({ a: rows.map(function (r) { return g(r, 'ADL'); }), op: '<=', rhs: adlMax, name: 'lignín – maximum' });

  var cdLimit = val('#cdLimit'), baf = parseFloat($('#bafCd').value);
  var anyCd = rows.some(function (r) { return r.cd !== '' && r.cd !== null; });
  if (!skip.cd && cdLimit !== null && anyCd) {
    cons.push({ a: rows.map(function (r) { return baf * (parseFloat(r.cd) || 0); }), op: '<=', rhs: cdLimit, name: 'kadmium v larve (po bioakumulácii)' });
  }

  var bounds = rows.map(function (r) {
    var m = parseFloat(r.max); if (isNaN(m)) m = 100;
    return { lo: 0, hi: Math.max(0, Math.min(100, m)) / 100 };
  });
  return { rows: rows, model: { c: c, maximize: obj !== 'cost', constraints: cons, bounds: bounds },
           anyCd: anyCd, cdActive: !skip.cd && cdLimit !== null && anyCd };
}

function diagnose() {
  var groups = [
    ['pc', 'okno pomeru C : CP'],
    ['cp', 'rozsah dusíkatých látok'],
    ['fib', 'limity NDF alebo lignínu'],
    ['cd', 'limit kadmia v larve']
  ];
  var culprits = [];
  groups.forEach(function (grp) {
    var skip = {}; skip[grp[0]] = true;
    var b = buildModel(skip);
    if (b && LPs(b.model).status === 'optimal') culprits.push(grp[1]);
  });
  if (culprits.length) return 'Riešenie neexistuje. Postačí uvoľniť: <strong>' + culprits.join('</strong> alebo <strong>') + '</strong>.';
  var all = buildModel({ pc: 1, cp: 1, fib: 1, cd: 1 });
  if (all && LPs(all.model).status === 'optimal')
    return 'Riešenie neexistuje a nestačí uvoľniť jedno obmedzenie — bráni tomu ich kombinácia. ' +
           'Skúste uvoľniť dve naraz, alebo pridať surovinu s iným profilom.';
  return 'Riešenie neexistuje ani bez nutričných obmedzení — dostupné suroviny a ich horné limity ' +
         'nedovolia zostaviť zmes na 100 %. Zvýšte „Max %“ alebo pridajte ďalšie suroviny.';
}

$('#run').onclick = function () {
  var b = buildModel();
  var out = $('#result');
  if (!b) { out.innerHTML = '<div class="note bad">Nie je označená ani jedna surovina.</div>'; return; }
  if ($('#objective').value === 'custom' && !b.rows.some(function (rw) { return rw.s.vlastna; })) {
    out.innerHTML = '<div class="note warn">Cieľ „Dobalancovať vlastnú surovinu“ je zvolený, ' +
      'ale žiadna vlastná surovina nie je pridaná a označená. Pridajte ju v paneli vyššie.</div>';
    return;
  }
  var pravna = posledneVyradene.length
    ? '<div class="note warn"><strong>Právny filter vyradil ' + posledneVyradene.length +
      ' substrátov</strong> ešte pred výpočtom, pretože sa nimi hmyz podľa (ES) 1069/2009 ' +
      'kŕmiť nesmie: ' + posledneVyradene.map(esc).join(', ') + '.</div>'
    : ($('#ignoreAbp').checked
      ? '<div class="note bad"><strong>Právny filter je vypnutý.</strong> Zmes môže ' +
        'obsahovať substráty zakázané pre chov hmyzu a nesmie sa použiť v produkcii ' +
        'krmív ani potravín.</div>' : '');
  var r = LPs(b.model);
  if (r.status !== 'optimal') {
    out.innerHTML = pravna + '<div class="note bad">' + diagnose() + '</div>';
    return;
  }
  var rows = b.rows, x = r.x;
  var g = function (i, k) { var v = pct(rows[i].s, k); return v === null ? 0 : v; };
  var agg = function (k) { return x.reduce(function (s, v, i) { return s + v * g(i, k); }, 0); };
  var CP = agg('CP'), NSC = agg('NSC'), NDF = agg('NDF'), ADF = agg('ADF'),
      ADL = agg('ADL'), EE = agg('EE'), ME = agg('ME');
  var waste = x.reduce(function (s, v, i) { return s + (rows[i].secondary ? v : 0); }, 0);
  var price = x.reduce(function (s, v, i) { return s + v * (parseFloat(rows[i].price) || 0); }, 0);
  var cdSub = x.reduce(function (s, v, i) { return s + v * (parseFloat(rows[i].cd) || 0); }, 0);
  var cdLarva = cdSub * parseFloat($('#bafCd').value);
  var cdLimit = val('#cdLimit');

  var mix = rows.map(function (rw, i) { return { n: rw.s.nazov_sk, v: x[i], sec: rw.secondary,
                                                 vl: rw.s.vlastna }; })
    .filter(function (m) { return m.v > 1e-6; }).sort(function (a, c) { return c.v - a.v; });

  var vlastnePodiel = x.reduce(function (s2_, v, i) { return s2_ + (rows[i].s.vlastna ? v : 0); }, 0);
  var maVlastne = rows.some(function (rw) { return rw.s.vlastna; });

  var html = pravna + '<div class="note ok" style="margin-top:16px"><strong>Zmes nájdená.</strong> ' +
    'Zmes spĺňa všetky zadané obmedzenia' +
    (posledneVyradene.length ? ' aj právny filter' : '') + '.</div>';

  if (maVlastne) {
    var doplnok = mixDoplnok(rows, x);
    html += vlastnePodiel > 1e-6
      ? '<div class="note"><strong>Z vašej suroviny sa dá využiť ' +
        (vlastnePodiel * 100).toFixed(1) + ' % zmesi.</strong> ' +
        (doplnok.length ? 'Dobalancovať ju treba týmto: ' + doplnok + '.'
                        : 'Zvyšok zmesi netvorí nič ďalšie.') + '</div>'
      : '<div class="note warn"><strong>Vaša surovina sa do zmesi nedostala.</strong> ' +
        'Pri zadaných obmedzeniach ju optimalizátor nepotrebuje. Skúste prepnúť cieľ na ' +
        '„Dobalancovať vlastnú surovinu", alebo znížiť „Max %“ pri ostatných surovinách.</div>';
  }
  html += '<div class="kpi">' +
    kpi('Podiel druhotných', (waste * 100).toFixed(1) + ' %') +
    (maVlastne ? kpi('Podiel vlastnej', (vlastnePodiel * 100).toFixed(1) + ' %') : '') +
    kpi('Pomer C : CP', CP > 0 ? '1 : ' + (NSC / CP).toFixed(2) : '—') +
    kpi('Dusíkaté látky', CP.toFixed(1) + ' %') +
    kpi('NDF', NDF.toFixed(1) + ' %') +
    kpi('ME', ME.toFixed(2) + ' MJ/kg') +
    ($('#objective').value === 'cost' ? kpi('Cena', price.toFixed(2) + ' €/t') : '') +
    '</div>';

  html += '<div class="tablewrap"><table><thead><tr><th>Surovina</th><th class="num">Podiel</th>' +
    '<th style="width:180px">&nbsp;</th><th>Typ</th></tr></thead><tbody>' +
    mix.map(function (m) {
      return '<tr><td class="name">' + esc(m.n) + '</td><td class="num">' + (m.v * 100).toFixed(1) + ' %</td>' +
        '<td><div class="bar"><i style="width:' + (m.v * 100).toFixed(1) + '%"></i></div></td>' +
        '<td style="font-size:12px;color:var(--ink-2)">' +
        (m.vl ? 'vlastná surovina' : m.sec ? 'druhotná surovina' : 'nakupovaná') + '</td></tr>';
    }).join('') + '</tbody></table></div>';

  html += '<div class="tablewrap" style="margin-top:16px"><table><thead><tr><th>Vypočítané zloženie zmesi</th>' +
    '<th class="num">Hodnota</th><th>Jednotka</th></tr></thead><tbody>' +
    [['Dusíkaté látky', CP, '% sušiny'], ['Tuk', EE, '% sušiny'],
     ['Neštruktúrové sacharidy', NSC, '% sušiny'], ['NDF', NDF, '% sušiny'],
     ['ADF', ADF, '% sušiny'], ['Lignín (ADL)', ADL, '% sušiny'],
     ['Hemicelulóza (NDF−ADF)', NDF - ADF, '% sušiny'],
     ['Celulóza (ADF−ADL)', ADF - ADL, '% sušiny'],
     ['Metabolizovateľná energia', ME, 'MJ/kg sušiny']]
    .map(function (r2) { return '<tr><td>' + r2[0] + '</td><td class="num">' + num(r2[1], 2) + '</td><td>' + r2[2] + '</td></tr>'; })
    .join('') + '</tbody></table></div>';

  if (b.cdActive) {
    var okCd = cdLimit === null || cdLarva <= cdLimit + 1e-9;
    html += '<div class="note ' + (okCd ? 'ok' : 'bad') + '">Kadmium v substráte ' + cdSub.toFixed(3) +
      ' mg/kg → po bioakumulácii (BAF ' + parseFloat($('#bafCd').value).toFixed(2) + ') <strong>' +
      cdLarva.toFixed(3) + ' mg/kg v larve</strong>' +
      (cdLimit !== null ? ' pri limite ' + cdLimit + ' mg/kg.' : '.') + '</div>';
  } else {
    html += '<div class="note warn"><strong>Bezpečnostné obmedzenie nebolo uplatnené.</strong> ' +
      'Dataset neobsahuje obsah kadmia v jednotlivých substrátoch. Výsledok hovorí o nutričnej ' +
      'vhodnosti zmesi, nie o jej bezpečnosti pre potravinovú alebo krmivovú dráhu.</div>';
  }

  html += '<div class="note">Lineárny program môže mať viac rovnako dobrých riešení. Ak potrebujete ' +
    'konkrétnu surovinu v zmesi udržať alebo vylúčiť, upravte jej „Max %“ a prepočítajte.</div>';
  html += '<p class="hint">Výsledok sa dá stiahnuť ako CSV.</p>';
  out.innerHTML = html;

  if (false) $('#expMix').onclick = function () {
    var lines = ['surovina,podiel_pct,druhotna'];
    mix.forEach(function (m) { lines.push('"' + m.n.replace(/"/g, '""') + '",' + (m.v * 100).toFixed(2) + ',' + (m.sec ? 1 : 0)); });
    lines.push('');
    lines.push('parameter,hodnota,jednotka');
    lines.push('CP,' + CP.toFixed(2) + ',% susiny');
    lines.push('EE,' + EE.toFixed(2) + ',% susiny');
    lines.push('NSC,' + NSC.toFixed(2) + ',% susiny');
    lines.push('NDF,' + NDF.toFixed(2) + ',% susiny');
    lines.push('ADL,' + ADL.toFixed(2) + ',% susiny');
    lines.push('ME,' + ME.toFixed(2) + ',MJ/kg susiny');
    lines.push('C_CP,' + (CP > 0 ? (NSC / CP).toFixed(3) : ''), '');
    download('davka.csv', lines.join('\n'));
  };
};

/* --------------------------------------------- 3. DRUHY A VÝKONNOSŤ */
(function () {
  function tab(sel, head, rows) {
    var t = $(sel);
    t.querySelector('thead').innerHTML = '<tr>' + head + '</tr>';
    t.querySelector('tbody').innerHTML = rows.join('');
  }
  function ano(v, txt) {
    return v ? '<span style="color:var(--ok);font-weight:600">' + txt + '</span>'
             : '<span style="color:var(--ink-3)">nie</span>';
  }

  tab('#druhyTable',
    '<th>Vedecký názov</th><th>Slovensky</th><th>Krmivo</th><th>Potravina</th>' +
    '<th>Predpis — krmivo</th><th>Predpis — potravina</th><th class="num">N × faktor</th>',
    D.druh_hmyzu.map(function (d) {
      return '<tr><td class="name"><em>' + esc(d.nazov_vedecky) + '</em></td><td>' + esc(d.nazov_sk || '') + '</td>' +
        '<td>' + ano(d.status_krmivo, 'áno') + '</td><td>' + ano(d.status_potravina, 'áno') + '</td>' +
        '<td>' + esc(d.predpis_krmivo || '—') + '</td><td>' + esc(d.predpis_potravina || '—') + '</td>' +
        '<td class="num">' + d.prepocet_n.toFixed(2) + '</td></tr>';
    }));

  tab('#reqTable',
    '<th>Druh</th><th>Dráha</th><th>Parameter</th><th class="num">Min</th><th class="num">Max</th>' +
    '<th>Jednotka</th><th>Dôkaz</th><th>Zdroj</th><th>Poznámka</th>',
    D.poziadavka.map(function (r) {
      var z = SRC[r.zdroj_id];
      return '<tr><td class="name"><em>' + esc(r.nazov_vedecky) + '</em></td><td>' + esc(r.draha) + '</td>' +
        '<td>' + esc(r.parameter_kod) + '</td><td class="num">' + num(r.min_hodnota, 2) + '</td>' +
        '<td class="num">' + num(r.max_hodnota, 2) + '</td><td>' + esc(r.jednotka || '') + '</td>' +
        '<td><span class="ev ' + esc(r.uroven_dokazu) + '">' + esc(r.uroven_dokazu) + '</span></td>' +
        '<td>' + (z.doi ? '<a href="https://doi.org/' + esc(z.doi) + '" target="_blank" rel="noopener">' + esc(z.kod) + '</a>' : esc(z.kod)) + '</td>' +
        '<td class="name" style="max-width:340px;font-size:12px;color:var(--ink-2)">' + esc(r.poznamka || '') + '</td></tr>';
    }));

  tab('#larvyTable',
    '<th>Druh</th><th>Substrát</th><th>Parameter</th><th class="num">Hodnota</th>' +
    '<th>Dôkaz</th><th>Zdroj</th><th>Poznámka</th>',
    D.zlozenie_lariev.map(function (r) {
      var z = SRC[r.zdroj_id];
      var v = r.hodnota_min !== null ? num(r.hodnota_min, 1) + ' – ' + num(r.hodnota_max, 1) : num(r.hodnota, 2);
      var nazov = { CP_LARVA: 'bielkoviny', EE_LARVA: 'tuk', CHITIN_LARVA: 'chitín' }[r.parameter_kod] || r.parameter_kod;
      return '<tr><td class="name"><em>' + esc(r.nazov_vedecky) + '</em></td>' +
        '<td class="name">' + esc(r.substrat_popis) + '</td><td>' + nazov + '</td>' +
        '<td class="num">' + v + ' %</td>' +
        '<td><span class="ev ' + esc(r.uroven_dokazu) + '">' + esc(r.uroven_dokazu) + '</span></td>' +
        '<td>' + (z.doi ? '<a href="https://doi.org/' + esc(z.doi) + '" target="_blank" rel="noopener">' + esc(z.kod) + '</a>' : esc(z.kod)) + '</td>' +
        '<td class="name" style="max-width:300px;font-size:12px;color:var(--ink-2)">' + esc(r.poznamka || '') + '</td></tr>';
    }));

  var UK = { hmotnost_larvy: 'hmotnosť larvy', prezitie: 'prežitie', mortalita: 'mortalita',
             BCR: 'miera biokonverzie', redukcia_odpadu: 'redukcia odpadu', FCR: 'konverzia krmiva',
             ECI: 'efektivita konverzie', vytazok_lariev: 'výťažok lariev',
             konverzia_susiny: 'konverzia sušiny' };
  tab('#perfTable',
    '<th>Druh</th><th>Substrát</th><th>Ukazovateľ</th><th class="num">Hodnota</th><th>Jednotka</th><th>Zdroj</th>',
    D.vykonnost.map(function (r) {
      var z = SRC[r.zdroj_id];
      return '<tr><td class="name"><em>' + esc(r.nazov_vedecky) + '</em></td>' +
        '<td class="name">' + esc(r.substrat_popis) + '</td>' +
        '<td>' + esc(UK[r.ukazovatel] || r.ukazovatel) + '</td>' +
        '<td class="num">' + num(r.hodnota, 2) + '</td><td>' + esc(r.jednotka) + '</td>' +
        '<td>' + (z.doi ? '<a href="https://doi.org/' + esc(z.doi) + '" target="_blank" rel="noopener">' + esc(z.kod) + '</a>' : esc(z.kod)) + '</td></tr>';
    }));
})();

/* ------------------------------------------------------ 4. BIOAKUMULÁCIA */
(function () {
  var t = $('#bafTable');
  t.querySelector('thead').innerHTML = '<tr><th>Kov</th><th>Štádium</th><th>Expozícia</th>' +
    '<th class="num">BAF</th><th class="num">SD</th><th>Zdroj</th></tr>';
  var tb = t.querySelector('tbody');
  D.bioakumulacia.forEach(function (b) {
    var z = SRC[b.zdroj_id];
    tb.insertAdjacentHTML('beforeend', '<tr><td>' + esc(b.parameter_kod) + '</td><td>' +
      esc(b.stadium.replace(/_/g, ' ')) + '</td><td>' + esc(b.uroven_expozicie) + '</td>' +
      '<td class="num"' + (b.baf > 1 ? ' style="color:var(--bad);font-weight:700"' : '') + '>' + b.baf.toFixed(2) + '</td>' +
      '<td class="num">' + (b.baf_sd !== null ? b.baf_sd.toFixed(2) : '—') + '</td>' +
      '<td><a href="https://doi.org/' + esc(z.doi) + '" target="_blank" rel="noopener">' + esc(z.kod) + '</a></td></tr>');
  });

  var t2 = $('#expTable');
  t2.querySelector('thead').innerHTML = '<tr><th>Kov</th><th>Úroveň</th><th>Matrica</th>' +
    '<th class="num">Hodnota</th><th class="num">SD</th><th>Jednotka</th></tr>';
  var tb2 = t2.querySelector('tbody');
  D.expozicia_kov.forEach(function (e) {
    tb2.insertAdjacentHTML('beforeend', '<tr><td>' + esc(e.parameter_kod) + '</td><td>' + esc(e.uroven) +
      '</td><td>' + esc(e.matrica.replace(/_/g, ' ')) + '</td><td class="num">' + num(e.hodnota, 1) +
      '</td><td class="num">' + (e.sd !== null ? num(e.sd, 2) : '—') + '</td><td>' + esc(e.jednotka) + '</td></tr>');
  });
})();

/* ------------------------------------------------------------ 5. ZDROJE */
(function () {
  $('#srcList').innerHTML = D.zdroj.map(function (z) {
    var cls = z.pouzitelnost === 'volne_pouzitelny' ? 'ok' : z.pouzitelnost === 'citovatelny' ? '' : 'warn';
    return '<div class="note ' + cls + '"><strong>' + esc(z.kod) + '</strong> — ' + esc(z.citacia) +
      (z.doi ? '<br>DOI: <a href="https://doi.org/' + esc(z.doi) + '" target="_blank" rel="noopener">' + esc(z.doi) + '</a>' : '') +
      '<br>Licencia: ' + esc(z.licencia || '—') + ' · režim: ' + esc(z.pouzitelnost.replace(/_/g, ' ')) +
      '<br><span style="color:var(--ink-2)">Overenie: ' + esc(z.overenie) + '</span>' +
      (z.poznamka ? '<br><span style="color:var(--ink-2)">' + esc(z.poznamka) + '</span>' : '') + '</div>';
  }).join('');
})();

/* ------------------------------------------------------ 6. O DATABÁZE */
(function () {
  var nVal = D.substrat.reduce(function (s, x) { return s + Object.keys(x.hodnoty).length; }, 0);
  $('#aboutBody').innerHTML =
    '<div class="kpi">' + kpi('Substrátov', D.substrat.length) + kpi('Nameraných hodnôt', nVal) +
    kpi('Bioakum. faktorov', D.bioakumulacia.length) + kpi('Zdrojov', D.zdroj.length) +
    kpi('Produktových dráh', D.draha.length) + '</div>' +
    '<p>Databáza spája voľne dostupné vedecké zdroje do relačnej štruktúry, v ktorej ' +
    '<strong>každá jednotlivá hodnota nesie odkaz na svoj zdroj, tabuľku a úroveň dôkazu</strong>. ' +
    'Prázdne miesta sú zámerné a označené — nedopĺňali sa odhadom.</p>' +
    '<h2 style="margin-top:18px">Kde sú diery</h2>' +
    '<p class="hint">Chýbajú aminokyseliny, mastné kyseliny, minerály okrem Cd, Pb a Zn, mykotoxíny ' +
    'a mikrobiologické ukazovatele. Sušina a popol nie sú v zdrojovej tabuľke uvedené; popol je ' +
    'dopočítateľný z organickej hmoty, ale ide o odvodenú, nie meranú hodnotu.</p>' +
    '<h2 style="margin-top:18px">Ako čítať úroveň dôkazu</h2>' +
    '<p class="hint"><span class="ev A">A</span> vlastná akreditovaná analýza · ' +
    '<span class="ev B">B</span> recenzovaná publikácia s uvedenou metódou · ' +
    '<span class="ev C">C</span> publikácia bez metódy alebo neoverený prepis · ' +
    '<span class="ev D">D</span> odborný odhad, nie meranie</p>' +
    '<h2 style="margin-top:18px">Upozornenie</h2>' +
    '<p class="hint">Katalógové čísla odpadu sú návrh podľa kategórie substrátu, nie overené zaradenie. ' +
    'Prípustnosť pre chov hmyzu je právny výklad, nie rozhodnutie orgánu. Pred prevádzkovým použitím ' +
    'si vyžiadajte stanovisko ŠVPS SR.</p>';
})();

/* -------------------------------------------------------------- init */
$('#ver').textContent = 'v' + D.verzia;
$('#verFoot').textContent = D.verzia;
$('#updated').textContent = document.lastModified.split(' ')[0];
renderDb(); prestavStock(); syncPathway();
})();

