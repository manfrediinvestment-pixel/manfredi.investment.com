/* Warren IA: render de respuestas, tarjeta de informe y lector en grande.
   window.WarrenUI = { parse, render, mountCharts, card, openReader }.
   El chat (index.html) maneja la conversación y el streaming; acá solo se
   dibuja. Todo el texto del modelo se escapa antes de convertir el markdown. */
(function () {
  'use strict';

  var SITE = 'https://manfredinvestment.com';
  var LOGOS = ['aapl','abbv','adbe','amd','amzn','arm','asml','avgo','axp','bac','brk.b','c','cost','crm','crwd','dis','ggal','googl','gs','intc','intu','jnj','jpm','ko','lly','ma','mcd','meli','meta','mrk','ms','msft','mu','nflx','now','nvda','orcl','pep','pfe','pg','pltr','qcom','sap','shop','snow','spot','tsla','tsm','txn','uber','unh','v','wfc','wmt','xom','cvx','ypf','pamp','vist','loma'];

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

  // ── Separar metadatos del informe ──────────────────────────────────────
  // El worker pide que la respuesta profunda empiece con ```informe {json}```.
  function parse(text) {
    text = String(text || '');
    var meta = null;
    var m = /^\s*```informe\s*([\s\S]*?)```\s*/.exec(text);
    if (m) {
      try { meta = JSON.parse(m[1].trim()); } catch (e) { meta = { tipo: 'empresa' }; }
      text = text.slice(m[0].length);
    } else if (/^\s*```informe/.test(text)) {
      // Todavía se está escribiendo el bloque de metadatos.
      return { meta: { tipo: 'empresa', pendiente: true }, body: '' };
    }
    return { meta: meta, body: text };
  }

  // ── Markdown -> HTML ───────────────────────────────────────────────────
  // Claude a veces mete saltos de línea dentro de una celda: se juntan líneas
  // hasta completar la cantidad de pipes de la fila separadora.
  function normalizeTables(text) {
    var lines = text.split('\n'), out = [];
    var isSep = function (l) { return /^\s*\|?[\s\-:|]+\|?\s*$/.test(l) && l.indexOf('-') !== -1 && l.indexOf('|') !== -1; };
    var pipes = function (l) { return (l.match(/\|/g) || []).length; };
    for (var i = 0; i < lines.length; i++) {
      if (!isSep(lines[i])) { out.push(lines[i]); continue; }
      var expected = pipes(lines[i]); out.push(lines[i]); i++;
      var buf = '', n = 0;
      while (i < lines.length) {
        var line = lines[i];
        if (!line.trim()) { if (buf) { out.push(buf); buf = ''; n = 0; } break; }
        if (!buf && pipes(line) === 0) break;
        buf = buf ? buf + ' ' + line.trim() : line; n += pipes(line); i++;
        if (n >= expected) { out.push(buf); buf = ''; n = 0; }
      }
      if (buf) out.push(buf);
      i--;
    }
    return out.join('\n');
  }

  function inline(s) {
    s = esc(s);
    s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
    s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    s = s.replace(/(^|[\s(])\*([^*\s][^*]*?)\*(?=[\s).,;:]|$)/g, '$1<em>$2</em>');
    s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    s = s.replace(/(^|[\s(])(https?:\/\/[^\s<)]+[^\s<).,;:])/g, '$1<a href="$2" target="_blank" rel="noopener noreferrer">$2</a>');
    return s;
  }

  var NUM_CELL = /^[\s$€£US+\-−–~≈()\d.,%xX×\/BMKbpmilnd→]*\d[\s$€£US+\-−–~≈()\d.,%xX×\/BMKbpmilnd→]*$/;
  function cell(raw, tag, numCol) {
    var t = raw.trim(), bare = t.replace(/\*\*/g, '');
    var cls = [];
    if (numCol) cls.push('r');
    if (tag === 'td' && NUM_CELL.test(bare)) {
      cls.push('num');
      if (/^\+\s?[\d$]/.test(bare)) cls.push('pos');
      else if (/^[\-−–]\s?[\d$]/.test(bare)) cls.push('neg');
    }
    return '<' + tag + (cls.length ? ' class="' + cls.join(' ') + '"' : '') + '>' + inline(t) + '</' + tag + '>';
  }

  function table(rows) {
    var isSep = function (r) { return /^\s*\|?[\s\-:|]+\|?\s*$/.test(r); };
    var split = function (r) { return r.trim().replace(/^\|/, '').replace(/\|$/, '').split('|'); };
    var sepAt = rows.findIndex(isSep);
    var headRow = sepAt > 0 ? split(rows[0]) : null;
    var body = rows.filter(function (r, k) { return !isSep(r) && !(headRow && k === 0); }).map(split);
    // Columna numérica (alineada a la derecha) si la mayoría de sus celdas son números.
    var numCol = [];
    var ncols = Math.max.apply(null, body.map(function (c) { return c.length; }).concat([headRow ? headRow.length : 0]));
    for (var c = 1; c < ncols; c++) {
      var vals = body.map(function (r) { return (r[c] || '').trim(); }).filter(Boolean);
      numCol[c] = vals.length && vals.filter(function (v) { return NUM_CELL.test(v.replace(/\*\*/g, '')); }).length / vals.length >= 0.6;
    }
    var html = '<div class="wu-tbl"><table>';
    if (headRow) html += '<thead><tr>' + headRow.map(function (t, k) { return cell(t, 'th', numCol[k]); }).join('') + '</tr></thead>';
    html += '<tbody>';
    body.forEach(function (cells) {
      var lbl = cells[0] ? cells[0].trim().replace(/\*\*/g, '').toLowerCase() : '';
      var tot = /^(total|fair value|blend|valor esperado|cartera total)/.test(lbl);
      html += '<tr' + (tot ? ' class="tot"' : '') + '>' + cells.map(function (t, k) { return cell(t, 'td', numCol[k]); }).join('') + '</tr>';
    });
    return html + '</tbody></table></div>';
  }

  function slug(s, used) {
    var b = s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40) || 'sec';
    var k = b, n = 2; while (used[k]) k = b + '-' + (n++); used[k] = 1; return k;
  }

  // Devuelve { html, charts:[{id,data}], toc:[{id,title}] }
  function render(md, prefix) {
    prefix = prefix || ('wu' + Math.random().toString(36).slice(2, 7));
    md = normalizeTables(String(md || '').replace(/\r/g, ''));
    var lines = md.split('\n'), out = [], charts = [], toc = [], used = {};
    var i = 0, para = [];
    function flush() { if (para.length) { out.push('<p>' + inline(para.join(' ')) + '</p>'); para = []; } }
    while (i < lines.length) {
      var l = lines[i];
      var fence = /^\s*```(\w*)\s*$/.exec(l);
      if (fence) {
        flush();
        var lang = fence[1].toLowerCase(), buf = []; i++;
        while (i < lines.length && !/^\s*```\s*$/.test(lines[i])) buf.push(lines[i++]);
        var closed = i < lines.length; i++;
        var code = buf.join('\n').trim();
        if (lang === 'informe') continue;
        var data = null;
        if (lang === 'grafico' || lang === 'json' || lang === '') { try { data = JSON.parse(code); } catch (e) { data = null; } }
        if (data && (data.datasets || (data.data && data.data.datasets))) {
          var id = prefix + '-c' + charts.length;
          charts.push({ id: id, data: data });
          out.push('<figure class="wu-chart"' + (data.titulo ? '' : ' aria-label="Gráfico"') + '>' + (data.titulo ? '<figcaption>' + esc(data.titulo) + '</figcaption>' : '') + '<div class="wu-chart-box"><canvas id="' + id + '"></canvas></div></figure>');
        } else if (closed && lang !== 'grafico') {
          out.push('<pre class="wu-pre">' + esc(code) + '</pre>');
        }
        continue;
      }
      if (/^\s*\|.*\|\s*$/.test(l)) {
        flush(); var rows = [];
        while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) rows.push(lines[i++]);
        out.push(rows.length > 1 ? table(rows) : '<p>' + inline(rows[0]) + '</p>');
        continue;
      }
      var h = /^(#{1,4})\s+(.+?)\s*#*\s*$/.exec(l);
      if (h) {
        flush();
        var lvl = h[1].length, title = h[2].replace(/\*\*/g, '');
        if (lvl <= 2) { var sid = prefix + '-' + slug(title, used); toc.push({ id: sid, title: title }); out.push('<h2 id="' + sid + '">' + inline(title) + '</h2>'); }
        else out.push('<h3>' + inline(title) + '</h3>');
        i++; continue;
      }
      if (/^\s*([-*•])\s+/.test(l) || /^\s*\d+[.)]\s+/.test(l)) {
        flush();
        var ordered = /^\s*\d+[.)]\s+/.test(l), items = [];
        var itemRe = ordered ? /^\s*\d+[.)]\s+/ : /^\s*([-*•])\s+/;
        var start = ordered ? parseInt(l, 10) : 1;
        for (;;) {
          while (i < lines.length && itemRe.test(lines[i])) {
            var it = lines[i].replace(itemRe, ''); i++;
            while (i < lines.length && lines[i].trim() && /^\s{2,}\S/.test(lines[i])) it += ' ' + lines[i++].trim();
            items.push('<li>' + inline(it) + '</li>');
          }
          // Ítems separados por una línea en blanco siguen siendo la misma lista.
          var j = i; while (j < lines.length && !lines[j].trim()) j++;
          if (j > i && j < lines.length && itemRe.test(lines[j])) { i = j; continue; }
          break;
        }
        out.push(ordered ? '<ol' + (start > 1 ? ' start="' + start + '"' : '') + '>' + items.join('') + '</ol>' : '<ul>' + items.join('') + '</ul>');
        continue;
      }
      if (/^\s*(---+|\*\*\*+)\s*$/.test(l)) { flush(); out.push('<hr>'); i++; continue; }
      if (/^\s*>\s?/.test(l)) { flush(); var q = []; while (i < lines.length && /^\s*>\s?/.test(lines[i])) q.push(lines[i++].replace(/^\s*>\s?/, '')); out.push('<blockquote>' + inline(q.join(' ')) + '</blockquote>'); continue; }
      if (!l.trim()) { flush(); i++; continue; }
      if (/^Análisis educativo de Manfredi Investment/.test(l.trim())) { flush(); out.push('<p class="wu-disc">' + inline(l.trim()) + '</p>'); i++; continue; }
      para.push(l.trim()); i++;
    }
    flush();
    return { html: out.join('\n'), charts: charts, toc: toc };
  }

  // ── Gráficos con la paleta del sitio ────────────────────────────────────
  var PALETTE = ['#f2c94c', '#6fb1e8', '#56c793', '#f07b70', '#b59cf0', '#e8a35a', '#7fd3d0', '#d58bc4'];
  function mountCharts(charts) {
    if (!charts || !charts.length) return;
    if (typeof Chart === 'undefined') { setTimeout(function () { mountCharts(charts); }, 300); return; }
    charts.forEach(function (c) {
      var el = document.getElementById(c.id);
      if (!el || el._wuChart) return;
      var d = c.data;
      if (!d.datasets && d.data) { d.datasets = d.data.datasets; d.labels = d.labels || d.data.labels; }
      var raw = String(d.tipo || 'barra').toLowerCase();
      var type = { linea: 'line', line: 'line', area: 'line', barra: 'bar', barras: 'bar', bar: 'bar', torta: 'doughnut', pie: 'doughnut', dona: 'doughnut', doughnut: 'doughnut' }[raw] || 'bar';
      var round = type === 'doughnut';
      var cfg = {
        type: type,
        data: {
          labels: d.labels || [],
          datasets: (d.datasets || []).map(function (ds, i) {
            var col = PALETTE[i % PALETTE.length];
            return {
              label: ds.nombre || ds.label || '', data: ds.datos || ds.data || [],
              backgroundColor: round ? PALETTE : (type === 'line' ? col + '26' : col),
              borderColor: round ? '#0b1629' : col, borderWidth: round ? 2 : (type === 'line' ? 2 : 0),
              borderRadius: type === 'bar' ? 3 : 0, fill: raw === 'area', tension: .3,
              pointRadius: type === 'line' ? 2.5 : 0, maxBarThickness: 46
            };
          })
        },
        options: {
          responsive: true, maintainAspectRatio: false, animation: { duration: 500 },
          plugins: {
            legend: { display: round || (d.datasets || []).length > 1, labels: { color: '#c9d5e6', font: { family: 'IBM Plex Sans', size: 11 }, boxWidth: 10, boxHeight: 10 } },
            tooltip: { backgroundColor: '#0b1629', borderColor: 'rgba(242,201,76,.35)', borderWidth: 1, titleFont: { family: 'IBM Plex Sans' }, bodyFont: { family: 'IBM Plex Mono' } }
          },
          scales: round ? {} : {
            x: { ticks: { color: '#9fb3cf', font: { family: 'IBM Plex Sans', size: 10.5 } }, grid: { display: false }, border: { color: 'rgba(214,226,244,.18)' } },
            y: { ticks: { color: '#9fb3cf', font: { family: 'IBM Plex Mono', size: 10.5 } }, grid: { color: 'rgba(214,226,244,.07)' }, border: { display: false }, beginAtZero: type === 'bar' }
          }
        }
      };
      try { el._wuChart = new Chart(el, cfg); } catch (e) { /* un gráfico mal armado no rompe la respuesta */ }
    });
  }

  // ── Piezas compartidas ─────────────────────────────────────────────────
  var POSTURA = { CONSTRUCTIVA: 'up', NEUTRAL: 'n', CAUTELOSA: 'dn' };
  function chip(postura) {
    var p = String(postura || '').toUpperCase();
    if (!POSTURA[p]) return '';
    return '<span class="wu-chip wu-chip--' + POSTURA[p] + '">' + esc(p.charAt(0) + p.slice(1).toLowerCase()) + '</span>';
  }
  function money(v, cur) {
    if (v == null || !isFinite(v)) return null;
    var s = Number(v).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    return (cur === 'ARS' ? '$' : 'US$') + ' ' + s;
  }
  function upside(meta) {
    if (!meta || !(meta.fair_value > 0) || !(meta.precio > 0)) return null;
    return meta.fair_value / meta.precio - 1;
  }
  function pctTxt(x) { return (x >= 0 ? '+' : '−') + Math.abs(x * 100).toFixed(1).replace('.', ',') + '%'; }
  function logos(meta, size) {
    var t = (meta && meta.tickers) || [];
    return t.slice(0, 3).map(function (tk) {
      var k = String(tk).toLowerCase();
      var mono = '<span class="wu-logo wu-logo--' + size + ' wu-logo--mono">' + esc(String(tk).toUpperCase().slice(0, 4)) + '</span>';
      if (LOGOS.indexOf(k) === -1) return mono;
      return '<img class="wu-logo wu-logo--' + size + '" src="/assets/logos/' + encodeURIComponent(k) + '.png" alt="' + esc(tk) + '" onerror="this.outerHTML=\'' + mono.replace(/'/g, '&#39;').replace(/"/g, '&quot;') + '\'">';
    }).join('');
  }
  function fecha(ts) {
    return new Date(ts || Date.now()).toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' }).replace('.', '');
  }
  var TIPO = { empresa: 'Análisis de empresa', comparacion: 'Comparación', sector: 'Análisis sectorial', cartera: 'Análisis de cartera', macro: 'Análisis macro' };

  function stats(body) {
    var secs = (body.match(/^##\s/gm) || []).length;
    var tbls = (normalizeTables(body).match(/^\s*\|[\s\-:|]+\|\s*$/gm) || []).length;
    var ch = (body.match(/^\s*```grafico/gm) || []).length;
    var words = body.split(/\s+/).filter(Boolean).length;
    return { secs: secs, tbls: tbls, ch: ch, mins: Math.max(1, Math.round(words / 220)) };
  }

  // ── Tarjeta en el chat ─────────────────────────────────────────────────
  // state: { working, steps:[label], elapsed, section, ts }
  function card(text, state) {
    state = state || {};
    var p = parse(text), meta = p.meta || {}, st = stats(p.body);
    var up = upside(meta);
    var title = meta.titulo || (meta.tickers || []).join(' vs ') || 'Informe de Warren';
    var h = '<div class="wu-card' + (state.working ? ' is-working' : '') + '">';
    h += '<div class="wu-card__top">' + logos(meta, 'sm') + '<span class="wu-card__t">' + esc(title) + '</span>' + chip(meta.postura) + '</div>';
    if (meta.fair_value > 0) {
      h += '<div class="wu-card__fv"><span class="wu-card__fvv">' + esc(money(meta.fair_value, meta.moneda)) + '</span>'
        + (up != null ? '<span class="wu-chip wu-chip--' + (up >= 0 ? 'up' : 'dn') + '">' + pctTxt(up) + '</span>' : '') + '</div>';
    }
    if (state.working) {
      var last = (state.steps || []).slice(-3);
      h += '<div class="wu-steps">' + last.map(function (s, i) { return '<span class="' + (i === last.length - 1 ? 'run' : 'ok') + '">' + esc(s) + '</span>'; }).join('') + '</div>';
      h += '<div class="wu-card__meta">' + (state.section ? 'Escribiendo: ' + esc(state.section) : 'Trabajando') + ' · ' + esc(state.elapsed || '0:00') + '</div>';
      h += '<button type="button" class="wu-btn wu-btn--ghost" data-wu-open>Ver en vivo</button>';
    } else {
      h += '<div class="wu-card__meta">' + esc(TIPO[meta.tipo] || 'Informe') + ' · ' + st.secs + ' secciones · ' + st.tbls + ' tablas' + (st.ch ? ' · ' + st.ch + (st.ch === 1 ? ' gráfico' : ' gráficos') : '') + ' · ' + st.mins + ' min de lectura</div>';
      h += '<button type="button" class="wu-btn wu-btn--gold" data-wu-open>Abrir informe</button>';
    }
    return h + '</div>';
  }

  // ── Lector en grande ───────────────────────────────────────────────────
  var R = null; // lector abierto

  function plainText(text) {
    var p = parse(text);
    return p.body.replace(/^\s*```grafico[\s\S]*?```\s*$/gm, '').replace(/\*\*/g, '').replace(/^#{1,4}\s*/gm, '').replace(/\n{3,}/g, '\n\n').trim()
      + '\n\n— Warren IA · Manfredi Investment · ' + SITE;
  }

  function toast(msg) {
    if (!R) return;
    var t = R.el.querySelector('.wr-toast');
    t.textContent = msg; t.classList.add('on');
    clearTimeout(t._h); t._h = setTimeout(function () { t.classList.remove('on'); }, 1800);
  }
  function copy(text) {
    var done = function () { toast('Copiado'); };
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text).then(done, fallback);
    fallback();
    function fallback() {
      var ta = document.createElement('textarea'); ta.value = text; ta.style.cssText = 'position:fixed;opacity:0';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (e) { toast('No se pudo copiar'); }
      ta.remove();
    }
  }

  function header(meta, ts) {
    var up = upside(meta);
    var title = meta.titulo || (meta.tickers || []).join(' vs ') || 'Informe de Warren';
    var h = '<header class="wr-head">';
    h += '<div class="wr-brand"><span class="wr-brand__m">Manfredi Investment</span><span class="wr-brand__s">Warren IA · ' + esc(TIPO[meta.tipo] || 'Informe') + '</span></div>';
    h += '<div class="wr-id">' + logos(meta, 'lg') + '<div class="wr-id__txt"><h1 class="wr-title">' + esc(title) + '</h1><div class="wr-sub">'
      + esc(((meta.tickers || []).join(' · ') ? (meta.tickers || []).join(' · ') + ' · ' : '') + fecha(ts)) + '</div></div></div>';
    var cells = [];
    if (meta.postura) cells.push('<div><small>Postura</small>' + chip(meta.postura) + '</div>');
    if (meta.fair_value > 0) cells.push('<div><small>Fair value</small><strong>' + esc(money(meta.fair_value, meta.moneda)) + '</strong></div>');
    if (meta.precio > 0) cells.push('<div><small>Precio</small><strong>' + esc(money(meta.precio, meta.moneda)) + '</strong></div>');
    if (up != null) cells.push('<div><small>Potencial</small><strong class="' + (up >= 0 ? 'pos' : 'neg') + '">' + pctTxt(up) + '</strong></div>');
    if (cells.length) h += '<div class="wr-fv">' + cells.join('') + '</div>';
    return h + '</header>';
  }

  function paint(text, done) {
    if (!R) return;
    var p = parse(text), meta = p.meta || {};
    var r = render(p.body, 'wr');
    R.text = text;
    R.el.querySelector('.wr-doc').innerHTML = header(meta, R.ts) + '<div class="wr-body wu-md">' + r.html + '</div>'
      + (done ? '' : '<div class="wr-live"><span class="wu-dot"></span>Warren está escribiendo…</div>');
    R.el.querySelector('.wr-toc').innerHTML = r.toc.map(function (t, i) {
      return '<a href="#' + t.id + '" data-wr-to="' + t.id + '"><span>' + String(i + 1).padStart(2, '0') + '</span>' + esc(t.title) + '</a>';
    }).join('');
    R.el.querySelector('.wr-t').textContent = meta.titulo || 'Informe de Warren';
    R.el.querySelector('.wr-x').disabled = false;
    R.el.querySelectorAll('[data-wr-act]').forEach(function (b) { b.disabled = !done; });
    mountCharts(r.charts);
    R.done = !!done;
  }

  function close() {
    if (!R) return;
    var el = R.el; R = null;
    document.removeEventListener('keydown', onKey);
    el.classList.remove('on'); el.classList.add('off');
    document.documentElement.classList.remove('wr-open');
    setTimeout(function () { el.remove(); }, 200);
  }
  function onKey(e) { if (e.key === 'Escape') close(); }

  // opts: { ts, live } -> { update(text, done), close(), isOpen() }
  function openReader(text, opts) {
    opts = opts || {};
    if (R) close();
    var el = document.createElement('div');
    el.className = 'wr';
    el.setAttribute('role', 'dialog'); el.setAttribute('aria-modal', 'true'); el.setAttribute('aria-label', 'Informe de Warren');
    el.innerHTML = '<div class="wr-scrim" data-wr-close></div>'
      + '<div class="wr-panel">'
      + '<div class="wr-top"><span class="wr-av" aria-hidden="true">W</span><span class="wr-t"></span>'
      + '<div class="wr-tools">'
      + '<button type="button" class="wu-btn wu-btn--ghost" data-wr-act="copy" title="Copiar el texto"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg><span>Copiar</span></button>'
      + '<button type="button" class="wu-btn wu-btn--ghost" data-wr-act="share" title="Compartir"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12v7a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-7M16 6l-4-4-4 4M12 2v13"/></svg><span>Compartir</span></button>'
      + '<button type="button" class="wu-btn wu-btn--gold" data-wr-act="pdf" title="Descargar en PDF"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12m0 0-4-4m4 4 4-4M4 21h16"/></svg><span>PDF</span></button>'
      + '<button type="button" class="wr-x" data-wr-close aria-label="Cerrar"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg></button>'
      + '</div></div>'
      + '<div class="wr-main"><nav class="wr-toc" aria-label="Secciones"></nav><article class="wr-scroll"><div class="wr-doc"></div>'
      + '<footer class="wr-foot">Análisis generado por Warren IA, el analista de Manfredi Investment. Educativo: no constituye asesoramiento financiero regulado. manfredinvestment.com</footer></article></div>'
      + '<div class="wr-toast" role="status" aria-live="polite"></div>'
      + '</div>';
    document.body.appendChild(el);
    document.documentElement.classList.add('wr-open');
    R = { el: el, ts: opts.ts || Date.now(), text: '', done: false };

    el.addEventListener('click', function (e) {
      var c = e.target.closest('[data-wr-close]'); if (c) { close(); return; }
      var to = e.target.closest('[data-wr-to]');
      if (to) { e.preventDefault(); var t = document.getElementById(to.getAttribute('data-wr-to')); if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' }); return; }
      var a = e.target.closest('[data-wr-act]'); if (!a || !R) return;
      var act = a.getAttribute('data-wr-act');
      var meta = parse(R.text).meta || {};
      if (act === 'copy') copy(plainText(R.text));
      if (act === 'share') {
        var title = (meta.titulo || 'Informe') + ' · Warren IA';
        if (navigator.share) navigator.share({ title: title, text: plainText(R.text) }).catch(function () {});
        else copy(plainText(R.text));
      }
      if (act === 'pdf') {
        var prev = document.title;
        document.title = (meta.titulo || 'Informe') + ' - Warren IA - Manfredi Investment';
        window.print();
        setTimeout(function () { document.title = prev; }, 500);
      }
    });
    document.addEventListener('keydown', onKey);
    requestAnimationFrame(function () { requestAnimationFrame(function () { if (R && R.el === el) { el.classList.add('on'); el.querySelector('.wr-x').focus({ preventScroll: true }); } }); });

    paint(text, !opts.live);
    return {
      update: function (t, d) { if (R && R.el === el) paint(t, d); },
      close: close,
      isOpen: function () { return !!(R && R.el === el); }
    };
  }

  window.WarrenUI = { parse: parse, render: render, mountCharts: mountCharts, card: card, openReader: openReader, esc: esc };
})();
