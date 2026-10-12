/* Portfolio → Métricas de cartera: al tocar un ratio se abre su detalle con un gráfico
   y una explicación según el perfil del test. Todo se calcula en el navegador con los
   mismos datos de las tarjetas (pfBuildAdvancedMetrics en index.html): no usa IA ni
   ningún servicio pago. Reemplaza al mini-botón de Warren, que llamaba a una ruta vieja.
   Expone window.PfRatios.panel(key, datos) → HTML. */
(function () {
  var CART = '#e9d3a0', SPX = '#8fb4ff', OK = '#56c793', OJO = '#e9c46a', MAL = '#ef7a6b';
  var TD = 252;
  var PERFILES = ['Conservador', 'Moderado-Conservador', 'Moderado', 'Moderado-Agresivo', 'Agresivo'];
  // referencias orientativas por perfil (de más prudente a más arriesgado)
  var REF = {
    beta: [0.6, 0.8, 1.1, 1.3, 1.5],
    vol: [0.10, 0.15, 0.20, 0.28, 0.40],
    dd: [-0.08, -0.12, -0.18, -0.25, -0.35],
    var: [-0.01, -0.015, -0.02, -0.03, -0.04]
  };

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function pct(x, d) { return (x * 100).toFixed(d == null ? 1 : d).replace('.', ',') + '%'; }
  function num(x, d) { return x.toFixed(d == null ? 2 : d).replace('.', ','); }
  function mean(a) { return a.reduce(function (s, x) { return s + x; }, 0) / a.length; }
  function sd(a) { var m = mean(a); return Math.sqrt(a.reduce(function (s, x) { return s + (x - m) * (x - m); }, 0) / Math.max(1, a.length - 1)); }
  function cov(a, b) { var ma = mean(a), mb = mean(b), s = 0; for (var i = 0; i < a.length; i++) s += (a[i] - ma) * (b[i] - mb); return s / Math.max(1, a.length - 1); }
  function corr(a, b) { var n = Math.min(a.length, b.length); a = a.slice(-n); b = b.slice(-n); var s = sd(a) * sd(b); return s ? cov(a, b) / s : 0; }
  function base100(s) { return s.map(function (v) { return v / s[0] * 100; }); }
  function bajoAgua(s) { var pk = s[0]; return s.map(function (v) { if (v > pk) pk = v; return v / pk - 1; }); }
  function volMovil(r, w) { var out = []; for (var i = w; i <= r.length; i++) out.push(sd(r.slice(i - w, i)) * Math.sqrt(TD)); return out; }
  function perfil() {
    var p = window._qzLastProfile;
    if (!p || p.tier == null) return null;
    var i = Math.max(0, Math.min(4, +p.tier));
    return { i: i, nombre: p.name || PERFILES[i] };
  }

  /* ------------------------------ gráficos (SVG) ------------------------------ */
  var W = 640, H = 230, L = 46, R = 14, T = 14, B = 26;
  function escala(min, max, a, b) { var d = max - min || 1; return function (v) { return a + (v - min) / d * (b - a); }; }
  function ejeY(ticks, Y, fmt) {
    return ticks.map(function (t) {
      return '<line x1="' + L + '" x2="' + (W - R) + '" y1="' + Y(t).toFixed(1) + '" y2="' + Y(t).toFixed(1) + '" class="pfr-grid' + (t === 0 ? ' pfr-cero' : '') + '"/>' +
        '<text x="' + (L - 8) + '" y="' + (Y(t) + 3.5).toFixed(1) + '" text-anchor="end" class="pfr-tick">' + fmt(t) + '</text>';
    }).join('');
  }
  function ticks(min, max, n) {
    var paso = (max - min) / (n || 4), p = Math.pow(10, Math.floor(Math.log10(paso || 1))), m = paso / p;
    paso = (m <= 1 ? 1 : m <= 2 ? 2 : m <= 5 ? 5 : 10) * p;
    var out = [], v = Math.ceil(min / paso) * paso;
    for (; v <= max + 1e-12; v += paso) out.push(+v.toFixed(10));
    return out;
  }
  function svg(cuerpo, alto) { return '<svg class="pfr-svg" viewBox="0 0 ' + W + ' ' + (alto || H) + '" role="img" preserveAspectRatio="none">' + cuerpo + '</svg>'; }
  function leyenda(items) {
    return '<div class="pfr-ley">' + items.map(function (it) { return '<span><i style="background:' + it[1] + '"></i>' + esc(it[0]) + '</span>'; }).join('') + '</div>';
  }
  function lineas(series, o) {
    o = o || {};
    var todos = [].concat.apply([], series.map(function (s) { return s.v; }));
    var min = Math.min.apply(null, todos.concat(o.incluir || [])), max = Math.max.apply(null, todos.concat(o.incluir || []));
    var pad = (max - min) * 0.08 || 1; min -= pad; max += pad;
    if (o.techoCero) max = Math.max(max, 0);
    var n = series[0].v.length, X = escala(0, n - 1, L, W - R), Y = escala(min, max, H - B, T);
    var c = ejeY(ticks(min, max, 4), Y, o.fmt || function (t) { return t; });
    series.forEach(function (s, k) {
      var pts = s.v.map(function (v, i) { return X(i).toFixed(1) + ',' + Y(v).toFixed(1); });
      if (k === 0 && o.area) {
        var y0 = Y(o.areaBase != null ? o.areaBase : min).toFixed(1);
        c += '<path d="M' + X(0).toFixed(1) + ',' + y0 + ' L' + pts.join(' L') + ' L' + X(n - 1).toFixed(1) + ',' + y0 + 'Z" fill="' + s.c + '" opacity=".13"/>';
      }
      c += '<polyline points="' + pts.join(' ') + '" fill="none" stroke="' + s.c + '" stroke-width="' + (k === 0 ? 2 : 1.6) + '"' + (k ? ' stroke-dasharray="5 4"' : '') + ' stroke-linejoin="round"/>';
    });
    (o.marcas || []).forEach(function (m) {
      c += '<line x1="' + L + '" x2="' + (W - R) + '" y1="' + Y(m.v).toFixed(1) + '" y2="' + Y(m.v).toFixed(1) + '" stroke="' + m.c + '" stroke-dasharray="2 4" stroke-width="1.2"/>' +
        '<text x="' + (W - R) + '" y="' + (Y(m.v) - 5).toFixed(1) + '" text-anchor="end" class="pfr-tag" fill="' + m.c + '">' + esc(m.t) + '</text>';
    });
    c += '<text x="' + L + '" y="' + (H - 6) + '" class="pfr-tick">hace ' + (n - 1) + ' ruedas</text><text x="' + (W - R) + '" y="' + (H - 6) + '" text-anchor="end" class="pfr-tick">hoy</text>';
    return svg(c);
  }
  function dispersion(x, y, beta) {
    var lim = Math.max.apply(null, x.concat(y).map(Math.abs)) * 1.1 || 0.01;
    var X = escala(-lim, lim, L, W - R), Y = escala(-lim, lim, H - B, T), f = function (t) { return pct(t, 0); };
    var c = ejeY(ticks(-lim, lim, 4), Y, f);
    c += '<line x1="' + X(0) + '" x2="' + X(0) + '" y1="' + T + '" y2="' + (H - B) + '" class="pfr-grid pfr-cero"/>';
    c += x.map(function (v, i) { return '<circle cx="' + X(v).toFixed(1) + '" cy="' + Y(y[i]).toFixed(1) + '" r="2.6" fill="' + CART + '" opacity=".55"/>'; }).join('');
    var a = mean(y) - beta * mean(x);
    c += '<line x1="' + X(-lim) + '" y1="' + Y(-lim) + '" x2="' + X(lim) + '" y2="' + Y(lim) + '" stroke="' + SPX + '" stroke-dasharray="5 4" stroke-width="1.4"/>';
    c += '<line x1="' + X(-lim) + '" y1="' + Y(a - beta * lim).toFixed(1) + '" x2="' + X(lim) + '" y2="' + Y(a + beta * lim).toFixed(1) + '" stroke="' + CART + '" stroke-width="2"/>';
    c += '<text x="' + (W - R) + '" y="' + (H - 6) + '" text-anchor="end" class="pfr-tick">S&amp;P 500 en el día →</text><text x="' + (L + 4) + '" y="' + (T + 10) + '" class="pfr-tick">↑ tu cartera</text>';
    return svg(c);
  }
  function histograma(r, corte) {
    var min = Math.min.apply(null, r), max = Math.max.apply(null, r), nb = 24, w = (max - min) / nb || 1, bins = new Array(nb).fill(0);
    r.forEach(function (v) { bins[Math.min(nb - 1, Math.floor((v - min) / w))]++; });
    var X = escala(min, max, L, W - R), Y = escala(0, Math.max.apply(null, bins) * 1.1, H - B, T);
    var c = ejeY(ticks(0, Math.max.apply(null, bins) * 1.1, 3), Y, function (t) { return t; });
    bins.forEach(function (n, i) {
      var x0 = X(min + i * w), x1 = X(min + (i + 1) * w), mal = min + (i + 1) * w <= corte;
      c += '<rect x="' + (x0 + 1).toFixed(1) + '" y="' + Y(n).toFixed(1) + '" width="' + Math.max(1, x1 - x0 - 2).toFixed(1) + '" height="' + (H - B - Y(n)).toFixed(1) + '" rx="2" fill="' + (mal ? MAL : CART) + '" opacity="' + (mal ? .85 : .6) + '"/>';
    });
    c += '<line x1="' + X(corte).toFixed(1) + '" x2="' + X(corte).toFixed(1) + '" y1="' + T + '" y2="' + (H - B) + '" stroke="' + MAL + '" stroke-dasharray="3 3" stroke-width="1.4"/>' +
      '<text x="' + (X(corte) + 6).toFixed(1) + '" y="' + (T + 10) + '" class="pfr-tag" fill="' + MAL + '">VaR ' + pct(corte) + '</text>';
    c += '<text x="' + L + '" y="' + (H - 6) + '" class="pfr-tick">' + pct(min) + '</text><text x="' + (W - R) + '" y="' + (H - 6) + '" text-anchor="end" class="pfr-tick">' + pct(max) + '</text>';
    return svg(c);
  }
  function mapaCorr(rbt, nombres) {
    var ks = Object.keys(rbt).slice(0, 8), n = ks.length, cel = Math.min(52, Math.floor(420 / n)), off = 70;
    var alto = off + n * cel + 6, c = '';
    ks.forEach(function (a, i) {
      c += '<text x="' + (off - 8) + '" y="' + (off + i * cel + cel / 2 + 4) + '" text-anchor="end" class="pfr-tick pfr-tick--b">' + esc(nombres[a] || a) + '</text>';
      c += '<text x="' + (off + i * cel + cel / 2) + '" y="' + (off - 10) + '" text-anchor="middle" class="pfr-tick pfr-tick--b">' + esc(nombres[a] || a) + '</text>';
      ks.forEach(function (b, j) {
        var v = i === j ? 1 : corr(rbt[a], rbt[b]), col = v >= 0.7 ? MAL : v >= 0.3 ? OJO : OK;
        c += '<rect x="' + (off + j * cel + 1) + '" y="' + (off + i * cel + 1) + '" width="' + (cel - 2) + '" height="' + (cel - 2) + '" rx="4" fill="' + col + '" opacity="' + (i === j ? .12 : (0.18 + Math.abs(v) * 0.6)).toFixed(2) + '"/>' +
          (i === j ? '' : '<text x="' + (off + j * cel + cel / 2) + '" y="' + (off + i * cel + cel / 2 + 4) + '" text-anchor="middle" class="pfr-cel">' + num(v) + '</text>');
      });
    });
    return '<svg class="pfr-svg pfr-svg--sq" viewBox="0 0 ' + (off + n * cel + 6) + ' ' + alto + '" role="img">' + c + '</svg>';
  }
  function barras(items, ref, fmt) {
    var max = Math.max.apply(null, items.map(function (x) { return x.v; }).concat([ref.v])) * 1.15 || 1;
    return '<div class="pfr-bars">' + items.map(function (x) {
      return '<div class="pfr-bar"><span class="pfr-bar__n">' + esc(x.n) + '<small>' + pct(x.w, 0) + ' de la cartera</small></span>' +
        '<span class="pfr-bar__t"><i style="width:' + (x.v / max * 100).toFixed(1) + '%"></i><em style="left:' + (ref.v / max * 100).toFixed(1) + '%"></em></span>' +
        '<b>' + fmt(x.v) + '</b></div>';
    }).join('') + '<p class="pfr-bars__ref"><em></em>' + esc(ref.t) + '</p></div>';
  }

  /* ------------------------------ textos ------------------------------ */
  function segunPerfil(key, valor) {
    var p = perfil();
    if (!p) return '<p class="pfr-p">Hacé el <button type="button" class="pfr-a" onclick="openQuiz()">test de perfil de inversor</button> y te mostramos esta métrica comparada con lo que suele aceptar alguien como vos.</p>';
    var ref = REF[key];
    if (!ref) return '';
    var lim = ref[p.i], peor = key === 'beta' || key === 'vol' ? valor > lim : valor < lim;
    var f = key === 'beta' ? function (x) { return num(x); } : function (x) { return pct(x); };
    var dir = key === 'beta' || key === 'vol' ? 'hasta' : 'no más de';
    return '<p class="pfr-p pfr-perfil ' + (peor ? 'ojo' : 'ok') + '"><b>Para tu perfil ' + esc(p.nombre) + '.</b> Como referencia orientativa, un perfil así suele convivir con ' + dir + ' <b>' + f(lim) + '</b>. ' +
      (peor ? 'Tu cartera está por encima de ese nivel: se mueve más de lo que tu perfil suele tolerar.' : 'Tu cartera está dentro de ese rango.') + '</p>';
  }
  var TXT = {
    beta: function (d) {
      var b = d.m.beta;
      return { t: 'Beta vs S&P 500', que: 'Cuánto se mueve tu cartera cuando se mueve el mercado. Con beta 1 acompaña al S&P 500 punto por punto; con 1,5 tiende a moverse un 50% más, para arriba y para abajo.',
        tuya: 'Tu cartera tiene beta <b>' + num(b) + '</b>: cuando el S&P 500 se movió 1%, tu cartera se movió en promedio ' + pct(b / 100, 2) + '. Cada punto del gráfico es un día; la línea dorada es tu cartera y la punteada, una cartera que copia al índice.',
        graf: dispersion(d.bench, d.port, b), ley: leyenda([['Tu cartera (cada día)', CART], ['Igual que el S&P 500', SPX]]) };
    },
    vol: function (d) {
      var vc = volMovil(d.port, 20), vs = volMovil(d.bench, 20);
      return { t: 'Volatilidad anual', que: 'Qué tan grandes son las subas y bajas diarias, llevadas a un año. Más volatilidad es un camino con más sobresaltos, aunque el destino sea bueno.',
        tuya: 'Tu cartera tiene <b>' + pct(d.m.volAnual) + '</b> contra <b>' + pct(d.m.benchVolAnual) + '</b> del S&P 500 en el mismo período. El gráfico muestra la volatilidad de las últimas 20 ruedas a lo largo del tiempo: así ves si los sobresaltos vienen creciendo.',
        graf: lineas([{ v: vc, c: CART }, { v: vs, c: SPX }], { fmt: function (t) { return pct(t, 0); }, area: true }), ley: leyenda([['Tu cartera', CART], ['S&P 500', SPX]]) };
    },
    sharpe: function (d) {
      return { t: 'Sharpe Ratio', que: 'Cuánto rendimiento obtuviste por cada unidad de riesgo que tomaste, después de descontar lo que paga una inversión sin riesgo. Arriba de 1 es bueno; debajo de 0, el riesgo no se pagó.',
        tuya: 'Tu cartera tiene Sharpe <b>' + num(d.m.sharpe) + '</b> y el S&P 500 <b>' + num(d.m.benchSharpe) + '</b>. Rendimiento anualizado: <b>' + pct(d.m.retAnual) + '</b> con <b>' + pct(d.m.volAnual) + '</b> de volatilidad. El gráfico muestra cómo creció $100 en cada una.',
        graf: lineas([{ v: base100(d.serie), c: CART }, { v: base100(d.benchSerie), c: SPX }], { fmt: function (t) { return '$' + Math.round(t); }, area: true, areaBase: 100, marcas: [{ v: 100, c: CART, t: 'punto de partida' }] }),
        ley: leyenda([['$100 en tu cartera', CART], ['$100 en el S&P 500', SPX]]) };
    },
    dd: function (d) {
      return { t: 'Máximo drawdown', que: 'La peor caída desde un máximo hasta el piso siguiente. Es lo que hubieras sentido si entrabas en el peor momento: mide el golpe, no el promedio.',
        tuya: 'La peor caída de tu cartera fue <b>' + pct(d.m.maxDrawdown) + '</b>; la del S&P 500, <b>' + pct(d.m.benchMaxDrawdown) + '</b>. El gráfico muestra, cada día, cuánto estabas debajo de tu último máximo.',
        graf: lineas([{ v: bajoAgua(d.serie), c: CART }, { v: bajoAgua(d.benchSerie), c: SPX }], { fmt: function (t) { return pct(t, 0); }, area: true, areaBase: 0, techoCero: true }),
        ley: leyenda([['Tu cartera debajo de su máximo', CART], ['S&P 500', SPX]]) };
    },
    corr: function (d) {
      var v = d.m.avgCorrelation;
      return { t: 'Correlación promedio', que: 'Si tus activos suben y bajan juntos o cada uno por su lado. Cerca de 1, cuando cae uno caen todos; cerca de 0, se compensan entre sí. Es la medida más directa de diversificación.',
        tuya: (v == null ? 'No hay suficientes datos para calcularla.' : 'El promedio de tu cartera es <b>' + num(v) + '</b>. ') + 'En el mapa ves cada par: en verde los que se mueven distinto (menos de 0,3), en dorado los intermedios y en rojo los que se mueven casi igual (más de 0,7).',
        graf: mapaCorr(d.rbt, d.nombres), ley: '' };
    },
    var: function (d) {
      return { t: 'VaR diario (95%)', que: 'La pérdida de un día malo: en 19 de cada 20 ruedas, tu cartera no debería caer más que esto en un solo día. El día 20 puede ser peor.',
        tuya: 'Tu VaR es <b>' + pct(d.m.var95Daily) + '</b> contra <b>' + pct(d.m.benchVar95Daily) + '</b> del S&P 500. El gráfico cuenta cuántos días tuvo tu cartera cada resultado; en rojo, el 5% de los peores días.',
        graf: histograma(d.port, d.m.var95Daily), ley: '' };
    },
    roe: function (d) { return fund(d, 'roe', 'ROE ponderado', 'Cuánto ganan las empresas que tenés por cada peso de patrimonio de sus accionistas. Es una medida de calidad del negocio: más ROE, más eficiente es la empresa para generar ganancias.', { v: 18, t: 'S&P 500, promedio histórico ~18%' }, function (x) { return num(x, 1) + '%'; }); },
    pe: function (d) { return fund(d, 'pe', 'P/E ponderado', 'Cuántos años de ganancias actuales estás pagando por cada empresa. Un P/E alto no es malo en sí: suele reflejar que el mercado espera mucho crecimiento, y por eso también más exigencia.', { v: 21, t: 'S&P 500, promedio histórico ~21x' }, function (x) { return num(x, 1) + 'x'; }); },
    div: function (d) { return fund(d, 'div', 'Dividend yield ponderado', 'Qué porcentaje de lo que vale cada empresa te devuelve por año en dividendos. Es un ingreso que llega aunque no vendas nada.', { v: 1.3, t: 'S&P 500, promedio histórico ~1,3%' }, function (x) { return num(x, 1) + '%'; }); }
  };
  function fund(d, campo, t, que, ref, fmt) {
    var items = (d.fund && d.fund.porActivo || []).filter(function (x) { return x[campo] != null && isFinite(x[campo]); }).map(function (x) { return { n: x.n, v: x[campo], w: x.w }; })
      .sort(function (a, b) { return b.w - a.w; }).slice(0, 10);
    var prom = d.fund && d.fund[campo === 'div' ? 'divYield' : campo];
    return { t: t, que: que,
      tuya: prom == null ? 'No encontramos este dato para tus posiciones.' : 'El promedio ponderado de tu cartera es <b>' + fmt(prom) + '</b>. Cada barra es una de tus posiciones, ordenadas por cuánto pesan; la marca vertical es la referencia del S&P 500.',
      graf: items.length ? barras(items, ref, fmt) : '', ley: '' };
  }

  window.PfRatios = {
    panel: function (key, d) {
      var f = TXT[key];
      if (!f || !d) return '';
      var x = f(d), valor = { beta: d.m.beta, vol: d.m.volAnual, dd: d.m.maxDrawdown, var: d.m.var95Daily }[key];
      return '<div class="pfr-in" role="region" aria-label="' + esc(x.t) + '">' +
        '<div class="pfr-head"><h3>' + esc(x.t) + '</h3><button type="button" class="pfr-x" data-pfr-cerrar aria-label="Cerrar">×</button></div>' +
        '<div class="pfr-grid"><div class="pfr-chart">' + x.graf + x.ley + '</div>' +
        '<div class="pfr-txt"><h4>Qué mide</h4><p class="pfr-p">' + x.que + '</p><h4>Tu cartera</h4><p class="pfr-p">' + x.tuya + '</p>' +
        (valor != null ? segunPerfil(key, valor) : '') +
        '<p class="pfr-disc">Herramienta educativa de autogestión. No es asesoramiento financiero ni una recomendación de inversión personalizada.</p></div></div></div>';
    }
  };
})();
