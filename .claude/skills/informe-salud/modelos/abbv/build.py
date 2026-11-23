# Arma informes/abbv.html: cabecera y CSS (abbv.head.html, copia de LLY con .verdict-note en var(--muted)), cuerpo
# (abbv.body.tpl.html), motor de gráficos (engine.js de LLY) con los mismos parches para celular, y charts_abbv.js.
# Las tablas de largo variable (pares, pipeline, reversión y el cuadro PFE/ABBV/LLY/JNJ) se generan acá con tokens
# {{...}} que después reemplaza render.py, así verify.py controla también esas celdas.
import subprocess, sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()   # raíz del repo
head = open('abbv.head.html', encoding='utf-8').read()
assert '#5d646f' not in head and '.verdict-note{color:var(--muted) !important;}' in head   # CERO texto gris
eng = open('engine.js', encoding='utf-8').read()
def patch(a, b):
    global eng
    assert eng.count(a) == 1, a[:60]
    eng = eng.replace(a, b, 1)
# 1) drawHBars: el margen de las etiquetas no puede comerse el gráfico en celular; etiquetas largas en dos líneas
patch("    var padL = opts.padL || 128, padR = 54, padT = 10, padB = 10;\n",
      "    var padL = Math.min(opts.padL || 128, Math.round(W * 0.42)), padR = 54, padT = 10, padB = 10;\n")
patch("""      ctx.font = '12px "Inter", sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(labels[i], padL - 10, cy + 4);
""", """      ctx.font = '12px "Inter", sans-serif';
      ctx.textAlign = 'right';
      if(ctx.measureText(labels[i]).width > padL - 14){ ctx.font = '10.5px "Inter", sans-serif'; wrapLabel(ctx, labels[i], padL - 10, cy - 2, padL - 14, 'right'); }
      else ctx.fillText(labels[i], padL - 10, cy + 4);
""")
# 2) drawRangeBars: mismo límite de margen
patch("    var padL = opts.padL || 200, padR = 40, padT = 34, padB = 10;\n",
      "    var padL = Math.min(opts.padL || 200, Math.round(W * 0.40)), padR = 40, padT = 34, padB = 10;\n")
# 3) drawLines: la leyenda pasa a varias filas si no entra (celular) y el margen inferior crece
patch("    var padL = 40, padR = 28, padT = 16, padB = 54;\n",
      "    var padL = 40, padR = 28, padT = 16, padB = 54;\n"
      "    ctx.font = '11px \"Inter\", sans-serif'; var lrows = 1, lxx = padL; series.forEach(function(s){ var iw = 14 + ctx.measureText(s.name).width + 22; if(lxx + iw > W - 8 && lxx > padL){ lrows++; lxx = padL; } lxx += iw; }); padB += (lrows - 1) * 15;\n")
patch("    var lx = padL, ly = H - 12;\n", "    var lx = padL, ly = H - 12 - (lrows - 1) * 15;\n")
patch("    series.forEach(function(s){\n      ctx.fillStyle = s.color;\n      ctx.fillRect(lx, ly-8, 10, 10);",
      "    series.forEach(function(s){\n      var iw = 14 + ctx.measureText(s.name).width + 22; if(lx + iw > W - 8 && lx > padL){ lx = padL; ly += 15; }\n      ctx.fillStyle = s.color;\n      ctx.fillRect(lx, ly-8, 10, 10);")
# 4) drawDiverging: barras horizontales desde cero (positivas a la derecha, negativas a la izquierda)
patch("  function drawRangeBars(canvas, opts){", """  function drawDiverging(canvas, opts){
    var cssH = parseInt(canvas.getAttribute('height'), 10) || 260;
    var setup = setupCanvas(canvas, cssH);
    var ctx = setup.ctx, W = setup.w, H = setup.h;
    ctx.clearRect(0,0,W,H);
    var labels = opts.labels, values = opts.values;
    var padL = Math.min(opts.padL || 160, Math.round(W * 0.40)), padR = 56, padT = 10, padB = 10;
    var plotW = W - padL - padR - 44, plotH = H - padT - padB;
    var maxV = Math.max.apply(null, values.map(Math.abs)), minV = Math.min.apply(null, values);
    var negW = minV < 0 ? plotW * (Math.abs(minV) / (Math.abs(minV) + maxV)) : 0;
    var x0 = padL + 44 + negW, scale = (plotW - negW) / maxV;
    var n = values.length, slot = plotH / n, barH = Math.min(slot * 0.55, 24);
    ctx.strokeStyle = PALETTE.navy; ctx.lineWidth = 1.2;
    ctx.beginPath(); ctx.moveTo(x0, padT); ctx.lineTo(x0, padT + plotH); ctx.stroke();
    for(var i=0;i<n;i++){
      var cy = padT + slot*i + slot/2, v = values[i], w = v * scale;
      ctx.fillStyle = v >= 0 ? PALETTE.navy2 : PALETTE.red;
      ctx.fillRect(v >= 0 ? x0 : x0 + w, cy - barH/2, Math.abs(w), barH);
      ctx.fillStyle = PALETTE.ink; ctx.textAlign = 'right';
      ctx.font = '12px "Inter", sans-serif';
      if(ctx.measureText(labels[i]).width > padL - 14){ ctx.font = '10.5px "Inter", sans-serif'; wrapLabel(ctx, labels[i], padL - 10, cy - 2, padL - 14, 'right'); }
      else ctx.fillText(labels[i], padL - 10, cy + 4);
      ctx.font = '600 11px "IBM Plex Mono", monospace';
      var vl = opts.valueFmt ? opts.valueFmt(v) : v;
      if(v >= 0){ ctx.textAlign = 'left'; ctx.fillText(vl, x0 + w + 6, cy + 4); }
      else { ctx.textAlign = 'right'; ctx.fillText(vl, x0 + w - 6, cy + 4); }
    }
  }

  function drawRangeBars(canvas, opts){""")
M = json.load(open('model.json', encoding='utf-8'))
body = open('abbv.body.tpl.html', encoding='utf-8').read()
ch = open('charts_abbv.js', encoding='utf-8').read()
NAMES = dict(LLY='Eli Lilly', JNJ='Johnson &amp; Johnson', MRK='Merck &amp; Co.', BMY='Bristol-Myers Squibb', AMGN='Amgen', GILD='Gilead Sciences',
             NVO='Novo Nordisk', AZN='AstraZeneca', NVS='Novartis', GSK='GSK', SNY='Sanofi', REGN='Regeneron', VRTX='Vertex')
def cell(i, f, fmt, suf=''):
    return f'<td class="right-al">{{{{peer_rows.{i}.{f}|{fmt}}}}}{suf}</td>' if M['peer_rows'][i][f] is not None else '<td class="right-al">n.d.</td>'
rows = []
for i, r in enumerate(M['peer_rows']):
    rows.append(f'<tr><td class="label">{NAMES[r["t"]]} ({{{{peer_rows.{i}.t}}}})</td>' + cell(i, 'pe', 'f2', 'x') + cell(i, 'pe27', 'f2', 'x')
                + cell(i, 'peg', 'f2') + cell(i, 'eve', 'f2', 'x') + cell(i, 'dy', 'f2', '%') + cell(i, 'nde', 'f2') + '</tr>')
body = body.replace('@@PEER_ROWS@@', '\n    '.join(rows))
pr = []
for k in M['pipe']:
    pr.append(f'<tr><td class="label">{{{{pipe.{k}.name}}}}</td><td class="label">{{{{pipe.{k}.phase}}}}</td><td class="right-al">{{{{pipe.{k}.pos_pct|f1}}}}%</td>'
              f'<td class="right-al">{{{{pipe.{k}.peak|f1}}}}</td><td class="label">{{{{pipe.{k}.src}}}}</td><td class="right-al">{{{{sotp_pipe_ps.{k}|usd2}}}}</td></tr>')
body = body.replace('@@PIPE_ROWS@@', '\n    '.join(pr))
rr = [f'<tr><td class="label">{{{{rev_rows.{i}.d}}}}</td><td class="right-al">{{{{rev_rows.{i}.px|usd2}}}}</td><td class="right-al">{{{{rev_rows.{i}.eps|usd2}}}}</td><td class="right-al">{{{{rev_rows.{i}.pe|x2}}}}</td></tr>'
      for i in range(len(M['rev_rows']))]
body = body.replace('@@REV_ROWS@@', '\n    '.join(rr))
# Cuadro PFE vs. ABBV vs. LLY vs. JNJ: columnas = compañías presentes en model.json["cmp_rows"]
n = len(M['cmp_rows'])
FIELDS = [('Precio (cierre 20-nov-2026)', 'precio', 'usd2'), ('Fair value (blend)', 'fair_value', 'usd2'), ('Distancia al precio', 'gap_pct', 'spct1'),
          ('M1 suma de partes + rNPV', 'm1_sotp', 'usd2'), ('M2 comparables', 'm2_comp', 'usd2'), ('M3 reversión', 'm3_rev', 'usd2'),
          ('M4 consenso', 'm4_cons', 'usd2'), ('Independientes del precio (40%)', 'indep', 'usd2'), ('Anclados al mercado (60%)', 'anclados', 'usd2'),
          ('P/E sobre EPS 2027E', 'pe_fy27', 'x1'), ('Rendimiento del dividendo', 'div_yield_pct', 'pct2'), ('Dividendos / FCF (TTM)', 'payout_fcf_pct', 'pct0'),
          ('Deuda neta / EBITDA', 'nd_ebitda', 'x2'), ('I+D / ventas (TTM)', 'rd_ventas_pct', 'pct1'), ('Margen bruto GAAP (3T)', 'margen_bruto_pct', 'pct1'),
          ('Ventas en riesgo antes de 2031', 'ventas_riesgo_loe_2030_pct', 'pct1'), ('Crecimiento EPS 2027E', 'crec_eps_fy27_pct', 'spct1'),
          ('WACC', 'wacc_pct', 'pct2'), ('Postura', 'postura', '')]
t = ['<tr><th>Métrica</th>' + ''.join(f'<th class="right-al">{{{{cmp_rows.{j}.ticker}}}}</th>' for j in range(n)) + '</tr>']
for lab, f, fm in FIELDS:
    cls = ' class="total"' if f == 'fair_value' else ''
    t.append(f'<tr{cls}><td class="label">{lab}</td>' + ''.join(f'<td class="right-al">{{{{cmp_rows.{j}.{f}|{fm}}}}}</td>' for j in range(n)) + '</tr>')
body = body.replace('@@CMP_TABLE@@', '\n    '.join(t))
body = body.replace('@@CMP_NOTE@@', '' if M['cmp_has_pfe'] else
                    'El informe de Pfizer todavía no tiene su modelo en esta rama: el cuadro muestra AbbVie, Lilly y J&amp;J, y se completa al reconstruirlo con el model.json de Pfizer.')
full = head + body + '\n' + eng.rstrip() + '\n\n' + ch
assert '@@' not in full
open('abbv.full.tpl.html', 'w', encoding='utf-8', newline='\n').write(full)
subprocess.run([sys.executable, 'render.py', 'abbv.full.tpl.html', f'{ROOT}/informes/abbv.html'], check=True)
