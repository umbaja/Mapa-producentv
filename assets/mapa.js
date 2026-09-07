/* Mapa producentov biotransformovateľných odpadov v SR — KPB2
   Bez závislostí: vlastná SVG projekcia, pan/zoom, filtre, export CSV. */
(function(){
"use strict";
var D = window.MAPA, F = D.polia;
var IX = {}; F.forEach(function(k,i){IX[k]=i;});
var ODP = {}; D.odpady.forEach(function(o){ODP[o.id]=o;});

var SEKTORY = ["Potravinárstvo a nápoje","Poľnohospodárstvo a chov","Gastro a stravovacie zariadenia",
               "Retail a distribúcia potravín","Komunálny a gastro bioodpad","Drevo, lesníctvo a ostatné"];
var SFARBA = {"Potravinárstvo a nápoje":"var(--c1)","Poľnohospodárstvo a chov":"var(--c2)",
              "Gastro a stravovacie zariadenia":"var(--c5)","Retail a distribúcia potravín":"var(--c6)",
              "Komunálny a gastro bioodpad":"var(--c3)","Drevo, lesníctvo a ostatné":"var(--c4)"};
var DR = {}; (D.drahy||[]).forEach(function(d){DR[d.kod]=d;});
var KOEF = {}; (D.koeficienty||[]).forEach(function(k){KOEF[k.typ_prevadzky]=k;});
var PERM = {p:"povolené", c:"podmienené", z:"zakázané", m:"mimo regulácie"};

var state = {sektor:{}, typ:"", odpad:"", kat:"", okres:"", draha:"", pripust:"pc", q:"",
             sel:null, velkost:"objem", choro:"pocet", lenObjem:false};
SEKTORY.forEach(function(s){state.sektor[s]=true;});

/* ---------- projekcia ---------- */
var W=900,H=520,PAD=12, bb=null;
function bbox(){
  var x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
  D.okresy.forEach(function(o){o.r.forEach(function(r){r.forEach(function(p){
    if(p[0]<x0)x0=p[0]; if(p[0]>x1)x1=p[0]; if(p[1]<y0)y0=p[1]; if(p[1]>y1)y1=p[1];});});});
  return [x0,y0,x1,y1];
}
var K=1;
function proj(lon,lat){
  var x=(lon-bb[0])*K, y=(bb[3]-lat)*K/Math.cos(48.7*Math.PI/180);
  return [PAD+x*Math.cos(48.7*Math.PI/180)*1, PAD+y*Math.cos(48.7*Math.PI/180)];
}
function setupProj(){
  bb=bbox();
  var cl=Math.cos(48.7*Math.PI/180);
  var w=(bb[2]-bb[0])*cl, h=(bb[3]-bb[1]);
  K=(W-2*PAD)/w;
  H=Math.round(h*K+2*PAD);
  proj=function(lon,lat){return [PAD+(lon-bb[0])*cl*K, PAD+(bb[3]-lat)*K];};
}

/* ---------- filtre ---------- */
function odpadyOf(p){return p[IX.odpady].map(function(id){return ODP[id];}).filter(Boolean);}
function match(p){
  if(!state.sektor[p[IX.sektor]]) return false;
  if(state.typ && p[IX.typ]!==state.typ) return false;
  if(state.okres && p[IX.okres]!==state.okres) return false;
  if(state.odpad && p[IX.odpady].indexOf(+state.odpad)<0) return false;
  if(state.kat){
    var ok=odpadyOf(p).some(function(o){return o.katalogove_cislo_navrh===state.kat;});
    if(!ok) return false;
  }
  if(state.draha){
    var okd=odpadyOf(p).some(function(o){
      var v=(o.dr||{})[state.draha]; return v && state.pripust.indexOf(v)>=0;});
    if(!okd) return false;
  }
  if(state.lenObjem && !p[IX.odhad]) return false;
  if(state.q){
    var q=state.q.toLowerCase();
    if((p[IX.nazov]+" "+p[IX.obec]+" "+p[IX.okres]+" "+p[IX.ico]).toLowerCase().indexOf(q)<0) return false;
  }
  return true;
}
function filtered(){return D.producenti.filter(match);}

/* ---------- vykreslenie ---------- */
var svg=document.getElementById("map"), gOkr, gPts, tip=document.getElementById("tip");
var view={x:0,y:0,k:1};
function radius(p){
  var base = 3.2/Math.sqrt(view.k);
  if(state.velkost!=="objem") return base;
  var o = p[IX.odhad];
  if(!o) return base*0.62;
  return Math.min(base*4.2, base*(0.85+Math.sqrt(o[1])*0.85));
}
function applyView(){svg.querySelector("#zoomG").setAttribute("transform",
  "translate("+view.x+","+view.y+") scale("+view.k+")");
  gPts.querySelectorAll("circle").forEach(function(c){
    var p=c.__p; c.setAttribute("r", (p?radius(p):3.2/Math.sqrt(view.k)).toFixed(2));});
}
function drawBase(){
  setupProj();
  svg.setAttribute("viewBox","0 0 "+W+" "+H);
  var g=document.createElementNS("http://www.w3.org/2000/svg","g"); g.id="zoomG";
  gOkr=document.createElementNS("http://www.w3.org/2000/svg","g");
  gPts=document.createElementNS("http://www.w3.org/2000/svg","g");
  g.appendChild(gOkr); g.appendChild(gPts); svg.appendChild(g);
  D.okresy.forEach(function(o){
    var d=o.r.map(function(r){
      return "M"+r.map(function(p){var q=proj(p[0],p[1]);return q[0].toFixed(1)+","+q[1].toFixed(1);}).join("L")+"Z";
    }).join("");
    var path=document.createElementNS("http://www.w3.org/2000/svg","path");
    path.setAttribute("d",d); path.setAttribute("class","okres"); path.dataset.okres=o.n;
    path.addEventListener("mousemove",function(e){
      var n=+path.dataset.n||0;
      showTip(e,"<b>"+o.n+"</b><br>"+(state.choro==="objem"
        ? fmt(n)+" t/rok (odhad)" : n+" "+sklon(n)));});
    path.addEventListener("mouseleave",hideTip);
    path.addEventListener("click",function(){
      state.okres = (state.okres===o.n?"":o.n);
      document.getElementById("fOkres").value=state.okres; render();});
    gOkr.appendChild(path);
  });
}
function sklon(n){return n===1?"producent":(n>=2&&n<=4?"producenti":"producentov");}
function shade(n,max){
  if(!n) return "var(--land)";
  var t=Math.pow(n/max,.55);
  return "color-mix(in srgb, var(--accent) "+Math.round(12+t*58)+"%, var(--land))";
}
function render(){
  var rows=filtered();
  /* choropleth */
  var cnt={}; rows.forEach(function(p){
    var v = state.choro==="objem" ? ((p[IX.odhad]||[0,0,0])[1]) : 1;
    cnt[p[IX.okres]]=(cnt[p[IX.okres]]||0)+v;});
  var max=0.0001; for(var k in cnt) if(cnt[k]>max) max=cnt[k];
  gOkr.querySelectorAll("path").forEach(function(path){
    var n=cnt[path.dataset.okres]||0; path.dataset.n=n;
    path.style.fill=shade(n,max);
    path.style.strokeWidth = (state.okres===path.dataset.okres)?1.4:.35;
    path.style.stroke = (state.okres===path.dataset.okres)?"var(--accent)":"var(--land-line)";
  });
  /* body */
  gPts.textContent="";
  rows.forEach(function(p){
    var q=proj(p[IX.lon],p[IX.lat]);
    var c=document.createElementNS("http://www.w3.org/2000/svg","circle");
    c.setAttribute("cx",q[0].toFixed(1)); c.setAttribute("cy",q[1].toFixed(1));
    c.__p=p; c.setAttribute("r",radius(p).toFixed(2));
    c.setAttribute("class","pt"+(state.sel===p[IX.ico]?" sel":""));
    c.setAttribute("fill",SFARBA[p[IX.sektor]]||"var(--muted)");
    c.setAttribute("fill-opacity",".85");
    c.addEventListener("mousemove",function(e){
      var o=p[IX.odhad];
      showTip(e,"<b>"+esc(p[IX.nazov])+"</b><br>"+esc(p[IX.obec])+" · "+esc(p[IX.typ_nazov])+
        (o?"<br><b>"+fmt(o[1])+" t/rok</b> (odhad "+fmt(o[0])+"–"+fmt(o[2])+")":""));});
    c.addEventListener("mouseleave",hideTip);
    c.addEventListener("click",function(e){e.stopPropagation();detail(p);});
    gPts.appendChild(c);
  });
  /* štatistiky */
  var obce={},okr={},od={};
  rows.forEach(function(p){obce[p[IX.obec]]=1;okr[p[IX.okres]]=1;
    p[IX.odpady].forEach(function(i){od[i]=1;});});
  var tsum=0,nsum=0;
  rows.forEach(function(p){var o=p[IX.odhad]; if(o){tsum+=o[1];nsum++;}});
  set("sProd",rows.length); set("sObce",Object.keys(obce).length);
  set("sOkr",Object.keys(okr).length); set("sOdp",Object.keys(od).length);
  set("sObjem",fmt(tsum)); document.getElementById("sObjemPozn").textContent =
    nsum+" z "+rows.length+" prevádzok má odhad";
  var lbl=document.getElementById("drahaInfo");
  if(state.draha && DR[state.draha]){
    var dr=DR[state.draha], np=0, nz=0;
    D.odpady.forEach(function(o){var v=(o.dr||{})[state.draha];
      if(v==="p"||v==="c") np++; else if(v==="z") nz++;});
    lbl.innerHTML="<b>"+esc(dr.nazov)+"</b> — "+np+" druhov odpadu použiteľných, "+nz+
      " zakázaných.<br><span class=\"note\">"+esc(dr.popis)+"<br>Právny rámec: "+esc(dr.pravny_ramec)+"</span>";
    lbl.style.display="block";
  } else lbl.style.display="none";
  var lc=document.getElementById("legChoro");
  if(lc) lc.textContent = state.choro==="objem"
    ? "Sýtosť okresu = odhad objemu (t/rok)" : "Sýtosť okresu = počet producentov vo výbere";
  var lv=document.getElementById("legVel");
  if(lv) lv.textContent = state.velkost==="objem"
    ? "Veľkosť bodu = odhad objemu; malý bod = bez odhadu" : "Veľkosť bodu = rovnaká";
  /* zoznam */
  var list=document.getElementById("list"); list.textContent="";
  var zoz=rows.slice().sort(function(a,b){
    var x=(a[IX.odhad]||[0,0,0])[1], y=(b[IX.odhad]||[0,0,0])[1];
    return y-x || a[IX.nazov].localeCompare(b[IX.nazov],"sk");});
  zoz.slice(0,400).forEach(function(p){
    var r=document.createElement("div"); r.className="row";
    var o=p[IX.odhad];
    r.innerHTML="<span>"+esc(p[IX.nazov])+(o?' <b style="color:var(--accent)">'+fmt(o[1])+' t/rok</b>':"")+
      "</span><small>"+esc(p[IX.obec])+" · okres "+esc(p[IX.okres])+" · "+esc(p[IX.typ_nazov])+"</small>";
    r.addEventListener("click",function(){detail(p);});
    list.appendChild(r);
  });
  document.getElementById("listMore").textContent =
    rows.length>400 ? "Zobrazených prvých 400 z "+rows.length+" záznamov." : "";
  applyView();
}
function set(id,v){document.getElementById(id).textContent=v;}
function fmt(x){ if(x==null) return "—";
  if(x>=100) return Math.round(x).toLocaleString("sk-SK");
  if(x>=10) return x.toFixed(1).replace(".",",");
  return x.toFixed(2).replace(".",","); }
function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){
  return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];});}

/* ---------- detail ---------- */
function detail(p){
  state.sel=p[IX.ico];
  var od=odpadyOf(p);
  var h='<div class="nm">'+esc(p[IX.nazov])+'</div>';
  h+='<div class="meta">IČO '+esc(p[IX.ico])+' · '+esc(p[IX.typ_nazov])+'</div>';
  h+='<table>';
  h+=row("Adresa",[p[IX.ulica],p[IX.psc]?(p[IX.psc]+" "+p[IX.obec]):p[IX.obec]].filter(Boolean).join(", "));
  h+=row("Okres",p[IX.okres]); h+=row("Kraj",p[IX.kraj]);
  h+=row("Sektor",p[IX.sektor]);
  h+=row("Poloha",{obec:"ťažisko obce",mestska_cast:"ťažisko mestskej časti",
    obec_zaklad:"ťažisko základnej obce",okres:"ťažisko okresu",nezistena:"nezistená"}[p[IX.presnost]]||p[IX.presnost]);
  h+='</table>';
  var kp=p[IX.kapacita], oh=p[IX.odhad], kf=KOEF[p[IX.typ]];
  if(oh){
    h+='<h2>Odhad objemu</h2>';
    h+='<div style="font-size:1.5rem;font-weight:600;line-height:1.2">'+fmt(oh[1])+' <span style="font-size:.9rem;font-weight:400;color:var(--muted)">t/rok</span></div>';
    h+='<div class="note" style="margin-bottom:6px">rozpätie '+fmt(oh[0])+' – '+fmt(oh[2])+' t/rok</div>';
    h+='<table>';
    if(kp) h+=row("Kapacita", fmt(kp[0])+" "+kp[1]+" ("+(kp[2]==="merana"?"meraná":"typová")+")");
    if(kf){
      h+=row("Podiel stravníkov", Math.round(kf.podiel_stravnikov*100)+" %");
      h+=row("Jedál za deň", String(kf.jedal_za_den).replace(".",","));
      h+=row("Koeficient", kf.koef_min+" – "+kf.koef_stred+" – "+kf.koef_max+" g");
      h+=row("Dní v roku", kf.dni_rok);
    }
    h+='</table>';
    if(kf) h+='<div class="drmeta"><b>Výpočet:</b> kapacita × podiel stravníkov × jedál za deň × '+
      'koeficient × dní v roku.<br><b>Zdroj koeficientu:</b> '+esc(kf.zdroj)+
      (kf.doi?'<br>DOI: '+esc(kf.doi):'')+'<br><b>Úroveň dôkazu:</b> '+esc(kf.uroven_dokazu)+
      '<br>'+esc(kf.poznamka||"")+'</div>';
    if(kp && kp[2]==="typova") h+='<p class="note">Kapacita je <b>typová</b> — národný priemer na '+
      'zariadenie, nie skutočný počet v tejto prevádzke. Odhad je preto rádový. '+esc(kp[0]?"":"")+'</p>';
  } else {
    h+='<h2>Odhad objemu</h2><p class="note">Pre tento typ prevádzky vrstva objem nekvantifikuje — '+
       'chýba kapacitná veličina (počet stravníkov, lôžok, obrat). Pozri sektorové odhady v dokumentácii.</p>';
  }
  h+='<h2>Očakávané toky odpadu ('+od.length+')</h2><table>';
  od.forEach(function(o){
    h+='<tr><td><b>'+esc(o.nazov_sk)+'</b><br><span class="note">'+esc(o.nazov_en||"")+
       (o.poznamka?" · "+esc(o.poznamka):"")+'</span>'+perms(o)+'</td>'+
       '<td class="kat">'+esc(o.katalogove_cislo_navrh)+'<br>'+esc(o.pravny_status.replace(/_/g," "))+'</td></tr>';
  });
  h+='</table><p class="note">Toky sú odvodené z typu prevádzky (úroveň dôkazu D), nie z ohlásenia '+
     'o vzniku odpadu. Katalógové čísla sú návrh, neoverený odborne spôsobilou osobou. '+
     'Prípustnosť dráh je právny výklad riešiteľského tímu, nie rozhodnutie orgánu.</p>';
  document.getElementById("detail").innerHTML=h;
  render();
}
function row(k,v){return v?'<tr><td class="k">'+esc(k)+'</td><td>'+esc(v)+'</td></tr>':"";}
function perms(o){
  var d=o.dr||{}, h='<div style="margin-top:5px">';
  (D.drahy||[]).forEach(function(dr){
    var v=d[dr.kod]; if(!v) return;
    h+='<span class="perm '+v+'" title="'+esc(dr.nazov+" — "+PERM[v])+'">'+esc(dr.nazov)+'</span>';
  });
  if(d._p) h+='<div class="drmeta">'+esc(d._p)+'</div>';
  return h+'</div>';
}

/* ---------- tooltip / pan-zoom ---------- */
function showTip(e,html){
  tip.innerHTML=html; tip.style.opacity=1;
  var r=svg.parentNode.getBoundingClientRect();
  var x=e.clientX-r.left+12, y=e.clientY-r.top+12;
  if(x+tip.offsetWidth>r.width) x=e.clientX-r.left-tip.offsetWidth-12;
  tip.style.left=x+"px"; tip.style.top=y+"px";
}
function hideTip(){tip.style.opacity=0;}
function initPanZoom(){
  var dragging=false,sx=0,sy=0,ox=0,oy=0;
  svg.addEventListener("pointerdown",function(e){dragging=true;sx=e.clientX;sy=e.clientY;
    ox=view.x;oy=view.y;svg.classList.add("drag");svg.setPointerCapture(e.pointerId);});
  svg.addEventListener("pointermove",function(e){if(!dragging)return;
    var s=W/svg.getBoundingClientRect().width;
    view.x=ox+(e.clientX-sx)*s; view.y=oy+(e.clientY-sy)*s; applyView();});
  svg.addEventListener("pointerup",function(e){dragging=false;svg.classList.remove("drag");});
  svg.addEventListener("wheel",function(e){
    e.preventDefault();
    var r=svg.getBoundingClientRect(), s=W/r.width;
    var mx=(e.clientX-r.left)*s, my=(e.clientY-r.top)*s;
    var f=e.deltaY<0?1.18:1/1.18, nk=Math.max(1,Math.min(14,view.k*f));
    f=nk/view.k;
    view.x=mx-(mx-view.x)*f; view.y=my-(my-view.y)*f; view.k=nk; applyView();
  },{passive:false});
}
function zoomBy(f){var nk=Math.max(1,Math.min(14,view.k*f)),g=nk/view.k;
  view.x=W/2-(W/2-view.x)*g; view.y=H/2-(H/2-view.y)*g; view.k=nk; applyView();}
function resetView(){view={x:0,y:0,k:1};applyView();}

/* ---------- export ---------- */
function exportCSV(){
  var rows=filtered();
  var head=["ico","nazov","ulica","psc","obec","okres","kraj","lat","lon","presnost_polohy",
            "typ_prevadzky","sektor","druh_odpadu","katalogove_cislo_navrh","pravny_status",
            "regulacna_trieda","krmivo_hosp","potravina","technicky_tuk","chitin","hydrolyzat","frass",
            "kapacita","kapacita_jednotka","kapacita_uroven","odhad_t_rok_min","odhad_t_rok_stred","odhad_t_rok_max"];
  var out=[head.join(";")];
  rows.forEach(function(p){
    odpadyOf(p).forEach(function(o){
      out.push([p[IX.ico],p[IX.nazov],p[IX.ulica],p[IX.psc],p[IX.obec],p[IX.okres],p[IX.kraj],
        p[IX.lat],p[IX.lon],p[IX.presnost],p[IX.typ_nazov],p[IX.sektor],
        o.nazov_sk,o.katalogove_cislo_navrh,o.pravny_status,
        (o.dr||{})._t||"",PERM[(o.dr||{}).krmivo_hosp]||"",PERM[(o.dr||{}).potravina]||"",
        PERM[(o.dr||{}).technicky_tuk]||"",PERM[(o.dr||{}).chitin]||"",
        PERM[(o.dr||{}).hydrolyzat]||"",PERM[(o.dr||{}).frass]||"",
        (p[IX.kapacita]||["","",""])[0],(p[IX.kapacita]||["","",""])[1],(p[IX.kapacita]||["","",""])[2],
        (p[IX.odhad]||["","",""])[0],(p[IX.odhad]||["","",""])[1],(p[IX.odhad]||["","",""])[2]]
        .map(function(v){v=String(v==null?"":v);return /[;"\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v;}).join(";"));
    });
  });
  var blob=new Blob(["﻿"+out.join("\n")],{type:"text/csv;charset=utf-8"});
  var a=document.createElement("a");
  a.href=URL.createObjectURL(blob); a.download="kpb2_producenti_filter.csv";
  document.body.appendChild(a); a.click(); a.remove();
}

/* ---------- UI ---------- */
function buildUI(){
  var box=document.getElementById("sektory");
  SEKTORY.forEach(function(s){
    var l=document.createElement("label"); l.className="chk";
    l.innerHTML='<input type="checkbox" checked><span class="dot" style="background:'+SFARBA[s]+'"></span>'+esc(s);
    l.querySelector("input").addEventListener("change",function(e){state.sektor[s]=e.target.checked;render();});
    box.appendChild(l);
  });
  var typy={}; D.producenti.forEach(function(p){typy[p[IX.typ]]=p[IX.typ_nazov];});
  fill("fTyp",Object.keys(typy).sort(function(a,b){return typy[a].localeCompare(typy[b],"sk");})
       .map(function(k){return [k,typy[k]];}),"Všetky typy prevádzok");
  fill("fOdpad",D.odpady.map(function(o){return [o.id,o.nazov_sk+"  ("+o.katalogove_cislo_navrh+")"];}),
       "Všetky druhy odpadu");
  var kats={}; D.odpady.forEach(function(o){kats[o.katalogove_cislo_navrh]=1;});
  fill("fKat",Object.keys(kats).sort().map(function(k){return [k,k];}),"Všetky katalógové čísla");
  var okr=D.okresy.map(function(o){return o.n;}).sort(function(a,b){return a.localeCompare(b,"sk");});
  fill("fOkres",okr.map(function(k){return [k,k];}),"Celé Slovensko");

  fill("fDraha",(D.drahy||[]).map(function(x){return [x.kod,x.nazov];}),"Všetky dráhy zhodnotenia");
  bind("fTyp","typ"); bind("fOdpad","odpad"); bind("fKat","kat"); bind("fOkres","okres"); bind("fDraha","draha");
  document.getElementById("fPripust").addEventListener("change",function(e){
    state.pripust=e.target.value; render();});
  document.getElementById("fQ").addEventListener("input",function(e){state.q=e.target.value;render();});
  document.getElementById("bReset").addEventListener("click",function(){
    state.typ=state.odpad=state.kat=state.okres=state.draha=state.q=""; state.sel=null;
    state.pripust="pc"; document.getElementById("fPripust").value="pc";
    state.lenObjem=false; document.getElementById("fLenObjem").checked=false;
    ["fTyp","fOdpad","fKat","fOkres","fDraha"].forEach(function(i){document.getElementById(i).value="";});
    document.getElementById("fQ").value="";
    SEKTORY.forEach(function(s){state.sektor[s]=true;});
    document.querySelectorAll("#sektory input").forEach(function(i){i.checked=true;});
    document.getElementById("detail").innerHTML=uvod; resetView(); render();});
  document.getElementById("bCSV").addEventListener("click",exportCSV);
  document.getElementById("fVelkost").addEventListener("change",function(e){
    state.velkost=e.target.value; render();});
  document.getElementById("fChoro").addEventListener("change",function(e){
    state.choro=e.target.value; render();});
  document.getElementById("fLenObjem").addEventListener("change",function(e){
    state.lenObjem=e.target.checked; render();});
  document.getElementById("bIn").addEventListener("click",function(){zoomBy(1.4);});
  document.getElementById("bOut").addEventListener("click",function(){zoomBy(1/1.4);});
  document.getElementById("bFit").addEventListener("click",resetView);
  var lg=document.getElementById("legend");
  SEKTORY.forEach(function(s){var e=document.createElement("span");
    e.innerHTML='<i style="background:'+SFARBA[s]+'"></i>'+esc(s); lg.appendChild(e);});
  var e=document.createElement("span"); e.id="legChoro";
  e.textContent="Sýtosť okresu = počet producentov vo výbere"; lg.appendChild(e);
  var e2=document.createElement("span"); e2.id="legVel";
  e2.textContent="Veľkosť bodu = odhad objemu"; lg.appendChild(e2);
}
function fill(id,pairs,first){
  var s=document.getElementById(id); s.innerHTML='<option value="">'+esc(first)+'</option>';
  pairs.forEach(function(p){var o=document.createElement("option");o.value=p[0];o.textContent=p[1];s.appendChild(o);});
}
function bind(id,key){document.getElementById(id).addEventListener("change",function(e){
  state[key]=e.target.value; state.sel=null; render();});}

var uvod='<p class="note">Kliknutím na bod v mape sa zobrazí producent, jeho katalógové čísla '+
  'a očakávané toky odpadu. Kliknutím na okres sa filtruje výber, kolieskom myši sa približuje.</p>';

drawBase(); buildUI(); initPanZoom();
document.getElementById("detail").innerHTML=uvod;
render();
})();
