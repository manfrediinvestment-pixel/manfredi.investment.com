/* Modo claro / oscuro de todo el sitio (feat/modo-claro).
   El sitio está diseñado en oscuro. El modo claro NO invierte la pantalla: recorre las hojas de estilo
   y genera, regla por regla, la versión clara de cada color según para qué se usa:
     · fondos oscuros  → blancos y grises muy claros (con un leve tono azul)
     · letras claras   → azul tinta
     · líneas/velos blancos semitransparentes → líneas/velos azul tinta con la misma transparencia
     · dorado/verde/rojo como letra → el mismo tono, más profundo (para que se lea sobre blanco)
     · sombras → más suaves
   Las fotos y logos no se tocan. Los colores que el JS pone en línea (style="…") también se adaptan.
   La hoja generada se guarda en localStorage y el <head> la aplica antes de pintar (sin parpadeo). */
(function () {
  'use strict';
  var KEY = 'mi_tema', KCSS = 'mi_tema_css', VER = 'v10', root = document.documentElement;
  var CLARO = 'html[data-tema="claro"]';
  // ilustraciones que se ven igual en los dos modos (tapas y lomos de los informes)
  var FIJO = /\.(bk3|est-cover|spn|lec__light)(?![\w-])/, FIJO_SEL = '.bk3, .est-cover, .spn, [data-tema-fijo]';

  /* ---------- color: parseo y OKLab ---------- */
  var NOMBRES = { white: [255, 255, 255, 1], black: [0, 0, 0, 1] };
  function parse(tok) {
    tok = tok.trim().toLowerCase();
    if (NOMBRES[tok]) return NOMBRES[tok].slice();
    var m;
    if (tok[0] === '#') {
      var h = tok.slice(1);
      if (h.length === 3 || h.length === 4) h = h.split('').map(function (c) { return c + c; }).join('');
      if (h.length !== 6 && h.length !== 8) return null;
      return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16), h.length === 8 ? parseInt(h.slice(6, 8), 16) / 255 : 1];
    }
    if ((m = /^rgba?\(([^)]*)\)$/.exec(tok))) {
      var p = m[1].replace(/\//g, ' ').split(/[\s,]+/).filter(Boolean);
      if (p.length < 3) return null;
      var f = function (x, i) { return /%$/.test(x) ? (i < 3 ? parseFloat(x) * 2.55 : parseFloat(x) / 100) : parseFloat(x); };
      return [f(p[0], 0), f(p[1], 1), f(p[2], 2), p.length > 3 ? f(p[3], 3) : 1];
    }
    return null;
  }
  function lin(c) { c /= 255; return c <= .04045 ? c / 12.92 : Math.pow((c + .055) / 1.055, 2.4); }
  function gam(c) { c = c <= .0031308 ? 12.92 * c : 1.055 * Math.pow(c, 1 / 2.4) - .055; return Math.max(0, Math.min(255, Math.round(c * 255))); }
  function aLab(rgb) {
    var r = lin(rgb[0]), g = lin(rgb[1]), b = lin(rgb[2]);
    var l = Math.cbrt(.4122214708 * r + .5363325363 * g + .0514459929 * b), m = Math.cbrt(.2119034982 * r + .6806995451 * g + .1073969566 * b), s = Math.cbrt(.0883024619 * r + .2817188376 * g + .6299787005 * b);
    var L = .2104542553 * l + .793617785 * m - .0040720468 * s, A = 1.9779984951 * l - 2.428592205 * m + .4505937099 * s, B = .0259040371 * l + .7827717662 * m - .808675766 * s;
    return { L: L, C: Math.sqrt(A * A + B * B), h: Math.atan2(B, A) };
  }
  function deLab(L, C, h) {
    var A = C * Math.cos(h), B = C * Math.sin(h);
    var l = Math.pow(L + .3963377774 * A + .2158037573 * B, 3), m = Math.pow(L - .1055613458 * A - .0638541728 * B, 3), s = Math.pow(L - .0894841775 * A - 1.291485548 * B, 3);
    return [gam(4.0767416621 * l - 3.3077115913 * m + .2309699292 * s), gam(-1.2684380046 * l + 2.6097574011 * m - .3413193965 * s), gam(-.0041960863 * l - .7034186147 * m + 1.707614701 * s)];
  }
  function txt(rgb, a) { a = Math.round(a * 1000) / 1000; return a >= 1 ? 'rgb(' + rgb.join(',') + ')' : 'rgba(' + rgb.join(',') + ',' + a + ')'; }

  /* tipo de uso: 't' letra · 'b' fondo · 'l' línea · 's' sombra · 'v' variable */
  function mapear(c, tipo) {
    var o = aLab(c), L = o.L, C = o.C, h = o.h, a = c[3], neutro = C < .06;
    if (tipo === 's') return txt([8, 18, 40], a * .3);
    if (tipo === 'v') tipo = neutro ? (L > .55 ? 't' : 'b') : 'acento';
    if (tipo === 't') {
      if (neutro) return L > .55 ? txt(deLab(.25, Math.min(C, .03), h), a) : null;
      return L > .62 ? txt(deLab(.5, Math.min(C, .16), h), a) : null;
    }
    if (tipo === 'acento') return L > .74 ? txt(deLab(.7, C, h), a) : null; // dorado de rellenos y marcas: un punto más profundo
    if (tipo === 'b') {
      if (neutro) {
        if (L < .5) return txt(deLab(Math.min(.995, .99 - L * .2), Math.min(C * .5, .012), h), a);
        if (a >= .6) return null;                          // superficies claras opacas (botones crema): quedan igual
        return txt(deLab(.3, Math.min(C, .03), h), a); // velos blancos sobre oscuro → velos tinta sobre claro
      }
      return L < .35 ? txt(deLab(.95, C * .35, h), a) : null;
    }
    if (tipo === 'l') {
      if (neutro) return L > .5 ? txt(deLab(.3, Math.min(C, .03), h), Math.min(1, a * 1.15)) : txt(deLab(.88, Math.min(C, .02), h), a);
      return L > .62 ? txt(deLab(.55, C, h), a) : null;
    }
    return null;
  }
  var RE_COLOR = /#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|\b(?:white|black)\b/g;
  function remapValor(v, tipo) {
    var cambio = false;
    var out = v.replace(RE_COLOR, function (tok) {
      var c = parse(tok); if (!c) return tok;
      var r = mapear(c, tipo); if (r == null) return tok;
      cambio = true; return r;
    });
    return cambio ? out : null;
  }
  function tipoDe(prop) {
    if (prop.indexOf('--') === 0) return 'v';
    if (prop === 'fill' || prop === 'stroke') return 'v'; // en SVG un relleno oscuro es fondo y uno claro es letra
    if (/^(color|caret-color|-webkit-text-fill-color|text-decoration-color|accent-color)$/.test(prop)) return 't';
    if (/^background/.test(prop)) return 'b';
    if (/^(border|outline|column-rule)/.test(prop) && /color|^border(-(top|right|bottom|left))?$|^outline$/.test(prop)) return 'l';
    if (/shadow$/.test(prop)) return 's';
    return null;
  }

  /* ---------- selectores: anteponer html[data-tema="claro"] ---------- */
  function partir(sel) { // por comas de primer nivel
    var out = [], prof = 0, cur = '';
    for (var i = 0; i < sel.length; i++) { var ch = sel[i]; if (ch === '(' || ch === '[') prof++; else if (ch === ')' || ch === ']') prof--; if (ch === ',' && !prof) { out.push(cur); cur = ''; } else cur += ch; }
    out.push(cur); return out.map(function (s) { return s.trim(); }).filter(Boolean);
  }
  function prefijar(sel) {
    return partir(sel).map(function (s) {
      if (/^html(?![\w-])/.test(s)) return s.replace(/^html/, CLARO);
      if (/^:root/.test(s)) return s.replace(/^:root/, ':root[data-tema="claro"]');
      if (/^body(?![\w-])/.test(s)) return CLARO + ' ' + s;
      return CLARO + ' ' + s;
    }).join(', ');
  }

  /* ---------- generar la hoja clara ---------- */
  function reglas(lista, out) {
    for (var i = 0; i < lista.length; i++) {
      var r = lista[i];
      if (r.type === 1) { // CSSStyleRule
        if (/data-tema/.test(r.selectorText) || FIJO.test(r.selectorText)) continue;
        var st = r.style, decl = [];
        for (var j = 0; j < st.length; j++) {
          var p = st[j], t = tipoDe(p); if (!t) continue;
          var v = st.getPropertyValue(p); if (!v || !RE_COLOR.test(v)) { RE_COLOR.lastIndex = 0; continue; }
          RE_COLOR.lastIndex = 0;
          var n = remapValor(v, t); if (n == null) continue;
          decl.push(p + ':' + n + (st.getPropertyPriority(p) ? ' !important' : ''));
        }
        if (decl.length) out.push(prefijar(r.selectorText) + '{' + decl.join(';') + '}');
      } else if (r.type === 4 && r.cssRules) { // @media
        var sub = []; reglas(r.cssRules, sub);
        if (sub.length) out.push('@media ' + r.media.mediaText + '{' + sub.join('') + '}');
      } else if (r.cssRules && r.type === 12) { // @supports
        var sub2 = []; reglas(r.cssRules, sub2);
        if (sub2.length) out.push('@supports ' + r.conditionText + '{' + sub2.join('') + '}');
      }
    }
  }
  function generar() {
    var out = [];
    for (var i = 0; i < document.styleSheets.length; i++) {
      var sh = document.styleSheets[i];
      if (sh.ownerNode && (sh.ownerNode.id === 'temaClaro' || sh.ownerNode.id === 'temaCache')) continue;
      var rs; try { rs = sh.cssRules; } catch (e) { continue; } // hojas de otro dominio (fuentes)
      if (rs) reglas(rs, out);
    }
    return out.join('\n') + '\n' + EXTRA;
  }
  // retoques que no salen de la regla general
  var EXTRA = [
    CLARO + '{color-scheme:light;}',
    CLARO + ' body{background-color:#f5f7fb;}',
    CLARO + ' .ml-side{box-shadow:1px 0 0 rgba(15,30,60,.06);}',
    CLARO + ' :is(.bk3, .est-cover, .spn){color:#f4f7fb;}',
    // logos blancos en imagen (Balanz): en claro van en tinta
    CLARO + ' img.as-logo, ' + CLARO + ' img[src$="balanz.svg"]{filter:brightness(0) invert(.14);}'
  ].join('\n');

  /* ---------- estilos en línea (los arma el JS) ---------- */
  var escrito = new WeakMap(), origen = new WeakMap(), tocados = new Set();
  function remapEstilo(el) {
    var cur = el.getAttribute('style');
    if (!cur || escrito.get(el) === cur) return;          // lo escribimos nosotros: no volver a aclararlo
    if (el.closest(FIJO_SEL)) return;
    if (!/#|rgb|white|black/i.test(cur)) return;
    var cambio = false;
    var nuevo = cur.replace(/(^|;)\s*([-\w]+)\s*:\s*([^;]+)/g, function (all, pre, prop, val) {
      var t = tipoDe(prop.toLowerCase()); if (!t) return all;
      var n = remapValor(val, t); if (n == null) return all;
      cambio = true; return pre + prop + ':' + n;
    });
    if (!cambio) return;
    origen.set(el, cur); escrito.set(el, nuevo); tocados.add(el);
    el.setAttribute('style', nuevo);
  }
  var attrOrig = new WeakMap(), attrTocados = new Set();
  function remapAtributos(el) {
    if (!el.getAttribute || el.closest(FIJO_SEL)) return;
    ['fill', 'stroke', 'stop-color'].forEach(function (at) {
      var v = el.getAttribute(at); if (!v) return;
      var o = attrOrig.get(el) || {};
      if (o[at] && o[at].nuevo === v) return;
      var n = remapValor(v, 'v'); if (n == null) return;
      o[at] = { orig: v, nuevo: n }; attrOrig.set(el, o); attrTocados.add(el);
      el.setAttribute(at, n);
    });
  }
  function restaurarAtributos() {
    attrTocados.forEach(function (el) { var o = attrOrig.get(el) || {}; Object.keys(o).forEach(function (at) { if (el.getAttribute(at) === o[at].nuevo) el.setAttribute(at, o[at].orig); }); attrOrig.delete(el); });
    attrTocados.clear();
  }
  function restaurarEstilos() {
    tocados.forEach(function (el) { if (el.getAttribute('style') === escrito.get(el)) el.setAttribute('style', origen.get(el)); escrito.delete(el); });
    tocados.clear();
  }
  var obs = null;
  function observar(on) {
    if (on && !obs) {
      document.querySelectorAll('[style]').forEach(remapEstilo);
      document.querySelectorAll('svg [fill], svg [stroke], svg[fill], svg[stroke], svg stop').forEach(remapAtributos);
      obs = new MutationObserver(function (ms) {
        ms.forEach(function (m) {
          if (m.type === 'attributes') { if (m.target.nodeType === 1) { if (m.attributeName === 'style') remapEstilo(m.target); else remapAtributos(m.target); } }
          else m.addedNodes.forEach(function (n) { if (n.nodeType !== 1) return; if (n.hasAttribute('style')) remapEstilo(n); remapAtributos(n); if (n.querySelectorAll) { n.querySelectorAll('[style]').forEach(remapEstilo); n.querySelectorAll('[fill], [stroke], stop').forEach(remapAtributos); } });
        });
      });
      obs.observe(document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ['style', 'fill', 'stroke'] });
    } else if (!on && obs) { obs.disconnect(); obs = null; restaurarEstilos(); restaurarAtributos(); }
  }

  /* ---------- gráficos (LightweightCharts): los colores van por JS, se cambian con applyOptions ---------- */
  var graficos = [];
  var CLAVES_T = { textColor: 't' }, CLAVES_L = { color: 'l' }, CLAVES_B = { labelBackgroundColor: 'b' };
  function coloresDe(o, claro, ruta) { // devuelve solo las claves de color (remapeadas si claro)
    if (!o || typeof o !== 'object') return null;
    var out = null;
    Object.keys(o).forEach(function (k) {
      var v = o[k], tipo = null;
      if (typeof v === 'string') {
        if (CLAVES_T[k]) tipo = 't'; else if (CLAVES_B[k]) tipo = 'b'; else if (CLAVES_L[k] && ruta !== 'background') tipo = 'l';
        if (!tipo) return;
        var n = claro ? (remapValor(v, tipo) || v) : v;
        (out = out || {})[k] = n;
      } else if (v && typeof v === 'object' && !Array.isArray(v) && typeof v !== 'function') {
        var sub = coloresDe(v, claro, k); if (sub) (out = out || {})[k] = sub;
      }
    });
    return out;
  }
  function envolverGraficos() {
    var LC = window.LightweightCharts; if (!LC || LC.__mlTema) return !!LC;
    // el objeto de la librería es de solo lectura: se reemplaza por una copia con createChart envuelto
    var orig = LC.createChart, copia = {};
    Object.keys(LC).forEach(function (k) { copia[k] = LC[k]; });
    copia.createChart = function (el, opts) {
      var ch = orig.apply(LC, arguments);
      if (coloresDe(opts || {}, false)) { graficos.push({ ch: ch, opts: opts }); if (actual() === 'claro') try { ch.applyOptions(coloresDe(opts, true)); } catch (e) {} }
      return ch;
    };
    copia.__mlTema = true;
    try { window.LightweightCharts = copia; } catch (e) { return true; }
    return true;
  }
  if (!envolverGraficos()) { var tries = 0, iv = setInterval(function () { if (envolverGraficos() || ++tries > 100) clearInterval(iv); }, 100); }
  function repintarGraficos(claro) {
    graficos = graficos.filter(function (g) { try { g.ch.applyOptions(coloresDe(g.opts, claro)); return true; } catch (e) { return false; } });
  }

  /* ---------- aplicar ---------- */
  function hoja(css) {
    var st = document.getElementById('temaClaro');
    if (!st) { st = document.createElement('style'); st.id = 'temaClaro'; document.head.appendChild(st); }
    st.textContent = css;
    var c = document.getElementById('temaCache'); if (c) c.remove();
  }
  var generada = null;
  function aplicarClaro() {
    if (!generada) {
      generada = generar();
      try { localStorage.setItem(KCSS, JSON.stringify({ v: VER, n: document.styleSheets.length, css: generada })); } catch (e) {}
    }
    hoja(generada);
    observar(true);
  }
  function actual() { return root.getAttribute('data-tema') === 'claro' ? 'claro' : 'oscuro'; }
  function poner(t) {
    if (t === 'claro') { root.setAttribute('data-tema', 'claro'); aplicarClaro(); }
    else { root.removeAttribute('data-tema'); observar(false); }
    repintarGraficos(t === 'claro');
    try { localStorage.setItem(KEY, t); } catch (e) {}
    var b = document.getElementById('miTema');
    if (b) { b.setAttribute('aria-pressed', String(t === 'claro')); b.setAttribute('aria-label', t === 'claro' ? 'Pasar a modo oscuro' : 'Pasar a modo claro'); b.title = t === 'claro' ? 'Modo oscuro' : 'Modo claro'; }
  }
  function montar() {
    var inner = document.querySelector('.navbar .nav-inner'), user = document.getElementById('navUserArea');
    if (inner && !document.getElementById('miTema')) {
      var b = document.createElement('button');
      b.type = 'button'; b.id = 'miTema'; b.className = 'mi-tema';
      b.innerHTML = '<svg class="luna" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>' +
        '<svg class="sol" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
      b.addEventListener('click', function () { poner(actual() === 'claro' ? 'oscuro' : 'claro'); });
      if (user) inner.insertBefore(b, user); else inner.appendChild(b);
    }
    poner(actual());
  }
  // el botón aparece enseguida; la hoja clara se genera cuando cargaron todas las hojas de estilo
  function listo() { montar(); }
  if (document.readyState === 'complete') listo(); else window.addEventListener('load', listo);
  window.MiTema = { poner: poner, regenerar: function () { generada = null; if (actual() === 'claro') aplicarClaro(); } };
})();
