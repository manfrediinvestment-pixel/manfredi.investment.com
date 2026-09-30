# Arma informes/ko.html: CSS y motor de gráficos de informes/pg.html (ya probados en celular) + plantilla + modelo.
import subprocess, sys, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5].as_posix()   # raíz del repo
pg = open(f'{ROOT}/informes/pg.html', encoding='utf-8').read()
css = pg[pg.index('<style>'): pg.index('</style>')+len('</style>')]
css = css.replace('content:"PG";', 'content:"KO";')
assert 'content:"KO"' in css
s0 = pg.index('<script>', pg.index('</style>'))
s1 = pg.index('  function renderAll(){', s0)
eng = pg[s0:s1]
for fn in ('function drawVBars','function drawHBars','function drawLines','function drawRangeBars','function drawGroupedBars','function drawLegend','function wrapLabel','var padL = Math.min(opts.padL || 128'):
    assert fn in eng, fn
# drawLines: rango del eje Y opcional (opts.minV / opts.maxV) para escalas limpias
a = "    var minV = Math.min.apply(null, allVals) * 0.92;\n"
assert a in eng, 'drawLines minV'
eng = eng.replace(a, a + "    if(opts.minV != null) minV = opts.minV; if(opts.maxV != null) maxV = opts.maxV;\n", 1)
# drawLines: el margen inferior crece si la leyenda ocupa más de una fila (celular)
a = "    var padL = 40, padR = 28, padT = 16, padB = 54;\n"
assert eng.count(a) == 1, 'drawLines padB'
eng = eng.replace(a, a + "    ctx.font = '11px \"Inter\", sans-serif'; var lw = 0; series.forEach(function(s){ lw += 14 + ctx.measureText(s.name).width + 20; }); padB += Math.max(0, Math.ceil(lw / (W - padL)) - 1) * 15;\n", 1)
# drawGroupedBars: grilla cada 2 o 5 puntos si el rango es amplio, y etiquetas de los rombos más chicas si no entran
a = "    for(var gv = Math.ceil(minV); gv <= Math.floor(maxV); gv++){\n"
assert eng.count(a) == 1, 'grid step'
eng = eng.replace(a, "    var gstep = (maxV - minV) > 24 ? 5 : ((maxV - minV) > 12 ? 2 : 1);\n    for(var gv = Math.ceil(minV/gstep)*gstep; gv <= Math.floor(maxV); gv += gstep){\n", 1)
a = """        ctx.font = '600 10.5px "IBM Plex Mono", monospace'; ctx.textAlign = 'center';
        var mv = markers.values[i];
        ctx.fillText((mv>0?'+':'')+mv+'%', cx, padT - 6);"""
assert eng.count(a) == 1, 'markers'
eng = eng.replace(a, """        var narrow = slot < 40;
        ctx.font = (narrow ? '600 9px' : '600 10.5px') + ' "IBM Plex Mono", monospace'; ctx.textAlign = 'center';
        var mv = markers.values[i];
        ctx.fillText((mv>0?'+':'')+mv+(narrow?'':'%'), cx, padT - 6);""", 1)
ch = open('charts_ko.js', encoding='utf-8').read()
tpl = open('ko.tpl.html', encoding='utf-8').read().replace('@@CSS@@', css).replace('@@SCRIPT@@', eng.rstrip() + '\n' + ch.lstrip('\n').rstrip('\n'))
assert '@@' not in tpl
open('ko.full.tpl.html', 'w', encoding='utf-8', newline='\n').write(tpl)
subprocess.run([sys.executable, 'render.py', 'ko.full.tpl.html', f'{ROOT}/informes/ko.html'], check=True)
