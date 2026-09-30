# Arma informes/wmt.html: CSS y motor de gráficos de informes/pg.html (ya probados en celular) + plantilla + modelo.
import subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4].as_posix()   # raíz del repo (.claude/skills/informe-consumo-masivo/modelos/wmt)
pg = open(f'{ROOT}/informes/pg.html', encoding='utf-8').read()
css = pg[pg.index('<style>'): pg.index('</style>')+len('</style>')]
css = css.replace('content:"PG";', 'content:"WMT";')
assert 'content:"WMT"' in css
s0 = pg.index('<script>', pg.index('</style>'))
s1 = pg.index('  function renderAll(){', s0)
eng = pg[s0:s1]
for fn in ('function drawVBars', 'function drawHBars', 'function drawLines', 'function drawRangeBars', 'function drawGroupedBars', 'function drawLegend', 'function wrapLabel', 'var padL = Math.min(opts.padL || 128'):
    assert fn in eng, fn
# drawLines: rango del eje Y opcional (opts.minV / opts.maxV) para escalas limpias (mismo parche que UNH)
a = "    var minV = Math.min.apply(null, allVals) * 0.92;\n"
assert a in eng, 'drawLines minV'
eng = eng.replace(a, a + "    if(opts.minV != null) minV = opts.minV; if(opts.maxV != null) maxV = opts.maxV;\n", 1)
# drawGroupedBars: rótulo del rombo con un decimal (las comparables vienen con decimales)
b = "ctx.fillText((mv>0?'+':'')+mv+'%', cx, padT - 6);"
assert b in eng, 'grouped marker'
eng = eng.replace(b, "ctx.fillText((mv>0?'+':'')+(Math.round(mv*10)/10).toFixed(1)+'%', cx, padT - 6);", 1)
# en pantallas angostas el rótulo del rombo va en letra más chica para que no se encime con el vecino
c = "var mv = markers.values[i];"
assert c in eng, 'marker mv'
eng = eng.replace(c, c + " if(slot < 46) ctx.font = '600 8.5px \"IBM Plex Mono\", monospace';", 1)
ch = open(HERE/'charts_wmt.js', encoding='utf-8').read()
tpl = open(HERE/'wmt.tpl.html', encoding='utf-8').read().replace('@@CSS@@', css).replace('@@SCRIPT@@', eng.rstrip() + '\n' + ch.lstrip('\n').rstrip('\n'))
assert '@@' not in tpl
open(HERE/'wmt.full.tpl.html', 'w', encoding='utf-8', newline='\n').write(tpl)
subprocess.run([sys.executable, str(HERE/'render.py'), str(HERE/'wmt.full.tpl.html'), f'{ROOT}/informes/wmt.html'], check=True)
