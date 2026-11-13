# Arma informes/lly.html: cabecera y CSS (lly.head.html, con .verdict-note en var(--muted)), cuerpo (lly.body.tpl.html),
# motor de gráficos (engine.js, el de la edición de septiembre) con cuatro parches para celular, y charts_lly.js.
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()   # raíz del repo
head = open('lly.head.html', encoding='utf-8').read()
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
body = open('lly.body.tpl.html', encoding='utf-8').read()
ch = open('charts_lly.js', encoding='utf-8').read()
full = head + body + '\n' + eng.rstrip() + '\n\n' + ch
assert '@@' not in full
open('lly.full.tpl.html', 'w', encoding='utf-8', newline='\n').write(full)
subprocess.run([sys.executable, 'render.py', 'lly.full.tpl.html', f'{ROOT}/informes/lly.html'], check=True)
