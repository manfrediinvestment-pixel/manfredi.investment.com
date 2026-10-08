/* Pestaña Calendario: arma la tabla de la semana con los tres JSON del worker
   manfredi-calendario (económico, earnings y dividendos). Cada evento económico
   linkea a su fuente oficial (calSourceFor, en index.html) y cada empresa a su
   informe. Los campos opcionales hora, relevancia (1-3), previo, consenso y dato
   ganan si vienen en el JSON; si no, se sacan de la descripción. */
(function () {
  var API = 'https://manfredi-calendario.nachito2502.workers.dev/';
  var tabla = document.getElementById('calTabla');
  var tabs = document.getElementById('calTabs');
  if (!tabla || !tabs) return;

  var MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var NOMBRE = { aapl: 'Apple', abbv: 'AbbVie', adbe: 'Adobe', amd: 'AMD', amzn: 'Amazon', arm: 'Arm', asml: 'ASML', avgo: 'Broadcom', axp: 'American Express', bac: 'Bank of America', 'brk.b': 'Berkshire Hathaway', c: 'Citigroup', cost: 'Costco', crm: 'Salesforce', crwd: 'CrowdStrike', dis: 'Disney', googl: 'Alphabet', gs: 'Goldman Sachs', intc: 'Intel', intu: 'Intuit', jnj: 'Johnson & Johnson', jpm: 'JPMorgan Chase', ko: 'Coca-Cola', lly: 'Eli Lilly', ma: 'Mastercard', meta: 'Meta', ms: 'Morgan Stanley', msft: 'Microsoft', mu: 'Micron', nflx: 'Netflix', now: 'ServiceNow', nvda: 'Nvidia', orcl: 'Oracle', pep: 'PepsiCo', pfe: 'Pfizer', pg: 'Procter & Gamble', pltr: 'Palantir', qcom: 'Qualcomm', sap: 'SAP', shop: 'Shopify', snow: 'Snowflake', spot: 'Spotify', tsla: 'Tesla', tsm: 'TSMC', txn: 'Texas Instruments', uber: 'Uber', unh: 'UnitedHealth', v: 'Visa', wfc: 'Wells Fargo', wmt: 'Walmart' };
  var ALTA = /fomc|minutas de la fed|decisi[oó]n de tasas|\bipc\b|\bcpi\b|inflaci|n[oó]minas|nonfarm|payroll|\bpce\b|\bpbi\b|\bgdp\b|desempleo|jobless|\bism\b|michigan|\brem\b|relevamiento de expectativas|licitaci|manufacturer/i;
  var BAJA = /pesquer|servicios p[uú]blicos|s&p global|turismo|supermercados|centros de compras/i;
  var FILTROS = [['todo', 'Todo'], ['ar', 'Argentina'], ['us', 'EE.UU.'], ['|'], ['earnings', 'Resultados'], ['dividend', 'Dividendos']];
  var filtro = 'todo', dias = null;

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  // hora y fecha de hoy en Buenos Aires
  function ahoraART() {
    var p = {};
    new Intl.DateTimeFormat('en-US', { timeZone: 'America/Argentina/Buenos_Aires', year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric', hourCycle: 'h23' })
      .formatToParts(new Date()).forEach(function (x) { p[x.type] = +x.value; });
    return { fecha: p.day + '/' + p.month, d: p.day, m: p.month, min: p.hour * 60 + p.minute };
  }

  function titulo(t) {
    var m = t.match(/^(?:INDEC|BCRA)\s*[–-]\s*(.+)$/);
    if (m) t = m[1];
    t = t.replace(/,\s*[A-Z]{2,6}\b[^(,]*\(/, ' (');
    var en = t.match(/^(.+?)\s+-\s+[A-Z][^(]*?(\s*\(.+\))?$/);
    if (en) t = en[1] + (en[2] || '');
    return t.replace(/\(([A-ZÁÉÍÓÚ])([a-záéíóú]+)(?:\s+\d{4})?\)/, function (a, b, c) { return '(' + b.toLowerCase() + c + ')'; });
  }
  function hora(e) {
    if (e.hora) return e.hora;
    var d = e.descripcion || '';
    var m = d.match(/a las (\d{1,2}[:.]\d{2})\s*(?:hs\s*)?ART/i);
    if (m) return m[1].replace('.', ':');
    if (/al cierre de la jornada/i.test(d)) return 'Cierre';
    if (/^INDEC/.test(e.titulo || '')) return '16:00';
    if (/jobless|seguro de desempleo/i.test(e.titulo + ' ' + d)) return '9:30';
    return '';
  }
  function cifra(d, re) { var m = d.match(re); return m ? m[1].replace(/[.,]$/, '') : ''; }
  function minutos(h) { var m = /^(\d{1,2}):(\d{2})$/.exec(h); return m ? +m[1] * 60 + +m[2] : h === 'Cierre' ? 18 * 60 : null; }

  function normalizar(eco, earn, divs) {
    var hoy = ahoraART();
    return eco.dias.map(function (dia, i) {
      var f = String(dia.fecha || '').split('/'), d = +f[0], mes = +f[1];
      var rel = mes < hoy.m || (mes === hoy.m && d < hoy.d) ? 'pasado' : (dia.fecha === hoy.fecha ? 'hoy' : 'futuro');
      var evs = [];
      (dia.eventos || []).forEach(function (e) {
        var desc = e.descripcion || '';
        evs.push({
          tipo: e.tipo, titulo: titulo(e.titulo || ''), orig: e, hora: hora(e),
          imp: +e.relevancia || (ALTA.test(e.titulo) ? 3 : BAJA.test(e.titulo) ? 1 : 2),
          previo: e.previo || cifra(desc, /(?:[Pp]revio:?|final:)\s+(-?[\d.,]+\s?[KBM%]?)/),
          consenso: e.consenso || cifra(desc, /consenso[^:]*:\s+(-?[\d.,]+\s?[KBM%]?)/i),
          dato: e.dato || '', desc: desc, src: typeof calSourceFor === 'function' ? calSourceFor(e) : null
        });
      });
      [[earn, 'earnings'], [divs, 'dividend']].forEach(function (par) {
        var dd = par[0] && par[0].dias && par[0].dias[i];
        ((dd && dd.eventos) || []).forEach(function (e) {
          var tk = String(e.ticker || '').toLowerCase(), desc = e.descripcion || '';
          var pago = /pago/i.test(e.titulo || '');
          var nombre = NOMBRE[tk] || tk.toUpperCase();
          evs.push({
            tipo: par[1], ticker: tk, orig: e, desc: desc, imp: par[1] === 'earnings' ? 2 : 1,
            titulo: par[1] === 'earnings' ? nombre + ' presenta resultados' : nombre + (pago ? ' paga su dividendo' : ' cotiza ex-dividendo'),
            sub: par[1] === 'earnings' ? (desc.split(/[·.]/)[1] || '').replace(/\s*\(.*\)/, '').trim() : (cifra(desc, /((?:US|NT|R|€)?\$\s?[\d.,]+)/) + ' por acción' + (pago ? '' : (cifra(desc, /pago:\s*(\d+\/\d+)/) ? ' · pago ' + cifra(desc, /pago:\s*(\d+\/\d+)/) : ''))),
            hora: par[1] === 'earnings' ? (hora(e) || '') : (pago ? 'Pago' : 'Ex')
          });
        });
      });
      evs.sort(function (a, b) {
        var ka = a.hora === 'Ex' || a.hora === 'Pago' ? -1 : (minutos(a.hora) == null ? 9999 : minutos(a.hora));
        var kb = b.hora === 'Ex' || b.hora === 'Pago' ? -1 : (minutos(b.hora) == null ? 9999 : minutos(b.hora));
        return ka - kb;
      });
      return { nombre: dia.nombre, fecha: dia.fecha, num: d, mes: mes, rel: rel, eventos: evs, ahora: hoy.min };
    });
  }

  function imp(n) { return '<span class="cal-imp n' + n + '" title="Relevancia ' + ['', 'baja', 'media', 'alta'][n] + '" aria-label="Relevancia ' + ['', 'baja', 'media', 'alta'][n] + '"><i></i><i></i><i></i></span>'; }
  function logo(tk) { return '<img class="cal-logo" src="assets/logos/' + tk.replace('.', '-') + '.png" alt="" loading="lazy" onerror="this.style.visibility=\'hidden\'">'; }
  function esEmpresa(e) { return e.tipo === 'earnings' || e.tipo === 'dividend'; }
  function linkInforme(tk) { return 'informes/' + tk + '.html'; }
  function cuenta(f) { var n = 0; dias.forEach(function (d) { d.eventos.forEach(function (e) { if (f === 'todo' || e.tipo === f) n++; }); }); return n; }

  function pintarTabs() {
    tabs.innerHTML = FILTROS.map(function (f) {
      if (f[0] === '|') return '<span class="sep" aria-hidden="true"></span>';
      return '<button type="button" data-f="' + f[0] + '" aria-pressed="' + (f[0] === filtro) + '" class="' + (f[0] === filtro ? 'on' : '') + '">' + f[1] + '<em>' + cuenta(f[0]) + '</em></button>';
    }).join('');
  }

  function celdaDato(e, d) {
    if (esEmpresa(e)) return '<span class="cal-pub">—</span>';
    if (e.dato) return '<span class="dato">' + esc(e.dato) + '</span>';
    var m = minutos(e.hora);
    if (d.rel === 'pasado' || (d.rel === 'hoy' && m != null && d.ahora >= m)) return '<span class="cal-pub">Publicado</span>';
    return '<span class="cal-pend">' + (m != null && e.hora !== 'Cierre' ? 'a las ' + e.hora : e.hora === 'Cierre' ? 'al cierre' : 'pendiente') + '</span>';
  }

  function pintarTabla() {
    var h = '', k = 0;
    dias.forEach(function (d) {
      var evs = d.eventos.filter(function (e) { return filtro === 'todo' || e.tipo === filtro; });
      if (!evs.length) return;
      h += '<tr class="dh"><td colspan="6"><b>' + esc(d.nombre) + ' ' + d.num + '</b>' + (d.rel === 'hoy' ? ' <span class="hoy">Hoy</span>' : '<span>' + evs.length + (evs.length === 1 ? ' evento' : ' eventos') + '</span>') + '</td></tr>';
      evs.forEach(function (e) {
        k++;
        var url = esEmpresa(e) ? linkInforme(e.ticker) : (e.src && e.src.url);
        var ext = !esEmpresa(e);
        var a1 = url ? '<a href="' + esc(url) + '"' + (ext ? ' target="_blank" rel="noopener noreferrer"' : '') + '>' : '', a2 = url ? '</a>' : '';
        var ev = esEmpresa(e)
          ? '<div class="co">' + logo(e.ticker) + '<div>' + a1 + '<b>' + esc(e.titulo) + '</b>' + a2 + '<small>' + esc(e.sub) + '</small></div></div>'
          : a1 + '<b>' + esc(e.titulo) + '</b>' + a2 + '<span class="cal-fl ' + e.tipo + '">' + (e.tipo === 'ar' ? 'Argentina' : 'EE.UU.') + '</span>' + (e.src && e.src.fuente ? ' <small>· ' + esc(e.src.fuente) + '</small>' : '');
        var t = /\d/.test(e.hora) ? esc(e.hora) : '<small>' + (e.hora === 'Ex' ? 'Ex-div.' : esc(e.hora) || '—') + '</small>';
        h += '<tr class="row' + (d.rel === 'pasado' ? ' ps' : '') + '" data-k="' + k + '" tabindex="0" aria-expanded="false"><td class="t">' + t + '</td><td class="e">' + ev + '</td><td class="hide-m">' + imp(e.imp) + '</td>' +
          '<td class="r n hide-m">' + (esc(e.previo) || '—') + '</td><td class="r n hide-m">' + (esc(e.consenso) || '—') + '</td><td class="r">' + celdaDato(e, d) + '</td></tr>' +
          '<tr class="det" data-d="' + k + '" hidden><td colspan="6">' + esc(e.desc) +
          (url ? '<br><a href="' + esc(url) + '"' + (ext ? ' target="_blank" rel="noopener noreferrer">Ver el dato en ' + esc((e.src && e.src.fuente) || 'la fuente') + ' ↗' : '>Leer el informe de ' + esc(e.ticker.toUpperCase()) + ' →') + '</a>' : '') + '</td></tr>';
      });
    });
    tabla.innerHTML = h
      ? '<table class="cal-tbl"><thead><tr><th>Hora</th><th>Evento</th><th class="hide-m">Relevancia</th><th class="r hide-m">Previo</th><th class="r hide-m">Consenso</th><th class="r">Dato</th></tr></thead><tbody>' + h + '</tbody></table>'
      : '<p class="cal-vacio">No hay eventos de este tipo esta semana.</p>';
  }

  function pintarEmpresas() {
    var box = document.getElementById('calEmpresas');
    if (!box) return;
    var h = '';
    dias.forEach(function (d) {
      d.eventos.forEach(function (e) {
        if (!esEmpresa(e)) return;
        h += '<a class="cal-co" href="' + linkInforme(e.ticker) + '">' + logo(e.ticker) + '<div><b>' + esc(e.titulo) + '</b><small>' + esc(e.sub) + '</small></div><time>' + esc(d.nombre.slice(0, 3)) + ' ' + d.num + '</time></a>';
      });
    });
    box.innerHTML = '<h3 class="cal-card__h">Empresas esta semana</h3>' + (h || '<p class="cal-nada">Ninguna empresa de Inversiones presenta resultados ni paga dividendos esta semana.</p>');
  }

  function semana(d0, d1) {
    var meta = document.getElementById('calSemanaMeta');
    if (!meta || !d0) return;
    meta.textContent = 'Semana del ' + d0.num + (d0.mes !== d1.mes ? ' de ' + MESES[d0.mes - 1] : '') + ' al ' + d1.num + ' de ' + MESES[d1.mes - 1];
  }

  tabs.addEventListener('click', function (ev) {
    var b = ev.target.closest('button[data-f]');
    if (!b || !dias) return;
    filtro = b.dataset.f;
    pintarTabs(); pintarTabla();
  });
  function abrir(r) {
    var det = tabla.querySelector('[data-d="' + r.dataset.k + '"]');
    if (!det) return;
    det.hidden = !det.hidden;
    r.setAttribute('aria-expanded', String(!det.hidden));
  }
  tabla.addEventListener('click', function (ev) {
    if (ev.target.closest('a')) return;
    var r = ev.target.closest('tr.row');
    if (r) abrir(r);
  });
  tabla.addEventListener('keydown', function (ev) {
    var r = ev.target.closest && ev.target.closest('tr.row');
    if (r && (ev.key === 'Enter' || ev.key === ' ')) { ev.preventDefault(); abrir(r); }
  });

  function traer(p) {
    return fetch(API + p, { signal: AbortSignal.timeout(8000) }).then(function (r) { if (!r.ok) throw new Error('status ' + r.status); return r.json(); });
  }
  Promise.all([traer('calendario'), traer('earnings').catch(function () { return null; }), traer('dividends').catch(function () { return null; })])
    .then(function (r) {
      if (!r[0] || !r[0].dias || !r[0].dias.length) throw new Error('sin datos');
      dias = normalizar(r[0], r[1], r[2]);
      semana(dias[0], dias[dias.length - 1]);
      pintarTabs(); pintarTabla(); pintarEmpresas();
    })
    .catch(function (e) {
      console.warn('[MI] Calendario:', e.message);
      tabla.innerHTML = '<p class="cal-vacio">No pudimos cargar el calendario. Probá de nuevo en un rato.</p>';
    });
})();
