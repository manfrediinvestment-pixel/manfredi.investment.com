// Helpers de gráficos para los clips "a cámara". Arman DOM estático (determinista);
// cada sección anima lo que devuelven con su propia timeline de GSAP (seek-safe).
window.MC = {
  // Barras verticales. cfg: {labels, values, max, fmt, colors, w, h, gap, notes}
  vbars: function (el, cfg) {
    el.classList.add('vb');
    el.style.width = cfg.w + 'px'; el.style.height = cfg.h + 'px';
    var n = cfg.values.length, gap = cfg.gap || 36, bw = (cfg.w - gap * (n - 1)) / n;
    var out = { bars: [], vals: [], labs: [], notes: [] };
    cfg.values.forEach(function (v, i) {
      var col = document.createElement('div'); col.className = 'vb-col';
      col.style.left = (i * (bw + gap)) + 'px'; col.style.width = bw + 'px';
      var bh = (cfg.h - 150) * v / cfg.max;
      var bar = document.createElement('div'); bar.className = 'vb-bar';
      bar.style.height = bh + 'px'; bar.style.background = cfg.colors[i];
      if (cfg.outline && cfg.outline[i]) { bar.style.background = 'transparent'; bar.style.border = '3px dashed ' + cfg.colors[i]; }
      var val = document.createElement('div'); val.className = 'vb-val'; val.textContent = cfg.fmt(v);
      val.style.bottom = (bh + 70) + 'px'; val.style.color = cfg.valColors ? cfg.valColors[i] : '';
      var lab = document.createElement('div'); lab.className = 'vb-lab'; lab.textContent = cfg.labels[i];
      col.appendChild(bar); col.appendChild(val); col.appendChild(lab);
      if (cfg.notes && cfg.notes[i]) {
        var nt = document.createElement('div'); nt.className = 'vb-note'; nt.textContent = cfg.notes[i];
        nt.style.bottom = (bh + 128) + 'px'; col.appendChild(nt); out.notes.push(nt);
      }
      el.appendChild(col); out.bars.push(bar); out.vals.push(val); out.labs.push(lab);
    });
    return out;
  },
  // Barras horizontales. cfg: {labels, values, max, fmt, colors, w, rowH, labW, subs}
  hbars: function (el, cfg) {
    el.classList.add('hb');
    var out = { bars: [], vals: [], rows: [] };
    cfg.values.forEach(function (v, i) {
      var row = document.createElement('div'); row.className = 'hb-row'; row.style.height = cfg.rowH + 'px';
      var lab = document.createElement('div'); lab.className = 'hb-lab'; lab.style.width = cfg.labW + 'px';
      lab.innerHTML = cfg.labels[i] + (cfg.subs && cfg.subs[i] ? '<span>' + cfg.subs[i] + '</span>' : '');
      if (cfg.labColors && cfg.labColors[i]) lab.style.color = cfg.labColors[i];
      var track = document.createElement('div'); track.className = 'hb-track';
      var bar = document.createElement('div'); bar.className = 'hb-bar';
      bar.style.width = Math.max(10, (cfg.w * v / cfg.max)) + 'px'; bar.style.background = cfg.colors[i];
      bar.style.height = (cfg.barH || 64) + 'px';
      var val = document.createElement('div'); val.className = 'hb-val'; val.textContent = cfg.fmt(v);
      if (cfg.valColors) val.style.color = cfg.valColors[i];
      track.appendChild(bar); track.appendChild(val);
      row.appendChild(lab); row.appendChild(track); el.appendChild(row);
      out.bars.push(bar); out.vals.push(val); out.rows.push(row);
    });
    return out;
  },
  // Línea con puntos. cfg: {labels, values, min, max, w, h, fmt, color}
  line: function (el, cfg) {
    var NS = 'http://www.w3.org/2000/svg';
    el.style.width = cfg.w + 'px'; el.style.height = cfg.h + 'px'; el.classList.add('ln');
    var svg = document.createElementNS(NS, 'svg'); svg.setAttribute('width', cfg.w); svg.setAttribute('height', cfg.h);
    svg.style.overflow = 'visible';
    var padX = cfg.padX || 70, top = 90, bot = cfg.h - 80, n = cfg.values.length;
    function X(i) { return padX + (cfg.w - 2 * padX) * i / (n - 1); }
    function Y(v) { return top + (bot - top) * (cfg.max - v) / (cfg.max - cfg.min); }
    var d = ''; cfg.values.forEach(function (v, i) { d += (i ? 'L' : 'M') + X(i) + ',' + Y(v); });
    var path = document.createElementNS(NS, 'path'); path.setAttribute('d', d); path.setAttribute('fill', 'none');
    path.setAttribute('stroke', cfg.color); path.setAttribute('stroke-width', 7);
    path.setAttribute('stroke-linejoin', 'round'); path.setAttribute('stroke-linecap', 'round');
    svg.appendChild(path); el.appendChild(svg);
    var out = { path: path, dots: [], vals: [], labs: [], X: X, Y: Y };
    cfg.values.forEach(function (v, i) {
      var c = document.createElementNS(NS, 'circle'); c.setAttribute('cx', X(i)); c.setAttribute('cy', Y(v));
      c.setAttribute('r', cfg.r ? cfg.r[i] : 12); c.setAttribute('fill', cfg.dotColors ? cfg.dotColors[i] : cfg.color);
      svg.appendChild(c); out.dots.push(c);
      var val = document.createElement('div'); val.className = 'ln-val'; val.textContent = cfg.fmt(v);
      val.style.left = X(i) + 'px'; val.style.top = (Y(v) - 78) + 'px';
      if (cfg.valColors) val.style.color = cfg.valColors[i];
      var lab = document.createElement('div'); lab.className = 'ln-lab'; lab.textContent = cfg.labels[i];
      lab.style.left = X(i) + 'px'; lab.style.top = (cfg.h - 40) + 'px';
      el.appendChild(val); el.appendChild(lab); out.vals.push(val); out.labs.push(lab);
    });
    var len = path.getTotalLength(); path.style.strokeDasharray = len; path.style.strokeDashoffset = len;
    out.len = len;
    return out;
  }
};
