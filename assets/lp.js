/* Dvojfázový simplexový riešič lineárneho programu.
   Bez závislostí, beží v prehliadači aj v Node.

   solveLP({
     c:            [..],                       // koeficienty účelovej funkcie
     maximize:     true|false,
     constraints:  [{a:[..], op:'<='|'>='|'=', rhs: number, name:'...'}],
     bounds:       [{lo:0, hi:1}, ...]         // voliteľné, na premennú
   })
   -> {status:'optimal'|'infeasible'|'unbounded', x:[..], value:number}

   Používa Blandovo pravidlo, takže necykluje. Pre úlohy rádu desiatok
   premenných a stoviek obmedzení je to viac než dostatočné.                */

(function (root) {
  'use strict';
  var EPS = 1e-9;

  function solveLP(model) {
    var n = model.c.length;
    var cons = [];

    // horné a dolné medze prevedieme na bežné obmedzenia
    (model.bounds || []).forEach(function (b, i) {
      if (!b) return;
      if (b.hi !== undefined && b.hi !== null && isFinite(b.hi)) {
        var a = new Array(n).fill(0); a[i] = 1;
        cons.push({ a: a, op: '<=', rhs: b.hi, name: 'max ' + i });
      }
      if (b.lo) {
        var a2 = new Array(n).fill(0); a2[i] = 1;
        cons.push({ a: a2, op: '>=', rhs: b.lo, name: 'min ' + i });
      }
    });
    model.constraints.forEach(function (r) { cons.push(r); });

    // normalizácia: pravá strana musí byť nezáporná
    var rows = cons.map(function (r) {
      var a = r.a.slice(), rhs = r.rhs, op = r.op;
      if (rhs < 0) {
        a = a.map(function (v) { return -v; });
        rhs = -rhs;
        op = op === '<=' ? '>=' : op === '>=' ? '<=' : '=';
      }
      return { a: a, op: op, rhs: rhs, name: r.name };
    });

    // počty pomocných premenných
    var nSlack = rows.filter(function (r) { return r.op !== '='; }).length;
    var nArt = rows.filter(function (r) { return r.op !== '<='; }).length;
    var total = n + nSlack + nArt;

    var T = [], basis = [], si = 0, ai = 0;
    rows.forEach(function (r) {
      var row = new Array(total + 1).fill(0);
      for (var j = 0; j < n; j++) row[j] = r.a[j];
      if (r.op === '<=') { row[n + si] = 1; basis.push(n + si); si++; }
      else if (r.op === '>=') { row[n + si] = -1; si++; row[n + nSlack + ai] = 1; basis.push(n + nSlack + ai); ai++; }
      else { row[n + nSlack + ai] = 1; basis.push(n + nSlack + ai); ai++; }
      row[total] = r.rhs;
      T.push(row);
    });

    var m = T.length;

    function pivot(col, row) {
      var pv = T[row][col];
      for (var j = 0; j <= total; j++) T[row][j] /= pv;
      for (var i = 0; i < m; i++) {
        if (i === row) continue;
        var f = T[i][col];
        if (Math.abs(f) < EPS) continue;
        for (var j2 = 0; j2 <= total; j2++) T[i][j2] -= f * T[row][j2];
      }
      basis[row] = col;
    }

    // simplex nad danou nákladovou funkciou (minimalizácia)
    function simplex(cost, allowed) {
      for (var guard = 0; guard < 20000; guard++) {
        // redukované ceny  z_j - c_j  cez aktuálnu bázu
        var red = new Array(total).fill(0);
        for (var j = 0; j < total; j++) {
          if (!allowed[j]) { red[j] = 0; continue; }
          var z = 0;
          for (var i = 0; i < m; i++) z += cost[basis[i]] * T[i][j];
          red[j] = cost[j] - z;   // simplex tu vzdy MAXIMALIZUJE
        }
        // Blandovo pravidlo: prvý stĺpec so zlepšením
        var col = -1;
        for (var j3 = 0; j3 < total; j3++) {
          if (allowed[j3] && red[j3] > EPS) { col = j3; break; }
        }
        if (col < 0) return 'optimal';

        var row = -1, best = Infinity;
        for (var i2 = 0; i2 < m; i2++) {
          if (T[i2][col] > EPS) {
            var ratio = T[i2][total] / T[i2][col];
            if (ratio < best - EPS || (Math.abs(ratio - best) < EPS && (row < 0 || basis[i2] < basis[row]))) {
              best = ratio; row = i2;
            }
          }
        }
        if (row < 0) return 'unbounded';
        pivot(col, row);
      }
      return 'optimal';
    }

    // ---- fáza 1: vytlačiť umelé premenné z bázy
    var allowedAll = new Array(total).fill(true);
    if (nArt > 0) {
      var c1 = new Array(total).fill(0);
      for (var k = n + nSlack; k < total; k++) c1[k] = -1;   // min sum(art) == max -sum(art)
      simplex(c1, allowedAll);

      var infeas = 0;
      for (var i3 = 0; i3 < m; i3++) if (basis[i3] >= n + nSlack) infeas += Math.abs(T[i3][total]);
      if (infeas > 1e-7) return { status: 'infeasible', x: null, value: null };

      // umelé premenné, ktoré zostali v báze na nule, vytlačíme
      for (var i4 = 0; i4 < m; i4++) {
        if (basis[i4] >= n + nSlack) {
          for (var j4 = 0; j4 < n + nSlack; j4++) {
            if (Math.abs(T[i4][j4]) > EPS) { pivot(j4, i4); break; }
          }
        }
      }
    }

    // ---- fáza 2
    var allowed2 = new Array(total).fill(true);
    for (var k2 = n + nSlack; k2 < total; k2++) allowed2[k2] = false;   // umelé už nepoužívame

    var c2 = new Array(total).fill(0);
    for (var j5 = 0; j5 < n; j5++) c2[j5] = model.maximize ? model.c[j5] : -model.c[j5];

    var st = simplex(c2, allowed2);
    if (st === 'unbounded') return { status: 'unbounded', x: null, value: null };

    var x = new Array(n).fill(0);
    for (var i5 = 0; i5 < m; i5++) if (basis[i5] < n) x[basis[i5]] = T[i5][total];
    var val = 0;
    for (var j6 = 0; j6 < n; j6++) val += model.c[j6] * x[j6];
    return { status: 'optimal', x: x, value: val };
  }

  var api = { solveLP: solveLP };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.LP = api;
})(typeof window !== 'undefined' ? window : globalThis);
