/* Noticias · Argentina en datos
 * Sub-pestaña con datos oficiales del INDEC: Tablero · Inflación · Explorador · Calendario.
 * Datos: worker manfredi-indec (workers/indec), que guarda el token del Catálogo API-INDEC,
 * cachea y arma el tablero en un solo JSON. Gráficos: LightweightCharts (ya cargado en index).
 * Hashes: #datos, #datos-inflacion, #datos-explorador, #datos-calendario. El switch de
 * Noticias (assets/analistas/analistas.js) llama a window.DatosAR.mostrar(hash).
 */
(function () {
  'use strict';
  var root = document.getElementById('adPanel');
  if (!root) return;
  var LOCAL = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  var API = window.MI_INDEC_API || (LOCAL ? 'http://localhost:8789' : 'https://manfredi-indec.nachito2502.workers.dev');
  var C = ['#c09520', '#5b9cf5', '#e8725f', '#a77ff0']; // orden fijo (validado CVD sobre #0b1629)
  var ORO = '#f2c94c';
  var SECS = [['datos', 'Tablero'], ['datos-inflacion', 'Inflación'], ['datos-explorador', 'Explorador'], ['datos-calendario', 'Calendario INDEC']];
  var MES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  var MESL = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var DIAS = ['dom', 'lun', 'mar', 'mié', 'jue', 'vie', 'sáb'];

  var st = {
    t: null, carga: null, sec: null, armado: false, charts: [],
    ind: 'inflacion', modo: {}, rango: '5A',
    region: 'Nacional', det: {}, ordCol: 'm', abiertos: {}, catModo: 'ia', catVista: 'cat',
    exp: [], expModo: 'valor', expRango: 'Todo', expDatos: {},
    calMes: null, calTema: 'todos', cal: {}
  };

  /* ───────────── utilidades ───────────── */
  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function nf(v, d) { return v == null || !isFinite(v) ? '—' : Number(v).toLocaleString('es-AR', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function pct(v, d, signo) { if (v == null || !isFinite(v)) return '—'; d = d == null ? 1 : d; return (signo && v > 0 ? '+' : '') + nf(v, d) + '%'; }
  function pesos(v) { return v == null ? '—' : '$' + nf(Math.round(v), 0); }
  function usdM(v) { return v == null ? '—' : (v < 0 ? '−' : '') + 'US$ ' + nf(Math.abs(v), 0) + ' M'; }
  function pad(n) { return String(n).padStart(2, '0'); }
  // períodos: '2026-10' mensual, '2026-T2' trimestral, '2026-S1' semestral
  function perCorto(p) {
    var m = /^(\d{4})-(\d{2})$/.exec(p); if (m) return MES[+m[2] - 1] + '-' + m[1].slice(2);
    m = /^(\d{4})-([TS])(\d)$/.exec(p); if (m) return m[3] + m[2] + ' ' + m[1];
    return p;
  }
  function perLargo(p) { var m = /^(\d{4})-(\d{2})$/.exec(p); return m ? MESL[+m[2] - 1] + ' ' + m[1] : perCorto(p); }
  function aTiempo(p) {
    var m = /^(\d{4})-(\d{2})$/.exec(p); if (m) return p + '-01';
    m = /^(\d{4})-T(\d)$/.exec(p); if (m) return m[1] + '-' + pad((+m[2] - 1) * 3 + 1) + '-01';
    m = /^(\d{4})-S(\d)$/.exec(p); if (m) return m[1] + (m[2] === '1' ? '-01-01' : '-07-01');
    return p;
  }
  function claveT(t) {
    if (typeof t === 'string') return t;
    if (t && t.year) return t.year + '-' + pad(t.month) + '-' + pad(t.day);
    return new Date(t * 1000).toISOString().slice(0, 10);
  }
  function hoyAR() { return new Date(Date.now() - 3 * 3600e3); } // fechas "de pared" en Argentina (UTC−3, sin horario de verano)
  function fechaAR(f, h) { return new Date(f + 'T' + (h || '16:00') + ':00-03:00'); }
  function fechaCorta(f) { var d = new Date(f + 'T12:00:00-03:00'); return DIAS[d.getUTCDay()] + ' ' + d.getUTCDate() + ' ' + MES[d.getUTCMonth()]; }
  function getJSON(path) {
    var ctl = window.AbortController ? new AbortController() : null;
    var to = setTimeout(function () { if (ctl) ctl.abort(); }, 25000);
    return fetch(API + path, ctl ? { signal: ctl.signal } : {}).then(function (r) {
      clearTimeout(to);
      return r.json().then(function (j) { if (!r.ok || j.error) throw new Error(j.error || ('HTTP ' + r.status)); return j; });
    });
  }
  function conLC(cb) { var t0 = Date.now(); (function w() { if (window.LightweightCharts) return cb(window.LightweightCharts); if (Date.now() - t0 < 10000) setTimeout(w, 100); })(); }
  function skel(h) { return '<span class="nt-skel" style="height:' + h + 'px"></span>'; }
  function error(msg) { return '<div class="ad-err">' + esc(msg || 'No pudimos traer los datos del INDEC en este momento.') + '<br>Probá de nuevo en un rato.</div>'; }

  /* ───────────── carga del tablero (con copia local de 1 h para entrar al toque) ───────────── */
  var LS = 'mi_datos_ar_v3';
  function cargarTablero() {
    if (st.t) return Promise.resolve(st.t);
    if (st.carga) return st.carga;
    try { var c = JSON.parse(localStorage.getItem(LS) || 'null'); if (c && Date.now() - c.ts < 3600e3 && c.t && c.t.ipc) { st.t = c.t; return Promise.resolve(st.t); } } catch (e) {}
    st.carga = getJSON('/v1/tablero').then(function (t) {
      st.t = t;
      try { localStorage.setItem(LS, JSON.stringify({ ts: Date.now(), t: t })); } catch (e) {}
      return t;
    }).catch(function (e) { st.carga = null; throw e; });
    return st.carga;
  }

  /* ───────────── gráficos ───────────── */
  function limpiarCharts() { st.charts.forEach(function (c) { try { c.remove(); } catch (e) {} }); st.charts = []; }
  function cortar(datos, rango) {
    if (rango === 'Todo' || !datos.length) return datos;
    var anios = parseInt(rango, 10), u = datos[datos.length - 1].time;
    var lim = (+u.slice(0, 4) - anios) + u.slice(4);
    return datos.filter(function (d) { return d.time > lim; });
  }
  /* defs: [{nombre, color, tipo:'linea'|'barras', datos:[{time, value, color?}]}]
     fmt: formato de valor · etiqueta: time → texto del período · leg: nodo de la leyenda */
  function grafico(el, leg, defs, fmt, etiqueta, opts) {
    opts = opts || {};
    conLC(function (LC) {
      var ch = LC.createChart(el, {
        autoSize: true,
        layout: { background: { type: 'solid', color: 'transparent' }, textColor: '#f3f6fb', fontFamily: "'IBM Plex Sans', system-ui, sans-serif", fontSize: 11, attributionLogo: false },
        grid: { vertLines: { visible: false }, horzLines: { color: 'rgba(214,226,244,.06)' } },
        rightPriceScale: { borderVisible: false, scaleMargins: { top: .12, bottom: .08 } },
        timeScale: { borderVisible: false, fixLeftEdge: true, fixRightEdge: true, lockVisibleTimeRangeOnResize: true },
        crosshair: { mode: LC.CrosshairMode.Magnet, vertLine: { color: 'rgba(242,201,76,.5)', labelVisible: false, style: 3 }, horzLine: { color: 'rgba(214,226,244,.25)', labelBackgroundColor: '#1d3357', style: 3 } },
        localization: { locale: 'es-AR', priceFormatter: fmt },
        handleScale: { mouseWheel: false, pinch: true }, handleScroll: { mouseWheel: false, pressedMouseMove: true, horzTouchDrag: true, vertTouchDrag: false }
      });
      st.charts.push(ch);
      var pf = { type: 'custom', minMove: 0.01, formatter: fmt };
      var mapas = defs.map(function (d) {
        var s = d.tipo === 'barras'
          ? ch.addSeries(LC.HistogramSeries, { color: d.color, priceFormat: pf, priceLineVisible: false, lastValueVisible: false })
          : ch.addSeries(LC.LineSeries, { color: d.color, lineWidth: 2, priceFormat: pf, priceLineVisible: false, lastValueVisible: false, crosshairMarkerRadius: 4, crosshairMarkerBorderColor: '#0b1629', crosshairMarkerBorderWidth: 2 });
        s.setData(d.datos);
        if (opts.cero) s.createPriceLine({ price: 0, color: 'rgba(214,226,244,.3)', lineWidth: 1, lineStyle: 2, axisLabelVisible: false });
        var m = {}; d.datos.forEach(function (p) { m[p.time] = p.value; });
        return m;
      });
      var ultimo = defs.reduce(function (a, d) { var u = d.datos.length ? d.datos[d.datos.length - 1].time : ''; return u > a ? u : a; }, '');
      function pintarLeg(t) {
        t = t || ultimo;
        leg.innerHTML = '<span class="per">' + esc(etiqueta(t)) + '</span>' + defs.map(function (d, i) {
          var v = mapas[i][t];
          return '<span><i class="sw" style="background:' + d.color + '"></i>' + esc(d.nombre) + ' <b>' + (v == null ? '—' : esc(fmt(v))) + '</b></span>';
        }).join('');
      }
      ch.subscribeCrosshairMove(function (p) { pintarLeg(p && p.time ? claveT(p.time) : null); });
      pintarLeg();
      ch.timeScale().fitContent();
    });
  }

  /* ───────────── sparkline SVG (tarjetas y tabla) ───────────── */
  function spark(vals, cls, barras) {
    vals = vals.filter(function (v) { return v != null && isFinite(v); });
    if (vals.length < 2) return '';
    var W = 92, H = 40, min = Math.min.apply(null, vals), max = Math.max.apply(null, vals);
    if (barras) { min = Math.min(0, min); max = Math.max(0, max); }
    var r = max - min || 1, y = function (v) { return H - 3 - ((v - min) / r) * (H - 6); };
    if (barras) {
      var bw = W / vals.length, y0 = y(0);
      return '<svg class="' + cls + '" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none" aria-hidden="true">' + vals.map(function (v, i) {
        var yy = y(v); return '<rect class="bar' + (v < 0 ? ' neg' : '') + '" x="' + (i * bw + .6).toFixed(1) + '" y="' + Math.min(yy, y0).toFixed(1) + '" width="' + Math.max(bw - 1.2, .8).toFixed(1) + '" height="' + Math.max(Math.abs(y0 - yy), .8).toFixed(1) + '" rx="1"/>';
      }).join('') + '</svg>';
    }
    var pts = vals.map(function (v, i) { return (i / (vals.length - 1) * W).toFixed(1) + ',' + y(v).toFixed(1); });
    return '<svg class="' + cls + '" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none" aria-hidden="true"><path class="area" d="M0,' + H + ' L' + pts.join(' L') + ' L' + W + ',' + H + ' Z"/><path d="M' + pts.join(' L') + '"/></svg>';
  }

  /* ───────────── barras horizontales ───────────── */
  function barras(items, fmt, opts) {
    opts = opts || {};
    var vals = items.map(function (x) { return x.v; }).filter(function (v) { return v != null; });
    var min = Math.min(0, Math.min.apply(null, vals)), max = Math.max(0, Math.max.apply(null, vals)), r = max - min || 1, z = -min / r * 100;
    return '<div class="ad-bars">' + items.map(function (x) {
      var w = Math.abs(x.v || 0) / r * 100, neg = x.v < 0;
      return '<div class="ad-bar" title="' + esc(x.n + ': ' + fmt(x.v)) + '"><span class="ad-bar__n' + (x.yo ? ' yo' : '') + '">' + esc(x.n) + '</span>' +
        '<span class="ad-bar__t">' + (min < 0 ? '<i class="ad-bar__z" style="left:' + z.toFixed(2) + '%"></i>' : '') +
        '<i class="ad-bar__f' + (neg ? ' ng' : '') + '" style="left:' + (neg ? z - w : z).toFixed(2) + '%;width:' + Math.max(w, .6).toFixed(2) + '%"></i></span>' +
        '<span class="ad-bar__v">' + esc(fmt(x.v)) + '</span></div>';
    }).join('') + '</div>';
  }

  /* ───────────── próximo dato ───────────── */
  var PROX = {
    inflacion: /precios al consumidor/i, nucleo: /precios al consumidor/i, canasta: /canasta b[aá]sica alimentaria/i,
    salario: /[ií]ndice de salarios/i, emae: /estimador mensual de actividad/i, desempleo: /mercado de trabajo\. tasas/i,
    pobreza: /pobreza/i, balanza: /intercambio comercial argentino/i, pbi: /informe de avance del nivel de actividad/i
  };
  function proximoDe(re) {
    var ahora = Date.now();
    return ((st.t && st.t.proximos) || []).filter(function (e) { return re.test(e.titulo) && fechaAR(e.fecha, e.hora).getTime() > ahora - 3600e3; })[0] || null;
  }
  function cuenta(e) {
    var ms = fechaAR(e.fecha, e.hora).getTime() - Date.now();
    if (ms <= 0) return { n: 'hoy', u: 'ya publicado' };
    var h = ms / 3600e3;
    if (h < 24) return h < 1 ? { n: Math.max(1, Math.round(h * 60)), u: 'min' } : { n: Math.floor(h) + ' h', u: Math.round((h % 1) * 60) + ' min' };
    var d = Math.ceil(h / 24); return { n: d, u: d === 1 ? 'día' : 'días' };
  }
  function bloqueProximo() {
    var ahora = Date.now();
    var e = ((st.t && st.t.proximos) || []).filter(function (x) { return x.clave && fechaAR(x.fecha, x.hora).getTime() > ahora; })[0];
    if (!e) return '';
    var c = cuenta(e);
    return '<div class="ad-prox"><span class="ad-prox__k">Próximo dato clave</span>' +
      '<span class="ad-prox__t">' + esc(e.titulo) + '<small>' + esc(fechaCorta(e.fecha)) + ' · ' + esc(e.hora || '16:00') + ' h · INDEC</small></span>' +
      '<span class="ad-prox__c">' + (typeof c.n === 'number' ? 'en ' + c.n : c.n) + '<small>' + esc(c.u) + '</small></span></div>';
  }

  /* ───────────── indicadores ───────────── */
  function serieDe(lista, campo) { return lista.filter(function (o) { return o[campo] != null; }).map(function (o) { return { time: aTiempo(o.p), value: o[campo] }; }); }
  function prevDe(lista, campo, salto) {
    var v = lista.filter(function (o) { return o[campo] != null; });
    return v.length > (salto || 1) ? v[v.length - 1 - (salto || 1)] : null;
  }
  function delta(act, ant, menosEsMejor, unidad, contra) {
    if (act == null || ant == null) return '';
    var d = Math.round((act - ant) * 10) / 10;
    if (d === 0) return '<span class="ad-d">= ' + esc(contra) + '</span>';
    var bien = menosEsMejor ? d < 0 : d > 0;
    return '<span class="ad-d ' + (bien ? 'bien' : 'mal') + '">' + (d > 0 ? '▲ ' : '▼ ') + nf(Math.abs(d), 1) + ' ' + unidad + '</span> vs ' + esc(contra);
  }
  function etiquetaPer(t) {
    var m = /^(\d{4})-(\d{2})-01$/.exec(t); if (!m) return t;
    return MES[+m[2] - 1] + ' ' + m[1];
  }
  function etiquetaTrim(t) { var m = /^(\d{4})-(\d{2})/.exec(t); return m ? ((+m[2] - 1) / 3 + 1) + '° trim. ' + m[1] : t; }
  function etiquetaSem(t) { var m = /^(\d{4})-(\d{2})/.exec(t); return m ? (m[2] === '01' ? '1er' : '2do') + ' semestre ' + m[1] : t; }
  var fPct = function (v) { return pct(v, 1); };

  var IND = {
    inflacion: {
      t: 'Inflación', d: 'Variación del índice de precios al consumidor (IPC), nivel general, total del país.',
      modos: [['m', 'Mensual'], ['ia', 'Interanual']],
      armar: function (t, m) { return { defs: [{ nombre: m === 'm' ? 'Mensual' : 'Interanual', color: ORO, tipo: m === 'm' ? 'barras' : 'linea', datos: serieDe(t.ipc.serie, m) }], fmt: fPct, et: etiquetaPer }; }
    },
    nucleo: {
      t: 'Núcleo, regulados y nivel general', d: 'La inflación núcleo saca los precios estacionales y los regulados por el Estado: muestra la tendencia de fondo.',
      modos: [['m', 'Mensual'], ['ia', 'Interanual']],
      armar: function (t, m) {
        return { defs: [{ nombre: 'Nivel general', color: C[0], datos: serieDe(t.ipc.serie, m) }, { nombre: 'Núcleo', color: C[1], datos: serieDe(t.ipc.serie, 'n_' + m) }, { nombre: 'Regulados', color: C[2], datos: serieDe(t.ipc.serie, 'r_' + m) }], fmt: fPct, et: etiquetaPer };
      }
    },
    canasta: {
      t: 'Canasta básica (familia tipo)', d: 'Lo que necesita una familia de dos adultos y dos chicos en el Gran Buenos Aires para no ser pobre (total) o indigente (alimentaria).',
      modos: [['pesos', 'En pesos'], ['ia', 'Var. interanual']],
      armar: function (t, m) {
        if (m === 'ia') return { defs: [{ nombre: 'Total (CBT)', color: C[0], datos: serieDe(t.canasta.serie, 'cbt_ia') }, { nombre: 'Alimentaria (CBA)', color: C[1], datos: serieDe(t.canasta.serie, 'cba_ia') }], fmt: fPct, et: etiquetaPer };
        return { defs: [{ nombre: 'Total (CBT)', color: C[0], datos: serieDe(t.canasta.serie, 'cbt_h2') }, { nombre: 'Alimentaria (CBA)', color: C[1], datos: serieDe(t.canasta.serie, 'cba_h2') }], fmt: pesos, et: etiquetaPer };
      }
    },
    salario: {
      t: 'Salarios', d: 'Índice de salarios del INDEC. En "real" se descuenta la inflación: 100 = noviembre de 2023.',
      modos: [['real', 'Real'], ['ia', 'Interanual vs. inflación']],
      armar: function (t, m) {
        var s = t.salarios;
        if (m === 'ia') {
          var ipc = serieDe(t.ipc.serie, 'ia'), desde = s.serie[0].p + '-01';
          return { defs: [{ nombre: 'Registrado privado', color: C[0], datos: serieDe(s.serie, 'priv_ia') }, { nombre: 'Público', color: C[1], datos: serieDe(s.serie, 'pub_ia') }, { nombre: 'Inflación', color: C[2], datos: ipc.filter(function (d) { return d.time >= desde; }) }], fmt: fPct, et: etiquetaPer };
        }
        var base = s.real.filter(function (o) { return o.p === '2023-11'; })[0] || s.real[0];
        function rb(k) { return s.real.filter(function (o) { return o[k] != null && base[k]; }).map(function (o) { return { time: aTiempo(o.p), value: Math.round(o[k] / base[k] * 1000) / 10 }; }); }
        return { defs: [{ nombre: 'Registrado privado', color: C[0], datos: rb('priv') }, { nombre: 'Público', color: C[1], datos: rb('pub') }, { nombre: 'No registrado', color: C[2], datos: rb('noreg') }], fmt: function (v) { return nf(v, 1); }, et: etiquetaPer };
      }
    },
    emae: {
      t: 'Actividad económica (EMAE)', d: 'El "PBI mensual" del INDEC. La serie desestacionalizada permite comparar un mes con el anterior.',
      modos: [['nivel', 'Nivel'], ['ia', 'Interanual'], ['m', 'Mensual']],
      armar: function (t, m) {
        if (m === 'nivel') return { defs: [{ nombre: 'Desestacionalizado', color: C[0], datos: serieDe(t.emae.serie, 'desest') }, { nombre: 'Tendencia-ciclo', color: C[1], datos: serieDe(t.emae.serie, 'tc') }], fmt: function (v) { return nf(v, 1); }, et: etiquetaPer };
        return { defs: [{ nombre: m === 'ia' ? 'Interanual (serie original)' : 'Mensual (desestacionalizado)', color: ORO, tipo: 'barras', datos: serieDe(t.emae.serie, m).map(function (d) { return { time: d.time, value: d.value, color: d.value < 0 ? C[2] : ORO }; }) }], fmt: fPct, et: etiquetaPer, cero: true };
      }
    },
    desempleo: {
      t: 'Mercado de trabajo', d: 'Encuesta Permanente de Hogares, 31 aglomerados urbanos. Informalidad: ocupados sin aportes sobre el total de ocupados.',
      modos: [['desoc', 'Desocupación'], ['informal', 'Informalidad'], ['act', 'Actividad y empleo']],
      armar: function (t, m) {
        var s = t.trabajo.serie;
        if (m === 'act') return { defs: [{ nombre: 'Actividad', color: C[0], datos: serieDe(s, 'act') }, { nombre: 'Empleo', color: C[1], datos: serieDe(s, 'emp') }], fmt: fPct, et: etiquetaTrim };
        return { defs: [{ nombre: m === 'desoc' ? 'Desocupación' : 'Informalidad', color: ORO, datos: serieDe(s, m) }], fmt: fPct, et: etiquetaTrim };
      }
    },
    pobreza: {
      t: 'Pobreza e indigencia', d: 'Porcentaje de personas bajo la línea de pobreza e indigencia, por semestre (EPH, 31 aglomerados).',
      modos: [['pers', 'Personas']],
      armar: function (t) { return { defs: [{ nombre: 'Pobreza', color: C[0], datos: serieDe(t.pobreza.serie, 'pers') }, { nombre: 'Indigencia', color: C[1], datos: serieDe(t.pobreza.serie, 'indig') }], fmt: fPct, et: etiquetaSem }; }
    },
    balanza: {
      t: 'Comercio exterior', d: 'Intercambio comercial argentino de bienes, en millones de dólares. Exportaciones FOB, importaciones CIF.',
      modos: [['saldo', 'Saldo'], ['xm', 'Exportaciones e importaciones']],
      armar: function (t, m) {
        var s = t.comex.serie;
        if (m === 'xm') return { defs: [{ nombre: 'Exportaciones', color: C[0], datos: serieDe(s, 'x') }, { nombre: 'Importaciones', color: C[1], datos: serieDe(s, 'm') }], fmt: usdM, et: etiquetaPer };
        return { defs: [{ nombre: 'Saldo', color: ORO, tipo: 'barras', datos: serieDe(s, 'saldo').map(function (d) { return { time: d.time, value: d.value, color: d.value < 0 ? C[2] : ORO }; }) }], fmt: usdM, et: etiquetaPer, cero: true };
      }
    },
    pbi: {
      t: 'PBI', d: 'Producto interno bruto a precios constantes, variación contra el mismo trimestre del año anterior.',
      modos: [['ia', 'Interanual']],
      armar: function (t) { return { defs: [{ nombre: 'PBI interanual', color: ORO, tipo: 'barras', datos: serieDe(t.pbi.serie, 'ia').map(function (d) { return { time: d.time, value: d.value, color: d.value < 0 ? C[2] : ORO }; }) }], fmt: fPct, et: etiquetaTrim, cero: true }; }
    }
  };

  function tarjetas(t) {
    var out = [], ipc = t.ipc, u = ipc.ultimo;
    function sig(id) { var e = proximoDe(PROX[id]); return e ? '<br>Próximo dato: ' + esc(fechaCorta(e.fecha)) : ''; }
    function tile(id, nombre, per, valor, sub, sp, prov) {
      return '<button type="button" class="ad-kpi' + (st.ind === id ? ' on' : '') + '" data-ind="' + id + '" aria-pressed="' + (st.ind === id) + '">' +
        '<span class="ad-kpi__l"><span>' + esc(nombre) + (prov ? '<span class="ad-prov">provisorio</span>' : '') + '</span><span>' + esc(per) + '</span></span>' +
        '<span class="ad-kpi__v">' + valor + '</span>' + sp + '<span class="ad-kpi__s">' + sub + sig(id) + '</span></button>';
    }
    var pm = prevDe(ipc.serie, 'm');
    out.push(tile('inflacion', 'Inflación del mes', perCorto(u.p), pct(u.m), 'Interanual ' + pct(u.ia) + ' · acumulada ' + pct(u.acum) + '<br>' + delta(u.m, pm && pm.m, true, 'pp', pm ? perCorto(pm.p) : ''), spark(ipc.serie.slice(-24).map(function (o) { return o.m; }), 'ad-kpi__sp', true)));
    var pn = prevDe(ipc.serie, 'n_m');
    out.push(tile('nucleo', 'Inflación núcleo', perCorto(u.p), pct(u.n_m), 'Interanual ' + pct(u.n_ia) + ' · regulados ' + pct(u.r_m) + '<br>' + delta(u.n_m, pn && pn.n_m, true, 'pp', pn ? perCorto(pn.p) : ''), spark(ipc.serie.slice(-24).map(function (o) { return o.n_m; }), 'ad-kpi__sp', true)));
    if (t.canasta) { var cu = t.canasta.ultimo; out.push(tile('canasta', 'Canasta básica total', perCorto(cu.p), pesos(cu.cbt_h2), 'Familia tipo, para no ser pobre · ' + pct(cu.cbt_m, 1, true) + ' en el mes, ' + pct(cu.cbt_ia, 1, true) + ' en un año', spark(t.canasta.serie.slice(-24).map(function (o) { return o.cbt_h2; }), 'ad-kpi__sp'))); }
    if (t.salarios) {
      var su = t.salarios.ultimo, ipcMes = ipc.serie.filter(function (o) { return o.p === su.p; })[0];
      var r = su.real_priv && su.real_priv.ia;
      out.push(tile('salario', 'Salario real registrado', perCorto(su.p), '<span class="ad-d ' + (r >= 0 ? 'bien' : 'mal') + '">' + pct(r, 1, true) + '</span><small>interanual</small>',
        'Privado registrado: subió ' + pct(su.priv_ia) + ' contra una inflación de ' + pct(ipcMes && ipcMes.ia), spark(t.salarios.real.slice(-24).map(function (o) { return o.priv; }), 'ad-kpi__sp')));
    }
    if (t.emae) {
      var eu = t.emae.ultimo, dist = eu.maximo && eu.desest ? (eu.desest / eu.maximo.desest - 1) * 100 : null;
      out.push(tile('emae', 'Actividad (EMAE)', perCorto(eu.p), pct(eu.ia, 1, true) + '<small>interanual</small>',
        'Mensual desestacionalizado ' + pct(eu.m, 1, true) + '<br>' + (dist != null && dist > -0.05 ? 'En máximo histórico' : pct(Math.abs(dist), 1) + ' debajo del récord (' + perCorto(eu.maximo.p) + ')'), spark(t.emae.serie.slice(-24).map(function (o) { return o.desest; }), 'ad-kpi__sp')));
    }
    if (t.trabajo) {
      var tu = t.trabajo.ultimo, ta = prevDe(t.trabajo.serie, 'desoc', 4);
      out.push(tile('desempleo', 'Desocupación', tu.label, pct(tu.desoc), 'Informalidad ' + pct(tu.informal) + ' de los ocupados<br>' + delta(tu.desoc, ta && ta.desoc, true, 'pp', ta ? ta.label : ''), spark(t.trabajo.serie.slice(-12).map(function (o) { return o.desoc; }), 'ad-kpi__sp'), tu.prov));
    }
    if (t.pobreza) {
      var pu = t.pobreza.ultimo, pa = prevDe(t.pobreza.serie, 'pers', 2);
      out.push(tile('pobreza', 'Pobreza', pu.label, pct(pu.pers), 'Indigencia ' + pct(pu.indig) + ' de las personas<br>' + delta(pu.pers, pa && pa.pers, true, 'pp', pa ? pa.label : ''), spark(t.pobreza.serie.slice(-10).map(function (o) { return o.pers; }), 'ad-kpi__sp'), pu.prov));
    }
    if (t.comex) {
      var xu = t.comex.ultimo;
      out.push(tile('balanza', 'Balanza comercial', perCorto(xu.p), usdM(xu.saldo), 'Exportó ' + usdM(xu.x) + ', importó ' + usdM(xu.m) + '<br>Últimos 12 meses: ' + usdM(xu.saldo12), spark(t.comex.serie.slice(-24).map(function (o) { return o.saldo; }), 'ad-kpi__sp', true)));
    }
    if (t.pbi) {
      var bu = t.pbi.ultimo;
      out.push(tile('pbi', 'PBI', bu.label, pct(bu.ia, 1, true) + '<small>interanual</small>', 'A precios constantes', spark(t.pbi.serie.slice(-12).map(function (o) { return o.ia; }), 'ad-kpi__sp', true)));
    }
    return out.join('');
  }

  /* ───────────── Tablero ───────────── */
  function renderTablero(body) {
    body.innerHTML = skel(64) + '<div class="ad-kpis">' + [1, 2, 3, 4, 5, 6].map(function () { return skel(118); }).join('') + '</div>' + skel(380);
    cargarTablero().then(function (t) {
      if (st.sec !== 'datos') return;
      // si la sección del indicador elegido no vino (el INDEC falló en esa parte), volver a inflación
      var SEC_DE = { inflacion: 'ipc', nucleo: 'ipc', canasta: 'canasta', salario: 'salarios', emae: 'emae', desempleo: 'trabajo', pobreza: 'pobreza', balanza: 'comex', pbi: 'pbi' };
      if (!t[SEC_DE[st.ind]]) st.ind = 'inflacion';
      var ipc = t.ipc, u = ipc.ultimo;
      body.innerHTML = bloqueProximo() +
        '<div class="ad-kpis" id="adKpis">' + tarjetas(t) + '</div>' +
        '<section class="ad-chart" id="adChart" aria-live="polite"></section>' +
        '<div class="ad-grid">' +
        '<div class="ad-card"><div class="ad-card__h"><h3>Inflación por región</h3><span>' + esc(perCorto(u.p)) + ' · mensual</span></div>' +
        barras(ipc.regiones.map(function (r) { return { n: r.region === 'GBA' ? 'Gran Buenos Aires' : r.region, v: r.m, yo: r.region === 'Nacional' }; }), fPct) + '</div>' +
        '<div class="ad-card"><div class="ad-card__h"><h3>Qué subió más en ' + esc(MESL[+u.p.slice(5) - 1]) + '</h3><a href="#datos-inflacion" data-ad-ir="datos-inflacion">Inflación a fondo →</a></div>' +
        barras(ipc.rubros.slice(0, 8).map(function (r) { return { n: r.nombre, v: r.m }; }), fPct) + '</div>' +
        (t.emae ? '<div class="ad-card"><div class="ad-card__h"><h3>Actividad por sector</h3><span>' + esc(perCorto(t.emae.ultimo.p)) + ' · interanual</span></div>' +
          barras(t.emae.sectores.map(function (s) { return { n: s.nombre, v: s.ia }; }), function (v) { return pct(v, 1, true); }) + '</div>' : '') +
        (t.comex ? '<div class="ad-card"><div class="ad-card__h"><h3>Qué exporta y a quién</h3><span>' + esc(perCorto(t.comex.ultimo.p)) + ' · US$ M</span></div>' +
          barras(t.comex.rubros.filter(function (r) { return r.codigo !== '9'; }).map(function (r) { return { n: r.nombre, v: r.x }; }), function (v) { return nf(v, 0); }) +
          '<div style="height:18px"></div>' + barras(t.comex.destinos.slice(0, 6).map(function (r) { return { n: r.nombre, v: r.x }; }), function (v) { return nf(v, 0); }) + '</div>' : '') +
        '</div>' + pie(t);
      pintarIndicador();
    }).catch(function (e) { body.innerHTML = error(); console.warn('[datos-ar]', e.message); });
  }
  function pie(t) {
    var f = t && t.actualizado ? new Date(t.actualizado).toLocaleString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : '';
    return '<p class="ad-nota">Fuente: INDEC, <a href="https://api.indec.gob.ar" target="_blank" rel="noopener">Catálogo API-INDEC</a> (datos oficiales; los marcados como provisorios pueden revisarse). PBI: INDEC vía datos.gob.ar.' + (f ? ' Actualizado ' + esc(f) + '.' : '') + ' No es recomendación de inversión.</p>';
  }
  function pintarIndicador() {
    var t = st.t, box = $('adChart'); if (!t || !box) return;
    var def = IND[st.ind];
    var modo = st.modo[st.ind] || def.modos[0][0];
    var g = def.armar(t, modo);
    var trimestral = st.ind === 'desempleo' || st.ind === 'pobreza' || st.ind === 'pbi';
    var rangos = trimestral ? ['5A', '10A', 'Todo'] : ['1A', '3A', '5A', 'Todo'];
    var rango = rangos.indexOf(st.rango) >= 0 ? st.rango : (trimestral ? '10A' : '5A');
    box.innerHTML = '<div class="ad-chart__top"><div><h3 class="ad-chart__t">' + esc(def.t) + '</h3><p class="ad-chart__d">' + esc(def.d) + '</p></div>' +
      '<div class="ad-ctrls">' + (def.modos.length > 1 ? '<div class="ad-seg" role="group" aria-label="Unidad">' + def.modos.map(function (m) { return '<button type="button" data-modo="' + m[0] + '" class="' + (m[0] === modo ? 'on' : '') + '">' + esc(m[1]) + '</button>'; }).join('') + '</div>' : '') +
      '<div class="ad-seg" role="group" aria-label="Período">' + rangos.map(function (r) { return '<button type="button" data-rango="' + r + '" class="' + (r === rango ? 'on' : '') + '">' + (r === 'Todo' ? 'Todo' : r.replace('A', ' años').replace(/^1 años/, '1 año')) + '</button>'; }).join('') + '</div></div></div>' +
      '<div class="ad-leg" id="adLeg"></div><div class="ad-plot" id="adPlot"></div>' +
      '<div class="ad-chart__pie"><span>Pasá el dedo o el mouse por el gráfico para ver cada período.</span><a href="#" data-csv="1">Descargar datos (CSV)</a></div>';
    limpiarCharts();
    var defs = g.defs.map(function (d) { return Object.assign({}, d, { datos: cortar(d.datos, rango) }); });
    st.ultimoGrafico = { defs: defs, fmt: g.fmt, nombre: def.t };
    grafico($('adPlot'), $('adLeg'), defs, g.fmt, g.et, { cero: g.cero });
  }

  /* ───────────── CSV ───────────── */
  function descargarCSV(nombre, defs) {
    var tiempos = {}; defs.forEach(function (d) { d.datos.forEach(function (p) { tiempos[p.time] = 1; }); });
    var filas = [['fecha'].concat(defs.map(function (d) { return d.nombre; }))];
    Object.keys(tiempos).sort().forEach(function (t) {
      filas.push([t].concat(defs.map(function (d) { var p = d.datos.filter(function (x) { return x.time === t; })[0]; return p ? String(p.value).replace('.', ',') : ''; })));
    });
    var csv = '﻿' + filas.map(function (f) { return f.map(function (c) { return /[;"\n]/.test(c) ? '"' + c.replace(/"/g, '""') + '"' : c; }).join(';'); }).join('\n');
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    a.download = 'manfredi-' + nombre.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') + '.csv';
    document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }

  /* ───────────── Inflación a fondo ───────────── */
  var REGIONES = [['Nacional', 'Total país'], ['GBA', 'Gran Buenos Aires'], ['Pampeana', 'Pampeana'], ['Noreste', 'Noreste'], ['Noroeste', 'Noroeste'], ['Cuyo', 'Cuyo'], ['Patagonia', 'Patagonia']];
  function renderInflacion(body) {
    body.innerHTML = '<div class="ad-chips" id="adRegs">' + REGIONES.map(function (r) { return '<button type="button" class="ad-chip' + (r[0] === st.region ? ' on' : '') + '" data-region="' + r[0] + '">' + esc(r[1]) + '</button>'; }).join('') + '</div><div id="adInf">' + skel(380) + '<div style="height:16px"></div>' + skel(420) + '</div>';
    var reg = st.region;
    var pDet = st.det[reg] ? Promise.resolve(st.det[reg]) : getJSON('/v1/ipc?region=' + encodeURIComponent(reg)).then(function (d) { st.det[reg] = d; return d; });
    Promise.all([pDet, cargarTablero()]).then(function (r) {
      if (st.sec !== 'datos-inflacion' || st.region !== reg) return;
      var d = r[0], t = r[1], box = $('adInf');
      var u = d.categorias[d.categorias.length - 1];
      box.innerHTML = '<section class="ad-chart"><div class="ad-chart__top"><div><h3 class="ad-chart__t">Qué está empujando los precios</h3><p class="ad-chart__d">' +
        (st.catVista === 'cat' ? 'Núcleo (la tendencia de fondo), regulados (tarifas, combustibles, prepagas: los fija o autoriza el Estado) y estacionales (frutas, verduras, ropa, turismo).' : 'Bienes (lo que se puede tocar: alimentos, ropa, autos) contra servicios (alquileres, tarifas, educación, salud).') +
        '</p></div><div class="ad-ctrls"><div class="ad-seg" role="group"><button type="button" data-catv="cat" class="' + (st.catVista === 'cat' ? 'on' : '') + '">Por categoría</button><button type="button" data-catv="bys" class="' + (st.catVista === 'bys' ? 'on' : '') + '">Bienes y servicios</button></div>' +
        '<div class="ad-seg" role="group"><button type="button" data-catm="m" class="' + (st.catModo === 'm' ? 'on' : '') + '">Mensual</button><button type="button" data-catm="ia" class="' + (st.catModo === 'ia' ? 'on' : '') + '">Interanual</button></div></div></div>' +
        '<div class="ad-leg" id="adLeg2"></div><div class="ad-plot" id="adPlot2"></div>' +
        '<div class="ad-chart__pie"><span>' + esc(REGIONES.filter(function (x) { return x[0] === reg; })[0][1]) + ' · últimos 3 años</span><span>Nivel general ' + esc(perCorto(d.periodo)) + ': ' + pct(u.ng_m) + ' mensual, ' + pct(u.ng_ia) + ' interanual</span></div></section>' +
        '<section class="ad-card" style="margin-bottom:22px"><div class="ad-card__h"><h3>Los 12 rubros del IPC</h3><span>' + esc(perCorto(d.periodo)) + '</span></div><div class="ad-scroll" id="adRubros"></div>' +
        '<p class="ad-nota">' + (reg === 'Nacional' ? 'La incidencia (cuántos puntos del índice aporta cada rubro) el INDEC la publica por región: elegí una arriba para verla.' : 'Incidencia: cuántos puntos porcentuales de la inflación del mes explica cada rubro (pesa más el que tiene más peso en la canasta).') + ' Tocá un rubro para ver sus aperturas.</p></section>' +
        calculadora(t) + pie(t);
      pintarCategorias(d);
      pintarRubros(d);
      armarCalculadora(t);
    }).catch(function (e) { $('adInf').innerHTML = error(); console.warn('[datos-ar]', e.message); });
  }
  function pintarCategorias(d) {
    var m = st.catModo, cats = d.categorias;
    var defs = st.catVista === 'cat'
      ? [['Nivel general', 'ng'], ['Núcleo', 'n'], ['Regulados', 'r'], ['Estacional', 'e']]
      : [['Bienes', 'b'], ['Servicios', 's']];
    limpiarCharts();
    grafico($('adPlot2'), $('adLeg2'), defs.map(function (x, i) { return { nombre: x[0], color: C[i], datos: serieDe(cats, x[1] + '_' + m) }; }), fPct, etiquetaPer, { cero: m === 'm' });
  }
  function pintarRubros(d) {
    var inc = {}; d.incidencias.forEach(function (x) { inc[x.codigo] = x.inc; });
    var conInc = d.incidencias.length > 0;
    var rows = d.rubros.map(function (r) {
      var u = r.serie[r.serie.length - 1] || {};
      return { codigo: r.codigo, nombre: r.nombre, m: u.m, ia: u.ia, inc: inc[r.codigo], sp: r.serie.map(function (o) { return o.ia; }) };
    });
    var k = st.ordCol;
    rows.sort(function (a, b) { return k === 'nombre' ? a.codigo.localeCompare(b.codigo) : (b[k] == null ? -1 : a[k] == null ? 1 : b[k] - a[k]); });
    var cols = [['nombre', 'Rubro'], ['m', 'Mensual'], ['ia', 'Interanual']].concat(conInc ? [['inc', 'Incidencia']] : []);
    var html = '<table class="ad-tab"><thead><tr>' + cols.map(function (c) { return '<th data-ord="' + c[0] + '" class="' + (c[0] === k ? 'ord' : '') + '" scope="col">' + c[1] + '</th>'; }).join('') + '<th class="col-sp" scope="col">Interanual, 3 años</th></tr></thead><tbody>';
    rows.forEach(function (r) {
      var ab = !!st.abiertos[r.codigo];
      html += '<tr class="rub' + (ab ? ' abierto' : '') + '" data-rub="' + esc(r.codigo) + '" tabindex="0" aria-expanded="' + ab + '"><td>' + esc(r.nombre) + '</td><td><b>' + pct(r.m) + '</b></td><td>' + pct(r.ia) + '</td>' + (conInc ? '<td>' + (r.inc == null ? '—' : nf(r.inc, 2) + ' pp') + '</td>' : '') +
        '<td class="col-sp">' + spark(r.sp, 'sp') + '</td></tr>';
      if (ab) d.aperturas.filter(function (a) { return a.codigo.indexOf(r.codigo + '.') === 0; }).forEach(function (a) {
        html += '<tr class="sub' + (a.nivel === 'Clase' ? ' clase' : '') + '"><td>' + esc(a.nombre) + '</td><td>' + pct(a.m) + '</td><td>' + pct(a.ia) + '</td>' + (conInc ? '<td></td>' : '') + '<td class="col-sp"></td></tr>';
      });
    });
    $('adRubros').innerHTML = html + '</tbody></table>';
  }

  /* calculadora de inflación: usa el IPC nacional (índice base dic-2016 = 100) */
  function calculadora(t) {
    return '<section class="ad-card" style="margin-bottom:22px"><div class="ad-card__h"><h3>Calculadora de inflación</h3><span>IPC nacional</span></div>' +
      '<div class="ad-calc"><label class="ad-f">Monto en pesos<input id="adCalcM" inputmode="numeric" autocomplete="off" value="100.000"></label>' +
      '<label class="ad-f">Desde<select id="adCalcD"></select></label><label class="ad-f">Hasta<select id="adCalcH"></select></label></div>' +
      '<div class="ad-res" id="adCalcR" aria-live="polite"></div></section>';
  }
  function armarCalculadora(t) {
    var s = t.ipc.serie.filter(function (o) { return o.idx != null; });
    var opts = s.map(function (o) { return '<option value="' + o.p + '">' + esc(perLargo(o.p)) + '</option>'; }).reverse().join('');
    var D = $('adCalcD'), H = $('adCalcH'), M = $('adCalcM');
    D.innerHTML = opts; H.innerHTML = opts;
    var ult = s[s.length - 1].p, a = +ult.slice(0, 4), m = ult.slice(5);
    D.value = (a - 1) + '-' + m; if (!D.value) D.value = s[0].p;
    H.value = ult;
    var idx = {}; s.forEach(function (o) { idx[o.p] = o.idx; });
    function calc() {
      var monto = parseFloat((M.value || '').replace(/\./g, '').replace(',', '.')) || 0;
      var i0 = idx[D.value], i1 = idx[H.value];
      if (!i0 || !i1) return;
      var f = i1 / i0, res = monto * f, adelante = H.value >= D.value;
      $('adCalcR').innerHTML = adelante
        ? 'Lo que comprabas con ' + pesos(monto) + ' en ' + esc(perLargo(D.value)) + ', en ' + esc(perLargo(H.value)) + ' cuesta<strong>' + pesos(res) + '</strong>Inflación acumulada: <b>' + pct((f - 1) * 100, 1) + '</b>. Si esa plata quedó quieta, perdió el <b>' + pct((1 - 1 / f) * 100, 1) + '</b> de su poder de compra.'
        : pesos(monto) + ' de ' + esc(perLargo(D.value)) + ' equivalían a<strong>' + pesos(res) + '</strong>en ' + esc(perLargo(H.value)) + '.';
    }
    M.addEventListener('input', function () {
      var dig = M.value.replace(/\D/g, '').slice(0, 13);
      M.value = dig ? Number(dig).toLocaleString('es-AR') : '';
      calc();
    });
    D.addEventListener('change', calc); H.addEventListener('change', calc);
    calc();
  }

  /* ───────────── Explorador de series (datos.gob.ar) ───────────── */
  var FREC = { 'R/P1D': 'Diaria', 'R/P1M': 'Mensual', 'R/P3M': 'Trimestral', 'R/P6M': 'Semestral', 'R/P1Y': 'Anual' };
  var SUGERIDAS = ['inflación', 'tipo de cambio', 'reservas internacionales', 'base monetaria', 'EMAE', 'salarios', 'exportaciones', 'desocupación', 'producción industrial'];
  var COMBOS = [
    { n: 'Salarios vs. inflación', ids: [['149.1_TL_INDIIOS_OCTU_0_21', 'Índice de salarios'], ['148.3_INIVELNAL_DICI_M_26', 'IPC nacional']], modo: 'base100' },
    { n: 'Exportaciones vs. importaciones', ids: [['74.3_IET_0_M_16', 'Exportaciones (US$ M)'], ['74.3_IIT_0_M_25', 'Importaciones (US$ M)']], modo: 'valor' },
    { n: 'Actividad (EMAE)', ids: [['143.3_NO_PR_2004_A_31', 'EMAE desestacionalizado']], modo: 'valor' }
  ];
  function renderExplorador(body) {
    body.innerHTML = '<div class="ad-busca"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>' +
      '<input id="adQ" type="search" placeholder="Buscá cualquier serie: inflación, dólar, reservas, salarios, soja…" autocomplete="off" aria-label="Buscar series"></div>' +
      '<div class="ad-sug"><span>Probá:</span>' + SUGERIDAS.map(function (s) { return '<button type="button" class="ad-chip" data-sug="' + esc(s) + '">' + esc(s) + '</button>'; }).join('') + '</div>' +
      '<div class="ad-sug"><span>Comparaciones listas:</span>' + COMBOS.map(function (c, i) { return '<button type="button" class="ad-chip" data-combo="' + i + '">' + esc(c.n) + '</button>'; }).join('') + '</div>' +
      '<div class="ad-res-l" id="adRes" aria-live="polite"></div>' +
      '<section class="ad-chart" id="adExp"></section>' +
      '<p class="ad-nota">Fuente: <a href="https://datos.gob.ar/series" target="_blank" rel="noopener">Series de tiempo de datos.gob.ar</a> (INDEC, BCRA, Ministerio de Economía y otros organismos). Hasta 4 series a la vez; con unidades distintas usá "Base 100" para compararlas en la misma escala.</p>';
    pintarExp();
  }
  var tBusca = null;
  function buscar(q) {
    var box = $('adRes'); if (!box) return;
    if (q.trim().length < 2) { box.innerHTML = ''; return; }
    box.innerHTML = skel(56) + skel(56);
    getJSON('/v1/buscar?q=' + encodeURIComponent(q) + '&limit=25').then(function (r) {
      if (!$('adRes')) return;
      if (!r.data.length) { box.innerHTML = '<p class="ad-nota">No encontramos series para "' + esc(q) + '".</p>'; return; }
      box.innerHTML = r.data.map(function (s) {
        return '<button type="button" class="ad-res-i" data-add="' + esc(s.id) + '" data-nom="' + esc(s.titulo) + '"><b>' + esc(s.titulo) + '</b><small>' + esc(FREC[s.frecuencia] || s.frecuencia || '') + ' · ' + esc((s.desde || '').slice(0, 4)) + '–' + esc((s.hasta || '').slice(0, 7)) + (s.unidad ? ' · ' + esc(s.unidad) : '') + ' · ' + esc(s.fuente || '') + '</small><em>+ Agregar</em></button>';
      }).join('');
    }).catch(function () { box.innerHTML = '<p class="ad-nota">La búsqueda no respondió. Probá de nuevo.</p>'; });
  }
  function agregarSerie(id, nombre) {
    if (st.exp.some(function (s) { return s.id === id; })) return pintarExp();
    if (st.exp.length >= 4) st.exp.shift();
    st.exp.push({ id: id, nombre: nombre });
    pintarExp();
  }
  function traerSerie(id, modo) {
    var k = id + '|' + modo;
    if (st.expDatos[k]) return Promise.resolve(st.expDatos[k]);
    var rm = modo === 'ia' ? '&representation_mode=percent_change_a_year_ago' : '';
    return getJSON('/v1/series?ids=' + encodeURIComponent(id) + '&limit=5000' + rm).then(function (r) {
      var mult = modo === 'ia' ? 100 : 1;
      var d = (r.data || []).filter(function (x) { return x[1] != null; }).map(function (x) { return { time: x[0], value: Math.round(x[1] * mult * 1000) / 1000 }; });
      st.expDatos[k] = d; return d;
    });
  }
  function pintarExp() {
    var box = $('adExp'); if (!box) return;
    if (!st.exp.length) { limpiarCharts(); box.innerHTML = '<div class="ad-err">Buscá una serie arriba o elegí una comparación lista para empezar.</div>'; return; }
    var modo = st.expModo;
    box.innerHTML = '<div class="ad-chart__top"><div class="ad-sel">' + st.exp.map(function (s, i) { return '<span><i style="background:' + C[i] + '"></i><b title="' + esc(s.nombre) + '">' + esc(s.nombre) + '</b><button type="button" data-quitar="' + esc(s.id) + '" aria-label="Quitar ' + esc(s.nombre) + '">×</button></span>'; }).join('') + '</div>' +
      '<div class="ad-ctrls"><div class="ad-seg" role="group" aria-label="Unidad">' + [['valor', 'Valor'], ['ia', 'Var. interanual'], ['base100', 'Base 100']].map(function (m) { return '<button type="button" data-expm="' + m[0] + '" class="' + (m[0] === modo ? 'on' : '') + '">' + m[1] + '</button>'; }).join('') + '</div>' +
      '<div class="ad-seg" role="group" aria-label="Período">' + ['5A', '10A', 'Todo'].map(function (r) { return '<button type="button" data-expr="' + r + '" class="' + (r === st.expRango ? 'on' : '') + '">' + (r === 'Todo' ? 'Todo' : r.replace('A', ' años')) + '</button>'; }).join('') + '</div></div></div>' +
      '<div class="ad-leg" id="adLeg3"></div><div class="ad-plot" id="adPlot3">' + skel(300) + '</div>' +
      '<div class="ad-chart__pie"><span>' + (modo === 'base100' ? '100 = primer período en común de las series elegidas.' : 'Pasá el dedo o el mouse por el gráfico para ver cada período.') + '</span><a href="#" data-csv="exp">Descargar datos (CSV)</a></div>';
    var fuente = modo === 'base100' ? 'valor' : modo;
    Promise.all(st.exp.map(function (s) { return traerSerie(s.id, fuente); })).then(function (datos) {
      if (!$('adPlot3')) return;
      var defs = st.exp.map(function (s, i) { return { nombre: s.nombre, color: C[i], datos: cortar(datos[i], st.expRango) }; });
      if (modo === 'base100') {
        var ini = defs.reduce(function (a, d) { return d.datos.length && d.datos[0].time > a ? d.datos[0].time : a; }, '');
        defs.forEach(function (d) {
          var b = d.datos.filter(function (p) { return p.time >= ini; })[0];
          d.datos = b ? d.datos.filter(function (p) { return p.time >= ini; }).map(function (p) { return { time: p.time, value: Math.round(p.value / b.value * 1000) / 10 }; }) : [];
        });
      }
      $('adPlot3').innerHTML = '';
      limpiarCharts();
      var fmt = modo === 'ia' ? fPct : function (v) { return Math.abs(v) >= 1000 ? nf(v, 0) : nf(v, Math.abs(v) < 10 ? 2 : 1); };
      st.ultimoExp = { defs: defs, nombre: 'explorador' };
      // series mensuales vienen con día 01 → "oct 2026"; las diarias, con la fecha completa
      var diaria = defs.some(function (d) { return d.datos.some(function (p) { return p.time.slice(8) !== '01'; }); });
      grafico($('adPlot3'), $('adLeg3'), defs, fmt, function (t) { return diaria ? t.slice(8) + '/' + t.slice(5, 7) + '/' + t.slice(0, 4) : etiquetaPer(t); }, { cero: modo === 'ia' });
    }).catch(function () { if ($('adPlot3')) $('adPlot3').innerHTML = error('No pudimos traer esa serie.'); });
  }

  /* ───────────── Calendario INDEC ───────────── */
  var TEMAS = [['todos', 'Todas'], ['clave', 'Las que mueven al mercado'], ['precios', 'Precios'], ['actividad', 'Actividad'], ['trabajo', 'Trabajo e ingresos'], ['externo', 'Sector externo'], ['otros', 'Otras']];
  var TEMA_N = { precios: 'Precios', actividad: 'Actividad', trabajo: 'Trabajo', externo: 'Externo', otros: 'Otras' };
  function renderCalendario(body) {
    var h = hoyAR();
    if (!st.calMes) st.calMes = h.getUTCFullYear() + '-' + pad(h.getUTCMonth() + 1);
    var a = +st.calMes.slice(0, 4), m = +st.calMes.slice(5);
    body.innerHTML = (st.t ? bloqueProximo() : '') +
      '<div class="ad-cal-top"><div class="ad-mes"><button type="button" data-mes="-1" aria-label="Mes anterior">‹</button><h3>' + MESL[m - 1] + ' ' + a + '</h3><button type="button" data-mes="1" aria-label="Mes siguiente">›</button></div>' +
      '<a class="ad-btn sec" href="https://www.indec.gob.ar/indec/web/Calendario-Fecha-0" target="_blank" rel="noopener">Calendario oficial ↗</a></div>' +
      '<div class="ad-chips">' + TEMAS.map(function (x) { return '<button type="button" class="ad-chip' + (x[0] === st.calTema ? ' on' : '') + '" data-tema="' + x[0] + '">' + esc(x[1]) + '</button>'; }).join('') + '</div>' +
      '<div id="adCal">' + skel(70) + skel(70) + skel(70) + '</div>' +
      '<p class="ad-nota">Las publicaciones del INDEC salen a las 16:00 (hora de Argentina) salvo que se indique otra hora. "Agendar" lo suma a tu Google Calendar.</p>';
    if (!st.t) cargarTablero().then(function () { if (st.sec === 'datos-calendario' && !document.querySelector('#adBody .ad-prox')) { var p = bloqueProximo(); if (p) $('adBody').insertAdjacentHTML('afterbegin', p); } }).catch(function () {});
    var mes = st.calMes;
    var p = st.cal[mes] ? Promise.resolve(st.cal[mes]) : getJSON('/v1/calendario?mes=' + mes).then(function (r) { st.cal[mes] = r; return r; });
    p.then(function (r) { if (st.sec === 'datos-calendario' && st.calMes === mes) pintarCal(r); })
      .catch(function () { if ($('adCal')) $('adCal').innerHTML = error('No pudimos leer el calendario del INDEC.'); });
  }
  function pintarCal(r) {
    var tema = st.calTema, hoy = hoyAR().toISOString().slice(0, 10);
    var evs = r.eventos.filter(function (e) { return tema === 'todos' || (tema === 'clave' ? e.clave : e.tema === tema); });
    if (!evs.length) { $('adCal').innerHTML = '<div class="ad-err">No hay publicaciones de este tipo en el mes.</div>'; return; }
    var dias = {}; evs.forEach(function (e) { (dias[e.fecha] = dias[e.fecha] || []).push(e); });
    $('adCal').innerHTML = '<div class="ad-dias">' + Object.keys(dias).sort().map(function (f) {
      var d = new Date(f + 'T12:00:00-03:00');
      return '<div class="ad-dia' + (f === hoy ? ' hoy' : '') + '"><div class="ad-dia__f"><b>' + d.getUTCDate() + '</b>' + (f === hoy ? 'hoy' : DIAS[d.getUTCDay()]) + '</div><div class="ad-evs">' + dias[f].map(function (e) {
        var hh = (e.hora || '16:00').replace(':', ''), fd = f.replace(/-/g, '');
        var g = 'https://calendar.google.com/calendar/render?action=TEMPLATE&text=' + encodeURIComponent('INDEC – ' + e.titulo) + '&dates=' + fd + 'T' + hh + '00/' + fd + 'T' + pad(+hh.slice(0, 2)) + '30' + '00&ctz=America/Argentina/Buenos_Aires&details=' + encodeURIComponent('Datos y gráficos en manfredinvestment.com/#datos');
        return '<div class="ad-ev' + (e.clave ? ' clave' : '') + '"><span>' + esc(e.titulo) + '</span><span class="ad-ev__m"><span class="ad-tag">' + esc(TEMA_N[e.tema] || 'Otras') + '</span>' + esc(e.hora || '16:00') + (f >= hoy ? ' · <a href="' + g + '" target="_blank" rel="noopener">Agendar</a>' : '') + '</span></div>';
      }).join('') + '</div></div>';
    }).join('') + '</div>';
  }

  /* ───────────── armado, navegación y eventos ───────────── */
  function armar() {
    if (st.armado) return;
    st.armado = true;
    root.innerHTML = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><linearGradient id="adSpGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f2c94c" stop-opacity=".22"/><stop offset="1" stop-color="#f2c94c" stop-opacity="0"/></linearGradient></defs></svg>' +
      '<nav class="ad-nav" id="adNav" aria-label="Argentina en datos">' + SECS.map(function (s) { return '<button type="button" data-ad-ir="' + s[0] + '">' + esc(s[1]) + '</button>'; }).join('') +
      '<i class="ad-nav__ind" aria-hidden="true"></i><span class="ad-fuente"><i></i>Datos oficiales del INDEC</span></nav><div id="adBody"></div>';
    root.addEventListener('click', onClick);
    root.addEventListener('input', function (e) {
      if (e.target.id === 'adQ') { clearTimeout(tBusca); var q = e.target.value; tBusca = setTimeout(function () { buscar(q); }, 320); }
    });
    root.addEventListener('keydown', function (e) {
      if ((e.key === 'Enter' || e.key === ' ') && e.target.matches && e.target.matches('tr.rub')) { e.preventDefault(); e.target.click(); }
    });
    window.addEventListener('resize', marcarNav);
  }
  function marcarNav() {
    var on = root.querySelector('.ad-nav button.on'), ind = root.querySelector('.ad-nav__ind');
    if (!on || !ind || !on.offsetWidth) return;
    ind.style.left = on.offsetLeft + 'px'; ind.style.width = on.offsetWidth + 'px';
  }
  function ir(sec) {
    if (location.hash !== '#' + sec) history.replaceState(null, '', '#' + sec);
    mostrar(sec, true);
  }
  function mostrar(hash, forzar) {
    armar();
    var sec = SECS.some(function (s) { return s[0] === hash; }) ? hash : 'datos';
    root.querySelectorAll('.ad-nav button').forEach(function (b) { var on = b.dataset.adIr === sec; b.classList.toggle('on', on); b.setAttribute('aria-current', on ? 'page' : 'false'); });
    requestAnimationFrame(marcarNav);
    if (st.sec === sec && !forzar) return;
    st.sec = sec;
    limpiarCharts();
    var body = $('adBody');
    if (sec === 'datos') renderTablero(body);
    else if (sec === 'datos-inflacion') renderInflacion(body);
    else if (sec === 'datos-explorador') renderExplorador(body);
    else renderCalendario(body);
  }
  function onClick(e) {
    var el = e.target.closest('button, a, tr.rub, th[data-ord]'); if (!el || !root.contains(el)) return;
    var ds = el.dataset;
    if (ds.adIr) { e.preventDefault(); ir(ds.adIr); window.scrollTo({ top: Math.max(0, root.getBoundingClientRect().top + scrollY - 90), behavior: 'smooth' }); return; }
    if (ds.ind) {
      st.ind = ds.ind;
      root.querySelectorAll('.ad-kpi').forEach(function (k) { var on = k.dataset.ind === st.ind; k.classList.toggle('on', on); k.setAttribute('aria-pressed', on); });
      pintarIndicador();
      var ch = $('adChart'); if (ch && window.innerWidth < 860) ch.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    if (ds.modo) { st.modo[st.ind] = ds.modo; pintarIndicador(); return; }
    if (ds.rango) { st.rango = ds.rango; pintarIndicador(); return; }
    if (ds.csv) {
      e.preventDefault();
      var g = ds.csv === 'exp' ? st.ultimoExp : st.ultimoGrafico;
      if (g) descargarCSV(g.nombre, g.defs);
      return;
    }
    if (ds.region) { st.region = ds.region; st.abiertos = {}; mostrar('datos-inflacion', true); return; }
    if (ds.catv) { st.catVista = ds.catv; root.querySelectorAll('[data-catv]').forEach(function (b) { b.classList.toggle('on', b.dataset.catv === st.catVista); }); var d = st.det[st.region]; if (d) { pintarCategorias(d); var p = root.querySelector('#adInf .ad-chart__d'); if (p) p.textContent = st.catVista === 'cat' ? 'Núcleo (la tendencia de fondo), regulados (tarifas, combustibles, prepagas: los fija o autoriza el Estado) y estacionales (frutas, verduras, ropa, turismo).' : 'Bienes (lo que se puede tocar: alimentos, ropa, autos) contra servicios (alquileres, tarifas, educación, salud).'; } return; }
    if (ds.catm) { st.catModo = ds.catm; root.querySelectorAll('[data-catm]').forEach(function (b) { b.classList.toggle('on', b.dataset.catm === st.catModo); }); if (st.det[st.region]) pintarCategorias(st.det[st.region]); return; }
    if (ds.ord) { st.ordCol = ds.ord; if (st.det[st.region]) pintarRubros(st.det[st.region]); return; }
    if (ds.rub) { st.abiertos[ds.rub] = !st.abiertos[ds.rub]; if (st.det[st.region]) pintarRubros(st.det[st.region]); var tr = root.querySelector('tr[data-rub="' + ds.rub + '"]'); if (tr) tr.focus({ preventScroll: true }); return; }
    if (ds.sug) { var q = $('adQ'); q.value = ds.sug; buscar(ds.sug); q.focus(); return; }
    if (ds.combo) { var c = COMBOS[+ds.combo]; st.exp = c.ids.map(function (x) { return { id: x[0], nombre: x[1] }; }); st.expModo = c.modo; pintarExp(); return; }
    if (ds.add) { agregarSerie(ds.add, ds.nom); return; }
    if (ds.quitar) { st.exp = st.exp.filter(function (s) { return s.id !== ds.quitar; }); pintarExp(); return; }
    if (ds.expm) { st.expModo = ds.expm; pintarExp(); return; }
    if (ds.expr) { st.expRango = ds.expr; pintarExp(); return; }
    if (ds.mes) {
      var a = +st.calMes.slice(0, 4), m = +st.calMes.slice(5) - 1 + (+ds.mes);
      var d2 = new Date(Date.UTC(a, m, 1)); st.calMes = d2.getUTCFullYear() + '-' + pad(d2.getUTCMonth() + 1);
      mostrar('datos-calendario', true); return;
    }
    if (ds.tema) { st.calTema = ds.tema; root.querySelectorAll('[data-tema]').forEach(function (b) { b.classList.toggle('on', b.dataset.tema === st.calTema); }); if (st.cal[st.calMes]) pintarCal(st.cal[st.calMes]); return; }
  }

  window.DatosAR = { mostrar: function (hash) { mostrar((hash || '').replace('#', '')); } };
})();
